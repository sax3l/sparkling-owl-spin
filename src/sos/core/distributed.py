"""
Distributed Crawling Coordinator - Enterprise-grade distributed architecture
Inspired by Apache Nutch's distributed crawling and modern microservices patterns
"""

import asyncio
import json
import time
import hashlib
import uuid
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import weakref
import pickle
import redis
import aioredis
from urllib.parse import urlparse
import socket
import psutil

class NodeRole(Enum):
    COORDINATOR = "coordinator"
    CRAWLER = "crawler"
    PARSER = "parser"
    STORAGE = "storage"

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"  
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"

@dataclass
class CrawlTask:
    """Distributed crawl task"""
    id: str
    url: str
    priority: int = 0
    depth: int = 0
    created_at: float = 0
    assigned_at: float = 0
    completed_at: float = 0
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = None
    parent_task_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if self.created_at == 0:
            self.created_at = time.time()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CrawlerNode:
    """Distributed crawler node"""
    id: str
    role: NodeRole
    host: str
    port: int
    status: str = "active"
    capabilities: List[str] = None
    max_concurrent_tasks: int = 10
    current_tasks: int = 0
    last_heartbeat: float = 0
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.performance_metrics is None:
            self.performance_metrics = {
                'cpu_usage': 0,
                'memory_usage': 0,
                'tasks_completed': 0,
                'avg_task_time': 0,
                'success_rate': 1.0
            }

