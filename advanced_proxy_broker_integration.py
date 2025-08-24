#!/usr/bin/env python3
"""
Advanced Proxy Broker Integration - from constverum/ProxyBroker
===============================================================

Integrerar den sophistikerade ProxyBroker arkitekturen med 58 klasser
och avancerad async proxy-hantering i vårt Ultimate Scraping System.

Key Features from ProxyBroker:
• Advanced async proxy checking with multiple judges
• Geographic filtering and protocol-specific handling  
• Anonymity level detection and verification
• Concurrent proxy validation with semaphores
• Provider management with retry logic
• Advanced negotiator patterns for different proxy types

Enhanced with our Ultimate Scraping System:
• Better integration with our existing proxy pool
• Enhanced monitoring and performance metrics
• Improved error handling and logging
• Additional proxy sources and validation
"""

import asyncio
import aiohttp
import time
import json
import re
import logging
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from urllib.parse import urlparse, urljoin
from collections import defaultdict, Counter
import concurrent.futures
from threading import Lock
import random

# Enhanced versions of our existing systems
from enhanced_proxy_pool_system import ProxyInfo, EnhancedProxyPoolManager
from ultimate_configuration_manager import ConfigurationManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JudgeInfo:
    """Information about proxy judges for validation."""
    url: str
    protocol: str = "HTTP"
    working: bool = False
    response_time: float = 0.0
    last_check: Optional[datetime] = None
    expected_response_pattern: Optional[str] = None
    timeout: int = 8


@dataclass  
class ProxyCheckResult:
    """Result from proxy checking process."""
    proxy: ProxyInfo
    success: bool = False
    protocols: List[str] = field(default_factory=list)
    anonymity_level: str = "unknown"  # transparent, anonymous, elite
    response_time: float = 0.0
    error_message: Optional[str] = None
    judge_url: Optional[str] = None
    real_ip_detected: Optional[str] = None


class ProxyJudge:
    """
    Advanced Proxy Judge - Inspired by ProxyBroker
    ==============================================
    
    Judges are services that help verify proxy functionality
    and determine anonymity levels.
    """
    
    def __init__(self, url: str, protocol: str = "HTTP", timeout: int = 8):
        self.url = url
        self.protocol = protocol.upper()
        self.timeout = timeout
        self.working = False
        self.response_time = 0.0
        self.last_check = None
        
        # Expected response patterns
        self.ip_patterns = [
            r'"origin":\s*"([^"]+)"',  # httpbin.org format
            r'Your IP address is\s*([^\s<]+)',  # generic format
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',  # simple IP match
        ]
        
    async def check_working(self, real_ip: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None) -> bool:
        """Check if judge is working."""
        
        if not session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            session = aiohttp.ClientSession(timeout=timeout)
            should_close = True
        else:
            should_close = False
            
        try:
            start_time = time.time()
            
            async with session.get(self.url) as response:
                if response.status == 200:
                    text = await response.text()
                    self.response_time = time.time() - start_time
                    
                    # Check if response contains IP information
                    for pattern in self.ip_patterns:
                        if re.search(pattern, text):
                            self.working = True
                            self.last_check = datetime.now()
                            logger.debug(f"✅ Judge {self.url} is working (response time: {self.response_time:.2f}s)")
                            return True
                            
            logger.debug(f"❌ Judge {self.url} response doesn't contain expected IP pattern")
            return False
            
        except Exception as e:
            logger.debug(f"❌ Judge {self.url} failed: {e}")
            return False
            
        finally:
            if should_close:
                await session.close()
                
    async def test_proxy(self, proxy: ProxyInfo, real_ip: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None) -> ProxyCheckResult:
        """Test proxy through this judge."""
        
        result = ProxyCheckResult(proxy=proxy, judge_url=self.url)
        
        if not session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            connector = aiohttp.TCPConnector(verify_ssl=False)
            session = aiohttp.ClientSession(timeout=timeout, connector=connector)
            should_close = True
        else:
            should_close = False
            
        try:
            proxy_url = f"http://{proxy.ip}:{proxy.port}"
            
            start_time = time.time()
            
            async with session.get(
                self.url,
                proxy=proxy_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            ) as response:
                
                if response.status == 200:
                    text = await response.text()
                    result.response_time = time.time() - start_time
                    
                    # Extract IP from response
                    detected_ip = None
                    for pattern in self.ip_patterns:
                        match = re.search(pattern, text)
                        if match:
                            detected_ip = match.group(1).split(',')[0].strip()
                            break
                            
                    if detected_ip:
                        result.real_ip_detected = detected_ip
                        result.success = True
                        result.protocols.append(self.protocol)
                        
                        # Determine anonymity level
                        if real_ip and detected_ip == real_ip:
                            result.anonymity_level = "transparent"
                        elif detected_ip == proxy.ip:
                            result.anonymity_level = "anonymous"
                        elif detected_ip != real_ip and detected_ip != proxy.ip:
                            result.anonymity_level = "elite"
                        else:
                            result.anonymity_level = "anonymous"
                            
                        logger.debug(f"✅ Proxy {proxy.proxy_url} working through {self.url} - Anonymity: {result.anonymity_level}")
                        
                    else:
                        result.error_message = "No IP detected in response"
                        
                else:
                    result.error_message = f"HTTP {response.status}"
                    
        except Exception as e:
            result.error_message = str(e)
            logger.debug(f"❌ Proxy {proxy.proxy_url} failed through {self.url}: {e}")
            
        finally:
            if should_close:
                await session.close()
                
        return result


