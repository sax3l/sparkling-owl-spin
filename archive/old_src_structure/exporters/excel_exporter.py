"""
Excel Exporter for exporting data to Excel format.
Supports multiple sheets, formatting, and compression.
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

try:
    import pandas as pd
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class ExcelExporter(BaseExporter):
    """Exporter for Excel format files."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.sheet_name = config.format_options.get('sheet_name', 'Sheet1')
        self.include_index = config.format_options.get('include_index', False)
        self.freeze_header = config.format_options.get('freeze_header', True)
        self.auto_adjust_columns = config.format_options.get('auto_adjust_columns', True)
    
    def validate_config(self) -> bool:
        """Validate Excel exporter configuration."""
        try:
            if not EXCEL_AVAILABLE:
                self.logger.error("Excel export requires pandas and openpyxl packages")
                return False
                
            if not self.config.output_path:
                self.logger.error("Output path is required for Excel export")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to Excel format."""
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
                    output_location="",
                    export_time=datetime.utcnow(),
                    metadata=self.create_metadata(0)
                )
            
            # Generate output filename
            output_path = kwargs.get('output_path', self.config.output_path)
            if not output_path.endswith('.xlsx'):
                output_path = f"{output_path}.xlsx"
            
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write Excel file
            await self._write_excel(output_path, prepared_data)
            
            self.logger.info(f"Exported {len(prepared_data)} records to {output_path}")
            
            return ExportResult(
                success=True,
                records_exported=len(prepared_data),
                output_location=output_path,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(len(prepared_data))
            )
            
        except Exception as e:
            self.logger.error(f"Excel export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_excel(self, output_path: str, data: List[Dict[str, Any]]):
        """Write data to Excel file."""
        def write_sync():
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Write to Excel with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(
                    writer,
                    sheet_name=self.sheet_name,
                    index=self.include_index
                )
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets[self.sheet_name]
                
                # Apply formatting
                if self.freeze_header:
                    worksheet.freeze_panes = worksheet['A2']
                
                if self.auto_adjust_columns:
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
        
        await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter only if dependencies are available
if EXCEL_AVAILABLE:
    ExporterRegistry.register('excel', ExcelExporter)
