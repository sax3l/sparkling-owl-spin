"""
Base scraper class for ECaDP platform.

Provides common functionality for all scraper implementations.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    url: str
    data: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    response_time_ms: int = 0
    status_code: Optional[int] = None
    scraped_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ScrapingConfig:
    """Configuration for scraping operations."""
    delay_seconds: float = 1.0
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    user_agent: Optional[str] = None
    headers: Dict[str, str] = None
    cookies: Dict[str, str] = None
    proxy: Optional[str] = None
    verify_ssl: bool = True
    follow_redirects: bool = True
    max_redirects: int = 5

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.cookies is None:
            self.cookies = {}

class BaseScraper(ABC):
    """Base class for all scrapers in the ECaDP platform."""
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.config = config or ScrapingConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._session = None
        self._last_request_time = 0
        
    @abstractmethod
    async def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape a single URL and return structured data."""
        pass
    
    @abstractmethod
    async def extract_data(self, content: str, url: str, **kwargs) -> Dict[str, Any]:
        """Extract structured data from HTML content."""
        pass
    
    async def scrape_multiple_urls(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrape multiple URLs sequentially."""
        results = []
        
        for url in urls:
            try:
                # Apply delay between requests
                await self._apply_delay()
                
                result = await self.scrape_url(url, **kwargs)
                results.append(result)
                
                self.logger.info(f"Scraped {url}: {'success' if result.success else 'failed'}")
                
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {e}")
                results.append(ScrapingResult(
                    url=url,
                    data={},
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    async def scrape_with_retries(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape URL with retry logic."""
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.config.retry_delay_seconds * (2 ** (attempt - 1))
                    self.logger.info(f"Retrying {url} (attempt {attempt + 1}) after {delay}s delay")
                    await self._sleep(delay)
                
                result = await self.scrape_url(url, **kwargs)
                
                if result.success:
                    return result
                else:
                    last_error = result.error_message
                    
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
        
        # All retries failed
        return ScrapingResult(
            url=url,
            data={},
            success=False,
            error_message=f"Failed after {self.config.max_retries + 1} attempts: {last_error}"
        )
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is properly formatted."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ['http', 'https'])
        except Exception:
            return False
    
    def normalize_url(self, url: str, base_url: Optional[str] = None) -> str:
        """Normalize URL by resolving relative URLs and cleaning up."""
        if base_url:
            url = urljoin(base_url, url)
        
        # Remove fragment identifier
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        return urlparse(url).netloc
    
    async def _apply_delay(self):
        """Apply rate limiting delay between requests."""
        if self.config.delay_seconds > 0:
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            
            if time_since_last < self.config.delay_seconds:
                delay_needed = self.config.delay_seconds - time_since_last
                await self._sleep(delay_needed)
            
            self._last_request_time = time.time()
    
    async def _sleep(self, seconds: float):
        """Async sleep wrapper."""
        import asyncio
        await asyncio.sleep(seconds)
    
    def _prepare_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers for request."""
        headers = self.config.headers.copy()
        
        if self.config.user_agent:
            headers['User-Agent'] = self.config.user_agent
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _handle_response_error(self, response, url: str) -> str:
        """Handle HTTP response errors."""
        if hasattr(response, 'status_code'):
            status_code = response.status_code
        elif hasattr(response, 'status'):
            status_code = response.status
        else:
            status_code = None
        
        if status_code:
            if status_code == 403:
                return "Access forbidden - possible anti-bot detection"
            elif status_code == 404:
                return "Page not found"
            elif status_code == 429:
                return "Rate limited - too many requests"
            elif status_code >= 500:
                return f"Server error: {status_code}"
            else:
                return f"HTTP error: {status_code}"
        
        return "Unknown response error"
    
    def get_scraper_stats(self) -> Dict[str, Any]:
        """Get statistics about this scraper instance."""
        return {
            "scraper_type": self.__class__.__name__,
            "config": {
                "delay_seconds": self.config.delay_seconds,
                "timeout_seconds": self.config.timeout_seconds,
                "max_retries": self.config.max_retries,
                "user_agent": self.config.user_agent,
                "proxy": self.config.proxy
            },
            "last_request_time": self._last_request_time
        }
    
    async def cleanup(self):
        """Clean up resources (sessions, connections, etc.)."""
        if self._session:
            if hasattr(self._session, 'close'):
                await self._session.close()
            self._session = None
        
        self.logger.info(f"{self.__class__.__name__} cleanup completed")

__all__ = ["BaseScraper", "ScrapingResult", "ScrapingConfig"]