"""
Tests for CSV exporter functionality.
"""
import pytest
import tempfile
import csv
from pathlib import Path
from unittest.mock import Mock, patch
from src.exporters.csv_exporter import CSVExporter


class TestCSVExporter:
    """Test cases for CSVExporter class."""
    
    def test_csv_exporter_initialization(self):
        """Test that CSVExporter initializes correctly."""
        exporter = CSVExporter()
        assert exporter is not None
    
    def test_export_creates_csv_file(self):
        """Test that export method creates a valid CSV file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.csv"
            exporter = CSVExporter(file_path=str(file_path))
            
            test_data = [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ]
            
            exporter.export(test_data)
            
            # Verify file was created
            assert file_path.exists()
            
            # Verify content
            with open(file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 2
                assert rows[0]["name"] == "John"
                assert rows[1]["age"] == "25"
    
    def test_export_handles_empty_data(self):
        """Test that export handles empty data gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "empty.csv"
            exporter = CSVExporter(file_path=str(file_path))
            
            exporter.export([])
            
            # File should still be created
            assert file_path.exists()
    
    def test_export_with_custom_delimiter(self):
        """Test export with custom CSV delimiter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "custom.csv"
            exporter = CSVExporter(file_path=str(file_path), delimiter=';')
            
            test_data = [{"name": "John", "city": "New York"}]
            exporter.export(test_data)
            
            # Verify delimiter was used
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert ';' in content
                assert ',' not in content.split('\n')[0]  # Header should use semicolon
