"""
Selenium-based scraper for JavaScript-heavy sites.

Provides browser automation capabilities for sites that require
JavaScript execution or complex user interactions.
"""

import time
import random
from typing import Dict, List, Optional, Any, Union, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException,
    StaleElementReferenceException, WebDriverException
)
try:
    from selenium_stealth import stealth
    import undetected_chromedriver as uc
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

from scraper.base_scraper import BaseScraper
from utils.logger import get_logger

logger = get_logger(__name__)

class SeleniumScraper(BaseScraper):
    """
    Advanced Selenium-based scraper with stealth capabilities.
    
    Features:
    - Stealth mode to avoid detection
    - Multiple browser engines
    - Proxy support
    - User agent rotation
    - Anti-fingerprinting measures
    - JavaScript interaction
    - File download handling
    """
    
    def __init__(self, 
                 browser: str = "chrome",
                 headless: bool = True,
                 stealth_mode: bool = True,
                 proxy: Optional[str] = None,
                 user_agent: Optional[str] = None,
                 window_size: Tuple[int, int] = (1920, 1080),
                 timeout: int = 30):
        super().__init__()
        
        self.browser = browser.lower()
        self.headless = headless
        self.stealth_mode = stealth_mode and STEALTH_AVAILABLE
        self.proxy = proxy
        self.user_agent = user_agent
        self.window_size = window_size
        self.timeout = timeout
        
        self.driver: Optional[webdriver.Remote] = None
        self.wait: Optional[WebDriverWait] = None
        
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup the WebDriver with appropriate options"""
        try:
            if self.browser == "chrome":
                self.driver = self._setup_chrome()
            elif self.browser == "firefox":
                self.driver = self._setup_firefox()
            elif self.browser == "undetected" and STEALTH_AVAILABLE:
                self.driver = self._setup_undetected_chrome()
            else:
                logger.warning(f"Browser {self.browser} not available, falling back to Chrome")
                self.driver = self._setup_chrome()
            
            # Configure wait
            self.wait = WebDriverWait(self.driver, self.timeout)
            
            # Apply stealth measures
            if self.stealth_mode and self.browser in ["chrome", "undetected"]:
                self._apply_stealth()
            
            logger.info(f"Selenium driver initialized: {self.browser}")
            
        except Exception as e:
            logger.error(f"Failed to setup Selenium driver: {e}")
            raise
    
    def _setup_chrome(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver"""
        options = ChromeOptions()
        
        # Basic options
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # Anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        if self.user_agent:
            options.add_argument(f"--user-agent={self.user_agent}")
        
        # Proxy
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")
        
        return webdriver.Chrome(options=options)
    
    def _setup_firefox(self) -> webdriver.Firefox:
        """Setup Firefox WebDriver"""
        options = FirefoxOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        # Profile preferences
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", self.user_agent or self._get_random_user_agent())
        profile.set_preference("dom.webdriver.enabled", False)
        profile.set_preference("useAutomationExtension", False)
        
        return webdriver.Firefox(firefox_profile=profile, options=options)
    
    def _setup_undetected_chrome(self) -> 'uc.Chrome':
        """Setup undetected Chrome WebDriver"""
        if not STEALTH_AVAILABLE:
            raise ImportError("undetected_chromedriver not available")
        
        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        
        if self.headless:
            options.add_argument("--headless")
        
        options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
        
        if self.user_agent:
            options.add_argument(f"--user-agent={self.user_agent}")
        
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")
        
        return uc.Chrome(options=options)
    
    def _apply_stealth(self):
        """Apply stealth measures to avoid detection"""
        if STEALTH_AVAILABLE and self.browser == "chrome":
            try:
                stealth(self.driver,
                       languages=["en-US", "en"],
                       vendor="Google Inc.",
                       platform="Win32",
                       webgl_vendor="Intel Inc.",
                       renderer="Intel Iris OpenGL Engine",
                       fix_hairline=True)
            except Exception as e:
                logger.warning(f"Failed to apply stealth mode: {e}")
        
        # Execute additional anti-detection scripts
        try:
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                })
            """)
        except Exception:
            pass
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        ]
        return random.choice(user_agents)
    
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Scrape a URL using Selenium.
        
        Args:
            url: URL to scrape
            **kwargs: Additional scraping parameters
            
        Returns:
            Scraped data
        """
        try:
            # Navigate to URL
            self.driver.get(url)
            
            # Wait for page load
            self._wait_for_page_load(**kwargs)
            
            # Handle JavaScript interactions
            if kwargs.get('javascript_actions'):
                self._execute_javascript_actions(kwargs['javascript_actions'])
            
            # Wait for specific elements if specified
            if kwargs.get('wait_for_elements'):
                self._wait_for_elements(kwargs['wait_for_elements'])
            
            # Scroll if needed
            if kwargs.get('scroll_behavior'):
                self._handle_scrolling(kwargs['scroll_behavior'])
            
            # Extract data
            data = self._extract_data(**kwargs)
            
            return {
                'url': url,
                'status': 'success',
                'data': data,
                'page_source': self.driver.page_source,
                'current_url': self.driver.current_url,
                'title': self.driver.title
            }
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return {
                'url': url,
                'status': 'error',
                'error': str(e),
                'page_source': getattr(self.driver, 'page_source', ''),
                'current_url': getattr(self.driver, 'current_url', url)
            }
    
    def _wait_for_page_load(self, **kwargs):
        """Wait for page to fully load"""
        try:
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Additional wait time if specified
            additional_wait = kwargs.get('page_load_wait', 2)
            time.sleep(additional_wait)
        except TimeoutException:
            logger.warning("Page load timeout")
    
    def _execute_javascript_actions(self, actions: List[Dict[str, Any]]):
        """Execute JavaScript actions on the page"""
        for action in actions:
            try:
                action_type = action.get('type')
                
                if action_type == 'click':
                    self._click_element(action.get('selector'))
                elif action_type == 'input':
                    self._input_text(action.get('selector'), action.get('text'))
                elif action_type == 'scroll':
                    self._scroll_to_element(action.get('selector'))
                elif action_type == 'wait':
                    time.sleep(action.get('duration', 1))
                elif action_type == 'execute_script':
                    self.driver.execute_script(action.get('script'))
            except Exception as e:
                logger.warning(f"JavaScript action failed: {e}")
    
    def _wait_for_elements(self, elements: List[str]):
        """Wait for specific elements to be present"""
        for selector in elements:
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            except TimeoutException:
                logger.warning(f"Element not found within timeout: {selector}")
    
    def _handle_scrolling(self, scroll_config: Dict[str, Any]):
        """Handle page scrolling behavior"""
        scroll_type = scroll_config.get('type', 'to_bottom')
        
        if scroll_type == 'to_bottom':
            self._scroll_to_bottom(scroll_config.get('pause_time', 1))
        elif scroll_type == 'infinite':
            self._infinite_scroll(scroll_config.get('max_scrolls', 10))
        elif scroll_type == 'to_element':
            self._scroll_to_element(scroll_config.get('selector'))
    
    def _scroll_to_bottom(self, pause_time: float = 1):
        """Scroll to bottom of page"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(pause_time)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            logger.warning(f"Scroll to bottom failed: {e}")
    
    def _infinite_scroll(self, max_scrolls: int = 10):
        """Perform infinite scroll with limited iterations"""
        for i in range(max_scrolls):
            try:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.warning(f"Infinite scroll iteration {i} failed: {e}")
                break
    
    def _scroll_to_element(self, selector: str):
        """Scroll to a specific element"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
        except NoSuchElementException:
            logger.warning(f"Element not found for scrolling: {selector}")
    
    def _click_element(self, selector: str):
        """Click an element"""
        try:
            element = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
        except (TimeoutException, ElementClickInterceptedException) as e:
            logger.warning(f"Failed to click element {selector}: {e}")
    
    def _input_text(self, selector: str, text: str):
        """Input text into an element"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
        except TimeoutException:
            logger.warning(f"Failed to input text into {selector}")
    
    def _extract_data(self, **kwargs) -> Dict[str, Any]:
        """Extract data from the page"""
        data = {}
        
        # Extract by CSS selectors
        if kwargs.get('css_selectors'):
            data.update(self._extract_by_css(kwargs['css_selectors']))
        
        # Extract by XPath
        if kwargs.get('xpath_selectors'):
            data.update(self._extract_by_xpath(kwargs['xpath_selectors']))
        
        # Extract form data
        if kwargs.get('extract_forms'):
            data['forms'] = self._extract_forms()
        
        # Extract links
        if kwargs.get('extract_links'):
            data['links'] = self._extract_links()
        
        return data
    
    def _extract_by_css(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using CSS selectors"""
        data = {}
        
        for key, selector in selectors.items():
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) == 1:
                    data[key] = elements[0].text.strip()
                elif len(elements) > 1:
                    data[key] = [elem.text.strip() for elem in elements]
                else:
                    data[key] = None
            except Exception as e:
                logger.warning(f"Failed to extract with CSS selector {selector}: {e}")
                data[key] = None
        
        return data
    
    def _extract_by_xpath(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using XPath selectors"""
        data = {}
        
        for key, xpath in selectors.items():
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                if len(elements) == 1:
                    data[key] = elements[0].text.strip()
                elif len(elements) > 1:
                    data[key] = [elem.text.strip() for elem in elements]
                else:
                    data[key] = None
            except Exception as e:
                logger.warning(f"Failed to extract with XPath {xpath}: {e}")
                data[key] = None
        
        return data
    
    def _extract_forms(self) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, "form")
            
            for form in form_elements:
                form_data = {
                    'action': form.get_attribute('action'),
                    'method': form.get_attribute('method'),
                    'fields': []
                }
                
                # Extract input fields
                inputs = form.find_elements(By.TAG_NAME, "input")
                for input_elem in inputs:
                    field_data = {
                        'name': input_elem.get_attribute('name'),
                        'type': input_elem.get_attribute('type'),
                        'value': input_elem.get_attribute('value'),
                        'placeholder': input_elem.get_attribute('placeholder')
                    }
                    form_data['fields'].append(field_data)
                
                forms.append(form_data)
        except Exception as e:
            logger.warning(f"Failed to extract forms: {e}")
        
        return forms
    
    def _extract_links(self) -> List[Dict[str, str]]:
        """Extract links from the page"""
        links = []
        
        try:
            link_elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in link_elements:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if href:
                    links.append({
                        'href': href,
                        'text': text,
                        'title': link.get_attribute('title')
                    })
        except Exception as e:
            logger.warning(f"Failed to extract links: {e}")
        
        return links
    
    def close(self):
        """Close the browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium driver closed")
            except Exception as e:
                logger.error(f"Error closing Selenium driver: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()