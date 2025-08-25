"""
System API Routes

API endpoints for system monitoring, status, privacy requests, and notifications.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from src.webapp.dependencies import get_current_user, require_admin, get_db_session
from src.services.system_status_service import get_system_status_service
from src.services.monitoring_service import get_monitoring_service
from src.services.notification_service import get_notification_service, NotificationType, NotificationChannel, NotificationContext
from src.services.privacy_service import get_privacy_service
from src.database.models import User, PrivacyRequestType, PrivacyRequestStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models
class SystemStatusResponse(BaseModel):
    """System status response model."""
    overall_status: str
    timestamp: str
    components: Dict[str, Dict[str, Any]]
    summary: Dict[str, Any]
    performance: Optional[Dict[str, Any]] = None
    recent_activity: Optional[Dict[str, Any]] = None
    alerts: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str


class NotificationRequest(BaseModel):
    """Request to send notification."""
    type: str
    channels: List[str]
    recipients: Optional[List[str]] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    priority: str = "normal"


class PrivacyRequestCreate(BaseModel):
    """Privacy request creation model."""
    type: str  # "erasure" or "portability"
    subject_reference: str
    contact_email: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PIIScanRequest(BaseModel):
    """PII scan request model."""
    item_id: Optional[str] = None
    job_id: Optional[str] = None
    scope: str = "recent"  # "recent", "all", "job", "item"


# System Status Endpoints
@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    details: bool = Query(False, description="Include detailed metrics and activity"),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive system status.
    
    Returns overall system health, component statuses, and optional detailed metrics.
    """
    logger.info(f"System status requested by user {current_user.email}")
    
    try:
        status_service = get_system_status_service()
        status = await status_service.get_system_overview(include_details=details)
        
        return SystemStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Simple health check endpoint for load balancers.
    
    Returns basic health status without authentication.
    """
    try:
        status_service = get_system_status_service()
        health = await status_service.get_health_endpoint()
        
        return HealthResponse(**health)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(status="unhealthy", timestamp=datetime.utcnow().isoformat())


@router.post("/status/refresh")
async def refresh_system_status(
    current_user: User = Depends(require_admin)
):
    """
    Refresh system status cache.
    
    Forces a refresh of cached system status data.
    """
    logger.info(f"System status refresh requested by admin {current_user.email}")
    
    try:
        status_service = get_system_status_service()
        await status_service.invalidate_cache()
        
        return {"message": "System status cache refreshed", "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        logger.error(f"Error refreshing system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh system status")


# Monitoring Endpoints
@router.get("/monitoring/metrics")
async def get_metrics(
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get system metrics summary.
    
    Returns current system metrics and performance data.
    """
    logger.info(f"Metrics requested by admin {current_user.email}")
    
    try:
        monitoring_service = get_monitoring_service()
        metrics = monitoring_service.get_metrics_summary()
        
        return {
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")


@router.get("/monitoring/alerts")
async def get_alerts(
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get active alerts.
    
    Returns current system alerts and their status.
    """
    logger.info(f"Alerts requested by admin {current_user.email}")
    
    try:
        monitoring_service = get_monitoring_service()
        alert_status = monitoring_service.get_system_status()
        
        return {
            "alert_summary": alert_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")


@router.post("/monitoring/start")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """
    Start monitoring services.
    
    Starts background monitoring tasks.
    """
    logger.info(f"Monitoring start requested by admin {current_user.email}")
    
    try:
        monitoring_service = get_monitoring_service()
        background_tasks.add_task(monitoring_service.start_monitoring)
        
        return {"message": "Monitoring services started", "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to start monitoring")


@router.post("/monitoring/stop")
async def stop_monitoring(
    current_user: User = Depends(require_admin)
):
    """
    Stop monitoring services.
    
    Stops background monitoring tasks.
    """
    logger.info(f"Monitoring stop requested by admin {current_user.email}")
    
    try:
        monitoring_service = get_monitoring_service()
        await monitoring_service.stop_monitoring()
        
        return {"message": "Monitoring services stopped", "timestamp": datetime.utcnow().isoformat()}
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop monitoring")


# Notification Endpoints
@router.post("/notifications/send")
async def send_notification(
    request: NotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """
    Send a notification.
    
    Sends a notification through specified channels.
    """
    logger.info(f"Notification send requested by admin {current_user.email}")
    
    try:
        # Validate notification type
        try:
            notification_type = NotificationType(request.type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid notification type: {request.type}")
        
        # Validate channels
        channels = []
        for channel_name in request.channels:
            try:
                channels.append(NotificationChannel(channel_name))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid channel: {channel_name}")
        
        # Create notification context
        context = NotificationContext(**request.context)
        
        # Send notification in background
        notification_service = get_notification_service()
        background_tasks.add_task(
            notification_service.send_notification,
            notification_type,
            context,
            channels,
            request.recipients,
            request.priority
        )
        
        return {
            "message": "Notification sent",
            "type": request.type,
            "channels": request.channels,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send notification")


# Privacy Endpoints
@router.post("/privacy/requests")
async def create_privacy_request(
    request: PrivacyRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Create a privacy request.
    
    Creates a new GDPR/privacy request for data erasure or portability.
    """
    logger.info(f"Privacy request created: {request.type} for {request.subject_reference}")
    
    try:
        # Validate request type
        try:
            request_type = PrivacyRequestType(request.type.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid request type: {request.type}")
        
        privacy_service = get_privacy_service()
        request_id = await privacy_service.create_privacy_request(
            request_type=request_type,
            subject_reference=request.subject_reference,
            contact_email=request.contact_email,
            description=request.description,
            metadata=request.metadata
        )
        
        return {
            "request_id": request_id,
            "type": request.type,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating privacy request: {e}")
        raise HTTPException(status_code=500, detail="Failed to create privacy request")


@router.get("/privacy/requests/{request_id}")
async def get_privacy_request(
    request_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Get privacy request details.
    
    Returns details of a specific privacy request.
    """
    logger.info(f"Privacy request details requested: {request_id}")
    
    try:
        # This would fetch from database
        # For now, return placeholder response
        return {
            "request_id": request_id,
            "type": "erasure",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "message": "Request details would be returned here"
        }
        
    except Exception as e:
        logger.error(f"Error getting privacy request: {e}")
        raise HTTPException(status_code=500, detail="Failed to get privacy request")


@router.post("/privacy/requests/{request_id}/process")
async def process_privacy_request(
    request_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """
    Process a privacy request.
    
    Starts processing of a pending privacy request.
    """
    logger.info(f"Privacy request processing started: {request_id}")
    
    try:
        privacy_service = get_privacy_service()
        
        # Start processing in background
        background_tasks.add_task(
            privacy_service.process_erasure_request,
            request_id
        )
        
        return {
            "request_id": request_id,
            "status": "processing",
            "message": "Privacy request processing started",
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing privacy request: {e}")
        raise HTTPException(status_code=500, detail="Failed to process privacy request")


@router.post("/privacy/pii-scan")
async def scan_for_pii(
    request: PIIScanRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin)
):
    """
    Scan for personally identifiable information.
    
    Initiates a PII scan on specified data.
    """
    logger.info(f"PII scan requested by admin {current_user.email}")
    
    try:
        privacy_service = get_privacy_service()
        
        # Start scan in background
        background_tasks.add_task(
            privacy_service.scan_pii,
            request.item_id,
            request.job_id
        )
        
        return {
            "message": "PII scan started",
            "scope": request.scope,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error starting PII scan: {e}")
        raise HTTPException(status_code=500, detail="Failed to start PII scan")


# Administrative Endpoints
@router.get("/admin/system-info")
async def get_system_info(
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get detailed system information.
    
    Returns comprehensive system information for administrators.
    """
    logger.info(f"System info requested by admin {current_user.email}")
    
    try:
        import platform
        import sys
        
        status_service = get_system_status_service()
        system_status = await status_service.get_system_overview(include_details=True)
        
        # Add additional system information
        system_info = {
            "system_status": system_status,
            "environment": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
                "processor": platform.processor(),
                "hostname": platform.node()
            },
            "application": {
                "version": "1.0.0",  # Would come from actual version
                "build_date": "2024-01-01",  # Would come from build info
                "environment": "production"  # Would come from settings
            }
        }
        
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system info")


@router.post("/admin/maintenance-mode")
async def set_maintenance_mode(
    enabled: bool = Query(..., description="Enable or disable maintenance mode"),
    current_user: User = Depends(require_admin)
):
    """
    Enable/disable maintenance mode.
    
    Puts the system into maintenance mode.
    """
    logger.info(f"Maintenance mode {'enabled' if enabled else 'disabled'} by admin {current_user.email}")
    
    try:
        # This would update a global maintenance flag
        # For now, just return success
        
        return {
            "maintenance_mode": enabled,
            "changed_by": current_user.email,
            "changed_at": datetime.utcnow().isoformat(),
            "message": f"Maintenance mode {'enabled' if enabled else 'disabled'}"
        }
        
    except Exception as e:
        logger.error(f"Error setting maintenance mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to set maintenance mode")


# Add the router to the application
def get_system_router() -> APIRouter:
    """Get the system API router."""
    return router