class TaskQueue:
    """Distributed task queue with Redis backend"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pending_queue = "crawl_tasks:pending"
        self.assigned_queue = "crawl_tasks:assigned"
        self.completed_queue = "crawl_tasks:completed"
        self.failed_queue = "crawl_tasks:failed"
        self.task_data_prefix = "crawl_task:"
        self.logger = logging.getLogger("task_queue")
    
    async def enqueue_task(self, task: CrawlTask) -> bool:
        """Add task to queue"""
        try:
            # Store task data
            task_key = f"{self.task_data_prefix}{task.id}"
            await self.redis.set(task_key, pickle.dumps(task))
            
            # Add to pending queue with priority
            await self.redis.zadd(self.pending_queue, {task.id: -task.priority})
            
            self.logger.info(f"Enqueued task {task.id} for URL {task.url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enqueue task {task.id}: {str(e)}")
            return False
    
    async def dequeue_task(self, node_id: str) -> Optional[CrawlTask]:
        """Get next task from queue"""
        try:
            # Get highest priority task
            task_ids = await self.redis.zrange(self.pending_queue, 0, 0, withscores=True)
            if not task_ids:
                return None
            
            task_id, priority = task_ids[0]
            task_id = task_id.decode('utf-8') if isinstance(task_id, bytes) else task_id
            
            # Remove from pending queue
            await self.redis.zrem(self.pending_queue, task_id)
            
            # Get task data
            task_key = f"{self.task_data_prefix}{task_id}"
            task_data = await self.redis.get(task_key)
            if not task_data:
                return None
            
            task = pickle.loads(task_data)
            
            # Mark as assigned
            task.status = TaskStatus.ASSIGNED
            task.assigned_to = node_id
            task.assigned_at = time.time()
            
            # Update task data and move to assigned queue
            await self.redis.set(task_key, pickle.dumps(task))
            await self.redis.zadd(self.assigned_queue, {task_id: time.time()})
            
            self.logger.info(f"Assigned task {task_id} to node {node_id}")
            return task
            
        except Exception as e:
            self.logger.error(f"Failed to dequeue task: {str(e)}")
            return None
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Mark task as completed"""
        try:
            task_key = f"{self.task_data_prefix}{task_id}"
            task_data = await self.redis.get(task_key)
            if not task_data:
                return False
            
            task = pickle.loads(task_data)
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.metadata['result'] = result
            
            # Update task data
            await self.redis.set(task_key, pickle.dumps(task))
            
            # Move queues
            await self.redis.zrem(self.assigned_queue, task_id)
            await self.redis.zadd(self.completed_queue, {task_id: time.time()})
            
            self.logger.info(f"Completed task {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete task {task_id}: {str(e)}")
            return False
    
    async def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed and potentially retry"""
        try:
            task_key = f"{self.task_data_prefix}{task_id}"
            task_data = await self.redis.get(task_key)
            if not task_data:
                return False
            
            task = pickle.loads(task_data)
            task.retry_count += 1
            task.metadata['last_error'] = error
            task.assigned_to = None
            
            # Move queues
            await self.redis.zrem(self.assigned_queue, task_id)
            
            if task.retry_count < task.max_retries:
                # Retry with lower priority
                task.status = TaskStatus.RETRY
                task.priority = max(0, task.priority - 1)
                await self.redis.zadd(self.pending_queue, {task_id: -task.priority})
                self.logger.info(f"Retrying task {task_id} (attempt {task.retry_count})")
            else:
                # Mark as permanently failed
                task.status = TaskStatus.FAILED
                await self.redis.zadd(self.failed_queue, {task_id: time.time()})
                self.logger.warning(f"Task {task_id} permanently failed after {task.retry_count} attempts")
            
            await self.redis.set(task_key, pickle.dumps(task))
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fail task {task_id}: {str(e)}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        return {
            'pending': await self.redis.zcard(self.pending_queue),
            'assigned': await self.redis.zcard(self.assigned_queue),
            'completed': await self.redis.zcard(self.completed_queue),
            'failed': await self.redis.zcard(self.failed_queue),
        }

class NodeRegistry:
    """Distributed node registry with health monitoring"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.nodes_key = "crawler_nodes"
        self.node_data_prefix = "crawler_node:"
        self.heartbeat_interval = 30  # seconds
        self.logger = logging.getLogger("node_registry")
    
    async def register_node(self, node: CrawlerNode) -> bool:
        """Register a crawler node"""
        try:
            node_key = f"{self.node_data_prefix}{node.id}"
            node.last_heartbeat = time.time()
            
            await self.redis.set(node_key, pickle.dumps(node))
            await self.redis.sadd(self.nodes_key, node.id)
            
            self.logger.info(f"Registered node {node.id} ({node.role.value}) at {node.host}:{node.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register node {node.id}: {str(e)}")
            return False
    
    async def update_node(self, node_id: str, updates: Dict[str, Any]) -> bool:
        """Update node information"""
        try:
            node_key = f"{self.node_data_prefix}{node_id}"
            node_data = await self.redis.get(node_key)
            if not node_data:
                return False
            
            node = pickle.loads(node_data)
            
            # Update fields
            for key, value in updates.items():
                if hasattr(node, key):
                    setattr(node, key, value)
            
            node.last_heartbeat = time.time()
            await self.redis.set(node_key, pickle.dumps(node))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to update node {node_id}: {str(e)}")
            return False
    
    async def heartbeat(self, node_id: str, metrics: Dict[str, Any] = None) -> bool:
        """Send heartbeat for node"""
        updates = {'last_heartbeat': time.time()}
        if metrics:
            updates['performance_metrics'] = metrics
        
        return await self.update_node(node_id, updates)
    
    async def get_active_nodes(self, role: NodeRole = None) -> List[CrawlerNode]:
        """Get list of active nodes"""
        try:
            node_ids = await self.redis.smembers(self.nodes_key)
            active_nodes = []
            current_time = time.time()
            
            for node_id in node_ids:
                node_id = node_id.decode('utf-8') if isinstance(node_id, bytes) else node_id
                node_key = f"{self.node_data_prefix}{node_id}"
                node_data = await self.redis.get(node_key)
                
                if node_data:
                    node = pickle.loads(node_data)
                    
                    # Check if node is active (heartbeat within threshold)
                    if current_time - node.last_heartbeat < self.heartbeat_interval * 2:
                        if role is None or node.role == role:
                            active_nodes.append(node)
                    else:
                        # Remove inactive node
                        await self.remove_node(node_id)
            
            return active_nodes
        except Exception as e:
            self.logger.error(f"Failed to get active nodes: {str(e)}")
            return []
    
    async def remove_node(self, node_id: str) -> bool:
        """Remove node from registry"""
        try:
            node_key = f"{self.node_data_prefix}{node_id}"
            await self.redis.delete(node_key)
            await self.redis.srem(self.nodes_key, node_id)
            
            self.logger.info(f"Removed node {node_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove node {node_id}: {str(e)}")
            return False

