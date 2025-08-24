"""
Sparkling Owl Spin - Revolutionary Webscraping Platform
========================================================

The ultimate integration of open-source webscraping innovations, combining the best
techniques from the world's leading frameworks into a unified, enterprise-grade platform.

INTEGRATED FRAMEWORKS:
• Scrapy (Python) - High-performance middleware architecture and async processing
• Apache Nutch (Java) - Enterprise distributed crawling with BFS/DFS algorithms
• Colly (Go) - Fast concurrent processing with clean API design
• Crawlee (JavaScript/Node & Python) - Modern stealth capabilities and anti-detection

REVOLUTIONARY COMPONENTS:
• Enhanced Crawler Manager - Scrapy-inspired middleware with Nutch algorithms
• Stealth Browser Manager - Complete browser automation stealth with AI CAPTCHA solving
• Advanced Proxy Pool - Multi-source proxy aggregation with intelligent rotation
• Anti-Detection System - Comprehensive bot detection evasion and behavioral simulation
• Revolutionary CAPTCHA Solver - AI-powered solving with computer vision and OCR
• Distributed Coordinator - Enterprise-grade scaling with fault-tolerant architecture

This platform represents decades of open-source webscraping research unified into
the most sophisticated crawling system ever created.
"""

# Core platform components
from .core.config import get_settings
from .core.platform import SOSPlatform, quick_crawl, stealth_crawl, distributed_crawl
from .core.enhanced_crawler import EnhancedCrawlerManager
from .core.stealth_browser import StealthBrowserManager  
from .core.anti_detection import AntiDetectionManager
from .core.distributed import DistributedCoordinator

# Traditional SOS components (backwards compatibility)
from .crawler.crawler import BaseCrawler, StandardCrawler, CrawlResult
from .exporters.factory import ExporterFactory
from .proxy.pool import ProxyPool
from .scheduler.scheduler import BFSScheduler

# Revolutionary new components
try:
    from .proxy.advanced_pool import (
        AdvancedProxyPool, ProxyInfo, ProxyType, ProxySource, 
        RotationStrategy, create_proxy_pool
    )
    ADVANCED_PROXY_AVAILABLE = True
except ImportError:
    ADVANCED_PROXY_AVAILABLE = False

try:
    from .stealth.revolutionary_system import (
        StealthBrowserManager as RevolutionaryStealthBrowser,
        FingerprintProfile, HumanBehaviorSimulator, AdvancedCaptchaSolver,
        StealthLevel, BrowserEngine, create_stealth_browser
    )
    REVOLUTIONARY_STEALTH_AVAILABLE = True
except ImportError:
    REVOLUTIONARY_STEALTH_AVAILABLE = False

try:
    from .captcha.revolutionary_solver import (
        RevolutionaryCaptchaSolver, CaptchaChallenge, CaptchaType,
        SolvingMethod, create_captcha_solver
    )
    CAPTCHA_SOLVER_AVAILABLE = True
except ImportError:
    CAPTCHA_SOLVER_AVAILABLE = False

__version__ = "2.0.0"
__title__ = "Sparkling Owl Spin"
__description__ = "Revolutionary webscraping platform with enterprise-grade capabilities"

# Core system components (always available)
__all__ = [
    # Core platform
    "SOSPlatform",
    "quick_crawl", 
    "stealth_crawl",
    "distributed_crawl",
    "get_settings",
    
    # Enhanced components
    "EnhancedCrawlerManager", 
    "StealthBrowserManager",
    "AntiDetectionManager",
    "DistributedCoordinator",
    
    # Traditional components
    "BaseCrawler",
    "StandardCrawler",
    "CrawlResult",
    "ExporterFactory", 
    "ProxyPool",
    "BFSScheduler",
]

# Add revolutionary components if available
if ADVANCED_PROXY_AVAILABLE:
    __all__.extend([
        "AdvancedProxyPool",
        "ProxyInfo", 
        "ProxyType",
        "ProxySource",
        "RotationStrategy",
        "create_proxy_pool"
    ])

if REVOLUTIONARY_STEALTH_AVAILABLE:
    __all__.extend([
        "RevolutionaryStealthBrowser",
        "FingerprintProfile",
        "HumanBehaviorSimulator", 
        "AdvancedCaptchaSolver",
        "StealthLevel",
        "BrowserEngine",
        "create_stealth_browser"
    ])

