"""
Router for privacy and data protection operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import get_db
from ..models import User, CrawlJob, ScrapeJob
from ..schemas.common import StatusResponse, PaginatedResponse
from ..dependencies import get_current_user, require_permissions
from ..services.privacy_service import PrivacyService
from ..utils.rate_limiting import rate_limit
from pydantic import BaseModel, Field

router = APIRouter(prefix="/privacy", tags=["privacy"])


class DataDeletionRequest(BaseModel):
    """Schema for data deletion requests."""
    reason: str = Field(..., max_length=500, description="Reason for deletion")
    data_types: List[str] = Field(..., description="Types of data to delete")
    confirm: bool = Field(..., description="Confirmation of deletion")


class DataExportRequest(BaseModel):
    """Schema for personal data export requests."""
    include_jobs: bool = Field(True, description="Include job data")
    include_results: bool = Field(True, description="Include job results")
    include_logs: bool = Field(False, description="Include system logs")
    format: str = Field("json", description="Export format")


class ConsentUpdate(BaseModel):
    """Schema for updating user consent."""
    analytics: bool = Field(..., description="Analytics consent")
    marketing: bool = Field(..., description="Marketing consent")  
    data_processing: bool = Field(..., description="Data processing consent")
    third_party_sharing: bool = Field(..., description="Third-party sharing consent")


class PrivacySettings(BaseModel):
    """Schema for privacy settings."""
    data_retention_days: int = Field(365, ge=30, le=2555, description="Data retention period")
    auto_delete_failed_jobs: bool = Field(False, description="Auto-delete failed jobs")
    anonymize_ip_addresses: bool = Field(True, description="Anonymize IP addresses")
    minimal_logging: bool = Field(False, description="Use minimal logging")


@router.post("/delete-account", response_model=StatusResponse)
@rate_limit(requests=1, window=86400)  # Once per day
async def request_account_deletion(
    request: DataDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Request complete account and data deletion."""
    
    if not request.confirm:
        raise HTTPException(
            status_code=400,
            detail="Account deletion must be confirmed"
        )
    
    privacy_service = PrivacyService(db)
    
    # Create deletion request
    deletion_request = await privacy_service.create_deletion_request(
        user_id=str(current_user.id),
        reason=request.reason,
        data_types=request.data_types
    )
    
    # Schedule background deletion (with grace period)
    background_tasks.add_task(
        privacy_service.schedule_account_deletion,
        deletion_request.id,
        grace_period_hours=72  # 72 hour grace period
    )
    
    return StatusResponse(
        success=True,
        message="Account deletion scheduled. You have 72 hours to cancel this request.",
        data={"deletion_id": deletion_request.id}
    )


