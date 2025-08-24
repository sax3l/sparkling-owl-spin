"""
Advanced Scrapy-Playwright Integration for Ultimate Scraping System

Integrerar scrapy-playwright-funktionalitet med våra befintliga stealth-system
för att skapa kraftfull, skalbar async web scraping med Playwright engine.
Kombinerar Scrapy's struktur med Playwright's browser automation.

Baserat på: https://github.com/scrapy-plugins/scrapy-playwright
"""

import asyncio
import logging
import time
import json
import uuid
import random
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from pathlib import Path
import tempfile
import concurrent.futures

try:
    from playwright.async_api import (
        async_playwright, 
        Browser, 
        BrowserContext, 
        Page, 
        Response as PlaywrightResponse,
        Request as PlaywrightRequest
    )
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available - Scrapy-Playwright integration disabled")

try:
    import scrapy
    from scrapy import Request, Spider
    from scrapy.http import Response, HtmlResponse
    from scrapy.settings import Settings
    from scrapy.crawler import CrawlerProcess, CrawlerRunner
    from scrapy.utils.project import get_project_settings
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    logging.warning("Scrapy not available - Scrapy integration features disabled")

# Import våra egna stealth-system
try:
    from enhanced_stealth_integration import EnhancedStealthManager, EnhancedStealthConfig
    STEALTH_INTEGRATION_AVAILABLE = True
except ImportError:
    STEALTH_INTEGRATION_AVAILABLE = False

# Stealth konfiguration för Playwright
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

@dataclass
class PageAction:
    """Representerar en action som ska utföras på en Playwright-sida"""
    
    method: str
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    wait_for: Optional[str] = None  # selector att vänta på
    delay: Optional[float] = None   # delay efter action
    result_key: Optional[str] = None  # nyckel för att spara resultat
    
    def __str__(self) -> str:
        return f"PageAction(method={self.method}, args={self.args[:2]}...)"

@dataclass 
class ScrapingResult:
    """Resultat från scraping-operation"""
    
    url: str
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    content: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    screenshots: List[bytes] = field(default_factory=list)
    pdfs: List[bytes] = field(default_factory=list)
    error: Optional[str] = None
    execution_time: float = 0.0
    page_actions_results: Dict[str, Any] = field(default_factory=dict)

