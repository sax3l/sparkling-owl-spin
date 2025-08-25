#!/usr/bin/env python3
"""
DrissionPage Integration - Revolutionary Ultimate System v4.0
Python browser automation with selenium-like simplicity
"""

import asyncio
import logging
import time
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import base64
import mimetypes

try:
    from DrissionPage import Chromium, WebPage, SessionPage
    from DrissionPage.errors import *
    DRISSION_AVAILABLE = True
except ImportError:
    DRISSION_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class DrissionConfig:
    """Configuration for DrissionPage"""
    enabled: bool = True
    headless: bool = True
    window_size: Tuple[int, int] = (1920, 1080)
    user_agent: Optional[str] = None
    disable_images: bool = False
    disable_css: bool = False
    disable_javascript: bool = False
    page_load_timeout: int = 30
    element_timeout: int = 10
    download_path: Optional[str] = None
    proxy: Optional[str] = None
    chrome_args: List[str] = None
    extensions: List[str] = None
    incognito: bool = True
    auto_port: bool = True
    existing_only: bool = False
    max_concurrent_pages: int = 5
    session_pool_size: int = 10
    enable_screenshots: bool = True
    screenshot_quality: int = 90
    retry_attempts: int = 3
    debug: bool = False

@dataclass
class DrissionElement:
    """Extracted element data"""
    tag: str
    text: str
    attributes: Dict[str, str]
    html: str
    xpath: str
    location: Optional[Dict[str, Any]] = None

@dataclass
class DrissionResult:
    """Container for DrissionPage results"""
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    html: Optional[str] = None
    status_code: int = 200
    load_time: float = 0.0
    screenshot: Optional[str] = None  # Base64 encoded
    elements: Optional[List[DrissionElement]] = None
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    forms: Optional[List[Dict[str, Any]]] = None
    cookies: Optional[List[Dict[str, Any]]] = None
    headers: Optional[Dict[str, str]] = None
    page_source: Optional[str] = None
    console_logs: Optional[List[str]] = None
    network_logs: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    extraction_time: float = 0.0

