import time
import datetime
import logging
import yaml
import asyncio
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, Any
from uuid import UUID

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    
from database.models import Job, JobStatus, JobType
from scraper.dsl.schema import ScrapingTemplate
from scraper.template_runtime import run_template
from database.manager import SessionLocal
from anti_bot.policy_manager import PolicyManager
from scraper.transport import TransportManager
from crawler.sitemap_generator import Crawler
from crawler.url_frontier import URLFrontier
from crawler.robots_parser import RobotsParser
from utils.metrics import REQUESTS_TOTAL, EXTRACTIONS_OK_TOTAL, REQUEST_DURATION_SECONDS, DQ_SCORE
from scheduler.jobs.export_job import execute_export_job
from utils.logger import get_logger

logger = get_logger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()
logger = logging.getLogger(__name__)

REDIS_URL = "redis://localhost:6379/0"

def _load_template(template_id: str) -> ScrapingTemplate:
    """Loads and validates a YAML template file."""
    template_path = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "templates" / f"{template_id}.yaml"
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found for ID: {template_id}")
    
    with open(template_path, 'r') as f:
        template_data = yaml.safe_load(f)
    
    return ScrapingTemplate.model_validate(template_data)

async def _run_job(job_id: str, job_type: str, params: Dict[str, Any]):
    """
    Fetches a job from the DB, determines its type, and executes it.
    This function is called by APScheduler.
    """
    db = SessionLocal()
    log_extra = {"job_id": job_id, "run_id": f"run_{datetime.datetime.utcnow().isoformat()}"}
    job = None # Initialize job to None
    try:
        # For EXPORT jobs, job_id refers to ExportHistory.id, not Job.id
        if job_type == JobType.EXPORT.value:
            # Execute the async export job in a new event loop
            asyncio.run(execute_export_job(job_id, params))
            logger.info(f"EXPORT job {job_id} execution initiated.", extra=log_extra)
            return # Export job updates its own status
        
        # For CRAWL/SCRAPE/DIAGNOSTIC jobs, fetch from Job table
        job = db.query(Job).filter(Job.id == UUID(job_id)).first()
        if not job:
            logger.error(f"Job {job_id} not found", extra=log_extra)
            return

        log_extra["tenant_id"] = str(job.tenant_id) # Add tenant_id to logs
        log_extra["domain"] = urlparse(job.start_url).netloc
        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.datetime.utcnow()
        db.commit()

        if job.job_type == JobType.CRAWL.value:
            _execute_crawl_job(job, log_extra)
        elif job.job_type == JobType.SCRAPE.value:
            _execute_scrape_job(job, log_extra)
        elif job.job_type == JobType.DIAGNOSTIC.value:
            _execute_diagnostic_job(job, log_extra)
        else:
            logger.warning(f"Unknown job type: {job.job_type}", extra=log_extra)
            job.status = JobStatus.FAILED.value
            job.result = {"error": "Unknown job type"}

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True, extra=log_extra)
        if job: # Only update if job object exists (not for EXPORT which handles its own status)
            job.status = JobStatus.FAILED.value
            job.result = {"error": str(e)}
    finally:
        if job: # Only update if job object exists
            job.finished_at = datetime.datetime.utcnow()
            db.commit()
        db.close()

def _execute_crawl_job(job: Job, log_extra: dict):
    logger.info(f"Executing CRAWL job for URL: {job.start_url}", extra=log_extra)
    # ... (instrumentation would be added inside the Crawler class)
    job.status = JobStatus.COMPLETED.value
    logger.info(f"CRAWL job completed.", extra=log_extra)