class AdvancedScrapyPlaywrightManager:
    """
    Avancerad manager för Scrapy-Playwright integration med stealth-funktionalitet
    """
    
    def __init__(self, 
                 headless: bool = True,
                 max_concurrent_contexts: int = 5,
                 context_lifetime: int = 300,  # seconds
                 stealth_enabled: bool = True,
                 proxy_rotation: bool = False):
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright required for Scrapy-Playwright integration")
            
        self.headless = headless
        self.max_concurrent_contexts = max_concurrent_contexts
        self.context_lifetime = context_lifetime
        self.stealth_enabled = stealth_enabled
        self.proxy_rotation = proxy_rotation
        
        # Playwright components
        self.playwright = None
        self.browser = None
        self.contexts = {}  # Active browser contexts
        self.context_semaphore = asyncio.Semaphore(max_concurrent_contexts)
        
        # Stealth manager
        self.stealth_manager = None
        if stealth_enabled and STEALTH_INTEGRATION_AVAILABLE:
            self.stealth_manager = EnhancedStealthManager()
            
        # Statistics
        self.stats = {
            'pages_scraped': 0,
            'contexts_created': 0,
            'contexts_destroyed': 0,
            'errors': 0,
            'total_execution_time': 0.0,
            'avg_execution_time': 0.0
        }
        
        logging.info("Advanced Scrapy-Playwright Manager initialized")
        
    async def initialize(self):
        """Initialisera Playwright browser"""
        
        if self.playwright:
            return  # Already initialized
            
        self.playwright = await async_playwright().start()
        
        # Launch browser med stealth-inställningar
        browser_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-gpu',
            '--disable-sync',
            '--disable-translate',
            '--hide-scrollbars',
            '--mute-audio',
            '--disable-background-networking',
            '--disable-client-side-phishing-detection',
            '--disable-hang-monitor',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-domain-reliability'
        ]
        
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=browser_args,
            ignore_default_args=['--enable-automation']
        )
        
        logging.info("Playwright browser initialized with stealth configuration")
        
    async def create_stealth_context(self, 
                                   proxy: Optional[Dict[str, str]] = None,
                                   user_agent: Optional[str] = None) -> BrowserContext:
        """Skapa en stealth browser context"""
        
        async with self.context_semaphore:
            if not self.browser:
                await self.initialize()
                
            # Cleanup gamla contexts
            await self._cleanup_expired_contexts()
            
            # Välj slumpmässig user agent
            if not user_agent:
                user_agent = random.choice(USER_AGENTS)
                
            # Context options
            context_options = {
                'user_agent': user_agent,
                'viewport': {
                    'width': random.randint(1200, 1920),
                    'height': random.randint(800, 1080)
                },
                'device_scale_factor': random.choice([1.0, 1.25, 1.5]),
                'locale': random.choice(['en-US', 'en-GB', 'de-DE', 'fr-FR']),
                'timezone_id': random.choice(['America/New_York', 'Europe/London', 'Asia/Tokyo']),
                'extra_http_headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                },
                'ignore_https_errors': True
            }
            
            # Add proxy if provided
            if proxy:
                context_options['proxy'] = proxy
                
            context = await self.browser.new_context(**context_options)
            
            # Apply stealth scripts
            if self.stealth_manager:
                await self.stealth_manager.stealth_playwright_async(
                    await context.new_page()  # Temporary page for stealth application
                )
                
            # Advanced stealth scripts
            await self._apply_advanced_stealth_scripts(context)
            
            # Store context
            context_id = str(uuid.uuid4())
            self.contexts[context_id] = {
                'context': context,
                'created_at': time.time(),
                'user_agent': user_agent,
                'proxy': proxy
            }
            
            self.stats['contexts_created'] += 1
            return context
            
    async def _apply_advanced_stealth_scripts(self, context: BrowserContext):
        """Apply avancerade stealth-skript till context"""
        
        stealth_script = """
        // Advanced stealth script for Scrapy-Playwright
        (() => {
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock chrome runtime
            if (!window.chrome) {
                window.chrome = {};
            }
            window.chrome.runtime = {
                onConnect: undefined,
                onMessage: undefined,
            };
            
            // Override permissions
            const originalQuery = navigator.permissions.query;
            navigator.permissions.query = (parameters) => {
                return parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters);
            };
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Randomize canvas
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type) {
                const context = getContext.call(this, type);
                if (type === '2d' && context) {
                    const imageData = context.getImageData;
                    context.getImageData = function(...args) {
                        const data = imageData.apply(this, args);
                        // Add subtle noise
                        for (let i = 0; i < data.data.length; i += 4) {
                            if (Math.random() < 0.001) {
                                data.data[i] = Math.min(255, data.data[i] + 1);
                            }
                        }
                        return data;
                    };
                }
                return context;
            };
            
            // Block WebRTC IP leakage
            const RTCPeerConnection = window.RTCPeerConnection || 
                                    window.webkitRTCPeerConnection || 
                                    window.mozRTCPeerConnection;
            if (RTCPeerConnection) {
                window.RTCPeerConnection = function() {
                    throw new Error('WebRTC blocked for privacy');
                };
            }
        })();
        """
        
        await context.add_init_script(stealth_script)
        
    async def scrape_url(self,
                        url: str,
                        page_actions: List[PageAction] = None,
                        wait_for_selector: Optional[str] = None,
                        wait_for_load_state: str = 'networkidle',
                        timeout: int = 30000,
                        screenshot: bool = False,
                        pdf: bool = False,
                        context: Optional[BrowserContext] = None) -> ScrapingResult:
        """Scrapa en URL med avancerade Playwright-funktioner"""
        
        start_time = time.time()
        result = ScrapingResult(url=url)
        
        # Create context if not provided
        if not context:
            context = await self.create_stealth_context()
            context_created = True
        else:
            context_created = False
            
        page = None
        
        try:
            # Create page
            page = await context.new_page()
            
            # Navigate to URL
            response = await page.goto(url, 
                                     wait_until=wait_for_load_state, 
                                     timeout=timeout)
            
            if response:
                result.status_code = response.status
                result.headers = dict(response.headers)
                
            # Wait for specific selector if provided
            if wait_for_selector:
                try:
                    await page.wait_for_selector(wait_for_selector, timeout=10000)
                except Exception as e:
                    logging.warning(f"Selector wait failed: {e}")
                    
            # Execute page actions
            if page_actions:
                for action in page_actions:
                    try:
                        action_result = await self._execute_page_action(page, action)
                        if action.result_key:
                            result.page_actions_results[action.result_key] = action_result
                    except Exception as e:
                        logging.error(f"Page action {action.method} failed: {e}")
                        
            # Get page content
            result.content = await page.content()
            
            # Take screenshot if requested
            if screenshot:
                screenshot_data = await page.screenshot(full_page=True)
                result.screenshots.append(screenshot_data)
                
            # Generate PDF if requested  
            if pdf:
                pdf_data = await page.pdf(format='A4', print_background=True)
                result.pdfs.append(pdf_data)
                
            # Extract structured data (title, meta, etc.)
            result.data = await self._extract_page_data(page)
            
            self.stats['pages_scraped'] += 1
            
        except Exception as e:
            result.error = str(e)
            self.stats['errors'] += 1
            logging.error(f"Scraping failed for {url}: {e}")
            
        finally:
            if page:
                await page.close()
                
            if context_created and context:
                await context.close()
                
            # Update execution time
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            self.stats['total_execution_time'] += execution_time
            
            if self.stats['pages_scraped'] > 0:
                self.stats['avg_execution_time'] = (
                    self.stats['total_execution_time'] / self.stats['pages_scraped']
                )
                
        return result
        
    async def _execute_page_action(self, page: Page, action: PageAction) -> Any:
        """Utför en page action"""
        
        # Wait before action if specified
        if action.delay:
            await asyncio.sleep(action.delay)
            
        # Execute the action
        if hasattr(page, action.method):
            method = getattr(page, action.method)
            result = await method(*action.args, **action.kwargs)
        else:
            # Try to evaluate as JavaScript
            result = await page.evaluate(f"() => {action.method}")
            
        # Wait for selector after action if specified
        if action.wait_for:
            try:
                await page.wait_for_selector(action.wait_for, timeout=5000)
            except Exception as e:
                logging.warning(f"Wait for selector {action.wait_for} failed: {e}")
                
        return result
        
    async def _extract_page_data(self, page: Page) -> Dict[str, Any]:
        """Extrahera strukturerad data från sidan"""
        
        data = {}
        
        try:
            # Basic page information
            data['title'] = await page.title()
            data['url'] = page.url
            
            # Meta tags
            meta_tags = await page.evaluate("""
                () => {
                    const metas = {};
                    document.querySelectorAll('meta').forEach(meta => {
                        const name = meta.getAttribute('name') || meta.getAttribute('property');
                        const content = meta.getAttribute('content');
                        if (name && content) {
                            metas[name] = content;
                        }
                    });
                    return metas;
                }
            """)
            data['meta'] = meta_tags
            
            # Links
            links = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => ({
                        text: a.textContent.trim(),
                        href: a.href
                    }));
                }
            """)
            data['links'] = links[:50]  # Limit to first 50 links
            
            # Images
            images = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('img[src]')).map(img => ({
                        alt: img.alt,
                        src: img.src
                    }));
                }
            """)
            data['images'] = images[:20]  # Limit to first 20 images
            
            # Text content stats
            text_stats = await page.evaluate("""
                () => {
                    const text = document.body.innerText || '';
                    return {
                        length: text.length,
                        word_count: text.split(/\\s+/).filter(w => w.length > 0).length,
                        paragraph_count: document.querySelectorAll('p').length
                    };
                }
            """)
            data['text_stats'] = text_stats
            
        except Exception as e:
            logging.warning(f"Data extraction failed: {e}")
            
        return data
        
    async def batch_scrape(self,
                          urls: List[str],
                          page_actions: List[PageAction] = None,
                          max_concurrent: int = 3,
                          **kwargs) -> List[ScrapingResult]:
        """Batch scraping av flera URLs"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.scrape_url(url, page_actions, **kwargs)
                
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ScrapingResult(
                    url=urls[i],
                    error=str(result)
                ))
            else:
                final_results.append(result)
                
        return final_results
        
    async def _cleanup_expired_contexts(self):
        """Rensa upp gamla browser contexts"""
        
        current_time = time.time()
        expired_contexts = []
        
        for context_id, data in self.contexts.items():
            if current_time - data['created_at'] > self.context_lifetime:
                expired_contexts.append(context_id)
                
        for context_id in expired_contexts:
            try:
                await self.contexts[context_id]['context'].close()
                del self.contexts[context_id]
                self.stats['contexts_destroyed'] += 1
                logging.info(f"Expired context {context_id} cleaned up")
            except Exception as e:
                logging.error(f"Failed to cleanup context {context_id}: {e}")
                
    async def close(self):
        """Stäng alla resurser"""
        
        try:
            # Close all contexts
            for context_data in self.contexts.values():
                await context_data['context'].close()
                
            self.contexts.clear()
            
            # Close browser
            if self.browser:
                await self.browser.close()
                
            # Close playwright
            if self.playwright:
                await self.playwright.stop()
                
            logging.info("Scrapy-Playwright Manager closed successfully")
            
        except Exception as e:
            logging.error(f"Error closing manager: {e}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """Få statistik"""
        return {
            **self.stats,
            'active_contexts': len(self.contexts)
        }


# Convenience class for simple scraping
class StealthPlaywrightScraper:
    """Enkel wrapper för stealth Playwright scraping"""
    
    def __init__(self, **kwargs):
        self.manager = AdvancedScrapyPlaywrightManager(**kwargs)
        
    async def __aenter__(self):
        await self.manager.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.manager.close()
        
    async def scrape(self, url: str, **kwargs) -> ScrapingResult:
        """Scrapa en URL"""
        return await self.manager.scrape_url(url, **kwargs)
        
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrapa flera URLs"""
        return await self.manager.batch_scrape(urls, **kwargs)


