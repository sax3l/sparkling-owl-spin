"""Google Sheets exporter for scraped data."""

import os
from typing import Any, Dict, List, Optional
import logging
from datetime import datetime
import json

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

from .base import BaseExporter, ExportResult, ExportConfig, ExportFormat


class GoogleSheetsExporter(BaseExporter):
    """Export data to Google Sheets."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        
        if not GSPREAD_AVAILABLE:
            raise ImportError("gspread is required for Google Sheets export. Install with: pip install gspread google-auth")
        
        # Google Sheets specific options
        self.credentials_file = config.options.get('credentials_file')
        self.credentials_json = config.options.get('credentials_json')
        self.sheet_name = config.options.get('sheet_name', 'Data')
        self.spreadsheet_id = config.options.get('spreadsheet_id')
        self.spreadsheet_name = config.options.get('spreadsheet_name')
        self.share_with = config.options.get('share_with', [])  # List of emails to share with
        self.max_rows_per_batch = config.options.get('max_rows_per_batch', 1000)
        self.clear_existing = config.options.get('clear_existing', False)
        
        # Initialize Google Sheets client
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Google Sheets client with credentials."""
        try:
            # Define required scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = None
            
            if self.credentials_json:
                # Use credentials from JSON string
                credentials_dict = json.loads(self.credentials_json)
                credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
            elif self.credentials_file:
                # Use credentials from file
                credentials = Credentials.from_service_account_file(self.credentials_file, scopes=scopes)
            else:
                # Try to use default credentials from environment
                try:
                    credentials = Credentials.from_service_account_file(
                        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
                        scopes=scopes
                    )
                except Exception:
                    self.logger.error("No valid Google credentials found. Please provide credentials_file or credentials_json")
                    return
            
            self.client = gspread.authorize(credentials)
            self.logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise
    
    def export(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Export data to Google Sheets.
        
        Args:
            data: List of records to export
            metadata: Optional metadata about the export
            
        Returns:
            ExportResult with export details
        """
        try:
            if not self.client:
                raise Exception("Google Sheets client not initialized")
            
            if not data:
                return ExportResult(
                    success=True,
                    records_exported=0,
                    destination=self.config.destination,
                    format=self.config.format,
                    warnings=["No data to export"]
                )
            
            # Prepare data
            metadata = self._add_standard_metadata(metadata)
            prepared_data = self._prepare_data(data, metadata)
            
            # Get or create spreadsheet
            spreadsheet = self._get_or_create_spreadsheet()
            
            # Get or create worksheet
            worksheet = self._get_or_create_worksheet(spreadsheet, self.sheet_name)
            
            # Clear existing data if requested
            if self.clear_existing:
                worksheet.clear()
            
            records_exported = 0
            
            # Prepare data for Google Sheets
            if prepared_data:
                fieldnames = list(prepared_data[0].keys())
                
                # Convert data to 2D array
                sheet_data = []
                
                # Add headers if requested
                if self.config.include_headers:
                    sheet_data.append(fieldnames)
                
                # Add data rows
                for record in prepared_data:
                    row = []
                    for fieldname in fieldnames:
                        value = record.get(fieldname)
                        converted_value = self._convert_value_for_sheets(value)
                        row.append(converted_value)
                    sheet_data.append(row)
                    records_exported += 1
                
                # Upload data in batches
                self._upload_data_in_batches(worksheet, sheet_data)
                
                # Apply formatting
                if self.config.include_headers:
                    self._format_header_row(worksheet, len(fieldnames))
                
                # Auto-resize columns
                self._auto_resize_columns(worksheet, len(fieldnames))
            
            # Add metadata sheet if requested
            if self.config.include_metadata and metadata:
                self._add_metadata_worksheet(spreadsheet, metadata)
            
            # Share spreadsheet if emails provided
            if self.share_with:
                self._share_spreadsheet(spreadsheet)
            
            # Get spreadsheet URL
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            
            self.logger.info(f"Successfully exported {records_exported} records to Google Sheets: {spreadsheet_url}")
            
            return ExportResult(
                success=True,
                records_exported=records_exported,
                destination=spreadsheet_url,
                format=self.config.format
            )
            
        except Exception as e:
            return self._handle_errors(e, "Google Sheets export")
    
    def validate_destination(self) -> bool:
        """
        Validate that Google Sheets can be accessed.
        
        Returns:
            True if Google Sheets is accessible, False otherwise
        """
        try:
            if not self.client:
                self.logger.error("Google Sheets client not initialized")
                return False
            
            # Try to access Google Sheets API
            try:
                if self.spreadsheet_id:
                    # Try to open existing spreadsheet
                    self.client.open_by_key(self.spreadsheet_id)
                else:
                    # Try to list spreadsheets (just to test API access)
                    # This will fail if credentials are invalid
                    pass
                
                return True
                
            except Exception as e:
                self.logger.error(f"Cannot access Google Sheets API: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"Destination validation failed: {e}")
            return False
    
    def append_data(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Append data to existing Google Sheets.
        
        Args:
            data: List of records to append
            metadata: Optional metadata about the export
            
        Returns:
            ExportResult with append details
        """
        try:
            if not self.client:
                raise Exception("Google Sheets client not initialized")
            
            if not data:
                return ExportResult(
                    success=True,
                    records_exported=0,
                    destination=self.config.destination,
                    format=self.config.format,
                    warnings=["No data to append"]
                )
            
            # Prepare data
            metadata = self._add_standard_metadata(metadata)
            prepared_data = self._prepare_data(data, metadata)
            
            # Get spreadsheet
            spreadsheet = self._get_or_create_spreadsheet()
            worksheet = self._get_or_create_worksheet(spreadsheet, self.sheet_name)
            
            records_exported = 0
            
            if prepared_data:
                fieldnames = list(prepared_data[0].keys())
                
                # Find next empty row
                values = worksheet.get_all_values()
                next_row = len(values) + 1
                
                # If worksheet is empty, add headers
                if not values and self.config.include_headers:
                    worksheet.insert_row(fieldnames, 1)
                    next_row = 2
                
                # Prepare data rows
                rows_to_add = []
                for record in prepared_data:
                    row = []
                    for fieldname in fieldnames:
                        value = record.get(fieldname)
                        converted_value = self._convert_value_for_sheets(value)
                        row.append(converted_value)
                    rows_to_add.append(row)
                    records_exported += 1
                
                # Append data in batches
                for i in range(0, len(rows_to_add), self.max_rows_per_batch):
                    batch = rows_to_add[i:i + self.max_rows_per_batch]
                    range_name = f"A{next_row + i}:Z{next_row + i + len(batch) - 1}"
                    worksheet.update(range_name, batch)
            
            # Update metadata if present
            if self.config.include_metadata and metadata:
                self._update_metadata_worksheet(spreadsheet, metadata)
            
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            
            self.logger.info(f"Successfully appended {records_exported} records to Google Sheets: {spreadsheet_url}")
            
            return ExportResult(
                success=True,
                records_exported=records_exported,
                destination=spreadsheet_url,
                format=self.config.format
            )
            
        except Exception as e:
            return self._handle_errors(e, "Google Sheets append")
    
    def read_sheets_data(self, sheet_name: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read data from Google Sheets.
        
        Args:
            sheet_name: Name of sheet to read (default sheet if None)
            limit: Maximum number of records to read
            
        Returns:
            List of records from the Google Sheets
        """
        try:
            if not self.client:
                self.logger.error("Google Sheets client not initialized")
                return []
            
            spreadsheet = self._get_or_create_spreadsheet()
            
            if sheet_name:
                try:
                    worksheet = spreadsheet.worksheet(sheet_name)
                except gspread.WorksheetNotFound:
                    self.logger.warning(f"Worksheet '{sheet_name}' not found")
                    return []
            else:
                worksheet = spreadsheet.get_worksheet(0)  # First worksheet
            
            # Get all values
            values = worksheet.get_all_values()
            
            if not values:
                return []
            
            # Convert to list of dictionaries
            headers = values[0] if self.config.include_headers else [f"Column_{i+1}" for i in range(len(values[0]))]
            data_rows = values[1:] if self.config.include_headers else values
            
            data = []
            for i, row in enumerate(data_rows):
                if limit and i >= limit:
                    break
                
                record = {}
                for j, header in enumerate(headers):
                    value = row[j] if j < len(row) else ""
                    record[header] = value
                
                data.append(record)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read Google Sheets data: {e}")
            return []
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the Google Sheets file.
        
        Returns:
            Dictionary with file information
        """
        try:
            if not self.client:
                return {"exists": False, "error": "Client not initialized"}
            
            spreadsheet = self._get_or_create_spreadsheet()
            
            # Get basic spreadsheet info
            worksheets = spreadsheet.worksheets()
            
            worksheets_info = []
            total_records = 0
            
            for worksheet in worksheets:
                if worksheet.title != 'Metadata':
                    values = worksheet.get_all_values()
                    row_count = len(values)
                    if self.config.include_headers and row_count > 0:
                        row_count -= 1
                    
                    worksheets_info.append({
                        "name": worksheet.title,
                        "rows": row_count,
                        "columns": worksheet.col_count
                    })
                    total_records += row_count
            
            return {
                "exists": True,
                "spreadsheet_id": spreadsheet.id,
                "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}",
                "title": spreadsheet.title,
                "total_records": total_records,
                "worksheets": worksheets_info,
                "has_metadata": any(ws.title == 'Metadata' for ws in worksheets)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            return {"exists": False, "error": str(e)}
    
    def _get_or_create_spreadsheet(self):
        """Get existing spreadsheet or create new one."""
        try:
            if self.spreadsheet_id:
                # Open existing spreadsheet by ID
                return self.client.open_by_key(self.spreadsheet_id)
            elif self.spreadsheet_name:
                # Try to open by name, create if doesn't exist
                try:
                    return self.client.open(self.spreadsheet_name)
                except gspread.SpreadsheetNotFound:
                    return self.client.create(self.spreadsheet_name)
            else:
                # Create new spreadsheet with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                spreadsheet_name = f"Export_{timestamp}"
                return self.client.create(spreadsheet_name)
                
        except Exception as e:
            self.logger.error(f"Failed to get or create spreadsheet: {e}")
            raise
    
    def _get_or_create_worksheet(self, spreadsheet, sheet_name: str):
        """Get existing worksheet or create new one."""
        try:
            return spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)
    
    def _convert_value_for_sheets(self, value: Any) -> str:
        """Convert value to Google Sheets compatible format."""
        if value is None:
            return ""
        elif isinstance(value, bool):
            return str(value).upper()
        elif isinstance(value, (list, dict)):
            return json.dumps(value)
        elif isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return str(value)
    
    def _upload_data_in_batches(self, worksheet, data: List[List[Any]]) -> None:
        """Upload data to worksheet in batches."""
        for i in range(0, len(data), self.max_rows_per_batch):
            batch = data[i:i + self.max_rows_per_batch]
            start_row = i + 1
            end_row = start_row + len(batch) - 1
            
            # Calculate the range
            end_col = chr(ord('A') + len(batch[0]) - 1) if batch else 'A'
            range_name = f"A{start_row}:{end_col}{end_row}"
            
            worksheet.update(range_name, batch)
    
    def _format_header_row(self, worksheet, num_columns: int) -> None:
        """Apply formatting to header row."""
        try:
            # Format header row (bold, background color)
            end_col = chr(ord('A') + num_columns - 1)
            header_range = f"A1:{end_col}1"
            
            worksheet.format(header_range, {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
            })
            
            # Freeze header row
            worksheet.freeze(rows=1)
            
        except Exception as e:
            self.logger.warning(f"Failed to format header row: {e}")
    
    def _auto_resize_columns(self, worksheet, num_columns: int) -> None:
        """Auto-resize columns to fit content."""
        try:
            # Auto-resize columns
            for i in range(num_columns):
                col_letter = chr(ord('A') + i)
                worksheet.format(f"{col_letter}:{col_letter}", {
                    "textFormat": {"wrapStrategy": "WRAP"}
                })
                
        except Exception as e:
            self.logger.warning(f"Failed to auto-resize columns: {e}")
    
    def _add_metadata_worksheet(self, spreadsheet, metadata: Dict[str, Any]) -> None:
        """Add metadata worksheet."""
        try:
            metadata_sheet = self._get_or_create_worksheet(spreadsheet, "Metadata")
            metadata_sheet.clear()
            
            # Prepare metadata as rows
            metadata_rows = [["Key", "Value"]]
            for key, value in metadata.items():
                metadata_rows.append([str(key), str(value)])
            
            metadata_sheet.update("A1", metadata_rows)
            
            # Format metadata sheet
            metadata_sheet.format("A1:B1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
            })
            
        except Exception as e:
            self.logger.warning(f"Failed to add metadata worksheet: {e}")
    
    def _update_metadata_worksheet(self, spreadsheet, metadata: Dict[str, Any]) -> None:
        """Update existing metadata worksheet."""
        self._add_metadata_worksheet(spreadsheet, metadata)
    
    def _share_spreadsheet(self, spreadsheet) -> None:
        """Share spreadsheet with specified emails."""
        try:
            for email in self.share_with:
                spreadsheet.share(email, perm_type='user', role='writer')
                self.logger.info(f"Shared spreadsheet with {email}")
                
        except Exception as e:
            self.logger.warning(f"Failed to share spreadsheet: {e}")
