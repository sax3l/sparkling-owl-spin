#!/usr/bin/env python3
"""
Manual Proxy Pool Implementation Guide
=====================================

Baserat på djupanalysen av jhao104/proxy_pool, här är en steg-för-steg guide
för att manuellt implementera de bästa delarna i vårt Sparkling Owl Spin system.

Analysens resultat:
- 37 Python filer, 14 klasser, 109 funktioner
- Välorganiserad arkitektur: api/, db/, fetcher/, handler/, helper/
- Databasstöd (Redis/SSDB), men INGET async support
- Nyckelklasser: ProxyFetcher, DbClient, ProxyHandler
"""

import os
import sys
from pathlib import Path
from datetime import datetime


class ProxyPoolImplementationGuide:
    """Guide för manuell implementation av proxy pool funktionalitet."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def create_implementation_plan(self):
        """Skapa detaljerad implementationsplan."""
        
        print("🎯 PROXY POOL IMPLEMENTATION PLAN")
        print("=" * 50)
        print()
        
        print("📊 ANALYS SAMMANFATTNING:")
        print("• Repository: jhao104/proxy_pool")
        print("• Arkitektur: Modulär med api/, db/, fetcher/, handler/")  
        print("• Nyckelklasser: ProxyFetcher, DbClient, ProxyHandler")
        print("• Databas: Redis/SSDB support")
        print("• VARNING: Inget async support - behöver moderniseras")
        print()
        
        steps = [
            {
                "step": 1,
                "title": "Skapa Enhanced Proxy Manager",
                "files": ["src/proxy_pool/enhanced_manager.py"],
                "extract_from": "Kombinera DbClient + ProxyHandler koncept",
                "description": "Moderniserad async proxy pool manager",
                "time": "2-3 timmar"
            },
            {
                "step": 2, 
                "title": "Implementera Advanced Fetcher System",
                "files": ["src/proxy_pool/advanced_fetchers.py"],
                "extract_from": "ProxyFetcher klass med alla freeProxy metoder",
                "description": "Async proxy fetching från multiple källor", 
                "time": "3-4 timmar"
            },
            {
                "step": 3,
                "title": "Skapa Async Database Layer", 
                "files": ["src/proxy_pool/async_storage.py"],
                "extract_from": "RedisClient + SsdbClient funktionalitet",
                "description": "Async Redis/memory storage för proxies",
                "time": "2-3 timmar"
            },
            {
                "step": 4,
                "title": "Implementera API Endpoints",
                "files": ["src/webapp/api/proxy_api.py"],
                "extract_from": "proxyApi.py REST endpoints",
                "description": "FastAPI endpoints för proxy management",
                "time": "2 timmar"
            },
            {
                "step": 5,
                "title": "Skapa Configuration System",
                "files": ["src/proxy_pool/config.py"],
                "extract_from": "ConfigHandler klass",
                "description": "Centraliserad konfiguration",
                "time": "1 timme"
            }
        ]
        
        for step_info in steps:
            print(f"📋 STEG {step_info['step']}: {step_info['title']}")
            print(f"   📂 Filer: {', '.join(step_info['files'])}")
            print(f"   🔄 Extrahera från: {step_info['extract_from']}")
            print(f"   📝 Beskrivning: {step_info['description']}")
            print(f"   ⏱️  Tid: {step_info['time']}")
            print()
            
        return steps
        
    def create_enhanced_proxy_manager(self):
        """Skapa förbättrad proxy manager baserat på proxy_pool analys."""
        
        target_file = self.project_root / "src" / "proxy_pool" / "enhanced_manager.py"
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        code = '''"""
Enhanced Proxy Pool Manager
===========================

Moderniserad async version av jhao104/proxy_pool arkitekturen.
Baserat på analys av DbClient och ProxyHandler klasser.