async def demo_scrapy_playwright():
    """Demo av Advanced Scrapy-Playwright Integration"""
    
    print("🕷️ Advanced Scrapy-Playwright Integration Demo")
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available - cannot run demo")
        return
        
    async with StealthPlaywrightScraper(headless=True, stealth_enabled=True) as scraper:
        
        # Test basic scraping
        print("🌐 Testing basic scraping...")
        result = await scraper.scrape(
            "https://httpbin.org/user-agent",
            screenshot=True
        )
        
        print(f"✅ Scraped {result.url}")
        print(f"📊 Status: {result.status_code}")
        print(f"⏱️ Time: {result.execution_time:.2f}s")
        print(f"📄 Content length: {len(result.content)} chars")
        print(f"🖼️ Screenshots: {len(result.screenshots)}")
        
        if result.data:
            print(f"📋 Page data: title='{result.data.get('title', 'N/A')}'")
            print(f"🔗 Links found: {len(result.data.get('links', []))}")
            
        # Test page actions
        print("\n🎭 Testing page actions...")
        actions = [
            PageAction(method="evaluate", args=("document.title",), result_key="title"),
            PageAction(method="evaluate", args=("window.location.href",), result_key="location")
        ]
        
        result2 = await scraper.scrape(
            "https://httpbin.org/html",
            page_actions=actions
        )
        
        print(f"✅ Page actions executed")
        print(f"🎯 Results: {result2.page_actions_results}")
        
        # Test batch scraping
        print("\n📦 Testing batch scraping...")
        urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/xml", 
            "https://httpbin.org/html"
        ]
        
        batch_results = await scraper.scrape_multiple(urls, max_concurrent=2)
        
        print(f"✅ Batch scraping completed")
        print(f"📊 Results: {len(batch_results)} pages scraped")
        
        success_count = sum(1 for r in batch_results if not r.error)
        print(f"✅ Success rate: {success_count}/{len(batch_results)}")
        
        # Statistics
        stats = scraper.manager.get_statistics()
        print(f"\n📈 Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(demo_scrapy_playwright())
