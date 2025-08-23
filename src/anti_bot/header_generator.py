import random
from typing import Literal, Dict, List, Optional

HeaderFamily = Literal["chrome", "firefox"]

# Based on real browser exports to ensure authenticity
CHROME_LIKE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7",
    "Sec-Ch-Ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}

FIREFOX_LIKE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3",
    "Dnt": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
}

HEADER_FAMILIES = {
    "chrome": CHROME_LIKE_HEADERS,
    "firefox": FIREFOX_LIKE_HEADERS,
}


class HeaderGenerator:
    """Generator for realistic browser headers with anti-detection features."""
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0"
        ]
    
    def get_headers(self, family: HeaderFamily = "chrome") -> Dict[str, str]:
        """Returns a dictionary of headers for a given browser family."""
        return HEADER_FAMILIES.get(family, CHROME_LIKE_HEADERS).copy()
    
    def get_random_headers(self) -> Dict[str, str]:
        """Generate random realistic headers."""
        family = random.choice(["chrome", "firefox"])
        headers = self.get_headers(family)
        
        # Randomize user agent
        headers["User-Agent"] = random.choice(self.user_agents)
        
        return headers
    
    def generate_headers_for_domain(self, domain: str, family: HeaderFamily = "chrome") -> Dict[str, str]:
        """Generate headers customized for a specific domain."""
        headers = self.get_headers(family)
        headers["Referer"] = f"https://{domain}/"
        return headers


def get_headers(family: HeaderFamily = "chrome") -> dict:
    """
    Returns a dictionary of headers for a given browser family.
    """
    return HEADER_FAMILIES.get(family, CHROME_LIKE_HEADERS).copy()