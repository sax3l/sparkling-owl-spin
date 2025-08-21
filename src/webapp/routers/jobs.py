"""
Job management router for the crawler platform.
"""
from typing import List, Optional, Dict, Any, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta
from enum import Enum
import uuid

from src.webapp.deps import (
    DatabaseSession, CurrentUser, AdminUser, PaginationDep,
    SortingDep, CacheServiceDep, RateLimitServiceDep
)
from src.services.job_scheduler import JobSchedulerService
from src.services.crawler import CrawlerService
from src.services.notification import NotificationService
from src.database.models import CrawlJob, JobTemplate, JobExecution
from src.utils.validators import validate_url, validate_cron_expression

router = APIRouter(prefix="/jobs", tags=["jobs"])

class JobType(str, Enum):
    """Job types."""
    CRAWL = "crawl"
    SCRAPE = "scrape"
    ANALYSIS = "analysis"
    EXPORT = "export"
    CLEANUP = "cleanup"

class JobStatus(str, Enum):
    """Job statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class JobPriority(str, Enum):
    """Job priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class CrawlConfig(BaseModel):
    """Crawl job configuration."""
    start_urls: List[str] = Field(..., min_items=1, description="Starting URLs")
    allowed_domains: Optional[List[str]] = Field(None, description="Allowed domains")
    max_depth: int = Field(3, ge=0, le=10, description="Maximum crawl depth")
    max_pages: int = Field(1000, ge=1, le=100000, description="Maximum pages to crawl")
    respect_robots_txt: bool = Field(True, description="Respect robots.txt")
    delay: float = Field(1.0, ge=0.1, le=60.0, description="Delay between requests")
    concurrent_requests: int = Field(8, ge=1, le=32, description="Concurrent requests")
    user_agent: Optional[str] = Field(None, description="Custom user agent")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    cookies: Optional[Dict[str, str]] = Field(None, description="Custom cookies")
    
    @validator('start_urls')
    def validate_start_urls(cls, v):
        for url in v:
            validate_url(url)
        return v

class ScheduleConfig(BaseModel):
    """Job schedule configuration."""
    enabled: bool = Field(False, description="Enable scheduling")
    cron_expression: Optional[str] = Field(None, description="Cron expression")
    timezone: str = Field("UTC", description="Timezone")
    max_executions: Optional[int] = Field(None, description="Maximum executions")
    end_date: Optional[datetime] = Field(None, description="Schedule end date")
    
    @validator('cron_expression')
    def validate_cron(cls, v):
        if v:
            validate_cron_expression(v)
        return v

class JobRequest(BaseModel):
    """Job creation request."""
    name: str = Field(..., min_length=1, max_length=255, description="Job name")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    type: JobType = Field(..., description="Job type")
    priority: JobPriority = Field(JobPriority.NORMAL, description="Job priority")
    tags: Optional[List[str]] = Field(None, description="Job tags")
    config: Dict[str, Any] = Field(..., description="Job configuration")
    schedule: Optional[ScheduleConfig] = Field(None, description="Schedule configuration")
    notifications: Optional[Dict[str, Any]] = Field(None, description="Notification settings")

class JobResponse(BaseModel):
    """Job response."""
    id: str
    name: str
    description: Optional[str]
    type: JobType
    status: JobStatus
    priority: JobPriority
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress: Dict[str, Any]
    statistics: Dict[str, Any]
    error_message: Optional[str]
    config: Dict[str, Any]
    schedule: Optional[ScheduleConfig]

