from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from src.database.models import Job, JobCreate, JobRead, JobStatus
from src.database.manager import get_db
from src.scheduler.scheduler import schedule_job
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/jobs", response_model=JobRead, status_code=202)
async def submit_job(task: JobCreate, db: Session = Depends(get_db)):
    """Submits a new job to the scheduler and saves it to the database."""
    logger.info(f"Received job submission for URL: {task.start_url}")
    
    job = Job(
        start_url=task.start_url,
        job_type=task.job_type.value,
        params=task.params,
        status=JobStatus.PENDING.value
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job {job.id} created and saved to database.")
    
    schedule_job(job.id)
    
    return job

@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    """Retrieves the status of a specific job from the database."""
    logger.debug(f"Fetching status for job {job_id}")
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        logger.warning(f"Job with ID {job_id} not found.")
        raise HTTPException(status_code=404, detail="Job not found")
        
    return job