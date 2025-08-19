import redis
from src.utils.url_utils import normalize_and_canonicalize_url
from typing import Optional

class URLFrontier:
    """
    Manages the queue of URLs to be crawled (the "frontier") using Redis.
    Handles deduplication via a visited set.
    """
    def __init__(self, redis_url: str, queue_name: str = "frontier:queue"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = queue_name
        self.visited_set_key = "visited:set"

    def add_url(self, url: str):
        """
        Adds a new URL to the frontier after normalization and duplicate checks.
        """
        normalized_url, canonical_key = normalize_and_canonicalize_url(url)
        
        if not self.redis.sismember(self.visited_set_key, canonical_key):
            self.redis.rpush(self.queue_name, normalized_url)

    def get_next_url(self) -> Optional[str]:
        """Retrieves the next URL to crawl from the queue."""
        return self.redis.lpop(self.queue_name)

    def mark_as_visited(self, url: str):
        """Marks a URL as visited in the persistent set."""
        _normalized_url, canonical_key = normalize_and_canonicalize_url(url)
        self.redis.sadd(self.visited_set_key, canonical_key)