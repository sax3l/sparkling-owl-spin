"""
Stealth Browser Manager - Fixed Import Version
Complete standalone implementation without relative imports
"""

import asyncio
import random
import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import sys
import time

# Fix import paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("⚠️ Playwright not available - using mock mode")
    PLAYWRIGHT_AVAILABLE = False

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
    """Advanced stealth browser manager with Crawlee-inspired patterns"""
    
    def __init__(self, browser_type: BrowserType = BrowserType.CHROMIUM):
        self.browser_type = browser_type
        self.browser = None
        self.contexts = []
        self.fingerprint_pool = self._generate_fingerprint_pool()
        self.logger = logging.getLogger(__name__)
        
    def _generate_fingerprint_pool(self) -> List[BrowserFingerprint]:
        """Generate pool of realistic browser fingerprints"""
        fingerprints = []
        
        # Chrome fingerprints
        chrome_uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        ]
        
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
        ]
        
        for ua in chrome_uas:
            for viewport in viewports:
                fingerprint = BrowserFingerprint(
                    user_agent=ua,
                    viewport=viewport,
                    locale="en-US",
                    timezone_id="America/New_York",
                    webgl_vendor="Google Inc. (Intel)",
                    webgl_renderer="ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
                    platform="Win32",
                    device_memory=8,
                    hardware_concurrency=8,
                    languages=["en-US", "en"]
                )
                fingerprints.append(fingerprint)
                
        return fingerprints
    
    async def launch_browser(self, headless: bool = True):
        """Launch browser with stealth configuration"""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning("Playwright not available - returning mock browser")
            return MockBrowser()
            
        playwright = await async_playwright().start()
        
        launch_options = {
            "headless": headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-default-apps",
                "--disable-translate",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
            ]
        }
        
        if self.browser_type == BrowserType.CHROMIUM:
            self.browser = await playwright.chromium.launch(**launch_options)
        elif self.browser_type == BrowserType.FIREFOX:
            self.browser = await playwright.firefox.launch(**launch_options)
        else:
            self.browser = await playwright.webkit.launch(**launch_options)
            
        return self.browser
    
    async def create_stealth_context(self, fingerprint: Optional[BrowserFingerprint] = None) -> BrowserContext:
        """Create stealth browser context with fingerprint"""
        if not self.browser:
            await self.launch_browser()
        
        if fingerprint is None:
            fingerprint = random.choice(self.fingerprint_pool)
        
        context_options = {
            "user_agent": fingerprint.user_agent,
            "viewport": fingerprint.viewport,
            "locale": fingerprint.locale,
            "timezone_id": fingerprint.timezone_id,
            "extra_http_headers": {
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
            }
        }
        
        if not PLAYWRIGHT_AVAILABLE:
            return MockBrowserContext(fingerprint)
            
        context = await self.browser.new_context(**context_options)
        await self._apply_stealth_measures(context, fingerprint)
        
        self.contexts.append(context)
        return context
    
    async def _apply_stealth_measures(self, context: BrowserContext, fingerprint: BrowserFingerprint):
        """Apply comprehensive stealth measures"""
        stealth_script = f"""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined,
        }});
        
        // Mock chrome object
        window.chrome = {{
            runtime: {{}},
            app: {{
                isInstalled: false,
            }},
            webstore: {{
                onInstallStageChanged: {{}},
                onDownloadProgress: {{}},
            }},
        }};
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // Override webGL
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return '{fingerprint.webgl_vendor}';
            if (parameter === 37446) return '{fingerprint.webgl_renderer}';
            return getParameter.call(this, parameter);
        }};
        
        // Override device memory and hardware concurrency
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {fingerprint.device_memory},
        }});
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fingerprint.hardware_concurrency},
        }});
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {{
            get: () => {json.dumps(fingerprint.languages)},
        }});
        
        // Add connection spoofing
        Object.defineProperty(navigator, 'connection', {{
            get: () => ({{
                effectiveType: '4g',
                rtt: 100,
                downlink: 10,
                saveData: false,
            }}),
        }});
        """
        
        await context.add_init_script(stealth_script)
    
    async def create_stealth_page(self, context: Optional[BrowserContext] = None) -> 'Page':
        """Create stealth page with human-like behavior"""
        if context is None:
            context = await self.create_stealth_context()
        
        if not PLAYWRIGHT_AVAILABLE:
            return MockPage()
            
        page = await context.new_page()
        
        # Add human-like behavior
        await self._add_human_behavior(page)
        
        return page
    
    async def _add_human_behavior(self, page):
        """Add human-like mouse movements and timing"""
        await page.evaluate("""
        // Add random mouse movements
        const originalClick = HTMLElement.prototype.click;
        HTMLElement.prototype.click = function() {
            const event = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                clientX: Math.random() * window.innerWidth,
                clientY: Math.random() * window.innerHeight,
            });
            this.dispatchEvent(event);
            return originalClick.apply(this, arguments);
        };
        
        // Add typing delays
        document.addEventListener('keydown', (e) => {
            setTimeout(() => {}, Math.random() * 100 + 50);
        });
        """)
    
    async def navigate_stealthily(self, page, url: str, options: Dict = None) -> Dict[str, Any]:
        """Navigate with stealth and human-like timing"""
        options = options or {}
        
        # Random delay before navigation
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        try:
            if PLAYWRIGHT_AVAILABLE:
                response = await page.goto(url, **options)
                
                # Random delay after navigation
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                return {
                    "status": response.status if response else 200,
                    "url": url,
                    "success": True,
                    "title": await page.title(),
                }
            else:
                # Mock response
                await asyncio.sleep(random.uniform(0.1, 0.5))
                return {
                    "status": 200,
                    "url": url,
                    "success": True,
                    "title": f"Mock Page - {url}",
                }
                
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return {
                "status": 0,
                "url": url,
                "success": False,
                "error": str(e),
            }
    
    async def close(self):
        """Close all contexts and browser"""
        for context in self.contexts:
            if hasattr(context, 'close'):
                await context.close()
        
        if self.browser and hasattr(self.browser, 'close'):
            await self.browser.close()


