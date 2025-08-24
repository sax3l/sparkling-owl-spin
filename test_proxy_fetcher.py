#!/usr/bin/env python3
"""
Test för Advanced Proxy Fetchers
===============================

Standalone test av den moderna proxy fetcher systemet baserad på jhao104/proxy_pool ProxyFetcher.
"""

import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Set, List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
    def key(self) -> str:
        """Unique key for proxy."""
        return f"{self.host}:{self.port}"


@dataclass 
class ProxySource:
    """Configuration for a proxy source."""
    name: str
    url: str
    parser_type: str
    headers: Dict[str, str] = None
    rate_limit: float = 1.0
    enabled: bool = True
    timeout: int = 30


class SimplifiedProxyFetcher:
    """
    Förenklad test version av Advanced Proxy Fetcher.
    Baserad på jhao104/proxy_pool ProxyFetcher med freeProxy metoder.
    """
    
    def __init__(self):
        # Simulerade proxy sources (baserat på original freeProxy01-05)
        self.sources = [
            ProxySource(
                name="FreeProxyList",
                url="https://www.free-proxy-list.net/",
                parser_type="html_table"
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
                name="MockAPI",
                url="https://api.example.com/proxies",
                parser_type="api",
                rate_limit=0.5
            )
        ]
        
        self.stats = {
            "fetches_completed": 0,
            "proxies_found": 0,
            "errors_encountered": 0,
            "last_fetch": None
        }
        
    async def fetch_all_sources(self) -> List[ProxyInfo]:
        """Fetch proxies from all enabled sources (simulerad)."""
        logger.info("🔄 Fetching proxies from all sources...")
        
        enabled_sources = [source for source in self.sources if source.enabled]
        all_proxies = []
        
        for source in enabled_sources:
            try:
                proxies = await self._fetch_from_source(source)
                all_proxies.extend(proxies)
                logger.info(f"✅ {source.name}: {len(proxies)} proxies")
                
            except Exception as e:
                logger.error(f"❌ Source {source.name} failed: {e}")
                self.stats["errors_encountered"] += 1
                
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
        """Simulera fetch från en källa (baserat på freeProxy metoder)."""
        logger.debug(f"📥 Fetching from {source.name}...")
        
        # Simulera rate limiting
        if source.rate_limit > 0:
            await asyncio.sleep(0.1)  # Förkortad för test
            
        # Simulera olika parser types
        if source.parser_type == "html_table":
            return self._simulate_html_table_parsing(source.name)
        elif source.parser_type == "html_custom":
            return self._simulate_html_custom_parsing(source.name)
        elif source.parser_type == "api":
            return self._simulate_api_parsing(source.name)
        else:
            logger.warning(f"❌ Unknown parser type: {source.parser_type}")
            return []
            
    def _simulate_html_table_parsing(self, source_name: str) -> List[ProxyInfo]:
        """
        Simulera HTML table parsing (baserat på original HTML parsing logic).
        I riktig implementation: BeautifulSoup för att parsa <table> element.
        """
        # Simulera att vi hittade proxies i HTML table
        simulated_proxies = [
            ProxyInfo("203.142.71.78", 8080, "http", source=source_name, country="TH"),
            ProxyInfo("185.199.84.161", 53281, "http", source=source_name, country="TR"),
            ProxyInfo("103.159.46.34", 3128, "https", source=source_name, country="ID"),
        ]
        
        return simulated_proxies
        
    def _simulate_html_custom_parsing(self, source_name: str) -> List[ProxyInfo]:
        """
        Simulera custom HTML parsing med regex.
        I riktig implementation: regex för IP:PORT mönster.
        """
        simulated_proxies = [
            ProxyInfo("45.77.55.173", 8080, "http", source=source_name),
            ProxyInfo("198.199.86.11", 3128, "http", source=source_name),
        ]
        
        return simulated_proxies
        
    def _simulate_api_parsing(self, source_name: str) -> List[ProxyInfo]:
        """
        Simulera API parsing (JSON response).
        I riktig implementation: JSON parsing från API.
        """
        simulated_proxies = [
            ProxyInfo("149.154.157.17", 3128, "http", source=source_name, country="RU"),
            ProxyInfo("192.41.13.71", 80, "http", source=source_name, country="US"),
        ]
        
        return simulated_proxies
        
    def _deduplicate_proxies(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicate proxies baserat på key."""
        seen_keys = set()
        unique_proxies = []
        
        for proxy in proxies:
            if proxy.key not in seen_keys:
                seen_keys.add(proxy.key)
                unique_proxies.append(proxy)
                
        return unique_proxies
        
    def add_custom_source(self, source: ProxySource):
        """Add custom source (från original extensibility)."""
        self.sources.append(source)
        logger.info(f"➕ Added custom source: {source.name}")
        
    def disable_source(self, source_name: str):
        """Disable a source."""
        for source in self.sources:
            if source.name == source_name:
                source.enabled = False
                logger.info(f"⏸️ Disabled source: {source_name}")
                return
        logger.warning(f"❌ Source not found: {source_name}")
        
    def get_stats(self) -> Dict[str, any]:
        """Get fetcher statistics."""
        return {
            **self.stats,
            "enabled_sources": len([s for s in self.sources if s.enabled]),
            "total_sources": len(self.sources)
        }


async def test_proxy_fetcher():
    """Test av proxy fetcher funktionalitet."""
    print("🚀 TESTING ADVANCED PROXY FETCHER")
    print("=" * 50)
    
    # Skapa fetcher
    fetcher = SimplifiedProxyFetcher()
    
    print("📋 Available Sources:")
    for i, source in enumerate(fetcher.sources):
        status = "✅ Enabled" if source.enabled else "⏸️ Disabled"
        print(f"   {i+1}. {source.name} ({source.parser_type}) - {status}")
        print(f"      URL: {source.url}")
        print(f"      Rate limit: {source.rate_limit}s")
    print()
    
    # Test fetch from all sources
    print("🔄 Fetching from all sources...")
    proxies = await fetcher.fetch_all_sources()
    print()
    
    print(f"📊 FETCH RESULTS:")
    print(f"   Total proxies found: {len(proxies)}")
    print()
    
    # Visa sample proxies
    print("🔍 Sample Proxies Found:")
    for i, proxy in enumerate(proxies[:8]):  # Show first 8
        print(f"   {i+1}. {proxy.key} ({proxy.protocol}) - {proxy.source}")
        if proxy.country:
            print(f"      Country: {proxy.country}")
    print()
    
    # Group by source
    by_source = {}
    for proxy in proxies:
        if proxy.source not in by_source:
            by_source[proxy.source] = 0
        by_source[proxy.source] += 1
        
    print("📈 Proxies by Source:")
    for source, count in by_source.items():
        print(f"   {source}: {count} proxies")
    print()
    
    # Group by protocol
    by_protocol = {}
    for proxy in proxies:
        if proxy.protocol not in by_protocol:
            by_protocol[proxy.protocol] = 0
        by_protocol[proxy.protocol] += 1
        
    print("🔧 Proxies by Protocol:")
    for protocol, count in by_protocol.items():
        print(f"   {protocol.upper()}: {count} proxies")
    print()
    
    # Test source management
    print("⚙️  Testing Source Management:")
    
    # Add custom source
    custom_source = ProxySource(
        name="CustomAPI",
        url="https://custom.proxy.api/list",
        parser_type="json",
        rate_limit=1.0
    )
    fetcher.add_custom_source(custom_source)
    
    # Disable a source
    fetcher.disable_source("SpysOne")
    print()
    
    # Show stats
    print("📊 Fetcher Statistics:")
    stats = fetcher.get_stats()
    for key, value in stats.items():
        if key == "last_fetch" and value:
            print(f"   {key}: {value.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   {key}: {value}")
    print()
    
    print("✅ ADVANCED PROXY FETCHER TEST COMPLETED!")
    print()
    print("🎯 IMPLEMENTATION SUCCESS!")
    print("   • ProxyFetcher logik från jhao104/proxy_pool implementerad")
    print("   • Async fetching från multiple sources")
    print("   • HTML table, custom HTML, och API parsing simulerad")
    print("   • Source management (enable/disable/add custom)")
    print("   • Deduplication och statistics")
    print("   • Rate limiting support")
    print()
    print("📋 NÄSTA STEG:")
    print("   1. Implementera riktig HTTP requests med aiohttp") 
    print("   2. Lägg till riktig HTML parsing med BeautifulSoup")
    print("   3. Implementera robusta error handling och retry logic")
    print("   4. Integrera med Enhanced Proxy Manager")
    print("   5. Lägg till proxy validation efter fetch")


if __name__ == "__main__":
    asyncio.run(test_proxy_fetcher())
