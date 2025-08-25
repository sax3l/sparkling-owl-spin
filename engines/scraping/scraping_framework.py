#!/usr/bin/env python3
"""
Enhanced Scraping Framework Adapter för Sparkling-Owl-Spin
Integrerar Scrapy, Crawlee, Playwright, Colly-inspirerad arkitektur och mer
"""

import logging
import asyncio
import aiohttp
import json
import time
import tempfile
import os
import random
from typing import Dict, List, Any, Optional, Union, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlencode
import subprocess
import yaml

# Scrapy integration
try:
    import scrapy
    from scrapy.crawler import CrawlerProcess, CrawlerRunner
    from scrapy.utils.project import get_project_settings
    from twisted.internet import reactor, defer
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False

# Playwright integration
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# BeautifulSoup integration
try:
    from bs4 import BeautifulSoup
    import lxml
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

# Requests-HTML integration
try:
    from requests_html import AsyncHTMLSession, HTMLSession
    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False

logger = logging.getLogger(__name__)

class ScrapingEngine(Enum):
    """Enhanced scraping engines"""
    SCRAPY = "scrapy"                    # Scrapy framework
    PLAYWRIGHT = "playwright"           # Playwright browser automation
    REQUESTS_HTML = "requests_html"     # Requests-HTML with PyQuery
    BEAUTIFULSOUP = "beautifulsoup"     # BeautifulSoup + aiohttp
    SELENIUM = "selenium"               # Selenium WebDriver
    COLLY_STYLE = "colly_style"         # Colly-inspired async scraping
    CRAWLEE_STYLE = "crawlee_style"     # Crawlee-inspired patterns
    CUSTOM_ASYNC = "custom_async"       # Custom async implementation

class DataExtractionMethod(Enum):
    """Data extraction methods"""
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    REGEX = "regex"
    JSON_PATH = "json_path"
    CUSTOM_PARSER = "custom_parser"
    AI_EXTRACTION = "ai_extraction"    # AI-powered extraction
    TEMPLATE_MATCHING = "template_matching"

class ScrapingStrategy(Enum):
    """Scraping strategies"""
    BREADTH_FIRST = "breadth_first"     # BFS crawling
    DEPTH_FIRST = "depth_first"         # DFS crawling
    PRIORITY_QUEUE = "priority_queue"   # Priority-based
    CONCURRENT = "concurrent"           # High concurrency
    POLITE = "polite"                   # Respectful crawling
    AGGRESSIVE = "aggressive"           # Fast extraction
    STEALTH = "stealth"                 # Anti-detection

@dataclass
class ScrapingRule:
    """Enhanced scraping rule definition"""
    name: str
    url_pattern: str
    extraction_rules: Dict[str, Any]
    follow_links: bool = True
    callback: Optional[str] = None
    priority: int = 0
    allowed_domains: List[str] = field(default_factory=list)
    denied_paths: List[str] = field(default_factory=list)
    custom_headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: Optional[float] = None
    javascript_required: bool = False
    wait_for_element: Optional[str] = None
    scroll_to_bottom: bool = False
    take_screenshot: bool = False
    extract_links: bool = True
    pagination: Optional[Dict[str, Any]] = None

@dataclass
class ScrapedItem:
    """Enhanced scraped item"""
    url: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    extracted_at: datetime = field(default_factory=datetime.now)
    rule_name: Optional[str] = None
    engine_used: Optional[ScrapingEngine] = None
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    links_found: List[str] = field(default_factory=list)
    images_found: List[str] = field(default_factory=list)
    content_hash: Optional[str] = None

@dataclass
class ScrapingJob:
    """Enhanced scraping job configuration"""
    job_id: str
    name: str
    start_urls: List[str]
    rules: List[ScrapingRule]
    engine: ScrapingEngine = ScrapingEngine.BEAUTIFULSOUP
    strategy: ScrapingStrategy = ScrapingStrategy.BREADTH_FIRST
    max_pages: Optional[int] = None
    max_depth: Optional[int] = None
    concurrency: int = 10
    delay_range: tuple = (1.0, 3.0)
    user_agents: List[str] = field(default_factory=list)
    proxies: List[str] = field(default_factory=list)
    cookies: Dict[str, str] = field(default_factory=dict)
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    output_format: str = "json"
    output_file: Optional[str] = None
    retry_attempts: int = 3
    timeout: int = 30
    respect_robots_txt: bool = True
    auto_throttle: bool = True

