"""
Scraper Module - Advanced data extraction capabilities.

Provides comprehensive data scraping functionality including:
- Template-based data extraction
- HTTP and browser-based scraping
- XPath and CSS selector support
- Data transformation and validation
- Image and file downloading
- Login and session management

Main Components:
- BaseScraper: Core scraping functionality
- HTTPScraper: HTTP-based scraping
- SeleniumScraper: Browser-based scraping
- TemplateExtractor: Template-driven extraction
- TemplateRuntime: Template execution engine
- XPathSuggester: XPath generation and optimization
- LoginHandler: Authentication management
- ImageDownloader: File download capabilities
"""

from .base_scraper import BaseScraper
from .http_scraper import HTTPScraper
from .selenium_scraper import SeleniumScraper
from .template_extractor import TemplateExtractor
from .template_runtime import TemplateRuntime
from .xpath_suggester import XPathSuggester
from .login_handler import LoginHandler
from .image_downloader import ImageDownloader
from .transport import ScrapingTransport

# DSL components
from .dsl import TemplateDSL, FieldTransformer, ValidationRule

__all__ = [
    "BaseScraper",
    "HTTPScraper",
    "SeleniumScraper", 
    "TemplateExtractor",
    "TemplateRuntime",
    "XPathSuggester",
    "LoginHandler",
    "ImageDownloader",
    "ScrapingTransport",
    "TemplateDSL",
    "FieldTransformer", 
    "ValidationRule"
]