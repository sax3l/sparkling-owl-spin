"""
Lovable Backend API

Main API router with all endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.manager import get_db
from .routers.api_routers import (
    user_router,
    project_router,  
    template_router,
    job_router,
    health_router
)
from .auth import auth_router

# Main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(project_router)
api_router.include_router(template_router)
api_router.include_router(job_router)
api_router.include_router(health_router)


@api_router.get("/")
async def root():
    """Root API endpoint."""
    return {
        "service": "lovable-backend",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "projects": "/api/v1/projects",
            "templates": "/api/v1/templates",
            "jobs": "/api/v1/jobs",
            "health": "/api/v1/health"
        }
    }