if CAPTCHA_SOLVER_AVAILABLE:
    __all__.extend([
        "RevolutionaryCaptchaSolver",
        "CaptchaChallenge",
        "CaptchaType",
        "SolvingMethod", 
        "create_captcha_solver"
    ])

# Convenience functions for unified platform access
async def create_ultimate_crawling_platform(
    stealth_level: str = "advanced",
    proxy_strategy: str = "least_connections",
    enable_captcha_solving: bool = True,
    enable_ai: bool = True,
    distributed: bool = False
) -> SOSPlatform:
    """
    Create the ultimate crawling platform with all revolutionary components
    
    This function initializes a complete SOS platform with:
    - Advanced proxy management with intelligent rotation
    - Revolutionary stealth browser with fingerprint spoofing
    - AI-powered CAPTCHA solving capabilities
    - Distributed coordination for enterprise scaling
    - Enhanced crawling with Scrapy/Nutch algorithms
    
    Args:
        stealth_level: Stealth intensity ("basic", "standard", "advanced", "maximum", "ultimate")
        proxy_strategy: Proxy rotation strategy ("random", "round_robin", "least_connections", etc.)
        enable_captcha_solving: Enable AI-powered CAPTCHA solving
        enable_ai: Enable AI components (computer vision, deep learning)
        distributed: Enable distributed crawling coordination
    
    Returns:
        Fully configured SOSPlatform ready for enterprise-grade webscraping
    """
    
    platform = SOSPlatform()
    
    # Initialize advanced proxy pool if available
    if ADVANCED_PROXY_AVAILABLE:
        proxy_pool = await create_proxy_pool(
            min_size=50,
            max_size=500,
            rotation_strategy=proxy_strategy
        )
        platform.proxy_manager = proxy_pool
    
    # Initialize revolutionary stealth browser if available  
    if REVOLUTIONARY_STEALTH_AVAILABLE:
        stealth_browser = await create_stealth_browser(
            stealth_level=stealth_level,
            browser_engine="chromium",
            enable_captcha_solving=enable_captcha_solving,
            proxy_manager=platform.proxy_manager
        )
        platform.stealth_manager = stealth_browser
    
    # Initialize CAPTCHA solver if available
    if CAPTCHA_SOLVER_AVAILABLE and enable_captcha_solving:
        captcha_solver = await create_captcha_solver(
            enable_ai=enable_ai,
            enable_ocr=True,
            enable_audio=True,
            enable_learning=True
        )
        platform.captcha_solver = captcha_solver
    
    # Initialize distributed coordination if requested
    if distributed:
        platform.enable_distributed = True
    
    await platform.initialize()
    
    return platform

def get_system_info() -> dict:
    """Get information about available SOS platform components"""
    
    return {
        "version": __version__,
        "title": __title__,
        "description": __description__,
        "components": {
            "core_platform": True,
            "enhanced_crawler": True, 
            "basic_stealth": True,
            "basic_proxy": True,
            "advanced_proxy_pool": ADVANCED_PROXY_AVAILABLE,
            "revolutionary_stealth": REVOLUTIONARY_STEALTH_AVAILABLE,
            "captcha_solver": CAPTCHA_SOLVER_AVAILABLE,
        },
        "integrated_frameworks": [
            "Scrapy - Python's most powerful webscraping framework",
            "Apache Nutch - Enterprise distributed web crawler",
            "Colly - Fast and elegant scraping framework (Go)",
            "Crawlee - Modern web scraping and browser automation"
        ],
        "capabilities": [
            "BFS/DFS Crawling with Scrapy middleware architecture",
            "Distributed scaling with Nutch-inspired coordination", 
            "High-performance concurrent processing from Colly",
            "Advanced stealth and anti-detection from Crawlee",
            "AI-powered CAPTCHA solving with computer vision",
            "Multi-source proxy aggregation and intelligent rotation",
            "Complete browser fingerprint spoofing and behavioral simulation",
            "Enterprise-grade fault tolerance and auto-scaling"
        ]
    }

# Export convenience functions
__all__.extend([
    "create_ultimate_crawling_platform",
    "get_system_info"
])
