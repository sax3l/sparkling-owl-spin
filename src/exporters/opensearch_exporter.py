"""
OpenSearch Exporter for exporting data to OpenSearch.
Supports bulk indexing and various authentication methods.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from opensearchpy import OpenSearch
    from opensearchpy.helpers import bulk
    OPENSEARCH_AVAILABLE = True
except ImportError:
    OPENSEARCH_AVAILABLE = False

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class OpenSearchExporter(BaseExporter):
    """Exporter for OpenSearch."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.hosts = config.format_options.get('hosts', ['localhost:9200'])
        self.index = config.format_options.get('index')
        self.username = config.format_options.get('username')
        self.password = config.format_options.get('password')
        self.use_ssl = config.format_options.get('use_ssl', False)
        self.verify_certs = config.format_options.get('verify_certs', True)
        self.timeout = config.format_options.get('timeout', 30)
        self.refresh = config.format_options.get('refresh', 'wait_for')
    
    def validate_config(self) -> bool:
        """Validate OpenSearch exporter configuration."""
        try:
            if not OPENSEARCH_AVAILABLE:
                self.logger.error("OpenSearch export requires opensearch-py package")
                return False
            
            if not self.index:
                self.logger.error("Index name is required for OpenSearch export")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to OpenSearch."""
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
                    output_location=self.index,
                    export_time=datetime.utcnow(),
                    metadata=self.create_metadata(0)
                )
            
            # Write to OpenSearch
            success_count, failed_count = await self._write_opensearch(prepared_data)
            
            self.logger.info(f"Exported {success_count} records to OpenSearch index: {self.index}")
            
            return ExportResult(
                success=failed_count == 0,
                records_exported=success_count,
                output_location=self.index,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(success_count),
                error_message=f"{failed_count} records failed" if failed_count > 0 else None
            )
            
        except Exception as e:
            self.logger.error(f"OpenSearch export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_opensearch(self, data: List[Dict[str, Any]]) -> tuple:
        """Write data to OpenSearch."""
        def write_sync():
            # Connect to OpenSearch
            client_config = {
                'hosts': self.hosts,
                'timeout': self.timeout,
                'use_ssl': self.use_ssl,
                'verify_certs': self.verify_certs
            }
            
            if self.username and self.password:
                client_config['http_auth'] = (self.username, self.password)
            
            client = OpenSearch(**client_config)
            
            # Prepare documents for bulk indexing
            docs = []
            for doc in data:
                doc_dict = {
                    '_index': self.index,
                    '_source': doc
                }
                docs.append(doc_dict)
            
            # Perform bulk indexing
            success_count, failed_items = bulk(
                client,
                docs,
                refresh=self.refresh,
                chunk_size=self.config.batch_size
            )
            
            failed_count = len(failed_items) if failed_items else 0
            
            return success_count, failed_count
        
        return await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter only if dependencies are available
if OPENSEARCH_AVAILABLE:
    ExporterRegistry.register('opensearch', OpenSearchExporter)
