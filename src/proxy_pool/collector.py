"""
Proxy Collector Module for ECaDP Platform.

Collects proxies from various free and paid sources,
validates their functionality, and feeds them into the proxy pool.
"""

import asyncio
import aiohttp
import logging
import re
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Set, AsyncGenerator
from urllib.parse import urlparse
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ProxySource:
    """Configuration for a proxy source."""
    name: str
    url: str
    source_type: str  # 'api', 'webpage', 'file'
    format: str  # 'json', 'text', 'html'
    is_paid: bool = False
    rate_limit_seconds: int = 60
    requires_auth: bool = False
    auth_token: Optional[str] = None
    extraction_pattern: Optional[str] = None
    enabled: bool = True


@dataclass
class RawProxy:
    """Raw proxy data before validation."""
    ip: str
    port: int
    protocol: str = 'http'
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    anonymity: Optional[str] = None
    source: Optional[str] = None
    discovered_at: datetime = None
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.now()
    
    @property
    def proxy_url(self) -> str:
        """Get formatted proxy URL."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.ip}:{self.port}"
        return f"{self.protocol}://{self.ip}:{self.port}"
    
    def __hash__(self):
        return hash((self.ip, self.port, self.protocol))
    
    def __eq__(self, other):
        if not isinstance(other, RawProxy):
            return False
        return (self.ip, self.port, self.protocol) == (other.ip, other.port, other.protocol)


class ProxyCollector:
    """
    Collects proxies from multiple sources including free proxy lists,
    paid proxy services, and custom endpoints.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the proxy collector.
        
        Args:
            config: Configuration dictionary with source definitions
        """
        self.config = config or {}
        self.sources = self._load_sources()
        self.session = None
        self.collected_proxies: Set[RawProxy] = set()
        self.last_collection_times: Dict[str, datetime] = {}
        
    def _load_sources(self) -> List[ProxySource]:
        """Load proxy source configurations."""
        default_sources = [
            ProxySource(
                name="free-proxy-list",
                url="https://www.proxy-list.download/api/v1/get?type=http",
                source_type="api",
                format="text",
                rate_limit_seconds=300
            ),
            ProxySource(
                name="proxyrotator-api",
                url="https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
                source_type="api", 
                format="text",
                rate_limit_seconds=120
            ),
            ProxySource(
                name="spys-one",
                url="http://spys.one/en/http-proxy-list/",
                source_type="webpage",
                format="html",
                extraction_pattern=r'(\d+\.\d+\.\d+\.\d+):(\d+)',
                rate_limit_seconds=600
            ),
            ProxySource(
                name="hidemy-name",
                url="https://hidemy.name/en/proxy-list/?type=h#list",
                source_type="webpage", 
                format="html",
                extraction_pattern=r'(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)',
                rate_limit_seconds=600
            )
        ]
        
        # Add custom sources from config
        custom_sources = self.config.get('custom_sources', [])
        for source_config in custom_sources:
            default_sources.append(ProxySource(**source_config))
        
        return default_sources
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def collect_all(self) -> List[RawProxy]:
        """
        Collect proxies from all enabled sources.
        
        Returns:
            List of collected raw proxies
        """
        all_proxies = []
        
        for source in self.sources:
            if not source.enabled:
                continue
                
            try:
                # Check rate limiting
                if self._is_rate_limited(source):
                    logger.debug(f"Skipping {source.name} due to rate limiting")
                    continue
                
                logger.info(f"Collecting proxies from {source.name}")
                proxies = await self._collect_from_source(source)
                all_proxies.extend(proxies)
                
                # Update last collection time
                self.last_collection_times[source.name] = datetime.now()
                
                # Add small delay between sources
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Failed to collect from {source.name}: {e}")
        
        # Remove duplicates
        unique_proxies = list(set(all_proxies))
        logger.info(f"Collected {len(unique_proxies)} unique proxies from {len(self.sources)} sources")
        
        return unique_proxies
    
    async def _collect_from_source(self, source: ProxySource) -> List[RawProxy]:
        """Collect proxies from a single source."""
        if source.source_type == "api":
            return await self._collect_from_api(source)
        elif source.source_type == "webpage":
            return await self._collect_from_webpage(source)
        elif source.source_type == "file":
            return await self._collect_from_file(source)
        else:
            logger.warning(f"Unknown source type: {source.source_type}")
            return []
    
    async def _collect_from_api(self, source: ProxySource) -> List[RawProxy]:
        """Collect proxies from API endpoint."""
        try:
            headers = {}
            if source.requires_auth and source.auth_token:
                headers['Authorization'] = f'Bearer {source.auth_token}'
            
            async with self.session.get(source.url, headers=headers) as response:
                if response.status != 200:
                    logger.warning(f"API {source.name} returned status {response.status}")
                    return []
                
                content = await response.text()
                return self._parse_proxy_data(content, source)
                
        except Exception as e:
            logger.error(f"Error collecting from API {source.name}: {e}")
            return []
    
    async def _collect_from_webpage(self, source: ProxySource) -> List[RawProxy]:
        """Collect proxies from webpage."""
        try:
            async with self.session.get(source.url) as response:
                if response.status != 200:
                    logger.warning(f"Webpage {source.name} returned status {response.status}")
                    return []
                
                content = await response.text()
                return self._parse_proxy_data(content, source)
                
        except Exception as e:
            logger.error(f"Error collecting from webpage {source.name}: {e}")
            return []
    
    async def _collect_from_file(self, source: ProxySource) -> List[RawProxy]:
        """Collect proxies from local file."""
        try:
            with open(source.url, 'r') as f:
                content = f.read()
            return self._parse_proxy_data(content, source)
        except Exception as e:
            logger.error(f"Error collecting from file {source.name}: {e}")
            return []
    
    def _parse_proxy_data(self, content: str, source: ProxySource) -> List[RawProxy]:
        """Parse proxy data based on source format."""
        proxies = []
        
        try:
            if source.format == "json":
                data = json.loads(content)
                proxies = self._parse_json_proxies(data, source)
            elif source.format == "text":
                proxies = self._parse_text_proxies(content, source)
            elif source.format == "html":
                proxies = self._parse_html_proxies(content, source)
            else:
                logger.warning(f"Unknown format {source.format} for source {source.name}")
                
        except Exception as e:
            logger.error(f"Error parsing proxy data from {source.name}: {e}")
        
        return proxies
    
    def _parse_json_proxies(self, data: Dict, source: ProxySource) -> List[RawProxy]:
        """Parse JSON formatted proxy data."""
        proxies = []
        
        # Handle different JSON structures
        if isinstance(data, list):
            proxy_list = data
        elif 'proxies' in data:
            proxy_list = data['proxies']
        elif 'data' in data:
            proxy_list = data['data']
        else:
            proxy_list = [data]
        
        for proxy_data in proxy_list:
            try:
                if isinstance(proxy_data, str):
                    # Simple IP:PORT format
                    ip, port = proxy_data.split(':')
                    proxy = RawProxy(
                        ip=ip.strip(),
                        port=int(port.strip()),
                        source=source.name
                    )
                else:
                    # Dictionary format
                    proxy = RawProxy(
                        ip=proxy_data.get('ip', ''),
                        port=int(proxy_data.get('port', 0)),
                        protocol=proxy_data.get('protocol', 'http'),
                        username=proxy_data.get('username'),
                        password=proxy_data.get('password'),
                        country=proxy_data.get('country'),
                        anonymity=proxy_data.get('anonymity'),
                        source=source.name
                    )
                
                if self._is_valid_proxy(proxy):
                    proxies.append(proxy)
                    
            except Exception as e:
                logger.debug(f"Error parsing proxy entry: {e}")
                continue
        
        return proxies
    
    def _parse_text_proxies(self, content: str, source: ProxySource) -> List[RawProxy]:
        """Parse text formatted proxy data."""
        proxies = []
        
        # Common patterns for proxy lists
        patterns = [
            r'(\d+\.\d+\.\d+\.\d+):(\d+)',  # IP:PORT
            r'(\d+\.\d+\.\d+\.\d+)\s+(\d+)',  # IP PORT
            r'(\d+\.\d+\.\d+\.\d+)\t(\d+)',  # IP\tPORT
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        ip, port = match.groups()
                        proxy = RawProxy(
                            ip=ip.strip(),
                            port=int(port.strip()),
                            source=source.name
                        )
                        
                        if self._is_valid_proxy(proxy):
                            proxies.append(proxy)
                        break
                        
                    except Exception as e:
                        logger.debug(f"Error parsing proxy line '{line}': {e}")
                        continue
        
        return proxies
    
    def _parse_html_proxies(self, content: str, source: ProxySource) -> List[RawProxy]:
        """Parse HTML formatted proxy data."""
        proxies = []
        
        if source.extraction_pattern:
            pattern = source.extraction_pattern
        else:
            # Default HTML proxy extraction pattern
            pattern = r'(\d+\.\d+\.\d+\.\d+).*?(\d+)'
        
        matches = re.findall(pattern, content)
        
        for match in matches:
            try:
                if len(match) >= 2:
                    ip, port = match[0], match[1]
                    proxy = RawProxy(
                        ip=ip.strip(),
                        port=int(port.strip()),
                        source=source.name
                    )
                    
                    if self._is_valid_proxy(proxy):
                        proxies.append(proxy)
                        
            except Exception as e:
                logger.debug(f"Error parsing HTML proxy match {match}: {e}")
                continue
        
        return proxies
    
    def _is_valid_proxy(self, proxy: RawProxy) -> bool:
        """Validate basic proxy format."""
        try:
            # Validate IP format
            parts = proxy.ip.split('.')
            if len(parts) != 4:
                return False
            
            for part in parts:
                if not (0 <= int(part) <= 255):
                    return False
            
            # Validate port range
            if not (1 <= proxy.port <= 65535):
                return False
            
            # Exclude private/reserved IP ranges
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            # Private ranges: 10.x.x.x, 172.16-31.x.x, 192.168.x.x
            if first_octet == 10:
                return False
            if first_octet == 172 and 16 <= second_octet <= 31:
                return False
            if first_octet == 192 and second_octet == 168:
                return False
            
            # Localhost and reserved ranges
            if first_octet in [0, 127, 224, 240]:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _is_rate_limited(self, source: ProxySource) -> bool:
        """Check if source is rate limited."""
        last_time = self.last_collection_times.get(source.name)
        if not last_time:
            return False
        
        time_diff = datetime.now() - last_time
        return time_diff.total_seconds() < source.rate_limit_seconds
    
    async def collect_continuously(self, interval_minutes: int = 60) -> AsyncGenerator[List[RawProxy], None]:
        """
        Continuously collect proxies at specified intervals.
        
        Args:
            interval_minutes: Collection interval in minutes
            
        Yields:
            List of newly collected proxies
        """
        while True:
            try:
                new_proxies = await self.collect_all()
                if new_proxies:
                    yield new_proxies
                    
                # Wait for next collection
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in continuous collection: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def get_collection_stats(self) -> Dict[str, any]:
        """Get collection statistics."""
        stats = {
            'total_sources': len(self.sources),
            'enabled_sources': len([s for s in self.sources if s.enabled]),
            'last_collection_times': self.last_collection_times.copy(),
            'collected_proxies_count': len(self.collected_proxies)
        }
        
        return stats


# Backward compatibility alias
ProxyInfo = RawProxy