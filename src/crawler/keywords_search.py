"""
Keywords Search Crawler - Advanced keyword-based website crawling system.
Provides intelligent search-driven crawling for discovering content based on keywords,
search patterns, and semantic relevance.
"""

import asyncio
import re
import urllib.parse
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse

from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class SearchTarget:
    """Configuration for keyword-based search crawling."""
    keywords: List[str]
    search_patterns: List[str]
    target_domains: List[str]
    max_depth: int = 3
    max_results: int = 1000
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None
    
    def __post_init__(self):
        if self.include_patterns is None:
            self.include_patterns = []
        if self.exclude_patterns is None:
            self.exclude_patterns = []


@dataclass
class SearchResult:
    """Result from keyword search crawling."""
    url: str
    title: str
    content_snippet: str
    keywords_found: List[str]
    relevance_score: float
    depth: int
    found_at: datetime
    parent_url: Optional[str] = None


class KeywordSearchCrawler:
    """
    Advanced keyword-based crawling system.
    
    Features:
    - Keyword relevance scoring
    - Content pattern matching
    - Search term discovery
    - Domain-specific search strategies
    - Semantic content analysis
    - Result ranking and filtering
    """
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        min_relevance_score: float = 0.3,
        max_concurrent_requests: int = 5
    ):
        self.metrics = metrics_collector
        self.min_relevance_score = min_relevance_score
        self.max_concurrent_requests = max_concurrent_requests
        
        # State tracking
        self.visited_urls: Set[str] = set()
        self.search_results: List[SearchResult] = []
        self.keyword_patterns: Dict[str, re.Pattern] = {}
        
    async def search_crawl(
        self,
        search_target: SearchTarget,
        http_client = None,
        browser_client = None
    ) -> List[SearchResult]:
        """
        Perform keyword-based crawling across target domains.
        
        Args:
            search_target: Search configuration and targets
            http_client: HTTP client for fast requests
            browser_client: Browser client for dynamic content
            
        Returns:
            List of search results ranked by relevance
        """
        logger.info(f"Starting keyword search crawl for: {search_target.keywords}")
        
        # Compile keyword patterns
        self._compile_keyword_patterns(search_target.keywords)
        
        # Generate search URLs for each domain
        search_urls = self._generate_search_urls(search_target)
        
        # Perform parallel crawling
        semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        tasks = []
        
        for url in search_urls:
            task = asyncio.create_task(
                self._crawl_search_url(
                    semaphore, url, search_target, 0, http_client, browser_client
                )
            )
            tasks.append(task)
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
        # Rank and filter results
        ranked_results = self._rank_results(search_target)
        
        logger.info(f"Keyword search completed: {len(ranked_results)} results found")
        
        # Update metrics
        self.metrics.counter("keywords_search_completed", 1)
        self.metrics.gauge("keywords_search_results", len(ranked_results))
        
        return ranked_results
        
    def _compile_keyword_patterns(self, keywords: List[str]):
        """Compile regex patterns for keyword matching."""
        self.keyword_patterns = {}
        
        for keyword in keywords:
            # Create case-insensitive word boundary pattern
            pattern = rf'\b{re.escape(keyword)}\b'
            self.keyword_patterns[keyword] = re.compile(pattern, re.IGNORECASE)
            
    def _generate_search_urls(self, search_target: SearchTarget) -> List[str]:
        """Generate search URLs for target domains."""
        search_urls = []
        
        # Common search patterns for different sites
        search_patterns = {
            'generic': '/search?q={keyword}',
            'wordpress': '/?s={keyword}',
            'drupal': '/search/node/{keyword}',
            'joomla': '/search?searchword={keyword}',
            'shopify': '/search?q={keyword}',
            'magento': '/catalogsearch/result/?q={keyword}',
        }
        
        for domain in search_target.target_domains:
            for keyword in search_target.keywords:
                encoded_keyword = urllib.parse.quote_plus(keyword)
                
                # Try multiple search patterns
                for pattern_name, pattern in search_patterns.items():
                    search_url = f"https://{domain}{pattern.format(keyword=encoded_keyword)}"
                    search_urls.append(search_url)
                    
                # Also try custom patterns from search_target
                for custom_pattern in search_target.search_patterns:
                    search_url = f"https://{domain}{custom_pattern.format(keyword=encoded_keyword)}"
                    search_urls.append(search_url)
                    
        return list(set(search_urls))  # Remove duplicates
        
    async def _crawl_search_url(
        self,
        semaphore: asyncio.Semaphore,
        url: str,
        search_target: SearchTarget,
        depth: int,
        http_client=None,
        browser_client=None
    ):
        """Crawl a specific search URL."""
        async with semaphore:
            if (
                url in self.visited_urls or
                depth > search_target.max_depth or
                len(self.search_results) >= search_target.max_results
            ):
                return
                
            self.visited_urls.add(url)
            
            try:
                # Fetch page content
                content, title = await self._fetch_page_content(
                    url, http_client, browser_client
                )
                
                if not content:
                    return
                    
                # Analyze content for keywords
                analysis = self._analyze_content(content, title, search_target.keywords)
                
                if analysis['relevance_score'] >= self.min_relevance_score:
                    # Create search result
                    result = SearchResult(
                        url=url,
                        title=title or "No title",
                        content_snippet=analysis['snippet'],
                        keywords_found=analysis['keywords_found'],
                        relevance_score=analysis['relevance_score'],
                        depth=depth,
                        found_at=datetime.now()
                    )
                    
                    self.search_results.append(result)
                    
                    logger.debug(
                        f"Found relevant content: {url} "
                        f"(score: {analysis['relevance_score']:.2f})"
                    )
                    
                # Extract and follow relevant links
                if depth < search_target.max_depth:
                    links = self._extract_relevant_links(
                        content, url, search_target
                    )
                    
                    # Follow most promising links
                    for link_url in links[:5]:  # Limit links per page
                        await self._crawl_search_url(
                            semaphore, link_url, search_target, depth + 1,
                            http_client, browser_client
                        )
                        
            except Exception as e:
                logger.error(f"Error crawling search URL {url}: {e}")
                
    async def _fetch_page_content(
        self, url: str, http_client=None, browser_client=None
    ) -> Tuple[str, str]:
        """Fetch page content using appropriate client."""
        try:
            # Try HTTP client first for speed
            if http_client:
                try:
                    response = await http_client.get(url, timeout=30)
                    if response.status_code == 200:
                        content = response.text
                        title = self._extract_title(content)
                        return content, title
                except Exception as e:
                    logger.debug(f"HTTP client failed for {url}: {e}")
                    
            # Fallback to browser client for dynamic content
            if browser_client:
                try:
                    await browser_client.goto(url, timeout=30000)
                    content = await browser_client.content()
                    title = await browser_client.title()
                    return content, title
                except Exception as e:
                    logger.debug(f"Browser client failed for {url}: {e}")
                    
            return "", ""
            
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return "", ""
            
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML content."""
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return ""
        
    def _analyze_content(
        self, content: str, title: str, keywords: List[str]
    ) -> Dict:
        """Analyze content for keyword relevance."""
        # Clean content (remove HTML tags, normalize whitespace)
        clean_content = re.sub(r'<[^>]+>', ' ', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Combine title and content for analysis
        full_text = f"{title} {clean_content}"
        
        # Find keywords
        keywords_found = []
        keyword_scores = {}
        
        for keyword in keywords:
            pattern = self.keyword_patterns.get(keyword)
            if pattern:
                matches = pattern.findall(full_text)
                if matches:
                    keywords_found.append(keyword)
                    # Score based on frequency and position
                    title_matches = pattern.findall(title)
                    content_matches = pattern.findall(clean_content)
                    
                    # Higher score for title matches
                    score = len(title_matches) * 2 + len(content_matches)
                    keyword_scores[keyword] = score
                    
        # Calculate relevance score
        if not keywords_found:
            relevance_score = 0.0
        else:
            # Normalize score based on content length and keyword importance
            total_score = sum(keyword_scores.values())
            content_factor = min(1.0, len(clean_content) / 1000)  # Longer content = better
            keyword_factor = len(keywords_found) / len(keywords)  # More keywords = better
            
            relevance_score = (total_score * content_factor * keyword_factor) / 10
            relevance_score = min(1.0, relevance_score)  # Cap at 1.0
            
        # Create content snippet
        snippet = self._create_snippet(clean_content, keywords_found)
        
        return {
            'keywords_found': keywords_found,
            'relevance_score': relevance_score,
            'snippet': snippet,
            'keyword_scores': keyword_scores
        }
        
    def _create_snippet(self, content: str, keywords: List[str]) -> str:
        """Create content snippet highlighting keywords."""
        if not keywords:
            return content[:200] + "..." if len(content) > 200 else content
            
        # Find first keyword occurrence
        snippet_start = 0
        for keyword in keywords:
            pattern = self.keyword_patterns.get(keyword)
            if pattern:
                match = pattern.search(content)
                if match:
                    snippet_start = max(0, match.start() - 50)
                    break
                    
        # Extract snippet around keyword
        snippet_end = min(len(content), snippet_start + 300)
        snippet = content[snippet_start:snippet_end]
        
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(content):
            snippet = snippet + "..."
            
        return snippet.strip()
        
    def _extract_relevant_links(
        self, content: str, base_url: str, search_target: SearchTarget
    ) -> List[str]:
        """Extract links that might contain relevant content."""
        links = []
        
        # Extract all links from content
        link_pattern = re.compile(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>', re.IGNORECASE)
        matches = link_pattern.findall(content)
        
        base_domain = urlparse(base_url).netloc
        
        for href in matches:
            try:
                # Resolve relative URLs
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                
                # Only follow links on target domains
                if parsed_url.netloc not in search_target.target_domains:
                    continue
                    
                # Apply include/exclude patterns
                if search_target.include_patterns:
                    if not any(re.search(pattern, full_url) for pattern in search_target.include_patterns):
                        continue
                        
                if search_target.exclude_patterns:
                    if any(re.search(pattern, full_url) for pattern in search_target.exclude_patterns):
                        continue
                        
                # Score link relevance (simple heuristic)
                link_text = self._extract_link_text(content, href)
                if self._is_link_relevant(link_text, full_url, search_target.keywords):
                    links.append(full_url)
                    
            except Exception as e:
                logger.debug(f"Error processing link {href}: {e}")
                
        return list(set(links))  # Remove duplicates
        
    def _extract_link_text(self, content: str, href: str) -> str:
        """Extract text content of a link."""
        # Find the link in content and extract its text
        pattern = f'<a[^>]+href=[\'"].*?{re.escape(href)}.*?[\'"][^>]*>([^<]*)</a>'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
        
    def _is_link_relevant(self, link_text: str, url: str, keywords: List[str]) -> bool:
        """Check if a link is relevant to search keywords."""
        combined_text = f"{link_text} {url}".lower()
        
        # Check if any keyword appears in link text or URL
        for keyword in keywords:
            if keyword.lower() in combined_text:
                return True
                
        # Check for common relevant patterns
        relevant_patterns = [
            'detail', 'product', 'article', 'news', 'blog', 'post',
            'view', 'show', 'item', 'page', 'content'
        ]
        
        for pattern in relevant_patterns:
            if pattern in combined_text:
                return True
                
        return False
        
    def _rank_results(self, search_target: SearchTarget) -> List[SearchResult]:
        """Rank and filter search results."""
        # Sort by relevance score (descending)
        ranked_results = sorted(
            self.search_results,
            key=lambda r: (r.relevance_score, len(r.keywords_found), -r.depth),
            reverse=True
        )
        
        # Apply result limit
        if search_target.max_results:
            ranked_results = ranked_results[:search_target.max_results]
            
        return ranked_results
        
    def get_keyword_statistics(self) -> Dict[str, int]:
        """Get statistics about keyword occurrences."""
        keyword_stats = {}
        
        for result in self.search_results:
            for keyword in result.keywords_found:
                keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
                
        return keyword_stats
        
    def clear_results(self):
        """Clear search results and state."""
        self.search_results.clear()
        self.visited_urls.clear()
        self.keyword_patterns.clear()