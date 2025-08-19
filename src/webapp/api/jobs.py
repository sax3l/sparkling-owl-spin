from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from src.database.models import Job, CrawlJobCreate, ScrapeJobCreate, JobRead, JobStatus, JobType
from src.database.manager import get_db
from src.scheduler.scheduler import schedule_job
from src.webapp.security import get_api_key
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/jobs/crawl", response_model=JobRead, status_code=202, dependencies=[Depends(get_api_key)])
async def submit_crawl_job(
    task: CrawlJobCreate, 
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """Submits a new crawl job to the scheduler."""
    logger.info(f"Received crawl job submission for seeds: {task.seeds}", extra={"idempotency_key": idempotency_key})
    
    if not task.seeds:
        raise HTTPException(status_code=400, detail="Seed list cannot be empty")

    job = Job(
        start_url=task.seeds[0],
        job_type=JobType.CRAWL.value,
        params=task.model_dump(),
        status=JobStatus.QUEUED.value
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job {job.id} created and queued.", extra={"job_id": str(job.id)})
    
    schedule_job(str(job.id))
    
    response_data = {**job.__dict__, "links": {"self": f"/v1/jobs/{job.id}"}}
    return response_data

@router.post("/jobs/scrape", response_model=JobRead, status_code=202, dependencies=[Depends(get_api_key)])
async def submit_scrape_job(
    task: ScrapeJobCreate,
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """Submits a new scrape job to the scheduler."""
    logger.info(f"Received scrape job submission for template: {task.template_id}", extra={"idempotency_key": idempotency_key})

    start_url = task.source.sitemap_query.domain if task.source.sitemap_query else (task.source.urls[0] if task.source.urls else "N/A")

    job = Job(
        start_url=start_url,
        job_type=JobType.SCRAPE.value,
        params=task.model_dump(),
        status=JobStatus.QUEUED.value
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(f"Job {job.id} created and queued.", extra={"job_id": str(job.id)})
    schedule_job(str(job.id))

    response_data = {**job.__dict__, "links": {"self": f"/v1/jobs/{job.id}"}}
    return response_data

@router.get("/jobs/{job_id}", response_model=JobRead, dependencies=[Depends(get_api_key)])
async def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    """Retrieves the status of a specific job from the database."""
    logger.debug(f"Fetching status for job {job_id}", extra={"job_id": str(job_id)})
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        logger.warning(f"Job with ID {job_id} not found.", extra={"job_id": str(job_id)})
        raise HTTPException(status_code=404, detail="Job not found")
        
    response_data = {**job.__dict__, "links": {"self": f"/v1/jobs/{job.id}"}}
    return response_data