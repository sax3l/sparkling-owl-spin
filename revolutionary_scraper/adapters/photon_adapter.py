#!/usr/bin/env python3
"""
Photon Integration - Revolutionary Ultimate System v4.0
Advanced web crawler and URL discovery system
"""

import asyncio
import logging
import time
import json
import re
import hashlib
from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from urllib.parse import urljoin, urlparse, parse_qs
from pathlib import Path
import tempfile
import subprocess
import shutil

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp
    import aiofiles
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    from bs4 import BeautifulSoup, Comment
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CrawlResult:
    """Container for crawl results"""
    url: str
    title: Optional[str] = None
    status_code: int = 0
    content_type: Optional[str] = None
    content_length: int = 0
    response_time: float = 0.0
    redirect_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: float = 0.0
    depth: int = 0
    parent_url: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

@dataclass
class ExtractedData:
    """Container for extracted data from pages"""
    urls: Set[str]
    external_urls: Set[str]
    emails: Set[str]
    phone_numbers: Set[str]
    social_media: Set[str]
    documents: Set[str]  # PDFs, docs, etc.
    images: Set[str]
    scripts: Set[str]
    stylesheets: Set[str]
    forms: List[Dict[str, Any]]
    comments: List[str]
    meta_data: Dict[str, str]
    technology_stack: Set[str]

@dataclass
class PhotonConfig:
    """Configuration for Photon crawler"""
    enabled: bool = True
    start_urls: List[str] = None
    max_depth: int = 2
    max_urls: int = 100
    max_threads: int = 10
    delay: float = 0.1
    timeout: int = 30
    retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    follow_redirects: bool = True
    respect_robots: bool = True
    allowed_domains: List[str] = None
    excluded_domains: List[str] = None
    allowed_extensions: List[str] = None  # e.g., ['.html', '.php', '.asp']
    excluded_extensions: List[str] = None  # e.g., ['.jpg', '.png', '.css', '.js']
    include_external_urls: bool = True
    extract_emails: bool = True
    extract_phones: bool = True
    extract_social: bool = True
    extract_documents: bool = True
    extract_images: bool = True
    extract_scripts: bool = True
    extract_comments: bool = True
    extract_metadata: bool = True
    detect_technologies: bool = True
    output_format: str = 'json'  # json, csv, txt
    debug: bool = False

