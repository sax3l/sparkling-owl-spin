"""
Production Scheduler for Sparkling Owl Spin Platform
Advanced job scheduling with cron-like functionality, monitoring, and error recovery.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
import heapq
import time

import croniter
import redis.asyncio as redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from .crawl_coordinator import CrawlCoordinator, CrawlConfiguration
from .url_queue import URLQueue
from ..database.crawl_database import CrawlDatabaseService
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ScheduleType(Enum):
    """Types of scheduling supported"""
    ONCE = "once"
    INTERVAL = "interval" 
    CRON = "cron"
    CONTINUOUS = "continuous"

class JobStatus(Enum):
    """Job execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

@dataclass
class ScheduledJob:
    """Represents a scheduled crawling job"""
    id: str
    name: str
    description: str = ""
    
    # Schedule configuration
    schedule_type: ScheduleType = ScheduleType.ONCE
    cron_expression: Optional[str] = None
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
    
    # Monitoring
    webhook_url: Optional[str] = None
    notification_emails: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'schedule_type': self.schedule_type.value,
            'cron_expression': self.cron_expression,
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
            'failure_count': self.failure_count,
            'webhook_url': self.webhook_url,
            'notification_emails': self.notification_emails
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
            cron_expression=data.get('cron_expression'),
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
            failure_count=data.get('failure_count', 0),
            webhook_url=data.get('webhook_url'),
            notification_emails=data.get('notification_emails', [])
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

