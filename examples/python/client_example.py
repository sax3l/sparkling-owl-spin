"""
Example Python client for the scraping platform.

Usage:
    python client_example.py
"""

import requests
import json

class ScrapingClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def start_crawl(self, url: str, template: str) -> dict:
        """Start a new crawling job."""
        payload = {
            "url": url,
            "template": template
        }
        response = requests.post(
            f"{self.base_url}/api/v1/crawl",
            headers=self.headers,
            json=payload
        )
        return response.json()
    
    def get_job_status(self, job_id: str) -> dict:
        """Get the status of a crawling job."""
        response = requests.get(
            f"{self.base_url}/api/v1/jobs/{job_id}",
            headers=self.headers
        )
        return response.json()

if __name__ == "__main__":
    client = ScrapingClient("your-api-key-here")
    result = client.start_crawl("https://example.com", "company_profile_v1")
    print(json.dumps(result, indent=2))
