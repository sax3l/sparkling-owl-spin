# API Clients

This directory contains generated API clients for various programming languages.

## Structure

- `openapi/` - Generated clients from OpenAPI specification
  - `python/` - Python client
  - `typescript/` - TypeScript client
- `postman/` - Postman collection for manual testing

## Generation

API clients are automatically generated from the OpenAPI specification using the `bin/gen-openapi-clients` script.

## Usage

### Python Client

```python
from scraping_client import ApiClient, DefaultApi

client = ApiClient()
client.configuration.host = "http://localhost:8000"
api = DefaultApi(client)

# Use the API
response = api.get_jobs()
```

### TypeScript Client

```typescript
import { DefaultApi, Configuration } from 'scraping-api-client';

const config = new Configuration({
  basePath: 'http://localhost:8000'
});

const api = new DefaultApi(config);

// Use the API
const response = await api.getJobs();
```
