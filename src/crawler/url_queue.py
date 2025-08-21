"""
URL Queue Management for Crawler
Implements a persistent URL queue using Redis with deduplication and priority handling.
"""

import asyncio
import json
import hashlib
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

import redis.asyncio as redis
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class QueuedURL:
    """Represents a URL in the crawling queue"""
    url: str
    parent_url: Optional[str] = None
    depth: int = 0
    priority: int = 5  # 1-10, lower is higher priority
    discovered_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    domain: Optional[str] = None
    template_hint: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.discovered_at is None:
            self.discovered_at = datetime.utcnow()
        if self.domain is None:
            parsed = urlparse(self.url)
            self.domain = parsed.netloc.lower()
        if self.metadata is None:
            self.metadata = {}

    @property
    def url_hash(self) -> str:
        """Generate a hash for URL deduplication"""
        return hashlib.sha256(self.url.encode()).hexdigest()[:16]

class URLQueue:
    """
    Redis-based URL queue with deduplication, priority, and domain-aware scheduling.
    
    Features:
    - Deduplication based on URL hash
    - Priority-based scheduling
    - Domain-aware rate limiting
    - Persistent storage in Redis
    - Batch operations for efficiency
    """
    
    def __init__(self, redis_client: redis.Redis, queue_name: str = "crawler_queue"):
        self.redis = redis_client
        self.queue_name = queue_name
        self.seen_urls_key = f"{queue_name}:seen"
        self.priority_queue_key = f"{queue_name}:priority"
        self.domain_last_crawl_key = f"{queue_name}:domain_last"
        self.url_data_key = f"{queue_name}:data"
        
    async def add_url(self, queued_url: QueuedURL, force: bool = False) -> bool:
        """
        Add a single URL to the queue.
        
        Args:
            queued_url: URL to add
            force: If True, bypass deduplication
            
        Returns:
            True if URL was added, False if already seen
        """
        url_hash = queued_url.url_hash
        
        # Check if URL already seen (unless forced)
        if not force:
            if await self.redis.sismember(self.seen_urls_key, url_hash):
                logger.debug(f"URL already seen: {queued_url.url}")
                return False
        
        # Mark as seen
        await self.redis.sadd(self.seen_urls_key, url_hash)
        
        # Store URL data
        url_data = asdict(queued_url)
        url_data['discovered_at'] = queued_url.discovered_at.isoformat() if queued_url.discovered_at else None
        url_data['scheduled_for'] = queued_url.scheduled_for.isoformat() if queued_url.scheduled_for else None
        
        await self.redis.hset(
            self.url_data_key,
            url_hash,
            json.dumps(url_data, default=str)
        )
        
        # Add to priority queue (score = priority + timestamp for FIFO within priority)
        score = queued_url.priority * 1000000 + int(datetime.utcnow().timestamp())
        await self.redis.zadd(self.priority_queue_key, {url_hash: score})
        
        logger.info(f"Added URL to queue: {queued_url.url} (priority: {queued_url.priority})")
        return True
        
    async def add_urls_batch(self, queued_urls: List[QueuedURL], force: bool = False) -> int:
        """
        Add multiple URLs in a batch operation.
        
        Args:
            queued_urls: List of URLs to add
            force: If True, bypass deduplication
            
        Returns:
            Number of URLs actually added
        """
        added_count = 0
        
        # Process in batches to avoid memory issues
        batch_size = 100
        for i in range(0, len(queued_urls), batch_size):
            batch = queued_urls[i:i + batch_size]
            
            async with self.redis.pipeline() as pipe:
                for queued_url in batch:
                    url_hash = queued_url.url_hash
                    
                    # Check deduplication
                    if not force and await self.redis.sismember(self.seen_urls_key, url_hash):
                        continue
                    
                    # Prepare data
                    url_data = asdict(queued_url)
                    url_data['discovered_at'] = queued_url.discovered_at.isoformat() if queued_url.discovered_at else None
                    url_data['scheduled_for'] = queued_url.scheduled_for.isoformat() if queued_url.scheduled_for else None
                    
                    # Add to pipeline
                    pipe.sadd(self.seen_urls_key, url_hash)
                    pipe.hset(self.url_data_key, url_hash, json.dumps(url_data, default=str))
                    
                    score = queued_url.priority * 1000000 + int(datetime.utcnow().timestamp())
                    pipe.zadd(self.priority_queue_key, {url_hash: score})
                    
                    added_count += 1
                
                await pipe.execute()
        
        logger.info(f"Added {added_count} URLs to queue in batch")
        return added_count
        
    async def get_next_url(self, domain_delay_seconds: int = 1) -> Optional[QueuedURL]:
        """
        Get the next URL to crawl, respecting domain delays.
        
        Args:
            domain_delay_seconds: Minimum seconds between requests to same domain
            
        Returns:
            Next URL to crawl, or None if queue empty or all domains delayed
        """
        # Get URLs by priority
        url_hashes = await self.redis.zrange(self.priority_queue_key, 0, 100)
        
        if not url_hashes:
            return None
            
        current_time = datetime.utcnow()
        
        for url_hash in url_hashes:
            # Get URL data
            url_data_json = await self.redis.hget(self.url_data_key, url_hash)
            if not url_data_json:
                # Clean up orphaned entry
                await self.redis.zrem(self.priority_queue_key, url_hash)
                continue
                
            url_data = json.loads(url_data_json)
            
            # Check domain delay
            domain = url_data.get('domain')
            if domain:
                last_crawl_str = await self.redis.get(f"{self.domain_last_crawl_key}:{domain}")
                if last_crawl_str:
                    last_crawl = datetime.fromisoformat(last_crawl_str.decode())
                    if current_time - last_crawl < timedelta(seconds=domain_delay_seconds):
                        continue  # Skip this domain for now
            
            # Remove from queue and return
            await self.redis.zrem(self.priority_queue_key, url_hash)
            await self.redis.hdel(self.url_data_key, url_hash)
            
            # Update domain last crawl time
            if domain:
                await self.redis.set(
                    f"{self.domain_last_crawl_key}:{domain}",
                    current_time.isoformat(),
                    ex=3600  # Expire after 1 hour
                )
            
            # Reconstruct QueuedURL object
            url_data['discovered_at'] = datetime.fromisoformat(url_data['discovered_at']) if url_data.get('discovered_at') else None
            url_data['scheduled_for'] = datetime.fromisoformat(url_data['scheduled_for']) if url_data.get('scheduled_for') else None
            
            return QueuedURL(**url_data)
            
        return None  # All domains are delayed
        
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        total_queued = await self.redis.zcard(self.priority_queue_key)
        total_seen = await self.redis.scard(self.seen_urls_key)
        
        # Get domain distribution
        domain_counts = {}
        url_hashes = await self.redis.zrange(self.priority_queue_key, 0, -1)
        
        for url_hash in url_hashes[:1000]:  # Limit for performance
            url_data_json = await self.redis.hget(self.url_data_key, url_hash)
            if url_data_json:
                url_data = json.loads(url_data_json)
                domain = url_data.get('domain', 'unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            'total_queued': total_queued,
            'total_seen': total_seen,
            'domain_distribution': domain_counts,
            'top_domains': sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        
    async def clear_queue(self, confirm: bool = False) -> bool:
        """Clear the entire queue (use with caution)"""
        if not confirm:
            logger.warning("Queue clear requested but not confirmed")
            return False
            
        await self.redis.delete(
            self.seen_urls_key,
            self.priority_queue_key,
            self.url_data_key
        )
        
        # Clear domain delays
        domain_keys = await self.redis.keys(f"{self.domain_last_crawl_key}:*")
        if domain_keys:
            await self.redis.delete(*domain_keys)
            
        logger.info("Queue cleared")
        return True
        
    async def is_url_seen(self, url: str) -> bool:
        """Check if URL has been seen before"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        return await self.redis.sismember(self.seen_urls_key, url_hash)
        
    async def mark_url_processed(self, url: str, status: str = "completed") -> bool:
        """Mark a URL as processed (for tracking purposes)"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
        processed_key = f"{self.queue_name}:processed"
        
        processed_data = {
            'url': url,
            'status': status,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        await self.redis.hset(processed_key, url_hash, json.dumps(processed_data))
        return True