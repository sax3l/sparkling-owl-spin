"""Base exporter interface for scraped data."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum


class ExportFormat(Enum):
    """Supported export formats."""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PARQUET = "parquet"
    GOOGLE_SHEETS = "google_sheets"
    DATABASE = "database"
    API = "api"


@dataclass
class ExportConfig:
    """Configuration for data export."""
    format: ExportFormat
    destination: str
    batch_size: int = 1000
    include_metadata: bool = True
    include_headers: bool = True
    compression: Optional[str] = None
    encoding: str = "utf-8"
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    records_exported: int
    destination: str
    format: ExportFormat
    file_size: Optional[int] = None
    export_time: Optional[datetime] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.export_time is None:
            self.export_time = datetime.now()


class BaseExporter(ABC):
    """Base class for all data exporters."""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def export(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Export data to the configured destination.
        
        Args:
            data: List of records to export
            metadata: Optional metadata about the export
            
        Returns:
            ExportResult with export details
        """
        pass
    
    @abstractmethod
    def validate_destination(self) -> bool:
        """
        Validate that the export destination is accessible and writable.
        
        Returns:
            True if destination is valid, False otherwise
        """
        pass
    
    def _prepare_data(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Prepare data for export by applying transformations and adding metadata.
        
        Args:
            data: Raw data to prepare
            metadata: Optional metadata to include
            
        Returns:
            Prepared data ready for export
        """
        prepared_data = []
        
        for record in data:
            prepared_record = record.copy()
            
            # Add metadata if requested
            if self.config.include_metadata and metadata:
                prepared_record.update({
                    f"_meta_{key}": value for key, value in metadata.items()
                })
            
            prepared_data.append(prepared_record)
        
        return prepared_data
    
    def _add_standard_metadata(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add standard metadata fields.
        
        Args:
            metadata: Existing metadata to extend
            
        Returns:
            Metadata with standard fields added
        """
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "export_timestamp": datetime.now().isoformat(),
            "export_format": self.config.format.value,
            "exporter_version": "1.0.0"
        })
        
        return metadata
    
    def _handle_errors(self, error: Exception, context: str = "") -> ExportResult:
        """
        Handle errors during export operations.
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            ExportResult indicating failure
        """
        error_msg = f"Export failed{f' during {context}' if context else ''}: {str(error)}"
        self.logger.error(error_msg)
        
        return ExportResult(
            success=False,
            records_exported=0,
            destination=self.config.destination,
            format=self.config.format,
            errors=[error_msg]
        )
    
    def _batch_data(self, data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Split data into batches for processing.
        
        Args:
            data: Data to batch
            
        Returns:
            List of data batches
        """
        batch_size = self.config.batch_size
        return [data[i:i + batch_size] for i in range(0, len(data), batch_size)]


class MultiFormatExporter:
    """Exporter that can handle multiple formats."""
    
    def __init__(self):
        self.exporters = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_exporter(self, format_type: ExportFormat, exporter_class: type):
        """
        Register an exporter for a specific format.
        
        Args:
            format_type: The export format this exporter handles
            exporter_class: The exporter class
        """
        self.exporters[format_type] = exporter_class
        self.logger.info(f"Registered exporter for format: {format_type.value}")
    
    def export(self, data: List[Dict[str, Any]], config: ExportConfig, metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Export data using the appropriate exporter for the configured format.
        
        Args:
            data: Data to export
            config: Export configuration
            metadata: Optional metadata
            
        Returns:
            ExportResult with export details
        """
        if config.format not in self.exporters:
            return ExportResult(
                success=False,
                records_exported=0,
                destination=config.destination,
                format=config.format,
                errors=[f"No exporter registered for format: {config.format.value}"]
            )
        
        try:
            exporter_class = self.exporters[config.format]
            exporter = exporter_class(config)
            return exporter.export(data, metadata)
        
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            return ExportResult(
                success=False,
                records_exported=0,
                destination=config.destination,
                format=config.format,
                errors=[f"Export failed: {str(e)}"]
            )
    
    def get_supported_formats(self) -> List[ExportFormat]:
        """
        Get list of supported export formats.
        
        Returns:
            List of supported formats
        """
        return list(self.exporters.keys())


# Factory function for creating exporters
def create_exporter(config: ExportConfig) -> BaseExporter:
    """
    Factory function to create appropriate exporter based on configuration.
    
    Args:
        config: Export configuration
        
    Returns:
        Exporter instance
        
    Raises:
        ValueError: If format is not supported
    """
    from .csv_exporter import CSVExporter
    from .json_exporter import JSONExporter
    from .excel_exporter import ExcelExporter
    from .google_sheets_exporter import GoogleSheetsExporter
    
    exporters = {
        ExportFormat.CSV: CSVExporter,
        ExportFormat.JSON: JSONExporter,
        ExportFormat.EXCEL: ExcelExporter,
        ExportFormat.GOOGLE_SHEETS: GoogleSheetsExporter,
    }
    
    exporter_class = exporters.get(config.format)
    if not exporter_class:
        raise ValueError(f"Unsupported export format: {config.format.value}")
    
    return exporter_class(config)


# Utility functions
def validate_data_structure(data: List[Dict[str, Any]]) -> bool:
    """
    Validate that data has consistent structure for export.
    
    Args:
        data: Data to validate
        
    Returns:
        True if data structure is consistent, False otherwise
    """
    if not data:
        return True
    
    # Check that all records have the same keys
    expected_keys = set(data[0].keys())
    for record in data[1:]:
        if set(record.keys()) != expected_keys:
            return False
    
    return True


def sanitize_field_names(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sanitize field names for export compatibility.
    
    Args:
        data: Data with potentially problematic field names
        
    Returns:
        Data with sanitized field names
    """
    import re
    
    if not data:
        return data
    
    sanitized_data = []
    
    for record in data:
        sanitized_record = {}
        for key, value in record.items():
            # Replace problematic characters with underscores
            sanitized_key = re.sub(r'[^\w]', '_', key)
            # Remove consecutive underscores
            sanitized_key = re.sub(r'_+', '_', sanitized_key)
            # Remove leading/trailing underscores
            sanitized_key = sanitized_key.strip('_')
            
            sanitized_record[sanitized_key] = value
        
        sanitized_data.append(sanitized_record)
    
    return sanitized_data
