"""
ECaDP - Enterprise Crawler and Data Platform
============================================

A comprehensive, production-ready web crawling and data extraction platform
that respects robots.txt, implements advanced anti-bot countermeasures,
and provides robust data processing capabilities.

Key Features:
- Advanced web crawling with sitemap generation
- Intelligent data scraping with template-based extraction
- Sophisticated proxy pool management with health monitoring
- Anti-bot protection with stealth browsing capabilities
- Comprehensive data processing and quality assurance
- Real-time monitoring and observability
- GraphQL and REST APIs
- Production-ready deployment with Docker and Kubernetes

Components:
- crawler: Web crawling and sitemap generation
- scraper: Data extraction and template processing
- proxy_pool: Proxy management and rotation
- anti_bot: Stealth browsing and detection avoidance
- database: Data storage and management
- scheduler: Job scheduling and orchestration
- webapp: Web interface and APIs
- observability: Monitoring and metrics
- utils: Shared utilities and helpers

License: MIT
"""

__version__ = "1.0.0"
__author__ = "ECaDP Development Team"
__email__ = "dev@ecadp.com"

# Core imports for easy access
from .crawler import BaseCrawler
from .scraper import BaseScraper
from .proxy_pool import ProxyManager
from .database import DatabaseManager
from .observability import MetricsCollector

__all__ = [
    "BaseCrawler",
    "BaseScraper", 
    "ProxyManager",
    "DatabaseManager",
    "MetricsCollector",
    "__version__",
    "__author__",
    "__email__"
]