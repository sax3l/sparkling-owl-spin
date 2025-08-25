"""
Fallback strategies for anti-bot system.

Implements intelligent fallback mechanisms when initial scraping attempts fail,
including mode switching, proxy rotation, and progressive backoff.
"""

import time
import random
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)

class TransportMode(Enum):
    """Available transport modes"""
    HTTP = "http"
    BROWSER = "browser"
    STEALTH_BROWSER = "stealth_browser"

class FallbackTrigger(Enum):
    """Events that trigger fallback strategies"""
    HTTP_ERROR = "http_error"
    TIMEOUT = "timeout"
    CAPTCHA_DETECTED = "captcha_detected"
    RATE_LIMITED = "rate_limited"
    BLOCKED_IP = "blocked_ip"
    CLOUDFLARE_DETECTED = "cloudflare_detected"
    CONTENT_MISSING = "content_missing"
    JAVASCRIPT_REQUIRED = "javascript_required"

@dataclass
class FallbackAttempt:
    """Record of a fallback attempt"""
    trigger: FallbackTrigger
    original_mode: TransportMode
    fallback_mode: TransportMode
    timestamp: datetime
    success: bool = False
    error: Optional[str] = None
    response_time: Optional[float] = None

@dataclass
class DomainFallbackState:
    """Fallback state for a specific domain"""
    domain: str
    current_mode: TransportMode = TransportMode.HTTP
    consecutive_failures: int = 0
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    fallback_history: List[FallbackAttempt] = field(default_factory=list)
    banned_until: Optional[datetime] = None
    preferred_mode: Optional[TransportMode] = None
    
    @property
    def is_banned(self) -> bool:
        """Check if domain is currently banned"""
        if self.banned_until is None:
            return False
        return datetime.utcnow() < self.banned_until

