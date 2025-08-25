import asyncio
import logging
from typing import Optional, List, Dict, Any
from collections import deque
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class BFSScheduler:
    """Breadth-First Search scheduler for URL crawling"""
    
    def __init__(self):
        self.queue = deque()
        self.visited = set()
        self.stats = {
            'total_scheduled': 0,
            'total_processed': 0,
            'queue_size': 0
        }
    
    def add_url(self, url: str, depth: int = 0, metadata: Dict[str, Any] = None):
        """Add URL to crawling queue"""
        if url not in self.visited:
            self.queue.append({
                'url': url,
                'depth': depth,
                'metadata': metadata or {}
            })
            self.visited.add(url)
            self.stats['total_scheduled'] += 1
            self.stats['queue_size'] = len(self.queue)
    
    def get_next(self) -> Optional[Dict[str, Any]]:
        """Get next URL to crawl (BFS order)"""
        if self.queue:
            item = self.queue.popleft()
            self.stats['total_processed'] += 1
            self.stats['queue_size'] = len(self.queue)
            return item
        return None
    
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self.queue) == 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return self.stats.copy()

# Global job queue (in-memory for MVP, Redis for production)
_job_queue: asyncio.Queue = asyncio.Queue()

