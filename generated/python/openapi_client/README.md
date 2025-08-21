# Generated Python OpenAPI Client

This directory contains the auto-generated Python client based on the OpenAPI specification.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from openapi_client import ApiClient, Configuration
from openapi_client.api import CrawlApi

# Configure the client
config = Configuration()
config.host = "http://localhost:8000"
config.api_key['Authorization'] = 'your-api-key'

# Create API instance
api_client = ApiClient(config)
crawl_api = CrawlApi(api_client)

# Start a crawl
response = crawl_api.start_crawl({
    "url": "https://example.com",
    "template": "company_profile_v1"
})
```

## Generated Files

- `api/` - API endpoint classes
- `models/` - Data model classes  
- `exceptions.py` - Custom exceptions
- `configuration.py` - Client configuration
