"""
Tests for BigQuery exporter functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.exporters.bigquery_exporter import BigQueryExporter


class TestBigQueryExporter:
    """Test cases for BigQueryExporter class."""
    
    def test_bigquery_exporter_initialization(self):
        """Test that BigQueryExporter initializes correctly."""
        exporter = BigQueryExporter(
            project_id="test-project",
            dataset_id="test_dataset",
            table_id="test_table"
        )
        assert exporter is not None
        assert exporter.project_id == "test-project"
        assert exporter.dataset_id == "test_dataset"
        assert exporter.table_id == "test_table"
    
    @patch('google.cloud.bigquery.Client')
    def test_export_uploads_to_bigquery(self, mock_client):
        """Test that export method uploads data to BigQuery."""
        # Mock BigQuery client and job
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client
        mock_job = MagicMock()
        mock_bq_client.load_table_from_json.return_value = mock_job
        mock_job.result.return_value = None
        
        exporter = BigQueryExporter(
            project_id="test-project",
            dataset_id="test_dataset", 
            table_id="test_table"
        )
        
        test_data = [
            {"name": "John", "age": 30, "created_at": "2025-08-21"},
            {"name": "Jane", "age": 25, "created_at": "2025-08-21"}
        ]
        
        exporter.export(test_data)
        
        # Verify BigQuery client was used
        mock_client.assert_called_once()
        mock_bq_client.load_table_from_json.assert_called_once()
        mock_job.result.assert_called_once()
    
    @patch('google.cloud.bigquery.Client')
    def test_export_with_job_config(self, mock_client):
        """Test export with custom job configuration."""
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client
        mock_job = MagicMock()
        mock_bq_client.load_table_from_json.return_value = mock_job
        
        exporter = BigQueryExporter(
            project_id="test-project",
            dataset_id="test_dataset",
            table_id="test_table",
            write_disposition="WRITE_APPEND"
        )
        
        test_data = [{"name": "John", "age": 30}]
        exporter.export(test_data)
        
        # Verify job config was passed
        call_args = mock_bq_client.load_table_from_json.call_args
        assert call_args is not None
        job_config = call_args[1].get('job_config')
        assert job_config is not None
    
    @patch('google.cloud.bigquery.Client')
    def test_export_handles_schema_inference(self, mock_client):
        """Test that export handles schema inference correctly."""
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client
        mock_job = MagicMock()
        mock_bq_client.load_table_from_json.return_value = mock_job
        
        exporter = BigQueryExporter(
            project_id="test-project",
            dataset_id="test_dataset",
            table_id="test_table",
            autodetect_schema=True
        )
        
        test_data = [
            {"name": "John", "age": 30, "active": True},
            {"name": "Jane", "age": 25, "active": False}
        ]
        
        exporter.export(test_data)
        
        # Verify autodetect was enabled
        call_args = mock_bq_client.load_table_from_json.call_args
        job_config = call_args[1].get('job_config')
        assert hasattr(job_config, 'autodetect')
    
    @patch('google.cloud.bigquery.Client')
    def test_export_handles_empty_data(self, mock_client):
        """Test that export handles empty data gracefully."""
        mock_bq_client = MagicMock()
        mock_client.return_value = mock_bq_client
        
        exporter = BigQueryExporter(
            project_id="test-project",
            dataset_id="test_dataset",
            table_id="test_table"
        )
        
        # Should not raise exception with empty data
        exporter.export([])
        
        # Should not attempt to load empty data
        mock_bq_client.load_table_from_json.assert_not_called()
    
    def test_table_reference_construction(self):
        """Test that table reference is constructed correctly."""
        exporter = BigQueryExporter(
            project_id="my-project",
            dataset_id="my_dataset",
            table_id="my_table"
        )
        
        table_ref = exporter.get_table_reference()
        expected = "my-project.my_dataset.my_table"
        assert table_ref == expected
