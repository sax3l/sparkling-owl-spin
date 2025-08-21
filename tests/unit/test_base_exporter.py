"""
Tests for base exporter functionality.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from src.exporters.base import (
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
    
    def test_prepare_data_basic(self):
        """Test data preparation without metadata."""
        config = ExportConfig(include_metadata=False)
        exporter = ConcreteExporter(config)
        
        test_data = [{"name": "John", "age": 30}]
        prepared = exporter.prepare_data(test_data)
        
        assert len(prepared) == 1
        assert prepared[0]["name"] == "John"
        assert prepared[0]["age"] == 30
        assert "_export_timestamp" not in prepared[0]
    
    def test_prepare_data_with_metadata(self):
        """Test data preparation with metadata."""
        config = ExportConfig(include_metadata=True)
        exporter = ConcreteExporter(config)
        
        test_data = [{"name": "John", "age": 30}]
        prepared = exporter.prepare_data(test_data)
        
        assert len(prepared) == 1
        assert prepared[0]["name"] == "John"
        assert prepared[0]["age"] == 30
        assert "_export_timestamp" in prepared[0]
        assert "_exporter" in prepared[0]
        assert prepared[0]["_exporter"] == "ConcreteExporter"
    
    def test_create_metadata(self):
        """Test metadata creation."""
        config = ExportConfig()
        exporter = ConcreteExporter(config)
        
        metadata = exporter.create_metadata(100)
        
        assert "export_timestamp" in metadata
        assert "exporter" in metadata
        assert metadata["exporter"] == "ConcreteExporter"
        assert metadata["record_count"] == 100
        assert "config" in metadata
    
    def test_validate_config_implementation(self):
        """Test validate_config implementation."""
        config = ExportConfig()
        exporter = ConcreteExporter(config)
        
        assert exporter.validate_config() is True
    
    @pytest.mark.asyncio
    async def test_export_batched_empty_data(self):
        """Test export_batched with empty data."""
        config = ExportConfig()
        exporter = ConcreteExporter(config)
        
        result = await exporter.export_batched([])
        
        assert result.success is True
        assert result.records_exported == 0
    
    @pytest.mark.asyncio
    async def test_export_batched_single_batch(self):
        """Test export_batched with single batch."""
        config = ExportConfig(batch_size=10)
        exporter = ConcreteExporter(config)
        
        test_data = [{"id": i} for i in range(5)]
        result = await exporter.export_batched(test_data)
        
        assert result.success is True
        assert result.records_exported == 5
    
    @pytest.mark.asyncio
    async def test_export_batched_multiple_batches(self):
        """Test export_batched with multiple batches."""
        config = ExportConfig(batch_size=3)
        exporter = ConcreteExporter(config)
        
        test_data = [{"id": i} for i in range(10)]
        result = await exporter.export_batched(test_data)
        
        assert result.success is True
        assert result.records_exported == 10
    
    @pytest.mark.asyncio
    async def test_export_batched_failure(self):
        """Test export_batched with failure."""
        config = ExportConfig(batch_size=3)
        exporter = FailingExporter(config)
        
        test_data = [{"id": i} for i in range(5)]
        result = await exporter.export_batched(test_data)
        
        assert result.success is False
        assert result.error_message == "Test failure"


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
    
    @patch('src.exporters.base.Path.mkdir')
    def test_ensure_directory(self, mock_mkdir):
        """Test directory creation."""
        from pathlib import Path
        with patch('src.exporters.base.Path') as mock_path:
            mock_path_instance = Mock()
            mock_path.return_value = mock_path_instance
            
            result = ensure_directory("/test/path")
            
            mock_path.assert_called_once_with("/test/path")
            mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    
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
