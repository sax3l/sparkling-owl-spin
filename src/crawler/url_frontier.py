import redis
from src.utils.url_utils import normalize_and_canonicalize_url

class URLFrontier:
    """
    Manages the queue of URLs to be crawled (the "frontier").
    
    This class will handle:
    - Per-host queues to ensure politeness.
    - A global priority queue for scheduling hosts.
    - Visited set to avoid re-crawling, using a Bloom filter and a persistent set.
    - URL normalization and canonicalization before adding to the queue.
    """
    def __init__(self, redis_url: str):
        """
        Initializes the connection to Redis.
        """
        self.redis = redis.from_url(redis_url, decode_responses=True)
        # TODO: Initialize Bloom filter

    def add_url(self, url: str, depth: int = 0):
        """
        Adds a new URL to the frontier after normalization and duplicate checks.
        """
        normalized_url, canonical_key = normalize_and_canonicalize_url(url)
        
        # TODO: Check against Bloom filter and visited set
        # is_visited = self.redis.sismember('visited:set', canonical_key)
        # if is_visited:
        #     return

        # TODO: Add to per-host queue and global scheduler
        # host = urlparse(normalized_url).netloc
        # self.redis.rpush(f'frontier:host:{host}', normalized_url)
        print(f"URL added (stub): {normalized_url}")

    def get_next_url(self) -> str | None:
        """
        Retrieves the next URL to crawl based on scheduling logic.
        """
        # TODO: Implement round-robin or priority-based host selection
        # TODO: Pop URL from the selected host's queue
        print("Getting next URL (stub)")
        return None

    def mark_as_visited(self, url: str):
        """
        Marks a URL as visited in the persistent set and Bloom filter.
        """
        _normalized_url, canonical_key = normalize_and_canonicalize_url(url)
        # TODO: Add to Redis set and update Bloom filter
        # self.redis.sadd('visited:set', canonical_key)
        print(f"Marked as visited (stub): {url}")