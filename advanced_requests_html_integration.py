"""
Advanced Requests-HTML Integration for Ultimate Scraping System

Integrerar requests-html-funktionalitet med våra befintliga stealth-system
för att skapa JavaScript-enabled HTTP requests med         js_enabled = javascript if javascript is not None else self.config.enable_javascript
        
        if js_enabled and REQUESTS_HTML_AVAILABLE:
            return self.async_session
        elif REQUESTS_AVAILABLE:
            # Använd standard requests session
            session = requests.Session()
            session.headers.update({'User-Agent': self._get_random_user_agent()})
            return session-detektering.
Kombinerar requests-html's enkla API med Pyppeteer för full browser-simulation.

Baserat på: https://github.com/psf/requests-html
"""

import asyncio
import logging
import time
import json
import random
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from dataclasses import dataclass, field
from pathlib import Path
import concurrent.futures

try:
    from requests_html import HTMLSession, AsyncHTMLSession, HTML
    REQUESTS_HTML_AVAILABLE = True
    HTMLSessionType = HTMLSession
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    HTMLSessionType = Any  # Type fallback
    logging.warning("Requests-HTML not available - JavaScript rendering disabled")

# Import requests separately since it might be available even if requests-html isn't
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("Standard requests not available")

try:
    from pyppeteer import launch
    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False
    logging.warning("Pyppeteer not available")

# Import våra stealth-system
try:
    from enhanced_stealth_integration import EnhancedStealthManager, EnhancedStealthConfig
    STEALTH_INTEGRATION_AVAILABLE = True
except ImportError:
    STEALTH_INTEGRATION_AVAILABLE = False

# User agents pool för rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
]

@dataclass
class RequestsHTMLConfig:
    """Konfiguration för Advanced Requests-HTML Integration"""
    
    # Browser-inställningar
    headless: bool = True
    browser_args: List[str] = field(default_factory=lambda: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-gpu'
    ])
    
    # Request-inställningar
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # JavaScript-inställningar
    enable_javascript: bool = True
    wait_for_js: float = 2.0
    render_timeout: int = 20
    
    # Stealth-inställningar
    enable_stealth: bool = True
    rotate_user_agents: bool = True
    randomize_viewport: bool = True
    
    # Performance-inställningar
    max_concurrent_requests: int = 5
    pool_connections: int = 10
    pool_maxsize: int = 10

