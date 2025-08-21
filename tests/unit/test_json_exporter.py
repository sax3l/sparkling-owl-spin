"""
Tests for JSON exporter functionality.
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
from src.exporters.json_exporter import JSONExporter


class TestJSONExporter:
    """Test cases for JSONExporter class."""
    
    def test_json_exporter_initialization(self):
        """Test that JSONExporter initializes correctly."""
        exporter = JSONExporter()
        assert exporter is not None
    
    def test_export_creates_json_file(self):
        """Test that export method creates a valid JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.json"
            exporter = JSONExporter(file_path=str(file_path))
            
            test_data = {
                "users": [
                    {"name": "John", "age": 30},
                    {"name": "Jane", "age": 25}
                ],
                "metadata": {"exported_at": "2025-08-21"}
            }
            
            exporter.export(test_data)
            
            # Verify file was created
            assert file_path.exists()
            
            # Verify content
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                assert loaded_data == test_data
                assert len(loaded_data["users"]) == 2
                assert loaded_data["metadata"]["exported_at"] == "2025-08-21"
    
    def test_export_handles_empty_data(self):
        """Test that export handles empty data gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "empty.json"
            exporter = JSONExporter(file_path=str(file_path))
            
            exporter.export({})
            
            # File should be created with empty object
            assert file_path.exists()
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert data == {}
    
    def test_export_with_pretty_formatting(self):
        """Test export with pretty JSON formatting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "pretty.json"
            exporter = JSONExporter(file_path=str(file_path), indent=2)
            
            test_data = {"name": "John", "details": {"age": 30, "city": "NYC"}}
            exporter.export(test_data)
            
            # Verify formatting
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                assert len(lines) > 1  # Should be multi-line
                assert '  ' in content  # Should have indentation
    
    def test_export_handles_special_characters(self):
        """Test export handles special characters correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "special.json"
            exporter = JSONExporter(file_path=str(file_path))
            
            test_data = {
                "unicode": "åäö",
                "quotes": 'He said "Hello"',
                "newlines": "Line 1\nLine 2"
            }
            
            exporter.export(test_data)
            
            # Verify content
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                assert loaded_data["unicode"] == "åäö"
                assert loaded_data["quotes"] == 'He said "Hello"'
                assert loaded_data["newlines"] == "Line 1\nLine 2"
