#!/usr/bin/env python3
"""
Playwright Integration - Revolutionary Ultimate System v4.0
Modern browser automation with multi-browser support
"""

import asyncio
import logging
import time
import json
import os
import tempfile
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
    from playwright.async_api import Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PlaywrightConfig:
    """Configuration for Playwright"""
    enabled: bool = True
    browser_type: str = 'chromium'  # chromium, firefox, webkit
    headless: bool = True
    viewport: Dict[str, int] = None
    user_agent: Optional[str] = None
    timeout: int = 30000  # milliseconds
    navigation_timeout: int = 30000
    extra_http_headers: Optional[Dict[str, str]] = None
    ignore_https_errors: bool = True
    java_script_enabled: bool = True
    bypass_csp: bool = False
    locale: str = 'en-US'
    timezone: str = 'UTC'
    geolocation: Optional[Dict[str, float]] = None
    permissions: Optional[List[str]] = None
    color_scheme: str = 'light'  # light, dark, no-preference
    reduced_motion: str = 'no-preference'  # reduce, no-preference
    forced_colors: str = 'none'  # active, none
    proxy: Optional[Dict[str, str]] = None
    device_name: Optional[str] = None  # iPhone 12, Pixel 5, etc.
    max_concurrent_contexts: int = 5
    max_concurrent_pages: int = 10
    screenshot_mode: str = 'on-failure'  # always, on-failure, never
    video_mode: str = 'off'  # on, off, retain-on-failure
    trace_mode: str = 'off'  # on, off, retain-on-failure
    slow_mo: int = 0  # milliseconds
    debug: bool = False

