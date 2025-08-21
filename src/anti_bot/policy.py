from src.utils.contracts import FetchPolicy

class PolicyService:
    """
    Central service for making decisions about how to fetch a URL.
    """
    def decide(self, domain: str, path: str | None = None, last_errors: list[int] = []) -> FetchPolicy:
        """
        Reads domain profiles, error history, and other signals to decide
        on the appropriate fetch policy.
        """
        # TODO: Implement logic to read from config/anti_bot.yml and adapt based on feedback.
        # For now, return a default, cautious policy.
        return FetchPolicy(
            transport="http",
            user_agent_family="chrome",
            delay_ms_range=(2000, 5000),
            reuse_session_s=300
        )

    def feedback(self, domain: str, status_code: int | None, rtt_ms: int | None):
        """
        Receives feedback from fetchers to update error rates and telemetry,
        which influences future policy decisions.
        """
        """
Anti-bot policy management system.

Implements adaptive policies for bot detection avoidance,
including risk assessment, behavior modification, and
dynamic strategy adjustment.
"""

import time
import random
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib

from src.utils.logger import get_logger

logger = get_logger(__name__)

class RiskLevel(Enum):
    """Risk assessment levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PolicyAction(Enum):
    """Available policy actions"""
    ALLOW = "allow"
    DELAY = "delay"
    ROTATE_PROXY = "rotate_proxy"
    SWITCH_USER_AGENT = "switch_user_agent"
    INCREASE_DELAY = "increase_delay"
    FALLBACK_MODE = "fallback_mode"
    PAUSE_DOMAIN = "pause_domain"
    BLOCK = "block"

class DetectionSignal(Enum):
    """Bot detection signals"""
    CAPTCHA = "captcha"
    RATE_LIMIT = "rate_limit"
    IP_BLOCK = "ip_block"
    UNUSUAL_RESPONSE = "unusual_response"
    CLOUDFLARE_CHALLENGE = "cloudflare_challenge"
    HTTP_403 = "http_403"
    HTTP_429 = "http_429"
    EMPTY_RESPONSE = "empty_response"
    REDIRECT_LOOP = "redirect_loop"

@dataclass
class PolicyRule:
    """A single policy rule"""
    name: str
    conditions: Dict[str, Any]
    actions: List[PolicyAction]
    priority: int = 100
    enabled: bool = True
    hit_count: int = 0
    last_triggered: Optional[datetime] = None
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if rule matches current context"""
        for key, condition in self.conditions.items():
            if key not in context:
                return False
            
            value = context[key]
            
            if isinstance(condition, dict):
                # Complex condition with operators
                if 'equals' in condition and value != condition['equals']:
                    return False
                if 'in' in condition and value not in condition['in']:
                    return False
                if 'gt' in condition and value <= condition['gt']:
                    return False
                if 'lt' in condition and value >= condition['lt']:
                    return False
                if 'contains' in condition and condition['contains'] not in str(value):
                    return False
            else:
                # Simple equality check
                if value != condition:
                    return False
        
        return True
    
    def trigger(self):
        """Record rule trigger"""
        self.hit_count += 1
        self.last_triggered = datetime.utcnow()

@dataclass
class DomainProfile:
    """Risk and behavior profile for a domain"""
    domain: str
    risk_level: RiskLevel = RiskLevel.LOW
    detection_signals: List[DetectionSignal] = field(default_factory=list)
    last_detection: Optional[datetime] = None
    request_count: int = 0
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    blocked_until: Optional[datetime] = None
    preferred_delay: float = 1.0
    requires_js: bool = False
    has_cloudflare: bool = False
    captcha_probability: float = 0.0
    
    @property
    def is_blocked(self) -> bool:
        """Check if domain is currently blocked"""
        if self.blocked_until is None:
            return False
        return datetime.utcnow() < self.blocked_until
    
    def add_detection_signal(self, signal: DetectionSignal):
        """Add a detection signal"""
        self.detection_signals.append(signal)
        self.last_detection = datetime.utcnow()
        
        # Update risk level based on recent signals
        recent_signals = [
            s for s in self.detection_signals[-10:]  # Last 10 signals
        ]
        
        if len(recent_signals) >= 5:
            self.risk_level = RiskLevel.CRITICAL
        elif len(recent_signals) >= 3:
            self.risk_level = RiskLevel.HIGH
        elif len(recent_signals) >= 2:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW

