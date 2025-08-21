"""
JSON Exporter for exporting data to JSON format.
Supports various JSON configurations including pretty printing and compression.
"""

import json
import gzip
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class JSONExporter(BaseExporter):
    """Exporter for JSON format files."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.indent = config.format_options.get('indent', 2)
        self.ensure_ascii = config.format_options.get('ensure_ascii', False)
        self.sort_keys = config.format_options.get('sort_keys', False)
        self.encoding = config.format_options.get('encoding', 'utf-8')
        self.array_format = config.format_options.get('array_format', True)  # True for array, False for JSONL
    
    def validate_config(self) -> bool:
        """Validate JSON exporter configuration."""
        try:
            # Check if output path is specified
            if not self.config.output_path:
                self.logger.error("Output path is required for JSON export")
                return False
            
            # Validate indent
            if self.indent is not None and not isinstance(self.indent, int):
                self.logger.error("Indent must be an integer or None")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to JSON format."""
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
            
            # Generate output filename
            output_path = kwargs.get('output_path', self.config.output_path)
            if self.array_format and not output_path.endswith('.json'):
                output_path = f"{output_path}.json"
            elif not self.array_format and not output_path.endswith('.jsonl'):
                output_path = f"{output_path}.jsonl"
            
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON file
            if self.config.compress:
                await self._write_compressed_json(output_path, prepared_data)
                output_path = f"{output_path}.gz"
            else:
                await self._write_json(output_path, prepared_data)
            
            self.logger.info(f"Exported {len(prepared_data)} records to {output_path}")
            
            return ExportResult(
                success=True,
                records_exported=len(prepared_data),
                output_location=output_path,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(len(prepared_data))
            )
            
        except Exception as e:
            self.logger.error(f"JSON export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_json(self, output_path: str, data: List[Dict[str, Any]]):
        """Write data to JSON file."""
        def write_sync():
            with open(output_path, 'w', encoding=self.encoding) as jsonfile:
                if self.array_format:
                    # Write as JSON array
                    json.dump(
                        data,
                        jsonfile,
                        indent=self.indent,
                        ensure_ascii=self.ensure_ascii,
                        sort_keys=self.sort_keys,
                        default=str  # Handle datetime and other non-serializable objects
                    )
                else:
                    # Write as JSON Lines (JSONL)
                    for record in data:
                        json.dump(
                            record,
                            jsonfile,
                            ensure_ascii=self.ensure_ascii,
                            sort_keys=self.sort_keys,
                            default=str
                        )
                        jsonfile.write('\n')
        
        await asyncio.get_event_loop().run_in_executor(None, write_sync)
    
    async def _write_compressed_json(self, output_path: str, data: List[Dict[str, Any]]):
        """Write data to compressed JSON file."""
        def write_sync():
            with gzip.open(f"{output_path}.gz", 'wt', encoding=self.encoding) as jsonfile:
                if self.array_format:
                    # Write as JSON array
                    json.dump(
                        data,
                        jsonfile,
                        indent=self.indent,
                        ensure_ascii=self.ensure_ascii,
                        sort_keys=self.sort_keys,
                        default=str
                    )
                else:
                    # Write as JSON Lines (JSONL)
                    for record in data:
                        json.dump(
                            record,
                            jsonfile,
                            ensure_ascii=self.ensure_ascii,
                            sort_keys=self.sort_keys,
                            default=str
                        )
                        jsonfile.write('\n')
        
        await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter
ExporterRegistry.register('json', JSONExporter)
ExporterRegistry.register('jsonl', JSONExporter)