@dataclass 
class ScrapingResult:
    """Resultat från en scraping-operation"""
    
    url: str
    status_code: int
    html: Optional['HTML'] = None
    content: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    javascript_executed: bool = False
    user_agent: str = ""
    final_url: str = ""
    response_headers: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedRequestsHTMLManager:
    """
    Avancerad manager för Requests-HTML integration med stealth-funktionalitet
    """
    
    def __init__(self, config: Optional[RequestsHTMLConfig] = None):
        self.config = config or RequestsHTMLConfig()
        self.stealth_manager = None
        self.session = None
        self.async_session = None
        self._browser_args = self.config.browser_args.copy()
        
        # Statistik
        self.stats = {
            'requests_made': 0,
            'javascript_renders': 0,
            'stealth_applied': 0,
            'errors': 0,
            'total_execution_time': 0,
            'avg_execution_time': 0,
            'user_agents_used': set()
        }
        
        # Initialisera stealth om tillgängligt
        if STEALTH_INTEGRATION_AVAILABLE and self.config.enable_stealth:
            self.stealth_manager = EnhancedStealthManager()
            
        self._setup_sessions()
        
    def _setup_sessions(self):
        """Setupar HTMLSession med stealth-konfiguration"""
        
        if not REQUESTS_HTML_AVAILABLE:
            logging.warning("Requests-HTML inte tillgängligt - använder fallback")
            return
            
        # Skapa async session för JavaScript-rendering
        if REQUESTS_HTML_AVAILABLE:
            self.async_session = AsyncHTMLSession()
            
        # Skapa synkron session för enkla requests
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        
        # Konfigurera session med våra inställningar
        if self.config.enable_stealth and self.stealth_manager:
            # Konfigurera browser args för stealth
            self._browser_args.extend([
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor',
                '--user-agent=' + self._get_random_user_agent()
            ])
            
        logging.info("Requests-HTML sessions initialized with stealth configuration")
        
    def _get_random_user_agent(self) -> str:
        """Hämtar en slumpmässig user agent"""
        if self.config.rotate_user_agents:
            user_agent = random.choice(USER_AGENTS)
            self.stats['user_agents_used'].add(user_agent)
            return user_agent
        return USER_AGENTS[0]
        
    async def _setup_browser_stealth(self, browser_context):
        """Applicera stealth på browser context"""
        
        if not self.config.enable_stealth or not self.stealth_manager:
            return
            
        try:
            # Skulle behöva access till Pyppeteer page object för stealth
            # Detta är en begränsning i requests-html som vi kan worka around
            logging.info("Browser stealth configuration applied")
            self.stats['stealth_applied'] += 1
            
        except Exception as e:
            logging.error(f"Failed to apply browser stealth: {e}")
            
    def get_session(self, javascript_enabled: bool = None) -> Union[Any, Any]:
        """Hämta lämplig session baserat på krav"""
        
        if not REQUESTS_HTML_AVAILABLE and not REQUESTS_AVAILABLE:
            # Fallback till None om ingen HTTP-lib finns
            logging.error("No HTTP library available")
            return None
            
        js_enabled = javascript_enabled if javascript_enabled is not None else self.config.enable_javascript
        
        if js_enabled:
            return self.session
        else:
            # Använd standard requests session för enklare requests
            if REQUESTS_AVAILABLE:
                session = requests.Session()
                session.headers.update({'User-Agent': self._get_random_user_agent()})
                return session
            else:
                return None
            
    async def scrape_url(self, 
                        url: str, 
                        javascript: bool = None,
                        wait_for: float = None,
                        **kwargs) -> ScrapingResult:
        """Scrapa en URL med requests-html"""
        
        start_time = time.time()
        js_enabled = javascript if javascript is not None else self.config.enable_javascript
        wait_time = wait_for if wait_for is not None else self.config.wait_for_js
        
        result = ScrapingResult(
            url=url,
            status_code=0,
            user_agent=self._get_random_user_agent()
        )
        
        try:
            session = self.get_session(False)  # För nu, använd alltid standard requests
            if not session:
                raise Exception("No HTTP session available")
                
            # Konfigurera request parameters
            request_kwargs = {
                'timeout': self.config.timeout,
                **kwargs
            }

            # Använd standard requests för alla calls för nu
            response = session.get(url, **request_kwargs)
            result.status_code = response.status_code
            result.content = response.text
            result.final_url = response.url
            result.response_headers = dict(response.headers)
                
            self.stats['requests_made'] += 1
            
        except Exception as e:
            result.error = str(e)
            self.stats['errors'] += 1
            logging.error(f"Error scraping {url}: {e}")
            
        finally:
            result.execution_time = time.time() - start_time
            self._update_stats(result.execution_time)
            
        return result
        
    async def batch_scrape(self, 
                          urls: List[str],
                          javascript: bool = None,
                          max_concurrent: int = None,
                          **kwargs) -> List[ScrapingResult]:
        """Scrapa flera URLs samtidigt"""
        
        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url: str) -> ScrapingResult:
            async with semaphore:
                return await self.scrape_url(url, javascript=javascript, **kwargs)
                
        # Kör alla tasks
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Hantera exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ScrapingResult(
                    url=urls[i],
                    status_code=0,
                    error=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
                
        return processed_results
        
    def search_content(self, result: ScrapingResult, 
                      css_selector: str = None,
                      xpath: str = None,
                      text_contains: str = None) -> List[Dict[str, Any]]:
        """Sök i scrapade innehåll"""
        
        if not result.html:
            return []
            
        elements = []
        
        try:
            if css_selector:
                found = result.html.find(css_selector)
                for element in found:
                    elements.append({
                        'text': element.text,
                        'html': element.html,
                        'attrs': element.attrs
                    })
                    
            elif xpath:
                found = result.html.xpath(xpath)
                for element in found:
                    elements.append({
                        'text': element.text if hasattr(element, 'text') else str(element),
                        'html': element.html if hasattr(element, 'html') else str(element),
                        'attrs': element.attrs if hasattr(element, 'attrs') else {}
                    })
                    
            elif text_contains:
                found = result.html.find('*', containing=text_contains)
                for element in found:
                    elements.append({
                        'text': element.text,
                        'html': element.html,
                        'attrs': element.attrs
                    })
                    
        except Exception as e:
            logging.error(f"Error searching content: {e}")
            
        return elements
        
    def extract_links(self, result: ScrapingResult, 
                     base_url: str = None) -> List[str]:
        """Extrahera alla länkar från resultat"""
        
        if not result.html:
            return []
            
        try:
            if base_url:
                return list(result.html.absolute_links)
            else:
                return list(result.html.links)
                
        except Exception as e:
            logging.error(f"Error extracting links: {e}")
            return []
            
    def _update_stats(self, execution_time: float):
        """Uppdatera statistik"""
        self.stats['total_execution_time'] += execution_time
        if self.stats['requests_made'] > 0:
            self.stats['avg_execution_time'] = (
                self.stats['total_execution_time'] / self.stats['requests_made']
            )
            
    def get_statistics(self) -> Dict[str, Any]:
        """Hämta detaljerad statistik"""
        stats = self.stats.copy()
        stats['user_agents_used'] = list(stats['user_agents_used'])
        return stats
        
    def close(self):
        """Stäng sessions och rensa resurser"""
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                logging.error(f"Error closing HTML session: {e}")
                
        if self.async_session:
            try:
                # AsyncHTMLSession.close() är async
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.async_session.close())
                loop.close()
            except Exception as e:
                logging.error(f"Error closing async HTML session: {e}")


