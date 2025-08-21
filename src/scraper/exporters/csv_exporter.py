"""CSV exporter for scraped data."""

import csv
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import gzip
import logging

from .base import BaseExporter, ExportResult, ExportConfig, ExportFormat


class CSVExporter(BaseExporter):
    """Export data to CSV format."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        
        # CSV-specific options
        self.delimiter = config.options.get('delimiter', ',')
        self.quotechar = config.options.get('quotechar', '"')
        self.quoting = getattr(csv, config.options.get('quoting', 'QUOTE_MINIMAL'))
        self.lineterminator = config.options.get('lineterminator', '\n')
        self.escapechar = config.options.get('escapechar', None)
    
    def export(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Export data to CSV file.
        
        Args:
            data: List of records to export
            metadata: Optional metadata about the export
            
        Returns:
            ExportResult with export details
        """
        try:
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
            
            # Ensure destination directory exists
            destination_path = Path(self.config.destination)
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            
            records_exported = 0
            file_size = 0
            
            # Determine if we should use compression
            use_compression = self.config.compression == 'gzip' or self.config.destination.endswith('.gz')
            
            # Open file with appropriate mode
            if use_compression:
                file_handle = gzip.open(destination_path, 'wt', encoding=self.config.encoding)
            else:
                file_handle = open(destination_path, 'w', encoding=self.config.encoding, newline='')
            
            try:
                # Get field names from first record
                fieldnames = list(prepared_data[0].keys())
                
                writer = csv.DictWriter(
                    file_handle,
                    fieldnames=fieldnames,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=self.quoting,
                    lineterminator=self.lineterminator,
                    escapechar=self.escapechar
                )
                
                # Write header if requested
                if self.config.include_headers:
                    writer.writeheader()
                
                # Process data in batches
                batches = self._batch_data(prepared_data)
                
                for batch in batches:
                    for record in batch:
                        # Convert all values to strings and handle None values
                        cleaned_record = {}
                        for key, value in record.items():
                            if value is None:
                                cleaned_record[key] = ''
                            elif isinstance(value, (list, dict)):
                                # Convert complex types to JSON strings
                                import json
                                cleaned_record[key] = json.dumps(value)
                            else:
                                cleaned_record[key] = str(value)
                        
                        writer.writerow(cleaned_record)
                        records_exported += 1
                
                # Get file size
                file_handle.flush()
                file_size = file_handle.tell() if hasattr(file_handle, 'tell') else 0
                
            finally:
                file_handle.close()
            
            # Verify file was created
            if destination_path.exists():
                actual_file_size = destination_path.stat().st_size
                file_size = actual_file_size
            
            self.logger.info(f"Successfully exported {records_exported} records to {self.config.destination}")
            
            return ExportResult(
                success=True,
                records_exported=records_exported,
                destination=self.config.destination,
                format=self.config.format,
                file_size=file_size
            )
            
        except Exception as e:
            return self._handle_errors(e, "CSV export")
    
    def validate_destination(self) -> bool:
        """
        Validate that the CSV destination is writable.
        
        Returns:
            True if destination is valid, False otherwise
        """
        try:
            destination_path = Path(self.config.destination)
            
            # Check if parent directory exists or can be created
            parent_dir = destination_path.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.logger.error(f"Cannot create destination directory: {e}")
                    return False
            
            # Check if we can write to the directory
            if not os.access(parent_dir, os.W_OK):
                self.logger.error(f"No write permission for directory: {parent_dir}")
                return False
            
            # If file exists, check if we can overwrite it
            if destination_path.exists():
                if not os.access(destination_path, os.W_OK):
                    self.logger.error(f"No write permission for file: {destination_path}")
                    return False
            
            # Try to create a test file
            test_file = parent_dir / f".test_write_{os.getpid()}"
            try:
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                self.logger.error(f"Cannot write to destination directory: {e}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Destination validation failed: {e}")
            return False
    
    def append_data(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Append data to existing CSV file.
        
        Args:
            data: List of records to append
            metadata: Optional metadata about the export
            
        Returns:
            ExportResult with append details
        """
        try:
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
            
            destination_path = Path(self.config.destination)
            
            # Check if file exists
            file_exists = destination_path.exists()
            write_headers = not file_exists and self.config.include_headers
            
            records_exported = 0
            
            # Open file in append mode
            use_compression = self.config.compression == 'gzip' or self.config.destination.endswith('.gz')
            
            if use_compression:
                # For gzip, we need to read existing content and rewrite
                existing_data = []
                if file_exists:
                    with gzip.open(destination_path, 'rt', encoding=self.config.encoding) as f:
                        existing_data = list(csv.DictReader(f))
                
                # Combine existing and new data
                all_data = existing_data + prepared_data
                
                # Export all data
                return self.export(all_data, metadata)
            else:
                with open(destination_path, 'a', encoding=self.config.encoding, newline='') as f:
                    fieldnames = list(prepared_data[0].keys())
                    
                    writer = csv.DictWriter(
                        f,
                        fieldnames=fieldnames,
                        delimiter=self.delimiter,
                        quotechar=self.quotechar,
                        quoting=self.quoting,
                        lineterminator=self.lineterminator,
                        escapechar=self.escapechar
                    )
                    
                    # Write header if this is a new file
                    if write_headers:
                        writer.writeheader()
                    
                    # Write data
                    for record in prepared_data:
                        # Clean record similar to export method
                        cleaned_record = {}
                        for key, value in record.items():
                            if value is None:
                                cleaned_record[key] = ''
                            elif isinstance(value, (list, dict)):
                                import json
                                cleaned_record[key] = json.dumps(value)
                            else:
                                cleaned_record[key] = str(value)
                        
                        writer.writerow(cleaned_record)
                        records_exported += 1
            
            self.logger.info(f"Successfully appended {records_exported} records to {self.config.destination}")
            
            return ExportResult(
                success=True,
                records_exported=records_exported,
                destination=self.config.destination,
                format=self.config.format,
                file_size=destination_path.stat().st_size if destination_path.exists() else 0
            )
            
        except Exception as e:
            return self._handle_errors(e, "CSV append")
    
    def read_csv_data(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read data from CSV file.
        
        Args:
            limit: Maximum number of records to read
            
        Returns:
            List of records from the CSV file
        """
        try:
            destination_path = Path(self.config.destination)
            
            if not destination_path.exists():
                return []
            
            data = []
            use_compression = self.config.compression == 'gzip' or self.config.destination.endswith('.gz')
            
            if use_compression:
                file_handle = gzip.open(destination_path, 'rt', encoding=self.config.encoding)
            else:
                file_handle = open(destination_path, 'r', encoding=self.config.encoding)
            
            try:
                reader = csv.DictReader(
                    file_handle,
                    delimiter=self.delimiter,
                    quotechar=self.quotechar,
                    quoting=self.quoting
                )
                
                for i, row in enumerate(reader):
                    if limit and i >= limit:
                        break
                    data.append(dict(row))
                
            finally:
                file_handle.close()
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read CSV data: {e}")
            return []
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the CSV file.
        
        Returns:
            Dictionary with file information
        """
        try:
            destination_path = Path(self.config.destination)
            
            if not destination_path.exists():
                return {"exists": False}
            
            stat = destination_path.stat()
            
            # Count rows (excluding header if present)
            row_count = 0
            use_compression = self.config.compression == 'gzip' or self.config.destination.endswith('.gz')
            
            if use_compression:
                with gzip.open(destination_path, 'rt', encoding=self.config.encoding) as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for _ in reader)
            else:
                with open(destination_path, 'r', encoding=self.config.encoding) as f:
                    reader = csv.reader(f)
                    row_count = sum(1 for _ in reader)
            
            # Adjust for header
            if self.config.include_headers and row_count > 0:
                row_count -= 1
            
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "row_count": row_count,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_compressed": use_compression
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            return {"exists": False, "error": str(e)}
