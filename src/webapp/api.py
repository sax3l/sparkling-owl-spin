from fastapi import APIRouter, HTTPException
from uuid import UUID
from src.database.models import Job, ScrapeTask, JobStatus
from src.scheduler.scheduler import schedule_job

router = APIRouter()

# In-memory storage for jobs (replace with DB later)
jobs_db: dict[UUID, Job] = {}

@router.post("/jobs", response_model=Job, status_code=202)
async def submit_job(task: ScrapeTask):
    """Submits a new job to the scheduler."""
    job = Job(task=task)
    jobs_db[job.id] = job
    schedule_job(job)
    return job

@router.get("/jobs/{job_id}", response_model=Job)
async def get_job_status(job_id: UUID):
    """Retrieves the status of a specific job."""
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job