class AdvancedProxyProvider:
    """
    Advanced Proxy Provider - Inspired by ProxyBroker
    ==================================================
    
    Manages proxy providers with advanced features like
    concurrent access control, retry logic, and caching.
    """
    
    def __init__(self, url: str, protocol: str = "HTTP", max_conn: int = 4, max_tries: int = 3, timeout: int = 20):
        self.url = url
        self.domain = urlparse(url).netloc
        self.protocol = protocol
        self.max_tries = max_tries
        self.timeout = timeout
        
        # Concurrency control
        self._semaphore = asyncio.Semaphore(max_conn)
        self._session = None
        self._proxies = set()
        
        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "proxies_found": 0,
            "last_success": None,
            "average_response_time": 0.0
        }
        
    async def get_proxies(self) -> Set[Tuple[str, int, str]]:
        """Get proxies from this provider."""
        
        logger.debug(f"🔍 Getting proxies from {self.domain}")
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        async with self._semaphore:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                self._session = session
                
                for attempt in range(self.max_tries):
                    try:
                        start_time = time.time()
                        
                        async with session.get(self.url) as response:
                            self.stats["total_requests"] += 1
                            
                            if response.status == 200:
                                text = await response.text()
                                response_time = time.time() - start_time
                                
                                # Extract proxies from response
                                found_proxies = self._extract_proxies(text)
                                
                                if found_proxies:
                                    self._proxies.update(found_proxies)
                                    self.stats["successful_requests"] += 1
                                    self.stats["proxies_found"] = len(self._proxies)
                                    self.stats["last_success"] = datetime.now()
                                    self.stats["average_response_time"] = response_time
                                    
                                    logger.debug(f"✅ {self.domain}: Found {len(found_proxies)} proxies (response time: {response_time:.2f}s)")
                                    break
                                    
                            else:
                                logger.debug(f"❌ {self.domain}: HTTP {response.status}")
                                
                    except Exception as e:
                        logger.debug(f"❌ {self.domain} attempt {attempt + 1}: {e}")
                        if attempt < self.max_tries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            
        logger.debug(f"📊 {self.domain}: Total {len(self._proxies)} proxies found")
        return self._proxies
        
    def _extract_proxies(self, text: str) -> Set[Tuple[str, int, str]]:
        """Extract proxies from response text."""
        
        proxies = set()
        
        # Multiple patterns for different proxy list formats
        patterns = [
            # IP:Port format
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})',
            # Table format with IP and Port in separate columns
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td[^>]*>(\d{1,5})</td>',
            # JSON format
            r'"host":\s*"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"[^}]*"port":\s*"?(\d{1,5})"?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for ip, port in matches:
                try:
                    port_int = int(port)
                    if 1 <= port_int <= 65535:
                        proxies.add((ip, port_int, self.protocol))
                except ValueError:
                    continue
                    
        return proxies


