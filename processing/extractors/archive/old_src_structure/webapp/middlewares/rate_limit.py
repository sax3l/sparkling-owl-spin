"""
Rate limiting middleware for the FastAPI application.
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import asyncio
from datetime import datetime, timedelta

class RateLimitMiddleware:
    """Rate limiting middleware using Redis for storage."""
    
    def __init__(
        self,
        redis_client: redis.Redis,
        default_requests: int = 100,
        default_window: int = 3600,  # 1 hour
        key_func=None
    ):
        self.redis = redis_client
        self.default_requests = default_requests
        self.default_window = default_window
        self.key_func = key_func or self._default_key_func
    
    def _default_key_func(self, request: Request) -> str:
        """Default function to generate rate limit key."""
        # Use client IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        
        if forwarded_for:
            # Use the first IP in the X-Forwarded-For header
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"rate_limit:{client_ip}"
    
    async def __call__(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Generate rate limit key
        key = self.key_func(request)
        
        # Check rate limit
        try:
            current_requests = await self._check_rate_limit(
                key, 
                self.default_requests, 
                self.default_window
            )
            
            if current_requests > self.default_requests:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {self.default_requests} requests per hour allowed",
                        "retry_after": self.default_window
                    },
                    headers={
                        "Retry-After": str(self.default_window),
                        "X-RateLimit-Limit": str(self.default_requests),
                        "X-RateLimit-Remaining": str(max(0, self.default_requests - current_requests)),
                        "X-RateLimit-Reset": str(int(time.time()) + self.default_window)
                    }
                )
            
            # Process the request
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit"] = str(self.default_requests)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.default_requests - current_requests))
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.default_window)
            
            return response
            
        except Exception as e:
            # If Redis is down, log error and continue without rate limiting
            print(f"Rate limiting error: {e}")
            return await call_next(request)
    
    async def _check_rate_limit(self, key: str, limit: int, window: int) -> int:
        """Check and update rate limit using sliding window."""
        now = int(time.time())
        pipeline = self.redis.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_count = results[1]  # Result from zcard
        
        return current_count + 1  # +1 for the current request

class EndpointRateLimiter:
    """Per-endpoint rate limiter with different limits."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.endpoint_limits = {
            # API endpoints with stricter limits
            "/api/v1/crawl": {"requests": 10, "window": 3600},  # 10 per hour
            "/api/v1/export": {"requests": 5, "window": 3600},   # 5 per hour
            "/api/v1/jobs": {"requests": 50, "window": 3600},    # 50 per hour
            
            # Auth endpoints
            "/auth/login": {"requests": 10, "window": 900},      # 10 per 15 minutes
            "/auth/register": {"requests": 3, "window": 3600},   # 3 per hour
            "/auth/reset-password": {"requests": 5, "window": 3600},  # 5 per hour
            
            # Default for other endpoints
            "default": {"requests": 100, "window": 3600}        # 100 per hour
        }
    
    def get_limit_for_endpoint(self, path: str) -> Dict[str, int]:
        """Get rate limit configuration for endpoint."""
        # Check for exact match
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]
        
        # Check for pattern match
        for pattern, limits in self.endpoint_limits.items():
            if pattern != "default" and path.startswith(pattern):
                return limits
        
        # Return default
        return self.endpoint_limits["default"]
    
    async def check_rate_limit(
        self, 
        request: Request, 
        user_id: Optional[str] = None
    ) -> bool:
        """Check if request is within rate limits."""
        path = request.url.path
        limits = self.get_limit_for_endpoint(path)
        
        # Generate key based on user ID or IP
        if user_id:
            key = f"rate_limit:user:{user_id}:{path}"
        else:
            client_ip = request.client.host
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                client_ip = forwarded_for.split(",")[0].strip()
            key = f"rate_limit:ip:{client_ip}:{path}"
        
        # Check rate limit
        current_requests = await self._sliding_window_check(
            key, 
            limits["requests"], 
            limits["window"]
        )
        
        return current_requests <= limits["requests"]
    
    async def _sliding_window_check(self, key: str, limit: int, window: int) -> int:
        """Sliding window rate limit check."""
        now = int(time.time())
        
        # Use Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        -- Remove expired entries
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
        
        -- Get current count
        local current = redis.call('ZCARD', key)
        
        if current < limit then
            -- Add current request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window)
            return current + 1
        else
            return current
        end
        """
        
        result = await self.redis.eval(
            lua_script, 
            1, 
            key, 
            window, 
            limit, 
            now
        )
        
        return result

class UserBasedRateLimiter:
    """User-based rate limiter with tier support."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.tier_limits = {
            "free": {"requests": 100, "window": 3600},
            "basic": {"requests": 1000, "window": 3600},
            "premium": {"requests": 10000, "window": 3600},
            "enterprise": {"requests": 100000, "window": 3600}
        }
    
    async def check_user_rate_limit(
        self, 
        user_id: str, 
        user_tier: str = "free",
        endpoint: str = "default"
    ) -> Dict[str, any]:
        """Check user rate limit based on their tier."""
        limits = self.tier_limits.get(user_tier, self.tier_limits["free"])
        key = f"rate_limit:user:{user_id}:{endpoint}"
        
        current_requests = await self._sliding_window_check(
            key, 
            limits["requests"], 
            limits["window"]
        )
        
        return {
            "allowed": current_requests <= limits["requests"],
            "current": current_requests,
            "limit": limits["requests"],
            "window": limits["window"],
            "remaining": max(0, limits["requests"] - current_requests),
            "reset_at": int(time.time()) + limits["window"]
        }
    
    async def _sliding_window_check(self, key: str, limit: int, window: int) -> int:
        """Sliding window rate limit check."""
        now = int(time.time())
        pipeline = self.redis.pipeline()
        
        # Remove expired entries
        pipeline.zremrangebyscore(key, 0, now - window)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request if under limit
        current_count = await pipeline.execute()
        current_count = current_count[1]  # Result from zcard
        
        if current_count < limit:
            # Add current request
            pipeline.zadd(key, {str(now): now})
            pipeline.expire(key, window)
            await pipeline.execute()
            return current_count + 1
        
        return current_count

def create_rate_limit_middleware(redis_client: redis.Redis) -> RateLimitMiddleware:
    """Create rate limiting middleware."""
    return RateLimitMiddleware(redis_client)

def rate_limit_dependency(
    requests_per_hour: int = 100,
    requests_per_minute: int = 60
):
    """Dependency for rate limiting specific endpoints."""
    async def dependency(request: Request):
        # This would be used with Depends() in FastAPI endpoints
        # Implementation would check rate limits here
        pass
    
    return dependency
