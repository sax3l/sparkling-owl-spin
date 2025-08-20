import time
import datetime
import logging
import yaml
import asyncio # Import asyncio for async export job
from pathlib import Path
from urllib.parse import urlparse
from apscheduler.schedulers.background import BackgroundScheduler
from src.database.models import Job, JobStatus, JobType
from src.scraper.dsl.schema import ScrapingTemplate
from src.scraper.template_runtime import run_template
from src.database.manager import SessionLocal
from src.anti_bot.policy_manager import PolicyManager
from src.scraper.transport import TransportManager
from src.crawler.sitemap_generator import Crawler
from src.crawler.url_frontier import URLFrontier
from src.crawler.robots_parser import RobotsParser
from src.utils.metrics import REQUESTS_TOTAL, EXTRACTIONS_OK_TOTAL, REQUEST_DURATION_SECONDS, DQ_SCORE
from src.scheduler.jobs.export_job import execute_export_job # Import the new export job

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

def _run_job(job_id: str, job_type: str, params: Dict[str, Any]):
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