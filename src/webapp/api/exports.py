import datetime
import os
from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks, Response, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict, Any
from src.database.models import ExportHistory, ExportCreate, ExportRead, JobType, JobStatus
from src.database.manager import get_db
from src.webapp.security import get_current_tenant_id, authorize_with_scopes
from src.scheduler.scheduler import schedule_job
from src.utils.export_utils import (
    get_data_from_db, generate_csv_stream, generate_ndjson_stream, generate_json_stream,
    get_fieldnames_for_export_type, get_latest_update_timestamp_for_export_type
)
import logging
import hashlib
import json
import io
import gzip

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/exports", response_model=ExportRead, status_code=202, dependencies=[Depends(authorize_with_scopes(["exports:write"]))])
async def create_export_job(
    export_create: ExportCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None)
):
    """
    Initiates a new asynchronous data export job.
    Returns a 202 Accepted response with the job ID.
    """
    logger.info(f"Received export job request for type: {export_create.export_type}", extra={"tenant_id": str(tenant_id), "idempotency_key": idempotency_key})

    # Generate a unique file name
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_prefix = export_create.file_name_prefix or export_create.export_type
    file_name = f"{file_prefix}_{timestamp}.{export_create.format}"
    if export_create.compress == "gzip":
        file_name += ".gz"

    new_export = ExportHistory(
        user_id=tenant_id, # Assuming user_id is tenant_id for simplicity here
        export_type=export_create.export_type,
        file_name=file_name,
        file_size_mb=0, # Will be updated by the background job
        credits_used=0, # Will be updated by the background job
        status=JobStatus.QUEUED.value,
        filters_json=export_create.filters,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(hours=export_create.destination.retention_hours)
    )

    db.add(new_export)
    db.commit()
    db.refresh(new_export)

    # Schedule the actual export processing as a background job
    schedule_job(str(new_export.id), job_type=JobType.EXPORT.value, params=export_create.model_dump())

    logger.info(f"Export job {new_export.id} queued.", extra={"export_id": str(new_export.id), "tenant_id": str(tenant_id)})
    return ExportRead.from_orm(new_export)

@router.get("/exports/{export_id}", response_model=ExportRead, dependencies=[Depends(authorize_with_scopes(["exports:read"]))])
async def get_export_status(
    export_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db)
):
    """Retrieves the status of a specific export job."""
    export_job = db.query(ExportHistory).filter(
        ExportHistory.id == export_id,
        ExportHistory.user_id == tenant_id # Ensure tenant can only see their own exports
    ).first()

    if not export_job:
        raise HTTPException(status_code=404, detail="Export job not found.")
    
    return ExportRead.from_orm(export_job)

@router.get("/exports", response_model=List[ExportRead], dependencies=[Depends(authorize_with_scopes(["exports:read"]))])
async def list_exports(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    status: Optional[JobStatus] = Query(None),
    export_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Lists all export jobs for the authenticated tenant."""
    query = db.query(ExportHistory).filter(ExportHistory.user_id == tenant_id)

    if status:
        query = query.filter(ExportHistory.status == status.value)
    if export_type:
        query = query.filter(ExportHistory.export_type == export_type)

    exports = query.order_by(ExportHistory.created_at.desc()).offset(offset).limit(limit).all()
    return [ExportRead.from_orm(e) for e in exports]

# Direct data export endpoints (synchronous, for smaller datasets or specific use cases)
@router.get("/data/{export_type}", dependencies=[Depends(authorize_with_scopes(["data:read"]))])
async def get_data_direct(
    export_type: str,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    format: Optional[str] = Query(None, description="Desired format: csv, ndjson, json"),
    compress: Optional[bool] = Query(False, description="Apply gzip compression"),
    filters: Optional[str] = Query(None, description="JSON string of filters, e.g., '{\"field\":\"value\"}' or '{\"field\":{\"gte\":\"value\"}}'"),
    sort_by: Optional[str] = Query(None, description="Field to sort by, e.g., 'created_at' or '-created_at' for descending."),
    fields: Optional[str] = Query(None, description="Comma-separated list of fields to include, e.g., 'id,name,email'"),
    mask_pii: bool = Query(True, description="Apply PII masking to sensitive fields (e.g., personal numbers, salaries). Requires 'data:read' scope to disable."), # Updated description
    if_none_match: Optional[str] = Header(None, alias="If-None-Match"),
    request: Request = Request # Inject Request object to access state.scopes
):
    """
    Directly retrieves data in specified format (CSV, NDJSON, JSON).
    Supports content negotiation via Accept header.
    """
    # PII masking enforcement
    if not mask_pii: # If client explicitly requests to disable masking
        user_scopes = getattr(request.state, "scopes", [])
        if "data:read:pii" not in user_scopes and "admin:*" not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions. 'data:read:pii' scope required to disable PII masking."
            )

    parsed_filters = {}
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid filters JSON format.")

    parsed_fields = fields.split(',') if fields else None

    # Determine ETag based on data content and filters
    latest_update = get_latest_update_timestamp_for_export_type(db, export_type, tenant_id, parsed_filters)
    etag_content = {
        "export_type": export_type,
        "filters": parsed_filters,
        "sort_by": sort_by,
        "fields": parsed_fields,
        "mask_pii": mask_pii, # Include mask_pii in ETag calculation
        "latest_update": latest_update.isoformat() if latest_update else "none"
    }
    current_etag = f'"{hashlib.sha256(json.dumps(etag_content, sort_keys=True).encode()).hexdigest()}"'

    # Check If-None-Match header for conditional GET
    if if_none_match == current_etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    # Pass mask_pii to the data retrieval function
    data_generator = get_data_from_db(db, export_type, tenant_id, parsed_filters, sort_by, parsed_fields, mask_pii=mask_pii)
    fieldnames = parsed_fields if parsed_fields else get_fieldnames_for_export_type(export_type)

    # Determine format based on query param or Accept header
    response_format = format
    if not response_format:
        accept_header = Request.headers.get("Accept", "")
        if "text/csv" in accept_header:
            response_format = "csv"
        elif "application/x-ndjson" in accept_header:
            response_format = "ndjson"
        elif "application/json" in accept_header:
            response_format = "json"
        else:
            response_format = "json" # Default to JSON if no specific format requested

    media_type = "application/json"
    stream_generator = None

    if response_format == "csv":
        stream_generator = generate_csv_stream(data_generator, fieldnames)
        media_type = "text/csv"
    elif response_format == "ndjson":
        stream_generator = generate_ndjson_stream(data_generator)
        media_type = "application/x-ndjson"
    elif response_format == "json":
        stream_generator = generate_json_stream(data_generator)
        media_type = "application/json"
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format.")

    headers = {
        "Content-Disposition": f"attachment; filename={export_type}_data.{response_format}",
        "ETag": current_etag,
        "Cache-Control": "public, max-age=60" # Short TTL for dynamic data
    }
    if compress:
        headers["Content-Encoding"] = "gzip"
        def gzip_stream():
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
                for chunk in stream_generator:
                    gz.write(chunk)
                    yield buffer.getvalue()
                    buffer.seek(0)
                    buffer.truncate(0)
            yield buffer.getvalue()
        stream_generator = gzip_stream()
        headers["Content-Disposition"] += ".gz"


    return StreamingResponse(stream_generator, media_type=media_type, headers=headers)