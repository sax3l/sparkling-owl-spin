"""
Lovable Backend API Router

Main API routes and endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from .auth import get_current_user
from .models import User


router = APIRouter()


@router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "Lovable Backend API v1",
        "endpoints": {
            "users": "/users",
            "projects": "/projects",
            "templates": "/templates",
            "jobs": "/jobs"
        }
    }


@router.get("/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at
    }


@router.get("/projects")
async def get_projects(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's projects."""
    # Stub implementation
    return {
        "projects": [],
        "total": 0,
        "user_id": current_user.id
    }


@router.get("/templates")
async def get_templates(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get available templates."""
    # Stub implementation
    return {
        "templates": [
            {
                "id": "template_1",
                "name": "Basic Template",
                "description": "A basic template for getting started",
                "created_at": "2025-08-22T00:00:00Z"
            }
        ],
        "total": 1
    }


@router.get("/jobs")
async def get_jobs(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get user's jobs."""
    # Stub implementation
    return {
        "jobs": [],
        "total": 0,
        "user_id": current_user.id
    }


@router.post("/jobs")
async def create_job(
    job_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new job."""
    # Stub implementation
    return {
        "id": "job_123",
        "status": "created",
        "user_id": current_user.id,
        "created_at": "2025-08-22T00:00:00Z"
    }
