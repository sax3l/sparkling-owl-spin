"""
Proxy rotation strategies for ECaDP platform.

Implements intelligent proxy rotation with health tracking, load balancing,
and adaptive selection based on success rates and response times.
"""

import random
import time
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque

from src.utils.logger import get_logger
from .collector import ProxyInfo

logger = get_logger(__name__)

class RotationStrategy(Enum):
    """Available proxy rotation strategies"""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    WEIGHTED_RANDOM = "weighted_random"
    LEAST_USED = "least_used"
    BEST_PERFORMANCE = "best_performance"
    ADAPTIVE = "adaptive"

@dataclass
class ProxyStats:
    """Statistics for a proxy"""
    proxy_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    banned_until: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate (0.0 to 1.0)"""
        if self.total_requests == 0:
            return 1.0  # New proxy gets benefit of doubt
        return self.successful_requests / self.total_requests
    
    @property
    def average_response_time(self) -> float:
        """Calculate average response time"""
        if self.successful_requests == 0:
            return float('inf')
        return self.total_response_time / self.successful_requests
    
    @property
    def is_banned(self) -> bool:
        """Check if proxy is currently banned"""
        if self.banned_until is None:
            return False
        return datetime.utcnow() < self.banned_until
    
    @property
    def health_score(self) -> float:
        """Calculate overall health score (0.0 to 1.0)"""
        if self.is_banned:
            return 0.0
            
        # Base score from success rate
        score = self.success_rate
        
        # Penalize high response times
        if self.average_response_time < float('inf'):
            response_penalty = min(0.5, self.average_response_time / 10.0)  # Max 50% penalty
            score *= (1.0 - response_penalty)
        
        # Penalize consecutive failures
        failure_penalty = min(0.8, self.consecutive_failures * 0.1)  # Max 80% penalty
        score *= (1.0 - failure_penalty)
        
        # Bonus for recent successful usage
        if self.last_success:
            hours_since_success = (datetime.utcnow() - self.last_success).total_seconds() / 3600
            if hours_since_success < 1:  # Bonus for usage within last hour
                score *= 1.1
        
        return max(0.0, min(1.0, score))

class ProxyRotator:
    """
    Intelligent proxy rotator with multiple strategies and health tracking.
    
    Features:
    - Multiple rotation strategies
    - Proxy health tracking
    - Automatic ban detection and recovery
    - Performance-based selection
    - Load balancing
    """
    
    def __init__(self, 
                 strategy: RotationStrategy = RotationStrategy.ADAPTIVE,
                 health_check_interval: int = 300,  # 5 minutes
                 ban_threshold: int = 5,  # Consecutive failures before ban
                 ban_duration: int = 3600):  # 1 hour ban
        self.strategy = strategy
        self.health_check_interval = health_check_interval
        self.ban_threshold = ban_threshold
        self.ban_duration = ban_duration
        
        self.proxies: List[ProxyInfo] = []
        self.proxy_stats: Dict[str, ProxyStats] = {}
        self.round_robin_index = 0
        self.last_health_check = datetime.utcnow()
        
        # Strategy-specific state
        self.domain_proxy_mapping: Dict[str, str] = {}  # Sticky sessions per domain
        self.load_balancer_weights: Dict[str, float] = {}
        
    def add_proxy(self, proxy: ProxyInfo):
        """Add a proxy to the rotation pool"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            proxy_id = f"{proxy.ip}:{proxy.port}"
            if proxy_id not in self.proxy_stats:
                self.proxy_stats[proxy_id] = ProxyStats(proxy_id=proxy_id)
            logger.info(f"Added proxy to rotator: {proxy_id}")
    
    def remove_proxy(self, proxy: ProxyInfo):
        """Remove a proxy from the rotation pool"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            proxy_id = f"{proxy.ip}:{proxy.port}"
            if proxy_id in self.proxy_stats:
                del self.proxy_stats[proxy_id]
            logger.info(f"Removed proxy from rotator: {proxy_id}")
    
    def get_next_proxy(self, 
                      domain: Optional[str] = None,
                      exclude_proxies: Optional[List[str]] = None) -> Optional[ProxyInfo]:
        """
        Get the next proxy according to the rotation strategy.
        
        Args:
            domain: Target domain (for sticky sessions)
            exclude_proxies: List of proxy IDs to exclude
            
        Returns:
            Next proxy to use, or None if no suitable proxy available
        """
        # Health check if needed
        if self._should_run_health_check():
            self._run_health_check()
        
        # Filter available proxies
        available_proxies = self._get_available_proxies(exclude_proxies)
        
        if not available_proxies:
            logger.warning("No available proxies for rotation")
            return None
        
        # Select proxy based on strategy
        if self.strategy == RotationStrategy.ROUND_ROBIN:
            proxy = self._round_robin_selection(available_proxies)
        elif self.strategy == RotationStrategy.RANDOM:
            proxy = self._random_selection(available_proxies)
        elif self.strategy == RotationStrategy.WEIGHTED_RANDOM:
            proxy = self._weighted_random_selection(available_proxies)
        elif self.strategy == RotationStrategy.LEAST_USED:
            proxy = self._least_used_selection(available_proxies)
        elif self.strategy == RotationStrategy.BEST_PERFORMANCE:
            proxy = self._best_performance_selection(available_proxies)
        elif self.strategy == RotationStrategy.ADAPTIVE:
            proxy = self._adaptive_selection(available_proxies, domain)
        else:
            proxy = self._random_selection(available_proxies)
        
        if proxy:
            proxy_id = f"{proxy.ip}:{proxy.port}"
            self.proxy_stats[proxy_id].last_used = datetime.utcnow()
            logger.debug(f"Selected proxy: {proxy_id} (strategy: {self.strategy.value})")
        
        return proxy
    
    def record_request_result(self, 
                            proxy: ProxyInfo,
                            success: bool,
                            response_time: Optional[float] = None,
                            error: Optional[str] = None):
        """Record the result of a request using a proxy"""
        proxy_id = f"{proxy.ip}:{proxy.port}"
        
        if proxy_id not in self.proxy_stats:
            self.proxy_stats[proxy_id] = ProxyStats(proxy_id=proxy_id)
        
        stats = self.proxy_stats[proxy_id]
        stats.total_requests += 1
        
        if success:
            stats.successful_requests += 1
            stats.last_success = datetime.utcnow()
            stats.consecutive_failures = 0
            
            if response_time is not None:
                stats.total_response_time += response_time
                
        else:
            stats.failed_requests += 1
            stats.last_failure = datetime.utcnow()
            stats.consecutive_failures += 1
            
            # Check if we should ban this proxy
            if stats.consecutive_failures >= self.ban_threshold:
                stats.banned_until = datetime.utcnow() + timedelta(seconds=self.ban_duration)
                logger.warning(f"Banned proxy {proxy_id} for {self.ban_duration}s after {stats.consecutive_failures} consecutive failures")
        
        logger.debug(f"Recorded result for {proxy_id}: success={success}, response_time={response_time}")
    
    def _get_available_proxies(self, exclude_proxies: Optional[List[str]] = None) -> List[ProxyInfo]:
        """Get list of available (non-banned) proxies"""
        exclude_set = set(exclude_proxies or [])
        available = []
        
        for proxy in self.proxies:
            proxy_id = f"{proxy.ip}:{proxy.port}"
            
            if proxy_id in exclude_set:
                continue
                
            if proxy_id in self.proxy_stats:
                if self.proxy_stats[proxy_id].is_banned:
                    continue
            
            available.append(proxy)
        
        return available
    
    def _round_robin_selection(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Round-robin selection"""
        if not proxies:
            return None
            
        self.round_robin_index = (self.round_robin_index + 1) % len(proxies)
        return proxies[self.round_robin_index]
    
    def _random_selection(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Random selection"""
        return random.choice(proxies) if proxies else None
    
    def _weighted_random_selection(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Weighted random selection based on health scores"""
        if not proxies:
            return None
        
        weights = []
        for proxy in proxies:
            proxy_id = f"{proxy.ip}:{proxy.port}"
            if proxy_id in self.proxy_stats:
                weight = self.proxy_stats[proxy_id].health_score
            else:
                weight = 1.0  # New proxy gets full weight
            weights.append(weight)
        
        # If all weights are 0, fall back to random
        if sum(weights) == 0:
            return self._random_selection(proxies)
        
        return random.choices(proxies, weights=weights)[0]
    
    def _least_used_selection(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Select the least used proxy"""
        if not proxies:
            return None
        
        min_usage = float('inf')
        best_proxy = None
        
        for proxy in proxies:
            proxy_id = f"{proxy.ip}:{proxy.port}"
            if proxy_id in self.proxy_stats:
                usage = self.proxy_stats[proxy_id].total_requests
            else:
                usage = 0
            
            if usage < min_usage:
                min_usage = usage
                best_proxy = proxy
        
        return best_proxy or proxies[0]
    
    def _best_performance_selection(self, proxies: List[ProxyInfo]) -> Optional[ProxyInfo]:
        """Select the best performing proxy"""
        if not proxies:
            return None
        
        best_score = -1
        best_proxy = None
        
        for proxy in proxies:
            proxy_id = f"{proxy.ip}:{proxy.port}"
            if proxy_id in self.proxy_stats:
                score = self.proxy_stats[proxy_id].health_score
            else:
                score = 1.0  # New proxy gets benefit of doubt
            
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        return best_proxy or proxies[0]
    
    def _adaptive_selection(self, proxies: List[ProxyInfo], domain: Optional[str] = None) -> Optional[ProxyInfo]:
        """Adaptive selection combining multiple factors"""
        if not proxies:
            return None
        
        # Check for sticky session
        if domain and domain in self.domain_proxy_mapping:
            sticky_proxy_id = self.domain_proxy_mapping[domain]
            for proxy in proxies:
                if f"{proxy.ip}:{proxy.port}" == sticky_proxy_id:
                    # Check if sticky proxy is still healthy
                    if sticky_proxy_id in self.proxy_stats:
                        if self.proxy_stats[sticky_proxy_id].health_score > 0.5:
                            return proxy
                    break
        
        # Use weighted random selection for general adaptive behavior
        selected_proxy = self._weighted_random_selection(proxies)
        
        # Establish sticky session for domain
        if domain and selected_proxy:
            self.domain_proxy_mapping[domain] = f"{selected_proxy.ip}:{selected_proxy.port}"
        
        return selected_proxy
    
    def _should_run_health_check(self) -> bool:
        """Check if it's time to run health check"""
        return (datetime.utcnow() - self.last_health_check).total_seconds() > self.health_check_interval
    
    def _run_health_check(self):
        """Run health check and update proxy status"""
        current_time = datetime.utcnow()
        self.last_health_check = current_time
        
        for proxy_id, stats in self.proxy_stats.items():
            # Unban proxies that have served their time
            if stats.banned_until and current_time >= stats.banned_until:
                stats.banned_until = None
                stats.consecutive_failures = 0
                logger.info(f"Unbanned proxy: {proxy_id}")
        
        logger.debug("Completed proxy health check")
    
    def get_rotation_stats(self) -> Dict[str, Any]:
        """Get rotation statistics"""
        total_proxies = len(self.proxies)
        banned_proxies = sum(1 for stats in self.proxy_stats.values() if stats.is_banned)
        
        # Calculate average health score
        health_scores = [stats.health_score for stats in self.proxy_stats.values()]
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
        
        return {
            'strategy': self.strategy.value,
            'total_proxies': total_proxies,
            'available_proxies': total_proxies - banned_proxies,
            'banned_proxies': banned_proxies,
            'average_health_score': avg_health,
            'proxy_stats': {proxy_id: {
                'total_requests': stats.total_requests,
                'success_rate': stats.success_rate,
                'average_response_time': stats.average_response_time,
                'health_score': stats.health_score,
                'is_banned': stats.is_banned
            } for proxy_id, stats in self.proxy_stats.items()}
        }
    
    def reset_proxy_stats(self, proxy_id: Optional[str] = None):
        """Reset statistics for a proxy or all proxies"""
        if proxy_id:
            if proxy_id in self.proxy_stats:
                self.proxy_stats[proxy_id] = ProxyStats(proxy_id=proxy_id)
                logger.info(f"Reset stats for proxy: {proxy_id}")
        else:
            for proxy_id in self.proxy_stats:
                self.proxy_stats[proxy_id] = ProxyStats(proxy_id=proxy_id)
            logger.info("Reset stats for all proxies")