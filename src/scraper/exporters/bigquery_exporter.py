"""BigQuery exporter for large-scale data analytics and warehousing."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound, BadRequest
    from google.oauth2 import service_account
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False

from .base_exporter import BaseExporter, ExportResult, ExportFormat

logger = logging.getLogger(__name__)


class BigQueryExporter(BaseExporter):
    """Export data to Google BigQuery for analytics and warehousing."""
    
    SUPPORTED_FORMATS = [ExportFormat.JSON]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize BigQuery exporter.
        
        Args:
            config: Configuration dictionary containing:
                - project_id: GCP project ID
                - dataset_id: BigQuery dataset ID
                - credentials_file: Path to service account JSON file
                - location: Dataset location (default: US)
                - tables: Table configuration mapping
                - batch_size: Number of rows per batch (default: 1000)
                - timeout: Query timeout in seconds (default: 300)
        """
        super().__init__(config)
        
        if not BIGQUERY_AVAILABLE:
            raise ImportError("google-cloud-bigquery is required for BigQuery export")
        
        self.project_id = config.get('project_id')
        self.dataset_id = config.get('dataset_id')
        self.credentials_file = config.get('credentials_file')
        self.location = config.get('location', 'US')
        self.tables_config = config.get('tables', {})
        self.batch_size = config.get('batch_size', 1000)
        self.timeout = config.get('timeout', 300)
        
        # Validate required config
        if not self.project_id:
            raise ValueError("project_id is required for BigQuery export")
        if not self.dataset_id:
            raise ValueError("dataset_id is required for BigQuery export")
        
        # Initialize BigQuery client
        self.client = self._create_client()
        self.dataset_ref = self.client.dataset(self.dataset_id, project=self.project_id)
        
        # Ensure dataset exists
        self._ensure_dataset_exists()
        
        logger.info(f"BigQuery exporter initialized for project {self.project_id}, dataset {self.dataset_id}")
    
    def _create_client(self) -> bigquery.Client:
        """Create BigQuery client with proper authentication."""
        try:
            if self.credentials_file and Path(self.credentials_file).exists():
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_file
                )
                return bigquery.Client(
                    project=self.project_id,
                    credentials=credentials
                )
            else:
                # Use default credentials (e.g., from environment)
                return bigquery.Client(project=self.project_id)
        except Exception as e:
            logger.error(f"Failed to create BigQuery client: {e}")
            raise
    
    def _ensure_dataset_exists(self) -> None:
        """Ensure the dataset exists, create if it doesn't."""
        try:
            self.client.get_dataset(self.dataset_ref)
            logger.debug(f"Dataset {self.dataset_id} already exists")
        except NotFound:
            logger.info(f"Creating dataset {self.dataset_id}")
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = self.location
            dataset.description = f"Scraped data warehouse - created {datetime.now()}"
            
            self.client.create_dataset(dataset, exists_ok=True)
            logger.info(f"Dataset {self.dataset_id} created successfully")
    
    def _get_table_config(self, data_type: str) -> Dict[str, Any]:
        """Get table configuration for data type."""
        return self.tables_config.get(data_type, {
            'table_id': f"{data_type}_data",
            'write_disposition': 'WRITE_APPEND',
            'create_disposition': 'CREATE_IF_NEEDED'
        })
    
    def _infer_schema(self, sample_data: List[Dict[str, Any]]) -> List[bigquery.SchemaField]:
        """Infer BigQuery schema from sample data."""
        if not sample_data:
            return []
        
        # Use first non-empty record to infer schema
        sample_record = None
        for record in sample_data:
            if record:
                sample_record = record
                break
        
        if not sample_record:
            return []
        
        schema_fields = []
        for field_name, field_value in sample_record.items():
            field_type = self._infer_field_type(field_value)
            mode = 'NULLABLE'  # Default to nullable
            
            schema_fields.append(bigquery.SchemaField(
                name=field_name,
                field_type=field_type,
                mode=mode
            ))
        
        return schema_fields
    
    def _infer_field_type(self, value: Any) -> str:
        """Infer BigQuery field type from value."""
        if value is None:
            return 'STRING'  # Default for null values
        elif isinstance(value, bool):
            return 'BOOLEAN'
        elif isinstance(value, int):
            return 'INTEGER'
        elif isinstance(value, float):
            return 'FLOAT'
        elif isinstance(value, datetime):
            return 'TIMESTAMP'
        elif isinstance(value, str):
            # Try to detect if it's a date/timestamp string
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return 'TIMESTAMP'
            except (ValueError, AttributeError):
                return 'STRING'
        elif isinstance(value, (list, dict)):
            return 'JSON'  # Use JSON type for complex structures
        else:
            return 'STRING'  # Default fallback
    
    def _prepare_data_for_bigquery(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for BigQuery insertion."""
        prepared_data = []
        
        for record in data:
            prepared_record = {}
            
            for key, value in record.items():
                # Handle special cases for BigQuery
                if isinstance(value, datetime):
                    # Convert datetime to string in ISO format
                    prepared_record[key] = value.isoformat()
                elif value is None:
                    # BigQuery handles None values correctly
                    prepared_record[key] = None
                elif isinstance(value, (list, dict)):
                    # Convert complex types to JSON strings
                    prepared_record[key] = json.dumps(value, default=str)
                else:
                    prepared_record[key] = value
            
            # Add metadata fields
            prepared_record['_exported_at'] = datetime.now().isoformat()
            prepared_record['_batch_id'] = self._generate_batch_id()
            
            prepared_data.append(prepared_record)
        
        return prepared_data
    
    def _create_table_if_not_exists(self, table_id: str, schema: List[bigquery.SchemaField]) -> bigquery.Table:
        """Create table if it doesn't exist."""
        table_ref = self.dataset_ref.table(table_id)
        
        try:
            table = self.client.get_table(table_ref)
            logger.debug(f"Table {table_id} already exists")
            return table
        except NotFound:
            logger.info(f"Creating table {table_id}")
            
            table = bigquery.Table(table_ref, schema=schema)
            table.description = f"Scraped data table - created {datetime.now()}"
            
            # Set up partitioning and clustering for better performance
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field="_exported_at"
            )
            
            if len(schema) > 0:
                # Cluster by the first few string fields for better query performance
                cluster_fields = []
                for field in schema[:4]:  # Max 4 clustering fields
                    if field.field_type == 'STRING':
                        cluster_fields.append(field.name)
                
                if cluster_fields:
                    table.clustering_fields = cluster_fields
            
            table = self.client.create_table(table)
            logger.info(f"Table {table_id} created successfully")
            return table
    
    def export(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> ExportResult:
        """Export data to BigQuery.
        
        Args:
            data: List of dictionaries to export
            data_type: Type of data (used for table selection)
            output_path: Not used for BigQuery (table determined by config)
            **kwargs: Additional export options
        
        Returns:
            ExportResult with BigQuery-specific information
        """
        if not data:
            return ExportResult(
                success=True,
                message="No data to export",
                records_exported=0,
                file_path=None,
                file_size=0,
                metadata={}
            )
        
        try:
            # Get table configuration
            table_config = self._get_table_config(data_type)
            table_id = table_config['table_id']
            write_disposition = table_config.get('write_disposition', 'WRITE_APPEND')
            
            # Prepare data
            prepared_data = self._prepare_data_for_bigquery(data)
            
            # Infer schema from data
            schema = self._infer_schema(prepared_data)
            
            # Create table if needed
            table = self._create_table_if_not_exists(table_id, schema)
            
            # Configure load job
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition=write_disposition,
                autodetect=True,  # Let BigQuery auto-detect schema if needed
                ignore_unknown_values=True,
                max_bad_records=int(len(data) * 0.01)  # Allow 1% bad records
            )
            
            # Process data in batches
            total_rows_inserted = 0
            batch_results = []
            
            for i in range(0, len(prepared_data), self.batch_size):
                batch = prepared_data[i:i + self.batch_size]
                
                # Create load job for batch
                job = self.client.load_table_from_json(
                    batch,
                    table,
                    job_config=job_config
                )
                
                # Wait for job completion
                job.result(timeout=self.timeout)
                
                if job.errors:
                    logger.warning(f"Batch {i//self.batch_size + 1} had errors: {job.errors}")
                    batch_results.append({
                        'batch_index': i // self.batch_size + 1,
                        'rows_attempted': len(batch),
                        'rows_inserted': job.output_rows or 0,
                        'errors': job.errors
                    })
                else:
                    rows_inserted = job.output_rows or len(batch)
                    total_rows_inserted += rows_inserted
                    batch_results.append({
                        'batch_index': i // self.batch_size + 1,
                        'rows_attempted': len(batch),
                        'rows_inserted': rows_inserted,
                        'errors': None
                    })
                
                logger.info(f"Batch {i//self.batch_size + 1} completed: {job.output_rows or len(batch)} rows inserted")
            
            # Get table info for metadata
            table = self.client.get_table(table)
            
            return ExportResult(
                success=True,
                message=f"Successfully exported {total_rows_inserted} records to BigQuery table {table_id}",
                records_exported=total_rows_inserted,
                file_path=f"{self.project_id}.{self.dataset_id}.{table_id}",
                file_size=0,  # Not applicable for BigQuery
                metadata={
                    'project_id': self.project_id,
                    'dataset_id': self.dataset_id,
                    'table_id': table_id,
                    'table_num_rows': table.num_rows,
                    'table_num_bytes': table.num_bytes,
                    'batch_results': batch_results,
                    'schema_fields': len(schema),
                    'write_disposition': write_disposition
                }
            )
            
        except Exception as e:
            logger.error(f"BigQuery export failed: {e}")
            return ExportResult(
                success=False,
                message=f"BigQuery export failed: {str(e)}",
                records_exported=0,
                file_path=None,
                file_size=0,
                metadata={'error': str(e)}
            )
    
    def validate_connection(self) -> bool:
        """Validate BigQuery connection and permissions."""
        try:
            # Try to list datasets to test connection
            datasets = list(self.client.list_datasets(max_results=1))
            
            # Try to get dataset info
            dataset = self.client.get_dataset(self.dataset_ref)
            
            logger.info("BigQuery connection validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"BigQuery connection validation failed: {e}")
            return False
    
    def get_table_info(self, table_id: str) -> Dict[str, Any]:
        """Get information about a BigQuery table."""
        try:
            table_ref = self.dataset_ref.table(table_id)
            table = self.client.get_table(table_ref)
            
            return {
                'table_id': table.table_id,
                'num_rows': table.num_rows,
                'num_bytes': table.num_bytes,
                'created': table.created.isoformat() if table.created else None,
                'modified': table.modified.isoformat() if table.modified else None,
                'schema_fields': len(table.schema),
                'partitioning': table.time_partitioning.type_.name if table.time_partitioning else None,
                'clustering_fields': table.clustering_fields or []
            }
            
        except NotFound:
            return {'error': f"Table {table_id} not found"}
        except Exception as e:
            return {'error': str(e)}
    
    def query_table(self, table_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query a BigQuery table and return sample data."""
        try:
            query = f"""
                SELECT *
                FROM `{self.project_id}.{self.dataset_id}.{table_id}`
                ORDER BY _exported_at DESC
                LIMIT {limit}
            """
            
            job = self.client.query(query)
            results = job.result()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to query table {table_id}: {e}")
            return []