class LoadBalancer:
    """Load balancer for distributing tasks to nodes"""
    
    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry
        self.logger = logging.getLogger("load_balancer")
    
    async def select_node(self, task: CrawlTask, role: NodeRole = NodeRole.CRAWLER) -> Optional[CrawlerNode]:
        """Select best node for task using weighted round-robin"""
        active_nodes = await self.node_registry.get_active_nodes(role)
        if not active_nodes:
            return None
        
        # Filter nodes with available capacity
        available_nodes = [
            node for node in active_nodes 
            if node.current_tasks < node.max_concurrent_tasks
        ]
        
        if not available_nodes:
            return None
        
        # Calculate scores for each node
        scored_nodes = []
        for node in available_nodes:
            score = self._calculate_node_score(node, task)
            scored_nodes.append((node, score))
        
        # Sort by score (higher is better)
        scored_nodes.sort(key=lambda x: x[1], reverse=True)
        
        selected_node = scored_nodes[0][0]
        self.logger.debug(f"Selected node {selected_node.id} with score {scored_nodes[0][1]}")
        
        return selected_node
    
    def _calculate_node_score(self, node: CrawlerNode, task: CrawlTask) -> float:
        """Calculate node score for task assignment"""
        metrics = node.performance_metrics
        
        # Base score on availability (0-1)
        availability_score = 1.0 - (node.current_tasks / node.max_concurrent_tasks)
        
        # Performance score (0-1, inverted for CPU/memory usage)
        performance_score = (
            (1.0 - metrics.get('cpu_usage', 0) / 100) * 0.4 +
            (1.0 - metrics.get('memory_usage', 0) / 100) * 0.3 +
            metrics.get('success_rate', 1.0) * 0.3
        )
        
        # Task completion rate (higher is better)
        completion_rate = min(1.0, metrics.get('tasks_completed', 0) / 1000)
        
        # Response time score (lower avg_task_time is better)
        avg_time = metrics.get('avg_task_time', 10)
        time_score = max(0.1, 1.0 - (avg_time / 60))  # Normalize to 1 minute
        
        # Combine scores with weights
        total_score = (
            availability_score * 0.4 +
            performance_score * 0.3 +
            completion_rate * 0.2 +
            time_score * 0.1
        )
        
        return total_score