class EnhancedScrapingFrameworkAdapter:
    """Enhanced Scraping Framework med integration av flera engines"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        
        # Active jobs
        self.active_jobs: Dict[str, ScrapingJob] = {}
        self.job_results: Dict[str, List[ScrapedItem]] = {}
        self.job_status: Dict[str, str] = {}  # running, completed, failed, stopped
        
        # Scraping engines
        self.available_engines: List[ScrapingEngine] = []
        self.engine_sessions: Dict[str, Any] = {}
        
        # Browser instances för Playwright
        self.playwright_browsers: Dict[str, Browser] = {}
        
        # Session management
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None
        self.requests_html_session: Optional[AsyncHTMLSession] = None
        
        # Rate limiting och throttling
        self.domain_delays: Dict[str, float] = {}
        self.last_request_times: Dict[str, datetime] = {}
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Proxy rotation
        self.proxies: List[str] = []
        self.proxy_index = 0
        
        # Content deduplication
        self.content_hashes: set = set()
        
        # Penetrationstestning disclaimer
        self.authorized_domains = set()
        
        # Statistik
        self.stats = {
            "total_jobs_started": 0,
            "jobs_completed": 0,
            "jobs_failed": 0,
            "total_pages_scraped": 0,
            "total_items_extracted": 0,
            "by_engine": {},
            "by_strategy": {},
            "total_errors": 0,
            "content_duplicates": 0,
            "average_response_time": 0.0,
            "domains_scraped": set()
        }
        
    async def initialize(self):
        """Initialize Enhanced Scraping Framework adapter"""
        try:
            logger.info("🕷️ Initializing Enhanced Scraping Framework Adapter (Authorized Pentest Only)")
            
            # Detect available engines
            self.available_engines = await self._detect_available_engines()
            logger.info(f"📋 Available scraping engines: {', '.join([e.value for e in self.available_engines])}")
            
            # Initialize aiohttp session
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.aiohttp_session = aiohttp.ClientSession(
                timeout=timeout,
                headers={'User-Agent': random.choice(self.user_agents)}
            )
            
            # Initialize Requests-HTML session
            if REQUESTS_HTML_AVAILABLE:
                self.requests_html_session = AsyncHTMLSession()
                
            # Initialize statistics
            for engine in ScrapingEngine:
                self.stats["by_engine"][engine.value] = {
                    "jobs": 0,
                    "pages": 0,
                    "items": 0,
                    "errors": 0,
                    "avg_response_time": 0.0
                }
                
            for strategy in ScrapingStrategy:
                self.stats["by_strategy"][strategy.value] = {
                    "jobs": 0,
                    "pages": 0,
                    "success_rate": 0.0
                }
            
            self.initialized = True
            logger.info("✅ Enhanced Scraping Framework Adapter initialized för penetrationstestning")
            logger.warning("⚠️ ENDAST FÖR PENETRATIONSTESTNING AV EGNA SERVRAR")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Scraping Framework: {str(e)}")
            self.initialized = True  # Continue with basic functionality
            
    async def _detect_available_engines(self) -> List[ScrapingEngine]:
        """Detect tillgängliga scraping engines"""
        available = [ScrapingEngine.CUSTOM_ASYNC]  # Always available
        
        if SCRAPY_AVAILABLE:
            available.append(ScrapingEngine.SCRAPY)
            
        if PLAYWRIGHT_AVAILABLE:
            available.append(ScrapingEngine.PLAYWRIGHT)
            
        if BEAUTIFULSOUP_AVAILABLE:
            available.append(ScrapingEngine.BEAUTIFULSOUP)
            
        if REQUESTS_HTML_AVAILABLE:
            available.append(ScrapingEngine.REQUESTS_HTML)
            
        # Colly and Crawlee style are built-in
        available.extend([
            ScrapingEngine.COLLY_STYLE,
            ScrapingEngine.CRAWLEE_STYLE
        ])
        
        return available
        
    def add_authorized_domain(self, domain: str):
        """Lägg till auktoriserad domän för scraping"""
        self.authorized_domains.add(domain.lower())
        logger.info(f"✅ Added authorized domain för scraping: {domain}")
        
    def _is_domain_authorized(self, url: str) -> bool:
        """Kontrollera om domän är auktoriserad för scraping"""
        domain = urlparse(url).netloc.lower()
        
        if domain in self.authorized_domains:
            return True
            
        for auth_domain in self.authorized_domains:
            if domain.endswith(f".{auth_domain}"):
                return True
                
        return False
        
    async def create_scraping_job(self, job_config: Dict[str, Any]) -> str:
        """Skapa nytt scraping job"""
        
        if not self.initialized:
            await self.initialize()
            
        # Validate authorized domains
        start_urls = job_config.get('start_urls', [])
        for url in start_urls:
            if not self._is_domain_authorized(url):
                error_msg = f"🚫 Domain not authorized för scraping: {url}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
        # Generate job ID
        job_id = f"job_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Create scraping job
        job = ScrapingJob(
            job_id=job_id,
            name=job_config.get('name', f'Scraping Job {job_id}'),
            start_urls=start_urls,
            rules=self._parse_scraping_rules(job_config.get('rules', [])),
            engine=ScrapingEngine(job_config.get('engine', 'beautifulsoup')),
            strategy=ScrapingStrategy(job_config.get('strategy', 'breadth_first')),
            max_pages=job_config.get('max_pages'),
            max_depth=job_config.get('max_depth'),
            concurrency=job_config.get('concurrency', 10),
            delay_range=tuple(job_config.get('delay_range', [1.0, 3.0])),
            user_agents=job_config.get('user_agents', self.user_agents),
            proxies=job_config.get('proxies', []),
            custom_settings=job_config.get('custom_settings', {})
        )
        
        self.active_jobs[job_id] = job
        self.job_results[job_id] = []
        self.job_status[job_id] = "created"
        
        self.stats["total_jobs_started"] += 1
        self.stats["by_engine"][job.engine.value]["jobs"] += 1
        self.stats["by_strategy"][job.strategy.value]["jobs"] += 1
        
        logger.info(f"✅ Created scraping job: {job_id} ({job.engine.value})")
        return job_id
        
    def _parse_scraping_rules(self, rules_config: List[Dict[str, Any]]) -> List[ScrapingRule]:
        """Parse scraping rules från configuration"""
        rules = []
        
        for rule_config in rules_config:
            rule = ScrapingRule(
                name=rule_config.get('name', 'default'),
                url_pattern=rule_config.get('url_pattern', '.*'),
                extraction_rules=rule_config.get('extraction_rules', {}),
                follow_links=rule_config.get('follow_links', True),
                callback=rule_config.get('callback'),
                priority=rule_config.get('priority', 0),
                allowed_domains=rule_config.get('allowed_domains', []),
                denied_paths=rule_config.get('denied_paths', []),
                custom_headers=rule_config.get('custom_headers', {}),
                rate_limit=rule_config.get('rate_limit'),
                javascript_required=rule_config.get('javascript_required', False),
                wait_for_element=rule_config.get('wait_for_element'),
                scroll_to_bottom=rule_config.get('scroll_to_bottom', False),
                take_screenshot=rule_config.get('take_screenshot', False),
                pagination=rule_config.get('pagination')
            )
            rules.append(rule)
            
        return rules
        
    async def start_scraping_job(self, job_id: str) -> bool:
        """Starta scraping job"""
        
        job = self.active_jobs.get(job_id)
        if not job:
            logger.error(f"❌ Job {job_id} not found")
            return False
            
        if self.job_status[job_id] != "created":
            logger.error(f"❌ Job {job_id} redan startad eller avslutad")
            return False
            
        try:
            self.job_status[job_id] = "running"
            logger.info(f"🚀 Starting scraping job: {job_id}")
            
            # Start job based on engine
            if job.engine == ScrapingEngine.SCRAPY:
                await self._run_scrapy_job(job)
            elif job.engine == ScrapingEngine.PLAYWRIGHT:
                await self._run_playwright_job(job)
            elif job.engine == ScrapingEngine.REQUESTS_HTML:
                await self._run_requests_html_job(job)
            elif job.engine == ScrapingEngine.COLLY_STYLE:
                await self._run_colly_style_job(job)
            elif job.engine == ScrapingEngine.CRAWLEE_STYLE:
                await self._run_crawlee_style_job(job)
            else:  # BEAUTIFULSOUP or CUSTOM_ASYNC
                await self._run_beautifulsoup_job(job)
                
            self.job_status[job_id] = "completed"
            self.stats["jobs_completed"] += 1
            
            logger.info(f"✅ Scraping job completed: {job_id} ({len(self.job_results[job_id])} items)")
            return True
            
        except Exception as e:
            self.job_status[job_id] = "failed"
            self.stats["jobs_failed"] += 1
            logger.error(f"❌ Scraping job failed: {job_id} - {str(e)}")
            return False
            
    async def _run_beautifulsoup_job(self, job: ScrapingJob):
        """Run scraping job med BeautifulSoup + aiohttp"""
        
        visited_urls = set()
        url_queue = job.start_urls.copy()
        pages_scraped = 0
        
        # Create semaphore för concurrency control
        semaphore = asyncio.Semaphore(job.concurrency)
        
        async def scrape_url(url: str, depth: int = 0):
            nonlocal pages_scraped
            
            if pages_scraped >= (job.max_pages or float('inf')):
                return
                
            if depth > (job.max_depth or float('inf')):
                return
                
            if url in visited_urls:
                return
                
            visited_urls.add(url)
            
            async with semaphore:
                try:
                    # Rate limiting
                    await self._apply_rate_limit(url, job)
                    
                    # Make request
                    start_time = time.time()
                    headers = {'User-Agent': random.choice(job.user_agents or self.user_agents)}
                    
                    async with self.aiohttp_session.get(url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()
                            response_time = time.time() - start_time
                            
                            # Parse with BeautifulSoup
                            soup = BeautifulSoup(content, 'lxml' if 'lxml' in str(BEAUTIFULSOUP_AVAILABLE) else 'html.parser')
                            
                            # Extract data
                            extracted_data = await self._extract_data_with_beautifulsoup(soup, job.rules, url)
                            
                            # Find links
                            links = self._extract_links(soup, url)
                            
                            # Create scraped item
                            item = ScrapedItem(
                                url=url,
                                data=extracted_data,
                                metadata={'depth': depth, 'links_count': len(links)},
                                rule_name=job.rules[0].name if job.rules else None,
                                engine_used=ScrapingEngine.BEAUTIFULSOUP,
                                response_time=response_time,
                                status_code=response.status,
                                links_found=links
                            )
                            
                            self.job_results[job.job_id].append(item)
                            pages_scraped += 1
                            
                            # Add new URLs to queue
                            for link in links:
                                if link not in visited_urls and len(url_queue) < 1000:  # Limit queue size
                                    url_queue.append(link)
                                    
                            self.stats["total_pages_scraped"] += 1
                            self.stats["by_engine"][job.engine.value]["pages"] += 1
                            
                            logger.debug(f"✅ Scraped: {url} ({response_time:.2f}s)")
                            
                        else:
                            logger.warning(f"⚠️ HTTP {response.status} för {url}")
                            
                except Exception as e:
                    logger.error(f"❌ Error scraping {url}: {str(e)}")
                    self.stats["total_errors"] += 1
                    
        # Process URLs in queue
        tasks = []
        for url in url_queue[:job.concurrency]:
            task = asyncio.create_task(scrape_url(url))
            tasks.append(task)
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _extract_data_with_beautifulsoup(self, soup: BeautifulSoup, 
                                             rules: List[ScrapingRule], 
                                             url: str) -> Dict[str, Any]:
        """Extract data från BeautifulSoup med scraping rules"""
        
        extracted_data = {'url': url}
        
        for rule in rules:
            for field_name, extraction_config in rule.extraction_rules.items():
                try:
                    if isinstance(extraction_config, str):
                        # Simple CSS selector
                        elements = soup.select(extraction_config)
                        extracted_data[field_name] = [elem.get_text(strip=True) for elem in elements]
                    elif isinstance(extraction_config, dict):
                        method = extraction_config.get('method', 'css_selector')
                        selector = extraction_config.get('selector', '')
                        
                        if method == 'css_selector':
                            elements = soup.select(selector)
                            if extraction_config.get('attribute'):
                                extracted_data[field_name] = [elem.get(extraction_config['attribute'], '') for elem in elements]
                            else:
                                extracted_data[field_name] = [elem.get_text(strip=True) for elem in elements]
                        elif method == 'xpath':
                            # XPath not directly supported in BeautifulSoup, use CSS equivalent
                            logger.warning(f"XPath not supported in BeautifulSoup, skipping {field_name}")
                        elif method == 'regex':
                            import re
                            pattern = extraction_config.get('pattern', '')
                            matches = re.findall(pattern, str(soup), re.IGNORECASE)
                            extracted_data[field_name] = matches
                            
                except Exception as e:
                    logger.error(f"❌ Extraction error för {field_name}: {str(e)}")
                    extracted_data[field_name] = None
                    
        return extracted_data
        
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links från page"""
        links = []
        
        for link_elem in soup.find_all('a', href=True):
            href = link_elem['href']
            absolute_url = urljoin(base_url, href)
            
            # Filter out non-HTTP links
            if absolute_url.startswith(('http://', 'https://')):
                links.append(absolute_url)
                
        return list(set(links))  # Remove duplicates
        
    async def _apply_rate_limit(self, url: str, job: ScrapingJob):
        """Apply rate limiting för respectful scraping"""
        domain = urlparse(url).netloc
        
        # Check last request time för domain
        if domain in self.last_request_times:
            time_since_last = datetime.now() - self.last_request_times[domain]
            min_delay = random.uniform(*job.delay_range)
            
            if time_since_last.total_seconds() < min_delay:
                sleep_time = min_delay - time_since_last.total_seconds()
                await asyncio.sleep(sleep_time)
                
        self.last_request_times[domain] = datetime.now()
        
    async def _run_playwright_job(self, job: ScrapingJob):
        """Run scraping job med Playwright browser automation"""
        
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available")
            
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                visited_urls = set()
                pages_scraped = 0
                
                for start_url in job.start_urls:
                    if pages_scraped >= (job.max_pages or float('inf')):
                        break
                        
                    if start_url in visited_urls:
                        continue
                        
                    visited_urls.add(start_url)
                    
                    # Rate limiting
                    await self._apply_rate_limit(start_url, job)
                    
                    start_time = time.time()
                    
                    # Navigate to page
                    await page.goto(start_url, wait_until='load', timeout=job.timeout * 1000)
                    
                    # Wait för specific element if configured
                    for rule in job.rules:
                        if rule.wait_for_element:
                            try:
                                await page.wait_for_selector(rule.wait_for_element, timeout=5000)
                            except Exception:
                                logger.warning(f"⚠️ Wait element not found: {rule.wait_for_element}")
                                
                        if rule.scroll_to_bottom:
                            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            await asyncio.sleep(1)
                            
                    response_time = time.time() - start_time
                    
                    # Extract data
                    extracted_data = await self._extract_data_with_playwright(page, job.rules, start_url)
                    
                    # Extract links
                    links = await page.evaluate("""
                        () => Array.from(document.links).map(link => link.href)
                    """)
                    
                    # Take screenshot if requested
                    screenshot_path = None
                    for rule in job.rules:
                        if rule.take_screenshot:
                            screenshot_path = f"screenshot_{job.job_id}_{pages_scraped}.png"
                            await page.screenshot(path=screenshot_path)
                            
                    # Create scraped item
                    item = ScrapedItem(
                        url=start_url,
                        data=extracted_data,
                        metadata={'screenshot': screenshot_path},
                        engine_used=ScrapingEngine.PLAYWRIGHT,
                        response_time=response_time,
                        links_found=links or []
                    )
                    
                    self.job_results[job.job_id].append(item)
                    pages_scraped += 1
                    
                    self.stats["total_pages_scraped"] += 1
                    self.stats["by_engine"][job.engine.value]["pages"] += 1
                    
                    logger.debug(f"✅ Playwright scraped: {start_url}")
                    
            finally:
                await browser.close()
                
    async def _extract_data_with_playwright(self, page: Page, 
                                          rules: List[ScrapingRule], 
                                          url: str) -> Dict[str, Any]:
        """Extract data från Playwright page"""
        
        extracted_data = {'url': url}
        
        for rule in rules:
            for field_name, extraction_config in rule.extraction_rules.items():
                try:
                    if isinstance(extraction_config, str):
                        # Simple CSS selector
                        elements = await page.query_selector_all(extraction_config)
                        values = []
                        for element in elements:
                            text = await element.text_content()
                            if text:
                                values.append(text.strip())
                        extracted_data[field_name] = values
                        
                    elif isinstance(extraction_config, dict):
                        method = extraction_config.get('method', 'css_selector')
                        selector = extraction_config.get('selector', '')
                        
                        if method == 'css_selector':
                            elements = await page.query_selector_all(selector)
                            values = []
                            for element in elements:
                                if extraction_config.get('attribute'):
                                    value = await element.get_attribute(extraction_config['attribute'])
                                else:
                                    value = await element.text_content()
                                if value:
                                    values.append(value.strip())
                            extracted_data[field_name] = values
                            
                except Exception as e:
                    logger.error(f"❌ Playwright extraction error för {field_name}: {str(e)}")
                    extracted_data[field_name] = None
                    
        return extracted_data
        
    async def _run_colly_style_job(self, job: ScrapingJob):
        """Run Colly-inspired scraping job"""
        
        # Colly-style collector pattern
        class Collector:
            def __init__(self, job: ScrapingJob):
                self.job = job
                self.visited = set()
                self.results = []
                
            async def visit(self, url: str):
                if url in self.visited:
                    return
                    
                self.visited.add(url)
                
                try:
                    headers = {'User-Agent': random.choice(job.user_agents or self.user_agents)}
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                content = await response.text()
                                soup = BeautifulSoup(content, 'html.parser')
                                
                                # Extract data
                                data = {}
                                for rule in job.rules:
                                    for field, selector in rule.extraction_rules.items():
                                        if isinstance(selector, str):
                                            elements = soup.select(selector)
                                            data[field] = [elem.get_text(strip=True) for elem in elements]
                                            
                                item = ScrapedItem(
                                    url=url,
                                    data=data,
                                    engine_used=ScrapingEngine.COLLY_STYLE
                                )
                                
                                self.results.append(item)
                                
                                # Find more links
                                links = [urljoin(url, a.get('href', '')) for a in soup.find_all('a', href=True)]
                                for link in links[:5]:  # Limit to prevent infinite crawling
                                    if self._is_domain_authorized(link):
                                        await self.visit(link)
                                        
                except Exception as e:
                    logger.error(f"Colly-style error: {str(e)}")
                    
        collector = Collector(job)
        
        # Visit all start URLs
        for start_url in job.start_urls:
            await collector.visit(start_url)
            
        # Add results
        self.job_results[job.job_id].extend(collector.results)
        self.stats["total_pages_scraped"] += len(collector.results)
        
    async def _run_crawlee_style_job(self, job: ScrapingJob):
        """Run Crawlee-inspired scraping job"""
        
        # Crawlee-style request queue och processing
        request_queue = job.start_urls.copy()
        processed = set()
        
        while request_queue and len(processed) < (job.max_pages or 100):
            url = request_queue.pop(0)
            
            if url in processed:
                continue
                
            processed.add(url)
            
            try:
                # Rate limiting
                await self._apply_rate_limit(url, job)
                
                # Process request
                headers = {'User-Agent': random.choice(job.user_agents or self.user_agents)}
                
                async with self.aiohttp_session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract data using rules
                        data = {}
                        for rule in job.rules:
                            for field, extraction_rule in rule.extraction_rules.items():
                                if isinstance(extraction_rule, str):
                                    elements = soup.select(extraction_rule)
                                    data[field] = [elem.get_text(strip=True) for elem in elements[:10]]
                                    
                        # Create item
                        item = ScrapedItem(
                            url=url,
                            data=data,
                            engine_used=ScrapingEngine.CRAWLEE_STYLE,
                            status_code=response.status
                        )
                        
                        self.job_results[job.job_id].append(item)
                        
                        # Add new URLs if following links
                        for rule in job.rules:
                            if rule.follow_links:
                                links = [urljoin(url, a.get('href', '')) for a in soup.find_all('a', href=True)]
                                for link in links[:10]:  # Limit new URLs
                                    if link not in processed and len(request_queue) < 100:
                                        if self._is_domain_authorized(link):
                                            request_queue.append(link)
                                            
                        logger.debug(f"✅ Crawlee-style processed: {url}")
                        
            except Exception as e:
                logger.error(f"❌ Crawlee-style error för {url}: {str(e)}")
                
        self.stats["total_pages_scraped"] += len(processed)
        
    async def _run_scrapy_job(self, job: ScrapingJob):
        """Run Scrapy-based scraping job (placeholder)"""
        logger.warning("Scrapy integration not fully implemented, using fallback")
        await self._run_beautifulsoup_job(job)
        
    async def _run_requests_html_job(self, job: ScrapingJob):
        """Run Requests-HTML based job (placeholder)"""
        logger.warning("Requests-HTML integration not fully implemented, using fallback") 
        await self._run_beautifulsoup_job(job)
        
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Hämta status för scraping job"""
        
        job = self.active_jobs.get(job_id)
        if not job:
            return {"error": f"Job {job_id} not found"}
            
        results_count = len(self.job_results.get(job_id, []))
        
        return {
            "job_id": job_id,
            "status": self.job_status.get(job_id, "unknown"),
            "results_count": results_count,
            "job_config": {
                "name": job.name,
                "engine": job.engine.value,
                "strategy": job.strategy.value,
                "start_urls_count": len(job.start_urls),
                "rules_count": len(job.rules)
            },
            "last_updated": datetime.now().isoformat()
        }
        
    async def get_job_results(self, job_id: str, format: str = "json") -> Union[List[Dict], str]:
        """Hämta resultat från scraping job"""
        
        results = self.job_results.get(job_id, [])
        
        if format.lower() == "json":
            return [
                {
                    "url": item.url,
                    "data": item.data,
                    "metadata": item.metadata,
                    "extracted_at": item.extracted_at.isoformat(),
                    "engine_used": item.engine_used.value if item.engine_used else None,
                    "response_time": item.response_time,
                    "status_code": item.status_code,
                    "error": item.error,
                    "links_found_count": len(item.links_found)
                }
                for item in results
            ]
        elif format.lower() == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if results:
                writer = csv.DictWriter(output, fieldnames=results[0].data.keys())
                writer.writeheader()
                for item in results:
                    writer.writerow(item.data)
                    
            return output.getvalue()
        else:
            return json.dumps({"error": f"Unsupported format: {format}"})
            
    async def stop_job(self, job_id: str) -> bool:
        """Stoppa running scraping job"""
        
        if job_id not in self.active_jobs:
            return False
            
        if self.job_status.get(job_id) == "running":
            self.job_status[job_id] = "stopped"
            logger.info(f"⏹️ Stopped scraping job: {job_id}")
            return True
            
        return False
        
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Hämta enhanced scraping statistics"""
        
        return {
            "total_jobs_started": self.stats["total_jobs_started"],
            "jobs_completed": self.stats["jobs_completed"],
            "jobs_failed": self.stats["jobs_failed"],
            "active_jobs": len([job_id for job_id, status in self.job_status.items() if status == "running"]),
            "total_pages_scraped": self.stats["total_pages_scraped"],
            "total_items_extracted": sum(len(results) for results in self.job_results.values()),
            "by_engine": self.stats["by_engine"],
            "by_strategy": self.stats["by_strategy"],
            "total_errors": self.stats["total_errors"],
            "content_duplicates": self.stats["content_duplicates"],
            "domains_scraped": list(self.stats["domains_scraped"]),
            "authorized_domains": list(self.authorized_domains),
            "available_engines": [engine.value for engine in self.available_engines],
            "average_response_time": self.stats["average_response_time"]
        }
        
    async def cleanup(self):
        """Cleanup Enhanced Scraping Framework adapter"""
        logger.info("🧹 Cleaning up Enhanced Scraping Framework Adapter")
        
        # Stop alla running jobs
        for job_id, status in self.job_status.items():
            if status == "running":
                await self.stop_job(job_id)
                
        # Close aiohttp session
        if self.aiohttp_session:
            await self.aiohttp_session.close()
            
        # Close Requests-HTML session
        if self.requests_html_session:
            await self.requests_html_session.close()
            
        # Close Playwright browsers
        for browser in self.playwright_browsers.values():
            await browser.close()
            
        self.active_jobs.clear()
        self.job_results.clear()
        self.job_status.clear()
        self.engine_sessions.clear()
        self.authorized_domains.clear()
        self.stats.clear()
        self.initialized = False
        logger.info("✅ Enhanced Scraping Framework Adapter cleanup completed")
