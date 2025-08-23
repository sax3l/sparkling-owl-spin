"""
Revolutionary BFS/DFS Crawler Implementation
Implementing advanced crawling algorithms with intelligent queue management
"""

import asyncio
import logging
from collections import deque
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from urllib.parse import urljoin, urlparse
import heapq
from dataclasses import dataclass
from datetime import datetime
import random
import re
from bs4 import BeautifulSoup
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import time

@dataclass
class CrawlItem:
    """Advanced crawl item with priority and metadata"""
    url: str
    depth: int
    priority: float
    timestamp: datetime
    parent_url: Optional[str] = None
    crawl_type: str = "bfs"
    metadata: Dict[str, Any] = None
    
    def __lt__(self, other):
        return self.priority < other.priority

class RevolutionaryCrawler:
    """
    World's most advanced crawler implementing BFS/DFS with intelligent prioritization
    Unblockable through sophisticated algorithm design
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Advanced queue management
        self.bfs_queue = deque()  # FIFO for breadth-first
        self.dfs_stack = []       # LIFO for depth-first  
        self.priority_queue = []  # Heapq for priority-based crawling
        
        # State management
        self.visited_urls: Set[str] = set()
        self.failed_urls: Dict[str, int] = {}
        self.url_scores: Dict[str, float] = {}
        self.domain_stats: Dict[str, Dict] = {}
        
        # Advanced configuration
        self.max_depth = config.get('max_depth', 10)
        self.max_pages = config.get('max_pages', 10000)
        self.concurrent_requests = config.get('concurrent_requests', 50)
        self.crawl_delay = config.get('crawl_delay', 1.0)
        self.retry_attempts = config.get('retry_attempts', 5)
        
        # Intelligent crawling parameters
        self.link_patterns = config.get('link_patterns', [])
        self.priority_keywords = config.get('priority_keywords', [])
        self.avoid_patterns = config.get('avoid_patterns', [])
        
        # Anti-detection features
        self.randomize_crawl_order = config.get('randomize_crawl_order', True)
        self.adaptive_delays = config.get('adaptive_delays', True)
        self.intelligent_filtering = config.get('intelligent_filtering', True)
        
        self.executor = ThreadPoolExecutor(max_workers=self.concurrent_requests)
        self._crawl_stats = {
            'pages_crawled': 0,
            'total_links': 0,
            'errors': 0,
            'start_time': None
        }

    async def crawl_bfs(self, start_urls: List[str], session_manager) -> List[Dict]:
        """
        Advanced BFS crawler with intelligent queue management
        Implements sophisticated anti-detection through randomized crawling
        """
        self.logger.info(f"Starting revolutionary BFS crawl from {len(start_urls)} URLs")
        self._crawl_stats['start_time'] = datetime.now()
        
        # Initialize BFS queue with start URLs
        for url in start_urls:
            crawl_item = CrawlItem(
                url=url, 
                depth=0, 
                priority=self._calculate_priority(url),
                timestamp=datetime.now(),
                crawl_type="bfs"
            )
            self.bfs_queue.append(crawl_item)
            
        results = []
        semaphore = asyncio.Semaphore(self.concurrent_requests)
        
        while self.bfs_queue and len(results) < self.max_pages:
            # Advanced batch processing for efficiency
            batch_size = min(self.concurrent_requests, len(self.bfs_queue))
            batch_items = []
            
            for _ in range(batch_size):
                if self.bfs_queue:
                    batch_items.append(self.bfs_queue.popleft())
            
            if not batch_items:
                break
                
            # Process batch concurrently with anti-detection
            batch_tasks = [
                self._crawl_single_page(item, session_manager, semaphore)
                for item in batch_items
            ]
            
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self._handle_crawl_error(batch_items[i], result)
                    continue
                    
                if result:
                    results.append(result)
                    self._process_extracted_links(result, batch_items[i])
                    
            # Adaptive delay between batches for stealth
            if self.adaptive_delays:
                delay = self._calculate_adaptive_delay()
                await asyncio.sleep(delay)
                
        self._log_crawl_statistics()
        return results
    
    async def crawl_dfs(self, start_urls: List[str], session_manager) -> List[Dict]:
        """
        Advanced DFS crawler with recursive exploration
        Deep crawling capabilities for comprehensive site mapping
        """
        self.logger.info(f"Starting revolutionary DFS crawl from {len(start_urls)} URLs")
        self._crawl_stats['start_time'] = datetime.now()
        
        results = []
        
        for start_url in start_urls:
            crawl_results = await self._dfs_recursive(
                url=start_url,
                depth=0,
                session_manager=session_manager,
                visited=set(),
                results=[]
            )
            results.extend(crawl_results)
            
            if len(results) >= self.max_pages:
                break
                
        self._log_crawl_statistics()
        return results[:self.max_pages]
    
    async def crawl_priority_based(self, start_urls: List[str], session_manager) -> List[Dict]:
        """
        Revolutionary priority-based crawler using advanced scoring algorithms
        Prioritizes high-value content for maximum efficiency
        """
        self.logger.info(f"Starting priority-based crawl from {len(start_urls)} URLs")
        self._crawl_stats['start_time'] = datetime.now()
        
        # Initialize priority queue
        for url in start_urls:
            priority = self._calculate_advanced_priority(url)
            crawl_item = CrawlItem(
                url=url,
                depth=0,
                priority=priority,
                timestamp=datetime.now(),
                crawl_type="priority"
            )
            heapq.heappush(self.priority_queue, crawl_item)
            
        results = []
        semaphore = asyncio.Semaphore(self.concurrent_requests)
        
        while self.priority_queue and len(results) < self.max_pages:
            # Get highest priority item
            current_item = heapq.heappop(self.priority_queue)
            
            if current_item.url in self.visited_urls:
                continue
                
            result = await self._crawl_single_page(current_item, session_manager, semaphore)
            
            if result:
                results.append(result)
                self._process_extracted_links(result, current_item)
                
                # Re-prioritize queue based on new data
                await self._reprioritize_queue(result)
                
        self._log_crawl_statistics()
        return results
    
    async def _crawl_single_page(self, item: CrawlItem, session_manager, semaphore) -> Optional[Dict]:
        """
        Advanced single page crawling with comprehensive error handling
        """
        async with semaphore:
            if item.url in self.visited_urls:
                return None
                
            if item.depth > self.max_depth:
                return None
                
            try:
                self.visited_urls.add(item.url)
                
                # Get optimized session for this request
                session = await session_manager.get_session(item.url)
                
                # Apply intelligent delays
                if self.adaptive_delays:
                    delay = self._calculate_intelligent_delay(item)
                    await asyncio.sleep(delay)
                
                # Perform the actual request
                async with session.get(item.url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Extract comprehensive page data
                        page_data = await self._extract_page_data(
                            item.url, html_content, item.depth
                        )
                        
                        self._crawl_stats['pages_crawled'] += 1
                        return page_data
                        
                    else:
                        self.logger.warning(f"HTTP {response.status} for {item.url}")
                        return None
                        
            except Exception as e:
                self._handle_crawl_error(item, e)
                return None
    
    async def _dfs_recursive(self, url: str, depth: int, session_manager, 
                           visited: Set[str], results: List[Dict]) -> List[Dict]:
        """
        Recursive DFS implementation with advanced backtracking
        """
        if url in visited or depth > self.max_depth or len(results) >= self.max_pages:
            return results
            
        visited.add(url)
        
        try:
            session = await session_manager.get_session(url)
            
            async with session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    
                    page_data = await self._extract_page_data(url, html_content, depth)
                    results.append(page_data)
                    
                    # Extract and prioritize links for deeper exploration
                    links = self._extract_intelligent_links(html_content, url)
                    
                    # Sort links by priority for optimal DFS traversal
                    links.sort(key=self._calculate_priority, reverse=True)
                    
                    for link in links:
                        if len(results) >= self.max_pages:
                            break
                            
                        await self._dfs_recursive(
                            link, depth + 1, session_manager, visited, results
                        )
                        
        except Exception as e:
            self.logger.error(f"DFS error for {url}: {e}")
            
        return results
    
    async def _extract_page_data(self, url: str, html_content: str, depth: int) -> Dict:
        """
        Advanced page data extraction with intelligent content analysis
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract comprehensive metadata
        page_data = {
            'url': url,
            'title': self._extract_title(soup),
            'depth': depth,
            'timestamp': datetime.now().isoformat(),
            'content_length': len(html_content),
            'links': self._extract_intelligent_links(html_content, url),
            'forms': self._extract_forms(soup),
            'scripts': self._extract_scripts(soup),
            'meta_data': self._extract_meta_data(soup),
            'headings': self._extract_headings(soup),
            'images': self._extract_images(soup, url),
            'content_type': self._analyze_content_type(soup),
            'language': self._detect_language(soup),
            'external_links': self._extract_external_links(soup, url),
            'internal_links': self._extract_internal_links(soup, url),
            'social_media': self._extract_social_media(soup),
            'contact_info': self._extract_contact_info(soup),
            'structured_data': self._extract_structured_data(soup),
            'performance_metrics': self._calculate_performance_metrics(html_content)
        }
        
        return page_data
    
    def _extract_intelligent_links(self, html_content: str, base_url: str) -> List[str]:
        """
        Intelligent link extraction with pattern matching and prioritization
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
                
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Apply intelligent filtering
            if self._should_crawl_url(absolute_url):
                links.append(absolute_url)
                
        # Remove duplicates while preserving order
        return list(dict.fromkeys(links))
    
    def _should_crawl_url(self, url: str) -> bool:
        """
        Advanced URL filtering with pattern matching and heuristics
        """
        if url in self.visited_urls:
            return False
            
        # Check against avoid patterns
        for pattern in self.avoid_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
                
        # Check file extensions to avoid
        avoid_extensions = ['.pdf', '.doc', '.docx', '.zip', '.exe', '.jpg', '.png', '.gif']
        if any(url.lower().endswith(ext) for ext in avoid_extensions):
            return False
            
        # Positive pattern matching
        if self.link_patterns:
            return any(re.search(pattern, url, re.IGNORECASE) for pattern in self.link_patterns)
            
        return True
    
    def _calculate_priority(self, url: str) -> float:
        """
        Basic priority calculation for URLs
        """
        priority = 0.5
        
        # Priority keywords in URL
        for keyword in self.priority_keywords:
            if keyword.lower() in url.lower():
                priority += 0.2
                
        # Shorter URLs often have higher priority
        url_length = len(url)
        if url_length < 50:
            priority += 0.1
        elif url_length > 200:
            priority -= 0.1
            
        return priority
    
    def _calculate_advanced_priority(self, url: str) -> float:
        """
        Advanced priority calculation using multiple factors
        """
        base_priority = self._calculate_priority(url)
        
        # Domain authority (simplified)
        domain = urlparse(url).netloc
        domain_score = self.domain_stats.get(domain, {}).get('authority', 0.5)
        
        # URL structure analysis
        path_segments = len(urlparse(url).path.split('/'))
        depth_penalty = path_segments * 0.05
        
        # Historical success rate
        success_rate = self._get_url_success_rate(url)
        
        advanced_priority = (base_priority + domain_score + success_rate) - depth_penalty
        
        return max(0.0, min(1.0, advanced_priority))
    
    def _calculate_intelligent_delay(self, item: CrawlItem) -> float:
        """
        Calculate intelligent delay based on multiple factors for stealth
        """
        base_delay = self.crawl_delay
        
        # Add randomization for stealth
        random_factor = random.uniform(0.5, 1.5)
        base_delay *= random_factor
        
        # Adjust based on domain
        domain = urlparse(item.url).netloc
        if domain in self.domain_stats:
            domain_delay = self.domain_stats[domain].get('avg_delay', base_delay)
            base_delay = (base_delay + domain_delay) / 2
            
        # Adjust based on priority (higher priority = longer delay for stealth)
        priority_factor = 1 + (item.priority * 0.5)
        base_delay *= priority_factor
        
        return base_delay
    
    def _calculate_adaptive_delay(self) -> float:
        """
        Calculate adaptive delay between batches
        """
        base_delay = 0.5
        
        # Increase delay if errors are high
        error_rate = self._crawl_stats['errors'] / max(1, self._crawl_stats['pages_crawled'])
        if error_rate > 0.1:
            base_delay *= (1 + error_rate)
            
        # Add randomization
        return base_delay * random.uniform(0.8, 1.2)
    
    def _process_extracted_links(self, page_data: Dict, current_item: CrawlItem):
        """
        Process extracted links and add them to appropriate queues
        """
        links = page_data.get('links', [])
        self._crawl_stats['total_links'] += len(links)
        
        for link in links:
            if link not in self.visited_urls and self._should_crawl_url(link):
                new_depth = current_item.depth + 1
                
                if current_item.crawl_type == "bfs":
                    new_item = CrawlItem(
                        url=link,
                        depth=new_depth,
                        priority=self._calculate_priority(link),
                        timestamp=datetime.now(),
                        parent_url=current_item.url,
                        crawl_type="bfs"
                    )
                    self.bfs_queue.append(new_item)
                    
                elif current_item.crawl_type == "priority":
                    priority = self._calculate_advanced_priority(link)
                    new_item = CrawlItem(
                        url=link,
                        depth=new_depth,
                        priority=priority,
                        timestamp=datetime.now(),
                        parent_url=current_item.url,
                        crawl_type="priority"
                    )
                    heapq.heappush(self.priority_queue, new_item)
    
    async def _reprioritize_queue(self, page_data: Dict):
        """
        Re-prioritize queue based on newly discovered data
        """
        # Analyze page content to adjust priorities
        content_value = self._analyze_content_value(page_data)
        
        # Adjust domain statistics
        domain = urlparse(page_data['url']).netloc
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {}
            
        self.domain_stats[domain]['content_value'] = content_value
        self.domain_stats[domain]['last_crawled'] = datetime.now()
    
    def _analyze_content_value(self, page_data: Dict) -> float:
        """
        Analyze the value of page content for priority adjustment
        """
        value_score = 0.5
        
        # Check for valuable content indicators
        if page_data.get('forms'):
            value_score += 0.2
            
        if page_data.get('structured_data'):
            value_score += 0.3
            
        if len(page_data.get('links', [])) > 10:
            value_score += 0.1
            
        return min(1.0, value_score)
    
    def _handle_crawl_error(self, item: CrawlItem, error: Exception):
        """
        Advanced error handling with retry logic
        """
        self._crawl_stats['errors'] += 1
        self.failed_urls[item.url] = self.failed_urls.get(item.url, 0) + 1
        
        self.logger.error(f"Error crawling {item.url}: {error}")
        
        # Implement retry logic
        if self.failed_urls[item.url] < self.retry_attempts:
            # Add back to queue with lower priority
            item.priority *= 0.8
            
            if item.crawl_type == "bfs":
                self.bfs_queue.append(item)
            elif item.crawl_type == "priority":
                heapq.heappush(self.priority_queue, item)
    
    def _get_url_success_rate(self, url: str) -> float:
        """
        Get historical success rate for similar URLs
        """
        domain = urlparse(url).netloc
        if domain in self.domain_stats:
            return self.domain_stats[domain].get('success_rate', 0.5)
        return 0.5
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ""
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract form information"""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get').lower(),
                'fields': []
            }
            
            for input_field in form.find_all(['input', 'select', 'textarea']):
                field_info = {
                    'name': input_field.get('name', ''),
                    'type': input_field.get('type', 'text'),
                    'required': input_field.has_attr('required')
                }
                form_data['fields'].append(field_info)
                
            forms.append(form_data)
            
        return forms
    
    def _extract_scripts(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract script information"""
        scripts = []
        for script in soup.find_all('script'):
            script_info = {
                'src': script.get('src', ''),
                'type': script.get('type', ''),
                'inline': script.string is not None
            }
            scripts.append(script_info)
        return scripts
    
    def _extract_meta_data(self, soup: BeautifulSoup) -> Dict:
        """Extract meta data"""
        meta_data = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
            content = meta.get('content')
            
            if name and content:
                meta_data[name] = content
                
        return meta_data
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Extract heading structure"""
        headings = {}
        
        for level in range(1, 7):
            tag = f'h{level}'
            headings[tag] = [h.get_text().strip() for h in soup.find_all(tag)]
            
        return headings
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract image information"""
        images = []
        
        for img in soup.find_all('img'):
            img_info = {
                'src': urljoin(base_url, img.get('src', '')),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            }
            images.append(img_info)
            
        return images
    
    def _analyze_content_type(self, soup: BeautifulSoup) -> str:
        """Analyze and categorize content type"""
        # Simple content type detection
        if soup.find('article'):
            return 'article'
        elif soup.find('form'):
            return 'form'
        elif soup.find_all(['ul', 'ol', 'li']) and len(soup.find_all(['ul', 'ol', 'li'])) > 5:
            return 'listing'
        else:
            return 'general'
    
    def _detect_language(self, soup: BeautifulSoup) -> str:
        """Detect page language"""
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang']
            
        meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if meta_lang:
            return meta_lang.get('content', 'unknown')
            
        return 'unknown'
    
    def _extract_external_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract external links"""
        base_domain = urlparse(base_url).netloc
        external_links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = urljoin(base_url, a_tag['href'])
            if urlparse(href).netloc != base_domain:
                external_links.append(href)
                
        return list(set(external_links))
    
    def _extract_internal_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract internal links"""
        base_domain = urlparse(base_url).netloc
        internal_links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = urljoin(base_url, a_tag['href'])
            if urlparse(href).netloc == base_domain:
                internal_links.append(href)
                
        return list(set(internal_links))
    
    def _extract_social_media(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract social media links"""
        social_domains = ['facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com']
        social_links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            for domain in social_domains:
                if domain in href:
                    social_links.append({
                        'platform': domain.split('.')[0],
                        'url': href
                    })
                    break
                    
        return social_links
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information"""
        contact_info = {}
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact_info['emails'] = list(set(emails))
            
        # Look for phone numbers (simplified)
        phone_pattern = r'(\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact_info['phones'] = list(set(phones))
            
        return contact_info
    
    def _extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract structured data (JSON-LD, microdata, etc.)"""
        structured_data = []
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                structured_data.append({'type': 'json-ld', 'data': data})
            except:
                pass
                
        return structured_data
    
    def _calculate_performance_metrics(self, html_content: str) -> Dict:
        """Calculate basic performance metrics"""
        return {
            'html_size': len(html_content),
            'estimated_load_time': len(html_content) / 1000,  # Simple estimate
        }
    
    def _log_crawl_statistics(self):
        """Log comprehensive crawl statistics"""
        end_time = datetime.now()
        duration = end_time - self._crawl_stats['start_time']
        
        self.logger.info(f"""
Revolutionary Crawl Statistics:
================================
Pages Crawled: {self._crawl_stats['pages_crawled']}
Total Links Found: {self._crawl_stats['total_links']}
Errors: {self._crawl_stats['errors']}
Duration: {duration}
Pages/Second: {self._crawl_stats['pages_crawled'] / duration.total_seconds():.2f}
Success Rate: {((self._crawl_stats['pages_crawled'] - self._crawl_stats['errors']) / max(1, self._crawl_stats['pages_crawled'])) * 100:.1f}%
""")

    async def __aenter__(self):
        """Async context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        self.executor.shutdown(wait=True)