Key improvements:
- Async/await support 
- Better error handling
- Metrics integration
- Modern Python patterns
"""

import asyncio
import aioredis
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum

from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


class ProxyStatus(Enum):
    """Proxy status states."""
    UNKNOWN = "unknown"
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    BLOCKED = "blocked"


@dataclass
class ProxyInfo:
    """Enhanced proxy information."""
    host: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    status: ProxyStatus = ProxyStatus.UNKNOWN
    last_checked: Optional[datetime] = None
    success_rate: float = 0.0
    response_time: float = 0.0
    source: str = "unknown"
    country: Optional[str] = None
    anonymity: Optional[str] = None
    
    @property
    def url(self) -> str:
        """Get proxy URL."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def is_active(self) -> bool:
        """Check if proxy is active."""
        return self.status == ProxyStatus.ACTIVE
        
    @property
    def key(self) -> str:
        """Unique key for proxy."""
        return f"{self.host}:{self.port}"


class EnhancedProxyManager:
    """
    Enhanced async proxy pool manager.
    
    Inspired by jhao104/proxy_pool but modernized with:
    - Async/await support
    - Better validation
    - Metrics integration 
    - Memory + Redis storage
    """
    
    def __init__(self, redis_url: Optional[str] = None, metrics: Optional[MetricsCollector] = None):
        self.redis_url = redis_url
        self.metrics = metrics or MetricsCollector()
        self.redis_client: Optional[aioredis.Redis] = None
        
        # In-memory storage as fallback
        self._proxy_pool: Dict[str, ProxyInfo] = {}
        self._active_proxies: Set[str] = set()
        self._testing_proxies: Set[str] = set()
        
        # Configuration
        self.max_pool_size = 1000
        self.validation_interval = 300  # 5 minutes
        self.max_test_concurrent = 10
        
        # Stats
        self._stats = {
            "total_proxies": 0,
            "active_proxies": 0,
            "tests_completed": 0,
            "success_rate": 0.0
        }
        
    async def initialize(self):
        """Initialize the proxy manager."""
        logger.info("🔄 Initializing Enhanced Proxy Manager...")
        
        # Setup Redis connection if URL provided
        if self.redis_url:
            try:
                self.redis_client = aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("✅ Connected to Redis")
            except Exception as e:
                logger.warning(f"❌ Redis connection failed: {e}, using memory storage")
                self.redis_client = None
                
        # Load existing proxies
        await self._load_existing_proxies()
        
        logger.info(f"✅ Proxy Manager initialized with {len(self._proxy_pool)} proxies")
        
    async def add_proxy(self, proxy_info: ProxyInfo) -> bool:
        """
        Add proxy to pool.
        Equivalent to DbClient.put() from original.
        """
        try:
            key = proxy_info.key
            
            # Check if already exists
            if key in self._proxy_pool:
                logger.debug(f"Proxy {key} already exists, updating...")
                
            # Add to memory pool
            self._proxy_pool[key] = proxy_info
            
            # Add to Redis if available
            if self.redis_client:
                await self.redis_client.hset(
                    "proxy_pool", 
                    key, 
                    str(asdict(proxy_info))
                )
                
            # Update stats
            self._update_stats()
            
            logger.debug(f"➕ Added proxy: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add proxy {proxy_info.key}: {e}")
            return False
            
    async def get_proxy(self, protocol: Optional[str] = None, country: Optional[str] = None) -> Optional[ProxyInfo]:
        """
        Get random active proxy.
        Equivalent to DbClient.get() from original.
        """
        try:
            # Filter active proxies
            candidates = [
                proxy for proxy in self._proxy_pool.values()
                if proxy.is_active and (not protocol or proxy.protocol == protocol)
                and (not country or proxy.country == country)
            ]
            
            if not candidates:
                logger.warning("❌ No active proxies available")
                return None
                
            # Select based on success rate (weighted random)
            weights = [max(proxy.success_rate, 0.1) for proxy in candidates]
            selected = random.choices(candidates, weights=weights)[0]
            
            # Update metrics
            self.metrics.counter("proxy_requests", 1)
            
            logger.debug(f"✅ Selected proxy: {selected.key} (success_rate: {selected.success_rate:.2f})")
            return selected
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxy: {e}")
            return None
            
    async def remove_proxy(self, proxy_key: str) -> bool:
        """Remove proxy from pool."""
        try:
            # Remove from memory
            if proxy_key in self._proxy_pool:
                del self._proxy_pool[proxy_key]
                
            # Remove from sets
            self._active_proxies.discard(proxy_key)
            self._testing_proxies.discard(proxy_key)
            
            # Remove from Redis
            if self.redis_client:
                await self.redis_client.hdel("proxy_pool", proxy_key)
                
            # Update stats  
            self._update_stats()
            
            logger.debug(f"➖ Removed proxy: {proxy_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove proxy {proxy_key}: {e}")
            return False
            
    async def validate_proxy(self, proxy_info: ProxyInfo, test_url: str = "http://httpbin.org/ip") -> bool:
        """
        Validate proxy by making test request.
        Enhanced version of original validation logic.
        """
        import aiohttp
        import time
        
        try:
            start_time = time.time()
            
            proxy_url = proxy_info.url
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy_url) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        # Update proxy stats
                        proxy_info.status = ProxyStatus.ACTIVE
                        proxy_info.last_checked = datetime.now()
                        proxy_info.response_time = response_time
                        
                        # Calculate success rate (simple moving average)
                        old_rate = proxy_info.success_rate
                        proxy_info.success_rate = (old_rate * 0.8) + (1.0 * 0.2)
                        
                        # Add to active set
                        self._active_proxies.add(proxy_info.key)
                        
                        logger.debug(f"✅ Proxy {proxy_info.key} validated in {response_time:.2f}s")
                        return True
                        
        except Exception as e:
            logger.debug(f"❌ Proxy {proxy_info.key} validation failed: {e}")
            
        # Mark as inactive on failure
        proxy_info.status = ProxyStatus.INACTIVE
        proxy_info.last_checked = datetime.now()
        
        # Update success rate
        old_rate = proxy_info.success_rate
        proxy_info.success_rate = (old_rate * 0.8) + (0.0 * 0.2)
        
        # Remove from active set
        self._active_proxies.discard(proxy_info.key)
        
        return False
        
    async def validate_all_proxies(self):
        """
        Validate all proxies in pool.
        Enhanced version of original batch validation.
        """
        logger.info(f"🔄 Starting validation of {len(self._proxy_pool)} proxies...")
        
        # Create semaphore to limit concurrent tests
        semaphore = asyncio.Semaphore(self.max_test_concurrent)
        
        async def validate_with_semaphore(proxy_info):
            async with semaphore:
                await self.validate_proxy(proxy_info)
                
        # Run validations concurrently
        tasks = [validate_with_semaphore(proxy) for proxy in self._proxy_pool.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update stats
        self._update_stats()
        
        active_count = len(self._active_proxies)
        total_count = len(self._proxy_pool)
        success_rate = (active_count / total_count) * 100 if total_count > 0 else 0
        
        logger.info(f"✅ Validation complete: {active_count}/{total_count} active ({success_rate:.1f}%)")
        
    async def cleanup_inactive_proxies(self, max_inactive_hours: int = 24):
        """Remove old inactive proxies."""
        cutoff_time = datetime.now() - timedelta(hours=max_inactive_hours)
        
        to_remove = []
        for key, proxy in self._proxy_pool.items():
            if (proxy.status == ProxyStatus.INACTIVE and 
                proxy.last_checked and 
                proxy.last_checked < cutoff_time):
                to_remove.append(key)
                
        for key in to_remove:
            await self.remove_proxy(key)
            
        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} inactive proxies")
            
    async def get_stats(self) -> Dict[str, any]:
        """Get pool statistics."""
        active_proxies = [p for p in self._proxy_pool.values() if p.is_active]
        
        avg_response_time = 0.0
        if active_proxies:
            avg_response_time = sum(p.response_time for p in active_proxies) / len(active_proxies)
            
        return {
            "total_proxies": len(self._proxy_pool),
            "active_proxies": len(active_proxies),
            "inactive_proxies": len(self._proxy_pool) - len(active_proxies),
            "average_response_time": avg_response_time,
            "success_rate": sum(p.success_rate for p in active_proxies) / len(active_proxies) if active_proxies else 0.0,
            "protocols": list(set(p.protocol for p in self._proxy_pool.values())),
            "countries": list(set(p.country for p in self._proxy_pool.values() if p.country))
        }
        
    async def _load_existing_proxies(self):
        """Load existing proxies from Redis."""
        if not self.redis_client:
            return
            
        try:
            proxy_data = await self.redis_client.hgetall("proxy_pool")
            for key, data in proxy_data.items():
                # Parse stored proxy data (simplified)
                # In real implementation, properly deserialize JSON
                pass
                
        except Exception as e:
            logger.warning(f"❌ Failed to load existing proxies: {e}")
            
    def _update_stats(self):
        """Update internal statistics."""
        active_count = len([p for p in self._proxy_pool.values() if p.is_active])
        
        self._stats.update({
            "total_proxies": len(self._proxy_pool),
            "active_proxies": active_count,
            "success_rate": (active_count / len(self._proxy_pool)) * 100 if self._proxy_pool else 0.0
        })
        
        # Send metrics
        self.metrics.counter("proxy_pool_total", len(self._proxy_pool))
        self.metrics.counter("proxy_pool_active", active_count)
        

