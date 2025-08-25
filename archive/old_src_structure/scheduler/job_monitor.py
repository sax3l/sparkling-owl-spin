"""
Job monitoring and health checking for the ECaDP scheduler.

Monitors job execution, tracks performance metrics, and handles job failures.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock

from src.utils.logger import get_logger
from src.database.models import Job, JobStatus, JobType

logger = get_logger(__name__)

class JobHealth(Enum):
    """Job health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class JobMetrics:
    """Metrics for a single job execution"""
    job_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: JobStatus = JobStatus.RUNNING
    error_message: Optional[str] = None
    items_processed: int = 0
    items_failed: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

@dataclass
class JobHealthStatus:
    """Health status for a job type"""
    job_type: JobType
    health: JobHealth = JobHealth.UNKNOWN
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_duration: float = 0.0
    last_execution: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    error_rate: float = 0.0
    recent_errors: List[str] = field(default_factory=list)

class JobMonitor:
    """
    Monitors job execution and provides health metrics.
    
    Features:
    - Real-time job tracking
    - Performance metrics collection
    - Health status calculation
    - Alert generation
    - Historical data retention
    """
    
    def __init__(self, alert_callback: Optional[Callable] = None):
        self.active_jobs: Dict[str, JobMetrics] = {}
        self.job_health: Dict[JobType, JobHealthStatus] = {}
        self.alert_callback = alert_callback
        self._lock = Lock()
        
        # Initialize health status for all job types
        for job_type in JobType:
            self.job_health[job_type] = JobHealthStatus(job_type=job_type)
    
    def start_job_monitoring(self, job_id: str, job_type: JobType) -> JobMetrics:
        """Start monitoring a job execution"""
        with self._lock:
            metrics = JobMetrics(
                job_id=job_id,
                start_time=datetime.utcnow(),
                status=JobStatus.RUNNING
            )
            self.active_jobs[job_id] = metrics
            
            logger.info(f"Started monitoring job {job_id} ({job_type.value})")
            return metrics
    
    def update_job_progress(self, 
                          job_id: str, 
                          items_processed: int = 0,
                          items_failed: int = 0,
                          memory_usage_mb: float = 0.0,
                          cpu_usage_percent: float = 0.0):
        """Update job progress metrics"""
        with self._lock:
            if job_id in self.active_jobs:
                metrics = self.active_jobs[job_id]
                metrics.items_processed = items_processed
                metrics.items_failed = items_failed
                metrics.memory_usage_mb = memory_usage_mb
                metrics.cpu_usage_percent = cpu_usage_percent
    
    def complete_job_monitoring(self, 
                              job_id: str, 
                              job_type: JobType,
                              status: JobStatus,
                              error_message: Optional[str] = None) -> Optional[JobMetrics]:
        """Complete job monitoring and update health status"""
        with self._lock:
            if job_id not in self.active_jobs:
                logger.warning(f"Attempted to complete monitoring for unknown job {job_id}")
                return None
            
            metrics = self.active_jobs[job_id]
            metrics.end_time = datetime.utcnow()
            metrics.status = status
            metrics.error_message = error_message
            metrics.duration = (metrics.end_time - metrics.start_time).total_seconds()
            
            # Update health status
            self._update_job_health(job_type, metrics)
            
            # Remove from active jobs
            completed_metrics = self.active_jobs.pop(job_id)
            
            logger.info(f"Completed monitoring job {job_id} - Status: {status.value}, Duration: {metrics.duration:.2f}s")
            
            # Check for alerts
            self._check_alerts(job_type, metrics)
            
            return completed_metrics
    
    def _update_job_health(self, job_type: JobType, metrics: JobMetrics):
        """Update health status for a job type"""
        health_status = self.job_health[job_type]
        
        health_status.total_executions += 1
        health_status.last_execution = metrics.end_time
        
        if metrics.status == JobStatus.COMPLETED:
            health_status.successful_executions += 1
            health_status.last_success = metrics.end_time
        else:
            health_status.failed_executions += 1
            health_status.last_failure = metrics.end_time
            
            # Track recent errors
            if metrics.error_message:
                health_status.recent_errors.append(
                    f"{metrics.end_time.isoformat()}: {metrics.error_message}"
                )
                # Keep only last 10 errors
                health_status.recent_errors = health_status.recent_errors[-10:]
        
        # Calculate error rate
        if health_status.total_executions > 0:
            health_status.error_rate = health_status.failed_executions / health_status.total_executions
        
        # Calculate average duration (simple moving average)
        if metrics.duration:
            if health_status.average_duration == 0:
                health_status.average_duration = metrics.duration
            else:
                # Exponential moving average
                alpha = 0.2
                health_status.average_duration = (
                    alpha * metrics.duration + (1 - alpha) * health_status.average_duration
                )
        
        # Determine health status
        health_status.health = self._calculate_health(health_status)
    
    def _calculate_health(self, health_status: JobHealthStatus) -> JobHealth:
        """Calculate overall health for a job type"""
        if health_status.total_executions == 0:
            return JobHealth.UNKNOWN
        
        # Check error rate
        if health_status.error_rate > 0.5:  # More than 50% failure rate
            return JobHealth.CRITICAL
        elif health_status.error_rate > 0.2:  # More than 20% failure rate
            return JobHealth.WARNING
        
        # Check if recent executions have failed
        recent_window = datetime.utcnow() - timedelta(hours=1)
        if health_status.last_failure and health_status.last_failure > recent_window:
            if not health_status.last_success or health_status.last_success < health_status.last_failure:
                return JobHealth.WARNING
        
        # Check execution frequency (if we haven't seen executions recently)
        if health_status.last_execution:
            time_since_last = datetime.utcnow() - health_status.last_execution
            if time_since_last > timedelta(hours=24):  # No executions in 24 hours
                return JobHealth.WARNING
        
        return JobHealth.HEALTHY
    
    def _check_alerts(self, job_type: JobType, metrics: JobMetrics):
        """Check if we should generate alerts based on job metrics"""
        if not self.alert_callback:
            return
        
        health_status = self.job_health[job_type]
        alerts = []
        
        # High error rate alert
        if health_status.error_rate > 0.3:
            alerts.append({
                'type': 'high_error_rate',
                'job_type': job_type.value,
                'error_rate': health_status.error_rate,
                'message': f"High error rate for {job_type.value}: {health_status.error_rate:.1%}"
            })
        
        # Long duration alert
        if metrics.duration and health_status.average_duration > 0:
            if metrics.duration > health_status.average_duration * 3:  # 3x longer than average
                alerts.append({
                    'type': 'long_duration',
                    'job_type': job_type.value,
                    'duration': metrics.duration,
                    'average': health_status.average_duration,
                    'message': f"Job {metrics.job_id} took {metrics.duration:.1f}s (avg: {health_status.average_duration:.1f}s)"
                })
        
        # Failed job alert
        if metrics.status != JobStatus.COMPLETED:
            alerts.append({
                'type': 'job_failed',
                'job_type': job_type.value,
                'job_id': metrics.job_id,
                'error': metrics.error_message,
                'message': f"Job {metrics.job_id} failed: {metrics.error_message}"
            })
        
        # Send alerts
        for alert in alerts:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
    
    def get_active_jobs(self) -> Dict[str, JobMetrics]:
        """Get currently active jobs"""
        with self._lock:
            return self.active_jobs.copy()
    
    def get_job_health_status(self, job_type: Optional[JobType] = None) -> Dict[JobType, JobHealthStatus]:
        """Get health status for job types"""
        with self._lock:
            if job_type:
                return {job_type: self.job_health[job_type]}
            return self.job_health.copy()
    
    def get_overall_health(self) -> JobHealth:
        """Get overall system health based on all job types"""
        with self._lock:
            healths = [status.health for status in self.job_health.values()]
            
            if JobHealth.CRITICAL in healths:
                return JobHealth.CRITICAL
            elif JobHealth.WARNING in healths:
                return JobHealth.WARNING
            elif JobHealth.HEALTHY in healths:
                return JobHealth.HEALTHY
            else:
                return JobHealth.UNKNOWN
    
    def reset_job_health(self, job_type: JobType):
        """Reset health statistics for a job type"""
        with self._lock:
            self.job_health[job_type] = JobHealthStatus(job_type=job_type)
            logger.info(f"Reset health statistics for {job_type.value}")
    
    def cleanup_old_data(self, max_age_hours: int = 168):  # 1 week default
        """Clean up old monitoring data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        with self._lock:
            # Clean up old error messages
            for health_status in self.job_health.values():
                health_status.recent_errors = [
                    error for error in health_status.recent_errors 
                    if not error.startswith(cutoff_time.strftime("%Y-%m-%d"))
                ]