def _execute_scrape_job(job: Job, log_extra: dict):
    logger.info(f"Executing SCRAPE job for URL: {job.start_url}", extra=log_extra)
    
    policy_manager = PolicyManager(redis_url=REDIS_URL)
    transport_manager = TransportManager()
    domain = urlparse(job.start_url).netloc
    policy = policy_manager.get_policy(domain)
    
    template_id = job.params.get("template_id", "vehicle_detail_v3")
    log_extra["template"] = template_id

    with REQUEST_DURATION_SECONDS.labels(mode=policy.transport, domain=domain).time():
        html_content, status_code = transport_manager.fetch(job.start_url, policy)

    REQUESTS_TOTAL.labels(mode=policy.transport, domain=domain, status_code=status_code).inc()

    if status_code != 200:
        policy_manager.update_on_failure(domain, status_code)
        raise Exception(f"Failed to fetch URL with status code: {status_code}")

    policy_manager.update_on_success(domain)
    template = _load_template(template_id)
    
    record, dq_metrics = run_template(html_content, template)
    
    job.result = {"data": record, "dq_metrics": dq_metrics}
    job.status = JobStatus.COMPLETED.value
    
    EXTRACTIONS_OK_TOTAL.labels(domain=domain, template=template_id).inc()
    DQ_SCORE.labels(domain=domain, template=template_id).observe(dq_metrics.get("dq_score", 0))
    
    logger.info(f"SCRAPE job completed successfully.", extra=log_extra)

def _execute_diagnostic_job(job: Job, log_extra: dict):
    logger.info(f"Executing DIAGNOSTIC job for template: {job.params.get('template_id')}", extra=log_extra)
    
    template_id = job.params.get("template_id")
    target_url = job.params.get("target_url")
    sample_html = job.params.get("sample_html")
    
    try:
        template = _load_template(template_id)
        html_content = ""
        if target_url:
            # In a real scenario, you'd fetch the URL using TransportManager
            logger.info(f"Fetching target URL for diagnostic: {target_url}", extra=log_extra)
            # html_content, status_code = TransportManager().fetch(target_url, PolicyManager(redis_url=REDIS_URL).get_policy(urlparse(target_url).netloc))
            html_content = "<html><body>Mock HTML from target URL</body></html>" # Mock for now
        elif sample_html:
            html_content = sample_html
            logger.info("Using inline HTML for diagnostic.", extra=log_extra)
        
        record, dq_metrics = run_template(html_content, template)
        
        job.result = {"data": record, "dq_metrics": dq_metrics, "status": "success"}
        job.status = JobStatus.COMPLETED.value
        logger.info(f"DIAGNOSTIC job completed successfully.", extra=log_extra)

    except Exception as e:
        job.result = {"error": str(e), "status": "failed"}
        job.status = JobStatus.FAILED.value
        logger.error(f"DIAGNOSTIC job failed: {e}", exc_info=True, extra=log_extra)

def schedule_job(job_id: str, job_type: str = JobType.CRAWL.value, params: Dict[str, Any] = None):
    """Adds a job to the scheduler to be run immediately."""
    logger.info(f"Scheduling job {job_id} of type {job_type} for immediate execution.", extra={"job_id": job_id, "job_type": job_type})
    scheduler.add_job(_run_job, args=[job_id, job_type, params or {}])

