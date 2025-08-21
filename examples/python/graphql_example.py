"""
GraphQL client example for the scraping platform.
"""

import requests
import json

class GraphQLClient:
    def __init__(self, api_key: str, endpoint: str = "http://localhost:8000/graphql"):
        self.endpoint = endpoint
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def execute_query(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query."""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        response = requests.post(
            self.endpoint,
            headers=self.headers,
            json=payload
        )
        return response.json()
    
    def get_crawl_jobs(self, limit: int = 10) -> dict:
        """Get recent crawling jobs."""
        query = """
        query GetCrawlJobs($limit: Int!) {
            crawlJobs(limit: $limit) {
                id
                url
                status
                createdAt
                results {
                    data
                    extractedAt
                }
            }
        }
        """
        return self.execute_query(query, {"limit": limit})

if __name__ == "__main__":
    client = GraphQLClient("your-api-key-here")
    jobs = client.get_crawl_jobs(5)
    print(json.dumps(jobs, indent=2))