class AntiBot:
    """
    Adaptive anti-bot policy engine.
    
    Features:
    - Risk assessment and profiling
    - Dynamic policy adjustment
    - Behavior modification
    - Detection signal learning
    - Domain-specific strategies
    """
    
    def __init__(self, 
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 learning_enabled: bool = True):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.learning_enabled = learning_enabled
        
        self.rules: List[PolicyRule] = []
        self.domain_profiles: Dict[str, DomainProfile] = {}
        self.global_stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'detection_signals': 0,
            'policy_triggers': 0
        }
        
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default anti-bot policy rules"""
        
        # High-priority blocking rules
        self.rules.extend([
            PolicyRule(
                name="critical_risk_block",
                conditions={'risk_level': RiskLevel.CRITICAL},
                actions=[PolicyAction.PAUSE_DOMAIN],
                priority=10
            ),
            PolicyRule(
                name="ip_block_detected",
                conditions={'last_signal': DetectionSignal.IP_BLOCK},
                actions=[PolicyAction.ROTATE_PROXY, PolicyAction.INCREASE_DELAY],
                priority=20
            ),
            PolicyRule(
                name="captcha_detected",
                conditions={'last_signal': DetectionSignal.CAPTCHA},
                actions=[PolicyAction.FALLBACK_MODE, PolicyAction.INCREASE_DELAY],
                priority=25
            ),
            PolicyRule(
                name="cloudflare_challenge",
                conditions={'last_signal': DetectionSignal.CLOUDFLARE_CHALLENGE},
                actions=[PolicyAction.FALLBACK_MODE, PolicyAction.SWITCH_USER_AGENT],
                priority=30
            )
        ])
        
        # Medium-priority rate limiting rules
        self.rules.extend([
            PolicyRule(
                name="rate_limit_detected",
                conditions={'last_signal': DetectionSignal.RATE_LIMIT},
                actions=[PolicyAction.INCREASE_DELAY],
                priority=50
            ),
            PolicyRule(
                name="high_risk_delay",
                conditions={'risk_level': RiskLevel.HIGH},
                actions=[PolicyAction.INCREASE_DELAY, PolicyAction.SWITCH_USER_AGENT],
                priority=60
            ),
            PolicyRule(
                name="http_429_response",
                conditions={'last_signal': DetectionSignal.HTTP_429},
                actions=[PolicyAction.DELAY, PolicyAction.ROTATE_PROXY],
                priority=70
            )
        ])
        
        # Low-priority preventive rules
        self.rules.extend([
            PolicyRule(
                name="medium_risk_caution",
                conditions={'risk_level': RiskLevel.MEDIUM},
                actions=[PolicyAction.DELAY, PolicyAction.SWITCH_USER_AGENT],
                priority=80
            ),
            PolicyRule(
                name="cloudflare_domain",
                conditions={'has_cloudflare': True},
                actions=[PolicyAction.DELAY, PolicyAction.SWITCH_USER_AGENT],
                priority=90
            ),
            PolicyRule(
                name="high_request_rate",
                conditions={'request_rate': {'gt': 10}},
                actions=[PolicyAction.INCREASE_DELAY],
                priority=100
            )
        ])
    
    def assess_request(self, 
                      domain: str,
                      url: str,
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess a request and determine policy actions.
        
        Args:
            domain: Target domain
            url: Target URL
            context: Additional context information
            
        Returns:
            Policy decision with actions and parameters
        """
        profile = self._get_domain_profile(domain)
        
        # Build assessment context
        assessment_context = {
            'domain': domain,
            'url': url,
            'risk_level': profile.risk_level,
            'is_blocked': profile.is_blocked,
            'has_cloudflare': profile.has_cloudflare,
            'requires_js': profile.requires_js,
            'request_count': profile.request_count,
            'success_rate': profile.success_rate,
            'captcha_probability': profile.captcha_probability
        }
        
        # Add recent detection signals
        if profile.detection_signals:
            assessment_context['last_signal'] = profile.detection_signals[-1]
            assessment_context['recent_signals'] = len(profile.detection_signals[-5:])
        
        # Add context information
        if context:
            assessment_context.update(context)
        
        # Calculate request rate
        now = datetime.utcnow()
        recent_window = timedelta(minutes=5)
        # This would typically track actual request timestamps
        assessment_context['request_rate'] = profile.request_count / 5.0  # Simplified
        
        # Find matching rules
        triggered_rules = []
        for rule in sorted(self.rules, key=lambda r: r.priority):
            if rule.enabled and rule.matches(assessment_context):
                rule.trigger()
                triggered_rules.append(rule)
        
        # Determine actions
        actions = []
        for rule in triggered_rules:
            actions.extend(rule.actions)
        
        # Remove duplicates while preserving order
        unique_actions = []
        for action in actions:
            if action not in unique_actions:
                unique_actions.append(action)
        
        # Calculate delay
        delay = self._calculate_delay(profile, unique_actions, assessment_context)
        
        # Build decision
        decision = {
            'allowed': PolicyAction.BLOCK not in unique_actions and not profile.is_blocked,
            'actions': unique_actions,
            'delay': delay,
            'risk_level': profile.risk_level.value,
            'triggered_rules': [rule.name for rule in triggered_rules],
            'recommendations': self._get_recommendations(profile, unique_actions)
        }
        
        # Update stats
        self.global_stats['total_requests'] += 1
        if not decision['allowed']:
            self.global_stats['blocked_requests'] += 1
        if triggered_rules:
            self.global_stats['policy_triggers'] += 1
        
        logger.debug(f"Policy assessment for {domain}: {decision}")
        return decision
    
    def report_detection(self, 
                        domain: str,
                        signal: DetectionSignal,
                        details: Optional[Dict[str, Any]] = None):
        """
        Report a bot detection signal.
        
        Args:
            domain: Domain where detection occurred
            signal: Type of detection signal
            details: Additional detection details
        """
        profile = self._get_domain_profile(domain)
        profile.add_detection_signal(signal)
        
        # Update domain characteristics based on signal
        if signal == DetectionSignal.CLOUDFLARE_CHALLENGE:
            profile.has_cloudflare = True
        elif signal == DetectionSignal.CAPTCHA:
            profile.captcha_probability = min(1.0, profile.captcha_probability + 0.1)
        elif signal == DetectionSignal.EMPTY_RESPONSE:
            profile.requires_js = True
        
        # Apply immediate blocking for critical signals
        if signal in [DetectionSignal.IP_BLOCK, DetectionSignal.CAPTCHA]:
            if profile.risk_level == RiskLevel.CRITICAL:
                profile.blocked_until = datetime.utcnow() + timedelta(hours=1)
        
        self.global_stats['detection_signals'] += 1
        
        logger.warning(f"Detection signal for {domain}: {signal.value}")
        
        if details:
            logger.debug(f"Detection details: {details}")
    
    def report_success(self, 
                      domain: str,
                      response_time: float,
                      content_length: int):
        """
        Report a successful request.
        
        Args:
            domain: Domain of successful request
            response_time: Response time in seconds
            content_length: Response content length
        """
        profile = self._get_domain_profile(domain)
        profile.request_count += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.1
        profile.success_rate = (1 - alpha) * profile.success_rate + alpha * 1.0
        
        # Update average response time
        profile.avg_response_time = (
            (profile.avg_response_time * (profile.request_count - 1) + response_time) / 
            profile.request_count
        )
        
        # Reduce risk level on consistent success
        if profile.request_count % 10 == 0 and profile.success_rate > 0.9:
            if profile.risk_level == RiskLevel.HIGH:
                profile.risk_level = RiskLevel.MEDIUM
            elif profile.risk_level == RiskLevel.MEDIUM:
                profile.risk_level = RiskLevel.LOW
    
    def report_failure(self, 
                      domain: str,
                      error_type: str,
                      status_code: Optional[int] = None):
        """
        Report a failed request.
        
        Args:
            domain: Domain of failed request
            error_type: Type of error
            status_code: HTTP status code if available
        """
        profile = self._get_domain_profile(domain)
        profile.request_count += 1
        
        # Update success rate
        alpha = 0.1
        profile.success_rate = (1 - alpha) * profile.success_rate + alpha * 0.0
        
        # Map error types to detection signals
        if status_code == 403:
            self.report_detection(domain, DetectionSignal.HTTP_403)
        elif status_code == 429:
            self.report_detection(domain, DetectionSignal.HTTP_429)
        elif error_type == 'timeout':
            # Don't treat timeouts as detection signals by default
            pass
        elif error_type == 'empty_response':
            self.report_detection(domain, DetectionSignal.EMPTY_RESPONSE)
    
    def _get_domain_profile(self, domain: str) -> DomainProfile:
        """Get or create domain profile"""
        if domain not in self.domain_profiles:
            self.domain_profiles[domain] = DomainProfile(domain=domain)
        return self.domain_profiles[domain]
    
    def _calculate_delay(self, 
                        profile: DomainProfile,
                        actions: List[PolicyAction],
                        context: Dict[str, Any]) -> float:
        """Calculate appropriate delay based on actions and risk"""
        base_delay = profile.preferred_delay
        
        # Apply action-based delay modifications
        if PolicyAction.INCREASE_DELAY in actions:
            base_delay *= 2.0
        
        if PolicyAction.DELAY in actions:
            base_delay = max(base_delay, self.base_delay * 2)
        
        # Apply risk-based delay modifications
        risk_multipliers = {
            RiskLevel.VERY_LOW: 0.5,
            RiskLevel.LOW: 1.0,
            RiskLevel.MEDIUM: 2.0,
            RiskLevel.HIGH: 4.0,
            RiskLevel.CRITICAL: 8.0
        }
        
        base_delay *= risk_multipliers.get(profile.risk_level, 1.0)
        
        # Add jitter
        jitter = random.uniform(0.8, 1.2)
        final_delay = base_delay * jitter
        
        # Enforce bounds
        return max(0.1, min(self.max_delay, final_delay))
    
    def _get_recommendations(self, 
                           profile: DomainProfile,
                           actions: List[PolicyAction]) -> List[str]:
        """Get recommendations based on profile and actions"""
        recommendations = []
        
        if PolicyAction.ROTATE_PROXY in actions:
            recommendations.append("Use different proxy")
        
        if PolicyAction.SWITCH_USER_AGENT in actions:
            recommendations.append("Switch user agent")
        
        if PolicyAction.FALLBACK_MODE in actions:
            recommendations.append("Switch to browser mode")
        
        if profile.has_cloudflare:
            recommendations.append("Use Cloudflare bypass techniques")
        
        if profile.requires_js:
            recommendations.append("Enable JavaScript execution")
        
        if profile.captcha_probability > 0.5:
            recommendations.append("Consider CAPTCHA solving service")
        
        return recommendations
    
    def add_rule(self, rule: PolicyRule):
        """Add a custom policy rule"""
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority)
        logger.info(f"Added policy rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a policy rule"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                logger.info(f"Removed policy rule: {rule_name}")
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """Enable a policy rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                logger.info(f"Enabled policy rule: {rule_name}")
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """Disable a policy rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                logger.info(f"Disabled policy rule: {rule_name}")
                return True
        return False
    
    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """Get statistics for a specific domain"""
        if domain not in self.domain_profiles:
            return {}
        
        profile = self.domain_profiles[domain]
        
        recent_signals = [
            signal.value for signal in profile.detection_signals[-5:]
        ]
        
        return {
            'domain': domain,
            'risk_level': profile.risk_level.value,
            'request_count': profile.request_count,
            'success_rate': profile.success_rate,
            'avg_response_time': profile.avg_response_time,
            'is_blocked': profile.is_blocked,
            'blocked_until': profile.blocked_until.isoformat() if profile.blocked_until else None,
            'has_cloudflare': profile.has_cloudflare,
            'requires_js': profile.requires_js,
            'captcha_probability': profile.captcha_probability,
            'recent_signals': recent_signals,
            'total_detections': len(profile.detection_signals),
            'last_detection': profile.last_detection.isoformat() if profile.last_detection else None
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global policy statistics"""
        active_rules = sum(1 for rule in self.rules if rule.enabled)
        triggered_rules = sum(1 for rule in self.rules if rule.hit_count > 0)
        
        risk_distribution = {}
        for level in RiskLevel:
            count = sum(1 for profile in self.domain_profiles.values() 
                       if profile.risk_level == level)
            risk_distribution[level.value] = count
        
        return {
            'total_requests': self.global_stats['total_requests'],
            'blocked_requests': self.global_stats['blocked_requests'],
            'detection_signals': self.global_stats['detection_signals'],
            'policy_triggers': self.global_stats['policy_triggers'],
            'total_domains': len(self.domain_profiles),
            'blocked_domains': sum(1 for profile in self.domain_profiles.values() if profile.is_blocked),
            'total_rules': len(self.rules),
            'active_rules': active_rules,
            'triggered_rules': triggered_rules,
            'risk_distribution': risk_distribution
        }
    
    def reset_domain(self, domain: str):
        """Reset policy state for a domain"""
        if domain in self.domain_profiles:
            # Keep learned characteristics but reset risk state
            profile = self.domain_profiles[domain]
            profile.risk_level = RiskLevel.LOW
            profile.detection_signals = []
            profile.blocked_until = None
            profile.last_detection = None
            logger.info(f"Reset policy state for domain: {domain}")
    
    def unblock_domain(self, domain: str):
        """Manually unblock a domain"""
        if domain in self.domain_profiles:
            profile = self.domain_profiles[domain]
            profile.blocked_until = None
            profile.risk_level = RiskLevel.LOW
            logger.info(f"Manually unblocked domain: {domain}")