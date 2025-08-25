"""
Exporter Factory - Create and manage different export formats
Supports CSV, JSON, BigQuery, GCS, and custom exporters
"""

import logging
from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod
from enum import Enum

from .csv_exporter import CSVExporter
from .bigquery_exporter import BigQueryExporter  
from .gcs_exporter import GCSExporter

class ExportFormat(Enum):
    CSV = "csv"
    JSON = "json" 
    BIGQUERY = "bigquery"
    GCS = "gcs"
    JSONLINES = "jsonlines"
    PARQUET = "parquet"

class BaseExporter(ABC):
    """Base class for all exporters"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> bool:
        """Export data to destination"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate exporter configuration"""
        pass

class JSONExporter(BaseExporter):
    """JSON file exporter"""
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(kwargs)
        self.file_path = file_path
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> bool:
        """Export data to JSON file"""
        import json
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(data)} records to {self.file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {str(e)}")
            return False
    
    def validate_config(self) -> bool:
        return bool(self.file_path)

class JSONLinesExporter(BaseExporter):
    """JSON Lines exporter"""
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(kwargs)
        self.file_path = file_path
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> bool:
        """Export data to JSONL file"""
        import json
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for record in data:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            self.logger.info(f"Exported {len(data)} records to {self.file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to JSONL: {str(e)}")
            return False
    
    def validate_config(self) -> bool:
        return bool(self.file_path)

class ParquetExporter(BaseExporter):
    """Parquet file exporter"""
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(kwargs)
        self.file_path = file_path
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> bool:
        """Export data to Parquet file"""
        try:
            import pandas as pd
            import pyarrow.parquet as pq
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Write to Parquet
            df.to_parquet(self.file_path, index=False)
            
            self.logger.info(f"Exported {len(data)} records to {self.file_path}")
            return True
            
        except ImportError:
            self.logger.error("pandas and pyarrow required for Parquet export")
            return False
        except Exception as e:
            self.logger.error(f"Failed to export to Parquet: {str(e)}")
            return False
    
    def validate_config(self) -> bool:
        return bool(self.file_path)

class ExporterFactory:
    """Factory for creating and managing exporters"""
    
    # Registry of available exporters
    _exporters: Dict[ExportFormat, Type[BaseExporter]] = {
        ExportFormat.CSV: CSVExporter,
        ExportFormat.JSON: JSONExporter,
        ExportFormat.BIGQUERY: BigQueryExporter,
        ExportFormat.GCS: GCSExporter,
        ExportFormat.JSONLINES: JSONLinesExporter,
        ExportFormat.PARQUET: ParquetExporter,
    }
    
    @classmethod
    def create_exporter(cls, 
                       format_type: ExportFormat | str,
                       **config) -> BaseExporter:
        """Create an exporter instance"""
        
        # Handle string format
        if isinstance(format_type, str):
            try:
                format_type = ExportFormat(format_type.lower())
            except ValueError:
                raise ValueError(f"Unsupported export format: {format_type}")
        
        # Get exporter class
        exporter_class = cls._exporters.get(format_type)
        if not exporter_class:
            raise ValueError(f"No exporter available for format: {format_type}")
        
        # Create and validate exporter
        exporter = exporter_class(**config)
        if not exporter.validate_config():
            raise ValueError(f"Invalid configuration for {format_type} exporter")
        
        return exporter
    
    @classmethod
    def register_exporter(cls, 
                         format_type: ExportFormat,
                         exporter_class: Type[BaseExporter]):
        """Register a custom exporter"""
        cls._exporters[format_type] = exporter_class
    
    @classmethod
    def get_available_formats(cls) -> List[str]:
        """Get list of available export formats"""
        return [fmt.value for fmt in cls._exporters.keys()]
    
    @classmethod
    async def export_data(cls,
                         data: List[Dict[str, Any]],
                         format_type: ExportFormat | str,
                         **config) -> bool:
        """Convenience method to export data in one call"""
        
        exporter = cls.create_exporter(format_type, **config)
        return await exporter.export(data, **config)

class MultiExporter:
    """Export data to multiple destinations simultaneously"""
    
    def __init__(self, exporters: List[BaseExporter]):
        self.exporters = exporters
        self.logger = logging.getLogger("multi_exporter")
    
    async def export_all(self, data: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Export to all configured exporters"""
        results = {}
        
        for exporter in self.exporters:
            exporter_name = exporter.__class__.__name__
            try:
                success = await exporter.export(data)
                results[exporter_name] = success
                
                if success:
                    self.logger.info(f"Successfully exported via {exporter_name}")
                else:
                    self.logger.warning(f"Failed to export via {exporter_name}")
                    
            except Exception as e:
                self.logger.error(f"Error in {exporter_name}: {str(e)}")
                results[exporter_name] = False
        
        return results
    
    @classmethod
    def from_configs(cls, export_configs: List[Dict[str, Any]]) -> 'MultiExporter':
        """Create MultiExporter from configuration list"""
        exporters = []
        
        for config in export_configs:
            format_type = config.pop('format')
            exporter = ExporterFactory.create_exporter(format_type, **config)
            exporters.append(exporter)
        
        return cls(exporters)

# Convenience functions
async def export_to_csv(data: List[Dict[str, Any]], file_path: str, **kwargs) -> bool:
    """Quick CSV export"""
    return await ExporterFactory.export_data(data, ExportFormat.CSV, file_path=file_path, **kwargs)

async def export_to_json(data: List[Dict[str, Any]], file_path: str, **kwargs) -> bool:
    """Quick JSON export"""
    return await ExporterFactory.export_data(data, ExportFormat.JSON, file_path=file_path, **kwargs)

async def export_to_bigquery(data: List[Dict[str, Any]], 
                           dataset: str, 
                           table: str, 
                           **kwargs) -> bool:
    """Quick BigQuery export"""
    return await ExporterFactory.export_data(
        data, 
        ExportFormat.BIGQUERY, 
        dataset=dataset, 
        table=table, 
        **kwargs
    )

# Example usage configurations
EXAMPLE_EXPORT_CONFIGS = {
    'csv_local': {
        'format': 'csv',
        'file_path': 'data/exports/crawl_results.csv'
    },
    'json_local': {
        'format': 'json', 
        'file_path': 'data/exports/crawl_results.json'
    },
    'bigquery_prod': {
        'format': 'bigquery',
        'dataset': 'crawl_data',
        'table': 'web_pages',
        'project_id': 'your-project-id'
    },
    'gcs_backup': {
        'format': 'gcs',
        'bucket': 'crawl-backups',
        'prefix': 'daily-crawls/'
    }
}
