"""
Sparkling Owl Spin Core Module Initialization
============================================

This module initializes the core components of the SOS platform.
"""

# Export the main platform components
from .platform import SOSPlatform, quick_crawl, stealth_crawl, distributed_crawl
from .config import get_settings
from .enhanced_crawler import EnhancedCrawlerManager
from .stealth_browser import StealthBrowserManager  
from .anti_detection import AntiDetectionManager
from .distributed import DistributedCoordinator

__all__ = [
    "SOSPlatform",
    "quick_crawl",
    "stealth_crawl", 
    "distributed_crawl",
    "get_settings",
    "EnhancedCrawlerManager",
    "StealthBrowserManager",
    "AntiDetectionManager",
    "DistributedCoordinator"
]
