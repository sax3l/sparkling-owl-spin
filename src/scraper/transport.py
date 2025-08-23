"""
Scraping Transport - Advanced transport layer for data extraction.

Provides intelligent transport selection and management including:
- HTTP and browser-based fetching
- Stealth techniques and fingerprint avoidance
- Dynamic transport switching
- Resource optimization and blocking
- Policy-based transport selection
"""

import asyncio
import time
from typing import Tuple, Dict, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from playwright.async_api import async_playwright, Page, Browser

from ..anti_bot.policy_manager import DomainPolicy  
from ..anti_bot.header_generator import HeaderGenerator
from ..anti_bot.session_manager import SessionManager
from ..utils.logger import get_logger
from ..observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class TransportResult:
    """Result from transport operation."""
    content: str
    status_code: int
    response_time: float
    transport_type: str
    final_url: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ScrapingTransport:
    """
    Advanced transport manager for intelligent content fetching.
    
    Abstracts the fetching mechanism, allowing for dynamic switching
    between HTTP requests and browser sessions based on policy and content analysis.
    
    Features:
    - Intelligent transport selection
    - Stealth browsing capabilities
    - Resource optimization
    - Fallback mechanisms
    - Performance monitoring
    """
    
    def __init__(
        self,
        header_generator: HeaderGenerator,
        session_manager: SessionManager,
        metrics_collector: MetricsCollector,
        http_timeout: float = 30.0,
        browser_timeout: float = 60.0
    ):
        self.header_generator = header_generator
        self.session_manager = session_manager
        self.metrics = metrics_collector
        self.http_timeout = http_timeout
        self.browser_timeout = browser_timeout
        
        # Browser context management
        self._browser_context = None
        self._page_pool = []
        self._max_pages = 5
        
    async def fetch(
        self, 
        url: str, 
        policy: DomainPolicy,
        force_transport: Optional[str] = None
    ) -> TransportResult:
        """
        Fetch URL content based on transport policy.
        
        Args:
            url: Target URL to fetch
            policy: Domain-specific policy configuration
            force_transport: Override transport selection ('http' or 'browser')
            
        Returns:
            TransportResult with content and metadata
        """
        start_time = time.time()
        
        # Determine transport method
        transport_type = force_transport or policy.transport
        
        logger.debug(f"Fetching {url} using {transport_type} transport")
        
        try:
            if transport_type == "browser":
                result = await self._fetch_with_browser(url, policy)
            else:
                result = await self._fetch_with_http(url, policy)
                
            # If HTTP fails and policy allows fallback, try browser
            if (result.status_code >= 400 and 
                transport_type == "http" and 
                policy.fallback_to_browser):
                
                logger.info(f"HTTP fetch failed for {url}, falling back to browser")
                result = await self._fetch_with_browser(url, policy)
                
            result.response_time = time.time() - start_time
            
            # Update metrics
            self.metrics.timer(f"transport_{result.transport_type}_time", result.response_time)
            self.metrics.counter(f"transport_{result.transport_type}_requests", 1)
            
            if result.status_code >= 400:
                self.metrics.counter(f"transport_{result.transport_type}_errors", 1)
                
            return result
            
        except Exception as e:
            logger.error(f"Transport error for {url}: {e}")
            return TransportResult(
                content="",
                status_code=500,
                response_time=time.time() - start_time,
                transport_type=transport_type,
                final_url=url,
                error=str(e)
            )
            
    async def _fetch_with_http(self, url: str, policy: DomainPolicy) -> TransportResult:
        """Fetch content using HTTP client."""
        try:
            # Generate headers
            headers = self.header_generator.generate_headers(policy.domain)
            
            # Get session and proxy
            session_data = await self.session_manager.get_session(policy.domain)
            
            # Configure HTTP client
            client_config = {
                'timeout': self.http_timeout,
                'follow_redirects': True,
                'headers': headers
            }
            
            # Add proxy if available
            if session_data.get('proxy'):
                proxy_config = session_data['proxy']
                client_config['proxies'] = {
                    'http://': f"http://{proxy_config['host']}:{proxy_config['port']}",
                    'https://': f"http://{proxy_config['host']}:{proxy_config['port']}"
                }
                
            # Add cookies if available
            cookies = session_data.get('cookies', {})
            
            async with httpx.AsyncClient(**client_config) as client:
                # Apply rate limiting
                await self._apply_rate_limiting(policy)
                
                response = await client.get(url, cookies=cookies)
                
                # Update session with new cookies
                if response.cookies:
                    new_cookies = dict(response.cookies)
                    await self.session_manager.update_session_cookies(
                        policy.domain, new_cookies
                    )
                    
                return TransportResult(
                    content=response.text,
                    status_code=response.status_code,
                    response_time=0.0,  # Will be set by caller
                    transport_type="http",
                    final_url=str(response.url),
                    metadata={
                        'headers': dict(response.headers),
                        'cookies': dict(response.cookies),
                        'redirects': len(response.history)
                    }
                )
                
        except Exception as e:
            logger.error(f"HTTP fetch error for {url}: {e}")
            return TransportResult(
                content="",
                status_code=500,
                response_time=0.0,
                transport_type="http",
                final_url=url,
                error=str(e)
            )
            
    async def _fetch_with_browser(self, url: str, policy: DomainPolicy) -> TransportResult:
        """Fetch content using browser automation."""
        page = None
        try:
            # Get or create browser page
            page = await self._get_browser_page()
            
            # Apply stealth measures
            await self._apply_stealth_measures(page, policy)
            
            # Apply rate limiting
            await self._apply_rate_limiting(policy)
            
            # Navigate to URL
            response = await page.goto(
                url,
                timeout=self.browser_timeout * 1000,  # Convert to milliseconds
                wait_until='domcontentloaded'
            )
            
            status_code = response.status if response else 200
            
            # Wait for dynamic content if needed
            if policy.wait_for_js:
                await page.wait_for_load_state('networkidle', timeout=10000)
                
            # Extract content
            content = await page.content()
            final_url = page.url
            
            # Get metadata
            metadata = {
                'user_agent': await page.evaluate('navigator.userAgent'),
                'viewport': await page.viewport_size(),
                'cookies': await page.context.cookies(url)
            }
            
            return TransportResult(
                content=content,
                status_code=status_code,
                response_time=0.0,  # Will be set by caller
                transport_type="browser",
                final_url=final_url,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Browser fetch error for {url}: {e}")
            return TransportResult(
                content="",
                status_code=500,
                response_time=0.0,
                transport_type="browser",
                final_url=url,
                error=str(e)
            )
        finally:
            if page:
                await self._release_browser_page(page)
                
    async def _get_browser_page(self) -> Page:
        """Get or create a browser page from the pool."""
        if self._page_pool:
            return self._page_pool.pop()
            
        # Create new browser context if needed
        if not self._browser_context:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Speed optimization
                    '--disable-javascript-harmony-shipping',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection'
                ]
            )
            
            self._browser_context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
        return await self._browser_context.new_page()
        
    async def _release_browser_page(self, page: Page):
        """Return page to pool or close it."""
        try:
            # Clear page state
            await page.goto('about:blank')
            
            # Add to pool if under limit
            if len(self._page_pool) < self._max_pages:
                self._page_pool.append(page)
            else:
                await page.close()
                
        except Exception as e:
            logger.debug(f"Error releasing page: {e}")
            try:
                await page.close()
            except:
                pass
                
    async def _apply_stealth_measures(self, page: Page, policy: DomainPolicy):
        """Apply stealth measures to browser page."""
        try:
            # Block unnecessary resources for speed and stealth
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2,ttf,ico}", 
                            lambda route: route.abort())
            
            # Block tracking and analytics
            tracking_patterns = [
                '**/analytics.js', '**/gtag/*', '**/ga.js', '**/google-analytics/*',
                '**/facebook.net/*', '**/doubleclick.net/*', '**/googletagmanager.com/*'
            ]
            
            for pattern in tracking_patterns:
                await page.route(pattern, lambda route: route.abort())
                
            # Override navigator properties to avoid detection
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                window.chrome = {
                    runtime: {},
                };
            """)
            
            # Set realistic headers
            domain = urlparse(page.url).netloc if hasattr(page, 'url') else policy.domain
            headers = self.header_generator.generate_headers(domain)
            await page.set_extra_http_headers(headers)
            
        except Exception as e:
            logger.debug(f"Error applying stealth measures: {e}")
            
    async def _apply_rate_limiting(self, policy: DomainPolicy):
        """Apply rate limiting based on policy."""
        if policy.request_delay > 0:
            await asyncio.sleep(policy.request_delay)
            
    async def batch_fetch(
        self, 
        urls: list[str], 
        policy: DomainPolicy,
        max_concurrent: int = 5
    ) -> list[TransportResult]:
        """Fetch multiple URLs concurrently with rate limiting."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url):
            async with semaphore:
                return await self.fetch(url, policy)
                
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(TransportResult(
                    content="",
                    status_code=500,
                    response_time=0.0,
                    transport_type="unknown",
                    final_url=urls[i],
                    error=str(result)
                ))
            else:
                final_results.append(result)
                
        return final_results
        
    async def cleanup(self):
        """Clean up browser resources."""
        try:
            # Close all pages in pool
            while self._page_pool:
                page = self._page_pool.pop()
                await page.close()
                
            # Close browser context
            if self._browser_context:
                await self._browser_context.close()
                self._browser_context = None
                
        except Exception as e:
            logger.error(f"Error during transport cleanup: {e}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get transport statistics."""
        return {
            'browser_pages_pooled': len(self._page_pool),
            'browser_context_active': self._browser_context is not None,
            'max_pages': self._max_pages,
            'http_timeout': self.http_timeout,
            'browser_timeout': self.browser_timeout
        }


# Backward compatibility alias
TransportManager = ScrapingTransport