# Helper functions for easy integration
async def create_proxy_manager(redis_url: Optional[str] = None) -> EnhancedProxyManager:
    """Factory function to create and initialize proxy manager."""
    manager = EnhancedProxyManager(redis_url=redis_url)
    await manager.initialize()
    return manager


# Usage example
async def example_usage():
    """Example of how to use the Enhanced Proxy Manager."""
    
    # Create manager
    manager = await create_proxy_manager()
    
    # Add some test proxies
    test_proxies = [
        ProxyInfo("127.0.0.1", 8080, "http", source="manual"),
        ProxyInfo("127.0.0.1", 3128, "http", source="manual"),
    ]
    
    for proxy in test_proxies:
        await manager.add_proxy(proxy)
        
    # Validate all proxies
    await manager.validate_all_proxies()
    
    # Get a proxy for use
    proxy = await manager.get_proxy()
    if proxy:
        print(f"✅ Got proxy: {proxy.url}")
        
    # Get statistics
    stats = await manager.get_stats()
    print(f"📊 Pool stats: {stats}")


if __name__ == "__main__":
    asyncio.run(example_usage())
'''

        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(code)
            
        print(f"✅ Created: {target_file}")
        return target_file
        
    def create_advanced_fetchers(self):
        """Skapa förbättrat fetcher system baserat på ProxyFetcher."""
        
        target_file = self.project_root / "src" / "proxy_pool" / "advanced_fetchers.py"
        
        code = '''"""
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
            ip_port_pattern = r'(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}):(\\d{2,5})'
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
'''

        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(code)
            
        print(f"✅ Created: {target_file}")
        return target_file
        
    def create_async_storage(self):
        """Skapa async storage layer baserat på RedisClient/SsdbClient."""
        
        target_file = self.project_root / "src" / "proxy_pool" / "async_storage.py"
        
        code = '''"""