# Mock classes for when Playwright is not available
class MockBrowser:
    async def new_context(self, **kwargs):
        return MockBrowserContext()
    
    async def close(self):
        pass

class MockBrowserContext:
    def __init__(self, fingerprint=None):
        self.fingerprint = fingerprint
    
    async def new_page(self):
        return MockPage()
    
    async def close(self):
        pass
    
    async def add_init_script(self, script):
        pass

class MockPage:
    async def goto(self, url, **kwargs):
        await asyncio.sleep(0.1)
        return MockResponse()
    
    async def title(self):
        return "Mock Page Title"
    
    async def evaluate(self, script):
        return None
    
    async def close(self):
        pass

class MockResponse:
    def __init__(self):
        self.status = 200


# Crawlee-inspired browser crawler
class CrawleeBrowserCrawler:
    """Browser crawler inspired by Crawlee patterns"""
    
    def __init__(self, stealth_manager: StealthBrowserManager = None):
        self.stealth_manager = stealth_manager or StealthBrowserManager()
        self.request_queue = []
        self.results = []
        
    async def run(self, urls: List[str], handler: Callable = None):
        """Run crawler on URLs"""
        if handler is None:
            handler = self.default_handler
            
        browser = await self.stealth_manager.launch_browser()
        context = await self.stealth_manager.create_stealth_context()
        
        try:
            for url in urls:
                page = await self.stealth_manager.create_stealth_page(context)
                
                result = await self.stealth_manager.navigate_stealthily(page, url)
                
                if result["success"]:
                    processed_result = await handler(page, result)
                    self.results.append(processed_result)
                
                await page.close()
                
        finally:
            await self.stealth_manager.close()
    
    async def default_handler(self, page, response_data):
        """Default request handler"""
        return {
            "url": response_data["url"],
            "title": response_data.get("title", ""),
            "status": response_data["status"],
            "timestamp": time.time(),
        }


# Export all classes
__all__ = [
    'StealthBrowserManager',
    'CrawleeBrowserCrawler',
    'BrowserType',
    'BrowserFingerprint',
    'StealthPlugin'
]
