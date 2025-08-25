"""
Export registry initialization and default exporters.
"""

from .base import ExporterRegistry, ExportManager

# Global registry instance
_global_registry = None

def get_export_registry() -> ExporterRegistry:
    """Get the global export registry with default exporters"""
    global _global_registry
    if _global_registry is None:
        _global_registry = ExporterRegistry()
        
        # Register default exporters when they're created
        # _global_registry.register('csv', CSVExporter)
        # _global_registry.register('json', JSONExporter)
        # _global_registry.register('excel', ExcelExporter)
        
    return _global_registry

def get_export_manager() -> ExportManager:
    """Get export manager with default registry"""
    return ExportManager(get_export_registry())
