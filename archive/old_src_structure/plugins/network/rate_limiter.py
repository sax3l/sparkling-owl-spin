#!/usr/bin/env python3
"""
Rate Limiter Adapter för Sparkling-Owl-Spin
Integration av Node Rate Limiter Flexible för Python
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    EXPONENTIAL_BACKOFF = "exponential_backoff"

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    key_generator: str = "ip"  # ip, user_id, api_key, custom
    points: int = 10  # Number of points
    duration: int = 60  # Duration in seconds
    block_duration: int = 60  # Block duration in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    max_hits: Optional[int] = None
    white_list: List[str] = None
    black_list: List[str] = None
    
@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    key: str
    hits: int
    remaining: int
    reset_time: datetime
    retry_after: Optional[int] = None
    blocked: bool = False

@dataclass
class RateLimitStats:
    """Rate limit statistics"""
    key: str
    total_requests: int
    blocked_requests: int
    first_request: datetime
    last_request: datetime
    current_hits: int
    remaining_points: int
    reset_time: datetime

class RateLimiterAdapter:
    """Rate Limiter integration för request throttling"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        self.limiters = {}  # Different limiters for different endpoints/keys
        self.stats = {}
        self.redis_available = False
        self.memory_store = {}
        
    async def initialize(self):
        """Initiera Rate Limiter adapter"""
        try:
            logger.info("⏱️ Initializing Rate Limiter Adapter")
            
            # Check for Redis availability
            await self._check_redis_availability()
            
            # Setup default limiters
            await self._setup_default_limiters()
            
            self.initialized = True
            logger.info("✅ Rate Limiter Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Rate Limiter: {str(e)}")
            raise
            
    async def _check_redis_availability(self):
        """Check if Redis is available för distributed rate limiting"""
        try:
            # import redis.asyncio as redis  # Uncomment when available
            logger.info("🔴 Redis availability check (mock - not connected)")
            self.redis_available = False
        except ImportError:
            logger.info("⚠️ Redis not available - using in-memory store")
            self.redis_available = False
            
    async def _setup_default_limiters(self):
        """Setup default rate limiters"""
        
        # Global API limiter
        self.limiters["global_api"] = RateLimitConfig(
            key_generator="ip",
            points=100,
            duration=3600,  # 1 hour
            block_duration=300,  # 5 minutes
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
        
        # Strict limiter för sensitive endpoints
        self.limiters["strict"] = RateLimitConfig(
            key_generator="ip", 
            points=10,
            duration=60,  # 1 minute
            block_duration=600,  # 10 minutes
            strategy=RateLimitStrategy.FIXED_WINDOW
        )
        
        # Generous limiter för public endpoints
        self.limiters["generous"] = RateLimitConfig(
            key_generator="ip",
            points=1000,
            duration=3600,  # 1 hour
            block_duration=60,  # 1 minute
            strategy=RateLimitStrategy.TOKEN_BUCKET
        )
        
        # Per-user limiter
        self.limiters["per_user"] = RateLimitConfig(
            key_generator="user_id",
            points=500,
            duration=3600,  # 1 hour
            block_duration=300,  # 5 minutes
            strategy=RateLimitStrategy.SLIDING_WINDOW
        )
        
        logger.info(f"⚙️ Setup {len(self.limiters)} default rate limiters")
        
    async def create_limiter(self, name: str, config: RateLimitConfig):
        """Create new rate limiter"""
        self.limiters[name] = config
        logger.info(f"➕ Created rate limiter: {name}")
        
    async def check_limit(self, limiter_name: str, key: str, 
                         context: Dict[str, Any] = None) -> RateLimitResult:
        """Check if request should be rate limited"""
        
        if not self.initialized:
            await self.initialize()
            
        if limiter_name not in self.limiters:
            logger.warning(f"⚠️ Unknown limiter: {limiter_name}")
            return RateLimitResult(
                allowed=True,
                key=key,
                hits=0,
                remaining=999,
                reset_time=datetime.now() + timedelta(hours=1)
            )
            
        config = self.limiters[limiter_name]
        
        # Generate final key
        final_key = await self._generate_key(config.key_generator, key, context)
        
        # Check white/black lists
        if await self._is_blacklisted(final_key, config):
            return RateLimitResult(
                allowed=False,
                key=final_key,
                hits=config.points,
                remaining=0,
                reset_time=datetime.now() + timedelta(seconds=config.block_duration),
                blocked=True
            )
            
        if await self._is_whitelisted(final_key, config):
            return RateLimitResult(
                allowed=True,
                key=final_key,
                hits=0,
                remaining=config.points,
                reset_time=datetime.now() + timedelta(seconds=config.duration)
            )
            
        # Apply rate limiting strategy
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(final_key, config)
        elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(final_key, config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(final_key, config)
        elif config.strategy == RateLimitStrategy.LEAKY_BUCKET:
            return await self._check_leaky_bucket(final_key, config)
        elif config.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF:
            return await self._check_exponential_backoff(final_key, config)
        else:
            return await self._check_sliding_window(final_key, config)
            
    async def _generate_key(self, key_generator: str, key: str, 
                          context: Dict[str, Any] = None) -> str:
        """Generate final rate limiting key"""
        if context is None:
            context = {}
            
        if key_generator == "ip":
            return f"rl:ip:{key}"
        elif key_generator == "user_id":
            user_id = context.get("user_id", key)
            return f"rl:user:{user_id}"
        elif key_generator == "api_key":
            api_key = context.get("api_key", key)
            # Hash API key för privacy
            hashed = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"rl:api:{hashed}"
        elif key_generator == "custom":
            custom_key = context.get("custom_key", key)
            return f"rl:custom:{custom_key}"
        else:
            return f"rl:generic:{key}"
            
    async def _is_whitelisted(self, key: str, config: RateLimitConfig) -> bool:
        """Check if key is whitelisted"""
        if not config.white_list:
            return False
            
        # Extract IP or identifier från key
        identifier = key.split(":")[-1]
        return identifier in config.white_list
        
    async def _is_blacklisted(self, key: str, config: RateLimitConfig) -> bool:
        """Check if key is blacklisted"""
        if not config.black_list:
            return False
            
        # Extract IP or identifier från key
        identifier = key.split(":")[-1]
        return identifier in config.black_list
        
    async def _check_sliding_window(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Sliding window rate limiting"""
        now = time.time()
        window_start = now - config.duration
        
        # Get or create tracking data
        if key not in self.memory_store:
            self.memory_store[key] = []
            
        requests = self.memory_store[key]
        
        # Remove old requests outside the window
        requests[:] = [req_time for req_time in requests if req_time > window_start]
        
        # Check if limit exceeded
        if len(requests) >= config.points:
            oldest_request = min(requests)
            reset_time = datetime.fromtimestamp(oldest_request + config.duration)
            retry_after = int(reset_time.timestamp() - now)
            
            return RateLimitResult(
                allowed=False,
                key=key,
                hits=len(requests),
                remaining=0,
                reset_time=reset_time,
                retry_after=max(0, retry_after)
            )
            
        # Add current request
        requests.append(now)
        
        # Calculate next reset time
        if requests:
            oldest_request = min(requests)
            reset_time = datetime.fromtimestamp(oldest_request + config.duration)
        else:
            reset_time = datetime.fromtimestamp(now + config.duration)
            
        return RateLimitResult(
            allowed=True,
            key=key,
            hits=len(requests),
            remaining=config.points - len(requests),
            reset_time=reset_time
        )
        
    async def _check_fixed_window(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Fixed window rate limiting"""
        now = time.time()
        window_start = int(now // config.duration) * config.duration
        window_key = f"{key}:{window_start}"
        
        # Get current count för this window
        if window_key not in self.memory_store:
            self.memory_store[window_key] = {"count": 0, "start": window_start}
            
        window_data = self.memory_store[window_key]
        
        # Check if limit exceeded
        if window_data["count"] >= config.points:
            reset_time = datetime.fromtimestamp(window_start + config.duration)
            retry_after = int(reset_time.timestamp() - now)
            
            return RateLimitResult(
                allowed=False,
                key=key,
                hits=window_data["count"],
                remaining=0,
                reset_time=reset_time,
                retry_after=max(0, retry_after)
            )
            
        # Increment count
        window_data["count"] += 1
        
        reset_time = datetime.fromtimestamp(window_start + config.duration)
        
        return RateLimitResult(
            allowed=True,
            key=key,
            hits=window_data["count"],
            remaining=config.points - window_data["count"],
            reset_time=reset_time
        )
        
    async def _check_token_bucket(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Token bucket rate limiting"""
        now = time.time()
        
        # Initialize bucket
        if key not in self.memory_store:
            self.memory_store[key] = {
                "tokens": config.points,
                "last_refill": now
            }
            
        bucket = self.memory_store[key]
        
        # Refill tokens
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * (config.points / config.duration)
        bucket["tokens"] = min(config.points, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now
        
        # Check if token available
        if bucket["tokens"] < 1:
            # Calculate retry after
            time_for_one_token = config.duration / config.points
            retry_after = int(time_for_one_token)
            
            return RateLimitResult(
                allowed=False,
                key=key,
                hits=config.points - int(bucket["tokens"]),
                remaining=int(bucket["tokens"]),
                reset_time=datetime.fromtimestamp(now + retry_after),
                retry_after=retry_after
            )
            
        # Consume token
        bucket["tokens"] -= 1
        
        return RateLimitResult(
            allowed=True,
            key=key,
            hits=config.points - int(bucket["tokens"]),
            remaining=int(bucket["tokens"]),
            reset_time=datetime.fromtimestamp(now + config.duration)
        )
        
    async def _check_leaky_bucket(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Leaky bucket rate limiting"""
        now = time.time()
        
        # Initialize bucket
        if key not in self.memory_store:
            self.memory_store[key] = {
                "level": 0,
                "last_leak": now
            }
            
        bucket = self.memory_store[key]
        
        # Leak tokens
        time_passed = now - bucket["last_leak"] 
        leak_rate = config.points / config.duration
        tokens_to_leak = time_passed * leak_rate
        bucket["level"] = max(0, bucket["level"] - tokens_to_leak)
        bucket["last_leak"] = now
        
        # Check if bucket would overflow
        if bucket["level"] >= config.points:
            # Calculate retry after
            time_to_leak_one = 1.0 / leak_rate
            retry_after = int(time_to_leak_one)
            
            return RateLimitResult(
                allowed=False,
                key=key,
                hits=int(bucket["level"]),
                remaining=config.points - int(bucket["level"]),
                reset_time=datetime.fromtimestamp(now + retry_after),
                retry_after=retry_after
            )
            
        # Add request to bucket
        bucket["level"] += 1
        
        return RateLimitResult(
            allowed=True,
            key=key,
            hits=int(bucket["level"]),
            remaining=config.points - int(bucket["level"]),
            reset_time=datetime.fromtimestamp(now + config.duration)
        )
        
    async def _check_exponential_backoff(self, key: str, config: RateLimitConfig) -> RateLimitResult:
        """Exponential backoff rate limiting"""
        now = time.time()
        
        # Initialize tracking
        if key not in self.memory_store:
            self.memory_store[key] = {
                "failures": 0,
                "last_failure": 0,
                "backoff_until": 0
            }
            
        data = self.memory_store[key]
        
        # Check if still in backoff period
        if now < data["backoff_until"]:
            retry_after = int(data["backoff_until"] - now)
            return RateLimitResult(
                allowed=False,
                key=key,
                hits=data["failures"],
                remaining=0,
                reset_time=datetime.fromtimestamp(data["backoff_until"]),
                retry_after=retry_after
            )
            
        # Reset if it's been long enough
        if now - data["last_failure"] > config.duration:
            data["failures"] = 0
            
        # Allow request but increment failure count
        data["failures"] += 1
        data["last_failure"] = now
        
        # Calculate next backoff period
        backoff_seconds = min(300, 2 ** (data["failures"] - 1))  # Cap at 5 minutes
        data["backoff_until"] = now + backoff_seconds
        
        return RateLimitResult(
            allowed=True,
            key=key,
            hits=data["failures"],
            remaining=max(0, config.points - data["failures"]),
            reset_time=datetime.fromtimestamp(data["backoff_until"])
        )
        
    async def get_stats(self, key: str) -> Optional[RateLimitStats]:
        """Get statistics för a key"""
        # This would be more comprehensive with Redis
        matching_keys = [k for k in self.memory_store.keys() if key in k]
        if not matching_keys:
            return None
            
        # Aggregate stats från all matching keys
        total_requests = sum(
            len(data) if isinstance(data, list) else data.get("count", 1) 
            for data in self.memory_store.values()
        )
        
        return RateLimitStats(
            key=key,
            total_requests=total_requests,
            blocked_requests=0,  # Would track this properly
            first_request=datetime.now() - timedelta(hours=1),  # Mock
            last_request=datetime.now(),
            current_hits=0,
            remaining_points=100,
            reset_time=datetime.now() + timedelta(minutes=5)
        )
        
    async def reset_limit(self, limiter_name: str, key: str):
        """Reset rate limit för specific key"""
        if limiter_name not in self.limiters:
            return
            
        config = self.limiters[limiter_name]
        final_key = await self._generate_key(config.key_generator, key)
        
        # Remove från memory store
        keys_to_remove = [k for k in self.memory_store.keys() if k.startswith(final_key)]
        for k in keys_to_remove:
            del self.memory_store[k]
            
        logger.info(f"🔄 Reset rate limit för key: {final_key}")
        
    async def add_to_whitelist(self, limiter_name: str, key: str):
        """Add key to whitelist"""
        if limiter_name in self.limiters:
            config = self.limiters[limiter_name]
            if config.white_list is None:
                config.white_list = []
            if key not in config.white_list:
                config.white_list.append(key)
                logger.info(f"✅ Added {key} to {limiter_name} whitelist")
                
    async def add_to_blacklist(self, limiter_name: str, key: str):
        """Add key to blacklist"""
        if limiter_name in self.limiters:
            config = self.limiters[limiter_name]
            if config.black_list is None:
                config.black_list = []
            if key not in config.black_list:
                config.black_list.append(key)
                logger.info(f"🚫 Added {key} to {limiter_name} blacklist")
                
    def get_limiters(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured limiters"""
        return {
            name: {
                "key_generator": config.key_generator,
                "points": config.points,
                "duration": config.duration,
                "block_duration": config.block_duration,
                "strategy": config.strategy.value,
                "whitelist_size": len(config.white_list) if config.white_list else 0,
                "blacklist_size": len(config.black_list) if config.black_list else 0
            }
            for name, config in self.limiters.items()
        }
        
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory store usage statistics"""
        return {
            "total_keys": len(self.memory_store),
            "memory_size_estimate": len(str(self.memory_store)),  # Rough estimate
            "redis_available": self.redis_available
        }
        
    async def cleanup_expired(self):
        """Cleanup expired entries från memory store"""
        now = time.time()
        keys_to_remove = []
        
        for key, data in self.memory_store.items():
            should_remove = False
            
            if isinstance(data, list):  # Sliding window data
                # Remove if all entries are old
                if all(req_time < now - 3600 for req_time in data):  # 1 hour old
                    should_remove = True
            elif isinstance(data, dict):
                # Remove if data is very old
                last_time = data.get("last_refill", data.get("last_leak", data.get("last_failure", 0)))
                if now - last_time > 3600:  # 1 hour old
                    should_remove = True
                    
            if should_remove:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.memory_store[key]
            
        if keys_to_remove:
            logger.info(f"🧹 Cleaned up {len(keys_to_remove)} expired rate limit entries")
            
    async def cleanup(self):
        """Cleanup Rate Limiter adapter"""
        logger.info("🧹 Cleaning up Rate Limiter Adapter")
        await self.cleanup_expired()
        self.memory_store.clear()
        self.limiters.clear()
        self.stats.clear()
        self.initialized = False
        logger.info("✅ Rate Limiter Adapter cleanup completed")
