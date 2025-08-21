"""
Data export and download router for the crawler platform.
"""
from typing import List, Optional, Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import io
import csv
import json
from enum import Enum

from src.webapp.deps import (
    DatabaseSession, CurrentUser, AdminUser, PaginationDep, 
    CacheServiceDep, RateLimitServiceDep
)
from src.services.export import ExportService
from src.services.data_quality import DataQualityService
from src.database.models import CrawlJob, ScrapedData, ExportJob
from src.utils.validators import validate_date_range, validate_export_format

router = APIRouter(prefix="/data", tags=["data"])

class ExportFormat(str, Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    EXCEL = "xlsx"
    PARQUET = "parquet"
    GOOGLE_SHEETS = "google_sheets"

class DataFilterRequest(BaseModel):
    """Data filtering request."""
    job_ids: Optional[List[str]] = Field(None, description="Filter by specific job IDs")
    sources: Optional[List[str]] = Field(None, description="Filter by data sources")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    status: Optional[str] = Field(None, description="Filter by processing status")
    data_quality_threshold: Optional[float] = Field(0.8, description="Minimum data quality score")

class ExportRequest(BaseModel):
    """Data export request."""
    format: ExportFormat = Field(description="Export format")
    filters: DataFilterRequest = Field(description="Data filters")
    include_metadata: bool = Field(True, description="Include metadata in export")
    compress: bool = Field(False, description="Compress the export file")
    email_notification: bool = Field(False, description="Send email when export is ready")
    google_sheets_config: Optional[Dict[str, Any]] = Field(None, description="Google Sheets configuration")

class ExportResponse(BaseModel):
    """Export response."""
    export_id: str
    status: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    record_count: Optional[int] = None

@router.get("/summary", summary="Get data summary statistics")
async def get_data_summary(
    db: DatabaseSession,
    user: CurrentUser,
    cache: CacheServiceDep,
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date")
) -> Dict[str, Any]:
    """Get summary statistics of crawled data."""
    cache_key = f"data_summary:{user.id}:{date_from}:{date_to}"
    cached_result = await cache.get(cache_key)
    
    if cached_result:
        return cached_result
    
    # Validate date range
    if date_from and date_to:
        validate_date_range(date_from, date_to)
    
    # Get summary statistics
    query = db.query(ScrapedData)
    if date_from:
        query = query.filter(ScrapedData.created_at >= date_from)
    if date_to:
        query = query.filter(ScrapedData.created_at <= date_to)
    
    total_records = query.count()
    
    # Get statistics by source
    source_stats = (
        query.group_by(ScrapedData.source)
        .with_entities(ScrapedData.source, db.func.count(ScrapedData.id))
        .all()
    )
    
    # Get statistics by status
    status_stats = (
        query.group_by(ScrapedData.status)
        .with_entities(ScrapedData.status, db.func.count(ScrapedData.id))
        .all()
    )
    
    # Get data quality statistics
    avg_quality_score = query.with_entities(
        db.func.avg(ScrapedData.quality_score)
    ).scalar() or 0
    
    result = {
        "total_records": total_records,
        "date_range": {
            "from": date_from.isoformat() if date_from else None,
            "to": date_to.isoformat() if date_to else None
        },
        "by_source": dict(source_stats),
        "by_status": dict(status_stats),
        "quality_metrics": {
            "average_score": round(avg_quality_score, 3),
            "high_quality_count": query.filter(ScrapedData.quality_score >= 0.8).count(),
            "low_quality_count": query.filter(ScrapedData.quality_score < 0.5).count()
        },
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # Cache for 15 minutes
    await cache.set(cache_key, result, ttl=900)
    
    return result

@router.get("/jobs", summary="List data processing jobs")
async def list_data_jobs(
    db: DatabaseSession,
    user: CurrentUser,
    pagination: PaginationDep,
    status: Optional[str] = Query(None, description="Filter by job status")
) -> Dict[str, Any]:
    """List data processing and crawl jobs."""
    query = db.query(CrawlJob).filter(CrawlJob.user_id == user.id)
    
    if status:
        query = query.filter(CrawlJob.status == status)
    
    total = query.count()
    jobs = (
        query.order_by(CrawlJob.created_at.desc())
        .offset(pagination.skip)
        .limit(pagination.size)
        .all()
    )
    
    return {
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "status": job.status,
                "source": job.source,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "record_count": job.record_count,
                "error_count": job.error_count
            }
            for job in jobs
        ],
        "pagination": {
            "page": pagination.page,
            "size": pagination.size,
            "total": total,
            "pages": (total + pagination.size - 1) // pagination.size
        }
    }

