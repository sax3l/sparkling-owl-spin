# API Documentation

This document provides details about the REST and GraphQL APIs.

## REST API

The REST API is defined using the OpenAPI specification. You can find the interactive documentation at the `/docs` endpoint when the application is running.

The OpenAPI specification file is located at `docs/openapi.yaml`.

### API Versioning and Deprecation Policy

Our REST API uses **URL versioning** (e.g., `/api/v1/jobs`). This ensures that breaking changes can be introduced in new versions without immediately affecting existing integrations.

When an API endpoint or a specific field is deprecated, we follow these guidelines:

1.  **Documentation:** The deprecated feature will be clearly marked in this documentation and in the OpenAPI specification.
2.  **`Sunset` Header:** Responses from deprecated endpoints will include a `Sunset` HTTP header, indicating the date and time after which the endpoint is expected to be no longer supported.
    *   **Example Header:** `Sunset: 2025-01-01T00:00:00Z`
    *   A `Warning` header (code 299) may also be included to provide a human-readable message.
3.  **Grace Period:** Deprecated features will be maintained for a minimum of **6 to 12 months** from the date of deprecation before being removed. This provides ample time for clients to migrate to newer versions or alternative solutions.

## GraphQL API

The GraphQL API provides a flexible way to query data. The schema is available at the `/graphql` endpoint, which also serves a GraphiQL interface for interactive queries.

The GraphQL schema definition is located at `docs/graphql.graphql`.

### GraphQL Deprecation

For GraphQL, deprecated fields or types will be marked using the standard `@deprecated` directive within the schema. This directive will include a `reason` argument explaining why the field is deprecated and suggesting alternatives.

**Example:**
```graphql
type Query {
  oldField: String @deprecated(reason: "Use newField instead. Will be removed after 2025-01-01.")
  newField: String
}
```

## SDK & Examples

### cURL

**Start Scrape Job**
```bash
curl -X POST https://api.example.com/v1/jobs/scrape \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "template_id": "vehicle_detail_v1",
    "source": { "sitemap_query": { "domain": "synthetic.local", "pattern": "^https://synthetic\\\\.local/vehicle/.*$", "limit": 500 } },
    "policy": { "transport": "auto", "max_retries": 2 },
    "export": { "format": "ndjson", "compress": "gzip", "destination": { "type": "internal_staging", "retention_hours": 72 } }
  }'
```

**Fetch Persons (CSV)**
```bash
curl "https://api.example.com/v1/data/persons?fields=first_name,last_name,city&filter[city]=Göteborg&sort=-updated_at&page[size]=100" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: text/csv" \
  -o persons_gbg.csv
```

### Node.js (fetch)

```typescript
import fetch from "node-fetch"; // In Node.js < 18, you might need to import fetch. In modern browsers/Node.js 18+, it's global.

async function startScrape(token: string) {
  const res = await fetch("https://api.example.com/v1/jobs/scrape", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      "Idempotency-Key": crypto.randomUUID() // crypto is global in Node.js and browsers
    },
    body: JSON.stringify({
      template_id: "company_profile_v1",
      source: { sitemap_query: { domain: "synthetic.local", pattern: "^https://synthetic\\.local/company/.*$", limit: 1000 } },
      policy: { transport: "http" },
      caps: { max_concurrent: 16 }
    })
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(`HTTP ${res.status}: ${errorBody.message || JSON.stringify(errorBody)}`);
  }
  return res.json();
}

async function getPersonsCsv(token: string) {
  const params = new URLSearchParams({
    fields: "first_name,last_name,city",
    "filter[city]": "Göteborg",
    sort_by: "-updated_at",
    "page[size]": "100" // Note: page[size] is not directly supported by current backend, use limit/offset
  });

  const res = await fetch(`https://api.example.com/v1/data/persons?${params.toString()}`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "text/csv"
    }
  });
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(`HTTP ${res.status}: ${errorBody.message || JSON.stringify(errorBody)}`);
  }
  return res.text(); // Return as text for CSV
}

// Example usage (assuming you have a token)
// const MY_TOKEN = "your_api_token_here";
// startScrape(MY_TOKEN).then(job => console.log("Scrape job started:", job)).catch(console.error);
// getPersonsCsv(MY_TOKEN).then(csvData => console.log("Persons CSV:", csvData.substring(0, 200) + "...")).catch(console.error);
```

### Python (requests)

```python
import requests, uuid

token = "YOUR_API_TOKEN_HERE" # Replace with your actual token
resp = requests.post(
  "https://api.example.com/v1/jobs/crawl",
  headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Idempotency-Key": str(uuid.uuid4())},
  json={
    "seeds": ["https://synthetic.local/vehicles"],
    "max_depth": 2,
    "allow_domains": ["synthetic.local"],
    "policy": {"transport": "http", "respect_robots": True, "parallelism": 8},
    "caps": {"rps_per_domain": 1.0}
  }
)
print(resp.status_code, resp.json())
```

### GraphQL (fetch)

```typescript
const query = `
query($id: ID!) {
  vehicle(id: $id) {
    registration_number
    model_year
    tech_specs { fuel_type wltp_co2 }
    owners(first: 1) { edges { node { owner_type role } } }
  }
}`;

const token = "YOUR_API_TOKEN_HERE"; // Replace with your actual token
const res = await fetch("https://api.example.com/graphql", {
  method: "POST",
  headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
  body: JSON.stringify({ query, variables: { id: "veh_01H..." } }) # Replace with a real vehicle ID
});
console.log(await res.json());