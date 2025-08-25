"""
Base Job Class

Abstract base class for all job types.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from src.database.manager import DatabaseManager
from src.database.models import Job
from src.utils.logger import get_logger


logger = get_logger(__name__)


class BaseJob(ABC):
    """Base class for all job types."""
    
    def __init__(self, job_id: int, db_manager: DatabaseManager):
        self.job_id = job_id
        self.db_manager = db_manager
        self.started_at: Optional[datetime] = None
        self.is_paused = False
        self.is_terminated = False
        self.timeout = 3600  # Default 1 hour timeout
        
        # Job-specific data loaded from database
        self.job_data: Optional[Job] = None
        self.config: Dict[str, Any] = {}
        
    async def initialize(self):
        """Initialize job with data from database."""
        async with self.db_manager.get_session() as session:
            self.job_data = session.query(Job).filter(Job.id == self.job_id).first()
            
            if not self.job_data:
                raise Exception(f"Job {self.job_id} not found")
            
            self.config = self.job_data.config_json or {}
            self.timeout = self.config.get('timeout', 3600)
    
    async def execute(self):
        """Execute the job."""
        try:
            await self.initialize()
            self.started_at = datetime.utcnow()
            
            logger.info(f"Starting job {self.job_id} ({self.job_data.type})")
            
            # Run the job-specific implementation
            await self.run()
            
            logger.info(f"Job {self.job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {self.job_id} failed: {e}")
            raise
    
    @abstractmethod
    async def run(self):
        """Job-specific execution logic. Must be implemented by subclasses."""
        pass
    
    async def pause(self):
        """Pause job execution."""
        self.is_paused = True
        logger.info(f"Job {self.job_id} paused")
    
    async def resume(self):
        """Resume job execution."""
        self.is_paused = False
        logger.info(f"Job {self.job_id} resumed")
    
    async def terminate(self):
        """Terminate job execution."""
        self.is_terminated = True
        logger.info(f"Job {self.job_id} terminated")
    
    async def is_healthy(self) -> bool:
        """Check if job is healthy and responding."""
        # Default implementation - can be overridden
        return not self.is_terminated
    
    async def get_progress(self) -> Dict[str, Any]:
        """Get job progress information."""
        # Default implementation - should be overridden for jobs that track progress
        return {
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "is_paused": self.is_paused,
            "is_terminated": self.is_terminated
        }
    
    async def log_info(self, message: str, meta: Dict[str, Any] = None):
        """Log info message."""
        await self._log("INFO", message, meta)
    
    async def log_warning(self, message: str, meta: Dict[str, Any] = None):
        """Log warning message."""
        await self._log("WARN", message, meta)
    
    async def log_error(self, message: str, meta: Dict[str, Any] = None):
        """Log error message."""
        await self._log("ERROR", message, meta)
    
    async def _log(self, level: str, message: str, meta: Dict[str, Any] = None):
        """Internal logging method."""
        from src.database.models import JobLog
        
        try:
            async with self.db_manager.get_session() as session:
                log_entry = JobLog(
                    job_id=self.job_id,
                    ts=datetime.utcnow(),
                    level=level,
                    message=message,
                    meta_json=meta or {}
                )
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to log job message: {e}")
    
    def _check_termination(self):
        """Check if job should terminate."""
        if self.is_terminated:
            raise Exception("Job was terminated")
    
    def _check_pause(self):
        """Check if job should pause."""
        while self.is_paused and not self.is_terminated:
            asyncio.sleep(1)
        
        self._check_termination()
    
    async def wait_with_pause_check(self, seconds: float):
        """Wait for specified time while checking for pause/termination."""
        elapsed = 0
        check_interval = 0.1
        
        while elapsed < seconds:
            if self.is_terminated:
                raise Exception("Job was terminated")
            
            if not self.is_paused:
                await asyncio.sleep(min(check_interval, seconds - elapsed))
                elapsed += check_interval
            else:
                await asyncio.sleep(check_interval)
                # Don't increment elapsed time while paused
