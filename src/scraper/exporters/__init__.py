"""Data exporters for the scraper system."""

from .base import (
    BaseExporter,
    ExportConfig,
    ExportResult,
    ExportFormat,
    MultiFormatExporter,
    create_exporter,
    validate_data_structure,
    sanitize_field_names
)

from .csv_exporter import CSVExporter
from .json_exporter import JSONExporter
from .excel_exporter import ExcelExporter

# Optional exporters that require additional dependencies
try:
    from .google_sheets_exporter import GoogleSheetsExporter
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GoogleSheetsExporter = None
    GOOGLE_SHEETS_AVAILABLE = False

__all__ = [
    'BaseExporter',
    'ExportConfig', 
    'ExportResult',
    'ExportFormat',
    'MultiFormatExporter',
    'CSVExporter',
    'JSONExporter',
    'ExcelExporter',
    'GoogleSheetsExporter',
    'create_exporter',
    'validate_data_structure',
    'sanitize_field_names',
    'GOOGLE_SHEETS_AVAILABLE'
]

# Factory function with fallbacks for missing dependencies
def get_exporter(format_type: ExportFormat, config: ExportConfig) -> BaseExporter:
    """
    Get exporter instance for the specified format.
    
    Args:
        format_type: Export format
        config: Export configuration
        
    Returns:
        Exporter instance
        
    Raises:
        ValueError: If format is not supported or dependencies are missing
    """
    if format_type == ExportFormat.CSV:
        return CSVExporter(config)
    elif format_type == ExportFormat.JSON:
        return JSONExporter(config)
    elif format_type == ExportFormat.EXCEL:
        return ExcelExporter(config)
    elif format_type == ExportFormat.GOOGLE_SHEETS:
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ValueError("Google Sheets export requires 'gspread' and 'google-auth' packages")
        return GoogleSheetsExporter(config)
    else:
        raise ValueError(f"Unsupported export format: {format_type.value}")


def get_available_formats() -> list[ExportFormat]:
    """
    Get list of available export formats based on installed dependencies.
    
    Returns:
        List of available export formats
    """
    formats = [
        ExportFormat.CSV,
        ExportFormat.JSON,
        ExportFormat.EXCEL,
    ]
    
    if GOOGLE_SHEETS_AVAILABLE:
        formats.append(ExportFormat.GOOGLE_SHEETS)
    
    return formats


def check_dependencies() -> dict[str, bool]:
    """
    Check which export dependencies are available.
    
    Returns:
        Dictionary mapping format to availability
    """
    dependencies = {
        'csv': True,  # Built-in
        'json': True,  # Built-in
        'excel': False,
        'google_sheets': GOOGLE_SHEETS_AVAILABLE
    }
    
    # Check for openpyxl (Excel)
    try:
        import openpyxl
        dependencies['excel'] = True
    except ImportError:
        pass
    
    return dependencies