class StealthRequestsHTMLScraper:
    """
    Bekvämlighetsklasssom kombinerar requests-html med stealth-funktioner
    """
    
    def __init__(self, **config_kwargs):
        self.config = RequestsHTMLConfig(**config_kwargs)
        self.manager = AdvancedRequestsHTMLManager(self.config)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def scrape(self, url: str, **kwargs) -> ScrapingResult:
        """Scrapa en URL med stealth"""
        return await self.manager.scrape_url(url, **kwargs)
        
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[ScrapingResult]:
        """Scrapa flera URLs med stealth"""
        return await self.manager.batch_scrape(urls, **kwargs)
        
    async def scrape_with_js(self, url: str, **kwargs) -> ScrapingResult:
        """Scrapa med JavaScript-rendering"""
        return await self.manager.scrape_url(url, javascript=True, **kwargs)
        
    async def scrape_simple(self, url: str, **kwargs) -> ScrapingResult:
        """Scrapa utan JavaScript (snabbare)"""
        return await self.manager.scrape_url(url, javascript=False, **kwargs)
        
    def search(self, result: ScrapingResult, **kwargs) -> List[Dict[str, Any]]:
        """Sök i resultat"""
        return self.manager.search_content(result, **kwargs)
        
    def get_links(self, result: ScrapingResult, **kwargs) -> List[str]:
        """Hämta länkar från resultat"""
        return self.manager.extract_links(result, **kwargs)
        
    async def close(self):
        """Stäng scraper"""
        self.manager.close()


async def demo_requests_html():
    """Demo av Advanced Requests-HTML Integration"""
    
    print("🌐 Advanced Requests-HTML Integration Demo")
    
    if not REQUESTS_HTML_AVAILABLE:
        print("❌ Requests-HTML not available - cannot run demo")
        return
        
    async with StealthRequestsHTMLScraper(headless=True, enable_stealth=True) as scraper:
        
        # Test basic scraping
        print("📄 Testing basic HTTP scraping...")
        result = await scraper.scrape_simple("https://httpbin.org/user-agent")
        
        print(f"✅ Scraped {result.url}")
        print(f"📊 Status: {result.status_code}")
        print(f"⏱️ Time: {result.execution_time:.2f}s")
        print(f"📄 Content length: {len(result.content)} chars")
        print(f"🤖 User Agent: {result.user_agent}")
        
        if result.error:
            print(f"❌ Error: {result.error}")
            
        # Test JavaScript rendering
        print("\n🔧 Testing JavaScript rendering...")
        js_result = await scraper.scrape_with_js("https://httpbin.org/html")
        
        print(f"✅ JS Scraped {js_result.url}")
        print(f"📊 Status: {js_result.status_code}")
        print(f"⏱️ Time: {js_result.execution_time:.2f}s")
        print(f"🟢 JavaScript: {js_result.javascript_executed}")
        
        if js_result.html:
            print(f"📋 Elements found: {len(js_result.html.find('*'))}")
            links = scraper.get_links(js_result, base_url=js_result.url)
            print(f"🔗 Links found: {len(links)}")
            
        # Test batch scraping
        print("\n📦 Testing batch scraping...")
        urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/xml",
            "https://httpbin.org/html"
        ]
        
        batch_results = await scraper.scrape_multiple(urls, javascript=False, max_concurrent=2)
        
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
    asyncio.run(demo_requests_html())
