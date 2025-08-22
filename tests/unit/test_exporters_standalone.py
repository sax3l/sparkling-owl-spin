"""
Tests for exporter functionality - standalone version.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add src to path to import exporters directly
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from exporters.base import (
    BaseExporter, 
    ExportConfig, 
    ExportResult, 
    ExporterRegistry,
    sanitize_filename,
    ensure_directory,
    generate_filename
)


class ConcreteExporter(BaseExporter):
    """Concrete implementation for testing abstract BaseExporter."""
    
    async def export(self, data, **kwargs):
        """Test implementation of export method."""
        return ExportResult(
            success=True,
            records_exported=len(data),
            output_location=kwargs.get("output_path", "/test/output"),
            export_time=datetime.utcnow()
        )
    
    def validate_config(self):
        """Test implementation of validate_config method."""
        return True


class FailingExporter(BaseExporter):
    """Failing exporter for testing error handling."""
    
    async def export(self, data, **kwargs):
        """Test implementation that fails."""
        return ExportResult(
            success=False,
            records_exported=0,
            output_location="",
            export_time=datetime.utcnow(),
            error_message="Test failure"
        )
    
    def validate_config(self):
        """Test implementation of validate_config method."""
        return False


class TestExportConfig:
    """Test cases for ExportConfig class."""
    
    def test_export_config_defaults(self):
        """Test ExportConfig default values."""
        config = ExportConfig()
        assert config.output_path is None
        assert config.batch_size == 1000
        assert config.compress is False
        assert config.include_metadata is True
        assert config.format_options == {}
    
    def test_export_config_custom_values(self):
        """Test ExportConfig with custom values."""
        config = ExportConfig(
            output_path="/custom/path",
            batch_size=500,
            compress=True,
            include_metadata=False,
            format_options={"delimiter": ","}
        )
        assert config.output_path == "/custom/path"
        assert config.batch_size == 500
        assert config.compress is True
        assert config.include_metadata is False
        assert config.format_options == {"delimiter": ","}


class TestExportResult:
    """Test cases for ExportResult class."""
    
    def test_export_result_creation(self):
        """Test ExportResult creation."""
        timestamp = datetime.utcnow()
        result = ExportResult(
            success=True,
            records_exported=100,
            output_location="/test/output.csv",
            export_time=timestamp
        )
        assert result.success is True
        assert result.records_exported == 100
        assert result.output_location == "/test/output.csv"
        assert result.export_time == timestamp
        assert result.error_message is None
        assert result.metadata == {}
    
    def test_export_result_with_error(self):
        """Test ExportResult with error."""
        timestamp = datetime.utcnow()
        result = ExportResult(
            success=False,
            records_exported=0,
            output_location="",
            export_time=timestamp,
            error_message="Test error",
            metadata={"test": "value"}
        )
        assert result.success is False
        assert result.error_message == "Test error"
        assert result.metadata == {"test": "value"}


class TestBaseExporter:
    """Test cases for BaseExporter class."""
    
    def test_base_exporter_initialization(self):
        """Test that BaseExporter initializes correctly."""
        config = ExportConfig()
        exporter = ConcreteExporter(config)
        assert exporter is not None
        assert exporter.config == config
        assert exporter.logger is not None
    
    def test_base_exporter_is_abstract(self):
        """Test that BaseExporter cannot be instantiated directly."""
        config = ExportConfig()
        with pytest.raises(TypeError):
            BaseExporter(config)
    
    @pytest.mark.asyncio
    async def test_concrete_exporter_export(self):
        """Test that concrete exporter can export data."""
        config = ExportConfig()
        exporter = ConcreteExporter(config)
        
        test_data = [{"name": "John"}, {"name": "Jane"}]
        result = await exporter.export(test_data)
        
        assert result.success is True
        assert result.records_exported == 2


class TestExporterRegistry:
    """Test cases for ExporterRegistry class."""
    
    def setup_method(self):
        """Clean registry before each test."""
        ExporterRegistry._exporters.clear()
    
    def test_register_exporter(self):
        """Test registering an exporter."""
        ExporterRegistry.register("test", ConcreteExporter)
        assert "test" in ExporterRegistry._exporters
        assert ExporterRegistry._exporters["test"] == ConcreteExporter
    
    def test_get_exporter(self):
        """Test getting an exporter."""
        ExporterRegistry.register("test", ConcreteExporter)
        exporter_class = ExporterRegistry.get_exporter("test")
        assert exporter_class == ConcreteExporter
    
    def test_get_nonexistent_exporter(self):
        """Test getting a non-existent exporter."""
        exporter_class = ExporterRegistry.get_exporter("nonexistent")
        assert exporter_class is None
    
    def test_list_exporters(self):
        """Test listing exporters."""
        ExporterRegistry.register("test1", ConcreteExporter)
        ExporterRegistry.register("test2", FailingExporter)
        exporters = ExporterRegistry.list_exporters()
        assert "test1" in exporters
        assert "test2" in exporters
        assert len(exporters) == 2
    
    def test_create_exporter(self):
        """Test creating an exporter instance."""
        ExporterRegistry.register("test", ConcreteExporter)
        config = ExportConfig()
        exporter = ExporterRegistry.create_exporter("test", config)
        assert isinstance(exporter, ConcreteExporter)
        assert exporter.config == config
    
    def test_create_nonexistent_exporter(self):
        """Test creating a non-existent exporter."""
        config = ExportConfig()
        exporter = ExporterRegistry.create_exporter("nonexistent", config)
        assert exporter is None


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        result = sanitize_filename("test<>file|name?.txt")
        assert result == "test__file_name_.txt"
    
    def test_sanitize_filename_no_changes(self):
        """Test filename sanitization with clean filename."""
        result = sanitize_filename("clean_filename.txt")
        assert result == "clean_filename.txt"
    
    def test_generate_filename_without_timestamp(self):
        """Test filename generation without timestamp."""
        result = generate_filename("test", "csv", timestamp=False)
        assert result == "test.csv"
    
    def test_generate_filename_with_timestamp(self):
        """Test filename generation with timestamp."""
        result = generate_filename("test", "csv", timestamp=True)
        assert result.startswith("test_")
        assert result.endswith(".csv")
        assert len(result) > len("test.csv")
