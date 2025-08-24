"""
Built-in Crawler Scheduler
Simple but robust scheduler implementation without external dependencies.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import heapq
import threading
from concurrent.futures import ThreadPoolExecutor

import redis.asyncio as redis

from ..utils.logger import get_logger

logger = get_logger(__name__)

class ScheduleType(Enum):
    """Types of scheduling supported"""
    ONCE = "once"
    INTERVAL = "interval" 
    CONTINUOUS = "continuous"

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ScheduledJob:
    """Represents a scheduled crawling job"""
    id: str
    name: str
    description: str = ""
    
    # Schedule configuration
    schedule_type: ScheduleType = ScheduleType.ONCE
    interval_seconds: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Crawl configuration
    start_urls: List[str] = field(default_factory=list)
    crawl_config: Dict[str, Any] = field(default_factory=dict)
    
    # Execution settings
    max_retries: int = 3
    retry_delay: int = 300  # 5 minutes
    timeout_minutes: int = 480  # 8 hours
    
    # Status and metadata
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'schedule_type': self.schedule_type.value,
            'interval_seconds': self.interval_seconds,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'start_urls': self.start_urls,
            'crawl_config': self.crawl_config,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'timeout_minutes': self.timeout_minutes,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledJob':
        """Create from dictionary"""
        # Parse datetime fields
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        last_run = datetime.fromisoformat(data['last_run']) if data.get('last_run') else None
        next_run = datetime.fromisoformat(data['next_run']) if data.get('next_run') else None
        start_date = datetime.fromisoformat(data['start_date']) if data.get('start_date') else None
        end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
        
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            schedule_type=ScheduleType(data.get('schedule_type', 'once')),
            interval_seconds=data.get('interval_seconds'),
            start_date=start_date,
            end_date=end_date,
            start_urls=data.get('start_urls', []),
            crawl_config=data.get('crawl_config', {}),
            max_retries=data.get('max_retries', 3),
            retry_delay=data.get('retry_delay', 300),
            timeout_minutes=data.get('timeout_minutes', 480),
            status=JobStatus(data.get('status', 'pending')),
            created_at=created_at,
            last_run=last_run,
            next_run=next_run,
            run_count=data.get('run_count', 0),
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0)
        )

@dataclass
class JobExecution:
    """Represents a single job execution"""
    job_id: str
    execution_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.RUNNING
    crawl_id: Optional[str] = None
    error_message: Optional[str] = None
    pages_crawled: int = 0
    execution_time_seconds: float = 0.0
    retry_count: int = 0

class SimpleScheduler:
    """
    Simple but robust crawler scheduler.
    
    Features:
    - Redis-backed job persistence
    - Interval and one-time scheduling
    - Basic retry logic
    - Concurrent job execution
    """
    
    def __init__(self,
                 redis_client: redis.Redis,
                 max_concurrent_jobs: int = 10):
        
        self.redis = redis_client
        self.max_concurrent_jobs = max_concurrent_jobs
        
        # Job storage keys
        self.jobs_key = "scheduler:jobs"
        self.executions_key = "scheduler:executions"
        self.next_jobs_key = "scheduler:next_jobs"  # Priority queue for next jobs
        
        # State tracking
        self.running_jobs: Dict[str, JobExecution] = {}
        self.is_running = False
        
        # Statistics
        self.stats = {
            'jobs_scheduled': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'scheduler_start_time': None
        }
        
        logger.info("Simple scheduler initialized")
    
    async def start(self):
        """Start the scheduler"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stats['scheduler_start_time'] = datetime.utcnow()
        
        # Start the scheduler loop
        asyncio.create_task(self._scheduler_loop())
        
        logger.info("Simple scheduler started")
    
    async def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        
        # Wait for running jobs to complete (with timeout)
        timeout = 30
        start_time = time.time()
        
        while self.running_jobs and (time.time() - start_time) < timeout:
            await asyncio.sleep(1)
        
        logger.info("Simple scheduler stopped")
    
    async def schedule_job(self, job: ScheduledJob) -> bool:
        """Schedule a new crawling job"""
        try:
            # Calculate next run time
            next_run = self._calculate_next_run(job)
            job.next_run = next_run
            
            # Store job configuration
            await self.redis.hset(
                self.jobs_key,
                job.id,
                json.dumps(job.to_dict())
            )
            
            # Add to priority queue if has next run
            if next_run:
                score = next_run.timestamp()
                await self.redis.zadd(self.next_jobs_key, {job.id: score})
            
            self.stats['jobs_scheduled'] += 1
            logger.info(f"Scheduled job {job.id}: {job.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule job {job.id}: {e}")
            return False
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        try:
            # Remove from next jobs queue
            await self.redis.zrem(self.next_jobs_key, job_id)
            
            # Update job status
            job = await self.get_job(job_id)
            if job:
                job.status = JobStatus.CANCELLED
                await self.redis.hset(
                    self.jobs_key,
                    job_id,
                    json.dumps(job.to_dict())
                )
            
            # Stop if currently running
            if job_id in self.running_jobs:
                self.running_jobs[job_id].status = JobStatus.CANCELLED
            
            logger.info(f"Cancelled job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    async def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """Get a scheduled job by ID"""
        job_data = await self.redis.hget(self.jobs_key, job_id)
        if job_data:
            return ScheduledJob.from_dict(json.loads(job_data))
        return None
    
    async def list_jobs(self, status_filter: Optional[JobStatus] = None) -> List[ScheduledJob]:
        """List all scheduled jobs with optional status filter"""
        jobs = []
        
        all_jobs = await self.redis.hgetall(self.jobs_key)
        for job_data in all_jobs.values():
            job = ScheduledJob.from_dict(json.loads(job_data))
            
            if status_filter is None or job.status == status_filter:
                jobs.append(job)
        
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                # Check for jobs that need to run
                await self._check_and_run_due_jobs()
                
                # Clean up completed executions
                await self._cleanup_completed_jobs()
                
                # Sleep for a bit before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(30)  # Longer sleep on error
    
    async def _check_and_run_due_jobs(self):
        """Check for and run jobs that are due"""
        current_time = datetime.utcnow()
        
        # Get jobs due to run (score <= current timestamp)
        due_jobs = await self.redis.zrangebyscore(
            self.next_jobs_key,
            0,
            current_time.timestamp(),
            withscores=True
        )
        
        for job_id, score in due_jobs:
            # Skip if already running or at max capacity
            if job_id in self.running_jobs or len(self.running_jobs) >= self.max_concurrent_jobs:
                continue
            
            # Remove from queue and run
            await self.redis.zrem(self.next_jobs_key, job_id)
            asyncio.create_task(self._execute_job(job_id))
    
    async def _execute_job(self, job_id: str):
        """Execute a scheduled crawling job"""
        execution_id = f"{job_id}_{int(time.time())}"
        
        # Get job configuration
        job = await self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Create execution record
        execution = JobExecution(
            job_id=job_id,
            execution_id=execution_id,
            started_at=datetime.utcnow()
        )
        
        self.running_jobs[job_id] = execution
        
        try:
            logger.info(f"Starting execution {execution_id} for job {job.name}")
            
            # Update job status
            job.status = JobStatus.RUNNING
            await self._save_job(job)
            
            # Execute the crawl (placeholder - would integrate with actual crawler)
            await self._run_crawl(job, execution)
            
            # Mark as completed
            execution.status = JobStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.execution_time_seconds = (execution.completed_at - execution.started_at).total_seconds()
            
            # Update job statistics
            job.run_count += 1
            job.last_run = execution.started_at
            job.success_count += 1
            
            # Schedule next run if recurring
            if job.schedule_type in [ScheduleType.INTERVAL, ScheduleType.CONTINUOUS]:
                next_run = self._calculate_next_run(job)
                if next_run:
                    job.next_run = next_run
                    job.status = JobStatus.PENDING
                    await self.redis.zadd(self.next_jobs_key, {job.id: next_run.timestamp()})
                else:
                    job.status = JobStatus.COMPLETED
            else:
                job.status = JobStatus.COMPLETED
            
            self.stats['jobs_completed'] += 1
            
        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            execution.status = JobStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            job.failure_count += 1
            self.stats['jobs_failed'] += 1
            
            # Handle retries
            if execution.retry_count < job.max_retries:
                retry_time = datetime.utcnow() + timedelta(seconds=job.retry_delay)
                await self.redis.zadd(self.next_jobs_key, {job.id: retry_time.timestamp()})
                execution.retry_count += 1
                job.status = JobStatus.PENDING
                logger.info(f"Scheduled retry {execution.retry_count} for job {job_id}")
            else:
                job.status = JobStatus.FAILED
        
        finally:
            # Save job and execution
            await self._save_job(job)
            await self._save_execution(execution)
            
            # Cleanup
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            
            logger.info(f"Execution {execution_id} completed with status: {execution.status.value}")
    
    async def _run_crawl(self, job: ScheduledJob, execution: JobExecution):
        """Run the actual crawl (placeholder implementation)"""
        # This would integrate with the actual crawler
        # For now, simulate crawling
        
        logger.info(f"Simulating crawl for {job.name} with {len(job.start_urls)} URLs")
        
        # Simulate crawling time
        crawl_time = min(60, job.timeout_minutes * 60)  # Max 1 minute simulation
        await asyncio.sleep(crawl_time)
        
        # Simulate results
        execution.pages_crawled = len(job.start_urls) * 10  # Pretend we found 10 pages per start URL
        execution.crawl_id = f"crawl_{execution.execution_id}"
        
        logger.info(f"Simulated crawl completed: {execution.pages_crawled} pages")
    
    def _calculate_next_run(self, job: ScheduledJob) -> Optional[datetime]:
        """Calculate next run time for a job"""
        current_time = datetime.utcnow()
        
        if job.schedule_type == ScheduleType.ONCE:
            return job.start_date or current_time
        
        elif job.schedule_type == ScheduleType.INTERVAL and job.interval_seconds:
            if job.last_run:
                return job.last_run + timedelta(seconds=job.interval_seconds)
            else:
                return job.start_date or current_time
        
        elif job.schedule_type == ScheduleType.CONTINUOUS:
            # Continuous jobs restart immediately after completion
            return current_time + timedelta(seconds=30)
        
        return None
    
    async def _save_job(self, job: ScheduledJob):
        """Save job to Redis"""
        await self.redis.hset(
            self.jobs_key,
            job.id,
            json.dumps(job.to_dict())
        )
    
    async def _save_execution(self, execution: JobExecution):
        """Save execution record"""
        execution_data = {
            'job_id': execution.job_id,
            'execution_id': execution.execution_id,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'status': execution.status.value,
            'crawl_id': execution.crawl_id,
            'error_message': execution.error_message,
            'pages_crawled': execution.pages_crawled,
            'execution_time_seconds': execution.execution_time_seconds,
            'retry_count': execution.retry_count
        }
        
        execution_key = f"execution:{execution.execution_id}"
        
        # Store execution data
        await self.redis.setex(
            execution_key,
            86400 * 7,  # Keep for 7 days
            json.dumps(execution_data)
        )
        
        # Add to job execution list
        await self.redis.lpush(f"{self.executions_key}:{execution.job_id}", execution_key)
        await self.redis.ltrim(f"{self.executions_key}:{execution.job_id}", 0, 49)  # Keep last 50
    
    async def _cleanup_completed_jobs(self):
        """Clean up completed job executions periodically"""
        # This could clean up old execution records
        pass
    
    async def get_scheduler_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics"""
        return {
            'jobs_scheduled': self.stats['jobs_scheduled'],
            'jobs_completed': self.stats['jobs_completed'],
            'jobs_failed': self.stats['jobs_failed'],
            'currently_running': len(self.running_jobs),
            'max_concurrent_jobs': self.max_concurrent_jobs,
            'scheduler_uptime_seconds': (
                (datetime.utcnow() - self.stats['scheduler_start_time']).total_seconds()
                if self.stats['scheduler_start_time'] else 0
            )
        }

# Convenience functions
async def create_simple_scheduler(redis_client: redis.Redis, 
                                  max_concurrent_jobs: int = 10) -> SimpleScheduler:
    """Create and start a simple scheduler"""
    scheduler = SimpleScheduler(redis_client, max_concurrent_jobs)
    await scheduler.start()
    return scheduler

def create_simple_job(name: str, 
                      start_urls: List[str],
                      schedule_type: str = "once",
                      interval_seconds: Optional[int] = None,
                      crawl_config: Dict[str, Any] = None) -> ScheduledJob:
    """Create a simple scheduled job"""
    
    job_id = f"job_{int(time.time())}_{hash(name) % 10000}"
    
    return ScheduledJob(
        id=job_id,
        name=name,
        start_urls=start_urls,
        crawl_config=crawl_config or {},
        schedule_type=ScheduleType(schedule_type),
        interval_seconds=interval_seconds
    )
