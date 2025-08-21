"""
API v1 router configuration.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional

from src.webapp.api.v1.endpoints import scraping, templates, exports, jobs
from src.webapp.dependencies import get_current_user, get_db_session

api_router = APIRouter(prefix="/v1")

# Include endpoint routers
api_router.include_router(
    scraping.router,
    prefix="/scraping",
    tags=["scraping"]
)

api_router.include_router(
    templates.router,
    prefix="/templates", 
    tags=["templates"]
)

api_router.include_router(
    exports.router,
    prefix="/exports",
    tags=["exports"]
)

api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["jobs"]
)


@api_router.get("/")
async def api_info():
    """Get API information."""
    return {
        "name": "Scraping Platform API",
        "version": "1.0.0",
        "description": "Advanced web scraping and data extraction platform",
        "endpoints": [
            "/scraping",
            "/templates", 
            "/exports",
            "/jobs"
        ]
    }