class CrawlScheduler:
    """
    Production-grade crawler scheduler with advanced features:
    - Cron-like scheduling with multiple triggers
    - Redis-backed job persistence  
    - Automatic retry and error recovery
    - Real-time monitoring and notifications
    - Resource management and concurrency control
    """
    
    def __init__(self,
                 redis_client: redis.Redis,
                 crawl_db_service: CrawlDatabaseService,
                 max_concurrent_jobs: int = 10):
        
        self.redis = redis_client
        self.db_service = crawl_db_service
        self.max_concurrent_jobs = max_concurrent_jobs
        
        # Job storage
        self.jobs_key = "scheduler:jobs"
        self.executions_key = "scheduler:executions"
        self.running_jobs_key = "scheduler:running"
        
        # Scheduler setup
        job_stores = {
            'default': RedisJobStore(
                host=redis_client.connection_pool.connection_kwargs.get('host', 'localhost'),
                port=redis_client.connection_pool.connection_kwargs.get('port', 6379),
                db=redis_client.connection_pool.connection_kwargs.get('db', 0)
            )
        }
        
        executors = {
            'default': AsyncIOExecutor(max_workers=max_concurrent_jobs)
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=job_stores,
            executors=executors
        )
        
        # State tracking
        self.running_jobs: Dict[str, JobExecution] = {}
        self.job_coordinators: Dict[str, CrawlCoordinator] = {}
        
        # Monitoring
        self.stats = {
            'jobs_scheduled': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_execution_time': 0.0,
            'scheduler_start_time': None
        }
        
        logger.info("Crawl scheduler initialized")
    
    async def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.stats['scheduler_start_time'] = datetime.utcnow()
            
            # Schedule periodic maintenance tasks
            await self._schedule_maintenance_tasks()
            
            logger.info("Crawl scheduler started")
    
    async def shutdown(self):
        """Gracefully shutdown the scheduler"""
        logger.info("Shutting down scheduler...")
        
        # Stop accepting new jobs
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        
        # Stop running jobs gracefully
        for coordinator in self.job_coordinators.values():
            await coordinator.stop_crawl()
        
        # Wait for jobs to complete or timeout
        timeout = 30
        start_time = time.time()
        
        while self.running_jobs and (time.time() - start_time) < timeout:
            await asyncio.sleep(1)
        
        # Force stop any remaining jobs
        for execution in self.running_jobs.values():
            execution.status = JobStatus.CANCELLED
        
        logger.info("Scheduler shutdown complete")
    
    async def schedule_job(self, job: ScheduledJob) -> bool:
        """Schedule a new crawling job"""
        try:
            # Store job configuration
            await self.redis.hset(
                self.jobs_key,
                job.id,
                json.dumps(job.to_dict())
            )
            
            # Create appropriate trigger based on schedule type
            trigger = await self._create_trigger(job)
            if not trigger:
                logger.error(f"Failed to create trigger for job {job.id}")
                return False
            
            # Schedule with APScheduler
            self.scheduler.add_job(
                func=self._execute_job,
                trigger=trigger,
                args=[job.id],
                id=job.id,
                name=f"crawl_job_{job.name}",
                max_instances=1,
                coalesce=True,
                misfire_grace_time=300  # 5 minutes
            )
            
            self.stats['jobs_scheduled'] += 1
            logger.info(f"Scheduled job {job.id}: {job.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule job {job.id}: {e}")
            return False
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        try:
            # Remove from scheduler
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            
            # Update job status
            await self._update_job_status(job_id, JobStatus.CANCELLED)
            
            # Stop if currently running
            if job_id in self.running_jobs:
                if job_id in self.job_coordinators:
                    await self.job_coordinators[job_id].stop_crawl()
                
                self.running_jobs[job_id].status = JobStatus.CANCELLED
                del self.running_jobs[job_id]
            
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
    
    async def get_job_executions(self, job_id: str, limit: int = 50) -> List[JobExecution]:
        """Get execution history for a job"""
        executions = []
        
        # Get executions from Redis
        execution_keys = await self.redis.lrange(f"{self.executions_key}:{job_id}", 0, limit-1)
        
        for key in execution_keys:
            execution_data = await self.redis.get(key)
            if execution_data:
                data = json.loads(execution_data)
                execution = JobExecution(
                    job_id=data['job_id'],
                    execution_id=data['execution_id'],
                    started_at=datetime.fromisoformat(data['started_at']),
                    completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                    status=JobStatus(data['status']),
                    crawl_id=data.get('crawl_id'),
                    error_message=data.get('error_message'),
                    pages_crawled=data.get('pages_crawled', 0),
                    execution_time_seconds=data.get('execution_time_seconds', 0.0),
                    retry_count=data.get('retry_count', 0)
                )
                executions.append(execution)
        
        return executions
    
    async def _create_trigger(self, job: ScheduledJob):
        """Create APScheduler trigger based on job schedule type"""
        try:
            if job.schedule_type == ScheduleType.ONCE:
                return DateTrigger(run_date=job.start_date or datetime.utcnow())
            
            elif job.schedule_type == ScheduleType.INTERVAL:
                return IntervalTrigger(
                    seconds=job.interval_seconds,
                    start_date=job.start_date,
                    end_date=job.end_date
                )
            
            elif job.schedule_type == ScheduleType.CRON:
                return CronTrigger.from_crontab(
                    job.cron_expression,
                    start_date=job.start_date,
                    end_date=job.end_date
                )
            
            elif job.schedule_type == ScheduleType.CONTINUOUS:
                # Continuous jobs restart immediately after completion
                return IntervalTrigger(seconds=30)  # Small delay between runs
            
            else:
                logger.error(f"Unknown schedule type: {job.schedule_type}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create trigger for job {job.id}: {e}")
            return None
    
    async def _execute_job(self, job_id: str):
        """Execute a scheduled crawling job"""
        execution_id = f"{job_id}_{int(time.time())}"
        
        # Check concurrent job limit
        if len(self.running_jobs) >= self.max_concurrent_jobs:
            logger.warning(f"Max concurrent jobs reached, skipping {job_id}")
            return
        
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
            await self._update_job_status(job_id, JobStatus.RUNNING)
            
            # Create crawl coordinator
            crawl_config = CrawlConfiguration(**job.crawl_config)
            url_queue = URLQueue(self.redis, f"job_{job_id}")
            
            coordinator = CrawlCoordinator(crawl_config, url_queue)
            self.job_coordinators[job_id] = coordinator
            
            # Start crawling
            crawl_id = await coordinator.start_crawl(job.start_urls)
            execution.crawl_id = crawl_id
            
            # Wait for completion or timeout
            timeout_seconds = job.timeout_minutes * 60
            start_time = time.time()
            
            while coordinator.is_running:
                elapsed = time.time() - start_time
                
                if elapsed > timeout_seconds:
                    logger.warning(f"Job {job_id} timed out after {timeout_seconds} seconds")
                    await coordinator.stop_crawl()
                    execution.status = JobStatus.FAILED
                    execution.error_message = "Job timed out"
                    break
                
                await asyncio.sleep(5)  # Check every 5 seconds
            
            # Get final stats
            if execution.status != JobStatus.FAILED:
                status = await coordinator.get_crawl_status()
                execution.pages_crawled = status['stats']['total_crawled']
                execution.status = JobStatus.COMPLETED
            
            execution.completed_at = datetime.utcnow()
            execution.execution_time_seconds = (execution.completed_at - execution.started_at).total_seconds()
            
            # Update job statistics
            job.run_count += 1
            job.last_run = execution.started_at
            
            if execution.status == JobStatus.COMPLETED:
                job.success_count += 1
                self.stats['jobs_completed'] += 1
            else:
                job.failure_count += 1
                self.stats['jobs_failed'] += 1
            
            # Calculate next run for recurring jobs
            if job.schedule_type in [ScheduleType.INTERVAL, ScheduleType.CRON, ScheduleType.CONTINUOUS]:
                job.next_run = self._calculate_next_run(job)
            
            await self._save_job_execution(execution)
            await self._update_job_status(job_id, JobStatus.PENDING if job.next_run else JobStatus.COMPLETED)
            
        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            execution.status = JobStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            # Handle retries
            if execution.retry_count < job.max_retries:
                execution.retry_count += 1
                
                # Schedule retry
                retry_time = datetime.utcnow() + timedelta(seconds=job.retry_delay)
                self.scheduler.add_job(
                    func=self._execute_job,
                    trigger=DateTrigger(run_date=retry_time),
                    args=[job_id],
                    id=f"{job_id}_retry_{execution.retry_count}"
                )
                
                logger.info(f"Scheduled retry {execution.retry_count} for job {job_id}")
            
            await self._save_job_execution(execution)
            
        finally:
            # Cleanup
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            
            if job_id in self.job_coordinators:
                await self.job_coordinators[job_id].close()
                del self.job_coordinators[job_id]
            
            logger.info(f"Execution {execution_id} completed with status: {execution.status.value}")
    
    def _calculate_next_run(self, job: ScheduledJob) -> Optional[datetime]:
        """Calculate next run time for recurring jobs"""
        try:
            if job.schedule_type == ScheduleType.INTERVAL and job.interval_seconds:
                return datetime.utcnow() + timedelta(seconds=job.interval_seconds)
            
            elif job.schedule_type == ScheduleType.CRON and job.cron_expression:
                cron = croniter.croniter(job.cron_expression, datetime.utcnow())
                return cron.get_next(datetime)
            
            elif job.schedule_type == ScheduleType.CONTINUOUS:
                return datetime.utcnow() + timedelta(seconds=30)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate next run for job {job.id}: {e}")
            return None
    
    async def _update_job_status(self, job_id: str, status: JobStatus):
        """Update job status in storage"""
        job = await self.get_job(job_id)
        if job:
            job.status = status
            
            await self.redis.hset(
                self.jobs_key,
                job_id,
                json.dumps(job.to_dict())
            )
    
    async def _save_job_execution(self, execution: JobExecution):
        """Save job execution to storage"""
        execution_key = f"execution:{execution.execution_id}"
        
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
        
        # Store execution data
        await self.redis.setex(
            execution_key,
            86400 * 30,  # Keep for 30 days
            json.dumps(execution_data)
        )
        
        # Add to job execution list
        await self.redis.lpush(f"{self.executions_key}:{execution.job_id}", execution_key)
        await self.redis.ltrim(f"{self.executions_key}:{execution.job_id}", 0, 99)  # Keep last 100
    
    async def _schedule_maintenance_tasks(self):
        """Schedule periodic maintenance tasks"""
        # Clean up old executions
        self.scheduler.add_job(
            func=self._cleanup_old_executions,
            trigger=CronTrigger(hour=2, minute=0),  # Daily at 2 AM
            id="maintenance_cleanup",
            name="Cleanup old executions"
        )
        
        # Update job statistics
        self.scheduler.add_job(
            func=self._update_job_statistics,
            trigger=IntervalTrigger(minutes=5),
            id="maintenance_stats",
            name="Update job statistics"
        )
    
    async def _cleanup_old_executions(self):
        """Clean up old execution records"""
        logger.info("Running maintenance: cleaning up old executions")
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # This would clean up old execution records
        # Implementation depends on specific storage requirements
        
    async def _update_job_statistics(self):
        """Update scheduler statistics"""
        self.stats['total_execution_time'] = sum(
            exec.execution_time_seconds 
            for exec in self.running_jobs.values() 
            if exec.execution_time_seconds > 0
        )
    
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
async def create_scheduler(redis_client: redis.Redis, 
                          crawl_db_service: CrawlDatabaseService,
                          max_concurrent_jobs: int = 10) -> CrawlScheduler:
    """Create and start a crawl scheduler"""
    scheduler = CrawlScheduler(redis_client, crawl_db_service, max_concurrent_jobs)
    await scheduler.start()
    return scheduler

def create_job_from_config(name: str, 
                          start_urls: List[str],
                          schedule_config: Dict[str, Any],
                          crawl_config: Dict[str, Any]) -> ScheduledJob:
    """Create a scheduled job from configuration"""
    
    job_id = f"job_{int(time.time())}_{hash(name) % 10000}"
    
    # Parse schedule configuration
    schedule_type = ScheduleType(schedule_config.get('type', 'once'))
    
    job = ScheduledJob(
        id=job_id,
        name=name,
        start_urls=start_urls,
        crawl_config=crawl_config,
        schedule_type=schedule_type
    )
    
    if schedule_type == ScheduleType.CRON:
        job.cron_expression = schedule_config.get('cron_expression')
    elif schedule_type == ScheduleType.INTERVAL:
        job.interval_seconds = schedule_config.get('interval_seconds', 3600)
    elif schedule_type == ScheduleType.ONCE:
        start_date = schedule_config.get('start_date')
        if start_date:
            job.start_date = datetime.fromisoformat(start_date)
    
    return job
