"""
Tests for Excel exporter functionality.
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.exporters.excel_exporter import ExcelExporter


class TestExcelExporter:
    """Test cases for ExcelExporter class."""
    
    def test_excel_exporter_initialization(self):
        """Test that ExcelExporter initializes correctly."""
        exporter = ExcelExporter()
        assert exporter is not None
    
    @patch('openpyxl.Workbook')
    def test_export_creates_excel_file(self, mock_workbook):
        """Test that export method creates a valid Excel file."""
        # Mock workbook and worksheet
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.xlsx"
            exporter = ExcelExporter(file_path=str(file_path))
            
            test_data = [
                {"name": "John", "age": 30, "city": "NYC"},
                {"name": "Jane", "age": 25, "city": "LA"}
            ]
            
            exporter.export(test_data)
            
            # Verify workbook was created and saved
            mock_workbook.assert_called_once()
            mock_wb.save.assert_called_once_with(str(file_path))
    
    @patch('openpyxl.Workbook')
    def test_export_writes_headers(self, mock_workbook):
        """Test that export writes column headers correctly."""
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        
        exporter = ExcelExporter()
        test_data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        exporter.export(test_data)
        
        # Verify headers were written
        mock_ws.append.assert_any_call(["name", "age"])
    
    @patch('openpyxl.Workbook')
    def test_export_writes_data_rows(self, mock_workbook):
        """Test that export writes data rows correctly."""
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        
        exporter = ExcelExporter()
        test_data = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25}
        ]
        
        exporter.export(test_data)
        
        # Verify data rows were written
        mock_ws.append.assert_any_call(["John", 30])
        mock_ws.append.assert_any_call(["Jane", 25])
    
    @patch('openpyxl.Workbook')
    def test_export_handles_empty_data(self, mock_workbook):
        """Test that export handles empty data gracefully."""
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        
        exporter = ExcelExporter()
        exporter.export([])
        
        # Should still create workbook but with minimal content
        mock_workbook.assert_called_once()
        mock_wb.save.assert_called_once()
    
    @patch('openpyxl.Workbook')
    def test_export_with_worksheet_name(self, mock_workbook):
        """Test export with custom worksheet name."""
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_workbook.return_value = mock_wb
        mock_wb.active = mock_ws
        
        exporter = ExcelExporter(sheet_name="CustomSheet")
        test_data = [{"name": "John"}]
        
        exporter.export(test_data)
        
        # Verify worksheet title was set
        assert mock_ws.title == "CustomSheet"
