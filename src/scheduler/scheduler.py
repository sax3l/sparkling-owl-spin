import time
from apscheduler.schedulers.background import BackgroundScheduler
from src.database.models import Job, JobStatus
from src.scraper.template_runtime import run_template

scheduler = BackgroundScheduler()
scheduler.start()

def _run_job(job: Job):
    """Simulates running a crawl or scrape job."""
    print(f"Starting job {job.id} for URL: {job.task.start_url}")
    job.status = JobStatus.RUNNING
    
    try:
        # In a real scenario, you'd pass HTML content here
        html_content = f"<html><body>Mock content for {job.task.start_url}</body></html>"
        template = {"id": "mock-template"} # Placeholder for a real template
        
        record, dq_metrics = run_template(html_content, template)
        
        print(f"Job {job.id} completed successfully. Data: {record}, DQ: {dq_metrics}")
        job.status = JobStatus.COMPLETED
    except Exception as e:
        print(f"Job {job.id} failed: {e}")
        job.status = JobStatus.FAILED

def schedule_job(job: Job):
    """Adds a job to the scheduler to be run immediately."""
    scheduler.add_job(_run_job, args=[job])