class DistributedCoordinator:
    """Main coordinator for distributed crawling"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.task_queue = None
        self.node_registry = None
        self.load_balancer = None
        self.coordinator_id = str(uuid.uuid4())
        self.is_running = False
        self.logger = logging.getLogger("distributed_coordinator")
    
    async def initialize(self):
        """Initialize coordinator"""
        self.redis_client = aioredis.from_url(self.redis_url)
        self.task_queue = TaskQueue(self.redis_client)
        self.node_registry = NodeRegistry(self.redis_client)
        self.load_balancer = LoadBalancer(self.node_registry)
        
        # Register coordinator as a node
        coordinator_node = CrawlerNode(
            id=self.coordinator_id,
            role=NodeRole.COORDINATOR,
            host=socket.gethostname(),
            port=0,
            capabilities=['task_distribution', 'monitoring']
        )
        
        await self.node_registry.register_node(coordinator_node)
        self.logger.info(f"Initialized coordinator {self.coordinator_id}")
    
    async def submit_urls(self, urls: List[str], priority: int = 0) -> List[str]:
        """Submit URLs for crawling"""
        task_ids = []
        
        for url in urls:
            task = CrawlTask(
                id=str(uuid.uuid4()),
                url=url,
                priority=priority
            )
            
            if await self.task_queue.enqueue_task(task):
                task_ids.append(task.id)
        
        self.logger.info(f"Submitted {len(task_ids)} tasks for crawling")
        return task_ids
    
    async def start_task_distribution(self):
        """Start distributing tasks to nodes"""
        self.is_running = True
        self.logger.info("Started task distribution")
        
        while self.is_running:
            try:
                # Get pending task
                task = await self.task_queue.dequeue_task("coordinator")
                if not task:
                    await asyncio.sleep(1)
                    continue
                
                # Select appropriate node
                selected_node = await self.load_balancer.select_node(task)
                if not selected_node:
                    # No available nodes, put task back
                    task.status = TaskStatus.PENDING
                    await self.task_queue.enqueue_task(task)
                    await asyncio.sleep(5)
                    continue
                
                # Assign task to selected node
                await self._assign_task_to_node(task, selected_node)
                
                # Update node task count
                await self.node_registry.update_node(
                    selected_node.id,
                    {'current_tasks': selected_node.current_tasks + 1}
                )
                
            except Exception as e:
                self.logger.error(f"Error in task distribution: {str(e)}")
                await asyncio.sleep(1)
    
    async def _assign_task_to_node(self, task: CrawlTask, node: CrawlerNode):
        """Assign task to specific node via message queue"""
        # In a real implementation, this would send a message to the node
        # via Redis pub/sub, RabbitMQ, or direct HTTP API call
        
        message = {
            'type': 'task_assignment',
            'task': asdict(task),
            'assigned_by': self.coordinator_id,
            'timestamp': time.time()
        }
        
        channel = f"node:{node.id}:tasks"
        await self.redis_client.lpush(channel, json.dumps(message))
        
        self.logger.info(f"Assigned task {task.id} to node {node.id}")
    
    async def monitor_system(self):
        """Monitor system health and performance"""
        while self.is_running:
            try:
                # Get system stats
                queue_stats = await self.task_queue.get_queue_stats()
                active_nodes = await self.node_registry.get_active_nodes()
                
                # Log system status
                self.logger.info(f"System Status - Nodes: {len(active_nodes)}, "
                               f"Pending: {queue_stats['pending']}, "
                               f"Assigned: {queue_stats['assigned']}, "
                               f"Completed: {queue_stats['completed']}, "
                               f"Failed: {queue_stats['failed']}")
                
                # Check for stuck tasks (assigned too long ago)
                await self._check_stuck_tasks()
                
                # Send coordinator heartbeat
                await self.node_registry.heartbeat(self.coordinator_id)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in system monitoring: {str(e)}")
                await asyncio.sleep(30)
    
    async def _check_stuck_tasks(self):
        """Check for and recover stuck tasks"""
        current_time = time.time()
        timeout = 300  # 5 minutes
        
        try:
            # Get all assigned tasks
            assigned_tasks = await self.redis_client.zrangebyscore(
                self.task_queue.assigned_queue, 
                0, current_time - timeout
            )
            
            for task_id in assigned_tasks:
                task_id = task_id.decode('utf-8') if isinstance(task_id, bytes) else task_id
                await self.task_queue.fail_task(task_id, "Task timeout - reassigning")
                self.logger.warning(f"Recovered stuck task {task_id}")
                
        except Exception as e:
            self.logger.error(f"Error checking stuck tasks: {str(e)}")
    
    async def stop(self):
        """Stop coordinator"""
        self.is_running = False
        await self.node_registry.remove_node(self.coordinator_id)
        if self.redis_client:
            await self.redis_client.close()
        
        self.logger.info("Stopped coordinator")

class DistributedCrawlerNode:
    """Individual crawler node in distributed system"""
    
    def __init__(self, 
                 node_id: str = None,
                 redis_url: str = "redis://localhost:6379",
                 max_concurrent_tasks: int = 10):
        
        self.node_id = node_id or str(uuid.uuid4())
        self.redis_url = redis_url
        self.max_concurrent_tasks = max_concurrent_tasks
        self.redis_client = None
        self.node_registry = None
        self.current_tasks = 0
        self.is_running = False
        self.task_executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        self.logger = logging.getLogger(f"crawler_node_{self.node_id}")
    
    async def initialize(self):
        """Initialize crawler node"""
        self.redis_client = aioredis.from_url(self.redis_url)
        self.node_registry = NodeRegistry(self.redis_client)
        
        # Register this node
        node = CrawlerNode(
            id=self.node_id,
            role=NodeRole.CRAWLER,
            host=socket.gethostname(),
            port=0,
            max_concurrent_tasks=self.max_concurrent_tasks,
            capabilities=['web_crawling', 'data_extraction']
        )
        
        await self.node_registry.register_node(node)
        self.logger.info(f"Initialized crawler node {self.node_id}")
    
    async def start_processing(self):
        """Start processing assigned tasks"""
        self.is_running = True
        
        # Start task listener and heartbeat sender
        await asyncio.gather(
            self._task_listener(),
            self._heartbeat_sender()
        )
    
    async def _task_listener(self):
        """Listen for assigned tasks"""
        task_channel = f"node:{self.node_id}:tasks"
        
        while self.is_running:
            try:
                # Get task from queue
                message = await self.redis_client.brpop(task_channel, timeout=1)
                if not message:
                    continue
                
                _, message_data = message
                message_obj = json.loads(message_data)
                
                if message_obj['type'] == 'task_assignment':
                    task_data = message_obj['task']
                    task = CrawlTask(**task_data)
                    
                    # Process task asynchronously
                    asyncio.create_task(self._process_task(task))
                
            except Exception as e:
                self.logger.error(f"Error in task listener: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_task(self, task: CrawlTask):
        """Process individual crawl task"""
        if self.current_tasks >= self.max_concurrent_tasks:
            # Return task to queue if overloaded
            await self._return_task(task)
            return
        
        self.current_tasks += 1
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing task {task.id} for URL {task.url}")
            
            # Simulate crawling (replace with actual crawling logic)
            await asyncio.sleep(random.uniform(2, 10))
            
            # Simulate successful result
            result = {
                'url': task.url,
                'title': f'Title for {task.url}',
                'content_length': random.randint(1000, 50000),
                'links_found': random.randint(10, 100),
                'processing_time': time.time() - start_time,
            }
            
            # Report completion
            await self._complete_task(task.id, result)
            
        except Exception as e:
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            await self._fail_task(task.id, str(e))
        
        finally:
            self.current_tasks -= 1
    
    async def _complete_task(self, task_id: str, result: Dict[str, Any]):
        """Report task completion"""
        # Update task queue
        task_queue = TaskQueue(self.redis_client)
        await task_queue.complete_task(task_id, result)
        
        # Update node metrics
        await self.node_registry.update_node(self.node_id, {
            'current_tasks': self.current_tasks,
            'performance_metrics.tasks_completed': 1  # Increment
        })
        
        self.logger.info(f"Completed task {task_id}")
    
    async def _fail_task(self, task_id: str, error: str):
        """Report task failure"""
        task_queue = TaskQueue(self.redis_client)
        await task_queue.fail_task(task_id, error)
        
        self.logger.warning(f"Failed task {task_id}: {error}")
    
    async def _return_task(self, task: CrawlTask):
        """Return task to queue if node is overloaded"""
        task.status = TaskStatus.PENDING
        task.assigned_to = None
        task_queue = TaskQueue(self.redis_client)
        await task_queue.enqueue_task(task)
    
    async def _heartbeat_sender(self):
        """Send periodic heartbeat with performance metrics"""
        while self.is_running:
            try:
                # Collect performance metrics
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                metrics = {
                    'cpu_usage': cpu_percent,
                    'memory_usage': memory_percent,
                    'current_tasks': self.current_tasks,
                    'timestamp': time.time()
                }
                
                await self.node_registry.heartbeat(self.node_id, metrics)
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error sending heartbeat: {str(e)}")
                await asyncio.sleep(30)
    
    async def stop(self):
        """Stop crawler node"""
        self.is_running = False
        await self.node_registry.remove_node(self.node_id)
        if self.redis_client:
            await self.redis_client.close()
        
        self.task_executor.shutdown(wait=True)
        self.logger.info("Stopped crawler node")

# Example usage and deployment helpers
async def deploy_coordinator():
    """Deploy coordinator node"""
    coordinator = DistributedCoordinator()
    await coordinator.initialize()
    
    # Start background tasks
    await asyncio.gather(
        coordinator.start_task_distribution(),
        coordinator.monitor_system()
    )

async def deploy_crawler_node():
    """Deploy crawler node"""
    node = DistributedCrawlerNode(max_concurrent_tasks=5)
    await node.initialize()
    await node.start_processing()

async def example_distributed_crawling():
    """Example of distributed crawling system"""
    
    # Start coordinator
    coordinator = DistributedCoordinator()
    await coordinator.initialize()
    
    # Start crawler nodes
    nodes = []
    for i in range(3):  # Start 3 crawler nodes
        node = DistributedCrawlerNode(
            node_id=f"crawler_{i}",
            max_concurrent_tasks=3
        )
        await node.initialize()
        nodes.append(node)
    
    try:
        # Submit crawling tasks
        urls = [
            f"https://example.com/page/{i}" 
            for i in range(50)  # 50 URLs to crawl
        ]
        
        task_ids = await coordinator.submit_urls(urls, priority=5)
        print(f"Submitted {len(task_ids)} crawling tasks")
        
        # Start processing (in background)
        tasks = [coordinator.start_task_distribution()]
        tasks.extend([node.start_processing() for node in nodes])
        
        # Monitor for a while
        await asyncio.sleep(60)  # Run for 1 minute
        
        # Check final stats
        queue_stats = await coordinator.task_queue.get_queue_stats()
        print(f"Final stats: {queue_stats}")
        
    finally:
        # Cleanup
        await coordinator.stop()
        for node in nodes:
            await node.stop()

if __name__ == "__main__":
    asyncio.run(example_distributed_crawling())
