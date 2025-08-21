"""
Data export functionality for ECaDP platform.

Provides various export formats and destinations for scraped data.
"""

import csv
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ExportConfig:
    """Configuration for data exports."""
    format: str
    destination: str  # file, url, service
    filename: Optional[str] = None
    include_metadata: bool = True
    compress: bool = False
    encryption: bool = False
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class ExportResult:
    """Result of an export operation."""
    success: bool
    file_path: Optional[str] = None
    url: Optional[str] = None
    record_count: int = 0
    file_size: int = 0
    export_time: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseExporter(ABC):
    """Base class for all data exporters."""
    
    def __init__(self, config: ExportConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to the specified format/destination."""
        pass
    
    def _prepare_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for export (cleaning, formatting)."""
        prepared_data = []
        
        for record in data:
            prepared_record = {}
            for key, value in record.items():
                # Convert datetime objects to ISO strings
                if isinstance(value, datetime):
                    prepared_record[key] = value.isoformat()
                # Convert None to empty string for better CSV compatibility
                elif value is None:
                    prepared_record[key] = ""
                else:
                    prepared_record[key] = value
            
            prepared_data.append(prepared_record)
        
        return prepared_data
    
    def _add_metadata(self, result: ExportResult, data: List[Dict[str, Any]]) -> None:
        """Add metadata to export result if enabled."""
        if self.config.include_metadata:
            result.metadata.update({
                'export_timestamp': datetime.now().isoformat(),
                'record_count': len(data),
                'format': self.config.format,
                'exporter': self.__class__.__name__,
                'config': self.config.custom_options
            })


class CSVExporter(BaseExporter):
    """Export data to CSV format."""
    
    def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to CSV file."""
        result = ExportResult(success=False, record_count=len(data))
        
        try:
            if not data:
                result.error_message = "No data to export"
                return result
            
            # Prepare data
            prepared_data = self._prepare_data(data)
            
            # Generate filename if not provided
            filename = self.config.filename or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            file_path = Path(filename)
            
            # Write CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if prepared_data:
                    fieldnames = prepared_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(prepared_data)
            
            # Set result properties
            result.success = True
            result.file_path = str(file_path.absolute())
            result.file_size = file_path.stat().st_size
            
            self._add_metadata(result, data)
            
            self.logger.info(f"Successfully exported {len(data)} records to {file_path}")
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"CSV export failed: {e}")
        
        return result


class JSONExporter(BaseExporter):
    """Export data to JSON format."""
    
    def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to JSON file."""
        result = ExportResult(success=False, record_count=len(data))
        
        try:
            # Prepare data
            prepared_data = self._prepare_data(data)
            
            # Generate filename if not provided
            filename = self.config.filename or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = Path(filename)
            
            # Create export object
            export_object = {
                'data': prepared_data,
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'record_count': len(prepared_data),
                    'format': 'json'
                } if self.config.include_metadata else {}
            }
            
            # Write JSON
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_object, jsonfile, indent=2, ensure_ascii=False)
            
            # Set result properties
            result.success = True
            result.file_path = str(file_path.absolute())
            result.file_size = file_path.stat().st_size
            
            self._add_metadata(result, data)
            
            self.logger.info(f"Successfully exported {len(data)} records to {file_path}")
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"JSON export failed: {e}")
        
        return result


class ExcelExporter(BaseExporter):
    """Export data to Excel format."""
    
    def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to Excel file."""
        result = ExportResult(success=False, record_count=len(data))
        
        try:
            if not data:
                result.error_message = "No data to export"
                return result
            
            # Prepare data
            prepared_data = self._prepare_data(data)
            
            # Generate filename if not provided
            filename = self.config.filename or f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path = Path(filename)
            
            # Create DataFrame
            df = pd.DataFrame(prepared_data)
            
            # Write Excel with multiple sheets if specified
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Add metadata sheet if enabled
                if self.config.include_metadata:
                    metadata_df = pd.DataFrame([{
                        'Property': 'Export Timestamp',
                        'Value': datetime.now().isoformat()
                    }, {
                        'Property': 'Record Count', 
                        'Value': len(data)
                    }, {
                        'Property': 'Format',
                        'Value': 'Excel'
                    }])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            # Set result properties
            result.success = True
            result.file_path = str(file_path.absolute())
            result.file_size = file_path.stat().st_size
            
            self._add_metadata(result, data)
            
            self.logger.info(f"Successfully exported {len(data)} records to {file_path}")
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"Excel export failed: {e}")
        
        return result


class GoogleSheetsExporter(BaseExporter):
    """Export data to Google Sheets."""
    
    def __init__(self, config: ExportConfig, credentials_path: Optional[str] = None):
        super().__init__(config)
        self.credentials_path = credentials_path
    
    def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to Google Sheets."""
        result = ExportResult(success=False, record_count=len(data))
        
        try:
            # Note: This would require Google Sheets API setup
            # For now, we'll create a CSV and note that it needs Google Sheets integration
            
            result.error_message = "Google Sheets integration not yet implemented. Use CSV export instead."
            self.logger.warning("Google Sheets export attempted but not implemented")
            
            # Fallback to CSV export
            csv_config = ExportConfig(
                format="csv",
                destination=self.config.destination,
                filename=self.config.filename or f"google_sheets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            csv_exporter = CSVExporter(csv_config)
            return csv_exporter.export(data, **kwargs)
            
        except Exception as e:
            result.error_message = str(e)
            self.logger.error(f"Google Sheets export failed: {e}")
        
        return result


class ExportManager:
    """Manages and coordinates different export operations."""
    
    def __init__(self):
        self.exporters = {
            'csv': CSVExporter,
            'json': JSONExporter, 
            'excel': ExcelExporter,
            'xlsx': ExcelExporter,
            'google_sheets': GoogleSheetsExporter
        }
    
    def export_data(self, data: List[Dict[str, Any]], 
                   export_format: str, 
                   config: Optional[ExportConfig] = None,
                   **kwargs) -> ExportResult:
        """
        Export data using the specified format.
        
        Args:
            data: List of records to export
            export_format: Format to export to (csv, json, excel, etc.)
            config: Export configuration
            **kwargs: Additional arguments passed to exporter
            
        Returns:
            ExportResult with operation details
        """
        if export_format.lower() not in self.exporters:
            return ExportResult(
                success=False,
                error_message=f"Unsupported export format: {export_format}"
            )
        
        # Create default config if none provided
        if not config:
            config = ExportConfig(
                format=export_format.lower(),
                destination="file"
            )
        
        # Get exporter class and create instance
        exporter_class = self.exporters[export_format.lower()]
        exporter = exporter_class(config)
        
        # Perform export
        return exporter.export(data, **kwargs)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return list(self.exporters.keys())
    
    def register_exporter(self, format_name: str, exporter_class: type):
        """Register a custom exporter."""
        self.exporters[format_name.lower()] = exporter_class
