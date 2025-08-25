#!/usr/bin/env python3
"""
Base Models - Fundamental data models for the pyramid architecture

These base models provide common structures used across all layers:
- Engines
- Agents  
- Processing
- Integrations
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4
import json

class ServiceStatus(Enum):
    """Status of services in the pyramid"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy" 
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

class SystemHealth(Enum):
    """Overall system health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"

class TaskStatus(Enum):
    """Status of tasks throughout the pyramid"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5

@dataclass
class BaseTask:
    """Base task model for all pyramid layers"""
    task_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata,
            'error_message': self.error_message,
            'retries': self.retries,
            'max_retries': self.max_retries
        }

@dataclass  
class BaseResult:
    """Base result model for all pyramid layers"""
    result_id: str = field(default_factory=lambda: str(uuid4()))
    task_id: str = ""
    success: bool = False
    data: Any = None
    error: str = ""
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'result_id': self.result_id,
            'task_id': self.task_id,
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'warnings': self.warnings,
            'metadata': self.metadata,
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat()
        }

@dataclass
class BaseTarget:
    """Base target model for operations"""
    target_id: str = field(default_factory=lambda: str(uuid4()))
    target_type: str = ""
    url: str = ""
    domain: str = ""
    additional_urls: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class BaseEngine:
    """Base engine model"""
    engine_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    status: ServiceStatus = ServiceStatus.UNKNOWN
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None

class BaseService(ABC):
    """Abstract base class for all services in the pyramid"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.status = ServiceStatus.UNKNOWN
        self.metrics = {}
        self.last_health_check = None
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Perform health check"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass
    
    def get_status(self) -> ServiceStatus:
        """Get current service status"""
        return self.status
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return self.metrics.copy()

class BaseEngine(BaseService):
    """Base class for all engines"""
    
    @abstractmethod
    async def execute(self, task: BaseTask) -> BaseResult:
        """Execute a task"""
        pass

class BaseAgent(BaseService):
    """Base class for AI agents"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.knowledge_base = {}
        self.learning_enabled = config.get('learning_enabled', True) if config else True
    
    @abstractmethod
    async def analyze(self, input_data: Any) -> Dict[str, Any]:
        """Analyze input and provide insights"""
        pass
    
    @abstractmethod
    async def recommend(self, context: Dict[str, Any]) -> List[str]:
        """Provide recommendations based on context"""
        pass

class BaseProcessor(BaseService):
    """Base class for processing modules"""
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data"""
        pass
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate processed data"""
        pass

class BaseIntegration(BaseService):
    """Base class for integrations"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.api_client = None
        self.rate_limiter = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to external service"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from external service"""
        pass

@dataclass
class ScrapingTask(BaseTask):
    """Scraping-specific task model"""
    target_url: str = ""
    selectors: Dict[str, str] = field(default_factory=dict)
    strategy: str = "basic"
    max_pages: int = 1
    rate_limit: float = 1.0
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)

@dataclass
class SecurityTask(BaseTask):
    """Security analysis task model"""
    target: BaseTarget = field(default_factory=BaseTarget)
    analysis_type: str = "vulnerability_assessment"
    scan_level: str = "passive"
    compliance_frameworks: List[str] = field(default_factory=list)

@dataclass
class DataTask(BaseTask):
    """Data processing task model"""
    dataset_id: str = ""
    analysis_type: str = "exploratory"
    parameters: Dict[str, Any] = field(default_factory=dict)
    output_format: str = "json"

# Common response models
@dataclass
class HealthResponse:
    """Health check response model"""
    status: SystemHealth
    services: Dict[str, ServiceStatus]
    total_services: int
    healthy_services: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'services': {k: v.value for k, v in self.services.items()},
            'total_services': self.total_services,
            'healthy_services': self.healthy_services,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass 
class ErrorResponse:
    """Error response model"""
    error: str
    error_code: str = "UNKNOWN_ERROR"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error': self.error,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

# Utility functions
def create_task_id() -> str:
    """Create unique task ID"""
    return str(uuid4())

def serialize_datetime(dt: datetime) -> str:
    """Serialize datetime to ISO format"""
    return dt.isoformat()

def deserialize_datetime(dt_str: str) -> datetime:
    """Deserialize datetime from ISO format"""
    return datetime.fromisoformat(dt_str)

def validate_config(config: Dict[str, Any], required_keys: List[str]) -> bool:
    """Validate configuration has required keys"""
    return all(key in config for key in required_keys)

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configuration dictionaries"""
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged

# Export all models and classes
__all__ = [
    'ServiceStatus', 'SystemHealth', 'TaskStatus', 'Priority',
    'BaseTask', 'BaseResult', 'BaseTarget', 'BaseEngine', 
    'BaseService', 'BaseAgent', 'BaseProcessor', 'BaseIntegration',
    'ScrapingTask', 'SecurityTask', 'DataTask',
    'HealthResponse', 'ErrorResponse',
    'create_task_id', 'serialize_datetime', 'deserialize_datetime',
    'validate_config', 'merge_configs'
]
