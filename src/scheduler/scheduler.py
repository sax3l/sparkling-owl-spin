import time
import datetime
import logging
from urllib.parse import urlparse
from apscheduler.schedulers.background import BackgroundScheduler
from src.database.models import Job, JobStatus, JobType
from src.scraper.template_runtime import run_template
from src.database.manager import SessionLocal
from src.anti_bot.policy_manager import PolicyManager
from src.scraper.transport import TransportManager
from src.crawler.sitemap_generator import Crawler
from src.crawler.url_frontier import URLFrontier
from src.crawler.robots_parser import RobotsParser

scheduler = BackgroundScheduler()
scheduler.start()
logger = logging.getLogger(__name__)

REDIS_URL = "redis://localhost:6379/0"
DQ_COMPLETENESS_THRESHOLD = 0.7

def _run_job(job_id: str):
    """
    Fetches a job from the DB, determines its type, and executes it.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database for execution.")
            return

        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.datetime.utcnow()
        db.commit()

        if job.job_type == JobType.CRAWL.value:
            _execute_crawl_job(job)
        else:
            _execute_scrape_job(job)

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}", exc_info=True)
        if 'job' in locals() and job:
            job.status = JobStatus.FAILED.value
            job.result = {"error": str(e)}
    finally:
        if 'job' in locals() and job:
            job.finished_at = datetime.datetime.utcnow()
            db.commit()
        db.close()

def _execute_crawl_job(job: Job):
    logger.info(f"Executing CRAWL job {job.id} for URL: {job.start_url}")
    
    # Setup dependencies for the crawler
    frontier = URLFrontier(redis_url=REDIS_URL, queue_name=f"frontier:{job.id}")
    robots_parser = RobotsParser(redis_url=REDIS_URL)
    policy_manager = PolicyManager(redis_url=REDIS_URL)
    transport_manager = TransportManager()
    
    crawler = Crawler(frontier, robots_parser, policy_manager, transport_manager)
    crawler.crawl_domain(job.start_url)
    
    job.status = JobStatus.COMPLETED.value
    logger.info(f"CRAWL job {job.id} completed.")

def _execute_scrape_job(job: Job):
    logger.info(f"Executing SCRAPE job {job.id} for URL: {job.start_url}")
    
    policy_manager = PolicyManager(redis_url=REDIS_URL)
    transport_manager = TransportManager()
    domain = urlparse(job.start_url).netloc
    policy = policy_manager.get_policy(domain)

    html_content, status_code = transport_manager.fetch(job.start_url, policy)

    if status_code != 200:
        raise Exception(f"Failed to fetch URL with status code: {status_code}")

    template = {"id": "mock-template"}
    record, dq_metrics = run_template(html_content, template)
    
    job.result = {"data": record, "dq_metrics": dq_metrics}
    job.status = JobStatus.COMPLETED.value
    logger.info(f"SCRAPE job {job.id} completed.")

def schedule_job(job_id: str):
    """Adds a job to the scheduler to be run immediately."""
    logger.info(f"Scheduling job {job_id} for immediate execution.")
    scheduler.add_job(_run_job, args=[job_id])