class FallbackStrategy:
    """
    Intelligent fallback strategy manager for handling scraping failures.
    
    Features:
    - Mode escalation (HTTP -> Browser -> Stealth)
    - Proxy rotation on IP blocks
    - Progressive delays and backoff
    - Domain-specific learning
    - Automatic recovery
    """
    
    def __init__(self, 
                 max_retries: int = 3,
                 escalation_threshold: int = 2,
                 ban_duration: int = 3600,
                 learning_enabled: bool = True):
        self.max_retries = max_retries
        self.escalation_threshold = escalation_threshold
        self.ban_duration = ban_duration
        self.learning_enabled = learning_enabled
        
        self.domain_states: Dict[str, DomainFallbackState] = {}
        self.global_stats = {
            'total_fallbacks': 0,
            'successful_fallbacks': 0,
            'mode_switches': 0,
            'domain_bans': 0
        }
        
        # Fallback escalation rules
        self.escalation_rules = {
            FallbackTrigger.HTTP_ERROR: [TransportMode.HTTP, TransportMode.BROWSER],
            FallbackTrigger.TIMEOUT: [TransportMode.HTTP, TransportMode.BROWSER],
            FallbackTrigger.CAPTCHA_DETECTED: [TransportMode.BROWSER, TransportMode.STEALTH_BROWSER],
            FallbackTrigger.RATE_LIMITED: [TransportMode.HTTP, TransportMode.BROWSER, TransportMode.STEALTH_BROWSER],
            FallbackTrigger.BLOCKED_IP: [TransportMode.HTTP, TransportMode.BROWSER, TransportMode.STEALTH_BROWSER],
            FallbackTrigger.CLOUDFLARE_DETECTED: [TransportMode.STEALTH_BROWSER],
            FallbackTrigger.CONTENT_MISSING: [TransportMode.BROWSER, TransportMode.STEALTH_BROWSER],
            FallbackTrigger.JAVASCRIPT_REQUIRED: [TransportMode.BROWSER, TransportMode.STEALTH_BROWSER]
        }
    
    def should_attempt_fallback(self, 
                              domain: str, 
                              trigger: FallbackTrigger,
                              current_mode: TransportMode) -> bool:
        """
        Determine if a fallback should be attempted.
        
        Args:
            domain: Target domain
            trigger: What triggered the fallback
            current_mode: Current transport mode
            
        Returns:
            True if fallback should be attempted
        """
        state = self._get_domain_state(domain)
        
        # Check if domain is banned
        if state.is_banned:
            logger.debug(f"Domain {domain} is banned, no fallback attempt")
            return False
        
        # Check consecutive failures
        if state.consecutive_failures >= self.max_retries:
            logger.debug(f"Domain {domain} exceeded max retries ({self.max_retries})")
            return False
        
        # Check if we have fallback options for this trigger
        available_modes = self.escalation_rules.get(trigger, [])
        if not available_modes:
            logger.debug(f"No fallback modes available for trigger {trigger.value}")
            return False
        
        # Check if we can escalate from current mode
        try:
            current_index = available_modes.index(current_mode)
            if current_index >= len(available_modes) - 1:
                logger.debug(f"Already at highest fallback mode for trigger {trigger.value}")
                return False
        except ValueError:
            # Current mode not in escalation path, can start from beginning
            pass
        
        return True
    
    def get_fallback_strategy(self, 
                            domain: str,
                            trigger: FallbackTrigger,
                            current_mode: TransportMode,
                            error_details: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get the next fallback strategy to try.
        
        Args:
            domain: Target domain
            trigger: What triggered the fallback
            current_mode: Current transport mode
            error_details: Additional error information
            
        Returns:
            Fallback strategy configuration or None if no fallback available
        """
        if not self.should_attempt_fallback(domain, trigger, current_mode):
            return None
        
        state = self._get_domain_state(domain)
        
        # Determine next mode
        next_mode = self._get_next_mode(trigger, current_mode, state)
        if not next_mode:
            return None
        
        # Calculate delay
        delay = self._calculate_fallback_delay(state, trigger)
        
        # Determine if proxy rotation is needed
        rotate_proxy = self._should_rotate_proxy(trigger)
        
        # Build strategy
        strategy = {
            'mode': next_mode,
            'delay': delay,
            'rotate_proxy': rotate_proxy,
            'additional_headers': self._get_additional_headers(trigger, next_mode),
            'stealth_options': self._get_stealth_options(trigger, next_mode),
            'timeout': self._get_timeout(next_mode),
            'retry_count': state.consecutive_failures + 1
        }
        
        # Record the attempt
        attempt = FallbackAttempt(
            trigger=trigger,
            original_mode=current_mode,
            fallback_mode=next_mode,
            timestamp=datetime.utcnow()
        )
        state.fallback_history.append(attempt)
        
        # Update stats
        self.global_stats['total_fallbacks'] += 1
        if next_mode != current_mode:
            self.global_stats['mode_switches'] += 1
        
        logger.info(f"Fallback strategy for {domain}: {current_mode.value} -> {next_mode.value} (trigger: {trigger.value})")
        return strategy
    
    def record_fallback_result(self,
                             domain: str,
                             strategy: Dict[str, Any],
                             success: bool,
                             error: Optional[str] = None,
                             response_time: Optional[float] = None):
        """Record the result of a fallback attempt"""
        state = self._get_domain_state(domain)
        
        # Update the last attempt in history
        if state.fallback_history:
            last_attempt = state.fallback_history[-1]
            last_attempt.success = success
            last_attempt.error = error
            last_attempt.response_time = response_time
        
        if success:
            state.consecutive_failures = 0
            state.last_success = datetime.utcnow()
            state.current_mode = TransportMode(strategy['mode'])
            
            # Learn preferred mode if learning is enabled
            if self.learning_enabled:
                state.preferred_mode = state.current_mode
            
            self.global_stats['successful_fallbacks'] += 1
            logger.info(f"Fallback successful for {domain}: mode={strategy['mode']}")
            
        else:
            state.consecutive_failures += 1
            state.last_failure = datetime.utcnow()
            
            # Check if we should ban the domain
            if state.consecutive_failures >= self.max_retries:
                state.banned_until = datetime.utcnow() + timedelta(seconds=self.ban_duration)
                self.global_stats['domain_bans'] += 1
                logger.warning(f"Banned domain {domain} for {self.ban_duration}s after {state.consecutive_failures} failures")
    
    def _get_domain_state(self, domain: str) -> DomainFallbackState:
        """Get or create domain fallback state"""
        if domain not in self.domain_states:
            # Check if we have a learned preferred mode for this domain
            preferred_mode = self._get_learned_mode(domain)
            self.domain_states[domain] = DomainFallbackState(
                domain=domain,
                current_mode=preferred_mode or TransportMode.HTTP,
                preferred_mode=preferred_mode
            )
        return self.domain_states[domain]
    
    def _get_next_mode(self, 
                      trigger: FallbackTrigger, 
                      current_mode: TransportMode,
                      state: DomainFallbackState) -> Optional[TransportMode]:
        """Determine the next transport mode to try"""
        # Get escalation path for this trigger
        escalation_path = self.escalation_rules.get(trigger, [])
        
        if not escalation_path:
            return None
        
        # If we have a preferred mode and haven't tried it yet, use it
        if state.preferred_mode and state.preferred_mode in escalation_path:
            if state.preferred_mode != current_mode:
                return state.preferred_mode
        
        # Otherwise, follow escalation path
        try:
            current_index = escalation_path.index(current_mode)
            if current_index < len(escalation_path) - 1:
                return escalation_path[current_index + 1]
        except ValueError:
            # Current mode not in path, start from first mode
            return escalation_path[0]
        
        return None
    
    def _calculate_fallback_delay(self, 
                                state: DomainFallbackState, 
                                trigger: FallbackTrigger) -> float:
        """Calculate delay before fallback attempt"""
        base_delay = 1.0
        
        # Increase delay based on consecutive failures
        exponential_delay = base_delay * (2 ** min(state.consecutive_failures, 5))
        
        # Add trigger-specific delays
        trigger_delays = {
            FallbackTrigger.RATE_LIMITED: 5.0,
            FallbackTrigger.BLOCKED_IP: 10.0,
            FallbackTrigger.CAPTCHA_DETECTED: 2.0,
            FallbackTrigger.CLOUDFLARE_DETECTED: 15.0
        }
        
        trigger_delay = trigger_delays.get(trigger, 0.0)
        
        # Combine delays and add jitter
        total_delay = exponential_delay + trigger_delay
        jitter = random.uniform(0.8, 1.2)
        
        return total_delay * jitter
    
    def _should_rotate_proxy(self, trigger: FallbackTrigger) -> bool:
        """Determine if proxy should be rotated"""
        proxy_rotation_triggers = {
            FallbackTrigger.BLOCKED_IP,
            FallbackTrigger.RATE_LIMITED,
            FallbackTrigger.CLOUDFLARE_DETECTED
        }
        return trigger in proxy_rotation_triggers
    
    def _get_additional_headers(self, 
                              trigger: FallbackTrigger, 
                              mode: TransportMode) -> Dict[str, str]:
        """Get additional headers for fallback attempt"""
        headers = {}
        
        if trigger == FallbackTrigger.CLOUDFLARE_DETECTED:
            headers.update({
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Upgrade-Insecure-Requests': '1'
            })
        
        if mode == TransportMode.STEALTH_BROWSER:
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1'
            })
        
        return headers
    
    def _get_stealth_options(self, 
                           trigger: FallbackTrigger, 
                           mode: TransportMode) -> Dict[str, Any]:
        """Get stealth options for browser mode"""
        if mode not in [TransportMode.BROWSER, TransportMode.STEALTH_BROWSER]:
            return {}
        
        options = {
            'disable_images': False,
            'disable_javascript': False,
            'user_agent_rotation': True,
            'viewport_randomization': True
        }
        
        if mode == TransportMode.STEALTH_BROWSER:
            options.update({
                'webdriver_stealth': True,
                'fingerprint_evasion': True,
                'canvas_randomization': True,
                'timezone_randomization': True
            })
        
        if trigger == FallbackTrigger.CLOUDFLARE_DETECTED:
            options.update({
                'cloudflare_bypass': True,
                'extra_stealth': True
            })
        
        return options
    
    def _get_timeout(self, mode: TransportMode) -> int:
        """Get timeout for transport mode"""
        timeouts = {
            TransportMode.HTTP: 30,
            TransportMode.BROWSER: 60,
            TransportMode.STEALTH_BROWSER: 90
        }
        return timeouts.get(mode, 30)
    
    def _get_learned_mode(self, domain: str) -> Optional[TransportMode]:
        """Get learned preferred mode for domain"""
        if not self.learning_enabled:
            return None
        
        if domain in self.domain_states:
            return self.domain_states[domain].preferred_mode
        
        # Could implement persistent learning storage here
        return None
    
    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a specific domain"""
        if domain not in self.domain_states:
            return {}
        
        state = self.domain_states[domain]
        
        # Calculate success rate from history
        if state.fallback_history:
            successful = sum(1 for attempt in state.fallback_history if attempt.success)
            success_rate = successful / len(state.fallback_history)
        else:
            success_rate = 0.0
        
        return {
            'current_mode': state.current_mode.value,
            'preferred_mode': state.preferred_mode.value if state.preferred_mode else None,
            'consecutive_failures': state.consecutive_failures,
            'is_banned': state.is_banned,
            'banned_until': state.banned_until.isoformat() if state.banned_until else None,
            'total_attempts': len(state.fallback_history),
            'success_rate': success_rate,
            'last_success': state.last_success.isoformat() if state.last_success else None,
            'last_failure': state.last_failure.isoformat() if state.last_failure else None
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global fallback statistics"""
        total_domains = len(self.domain_states)
        banned_domains = sum(1 for state in self.domain_states.values() if state.is_banned)
        
        # Calculate average success rate
        if self.global_stats['total_fallbacks'] > 0:
            success_rate = self.global_stats['successful_fallbacks'] / self.global_stats['total_fallbacks']
        else:
            success_rate = 0.0
        
        return {
            'total_fallbacks': self.global_stats['total_fallbacks'],
            'successful_fallbacks': self.global_stats['successful_fallbacks'],
            'mode_switches': self.global_stats['mode_switches'],
            'domain_bans': self.global_stats['domain_bans'],
            'success_rate': success_rate,
            'total_domains': total_domains,
            'banned_domains': banned_domains
        }
    
    def reset_domain(self, domain: str):
        """Reset fallback state for a domain"""
        if domain in self.domain_states:
            # Keep preferred mode if learning is enabled
            preferred_mode = self.domain_states[domain].preferred_mode if self.learning_enabled else None
            self.domain_states[domain] = DomainFallbackState(
                domain=domain,
                preferred_mode=preferred_mode
            )
            logger.info(f"Reset fallback state for domain: {domain}")
    
    def unban_domain(self, domain: str):
        """Manually unban a domain"""
        if domain in self.domain_states:
            state = self.domain_states[domain]
            state.banned_until = None
            state.consecutive_failures = 0
            logger.info(f"Manually unbanned domain: {domain}")