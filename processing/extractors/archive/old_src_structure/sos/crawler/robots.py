import asyncio
from urllib.parse import urlparse
from urllib import robotparser
from functools import lru_cache

@lru_cache(maxsize=256)
def _rp_for(origin: str) -> robotparser.RobotFileParser:
    rp = robotparser.RobotFileParser()
    rp.set_url(origin.rstrip("/") + "/robots.txt")
    try:
        rp.read()
    except Exception:
        pass
    return rp

def is_allowed(url: str, user_agent: str = "sos-crawler") -> bool:
    p = urlparse(url)
    origin = f"{p.scheme}://{p.netloc}"
    rp = _rp_for(origin)
    try:
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True

class RobotsChecker:
    """Robots.txt checker for compliance"""
    
    def __init__(self, user_agent: str = "sos-crawler"):
        self.user_agent = user_agent
    
    async def can_fetch(self, url: str) -> bool:
        """Check if URL can be fetched according to robots.txt"""
        return is_allowed(url, self.user_agent)
