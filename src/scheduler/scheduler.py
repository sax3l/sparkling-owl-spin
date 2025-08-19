import time
import datetime
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.database.models import Job, JobStatus
from src.scraper.template_runtime import run_template
from src.database.manager import SessionLocal

scheduler = BackgroundScheduler()
scheduler.start()
logger = logging.getLogger(__name__)

def _run_job(job_id: str):
    """
    Fetches a job from the DB, runs it, and updates its status.
    A new DB session is created for each job run.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found in database for execution.")
            return

        logger.info(f"Starting job {job.id} for URL: {job.start_url}")
        job.status = JobStatus.RUNNING.value
        job.started_at = datetime.datetime.utcnow()
        db.commit()
        
        # In a real scenario, you'd pass real HTML content here
        html_content = f"<html><body>Mock content for {job.start_url}</body></html>"
        template = {"id": "mock-template"} # Placeholder for a real template
        
        record, dq_metrics = run_template(html_content, template)
        
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