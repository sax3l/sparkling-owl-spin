import httpx
import uuid
import json
from typing import Optional, Dict, Any, List, Union

class ECaDPClient:
    """Python SDK for the ECaDP API."""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1", api_key: str = ""):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def _request(self, method: str, path: str, json_data: Optional[Dict] = None, headers: Optional[Dict] = None, stream: bool = False) -> Union[Dict, httpx.Response]:
        _headers = self.headers.copy()
        if headers:
            _headers.update(headers)
        
        try:
            if stream:
                response = self.client.request(method, path, json=json_data, headers=_headers, follow_redirects=True)
            else:
                response = self.client.request(method, path, json=json_data, headers=_headers)
            
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses
            
            if stream:
                return response
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"API Error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"Network Error: {e}")
            raise

    def submit_crawl_job(self, seeds: List[str], max_depth: int = 3, max_urls: int = 20000, allow_domains: List[str] = [], disallow_patterns: List[str] = [], policy: Optional[Dict] = None, caps: Optional[Dict] = None, tags: Optional[List[str]] = None) -> Dict:
        """Submits a new crawl job."""
        payload = {
            "seeds": seeds,
            "max_depth": max_depth,
            "max_urls": max_urls,
            "allow_domains": allow_domains,
            "disallow_patterns": disallow_patterns,
            "policy": policy or {},
            "caps": caps or {},
            "tags": tags or []
        }
        headers = {"Idempotency-Key": str(uuid.uuid4())}
        return self._request("POST", "/jobs/crawl", json_data=payload, headers=headers)

    def submit_scrape_job(self, template_id: str, source: Dict, template_version: Optional[str] = None, policy: Optional[Dict] = None, caps: Optional[Dict] = None, export: Optional[Dict] = None, tags: Optional[List[str]] = None) -> Dict:
        """Submits a new scrape job."""
        payload = {
            "template_id": template_id,
            "source": source,
            "template_version": template_version,
            "policy": policy or {},
            "caps": caps or {},
            "export": export or {},
            "tags": tags or []
        }
        headers = {"Idempotency-Key": str(uuid.uuid4())}
        return self._request("POST", "/jobs/scrape", json_data=payload, headers=headers)

    def get_job_status(self, job_id: str) -> Dict:
        """Retrieves the status of a specific job."""
        return self._request("GET", f"/jobs/{job_id}")

    def get_data_stream(self, entity_type: str, format: str = "json", compress: bool = False, filters: Optional[Dict] = None, sort_by: Optional[str] = None, fields: Optional[List[str]] = None, mask_pii: bool = True) -> httpx.Response:
        """
        Directly retrieves data as a stream (CSV, NDJSON, JSON).
        Returns an httpx.Response object which can be iterated for chunks.
        """
        params = {
            "format": format,
            "compress": str(compress).lower(),
            "mask_pii": str(mask_pii).lower()
        }
        if filters:
            params["filters"] = json.dumps(filters)
        if sort_by:
            params["sort_by"] = sort_by
        if fields:
            params["fields"] = ",".join(fields)

        headers = {}
        if format == "csv":
            headers["Accept"] = "text/csv"
        elif format == "ndjson":
            headers["Accept"] = "application/x-ndjson"
        elif format == "json":
            headers["Accept"] = "application/json"

        return self._request("GET", f"/data/{entity_type}", headers=headers, params=params, stream=True)

    # TODO: Implement other SDK methods (templates, webhooks, proxy stats)