Async Proxy Storage Layer
========================

Modernized async version of jhao104/proxy_pool storage system.
Baserat på analys av RedisClient och SsdbClient klasser.

Key improvements:
- Async Redis support
- Memory fallback
- Better error handling
- Serialization support
"""

import asyncio
import json
import pickle
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import asdict

try:
    import aioredis
except ImportError:
    aioredis = None

from utils.logger import get_logger
from .enhanced_manager import ProxyInfo, ProxyStatus

logger = get_logger(__name__)


class AsyncProxyStorage:
    """
    Async proxy storage system.
    
    Inspired by RedisClient from jhao104/proxy_pool but async:
    - Redis primary storage
    - Memory fallback
    - Serialization handling
    """
    
    def __init__(self, redis_url: Optional[str] = None, key_prefix: str = "proxy_pool"):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Memory storage as fallback
        self._memory_storage: Dict[str, str] = {}
        self._memory_sets: Dict[str, Set[str]] = {}
        
        self.use_redis = aioredis is not None and redis_url is not None
        
    async def initialize(self):
        """Initialize storage connections."""
        if self.use_redis:
            try:
                self.redis_client = aioredis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("✅ Connected to Redis for proxy storage")
            except Exception as e:
                logger.warning(f"❌ Redis connection failed: {e}, using memory storage")
                self.redis_client = None
                self.use_redis = False
        else:
            logger.info("📝 Using memory storage for proxies")
            
    async def close(self):
        """Close storage connections."""
        if self.redis_client:
            await self.redis_client.close()
            
    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store value by key.
        Equivalent to RedisClient.put() from original.
        """
        try:
            serialized_value = self._serialize(value)
            
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                if ttl:
                    await self.redis_client.setex(redis_key, ttl, serialized_value)
                else:
                    await self.redis_client.set(redis_key, serialized_value)
            else:
                # Memory storage
                self._memory_storage[key] = serialized_value
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to put {key}: {e}")
            return False
            
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.
        Equivalent to RedisClient.get() from original.
        """
        try:
            serialized_value = None
            
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                serialized_value = await self.redis_client.get(redis_key)
            else:
                # Memory storage
                serialized_value = self._memory_storage.get(key)
                
            if serialized_value:
                return self._deserialize(serialized_value)
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get {key}: {e}")
            return None
            
    async def delete(self, key: str) -> bool:
        """
        Delete value by key.
        Equivalent to RedisClient.delete() from original.
        """
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                result = await self.redis_client.delete(redis_key)
                return result > 0
            else:
                # Memory storage
                if key in self._memory_storage:
                    del self._memory_storage[key]
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete {key}: {e}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                return await self.redis_client.exists(redis_key) > 0
            else:
                return key in self._memory_storage
                
        except Exception as e:
            logger.error(f"❌ Failed to check existence of {key}: {e}")
            return False
            
    async def get_all_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        try:
            if self.use_redis and self.redis_client:
                redis_pattern = f"{self.key_prefix}:{pattern}"
                keys = await self.redis_client.keys(redis_pattern)
                # Remove prefix
                return [key.replace(f"{self.key_prefix}:", "") for key in keys]
            else:
                # Memory storage - simple pattern matching
                import fnmatch
                return [key for key in self._memory_storage.keys() if fnmatch.fnmatch(key, pattern)]
                
        except Exception as e:
            logger.error(f"❌ Failed to get keys with pattern {pattern}: {e}")
            return []
            
    async def set_add(self, set_name: str, value: str) -> bool:
        """Add value to set."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:set:{set_name}"
                result = await self.redis_client.sadd(redis_key, value)
                return result > 0
            else:
                # Memory storage
                if set_name not in self._memory_sets:
                    self._memory_sets[set_name] = set()
                self._memory_sets[set_name].add(value)
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add to set {set_name}: {e}")
            return False
            
    async def set_remove(self, set_name: str, value: str) -> bool:
        """Remove value from set."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:set:{set_name}"
                result = await self.redis_client.srem(redis_key, value)
                return result > 0
            else:
                # Memory storage
                if set_name in self._memory_sets:
                    self._memory_sets[set_name].discard(value)
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to remove from set {set_name}: {e}")
            return False
            
    async def set_members(self, set_name: str) -> Set[str]:
        """Get all members of set."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:set:{set_name}"
                members = await self.redis_client.smembers(redis_key)
                return set(members)
            else:
                # Memory storage
                return self._memory_sets.get(set_name, set()).copy()
                
        except Exception as e:
            logger.error(f"❌ Failed to get set members {set_name}: {e}")
            return set()
            
    async def cleanup_expired(self, max_age_hours: int = 24):
        """Clean up expired entries (memory storage only)."""
        if not self.use_redis:
            # For memory storage, we'd need to track timestamps
            # This is a simplified version
            pass
            
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage."""
        if isinstance(value, str):
            return value
        elif isinstance(value, ProxyInfo):
            return json.dumps(asdict(value), default=str)
        elif isinstance(value, dict):
            return json.dumps(value, default=str)
        else:
            # Fallback to pickle for complex objects
            import base64
            pickled = pickle.dumps(value)
            return base64.b64encode(pickled).decode('utf-8')
            
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage."""
        try:
            # Try JSON first
            data = json.loads(value)
            
            # Check if it's a ProxyInfo dict
            if isinstance(data, dict) and 'host' in data and 'port' in data:
                # Reconstruct ProxyInfo
                return ProxyInfo(
                    host=data['host'],
                    port=data['port'],
                    protocol=data.get('protocol', 'http'),
                    username=data.get('username'),
                    password=data.get('password'),
                    status=ProxyStatus(data.get('status', 'unknown')),
                    last_checked=datetime.fromisoformat(data['last_checked']) if data.get('last_checked') else None,
                    success_rate=data.get('success_rate', 0.0),
                    response_time=data.get('response_time', 0.0),
                    source=data.get('source', 'unknown'),
                    country=data.get('country'),
                    anonymity=data.get('anonymity')
                )
            
            return data
            
        except json.JSONDecodeError:
            try:
                # Try pickle fallback
                import base64
                pickled = base64.b64decode(value.encode('utf-8'))
                return pickle.loads(pickled)
            except Exception:
                # Return as string if all else fails
                return value


