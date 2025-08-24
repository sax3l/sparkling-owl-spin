"""
Advanced Proxy Fetchers
======================

Modernized async version of jhao104/proxy_pool ProxyFetcher system.
Baserat på analys av ProxyFetcher klass med freeProxy01-05 metoder.

Key improvements:
- Async/await support
- Better error handling  
- Configurable sources
- Rate limiting
- Retry logic
"""

import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from utils.logger import get_logger
from .enhanced_manager import ProxyInfo, ProxyStatus

logger = get_logger(__name__)


@dataclass
class ProxySource:
    """Configuration for a proxy source."""
    name: str
    url: str
    parser_type: str
    headers: Dict[str, str] = None
    rate_limit: float = 1.0  # seconds between requests
    enabled: bool = True
    timeout: int = 30
    

class AdvancedProxyFetcher:
    """
    Advanced async proxy fetcher system.
    
    Inspired by ProxyFetcher from jhao104/proxy_pool but modernized:
    - Multiple async sources
    - Configurable parsers
    - Rate limiting
    - Better error handling
    """
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Built-in proxy sources (inspired by original freeProxy methods)
        self.sources = [
            ProxySource(
                name="FreeProxyList",
                url="https://www.free-proxy-list.net/", 
                parser_type="html_table",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            ),
            ProxySource(
                name="ProxyNova",
                url="https://www.proxynova.com/proxy-server-list/",
                parser_type="html_table", 
                rate_limit=2.0
            ),
            ProxySource(
                name="SpysOne",
                url="https://spys.one/free-proxy-list/",
                parser_type="html_custom",
                rate_limit=3.0
            ),
            ProxySource(
                name="ProxyDB",
                url="http://proxydb.net/",
                parser_type="json",
                enabled=False  # API might need key
            ),
            ProxySource(
                name="FreeProxy",
                url="https://api.proxyscrape.com/v2/",
                parser_type="api",
                rate_limit=0.5
            )
        ]
        
        # Statistics
        self.stats = {
            "fetches_completed": 0,
            "proxies_found": 0,
            "errors_encountered": 0,
            "last_fetch": None
        }
        
    async def initialize(self):
        """Initialize the fetcher."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        
        logger.info("✅ Advanced Proxy Fetcher initialized")
        
    async def close(self):
        """Close the fetcher session."""
        if self.session:
            await self.session.close()
            
    async def fetch_all_sources(self) -> List[ProxyInfo]:
        """
        Fetch proxies from all enabled sources.
        Enhanced version of original batch fetching.
        """
        logger.info("🔄 Fetching proxies from all sources...")
        
        enabled_sources = [source for source in self.sources if source.enabled]
        
        # Create semaphore for concurrent fetching
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_with_semaphore(source):
            async with semaphore:
                return await self._fetch_from_source(source)
                
        # Fetch from all sources concurrently
        results = await asyncio.gather(
            *[fetch_with_semaphore(source) for source in enabled_sources],
            return_exceptions=True
        )
        
        # Combine results
        all_proxies = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Source {enabled_sources[i].name} failed: {result}")
                self.stats["errors_encountered"] += 1
            elif isinstance(result, list):
                all_proxies.extend(result)
                logger.info(f"✅ {enabled_sources[i].name}: {len(result)} proxies")
                
        # Remove duplicates
        unique_proxies = self._deduplicate_proxies(all_proxies)
        
        self.stats.update({
            "fetches_completed": self.stats["fetches_completed"] + 1,
            "proxies_found": len(unique_proxies),
            "last_fetch": datetime.now()
        })
        
        logger.info(f"✅ Fetched {len(unique_proxies)} unique proxies from {len(enabled_sources)} sources")
        return unique_proxies
        
    async def _fetch_from_source(self, source: ProxySource) -> List[ProxyInfo]:
        """Fetch proxies from a single source."""
        try:
            logger.debug(f"📥 Fetching from {source.name}...")
            
            # Rate limiting
            if source.rate_limit > 0:
                await asyncio.sleep(source.rate_limit)
                
            # Make request
            headers = source.headers or {}
            async with self.session.get(source.url, headers=headers) as response:
                if response.status != 200:
                    logger.warning(f"❌ {source.name} returned status {response.status}")
                    return []
                    
                content = await response.text()
                
            # Parse based on parser type
            if source.parser_type == "html_table":
                proxies = self._parse_html_table(content, source.name)
            elif source.parser_type == "html_custom":
                proxies = self._parse_html_custom(content, source.name) 
            elif source.parser_type == "json":
                json_data = await response.json()
                proxies = self._parse_json(json_data, source.name)
            elif source.parser_type == "api":
                proxies = await self._fetch_api_proxies(source)
            else:
                logger.warning(f"❌ Unknown parser type: {source.parser_type}")
                return []
                
            logger.debug(f"✅ {source.name}: extracted {len(proxies)} proxies")
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Error fetching from {source.name}: {e}")
            return []
            
    def _parse_html_table(self, html: str, source_name: str) -> List[ProxyInfo]:
        """
        Parse HTML table format (like free-proxy-list.net).
        Enhanced version of original HTML parsing.
        """
        proxies = []
        
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find proxy table (common patterns)
            table = soup.find('table', {'id': 'proxylisttable'}) or soup.find('table', class_='table')
            
            if not table:
                logger.warning(f"❌ {source_name}: No proxy table found")
                return []
                
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    try:
                        host = cols[0].text.strip()
                        port = int(cols[1].text.strip())
                        
                        # Extract additional info if available
                        protocol = "http"
                        country = None
                        anonymity = None
                        
                        if len(cols) > 3:
                            country = cols[2].text.strip()
                        if len(cols) > 4:
                            anonymity = cols[3].text.strip()
                        if len(cols) > 6:
                            https_support = cols[6].text.strip().lower()
                            if https_support == "yes":
                                protocol = "https"
                                
                        proxy = ProxyInfo(
                            host=host,
                            port=port,
                            protocol=protocol,
                            source=source_name,
                            country=country,
                            anonymity=anonymity
                        )
                        
                        proxies.append(proxy)
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"❌ {source_name}: Failed to parse row: {e}")
                        continue
                        
        except ImportError:
            logger.error("❌ BeautifulSoup not available for HTML parsing")
        except Exception as e:
            logger.error(f"❌ {source_name}: HTML parsing error: {e}")
            
        return proxies
        
    def _parse_html_custom(self, html: str, source_name: str) -> List[ProxyInfo]:
        """Parse custom HTML format using regex."""
        proxies = []
        
        try:
            # Generic IP:PORT pattern
            ip_port_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
            matches = re.findall(ip_port_pattern, html)
            
            for host, port in matches:
                try:
                    proxy = ProxyInfo(
                        host=host,
                        port=int(port),
                        protocol="http",
                        source=source_name
                    )
                    proxies.append(proxy)
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.error(f"❌ {source_name}: Custom HTML parsing error: {e}")
            
        return proxies
        
    def _parse_json(self, json_data: Dict[str, Any], source_name: str) -> List[ProxyInfo]:
        """Parse JSON format."""
        proxies = []
        
        try:
            # Handle different JSON structures
            if 'proxies' in json_data:
                proxy_list = json_data['proxies']
            elif 'data' in json_data:
                proxy_list = json_data['data']
            elif isinstance(json_data, list):
                proxy_list = json_data
            else:
                logger.warning(f"❌ {source_name}: Unknown JSON structure")
                return []
                
            for item in proxy_list:
                try:
                    host = item.get('ip', item.get('host'))
                    port = int(item.get('port', 0))
                    protocol = item.get('protocol', item.get('type', 'http'))
                    country = item.get('country')
                    
                    if host and port:
                        proxy = ProxyInfo(
                            host=host,
                            port=port,
                            protocol=protocol.lower(),
                            source=source_name,
                            country=country
                        )
                        proxies.append(proxy)
                        
                except (ValueError, KeyError) as e:
                    logger.debug(f"❌ {source_name}: Failed to parse JSON item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ {source_name}: JSON parsing error: {e}")
            
        return proxies
        
    async def _fetch_api_proxies(self, source: ProxySource) -> List[ProxyInfo]:
        """Fetch from API sources (like ProxyScrape)."""
        proxies = []
        
        try:
            # Build API URL for ProxyScrape format
            api_url = source.url + "?request=get&format=json&protocol=http"
            
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        for item in data:
                            try:
                                proxy = ProxyInfo(
                                    host=item['ip'],
                                    port=int(item['port']),
                                    protocol="http",
                                    source=source.name,
                                    country=item.get('country')
                                )
                                proxies.append(proxy)
                            except (KeyError, ValueError):
                                continue
                                
        except Exception as e:
            logger.error(f"❌ {source.name}: API fetch error: {e}")
            
        return proxies
        
    def _deduplicate_proxies(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicate proxies."""
        seen_keys = set()
        unique_proxies = []
        
        for proxy in proxies:
            if proxy.key not in seen_keys:
                seen_keys.add(proxy.key)
                unique_proxies.append(proxy)
                
        return unique_proxies
        
    def add_custom_source(self, source: ProxySource):
        """Add a custom proxy source."""
        self.sources.append(source)
        logger.info(f"➕ Added custom source: {source.name}")
        
    def disable_source(self, source_name: str):
        """Disable a proxy source."""
        for source in self.sources:
            if source.name == source_name:
                source.enabled = False
                logger.info(f"⏸️ Disabled source: {source_name}")
                return
        logger.warning(f"❌ Source not found: {source_name}")
        
    def get_stats(self) -> Dict[str, Any]:
        """Get fetcher statistics."""
        return {
            **self.stats,
            "enabled_sources": len([s for s in self.sources if s.enabled]),
            "total_sources": len(self.sources)
        }


# Factory function for easy integration
async def create_proxy_fetcher(max_concurrent: int = 5) -> AdvancedProxyFetcher:
    """Factory function to create and initialize proxy fetcher."""
    fetcher = AdvancedProxyFetcher(max_concurrent=max_concurrent)
    await fetcher.initialize()
    return fetcher


# Usage example
async def example_usage():
    """Example of using the Advanced Proxy Fetcher."""
    
    # Create fetcher
    fetcher = await create_proxy_fetcher()
    
    try:
        # Fetch proxies from all sources
        proxies = await fetcher.fetch_all_sources()
        
        print(f"✅ Fetched {len(proxies)} total proxies")
        
        # Show sample proxies
        for proxy in proxies[:5]:
            print(f"  📡 {proxy.key} ({proxy.source})")
            
        # Show stats
        stats = fetcher.get_stats()
        print(f"📊 Fetcher stats: {stats}")
        
    finally:
        await fetcher.close()


if __name__ == "__main__":
    asyncio.run(example_usage())
