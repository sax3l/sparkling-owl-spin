import time
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Set, Optional, Any
import aiohttp
import asyncio
from src.crawler.url_frontier import URLFrontier
from src.crawler.robots_parser import RobotsParser
from src.crawler.link_extractor import extract_links
from src.crawler.template_detector import TemplateDetector
from src.anti_bot.policy_manager import PolicyManager
from src.scraper.transport import TransportManager

logger = logging.getLogger(__name__)

class SitemapGenerator:
    """Advanced sitemap generator with XML sitemap support and intelligent discovery."""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._should_close_session = session is None
        self._sitemap_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._discovered_urls: Set[str] = set()
        
    async def __aenter__(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._should_close_session and self.session:
            await self.session.close()

    async def discover_from_xml_sitemap(self, base_url: str) -> List[str]:
        """
        Discover and parse XML sitemaps for rapid URL initialization.
        This implements the first improvement from the analysis report.
        """
        logger.info(f"Discovering XML sitemaps for {base_url}")
        
        # Try common sitemap locations
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml'),
            urljoin(base_url, '/sitemaps.xml'),
        ]
        
        # Also check robots.txt for sitemap declarations
        robots_sitemaps = await self._get_sitemaps_from_robots(base_url)
        sitemap_urls.extend(robots_sitemaps)
        
        all_urls = []
        for sitemap_url in sitemap_urls:
            try:
                urls = await self._parse_xml_sitemap(sitemap_url)
                all_urls.extend(urls)
                logger.info(f"Discovered {len(urls)} URLs from {sitemap_url}")
            except Exception as e:
                logger.debug(f"Failed to parse sitemap {sitemap_url}: {e}")
                continue
                
        # Remove duplicates
        unique_urls = list(set(all_urls))
        logger.info(f"Total unique URLs discovered from XML sitemaps: {len(unique_urls)}")
        return unique_urls
    
    async def _get_sitemaps_from_robots(self, base_url: str) -> List[str]:
        """Extract sitemap URLs from robots.txt"""
        robots_url = urljoin(base_url, '/robots.txt')
        sitemaps = []
        
        try:
            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    content = await response.text()
                    for line in content.split('\n'):
                        line = line.strip()
                        if line.lower().startswith('sitemap:'):
                            sitemap_url = line[8:].strip()
                            sitemaps.append(sitemap_url)
                            logger.debug(f"Found sitemap in robots.txt: {sitemap_url}")
        except Exception as e:
            logger.debug(f"Error reading robots.txt from {base_url}: {e}")
        
        return sitemaps
    
    async def _parse_xml_sitemap(self, sitemap_url: str) -> List[str]:
        """Parse XML sitemap and extract URLs"""
        if sitemap_url in self._sitemap_cache:
            return [item['url'] for item in self._sitemap_cache[sitemap_url]]
            
        try:
            async with self.session.get(sitemap_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch sitemap {sitemap_url}: {response.status}")
                    return []
                    
                content = await response.text()
                
            # Parse XML
            urls = []
            try:
                root = ET.fromstring(content)
                
                # Handle sitemap index files (contains references to other sitemaps)
                if 'sitemapindex' in root.tag:
                    for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                        loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc is not None and loc.text:
                            # Recursively parse child sitemaps
                            child_urls = await self._parse_xml_sitemap(loc.text)
                            urls.extend(child_urls)
                    return urls
                
                # Handle regular sitemap files
                for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                    loc = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and loc.text:
                        url_info = {
                            'url': loc.text.strip(),
                            'lastmod': None,
                            'changefreq': None,
                            'priority': 0.5
                        }
                        
                        # Extract additional metadata
                        lastmod = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                        if lastmod is not None and lastmod.text:
                            url_info['lastmod'] = lastmod.text.strip()
                            
                        changefreq = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
                        if changefreq is not None and changefreq.text:
                            url_info['changefreq'] = changefreq.text.strip()
                            
                        priority = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                        if priority is not None and priority.text:
                            try:
                                url_info['priority'] = float(priority.text)
                            except ValueError:
                                pass
                                
                        urls.append(url_info['url'])
                        
            except ET.ParseError as e:
                logger.error(f"XML parsing error for {sitemap_url}: {e}")
                return []
                
            # Cache the results
            self._sitemap_cache[sitemap_url] = [{'url': url} for url in urls]
            return urls
            
        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
            return []

    async def generate_intelligent_sitemap(
        self, 
        start_url: str, 
        max_depth: int = 3,
        max_urls: int = 1000,
        strategy: str = "breadth_first"
    ) -> List[str]:
        """
        Generate sitemap using intelligent crawling with both BFS and DFS support.
        Combines XML sitemap discovery with intelligent link following.
        """
        logger.info(f"Generating intelligent sitemap for {start_url}")
        
        # First try to get URLs from XML sitemaps for quick initialization
        xml_urls = await self.discover_from_xml_sitemap(start_url)
        if xml_urls:
            logger.info(f"Using {len(xml_urls)} URLs from XML sitemaps as seed")
            return xml_urls[:max_urls]
        
        # Fall back to intelligent crawling
        logger.info("No XML sitemaps found, using intelligent crawling")
        return await self._intelligent_crawl(start_url, max_depth, max_urls, strategy)
    
    async def _intelligent_crawl(
        self, 
        start_url: str, 
        max_depth: int,
        max_urls: int, 
        strategy: str
    ) -> List[str]:
        """Intelligent crawling with BFS/DFS strategy selection"""
        visited = set()
        discovered_urls = []
        
        if strategy == "breadth_first":
            queue = [(start_url, 0)]  # (url, depth)
        else:  # depth_first
            queue = [(start_url, 0)]
            
        domain = urlparse(start_url).netloc
        
        while queue and len(discovered_urls) < max_urls:
            if strategy == "breadth_first":
                current_url, depth = queue.pop(0)  # FIFO for BFS
            else:
                current_url, depth = queue.pop()   # LIFO for DFS
                
            if current_url in visited or depth > max_depth:
                continue
                
            visited.add(current_url)
            discovered_urls.append(current_url)
            
            if depth < max_depth:
                try:
                    # Extract links from current page
                    links = await self._extract_page_links(current_url, domain)
                    for link in links:
                        if link not in visited:
                            queue.append((link, depth + 1))
                except Exception as e:
                    logger.debug(f"Failed to extract links from {current_url}: {e}")
                    continue
        
        logger.info(f"Intelligent crawl discovered {len(discovered_urls)} URLs")
        return discovered_urls
    
    async def _extract_page_links(self, url: str, domain: str) -> List[str]:
        """Extract links from a page, filtering for same domain"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return []
                    
                html = await response.text()
                
            # Use existing link extractor with domain filtering
            links = extract_links(html, base_url=url)
            
            # Filter for same domain only
            same_domain_links = []
            for link in links:
                parsed = urlparse(link)
                if parsed.netloc == domain or parsed.netloc == '':
                    if parsed.netloc == '':
                        # Convert relative URLs to absolute
                        link = urljoin(url, link)
                    same_domain_links.append(link)
            
            return same_domain_links
            
        except Exception as e:
            logger.debug(f"Error extracting links from {url}: {e}")
            return []

    def get_sitemap_stats(self) -> Dict[str, Any]:
        """Get statistics about discovered sitemaps and URLs"""
        total_sitemaps = len(self._sitemap_cache)
        total_urls = len(self._discovered_urls)
        
        return {
            'total_sitemaps_parsed': total_sitemaps,
            'total_urls_discovered': total_urls,
            'cache_size': total_sitemaps,
            'cached_sitemaps': list(self._sitemap_cache.keys())
        }
    
    def clear_cache(self):
        """Clear the sitemap cache"""
        self._sitemap_cache.clear()
        self._discovered_urls.clear()
        logger.info("Sitemap cache cleared")


class Crawler:
    def __init__(
        self, 
        frontier: URLFrontier, 
        robots_parser: RobotsParser, 
        policy_manager: PolicyManager, 
        transport_manager: TransportManager,
        template_detector: TemplateDetector
    ):
        self.frontier = frontier
        self.robots_parser = robots_parser
        self.policy_manager = policy_manager
        self.transport_manager = transport_manager
        self.template_detector = template_detector

    def crawl_domain(self, start_url: str, max_urls: int = 1000):
        """
        Performs a crawl of a domain starting from a seed URL, respecting all policies.
        """
        self.frontier.clear()
        self.frontier.add_url(start_url)
        crawled_count = 0
        
        while crawled_count < max_urls:
            url_to_crawl = self.frontier.get_next_url()
            if not url_to_crawl:
                logger.info("Frontier is empty. Crawl finished.")
                break

            domain = urlparse(url_to_crawl).netloc
            policy = self.policy_manager.get_policy(domain)
            user_agent = "ECaDP/0.1 (Ethical Crawler; +http://example.com/bot)"

            if not self.robots_parser.can_fetch(url_to_crawl, user_agent):
                logger.info(f"Skipping {url_to_crawl} due to robots.txt")
                self.frontier.mark_as_visited(url_to_crawl)
                continue

            if time.time() < policy.backoff_until:
                logger.warning(f"Domain {domain} is in backoff. Re-queueing {url_to_crawl}")
                self.frontier.add_url(url_to_crawl)
                time.sleep(1) # Avoid a tight loop
                continue

            logger.info(f"Crawling: {url_to_crawl} with delay {policy.current_delay_seconds:.2f}s")
            time.sleep(policy.current_delay_seconds)

            html_content, status_code = self.transport_manager.fetch(url_to_crawl, policy)
            self.frontier.mark_as_visited(url_to_crawl)
            crawled_count += 1

            if status_code == 200:
                self.policy_manager.update_on_success(domain)
                
                template_type = self.template_detector.classify(url_to_crawl)
                logger.info(f"URL classified as template: {template_type or 'None'}")
                # TODO: Write to sitemap database layer here

                new_links = extract_links(url_to_crawl, html_content)
                for link in new_links:
                    # Only add links within the same domain for this simple crawler
                    if urlparse(link).netloc == domain:
                        self.frontier.add_url(link)
                logger.info(f"Found {len(new_links)} new links on {url_to_crawl}")
            else:
                self.policy_manager.update_on_failure(domain, status_code)
                logger.error(f"Failed to fetch {url_to_crawl} with status code {status_code}")


# Backward compatibility alias
SitemapGenerator = Crawler


def crawl_site(seed_url: str, max_pages: int = 100):
    """Convenience function to crawl a site and generate sitemap."""
    crawler = Crawler(seed_url=seed_url, max_pages=max_pages)
    return crawler.crawl()