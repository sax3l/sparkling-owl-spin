"""
Proxy quality filtering for ECaDP platform.

Implements comprehensive proxy quality assessment including speed, reliability,
anonymity level, and geographic considerations.
"""

import asyncio
import time
import socket
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlparse
import ipaddress

import requests
import asyncio
from src.utils.logger import get_logger
from .collector import ProxyInfo

logger = get_logger(__name__)

class AnonymityLevel(Enum):
    """Proxy anonymity levels"""
    TRANSPARENT = "transparent"  # Real IP visible
    ANONYMOUS = "anonymous"      # Real IP hidden, proxy detected
    ELITE = "elite"             # Real IP hidden, proxy not detected

class GeographicRegion(Enum):
    """Geographic regions for proxy filtering"""
    NORTH_AMERICA = "north_america"
    EUROPE = "europe"
    ASIA = "asia"
    OCEANIA = "oceania"
    SOUTH_AMERICA = "south_america"
    AFRICA = "africa"
    UNKNOWN = "unknown"

@dataclass
class QualityMetrics:
    """Quality metrics for a proxy"""
    proxy_id: str
    response_time: float = 0.0
    success_rate: float = 0.0
    anonymity_level: AnonymityLevel = AnonymityLevel.TRANSPARENT
    geographic_region: GeographicRegion = GeographicRegion.UNKNOWN
    supports_https: bool = False
    uptime_percentage: float = 0.0
    last_tested: Optional[datetime] = None
    test_count: int = 0
    ban_score: float = 0.0  # Higher = more likely to be banned
    quality_score: float = 0.0  # Overall quality (0-100)
    
    def calculate_quality_score(self) -> float:
        """Calculate overall quality score"""
        score = 0.0
        
        # Response time component (30%)
        if self.response_time > 0:
            # Score decreases as response time increases
            time_score = max(0, 100 - (self.response_time * 10))
            score += time_score * 0.3
        
        # Success rate component (25%)
        score += self.success_rate * 100 * 0.25
        
        # Uptime component (20%)
        score += self.uptime_percentage * 0.2
        
        # Anonymity bonus (15%)
        anonymity_bonus = {
            AnonymityLevel.TRANSPARENT: 0,
            AnonymityLevel.ANONYMOUS: 50,
            AnonymityLevel.ELITE: 100
        }
        score += anonymity_bonus[self.anonymity_level] * 0.15
        
        # HTTPS support bonus (5%)
        if self.supports_https:
            score += 100 * 0.05
        
        # Ban score penalty (5%)
        score -= self.ban_score * 0.05
        
        self.quality_score = max(0, min(100, score))
        return self.quality_score

@dataclass
class FilterCriteria:
    """Criteria for filtering proxies"""
    min_response_time: Optional[float] = None
    max_response_time: Optional[float] = None
    min_success_rate: float = 0.8
    min_uptime: float = 0.9
    min_anonymity: AnonymityLevel = AnonymityLevel.ANONYMOUS
    required_regions: Optional[Set[GeographicRegion]] = None
    require_https: bool = False
    max_ban_score: float = 50.0
    min_quality_score: float = 70.0
    blacklisted_ips: Optional[Set[str]] = None
    whitelisted_ips: Optional[Set[str]] = None

