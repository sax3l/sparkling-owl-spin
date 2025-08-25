"""
Job definitions for ECaDP scheduler.

Defines all scheduled jobs that can be executed by the system.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

class JobPriority(Enum):
    """Job priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class JobFrequency(Enum):
    """Job execution frequency."""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

@dataclass
class JobDefinition:
    """Definition of a scheduled job."""
    id: str
    name: str
    description: str
    function: Callable
    frequency: JobFrequency
    priority: JobPriority = JobPriority.NORMAL
    parameters: Dict[str, Any] = None
    timeout_minutes: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 60
    enabled: bool = True
    next_run: Optional[datetime] = None
    last_run: Optional[datetime] = None
    tags: list = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.tags is None:
            self.tags = []

# Predefined job definitions
JOB_DEFINITIONS = {
    "data_quality_check": JobDefinition(
        id="data_quality_check",
        name="Data Quality Check",
        description="Performs comprehensive data quality analysis",
        function=None,  # Will be set by scheduler
        frequency=JobFrequency.DAILY,
        priority=JobPriority.HIGH,
        timeout_minutes=60,
        tags=["data_quality", "analysis"]
    ),
    
    "proxy_pool_refresh": JobDefinition(
        id="proxy_pool_refresh", 
        name="Proxy Pool Refresh",
        description="Refreshes and validates proxy pool",
        function=None,
        frequency=JobFrequency.HOURLY,
        priority=JobPriority.NORMAL,
        timeout_minutes=15,
        tags=["proxy", "maintenance"]
    ),
    
    "database_cleanup": JobDefinition(
        id="database_cleanup",
        name="Database Cleanup", 
        description="Cleans up old data and optimizes database",
        function=None,
        frequency=JobFrequency.WEEKLY,
        priority=JobPriority.LOW,
        timeout_minutes=120,
        tags=["database", "maintenance"]
    ),
    
    "export_scheduler": JobDefinition(
        id="export_scheduler",
        name="Export Job Scheduler",
        description="Processes pending export requests",
        function=None,
        frequency=JobFrequency.HOURLY,
        priority=JobPriority.NORMAL,
        timeout_minutes=45,
        tags=["export", "data"]
    ),
    
    "scraping_job_monitor": JobDefinition(
        id="scraping_job_monitor",
        name="Scraping Job Monitor",
        description="Monitors and manages active scraping jobs",
        function=None,
        frequency=JobFrequency.HOURLY,
        priority=JobPriority.HIGH,
        timeout_minutes=10,
        tags=["scraping", "monitoring"]
    ),
    
    "system_health_check": JobDefinition(
        id="system_health_check",
        name="System Health Check",
        description="Performs comprehensive system health monitoring",
        function=None,
        frequency=JobFrequency.HOURLY,
        priority=JobPriority.CRITICAL,
        timeout_minutes=5,
        tags=["health", "monitoring"]
    )
}

def get_job_definition(job_id: str) -> Optional[JobDefinition]:
    """Get job definition by ID."""
    return JOB_DEFINITIONS.get(job_id)

def get_all_job_definitions() -> Dict[str, JobDefinition]:
    """Get all job definitions."""
    return JOB_DEFINITIONS.copy()

def get_jobs_by_frequency(frequency: JobFrequency) -> Dict[str, JobDefinition]:
    """Get jobs by frequency."""
    return {
        job_id: job_def for job_id, job_def in JOB_DEFINITIONS.items()
        if job_def.frequency == frequency
    }

def get_jobs_by_priority(priority: JobPriority) -> Dict[str, JobDefinition]:
    """Get jobs by priority."""
    return {
        job_id: job_def for job_id, job_def in JOB_DEFINITIONS.items()
        if job_def.priority == priority
    }

def get_enabled_jobs() -> Dict[str, JobDefinition]:
    """Get only enabled jobs."""
    return {
        job_id: job_def for job_id, job_def in JOB_DEFINITIONS.items()
        if job_def.enabled
    }

__all__ = [
    "JobDefinition", "JobPriority", "JobFrequency", 
    "JOB_DEFINITIONS", "get_job_definition", "get_all_job_definitions",
    "get_jobs_by_frequency", "get_jobs_by_priority", "get_enabled_jobs"
]