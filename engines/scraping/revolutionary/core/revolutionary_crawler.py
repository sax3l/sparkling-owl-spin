"""
Revolutionary Crawler System - Ultimate BFS/DFS Implementation
Implements all advanced crawling algorithms from the specification for unblockable scraping.
"""

import asyncio
import heapq
import time
import random
import hashlib
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Callable, Any, Union
from urllib.parse import urljoin, urlparse, parse_qs
import aiohttp
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta


@dataclass
class CrawlItem:
    """Advanced crawl item with intelligence and priority"""
    url: str
    depth: int
    priority: float = 0.0
    parent_url: Optional[str] = None
    discovered_time: datetime = field(default_factory=datetime.now)
    content_type: Optional[str] = None
    estimated_value: float = 0.0
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    extraction_rules: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first


@dataclass 
class CrawlResult:
    """Comprehensive crawl result data"""
    url: str
    content: str
    links: List[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, float]
    security_indicators: Dict[str, bool]


class IntelligentLinkAnalyzer:
    """AI-powered link analysis and prioritization"""
    
    def __init__(self):
        self.url_patterns = {
            'product': [r'/product/', r'/item/', r'/p/\d+', r'pid=\d+'],
            'category': [r'/category/', r'/cat/', r'/c/'],
            'list': [r'/list/', r'/search', r'/results'],
            'detail': [r'/detail/', r'/view/', r'/show/'],
            'api': [r'/api/', r'/v\d+/', r'\.json', r'\.xml'],
            'pagination': [r'page=\d+', r'/page/\d+', r'p=\d+', r'offset=\d+'],
            'deep_content': [r'/\d{4}/', r'/archive/', r'/posts/', r'/articles/']
        }
        
        self.value_indicators = {
            'high_value': ['product', 'api', 'detail', 'deep_content'],
            'medium_value': ['category', 'list'], 
            'low_value': ['pagination', 'static']
        }
    
    def analyze_url(self, url: str, context: Dict = None) -> Dict[str, Any]:
        """Advanced URL analysis with AI-driven insights"""
        analysis = {
            'type': 'unknown',
            'priority_score': 1.0,
            'estimated_value': 0.5,
            'crawl_difficulty': 1.0,
            'content_indicators': {},
            'security_level': 'normal'
        }
        
        url_lower = url.lower()
        
        # Pattern matching for URL type
        for url_type, patterns in self.url_patterns.items():
            if any(re.search(pattern, url_lower) for pattern in patterns):
                analysis['type'] = url_type
                break
        
        # Calculate priority based on type
        if analysis['type'] in self.value_indicators['high_value']:
            analysis['priority_score'] = random.uniform(8.0, 10.0)
            analysis['estimated_value'] = random.uniform(0.8, 1.0)
        elif analysis['type'] in self.value_indicators['medium_value']:
            analysis['priority_score'] = random.uniform(5.0, 7.0)
            analysis['estimated_value'] = random.uniform(0.5, 0.8)
        else:
            analysis['priority_score'] = random.uniform(1.0, 4.0)
            analysis['estimated_value'] = random.uniform(0.1, 0.5)
        
        # Detect potential API endpoints
        if any(indicator in url_lower for indicator in ['.json', '/api/', 'ajax', 'xhr']):
            analysis['content_indicators']['api_endpoint'] = True
            analysis['priority_score'] *= 1.5
        
        # Detect deep content
        path_segments = len([s for s in urlparse(url).path.split('/') if s])
        if path_segments > 3:
            analysis['content_indicators']['deep_content'] = True
            analysis['estimated_value'] += 0.2
        
        # Security level assessment
        if any(indicator in url_lower for indicator in ['admin', 'config', 'debug', 'test']):
            analysis['security_level'] = 'high_value_target'
            analysis['priority_score'] *= 2.0
        
        return analysis


