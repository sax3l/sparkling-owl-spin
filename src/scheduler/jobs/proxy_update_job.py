"""
Proxy Update Job Implementation
===============================

Implementation of proxy pool update jobs for the ECaDP scheduler.
Handles periodic proxy pool maintenance, health checking, and optimization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json

from src.proxy_pool.manager import ProxyPoolManager
from src.proxy_pool.health_checker import ProxyHealthChecker
from src.proxy_pool.validator import ProxyValidator
from src.database.connection import DatabaseManager
from src.webhooks.client import WebhookClient

logger = logging.getLogger(__name__)

@dataclass
class ProxyUpdateJobConfig:
    """Configuration for proxy update jobs"""
    update_sources: bool = True
    validate_existing: bool = True
    remove_dead_proxies: bool = True
    fetch_new_proxies: bool = True
    max_concurrent_checks: int = 20
    health_check_timeout: int = 10
    validation_timeout: int = 15
    min_proxy_count: int = 50
    max_proxy_count: int = 1000
    quality_threshold: float = 0.7
    webhook_url: Optional[str] = None
    report_path: str = "data/reports/proxy_updates"

@dataclass
class ProxyUpdateJobResult:
    """Result of a proxy update job execution"""
    job_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    proxies_before: int = 0
    proxies_after: int = 0
    proxies_added: int = 0
    proxies_removed: int = 0
    proxies_validated: int = 0
    errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProxyUpdateJob:
    """
    Proxy update job implementation for ECaDP scheduler
    
    Handles periodic maintenance of the proxy pool including:
    - Fetching new proxies from sources
    - Validating existing proxies
    - Removing dead/low-quality proxies
    - Health monitoring and optimization
    """
    
    def __init__(self, config: Union[ProxyUpdateJobConfig, Dict[str, Any]], job_id: Optional[str] = None):
        if isinstance(config, dict):
            self.config = ProxyUpdateJobConfig(**config)
        else:
            self.config = config
            
        self.job_id = job_id or f"proxy_update_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Components
        self.proxy_manager = None
        self.health_checker = None
        self.validator = None
        self.db_manager = None
        self.webhook_client = None
        
        # Execution state
        self.result = ProxyUpdateJobResult(
            job_id=self.job_id,
            status="pending",
            start_time=datetime.utcnow()
        )
    
    async def initialize(self):
        """Initialize job components"""
        try:
            logger.info(f"Initializing proxy update job {self.job_id}")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Initialize proxy pool manager
            self.proxy_manager = ProxyPoolManager()
            await self.proxy_manager.initialize()
            
            # Initialize health checker
            self.health_checker = ProxyHealthChecker(
                max_concurrent=self.config.max_concurrent_checks,
                timeout=self.config.health_check_timeout
            )
            
            # Initialize validator
            self.validator = ProxyValidator(
                timeout=self.config.validation_timeout
            )
            
            # Initialize webhook client if configured
            if self.config.webhook_url:
                self.webhook_client = WebhookClient(self.config.webhook_url)
            
            # Get initial proxy count
            self.result.proxies_before = await self.proxy_manager.get_total_count()
            
            logger.info(f"Proxy update job {self.job_id} initialized successfully")
            logger.info(f"Starting with {self.result.proxies_before} proxies")
            
        except Exception as e:
            logger.error(f"Failed to initialize proxy update job {self.job_id}: {e}")
            self.result.status = "failed"
            self.result.errors.append(f"Initialization failed: {str(e)}")
            raise
    
    async def update_proxy_sources(self):
        """Update proxy pool from external sources"""
        try:
            if not self.config.update_sources:
                logger.info("Proxy source update disabled")
                return
            
            logger.info(f"Updating proxy sources for job {self.job_id}")
            
            # Get current proxy count
            current_count = await self.proxy_manager.get_active_count()
            
            # Determine how many new proxies to fetch
            needed_proxies = max(0, self.config.min_proxy_count - current_count)
            max_fetch = self.config.max_proxy_count - current_count
            fetch_count = min(needed_proxies + 50, max_fetch)  # Add buffer
            
            if fetch_count <= 0:
                logger.info("Sufficient proxies available, skipping source update")
                return
            
            logger.info(f"Fetching up to {fetch_count} new proxies")
            
            # Fetch new proxies
            new_proxies = await self.proxy_manager.fetch_new_proxies(fetch_count)
            
            if new_proxies:
                # Validate new proxies
                validated_proxies = await self._validate_proxies(new_proxies)
                
                # Add validated proxies to pool
                added_count = await self.proxy_manager.add_proxies(validated_proxies)
                self.result.proxies_added = added_count
                
                logger.info(f"Added {added_count} new validated proxies")
            else:
                logger.warning("No new proxies fetched from sources")
                
        except Exception as e:
            error_msg = f"Failed to update proxy sources: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def validate_existing_proxies(self):
        """Validate existing proxies in the pool"""
        try:
            if not self.config.validate_existing:
                logger.info("Existing proxy validation disabled")
                return
            
            logger.info(f"Validating existing proxies for job {self.job_id}")
            
            # Get all proxies for validation
            all_proxies = await self.proxy_manager.get_all_proxies()
            
            if not all_proxies:
                logger.info("No existing proxies to validate")
                return
            
            logger.info(f"Validating {len(all_proxies)} existing proxies")
            
            # Validate proxies in batches
            validated_results = await self._validate_proxies(all_proxies, update_stats=True)
            
            self.result.proxies_validated = len(all_proxies)
            
            # Update proxy statistics
            for proxy, is_valid in zip(all_proxies, validated_results):
                await self.proxy_manager.update_proxy_status(
                    proxy['id'], 
                    'active' if is_valid else 'failed'
                )
            
            valid_count = sum(1 for result in validated_results if result)
            invalid_count = len(validated_results) - valid_count
            
            logger.info(f"Validation completed: {valid_count} valid, {invalid_count} invalid")
            
        except Exception as e:
            error_msg = f"Failed to validate existing proxies: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def remove_dead_proxies(self):
        """Remove dead and low-quality proxies"""
        try:
            if not self.config.remove_dead_proxies:
                logger.info("Dead proxy removal disabled")
                return
            
            logger.info(f"Removing dead proxies for job {self.job_id}")
            
            # Get proxies that should be removed
            removal_criteria = {
                'status': 'failed',
                'quality_score__lt': self.config.quality_threshold,
                'last_success__lt': datetime.utcnow() - timedelta(hours=24)
            }
            
            dead_proxies = await self.proxy_manager.get_proxies_by_criteria(removal_criteria)
            
            if not dead_proxies:
                logger.info("No dead proxies found for removal")
                return
            
            logger.info(f"Removing {len(dead_proxies)} dead proxies")
            
            # Remove dead proxies
            removed_count = await self.proxy_manager.remove_proxies([p['id'] for p in dead_proxies])
            self.result.proxies_removed = removed_count
            
            logger.info(f"Removed {removed_count} dead proxies")
            
        except Exception as e:
            error_msg = f"Failed to remove dead proxies: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def _validate_proxies(self, proxies: List[Dict[str, Any]], update_stats: bool = False) -> List[bool]:
        """Validate a list of proxies"""
        try:
            if not proxies:
                return []
            
            logger.info(f"Validating {len(proxies)} proxies")
            
            # Create validation tasks
            semaphore = asyncio.Semaphore(self.config.max_concurrent_checks)
            tasks = []
            
            for proxy in proxies:
                task = asyncio.create_task(
                    self._validate_single_proxy(semaphore, proxy, update_stats)
                )
                tasks.append(task)
            
            # Execute validation tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            validation_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Validation error for proxy {proxies[i]}: {result}")
                    validation_results.append(False)
                else:
                    validation_results.append(result)
            
            valid_count = sum(1 for result in validation_results if result)
            logger.info(f"Validation completed: {valid_count}/{len(proxies)} proxies valid")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Proxy validation failed: {e}")
            return [False] * len(proxies)
    
    async def _validate_single_proxy(self, semaphore: asyncio.Semaphore, proxy: Dict[str, Any], update_stats: bool = False) -> bool:
        """Validate a single proxy"""
        async with semaphore:
            try:
                # Perform validation
                is_valid = await self.validator.validate_proxy(proxy)
                
                # Update statistics if requested
                if update_stats and self.proxy_manager:
                    if is_valid:
                        await self.proxy_manager.record_success(proxy['id'])
                    else:
                        await self.proxy_manager.record_failure(proxy['id'])
                
                return is_valid
                
            except Exception as e:
                logger.error(f"Error validating proxy {proxy}: {e}")
                return False
    
    async def perform_health_checks(self):
        """Perform comprehensive health checks on the proxy pool"""
        try:
            logger.info(f"Performing health checks for job {self.job_id}")
            
            # Get health statistics
            health_stats = await self.proxy_manager.get_health_statistics()
            
            # Update result statistics
            self.result.statistics.update({
                'health_stats': health_stats,
                'total_proxies': await self.proxy_manager.get_total_count(),
                'active_proxies': await self.proxy_manager.get_active_count(),
                'failed_proxies': await self.proxy_manager.get_failed_count(),
                'average_response_time': health_stats.get('avg_response_time', 0),
                'success_rate': health_stats.get('success_rate', 0)
            })
            
            # Check if proxy pool meets minimum requirements
            active_count = await self.proxy_manager.get_active_count()
            if active_count < self.config.min_proxy_count:
                warning_msg = f"Proxy pool below minimum threshold: {active_count} < {self.config.min_proxy_count}"
                logger.warning(warning_msg)
                self.result.errors.append(warning_msg)
            
            logger.info("Health checks completed")
            
        except Exception as e:
            error_msg = f"Health check failed: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def optimize_proxy_pool(self):
        """Optimize proxy pool for better performance"""
        try:
            logger.info(f"Optimizing proxy pool for job {self.job_id}")
            
            # Rebalance proxy priorities based on performance
            await self.proxy_manager.rebalance_priorities()
            
            # Update proxy quality scores
            await self.proxy_manager.update_quality_scores()
            
            # Clean up old metrics
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            await self.proxy_manager.cleanup_old_metrics(cutoff_date)
            
            logger.info("Proxy pool optimization completed")
            
        except Exception as e:
            error_msg = f"Proxy pool optimization failed: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def generate_report(self):
        """Generate proxy update job report"""
        try:
            logger.info(f"Generating report for proxy update job {self.job_id}")
            
            # Update final statistics
            self.result.proxies_after = await self.proxy_manager.get_total_count()
            
            self.result.statistics.update({
                'proxies_before': self.result.proxies_before,
                'proxies_after': self.result.proxies_after,
                'proxies_added': self.result.proxies_added,
                'proxies_removed': self.result.proxies_removed,
                'proxies_validated': self.result.proxies_validated,
                'net_change': self.result.proxies_after - self.result.proxies_before,
                'error_count': len(self.result.errors),
                'runtime_seconds': (datetime.utcnow() - self.result.start_time).total_seconds()
            })
            
            # Create report directory
            report_dir = Path(self.config.report_path) / self.job_id
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate JSON report
            report_path = report_dir / "report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'job_id': self.result.job_id,
                    'status': self.result.status,
                    'start_time': self.result.start_time.isoformat(),
                    'end_time': self.result.end_time.isoformat() if self.result.end_time else None,
                    'statistics': self.result.statistics,
                    'errors': self.result.errors,
                    'config': {
                        'update_sources': self.config.update_sources,
                        'validate_existing': self.config.validate_existing,
                        'remove_dead_proxies': self.config.remove_dead_proxies,
                        'min_proxy_count': self.config.min_proxy_count,
                        'max_proxy_count': self.config.max_proxy_count,
                        'quality_threshold': self.config.quality_threshold
                    }
                }, f, indent=2)
            
            logger.info(f"Report generated for job {self.job_id}: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report for job {self.job_id}: {e}")
    
    async def send_notifications(self):
        """Send job completion notifications"""
        try:
            if self.webhook_client:
                notification_data = {
                    'job_id': self.result.job_id,
                    'status': self.result.status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'statistics': self.result.statistics,
                    'summary': {
                        'proxies_before': self.result.proxies_before,
                        'proxies_after': self.result.proxies_after,
                        'net_change': self.result.proxies_after - self.result.proxies_before,
                        'errors': len(self.result.errors)
                    }
                }
                
                event_type = f"proxy_update_job.{self.result.status}"
                await self.webhook_client.send_event(event_type, notification_data)
                
                logger.info(f"Sent notification for job {self.job_id}")
                
        except Exception as e:
            logger.error(f"Failed to send notifications for job {self.job_id}: {e}")
    
    async def cleanup(self):
        """Clean up job resources"""
        try:
            logger.info(f"Cleaning up proxy update job {self.job_id}")
            
            if self.db_manager:
                await self.db_manager.close()
            
            if self.proxy_manager:
                await self.proxy_manager.cleanup()
            
            logger.info(f"Cleanup completed for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup for job {self.job_id}: {e}")
    
    async def execute(self) -> ProxyUpdateJobResult:
        """
        Execute the proxy update job
        
        Returns:
            ProxyUpdateJobResult: Result of the job execution
        """
        try:
            logger.info(f"Starting execution of proxy update job {self.job_id}")
            self.result.status = "running"
            self.result.start_time = datetime.utcnow()
            
            # Initialize components
            await self.initialize()
            
            # Execute update operations
            await self.update_proxy_sources()
            await self.validate_existing_proxies()
            await self.remove_dead_proxies()
            await self.perform_health_checks()
            await self.optimize_proxy_pool()
            
            # Mark as completed
            self.result.status = "completed"
            self.result.end_time = datetime.utcnow()
            
            # Generate report
            await self.generate_report()
            
            # Send notifications
            await self.send_notifications()
            
            logger.info(f"Proxy update job {self.job_id} completed successfully")
            logger.info(f"Statistics: {self.result.statistics}")
            
            return self.result
            
        except Exception as e:
            logger.error(f"Proxy update job {self.job_id} failed: {e}")
            
            self.result.status = "failed"
            self.result.end_time = datetime.utcnow()
            self.result.errors.append(f"Job execution failed: {str(e)}")
            
            # Try to generate report even for failed jobs
            try:
                await self.generate_report()
                await self.send_notifications()
            except Exception as report_error:
                logger.error(f"Failed to generate failure report: {report_error}")
            
            return self.result
            
        finally:
            # Always cleanup
            try:
                await self.cleanup()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")

# Convenience functions for common job patterns

async def create_maintenance_update_job(**kwargs) -> ProxyUpdateJob:
    """Create a standard maintenance proxy update job"""
    config = ProxyUpdateJobConfig(
        update_sources=True,
        validate_existing=True,
        remove_dead_proxies=True,
        fetch_new_proxies=True,
        **kwargs
    )
    return ProxyUpdateJob(config)

async def create_validation_only_job(**kwargs) -> ProxyUpdateJob:
    """Create a validation-only proxy update job"""
    config = ProxyUpdateJobConfig(
        update_sources=False,
        validate_existing=True,
        remove_dead_proxies=False,
        fetch_new_proxies=False,
        **kwargs
    )
    return ProxyUpdateJob(config)

async def create_refresh_job(**kwargs) -> ProxyUpdateJob:
    """Create a proxy refresh job (fetch new + remove dead)"""
    config = ProxyUpdateJobConfig(
        update_sources=True,
        validate_existing=False,
        remove_dead_proxies=True,
        fetch_new_proxies=True,
        **kwargs
    )
    return ProxyUpdateJob(config)