@router.post("/", summary="Create new job", response_model=JobResponse)
async def create_job(
    job_request: JobRequest,
    db: DatabaseSession,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    rate_limiter: RateLimitServiceDep
) -> JobResponse:
    """Create a new crawl or processing job."""
    # Rate limiting
    if not await rate_limiter.check_rate_limit(
        f"create_job:{user.id}", limit=50, window=3600
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Job creation limit exceeded. Maximum 50 jobs per hour."
        )
    
    # Validate job configuration based on type
    if job_request.type == JobType.CRAWL:
        crawl_config = CrawlConfig(**job_request.config)
        job_request.config = crawl_config.dict()
    
    # Create job
    job_service = JobSchedulerService(db)
    job = await job_service.create_job(
        user_id=user.id,
        name=job_request.name,
        description=job_request.description,
        job_type=job_request.type,
        priority=job_request.priority,
        config=job_request.config,
        tags=job_request.tags or [],
        schedule=job_request.schedule.dict() if job_request.schedule else None,
        notifications=job_request.notifications
    )
    
    # Schedule job execution
    if job_request.schedule and job_request.schedule.enabled:
        background_tasks.add_task(
            job_service.schedule_job,
            job.id
        )
    else:
        # Queue immediate execution
        background_tasks.add_task(
            job_service.queue_job,
            job.id
        )
    
    return JobResponse(
        id=job.id,
        name=job.name,
        description=job.description,
        type=job.type,
        status=job.status,
        priority=job.priority,
        tags=job.tags,
        created_at=job.created_at,
        updated_at=job.updated_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        progress=job.progress or {},
        statistics=job.statistics or {},
        error_message=job.error_message,
        config=job.config,
        schedule=ScheduleConfig(**job.schedule) if job.schedule else None
    )

@router.get("/", summary="List jobs")
async def list_jobs(
    db: DatabaseSession,
    user: CurrentUser,
    pagination: PaginationDep,
    sorting: SortingDep,
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    type: Optional[JobType] = Query(None, description="Filter by type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search in name and description")
) -> Dict[str, Any]:
    """List user's jobs with filtering and pagination."""
    query = db.query(CrawlJob).filter(CrawlJob.user_id == user.id)
    
    # Apply filters
    if status:
        query = query.filter(CrawlJob.status == status)
    if type:
        query = query.filter(CrawlJob.type == type)
    if tags:
        for tag in tags:
            query = query.filter(CrawlJob.tags.contains([tag]))
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            CrawlJob.name.ilike(search_filter) |
            CrawlJob.description.ilike(search_filter)
        )
    
    # Apply sorting
    if sorting.sort_by == "created_at":
        order_col = CrawlJob.created_at
    elif sorting.sort_by == "updated_at":
        order_col = CrawlJob.updated_at
    elif sorting.sort_by == "name":
        order_col = CrawlJob.name
    elif sorting.sort_by == "status":
        order_col = CrawlJob.status
    else:
        order_col = CrawlJob.created_at
    
    if sorting.sort_order == "desc":
        order_col = order_col.desc()
    
    total = query.count()
    jobs = (
        query.order_by(order_col)
        .offset(pagination.skip)
        .limit(pagination.size)
        .all()
    )
    
    return {
        "jobs": [
            JobResponse(
                id=job.id,
                name=job.name,
                description=job.description,
                type=job.type,
                status=job.status,
                priority=job.priority,
                tags=job.tags or [],
                created_at=job.created_at,
                updated_at=job.updated_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                progress=job.progress or {},
                statistics=job.statistics or {},
                error_message=job.error_message,
                config=job.config,
                schedule=ScheduleConfig(**job.schedule) if job.schedule else None
            )
            for job in jobs
        ],
        "pagination": {
            "page": pagination.page,
            "size": pagination.size,
            "total": total,
            "pages": (total + pagination.size - 1) // pagination.size
        }
    }

