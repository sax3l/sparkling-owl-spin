"""
Stealth Browser Manager - Advanced browser automation
Integrates Crawlee, Playwright, and Puppeteer patterns for maximum stealth
"""

import asyncio
import random
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import time

class BrowserType(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"

class StealthPlugin(Enum):
    """Stealth plugins inspired by puppeteer-extra-plugin-stealth"""
    USER_AGENT = "user_agent"
    VIEWPORT = "viewport"
    WEBGL_VENDOR = "webgl_vendor"
    NAVIGATOR_LANGUAGES = "navigator_languages"
    NAVIGATOR_PERMISSIONS = "navigator_permissions"
    CHROME_RUNTIME = "chrome_runtime"
    IFRAME_CONTENT_WINDOW = "iframe_content_window"
    MEDIA_CODECS = "media_codecs"

@dataclass
class BrowserFingerprint:
    """Browser fingerprint configuration"""
    user_agent: str
    viewport: Dict[str, int]
    locale: str
    timezone_id: str
    webgl_vendor: str
    webgl_renderer: str
    platform: str
    device_memory: int
    hardware_concurrency: int
    languages: List[str]

class StealthBrowserManager:
    """Advanced stealth browser manager"""
    
    def __init__(self, browser_type: BrowserType = BrowserType.CHROMIUM):
        self.browser_type = browser_type
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.contexts: List[BrowserContext] = []
        self.stealth_enabled = True
        self.logger = logging.getLogger("stealth_browser")
        
        # Fingerprint pools
        self.fingerprint_pool = self._generate_fingerprint_pool()
    
    def _generate_fingerprint_pool(self) -> List[BrowserFingerprint]:
        """Generate pool of realistic browser fingerprints"""
        fingerprints = []
        
        # Windows Chrome fingerprints
        for i in range(5):
            fingerprints.append(BrowserFingerprint(
                user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/12{i}.0.0.0 Safari/537.36",
                viewport={'width': random.choice([1920, 1366, 1536]), 'height': random.choice([1080, 768, 864])},
                locale="en-US",
                timezone_id="America/New_York",
                webgl_vendor="Google Inc. (Intel)",
                webgl_renderer="ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
                platform="Win32",
                device_memory=8,
                hardware_concurrency=random.choice([4, 8, 12, 16]),
                languages=["en-US", "en"]
            ))
        
        # macOS Safari fingerprints
        for i in range(3):
            fingerprints.append(BrowserFingerprint(
                user_agent=f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.{i} Safari/605.1.15",
                viewport={'width': random.choice([1440, 1680, 1920]), 'height': random.choice([900, 1050, 1080])},
                locale="en-US",
                timezone_id="America/Los_Angeles",
                webgl_vendor="Apple Inc.",
                webgl_renderer="Apple GPU",
                platform="MacIntel",
                device_memory=16,
                hardware_concurrency=random.choice([8, 10, 12]),
                languages=["en-US", "en"]
            ))
        
        # Linux Firefox fingerprints
        for i in range(3):
            fingerprints.append(BrowserFingerprint(
                user_agent=f"Mozilla/5.0 (X11; Linux x86_64; rv:12{i}.0) Gecko/20100101 Firefox/12{i}.0",
                viewport={'width': random.choice([1920, 1366, 1600]), 'height': random.choice([1080, 768, 900])},
                locale="en-US",
                timezone_id="America/Chicago",
                webgl_vendor="Mesa",
                webgl_renderer="Mesa Intel UHD Graphics 620 (CML GT2)",
                platform="Linux x86_64",
                device_memory=16,
                hardware_concurrency=random.choice([4, 8, 16]),
                languages=["en-US", "en"]
            ))
        
        return fingerprints
    
    async def launch(self, headless: bool = True, proxy: Optional[str] = None) -> Browser:
        """Launch browser with stealth configuration"""
        self.playwright = await async_playwright().start()
        
        # Browser launch options inspired by Crawlee
        launch_options = {
            'headless': headless,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
            ]
        }
        
        # Add proxy if specified
        if proxy:
            proxy_parts = proxy.replace('http://', '').replace('https://', '').split(':')
            if len(proxy_parts) == 2:
                launch_options['proxy'] = {
                    'server': f"http://{proxy_parts[0]}:{proxy_parts[1]}"
                }
        
        # Launch appropriate browser
        if self.browser_type == BrowserType.CHROMIUM:
            self.browser = await self.playwright.chromium.launch(**launch_options)
        elif self.browser_type == BrowserType.FIREFOX:
            self.browser = await self.playwright.firefox.launch(**launch_options)
        else:  # WEBKIT
            self.browser = await self.playwright.webkit.launch(**launch_options)
        
        return self.browser
    
    async def create_stealth_context(self, fingerprint: Optional[BrowserFingerprint] = None) -> BrowserContext:
        """Create a stealth browser context with fingerprint"""
        if not self.browser:
            await self.launch()
        
        if fingerprint is None:
            fingerprint = random.choice(self.fingerprint_pool)
        
        # Context options inspired by Crawlee fingerprints
        context_options = {
            'user_agent': fingerprint.user_agent,
            'viewport': fingerprint.viewport,
            'locale': fingerprint.locale,
            'timezone_id': fingerprint.timezone_id,
            'permissions': ['geolocation'],
            'java_script_enabled': True,
            'accept_downloads': False,
        }
        
        context = await self.browser.new_context(**context_options)
        
        # Apply stealth measures
        if self.stealth_enabled:
            await self._apply_stealth_measures(context, fingerprint)
        
        self.contexts.append(context)
        return context
    
    async def _apply_stealth_measures(self, context: BrowserContext, fingerprint: BrowserFingerprint):
        """Apply various stealth measures to context"""
        
        # Stealth script inspired by puppeteer-extra-plugin-stealth
        stealth_script = """
        // Override webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => %s,
        });
        
        // Override platform
        Object.defineProperty(navigator, 'platform', {
            get: () => '%s',
        });
        
        // Override deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => %d,
        });
        
        // Override hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => %d,
        });
        
        // Override WebGL vendor/renderer
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return '%s'; // UNMASKED_VENDOR_WEBGL
            if (parameter === 37446) return '%s'; // UNMASKED_RENDERER_WEBGL
            return getParameter.apply(this, arguments);
        };
        
        // Override chrome runtime (for Chrome detection)
        if (!window.chrome) {
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
            };
        }
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Hide iframe.contentWindow references
        const originalFrameContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
        Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
            get: function() {
                const originalReturn = originalFrameContentWindow.get.call(this);
                if (originalReturn) {
                    originalReturn.navigator.webdriver = undefined;
                }
                return originalReturn;
            }
        });
        """ % (
            json.dumps(fingerprint.languages),
            fingerprint.platform,
            fingerprint.device_memory,
            fingerprint.hardware_concurrency,
            fingerprint.webgl_vendor,
            fingerprint.webgl_renderer
        )
        
        # Add stealth script to all pages in context
        await context.add_init_script(stealth_script)
        
        # Additional stealth measures
        await self._add_stealth_headers(context)
        await self._setup_request_interception(context)
    
    async def _add_stealth_headers(self, context: BrowserContext):
        """Add stealth headers to all requests"""
        
        async def handle_route(route):
            headers = route.request.headers
            
            # Add/modify stealth headers
            stealth_headers = {
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
            }
            
            headers.update(stealth_headers)
            await route.continue_(headers=headers)
        
        await context.route("**/*", handle_route)
    
    async def _setup_request_interception(self, context: BrowserContext):
        """Setup request interception for additional stealth"""
        
        async def handle_request(route):
            request = route.request
            
            # Block known tracking/detection resources
            blocked_domains = [
                'doubleclick.net',
                'googletagmanager.com',
                'google-analytics.com',
                'googleadservices.com',
                'googlesyndication.com',
                'facebook.com/tr',
                'connect.facebook.net',
                'hotjar.com',
                'crazyegg.com',
            ]
            
            if any(domain in request.url for domain in blocked_domains):
                await route.abort()
                return
            
            # Add random delays to mimic human behavior
            if random.random() < 0.1:  # 10% chance
                await asyncio.sleep(random.uniform(0.1, 0.5))
            
            await route.continue_()
        
        await context.route("**/*", handle_request)
    
    async def create_stealth_page(self, context: Optional[BrowserContext] = None) -> Page:
        """Create a stealth page"""
        if context is None:
            context = await self.create_stealth_context()
        
        page = await context.new_page()
        
        # Additional page-level stealth measures
        await self._setup_page_stealth(page)
        
        return page
    
    async def _setup_page_stealth(self, page: Page):
        """Setup page-level stealth measures"""
        
        # Random viewport variations
        viewport = page.viewport_size
        if viewport:
            # Add small random variations to viewport
            width_variation = random.randint(-10, 10)
            height_variation = random.randint(-10, 10)
            await page.set_viewport_size({
                'width': max(800, viewport['width'] + width_variation),
                'height': max(600, viewport['height'] + height_variation)
            })
        
        # Human-like mouse movements
        await page.add_init_script("""
        // Add subtle mouse movement variations
        const originalDispatchEvent = EventTarget.prototype.dispatchEvent;
        EventTarget.prototype.dispatchEvent = function(event) {
            if (event.type === 'mousemove') {
                // Add tiny random variations to mouse position
                if (event.clientX !== undefined) {
                    event.clientX += Math.random() * 2 - 1;
                    event.clientY += Math.random() * 2 - 1;
                }
            }
            return originalDispatchEvent.call(this, event);
        };
        """)
    
    async def navigate_with_stealth(self, page: Page, url: str, **kwargs):
        """Navigate to URL with stealth measures"""
        
        # Random pre-navigation delay
        await asyncio.sleep(random.uniform(1, 3))
        
        # Navigate with human-like timing
        start_time = time.time()
        
        try:
            response = await page.goto(url, **kwargs)
            
            # Random post-navigation delay
            await asyncio.sleep(random.uniform(0.5, 2))
            
            # Simulate human reading time
            if response and response.status == 200:
                reading_time = random.uniform(2, 8)
                await asyncio.sleep(reading_time)
            
            navigation_time = time.time() - start_time
            self.logger.info(f"Navigation to {url} took {navigation_time:.2f}s")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Navigation error for {url}: {str(e)}")
            raise
    
    async def human_click(self, page: Page, selector: str, **kwargs):
        """Click with human-like behavior"""
        element = await page.query_selector(selector)
        if not element:
            raise Exception(f"Element not found: {selector}")
        
        # Get element bounding box for realistic click position
        box = await element.bounding_box()
        if box:
            # Click at a slightly random position within the element
            x = box['x'] + box['width'] * (0.3 + random.random() * 0.4)
            y = box['y'] + box['height'] * (0.3 + random.random() * 0.4)
            
            # Move mouse to element first (human-like)
            await page.mouse.move(x - 50, y - 50)
            await asyncio.sleep(random.uniform(0.1, 0.3))
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.2))
            
            # Click with human-like timing
            await page.mouse.click(x, y)
        else:
            # Fallback to selector click
            await element.click(**kwargs)
        
        # Post-click delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def human_type(self, page: Page, selector: str, text: str, **kwargs):
        """Type with human-like behavior"""
        await page.focus(selector)
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Type with random delays between characters
        for char in text:
            await page.keyboard.type(char)
            delay = random.uniform(0.05, 0.15)
            # Occasional longer pauses (like thinking)
            if random.random() < 0.1:
                delay += random.uniform(0.3, 0.8)
            await asyncio.sleep(delay)
        
        await asyncio.sleep(random.uniform(0.3, 0.7))
    
    async def scroll_page(self, page: Page, scroll_count: int = 3):
        """Scroll page with human-like behavior"""
        viewport = page.viewport_size
        if not viewport:
            return
        
        for i in range(scroll_count):
            # Scroll down
            scroll_y = random.randint(200, 600)
            await page.mouse.wheel(0, scroll_y)
            
            # Random reading pause
            await asyncio.sleep(random.uniform(1, 4))
            
            # Occasionally scroll back up slightly
            if random.random() < 0.3:
                await page.mouse.wheel(0, -random.randint(50, 150))
                await asyncio.sleep(random.uniform(0.5, 1.5))
    
    async def close(self):
        """Clean up browser resources"""
        for context in self.contexts:
            await context.close()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()