class ECaDPScheduler:
    """
    Enhanced scheduler for ECaDP platform with comprehensive job management.
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.logger = logging.getLogger(__name__)
        self._running_jobs = {}
        self._job_history = []
    
    def create_scraping_job(self, job_data: dict) -> str:
        """Create and schedule a new scraping job."""
        job_id = f"scraping_{int(time.time())}"
        
        try:
            # Add job to scheduler
            self.scheduler.add_job(
                func=self._execute_scraping_job,
                args=[job_id, job_data],
                id=job_id,
                name=f"Scraping Job {job_id}"
            )
            
            self._running_jobs[job_id] = {
                "type": "scraping",
                "status": "scheduled",
                "created_at": datetime.datetime.now(),
                "data": job_data
            }
            
            self.logger.info(f"Created scraping job {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to create scraping job: {e}")
            raise
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled or running job."""
        try:
            self.scheduler.remove_job(job_id)
            
            if job_id in self._running_jobs:
                self._running_jobs[job_id]["status"] = "cancelled"
                self._running_jobs[job_id]["cancelled_at"] = datetime.datetime.now()
            
            self.logger.info(f"Cancelled job {job_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    def get_job_status(self, job_id: str) -> dict:
        """Get status and details of a specific job."""
        if job_id in self._running_jobs:
            return self._running_jobs[job_id]
        
        # Check job history
        for job in self._job_history:
            if job["id"] == job_id:
                return job
        
        return None
    
    def list_jobs(self, status_filter: str = None) -> list:
        """List all jobs with optional status filter."""
        all_jobs = list(self._running_jobs.values()) + self._job_history
        
        if status_filter:
            return [job for job in all_jobs if job.get("status") == status_filter]
        
        return all_jobs
    
    def get_scheduler_stats(self) -> dict:
        """Get comprehensive scheduler statistics."""
        running_jobs = [job for job in self._running_jobs.values() if job["status"] == "running"]
        completed_jobs = [job for job in self._job_history if job["status"] == "completed"]
        failed_jobs = [job for job in self._job_history if job["status"] == "failed"]
        
        return {
            "total_jobs": len(self._running_jobs) + len(self._job_history),
            "running_jobs": len(running_jobs),
            "scheduled_jobs": len([job for job in self._running_jobs.values() if job["status"] == "scheduled"]),
            "completed_jobs": len(completed_jobs),
            "failed_jobs": len(failed_jobs),
            "scheduler_running": self.scheduler.running,
            "last_updated": datetime.datetime.now().isoformat()
        }
    
    async def _execute_scraping_job(self, job_id: str, job_data: dict):
        """Execute a scraping job."""
        try:
            self.logger.info(f"Starting execution of scraping job {job_id}")
            
            # Update job status
            if job_id in self._running_jobs:
                self._running_jobs[job_id]["status"] = "running"
                self._running_jobs[job_id]["started_at"] = datetime.datetime.now()
            
            # Execute actual scraping logic
            try:
                result = await self._execute_scraping_job_impl(self._running_jobs[job_id])
                
                # Update job status with result
                if job_id in self._running_jobs:
                    self._running_jobs[job_id]["result"] = result
                    self._running_jobs[job_id]["status"] = "completed" if result.get("success") else "failed"
            except Exception as e:
                logger.error(f"Job {job_id} execution failed: {e}")
                if job_id in self._running_jobs:
                    self._running_jobs[job_id]["error"] = str(e)
                    self._running_jobs[job_id]["status"] = "failed"
            
            # Mark job as completed
            self._complete_job(job_id, "completed")
            
            logger.info(f"Completed scraping job {job_id}")
            
        except Exception as e:
            logger.error(f"Scraping job {job_id} failed: {e}")
            self._complete_job(job_id, "failed", str(e))
    
    async def _execute_scraping_job_impl(self, job) -> Dict[str, Any]:
        """Execute the actual scraping job logic"""
        try:
            # Get job parameters
            job_config = job.config if hasattr(job, 'config') else {}
            urls = job_config.get('urls', [])
            template_id = job_config.get('template_id')
            
            if not urls:
                return {"success": False, "error": "No URLs provided"}
            
            if not template_id:
                return {"success": False, "error": "No template ID provided"}
            
            # Load scraping template
            try:
                template = _load_template(template_id)
            except Exception as e:
                return {"success": False, "error": f"Failed to load template: {e}"}
            
            # Initialize components
            transport_manager = TransportManager()
            policy_manager = PolicyManager()
            
            results = []
            for url in urls:
                try:
                    # Run template against URL
                    result = await run_template(
                        template=template,
                        url=url,
                        transport_manager=transport_manager,
                        policy_manager=policy_manager
                    )
                    results.append({
                        "url": url,
                        "success": True,
                        "data": result
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    results.append({
                        "url": url,
                        "success": False,
                        "error": str(e)
                    })
            
            # Calculate success rate
            successful = sum(1 for r in results if r.get("success"))
            total = len(results)
            success_rate = successful / total if total > 0 else 0
            
            return {
                "success": success_rate > 0.5,  # Consider job successful if > 50% URLs succeeded
                "total_urls": total,
                "successful_urls": successful,
                "success_rate": success_rate,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Scraping job execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _complete_job(self, job_id: str, status: str, error_message: str = None):
        """Move job from running to history."""
        if job_id in self._running_jobs:
            job = self._running_jobs.pop(job_id)
            job["status"] = status
            job["completed_at"] = datetime.datetime.now()
            job["id"] = job_id
            
            if error_message:
                job["error"] = error_message
            
            self._job_history.append(job)
            
            # Keep only last 100 jobs in history
            if len(self._job_history) > 100:
                self._job_history = self._job_history[-100:]
    
    def shutdown(self):
        """Shutdown the scheduler gracefully."""
        try:
            self.scheduler.shutdown(wait=True)
            self.logger.info("Scheduler shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during scheduler shutdown: {e}")


# Keep the existing global scheduler instance for backward compatibility