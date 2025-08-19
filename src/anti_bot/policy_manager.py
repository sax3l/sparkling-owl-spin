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