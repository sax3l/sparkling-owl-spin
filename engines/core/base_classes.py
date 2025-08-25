"""
Core Base Classes for Sparkling Owl Spin
Sammanfogade base-klasser för pyramid-arkitekturen
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar
from enum import Enum
from dataclasses import dataclass
import uuid

try:
    from pydantic import BaseModel
except ImportError:
    # Fallback if pydantic is not available
    class BaseModel:
        pass

logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
TaskType = TypeVar('TaskType')

class ServiceStatus(Enum):
    """Service status enumeration"""
    INITIALIZING = "initializing"
    RUNNING = "running" 
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ServiceInfo:
    """Service information structure"""
    name: str
    version: str
    status: ServiceStatus
    health_status: str = "unknown"
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class BaseService(ABC):
    """
    Base service class for all services in the pyramid architecture
    Sammanfogad från core/base.py och andra base-klasser
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.status = ServiceStatus.INITIALIZING
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.dependencies: List[str] = []
        self.health_checks: Dict[str, callable] = {}
        self._lock = asyncio.Lock()
        
    @abstractmethod
    async def start(self) -> bool:
        """Start the service"""
        pass
        
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the service"""
        pass
        
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        pass
        
    async def get_info(self) -> ServiceInfo:
        """Get service information"""
        health = await self.health_check()
        return ServiceInfo(
            name=self.name,
            version=self.version,
            status=self.status,
            health_status=health.get('status', 'unknown'),
            dependencies=self.dependencies
        )

class BaseAgent(BaseService):
    """
    Base agent class for AI agents in the system
    Sammanfogad från agents/base.py
    """
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str] = None):
        super().__init__(name)
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.current_task: Optional[Dict[str, Any]] = None
        self.performance_metrics: Dict[str, Any] = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'average_execution_time': 0.0
        }
        
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task"""
        pass
        
    async def can_handle_task(self, task: Dict[str, Any]) -> bool:
        """Check if agent can handle the task"""
        task_type = task.get('type', '')
        return task_type in self.capabilities
        
    async def start(self) -> bool:
        """Start the agent"""
        self.status = ServiceStatus.RUNNING
        self.logger.info(f"Agent {self.name} started with capabilities: {self.capabilities}")
        return True
        
    async def stop(self) -> bool:
        """Stop the agent"""
        self.status = ServiceStatus.STOPPING
        # Wait for current task to complete
        if self.current_task:
            self.logger.info(f"Waiting for current task to complete: {self.current_task.get('id', 'unknown')}")
            # Implementation would wait for task completion
        self.status = ServiceStatus.STOPPED
        self.logger.info(f"Agent {self.name} stopped")
        return True
        
    async def health_check(self) -> Dict[str, Any]:
        """Agent health check"""
        return {
            'status': 'healthy' if self.status == ServiceStatus.RUNNING else 'unhealthy',
            'agent_id': self.agent_id,
            'capabilities': self.capabilities,
            'queue_size': self.task_queue.qsize(),
            'current_task': self.current_task.get('id', None) if self.current_task else None,
            'metrics': self.performance_metrics
        }

class BaseEngine(BaseService):
    """
    Base engine class for processing engines
    Sammanfogad från tools/base.py och engines
    """
    
    def __init__(self, engine_id: str, name: str, engine_type: str):
        super().__init__(name)
        self.engine_id = engine_id
        self.engine_type = engine_type
        self.configuration: Dict[str, Any] = {}
        self.is_available: bool = True
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        
    @abstractmethod
    async def process(self, data: Any, config: Dict[str, Any] = None) -> Any:
        """Process data through the engine"""
        pass
        
    @abstractmethod
    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate engine configuration"""
        pass
        
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure the engine"""
        if await self.validate_config(config):
            self.configuration.update(config)
            self.logger.info(f"Engine {self.name} configured successfully")
            return True
        else:
            self.logger.error(f"Invalid configuration for engine {self.name}")
            return False
            
    async def start(self) -> bool:
        """Start the engine"""
        self.status = ServiceStatus.RUNNING
        self.is_available = True
        self.logger.info(f"Engine {self.name} ({self.engine_type}) started")
        return True
        
    async def stop(self) -> bool:
        """Stop the engine"""
        self.status = ServiceStatus.STOPPING
        self.is_available = False
        # Wait for processing queue to empty
        while not self.processing_queue.empty():
            await asyncio.sleep(0.1)
        self.status = ServiceStatus.STOPPED
        self.logger.info(f"Engine {self.name} stopped")
        return True
        
    async def health_check(self) -> Dict[str, Any]:
        """Engine health check"""
        return {
            'status': 'healthy' if self.is_available else 'unhealthy',
            'engine_id': self.engine_id,
            'engine_type': self.engine_type,
            'queue_size': self.processing_queue.qsize(),
            'configuration': bool(self.configuration),
            'is_available': self.is_available
        }

