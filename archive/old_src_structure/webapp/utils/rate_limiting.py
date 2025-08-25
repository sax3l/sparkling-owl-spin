"""
Rate limiting utilities for FastAPI endpoints.
"""

import asyncio
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware


class InMemoryRateLimiter:
    """Simple in-memory rate limiter using sliding window."""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            key: Unique identifier for rate limiting
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            bool: True if request is allowed, False otherwise
        """
        async with self.lock:
            now = time.time()
            cutoff = now - window
            
            # Remove old requests outside the window
            while self.requests[key] and self.requests[key][0] <= cutoff:
                self.requests[key].popleft()
            
            # Check if we're under the limit
            if len(self.requests[key]) < limit:
                self.requests[key].append(now)
                return True
            
            return False
    
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            key: Unique identifier for rate limiting
            limit: Maximum number of requests allowed
            window: Time window in seconds
            
        Returns:
            int: Number of remaining requests
        """
        async with self.lock:
            now = time.time()
            cutoff = now - window
            
            # Remove old requests outside the window
            while self.requests[key] and self.requests[key][0] <= cutoff:
                self.requests[key].popleft()
            
            return max(0, limit - len(self.requests[key]))
    
    async def get_reset_time(self, key: str, window: int) -> Optional[float]:
        """
        Get time when rate limit resets.
        
        Args:
            key: Unique identifier for rate limiting
            window: Time window in seconds
            
        Returns:
            float: Timestamp when rate limit resets, or None if no requests
        """
        if not self.requests[key]:
            return None
        
        oldest_request = self.requests[key][0]
        return oldest_request + window


# Global rate limiter instance
rate_limiter = InMemoryRateLimiter()


