"""
Scheduler service for managing crawl jobs
Provides distributed task queue management with priority scheduling
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass
from celery import Celery
from redis import Redis

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class JobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class CrawlJob:
    id: str
    name: str
    template_id: str
    target_urls: List[str]
    selectors: Dict[str, Any]
    proxy_config: Dict[str, Any]
    schedule_config: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    priority: JobPriority = JobPriority.NORMAL
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    progress: float = 0.0
    results_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class SchedulerService:
    """Enhanced job scheduler matching Apify's scalability"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url)
        self.celery = Celery('crawler-scheduler', broker=redis_url)
        self.jobs: Dict[str, CrawlJob] = {}
        self.logger = logging.getLogger(__name__)
    
    async def submit_job(self, job: CrawlJob) -> str:
        """Submit job for execution with priority scheduling"""
        self.jobs[job.id] = job
        
        # Store in Redis for persistence
        await self._store_job(job)
        
        # Queue based on priority
        queue_name = f"queue_{job.priority.name.lower()}"
        
        # Schedule immediate or delayed execution
        if job.schedule_config.get('immediate', True):
            self.celery.send_task(
                'crawler.execute_job',
                args=[job.id],
                queue=queue_name
            )
        else:
            # Schedule for later
            schedule_time = job.schedule_config.get('scheduled_time')
            if schedule_time:
                self.celery.send_task(
                    'crawler.execute_job',
                    args=[job.id],
                    eta=schedule_time,
                    queue=queue_name
                )
        
        self.logger.info(f"Job {job.id} submitted to {queue_name}")
        return job.id
    
    async def get_job_status(self, job_id: str) -> Optional[CrawlJob]:
        """Get current job status"""
        return self.jobs.get(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel running job"""
        job = self.jobs.get(job_id)
        if job and job.status in [JobStatus.PENDING, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            await self._store_job(job)
            return True
        return False
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause running job"""
        job = self.jobs.get(job_id)
        if job and job.status == JobStatus.RUNNING:
            job.status = JobStatus.PAUSED
            await self._store_job(job)
            return True
        return False
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume paused job"""
        job = self.jobs.get(job_id)
        if job and job.status == JobStatus.PAUSED:
            job.status = JobStatus.PENDING
            await self._store_job(job)
            
            # Requeue the job
            queue_name = f"queue_{job.priority.name.lower()}"
            self.celery.send_task(
                'crawler.execute_job',
                args=[job.id],
                queue=queue_name
            )
            return True
        return False
    
    async def get_job_stats(self) -> Dict[str, Any]:
        """Get comprehensive job statistics"""
        stats = {
            'total_jobs': len(self.jobs),
            'by_status': {},
            'by_priority': {},
            'active_workers': self._get_active_workers(),
            'queue_sizes': self._get_queue_sizes()
        }
        
        for job in self.jobs.values():
            stats['by_status'][job.status.value] = stats['by_status'].get(job.status.value, 0) + 1
            stats['by_priority'][job.priority.name] = stats['by_priority'].get(job.priority.name, 0) + 1
        
        return stats
    
    async def _store_job(self, job: CrawlJob):
        """Store job in Redis for persistence"""
        job_data = {
            'id': job.id,
            'name': job.name,
            'status': job.status.value,
            'priority': job.priority.value,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'progress': job.progress,
            'results_count': job.results_count,
            'error_message': job.error_message
        }
        self.redis.hset(f"job:{job.id}", mapping=job_data)
    
    def _get_active_workers(self) -> int:
        """Get number of active Celery workers"""
        inspect = self.celery.control.inspect()
        active = inspect.active()
        return len(active) if active else 0
    
    def _get_queue_sizes(self) -> Dict[str, int]:
        """Get queue sizes for different priorities"""
        queues = {}
        for priority in JobPriority:
            queue_name = f"queue_{priority.name.lower()}"
            size = self.redis.llen(queue_name)
            queues[queue_name] = size
        return queues

# Celery tasks
from celery import Celery

@Celery(broker='redis://localhost:6379').task
def execute_job(job_id: str):
    """Execute crawl job"""
    import logging
    from backend.main import get_db
    from src.database.models import Job, JobStatus
    from src.crawler.base_crawler import BaseCrawler
    from sqlalchemy.orm import Session
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting job execution: {job_id}")
    
    try:
        # Get database session
        db: Session = next(get_db())
        
        # Find the job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"error": f"Job {job_id} not found"}
        
        # Update job status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Initialize crawler based on job configuration
        crawler_config = job.configuration or {}
        
        # Create crawler instance
        crawler = BaseCrawler(
            base_url=job.start_urls[0] if job.start_urls else None,
            max_depth=crawler_config.get('max_depth', 3),
            respect_robots=crawler_config.get('respect_robots', True),
            delay=crawler_config.get('delay', 1.0),
            concurrent_requests=crawler_config.get('concurrent_requests', 5)
        )
        
        # Execute crawling
        results = []
        for start_url in job.start_urls:
            try:
                crawl_result = crawler.crawl(start_url)
                results.extend(crawl_result)
            except Exception as e:
                logger.error(f"Error crawling {start_url}: {e}")
                continue
        
        # Update job with results
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.results_count = len(results)
        db.commit()
        
        logger.info(f"Job {job_id} completed successfully with {len(results)} results")
        return {
            "job_id": job_id,
            "status": "completed",
            "results_count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        
        # Update job status to failed
        try:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
        except:
            pass  # Database might be unavailable
        
        return {"error": str(e), "job_id": job_id}
        
    finally:
        try:
            db.close()
        except:
            pass
