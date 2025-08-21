"""
Web views for the crawler admin interface.

Provides HTML templates and server-side rendering for:
- Dashboard with real-time metrics
- Job management interface
- Configuration management
- System health monitoring
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Dict, List, Optional, Any
import json
from datetime import datetime, timedelta

from src.webapp.auth import get_current_user, User
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize router and templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    """Main dashboard view with system overview."""
    try:
        # Get system metrics for dashboard
        metrics = await get_dashboard_metrics()
        
        context = {
            "request": request,
            "user": current_user,
            "metrics": metrics,
            "page_title": "Crawler Dashboard",
            "active_page": "dashboard"
        }
        
        return templates.TemplateResponse("dashboard.html", context)
        
    except Exception as e:
        logger.error(f"Dashboard view error: {e}")
        raise HTTPException(status_code=500, detail="Dashboard unavailable")

@router.get("/jobs", response_class=HTMLResponse)
async def jobs_view(request: Request, current_user: User = Depends(get_current_user)):
    """Jobs management interface."""
    try:
        # Get active and recent jobs
        jobs_data = await get_jobs_data()
        
        context = {
            "request": request,
            "user": current_user,
            "jobs": jobs_data,
            "page_title": "Job Management",
            "active_page": "jobs"
        }
        
        return templates.TemplateResponse("jobs.html", context)
        
    except Exception as e:
        logger.error(f"Jobs view error: {e}")
        raise HTTPException(status_code=500, detail="Jobs view unavailable")

@router.get("/proxy-pool", response_class=HTMLResponse)
async def proxy_pool_view(request: Request, current_user: User = Depends(get_current_user)):
    """Proxy pool management interface."""
    try:
        # Get proxy pool status and statistics
        proxy_data = await get_proxy_pool_data()
        
        context = {
            "request": request,
            "user": current_user,
            "proxy_data": proxy_data,
            "page_title": "Proxy Pool Management",
            "active_page": "proxy-pool"
        }
        
        return templates.TemplateResponse("proxy_pool.html", context)
        
    except Exception as e:
        logger.error(f"Proxy pool view error: {e}")
        raise HTTPException(status_code=500, detail="Proxy pool view unavailable")

@router.get("/config", response_class=HTMLResponse)
async def config_view(request: Request, current_user: User = Depends(get_current_user)):
    """Configuration management interface."""
    try:
        # Get current configuration
        config_data = await get_configuration_data()
        
        context = {
            "request": request,
            "user": current_user,
            "config": config_data,
            "page_title": "Configuration",
            "active_page": "config"
        }
        
        return templates.TemplateResponse("config.html", context)
        
    except Exception as e:
        logger.error(f"Config view error: {e}")
        raise HTTPException(status_code=500, detail="Configuration view unavailable")

@router.get("/monitoring", response_class=HTMLResponse)
async def monitoring_view(request: Request, current_user: User = Depends(get_current_user)):
    """System monitoring interface with real-time metrics."""
    try:
        # Get monitoring data
        monitoring_data = await get_monitoring_data()
        
        context = {
            "request": request,
            "user": current_user,
            "monitoring": monitoring_data,
            "page_title": "System Monitoring",
            "active_page": "monitoring"
        }
        
        return templates.TemplateResponse("monitoring.html", context)
        
    except Exception as e:
        logger.error(f"Monitoring view error: {e}")
        raise HTTPException(status_code=500, detail="Monitoring view unavailable")

@router.get("/templates", response_class=HTMLResponse)
async def templates_view(request: Request, current_user: User = Depends(get_current_user)):
    """Template management interface for scraping templates."""
    try:
        # Get scraping templates
        templates_data = await get_templates_data()
        
        context = {
            "request": request,
            "user": current_user,
            "scraping_templates": templates_data,
            "page_title": "Scraping Templates",
            "active_page": "templates"
        }
        
        return templates.TemplateResponse("scraping_templates.html", context)
        
    except Exception as e:
        logger.error(f"Templates view error: {e}")
        raise HTTPException(status_code=500, detail="Templates view unavailable")

@router.get("/exports", response_class=HTMLResponse)
async def exports_view(request: Request, current_user: User = Depends(get_current_user)):
    """Data exports management interface."""
    try:
        # Get export history and status
        exports_data = await get_exports_data()
        
        context = {
            "request": request,
            "user": current_user,
            "exports": exports_data,
            "page_title": "Data Exports",
            "active_page": "exports"
        }
        
        return templates.TemplateResponse("exports.html", context)
        
    except Exception as e:
        logger.error(f"Exports view error: {e}")
        raise HTTPException(status_code=500, detail="Exports view unavailable")

@router.get("/logs", response_class=HTMLResponse)
async def logs_view(request: Request, current_user: User = Depends(get_current_user)):
    """System logs viewer interface."""
    try:
        # Get recent logs
        logs_data = await get_logs_data()
        
        context = {
            "request": request,
            "user": current_user,
            "logs": logs_data,
            "page_title": "System Logs",
            "active_page": "logs"
        }
        
        return templates.TemplateResponse("logs.html", context)
        
    except Exception as e:
        logger.error(f"Logs view error: {e}")
        raise HTTPException(status_code=500, detail="Logs view unavailable")

# Helper functions to fetch data for views

async def get_dashboard_metrics() -> Dict[str, Any]:
    """Get dashboard metrics data."""
    # In a real implementation, this would fetch from database/cache
    return {
        "active_jobs": 5,
        "completed_jobs_today": 23,
        "failed_jobs_today": 2,
        "proxy_pool_size": 150,
        "active_proxies": 142,
        "data_points_scraped_today": 1543,
        "system_status": "healthy",
        "last_update": datetime.utcnow().isoformat(),
        "performance_metrics": {
            "avg_response_time": 1.2,
            "success_rate": 96.5,
            "proxy_rotation_rate": 0.8
        }
    }

async def get_jobs_data() -> Dict[str, Any]:
    """Get jobs data for management interface."""
    return {
        "active_jobs": [
            {
                "id": "job_001",
                "name": "Daily Vehicle Data Scrape",
                "status": "running",
                "progress": 65,
                "started_at": "2024-01-15T10:30:00Z",
                "estimated_completion": "2024-01-15T12:30:00Z"
            },
            {
                "id": "job_002", 
                "name": "Company Profiles Update",
                "status": "queued",
                "progress": 0,
                "scheduled_for": "2024-01-15T14:00:00Z"
            }
        ],
        "recent_completed": [
            {
                "id": "job_003",
                "name": "Weekly Person Data Export",
                "status": "completed",
                "completed_at": "2024-01-15T09:45:00Z",
                "duration": "2h 15m",
                "records_processed": 15420
            }
        ],
        "failed_jobs": [
            {
                "id": "job_004",
                "name": "Failed Template Test",
                "status": "failed",
                "failed_at": "2024-01-15T08:20:00Z",
                "error": "Template validation failed"
            }
        ]
    }

async def get_proxy_pool_data() -> Dict[str, Any]:
    """Get proxy pool data for management interface."""
    return {
        "summary": {
            "total_proxies": 150,
            "active_proxies": 142,
            "failed_proxies": 5,
            "testing_proxies": 3,
            "average_response_time": 1.2,
            "success_rate": 96.5
        },
        "by_country": {
            "US": 45,
            "DE": 32,
            "UK": 28,
            "FR": 25,
            "Others": 20
        },
        "recent_activity": [
            {
                "timestamp": "2024-01-15T11:45:00Z",
                "action": "proxy_added",
                "proxy": "198.51.100.45:8080",
                "country": "US"
            },
            {
                "timestamp": "2024-01-15T11:40:00Z",
                "action": "proxy_failed",
                "proxy": "203.0.113.22:3128",
                "reason": "timeout"
            }
        ]
    }

async def get_configuration_data() -> Dict[str, Any]:
    """Get configuration data for management interface."""
    return {
        "anti_bot": {
            "delay_range": [2000, 5000],
            "user_agent_rotation": True,
            "header_randomization": True,
            "stealth_mode": True
        },
        "proxy_pool": {
            "min_pool_size": 50,
            "max_pool_size": 200,
            "health_check_interval": 300,
            "retry_failed_after": 3600
        },
        "scraper": {
            "max_concurrent_jobs": 10,
            "request_timeout": 30,
            "retry_attempts": 3,
            "respect_robots_txt": True
        },
        "database": {
            "connection_pool_size": 20,
            "query_timeout": 30,
            "backup_enabled": True,
            "backup_interval": "daily"
        }
    }

async def get_monitoring_data() -> Dict[str, Any]:
    """Get monitoring data for system health interface."""
    return {
        "system_health": {
            "status": "healthy",
            "uptime": "5d 14h 32m",
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 23.1
        },
        "performance_metrics": {
            "requests_per_minute": 125,
            "average_response_time": 1.2,
            "error_rate": 3.5,
            "proxy_success_rate": 96.5
        },
        "alerts": [
            {
                "level": "warning",
                "message": "High memory usage detected",
                "timestamp": "2024-01-15T11:30:00Z"
            }
        ],
        "recent_errors": [
            {
                "timestamp": "2024-01-15T11:28:00Z",
                "level": "error",
                "message": "Proxy timeout: 198.51.100.22:8080",
                "component": "proxy_pool"
            }
        ]
    }

async def get_templates_data() -> Dict[str, Any]:
    """Get scraping templates data."""
    return {
        "templates": [
            {
                "id": "vehicle_template_v1",
                "name": "Vehicle Details Template V1",
                "version": "1.0",
                "sites": ["biluppgifter.se", "car.info"],
                "status": "active",
                "success_rate": 98.2,
                "last_updated": "2024-01-10T15:20:00Z"
            },
            {
                "id": "company_template_v2",
                "name": "Company Profile Template V2", 
                "version": "2.0",
                "sites": ["hitta.se"],
                "status": "testing",
                "success_rate": 85.1,
                "last_updated": "2024-01-15T09:15:00Z"
            }
        ],
        "drift_alerts": [
            {
                "template": "person_profile_v1",
                "site": "example.se",
                "drift_score": 0.75,
                "detected_at": "2024-01-15T10:45:00Z"
            }
        ]
    }

async def get_exports_data() -> Dict[str, Any]:
    """Get exports data for management interface."""
    return {
        "recent_exports": [
            {
                "id": "export_001",
                "name": "Vehicle Data Export",
                "format": "CSV",
                "records": 15420,
                "status": "completed",
                "created_at": "2024-01-15T09:00:00Z",
                "file_size": "2.3 MB"
            },
            {
                "id": "export_002",
                "name": "Company Profiles",
                "format": "JSON",
                "records": 8750,
                "status": "in_progress",
                "progress": 45,
                "created_at": "2024-01-15T11:30:00Z"
            }
        ],
        "export_stats": {
            "total_exports_this_month": 45,
            "total_records_exported": 125000,
            "most_popular_format": "CSV",
            "average_export_size": "1.8 MB"
        }
    }

async def get_logs_data() -> Dict[str, Any]:
    """Get logs data for viewer interface."""
    return {
        "recent_logs": [
            {
                "timestamp": "2024-01-15T11:45:23Z",
                "level": "INFO",
                "component": "scheduler",
                "message": "Job job_001 started successfully"
            },
            {
                "timestamp": "2024-01-15T11:44:15Z",
                "level": "WARNING",
                "component": "proxy_pool",
                "message": "Proxy 198.51.100.22:8080 failed health check"
            },
            {
                "timestamp": "2024-01-15T11:43:02Z",
                "level": "ERROR",
                "component": "scraper",
                "message": "Template validation failed for site example.com"
            }
        ],
        "log_stats": {
            "total_logs_today": 1542,
            "error_count": 23,
            "warning_count": 87,
            "info_count": 1432
        }
    }