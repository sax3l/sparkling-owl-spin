import datetime
import json
import os
import logging
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import ExportHistory, JobStatus, ExportCreate
from src.database.manager import SessionLocal
from src.utils.export_utils import get_data_from_db, generate_csv_stream, generate_ndjson_stream, generate_json_stream, get_fieldnames_for_export_type, upload_to_supabase_storage
from src.webhooks.events import export_ready_event # Assuming this event exists
from src.webhooks.service import WebhookService # Assuming this service exists

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

        data_generator = get_data_from_db(db, export_create.export_type, export_create.filters)
        fieldnames = get_fieldnames_for_export_type(export_create.export_type)

        # Determine stream generator and content type
        stream_generator = None
        content_type = ""
        if export_create.format == "csv":
            stream_generator = generate_csv_stream(data_generator, fieldnames)
            content_type = "text/csv"
        elif export_create.format == "ndjson":
            stream_generator = generate_ndjson_stream(data_generator)
            content_type = "application/x-ndjson"
        elif export_create.format == "json":
            stream_generator = generate_json_stream(data_generator)
            content_type = "application/json"
        else:
            raise ValueError(f"Unsupported export format: {export_create.format}")

        # Upload to Supabase Storage
        file_path_in_storage = f"{export_job.user_id}/{export_job.file_name}"
        download_url = await upload_to_supabase_storage(
            bucket_name=SUPABASE_EXPORTS_BUCKET,
            file_path=file_path_in_storage,
            data_stream=stream_generator,
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