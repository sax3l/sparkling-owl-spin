import redis
import time
from pydantic import BaseModel
from typing import Literal

class DomainPolicy(BaseModel):
    transport: Literal["http", "browser"] = "http"
    proxy_type: Literal["datacenter", "residential"] = "datacenter"
    session_policy: Literal["rotating", "sticky"] = "rotating"
    header_family: Literal["chrome", "firefox"] = "chrome"
    
    current_delay_seconds: float = 2.0
    backoff_until: float = 0.0
    error_rate: float = 0.0

class PolicyManager:
    """
    Manages and adapts scraping policies per domain using Redis.
    This forms the core of the adaptive regulator.
    """
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def get_policy(self, domain: str) -> DomainPolicy:
        """Retrieves the current policy for a domain, or returns a default."""
        policy_data = self.redis.get(f"policy:{domain}")
        if policy_data:
            return DomainPolicy.model_validate_json(policy_data)
        return DomainPolicy()

    def update_policy(self, domain: str, policy: DomainPolicy):
        """Saves the updated policy to Redis."""
        self.redis.set(f"policy:{domain}", policy.model_dump_json(), ex=86400)

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