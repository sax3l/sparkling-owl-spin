"""
Async Proxy Storage Layer
========================

Modernized async version of jhao104/proxy_pool storage system.
Baserat på analys av RedisClient och SsdbClient klasser.

Key improvements:
- Async Redis support
- Memory fallback
- Better error handling
- Serialization support
"""

import asyncio
import json
import pickle
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import asdict

try:
    import aioredis
except ImportError:
    aioredis = None

from utils.logger import get_logger
from .enhanced_manager import ProxyInfo, ProxyStatus

logger = get_logger(__name__)


class AsyncProxyStorage:
    """
    Async proxy storage system.
    
    Inspired by RedisClient from jhao104/proxy_pool but async:
    - Redis primary storage
    - Memory fallback
    - Serialization handling
    """
    
    def __init__(self, redis_url: Optional[str] = None, key_prefix: str = "proxy_pool"):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Memory storage as fallback
        self._memory_storage: Dict[str, str] = {}
        self._memory_sets: Dict[str, Set[str]] = {}
        
        self.use_redis = aioredis is not None and redis_url is not None
        
    async def initialize(self):
        """Initialize storage connections."""
        if self.use_redis:
            try:
                self.redis_client = aioredis.from_url(self.redis_url, decode_responses=True)
                await self.redis_client.ping()
                logger.info("✅ Connected to Redis for proxy storage")
            except Exception as e:
                logger.warning(f"❌ Redis connection failed: {e}, using memory storage")
                self.redis_client = None
                self.use_redis = False
        else:
            logger.info("📝 Using memory storage for proxies")
            
    async def close(self):
        """Close storage connections."""
        if self.redis_client:
            await self.redis_client.close()
            
    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store value by key.
        Equivalent to RedisClient.put() from original.
        """
        try:
            serialized_value = self._serialize(value)
            
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                if ttl:
                    await self.redis_client.setex(redis_key, ttl, serialized_value)
                else:
                    await self.redis_client.set(redis_key, serialized_value)
            else:
                # Memory storage
                self._memory_storage[key] = serialized_value
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to put {key}: {e}")
            return False
            
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.
        Equivalent to RedisClient.get() from original.
        """
        try:
            serialized_value = None
            
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                serialized_value = await self.redis_client.get(redis_key)
            else:
                # Memory storage
                serialized_value = self._memory_storage.get(key)
                
            if serialized_value:
                return self._deserialize(serialized_value)
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get {key}: {e}")
            return None
            
    async def delete(self, key: str) -> bool:
        """
        Delete value by key.
        Equivalent to RedisClient.delete() from original.
        """
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                result = await self.redis_client.delete(redis_key)
                return result > 0
            else:
                # Memory storage
                if key in self._memory_storage:
                    del self._memory_storage[key]
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete {key}: {e}")
            return False
            
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:{key}"
                return await self.redis_client.exists(redis_key) > 0
            else:
                return key in self._memory_storage
                
        except Exception as e:
            logger.error(f"❌ Failed to check existence of {key}: {e}")
            return False
            
    async def get_all_keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern."""
        try:
            if self.use_redis and self.redis_client:
                redis_pattern = f"{self.key_prefix}:{pattern}"
                keys = await self.redis_client.keys(redis_pattern)
                # Remove prefix
                return [key.replace(f"{self.key_prefix}:", "") for key in keys]
            else:
                # Memory storage - simple pattern matching
                import fnmatch
                return [key for key in self._memory_storage.keys() if fnmatch.fnmatch(key, pattern)]
                
        except Exception as e:
            logger.error(f"❌ Failed to get keys with pattern {pattern}: {e}")
            return []
            
    async def set_add(self, set_name: str, value: str) -> bool:
        """Add value to set."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:set:{set_name}"
                result = await self.redis_client.sadd(redis_key, value)
                return result > 0
            else:
                # Memory storage
                if set_name not in self._memory_sets:
                    self._memory_sets[set_name] = set()
                self._memory_sets[set_name].add(value)
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to add to set {set_name}: {e}")
            return False
            
    async def set_remove(self, set_name: str, value: str) -> bool:
        """Remove value from set."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:set:{set_name}"
                result = await self.redis_client.srem(redis_key, value)
                return result > 0
            else:
                # Memory storage
                if set_name in self._memory_sets:
                    self._memory_sets[set_name].discard(value)
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to remove from set {set_name}: {e}")
            return False
            
    async def set_members(self, set_name: str) -> Set[str]:
        """Get all members of set."""
        try:
            if self.use_redis and self.redis_client:
                redis_key = f"{self.key_prefix}:set:{set_name}"
                members = await self.redis_client.smembers(redis_key)
                return set(members)
            else:
                # Memory storage
                return self._memory_sets.get(set_name, set()).copy()
                
        except Exception as e:
            logger.error(f"❌ Failed to get set members {set_name}: {e}")
            return set()
            
    async def cleanup_expired(self, max_age_hours: int = 24):
        """Clean up expired entries (memory storage only)."""
        if not self.use_redis:
            # For memory storage, we'd need to track timestamps
            # This is a simplified version
            pass
            
    def _serialize(self, value: Any) -> str:
        """Serialize value for storage."""
        if isinstance(value, str):
            return value
        elif isinstance(value, ProxyInfo):
            return json.dumps(asdict(value), default=str)
        elif isinstance(value, dict):
            return json.dumps(value, default=str)
        else:
            # Fallback to pickle for complex objects
            import base64
            pickled = pickle.dumps(value)
            return base64.b64encode(pickled).decode('utf-8')
            
    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage."""
        try:
            # Try JSON first
            data = json.loads(value)
            
            # Check if it's a ProxyInfo dict
            if isinstance(data, dict) and 'host' in data and 'port' in data:
                # Reconstruct ProxyInfo
                return ProxyInfo(
                    host=data['host'],
                    port=data['port'],
                    protocol=data.get('protocol', 'http'),
                    username=data.get('username'),
                    password=data.get('password'),
                    status=ProxyStatus(data.get('status', 'unknown')),
                    last_checked=datetime.fromisoformat(data['last_checked']) if data.get('last_checked') else None,
                    success_rate=data.get('success_rate', 0.0),
                    response_time=data.get('response_time', 0.0),
                    source=data.get('source', 'unknown'),
                    country=data.get('country'),
                    anonymity=data.get('anonymity')
                )
            
            return data
            
        except json.JSONDecodeError:
            try:
                # Try pickle fallback
                import base64
                pickled = base64.b64decode(value.encode('utf-8'))
                return pickle.loads(pickled)
            except Exception:
                # Return as string if all else fails
                return value


