"""
CSV Exporter for exporting data to CSV format.
Supports various CSV configurations and compression options.
"""

import csv
import gzip
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class CSVExporter(BaseExporter):
    """Exporter for CSV format files."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.delimiter = config.format_options.get('delimiter', ',')
        self.quotechar = config.format_options.get('quotechar', '"')
        self.encoding = config.format_options.get('encoding', 'utf-8')
        self.include_headers = config.format_options.get('include_headers', True)
    
    def validate_config(self) -> bool:
        """Validate CSV exporter configuration."""
        try:
            # Check if output path is specified
            if not self.config.output_path:
                self.logger.error("Output path is required for CSV export")
                return False
            
            # Validate delimiter
            if len(self.delimiter) != 1:
                self.logger.error("Delimiter must be a single character")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to CSV format."""
        if not self.validate_config():
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message="Invalid configuration"
            )
        
        try:
            # Prepare data
            prepared_data = self.prepare_data(data)
            
            if not prepared_data:
                return ExportResult(
                    success=True,
                    records_exported=0,
                    output_location="",
                    export_time=datetime.utcnow(),
                    metadata=self.create_metadata(0)
                )
            
            # Generate output filename
            output_path = kwargs.get('output_path', self.config.output_path)
            if not output_path.endswith('.csv'):
                output_path = f"{output_path}.csv"
            
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Get fieldnames from first record
            fieldnames = list(prepared_data[0].keys())
            
            # Write CSV file
            if self.config.compress:
                await self._write_compressed_csv(output_path, prepared_data, fieldnames)
                output_path = f"{output_path}.gz"
            else:
                await self._write_csv(output_path, prepared_data, fieldnames)
            
            self.logger.info(f"Exported {len(prepared_data)} records to {output_path}")
            
            return ExportResult(
                success=True,
                records_exported=len(prepared_data),
                output_location=output_path,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(len(prepared_data))
            )
            
        except Exception as e:
            self.logger.error(f"CSV export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_csv(self, output_path: str, data: List[Dict[str, Any]], fieldnames: List[str]):
        """Write data to CSV file."""
        def write_sync():
            with open(output_path, 'w', newline='', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=csv.QUOTE_MINIMAL
                )
                
                if self.include_headers:
                    writer.writeheader()
                
                for row in data:
                    # Handle None values
                    clean_row = {k: (v if v is not None else '') for k, v in row.items()}
                    writer.writerow(clean_row)
        
        await asyncio.get_event_loop().run_in_executor(None, write_sync)
    
    async def _write_compressed_csv(self, output_path: str, data: List[Dict[str, Any]], fieldnames: List[str]):
        """Write data to compressed CSV file."""
        def write_sync():
            with gzip.open(f"{output_path}.gz", 'wt', encoding=self.encoding) as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=csv.QUOTE_MINIMAL
                )
                
                if self.include_headers:
                    writer.writeheader()
                
                for row in data:
                    # Handle None values
                    clean_row = {k: (v if v is not None else '') for k, v in row.items()}
                    writer.writerow(clean_row)
        
        await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter
ExporterRegistry.register('csv', CSVExporter)
