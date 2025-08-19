import time
import datetime
import logging
import yaml
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

def _run_job(job_id: str):
    """
    Fetches a job from the DB, determines its type, and executes it.
    """
    db = SessionLocal()
    log_extra = {"job_id": job_id, "run_id": f"run_{datetime.datetime.utcnow().isoformat()}"}
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found", extra=log_extra)
            return

        log_extra["domain"] = urlparse(job.start_url).netloc
        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.datetime.utcnow()
        db.commit()

        if job.job_type == JobType.CRAWL.value:
            _execute_crawl_job(job, log_extra)
        else:
            _execute_scrape_job(job, log_extra)

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True, extra=log_extra)
        if 'job' in locals() and job:
            job.status = JobStatus.FAILED.value
            job.result = {"error": str(e)}
    finally:
        if 'job' in locals() and job:
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

def schedule_job(job_id: str):
    """Adds a job to the scheduler to be run immediately."""
    logger.info(f"Scheduling job {job_id} for immediate execution.", extra={"job_id": job_id})
    scheduler.add_job(_run_job, args=[job_id])