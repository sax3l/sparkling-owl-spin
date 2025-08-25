"""
Job Service

Business logic for job management including creation, control, and monitoring.
Handles different job types: crawl, scrape, export, DQ, retention, erasure.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.database.manager import DatabaseManager
from src.database.models import Job, JobLog


logger = logging.getLogger(__name__)


class JobService:
    """Service for job operations and business logic."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.job_repo = self.db.job_repository
        self.project_repo = self.db.project_repository
    
    async def create_crawl_job(
        self, 
        project_id: int, 
        plan_id: int,
        config: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        user_id: int = None
    ) -> Job:
        """Create a new crawl job."""
        try:
            job = self.job_repo.create_job(
                job_type="CRAWL",
                project_id=project_id,
                plan_id=plan_id,
                config=config,
                priority=priority
            )
            
            # Log job creation
            self.job_repo.append_job_log(
                job_id=job.id,
                level="INFO",
                message=f"Crawl job created for project {project_id}",
                meta={"user_id": user_id, "plan_id": plan_id}
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create crawl job: {e}")
            raise
    
    async def create_scrape_job(
        self,
        project_id: int,
        template_id: int,
        url_list: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
        priority: int = 5,
        user_id: int = None
    ) -> Job:
        """Create a new scrape job."""
        try:
            scrape_config = config or {}
            if url_list:
                scrape_config["url_list"] = url_list
            
            job = self.job_repo.create_job(
                job_type="SCRAPE",
                project_id=project_id,
                template_id=template_id,
                config=scrape_config,
                priority=priority
            )
            
            self.job_repo.append_job_log(
                job_id=job.id,
                level="INFO",
                message=f"Scrape job created for project {project_id}",
                meta={"user_id": user_id, "template_id": template_id, "url_count": len(url_list) if url_list else 0}
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create scrape job: {e}")
            raise
    
    async def create_export_job(
        self,
        query: Dict[str, Any],
        target: str,
        config: Optional[Dict[str, Any]] = None,
        user_id: int = None
    ) -> Job:
        """Create a new export job."""
        try:
            export_config = config or {}
            export_config.update({
                "query": query,
                "target": target
            })
            
            job = self.job_repo.create_job(
                job_type="EXPORT",
                project_id=1,  # Export jobs don't need a specific project
                config=export_config,
                priority=3  # Lower priority for exports
            )
            
            self.job_repo.append_job_log(
                job_id=job.id,
                level="INFO",
                message=f"Export job created for target {target}",
                meta={"user_id": user_id, "target": target}
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create export job: {e}")
            raise
    
    async def create_dq_job(
        self,
        project_id: int,
        template_id: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None,
        user_id: int = None
    ) -> Job:
        """Create a new data quality job."""
        try:
            job = self.job_repo.create_job(
                job_type="DQ",
                project_id=project_id,
                template_id=template_id,
                config=config,
                priority=2  # Higher priority for DQ
            )
            
            self.job_repo.append_job_log(
                job_id=job.id,
                level="INFO",
                message=f"Data quality job created for project {project_id}",
                meta={"user_id": user_id, "template_id": template_id}
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to create DQ job: {e}")
            raise
    
    async def start_job(self, job_id: int) -> bool:
        """Start job execution."""
        try:
            # Update job status to RUNNING
            success = self.job_repo.update_job_status(
                job_id=job_id,
                status="RUNNING",
                started_at=datetime.utcnow()
            )
            
            if success:
                self.job_repo.append_job_log(
                    job_id=job_id,
                    level="INFO",
                    message="Job started"
                )
                
                # TODO: Send job to worker queue/scheduler
                # For now just log that it would be started
                logger.info(f"Job {job_id} started (would be sent to worker)")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to start job {job_id}: {e}")
            
            # Log failure
            self.job_repo.append_job_log(
                job_id=job_id,
                level="ERROR",
                message=f"Failed to start job: {str(e)}"
            )
            
            # Mark job as failed
            self.job_repo.update_job_status(job_id, "FAILED")
            return False
    
    async def pause_job(self, job_id: int) -> Dict[str, Any]:
        """Pause job execution."""
        try:
            success = self.job_repo.update_job_status(job_id, "PAUSED")
            
            if success:
                self.job_repo.append_job_log(
                    job_id=job_id,
                    level="INFO",
                    message="Job paused"
                )
                
                # TODO: Send pause signal to worker
                logger.info(f"Job {job_id} paused")
            
            return {"success": success, "message": "Job paused"}
            
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def resume_job(self, job_id: int) -> Dict[str, Any]:
        """Resume paused job."""
        try:
            success = self.job_repo.update_job_status(job_id, "RUNNING")
            
            if success:
                self.job_repo.append_job_log(
                    job_id=job_id,
                    level="INFO",
                    message="Job resumed"
                )
                
                # TODO: Send resume signal to worker
                logger.info(f"Job {job_id} resumed")
            
            return {"success": success, "message": "Job resumed"}
            
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def terminate_job(self, job_id: int) -> Dict[str, Any]:
        """Terminate job execution."""
        try:
            success = self.job_repo.update_job_status(
                job_id=job_id, 
                status="TERMINATED",
                finished_at=datetime.utcnow()
            )
            
            if success:
                self.job_repo.append_job_log(
                    job_id=job_id,
                    level="WARN",
                    message="Job terminated by user"
                )
                
                # TODO: Send termination signal to worker
                logger.info(f"Job {job_id} terminated")
            
            return {"success": success, "message": "Job terminated"}
            
        except Exception as e:
            logger.error(f"Failed to terminate job {job_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def scale_job(self, job_id: int, workers: int) -> Dict[str, Any]:
        """Scale job worker count."""
        try:
            # TODO: Implement actual scaling logic
            self.job_repo.append_job_log(
                job_id=job_id,
                level="INFO",
                message=f"Job scaled to {workers} workers"
            )
            
            logger.info(f"Job {job_id} scaled to {workers} workers")
            return {"success": True, "message": f"Job scaled to {workers} workers"}
            
        except Exception as e:
            logger.error(f"Failed to scale job {job_id}: {e}")
            return {"success": False, "message": str(e)}
    
    async def change_proxy_profile(self, job_id: int, proxy_profile: str) -> Dict[str, Any]:
        """Change proxy profile for running job."""
        try:
            # TODO: Implement proxy profile change logic
            self.job_repo.append_job_log(
                job_id=job_id,
                level="INFO",
                message=f"Proxy profile changed to {proxy_profile}"
            )
            
            logger.info(f"Job {job_id} proxy profile changed to {proxy_profile}")
            return {"success": True, "message": f"Proxy profile changed to {proxy_profile}"}
            
        except Exception as e:
            logger.error(f"Failed to change proxy profile for job {job_id}: {e}")
            return {"success": False, "message": str(e)}