@dataclass
class PlaywrightResult:
    """Container for Playwright results"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    html: Optional[str] = None
    status_code: int = 200
    load_time: float = 0.0
    screenshot: Optional[str] = None  # Base64 encoded
    pdf: Optional[str] = None  # Base64 encoded
    elements: Optional[List[Dict[str, Any]]] = None
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    network_logs: Optional[List[Dict[str, Any]]] = None
    console_logs: Optional[List[Dict[str, str]]] = None
    cookies: Optional[List[Dict[str, Any]]] = None
    local_storage: Optional[Dict[str, str]] = None
    session_storage: Optional[Dict[str, str]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    accessibility_tree: Optional[Dict[str, Any]] = None
    coverage_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    extraction_time: float = 0.0

class PlaywrightManager:
    """
    Playwright manager for modern browser automation.
    
    Features:
    - Multi-browser support (Chromium, Firefox, WebKit)
    - Device emulation
    - Network interception
    - Performance monitoring
    - Accessibility testing
    - Code coverage
    - Video recording
    - Tracing
    - PDF generation
    """
    
    def __init__(self, config: PlaywrightConfig):
        self.config = config
        self.playwright = None
        self.browser = None
        self.contexts = {}
        self.pages = {}
        self.temp_dir = None
        self._stats = {
            'browsers_launched': 0,
            'contexts_created': 0,
            'pages_created': 0,
            'pages_loaded': 0,
            'pages_failed': 0,
            'total_load_time': 0.0,
            'screenshots_taken': 0,
            'pdfs_generated': 0,
            'network_requests': 0,
            'console_messages': 0,
            'active_contexts': 0,
            'active_pages': 0
        }
        
        if not PLAYWRIGHT_AVAILABLE:
            if self.config.enabled:
                raise ImportError("Playwright not available. Install with: pip install playwright && playwright install")
            
    async def initialize(self):
        """Initialize Playwright manager"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing Playwright manager...")
        
        try:
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix="playwright_"))
            
            # Initialize Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser
            await self._launch_browser()
            
            logger.info("✅ Playwright manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Playwright: {str(e)}")
            raise
            
    async def _launch_browser(self):
        """Launch browser"""
        
        try:
            # Configure browser options
            browser_options = {
                'headless': self.config.headless,
                'slow_mo': self.config.slow_mo,
                'timeout': self.config.timeout,
                'args': []
            }
            
            # Add proxy if configured
            if self.config.proxy:
                browser_options['proxy'] = self.config.proxy
                
            # Add extra arguments for Chromium
            if self.config.browser_type == 'chromium':
                browser_options['args'].extend([
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ])
                
            # Get browser
            if self.config.browser_type == 'chromium':
                self.browser = await self.playwright.chromium.launch(**browser_options)
            elif self.config.browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(**browser_options)
            elif self.config.browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(**browser_options)
            else:
                raise ValueError(f"Unsupported browser: {self.config.browser_type}")
                
            self._stats['browsers_launched'] += 1
            logger.info(f"✅ {self.config.browser_type.title()} browser launched")
            
        except Exception as e:
            logger.error(f"❌ Failed to launch browser: {str(e)}")
            raise
            
    async def create_context(self, context_id: str = None, **context_options) -> str:
        """Create new browser context"""
        
        if not self.config.enabled or not self.browser:
            raise RuntimeError("Playwright not available")
            
        if context_id is None:
            context_id = f"context_{len(self.contexts)}"
            
        try:
            # Prepare context options
            options = {
                'viewport': self.config.viewport or {'width': 1920, 'height': 1080},
                'user_agent': self.config.user_agent,
                'extra_http_headers': self.config.extra_http_headers,
                'ignore_https_errors': self.config.ignore_https_errors,
                'java_script_enabled': self.config.java_script_enabled,
                'bypass_csp': self.config.bypass_csp,
                'locale': self.config.locale,
                'timezone_id': self.config.timezone,
                'geolocation': self.config.geolocation,
                'permissions': self.config.permissions,
                'color_scheme': self.config.color_scheme,
                'reduced_motion': self.config.reduced_motion,
                'forced_colors': self.config.forced_colors
            }
            
            # Add device emulation if specified
            if self.config.device_name:
                device = self.playwright.devices.get(self.config.device_name)
                if device:
                    options.update(device)
                else:
                    logger.warning(f"⚠️ Unknown device: {self.config.device_name}")
                    
            # Add recording options
            if self.config.video_mode != 'off':
                video_dir = self.temp_dir / "videos"
                video_dir.mkdir(exist_ok=True)
                options['record_video_dir'] = str(video_dir)
                options['record_video_size'] = options['viewport']
                
            if self.config.trace_mode != 'off':
                # Tracing will be started per page
                pass
                
            # Override with custom options
            options.update(context_options)
            
            # Filter None values
            options = {k: v for k, v in options.items() if v is not None}
            
            # Create context
            context = await self.browser.new_context(**options)
            
            # Setup event listeners
            await self._setup_context_listeners(context)
            
            self.contexts[context_id] = context
            self._stats['contexts_created'] += 1
            self._stats['active_contexts'] = len(self.contexts)
            
            logger.info(f"✅ Context '{context_id}' created")
            return context_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create context: {str(e)}")
            raise
            
    async def _setup_context_listeners(self, context: BrowserContext):
        """Setup event listeners for context"""
        
        # Network monitoring
        async def handle_request(request):
            self._stats['network_requests'] += 1
            if self.config.debug:
                logger.debug(f"🌐 Request: {request.method} {request.url}")
                
        async def handle_response(response):
            if self.config.debug:
                logger.debug(f"📥 Response: {response.status} {response.url}")
                
        context.on('request', handle_request)
        context.on('response', handle_response)
        
    async def create_page(self, context_id: str, page_id: str = None) -> str:
        """Create new page in context"""
        
        if context_id not in self.contexts:
            raise ValueError(f"Context '{context_id}' not found")
            
        if page_id is None:
            page_id = f"page_{len(self.pages)}"
            
        try:
            context = self.contexts[context_id]
            page = await context.new_page()
            
            # Setup page timeouts
            page.set_default_timeout(self.config.timeout)
            page.set_default_navigation_timeout(self.config.navigation_timeout)
            
            # Setup event listeners
            await self._setup_page_listeners(page)
            
            # Start tracing if enabled
            if self.config.trace_mode != 'off':
                trace_file = self.temp_dir / f"trace_{page_id}.zip"
                await page.context.tracing.start(
                    screenshots=True,
                    snapshots=True
                )
                
            self.pages[page_id] = {
                'page': page,
                'context_id': context_id,
                'console_logs': [],
                'network_logs': []
            }
            
            self._stats['pages_created'] += 1
            self._stats['active_pages'] = len(self.pages)
            
            logger.info(f"✅ Page '{page_id}' created in context '{context_id}'")
            return page_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create page: {str(e)}")
            raise
            
    async def _setup_page_listeners(self, page: Page):
        """Setup event listeners for page"""
        
        # Console monitoring
        async def handle_console(message):
            self._stats['console_messages'] += 1
            console_entry = {
                'type': message.type,
                'text': message.text,
                'location': f"{message.location.get('url', '')}:{message.location.get('lineNumber', 0)}",
                'timestamp': time.time()
            }
            
            # Find page data and add console log
            for page_data in self.pages.values():
                if page_data['page'] == page:
                    page_data['console_logs'].append(console_entry)
                    break
                    
            if self.config.debug:
                logger.debug(f"📝 Console {message.type}: {message.text}")
                
        page.on('console', handle_console)
        
        # Error monitoring
        async def handle_page_error(error):
            logger.error(f"❌ Page error: {str(error)}")
            
        page.on('pageerror', handle_page_error)
        
    async def navigate_to(self, page_id: str, url: str,
                         wait_until: str = 'domcontentloaded') -> PlaywrightResult:
        """Navigate page to URL"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page_data = self.pages[page_id]
        page = page_data['page']
        start_time = time.time()
        
        try:
            logger.info(f"🌐 Navigating to {url} in page '{page_id}'")
            
            # Clear logs
            page_data['console_logs'] = []
            page_data['network_logs'] = []
            
            # Navigate
            response = await page.goto(url, wait_until=wait_until)
            
            load_time = time.time() - start_time
            status_code = response.status if response else 200
            
            # Create result
            result = PlaywrightResult(
                url=page.url,
                title=await page.title(),
                load_time=load_time,
                status_code=status_code
            )
            
            self._stats['pages_loaded'] += 1
            self._stats['total_load_time'] += load_time
            
            logger.info(f"✅ Page loaded in {load_time:.2f}s (status: {status_code})")
            return result
            
        except Exception as e:
            load_time = time.time() - start_time
            self._stats['pages_failed'] += 1
            
            logger.error(f"❌ Failed to navigate: {str(e)}")
            return PlaywrightResult(
                url=url,
                load_time=load_time,
                status_code=0,
                error=str(e)
            )
            
    async def extract_content(self, page_id: str,
                            selectors: Optional[Dict[str, str]] = None,
                            extract_links: bool = True,
                            extract_images: bool = True,
                            extract_performance: bool = False,
                            extract_accessibility: bool = False) -> PlaywrightResult:
        """Extract content from page"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page_data = self.pages[page_id]
        page = page_data['page']
        start_time = time.time()
        
        try:
            result = PlaywrightResult(
                url=page.url,
                title=await page.title(),
                content=await page.text_content('body'),
                html=await page.content()
            )
            
            # Extract elements with selectors
            if selectors:
                elements = []
                
                for name, selector in selectors.items():
                    try:
                        elements_found = await page.query_selector_all(selector)
                        
                        for element in elements_found:
                            element_data = {
                                'selector': selector,
                                'tag_name': await element.evaluate('el => el.tagName'),
                                'text_content': await element.text_content(),
                                'inner_html': await element.inner_html(),
                                'attributes': await element.evaluate('''el => {
                                    const attrs = {};
                                    for (let i = 0; i < el.attributes.length; i++) {
                                        attrs[el.attributes[i].name] = el.attributes[i].value;
                                    }
                                    return attrs;
                                }'''),
                                'bounding_box': await element.bounding_box(),
                                'visible': await element.is_visible()
                            }
                            elements.append(element_data)
                            
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to extract with selector '{selector}': {str(e)}")
                        
                result.elements = elements
                
            # Extract links
            if extract_links:
                try:
                    links = await page.evaluate('''() => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(link => ({
                            href: link.href,
                            text: link.textContent.trim(),
                            title: link.title || ''
                        }));
                    }''')
                    result.links = [link['href'] for link in links]
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract links: {str(e)}")
                    
            # Extract images
            if extract_images:
                try:
                    images = await page.evaluate('''() => {
                        const imgs = Array.from(document.querySelectorAll('img[src]'));
                        return imgs.map(img => ({
                            src: img.src,
                            alt: img.alt || '',
                            width: img.naturalWidth,
                            height: img.naturalHeight
                        }));
                    }''')
                    result.images = [img['src'] for img in images]
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract images: {str(e)}")
                    
            # Extract performance metrics
            if extract_performance:
                try:
                    metrics = await page.evaluate('''() => {
                        const perf = performance.getEntriesByType('navigation')[0];
                        return {
                            dom_content_loaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
                            load_complete: perf.loadEventEnd - perf.loadEventStart,
                            dns_lookup: perf.domainLookupEnd - perf.domainLookupStart,
                            tcp_connection: perf.connectEnd - perf.connectStart,
                            request_response: perf.responseEnd - perf.requestStart,
                            dom_processing: perf.domComplete - perf.domLoading,
                            total_time: perf.loadEventEnd - perf.fetchStart
                        };
                    }''')
                    result.performance_metrics = metrics
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract performance: {str(e)}")
                    
            # Extract accessibility tree
            if extract_accessibility and hasattr(page, 'accessibility'):
                try:
                    accessibility = await page.accessibility.snapshot()
                    result.accessibility_tree = accessibility
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract accessibility: {str(e)}")
                    
            # Get cookies
            try:
                cookies = await page.context.cookies()
                result.cookies = [dict(cookie) for cookie in cookies]
            except Exception as e:
                logger.warning(f"⚠️ Failed to get cookies: {str(e)}")
                
            # Get storage
            try:
                local_storage = await page.evaluate('() => ({ ...localStorage })')
                session_storage = await page.evaluate('() => ({ ...sessionStorage })')
                result.local_storage = local_storage
                result.session_storage = session_storage
            except Exception as e:
                logger.warning(f"⚠️ Failed to get storage: {str(e)}")
                
            # Add logs
            result.console_logs = page_data['console_logs'].copy()
            result.network_logs = page_data['network_logs'].copy()
            
            extraction_time = time.time() - start_time
            result.extraction_time = extraction_time
            
            logger.info(f"✅ Content extracted in {extraction_time:.2f}s")
            return result
            
        except Exception as e:
            extraction_time = time.time() - start_time
            
            logger.error(f"❌ Content extraction failed: {str(e)}")
            return PlaywrightResult(
                url=page.url,
                extraction_time=extraction_time,
                error=str(e)
            )
            
    async def take_screenshot(self, page_id: str,
                            full_page: bool = True,
                            element_selector: Optional[str] = None,
                            format: str = 'png') -> Optional[str]:
        """Take screenshot of page or element"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]['page']
        
        try:
            screenshot_options = {
                'type': format,
                'full_page': full_page
            }
            
            if element_selector:
                # Screenshot of specific element
                element = await page.query_selector(element_selector)
                if element:
                    screenshot_data = await element.screenshot(**screenshot_options)
                else:
                    logger.warning(f"⚠️ Element '{element_selector}' not found for screenshot")
                    return None
            else:
                # Full page screenshot
                screenshot_data = await page.screenshot(**screenshot_options)
                
            # Convert to base64
            screenshot_b64 = base64.b64encode(screenshot_data).decode()
            
            self._stats['screenshots_taken'] += 1
            return screenshot_b64
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {str(e)}")
            return None
            
    async def generate_pdf(self, page_id: str,
                          format: str = 'A4',
                          margin: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Generate PDF from page"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]['page']
        
        try:
            pdf_options = {
                'format': format,
                'print_background': True,
                'margin': margin or {'top': '1cm', 'right': '1cm', 'bottom': '1cm', 'left': '1cm'}
            }
            
            pdf_data = await page.pdf(**pdf_options)
            pdf_b64 = base64.b64encode(pdf_data).decode()
            
            self._stats['pdfs_generated'] += 1
            return pdf_b64
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {str(e)}")
            return None
            
    async def execute_script(self, page_id: str, script: str) -> Any:
        """Execute JavaScript in page"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]['page']
        
        try:
            result = await page.evaluate(script)
            logger.info("✅ JavaScript executed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ JavaScript execution failed: {str(e)}")
            return None
            
    async def interact_with_element(self, page_id: str,
                                  selector: str,
                                  action: str,
                                  **kwargs) -> bool:
        """Interact with page element"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]['page']
        
        try:
            element = await page.wait_for_selector(selector)
            if not element:
                logger.warning(f"⚠️ Element '{selector}' not found")
                return False
                
            if action == 'click':
                await element.click(**kwargs)
            elif action == 'fill':
                await element.fill(kwargs.get('value', ''))
            elif action == 'type':
                await element.type(kwargs.get('text', ''), **kwargs)
            elif action == 'select':
                await element.select_option(kwargs.get('values', []))
            elif action == 'check':
                await element.check()
            elif action == 'uncheck':
                await element.uncheck()
            elif action == 'hover':
                await element.hover()
            elif action == 'scroll':
                await element.scroll_into_view_if_needed()
            else:
                logger.error(f"❌ Unknown action: {action}")
                return False
                
            logger.info(f"✅ {action} performed on '{selector}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Element interaction failed: {str(e)}")
            return False
            
    async def wait_for_condition(self, page_id: str,
                               condition_type: str,
                               selector_or_script: str,
                               timeout: int = None) -> bool:
        """Wait for specific condition"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]['page']
        timeout = timeout or self.config.timeout
        
        try:
            if condition_type == 'selector':
                await page.wait_for_selector(selector_or_script, timeout=timeout)
            elif condition_type == 'function':
                await page.wait_for_function(selector_or_script, timeout=timeout)
            elif condition_type == 'url':
                await page.wait_for_url(selector_or_script, timeout=timeout)
            elif condition_type == 'load_state':
                await page.wait_for_load_state(selector_or_script, timeout=timeout)
            else:
                logger.error(f"❌ Unknown condition type: {condition_type}")
                return False
                
            logger.info(f"✅ Condition '{condition_type}' met")
            return True
            
        except Exception as e:
            logger.error(f"❌ Wait condition failed: {str(e)}")
            return False
            
    async def close_page(self, page_id: str):
        """Close page"""
        
        if page_id in self.pages:
            try:
                page_data = self.pages[page_id]
                page = page_data['page']
                
                # Stop tracing if active
                if self.config.trace_mode != 'off':
                    try:
                        trace_file = self.temp_dir / f"trace_{page_id}.zip"
                        await page.context.tracing.stop(path=str(trace_file))
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to stop tracing: {str(e)}")
                        
                await page.close()
                del self.pages[page_id]
                self._stats['active_pages'] = len(self.pages)
                
                logger.info(f"✅ Page '{page_id}' closed")
            except Exception as e:
                logger.error(f"❌ Failed to close page '{page_id}': {str(e)}")
                
    async def close_context(self, context_id: str):
        """Close browser context"""
        
        if context_id in self.contexts:
            try:
                # Close all pages in context first
                pages_to_close = [
                    pid for pid, pdata in self.pages.items()
                    if pdata['context_id'] == context_id
                ]
                
                for page_id in pages_to_close:
                    await self.close_page(page_id)
                    
                # Close context
                context = self.contexts[context_id]
                await context.close()
                del self.contexts[context_id]
                self._stats['active_contexts'] = len(self.contexts)
                
                logger.info(f"✅ Context '{context_id}' closed")
            except Exception as e:
                logger.error(f"❌ Failed to close context '{context_id}': {str(e)}")
                
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        
        avg_load_time = 0.0
        if self._stats['pages_loaded'] > 0:
            avg_load_time = self._stats['total_load_time'] / self._stats['pages_loaded']
            
        success_rate = 0.0
        total_attempts = self._stats['pages_loaded'] + self._stats['pages_failed']
        if total_attempts > 0:
            success_rate = self._stats['pages_loaded'] / total_attempts
            
        return {
            **self._stats,
            'average_load_time': avg_load_time,
            'success_rate': success_rate,
            'config': asdict(self.config)
        }
        
    async def cleanup(self):
        """Clean up resources"""
        
        # Close all pages
        for page_id in list(self.pages.keys()):
            await self.close_page(page_id)
            
        # Close all contexts
        for context_id in list(self.contexts.keys()):
            await self.close_context(context_id)
            
        # Close browser
        if self.browser:
            try:
                await self.browser.close()
                logger.info("🛑 Browser closed")
            except Exception as e:
                logger.error(f"❌ Failed to close browser: {str(e)}")
                
        # Stop playwright
        if self.playwright:
            try:
                await self.playwright.stop()
                logger.info("🛑 Playwright stopped")
            except Exception as e:
                logger.error(f"❌ Failed to stop Playwright: {str(e)}")
                
        # Clean up temp directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 Temporary directory cleaned")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class PlaywrightAdapter:
    """High-level adapter for Playwright integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = PlaywrightConfig(**config)
        self.manager = PlaywrightManager(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Playwright adapter disabled")
            return
            
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("❌ Playwright not available")
            if self.config.enabled:
                raise ImportError("Playwright package required. Install with: pip install playwright && playwright install")
            return
            
        if self.manager:
            await self.manager.initialize()
            logger.info("✅ Playwright adapter initialized")
        else:
            logger.error("❌ Playwright manager not available")
            
    async def scrape_page(self, url: str,
                         browser_type: str = None,
                         selectors: Optional[Dict[str, str]] = None,
                         take_screenshot: bool = False,
                         generate_pdf: bool = False,
                         extract_performance: bool = False,
                         device_name: str = None) -> Dict[str, Any]:
        """
        Scrape page using browser automation.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'title': str,
            'content': str,
            'elements': list,
            'links': list,
            'images': list,
            'load_time': float
        }
        """
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'Playwright is disabled or not available'
            }
            
        try:
            # Create context with device emulation if specified
            context_options = {}
            if device_name:
                device = self.manager.playwright.devices.get(device_name)
                if device:
                    context_options.update(device)
                    
            context_id = await self.manager.create_context(**context_options)
            page_id = await self.manager.create_page(context_id)
            
            # Navigate to page
            nav_result = await self.manager.navigate_to(page_id, url)
            
            if nav_result.error:
                return {
                    'success': False,
                    'error': nav_result.error,
                    'url': url,
                    'method': 'playwright'
                }
                
            # Extract content
            extraction_result = await self.manager.extract_content(
                page_id,
                selectors=selectors,
                extract_performance=extract_performance
            )
            
            # Take screenshot if requested
            screenshot_data = None
            if take_screenshot:
                screenshot_data = await self.manager.take_screenshot(page_id)
                
            # Generate PDF if requested
            pdf_data = None
            if generate_pdf:
                pdf_data = await self.manager.generate_pdf(page_id)
                
            # Clean up
            await self.manager.close_context(context_id)
            
            return {
                'success': True,
                'url': extraction_result.url,
                'title': extraction_result.title,
                'content': extraction_result.content,
                'html': extraction_result.html,
                'elements': extraction_result.elements or [],
                'links': extraction_result.links or [],
                'images': extraction_result.images or [],
                'console_logs': extraction_result.console_logs or [],
                'performance_metrics': extraction_result.performance_metrics,
                'accessibility_tree': extraction_result.accessibility_tree,
                'cookies': extraction_result.cookies or [],
                'local_storage': extraction_result.local_storage or {},
                'session_storage': extraction_result.session_storage or {},
                'load_time': nav_result.load_time,
                'extraction_time': extraction_result.extraction_time,
                'screenshot': screenshot_data,
                'pdf': pdf_data,
                'browser_type': browser_type or self.config.browser_type,
                'device': device_name,
                'method': 'playwright'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape page: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'method': 'playwright'
            }
            
    async def automate_workflow(self, workflow: List[Dict[str, Any]],
                              device_name: str = None) -> Dict[str, Any]:
        """Execute automated workflow"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'Playwright not available'}
            
        try:
            # Create context
            context_options = {}
            if device_name:
                device = self.manager.playwright.devices.get(device_name)
                if device:
                    context_options.update(device)
                    
            context_id = await self.manager.create_context(**context_options)
            page_id = await self.manager.create_page(context_id)
            
            workflow_results = []
            
            for i, step in enumerate(workflow):
                step_start = time.time()
                action = step.get('action')
                
                try:
                    if action == 'navigate':
                        result = await self.manager.navigate_to(page_id, step['url'])
                        
                    elif action == 'click':
                        result = await self.manager.interact_with_element(
                            page_id, step['selector'], 'click', **step.get('options', {})
                        )
                        
                    elif action == 'fill':
                        result = await self.manager.interact_with_element(
                            page_id, step['selector'], 'fill', value=step['value']
                        )
                        
                    elif action == 'type':
                        result = await self.manager.interact_with_element(
                            page_id, step['selector'], 'type', text=step['text']
                        )
                        
                    elif action == 'wait':
                        if 'selector' in step:
                            result = await self.manager.wait_for_condition(
                                page_id, 'selector', step['selector']
                            )
                        else:
                            await asyncio.sleep(step.get('time', 1))
                            result = True
                            
                    elif action == 'screenshot':
                        result = await self.manager.take_screenshot(
                            page_id, 
                            element_selector=step.get('selector'),
                            full_page=step.get('full_page', True)
                        )
                        
                    elif action == 'extract':
                        result = await self.manager.extract_content(
                            page_id,
                            selectors=step.get('selectors'),
                            extract_performance=step.get('extract_performance', False)
                        )
                        
                    elif action == 'javascript':
                        result = await self.manager.execute_script(page_id, step['script'])
                        
                    else:
                        result = {'error': f'Unknown action: {action}'}
                        
                except Exception as e:
                    result = {'error': str(e)}
                    
                step_time = time.time() - step_start
                workflow_results.append({
                    'step': i + 1,
                    'action': action,
                    'result': result,
                    'time': step_time
                })
                
            # Clean up
            await self.manager.close_context(context_id)
            
            return {
                'success': True,
                'workflow_results': workflow_results,
                'total_steps': len(workflow),
                'device': device_name,
                'browser_type': self.config.browser_type,
                'method': 'playwright-workflow'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'playwright-workflow'
            }
            
    async def test_page_accessibility(self, url: str) -> Dict[str, Any]:
        """Test page accessibility"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'Playwright not available'}
            
        try:
            context_id = await self.manager.create_context()
            page_id = await self.manager.create_page(context_id)
            
            # Navigate
            await self.manager.navigate_to(page_id, url)
            
            # Extract accessibility information
            result = await self.manager.extract_content(
                page_id, extract_accessibility=True
            )
            
            # Clean up
            await self.manager.close_context(context_id)
            
            return {
                'success': True,
                'url': url,
                'accessibility_tree': result.accessibility_tree,
                'method': 'playwright-accessibility'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'playwright-accessibility'
            }
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.manager:
            base_stats['manager_stats'] = self.manager.get_stats()
        else:
            base_stats['manager_stats'] = {}
            
        return base_stats
        
    async def cleanup(self):
        """Clean up all resources"""
        if self.manager:
            await self.manager.cleanup()

# Factory function
def create_playwright_adapter(config: Dict[str, Any]) -> PlaywrightAdapter:
    """Create and configure Playwright adapter"""
    return PlaywrightAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'browser_type': 'chromium',
        'headless': False,  # Show browser for demo
        'screenshot_mode': 'always',
        'debug': True
    }
    
    adapter = create_playwright_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Scrape page with custom selectors
        result = await adapter.scrape_page(
            'http://example.com',
            selectors={'headings': 'h1, h2, h3'},
            take_screenshot=True,
            extract_performance=True
        )
        
        if result['success']:
            print(f"✅ Scraped: {result['title']}")
            print(f"Found {len(result['links'])} links")
            print(f"Load time: {result['load_time']:.2f}s")
            print(f"Performance: {result['performance_metrics']}")
        else:
            print(f"❌ Scraping failed: {result['error']}")
            
        # Mobile device emulation
        mobile_result = await adapter.scrape_page(
            'http://example.com',
            device_name='iPhone 12',
            take_screenshot=True
        )
        
        if mobile_result['success']:
            print(f"✅ Mobile scraping successful")
        else:
            print(f"❌ Mobile scraping failed: {mobile_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
