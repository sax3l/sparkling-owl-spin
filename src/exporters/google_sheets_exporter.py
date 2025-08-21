"""
Google Sheets Exporter for exporting data to Google Sheets.
Supports authentication and real-time data updates.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class GoogleSheetsExporter(BaseExporter):
    """Exporter for Google Sheets."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.credentials_path = config.format_options.get('credentials_path')
        self.spreadsheet_id = config.format_options.get('spreadsheet_id')
        self.sheet_name = config.format_options.get('sheet_name', 'Sheet1')
        self.append_mode = config.format_options.get('append_mode', False)
        self.clear_before_write = config.format_options.get('clear_before_write', True)
        self.include_headers = config.format_options.get('include_headers', True)
    
    def validate_config(self) -> bool:
        """Validate Google Sheets exporter configuration."""
        try:
            if not GSHEETS_AVAILABLE:
                self.logger.error("Google Sheets export requires gspread and google-auth packages")
                return False
            
            if not self.credentials_path:
                self.logger.error("Credentials path is required for Google Sheets export")
                return False
            
            if not self.spreadsheet_id:
                self.logger.error("Spreadsheet ID is required for Google Sheets export")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to Google Sheets."""
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
                    output_location=f"Sheet: {self.sheet_name}",
                    export_time=datetime.utcnow(),
                    metadata=self.create_metadata(0)
                )
            
            # Write to Google Sheets
            await self._write_sheets(prepared_data)
            
            location = f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
            self.logger.info(f"Exported {len(prepared_data)} records to Google Sheets: {location}")
            
            return ExportResult(
                success=True,
                records_exported=len(prepared_data),
                output_location=location,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(len(prepared_data))
            )
            
        except Exception as e:
            self.logger.error(f"Google Sheets export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_sheets(self, data: List[Dict[str, Any]]):
        """Write data to Google Sheets."""
        def write_sync():
            # Authenticate
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
            client = gspread.authorize(creds)
            
            # Open spreadsheet
            spreadsheet = client.open_by_key(self.spreadsheet_id)
            
            # Get or create worksheet
            try:
                worksheet = spreadsheet.worksheet(self.sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title=self.sheet_name,
                    rows=len(data) + 100,
                    cols=len(data[0].keys()) if data else 10
                )
            
            # Prepare data for upload
            if not data:
                return
            
            # Get headers from first record
            headers = list(data[0].keys())
            
            # Convert data to list of lists
            rows = []
            if self.include_headers:
                rows.append(headers)
            
            for record in data:
                row = [str(record.get(header, '')) for header in headers]
                rows.append(row)
            
            # Clear existing data if requested
            if self.clear_before_write and not self.append_mode:
                worksheet.clear()
            
            # Upload data
            if self.append_mode and not self.clear_before_write:
                # Find the next empty row
                existing_data = worksheet.get_all_values()
                start_row = len(existing_data) + 1
                
                # Skip headers if appending
                if self.include_headers and existing_data:
                    rows = rows[1:]
                
                # Append data
                if rows:
                    worksheet.append_rows(rows)
            else:
                # Replace all data
                worksheet.update('A1', rows)
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, len(headers))
        
        await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter only if dependencies are available
if GSHEETS_AVAILABLE:
    ExporterRegistry.register('google_sheets', GoogleSheetsExporter)
    ExporterRegistry.register('gsheets', GoogleSheetsExporter)
