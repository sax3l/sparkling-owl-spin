"""
Stealth browser implementation for anti-bot detection avoidance.

Provides:
- Browser fingerprint modification
- Navigator property patching
- WebDriver detection hiding
- Human-like behavior simulation
- Advanced stealth techniques
"""

import random
import time
import asyncio
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

from src.utils.logger import get_logger

logger = get_logger(__name__)

class StealthBrowser:
    """Advanced stealth browser with anti-detection capabilities."""
    
    def __init__(self, browser_type: str = "chrome", headless: bool = True, 
                 stealth_level: str = "high"):
        self.browser_type = browser_type
        self.headless = headless
        self.stealth_level = stealth_level
        self.driver = None
        self.user_agents = self._load_user_agents()
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1280, 720), (1600, 900), (1024, 768), (1680, 1050)
        ]
    
    def _load_user_agents(self) -> List[str]:
        """Load realistic user agent strings."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
    
    async def create_driver(self) -> webdriver:
        """Create a stealth-configured browser driver."""
        if self.browser_type.lower() == "chrome":
            return await self._create_chrome_driver()
        elif self.browser_type.lower() == "firefox":
            return await self._create_firefox_driver()
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
    
    async def _create_chrome_driver(self) -> webdriver:
        """Create stealth Chrome driver with undetected-chromedriver."""
        try:
            # Use undetected-chromedriver for maximum stealth
            options = uc.ChromeOptions()
            
            # Basic stealth options
            if self.headless:
                options.add_argument("--headless=new")
            
            # Anti-detection arguments
            stealth_args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-javascript",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-default-apps",
                "--disable-popup-blocking",
                "--disable-translate",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-client-side-phishing-detection",
                "--disable-sync",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--disable-hang-monitor",
                "--disable-prompt-on-repost",
                "--disable-domain-reliability",
                "--disable-background-networking",
                "--disable-background-mode",
                "--disable-features=VizServiceSharedBitmapManager"
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            # Random user agent
            user_agent = random.choice(self.user_agents)
            options.add_argument(f"--user-agent={user_agent}")
            
            # Random window size
            width, height = random.choice(self.screen_resolutions)
            options.add_argument(f"--window-size={width},{height}")
            
            # Advanced stealth for high level
            if self.stealth_level == "high":
                options.add_experimental_option("excludeSwitches", [
                    "enable-automation", "enable-logging"
                ])
                options.add_experimental_option("useAutomationExtension", False)
                
                # Additional fingerprint randomization
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-dev-shm-usage")
            
            # Create driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Execute stealth scripts
            await self._apply_stealth_scripts()
            
            logger.info("Stealth Chrome driver created successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create Chrome driver: {e}")
            raise
    
    async def _create_firefox_driver(self) -> webdriver:
        """Create stealth Firefox driver."""
        try:
            options = FirefoxOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            # Firefox stealth options
            stealth_args = [
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ]
            
            for arg in stealth_args:
                options.add_argument(arg)
            
            # Firefox preferences for stealth
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            options.set_preference("general.useragent.override", random.choice(self.user_agents))
            
            self.driver = webdriver.Firefox(options=options)
            
            # Execute stealth scripts
            await self._apply_stealth_scripts()
            
            logger.info("Stealth Firefox driver created successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to create Firefox driver: {e}")
            raise
    
    async def _apply_stealth_scripts(self):
        """Apply JavaScript-based stealth modifications."""
        if not self.driver:
            return
        
        # Hide webdriver property
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        # Override plugins
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        # Override languages
        self.driver.execute_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        # Override permissions
        self.driver.execute_script("""
            const originalQuery = window.navigator.permissions.query;
            return window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        # Random screen properties
        width, height = random.choice(self.screen_resolutions)
        self.driver.execute_script(f"""
            Object.defineProperty(screen, 'width', {{
                get: () => {width}
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => {height}
            }});
            Object.defineProperty(screen, 'availWidth', {{
                get: () => {width}
            }});
            Object.defineProperty(screen, 'availHeight', {{
                get: () => {height - 40}
            }});
        """)
        
        # Hide automation indicators
        self.driver.execute_script("""
            window.chrome = {
                runtime: {},
            };
        """)
        
        # Randomize timezone
        timezones = ["America/New_York", "Europe/London", "Asia/Tokyo", "Europe/Berlin"]
        timezone = random.choice(timezones)
        self.driver.execute_script(f"""
            Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {{
                value: function() {{
                    return {{
                        timeZone: '{timezone}'
                    }};
                }}
            }});
        """)
        
        logger.debug("Stealth scripts applied successfully")
    
    async def human_like_navigation(self, url: str, delay_range: tuple = (2, 5)):
        """Navigate to URL with human-like behavior."""
        if not self.driver:
            await self.create_driver()
        
        # Random delay before navigation
        delay = random.uniform(*delay_range)
        await asyncio.sleep(delay)
        
        try:
            # Navigate to page
            self.driver.get(url)
            
            # Random scroll behavior
            await self._simulate_human_scrolling()
            
            # Random mouse movements (if not headless)
            if not self.headless:
                await self._simulate_mouse_movement()
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logger.info(f"Successfully navigated to: {url}")
            
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {e}")
            raise
    
    async def _simulate_human_scrolling(self):
        """Simulate human-like scrolling behavior."""
        try:
            # Get page height
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Random number of scrolls
            num_scrolls = random.randint(2, 5)
            
            for i in range(num_scrolls):
                # Random scroll position
                scroll_position = random.randint(0, max(0, page_height - viewport_height))
                
                # Smooth scroll with easing
                self.driver.execute_script(f"""
                    window.scrollTo({{
                        top: {scroll_position},
                        behavior: 'smooth'
                    }});
                """)
                
                # Random pause between scrolls
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            logger.debug(f"Scrolling simulation failed: {e}")
    
    async def _simulate_mouse_movement(self):
        """Simulate random mouse movements."""
        try:
            from selenium.webdriver import ActionChains
            
            actions = ActionChains(self.driver)
            
            # Random mouse movements
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                
                actions.move_by_offset(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.5))
            
            actions.perform()
            
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed: {e}")
    
    async def wait_and_find_element(self, locator: tuple, timeout: int = 10):
        """Wait for element with random delays."""
        # Random wait before searching
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            
            # Random delay after finding element
            await asyncio.sleep(random.uniform(0.2, 0.8))
            
            return element
            
        except Exception as e:
            logger.error(f"Element not found: {locator}, error: {e}")
            raise
    
    async def human_like_click(self, element):
        """Perform human-like click with random delays."""
        try:
            # Random delay before click
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Small delay after scroll
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Click element
            element.click()
            
            # Random delay after click
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            raise
    
    async def human_like_typing(self, element, text: str, typing_speed: str = "normal"):
        """Type text with human-like speed and patterns."""
        try:
            # Clear existing text
            element.clear()
            
            # Determine typing delays based on speed
            speed_configs = {
                "slow": (0.1, 0.3),
                "normal": (0.05, 0.15),
                "fast": (0.02, 0.08)
            }
            
            min_delay, max_delay = speed_configs.get(typing_speed, speed_configs["normal"])
            
            # Type character by character
            for char in text:
                element.send_keys(char)
                
                # Random delay between keystrokes
                delay = random.uniform(min_delay, max_delay)
                
                # Longer pause for spaces and punctuation
                if char in " .,!?":
                    delay *= random.uniform(1.5, 3.0)
                
                await asyncio.sleep(delay)
            
            # Random pause after typing
            await asyncio.sleep(random.uniform(0.5, 1.0))
            
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            raise
    
    def get_page_source(self) -> str:
        """Get current page source."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """Get current page URL."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        return self.driver.current_url
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot of current page."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        if not filename:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        self.driver.save_screenshot(filename)
        return filename
    
    async def close(self):
        """Close the browser driver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser driver closed successfully")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            finally:
                self.driver = None

class StealthBrowserPool:
    """Pool of stealth browsers for concurrent operations."""
    
    def __init__(self, pool_size: int = 3, browser_type: str = "chrome"):
        self.pool_size = pool_size
        self.browser_type = browser_type
        self.browsers: List[StealthBrowser] = []
        self.available_browsers: asyncio.Queue = asyncio.Queue()
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize browser pool."""
        async with self.lock:
            for i in range(self.pool_size):
                browser = StealthBrowser(
                    browser_type=self.browser_type,
                    headless=True,
                    stealth_level="high"
                )
                await browser.create_driver()
                self.browsers.append(browser)
                await self.available_browsers.put(browser)
                
        logger.info(f"Initialized browser pool with {self.pool_size} browsers")
    
    async def get_browser(self) -> StealthBrowser:
        """Get an available browser from the pool."""
        return await self.available_browsers.get()
    
    async def return_browser(self, browser: StealthBrowser):
        """Return browser to the pool."""
        await self.available_browsers.put(browser)
    
    async def close_all(self):
        """Close all browsers in the pool."""
        async with self.lock:
            for browser in self.browsers:
                await browser.close()
            self.browsers.clear()
            
        logger.info("All browsers in pool closed")

# Context manager for stealth browser usage
class StealthBrowserContext:
    """Context manager for stealth browser operations."""
    
    def __init__(self, browser_type: str = "chrome", headless: bool = True):
        self.browser_type = browser_type
        self.headless = headless
        self.browser = None
    
    async def __aenter__(self) -> StealthBrowser:
        self.browser = StealthBrowser(
            browser_type=self.browser_type,
            headless=self.headless,
            stealth_level="high"
        )
        await self.browser.create_driver()
        return self.browser
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()

# Factory function for creating stealth browsers
async def create_stealth_browser(browser_type: str = "chrome", 
                               headless: bool = True,
                               stealth_level: str = "high") -> StealthBrowser:
    """Factory function to create and initialize a stealth browser."""
    browser = StealthBrowser(
        browser_type=browser_type,
        headless=headless,
        stealth_level=stealth_level
    )
    await browser.create_driver()
    return browser