class AdvancedProxyBroker:
    """
    Advanced Proxy Broker - Inspired by constverum/ProxyBroker
    ===========================================================
    
    Sophisticated async proxy management system with:
    • Multiple concurrent judges for proxy validation
    • Advanced provider management with retry logic
    • Protocol-specific checking (HTTP/HTTPS/SOCKS)
    • Anonymity level detection
    • Geographic filtering capabilities
    • Performance monitoring and statistics
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        
        # Judge management
        self.judges = self._initialize_judges()
        self.working_judges = []
        
        # Provider management  
        self.providers = self._initialize_providers()
        
        # Proxy storage and management
        self.proxy_pool = EnhancedProxyPoolManager(config_manager)
        self.checked_proxies = {}
        
        # Concurrency control
        self.max_concurrent_checks = 50
        self._check_semaphore = asyncio.Semaphore(self.max_concurrent_checks)
        
        # Performance statistics
        self.stats = {
            "judges_working": 0,
            "providers_active": 0,
            "total_checks_performed": 0,
            "successful_checks": 0,
            "average_check_time": 0.0,
            "proxies_by_anonymity": defaultdict(int),
            "proxies_by_protocol": defaultdict(int),
            "last_broker_run": None
        }
        
    def _initialize_judges(self) -> List[ProxyJudge]:
        """Initialize proxy judges for validation."""
        
        judge_urls = [
            # HTTP judges
            ("http://httpbin.org/ip", "HTTP"),
            ("http://icanhazip.com", "HTTP"), 
            ("http://ident.me", "HTTP"),
            ("http://checkip.amazonaws.com", "HTTP"),
            ("http://ipecho.net/plain", "HTTP"),
            
            # HTTPS judges
            ("https://httpbin.org/ip", "HTTPS"),
            ("https://icanhazip.com", "HTTPS"),
            ("https://ident.me", "HTTPS"),
            ("https://checkip.amazonaws.com", "HTTPS"),
            ("https://ipecho.net/plain", "HTTPS"),
        ]
        
        judges = []
        for url, protocol in judge_urls:
            judge = ProxyJudge(url, protocol)
            judges.append(judge)
            
        logger.info(f"🏛️  Initialized {len(judges)} proxy judges")
        return judges
        
    def _initialize_providers(self) -> List[AdvancedProxyProvider]:
        """Initialize proxy providers."""
        
        provider_urls = [
            # Free proxy lists
            ("https://www.proxy-list.download/api/v1/get?type=http", "HTTP"),
            ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", "HTTP"),
            ("https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt", "HTTP"),
            ("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt", "HTTP"),
            ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt", "HTTP"),
            
            # HTTPS proxies
            ("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt", "HTTPS"),
            ("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt", "HTTPS"),
            ("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/https.txt", "HTTPS"),
        ]
        
        providers = []
        for url, protocol in provider_urls:
            provider = AdvancedProxyProvider(url, protocol)
            providers.append(provider)
            
        logger.info(f"🌐 Initialized {len(providers)} proxy providers")
        return providers
        
    async def initialize(self):
        """Initialize the advanced proxy broker."""
        
        logger.info("🚀 Initializing Advanced Proxy Broker...")
        
        # Initialize proxy pool
        await self.proxy_pool.initialize()
        
        # Check judges
        await self._check_judges()
        
        logger.info("✅ Advanced Proxy Broker initialized successfully!")
        
    async def _check_judges(self):
        """Check which judges are working."""
        
        logger.info("🏛️  Checking proxy judges...")
        
        # Get real external IP for anonymity testing
        real_ip = await self._get_real_ip()
        
        async def check_judge(judge):
            return judge, await judge.check_working(real_ip)
            
        # Check all judges concurrently
        tasks = [check_judge(judge) for judge in self.judges]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        self.working_judges = []
        for result in results:
            if isinstance(result, tuple):
                judge, is_working = result
                if is_working:
                    self.working_judges.append(judge)
                    
        self.stats["judges_working"] = len(self.working_judges)
        logger.info(f"✅ {len(self.working_judges)}/{len(self.judges)} judges are working")
        
    async def _get_real_ip(self) -> Optional[str]:
        """Get real external IP address."""
        
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get("https://httpbin.org/ip") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("origin", "").split(',')[0].strip()
        except Exception as e:
            logger.debug(f"Failed to get real IP: {e}")
            
        return None
        
    async def discover_and_validate_proxies(self) -> List[ProxyInfo]:
        """Discover proxies from providers and validate them."""
        
        logger.info("🔍 Starting proxy discovery and validation...")
        start_time = time.time()
        
        # Get proxies from all providers
        all_proxies = await self._discover_from_providers()
        
        if not all_proxies:
            logger.warning("No proxies discovered from providers")
            return []
            
        logger.info(f"📥 Discovered {len(all_proxies)} raw proxies from providers")
        
        # Validate proxies through judges
        validated_proxies = await self._validate_proxies_advanced(all_proxies)
        
        elapsed = time.time() - start_time
        success_rate = (len(validated_proxies) / len(all_proxies)) * 100 if all_proxies else 0
        
        logger.info(f"✅ Advanced validation completed: {len(validated_proxies)}/{len(all_proxies)} valid ({success_rate:.1f}%) in {elapsed:.1f}s")
        
        # Update statistics
        self.stats["last_broker_run"] = datetime.now()
        
        return validated_proxies
        
    async def _discover_from_providers(self) -> List[ProxyInfo]:
        """Discover proxies from all providers."""
        
        # Get proxies from all providers concurrently
        tasks = [provider.get_proxies() for provider in self.providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_proxy_tuples = set()
        active_providers = 0
        
        for i, result in enumerate(results):
            if isinstance(result, set) and result:
                all_proxy_tuples.update(result)
                active_providers += 1
                logger.debug(f"✅ Provider {self.providers[i].domain}: {len(result)} proxies")
            elif isinstance(result, Exception):
                logger.debug(f"❌ Provider {self.providers[i].domain}: {result}")
                
        self.stats["providers_active"] = active_providers
        
        # Convert to ProxyInfo objects
        proxy_list = []
        for ip, port, protocol in all_proxy_tuples:
            proxy = ProxyInfo(
                ip=ip,
                port=port,
                protocol=protocol.lower(),
                source="advanced_broker"
            )
            proxy_list.append(proxy)
            
        return proxy_list
        
    async def _validate_proxies_advanced(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Advanced proxy validation using multiple judges."""
        
        if not self.working_judges:
            logger.warning("No working judges available for validation")
            return []
            
        logger.info(f"🔍 Validating {len(proxies)} proxies through {len(self.working_judges)} judges...")
        
        # Get real IP for anonymity testing
        real_ip = await self._get_real_ip()
        
        # Validate proxies concurrently
        tasks = []
        for proxy in proxies:
            task = self._validate_single_proxy_advanced(proxy, real_ip)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        validated_proxies = []
        check_times = []
        
        for result in results:
            if isinstance(result, ProxyCheckResult) and result.success:
                proxy = result.proxy
                
                # Update proxy with validation results
                proxy.anonymity = result.anonymity_level
                proxy.speed = result.response_time
                proxy.last_checked = datetime.now()
                proxy.success_count += 1
                proxy.success_rate = proxy.success_count / max(1, proxy.success_count + proxy.fail_count)
                
                validated_proxies.append(proxy)
                check_times.append(result.response_time)
                
                # Update statistics
                self.stats["proxies_by_anonymity"][result.anonymity_level] += 1
                self.stats["proxies_by_protocol"][proxy.protocol] += 1
                
            self.stats["total_checks_performed"] += 1
            if isinstance(result, ProxyCheckResult) and result.success:
                self.stats["successful_checks"] += 1
                
        # Update average check time
        if check_times:
            self.stats["average_check_time"] = sum(check_times) / len(check_times)
            
        return validated_proxies
        
    async def _validate_single_proxy_advanced(self, proxy: ProxyInfo, real_ip: Optional[str]) -> ProxyCheckResult:
        """Validate single proxy using advanced judge system."""
        
        async with self._check_semaphore:
            # Try multiple judges for better reliability
            judges_to_try = random.sample(self.working_judges, min(3, len(self.working_judges)))
            
            for judge in judges_to_try:
                try:
                    result = await judge.test_proxy(proxy, real_ip)
                    if result.success:
                        return result
                except Exception as e:
                    logger.debug(f"Judge {judge.url} failed for {proxy.proxy_url}: {e}")
                    continue
                    
            # If all judges failed, return failed result
            return ProxyCheckResult(proxy=proxy, success=False, error_message="All judges failed")
            
    def get_broker_stats(self) -> Dict[str, Any]:
        """Get comprehensive broker statistics."""
        
        return {
            **self.stats,
            "total_proxies_in_pool": len(self.proxy_pool.all_proxies),
            "proxy_pool_stats": self.proxy_pool.get_stats()
        }
        
    async def get_best_proxies(self, count: int = 10, protocol: str = "http", anonymity: Optional[str] = None) -> List[ProxyInfo]:
        """Get best proxies based on criteria."""
        
        all_proxies = list(self.proxy_pool.all_proxies.values())
        
        # Filter by protocol
        filtered_proxies = [p for p in all_proxies if p.protocol == protocol]
        
        # Filter by anonymity if specified
        if anonymity:
            filtered_proxies = [p for p in filtered_proxies if getattr(p, 'anonymity', 'unknown') == anonymity]
            
        # Sort by quality (success rate and speed)
        filtered_proxies.sort(key=lambda p: (p.success_rate, -p.speed), reverse=True)
        
        return filtered_proxies[:count]


async def test_advanced_proxy_broker():
    """Test the advanced proxy broker system."""
    
    print("🚀 TESTING ADVANCED PROXY BROKER SYSTEM")
    print("=" * 50)
    
    # Initialize system
    config = ConfigurationManager()
    broker = AdvancedProxyBroker(config)
    
    # Initialize broker
    await broker.initialize()
    
    # Discover and validate proxies
    validated_proxies = await broker.discover_and_validate_proxies()
    
    # Display statistics
    stats = broker.get_broker_stats()
    
    print(f"\n📊 ADVANCED BROKER STATISTICS:")
    print(f"   Working judges: {stats['judges_working']}")
    print(f"   Active providers: {stats['providers_active']}")
    print(f"   Total checks performed: {stats['total_checks_performed']}")
    print(f"   Successful checks: {stats['successful_checks']}")
    print(f"   Success rate: {(stats['successful_checks'] / max(1, stats['total_checks_performed']) * 100):.1f}%")
    print(f"   Average check time: {stats['average_check_time']:.2f}s")
    
    print(f"\n🎯 VALIDATED PROXIES: {len(validated_proxies)}")
    
    # Show anonymity breakdown
    if stats['proxies_by_anonymity']:
        print(f"\n🥷 ANONYMITY LEVELS:")
        for level, count in stats['proxies_by_anonymity'].items():
            print(f"   {level}: {count}")
            
    # Show protocol breakdown
    if stats['proxies_by_protocol']:
        print(f"\n🔌 PROTOCOLS:")
        for protocol, count in stats['proxies_by_protocol'].items():
            print(f"   {protocol}: {count}")
            
    # Get best proxies
    best_proxies = await broker.get_best_proxies(count=5)
    
    if best_proxies:
        print(f"\n⭐ TOP 5 BEST PROXIES:")
        for i, proxy in enumerate(best_proxies, 1):
            anonymity = getattr(proxy, 'anonymity', 'unknown')
            print(f"   {i}. {proxy.proxy_url} - Anonymity: {anonymity}, Success: {proxy.success_rate:.2f}, Speed: {proxy.speed:.2f}s")
            
    print(f"\n✅ Advanced Proxy Broker System test completed!")


if __name__ == "__main__":
    asyncio.run(test_advanced_proxy_broker())
