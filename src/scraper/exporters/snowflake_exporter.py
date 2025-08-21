"""Snowflake exporter for enterprise data warehousing."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import tempfile
import csv

try:
    import snowflake.connector
    from snowflake.connector import DictCursor
    from snowflake.connector.errors import ProgrammingError, DatabaseError
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

from .base_exporter import BaseExporter, ExportResult, ExportFormat

logger = logging.getLogger(__name__)


class SnowflakeExporter(BaseExporter):
    """Export data to Snowflake for enterprise data warehousing."""
    
    SUPPORTED_FORMATS = [ExportFormat.JSON, ExportFormat.CSV]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Snowflake exporter.
        
        Args:
            config: Configuration dictionary containing:
                - account: Snowflake account identifier
                - user: Username
                - password: Password (or use private_key for key-pair auth)
                - private_key: Private key for key-pair authentication
                - warehouse: Warehouse name
                - database: Database name
                - schema: Schema name (default: PUBLIC)
                - role: Role to use (optional)
                - tables: Table configuration mapping
                - batch_size: Number of rows per batch (default: 5000)
                - timeout: Query timeout in seconds (default: 600)
        """
        super().__init__(config)
        
        if not SNOWFLAKE_AVAILABLE:
            raise ImportError("snowflake-connector-python is required for Snowflake export")
        
        self.account = config.get('account')
        self.user = config.get('user')
        self.password = config.get('password')
        self.private_key = config.get('private_key')
        self.warehouse = config.get('warehouse')
        self.database = config.get('database')
        self.schema = config.get('schema', 'PUBLIC')
        self.role = config.get('role')
        self.tables_config = config.get('tables', {})
        self.batch_size = config.get('batch_size', 5000)
        self.timeout = config.get('timeout', 600)
        
        # Validate required config
        required_fields = ['account', 'user', 'warehouse', 'database']
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"{field} is required for Snowflake export")
        
        if not self.password and not self.private_key:
            raise ValueError("Either password or private_key is required for authentication")
        
        # Initialize connection
        self.connection = self._create_connection()
        
        logger.info(f"Snowflake exporter initialized for {self.account}")
    
    def _create_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Create Snowflake connection."""
        try:
            connection_params = {
                'account': self.account,
                'user': self.user,
                'warehouse': self.warehouse,
                'database': self.database,
                'schema': self.schema,
                'autocommit': True,
                'network_timeout': self.timeout
            }
            
            if self.role:
                connection_params['role'] = self.role
            
            # Choose authentication method
            if self.private_key:
                connection_params['private_key'] = self.private_key
            else:
                connection_params['password'] = self.password
            
            connection = snowflake.connector.connect(**connection_params)
            
            logger.info("Snowflake connection established successfully")
            return connection
            
        except Exception as e:
            logger.error(f"Failed to create Snowflake connection: {e}")
            raise
    
    def _get_table_config(self, data_type: str) -> Dict[str, Any]:
        """Get table configuration for data type."""
        return self.tables_config.get(data_type, {
            'table_name': f"{data_type.upper()}_DATA",
            'merge_keys': ['id'],  # Default merge key
            'create_if_missing': True
        })
    
    def _infer_snowflake_schema(self, sample_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Infer Snowflake schema from sample data."""
        if not sample_data:
            return {}
        
        # Use first non-empty record to infer schema
        sample_record = None
        for record in sample_data:
            if record:
                sample_record = record
                break
        
        if not sample_record:
            return {}
        
        schema = {}
        for field_name, field_value in sample_record.items():
            snowflake_type = self._infer_snowflake_type(field_value)
            schema[field_name] = snowflake_type
        
        return schema
    
    def _infer_snowflake_type(self, value: Any) -> str:
        """Infer Snowflake data type from value."""
        if value is None:
            return 'VARCHAR(16777216)'  # Default for null values
        elif isinstance(value, bool):
            return 'BOOLEAN'
        elif isinstance(value, int):
            return 'NUMBER(38,0)'  # Snowflake's integer type
        elif isinstance(value, float):
            return 'FLOAT'
        elif isinstance(value, datetime):
            return 'TIMESTAMP_NTZ'
        elif isinstance(value, str):
            # Try to detect if it's a date/timestamp string
            try:
                datetime.fromisoformat(value.replace('Z', '+00:00'))
                return 'TIMESTAMP_NTZ'
            except (ValueError, AttributeError):
                # Determine string length for VARCHAR
                if len(value) <= 255:
                    return 'VARCHAR(255)'
                elif len(value) <= 4000:
                    return 'VARCHAR(4000)'
                else:
                    return 'VARCHAR(16777216)'  # Max VARCHAR size
        elif isinstance(value, (list, dict)):
            return 'VARIANT'  # Snowflake's JSON type
        else:
            return 'VARCHAR(16777216)'  # Default fallback
    
    def _create_table_if_not_exists(self, table_name: str, schema: Dict[str, str]) -> None:
        """Create table if it doesn't exist."""
        try:
            cursor = self.connection.cursor()
            
            # Check if table exists
            check_query = f"""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = '{self.schema}' 
                AND table_name = '{table_name.upper()}'
            """
            
            cursor.execute(check_query)
            result = cursor.fetchone()
            
            if result:
                logger.debug(f"Table {table_name} already exists")
                return
            
            # Create table
            logger.info(f"Creating table {table_name}")
            
            column_definitions = []
            for column_name, column_type in schema.items():
                column_definitions.append(f"{column_name} {column_type}")
            
            # Add metadata columns
            column_definitions.extend([
                "_EXPORTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()",
                "_BATCH_ID VARCHAR(255)",
                "_SOURCE_URL VARCHAR(4000)",
                "_EXTRACTION_VERSION VARCHAR(50)"
            ])
            
            create_query = f"""
                CREATE TABLE {table_name} (
                    {', '.join(column_definitions)}
                )
            """
            
            cursor.execute(create_query)
            logger.info(f"Table {table_name} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise
        finally:
            cursor.close()
    
    def _prepare_data_for_snowflake(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for Snowflake insertion."""
        prepared_data = []
        batch_id = self._generate_batch_id()
        
        for record in data:
            prepared_record = {}
            
            for key, value in record.items():
                # Handle special cases for Snowflake
                if isinstance(value, datetime):
                    # Convert datetime to string in ISO format
                    prepared_record[key] = value.isoformat()
                elif value is None:
                    prepared_record[key] = None
                elif isinstance(value, (list, dict)):
                    # Convert complex types to JSON strings for VARIANT
                    prepared_record[key] = json.dumps(value, default=str)
                elif isinstance(value, bool):
                    # Snowflake expects boolean as string
                    prepared_record[key] = value
                else:
                    prepared_record[key] = value
            
            # Add metadata fields
            prepared_record['_EXPORTED_AT'] = datetime.now().isoformat()
            prepared_record['_BATCH_ID'] = batch_id
            prepared_record['_SOURCE_URL'] = record.get('source_url', '')
            prepared_record['_EXTRACTION_VERSION'] = '1.0'
            
            prepared_data.append(prepared_record)
        
        return prepared_data
    
    def _bulk_insert_via_stage(self, table_name: str, data: List[Dict[str, Any]]) -> int:
        """Bulk insert data using Snowflake staging area."""
        cursor = self.connection.cursor()
        
        try:
            # Create temporary CSV file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                temp_path = temp_file.name
                
                if data:
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            # Create stage
            stage_name = f"temp_stage_{self._generate_batch_id()}"
            cursor.execute(f"CREATE OR REPLACE TEMPORARY STAGE {stage_name}")
            
            # Upload file to stage
            cursor.execute(f"PUT file://{temp_path} @{stage_name}")
            
            # Copy from stage to table
            copy_query = f"""
                COPY INTO {table_name}
                FROM @{stage_name}
                FILE_FORMAT = (TYPE = 'CSV' FIELD_OPTIONALLY_ENCLOSED_BY = '"' SKIP_HEADER = 1)
                ON_ERROR = 'CONTINUE'
            """
            
            cursor.execute(copy_query)
            result = cursor.fetchone()
            
            # Clean up
            cursor.execute(f"DROP STAGE {stage_name}")
            Path(temp_path).unlink(missing_ok=True)
            
            # Parse result to get number of rows loaded
            if result and len(result) > 1:
                return int(result[1])  # rows_loaded is typically the second column
            else:
                return len(data)
            
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise
        finally:
            cursor.close()
    
    def _insert_batch(self, table_name: str, batch: List[Dict[str, Any]]) -> int:
        """Insert a batch of data using parameterized queries."""
        if not batch:
            return 0
        
        cursor = self.connection.cursor()
        
        try:
            # Build INSERT query
            columns = list(batch[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Prepare data for insertion
            rows = []
            for record in batch:
                row = tuple(record.get(col) for col in columns)
                rows.append(row)
            
            # Execute batch insert
            cursor.executemany(query, rows)
            
            return len(rows)
            
        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            raise
        finally:
            cursor.close()
    
    def export(
        self,
        data: List[Dict[str, Any]],
        data_type: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> ExportResult:
        """Export data to Snowflake.
        
        Args:
            data: List of dictionaries to export
            data_type: Type of data (used for table selection)
            output_path: Not used for Snowflake (table determined by config)
            **kwargs: Additional export options:
                - use_bulk_insert: Use staging area for bulk insert (default: True for large datasets)
                - merge_mode: Whether to use MERGE instead of INSERT (default: False)
        
        Returns:
            ExportResult with Snowflake-specific information
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
            table_name = table_config['table_name']
            use_bulk_insert = kwargs.get('use_bulk_insert', len(data) > 1000)
            
            # Prepare data
            prepared_data = self._prepare_data_for_snowflake(data)
            
            # Infer schema from data
            schema = self._infer_snowflake_schema(prepared_data)
            
            # Create table if needed
            if table_config.get('create_if_missing', True):
                self._create_table_if_not_exists(table_name, schema)
            
            # Insert data
            total_rows_inserted = 0
            
            if use_bulk_insert:
                # Use staging area for large datasets
                logger.info(f"Using bulk insert for {len(prepared_data)} rows")
                total_rows_inserted = self._bulk_insert_via_stage(table_name, prepared_data)
            else:
                # Use batch inserts for smaller datasets
                for i in range(0, len(prepared_data), self.batch_size):
                    batch = prepared_data[i:i + self.batch_size]
                    rows_inserted = self._insert_batch(table_name, batch)
                    total_rows_inserted += rows_inserted
                    
                    logger.info(f"Batch {i//self.batch_size + 1} completed: {rows_inserted} rows inserted")
            
            # Get table info for metadata
            table_info = self._get_table_info(table_name)
            
            return ExportResult(
                success=True,
                message=f"Successfully exported {total_rows_inserted} records to Snowflake table {table_name}",
                records_exported=total_rows_inserted,
                file_path=f"{self.database}.{self.schema}.{table_name}",
                file_size=0,  # Not applicable for Snowflake
                metadata={
                    'account': self.account,
                    'database': self.database,
                    'schema': self.schema,
                    'table_name': table_name,
                    'table_info': table_info,
                    'insert_method': 'bulk' if use_bulk_insert else 'batch',
                    'batch_size': self.batch_size
                }
            )
            
        except Exception as e:
            logger.error(f"Snowflake export failed: {e}")
            return ExportResult(
                success=False,
                message=f"Snowflake export failed: {str(e)}",
                records_exported=0,
                file_path=None,
                file_size=0,
                metadata={'error': str(e)}
            )
    
    def validate_connection(self) -> bool:
        """Validate Snowflake connection and permissions."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            result = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Snowflake connection validated successfully: {result[0]}")
            return True
            
        except Exception as e:
            logger.error(f"Snowflake connection validation failed: {e}")
            return False
    
    def _get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a Snowflake table."""
        try:
            cursor = self.connection.cursor(DictCursor)
            
            # Get table metadata
            query = f"""
                SELECT 
                    table_name,
                    row_count,
                    bytes,
                    created,
                    last_altered
                FROM information_schema.tables 
                WHERE table_schema = '{self.schema}' 
                AND table_name = '{table_name.upper()}'
            """
            
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return {
                    'table_name': result['TABLE_NAME'],
                    'row_count': result['ROW_COUNT'],
                    'bytes': result['BYTES'],
                    'created': result['CREATED'].isoformat() if result['CREATED'] else None,
                    'last_altered': result['LAST_ALTERED'].isoformat() if result['LAST_ALTERED'] else None
                }
            else:
                return {'error': f"Table {table_name} not found"}
                
        except Exception as e:
            return {'error': str(e)}
    
    def query_table(self, table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query a Snowflake table and return sample data."""
        try:
            cursor = self.connection.cursor(DictCursor)
            
            query = f"""
                SELECT *
                FROM {table_name}
                ORDER BY _EXPORTED_AT DESC
                LIMIT {limit}
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query table {table_name}: {e}")
            return []
    
    def close(self) -> None:
        """Close Snowflake connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.info("Snowflake connection closed")
        except Exception as e:
            logger.error(f"Error closing Snowflake connection: {e}")
    
    def __del__(self):
        """Ensure connection is closed when object is destroyed."""
        self.close()
