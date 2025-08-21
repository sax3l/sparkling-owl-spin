"""
Elasticsearch Exporter for exporting data to Elasticsearch.
Supports bulk indexing and various authentication methods.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
    ELASTIC_AVAILABLE = True
except ImportError:
    ELASTIC_AVAILABLE = False

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class ElasticExporter(BaseExporter):
    """Exporter for Elasticsearch."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.hosts = config.format_options.get('hosts', ['localhost:9200'])
        self.index = config.format_options.get('index')
        self.doc_type = config.format_options.get('doc_type', '_doc')
        self.username = config.format_options.get('username')
        self.password = config.format_options.get('password')
        self.api_key = config.format_options.get('api_key')
        self.use_ssl = config.format_options.get('use_ssl', False)
        self.verify_certs = config.format_options.get('verify_certs', True)
        self.timeout = config.format_options.get('timeout', 30)
        self.refresh = config.format_options.get('refresh', 'wait_for')
    
    def validate_config(self) -> bool:
        """Validate Elasticsearch exporter configuration."""
        try:
            if not ELASTIC_AVAILABLE:
                self.logger.error("Elasticsearch export requires elasticsearch package")
                return False
            
            if not self.index:
                self.logger.error("Index name is required for Elasticsearch export")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to Elasticsearch."""
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
            
            # Write to Elasticsearch
            success_count, failed_count = await self._write_elasticsearch(prepared_data)
            
            self.logger.info(f"Exported {success_count} records to Elasticsearch index: {self.index}")
            
            return ExportResult(
                success=failed_count == 0,
                records_exported=success_count,
                output_location=self.index,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(success_count),
                error_message=f"{failed_count} records failed" if failed_count > 0 else None
            )
            
        except Exception as e:
            self.logger.error(f"Elasticsearch export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_elasticsearch(self, data: List[Dict[str, Any]]) -> tuple:
        """Write data to Elasticsearch."""
        def write_sync():
            # Connect to Elasticsearch
            es_config = {
                'hosts': self.hosts,
                'timeout': self.timeout,
                'use_ssl': self.use_ssl,
                'verify_certs': self.verify_certs
            }
            
            if self.username and self.password:
                es_config['http_auth'] = (self.username, self.password)
            elif self.api_key:
                es_config['api_key'] = self.api_key
            
            es = Elasticsearch(**es_config)
            
            # Prepare documents for bulk indexing
            docs = []
            for doc in data:
                doc_dict = {
                    '_index': self.index,
                    '_type': self.doc_type,
                    '_source': doc
                }
                docs.append(doc_dict)
            
            # Perform bulk indexing
            success_count, failed_items = bulk(
                es,
                docs,
                refresh=self.refresh,
                chunk_size=self.config.batch_size
            )
            
            failed_count = len(failed_items) if failed_items else 0
            
            return success_count, failed_count
        
        return await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter only if dependencies are available
if ELASTIC_AVAILABLE:
    ExporterRegistry.register('elasticsearch', ElasticExporter)
    ExporterRegistry.register('elastic', ElasticExporter)
