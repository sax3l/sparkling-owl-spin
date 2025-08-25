import datetime
from fastapi import APIRouter, HTTPException, Depends, Header, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict, Any
from src.database.models import Job, CrawlJobCreate, ScrapeJobCreate, DiagnosticJobCreate, JobRead, JobStatus, JobType, JobProgress, JobMetrics, JobExport, JobExportArtifact, JobLogs, JobLinks
from src.database.manager import get_db
from src.scheduler.scheduler import schedule_job
from src.webapp.security import get_current_tenant_id, authorize_with_scopes
from src.utils.deprecation import deprecated_endpoint
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/jobs/crawl", response_model=JobRead, status_code=202, dependencies=[Depends(authorize_with_scopes(["jobs:write"]))])
@deprecated_endpoint(sunset_date=datetime.date(2025, 1, 1)) # Example: This endpoint will be deprecated by Jan 1, 2025
async def submit_crawl_job(
    task: CrawlJobCreate, 
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """Submits a new crawl job to the scheduler."""
    logger.info(f"Received crawl job submission for seeds: {task.seeds}", extra={"idempotency_key": idempotency_key, "tenant_id": str(tenant_id)})
    
    if not task.seeds:
        raise HTTPException(status_code=400, detail="Seed list cannot be empty")

    job = Job(
        tenant_id=tenant_id,
        start_url=task.seeds[0],
        job_type=JobType.CRAWL.value,
        params=task.model_dump(),
        status=JobStatus.QUEUED.value,
        created_at=datetime.datetime.utcnow() # Ensure created_at is set
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    logger.info(f"Job {job.id} created and queued.", extra={"job_id": str(job.id), "tenant_id": str(tenant_id)})
    
    schedule_job(str(job.id), job_type=JobType.CRAWL.value, params=task.model_dump())
    
    # Construct JobRead from the ORM object, which will use the model_validator
    return JobRead.model_validate(job)

@router.post("/jobs/scrape", response_model=JobRead, status_code=202, dependencies=[Depends(authorize_with_scopes(["jobs:write"]))])
async def submit_scrape_job(
    task: ScrapeJobCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """Submits a new scrape job to the scheduler."""
    logger.info(f"Received scrape job submission for template: {task.template_id}", extra={"idempotency_key": idempotency_key, "tenant_id": str(tenant_id)})

    start_url = task.source.sitemap_query.domain if task.source.sitemap_query else (task.source.urls[0] if task.source.urls else "N/A")

    job = Job(
        tenant_id=tenant_id,
        start_url=start_url,
        job_type=JobType.SCRAPE.value,
        params=task.model_dump(),
        status=JobStatus.QUEUED.value,
        created_at=datetime.datetime.utcnow() # Ensure created_at is set
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(f"Job {job.id} created and queued.", extra={"job_id": str(job.id), "tenant_id": str(tenant_id)})
    schedule_job(str(job.id), job_type=JobType.SCRAPE.value, params=task.model_dump())

    # Construct JobRead from the ORM object, which will use the model_validator
    return JobRead.model_validate(job)

@router.post("/jobs/diagnostic", response_model=JobRead, status_code=202, dependencies=[Depends(authorize_with_scopes(["jobs:write"]))])
async def submit_diagnostic_job(
    task: DiagnosticJobCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """
    Submits a new diagnostic job to run a template against a target URL or inline HTML.
    This is used for "stagingkörning" of templates.
    """
    logger.info(f"Received diagnostic job submission for template: {task.template_id}", extra={"idempotency_key": idempotency_key, "tenant_id": str(tenant_id)})

    start_url = task.target_url if task.target_url else "inline_html_diagnostic"

    job = Job(
        tenant_id=tenant_id,
        start_url=start_url,
        job_type=JobType.DIAGNOSTIC.value,
        params=task.model_dump(),
        status=JobStatus.QUEUED.value,
        created_at=datetime.datetime.utcnow()
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    logger.info(f"Diagnostic job {job.id} created and queued.", extra={"job_id": str(job.id), "tenant_id": str(tenant_id)})
    schedule_job(str(job.id), job_type=JobType.DIAGNOSTIC.value, params=task.model_dump())

    return JobRead.model_validate(job)

@router.get("/jobs/{job_id}", response_model=JobRead, dependencies=[Depends(authorize_with_scopes(["data:read"]))])
async def get_job_status(
    job_id: UUID, 
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Retrieves the status of a specific job from the database."""
    logger.debug(f"Fetching status for job {job_id}", extra={"job_id": str(job_id), "tenant_id": str(tenant_id)})
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == tenant_id).first()
    
    if not job:
        logger.warning(f"Job with ID {job_id} not found for tenant {tenant_id}.", extra={"job_id": str(job_id), "tenant_id": str(tenant_id)})
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Construct JobRead from the ORM object, which will use the model_validator
    return JobRead.model_validate(job)

@router.post("/jobs/{job_id}/cancel", status_code=202, dependencies=[Depends(authorize_with_scopes(["jobs:write"]))])
async def cancel_job(
    job_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Requests cancellation of a running or queued job."""
    logger.info(f"Received cancellation request for job {job_id}", extra={"job_id": str(job_id), "tenant_id": str(tenant_id)})
    job = db.query(Job).filter(Job.id == job_id, Job.tenant_id == tenant_id).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    
    if job.status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value, JobStatus.CANCELLED.value]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Job is already in status: {job.status}. Cannot cancel.")

    # Mark job as cancelled. The scheduler/worker should pick this up.
    job.status = JobStatus.CANCELLED.value
    job.finished_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(job)

    logger.info(f"Job {job_id} marked as CANCELLED.", extra={"job_id": str(job_id), "tenant_id": str(tenant_id)})
    return {"message": "Cancellation requested. Job status will update shortly."}


@router.get("/jobs", response_model=List[JobRead], dependencies=[Depends(authorize_with_scopes(["data:read"]))])
async def list_jobs(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    job_type: Optional[JobType] = Query(None),
    status: Optional[JobStatus] = Query(None),
    sort_by: str = Query("created_at", description="Sort by field (e.g., created_at, -status)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Lists jobs for the authenticated tenant with filtering and sorting."""
    query = db.query(Job).filter(Job.tenant_id == tenant_id)

    if job_type:
        query = query.filter(Job.job_type == job_type.value)
    if status:
        query = query.filter(Job.status == status.value)

    # Sorting
    sort_column = sort_by.lstrip('-')
    if hasattr(Job, sort_column):
        if sort_by.startswith('-'):
            query = query.order_by(getattr(Job, sort_column).desc())
        else:
            query = query.order_by(getattr(Job, sort_column).asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field: {sort_by}")

    jobs = query.offset(offset).limit(limit).all()
    # Construct JobRead from the ORM objects, which will use the model_validator
    return [JobRead.model_validate(job) for job in jobs]