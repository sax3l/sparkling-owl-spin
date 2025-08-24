import redis
import time
from pydantic import BaseModel
from typing import Literal, Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json

from utils.logger import get_logger

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

class DomainPolicy(BaseModel):
    transport: Literal["http", "browser"] = "http"
    proxy_type: Literal["datacenter", "residential"] = "datacenter"
    session_policy: Literal["rotating", "sticky"] = "rotating"
    header_family: Literal["chrome", "firefox"] = "chrome"
    
    current_delay_seconds: float = 2.0
    backoff_until: float = 0.0
    error_rate: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    detection_signals: List[str] = []
    policy_actions: List[str] = []
    last_detection: Optional[datetime] = None
    total_requests: int = 0
    blocked_requests: int = 0

class PolicyManager:
    """
    Enhanced adaptive policy manager with risk assessment and detection learning.
    Manages and adapts scraping policies per domain using Redis.
    This forms the core of the adaptive regulator.
    """
    def __init__(self, redis_url: str, learning_enabled: bool = True):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.learning_enabled = learning_enabled
        self.global_stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'detection_signals': 0,
            'policy_triggers': 0
        }

    def get_policy(self, domain: str) -> DomainPolicy:
        """Retrieves the current policy for a domain, or returns a default."""
        policy_data = self.redis.get(f"policy:{domain}")
        if policy_data:
            return DomainPolicy.model_validate_json(policy_data)
        return DomainPolicy()

    def update_policy(self, domain: str, policy: DomainPolicy):
        """Saves the updated policy to Redis."""
        self.redis.set(f"policy:{domain}", policy.model_dump_json(), ex=86400)

    def assess_risk(self, domain: str, detection_signals: List[DetectionSignal] = None) -> RiskLevel:
        """Assess risk level based on domain history and current signals"""
        policy = self.get_policy(domain)
        
        # Base risk on error rate
        if policy.error_rate > 0.8:
            return RiskLevel.CRITICAL
        elif policy.error_rate > 0.6:
            return RiskLevel.HIGH
        elif policy.error_rate > 0.4:
            return RiskLevel.MEDIUM
        elif policy.error_rate > 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW

    def add_detection_signal(self, domain: str, signal: DetectionSignal):
        """Record a bot detection signal for learning"""
        policy = self.get_policy(domain)
        
        # Add signal to history
        signal_str = signal.value
        if signal_str not in policy.detection_signals:
            policy.detection_signals.append(signal_str)
            # Keep only last 10 signals
            policy.detection_signals = policy.detection_signals[-10:]
        
        policy.last_detection = datetime.now()
        
        # Update risk level
        policy.risk_level = self.assess_risk(domain, [signal])
        
        # Apply adaptive response
        self._apply_adaptive_response(domain, policy, signal)
        
        self.update_policy(domain, policy)
        
        if self.learning_enabled:
            self._learn_from_signal(domain, signal)

    def _apply_adaptive_response(self, domain: str, policy: DomainPolicy, signal: DetectionSignal):
        """Apply adaptive response based on detection signal"""
        responses = {
            DetectionSignal.CAPTCHA: [PolicyAction.FALLBACK_MODE, PolicyAction.INCREASE_DELAY],
            DetectionSignal.RATE_LIMIT: [PolicyAction.INCREASE_DELAY, PolicyAction.ROTATE_PROXY],
            DetectionSignal.IP_BLOCK: [PolicyAction.ROTATE_PROXY, PolicyAction.PAUSE_DOMAIN],
            DetectionSignal.HTTP_403: [PolicyAction.SWITCH_USER_AGENT, PolicyAction.DELAY],
            DetectionSignal.HTTP_429: [PolicyAction.INCREASE_DELAY],
            DetectionSignal.CLOUDFLARE_CHALLENGE: [PolicyAction.FALLBACK_MODE]
        }
        
        actions = responses.get(signal, [PolicyAction.DELAY])
        
        for action in actions:
            if action == PolicyAction.INCREASE_DELAY:
                policy.current_delay_seconds = min(policy.current_delay_seconds * 2, 60.0)
            elif action == PolicyAction.ROTATE_PROXY:
                policy.proxy_type = "residential" if policy.proxy_type == "datacenter" else "datacenter"
            elif action == PolicyAction.SWITCH_USER_AGENT:
                policy.header_family = "firefox" if policy.header_family == "chrome" else "chrome"
            elif action == PolicyAction.FALLBACK_MODE:
                policy.transport = "browser"
            elif action == PolicyAction.PAUSE_DOMAIN:
                policy.backoff_until = time.time() + 3600  # 1 hour pause
        
        # Record applied actions
        policy.policy_actions.extend([action.value for action in actions])
        policy.policy_actions = policy.policy_actions[-5:]  # Keep last 5 actions

    def _learn_from_signal(self, domain: str, signal: DetectionSignal):
        """Update global learning from detection signal"""
        stats_key = f"global_stats:detection:{signal.value}"
        self.redis.incr(stats_key)
        self.redis.expire(stats_key, 86400 * 7)  # Keep for 7 days

    def update_on_failure(self, domain: str, status_code: int):
        """
        Increases delay, applies backoff, and escalates transport if blocking is detected.
        """
        policy = self.get_policy(domain)
        if status_code in [403, 429, 503] or status_code == 999: # 999 is our custom CAPTCHA code
            # Exponential backoff for delay
            policy.current_delay_seconds = min(policy.current_delay_seconds * 2, 60)
            policy.backoff_until = time.time() + policy.current_delay_seconds * 5
            
            # Escalate policy: switch header family, then proxy type, then to browser
            if policy.header_family == "chrome":
                policy.header_family = "firefox"
            elif policy.proxy_type == "datacenter":
                policy.proxy_type = "residential"
            
            policy.transport = "browser"
            
        self.update_policy(domain, policy)

    def update_on_success(self, domain: str):
        """Gradually reduces delay back to normal on successful requests."""
        policy = self.get_policy(domain)
        policy.current_delay_seconds = max(policy.current_delay_seconds * 0.95, 2.0)
        self.update_policy(domain, policy)

    def get_recommended_config(self, domain: str) -> dict:
        """Get recommended configuration based on domain analysis."""
        policy = self.get_policy(domain)
        
        # Analyze domain characteristics
        domain_analysis = self._analyze_domain(domain)
        
        recommendations = {
            "transport": self._recommend_transport(domain_analysis),
            "proxy_type": self._recommend_proxy_type(domain_analysis),
            "rate_limit": self._recommend_rate_limit(domain_analysis),
            "headers": self._recommend_headers(domain_analysis),
            "session_policy": self._recommend_session_policy(domain_analysis),
            "confidence": domain_analysis.get("confidence", 0.5)
        }
        
        return recommendations
    
    def get_health_status(self) -> dict:
        """Get anti-bot system health status."""
        try:
            # Test Redis connection
            self.redis.ping()
            redis_status = "healthy"
        except Exception:
            redis_status = "unhealthy"
        
        # Get policy statistics
        policy_keys = self.redis.keys("policy:*")
        active_domains = len(policy_keys)
        
        # Calculate average error rates
        total_error_rate = 0.0
        for key in policy_keys:
            policy_data = self.redis.get(key)
            if policy_data:
                try:
                    policy = DomainPolicy.model_validate_json(policy_data)
                    total_error_rate += policy.error_rate
                except Exception:
                    continue
        
        avg_error_rate = total_error_rate / max(active_domains, 1)
        
        return {
            "redis_status": redis_status,
            "active_domains": active_domains,
            "average_error_rate": avg_error_rate,
            "health": "healthy" if redis_status == "healthy" and avg_error_rate < 0.1 else "warning"
        }
    
    def _analyze_domain(self, domain: str) -> dict:
        """Analyze domain characteristics for recommendations."""
        # Simple domain analysis - in production this would be more sophisticated
        domain_lower = domain.lower()
        
        analysis = {
            "confidence": 0.7,
            "complexity": "medium",
            "javascript_heavy": False,
            "rate_sensitive": False,
            "anti_bot_level": "medium"
        }
        
        # Detect common patterns
        if any(indicator in domain_lower for indicator in ["api", "rest", "json"]):
            analysis["javascript_heavy"] = False
            analysis["rate_sensitive"] = True
            analysis["complexity"] = "low"
        elif any(indicator in domain_lower for indicator in ["spa", "app", "react", "angular"]):
            analysis["javascript_heavy"] = True
            analysis["complexity"] = "high"
        elif any(indicator in domain_lower for indicator in ["cloudflare", "ddos", "protection"]):
            analysis["anti_bot_level"] = "high"
            analysis["rate_sensitive"] = True
        
        return analysis
    
    def _recommend_transport(self, analysis: dict) -> str:
        """Recommend transport method based on analysis."""
        if analysis.get("javascript_heavy", False):
            return "browser"
        return "http"
    
    def _recommend_proxy_type(self, analysis: dict) -> str:
        """Recommend proxy type based on analysis."""
        if analysis.get("anti_bot_level") == "high":
            return "residential"
        return "datacenter"
    
    def _recommend_rate_limit(self, analysis: dict) -> float:
        """Recommend rate limit based on analysis."""
        if analysis.get("rate_sensitive", False):
            return 5.0  # 5 second delay
        elif analysis.get("anti_bot_level") == "high":
            return 3.0  # 3 second delay
        return 1.5  # 1.5 second delay
    
    def _recommend_headers(self, analysis: dict) -> str:
        """Recommend header family based on analysis."""
        # Simple recommendation - could be more sophisticated
        return "chrome"
    
    def _recommend_session_policy(self, analysis: dict) -> str:
        """Recommend session policy based on analysis."""
        if analysis.get("anti_bot_level") == "high":
            return "sticky"
        return "rotating"