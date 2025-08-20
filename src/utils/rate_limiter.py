import time
import redis
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)

class TokenBucket:
    def __init__(self, redis_client: redis.Redis, capacity: int, fill_rate: float):
        self.redis = redis_client
        self.capacity = capacity
        self.fill_rate = fill_rate # tokens per second

    async def consume(self, key: str, tokens: int = 1) -> bool:
        """
        Attempts to consume tokens from the bucket.
        Returns True if successful, False otherwise.
        """
        now = time.time()
        
        # Lua script for atomic token bucket logic
        # KEYS[1]: bucket_key (e.g., "rate_limit:tenant_id:api_key_id")
        # ARGV[1]: capacity
        # ARGV[2]: fill_rate (tokens per second)
        # ARGV[3]: current_timestamp
        # ARGV[4]: tokens_to_consume
        
        # Returns:
        #   1 if allowed, 0 if denied
        #   remaining_tokens
        #   reset_time (timestamp when bucket will be full)
        
        script = """
        local bucket_key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local fill_rate = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local tokens_to_consume = tonumber(ARGV[4])

        local last_fill_time = tonumber(redis.call("HGET", bucket_key, "last_fill_time")) or 0
        local current_tokens = tonumber(redis.call("HGET", bucket_key, "tokens")) or capacity

        local delta_time = now - last_fill_time
        local filled_tokens = delta_time * fill_rate
        
        current_tokens = math.min(capacity, current_tokens + filled_tokens)
        last_fill_time = now

        local allowed = 0
        local remaining_tokens = current_tokens
        local reset_time = now + (capacity - current_tokens) / fill_rate

        if current_tokens >= tokens_to_consume then
            allowed = 1
            remaining_tokens = current_tokens - tokens_to_consume
            reset_time = now + (capacity - remaining_tokens) / fill_rate
        end

        redis.call("HSET", bucket_key, "tokens", remaining_tokens, "last_fill_time", last_fill_time)
        
        return {allowed, remaining_tokens, math.ceil(reset_time)}
        """
        
        result = await self.redis.eval(script, 1, key, self.capacity, self.fill_rate, now, tokens)
        
        allowed = bool(result[0])
        remaining = int(result[1])
        reset_at = int(result[2])

        return allowed, remaining, reset_at

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, redis_url: str):
        super().__init__(app)
        self.redis = redis.asyncio.from_url(redis_url, decode_responses=True)
        # Default rate limits (can be overridden per tenant/API key)
        self.default_burst = 100
        self.default_sustained_per_minute = 6000
        self.default_fill_rate = self.default_sustained_per_minute / 60.0 # tokens per second

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip rate limiting for /health and /metrics endpoints
        if request.url.path in ["/health", "/metrics", "/oauth/token"]:
            return await call_next(request)

        # Get tenant_id and API key ID from request context (set by auth middleware/dependency)
        # For simplicity, we'll assume tenant_id is available in request.state.tenant_id
        # and api_key_id in request.state.api_key_id after authentication.
        # If not present, it means the request is unauthenticated or from an internal service.
        tenant_id = getattr(request.state, "tenant_id", "anonymous")
        api_key_id = getattr(request.state, "api_key_id", "anonymous")

        # Use a combined key for rate limiting
        rate_limit_key = f"rate_limit:{tenant_id}:{api_key_id}"

        # In a real system, you'd fetch specific limits for the tenant/API key from DB/cache
        # For now, use defaults
        capacity = self.default_burst
        fill_rate = self.default_fill_rate

        bucket = TokenBucket(self.redis, capacity, fill_rate)
        allowed, remaining, reset_at = await bucket.consume(rate_limit_key)

        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(capacity)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_at) # Unix timestamp

        if not allowed:
            logger.warning(f"Rate limit exceeded for {rate_limit_key}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(reset_at - int(time.time()))}
            )
        
        return response