import json
from typing import List, Dict, Any, Optional
from google.cloud import storage
from ..core.config import get_settings

class GCSExporter:
    def __init__(self, bucket_name: Optional[str] = None):
        settings = get_settings()
        self.client = storage.Client()
        self.bucket_name = bucket_name or settings.GCS_BUCKET
        
    def export_results(self, job_id: int, results: List[Dict[str, Any]], format: str = "json") -> str:
        """Export results to Google Cloud Storage"""
        if not self.bucket_name:
            raise ValueError("GCS_BUCKET must be configured")
            
        bucket = self.client.bucket(self.bucket_name)
        
        if format == "json":
            filename = f"job_{job_id}_results.json"
            content = json.dumps(results, indent=2, ensure_ascii=False)
            content_type = "application/json"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        blob = bucket.blob(f"scraped-data/{filename}")
        blob.upload_from_string(content, content_type=content_type)
        
        return f"gs://{self.bucket_name}/scraped-data/{filename}"
