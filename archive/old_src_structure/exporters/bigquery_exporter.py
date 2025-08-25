"""
BigQuery Exporter for exporting data to Google BigQuery.
Supports batch inserts, schema validation, and partitioning.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class BigQueryExporter(BaseExporter):
    """Exporter for Google BigQuery."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.project_id = config.format_options.get('project_id')
        self.dataset_id = config.format_options.get('dataset_id')
        self.table_id = config.format_options.get('table_id')
        self.credentials_path = config.format_options.get('credentials_path')
        self.write_disposition = config.format_options.get('write_disposition', 'WRITE_APPEND')
        self.create_disposition = config.format_options.get('create_disposition', 'CREATE_IF_NEEDED')
        self.auto_detect_schema = config.format_options.get('auto_detect_schema', True)
    
    def validate_config(self) -> bool:
        """Validate BigQuery exporter configuration."""
        try:
            if not BIGQUERY_AVAILABLE:
                self.logger.error("BigQuery export requires google-cloud-bigquery package")
                return False
            
            if not self.project_id:
                self.logger.error("Project ID is required for BigQuery export")
                return False
            
            if not self.dataset_id:
                self.logger.error("Dataset ID is required for BigQuery export")
                return False
            
            if not self.table_id:
                self.logger.error("Table ID is required for BigQuery export")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to BigQuery."""
        if not self.validate_config():
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message="Invalid configuration or missing dependencies"
            )
        
        try:
            # Prepare data
            prepared_data = self.prepare_data(data)
            
            if not prepared_data:
                return ExportResult(
                    success=True,
                    records_exported=0,
                    output_location=f"{self.project_id}.{self.dataset_id}.{self.table_id}",
                    export_time=datetime.utcnow(),
                    metadata=self.create_metadata(0)
                )
            
            # Write to BigQuery
            rows_inserted = await self._write_bigquery(prepared_data)
            
            location = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            self.logger.info(f"Exported {rows_inserted} records to BigQuery: {location}")
            
            return ExportResult(
                success=True,
                records_exported=rows_inserted,
                output_location=location,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(rows_inserted)
            )
            
        except Exception as e:
            self.logger.error(f"BigQuery export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_bigquery(self, data: List[Dict[str, Any]]) -> int:
        """Write data to BigQuery."""
        def write_sync():
            # Initialize client
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
                client = bigquery.Client(credentials=credentials, project=self.project_id)
            else:
                client = bigquery.Client(project=self.project_id)
            
            # Get table reference
            table_ref = client.dataset(self.dataset_id).table(self.table_id)
            
            # Configure job
            job_config = bigquery.LoadJobConfig(
                write_disposition=self.write_disposition,
                create_disposition=self.create_disposition,
                autodetect=self.auto_detect_schema,
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
            )
            
            # Insert rows
            job = client.load_table_from_json(data, table_ref, job_config=job_config)
            job.result()  # Wait for job to complete
            
            return len(data)
        
        return await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter only if dependencies are available
if BIGQUERY_AVAILABLE:
    ExporterRegistry.register('bigquery', BigQueryExporter)
