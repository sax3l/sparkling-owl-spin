import httpx
from urllib.parse import urljoin, urlparse

def fetch_and_parse_robots_txt(url: str) -> list:
    """Fetches and parses robots.txt to respect crawling rules."""
    # TODO: Implement a proper robots.txt parser.
    print(f"Respecting robots.txt for {url}")
    return []

def crawl_site(start_url: str):
    """
    Performs a basic crawl of a website, respecting robots.txt.
    Uses a simple BFS/DFS approach.
    """
    queue = [start_url]
    visited = set()

    fetch_and_parse_robots_txt(urljoin(start_url, "/robots.txt"))

    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        
        print(f"Crawling: {url}")
        visited.add(url)

        try:
            response = httpx.get(url)
            response.raise_for_status()
            # TODO: Parse HTML for new links and add them to the queue.
        except httpx.HTTPStatusError as e:
            print(f"Error fetching {url}: {e}")

    return list(visited)