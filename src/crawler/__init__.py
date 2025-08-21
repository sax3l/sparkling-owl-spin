"""
Crawler Module - Advanced web crawling capabilities.

Provides comprehensive web crawling functionality including:
- Site mapping and URL discovery
- Robots.txt compliance
- Link extraction and processing
- Template detection
- Keyword-based search crawling
- URL frontier management

Main Components:
- BaseCrawler: Core crawling functionality
- SitemapGenerator: Sitemap creation and management
- LinkExtractor: Link discovery and processing
- RobotsParser: robots.txt parsing and compliance
- TemplateDetector: Page template classification
- KeywordSearchCrawler: Keyword-based crawling
- URLFrontier: URL queue management
"""

from .sitemap_generator import SitemapGenerator
from .link_extractor import LinkExtractor
from .robots_parser import RobotsParser
from .template_detector import TemplateDetector
from .keywords_search import KeywordSearchCrawler
from .url_frontier import URLFrontier
from .url_queue import URLQueue

# Define a base crawler interface
class BaseCrawler:
    """Base crawler interface for consistent API."""
    
    def __init__(self, **kwargs):
        self.sitemap_generator = SitemapGenerator(**kwargs)
        self.link_extractor = LinkExtractor(**kwargs)
        self.robots_parser = RobotsParser(**kwargs)
        self.template_detector = TemplateDetector(**kwargs)
        self.url_frontier = URLFrontier(**kwargs)
        
    async def crawl(self, start_urls, **kwargs):
        """Crawl starting from given URLs."""
        raise NotImplementedError("Subclasses must implement crawl method")
        
    async def generate_sitemap(self, domain, **kwargs):
        """Generate sitemap for domain."""
        return await self.sitemap_generator.generate(domain, **kwargs)

__all__ = [
    "BaseCrawler",
    "SitemapGenerator",
    "LinkExtractor", 
    "RobotsParser",
    "TemplateDetector",
    "KeywordSearchCrawler",
    "URLFrontier",
    "URLQueue"
]