@router.post("/export", summary="Request data export")
async def request_data_export(
    export_request: ExportRequest,
    db: DatabaseSession,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    rate_limiter: RateLimitServiceDep
) -> ExportResponse:
    """Request a data export with specified filters and format."""
    # Rate limiting for exports
    if not await rate_limiter.check_rate_limit(
        f"export_requests:{user.id}", limit=10, window=3600
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Export request limit exceeded. Maximum 10 exports per hour."
        )
    
    # Validate export request
    if export_request.filters.date_from and export_request.filters.date_to:
        validate_date_range(
            export_request.filters.date_from, 
            export_request.filters.date_to
        )
    
    # Validate format-specific requirements
    if export_request.format == ExportFormat.GOOGLE_SHEETS:
        if not export_request.google_sheets_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google Sheets configuration required for this export format"
            )
    
    # Create export job
    export_service = ExportService(db)
    export_job = await export_service.create_export_job(
        user_id=user.id,
        format=export_request.format,
        filters=export_request.filters.dict(),
        options={
            "include_metadata": export_request.include_metadata,
            "compress": export_request.compress,
            "email_notification": export_request.email_notification,
            "google_sheets_config": export_request.google_sheets_config
        }
    )
    
    # Queue background export task
    background_tasks.add_task(
        export_service.process_export_job,
        export_job.id
    )
    
    return ExportResponse(
        export_id=export_job.id,
        status=export_job.status,
        created_at=export_job.created_at,
        estimated_completion=export_job.estimated_completion
    )

@router.get("/export/{export_id}", summary="Get export status")
async def get_export_status(
    export_id: str,
    db: DatabaseSession,
    user: CurrentUser
) -> ExportResponse:
    """Get the status of an export job."""
    export_job = (
        db.query(ExportJob)
        .filter(ExportJob.id == export_id, ExportJob.user_id == user.id)
        .first()
    )
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    return ExportResponse(
        export_id=export_job.id,
        status=export_job.status,
        created_at=export_job.created_at,
        estimated_completion=export_job.estimated_completion,
        download_url=export_job.download_url,
        file_size=export_job.file_size,
        record_count=export_job.record_count
    )

@router.get("/export/{export_id}/download", summary="Download export file")
async def download_export(
    export_id: str,
    db: DatabaseSession,
    user: CurrentUser
):
    """Download the exported data file."""
    export_job = (
        db.query(ExportJob)
        .filter(
            ExportJob.id == export_id, 
            ExportJob.user_id == user.id,
            ExportJob.status == "completed"
        )
        .first()
    )
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found or not completed"
        )
    
    if not export_job.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not available"
        )
    
    # Stream the file
    export_service = ExportService(db)
    file_stream = await export_service.get_export_file_stream(export_job.file_path)
    
    # Determine content type
    content_type_map = {
        "csv": "text/csv",
        "json": "application/json",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "parquet": "application/octet-stream"
    }
    
    content_type = content_type_map.get(export_job.format, "application/octet-stream")
    filename = f"export_{export_id}.{export_job.format}"
    
    return StreamingResponse(
        file_stream,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(export_job.file_size)
        }
    )

@router.delete("/export/{export_id}", summary="Cancel export job")
async def cancel_export(
    export_id: str,
    db: DatabaseSession,
    user: CurrentUser
) -> Dict[str, str]:
    """Cancel a pending export job."""
    export_job = (
        db.query(ExportJob)
        .filter(ExportJob.id == export_id, ExportJob.user_id == user.id)
        .first()
    )
    
    if not export_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export job not found"
        )
    
    if export_job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel export job with status: {export_job.status}"
        )
    
    # Cancel the export job
    export_service = ExportService(db)
    await export_service.cancel_export_job(export_id)
    
    return {"message": "Export job cancelled successfully"}

@router.get("/quality-report", summary="Get data quality report")
async def get_data_quality_report(
    db: DatabaseSession,
    user: CurrentUser,
    admin_user: AdminUser,  # Require admin access
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None)
) -> Dict[str, Any]:
    """Get comprehensive data quality report (admin only)."""
    dq_service = DataQualityService(db)
    
    if date_from and date_to:
        validate_date_range(date_from, date_to)
    
    report = await dq_service.generate_quality_report(
        date_from=date_from,
        date_to=date_to
    )
    
    return report

@router.get("/sample", summary="Get data sample")
async def get_data_sample(
    db: DatabaseSession,
    user: CurrentUser,
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(10, ge=1, le=100, description="Number of samples")
) -> List[Dict[str, Any]]:
    """Get a sample of scraped data for preview."""
    query = db.query(ScrapedData).filter(ScrapedData.quality_score >= 0.7)
    
    if source:
        query = query.filter(ScrapedData.source == source)
    
    samples = (
        query.order_by(ScrapedData.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": sample.id,
            "source": sample.source,
            "data": sample.data,
            "quality_score": sample.quality_score,
            "created_at": sample.created_at.isoformat(),
            "metadata": sample.metadata
        }
        for sample in samples
    ]
