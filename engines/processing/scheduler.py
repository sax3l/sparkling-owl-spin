"""
Advanced Scheduler System for Sparkling Owl Spin
Enhanced BFS Scheduler with pyramid architecture integration
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any, Callable
from collections import deque
from datetime import datetime, timedelta
import heapq
import uuid
from enum import Enum

from core.base_classes import BaseScheduler, Priority, TaskRequest, TaskResponse

logger = logging.getLogger(__name__)

class SchedulingStrategy(Enum):
    """Scheduling strategies"""
    BFS = "breadth_first"
    DFS = "depth_first"  
    PRIORITY = "priority_based"
    ROUND_ROBIN = "round_robin"
    LOAD_BALANCED = "load_balanced"

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CrawlTask:
    """Enhanced crawl task with metadata"""
    
    def __init__(self, url: str, depth: int = 0, priority: Priority = Priority.NORMAL, 
                 metadata: Dict[str, Any] = None, parent_task_id: str = None):
        self.id = str(uuid.uuid4())
        self.url = url
        self.depth = depth
        self.priority = priority
        self.metadata = metadata or {}
        self.parent_task_id = parent_task_id
        self.status = TaskStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.retry_count = 0
        self.max_retries = 3
        self.execution_time: Optional[float] = None
        self.error_message: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'depth': self.depth,
            'priority': self.priority.name if isinstance(self.priority, Priority) else self.priority,
            'metadata': self.metadata,
            'parent_task_id': self.parent_task_id,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'execution_time': self.execution_time,
            'error_message': self.error_message
        }

class EnhancedBFSScheduler(BaseScheduler):
    """
    Enhanced Breadth-First Search scheduler with advanced features
    Integrerad med pyramid architecture
    """
    
    def __init__(self, scheduler_id: str = None, max_concurrent_tasks: int = 10, 
                 max_depth: int = 5, delay_between_requests: float = 1.0):
        super().__init__(scheduler_id or "enhanced_bfs_scheduler", "Enhanced BFS Scheduler")
        
        # Core scheduling components
        self.bfs_queue = deque()
        self.priority_queue = []  # heap for priority tasks
        self.visited_urls = set()
        self.active_tasks: Dict[str, CrawlTask] = {}
        self.completed_tasks: Dict[str, CrawlTask] = {}
        self.failed_tasks: Dict[str, CrawlTask] = {}
        
        # Configuration
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_depth = max_depth
        self.delay_between_requests = delay_between_requests
        self.strategy = SchedulingStrategy.BFS
        
        # Advanced features
        self.url_filters: List[Callable[[str], bool]] = []
        self.rate_limiter = {}  # domain -> last_request_time
        self.domain_delays: Dict[str, float] = {}  # custom delays per domain
        self.retry_delays: List[float] = [1.0, 5.0, 15.0]  # exponential backoff
        
        # Statistics
        self.stats.update({
            'urls_discovered': 0,
            'urls_filtered': 0,
            'active_tasks_count': 0,
            'completed_tasks_count': 0,
            'failed_tasks_count': 0,
            'retry_count': 0,
            'average_depth': 0.0,
            'domains_crawled': set()
        })
        
    def add_url_filter(self, filter_func: Callable[[str], bool]):
        """Add a URL filter function"""
        self.url_filters.append(filter_func)
        
    def set_domain_delay(self, domain: str, delay: float):
        """Set custom delay for a specific domain"""
        self.domain_delays[domain] = delay
        
    def _should_crawl_url(self, url: str) -> bool:
        """Check if URL should be crawled based on filters"""
        # Apply all URL filters
        for filter_func in self.url_filters:
            if not filter_func(url):
                self.stats['urls_filtered'] += 1
                return False
        return True
        
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""
            
    async def can_make_request_to_domain(self, domain: str) -> bool:
        """Check if we can make a request to domain (rate limiting)"""
        if not domain:
            return True
            
        now = datetime.utcnow()
        last_request = self.rate_limiter.get(domain)
        
        if last_request:
            delay = self.domain_delays.get(domain, self.delay_between_requests)
            time_since_last = (now - last_request).total_seconds()
            if time_since_last < delay:
                return False
                
        return True
        
    async def add_url(self, url: str, depth: int = 0, priority: Priority = Priority.NORMAL, 
                     metadata: Dict[str, Any] = None, parent_task_id: str = None) -> Optional[str]:
        """Add URL to crawling queue with enhanced validation"""
        
        # Check if URL should be crawled
        if url in self.visited_urls:
            return None
            
        if depth > self.max_depth:
            self.logger.debug(f"URL {url} exceeds max depth {self.max_depth}")
            return None
            
        if not self._should_crawl_url(url):
            return None
            
        # Create crawl task
        task = CrawlTask(
            url=url,
            depth=depth,
            priority=priority,
            metadata=metadata,
            parent_task_id=parent_task_id
        )
        
        # Add to appropriate queue based on strategy
        if self.strategy == SchedulingStrategy.PRIORITY or priority != Priority.NORMAL:
            # Use priority queue
            heapq.heappush(self.priority_queue, (priority.value, task.created_at, task))
        else:
            # Use BFS queue
            self.bfs_queue.append(task)
            
        # Update tracking
        self.visited_urls.add(url)
        domain = self._extract_domain(url)
        if domain:
            self.stats['domains_crawled'].add(domain)
            
        # Update statistics
        self.stats['total_scheduled'] += 1
        self.stats['urls_discovered'] += 1
        self.stats['queue_size'] = len(self.bfs_queue) + len(self.priority_queue)
        
        if depth > 0:
            # Update average depth
            current_avg = self.stats['average_depth']
            total_tasks = self.stats['total_scheduled']
            self.stats['average_depth'] = ((current_avg * (total_tasks - 1)) + depth) / total_tasks
            
        self.logger.debug(f"Added URL {url} at depth {depth} with priority {priority}")
        return task.id
        
    async def get_next_task(self) -> Optional[CrawlTask]:
        """Get next task to process with rate limiting"""
        
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return None
            
        task = None
        
        # Try priority queue first
        while self.priority_queue and not task:
            priority_val, created_at, candidate_task = heapq.heappop(self.priority_queue)
            
            domain = self._extract_domain(candidate_task.url)
            if await self.can_make_request_to_domain(domain):
                task = candidate_task
                break
            else:
                # Put back in queue with slight delay
                heapq.heappush(self.priority_queue, (priority_val, created_at, candidate_task))
                await asyncio.sleep(0.1)
                
        # Try BFS queue if no priority task available
        if not task and self.bfs_queue:
            # Look for a task we can execute
            for _ in range(len(self.bfs_queue)):
                candidate_task = self.bfs_queue.popleft()
                domain = self._extract_domain(candidate_task.url)
                
                if await self.can_make_request_to_domain(domain):
                    task = candidate_task
                    break
                else:
                    # Put back at end of queue
                    self.bfs_queue.append(candidate_task)
                    
        if task:
            # Update rate limiter
            domain = self._extract_domain(task.url)
            if domain:
                self.rate_limiter[domain] = datetime.utcnow()
                
            # Mark as active
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self.active_tasks[task.id] = task
            
            # Update stats
            self.stats['total_processed'] += 1
            self.stats['active_tasks_count'] = len(self.active_tasks)
            self.stats['queue_size'] = len(self.bfs_queue) + len(self.priority_queue)
            
        return task
        
    async def mark_task_completed(self, task_id: str, result: Dict[str, Any] = None, 
                                 discovered_urls: List[str] = None):
        """Mark task as completed and process discovered URLs"""
        
        if task_id not in self.active_tasks:
            self.logger.warning(f"Task {task_id} not found in active tasks")
            return
            
        task = self.active_tasks.pop(task_id)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.execution_time = (task.completed_at - task.started_at).total_seconds()
        
        self.completed_tasks[task_id] = task
        
        # Process discovered URLs
        if discovered_urls:
            for url in discovered_urls:
                await self.add_url(
                    url=url,
                    depth=task.depth + 1,
                    priority=task.priority,
                    metadata={'discovered_from': task.url},
                    parent_task_id=task_id
                )
                
        # Update stats
        self.stats['active_tasks_count'] = len(self.active_tasks)
        self.stats['completed_tasks_count'] = len(self.completed_tasks)
        
        # Call parent method
        await super().mark_task_completed(task_id, result)
        
    async def mark_task_failed(self, task_id: str, error: str, retry: bool = True):
        """Mark task as failed with retry logic"""
        
        if task_id not in self.active_tasks:
            self.logger.warning(f"Task {task_id} not found in active tasks")
            return
            
        task = self.active_tasks.pop(task_id)
        task.error_message = error
        
        if retry and task.retry_count < task.max_retries:
            # Retry logic
            task.retry_count += 1
            task.status = TaskStatus.PENDING
            
            # Add delay before retry
            retry_delay = self.retry_delays[min(task.retry_count - 1, len(self.retry_delays) - 1)]
            task.metadata['retry_after'] = datetime.utcnow() + timedelta(seconds=retry_delay)
            
            # Add back to queue
            if task.priority != Priority.NORMAL:
                heapq.heappush(self.priority_queue, (task.priority.value, task.created_at, task))
            else:
                self.bfs_queue.append(task)
                
            self.stats['retry_count'] += 1
            self.logger.info(f"Retrying task {task_id} (attempt {task.retry_count}/{task.max_retries})")
        else:
            # Mark as permanently failed
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            self.failed_tasks[task_id] = task
            self.stats['failed_tasks_count'] = len(self.failed_tasks)
            self.logger.error(f"Task {task_id} failed permanently: {error}")
            
        self.stats['active_tasks_count'] = len(self.active_tasks)
        
    def is_empty(self) -> bool:
        """Check if scheduler has no more tasks"""
        return (len(self.bfs_queue) == 0 and 
                len(self.priority_queue) == 0 and 
                len(self.active_tasks) == 0)
                
    async def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed scheduler statistics"""
        stats = await self.get_stats()
        stats.update({
            'strategy': self.strategy.value,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'max_depth': self.max_depth,
            'delay_between_requests': self.delay_between_requests,
            'domains_crawled_count': len(self.stats['domains_crawled']),
            'domains_crawled': list(self.stats['domains_crawled']),
            'url_filters_count': len(self.url_filters),
            'custom_domain_delays': dict(self.domain_delays),
            'task_distribution': {
                'bfs_queue': len(self.bfs_queue),
                'priority_queue': len(self.priority_queue),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks)
            }
        })
        return stats
        
    async def get_task_by_id(self, task_id: str) -> Optional[CrawlTask]:
        """Get task by ID from any queue/storage"""
        # Check active tasks first
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
            
        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
            
        # Check failed tasks
        if task_id in self.failed_tasks:
            return self.failed_tasks[task_id]
            
        # Check pending queues
        for _, _, task in self.priority_queue:
            if task.id == task_id:
                return task
                
        for task in self.bfs_queue:
            if task.id == task_id:
                return task
                
        return None
        
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or active task"""
        task = await self.get_task_by_id(task_id)
        if not task:
            return False
            
        if task.status == TaskStatus.RUNNING:
            # Remove from active tasks
            self.active_tasks.pop(task_id, None)
            
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        
        self.logger.info(f"Cancelled task {task_id}")
        return True
        
    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check"""
        base_health = await super().health_check()
        
        # Add scheduler-specific health info
        queue_health = "healthy"
        if len(self.active_tasks) >= self.max_concurrent_tasks * 0.9:
            queue_health = "high_load"
        elif len(self.bfs_queue) + len(self.priority_queue) > 10000:
            queue_health = "queue_overload"
            
        base_health.update({
            'queue_health': queue_health,
            'detailed_stats': await self.get_detailed_stats(),
            'rate_limiter_entries': len(self.rate_limiter),
            'memory_usage': {
                'visited_urls': len(self.visited_urls),
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'failed_tasks': len(self.failed_tasks)
            }
        })
        
        return base_health

# Global scheduler instances
_global_scheduler: Optional[EnhancedBFSScheduler] = None
_job_queue: Optional[asyncio.Queue] = None

async def get_scheduler() -> EnhancedBFSScheduler:
    """Get the global scheduler instance"""
    global _global_scheduler
    if _global_scheduler is None:
        _global_scheduler = EnhancedBFSScheduler(
            max_concurrent_tasks=10,
            max_depth=5,
            delay_between_requests=1.0
        )
    return _global_scheduler

async def get_job_queue() -> asyncio.Queue:
    """Get the global job queue"""
    global _job_queue
    if _job_queue is None:
        _job_queue = asyncio.Queue()
    return _job_queue
