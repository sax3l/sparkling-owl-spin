"""
Redis snapshot job for backing up cache data and proxy pool state.

Implements:
- Automated Redis backups
- Proxy pool state snapshots
- Cache validation and recovery
- Performance metrics tracking
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import redis.asyncio as redis
import boto3
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)

class RedisSnapshotJob:
    """Manages Redis data snapshots and backups."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", 
                 backup_location: str = "data/redis_backups"):
        self.redis_url = redis_url
        self.backup_location = Path(backup_location)
        self.backup_location.mkdir(parents=True, exist_ok=True)
        self._redis_client = None
    
    async def _get_redis_client(self) -> redis.Redis:
        """Get Redis client connection."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(self.redis_url)
        return self._redis_client
    
    async def run_snapshot(self) -> Dict[str, Any]:
        """Execute complete Redis snapshot."""
        logger.info("Starting Redis snapshot job")
        
        try:
            redis_client = await self._get_redis_client()
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            
            results = {
                "timestamp": timestamp,
                "proxy_pool": await self._backup_proxy_pool(redis_client, timestamp),
                "cache_data": await self._backup_cache_data(redis_client, timestamp),
                "session_data": await self._backup_session_data(redis_client, timestamp),
                "metrics": await self._backup_metrics(redis_client, timestamp)
            }
            
            # Create summary snapshot
            summary_file = self.backup_location / f"snapshot_summary_{timestamp}.json"
            with open(summary_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Redis snapshot completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Redis snapshot failed: {e}")
            raise
        finally:
            if self._redis_client:
                await self._redis_client.close()
    
    async def _backup_proxy_pool(self, redis_client: redis.Redis, timestamp: str) -> Dict[str, int]:
        """Backup proxy pool data."""
        logger.info("Backing up proxy pool data")
        
        # Get all proxy-related keys
        proxy_keys = []
        async for key in redis_client.scan_iter(match="proxy:*"):
            proxy_keys.append(key.decode())
        
        if not proxy_keys:
            logger.warning("No proxy data found in Redis")
            return {"count": 0}
        
        # Export proxy data
        proxy_data = {}
        for key in proxy_keys:
            data_type = await redis_client.type(key)
            
            if data_type == b'string':
                proxy_data[key] = await redis_client.get(key)
            elif data_type == b'hash':
                proxy_data[key] = await redis_client.hgetall(key)
            elif data_type == b'list':
                proxy_data[key] = await redis_client.lrange(key, 0, -1)
            elif data_type == b'set':
                proxy_data[key] = list(await redis_client.smembers(key))
            elif data_type == b'zset':
                proxy_data[key] = await redis_client.zrange(key, 0, -1, withscores=True)
        
        # Save to file
        backup_file = self.backup_location / f"proxy_pool_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(proxy_data, f, indent=2, default=str)
        
        logger.info(f"Backed up {len(proxy_keys)} proxy pool keys")
        return {"count": len(proxy_keys), "file": str(backup_file)}
    
    async def _backup_cache_data(self, redis_client: redis.Redis, timestamp: str) -> Dict[str, int]:
        """Backup general cache data."""
        logger.info("Backing up cache data")
        
        cache_keys = []
        async for key in redis_client.scan_iter(match="cache:*"):
            cache_keys.append(key.decode())
        
        if not cache_keys:
            return {"count": 0}
        
        cache_data = {}
        for key in cache_keys:
            try:
                ttl = await redis_client.ttl(key)
                value = await redis_client.get(key)
                cache_data[key] = {
                    "value": value.decode() if value else None,
                    "ttl": ttl
                }
            except Exception as e:
                logger.warning(f"Failed to backup cache key {key}: {e}")
        
        backup_file = self.backup_location / f"cache_data_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
        
        logger.info(f"Backed up {len(cache_keys)} cache keys")
        return {"count": len(cache_keys), "file": str(backup_file)}
    
    async def _backup_session_data(self, redis_client: redis.Redis, timestamp: str) -> Dict[str, int]:
        """Backup session data."""
        logger.info("Backing up session data")
        
        session_keys = []
        async for key in redis_client.scan_iter(match="session:*"):
            session_keys.append(key.decode())
        
        if not session_keys:
            return {"count": 0}
        
        session_data = {}
        for key in session_keys:
            try:
                session_data[key] = await redis_client.hgetall(key)
            except Exception as e:
                logger.warning(f"Failed to backup session key {key}: {e}")
        
        backup_file = self.backup_location / f"session_data_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        logger.info(f"Backed up {len(session_keys)} session keys")
        return {"count": len(session_keys), "file": str(backup_file)}
    
    async def _backup_metrics(self, redis_client: redis.Redis, timestamp: str) -> Dict[str, int]:
        """Backup metrics data."""
        logger.info("Backing up metrics data")
        
        metrics_keys = []
        async for key in redis_client.scan_iter(match="metrics:*"):
            metrics_keys.append(key.decode())
        
        if not metrics_keys:
            return {"count": 0}
        
        metrics_data = {}
        for key in metrics_keys:
            try:
                data_type = await redis_client.type(key)
                if data_type == b'zset':
                    metrics_data[key] = await redis_client.zrange(key, 0, -1, withscores=True)
                elif data_type == b'hash':
                    metrics_data[key] = await redis_client.hgetall(key)
                elif data_type == b'string':
                    metrics_data[key] = await redis_client.get(key)
            except Exception as e:
                logger.warning(f"Failed to backup metrics key {key}: {e}")
        
        backup_file = self.backup_location / f"metrics_data_{timestamp}.json"
        with open(backup_file, 'w') as f:
            json.dump(metrics_data, f, indent=2, default=str)
        
        logger.info(f"Backed up {len(metrics_keys)} metrics keys")
        return {"count": len(metrics_keys), "file": str(backup_file)}
    
    async def restore_from_snapshot(self, snapshot_timestamp: str) -> Dict[str, bool]:
        """Restore Redis data from snapshot."""
        logger.info(f"Restoring Redis data from snapshot: {snapshot_timestamp}")
        
        redis_client = await self._get_redis_client()
        results = {}
        
        try:
            # Restore proxy pool
            proxy_file = self.backup_location / f"proxy_pool_{snapshot_timestamp}.json"
            if proxy_file.exists():
                results["proxy_pool"] = await self._restore_data(redis_client, proxy_file)
            
            # Restore cache data
            cache_file = self.backup_location / f"cache_data_{snapshot_timestamp}.json"
            if cache_file.exists():
                results["cache_data"] = await self._restore_cache_data(redis_client, cache_file)
            
            # Restore session data
            session_file = self.backup_location / f"session_data_{snapshot_timestamp}.json"
            if session_file.exists():
                results["session_data"] = await self._restore_data(redis_client, session_file)
            
            # Restore metrics
            metrics_file = self.backup_location / f"metrics_data_{snapshot_timestamp}.json"
            if metrics_file.exists():
                results["metrics_data"] = await self._restore_data(redis_client, metrics_file)
            
            logger.info(f"Restore completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
        finally:
            await redis_client.close()
    
    async def _restore_data(self, redis_client: redis.Redis, backup_file: Path) -> bool:
        """Restore generic data from backup file."""
        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)
            
            for key, value in data.items():
                if isinstance(value, dict) and "value" in value:
                    # Cache data with TTL
                    ttl = value.get("ttl", -1)
                    if value["value"] and ttl > 0:
                        await redis_client.setex(key, ttl, value["value"])
                elif isinstance(value, dict):
                    # Hash data
                    await redis_client.hset(key, mapping=value)
                elif isinstance(value, list):
                    # List or set data
                    await redis_client.delete(key)
                    if value:
                        await redis_client.lpush(key, *value)
                else:
                    # String data
                    await redis_client.set(key, str(value))
            
            return True
        except Exception as e:
            logger.error(f"Failed to restore from {backup_file}: {e}")
            return False
    
    async def _restore_cache_data(self, redis_client: redis.Redis, backup_file: Path) -> bool:
        """Restore cache data with TTL information."""
        try:
            with open(backup_file, 'r') as f:
                data = json.load(f)
            
            for key, cache_item in data.items():
                if cache_item["value"] and cache_item["ttl"] > 0:
                    await redis_client.setex(key, cache_item["ttl"], cache_item["value"])
            
            return True
        except Exception as e:
            logger.error(f"Failed to restore cache data from {backup_file}: {e}")
            return False

async def run_redis_snapshot():
    """Entry point for Redis snapshot job execution."""
    job = RedisSnapshotJob()
    return await job.run_snapshot()