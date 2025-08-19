import time
import datetime
import logging
from urllib.parse import urlparse
from apscheduler.schedulers.background import BackgroundScheduler
from src.database.models import Job, JobStatus
from src.scraper.template_runtime import run_template
from src.database.manager import SessionLocal
from src.anti_bot.policy_manager import PolicyManager
from src.scraper.transport import TransportManager

scheduler = BackgroundScheduler()
scheduler.start()
logger = logging.getLogger(__name__)

# TODO: Move Redis URL to a central config
REDIS_URL = "redis://localhost:6379/0"
DQ_COMPLETENESS_THRESHOLD = 0.7 # Alert if less than 70% of fields are found

def _run_job(job_id: str):
    """
    Fetches a job from the DB, runs it using adaptive policies, and updates its status.
    """
    db = SessionLocal()
    policy_manager = PolicyManager(redis_url=REDIS_URL)
    transport_manager = TransportManager()
    
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database for execution.")
            return

        domain = urlparse(job.start_url).netloc
        policy = policy_manager.get_policy(domain)

        # Respect backoff period
        if time.time() < policy.backoff_until:
            logger.warning(f"Job {job.id} for domain {domain} is in backoff. Rescheduling.")
            # Reschedule for later instead of failing
            scheduler.add_job(_run_job, 'date', run_date=datetime.datetime.fromtimestamp(policy.backoff_until), args=[job_id])
            return

        logger.info(f"Starting job {job.id} for URL: {job.start_url} with delay {policy.current_delay_seconds:.2f}s")
        time.sleep(policy.current_delay_seconds)

        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.datetime.utcnow()
        db.commit()
        
        html_content, status_code = transport_manager.fetch(job.start_url, policy)

        if status_code != 200:
            policy_manager.update_on_failure(domain, status_code)
            raise Exception(f"Failed to fetch URL with status code: {status_code}")
        
        policy_manager.update_on_success(domain)

        # Basic CAPTCHA and drift detection
        if "captcha" in html_content.lower() or "are you a robot" in html_content.lower():
            policy_manager.update_on_failure(domain, 999) # Custom code for CAPTCHA
            raise Exception("CAPTCHA detected. Aborting job and applying backoff.")

        template = {"id": "mock-template"} # Placeholder for a real template
        record, dq_metrics = run_template(html_content, template)
        
        if dq_metrics.get("completeness", 1.0) < DQ_COMPLETENESS_THRESHOLD:
            logger.critical(f"Potential template drift detected for job {job.id} on domain {domain}. Completeness was {dq_metrics['completeness']:.2%}")
            # In a real system, this could trigger an alert or pause jobs for this template.

        job.result = {"data": record, "dq_metrics": dq_metrics}
        job.status = JobStatus.COMPLETED.value
        logger.info(f"Job {job.id} completed successfully.")

    except Exception as e:
        logger.error(f"Job {job.id} failed: {e}", exc_info=True)
        if 'job' in locals() and job:
            job.status = JobStatus.FAILED.value
            job.result = {"error": str(e)}
    finally:
        if 'job' in locals() and job:
            job.finished_at = datetime.datetime.utcnow()
            db.commit()
        db.close()

def schedule_job(job_id: str):
    """Adds a job to the scheduler to be run immediately."""
    logger.info(f"Scheduling job {job_id} for immediate execution.")
    scheduler.add_job(_run_job, args=[job_id])