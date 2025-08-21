"""
Router for data export operations.
"""

import asyncio
import csv
import json
import zipfile
from datetime import datetime
from io import BytesIO, StringIO
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database import get_db
from ..models import User, CrawlJob, ScrapeJob
from ..schemas.common import StatusResponse, ExportResponse
from ..schemas.jobs import JobFilter, OutputFormat
from ..dependencies import get_current_user, require_permissions
from ..services.export_service import ExportService
from ..utils.pagination import paginate
from ..utils.rate_limiting import rate_limit

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/jobs", response_model=ExportResponse)
@rate_limit(requests=10, window=3600)  # 10 exports per hour
async def export_jobs(
    background_tasks: BackgroundTasks,
    job_ids: List[str] = Query(..., description="Job IDs to export"),
    format: OutputFormat = Query(OutputFormat.JSON, description="Export format"),
    include_results: bool = Query(True, description="Include job results"),
    include_logs: bool = Query(False, description="Include job logs"),
    include_metadata: bool = Query(True, description="Include metadata"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export job data in various formats."""
    
    # Validate job IDs and permissions
    crawl_jobs = db.query(CrawlJob).filter(
        and_(
            CrawlJob.id.in_(job_ids),
            CrawlJob.user_id == current_user.id
        )
    ).all()
    
    scrape_jobs = db.query(ScrapeJob).filter(
        and_(
            ScrapeJob.id.in_(job_ids),
            ScrapeJob.user_id == current_user.id
        )
    ).all()
    
    if len(crawl_jobs) + len(scrape_jobs) == 0:
        raise HTTPException(status_code=404, detail="No accessible jobs found")
    
    # Create export task
    export_service = ExportService(db)
    export_task = await export_service.create_export_task(
        user_id=str(current_user.id),
        job_ids=job_ids,
        format=format.value,
        options={
            "include_results": include_results,
            "include_logs": include_logs,
            "include_metadata": include_metadata
        }
    )
    
    # Start background export
    background_tasks.add_task(
        export_service.process_export,
        export_task.id,
        crawl_jobs + scrape_jobs
    )
    
    return ExportResponse(
        export_id=export_task.id,
        format=format.value,
        status="processing"
    )


@router.get("/jobs/{export_id}", response_model=ExportResponse)
async def get_export_status(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get export status and download URL."""
    
    export_service = ExportService(db)
    export_task = await export_service.get_export_task(export_id, str(current_user.id))
    
    if not export_task:
        raise HTTPException(status_code=404, detail="Export task not found")
    
    return ExportResponse(
        export_id=export_task.id,
        format=export_task.format,
        status=export_task.status,
        download_url=export_task.download_url,
        expires_at=export_task.expires_at,
        file_size=export_task.file_size,
        records_count=export_task.records_count
    )


@router.get("/jobs/{export_id}/download")
async def download_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download exported data."""
    
    export_service = ExportService(db)
    export_task = await export_service.get_export_task(export_id, str(current_user.id))
    
    if not export_task:
        raise HTTPException(status_code=404, detail="Export task not found")
    
    if export_task.status != "completed":
        raise HTTPException(status_code=400, detail="Export not ready for download")
    
    if export_task.expires_at and datetime.utcnow() > export_task.expires_at:
        raise HTTPException(status_code=410, detail="Export has expired")
    
    # Get file data
    file_data = await export_service.get_export_file(export_task.id)
    
    if not file_data:
        raise HTTPException(status_code=404, detail="Export file not found")
    
    # Determine content type and filename
    content_type_map = {
        "json": "application/json",
        "csv": "text/csv",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xml": "application/xml"
    }
    
    extension_map = {
        "json": "json",
        "csv": "csv", 
        "excel": "xlsx",
        "xml": "xml"
    }
    
    content_type = content_type_map.get(export_task.format, "application/octet-stream")
    extension = extension_map.get(export_task.format, "bin")
    filename = f"export_{export_id}.{extension}"
    
    # Record download
    await export_service.record_download(export_task.id)
    
    return StreamingResponse(
        BytesIO(file_data),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/templates", response_model=ExportResponse)
@rate_limit(requests=5, window=3600)  # 5 template exports per hour
async def export_templates(
    background_tasks: BackgroundTasks,
    template_names: List[str] = Query(..., description="Template names to export"),
    format: OutputFormat = Query(OutputFormat.JSON, description="Export format"),
    include_examples: bool = Query(True, description="Include example configurations"),
    current_user: User = Depends(require_permissions(["read:templates"]))
):
    """Export scraping templates."""
    
    export_service = ExportService()
    export_task = await export_service.create_template_export(
        user_id=str(current_user.id),
        template_names=template_names,
        format=format.value,
        include_examples=include_examples
    )
    
    background_tasks.add_task(
        export_service.process_template_export,
        export_task.id
    )
    
    return ExportResponse(
        export_id=export_task.id,
        format=format.value,
        status="processing"
    )


@router.post("/results/bulk", response_model=ExportResponse)
@rate_limit(requests=3, window=3600)  # 3 bulk exports per hour
async def bulk_export_results(
    background_tasks: BackgroundTasks,
    filters: JobFilter,
    format: OutputFormat = Query(OutputFormat.JSON, description="Export format"),
    limit: int = Query(1000, le=10000, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bulk export job results based on filters."""
    
    # Build query based on filters
    crawl_query = db.query(CrawlJob).filter(CrawlJob.user_id == current_user.id)
    scrape_query = db.query(ScrapeJob).filter(ScrapeJob.user_id == current_user.id)
    
    if filters.status:
        crawl_query = crawl_query.filter(CrawlJob.status == filters.status)
        scrape_query = scrape_query.filter(ScrapeJob.status == filters.status)
    
    if filters.created_after:
        crawl_query = crawl_query.filter(CrawlJob.created_at >= filters.created_after)
        scrape_query = scrape_query.filter(ScrapeJob.created_at >= filters.created_after)
    
    if filters.created_before:
        crawl_query = crawl_query.filter(CrawlJob.created_at <= filters.created_before)
        scrape_query = scrape_query.filter(ScrapeJob.created_at <= filters.created_before)
    
    # Get jobs with limit
    crawl_jobs = crawl_query.limit(limit // 2).all()
    scrape_jobs = scrape_query.limit(limit // 2).all()
    
    if not crawl_jobs and not scrape_jobs:
        raise HTTPException(status_code=404, detail="No jobs found matching filters")
    
    # Create export task
    export_service = ExportService(db)
    export_task = await export_service.create_bulk_export(
        user_id=str(current_user.id),
        jobs=crawl_jobs + scrape_jobs,
        format=format.value,
        filters=filters.dict()
    )
    
    background_tasks.add_task(
        export_service.process_bulk_export,
        export_task.id
    )
    
    return ExportResponse(
        export_id=export_task.id,
        format=format.value,
        status="processing"
    )


@router.get("/formats")
async def get_export_formats():
    """Get available export formats and their capabilities."""
    
    return {
        "formats": [
            {
                "name": "json",
                "description": "JSON format with full data structure",
                "supports_nested": True,
                "supports_metadata": True,
                "file_extension": "json",
                "content_type": "application/json"
            },
            {
                "name": "csv",
                "description": "Comma-separated values (flattened structure)",
                "supports_nested": False,
                "supports_metadata": True,
                "file_extension": "csv",
                "content_type": "text/csv"
            },
            {
                "name": "excel",
                "description": "Microsoft Excel format with multiple sheets",
                "supports_nested": True,
                "supports_metadata": True,
                "file_extension": "xlsx",
                "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            },
            {
                "name": "xml",
                "description": "XML format with structured data",
                "supports_nested": True,
                "supports_metadata": True,
                "file_extension": "xml",
                "content_type": "application/xml"
            }
        ]
    }


@router.get("/history")
async def get_export_history(
    limit: int = Query(50, le=100, description="Number of exports to return"),
    offset: int = Query(0, ge=0, description="Number of exports to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's export history."""
    
    export_service = ExportService(db)
    exports = await export_service.get_user_exports(
        str(current_user.id),
        limit=limit,
        offset=offset
    )
    
    return {
        "exports": exports,
        "total": len(exports),
        "limit": limit,
        "offset": offset
    }


@router.delete("/{export_id}", response_model=StatusResponse)
async def delete_export(
    export_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an export task and its files."""
    
    export_service = ExportService(db)
    success = await export_service.delete_export(export_id, str(current_user.id))
    
    if not success:
        raise HTTPException(status_code=404, detail="Export task not found")
    
    return StatusResponse(
        success=True,
        message="Export deleted successfully"
    )


@router.post("/cleanup", response_model=StatusResponse)
@require_permissions(["admin:cleanup"])
async def cleanup_expired_exports(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up expired export files (admin only)."""
    
    export_service = ExportService(db)
    
    background_tasks.add_task(
        export_service.cleanup_expired_exports
    )
    
    return StatusResponse(
        success=True,
        message="Cleanup task started"
    )


@router.get("/stats")
async def get_export_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get export statistics for current user."""
    
    export_service = ExportService(db)
    stats = await export_service.get_user_export_stats(str(current_user.id))
    
    return stats


@router.post("/google-sheets", response_model=StatusResponse)
@rate_limit(requests=5, window=3600)  # 5 Google Sheets exports per hour
async def export_to_google_sheets(
    job_ids: List[str],
    sheet_id: str,
    sheet_name: Optional[str] = None,
    current_user: User = Depends(require_permissions(["export:google_sheets"])),
    db: Session = Depends(get_db)
):
    """Export job data to Google Sheets."""
    
    # Validate jobs
    crawl_jobs = db.query(CrawlJob).filter(
        and_(
            CrawlJob.id.in_(job_ids),
            CrawlJob.user_id == current_user.id
        )
    ).all()
    
    scrape_jobs = db.query(ScrapeJob).filter(
        and_(
            ScrapeJob.id.in_(job_ids),
            ScrapeJob.user_id == current_user.id
        )
    ).all()
    
    if len(crawl_jobs) + len(scrape_jobs) == 0:
        raise HTTPException(status_code=404, detail="No accessible jobs found")
    
    try:
        from ..services.google_sheets_service import GoogleSheetsService
        
        sheets_service = GoogleSheetsService()
        await sheets_service.export_jobs_to_sheet(
            jobs=crawl_jobs + scrape_jobs,
            sheet_id=sheet_id,
            sheet_name=sheet_name or f"Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        return StatusResponse(
            success=True,
            message="Data exported to Google Sheets successfully"
        )
        
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Google Sheets integration not available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export to Google Sheets: {str(e)}"
        )