class CrawleeBrowserCrawler:
    """Crawlee-inspired browser crawler with stealth capabilities"""
    
    def __init__(self, 
                 browser_type: BrowserType = BrowserType.CHROMIUM,
                 headless: bool = True,
                 max_concurrent_pages: int = 3,
                 stealth_enabled: bool = True):
        
        self.browser_manager = StealthBrowserManager(browser_type)
        self.browser_manager.stealth_enabled = stealth_enabled
        self.headless = headless
        self.max_concurrent_pages = max_concurrent_pages
        self.semaphore = asyncio.Semaphore(max_concurrent_pages)
        self.results = []
        self.logger = logging.getLogger("crawlee_browser")
    
    async def crawl_urls(self, urls: List[str], request_handler: Callable):
        """Crawl multiple URLs with stealth browser"""
        await self.browser_manager.launch(headless=self.headless)
        
        try:
            tasks = []
            for url in urls:
                task = asyncio.create_task(self._crawl_single_url(url, request_handler))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error crawling {urls[i]}: {str(result)}")
                else:
                    self.results.extend(result if isinstance(result, list) else [result])
        
        finally:
            await self.browser_manager.close()
        
        return self.results
    
    async def _crawl_single_url(self, url: str, request_handler: Callable):
        """Crawl single URL with stealth measures"""
        async with self.semaphore:
            context = await self.browser_manager.create_stealth_context()
            page = await self.browser_manager.create_stealth_page(context)
            
            try:
                response = await self.browser_manager.navigate_with_stealth(
                    page, url, wait_until='networkidle'
                )
                
                # Call user-defined request handler
                result = await request_handler({
                    'page': page,
                    'response': response,
                    'url': url,
                    'browser_manager': self.browser_manager
                })
                
                return result
            
            except Exception as e:
                self.logger.error(f"Error processing {url}: {str(e)}")
                return None
            
            finally:
                await context.close()