@router.get("/{job_id}", summary="Get job details")
async def get_job(
    job_id: str,
    db: DatabaseSession,
    user: CurrentUser,
    include_logs: bool = Query(False, description="Include execution logs")
) -> Dict[str, Any]:
    """Get detailed information about a specific job."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    response = JobResponse(
        id=job.id,
        name=job.name,
        description=job.description,
        type=job.type,
        status=job.status,
        priority=job.priority,
        tags=job.tags or [],
        created_at=job.created_at,
        updated_at=job.updated_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        progress=job.progress or {},
        statistics=job.statistics or {},
        error_message=job.error_message,
        config=job.config,
        schedule=ScheduleConfig(**job.schedule) if job.schedule else None
    ).dict()
    
    if include_logs:
        # Get execution logs
        executions = (
            db.query(JobExecution)
            .filter(JobExecution.job_id == job_id)
            .order_by(JobExecution.started_at.desc())
            .limit(10)
            .all()
        )
        
        response["executions"] = [
            {
                "id": execution.id,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "status": execution.status,
                "error_message": execution.error_message,
                "statistics": execution.statistics
            }
            for execution in executions
        ]
    
    return response

@router.put("/{job_id}", summary="Update job")
async def update_job(
    job_id: str,
    job_request: JobRequest,
    db: DatabaseSession,
    user: CurrentUser
) -> JobResponse:
    """Update an existing job."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update running job"
        )
    
    # Update job
    job_service = JobSchedulerService(db)
    updated_job = await job_service.update_job(
        job_id=job_id,
        name=job_request.name,
        description=job_request.description,
        priority=job_request.priority,
        config=job_request.config,
        tags=job_request.tags or [],
        schedule=job_request.schedule.dict() if job_request.schedule else None,
        notifications=job_request.notifications
    )
    
    return JobResponse(
        id=updated_job.id,
        name=updated_job.name,
        description=updated_job.description,
        type=updated_job.type,
        status=updated_job.status,
        priority=updated_job.priority,
        tags=updated_job.tags or [],
        created_at=updated_job.created_at,
        updated_at=updated_job.updated_at,
        started_at=updated_job.started_at,
        completed_at=updated_job.completed_at,
        progress=updated_job.progress or {},
        statistics=updated_job.statistics or {},
        error_message=updated_job.error_message,
        config=updated_job.config,
        schedule=ScheduleConfig(**updated_job.schedule) if updated_job.schedule else None
    )

@router.post("/{job_id}/start", summary="Start job")
async def start_job(
    job_id: str,
    db: DatabaseSession,
    user: CurrentUser,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """Start a pending or paused job."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status not in [JobStatus.PENDING, JobStatus.PAUSED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start job with status: {job.status}"
        )
    
    # Queue job for execution
    job_service = JobSchedulerService(db)
    background_tasks.add_task(
        job_service.queue_job,
        job_id
    )
    
    return {"message": "Job queued for execution"}

@router.post("/{job_id}/pause", summary="Pause job")
async def pause_job(
    job_id: str,
    db: DatabaseSession,
    user: CurrentUser
) -> Dict[str, str]:
    """Pause a running job."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only pause running jobs"
        )
    
    # Pause job
    job_service = JobSchedulerService(db)
    await job_service.pause_job(job_id)
    
    return {"message": "Job paused successfully"}

@router.post("/{job_id}/cancel", summary="Cancel job")
async def cancel_job(
    job_id: str,
    db: DatabaseSession,
    user: CurrentUser
) -> Dict[str, str]:
    """Cancel a job."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Cancel job
    job_service = JobSchedulerService(db)
    await job_service.cancel_job(job_id)
    
    return {"message": "Job cancelled successfully"}

@router.delete("/{job_id}", summary="Delete job")
async def delete_job(
    job_id: str,
    db: DatabaseSession,
    user: CurrentUser
) -> Dict[str, str]:
    """Delete a job and its data."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete running job. Cancel it first."
        )
    
    # Delete job
    job_service = JobSchedulerService(db)
    await job_service.delete_job(job_id)
    
    return {"message": "Job deleted successfully"}

@router.get("/{job_id}/logs", summary="Get job logs")
async def get_job_logs(
    job_id: str,
    db: DatabaseSession,
    user: CurrentUser,
    pagination: PaginationDep,
    level: Optional[str] = Query(None, description="Filter by log level")
) -> Dict[str, Any]:
    """Get job execution logs."""
    job = (
        db.query(CrawlJob)
        .filter(CrawlJob.id == job_id, CrawlJob.user_id == user.id)
        .first()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job_service = JobSchedulerService(db)
    logs = await job_service.get_job_logs(
        job_id=job_id,
        page=pagination.page,
        size=pagination.size,
        level=level
    )
    
    return logs
