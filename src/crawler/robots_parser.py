import redis
import httpx
from robotexclusionrulesparser import RobotExclusionRulesParser
from urllib.parse import urljoin, urlparse

class RobotsParser:
    """
    Fetches, parses, and caches robots.txt files to respect crawling rules.
    """
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.cache_ttl = 3600  # Cache for 1 hour

    def can_fetch(self, url: str, user_agent: str) -> bool:
        """Checks if a URL is allowed to be fetched according to robots.txt."""
        domain = urlparse(url).netloc
        cache_key = f"robots:{domain}"
        
        cached_rules = self.redis.get(cache_key)
        
        if cached_rules:
            parser = RobotExclusionRulesParser()
            parser.parse(cached_rules)
        else:
            robots_url = urljoin(f"https://{domain}", "/robots.txt")
            try:
                response = httpx.get(robots_url, timeout=10.0)
                if response.status_code == 200:
                    rules = response.text
                    self.redis.set(cache_key, rules, ex=self.cache_ttl)
                    parser = RobotExclusionRulesParser()
                    parser.parse(rules)
                else:
                    # If robots.txt is not found or gives an error, assume allow all
                    self.redis.set(cache_key, "", ex=self.cache_ttl)
                    return True
            except httpx.RequestError:
                # Network error, assume allow for this time
                return True

        return parser.is_allowed(user_agent, url)