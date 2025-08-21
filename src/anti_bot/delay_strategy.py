"""
Advanced delay strategies for anti-bot system.

Implements various delay strategies including adaptive backoff, domain-specific delays,
and traffic pattern mimicking.
"""

import time
import random
import math
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlparse

from src.utils.logger import get_logger

logger = get_logger(__name__)

class DelayStrategy(Enum):
    """Available delay strategies"""
    FIXED = "fixed"
    RANDOM = "random"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"
    HUMAN_LIKE = "human_like"
    RESPECTFUL = "respectful"

@dataclass
class DelayConfig:
    """Configuration for delay strategies"""
    strategy: DelayStrategy = DelayStrategy.RESPECTFUL
    min_delay: float = 1.0
    max_delay: float = 5.0
    base_delay: float = 1.0
    backoff_multiplier: float = 2.0
    max_backoff: float = 60.0
    jitter: bool = True
    respect_robots_delay: bool = True

@dataclass
class DomainDelayState:
    """Track delay state per domain"""
    last_request: Optional[datetime] = None
    consecutive_errors: int = 0
    current_backoff: float = 0.0
    robots_delay: Optional[float] = None
    request_count: int = 0
    success_rate: float = 1.0

class DelayManager:
    """
    Manages delays between requests with various strategies.
    
    Features:
    - Multiple delay strategies
    - Domain-specific tracking
    - Adaptive backoff on errors
    - Robots.txt compliance
    - Human-like traffic patterns
    """
    
    def __init__(self, config: DelayConfig = None):
        self.config = config or DelayConfig()
        self.domain_states: Dict[str, DomainDelayState] = {}
        
    def calculate_delay(self, 
                       url: str, 
                       success: bool = True, 
                       response_time: Optional[float] = None,
                       robots_delay: Optional[float] = None) -> float:
        """
        Calculate the delay for next request to given URL.
        
        Args:
            url: Target URL
            success: Whether last request was successful
            response_time: Response time of last request
            robots_delay: Crawl-Delay from robots.txt
            
        Returns:
            Delay in seconds
        """
        domain = self._extract_domain(url)
        state = self._get_domain_state(domain)
        
        # Update robots delay if provided
        if robots_delay is not None:
            state.robots_delay = robots_delay
            
        # Update state based on request result
        self._update_domain_state(state, success, response_time)
        
        # Calculate base delay
        delay = self._calculate_base_delay(state)
        
        # Apply strategy-specific modifications
        delay = self._apply_strategy(delay, state)
        
        # Respect robots.txt delay
        if self.config.respect_robots_delay and state.robots_delay:
            delay = max(delay, state.robots_delay)
            
        # Add jitter if enabled
        if self.config.jitter:
            delay = self._add_jitter(delay)
            
        logger.debug(f"Calculated delay for {domain}: {delay:.2f}s (strategy: {self.config.strategy.value})")
        return delay
        
    def apply_delay(self, 
                   url: str, 
                   success: bool = True, 
                   response_time: Optional[float] = None,
                   robots_delay: Optional[float] = None) -> float:
        """
        Calculate and apply delay.
        
        Returns:
            Actual delay applied
        """
        delay = self.calculate_delay(url, success, response_time, robots_delay)
        
        if delay > 0:
            logger.debug(f"Applying delay: {delay:.2f}s for {self._extract_domain(url)}")
            time.sleep(delay)
            
        return delay
        
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower()
        except Exception:
            return "unknown"
            
    def _get_domain_state(self, domain: str) -> DomainDelayState:
        """Get or create domain state"""
        if domain not in self.domain_states:
            self.domain_states[domain] = DomainDelayState()
        return self.domain_states[domain]
        
    def _update_domain_state(self, 
                           state: DomainDelayState, 
                           success: bool, 
                           response_time: Optional[float]):
        """Update domain state based on request result"""
        state.last_request = datetime.utcnow()
        state.request_count += 1
        
        if success:
            state.consecutive_errors = 0
            state.current_backoff = max(0, state.current_backoff * 0.5)  # Reduce backoff on success
            
            # Update success rate (exponential moving average)
            alpha = 0.1
            state.success_rate = (1 - alpha) * state.success_rate + alpha * 1.0
        else:
            state.consecutive_errors += 1
            
            # Increase backoff on errors
            if state.consecutive_errors > 1:
                state.current_backoff = min(
                    self.config.max_backoff,
                    max(self.config.base_delay, state.current_backoff * self.config.backoff_multiplier)
                )
                
            # Update success rate
            alpha = 0.1
            state.success_rate = (1 - alpha) * state.success_rate + alpha * 0.0
            
    def _calculate_base_delay(self, state: DomainDelayState) -> float:
        """Calculate base delay based on configuration"""
        if self.config.strategy == DelayStrategy.FIXED:
            return self.config.base_delay
            
        elif self.config.strategy == DelayStrategy.RANDOM:
            return random.uniform(self.config.min_delay, self.config.max_delay)
            
        elif self.config.strategy == DelayStrategy.EXPONENTIAL_BACKOFF:
            if state.consecutive_errors > 0:
                return min(
                    self.config.max_backoff,
                    self.config.base_delay * (self.config.backoff_multiplier ** state.consecutive_errors)
                )
            return self.config.base_delay
            
        elif self.config.strategy == DelayStrategy.ADAPTIVE:
            # Adapt based on success rate and response time
            base = self.config.base_delay
            
            # Increase delay if success rate is low
            if state.success_rate < 0.8:
                base *= (1.0 - state.success_rate) * 2 + 1
                
            # Add current backoff
            return base + state.current_backoff
            
        elif self.config.strategy == DelayStrategy.HUMAN_LIKE:
            return self._human_like_delay(state)
            
        elif self.config.strategy == DelayStrategy.RESPECTFUL:
            return self._respectful_delay(state)
            
        return self.config.base_delay
        
    def _apply_strategy(self, delay: float, state: DomainDelayState) -> float:
        """Apply strategy-specific modifications"""
        # Add backoff if there were recent errors
        if state.consecutive_errors > 0:
            delay += state.current_backoff
            
        return max(self.config.min_delay, min(self.config.max_delay, delay))
        
    def _human_like_delay(self, state: DomainDelayState) -> float:
        """Generate human-like delay patterns"""
        # Base delay with variation
        base = random.uniform(2.0, 8.0)
        
        # Occasional longer pauses (simulating user thinking/distraction)
        if random.random() < 0.1:  # 10% chance
            base += random.uniform(5.0, 30.0)
            
        # Slightly faster if we've been successful
        if state.success_rate > 0.9:
            base *= 0.8
            
        return base
        
    def _respectful_delay(self, state: DomainDelayState) -> float:
        """Generate respectful delay that adapts to server load"""
        base = self.config.base_delay
        
        # Increase delay if we're seeing errors (server might be overloaded)
        if state.success_rate < 0.9:
            base *= (2.0 - state.success_rate)  # Scale based on success rate
            
        # Add small random component
        variation = base * 0.3 * random.random()
        
        return base + variation
        
    def _add_jitter(self, delay: float) -> float:
        """Add random jitter to delay"""
        jitter_amount = delay * 0.1  # 10% jitter
        jitter = random.uniform(-jitter_amount, jitter_amount)
        return max(0.1, delay + jitter)
        
    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a domain"""
        if domain not in self.domain_states:
            return {}
            
        state = self.domain_states[domain]
        return {
            'request_count': state.request_count,
            'success_rate': state.success_rate,
            'consecutive_errors': state.consecutive_errors,
            'current_backoff': state.current_backoff,
            'robots_delay': state.robots_delay,
            'last_request': state.last_request.isoformat() if state.last_request else None
        }
        
    def reset_domain_state(self, domain: str):
        """Reset state for a domain"""
        if domain in self.domain_states:
            del self.domain_states[domain]
            logger.info(f"Reset delay state for domain: {domain}")

# Convenience functions for backward compatibility
def apply_delay(min_delay: int = 1, max_delay: int = 5):
    """Applies a random delay to be respectful to servers."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)