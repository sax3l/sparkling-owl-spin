import json
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from ..core.config import get_settings

class BigQueryExporter:
    def __init__(self, project_id: Optional[str] = None):
        settings = get_settings()
        self.client = bigquery.Client(project=project_id)
        self.dataset_id = settings.BQ_DATASET
        self.table_id = settings.BQ_TABLE
        
    def export_results(self, job_id: int, results: List[Dict[str, Any]]) -> str:
        """Export results to BigQuery table"""
        if not self.dataset_id or not self.table_id:
            raise ValueError("BQ_DATASET and BQ_TABLE must be configured")
            
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        
        # Transform results for BigQuery
        rows = []
        for result in results:
            row = {
                'job_id': job_id,
                'url': result.get('url', ''),
                'data_json': json.dumps(result.get('data', {})),
                'scraped_at': result.get('created_at')
            }
            rows.append(row)
        
        # Insert rows
        errors = self.client.insert_rows_json(table_ref, rows)
        
        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")
            
        return f"Exported {len(rows)} rows to {self.dataset_id}.{self.table_id}"
    
    def create_table_if_not_exists(self) -> None:
        """Create the BigQuery table if it doesn't exist"""
        if not self.dataset_id or not self.table_id:
            return
            
        schema = [
            bigquery.SchemaField("job_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("url", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("data_json", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("scraped_at", "TIMESTAMP", mode="NULLABLE"),
        ]
        
        table_ref = self.client.dataset(self.dataset_id).table(self.table_id)
        table = bigquery.Table(table_ref, schema=schema)
        
        try:
            table = self.client.create_table(table)
            print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
        except Exception as e:
            if "Already Exists" not in str(e):
                raise
