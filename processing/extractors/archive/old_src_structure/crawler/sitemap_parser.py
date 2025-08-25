"""
Sitemap parsing and URL discovery functionality.
"""
import asyncio
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import aiohttp
import requests

logger = logging.getLogger(__name__)


class SitemapParser:
    """Parses XML sitemaps and discovers URLs for crawling."""
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """Initialize sitemap parser.
        
        Args:
            session: Optional aiohttp session for requests
        """
        self.session = session
        self._discovered_urls: Set[str] = set()
        self._sitemap_cache: Dict[str, List[str]] = {}
    
    async def discover_sitemaps(self, base_url: str) -> List[str]:
        """Discover sitemap URLs from a website.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            List of discovered sitemap URLs
        """
        discovered_sitemaps = []
        
        # Common sitemap locations
        common_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemaps.xml',
            '/sitemap/sitemap.xml',
            '/sitemaps/sitemap.xml'
        ]
        
        for path in common_paths:
            sitemap_url = urljoin(base_url, path)
            if await self._check_sitemap_exists(sitemap_url):
                discovered_sitemaps.append(sitemap_url)
                logger.info(f"Found sitemap: {sitemap_url}")
        
        # Check robots.txt for sitemap declarations
        robots_sitemaps = await self._get_sitemaps_from_robots(base_url)
        discovered_sitemaps.extend(robots_sitemaps)
        
        return list(set(discovered_sitemaps))  # Remove duplicates
    
    async def _check_sitemap_exists(self, sitemap_url: str) -> bool:
        """Check if a sitemap URL exists and is valid XML.
        
        Args:
            sitemap_url: URL to check
            
        Returns:
            True if sitemap exists and is valid
        """
        try:
            if self.session:
                async with self.session.get(sitemap_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Quick check if it's XML
                        return content.strip().startswith('<?xml') or '<urlset' in content
            else:
                response = requests.get(sitemap_url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    return content.strip().startswith('<?xml') or '<urlset' in content
        except Exception as e:
            logger.debug(f"Error checking sitemap {sitemap_url}: {e}")
        
        return False
    
    async def _get_sitemaps_from_robots(self, base_url: str) -> List[str]:
        """Extract sitemap URLs from robots.txt.
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            List of sitemap URLs found in robots.txt
        """
        robots_url = urljoin(base_url, '/robots.txt')
        sitemaps = []
        
        try:
            if self.session:
                async with self.session.get(robots_url) as response:
                    if response.status == 200:
                        content = await response.text()
            else:
                response = requests.get(robots_url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                else:
                    return sitemaps
            
            # Parse robots.txt for sitemap declarations
            for line in content.split('\n'):
                line = line.strip()
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemaps.append(sitemap_url)
                    logger.info(f"Found sitemap in robots.txt: {sitemap_url}")
        
        except Exception as e:
            logger.debug(f"Error reading robots.txt from {base_url}: {e}")
        
        return sitemaps
    
    async def parse_sitemap(self, sitemap_url: str) -> List[Dict[str, Any]]:
        """Parse a sitemap and extract URL information.
        
        Args:
            sitemap_url: URL of the sitemap to parse
            
        Returns:
            List of URL information dictionaries
        """
        # Check cache first
        if sitemap_url in self._sitemap_cache:
            logger.debug(f"Using cached sitemap data for {sitemap_url}")
            return self._sitemap_cache[sitemap_url]
        
        try:
            # Fetch sitemap content
            if self.session:
                async with self.session.get(sitemap_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch sitemap {sitemap_url}: {response.status}")
                        return []
                    content = await response.text()
            else:
                response = requests.get(sitemap_url, timeout=30)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch sitemap {sitemap_url}: {response.status_code}")
                    return []
                content = response.text
            
            # Parse XML
            urls = self._parse_sitemap_xml(content)
            
            # Cache results
            self._sitemap_cache[sitemap_url] = urls
            
            logger.info(f"Parsed {len(urls)} URLs from sitemap {sitemap_url}")
            return urls
        
        except Exception as e:
            logger.error(f"Error parsing sitemap {sitemap_url}: {e}")
            return []
    
    def _parse_sitemap_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse sitemap XML content.
        
        Args:
            xml_content: Raw XML content
            
        Returns:
            List of URL information
        """
        urls = []
        
        try:
            root = ET.fromstring(xml_content)
            
            # Handle sitemap index files
            if 'sitemapindex' in root.tag:
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc_elem = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_elem is not None and loc_elem.text:
                        # Recursively parse child sitemaps
                        child_urls = asyncio.create_task(self.parse_sitemap(loc_elem.text))
                        # Note: In real implementation, would await this properly
                        logger.info(f"Found child sitemap: {loc_elem.text}")
                return urls
            
            # Handle regular sitemap files
            for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                url_info = self._extract_url_info(url_elem)
                if url_info:
                    urls.append(url_info)
                    self._discovered_urls.add(url_info['url'])
        
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing sitemap XML: {e}")
        
        return urls
    
    def _extract_url_info(self, url_elem: ET.Element) -> Optional[Dict[str, Any]]:
        """Extract URL information from XML element.
        
        Args:
            url_elem: XML element containing URL data
            
        Returns:
            URL information dictionary or None
        """
        url_info = {}
        
        # Extract URL
        loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        if loc_elem is None or not loc_elem.text:
            return None
        
        url_info['url'] = loc_elem.text.strip()
        
        # Extract last modification date
        lastmod_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
        if lastmod_elem is not None and lastmod_elem.text:
            try:
                url_info['lastmod'] = datetime.fromisoformat(lastmod_elem.text.replace('Z', '+00:00'))
            except ValueError:
                url_info['lastmod'] = lastmod_elem.text
        
        # Extract change frequency
        changefreq_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
        if changefreq_elem is not None and changefreq_elem.text:
            url_info['changefreq'] = changefreq_elem.text.strip()
        
        # Extract priority
        priority_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
        if priority_elem is not None and priority_elem.text:
            try:
                url_info['priority'] = float(priority_elem.text)
            except ValueError:
                url_info['priority'] = 0.5  # Default priority
        else:
            url_info['priority'] = 0.5
        
        return url_info
    
    async def get_urls_by_pattern(self, sitemap_url: str, pattern: str) -> List[str]:
        """Get URLs from sitemap that match a specific pattern.
        
        Args:
            sitemap_url: Sitemap to search
            pattern: URL pattern to match (simple string matching)
            
        Returns:
            List of matching URLs
        """
        urls = await self.parse_sitemap(sitemap_url)
        return [url_info['url'] for url_info in urls if pattern in url_info['url']]
    
    async def get_recent_urls(self, sitemap_url: str, days: int = 7) -> List[str]:
        """Get URLs that were modified within the last N days.
        
        Args:
            sitemap_url: Sitemap to search
            days: Number of days to look back
            
        Returns:
            List of recently modified URLs
        """
        urls = await self.parse_sitemap(sitemap_url)
        recent_urls = []
        
        cutoff_date = datetime.now().replace(tzinfo=None) - timedelta(days=days)
        
        for url_info in urls:
            if 'lastmod' in url_info:
                try:
                    if isinstance(url_info['lastmod'], datetime):
                        lastmod = url_info['lastmod'].replace(tzinfo=None)
                        if lastmod >= cutoff_date:
                            recent_urls.append(url_info['url'])
                except (ValueError, TypeError):
                    continue
        
        return recent_urls
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get statistics about URL discovery.
        
        Returns:
            Dictionary with discovery statistics
        """
        return {
            'total_discovered': len(self._discovered_urls),
            'cached_sitemaps': len(self._sitemap_cache),
            'discovered_urls': list(self._discovered_urls)
        }
    
    def clear_cache(self):
        """Clear the sitemap cache."""
        self._sitemap_cache.clear()
        logger.info("Sitemap cache cleared")
