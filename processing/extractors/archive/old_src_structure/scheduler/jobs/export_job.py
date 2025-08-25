import datetime
import json
import os
import logging
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import Export as ExportHistory, JobStatus, ExportCreate
from database.manager import SessionLocal
from exporters.registry import get_export_manager
from webhooks.events import export_ready_event # Assuming this event exists
from webhooks.service import WebhookService # Assuming this service exists

logger = logging.getLogger(__name__)

# Supabase Storage bucket for exports
SUPABASE_EXPORTS_BUCKET = os.getenv("SUPABASE_EXPORTS_BUCKET", "exports")

async def execute_export_job(export_id: str, export_params: Dict[str, Any]):
    """
    Background job to perform the actual data export, upload to storage,
    and update the ExportHistory record.
    """
    db: Session = SessionLocal()
    export_job = None
    try:
        export_job = db.query(ExportHistory).filter(ExportHistory.id == UUID(export_id)).first()
        if not export_job:
            logger.error(f"Export job {export_id} not found.", extra={"export_id": export_id})
            return

        export_job.status = JobStatus.RUNNING.value
        db.commit()

        export_create = ExportCreate(**export_params)
        
        logger.info(f"Starting export job {export_id} for type {export_create.export_type} in format {export_create.format}.", extra={"export_id": export_id, "export_type": export_create.export_type})

        # Use the new ExportManager system
        export_manager = get_export_manager()
        
        # Generate data stream using integrated database export
        data_stream = export_manager.export_from_database(
            db=db,
            export_type=export_create.export_type,
            format=export_create.format,
            tenant_id=export_job.user_id,  # Assuming user_id serves as tenant_id
            filters=export_create.filters or {},
            mask_pii=True
        )

        # Determine content type
        content_type_map = {
            "csv": "text/csv",
            "json": "application/json", 
            "ndjson": "application/x-ndjson",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        content_type = content_type_map.get(export_create.format, "application/octet-stream")

        # Upload to cloud storage using integrated method
        file_path_in_storage = f"{export_job.user_id}/{export_job.file_name}"
        download_url = await export_manager.export_to_cloud_storage(
            bucket_name=SUPABASE_EXPORTS_BUCKET,
            file_path=file_path_in_storage,
            data_stream=data_stream,
            content_type=content_type,
            compress=(export_create.compress == "gzip")
        )

        # Update job status and download URL
        export_job.status = JobStatus.COMPLETED.value
        export_job.download_url = download_url
        # TODO: Calculate actual file_size_mb and credits_used
        export_job.file_size_mb = 0.1 # Placeholder
        export_job.credits_used = 1 # Placeholder
        db.commit()
        logger.info(f"Export job {export_id} completed. Download URL: {download_url}", extra={"export_id": export_id, "download_url": download_url})

        # Trigger webhook (if WebhookService is initialized)
        # webhook_service = WebhookService(db) # You'd need to pass a proper db session or client
        # event = export_ready_event(
        #     export_id=str(export_job.id),
        #     user_id=str(export_job.user_id),
        #     file_name=export_job.file_name,
        #     download_url=download_url
        # )
        # await webhook_service.process_event(event)

    except Exception as e:
        logger.error(f"Export job {export_id} failed: {e}", exc_info=True, extra={"export_id": export_id})
        if export_job:
            export_job.status = JobStatus.FAILED.value
            export_job.error_text = str(e) # Assuming ExportHistory has an error_text field
            db.commit()
    finally:
        db.close()

class ExportJob:
    """
    Export job class for scheduler integration.
    Handles export job scheduling and execution.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
    async def execute(self, export_id: str, export_params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the export job."""
        try:
            await execute_export_job(export_id, export_params)
            return {
                'status': 'success', 
                'export_id': export_id,
                'timestamp': datetime.datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"ExportJob execution failed: {e}")
            return {
                'status': 'failed',
                'export_id': export_id, 
                'error': str(e),
                'timestamp': datetime.datetime.now().isoformat()
            }