class ProxyQualityFilter:
    """
    Advanced proxy quality filtering and assessment system.
    
    Features:
    - Multi-criteria quality assessment
    - Anonymity level detection
    - Geographic classification
    - Performance benchmarking
    - Blacklist/whitelist management
    - Dynamic quality scoring
    """
    
    def __init__(self, test_timeout: int = 10, test_urls: Optional[List[str]] = None):
        self.test_timeout = test_timeout
        self.test_urls = test_urls or [
            "http://httpbin.org/ip",
            "https://httpbin.org/ip",
            "http://httpbin.org/headers"
        ]
        
        self.quality_metrics: Dict[str, QualityMetrics] = {}
        self.geographic_db: Dict[str, GeographicRegion] = {}
        self.blacklisted_ips: Set[str] = set()
        self.whitelisted_ips: Set[str] = set()
        
        # Known anonymity test endpoints
        self.anonymity_test_urls = [
            "http://httpbin.org/headers",
            "https://httpbin.org/headers"
        ]
    
    async def test_proxy_quality(self, proxy: ProxyInfo) -> QualityMetrics:
        """Test a proxy's quality and return metrics"""
        proxy_id = f"{proxy.ip}:{proxy.port}"
        
        # Initialize or update metrics
        if proxy_id not in self.quality_metrics:
            self.quality_metrics[proxy_id] = QualityMetrics(proxy_id=proxy_id)
        
        metrics = self.quality_metrics[proxy_id]
        metrics.last_tested = datetime.utcnow()
        metrics.test_count += 1
        
        # Run all tests
        await asyncio.gather(
            self._test_response_time(proxy, metrics),
            self._test_anonymity_level(proxy, metrics),
            self._test_https_support(proxy, metrics),
            self._determine_geographic_region(proxy, metrics),
            return_exceptions=True
        )
        
        # Calculate overall quality score
        metrics.calculate_quality_score()
        
        logger.debug(f"Tested proxy {proxy_id}: quality_score={metrics.quality_score:.1f}")
        return metrics
    
    async def _test_response_time(self, proxy: ProxyInfo, metrics: QualityMetrics):
        """Test proxy response time"""
        try:
            start_time = time.time()
            
            proxy_dict = {
                'http': proxy.get_proxy_url(),
                'https': proxy.get_proxy_url()
            }
            
            response = requests.get(
                self.test_urls[0],
                proxies=proxy_dict,
                timeout=self.test_timeout
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                # Update response time with exponential moving average
                if metrics.response_time == 0:
                    metrics.response_time = response_time
                else:
                    alpha = 0.3
                    metrics.response_time = alpha * response_time + (1 - alpha) * metrics.response_time
                
                # Update success rate
                metrics.success_rate = min(1.0, metrics.success_rate + 0.1)
            else:
                metrics.success_rate = max(0.0, metrics.success_rate - 0.1)
                
        except Exception as e:
            logger.debug(f"Response time test failed for {proxy.ip}:{proxy.port}: {e}")
            metrics.success_rate = max(0.0, metrics.success_rate - 0.2)
            metrics.ban_score = min(100, metrics.ban_score + 5)
    
    async def _test_anonymity_level(self, proxy: ProxyInfo, metrics: QualityMetrics):
        """Test proxy anonymity level"""
        try:
            proxy_dict = {
                'http': proxy.get_proxy_url(),
                'https': proxy.get_proxy_url()
            }
            
            # Get our real IP first (without proxy)
            real_ip_response = requests.get("http://httpbin.org/ip", timeout=self.test_timeout)
            real_ip = real_ip_response.json().get('origin', '').split(',')[0].strip()
            
            # Test through proxy
            response = requests.get(
                "http://httpbin.org/headers",
                proxies=proxy_dict,
                timeout=self.test_timeout
            )
            
            if response.status_code == 200:
                headers = response.json().get('headers', {})
                
                # Check if real IP is leaked
                forwarded_for = headers.get('X-Forwarded-For', '')
                real_ip_leaked = real_ip in forwarded_for
                
                # Check for proxy headers
                proxy_headers = [
                    'X-Forwarded-For', 'X-Forwarded-Host', 'X-Forwarded-Proto',
                    'X-Real-Ip', 'Via', 'X-Proxy-Id', 'Forwarded'
                ]
                has_proxy_headers = any(header in headers for header in proxy_headers)
                
                if real_ip_leaked:
                    metrics.anonymity_level = AnonymityLevel.TRANSPARENT
                elif has_proxy_headers:
                    metrics.anonymity_level = AnonymityLevel.ANONYMOUS
                else:
                    metrics.anonymity_level = AnonymityLevel.ELITE
                
        except Exception as e:
            logger.debug(f"Anonymity test failed for {proxy.ip}:{proxy.port}: {e}")
            metrics.anonymity_level = AnonymityLevel.TRANSPARENT
    
    async def _test_https_support(self, proxy: ProxyInfo, metrics: QualityMetrics):
        """Test if proxy supports HTTPS"""
        try:
            proxy_dict = {
                'http': proxy.get_proxy_url(),
                'https': proxy.get_proxy_url()
            }
            
            response = requests.get(
                "https://httpbin.org/ip",
                proxies=proxy_dict,
                timeout=self.test_timeout,
                verify=False  # Skip SSL verification for testing
            )
            
            metrics.supports_https = response.status_code == 200
            
        except Exception as e:
            logger.debug(f"HTTPS test failed for {proxy.ip}:{proxy.port}: {e}")
            metrics.supports_https = False
    
    async def _determine_geographic_region(self, proxy: ProxyInfo, metrics: QualityMetrics):
        """Determine proxy's geographic region"""
        try:
            # Check cache first
            if proxy.ip in self.geographic_db:
                metrics.geographic_region = self.geographic_db[proxy.ip]
                return
            
            # Simple IP range-based geographic detection
            # In production, you'd use a GeoIP database
            ip_obj = ipaddress.ip_address(proxy.ip)
            
            if ip_obj.is_private:
                region = GeographicRegion.UNKNOWN
            else:
                # Very basic region detection (replace with real GeoIP)
                first_octet = int(proxy.ip.split('.')[0])
                if 1 <= first_octet <= 126:
                    region = GeographicRegion.NORTH_AMERICA
                elif 128 <= first_octet <= 191:
                    region = GeographicRegion.EUROPE
                elif 192 <= first_octet <= 223:
                    region = GeographicRegion.ASIA
                else:
                    region = GeographicRegion.UNKNOWN
            
            metrics.geographic_region = region
            self.geographic_db[proxy.ip] = region
            
        except Exception as e:
            logger.debug(f"Geographic detection failed for {proxy.ip}: {e}")
            metrics.geographic_region = GeographicRegion.UNKNOWN
    
    def filter_proxies(self, 
                      proxies: List[ProxyInfo], 
                      criteria: FilterCriteria) -> List[ProxyInfo]:
        """Filter proxies based on quality criteria"""
        filtered = []
        
        for proxy in proxies:
            proxy_id = f"{proxy.ip}:{proxy.port}"
            
            # Skip if not tested yet
            if proxy_id not in self.quality_metrics:
                logger.debug(f"Skipping untested proxy: {proxy_id}")
                continue
            
            metrics = self.quality_metrics[proxy_id]
            
            # Apply filters
            if not self._passes_filters(proxy, metrics, criteria):
                continue
            
            filtered.append(proxy)
        
        # Sort by quality score (highest first)
        filtered.sort(
            key=lambda p: self.quality_metrics[f"{p.ip}:{p.port}"].quality_score,
            reverse=True
        )
        
        logger.info(f"Filtered {len(filtered)} proxies from {len(proxies)} total")
        return filtered
    
    def _passes_filters(self, 
                       proxy: ProxyInfo, 
                       metrics: QualityMetrics, 
                       criteria: FilterCriteria) -> bool:
        """Check if a proxy passes all filter criteria"""
        # Check blacklist/whitelist
        if criteria.blacklisted_ips and proxy.ip in criteria.blacklisted_ips:
            return False
        
        if criteria.whitelisted_ips and proxy.ip not in criteria.whitelisted_ips:
            return False
        
        # Check response time
        if criteria.min_response_time and metrics.response_time < criteria.min_response_time:
            return False
        
        if criteria.max_response_time and metrics.response_time > criteria.max_response_time:
            return False
        
        # Check success rate
        if metrics.success_rate < criteria.min_success_rate:
            return False
        
        # Check uptime
        if metrics.uptime_percentage < criteria.min_uptime:
            return False
        
        # Check anonymity level
        anonymity_levels = {
            AnonymityLevel.TRANSPARENT: 1,
            AnonymityLevel.ANONYMOUS: 2,
            AnonymityLevel.ELITE: 3
        }
        
        if anonymity_levels[metrics.anonymity_level] < anonymity_levels[criteria.min_anonymity]:
            return False
        
        # Check geographic region
        if criteria.required_regions and metrics.geographic_region not in criteria.required_regions:
            return False
        
        # Check HTTPS support
        if criteria.require_https and not metrics.supports_https:
            return False
        
        # Check ban score
        if metrics.ban_score > criteria.max_ban_score:
            return False
        
        # Check quality score
        if metrics.quality_score < criteria.min_quality_score:
            return False
        
        return True
    
    def get_top_proxies(self, 
                       proxies: List[ProxyInfo], 
                       count: int = 10,
                       criteria: Optional[FilterCriteria] = None) -> List[ProxyInfo]:
        """Get top N proxies by quality"""
        if criteria:
            filtered = self.filter_proxies(proxies, criteria)
        else:
            filtered = [p for p in proxies if f"{p.ip}:{p.port}" in self.quality_metrics]
        
        return filtered[:count]
    
    def add_to_blacklist(self, ip: str):
        """Add IP to blacklist"""
        self.blacklisted_ips.add(ip)
        logger.info(f"Added {ip} to blacklist")
    
    def add_to_whitelist(self, ip: str):
        """Add IP to whitelist"""
        self.whitelisted_ips.add(ip)
        logger.info(f"Added {ip} to whitelist")
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get quality assessment report"""
        if not self.quality_metrics:
            return {"message": "No quality data available"}
        
        metrics_list = list(self.quality_metrics.values())
        
        # Calculate aggregated statistics
        avg_quality = sum(m.quality_score for m in metrics_list) / len(metrics_list)
        avg_response_time = sum(m.response_time for m in metrics_list if m.response_time > 0) / max(1, len([m for m in metrics_list if m.response_time > 0]))
        avg_success_rate = sum(m.success_rate for m in metrics_list) / len(metrics_list)
        
        # Count by anonymity level
        anonymity_counts = {}
        for level in AnonymityLevel:
            anonymity_counts[level.value] = len([m for m in metrics_list if m.anonymity_level == level])
        
        # Count by region
        region_counts = {}
        for region in GeographicRegion:
            region_counts[region.value] = len([m for m in metrics_list if m.geographic_region == region])
        
        return {
            'total_tested': len(metrics_list),
            'average_quality_score': avg_quality,
            'average_response_time': avg_response_time,
            'average_success_rate': avg_success_rate,
            'https_support_count': len([m for m in metrics_list if m.supports_https]),
            'anonymity_distribution': anonymity_counts,
            'geographic_distribution': region_counts,
            'blacklisted_count': len(self.blacklisted_ips),
            'whitelisted_count': len(self.whitelisted_ips)
        }