class ProxyStorageManager:
    """
    High-level proxy storage manager.
    Combines storage operations with proxy-specific logic.
    """
    
    def __init__(self, storage: AsyncProxyStorage):
        self.storage = storage
        
    async def store_proxy(self, proxy: ProxyInfo, ttl: Optional[int] = None) -> bool:
        """Store a proxy with metadata."""
        try:
            # Store main proxy data
            await self.storage.put(proxy.key, proxy, ttl)
            
            # Add to status sets
            status_set = f"status:{proxy.status.value}"
            await self.storage.set_add(status_set, proxy.key)
            
            # Add to protocol set
            protocol_set = f"protocol:{proxy.protocol}"
            await self.storage.set_add(protocol_set, proxy.key)
            
            # Add to country set if available
            if proxy.country:
                country_set = f"country:{proxy.country}"
                await self.storage.set_add(country_set, proxy.key)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store proxy {proxy.key}: {e}")
            return False
            
    async def get_proxy(self, proxy_key: str) -> Optional[ProxyInfo]:
        """Get a proxy by key."""
        return await self.storage.get(proxy_key)
        
    async def remove_proxy(self, proxy: ProxyInfo) -> bool:
        """Remove a proxy and clean up metadata."""
        try:
            # Remove main data
            await self.storage.delete(proxy.key)
            
            # Remove from all sets
            for status in ProxyStatus:
                await self.storage.set_remove(f"status:{status.value}", proxy.key)
                
            await self.storage.set_remove(f"protocol:{proxy.protocol}", proxy.key)
            
            if proxy.country:
                await self.storage.set_remove(f"country:{proxy.country}", proxy.key)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove proxy {proxy.key}: {e}")
            return False
            
    async def get_proxies_by_status(self, status: ProxyStatus) -> List[ProxyInfo]:
        """Get all proxies with specific status."""
        try:
            proxy_keys = await self.storage.set_members(f"status:{status.value}")
            proxies = []
            
            for key in proxy_keys:
                proxy = await self.storage.get(key)
                if proxy:
                    proxies.append(proxy)
                    
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxies by status {status}: {e}")
            return []
            
    async def get_proxies_by_protocol(self, protocol: str) -> List[ProxyInfo]:
        """Get all proxies with specific protocol."""
        try:
            proxy_keys = await self.storage.set_members(f"protocol:{protocol}")
            proxies = []
            
            for key in proxy_keys:
                proxy = await self.storage.get(key)
                if proxy:
                    proxies.append(proxy)
                    
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxies by protocol {protocol}: {e}")
            return []
            
    async def get_all_proxies(self) -> List[ProxyInfo]:
        """Get all stored proxies."""
        try:
            proxy_keys = await self.storage.get_all_keys()
            proxies = []
            
            for key in proxy_keys:
                if not key.startswith(('status:', 'protocol:', 'country:')):
                    proxy = await self.storage.get(key)
                    if proxy and isinstance(proxy, ProxyInfo):
                        proxies.append(proxy)
                        
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Failed to get all proxies: {e}")
            return []


