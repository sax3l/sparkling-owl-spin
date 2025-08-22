"""
Job scheduler for ECaDP platform.
Handles scheduling and execution of crawl and processing jobs.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class JobResult:
    """Job execution result."""
    job_id: str
    status: JobStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Job:
    """Represents a scheduled job."""
    job_id: str
    job_type: str
    payload: Dict[str, Any]
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 3600  # seconds
    scheduled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    # Execution state
    status: JobStatus = JobStatus.PENDING
    attempts: int = 0
    last_error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.scheduled_at is None:
            self.scheduled_at = self.created_at


class JobScheduler:
    """Main job scheduler class."""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.jobs: Dict[str, Job] = {}
        self.job_handlers: Dict[str, Callable] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def register_handler(self, job_type: str, handler: Callable):
        """
        Register a job handler for a specific job type.
        
        Args:
            job_type: Type of job
            handler: Async function to handle the job
        """
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    def schedule_job(
        self,
        job_type: str,
        payload: Dict[str, Any],
        priority: JobPriority = JobPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
        max_retries: int = 3,
        **kwargs
    ) -> str:
        """
        Schedule a new job.
        
        Args:
            job_type: Type of job
            payload: Job payload data
            priority: Job priority
            scheduled_at: When to execute the job
            max_retries: Maximum retry attempts
            **kwargs: Additional job parameters
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        job = Job(
            job_id=job_id,
            job_type=job_type,
            payload=payload,
            priority=priority,
            scheduled_at=scheduled_at,
            max_retries=max_retries,
            **kwargs
        )
        
        self.jobs[job_id] = job
        logger.info(f"Scheduled job {job_id} of type {job_type}")
        
        return job_id
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending or running job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            True if cancelled successfully
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        if job.status == JobStatus.RUNNING:
            # Cancel running task
            if job_id in self.running_jobs:
                self.running_jobs[job_id].cancel()
                del self.running_jobs[job_id]
        
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.utcnow()
        
        logger.info(f"Cancelled job {job_id}")
        return True
    
    def get_job_status(self, job_id: str) -> Optional[JobResult]:
        """
        Get job status and result.
        
        Args:
            job_id: Job ID
            
        Returns:
            JobResult or None if job not found
        """
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        
        execution_time = None
        if job.started_at and job.completed_at:
            execution_time = (job.completed_at - job.started_at).total_seconds()
        
        return JobResult(
            job_id=job_id,
            status=job.status,
            execution_time=execution_time,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error=job.last_error
        )
    
    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[str] = None,
        limit: int = 100
    ) -> List[JobResult]:
        """
        List jobs with optional filtering.
        
        Args:
            status: Filter by job status
            job_type: Filter by job type
            limit: Maximum number of jobs to return
            
        Returns:
            List of JobResult objects
        """
        results = []
        
        for job in self.jobs.values():
            if status and job.status != status:
                continue
            if job_type and job.job_type != job_type:
                continue
            
            result = self.get_job_status(job.job_id)
            if result:
                results.append(result)
            
            if len(results) >= limit:
                break
        
        # Sort by created_at descending
        results.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
        
        return results
    
    async def start(self):
        """Start the job scheduler."""
        if self.is_running:
            return
        
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Job scheduler started")
    
    async def stop(self):
        """Stop the job scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all running jobs
        for task in self.running_jobs.values():
            task.cancel()
        
        # Wait for running jobs to complete
        if self.running_jobs:
            await asyncio.gather(*self.running_jobs.values(), return_exceptions=True)
        
        # Cancel scheduler task
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Job scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                await self._process_pending_jobs()
                await self._cleanup_completed_jobs()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_pending_jobs(self):
        """Process pending jobs that are ready to run."""
        now = datetime.utcnow()
        available_workers = self.max_workers - len(self.running_jobs)
        
        if available_workers <= 0:
            return
        
        # Get pending jobs that are ready to run
        ready_jobs = []
        for job in self.jobs.values():
            if (job.status == JobStatus.PENDING and 
                job.scheduled_at <= now):
                ready_jobs.append(job)
        
        # Sort by priority and scheduled time
        ready_jobs.sort(key=lambda j: (j.priority.value, j.scheduled_at), reverse=True)
        
        # Start jobs up to worker limit
        for job in ready_jobs[:available_workers]:
            await self._start_job(job)
    
    async def _start_job(self, job: Job):
        """Start executing a job."""
        if job.job_type not in self.job_handlers:
            job.status = JobStatus.FAILED
            job.last_error = f"No handler registered for job type: {job.job_type}"
            job.completed_at = datetime.utcnow()
            logger.error(f"No handler for job {job.job_id} of type {job.job_type}")
            return
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.attempts += 1
        
        # Create and start job task
        task = asyncio.create_task(self._execute_job(job))
        self.running_jobs[job.job_id] = task
        
        logger.info(f"Started job {job.job_id} (attempt {job.attempts})")
    
    async def _execute_job(self, job: Job):
        """Execute a job with timeout and error handling."""
        try:
            handler = self.job_handlers[job.job_type]
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(job.payload),
                timeout=job.timeout
            )
            
            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except asyncio.TimeoutError:
            job.last_error = f"Job timed out after {job.timeout} seconds"
            await self._handle_job_failure(job)
            
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            logger.info(f"Job {job.job_id} was cancelled")
            
        except Exception as e:
            job.last_error = str(e)
            await self._handle_job_failure(job)
            
        finally:
            # Remove from running jobs
            if job.job_id in self.running_jobs:
                del self.running_jobs[job.job_id]
    
    async def _handle_job_failure(self, job: Job):
        """Handle job failure and retry logic."""
        logger.error(f"Job {job.job_id} failed: {job.last_error}")
        
        if job.attempts < job.max_retries:
            # Schedule retry
            job.status = JobStatus.RETRYING
            job.scheduled_at = datetime.utcnow() + timedelta(seconds=job.retry_delay)
            logger.info(f"Job {job.job_id} will retry in {job.retry_delay} seconds")
        else:
            # Max retries exceeded
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            logger.error(f"Job {job.job_id} failed permanently after {job.attempts} attempts")
    
    async def _cleanup_completed_jobs(self):
        """Clean up old completed jobs."""
        cutoff_time = datetime.utcnow() - timedelta(days=7)  # Keep jobs for 7 days
        
        jobs_to_remove = []
        for job_id, job in self.jobs.items():
            if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                job.completed_at and job.completed_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            logger.debug(f"Cleaned up old job {job_id}")


# Global scheduler instance
scheduler = JobScheduler()
