"""
Exporter package initialization.
Registers all available exporters and provides a unified interface.
"""

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry, ExportManager

# Import all exporters to trigger registration
from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .excel_exporter import ExcelExporter
from .sheets_exporter import SheetsExporter
from .bigquery_exporter import BigQueryExporter
from .snowflake_exporter import SnowflakeExporter
from .elastic_exporter import ElasticExporter
from .google_sheets_exporter import GoogleSheetsExporter
from .opensearch_exporter import OpenSearchExporter

__all__ = [
    'BaseExporter',
    'ExportConfig', 
    'ExportResult',
    'ExporterRegistry',
    'ExportManager',
    'CSVExporter',
    'JSONExporter',
    'ExcelExporter',
    'SheetsExporter',
    'BigQueryExporter',
    'SnowflakeExporter',
    'ElasticExporter',
    'GoogleSheetsExporter',
    'OpenSearchExporter',
    'get_exporter',
    'list_exporters',
    'create_exporter'
]

# Convenience functions
def get_exporter(name: str):
    """Get an exporter class by name."""
    return ExporterRegistry.get_exporter(name)

def list_exporters():
    """List all available exporters."""
    return ExporterRegistry.list_exporters()

def create_exporter(name: str, config: ExportConfig):
    """Create an exporter instance."""
    return ExporterRegistry.create_exporter(name, config)