# Factory functions
async def create_proxy_storage(redis_url: Optional[str] = None) -> AsyncProxyStorage:
    """Create and initialize proxy storage."""
    storage = AsyncProxyStorage(redis_url=redis_url)
    await storage.initialize()
    return storage


async def create_storage_manager(redis_url: Optional[str] = None) -> ProxyStorageManager:
    """Create and initialize storage manager."""
    storage = await create_proxy_storage(redis_url)
    return ProxyStorageManager(storage)


# Usage example
async def example_usage():
    """Example of using the storage system."""
    
    # Create storage
    storage_manager = await create_storage_manager()
    
    # Create test proxy
    proxy = ProxyInfo(
        host="127.0.0.1",
        port=8080,
        protocol="http",
        status=ProxyStatus.ACTIVE,
        source="manual"
    )
    
    # Store proxy
    await storage_manager.store_proxy(proxy)
    
    # Retrieve proxy
    retrieved = await storage_manager.get_proxy(proxy.key)
    print(f"✅ Retrieved proxy: {retrieved.key if retrieved else 'None'}")
    
    # Get all active proxies
    active_proxies = await storage_manager.get_proxies_by_status(ProxyStatus.ACTIVE)
    print(f"📊 Active proxies: {len(active_proxies)}")


if __name__ == "__main__":
    asyncio.run(example_usage())