class RevolutionaryBFSCrawler:
    """Advanced Breadth-First Search crawler with intelligent prioritization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.link_analyzer = IntelligentLinkAnalyzer()
        self.visited: Set[str] = set()
        self.queue: deque = deque()
        self.results: List[CrawlResult] = []
        self.performance_metrics: Dict[str, float] = {}
        self.content_filter = ContentIntelligenceFilter()
        self.semaphore = asyncio.Semaphore(config.get('max_concurrent', 10))
        
    async def crawl(self, start_urls: List[str], max_depth: int = 5, max_pages: int = 1000) -> List[CrawlResult]:
        """Execute intelligent BFS crawling"""
        start_time = time.time()
        
        # Initialize queue with analyzed start URLs
        for url in start_urls:
            analysis = self.link_analyzer.analyze_url(url)
            item = CrawlItem(
                url=url,
                depth=0,
                priority=analysis['priority_score'],
                estimated_value=analysis['estimated_value']
            )
            self.queue.append(item)
        
        pages_crawled = 0
        
        while self.queue and pages_crawled < max_pages:
            # Process current level (breadth-first)
            current_level_size = len(self.queue)
            tasks = []
            
            for _ in range(min(current_level_size, self.config.get('batch_size', 20))):
                if not self.queue:
                    break
                    
                item = self.queue.popleft()
                
                if item.url not in self.visited and item.depth <= max_depth:
                    self.visited.add(item.url)
                    task = self._crawl_page(item)
                    tasks.append(task)
            
            # Execute batch concurrently
            if tasks:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, CrawlResult):
                        self.results.append(result)
                        pages_crawled += 1
                        
                        # Add discovered links to queue for next level
                        for link in result.links:
                            if link not in self.visited:
                                analysis = self.link_analyzer.analyze_url(link, {'parent': result.url})
                                child_item = CrawlItem(
                                    url=link,
                                    depth=result.metadata.get('depth', 0) + 1,
                                    priority=analysis['priority_score'],
                                    parent_url=result.url,
                                    estimated_value=analysis['estimated_value']
                                )
                                self.queue.append(child_item)
        
        # Calculate performance metrics
        total_time = time.time() - start_time
        self.performance_metrics.update({
            'total_time': total_time,
            'pages_per_second': pages_crawled / total_time if total_time > 0 else 0,
            'pages_crawled': pages_crawled,
            'total_links_discovered': sum(len(r.links) for r in self.results),
            'crawl_efficiency': pages_crawled / max(len(self.visited), 1)
        })
        
        return self.results
    
    async def _crawl_page(self, item: CrawlItem) -> Optional[CrawlResult]:
        """Crawl individual page with intelligence"""
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    
                    async with session.get(item.url, timeout=30) as response:
                        content = await response.text()
                        
                        # Parse content and extract data
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Intelligent link extraction
                        links = self._extract_intelligent_links(soup, item.url)
                        
                        # Extract structured data
                        data = self._extract_structured_data(soup, item.url)
                        
                        # Calculate performance metrics
                        crawl_time = time.time() - start_time
                        
                        return CrawlResult(
                            url=item.url,
                            content=content,
                            links=links,
                            data=data,
                            metadata={
                                'depth': item.depth,
                                'parent_url': item.parent_url,
                                'crawl_time': crawl_time,
                                'content_length': len(content),
                                'links_found': len(links)
                            },
                            performance_metrics={
                                'response_time': crawl_time,
                                'content_size': len(content),
                                'link_density': len(links) / max(len(content), 1)
                            },
                            security_indicators={}
                        )
                        
            except Exception as e:
                print(f"Error crawling {item.url}: {e}")
                return None
    
    def _extract_intelligent_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Advanced link extraction with filtering and analysis"""
        links = []
        
        # Extract from various sources
        for tag in soup.find_all(['a', 'link'], href=True):
            href = tag.get('href')
            if href:
                full_url = urljoin(base_url, href)
                
                # Apply intelligent filtering
                if self._should_follow_link(full_url, tag):
                    links.append(full_url)
        
        # Extract from JavaScript (API calls, dynamic links)
        script_links = self._extract_javascript_links(soup, base_url)
        links.extend(script_links)
        
        return list(set(links))  # Remove duplicates
    
    def _should_follow_link(self, url: str, tag) -> bool:
        """Intelligent link filtering"""
        # Basic filters
        if any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.pdf', '.zip', '.mp4']):
            return False
        
        if any(pattern in url.lower() for pattern in ['logout', 'delete', 'remove']):
            return False
        
        # Analyze link context for value
        link_text = tag.get_text(strip=True).lower()
        if link_text:
            value_indicators = ['product', 'detail', 'view', 'more', 'read', 'search']
            if any(indicator in link_text for indicator in value_indicators):
                return True
        
        return True
    
    def _extract_javascript_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links from JavaScript code"""
        links = []
        
        for script in soup.find_all('script'):
            if script.string:
                # Look for API endpoints
                api_patterns = [
                    r'["\'](/api/[^"\']+)["\']',
                    r'["\']([^"\']*\.json[^"\']*)["\']',
                    r'fetch\(["\']([^"\']+)["\']',
                    r'ajax\(["\']url["\']:\s*["\']([^"\']+)["\']'
                ]
                
                for pattern in api_patterns:
                    matches = re.findall(pattern, script.string)
                    for match in matches:
                        full_url = urljoin(base_url, match)
                        links.append(full_url)
        
        return links
    
    def _extract_structured_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract structured data from page"""
        data = {}
        
        # JSON-LD structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_data = json.loads(script.string)
                data['json_ld'] = json_data
            except:
                pass
        
        # Meta tags
        meta_data = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_data[name] = content
        
        if meta_data:
            data['meta'] = meta_data
        
        # Extract main content based on common patterns
        content_selectors = [
            'main', 'article', '.content', '#content', '.main-content',
            '.post-content', '.entry-content', '.product-details'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                data['main_content'] = [elem.get_text(strip=True) for elem in elements[:3]]
                break
        
        return data


class RevolutionaryDFSCrawler:
    """Advanced Depth-First Search crawler with intelligent backtracking"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.link_analyzer = IntelligentLinkAnalyzer()
        self.visited: Set[str] = set()
        self.results: List[CrawlResult] = []
        self.crawl_stack: List[CrawlItem] = []
        self.performance_metrics: Dict[str, float] = {}
        self.semaphore = asyncio.Semaphore(config.get('max_concurrent', 5))  # Lower for DFS
        
    async def crawl(self, start_urls: List[str], max_depth: int = 10, max_pages: int = 1000) -> List[CrawlResult]:
        """Execute intelligent DFS crawling"""
        start_time = time.time()
        pages_crawled = 0
        
        for start_url in start_urls:
            if pages_crawled >= max_pages:
                break
                
            analysis = self.link_analyzer.analyze_url(start_url)
            start_item = CrawlItem(
                url=start_url,
                depth=0,
                priority=analysis['priority_score'],
                estimated_value=analysis['estimated_value']
            )
            
            # Recursive DFS with intelligent path selection
            await self._dfs_crawl_recursive(start_item, max_depth, max_pages - pages_crawled)
            pages_crawled = len(self.results)
        
        # Performance metrics
        total_time = time.time() - start_time
        self.performance_metrics.update({
            'total_time': total_time,
            'pages_per_second': pages_crawled / total_time if total_time > 0 else 0,
            'pages_crawled': pages_crawled,
            'max_depth_reached': max(r.metadata.get('depth', 0) for r in self.results) if self.results else 0,
            'average_depth': sum(r.metadata.get('depth', 0) for r in self.results) / max(len(self.results), 1)
        })
        
        return self.results
    
    async def _dfs_crawl_recursive(self, item: CrawlItem, max_depth: int, remaining_pages: int):
        """Recursive DFS with intelligent prioritization"""
        if (remaining_pages <= 0 or 
            item.depth > max_depth or 
            item.url in self.visited):
            return
        
        self.visited.add(item.url)
        
        # Crawl current page
        result = await self._crawl_page(item)
        if result:
            self.results.append(result)
            remaining_pages -= 1
            
            # Sort links by priority for intelligent path selection
            analyzed_links = []
            for link in result.links[:20]:  # Limit to prevent explosion
                if link not in self.visited:
                    analysis = self.link_analyzer.analyze_url(link, {'parent': result.url})
                    child_item = CrawlItem(
                        url=link,
                        depth=item.depth + 1,
                        priority=analysis['priority_score'],
                        parent_url=item.url,
                        estimated_value=analysis['estimated_value']
                    )
                    analyzed_links.append(child_item)
            
            # Sort by priority (highest first) for DFS path selection
            analyzed_links.sort(key=lambda x: x.priority, reverse=True)
            
            # Recursively follow top priority links
            for child_item in analyzed_links:
                if remaining_pages <= 0:
                    break
                await self._dfs_crawl_recursive(child_item, max_depth, remaining_pages)
                remaining_pages = max(0, remaining_pages - 1)
    
    async def _crawl_page(self, item: CrawlItem) -> Optional[CrawlResult]:
        """Same as BFS implementation but with DFS-specific optimizations"""
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = time.time()
                    
                    async with session.get(item.url, timeout=30) as response:
                        content = await response.text()
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Extract links with DFS preference (favor deep links)
                        links = self._extract_deep_links(soup, item.url)
                        data = self._extract_structured_data(soup, item.url)
                        
                        crawl_time = time.time() - start_time
                        
                        return CrawlResult(
                            url=item.url,
                            content=content,
                            links=links,
                            data=data,
                            metadata={
                                'depth': item.depth,
                                'parent_url': item.parent_url,
                                'crawl_time': crawl_time,
                                'crawl_method': 'DFS'
                            },
                            performance_metrics={
                                'response_time': crawl_time,
                                'content_size': len(content)
                            },
                            security_indicators={}
                        )
                        
            except Exception as e:
                print(f"DFS Error crawling {item.url}: {e}")
                return None
    
    def _extract_deep_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract links with preference for deeper content"""
        links = []
        
        # Prioritize links that suggest deeper content
        deep_indicators = ['detail', 'view', 'item', 'product', 'article', 'post']
        
        for tag in soup.find_all('a', href=True):
            href = tag.get('href')
            link_text = tag.get_text(strip=True).lower()
            
            if href:
                full_url = urljoin(base_url, href)
                
                # Boost priority for deep content indicators
                priority_boost = any(indicator in link_text or indicator in href.lower() 
                                   for indicator in deep_indicators)
                
                if priority_boost or self._should_follow_link(full_url, tag):
                    links.append(full_url)
        
        return list(set(links))
    
    def _should_follow_link(self, url: str, tag) -> bool:
        """DFS-specific link filtering"""
        # Same as BFS but with preference for deeper paths
        parsed = urlparse(url)
        path_segments = len([s for s in parsed.path.split('/') if s])
        
        # Prefer links that go deeper
        if path_segments > 2:
            return True
            
        # Standard filtering
        if any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.pdf']):
            return False
            
        return True
    
    def _extract_structured_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Same structured data extraction as BFS"""
        data = {}
        
        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_data = json.loads(script.string)
                data['json_ld'] = json_data
            except:
                pass
        
        # Meta tags
        meta_data = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_data[name] = content
                
        if meta_data:
            data['meta'] = meta_data
        
        return data


class IntelligentHybridCrawler:
    """Ultimate hybrid crawler combining BFS, DFS, and priority-based algorithms"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.link_analyzer = IntelligentLinkAnalyzer()
        self.bfs_crawler = RevolutionaryBFSCrawler(config)
        self.dfs_crawler = RevolutionaryDFSCrawler(config)
        self.priority_queue: List[CrawlItem] = []
        self.visited: Set[str] = set()
        self.results: List[CrawlResult] = []
        self.performance_metrics: Dict[str, float] = {}
        
    async def crawl(self, start_urls: List[str], strategy: str = 'intelligent') -> List[CrawlResult]:
        """Execute hybrid crawling with multiple strategies"""
        start_time = time.time()
        
        if strategy == 'intelligent':
            return await self._intelligent_hybrid_crawl(start_urls)
        elif strategy == 'multi_phase':
            return await self._multi_phase_crawl(start_urls)
        elif strategy == 'priority_first':
            return await self._priority_first_crawl(start_urls)
        else:
            # Default to BFS
            return await self.bfs_crawler.crawl(start_urls)
    
    async def _intelligent_hybrid_crawl(self, start_urls: List[str]) -> List[CrawlResult]:
        """Intelligent hybrid approach - adapts strategy based on site structure"""
        
        # Phase 1: Quick BFS sampling to understand site structure
        print("🔍 Phase 1: Site structure analysis...")
        bfs_sample = await self.bfs_crawler.crawl(start_urls[:3], max_depth=2, max_pages=50)
        
        # Analyze the sample results
        site_analysis = self._analyze_site_structure(bfs_sample)
        
        # Phase 2: Choose optimal strategy based on analysis
        if site_analysis['deep_content_ratio'] > 0.7:
            print("📊 Detected deep content structure - using DFS strategy")
            main_results = await self.dfs_crawler.crawl(start_urls, max_depth=15, max_pages=500)
        elif site_analysis['api_endpoint_ratio'] > 0.3:
            print("🔌 Detected API-heavy site - using priority strategy")  
            main_results = await self._priority_first_crawl(start_urls)
        else:
            print("🌐 Standard site structure - using enhanced BFS")
            main_results = await self.bfs_crawler.crawl(start_urls, max_depth=8, max_pages=800)
        
        # Phase 3: Targeted collection for missed high-value content
        print("🎯 Phase 3: High-value content targeting...")
        missed_urls = self._identify_missed_high_value_urls(main_results)
        if missed_urls:
            targeted_results = await self._targeted_crawl(missed_urls)
            main_results.extend(targeted_results)
        
        return main_results
    
    async def _multi_phase_crawl(self, start_urls: List[str]) -> List[CrawlResult]:
        """Multi-phase crawling: BFS for breadth, then DFS for depth"""
        all_results = []
        
        # Phase 1: BFS for site coverage
        print("📡 Phase 1: Broad coverage with BFS...")
        bfs_results = await self.bfs_crawler.crawl(start_urls, max_depth=3, max_pages=200)
        all_results.extend(bfs_results)
        
        # Phase 2: Extract interesting deep URLs from BFS results
        deep_urls = []
        for result in bfs_results:
            for link in result.links:
                analysis = self.link_analyzer.analyze_url(link)
                if (analysis['type'] in ['product', 'detail', 'api'] and 
                    link not in self.visited):
                    deep_urls.append(link)
        
        # Phase 3: DFS on selected deep URLs
        if deep_urls:
            print(f"🏊 Phase 2: Deep diving into {len(deep_urls)} high-value URLs...")
            dfs_results = await self.dfs_crawler.crawl(deep_urls[:20], max_depth=10, max_pages=300)
            all_results.extend(dfs_results)
        
        return all_results
    
    async def _priority_first_crawl(self, start_urls: List[str]) -> List[CrawlResult]:
        """Priority-based crawling using intelligent scoring"""
        
        # Initialize priority queue
        for url in start_urls:
            analysis = self.link_analyzer.analyze_url(url)
            item = CrawlItem(
                url=url,
                depth=0,
                priority=analysis['priority_score'],
                estimated_value=analysis['estimated_value']
            )
            heapq.heappush(self.priority_queue, item)
        
        results = []
        pages_crawled = 0
        max_pages = self.config.get('max_pages', 1000)
        
        while self.priority_queue and pages_crawled < max_pages:
            # Get highest priority item
            item = heapq.heappop(self.priority_queue)
            
            if item.url not in self.visited:
                self.visited.add(item.url)
                
                # Crawl the page
                result = await self._crawl_priority_page(item)
                if result:
                    results.append(result)
                    pages_crawled += 1
                    
                    # Add discovered links to priority queue
                    for link in result.links:
                        if link not in self.visited:
                            analysis = self.link_analyzer.analyze_url(link, {'parent': result.url})
                            child_item = CrawlItem(
                                url=link,
                                depth=item.depth + 1,
                                priority=analysis['priority_score'],
                                parent_url=item.url,
                                estimated_value=analysis['estimated_value']
                            )
                            heapq.heappush(self.priority_queue, child_item)
        
        return results
    
    def _analyze_site_structure(self, sample_results: List[CrawlResult]) -> Dict[str, float]:
        """Analyze sample results to understand site structure"""
        if not sample_results:
            return {'deep_content_ratio': 0.0, 'api_endpoint_ratio': 0.0}
        
        deep_content_count = 0
        api_endpoint_count = 0
        
        for result in sample_results:
            # Check for deep content indicators
            if (result.metadata.get('depth', 0) > 3 or
                any(indicator in result.url.lower() for indicator in ['product', 'detail', 'item', 'view'])):
                deep_content_count += 1
                
            # Check for API endpoints
            if any(indicator in result.url.lower() for indicator in ['.json', '/api/', 'ajax']):
                api_endpoint_count += 1
        
        total_results = len(sample_results)
        return {
            'deep_content_ratio': deep_content_count / total_results,
            'api_endpoint_ratio': api_endpoint_count / total_results,
            'average_links_per_page': sum(len(r.links) for r in sample_results) / total_results,
            'content_diversity': len(set(self.link_analyzer.analyze_url(r.url)['type'] for r in sample_results)) / 10.0
        }
    
    def _identify_missed_high_value_urls(self, results: List[CrawlResult]) -> List[str]:
        """Identify high-value URLs that might have been missed"""
        all_discovered_links = set()
        for result in results:
            all_discovered_links.update(result.links)
        
        high_value_urls = []
        for url in all_discovered_links:
            if url not in self.visited:
                analysis = self.link_analyzer.analyze_url(url)
                if (analysis['priority_score'] > 8.0 or 
                    analysis['security_level'] == 'high_value_target'):
                    high_value_urls.append(url)
        
        return high_value_urls[:50]  # Limit to prevent overload
    
    async def _targeted_crawl(self, urls: List[str]) -> List[CrawlResult]:
        """Targeted crawling of specific high-value URLs"""
        results = []
        
        for url in urls:
            item = CrawlItem(url=url, depth=0, priority=10.0)
            result = await self._crawl_priority_page(item)
            if result:
                results.append(result)
        
        return results
    
    async def _crawl_priority_page(self, item: CrawlItem) -> Optional[CrawlResult]:
        """Crawl page with priority-based optimizations"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(item.url, timeout=30) as response:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    links = self._extract_intelligent_links(soup, item.url)
                    data = self._extract_structured_data(soup, item.url)
                    
                    return CrawlResult(
                        url=item.url,
                        content=content,
                        links=links,
                        data=data,
                        metadata={'depth': item.depth, 'priority': item.priority},
                        performance_metrics={},
                        security_indicators={}
                    )
                    
        except Exception as e:
            print(f"Priority crawl error for {item.url}: {e}")
            return None
    
    def _extract_intelligent_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Enhanced link extraction for hybrid crawler"""
        links = []
        
        for tag in soup.find_all('a', href=True):
            href = tag.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if self._should_follow_link(full_url, tag):
                    links.append(full_url)
        
        return list(set(links))
    
    def _should_follow_link(self, url: str, tag) -> bool:
        """Enhanced link filtering for hybrid approach"""
        # Skip common unwanted file types
        if any(ext in url.lower() for ext in ['.jpg', '.png', '.gif', '.pdf', '.zip']):
            return False
        
        # Skip logout/delete actions
        if any(action in url.lower() for action in ['logout', 'delete', 'remove']):
            return False
        
        return True
    
    def _extract_structured_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Enhanced structured data extraction"""
        data = {}
        
        # JSON-LD structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                json_data = json.loads(script.string)
                data['json_ld'] = json_data
            except:
                pass
        
        # Meta tags
        meta_data = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_data[name] = content
        
        if meta_data:
            data['meta'] = meta_data
        
        return data


class ContentIntelligenceFilter:
    """AI-powered content analysis and filtering"""
    
    def __init__(self):
        self.content_patterns = {
            'high_value': [
                r'price.*\$\d+', r'product.*detail', r'api.*endpoint',
                r'json.*data', r'database.*query', r'admin.*panel'
            ],
            'medium_value': [
                r'search.*result', r'category.*list', r'user.*profile',
                r'article.*content', r'news.*item'
            ],
            'low_value': [
                r'footer.*link', r'sidebar.*widget', r'advertisement',
                r'social.*media', r'cookie.*policy'
            ]
        }
    
    def analyze_content_value(self, content: str, url: str) -> Dict[str, Any]:
        """Analyze content to determine its value and extraction priority"""
        content_lower = content.lower()
        url_lower = url.lower()
        
        value_score = 0.0
        indicators = []
        
        # Pattern matching
        for category, patterns in self.content_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, content_lower))
            if matches > 0:
                indicators.append(category)
                if category == 'high_value':
                    value_score += matches * 3.0
                elif category == 'medium_value':
                    value_score += matches * 1.5
                else:
                    value_score += matches * 0.5
        
        # Content length and structure analysis
        if len(content) > 50000:  # Large content pages often valuable
            value_score += 1.0
        
        if '<table' in content_lower and 'data' in content_lower:
            value_score += 2.0  # Structured data tables
            indicators.append('structured_data')
        
        if 'json' in content_lower or 'xml' in content_lower:
            value_score += 3.0  # API responses
            indicators.append('api_response')
        
        return {
            'value_score': min(value_score, 10.0),  # Cap at 10
            'indicators': indicators,
            'content_type': self._detect_content_type(content, url),
            'extraction_priority': 'high' if value_score > 5 else 'medium' if value_score > 2 else 'low'
        }
    
    def _detect_content_type(self, content: str, url: str) -> str:
        """Detect the type of content for targeted extraction"""
        content_lower = content.lower()
        
        if url.endswith('.json') or 'application/json' in content_lower:
            return 'json_api'
        elif '<table' in content_lower and len(re.findall(r'<tr', content_lower)) > 5:
            return 'data_table'
        elif any(indicator in content_lower for indicator in ['product', 'price', 'buy', 'cart']):
            return 'product_page'
        elif any(indicator in content_lower for indicator in ['article', 'post', 'news', 'blog']):
            return 'content_article'
        elif 'search' in url.lower() or 'results' in content_lower:
            return 'search_results'
        else:
            return 'general_page'


# Export the main classes
__all__ = [
    'RevolutionaryBFSCrawler',
    'RevolutionaryDFSCrawler', 
    'IntelligentHybridCrawler',
    'IntelligentLinkAnalyzer',
    'ContentIntelligenceFilter',
    'CrawlItem',
    'CrawlResult'
]