class BaseScheduler(BaseService):
    """
    Base scheduler class for task scheduling
    """
    
    def __init__(self, scheduler_id: str, name: str):
        super().__init__(name)
        self.scheduler_id = scheduler_id
        self.queue = asyncio.PriorityQueue()
        self.stats = {
            'total_scheduled': 0,
            'total_processed': 0,
            'queue_size': 0,
            'active_tasks': 0
        }
        
    async def schedule_task(self, task: Dict[str, Any], priority: Priority = Priority.NORMAL) -> str:
        """Schedule a task with priority"""
        task_id = str(uuid.uuid4())
        task['id'] = task_id
        task['priority'] = priority
        task['scheduled_at'] = asyncio.get_event_loop().time()
        
        await self.queue.put((priority.value, task_id, task))
        self.stats['total_scheduled'] += 1
        self.stats['queue_size'] = self.queue.qsize()
        
        self.logger.debug(f"Scheduled task {task_id} with priority {priority}")
        return task_id
        
    async def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task from queue"""
        if not self.queue.empty():
            priority, task_id, task = await self.queue.get()
            self.stats['total_processed'] += 1
            self.stats['queue_size'] = self.queue.qsize()
            self.stats['active_tasks'] += 1
            return task
        return None
        
    async def mark_task_completed(self, task_id: str, result: Dict[str, Any] = None):
        """Mark task as completed"""
        self.stats['active_tasks'] = max(0, self.stats['active_tasks'] - 1)
        self.logger.debug(f"Task {task_id} completed")
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return self.stats.copy()
        
    async def start(self) -> bool:
        """Start scheduler"""
        self.status = ServiceStatus.RUNNING
        self.logger.info(f"Scheduler {self.name} started")
        return True
        
    async def stop(self) -> bool:
        """Stop scheduler"""
        self.status = ServiceStatus.STOPPING
        # Wait for active tasks to complete
        while self.stats['active_tasks'] > 0:
            await asyncio.sleep(0.1)
        self.status = ServiceStatus.STOPPED
        self.logger.info(f"Scheduler {self.name} stopped")
        return True
        
    async def health_check(self) -> Dict[str, Any]:
        """Scheduler health check"""
        return {
            'status': 'healthy' if self.status == ServiceStatus.RUNNING else 'unhealthy',
            'scheduler_id': self.scheduler_id,
            'stats': self.stats,
            'queue_empty': self.queue.empty()
        }

# Pydantic models for data validation
class TaskRequest(BaseModel):
    """Task request model"""
    type: str
    priority: Optional[Priority] = Priority.NORMAL
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    """Task response model"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class ServiceHealthResponse(BaseModel):
    """Service health response model"""
    service_name: str
    status: ServiceStatus
    health_details: Dict[str, Any]
    timestamp: float

# Utility functions for base classes
def create_service_logger(service_name: str) -> logging.Logger:
    """Create a standardized logger for services"""
    return logging.getLogger(f"sparkling_owl_spin.{service_name}")

async def safe_execute(coro, timeout: float = 30.0, default_return=None):
    """Safely execute a coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout}s")
        return default_return
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return default_return
