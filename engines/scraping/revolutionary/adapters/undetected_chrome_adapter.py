#!/usr/bin/env python3
"""
Undetected ChromeDriver Integration - Revolutionary Ultimate System v4.0
Advanced browser automation that bypasses bot detection
"""

import asyncio
import logging
import time
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import random

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class UndetectedChromeConfig:
    """Configuration for Undetected ChromeDriver"""
    enabled: bool = True
    headless: bool = True
    no_sandbox: bool = True
    disable_dev_shm_usage: bool = True
    disable_gpu: bool = True
    window_size: str = "1920,1080"
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    user_data_dir: Optional[str] = None
    profile_directory: Optional[str] = None
    disable_blink_features: bool = True
    disable_web_security: bool = False
    ignore_certificate_errors: bool = True
    page_load_timeout: int = 30
    implicit_wait: int = 10
    script_timeout: int = 30
    prefs: Dict[str, Any] = None
    extensions: List[str] = None
    version_main: Optional[int] = None
    debug: bool = False

@dataclass
class BrowserSession:
    """Browser session information"""
    session_id: str
    driver: Any  # uc.Chrome instance
    created_at: float
    last_used: float
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    page_count: int = 0

class UndetectedChromeDriver:
    """
    Undetected ChromeDriver manager for stealth web automation.
    
    Features:
    - Automatic Chrome patching to avoid detection
    - Custom user agents and fingerprinting
    - Proxy support with authentication
    - Session management for performance
    - Anti-detection techniques built-in
    """
    
    def __init__(self, config: UndetectedChromeConfig):
        self.config = config
        self.sessions: Dict[str, BrowserSession] = {}
        self.session_counter = 0
        self.temp_dirs: List[Path] = []
        
        if not UC_AVAILABLE:
            raise ImportError("undetected-chromedriver not available. Install with: pip install undetected-chromedriver")
            
    def _get_chrome_options(self, proxy: Optional[str] = None, 
                           user_agent: Optional[str] = None) -> Options:
        """Get Chrome options with stealth settings"""
        options = Options()
        
        # Basic stealth options
        if self.config.headless:
            options.add_argument("--headless=new")  # Use new headless mode
            
        if self.config.no_sandbox:
            options.add_argument("--no-sandbox")
            
        if self.config.disable_dev_shm_usage:
            options.add_argument("--disable-dev-shm-usage")
            
        if self.config.disable_gpu:
            options.add_argument("--disable-gpu")
            
        # Window size
        options.add_argument(f"--window-size={self.config.window_size}")
        
        # Advanced stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional stealth arguments
        stealth_args = [
            "--disable-extensions-file-access-check",
            "--disable-extensions-http-throttling", 
            "--disable-extensions-password-manager",
            "--disable-component-extensions-with-background-pages",
            "--disable-default-apps",
            "--disable-sync",
            "--disable-translate",
            "--hide-scrollbars",
            "--mute-audio",
            "--no-default-browser-check",
            "--no-first-run",
            "--disable-logging",
            "--disable-log-file",
            "--silent-debugger-extension-api",
            "--disable-notifications",
            "--disable-popup-blocking"
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
            
        # Disable images and CSS for faster loading (optional)
        prefs = self.config.prefs or {}
        prefs.update({
            "profile.default_content_setting_values": {
                "images": 2,  # Block images
                "plugins": 2,  # Block plugins
                "popups": 2,  # Block popups
                "geolocation": 2,  # Block location sharing
                "notifications": 2,  # Block notifications
                "media_stream": 2,  # Block media stream
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        })
        
        options.add_experimental_option("prefs", prefs)
        
        # User agent
        if user_agent or self.config.user_agent:
            options.add_argument(f"--user-agent={user_agent or self.config.user_agent}")
            
        # Proxy configuration
        if proxy or self.config.proxy:
            proxy_url = proxy or self.config.proxy
            options.add_argument(f"--proxy-server={proxy_url}")
            
        # User data directory
        if self.config.user_data_dir:
            options.add_argument(f"--user-data-dir={self.config.user_data_dir}")
            
        if self.config.profile_directory:
            options.add_argument(f"--profile-directory={self.config.profile_directory}")
            
        # Certificate handling
        if self.config.ignore_certificate_errors:
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            options.add_argument("--ignore-certificate-errors-spki-list")
            
        # Web security
        if self.config.disable_web_security:
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            
        return options
        
    async def create_session(self, proxy: Optional[str] = None,
                           user_agent: Optional[str] = None,
                           custom_options: Optional[Dict[str, Any]] = None) -> str:
        """Create a new browser session"""
        
        try:
            self.session_counter += 1
            session_id = f"uc_session_{self.session_counter}_{int(time.time())}"
            
            logger.info(f"🌐 Creating undetected Chrome session: {session_id}")
            
            # Get Chrome options
            options = self._get_chrome_options(proxy=proxy, user_agent=user_agent)
            
            # Apply custom options
            if custom_options:
                for key, value in custom_options.items():
                    if key.startswith('--'):
                        options.add_argument(f"{key}={value}")
                    else:
                        options.add_argument(f"--{key}={value}")
                        
            # Create temporary user data directory if needed
            temp_user_data = None
            if not self.config.user_data_dir:
                temp_user_data = Path(tempfile.mkdtemp(prefix="uc_profile_"))
                self.temp_dirs.append(temp_user_data)
                options.add_argument(f"--user-data-dir={temp_user_data}")
                
            # Create driver instance
            driver = uc.Chrome(
                options=options,
                version_main=self.config.version_main,
                headless=self.config.headless
            )
            
            # Set timeouts
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            driver.set_script_timeout(self.config.script_timeout)
            
            # Execute stealth scripts
            await self._apply_stealth_scripts(driver)
            
            # Store session
            session = BrowserSession(
                session_id=session_id,
                driver=driver,
                created_at=time.time(),
                last_used=time.time(),
                proxy=proxy,
                user_agent=user_agent
            )
            
            self.sessions[session_id] = session
            
            logger.info(f"✅ Undetected Chrome session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create Chrome session: {str(e)}")
            raise
            
    async def _apply_stealth_scripts(self, driver):
        """Apply additional stealth JavaScript"""
        
        stealth_scripts = [
            # Override webdriver property
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});",
            
            # Override chrome property
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            """,
            
            # Override languages
            """
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """,
            
            # Override permissions
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """,
            
            # Override getUserMedia
            """
            const getParameter = WebGLRenderingContext.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter(parameter);
            };
            """
        ]
        
        for script in stealth_scripts:
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': script
                })
            except Exception as e:
                logger.debug(f"Failed to apply stealth script: {str(e)}")
                
    async def get_page(self, session_id: str, url: str, 
                      wait_for: Optional[str] = None,
                      wait_timeout: int = 10,
                      custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Navigate to a page and return content"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        driver = session.driver
        
        try:
            logger.info(f"🌐 Navigating to {url} in session {session_id}")
            start_time = time.time()
            
            # Set custom headers if provided
            if custom_headers:
                for name, value in custom_headers.items():
                    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        'userAgent': driver.execute_script("return navigator.userAgent;") + f" CustomHeader/{name}={value}"
                    })
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for specific element if requested
            if wait_for:
                try:
                    if wait_for.startswith('//'):
                        # XPath
                        element = WebDriverWait(driver, wait_timeout).until(
                            EC.presence_of_element_located((By.XPATH, wait_for))
                        )
                    elif wait_for.startswith('#'):
                        # ID
                        element = WebDriverWait(driver, wait_timeout).until(
                            EC.presence_of_element_located((By.ID, wait_for[1:]))
                        )
                    elif wait_for.startswith('.'):
                        # Class
                        element = WebDriverWait(driver, wait_timeout).until(
                            EC.presence_of_element_located((By.CLASS_NAME, wait_for[1:]))
                        )
                    else:
                        # CSS selector
                        element = WebDriverWait(driver, wait_timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                        )
                        
                    logger.info(f"✅ Found element: {wait_for}")
                    
                except TimeoutException:
                    logger.warning(f"⚠️ Timeout waiting for element: {wait_for}")
                    
            # Get page content
            html = driver.page_source
            current_url = driver.current_url
            title = driver.title
            
            # Get cookies
            cookies = {}
            for cookie in driver.get_cookies():
                cookies[cookie['name']] = cookie['value']
                
            # Update session stats
            session.last_used = time.time()
            session.page_count += 1
            
            response_time = time.time() - start_time
            
            logger.info(f"✅ Page loaded: {current_url} ({response_time:.2f}s)")
            
            return {
                'success': True,
                'url': current_url,
                'title': title,
                'html': html,
                'cookies': cookies,
                'response_time': response_time,
                'status_code': 200,  # Browser doesn't give us actual status
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get page {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'session_id': session_id
            }
            
    async def execute_script(self, session_id: str, script: str, 
                           *args) -> Dict[str, Any]:
        """Execute JavaScript in the browser"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        driver = session.driver
        
        try:
            logger.info(f"⚡ Executing script in session {session_id}")
            
            result = driver.execute_script(script, *args)
            session.last_used = time.time()
            
            return {
                'success': True,
                'result': result,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Script execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
            
    async def scroll_page(self, session_id: str, 
                         direction: str = "down",
                         pixels: Optional[int] = None,
                         pages: int = 1) -> Dict[str, Any]:
        """Scroll the page to load dynamic content"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        driver = session.driver
        
        try:
            logger.info(f"📜 Scrolling {direction} in session {session_id}")
            
            if pixels:
                if direction == "down":
                    script = f"window.scrollBy(0, {pixels});"
                else:
                    script = f"window.scrollBy(0, -{pixels});"
            else:
                # Scroll by pages
                for i in range(pages):
                    if direction == "down":
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    else:
                        driver.execute_script("window.scrollTo(0, 0);")
                        
                    # Wait a bit for dynamic content to load
                    await asyncio.sleep(1)
                    
            session.last_used = time.time()
            
            # Get updated page height
            height = driver.execute_script("return document.body.scrollHeight;")
            scroll_pos = driver.execute_script("return window.pageYOffset;")
            
            return {
                'success': True,
                'page_height': height,
                'scroll_position': scroll_pos,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Scrolling failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
            
    async def take_screenshot(self, session_id: str, 
                            save_path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        driver = session.driver
        
        try:
            logger.info(f"📷 Taking screenshot in session {session_id}")
            
            if save_path:
                success = driver.save_screenshot(save_path)
                screenshot_data = None
            else:
                screenshot_data = driver.get_screenshot_as_base64()
                success = True
                
            session.last_used = time.time()
            
            return {
                'success': success,
                'screenshot_data': screenshot_data,
                'save_path': save_path,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'session_id': session_id
            }
            
    async def destroy_session(self, session_id: str):
        """Destroy a browser session"""
        
        if session_id not in self.sessions:
            logger.warning(f"⚠️ Session {session_id} not found for destruction")
            return
            
        session = self.sessions[session_id]
        
        try:
            logger.info(f"🗑️ Destroying session {session_id}")
            session.driver.quit()
            
        except Exception as e:
            logger.error(f"❌ Failed to quit driver: {str(e)}")
            
        finally:
            # Remove from tracking
            del self.sessions[session_id]
            
    async def cleanup_expired_sessions(self, max_age_minutes: int = 30):
        """Clean up expired sessions"""
        current_time = time.time()
        max_age_seconds = max_age_minutes * 60
        
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if current_time - session.last_used > max_age_seconds:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            await self.destroy_session(session_id)
            
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get driver statistics"""
        return {
            'active_sessions': len(self.sessions),
            'total_sessions_created': self.session_counter,
            'sessions': {
                session_id: {
                    'created_at': session.created_at,
                    'last_used': session.last_used,
                    'age_minutes': (time.time() - session.created_at) / 60,
                    'page_count': session.page_count,
                    'proxy': session.proxy
                }
                for session_id, session in self.sessions.items()
            }
        }
        
    async def cleanup(self):
        """Clean up all resources"""
        # Destroy all active sessions
        for session_id in list(self.sessions.keys()):
            await self.destroy_session(session_id)
            
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"❌ Failed to remove temp dir {temp_dir}: {str(e)}")

class UndetectedChromeAdapter:
    """High-level adapter for Undetected Chrome integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = UndetectedChromeConfig(**config)
        self.driver = UndetectedChromeDriver(self.config)
        self._cleanup_task = None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not UC_AVAILABLE:
            if self.config.enabled:
                logger.error("❌ undetected-chromedriver not available")
            return
            
        logger.info("✅ Undetected Chrome adapter initialized")
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def get_page_stealth(self, url: str,
                             wait_for: Optional[str] = None,
                             proxy: Optional[str] = None,
                             user_agent: Optional[str] = None,
                             headers: Optional[Dict[str, str]] = None,
                             persistent_session: bool = False) -> Dict[str, Any]:
        """
        Get a page using stealth browser automation.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'title': str,
            'html_content': str,
            'cookies': dict,
            'response_time': float,
            'session_id': str (if persistent_session=True)
        }
        """
        
        if not self.config.enabled:
            return {
                'success': False,
                'url': url,
                'error': 'Undetected Chrome is disabled'
            }
            
        try:
            # Create session
            session_id = await self.driver.create_session(
                proxy=proxy,
                user_agent=user_agent
            )
            
            # Get the page
            result = await self.driver.get_page(
                session_id=session_id,
                url=url,
                wait_for=wait_for,
                custom_headers=headers
            )
            
            if result['success']:
                response = {
                    'success': True,
                    'url': result['url'],
                    'title': result['title'],
                    'html_content': result['html'],
                    'cookies': result['cookies'],
                    'response_time': result['response_time'],
                    'status_code': result['status_code'],
                    'method': 'undetected-chrome'
                }
                
                if persistent_session:
                    response['session_id'] = session_id
                else:
                    # Clean up session if not persistent
                    await self.driver.destroy_session(session_id)
                    
                return response
            else:
                # Clean up on failure
                await self.driver.destroy_session(session_id)
                return {
                    'success': False,
                    'url': url,
                    'error': result['error'],
                    'method': 'undetected-chrome'
                }
                
        except Exception as e:
            logger.error(f"❌ Stealth browsing failed: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'undetected-chrome'
            }
            
    async def execute_script_on_page(self, url: str, script: str,
                                   *args, **kwargs) -> Dict[str, Any]:
        """Execute JavaScript on a page"""
        
        try:
            session_id = await self.driver.create_session()
            
            # Navigate to page
            page_result = await self.driver.get_page(session_id, url)
            if not page_result['success']:
                await self.driver.destroy_session(session_id)
                return page_result
                
            # Execute script
            script_result = await self.driver.execute_script(session_id, script, *args)
            
            # Clean up
            await self.driver.destroy_session(session_id)
            
            return script_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    async def infinite_scroll_page(self, url: str, 
                                  max_scrolls: int = 10,
                                  scroll_delay: float = 2.0) -> Dict[str, Any]:
        """Perform infinite scroll to load dynamic content"""
        
        try:
            session_id = await self.driver.create_session()
            
            # Navigate to page
            page_result = await self.driver.get_page(session_id, url)
            if not page_result['success']:
                await self.driver.destroy_session(session_id)
                return page_result
                
            # Perform scrolls
            for i in range(max_scrolls):
                await self.driver.scroll_page(session_id, direction="down", pages=1)
                await asyncio.sleep(scroll_delay)
                
            # Get final content
            final_result = await self.driver.get_page(session_id, url)
            
            # Clean up
            await self.driver.destroy_session(session_id)
            
            return final_result
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            'enabled': self.config.enabled,
            'config': asdict(self.config),
            'driver_stats': self.driver.get_stats()
        }
        
    async def _cleanup_loop(self):
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(600)  # Check every 10 minutes
                await self.driver.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Cleanup task failed: {str(e)}")
                
    async def cleanup(self):
        """Clean up all resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        await self.driver.cleanup()

# Factory function
def create_undetected_chrome_adapter(config: Dict[str, Any]) -> UndetectedChromeAdapter:
    """Create and configure Undetected Chrome adapter"""
    return UndetectedChromeAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'headless': True,
        'debug': True,
        'page_load_timeout': 30,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    adapter = create_undetected_chrome_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test stealth browsing
        result = await adapter.get_page_stealth(
            'https://bot.sannysoft.com',  # Bot detection test site
            wait_for='body',
            persistent_session=False
        )
        
        if result['success']:
            print(f"✅ Success: {result['title']}")
            print(f"Content length: {len(result['html_content'])}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