'''

        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(code)
            
        print(f"✅ Created: {target_file}")
        return target_file
        
    def run_implementation_guide(self):
        """Kör full implementationsguide."""
        
        print("🚀 STARTING MANUAL PROXY POOL IMPLEMENTATION")
        print("=" * 60)
        print()
        
        # Skapa implementationsplan
        steps = self.create_implementation_plan()
        
        print("🔨 CREATING IMPLEMENTATION FILES...")
        print()
        
        # Skapa alla implementation files
        files_created = []
        
        try:
            # Steg 1: Enhanced Proxy Manager
            print("📝 Creating Enhanced Proxy Manager...")
            file1 = self.create_enhanced_proxy_manager()
            files_created.append(file1)
            
            # Steg 2: Advanced Fetchers
            print("📝 Creating Advanced Fetchers...")
            file2 = self.create_advanced_fetchers()
            files_created.append(file2)
            
            # Steg 3: Async Storage
            print("📝 Creating Async Storage...")
            file3 = self.create_async_storage()
            files_created.append(file3)
            
            print()
            print("✅ IMPLEMENTATION FILES CREATED!")
            print("=" * 50)
            
            for file_path in files_created:
                print(f"📄 {file_path}")
                
            print()
            print("📋 NEXT STEPS:")
            print("1. Review the created files")
            print("2. Install required dependencies: aioredis, aiohttp, beautifulsoup4")
            print("3. Test the individual components")
            print("4. Integrate with existing proxy_pool system")
            print("5. Create comprehensive tests")
            
            print()
            print("🎯 MANUAL TESTING COMMANDS:")
            print("python src/proxy_pool/enhanced_manager.py")
            print("python src/proxy_pool/advanced_fetchers.py")
            print("python src/proxy_pool/async_storage.py")
            
        except Exception as e:
            print(f"❌ Error during implementation: {e}")
            print("Created files so far:", files_created)


def main():
    """Huvudfunktion för implementationsguiden."""
    guide = ProxyPoolImplementationGuide()
    guide.run_implementation_guide()


if __name__ == "__main__":
    main()
