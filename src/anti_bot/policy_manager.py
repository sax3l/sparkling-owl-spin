import redis
import time
from pydantic import BaseModel
from urllib.parse import urlparse

class DomainPolicy(BaseModel):
    transport: str = "http"  # 'http' or 'browser'
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
        self.redis.set(f"policy:{domain}", policy.model_dump_json(), ex=86400) # 24h expiry

    def update_on_failure(self, domain: str, status_code: int):
        """Increases delay and applies backoff if a blocking status code is received."""
        policy = self.get_policy(domain)
        if status_code in [429, 403, 503]:
            # Exponential backoff
            new_delay = min(policy.current_delay_seconds * 2, 60) 
            policy.current_delay_seconds = new_delay
            policy.backoff_until = time.time() + new_delay * 5 # Pause for 5x the delay
            
            # Switch to browser mode on repeated failures as a fallback
            policy.transport = "browser"
            
        self.update_policy(domain, policy)

    def update_on_success(self, domain: str):
        """Gradually reduces delay back to normal on successful requests."""
        policy = self.get_policy(domain)
        # Slowly decrease delay if things are going well
        policy.current_delay_seconds = max(policy.current_delay_seconds * 0.95, 2.0)
        self.update_policy(domain, policy)