# Example usage
async def example_news_crawler():
    """Example news crawling with stealth browser"""
    
    async def handle_request(context):
        page = context['page']
        url = context['url']
        browser_manager = context['browser_manager']
        
        # Wait for content to load
        await page.wait_for_load_state('networkidle')
        
        # Extract data
        title = await page.title()
        
        # Get article headlines
        headlines = []
        headline_selectors = [
            'h1, h2, h3',  # Generic headlines
            '.headline',   # Common headline class
            '[data-testid*="headline"]',  # Test ID patterns
        ]
        
        for selector in headline_selectors:
            elements = await page.query_selector_all(selector)
            for element in elements[:10]:  # Limit to first 10
                text = await element.text_content()
                if text and len(text.strip()) > 10:
                    headlines.append(text.strip())
        
        # Simulate human reading behavior
        await browser_manager.scroll_page(page, scroll_count=2)
        
        return {
            'url': url,
            'title': title,
            'headlines': headlines[:10],  # Top 10 headlines
            'timestamp': time.time()
        }
    
    # Create crawler
    crawler = CrawleeBrowserCrawler(
        browser_type=BrowserType.CHROMIUM,
        headless=True,
        max_concurrent_pages=2,
        stealth_enabled=True
    )
    
    # Crawl news sites
    news_urls = [
        'https://news.ycombinator.com',
        'https://www.bbc.com/news',
        'https://techcrunch.com'
    ]
    
    results = await crawler.crawl_urls(news_urls, handle_request)
    
    for result in results:
        if result:
            print(f"\nSite: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Headlines: {len(result['headlines'])}")
            for headline in result['headlines'][:3]:
                print(f"  - {headline}")

if __name__ == "__main__":
    asyncio.run(example_news_crawler())
