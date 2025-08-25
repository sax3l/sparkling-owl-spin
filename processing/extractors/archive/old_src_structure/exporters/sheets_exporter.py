"""
Sheets Exporter - alias for Google Sheets Exporter.
Provides backwards compatibility and shorter name.
"""

from .google_sheets_exporter import GoogleSheetsExporter
from .base import ExporterRegistry

# Create alias
SheetsExporter = GoogleSheetsExporter

# Register with shorter name
try:
    ExporterRegistry.register('sheets', SheetsExporter)
except:
    # If GoogleSheetsExporter is not available, skip registration
    pass