class DrissionPageManager:
    """
    DrissionPage manager for Python browser automation.
    
    Features:
    - Chrome browser automation
    - Session-based requests
    - Element extraction with XPath/CSS selectors
    - Screenshot capture
    - Form interaction
    - JavaScript execution
    - Network monitoring
    - Multi-page management
    """
    
    def __init__(self, config: DrissionConfig):
        self.config = config
        self.browser = None
        self.pages = {}
        self.session_page = None
        self.temp_dir = None
        self._stats = {
            'pages_created': 0,
            'pages_loaded': 0,
            'pages_failed': 0,
            'total_load_time': 0.0,
            'screenshots_taken': 0,
            'elements_extracted': 0,
            'forms_found': 0,
            'browser_starts': 0,
            'active_pages': 0
        }
        
        if not DRISSION_AVAILABLE:
            if self.config.enabled:
                raise ImportError("DrissionPage not available. Install with: pip install DrissionPage")
            
    async def initialize(self):
        """Initialize DrissionPage manager"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing DrissionPage manager...")
        
        try:
            # Create temporary directory for downloads
            self.temp_dir = Path(tempfile.mkdtemp(prefix="drission_"))
            
            # Initialize Chromium browser
            await self._init_browser()
            
            # Initialize session page for HTTP requests
            await self._init_session()
            
            logger.info("✅ DrissionPage manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize DrissionPage: {str(e)}")
            raise
            
    async def _init_browser(self):
        """Initialize Chrome browser"""
        
        try:
            # Configure Chrome options
            chrome_options = []
            
            if self.config.headless:
                chrome_options.extend(['--headless', '--disable-gpu'])
                
            chrome_options.extend([
                f'--window-size={self.config.window_size[0]},{self.config.window_size[1]}',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--allow-running-insecure-content'
            ])
            
            if self.config.user_agent:
                chrome_options.append(f'--user-agent={self.config.user_agent}')
                
            if self.config.disable_images:
                chrome_options.append('--blink-settings=imagesEnabled=false')
                
            if self.config.proxy:
                chrome_options.append(f'--proxy-server={self.config.proxy}')
                
            if self.config.incognito:
                chrome_options.append('--incognito')
                
            # Add download directory
            download_path = self.config.download_path or str(self.temp_dir)
            chrome_options.extend([
                f'--disable-extensions-except={",".join(self.config.extensions or [])}',
                f'--load-extension={",".join(self.config.extensions or [])}'
            ])
            
            # Add custom arguments
            if self.config.chrome_args:
                chrome_options.extend(self.config.chrome_args)
                
            # Create browser instance
            self.browser = Chromium(
                auto_port=self.config.auto_port,
                existing_only=self.config.existing_only
            )
            
            # Configure browser
            if hasattr(self.browser, 'set_argument'):
                for arg in chrome_options:
                    self.browser.set_argument(arg)
                    
            self._stats['browser_starts'] += 1
            logger.info("✅ Chrome browser initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {str(e)}")
            raise
            
    async def _init_session(self):
        """Initialize session page for HTTP requests"""
        
        try:
            self.session_page = SessionPage()
            
            # Configure session
            if self.config.user_agent:
                self.session_page.set_headers({'User-Agent': self.config.user_agent})
                
            if self.config.proxy:
                self.session_page.set_proxies({'http': self.config.proxy, 'https': self.config.proxy})
                
            logger.info("✅ Session page initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize session: {str(e)}")
            raise
            
    async def create_page(self, page_id: str = None) -> str:
        """Create new browser page"""
        
        if not self.config.enabled or not self.browser:
            raise RuntimeError("DrissionPage not available")
            
        if page_id is None:
            page_id = f"page_{len(self.pages)}"
            
        try:
            # Create new page
            page = self.browser.get_tab()
            
            # Configure page timeouts
            page.set.timeouts(
                implicit=self.config.element_timeout,
                page_load=self.config.page_load_timeout
            )
            
            # Configure page settings
            if self.config.disable_images:
                page.set.load_images(False)
                
            if self.config.disable_css:
                page.set.load_css(False)
                
            # Store page
            self.pages[page_id] = page
            self._stats['pages_created'] += 1
            self._stats['active_pages'] = len(self.pages)
            
            logger.info(f"✅ Page '{page_id}' created")
            return page_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create page: {str(e)}")
            raise
            
    async def load_page(self, page_id: str, url: str) -> DrissionResult:
        """Load URL in browser page"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]
        start_time = time.time()
        
        try:
            logger.info(f"🌐 Loading {url} in page '{page_id}'")
            
            # Load page
            page.get(url)
            
            load_time = time.time() - start_time
            
            # Wait for page to be ready
            if hasattr(page, 'wait_loaded'):
                page.wait_loaded()
                
            # Extract basic information
            result = DrissionResult(
                url=page.url,
                title=page.title,
                load_time=load_time,
                status_code=getattr(page, 'status_code', 200)
            )
            
            self._stats['pages_loaded'] += 1
            self._stats['total_load_time'] += load_time
            
            logger.info(f"✅ Page loaded in {load_time:.2f}s")
            return result
            
        except Exception as e:
            load_time = time.time() - start_time
            self._stats['pages_failed'] += 1
            
            logger.error(f"❌ Failed to load page: {str(e)}")
            return DrissionResult(
                url=url,
                load_time=load_time,
                status_code=0,
                error=str(e)
            )
            
    async def extract_content(self, page_id: str, 
                            selectors: Optional[Dict[str, str]] = None,
                            extract_links: bool = True,
                            extract_images: bool = True,
                            extract_forms: bool = True) -> DrissionResult:
        """Extract content from page"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]
        start_time = time.time()
        
        try:
            result = DrissionResult(
                url=page.url,
                title=page.title,
                content=page.text,
                html=page.html,
                page_source=page.html
            )
            
            # Extract elements with selectors
            if selectors:
                elements = []
                
                for name, selector in selectors.items():
                    try:
                        if selector.startswith('//'):
                            # XPath selector
                            found_elements = page.eles(selector)
                        else:
                            # CSS selector
                            found_elements = page.eles(selector)
                            
                        for elem in found_elements:
                            element_data = DrissionElement(
                                tag=elem.tag,
                                text=elem.text,
                                attributes=dict(elem.attrs),
                                html=elem.html,
                                xpath=getattr(elem, 'xpath', ''),
                                location=getattr(elem, 'location', None)
                            )
                            elements.append(element_data)
                            
                        self._stats['elements_extracted'] += len(found_elements)
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to extract with selector '{selector}': {str(e)}")
                        
                result.elements = elements
                
            # Extract links
            if extract_links:
                links = []
                try:
                    link_elements = page.eles('a')
                    for link in link_elements:
                        href = link.attr('href')
                        if href:
                            absolute_url = urljoin(page.url, href)
                            links.append(absolute_url)
                    result.links = list(set(links))
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract links: {str(e)}")
                    
            # Extract images
            if extract_images:
                images = []
                try:
                    img_elements = page.eles('img')
                    for img in img_elements:
                        src = img.attr('src')
                        if src:
                            absolute_url = urljoin(page.url, src)
                            images.append(absolute_url)
                    result.images = list(set(images))
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract images: {str(e)}")
                    
            # Extract forms
            if extract_forms:
                forms = []
                try:
                    form_elements = page.eles('form')
                    for form in form_elements:
                        form_data = {
                            'action': form.attr('action') or '',
                            'method': form.attr('method') or 'get',
                            'inputs': []
                        }
                        
                        # Extract form inputs
                        inputs = form.eles('input, select, textarea')
                        for input_elem in inputs:
                            input_data = {
                                'tag': input_elem.tag,
                                'type': input_elem.attr('type') or '',
                                'name': input_elem.attr('name') or '',
                                'value': input_elem.attr('value') or '',
                                'placeholder': input_elem.attr('placeholder') or '',
                                'required': input_elem.attr('required') is not None
                            }
                            form_data['inputs'].append(input_data)
                            
                        forms.append(form_data)
                        
                    result.forms = forms
                    self._stats['forms_found'] += len(forms)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract forms: {str(e)}")
                    
            # Get cookies
            try:
                result.cookies = page.cookies().as_dict()
            except Exception as e:
                logger.warning(f"⚠️ Failed to get cookies: {str(e)}")
                
            # Get console logs if available
            try:
                if hasattr(page, 'console_logs'):
                    result.console_logs = page.console_logs
            except Exception as e:
                logger.warning(f"⚠️ Failed to get console logs: {str(e)}")
                
            extraction_time = time.time() - start_time
            result.extraction_time = extraction_time
            
            logger.info(f"✅ Content extracted in {extraction_time:.2f}s")
            return result
            
        except Exception as e:
            extraction_time = time.time() - start_time
            
            logger.error(f"❌ Content extraction failed: {str(e)}")
            return DrissionResult(
                url=page.url,
                extraction_time=extraction_time,
                error=str(e)
            )
            
    async def take_screenshot(self, page_id: str, 
                            full_page: bool = True,
                            element_selector: Optional[str] = None) -> Optional[str]:
        """Take screenshot of page or element"""
        
        if not self.config.enable_screenshots:
            return None
            
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]
        
        try:
            screenshot_path = self.temp_dir / f"screenshot_{page_id}_{int(time.time())}.png"
            
            if element_selector:
                # Screenshot of specific element
                element = page.ele(element_selector)
                if element:
                    element.get_screenshot(str(screenshot_path))
                else:
                    logger.warning(f"⚠️ Element '{element_selector}' not found for screenshot")
                    return None
            else:
                # Full page screenshot
                if full_page and hasattr(page, 'get_screenshot'):
                    page.get_screenshot(str(screenshot_path), full_page=True)
                elif hasattr(page, 'screenshot'):
                    page.screenshot(str(screenshot_path))
                else:
                    logger.warning("⚠️ Screenshot method not available")
                    return None
                    
            # Convert to base64
            if screenshot_path.exists():
                with open(screenshot_path, 'rb') as f:
                    screenshot_data = base64.b64encode(f.read()).decode()
                    
                # Clean up file
                screenshot_path.unlink()
                
                self._stats['screenshots_taken'] += 1
                return screenshot_data
            else:
                logger.warning("⚠️ Screenshot file not created")
                return None
                
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {str(e)}")
            return None
            
    async def execute_javascript(self, page_id: str, script: str) -> Any:
        """Execute JavaScript in page"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]
        
        try:
            if hasattr(page, 'run_js'):
                result = page.run_js(script)
                logger.info("✅ JavaScript executed successfully")
                return result
            else:
                logger.warning("⚠️ JavaScript execution not available")
                return None
                
        except Exception as e:
            logger.error(f"❌ JavaScript execution failed: {str(e)}")
            return None
            
    async def fill_form(self, page_id: str, form_data: Dict[str, Any]) -> bool:
        """Fill and submit form"""
        
        if page_id not in self.pages:
            raise ValueError(f"Page '{page_id}' not found")
            
        page = self.pages[page_id]
        
        try:
            # Fill form fields
            for field_name, value in form_data.items():
                if field_name == '_submit':
                    continue  # Skip submit action
                    
                try:
                    # Try different selector strategies
                    element = None
                    selectors = [
                        f'input[name="{field_name}"]',
                        f'select[name="{field_name}"]',
                        f'textarea[name="{field_name}"]',
                        f'#{field_name}',
                        f'[data-name="{field_name}"]'
                    ]
                    
                    for selector in selectors:
                        element = page.ele(selector)
                        if element:
                            break
                            
                    if element:
                        if element.tag.lower() == 'select':
                            element.select(value)
                        else:
                            element.input(value)
                        logger.info(f"✅ Filled field '{field_name}' with value '{value}'")
                    else:
                        logger.warning(f"⚠️ Field '{field_name}' not found")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fill field '{field_name}': {str(e)}")
                    
            # Submit form if requested
            if form_data.get('_submit'):
                try:
                    # Try to find submit button
                    submit_button = page.ele('input[type="submit"], button[type="submit"], button:contains("Submit")')
                    if submit_button:
                        submit_button.click()
                        logger.info("✅ Form submitted")
                        
                        # Wait for page to load after submit
                        if hasattr(page, 'wait_loaded'):
                            page.wait_loaded()
                            
                        return True
                    else:
                        logger.warning("⚠️ Submit button not found")
                        return False
                        
                except Exception as e:
                    logger.error(f"❌ Form submission failed: {str(e)}")
                    return False
            else:
                return True
                
        except Exception as e:
            logger.error(f"❌ Form filling failed: {str(e)}")
            return False
            
    async def session_request(self, url: str, method: str = 'GET', 
                            **kwargs) -> DrissionResult:
        """Make HTTP request using session page"""
        
        if not self.session_page:
            raise RuntimeError("Session page not initialized")
            
        start_time = time.time()
        
        try:
            # Make request
            if method.upper() == 'GET':
                response = self.session_page.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session_page.post(url, **kwargs)
            elif method.upper() == 'PUT':
                response = self.session_page.put(url, **kwargs)
            elif method.upper() == 'DELETE':
                response = self.session_page.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            load_time = time.time() - start_time
            
            # Create result
            result = DrissionResult(
                url=response.url,
                content=response.text,
                html=response.text,
                status_code=response.status_code,
                load_time=load_time,
                headers=dict(response.headers)
            )
            
            self._stats['pages_loaded'] += 1
            self._stats['total_load_time'] += load_time
            
            return result
            
        except Exception as e:
            load_time = time.time() - start_time
            self._stats['pages_failed'] += 1
            
            logger.error(f"❌ Session request failed: {str(e)}")
            return DrissionResult(
                url=url,
                load_time=load_time,
                status_code=0,
                error=str(e)
            )
            
    async def close_page(self, page_id: str):
        """Close browser page"""
        
        if page_id in self.pages:
            try:
                page = self.pages[page_id]
                if hasattr(page, 'close'):
                    page.close()
                del self.pages[page_id]
                self._stats['active_pages'] = len(self.pages)
                logger.info(f"✅ Page '{page_id}' closed")
            except Exception as e:
                logger.error(f"❌ Failed to close page '{page_id}': {str(e)}")
                
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
            
        # Close browser
        if self.browser:
            try:
                if hasattr(self.browser, 'quit'):
                    self.browser.quit()
                logger.info("🛑 Browser closed")
            except Exception as e:
                logger.error(f"❌ Failed to close browser: {str(e)}")
                
        # Close session
        if self.session_page:
            try:
                if hasattr(self.session_page, 'close'):
                    self.session_page.close()
                logger.info("🛑 Session closed")
            except Exception as e:
                logger.error(f"❌ Failed to close session: {str(e)}")
                
        # Clean up temp directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 Temporary directory cleaned")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class DrissionPageAdapter:
    """High-level adapter for DrissionPage integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = DrissionConfig(**config)
        self.manager = DrissionPageManager(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("DrissionPage adapter disabled")
            return
            
        if not DRISSION_AVAILABLE:
            logger.error("❌ DrissionPage not available")
            if self.config.enabled:
                raise ImportError("DrissionPage package required")
            return
            
        if self.manager:
            await self.manager.initialize()
            logger.info("✅ DrissionPage adapter initialized")
        else:
            logger.error("❌ DrissionPage manager not available")
            
    async def scrape_page(self, url: str, 
                         selectors: Optional[Dict[str, str]] = None,
                         extract_all: bool = True,
                         take_screenshot: bool = False) -> Dict[str, Any]:
        """
        Scrape page using browser automation.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'title': str,
            'content': str,
            'elements': dict,
            'links': list,
            'images': list,
            'load_time': float
        }
        """
        
        if not self.config.enabled or not self.manager:
            return {
                'success': False,
                'error': 'DrissionPage is disabled or not available'
            }
            
        try:
            # Create page
            page_id = await self.manager.create_page()
            
            # Load page
            result = await self.manager.load_page(page_id, url)
            
            if result.error:
                return {
                    'success': False,
                    'error': result.error,
                    'url': url,
                    'method': 'drission-browser'
                }
                
            # Extract content
            extraction_result = await self.manager.extract_content(
                page_id,
                selectors=selectors,
                extract_links=extract_all,
                extract_images=extract_all,
                extract_forms=extract_all
            )
            
            # Take screenshot if requested
            screenshot_data = None
            if take_screenshot:
                screenshot_data = await self.manager.take_screenshot(page_id)
                
            # Clean up
            await self.manager.close_page(page_id)
            
            return {
                'success': True,
                'url': extraction_result.url,
                'title': extraction_result.title,
                'content': extraction_result.content,
                'html': extraction_result.html,
                'elements': [asdict(el) for el in (extraction_result.elements or [])],
                'links': extraction_result.links or [],
                'images': extraction_result.images or [],
                'forms': extraction_result.forms or [],
                'load_time': result.load_time,
                'extraction_time': extraction_result.extraction_time,
                'screenshot': screenshot_data,
                'console_logs': extraction_result.console_logs or [],
                'method': 'drission-browser'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape page: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url,
                'method': 'drission-browser'
            }
            
    async def automate_workflow(self, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute automated workflow"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'DrissionPage not available'}
            
        try:
            # Create page
            page_id = await self.manager.create_page()
            workflow_results = []
            
            for i, step in enumerate(workflow):
                step_start = time.time()
                action = step.get('action')
                
                if action == 'navigate':
                    result = await self.manager.load_page(page_id, step['url'])
                    
                elif action == 'fill_form':
                    result = await self.manager.fill_form(page_id, step['data'])
                    
                elif action == 'click':
                    page = self.manager.pages[page_id]
                    element = page.ele(step['selector'])
                    if element:
                        element.click()
                        result = True
                    else:
                        result = False
                        
                elif action == 'wait':
                    await asyncio.sleep(step.get('time', 1))
                    result = True
                    
                elif action == 'screenshot':
                    result = await self.manager.take_screenshot(page_id)
                    
                elif action == 'extract':
                    result = await self.manager.extract_content(
                        page_id,
                        selectors=step.get('selectors'),
                        extract_links=step.get('extract_links', True),
                        extract_images=step.get('extract_images', True)
                    )
                    
                elif action == 'javascript':
                    result = await self.manager.execute_javascript(page_id, step['script'])
                    
                else:
                    result = {'error': f'Unknown action: {action}'}
                    
                step_time = time.time() - step_start
                workflow_results.append({
                    'step': i + 1,
                    'action': action,
                    'result': result,
                    'time': step_time
                })
                
            # Clean up
            await self.manager.close_page(page_id)
            
            return {
                'success': True,
                'workflow_results': workflow_results,
                'total_steps': len(workflow),
                'method': 'drission-workflow'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'drission-workflow'
            }
            
    async def session_crawl(self, urls: List[str],
                          method: str = 'GET',
                          **kwargs) -> Dict[str, Any]:
        """Crawl URLs using session (no browser)"""
        
        if not self.config.enabled or not self.manager:
            return {'success': False, 'error': 'DrissionPage not available'}
            
        try:
            results = []
            
            for url in urls:
                result = await self.manager.session_request(url, method, **kwargs)
                results.append({
                    'url': result.url,
                    'status_code': result.status_code,
                    'content': result.content,
                    'headers': result.headers or {},
                    'load_time': result.load_time,
                    'error': result.error
                })
                
            return {
                'success': True,
                'results': results,
                'total_urls': len(urls),
                'method': 'drission-session'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'drission-session'
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
def create_drission_adapter(config: Dict[str, Any]) -> DrissionPageAdapter:
    """Create and configure DrissionPage adapter"""
    return DrissionPageAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'headless': False,  # Show browser for demo
        'window_size': (1280, 720),
        'enable_screenshots': True,
        'debug': True
    }
    
    adapter = create_drission_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Scrape page with custom selectors
        result = await adapter.scrape_page(
            'http://example.com',
            selectors={'headings': 'h1, h2, h3'},
            take_screenshot=True
        )
        
        if result['success']:
            print(f"✅ Scraped: {result['title']}")
            print(f"Found {len(result['links'])} links")
            print(f"Load time: {result['load_time']:.2f}s")
        else:
            print(f"❌ Scraping failed: {result['error']}")
            
        # Example workflow
        workflow = [
            {'action': 'navigate', 'url': 'http://example.com'},
            {'action': 'wait', 'time': 2},
            {'action': 'screenshot'},
            {'action': 'extract', 'selectors': {'titles': 'h1'}}
        ]
        
        workflow_result = await adapter.automate_workflow(workflow)
        
        if workflow_result['success']:
            print(f"✅ Workflow completed: {workflow_result['total_steps']} steps")
        else:
            print(f"❌ Workflow failed: {workflow_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
