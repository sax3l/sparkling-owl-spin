# ECaDP Python SDK

Python client for the Ethical Crawler & Data Platform API.

## Installation
```bash
pip install .
```

## Usage
```python
from scrape_sdk import ECaDPClient

client = ECaDPClient(api_key="YOUR_API_KEY")

job = client.submit_crawl_job(start_url="http://example.com")
print(job)