class URLExtractor:
    """Advanced URL extraction and filtering"""
    
    def __init__(self, config: PhotonConfig):
        self.config = config
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}')
        self.social_patterns = {
            'facebook': re.compile(r'(?:https?://)?(?:www\.)?facebook\.com/[A-Za-z0-9._-]+'),
            'twitter': re.compile(r'(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/[A-Za-z0-9._-]+'),
            'linkedin': re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/(?:in|company)/[A-Za-z0-9._-]+'),
            'instagram': re.compile(r'(?:https?://)?(?:www\.)?instagram\.com/[A-Za-z0-9._-]+'),
            'youtube': re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/[A-Za-z0-9._-]+'),
            'github': re.compile(r'(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9._-]+')
        }
        
    def extract_from_html(self, html: str, base_url: str) -> ExtractedData:
        """Extract all data from HTML content"""
        
        if not BS4_AVAILABLE:
            logger.warning("BeautifulSoup not available, limited extraction")
            return self._extract_basic(html, base_url)
            
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            return ExtractedData(
                urls=self._extract_urls(soup, base_url),
                external_urls=self._extract_external_urls(soup, base_url),
                emails=self._extract_emails(html),
                phone_numbers=self._extract_phones(html),
                social_media=self._extract_social_media(html),
                documents=self._extract_documents(soup, base_url),
                images=self._extract_images(soup, base_url),
                scripts=self._extract_scripts(soup, base_url),
                stylesheets=self._extract_stylesheets(soup, base_url),
                forms=self._extract_forms(soup),
                comments=self._extract_comments(soup),
                meta_data=self._extract_metadata(soup),
                technology_stack=self._detect_technologies(html, soup)
            )
            
        except Exception as e:
            logger.error(f"❌ HTML extraction failed: {str(e)}")
            return self._extract_basic(html, base_url)
            
    def _extract_urls(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract internal URLs"""
        urls = set()
        
        # Extract from various elements
        for element in soup.find_all(['a', 'link']):
            href = element.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if self._is_valid_url(full_url, base_url):
                    urls.add(full_url)
                    
        # Extract from forms
        for form in soup.find_all('form'):
            action = form.get('action')
            if action:
                full_url = urljoin(base_url, action)
                if self._is_valid_url(full_url, base_url):
                    urls.add(full_url)
                    
        return urls
        
    def _extract_external_urls(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract external URLs"""
        if not self.config.include_external_urls:
            return set()
            
        external_urls = set()
        base_domain = urlparse(base_url).netloc
        
        for element in soup.find_all(['a', 'link']):
            href = element.get('href')
            if href:
                full_url = urljoin(base_url, href)
                url_domain = urlparse(full_url).netloc
                
                if url_domain and url_domain != base_domain:
                    external_urls.add(full_url)
                    
        return external_urls
        
    def _extract_emails(self, html: str) -> Set[str]:
        """Extract email addresses"""
        if not self.config.extract_emails:
            return set()
            
        return set(self.email_pattern.findall(html))
        
    def _extract_phones(self, html: str) -> Set[str]:
        """Extract phone numbers"""
        if not self.config.extract_phones:
            return set()
            
        return set(self.phone_pattern.findall(html))
        
    def _extract_social_media(self, html: str) -> Set[str]:
        """Extract social media URLs"""
        if not self.config.extract_social:
            return set()
            
        social_urls = set()
        
        for platform, pattern in self.social_patterns.items():
            matches = pattern.findall(html)
            social_urls.update(matches)
            
        return social_urls
        
    def _extract_documents(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract document URLs (PDF, DOC, etc.)"""
        if not self.config.extract_documents:
            return set()
            
        documents = set()
        doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf']
        
        for element in soup.find_all(['a', 'link']):
            href = element.get('href')
            if href:
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                
                if any(parsed_url.path.lower().endswith(ext) for ext in doc_extensions):
                    documents.add(full_url)
                    
        return documents
        
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract image URLs"""
        if not self.config.extract_images:
            return set()
            
        images = set()
        
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                full_url = urljoin(base_url, src)
                images.add(full_url)
                
        return images
        
    def _extract_scripts(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract JavaScript URLs"""
        if not self.config.extract_scripts:
            return set()
            
        scripts = set()
        
        for script in soup.find_all('script'):
            src = script.get('src')
            if src:
                full_url = urljoin(base_url, src)
                scripts.add(full_url)
                
        return scripts
        
    def _extract_stylesheets(self, soup: BeautifulSoup, base_url: str) -> Set[str]:
        """Extract CSS URLs"""
        stylesheets = set()
        
        for link in soup.find_all('link'):
            if link.get('rel') == ['stylesheet'] or 'stylesheet' in (link.get('rel') or []):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    stylesheets.add(full_url)
                    
        return stylesheets
        
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action'),
                'method': form.get('method', 'GET').upper(),
                'inputs': []
            }
            
            for input_elem in form.find_all(['input', 'textarea', 'select']):
                input_data = {
                    'name': input_elem.get('name'),
                    'type': input_elem.get('type', 'text'),
                    'value': input_elem.get('value'),
                    'required': input_elem.has_attr('required')
                }
                form_data['inputs'].append(input_data)
                
            forms.append(form_data)
            
        return forms
        
    def _extract_comments(self, soup: BeautifulSoup) -> List[str]:
        """Extract HTML comments"""
        if not self.config.extract_comments:
            return []
            
        comments = []
        
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment_text = comment.strip()
            if comment_text:
                comments.append(comment_text)
                
        return comments
        
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags and other metadata"""
        if not self.config.extract_metadata:
            return {}
            
        metadata = {}
        
        # Title
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text().strip()
            
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
                
        return metadata
        
    def _detect_technologies(self, html: str, soup: BeautifulSoup) -> Set[str]:
        """Detect web technologies"""
        if not self.config.detect_technologies:
            return set()
            
        technologies = set()
        html_lower = html.lower()
        
        # Framework detection
        if 'react' in html_lower or 'reactdom' in html_lower:
            technologies.add('React')
        if 'angular' in html_lower or 'ng-' in html_lower:
            technologies.add('Angular')
        if 'vue' in html_lower or 'v-' in html_lower:
            technologies.add('Vue.js')
        if 'jquery' in html_lower:
            technologies.add('jQuery')
        if 'bootstrap' in html_lower:
            technologies.add('Bootstrap')
        if 'wordpress' in html_lower or 'wp-content' in html_lower:
            technologies.add('WordPress')
        if 'drupal' in html_lower:
            technologies.add('Drupal')
        
        # Server technologies
        if 'x-powered-by' in html_lower:
            technologies.add('X-Powered-By detected')
        if 'php' in html_lower or '.php' in html_lower:
            technologies.add('PHP')
        if 'asp.net' in html_lower or 'aspnet' in html_lower:
            technologies.add('ASP.NET')
        if 'jsp' in html_lower or '.jsp' in html_lower:
            technologies.add('JSP')
            
        # Analytics and tracking
        if 'google-analytics' in html_lower or 'gtag' in html_lower:
            technologies.add('Google Analytics')
        if 'googletagmanager' in html_lower:
            technologies.add('Google Tag Manager')
        if 'facebook.com/tr' in html_lower:
            technologies.add('Facebook Pixel')
            
        return technologies
        
    def _is_valid_url(self, url: str, base_url: str) -> bool:
        """Check if URL should be included"""
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False
                
            # Check domains
            if self.config.allowed_domains:
                if parsed.netloc not in self.config.allowed_domains:
                    return False
                    
            if self.config.excluded_domains:
                if parsed.netloc in self.config.excluded_domains:
                    return False
                    
            # Check extensions
            if self.config.allowed_extensions:
                if not any(parsed.path.lower().endswith(ext) for ext in self.config.allowed_extensions):
                    return False
                    
            if self.config.excluded_extensions:
                if any(parsed.path.lower().endswith(ext) for ext in self.config.excluded_extensions):
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def _extract_basic(self, html: str, base_url: str) -> ExtractedData:
        """Basic extraction without BeautifulSoup"""
        
        # Simple URL extraction with regex
        url_pattern = re.compile(r'href=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
        raw_urls = url_pattern.findall(html)
        
        urls = set()
        for url in raw_urls:
            full_url = urljoin(base_url, url)
            if self._is_valid_url(full_url, base_url):
                urls.add(full_url)
                
        return ExtractedData(
            urls=urls,
            external_urls=set(),
            emails=self._extract_emails(html),
            phone_numbers=self._extract_phones(html),
            social_media=self._extract_social_media(html),
            documents=set(),
            images=set(),
            scripts=set(),
            stylesheets=set(),
            forms=[],
            comments=[],
            meta_data={},
            technology_stack=set()
        )

class PhotonCrawler:
    """
    Advanced web crawler inspired by Photon.
    
    Features:
    - Multi-threaded crawling
    - Intelligent URL discovery
    - Comprehensive data extraction  
    - Technology stack detection
    - Robots.txt compliance
    - Rate limiting and politeness
    - Duplicate URL detection
    - Export in multiple formats
    """
    
    def __init__(self, config: PhotonConfig):
        self.config = config
        self.extractor = URLExtractor(config)
        self.crawled_urls = set()
        self.url_queue = deque()
        self.results = []
        self.extracted_data = defaultdict(lambda: ExtractedData(
            urls=set(), external_urls=set(), emails=set(), phone_numbers=set(),
            social_media=set(), documents=set(), images=set(), scripts=set(),
            stylesheets=set(), forms=[], comments=[], meta_data={}, technology_stack=set()
        ))
        self.robots_cache = {}
        self.session = None
        
        self._stats = {
            'urls_crawled': 0,
            'urls_found': 0,
            'emails_found': 0,
            'documents_found': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not available. Install with: pip install requests")
        
    async def initialize(self):
        """Initialize crawler"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing Photon crawler...")
        
        # Setup session
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        logger.info("✅ Photon crawler initialized")
        
    async def crawl(self, start_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Start crawling from given URLs.
        
        Returns comprehensive crawl results with extracted data.
        """
        
        if not self.config.enabled:
            return {'success': False, 'error': 'Crawler disabled'}
            
        urls_to_crawl = start_urls or self.config.start_urls
        
        if not urls_to_crawl:
            return {'success': False, 'error': 'No start URLs provided'}
            
        logger.info(f"🕷️ Starting crawl with {len(urls_to_crawl)} URLs...")
        self._stats['start_time'] = time.time()
        
        # Initialize queue
        for url in urls_to_crawl:
            self.url_queue.append((url, 0))  # (url, depth)
            
        try:
            # Crawl with threading
            await self._crawl_threaded()
            
            # Compile results
            results = self._compile_results()
            
            self._stats['end_time'] = time.time()
            crawl_time = self._stats['end_time'] - self._stats['start_time']
            
            logger.info(f"✅ Crawl completed in {crawl_time:.2f}s")
            logger.info(f"📊 Found {self._stats['urls_found']} URLs, {self._stats['emails_found']} emails")
            
            return {
                'success': True,
                'crawl_time': crawl_time,
                'stats': self._stats.copy(),
                'results': results,
                'method': 'photon-crawler'
            }
            
        except Exception as e:
            logger.error(f"❌ Crawl failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'stats': self._stats.copy(),
                'method': 'photon-crawler'
            }
            
    async def _crawl_threaded(self):
        """Crawl URLs using thread pool"""
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            futures = []
            
            while self.url_queue and len(self.crawled_urls) < self.config.max_urls:
                # Submit batch of URLs
                batch_size = min(self.config.max_threads, len(self.url_queue))
                
                for _ in range(batch_size):
                    if not self.url_queue:
                        break
                        
                    url, depth = self.url_queue.popleft()
                    
                    if url not in self.crawled_urls and depth <= self.config.max_depth:
                        future = executor.submit(self._crawl_single_url, url, depth)
                        futures.append(future)
                        
                # Process completed requests
                for future in as_completed(futures):
                    try:
                        url, depth, success = future.result()
                        
                        if success and depth < self.config.max_depth:
                            # Add discovered URLs to queue
                            extracted = self.extracted_data[url]
                            for new_url in extracted.urls:
                                if (new_url not in self.crawled_urls and 
                                    len(self.crawled_urls) < self.config.max_urls):
                                    self.url_queue.append((new_url, depth + 1))
                                    
                    except Exception as e:
                        logger.error(f"❌ Future processing error: {str(e)}")
                        self._stats['errors'] += 1
                        
                futures.clear()
                
                # Rate limiting
                if self.config.delay > 0:
                    time.sleep(self.config.delay)
                    
    def _crawl_single_url(self, url: str, depth: int) -> Tuple[str, int, bool]:
        """Crawl single URL"""
        
        if url in self.crawled_urls:
            return url, depth, False
            
        try:
            # Check robots.txt if required
            if self.config.respect_robots and not self._can_fetch(url):
                logger.debug(f"🤖 Robots.txt disallows: {url}")
                return url, depth, False
                
            # Make request
            start_time = time.time()
            
            response = self.session.get(
                url,
                timeout=self.config.timeout,
                allow_redirects=self.config.follow_redirects
            )
            
            response_time = time.time() - start_time
            
            # Record URL as crawled
            self.crawled_urls.add(url)
            self._stats['urls_crawled'] += 1
            
            # Create crawl result
            result = CrawlResult(
                url=url,
                status_code=response.status_code,
                content_type=response.headers.get('content-type'),
                content_length=len(response.content),
                response_time=response_time,
                depth=depth
            )
            
            # Handle redirects
            if response.url != url:
                result.redirect_url = response.url
                
            # Extract data if HTML
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    try:
                        extracted = self.extractor.extract_from_html(response.text, url)
                        self.extracted_data[url] = extracted
                        
                        # Update stats
                        self._stats['urls_found'] += len(extracted.urls)
                        self._stats['emails_found'] += len(extracted.emails)
                        self._stats['documents_found'] += len(extracted.documents)
                        
                        # Extract title
                        if extracted.meta_data.get('title'):
                            result.title = extracted.meta_data['title']
                            
                    except Exception as e:
                        logger.error(f"❌ Data extraction failed for {url}: {str(e)}")
                        result.error = str(e)
                        self._stats['errors'] += 1
                        
            else:
                result.error = f"HTTP {response.status_code}"
                self._stats['errors'] += 1
                
            self.results.append(result)
            
            logger.debug(f"✅ Crawled: {url} ({response.status_code}) in {response_time:.2f}s")
            
            return url, depth, True
            
        except Exception as e:
            logger.error(f"❌ Failed to crawl {url}: {str(e)}")
            
            # Record error result
            result = CrawlResult(
                url=url,
                error=str(e),
                depth=depth
            )
            
            self.results.append(result)
            self.crawled_urls.add(url)
            self._stats['errors'] += 1
            
            return url, depth, False
            
    def _can_fetch(self, url: str) -> bool:
        """Check robots.txt compliance"""
        
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            if base_url not in self.robots_cache:
                robots_url = urljoin(base_url, '/robots.txt')
                
                try:
                    response = self.session.get(robots_url, timeout=10)
                    if response.status_code == 200:
                        self.robots_cache[base_url] = response.text
                    else:
                        self.robots_cache[base_url] = ""
                except Exception:
                    self.robots_cache[base_url] = ""
                    
            robots_content = self.robots_cache[base_url]
            
            # Simple robots.txt parsing
            if robots_content:
                lines = robots_content.split('\n')
                current_user_agent = None
                disallow_rules = []
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('User-agent:'):
                        user_agent = line.split(':', 1)[1].strip()
                        if user_agent == '*' or user_agent.lower() == 'photon':
                            current_user_agent = user_agent
                    elif line.startswith('Disallow:') and current_user_agent:
                        disallow_path = line.split(':', 1)[1].strip()
                        disallow_rules.append(disallow_path)
                        
                # Check if URL path is disallowed
                url_path = parsed_url.path or '/'
                for rule in disallow_rules:
                    if rule and url_path.startswith(rule):
                        return False
                        
            return True
            
        except Exception as e:
            logger.debug(f"Robots.txt check failed: {str(e)}")
            return True  # Allow if check fails
            
    def _compile_results(self) -> Dict[str, Any]:
        """Compile comprehensive results"""
        
        # Aggregate all extracted data
        all_urls = set()
        all_external_urls = set()
        all_emails = set()
        all_phones = set()
        all_social = set()
        all_documents = set()
        all_images = set()
        all_scripts = set()
        all_stylesheets = set()
        all_forms = []
        all_comments = []
        all_technologies = set()
        
        for extracted in self.extracted_data.values():
            all_urls.update(extracted.urls)
            all_external_urls.update(extracted.external_urls)
            all_emails.update(extracted.emails)
            all_phones.update(extracted.phone_numbers)
            all_social.update(extracted.social_media)
            all_documents.update(extracted.documents)
            all_images.update(extracted.images)
            all_scripts.update(extracted.scripts)
            all_stylesheets.update(extracted.stylesheets)
            all_forms.extend(extracted.forms)
            all_comments.extend(extracted.comments)
            all_technologies.update(extracted.technology_stack)
            
        return {
            'crawl_results': [asdict(result) for result in self.results],
            'discovered_data': {
                'urls': {
                    'internal': list(all_urls),
                    'external': list(all_external_urls),
                    'total_internal': len(all_urls),
                    'total_external': len(all_external_urls)
                },
                'contacts': {
                    'emails': list(all_emails),
                    'phone_numbers': list(all_phones),
                    'total_emails': len(all_emails),
                    'total_phones': len(all_phones)
                },
                'social_media': {
                    'urls': list(all_social),
                    'total': len(all_social)
                },
                'resources': {
                    'documents': list(all_documents),
                    'images': list(all_images),
                    'scripts': list(all_scripts),
                    'stylesheets': list(all_stylesheets),
                    'total_documents': len(all_documents),
                    'total_images': len(all_images),
                    'total_scripts': len(all_scripts),
                    'total_stylesheets': len(all_stylesheets)
                },
                'forms': all_forms,
                'comments': all_comments,
                'technologies': list(all_technologies),
                'metadata_samples': list(self.extracted_data.values())[:5] if self.extracted_data else []
            },
            'summary': {
                'total_pages_crawled': len(self.results),
                'successful_crawls': len([r for r in self.results if r.status_code == 200]),
                'failed_crawls': len([r for r in self.results if r.status_code != 200 or r.error]),
                'unique_domains': len(set(urlparse(r.url).netloc for r in self.results)),
                'average_response_time': sum(r.response_time for r in self.results) / len(self.results) if self.results else 0,
                'total_data_points': (len(all_urls) + len(all_emails) + len(all_phones) + 
                                    len(all_documents) + len(all_images) + len(all_social))
            }
        }

class PhotonAdapter:
    """High-level adapter for Photon crawler integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = PhotonConfig(**config)
        self.crawler = PhotonCrawler(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Photon crawler adapter disabled")
            return
            
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests not available")
            if self.config.enabled:
                raise ImportError("requests package required")
            return
            
        if self.crawler:
            await self.crawler.initialize()
            logger.info("✅ Photon crawler adapter initialized")
        else:
            logger.error("❌ Photon crawler not available")
            
    async def crawl_urls(self, start_urls: List[str], 
                        max_depth: Optional[int] = None,
                        max_urls: Optional[int] = None) -> Dict[str, Any]:
        """
        Crawl URLs and discover resources.
        
        Returns:
        {
            'success': bool,
            'crawl_time': float,
            'discovered_urls': list,
            'emails': list,
            'documents': list,
            'technologies': list,
            'summary': dict
        }
        """
        
        if not self.config.enabled or not self.crawler:
            return {
                'success': False,
                'error': 'Photon crawler is disabled or not available'
            }
            
        try:
            # Override config if specified
            if max_depth is not None:
                self.crawler.config.max_depth = max_depth
            if max_urls is not None:
                self.crawler.config.max_urls = max_urls
                
            result = await self.crawler.crawl(start_urls)
            
            if result['success']:
                discovered_data = result['results']['discovered_data']
                
                return {
                    'success': True,
                    'crawl_time': result['crawl_time'],
                    'discovered_urls': discovered_data['urls']['internal'],
                    'external_urls': discovered_data['urls']['external'],
                    'emails': discovered_data['contacts']['emails'],
                    'phone_numbers': discovered_data['contacts']['phone_numbers'],
                    'documents': discovered_data['resources']['documents'],
                    'images': discovered_data['resources']['images'],
                    'social_media': discovered_data['social_media']['urls'],
                    'technologies': discovered_data['technologies'],
                    'forms': discovered_data['forms'],
                    'summary': result['results']['summary'],
                    'stats': result['stats'],
                    'method': 'photon-crawler'
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"❌ Failed to crawl URLs: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'photon-crawler'
            }
            
    async def discover_urls(self, start_url: str, depth: int = 1) -> Dict[str, Any]:
        """Quick URL discovery from single page"""
        
        if not self.config.enabled or not self.crawler:
            return {'success': False, 'error': 'Photon crawler not available'}
            
        try:
            # Configure for quick discovery
            old_depth = self.crawler.config.max_depth
            old_urls = self.crawler.config.max_urls
            
            self.crawler.config.max_depth = depth
            self.crawler.config.max_urls = 50
            
            result = await self.crawler.crawl([start_url])
            
            # Restore config
            self.crawler.config.max_depth = old_depth
            self.crawler.config.max_urls = old_urls
            
            if result['success']:
                urls_data = result['results']['discovered_data']['urls']
                
                return {
                    'success': True,
                    'discovered_urls': urls_data['internal'],
                    'external_urls': urls_data['external'],
                    'total_internal': urls_data['total_internal'],
                    'total_external': urls_data['total_external'],
                    'method': 'photon-discovery'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'photon-discovery'
            }
            
    async def extract_contacts(self, urls: List[str]) -> Dict[str, Any]:
        """Extract contact information from URLs"""
        
        if not self.config.enabled or not self.crawler:
            return {'success': False, 'error': 'Photon crawler not available'}
            
        try:
            # Configure for contact extraction
            old_depth = self.crawler.config.max_depth
            self.crawler.config.max_depth = 0  # No follow links, just extract from provided URLs
            
            result = await self.crawler.crawl(urls)
            
            # Restore config
            self.crawler.config.max_depth = old_depth
            
            if result['success']:
                contacts_data = result['results']['discovered_data']['contacts']
                social_data = result['results']['discovered_data']['social_media']
                
                return {
                    'success': True,
                    'emails': contacts_data['emails'],
                    'phone_numbers': contacts_data['phone_numbers'],
                    'social_media': social_data['urls'],
                    'total_emails': contacts_data['total_emails'],
                    'total_phones': contacts_data['total_phones'],
                    'total_social': social_data['total'],
                    'method': 'photon-contacts'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'photon-contacts'
            }
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.crawler:
            base_stats['crawler_stats'] = self.crawler._stats.copy()
        else:
            base_stats['crawler_stats'] = {}
            
        return base_stats

# Factory function
def create_photon_adapter(config: Dict[str, Any]) -> PhotonAdapter:
    """Create and configure Photon adapter"""
    return PhotonAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'max_depth': 2,
        'max_urls': 20,
        'delay': 0.5,
        'extract_emails': True,
        'extract_documents': True,
        'detect_technologies': True,
        'debug': True
    }
    
    adapter = create_photon_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Crawl URLs
        result = await adapter.crawl_urls(['http://example.com'], max_depth=1)
        
        if result['success']:
            print(f"✅ Crawl successful: {result['summary']['total_pages_crawled']} pages")
            print(f"Found {len(result['discovered_urls'])} URLs")
            print(f"Found {len(result['emails'])} emails")
            print(f"Found {len(result['documents'])} documents")
            print(f"Technologies: {result['technologies']}")
        else:
            print(f"❌ Crawl failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