class ProxyStorageManager:
    """
    High-level proxy storage manager.
    Combines storage operations with proxy-specific logic.
    """
    
    def __init__(self, storage: AsyncProxyStorage):
        self.storage = storage
        
    async def store_proxy(self, proxy: ProxyInfo, ttl: Optional[int] = None) -> bool:
        """Store a proxy with metadata."""
        try:
            # Store main proxy data
            await self.storage.put(proxy.key, proxy, ttl)
            
            # Add to status sets
            status_set = f"status:{proxy.status.value}"
            await self.storage.set_add(status_set, proxy.key)
            
            # Add to protocol set
            protocol_set = f"protocol:{proxy.protocol}"
            await self.storage.set_add(protocol_set, proxy.key)
            
            # Add to country set if available
            if proxy.country:
                country_set = f"country:{proxy.country}"
                await self.storage.set_add(country_set, proxy.key)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store proxy {proxy.key}: {e}")
            return False
            
    async def get_proxy(self, proxy_key: str) -> Optional[ProxyInfo]:
        """Get a proxy by key."""
        return await self.storage.get(proxy_key)
        
    async def remove_proxy(self, proxy: ProxyInfo) -> bool:
        """Remove a proxy and clean up metadata."""
        try:
            # Remove main data
            await self.storage.delete(proxy.key)
            
            # Remove from all sets
            for status in ProxyStatus:
                await self.storage.set_remove(f"status:{status.value}", proxy.key)
                
            await self.storage.set_remove(f"protocol:{proxy.protocol}", proxy.key)
            
            if proxy.country:
                await self.storage.set_remove(f"country:{proxy.country}", proxy.key)
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove proxy {proxy.key}: {e}")
            return False
            
    async def get_proxies_by_status(self, status: ProxyStatus) -> List[ProxyInfo]:
        """Get all proxies with specific status."""
        try:
            proxy_keys = await self.storage.set_members(f"status:{status.value}")
            proxies = []
            
            for key in proxy_keys:
                proxy = await self.storage.get(key)
                if proxy:
                    proxies.append(proxy)
                    
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxies by status {status}: {e}")
            return []
            
    async def get_proxies_by_protocol(self, protocol: str) -> List[ProxyInfo]:
        """Get all proxies with specific protocol."""
        try:
            proxy_keys = await self.storage.set_members(f"protocol:{protocol}")
            proxies = []
            
            for key in proxy_keys:
                proxy = await self.storage.get(key)
                if proxy:
                    proxies.append(proxy)
                    
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Failed to get proxies by protocol {protocol}: {e}")
            return []
            
    async def get_all_proxies(self) -> List[ProxyInfo]:
        """Get all stored proxies."""
        try:
            proxy_keys = await self.storage.get_all_keys()
            proxies = []
            
            for key in proxy_keys:
                if not key.startswith(('status:', 'protocol:', 'country:')):
                    proxy = await self.storage.get(key)
                    if proxy and isinstance(proxy, ProxyInfo):
                        proxies.append(proxy)
                        
            return proxies
            
        except Exception as e:
            logger.error(f"❌ Failed to get all proxies: {e}")
            return []


# Factory functions
async def create_proxy_storage(redis_url: Optional[str] = None) -> AsyncProxyStorage:
    """Create and initialize proxy storage."""
    storage = AsyncProxyStorage(redis_url=redis_url)
    await storage.initialize()
    return storage


async def create_storage_manager(redis_url: Optional[str] = None) -> ProxyStorageManager:
    """Create and initialize storage manager."""
    storage = await create_proxy_storage(redis_url)
    return ProxyStorageManager(storage)


# Usage example
async def example_usage():
    """Example of using the storage system."""
    
    # Create storage
    storage_manager = await create_storage_manager()
    
    # Create test proxy
    proxy = ProxyInfo(
        host="127.0.0.1",
        port=8080,
        protocol="http",
        status=ProxyStatus.ACTIVE,
        source="manual"
    )
    
    # Store proxy
    await storage_manager.store_proxy(proxy)
    
    # Retrieve proxy
    retrieved = await storage_manager.get_proxy(proxy.key)
    print(f"✅ Retrieved proxy: {retrieved.key if retrieved else 'None'}")
    
    # Get all active proxies
    active_proxies = await storage_manager.get_proxies_by_status(ProxyStatus.ACTIVE)
    print(f"📊 Active proxies: {len(active_proxies)}")


if __name__ == "__main__":
    asyncio.run(example_usage())
