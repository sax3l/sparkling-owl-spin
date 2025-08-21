"""JSON exporter for scraped data."""

import json
import os
from typing import Any, Dict, List, Optional
from pathlib import Path
import gzip
from datetime import datetime
import logging

from .base import BaseExporter, ExportResult, ExportConfig, ExportFormat


class JSONExporter(BaseExporter):
    """Export data to JSON format."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        
        # JSON-specific options
        self.indent = config.options.get('indent', 2)
        self.ensure_ascii = config.options.get('ensure_ascii', False)
        self.sort_keys = config.options.get('sort_keys', False)
        self.separators = config.options.get('separators', (',', ': '))
        self.array_format = config.options.get('array_format', True)  # True for array, False for line-delimited JSON
    
    def export(self, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> ExportResult:
        """
        Export data to JSON file.
        
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
            
            # Create the export structure
            if self.config.include_metadata and metadata:
                export_data = {
                    "metadata": metadata,
                    "data": prepared_data,
                    "export_info": {
                        "total_records": len(prepared_data),
                        "format": self.config.format.value,
                        "exported_at": datetime.now().isoformat()
                    }
                }
            else:
                export_data = prepared_data
            
            # Open file with appropriate mode
            if use_compression:
                file_handle = gzip.open(destination_path, 'wt', encoding=self.config.encoding)
            else:
                file_handle = open(destination_path, 'w', encoding=self.config.encoding)
            
            try:
                if self.array_format:
                    # Export as single JSON array/object
                    json.dump(
                        export_data,
                        file_handle,
                        indent=self.indent,
                        ensure_ascii=self.ensure_ascii,
                        sort_keys=self.sort_keys,
                        separators=self.separators,
                        default=self._json_serializer
                    )
                    records_exported = len(prepared_data)
                else:
                    # Export as line-delimited JSON (JSONL/NDJSON)
                    if isinstance(export_data, dict) and 'data' in export_data:
                        # Write metadata first if present
                        if 'metadata' in export_data:
                            metadata_line = {"_type": "metadata", **export_data['metadata']}
                            file_handle.write(json.dumps(metadata_line, default=self._json_serializer) + '\n')
                        
                        # Write each data record as a separate line
                        for record in export_data['data']:
                            file_handle.write(json.dumps(record, default=self._json_serializer) + '\n')
                            records_exported += 1
                    else:
                        # Write each record as a separate line
                        for record in export_data:
                            file_handle.write(json.dumps(record, default=self._json_serializer) + '\n')
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
            return self._handle_errors(e, "JSON export")
    
    def validate_destination(self) -> bool:
        """
        Validate that the JSON destination is writable.
        
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
        Append data to existing JSON file.
        
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
            
            if self.array_format:
                # For array format, we need to read existing data and merge
                existing_data = []
                existing_metadata = None
                
                if destination_path.exists():
                    existing_json = self.read_json_data()
                    if isinstance(existing_json, dict) and 'data' in existing_json:
                        existing_data = existing_json.get('data', [])
                        existing_metadata = existing_json.get('metadata', {})
                    elif isinstance(existing_json, list):
                        existing_data = existing_json
                
                # Merge metadata
                if existing_metadata and metadata:
                    merged_metadata = existing_metadata.copy()
                    merged_metadata.update(metadata)
                    metadata = merged_metadata
                
                # Combine existing and new data
                all_data = existing_data + prepared_data
                
                # Export all data
                return self.export(all_data, metadata)
            else:
                # For line-delimited JSON, we can simply append
                records_exported = 0
                use_compression = self.config.compression == 'gzip' or self.config.destination.endswith('.gz')
                
                if use_compression:
                    # For gzip, we need to read existing content and rewrite
                    existing_data = self.read_json_data()
                    if isinstance(existing_data, list):
                        all_data = existing_data + prepared_data
                    else:
                        all_data = prepared_data
                    return self.export(all_data, metadata)
                else:
                    with open(destination_path, 'a', encoding=self.config.encoding) as f:
                        for record in prepared_data:
                            f.write(json.dumps(record, default=self._json_serializer) + '\n')
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
            return self._handle_errors(e, "JSON append")
    
    def read_json_data(self, limit: Optional[int] = None) -> Any:
        """
        Read data from JSON file.
        
        Args:
            limit: Maximum number of records to read (for line-delimited JSON)
            
        Returns:
            Data from the JSON file
        """
        try:
            destination_path = Path(self.config.destination)
            
            if not destination_path.exists():
                return [] if self.array_format else None
            
            use_compression = self.config.compression == 'gzip' or self.config.destination.endswith('.gz')
            
            if use_compression:
                file_handle = gzip.open(destination_path, 'rt', encoding=self.config.encoding)
            else:
                file_handle = open(destination_path, 'r', encoding=self.config.encoding)
            
            try:
                if self.array_format:
                    # Read as single JSON object/array
                    return json.load(file_handle)
                else:
                    # Read as line-delimited JSON
                    data = []
                    for i, line in enumerate(file_handle):
                        if limit and i >= limit:
                            break
                        line = line.strip()
                        if line:
                            data.append(json.loads(line))
                    return data
                
            finally:
                file_handle.close()
            
        except Exception as e:
            self.logger.error(f"Failed to read JSON data: {e}")
            return [] if self.array_format else None
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the JSON file.
        
        Returns:
            Dictionary with file information
        """
        try:
            destination_path = Path(self.config.destination)
            
            if not destination_path.exists():
                return {"exists": False}
            
            stat = destination_path.stat()
            
            # Try to determine record count
            record_count = 0
            try:
                data = self.read_json_data()
                if isinstance(data, dict) and 'data' in data:
                    record_count = len(data['data'])
                elif isinstance(data, list):
                    record_count = len(data)
            except Exception:
                record_count = -1  # Unknown
            
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "record_count": record_count,
                "modified_time": stat.st_mtime,
                "created_time": stat.st_ctime,
                "is_compressed": self.config.compression == 'gzip' or self.config.destination.endswith('.gz'),
                "format": "array" if self.array_format else "line_delimited"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info: {e}")
            return {"exists": False, "error": str(e)}
    
    def _json_serializer(self, obj: Any) -> str:
        """
        Custom JSON serializer for complex objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serializable representation
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    def validate_json_structure(self, data: Any) -> bool:
        """
        Validate that data can be serialized to JSON.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is JSON-serializable, False otherwise
        """
        try:
            json.dumps(data, default=self._json_serializer)
            return True
        except Exception as e:
            self.logger.warning(f"Data is not JSON-serializable: {e}")
            return False
    
    def pretty_print_preview(self, data: List[Dict[str, Any]], max_records: int = 5) -> str:
        """
        Create a pretty-printed preview of the data.
        
        Args:
            data: Data to preview
            max_records: Maximum number of records to include in preview
            
        Returns:
            Pretty-printed JSON string
        """
        try:
            preview_data = data[:max_records] if len(data) > max_records else data
            
            preview_obj = {
                "preview": True,
                "showing": f"{len(preview_data)} of {len(data)} records",
                "data": preview_data
            }
            
            return json.dumps(
                preview_obj,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
                sort_keys=self.sort_keys,
                separators=self.separators,
                default=self._json_serializer
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create preview: {e}")
            return f"Preview failed: {str(e)}"
