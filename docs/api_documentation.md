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