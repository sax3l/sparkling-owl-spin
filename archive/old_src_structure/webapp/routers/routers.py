"""
Lovable Backend Routers

API route handlers and endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from .database import get_db
from .dependencies import (
    get_current_active_user, 
    get_current_admin_user,
    get_user_or_api_key,
    rate_limit_normal,
    log_request
)
from .models import (
    UserInDB, UserCreate, UserUpdate, UserResponse,
    ProjectInDB, ProjectCreate, ProjectUpdate, ProjectResponse,
    TemplateInDB, TemplateCreate, TemplateUpdate, TemplateResponse,
    JobInDB, JobCreate, JobUpdate, JobResponse
)
from .services import (
    UserService, 
    ProjectService, 
    TemplateService, 
    JobService,
    AuditService
)

# User router
user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None,
    _: None = Depends(rate_limit_normal)
):
    """Create a new user."""
    db_user = UserService.create_user(db, user)
    
    # Log user creation
    if request:
        AuditService.log_action(
            db=db,
            action="user_created",
            resource_type="user",
            resource_id=str(db_user.id),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    
    return UserResponse.from_orm(db_user)


@user_router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@user_router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user."""
    updated_user = UserService.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(updated_user)


@user_router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: UserInDB = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)."""
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)


# Project router
project_router = APIRouter(prefix="/projects", tags=["projects"])


@project_router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_normal)
):
    """Create a new project."""
    db_project = ProjectService.create_project(db, project, current_user.id)
    return ProjectResponse.from_orm(db_project)


@project_router.get("/", response_model=List[ProjectResponse])
async def read_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Get user's projects."""
    projects = ProjectService.get_user_projects(db, current_user.id, skip, limit)
    return [ProjectResponse.from_orm(p) for p in projects]


@project_router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(
    project_id: int,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Get project by ID."""
    project = ProjectService.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return ProjectResponse.from_orm(project)


@project_router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Update project."""
    updated_project = ProjectService.update_project(db, project_id, project_update, current_user.id)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    return ProjectResponse.from_orm(updated_project)


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Delete project."""
    success = ProjectService.delete_project(db, project_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


# Template router
template_router = APIRouter(prefix="/templates", tags=["templates"])


@template_router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: TemplateCreate,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_normal)
):
    """Create a new template."""
    db_template = TemplateService.create_template(db, template, current_user.id)
    return TemplateResponse.from_orm(db_template)


@template_router.get("/", response_model=List[TemplateResponse])
async def read_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    my_only: bool = Query(False),
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Get templates."""
    if my_only:
        templates = TemplateService.get_user_templates(db, current_user.id, skip, limit)
    else:
        templates = TemplateService.get_public_templates(db, skip, limit)
    return [TemplateResponse.from_orm(t) for t in templates]


@template_router.get("/{template_id}", response_model=TemplateResponse)
async def read_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get template by ID."""
    template = TemplateService.get_template(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return TemplateResponse.from_orm(template)


# Job router
job_router = APIRouter(prefix="/jobs", tags=["jobs"])


@job_router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_normal)
):
    """Create a new job."""
    db_job = JobService.create_job(db, job, current_user.id)
    return JobResponse.from_orm(db_job)


@job_router.get("/", response_model=List[JobResponse])
async def read_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Get user's jobs."""
    jobs = JobService.get_user_jobs(db, current_user.id, skip, limit)
    return [JobResponse.from_orm(j) for j in jobs]


@job_router.get("/{job_id}", response_model=JobResponse)
async def read_job(
    job_id: int,
    current_user: UserInDB = Depends(get_user_or_api_key),
    db: Session = Depends(get_db)
):
    """Get job by ID."""
    job = JobService.get_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return JobResponse.from_orm(job)


@job_router.patch("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    job_id: int,
    status: str,
    result: Optional[dict] = None,
    error: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update job status (admin only)."""
    updated_job = JobService.update_job_status(db, job_id, status, result, error)
    if not updated_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return JobResponse.from_orm(updated_job)


# Health router
health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lovable-backend"}


@health_router.get("/db")
async def database_health_check(db: Session = Depends(get_db)):
    """Database health check."""
    try:
        # Simple query to check database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )
