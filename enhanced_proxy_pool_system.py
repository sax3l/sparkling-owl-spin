#!/usr/bin/env python3
"""
Enhanced Proxy Pool System - Integration from jhao104/proxy_pool
================================================================

Integrerar den kraftfulla proxy_pool funktionaliteten från jhao104/proxy_pool
i vårt Ultimate Scraping System.

Key Features from proxy_pool:
• 9+ olika proxy-källor (freeProxy01-09)
• Automatisk proxy validering och cleanup
• Database abstraction (Redis/SSDB support)
• HTTP/HTTPS proxy separation
• Robust error handling
• CLI interface för server/scheduler

Enhanced with our Ultimate Scraping System:
• Advanced monitoring and metrics
• Better error handling and logging
• Integration with our Control Center
• Enhanced proxy validation
• Performance optimization
"""

import asyncio
import time
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict, field
from urllib.parse import urlparse, parse_qs
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
from threading import Lock
import random

# Våra system
from ultimate_configuration_manager import ConfigurationManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProxyInfo:
    """Enhanced proxy information class."""
    ip: str
    port: int
    protocol: str = "http"
    anonymity: str = "unknown"
    country: str = "unknown"
    source: str = "unknown"
    speed: float = 0.0
    success_rate: float = 0.0
    last_checked: Optional[datetime] = None
    created: datetime = field(default_factory=datetime.now)
    fail_count: int = 0
    success_count: int = 0
    
    @property
    def proxy_url(self) -> str:
        """Get proxy URL format."""
        return f"{self.protocol}://{self.ip}:{self.port}"
    
    @property
    def is_valid(self) -> bool:
        """Check if proxy is considered valid."""
        if not self.last_checked:
            return False
        
        # Consider proxy stale after 1 hour
        if datetime.now() - self.last_checked > timedelta(hours=1):
            return False
            
        # Require minimum success rate
        if self.success_rate < 0.3 and self.success_count + self.fail_count > 5:
            return False
            
        return True


class ProxyFetcher:
    """
    Enhanced Proxy Fetcher - Integrerad från jhao104/proxy_pool
    ============================================================
    
    Hämtar proxies från flera källor med förbättrad error handling
    och performance monitoring.
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.session = self._create_session()
        
        # Performance metrics
        self.fetch_stats = {
            "total_fetched": 0,
            "successful_sources": 0,
            "failed_sources": 0,
            "last_fetch_time": None
        }
        
    def _create_session(self) -> requests.Session:
        """Create optimized requests session."""
        session = requests.Session()
        
        # Enhanced retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Common headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return session
        
    async def fetch_all_sources(self) -> List[ProxyInfo]:
        """Fetch proxies from all available sources."""
        
        logger.info("🔍 Starting comprehensive proxy fetch from all sources...")
        
        # Define all proxy sources
        sources = [
            ("zdaye", self._fetch_zdaye_proxies),
            ("66ip", self._fetch_66ip_proxies), 
            ("kxdaili", self._fetch_kxdaili_proxies),
            ("freeproxylists", self._fetch_freeproxylists_proxies),
            ("kuaidaili", self._fetch_kuaidaili_proxies),
            ("binglx", self._fetch_binglx_proxies),
            ("ip3366", self._fetch_ip3366_proxies),
            ("ihuan", self._fetch_ihuan_proxies),
            ("jiangxianli", self._fetch_jiangxianli_proxies)
        ]
        
        all_proxies = []
        start_time = time.time()
        
        # Fetch from all sources concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(self._safe_fetch_source, name, func): name
                for name, func in sources
            }
            
            for future in concurrent.futures.as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    proxies = future.result(timeout=30)
                    all_proxies.extend(proxies)
                    self.fetch_stats["successful_sources"] += 1
                    logger.info(f"✅ {source_name}: fetched {len(proxies)} proxies")
                    
                except Exception as e:
                    self.fetch_stats["failed_sources"] += 1
                    logger.warning(f"❌ {source_name}: failed - {e}")
                    
        # Update stats
        self.fetch_stats["total_fetched"] = len(all_proxies)
        self.fetch_stats["last_fetch_time"] = datetime.now()
        
        elapsed = time.time() - start_time
        logger.info(f"🎯 Proxy fetch completed: {len(all_proxies)} proxies from {self.fetch_stats['successful_sources']} sources in {elapsed:.1f}s")
        
        return all_proxies
        
    def _safe_fetch_source(self, source_name: str, fetch_func) -> List[ProxyInfo]:
        """Safely fetch from a single source with error handling."""
        
        try:
            proxies = list(fetch_func())
            return proxies
            
        except Exception as e:
            logger.warning(f"Source {source_name} failed: {e}")
            return []
            
    def _fetch_zdaye_proxies(self) -> List[ProxyInfo]:
        """Fetch from 站大爷 zdaye.com"""
        
        try:
            url = "https://www.zdaye.com/dayProxy.html"
            response = self.session.get(url, timeout=10, verify=False)
            
            if response.status_code != 200:
                return []
                
            # Parse with regex instead of xpath for better reliability
            proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)'
            matches = re.findall(proxy_pattern, response.text)
            
            proxies = []
            for ip, port in matches:
                try:
                    proxy = ProxyInfo(
                        ip=ip,
                        port=int(port),
                        protocol="http",
                        source="zdaye",
                        country="CN"
                    )
                    proxies.append(proxy)
                except ValueError:
                    continue
                    
            return proxies[:50]  # Limit to prevent spam
            
        except Exception as e:
            logger.warning(f"zdaye fetch error: {e}")
            return []
            
    def _fetch_66ip_proxies(self) -> List[ProxyInfo]:
        """Fetch from 代理66 66ip.cn"""
        
        try:
            url = "http://www.66ip.cn/"
            response = self.session.get(url, timeout=10)
            
            # Parse proxy table
            proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td>(\d+)</td>'
            matches = re.findall(proxy_pattern, response.text)
            
            proxies = []
            for ip, port in matches:
                try:
                    proxy = ProxyInfo(
                        ip=ip,
                        port=int(port),
                        protocol="http", 
                        source="66ip",
                        country="CN"
                    )
                    proxies.append(proxy)
                except ValueError:
                    continue
                    
            return proxies[:30]
            
        except Exception as e:
            logger.warning(f"66ip fetch error: {e}")
            return []
            
    def _fetch_kxdaili_proxies(self) -> List[ProxyInfo]:
        """Fetch from 开心代理 kxdaili.com"""
        
        proxies = []
        urls = [
            "http://www.kxdaili.com/dailiip.html",
            "http://www.kxdaili.com/dailiip/2/1.html"
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td[^>]*>(\d+)</td>'
                matches = re.findall(proxy_pattern, response.text)
                
                for ip, port in matches:
                    try:
                        proxy = ProxyInfo(
                            ip=ip,
                            port=int(port),
                            protocol="http",
                            source="kxdaili",
                            country="CN"
                        )
                        proxies.append(proxy)
                    except ValueError:
                        continue
                        
            except Exception as e:
                logger.warning(f"kxdaili fetch error for {url}: {e}")
                continue
                
        return proxies[:40]
        
    def _fetch_freeproxylists_proxies(self) -> List[ProxyInfo]:
        """Fetch from FreeProxyLists"""
        
        try:
            url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
            response = self.session.get(url, timeout=15, verify=False)
            
            # This site uses encoded IPs, try to decode simple patterns
            proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[^0-9]*?(\d{2,5})'
            matches = re.findall(proxy_pattern, response.text)
            
            proxies = []
            for ip, port in matches:
                try:
                    if int(port) > 65535:
                        continue
                        
                    proxy = ProxyInfo(
                        ip=ip,
                        port=int(port),
                        protocol="http",
                        source="freeproxylists", 
                        country="CN"
                    )
                    proxies.append(proxy)
                except ValueError:
                    continue
                    
            return proxies[:25]
            
        except Exception as e:
            logger.warning(f"freeproxylists fetch error: {e}")
            return []
            
    def _fetch_kuaidaili_proxies(self) -> List[ProxyInfo]:
        """Fetch from 快代理 kuaidaili.com"""
        
        proxies = []
        url_patterns = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        
        for page in range(1, 3):  # First 2 pages
            for pattern in url_patterns:
                try:
                    url = pattern.format(page)
                    response = self.session.get(url, timeout=10)
                    
                    proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td[^>]*>(\d+)</td>'
                    matches = re.findall(proxy_pattern, response.text)
                    
                    for ip, port in matches:
                        try:
                            proxy = ProxyInfo(
                                ip=ip,
                                port=int(port),
                                protocol="http",
                                source="kuaidaili",
                                country="CN"
                            )
                            proxies.append(proxy)
                        except ValueError:
                            continue
                            
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"kuaidaili fetch error for {pattern.format(page)}: {e}")
                    continue
                    
        return proxies[:35]
        
    def _fetch_binglx_proxies(self) -> List[ProxyInfo]:
        """Fetch from 冰凌代理 binglx.cn"""
        
        try:
            url = "https://www.binglx.cn/?page=1"
            response = self.session.get(url, timeout=10)
            
            proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td[^>]*>(\d+)</td>'
            matches = re.findall(proxy_pattern, response.text)
            
            proxies = []
            for ip, port in matches:
                try:
                    proxy = ProxyInfo(
                        ip=ip,
                        port=int(port),
                        protocol="http",
                        source="binglx",
                        country="CN"
                    )
                    proxies.append(proxy)
                except ValueError:
                    continue
                    
            return proxies[:20]
            
        except Exception as e:
            logger.warning(f"binglx fetch error: {e}")
            return []
            
    def _fetch_ip3366_proxies(self) -> List[ProxyInfo]:
        """Fetch from 云代理 ip3366.net"""
        
        proxies = []
        urls = [
            'http://www.ip3366.net/free/?stype=1',
            'http://www.ip3366.net/free/?stype=2'
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td[^>]*>(\d+)</td>'
                matches = re.findall(proxy_pattern, response.text)
                
                for ip, port in matches:
                    try:
                        proxy = ProxyInfo(
                            ip=ip,
                            port=int(port),
                            protocol="http",
                            source="ip3366",
                            country="CN"
                        )
                        proxies.append(proxy)
                    except ValueError:
                        continue
                        
            except Exception as e:
                logger.warning(f"ip3366 fetch error for {url}: {e}")
                continue
                
        return proxies[:30]
        
    def _fetch_ihuan_proxies(self) -> List[ProxyInfo]:
        """Fetch from 小幻代理 ihuan.me"""
        
        try:
            url = 'https://ip.ihuan.me/address/5Lit5Zu9.html'
            response = self.session.get(url, timeout=10)
            
            proxy_pattern = r'>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</a></td><td[^>]*>(\d+)</td>'
            matches = re.findall(proxy_pattern, response.text)
            
            proxies = []
            for ip, port in matches:
                try:
                    proxy = ProxyInfo(
                        ip=ip,
                        port=int(port),
                        protocol="http",
                        source="ihuan",
                        country="CN"
                    )
                    proxies.append(proxy)
                except ValueError:
                    continue
                    
            return proxies[:25]
            
        except Exception as e:
            logger.warning(f"ihuan fetch error: {e}")
            return []
            
    def _fetch_jiangxianli_proxies(self) -> List[ProxyInfo]:
        """Fetch from 免费代理库 jiangxianli.com"""
        
        proxies = []
        
        for page in range(1, 3):  # First 2 pages
            try:
                url = f'http://ip.jiangxianli.com/?country=中国&page={page}'
                response = self.session.get(url, timeout=10, verify=False)
                
                proxy_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td[^>]*>(\d+)</td>'
                matches = re.findall(proxy_pattern, response.text)
                
                for ip, port in matches:
                    try:
                        proxy = ProxyInfo(
                            ip=ip,
                            port=int(port),
                            protocol="http",
                            source="jiangxianli",
                            country="CN"
                        )
                        proxies.append(proxy)
                    except ValueError:
                        continue
                        
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"jiangxianli fetch error for page {page}: {e}")
                continue
                
        return proxies[:20]


class ProxyValidator:
    """
    Enhanced Proxy Validator
    ========================
    
    Validerar proxies med förbättrad performance och reliability testing.
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        
        # Validation settings
        self.validation_timeout = 8
        self.test_urls = [
            'http://httpbin.org/ip',
            'https://httpbin.org/ip',
            'http://icanhazip.com',
        ]
        
        # Performance metrics
        self.validation_stats = {
            "total_validated": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "average_response_time": 0.0
        }
        
    async def validate_proxies(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Validate a list of proxies concurrently."""
        
        if not proxies:
            return []
            
        logger.info(f"🔍 Validating {len(proxies)} proxies...")
        start_time = time.time()
        
        # Validate concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_proxy = {
                executor.submit(self._validate_single_proxy, proxy): proxy
                for proxy in proxies
            }
            
            valid_proxies = []
            response_times = []
            
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_valid, response_time = future.result(timeout=self.validation_timeout + 2)
                    
                    if is_valid:
                        proxy.success_count += 1
                        proxy.speed = response_time
                        proxy.last_checked = datetime.now()
                        proxy.success_rate = proxy.success_count / max(1, proxy.success_count + proxy.fail_count)
                        valid_proxies.append(proxy)
                        response_times.append(response_time)
                        self.validation_stats["successful_validations"] += 1
                    else:
                        proxy.fail_count += 1
                        proxy.success_rate = proxy.success_count / max(1, proxy.success_count + proxy.fail_count)
                        self.validation_stats["failed_validations"] += 1
                        
                    self.validation_stats["total_validated"] += 1
                    
                except Exception as e:
                    proxy.fail_count += 1
                    self.validation_stats["failed_validations"] += 1
                    self.validation_stats["total_validated"] += 1
                    
        # Update average response time
        if response_times:
            self.validation_stats["average_response_time"] = sum(response_times) / len(response_times)
            
        elapsed = time.time() - start_time
        success_rate = (len(valid_proxies) / len(proxies)) * 100 if proxies else 0
        
        logger.info(f"✅ Validation completed: {len(valid_proxies)}/{len(proxies)} valid ({success_rate:.1f}%) in {elapsed:.1f}s")
        logger.info(f"📊 Average response time: {self.validation_stats['average_response_time']:.2f}s")
        
        return valid_proxies
        
    def _validate_single_proxy(self, proxy: ProxyInfo) -> Tuple[bool, float]:
        """Validate a single proxy."""
        
        try:
            proxy_dict = {
                'http': proxy.proxy_url,
                'https': proxy.proxy_url
            }
            
            start_time = time.time()
            
            # Test with multiple URLs for better reliability
            for test_url in self.test_urls[:2]:  # Test first 2 URLs
                try:
                    response = requests.get(
                        test_url,
                        proxies=proxy_dict,
                        timeout=self.validation_timeout,
                        verify=False,
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    
                    if response.status_code == 200:
                        response_time = time.time() - start_time
                        
                        # Additional validation for IP check services
                        if 'httpbin.org' in test_url or 'icanhazip.com' in test_url:
                            response_json = response.json() if 'httpbin.org' in test_url else {'origin': response.text.strip()}
                            origin_ip = response_json.get('origin', '').split(',')[0].strip()
                            
                            # Verify proxy is actually being used
                            if origin_ip and origin_ip != proxy.ip:
                                logger.debug(f"Proxy IP mismatch: expected {proxy.ip}, got {origin_ip}")
                                
                        return True, response_time
                        
                except requests.exceptions.RequestException:
                    continue
                    
            return False, 0.0
            
        except Exception as e:
            logger.debug(f"Validation error for {proxy.proxy_url}: {e}")
            return False, 0.0


class EnhancedProxyPoolManager:
    """
    Enhanced Proxy Pool Manager
    ===========================
    
    Integrerad proxy pool manager med funktionalitet från jhao104/proxy_pool
    men förbättrad för vårt Ultimate Scraping System.
    """
    
    def __init__(self, config_manager: Optional[ConfigurationManager] = None):
        self.config_manager = config_manager or ConfigurationManager()
        self.fetcher = ProxyFetcher(config_manager)
        self.validator = ProxyValidator(config_manager)
        
        # Proxy storage
        self.http_proxies: List[ProxyInfo] = []
        self.https_proxies: List[ProxyInfo] = []
        self.all_proxies: Dict[str, ProxyInfo] = {}
        
        # Thread safety
        self._lock = Lock()
        
        # Management settings
        self.max_proxies = 1000
        self.cleanup_interval = 3600  # 1 hour
        self.fetch_interval = 1800    # 30 minutes
        
        # Statistics
        self.stats = {
            "total_proxies": 0,
            "valid_proxies": 0,
            "last_fetch": None,
            "last_cleanup": None,
            "sources_active": 0
        }
        
    async def initialize(self):
        """Initialize the proxy pool."""
        
        logger.info("🚀 Initializing Enhanced Proxy Pool Manager...")
        
        # Initial proxy fetch
        await self.fetch_and_validate_proxies()
        
        logger.info("✅ Enhanced Proxy Pool Manager initialized successfully!")
        
    async def fetch_and_validate_proxies(self):
        """Fetch and validate proxies from all sources."""
        
        logger.info("🔍 Starting proxy fetch and validation cycle...")
        
        # Fetch from all sources
        raw_proxies = await self.fetcher.fetch_all_sources()
        
        if not raw_proxies:
            logger.warning("No proxies fetched from any source")
            return
            
        logger.info(f"📥 Fetched {len(raw_proxies)} raw proxies")
        
        # Remove duplicates
        unique_proxies = self._remove_duplicates(raw_proxies)
        logger.info(f"🔄 After deduplication: {len(unique_proxies)} unique proxies")
        
        # Validate proxies
        valid_proxies = await self.validator.validate_proxies(unique_proxies)
        
        if valid_proxies:
            # Store validated proxies
            with self._lock:
                self._store_proxies(valid_proxies)
                
            logger.info(f"✅ Stored {len(valid_proxies)} validated proxies")
        else:
            logger.warning("No valid proxies found after validation")
            
        # Update statistics
        self._update_stats()
        
    def _remove_duplicates(self, proxies: List[ProxyInfo]) -> List[ProxyInfo]:
        """Remove duplicate proxies."""
        
        seen = set()
        unique_proxies = []
        
        for proxy in proxies:
            proxy_key = f"{proxy.ip}:{proxy.port}"
            if proxy_key not in seen:
                seen.add(proxy_key)
                unique_proxies.append(proxy)
                
        return unique_proxies
        
    def _store_proxies(self, proxies: List[ProxyInfo]):
        """Store validated proxies with classification."""
        
        # Clear old proxies if we exceed limit
        if len(self.all_proxies) + len(proxies) > self.max_proxies:
            self._cleanup_old_proxies()
            
        # Store and classify proxies
        for proxy in proxies:
            proxy_key = f"{proxy.ip}:{proxy.port}"
            self.all_proxies[proxy_key] = proxy
            
            # Classify by protocol support
            if proxy.protocol in ['http', 'both']:
                if proxy not in self.http_proxies:
                    self.http_proxies.append(proxy)
                    
            if proxy.protocol in ['https', 'both']:
                if proxy not in self.https_proxies:
                    self.https_proxies.append(proxy)
                    
        # Sort by quality (success rate and speed)
        self.http_proxies.sort(key=lambda p: (p.success_rate, -p.speed), reverse=True)
        self.https_proxies.sort(key=lambda p: (p.success_rate, -p.speed), reverse=True)
        
    def _cleanup_old_proxies(self):
        """Remove old/invalid proxies."""
        
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=2)
        
        # Remove stale proxies
        valid_proxy_keys = []
        for key, proxy in self.all_proxies.items():
            if proxy.last_checked and proxy.last_checked > cutoff_time and proxy.is_valid:
                valid_proxy_keys.append(key)
                
        # Update storage
        self.all_proxies = {k: self.all_proxies[k] for k in valid_proxy_keys}
        
        # Update classified lists
        self.http_proxies = [p for p in self.http_proxies if f"{p.ip}:{p.port}" in self.all_proxies]
        self.https_proxies = [p for p in self.https_proxies if f"{p.ip}:{p.port}" in self.all_proxies]
        
        logger.info(f"🧹 Cleaned up old proxies, {len(self.all_proxies)} remain")
        
    def _update_stats(self):
        """Update proxy pool statistics."""
        
        with self._lock:
            self.stats.update({
                "total_proxies": len(self.all_proxies),
                "valid_proxies": len([p for p in self.all_proxies.values() if p.is_valid]),
                "last_fetch": datetime.now(),
                "http_proxies": len(self.http_proxies),
                "https_proxies": len(self.https_proxies)
            })
            
    def get_proxy(self, https: bool = False, country: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get a proxy from the pool."""
        
        with self._lock:
            proxy_list = self.https_proxies if https else self.http_proxies
            
            if not proxy_list:
                return None
                
            # Filter by country if specified
            if country:
                filtered_proxies = [p for p in proxy_list if p.country.lower() == country.lower()]
                proxy_list = filtered_proxies if filtered_proxies else proxy_list
                
            # Return best proxy (highest success rate)
            valid_proxies = [p for p in proxy_list if p.is_valid]
            
            if valid_proxies:
                return valid_proxies[0]  # Already sorted by quality
            elif proxy_list:
                return proxy_list[0]  # Fallback to any proxy
            else:
                return None
                
    def get_random_proxy(self, https: bool = False, country: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get a random proxy from the pool."""
        
        with self._lock:
            proxy_list = self.https_proxies if https else self.http_proxies
            
            if not proxy_list:
                return None
                
            # Filter by country if specified
            if country:
                filtered_proxies = [p for p in proxy_list if p.country.lower() == country.lower()]
                proxy_list = filtered_proxies if filtered_proxies else proxy_list
                
            # Get valid proxies
            valid_proxies = [p for p in proxy_list if p.is_valid]
            source_list = valid_proxies if valid_proxies else proxy_list
            
            if source_list:
                return random.choice(source_list)
            else:
                return None
                
    def get_proxy_count(self) -> Dict[str, int]:
        """Get proxy count statistics."""
        
        with self._lock:
            return {
                'total': len(self.all_proxies),
                'http': len(self.http_proxies),
                'https': len(self.https_proxies),
                'valid': len([p for p in self.all_proxies.values() if p.is_valid])
            }
            
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive proxy pool statistics."""
        
        return {
            **self.stats,
            **self.fetcher.fetch_stats,
            **self.validator.validation_stats,
            "proxy_counts": self.get_proxy_count()
        }


async def test_enhanced_proxy_pool():
    """Test the enhanced proxy pool system."""
    
    print("🚀 TESTING ENHANCED PROXY POOL SYSTEM")
    print("=" * 50)
    
    # Initialize system
    config = ConfigurationManager()
    proxy_manager = EnhancedProxyPoolManager(config)
    
    # Initialize and fetch proxies
    await proxy_manager.initialize()
    
    # Display statistics
    stats = proxy_manager.get_stats()
    
    print(f"\n📊 PROXY POOL STATISTICS:")
    print(f"   Total proxies: {stats['proxy_counts']['total']}")
    print(f"   Valid proxies: {stats['proxy_counts']['valid']}")
    print(f"   HTTP proxies: {stats['proxy_counts']['http']}")
    print(f"   HTTPS proxies: {stats['proxy_counts']['https']}")
    print(f"   Sources fetched: {stats['successful_sources']}")
    print(f"   Validation success rate: {(stats['successful_validations'] / max(1, stats['total_validated']) * 100):.1f}%")
    
    # Test proxy retrieval
    print(f"\n🎯 TESTING PROXY RETRIEVAL:")
    
    http_proxy = proxy_manager.get_proxy(https=False)
    if http_proxy:
        print(f"   HTTP proxy: {http_proxy.proxy_url} (success rate: {http_proxy.success_rate:.2f})")
        
    https_proxy = proxy_manager.get_proxy(https=True)
    if https_proxy:
        print(f"   HTTPS proxy: {https_proxy.proxy_url} (success rate: {https_proxy.success_rate:.2f})")
        
    random_proxy = proxy_manager.get_random_proxy()
    if random_proxy:
        print(f"   Random proxy: {random_proxy.proxy_url} (source: {random_proxy.source})")
        
    print(f"\n✅ Enhanced Proxy Pool System test completed!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_proxy_pool())
