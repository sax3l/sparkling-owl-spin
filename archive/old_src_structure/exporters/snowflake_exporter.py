"""
Snowflake Exporter for exporting data to Snowflake.
Supports bulk inserts and various authentication methods.
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import snowflake.connector
    from snowflake.connector.pandas_tools import write_pandas
    import pandas as pd
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False

from .base import BaseExporter, ExportConfig, ExportResult, ExporterRegistry

class SnowflakeExporter(BaseExporter):
    """Exporter for Snowflake."""
    
    def __init__(self, config: ExportConfig):
        super().__init__(config)
        self.account = config.format_options.get('account')
        self.user = config.format_options.get('user')
        self.password = config.format_options.get('password')
        self.database = config.format_options.get('database')
        self.schema = config.format_options.get('schema')
        self.table = config.format_options.get('table')
        self.warehouse = config.format_options.get('warehouse')
        self.role = config.format_options.get('role')
        self.if_exists = config.format_options.get('if_exists', 'append')
    
    def validate_config(self) -> bool:
        """Validate Snowflake exporter configuration."""
        try:
            if not SNOWFLAKE_AVAILABLE:
                self.logger.error("Snowflake export requires snowflake-connector-python package")
                return False
            
            required_fields = ['account', 'user', 'password', 'database', 'schema', 'table']
            for field in required_fields:
                if not getattr(self, field):
                    self.logger.error(f"{field} is required for Snowflake export")
                    return False
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False
    
    async def export(self, data: List[Dict[str, Any]], **kwargs) -> ExportResult:
        """Export data to Snowflake."""
        if not self.validate_config():
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message="Invalid configuration or missing dependencies"
            )
        
        try:
            # Prepare data
            prepared_data = self.prepare_data(data)
            
            if not prepared_data:
                return ExportResult(
                    success=True,
                    records_exported=0,
                    output_location=f"{self.database}.{self.schema}.{self.table}",
                    export_time=datetime.utcnow(),
                    metadata=self.create_metadata(0)
                )
            
            # Write to Snowflake
            rows_inserted = await self._write_snowflake(prepared_data)
            
            location = f"{self.database}.{self.schema}.{self.table}"
            self.logger.info(f"Exported {rows_inserted} records to Snowflake: {location}")
            
            return ExportResult(
                success=True,
                records_exported=rows_inserted,
                output_location=location,
                export_time=datetime.utcnow(),
                metadata=self.create_metadata(rows_inserted)
            )
            
        except Exception as e:
            self.logger.error(f"Snowflake export failed: {str(e)}")
            return ExportResult(
                success=False,
                records_exported=0,
                output_location="",
                export_time=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _write_snowflake(self, data: List[Dict[str, Any]]) -> int:
        """Write data to Snowflake."""
        def write_sync():
            # Connect to Snowflake
            conn = snowflake.connector.connect(
                user=self.user,
                password=self.password,
                account=self.account,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                role=self.role
            )
            
            try:
                # Convert to DataFrame
                df = pd.DataFrame(data)
                
                # Write to Snowflake
                success, nchunks, nrows, _ = write_pandas(
                    conn,
                    df,
                    self.table,
                    auto_create_table=True,
                    overwrite=(self.if_exists == 'replace')
                )
                
                return nrows
            finally:
                conn.close()
        
        return await asyncio.get_event_loop().run_in_executor(None, write_sync)

# Register the exporter only if dependencies are available
if SNOWFLAKE_AVAILABLE:
    ExporterRegistry.register('snowflake', SnowflakeExporter)