def rate_limit(requests: int, window: int = 60, key_func: Optional[Callable] = None):
    """
    Decorator for rate limiting FastAPI endpoints.
    
    Args:
        requests: Maximum number of requests allowed
        window: Time window in seconds
        key_func: Function to generate rate limit key (optional)
        
    Returns:
        Decorated function with rate limiting
        
    Usage:
        @app.get("/api/data")
        @rate_limit(requests=100, window=3600)  # 100 requests per hour
        async def get_data():
            return {"data": "value"}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and user from function arguments
            request = None
            current_user = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                elif key == "current_user" and hasattr(value, "id"):
                    current_user = value
            
            # Generate rate limit key
            if key_func:
                rate_key = key_func(request, current_user)
            elif current_user:
                rate_key = f"user:{current_user.id}"
            elif request:
                rate_key = f"ip:{request.client.host}"
            else:
                rate_key = "global"
            
            # Check rate limit
            allowed = await rate_limiter.is_allowed(rate_key, requests, window)
            
            if not allowed:
                remaining = await rate_limiter.get_remaining(rate_key, requests, window)
                reset_time = await rate_limiter.get_reset_time(rate_key, window)
                
                headers = {
                    "X-RateLimit-Limit": str(requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Window": str(window)
                }
                
                if reset_time:
                    retry_after = int(reset_time - time.time())
                    headers["Retry-After"] = str(max(1, retry_after))
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {requests} requests per {window} seconds",
                    headers=headers
                )
            
            # Add rate limit headers to response
            if request:
                remaining = await rate_limiter.get_remaining(rate_key, requests, window)
                # Store headers in request state to be added by middleware
                if not hasattr(request.state, "rate_limit_headers"):
                    request.state.rate_limit_headers = {}
                
                request.state.rate_limit_headers.update({
                    "X-RateLimit-Limit": str(requests),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Window": str(window)
                })
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add rate limit headers if they were set by rate_limit decorator
        if hasattr(request.state, "rate_limit_headers"):
            for key, value in request.state.rate_limit_headers.items():
                response.headers[key] = value
        
        return response


def user_rate_limit(requests: int, window: int = 60):
    """
    Rate limit decorator specific to authenticated users.
    
    Args:
        requests: Maximum number of requests allowed
        window: Time window in seconds
        
    Returns:
        Decorated function with user-based rate limiting
    """
    def key_func(request: Request, current_user) -> str:
        if current_user:
            return f"user:{current_user.id}"
        return f"ip:{request.client.host}"
    
    return rate_limit(requests, window, key_func)


def ip_rate_limit(requests: int, window: int = 60):
    """
    Rate limit decorator based on IP address.
    
    Args:
        requests: Maximum number of requests allowed
        window: Time window in seconds
        
    Returns:
        Decorated function with IP-based rate limiting
    """
    def key_func(request: Request, current_user) -> str:
        return f"ip:{request.client.host}"
    
    return rate_limit(requests, window, key_func)


def endpoint_rate_limit(endpoint: str, requests: int, window: int = 60):
    """
    Rate limit decorator for specific endpoints.
    
    Args:
        endpoint: Endpoint identifier
        requests: Maximum number of requests allowed
        window: Time window in seconds
        
    Returns:
        Decorated function with endpoint-specific rate limiting
    """
    def key_func(request: Request, current_user) -> str:
        base_key = f"user:{current_user.id}" if current_user else f"ip:{request.client.host}"
        return f"{base_key}:endpoint:{endpoint}"
    
    return rate_limit(requests, window, key_func)


class APIKeyRateLimiter:
    """Rate limiter for API keys with different limits per key."""
    
    def __init__(self):
        self.limiter = InMemoryRateLimiter()
    
    async def check_api_key_limit(
        self,
        api_key_id: str,
        requests_per_minute: int,
        requests_per_hour: int,
        requests_per_day: int
    ) -> bool:
        """
        Check if API key is within all rate limits.
        
        Args:
            api_key_id: API key identifier
            requests_per_minute: Requests per minute limit
            requests_per_hour: Requests per hour limit
            requests_per_day: Requests per day limit
            
        Returns:
            bool: True if all limits are respected
        """
        key_base = f"api_key:{api_key_id}"
        
        # Check minute limit
        if not await self.limiter.is_allowed(f"{key_base}:minute", requests_per_minute, 60):
            return False
        
        # Check hour limit
        if not await self.limiter.is_allowed(f"{key_base}:hour", requests_per_hour, 3600):
            return False
        
        # Check day limit
        if not await self.limiter.is_allowed(f"{key_base}:day", requests_per_day, 86400):
            return False
        
        return True


def adaptive_rate_limit(base_requests: int, window: int = 60, load_factor: float = 1.0):
    """
    Adaptive rate limit that adjusts based on system load.
    
    Args:
        base_requests: Base number of requests allowed
        window: Time window in seconds
        load_factor: Load factor to adjust limits (1.0 = normal, >1.0 = higher load)
        
    Returns:
        Decorated function with adaptive rate limiting
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Adjust requests based on load factor
            adjusted_requests = max(1, int(base_requests / load_factor))
            
            # Apply rate limiting with adjusted limit
            rate_limit_decorator = rate_limit(adjusted_requests, window)
            decorated_func = rate_limit_decorator(func)
            
            return await decorated_func(*args, **kwargs)
        
        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for rate limiting."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func, *args, **kwargs):
        """
        Call function with circuit breaker protection.
        
        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            HTTPException: If circuit is open
        """
        now = time.time()
        
        if self.state == "open":
            if now - self.last_failure_time < self.timeout:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporarily unavailable"
                )
            else:
                self.state = "half-open"
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = now
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e


def get_rate_limit_status(key: str, limit: int, window: int) -> Dict[str, Any]:
    """
    Get current rate limit status for a key.
    
    Args:
        key: Rate limit key
        limit: Rate limit
        window: Time window
        
    Returns:
        Dict with rate limit status
    """
    return {
        "limit": limit,
        "window": window,
        "remaining": asyncio.run(rate_limiter.get_remaining(key, limit, window)),
        "reset_time": asyncio.run(rate_limiter.get_reset_time(key, window))
    }
