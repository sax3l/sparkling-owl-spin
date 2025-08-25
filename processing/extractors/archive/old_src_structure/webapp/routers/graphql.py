"""
GraphQL endpoint for the web application.
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
import json

router = APIRouter(prefix="/graphql", tags=["graphql"])

# Simple GraphQL schema for basic functionality
SCHEMA = """
type Query {
  hello: String
  jobs: [Job]
  exports: [Export]
}

type Job {
  id: String!
  status: String!
  created_at: String!
  type: String!
}

type Export {
  id: String!
  format: String!
  status: String!
  download_url: String
}
"""

@router.get("/")
async def graphql_playground():
    """GraphQL playground for development."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GraphQL Playground</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
    </head>
    <body>
        <div id="root">
            <style>
                body { margin: 0; font-family: "Open Sans", sans-serif; overflow: hidden; }
                #root { height: 100vh; }
            </style>
        </div>
        <script>window.addEventListener('load', function (event) {
            GraphQLPlayground.init(document.getElementById('root'), {
                endpoint: '/graphql'
            })
        })</script>
        <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
    </body>
    </html>
    """)

@router.post("/")
async def graphql_endpoint(query: dict):
    """Simple GraphQL endpoint."""
    # This is a minimal implementation for development
    # In production, you'd use a proper GraphQL library like strawberry or graphene
    
    query_str = query.get("query", "")
    
    if "hello" in query_str:
        return {"data": {"hello": "Hello from Main Crawler GraphQL!"}}
    elif "jobs" in query_str:
        return {"data": {"jobs": [
            {"id": "1", "status": "completed", "created_at": "2025-01-08T10:00:00Z", "type": "crawl"},
            {"id": "2", "status": "running", "created_at": "2025-01-08T11:00:00Z", "type": "scrape"}
        ]}}
    elif "exports" in query_str:
        return {"data": {"exports": [
            {"id": "1", "format": "csv", "status": "completed", "download_url": "/api/exports/1/download"},
            {"id": "2", "format": "json", "status": "processing", "download_url": None}
        ]}}
    else:
        return {"errors": [{"message": "Query not supported in this minimal implementation"}]}