@router.post("/cancel-deletion", response_model=StatusResponse)
async def cancel_account_deletion(
    deletion_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a pending account deletion request."""
    
    privacy_service = PrivacyService(db)
    success = await privacy_service.cancel_deletion_request(
        deletion_id,
        str(current_user.id)
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Deletion request not found or cannot be cancelled"
        )
    
    return StatusResponse(
        success=True,
        message="Account deletion cancelled successfully"
    )


@router.post("/export-data", response_model=StatusResponse)
@rate_limit(requests=3, window=86400)  # 3 exports per day
async def export_personal_data(
    request: DataExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Export all personal data (GDPR compliance)."""
    
    privacy_service = PrivacyService(db)
    
    # Create export task
    export_task = await privacy_service.create_data_export_task(
        user_id=str(current_user.id),
        include_jobs=request.include_jobs,
        include_results=request.include_results,
        include_logs=request.include_logs,
        format=request.format
    )
    
    # Process export in background
    background_tasks.add_task(
        privacy_service.process_data_export,
        export_task.id
    )
    
    return StatusResponse(
        success=True,
        message="Data export started. You will receive an email when ready.",
        data={"export_id": export_task.id}
    )


@router.get("/export-status/{export_id}")
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get status of data export request."""
    
    privacy_service = PrivacyService(db)
    export_task = await privacy_service.get_export_task(
        export_id,
        str(current_user.id)
    )
    
    if not export_task:
        raise HTTPException(status_code=404, detail="Export task not found")
    
    return {
        "export_id": export_task.id,
        "status": export_task.status,
        "created_at": export_task.created_at,
        "completed_at": export_task.completed_at,
        "download_url": export_task.download_url,
        "expires_at": export_task.expires_at,
        "file_size": export_task.file_size
    }


@router.put("/consent", response_model=StatusResponse)
async def update_consent(
    consent: ConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user consent preferences."""
    
    privacy_service = PrivacyService(db)
    await privacy_service.update_user_consent(
        str(current_user.id),
        consent.dict()
    )
    
    return StatusResponse(
        success=True,
        message="Consent preferences updated successfully"
    )


@router.get("/consent")
async def get_consent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user consent preferences."""
    
    privacy_service = PrivacyService(db)
    consent = await privacy_service.get_user_consent(str(current_user.id))
    
    return consent


@router.put("/settings", response_model=StatusResponse)
async def update_privacy_settings(
    settings: PrivacySettings,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update privacy settings."""
    
    privacy_service = PrivacyService(db)
    await privacy_service.update_privacy_settings(
        str(current_user.id),
        settings.dict()
    )
    
    return StatusResponse(
        success=True,
        message="Privacy settings updated successfully"
    )


@router.get("/settings")
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current privacy settings."""
    
    privacy_service = PrivacyService(db)
    settings = await privacy_service.get_privacy_settings(str(current_user.id))
    
    return settings


@router.post("/anonymize-data", response_model=StatusResponse)
@rate_limit(requests=1, window=3600)  # Once per hour
async def anonymize_user_data(
    job_ids: Optional[List[str]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Anonymize user data while preserving functionality."""
    
    privacy_service = PrivacyService(db)
    
    # Start anonymization process
    background_tasks.add_task(
        privacy_service.anonymize_user_data,
        str(current_user.id),
        job_ids
    )
    
    return StatusResponse(
        success=True,
        message="Data anonymization started"
    )


@router.delete("/job-data/{job_id}", response_model=StatusResponse)
async def delete_job_data(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all data for a specific job."""
    
    # Check if user owns the job
    crawl_job = db.query(CrawlJob).filter(
        and_(CrawlJob.id == job_id, CrawlJob.user_id == current_user.id)
    ).first()
    
    scrape_job = db.query(ScrapeJob).filter(
        and_(ScrapeJob.id == job_id, ScrapeJob.user_id == current_user.id)
    ).first()
    
    if not crawl_job and not scrape_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    privacy_service = PrivacyService(db)
    await privacy_service.delete_job_data(job_id)
    
    return StatusResponse(
        success=True,
        message="Job data deleted successfully"
    )


@router.post("/forget-data", response_model=StatusResponse)
@rate_limit(requests=5, window=86400)  # 5 requests per day
async def request_data_forgetting(
    data_categories: List[str],
    reason: str = Field(..., max_length=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Request forgetting of specific data categories (Right to be forgotten)."""
    
    valid_categories = [
        "personal_info", "job_history", "api_usage", 
        "search_history", "preferences", "logs"
    ]
    
    invalid_categories = [cat for cat in data_categories if cat not in valid_categories]
    if invalid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data categories: {invalid_categories}"
        )
    
    privacy_service = PrivacyService(db)
    
    # Create forgetting request
    forget_request = await privacy_service.create_forget_request(
        user_id=str(current_user.id),
        data_categories=data_categories,
        reason=reason
    )
    
    # Process in background
    background_tasks.add_task(
        privacy_service.process_forget_request,
        forget_request.id
    )
    
    return StatusResponse(
        success=True,
        message="Data forgetting request submitted",
        data={"request_id": forget_request.id}
    )


@router.get("/audit-log")
async def get_privacy_audit_log(
    limit: int = Query(50, le=100, description="Number of entries"),
    offset: int = Query(0, ge=0, description="Offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get privacy-related audit log for user."""
    
    privacy_service = PrivacyService(db)
    audit_entries = await privacy_service.get_user_audit_log(
        str(current_user.id),
        limit=limit,
        offset=offset
    )
    
    return {
        "entries": audit_entries,
        "limit": limit,
        "offset": offset
    }


@router.get("/data-summary")
async def get_data_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary of user's data across the system."""
    
    privacy_service = PrivacyService(db)
    summary = await privacy_service.get_user_data_summary(str(current_user.id))
    
    return summary


@router.post("/rectification", response_model=StatusResponse)
async def request_data_rectification(
    corrections: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Request correction of inaccurate personal data."""
    
    privacy_service = PrivacyService(db)
    
    # Create rectification request
    rectification_request = await privacy_service.create_rectification_request(
        user_id=str(current_user.id),
        corrections=corrections
    )
    
    # Process in background
    background_tasks.add_task(
        privacy_service.process_rectification_request,
        rectification_request.id
    )
    
    return StatusResponse(
        success=True,
        message="Data rectification request submitted",
        data={"request_id": rectification_request.id}
    )


@router.get("/legal-basis")
async def get_legal_basis(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get information about legal basis for data processing."""
    
    return {
        "personal_data": {
            "legal_basis": "consent",
            "purpose": "User account management and service provision",
            "retention_period": "Until account deletion",
            "third_party_sharing": False
        },
        "job_data": {
            "legal_basis": "contract",
            "purpose": "Fulfilling web crawling and scraping services",
            "retention_period": "As configured in privacy settings",
            "third_party_sharing": False
        },
        "usage_analytics": {
            "legal_basis": "legitimate_interest",
            "purpose": "Service improvement and security",
            "retention_period": "12 months",
            "third_party_sharing": False,
            "opt_out_available": True
        },
        "logs": {
            "legal_basis": "legitimate_interest",
            "purpose": "Security and system monitoring",
            "retention_period": "90 days",
            "third_party_sharing": False
        }
    }


@router.get("/portability/{export_id}/download")
async def download_portable_data(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download portable data export (GDPR Article 20)."""
    
    privacy_service = PrivacyService(db)
    export_task = await privacy_service.get_export_task(
        export_id,
        str(current_user.id)
    )
    
    if not export_task:
        raise HTTPException(status_code=404, detail="Export not found")
    
    if export_task.status != "completed":
        raise HTTPException(status_code=400, detail="Export not ready")
    
    if export_task.expires_at and datetime.utcnow() > export_task.expires_at:
        raise HTTPException(status_code=410, detail="Export has expired")
    
    # Get download URL or file data
    file_data = await privacy_service.get_export_file(export_task.id)
    
    from fastapi.responses import StreamingResponse
    from io import BytesIO
    
    return StreamingResponse(
        BytesIO(file_data),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=personal_data_export_{export_id}.zip"
        }
    )
