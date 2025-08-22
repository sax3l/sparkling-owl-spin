"""
Base exporter interface for all export targets.
Provides common functionality and interface for data export operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generator
import logging
from dataclasses import dataclass
from datetime import datetime
import asyncio
from pathlib import Path
import uuid
from sqlalchemy.orm import Session

# Import database utilities
from src.utils.export_utils import (
    get_data_from_db, 
    generate_csv_stream, 
    generate_ndjson_stream, 
    generate_json_stream,
    get_fieldnames_for_export_type,
    upload_to_supabase_storage
)

logger = logging.getLogger(__name__)

@dataclass
class ExportConfig:
    """Configuration for export operations."""
    output_path: Optional[str] = None
    batch_size: int = 1000
    compress: bool = False
    include_metadata: bool = True
    format_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.format_options is None:
            self.format_options = {}

@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    records_exported: int
    output_location: str
    export_time: datetime
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class BaseExporter(ABC):
    """Base class for all data exporters."""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to the target destination."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the exporter configuration."""
        pass
    
    def prepare_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for export (common preprocessing)."""
        prepared_data = []
        
        for record in data:
            prepared_record = record.copy()
            
            # Add metadata if requested
            if self.config.include_metadata:
                prepared_record["_export_timestamp"] = datetime.utcnow().isoformat()
                prepared_record["_exporter"] = self.__class__.__name__
            
            prepared_data.append(prepared_record)
        
        return prepared_data
    
    def create_metadata(self, record_count: int) -> Dict[str, Any]:
        """Create export metadata."""
        return {
            "export_timestamp": datetime.utcnow().isoformat(),
            "exporter": self.__class__.__name__,
            "record_count": record_count,
            "config": {
                "batch_size": self.config.batch_size,
                "compress": self.config.compress,
                "include_metadata": self.config.include_metadata
            }
        }
    
    async def export_batched(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data in batches."""
        if not data:
            return ExportResult(
                success=True,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(0)
            )
        
        batch_size = self.config.batch_size
        total_records = len(data)
        exported_count = 0
        
        try:
            for i in range(0, total_records, batch_size):
                batch = data[i:i + batch_size]
                result = await self.export(batch, **kwargs)
                
                if not result.success:
                    return result
                
                exported_count += result.records_exported
                self.logger.info(f"Exported batch {i//batch_size + 1}, {result.records_exported} records")
            
            return ExportResult(
                success=True,
                records_exported=exported_count,
                output_location=kwargs.get("output_path", ""),
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(exported_count)
            )
            
        except Exception as e:
            self.logger.error(f"Export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=exported_count,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e),
                metadata=self.create_metadata(exported_count)
            )

class ExporterRegistry:
    """Registry for managing available exporters."""
    
    _exporters: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, exporter_class: type):
        """Register an exporter."""
        cls._exporters[name] = exporter_class
    
    @classmethod
    def get_exporter(cls, name: str) -> Optional[type]:
        """Get an exporter by name."""
        return cls._exporters.get(name)
    
    @classmethod
    def list_exporters(cls) -> List[str]:
        """List all registered exporters."""
        return list(cls._exporters.keys())
    
    @classmethod
    def create_exporter(cls, name: str, config: ExportConfig) -> Optional[BaseExporter]:
        """Create an exporter instance."""
        exporter_class = cls.get_exporter(name)
        if exporter_class:
            return exporter_class(config)
        return None

# Utility functions for common export operations
def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary."""
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

def generate_filename(base_name: str, extension: str, timestamp: bool = True) -> str:
    """Generate a unique filename."""
    if timestamp:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{ts}.{extension}"
    return f"{base_name}.{extension}"


class ExportManager:
    """
    Enhanced export manager with database integration and cloud storage support.
    Coordinates all export operations across different formats and destinations.
    """
    
    def __init__(self, registry: ExporterRegistry = None):
        self.registry = registry or ExporterRegistry()
        
    def export_data(self, data: Any, format: str, **kwargs) -> Any:
        """Export data using registered exporter"""
        exporter = self.registry.get_exporter(format)
        if not exporter:
            raise ValueError(f"No exporter registered for format: {format}")
        return exporter.export(data, **kwargs)
    
    def export_from_database(
        self,
        db: Session,
        export_type: str,
        format: str,
        tenant_id: uuid.UUID,
        filters: Dict[str, Any] = None,
        sort_by: Optional[str] = None,
        fields: Optional[List[str]] = None,
        mask_pii: bool = True,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs
    ) -> Generator[bytes, None, None]:
        """
        Export data directly from database with streaming support.
        
        Args:
            db: Database session
            export_type: Type of data to export (person, company, vehicle)
            format: Export format (csv, json, ndjson)
            tenant_id: Tenant ID for data filtering
            filters: Additional filters to apply
            sort_by: Sort field (prefix with '-' for descending)
            fields: Specific fields to include
            mask_pii: Whether to mask PII data
            limit: Maximum number of records
            offset: Records to skip
            **kwargs: Additional format-specific options
            
        Returns:
            Generator yielding data chunks as bytes
        """
        filters = filters or {}
        
        # Get data generator from database
        data_generator = get_data_from_db(
            db=db,
            export_type=export_type,
            tenant_id=tenant_id,
            filters=filters,
            sort_by=sort_by,
            fields=fields,
            mask_pii=mask_pii,
            limit=limit,
            offset=offset
        )
        
        # Generate appropriate stream based on format
        if format.lower() == 'csv':
            return generate_csv_stream(data_generator, get_fieldnames_for_export_type(export_type))
        elif format.lower() == 'json':
            return generate_json_stream(data_generator)
        elif format.lower() == 'ndjson':
            return generate_ndjson_stream(data_generator)
        else:
            # Fall back to standard export for other formats
            data_list = list(data_generator)
            result = self.export_data(data_list, format, **kwargs)
            if isinstance(result, str):
                yield result.encode('utf-8')
            elif isinstance(result, bytes):
                yield result
            else:
                yield str(result).encode('utf-8')
    
    async def export_to_cloud_storage(
        self,
        bucket_name: str,
        file_path: str,
        data_stream: Generator[bytes, None, None],
        content_type: str,
        compress: bool = False
    ) -> str:
        """
        Export data stream to cloud storage (Supabase).
        
        Returns:
            Public URL of uploaded file
        """
        return await upload_to_supabase_storage(
            bucket_name=bucket_name,
            file_path=file_path,
            data_stream=data_stream,
            content_type=content_type,
            compress=compress
        )
    
    def get_available_formats(self) -> List[str]:
        """Get list of available export formats"""
        return list(self.registry.exporters.keys())
