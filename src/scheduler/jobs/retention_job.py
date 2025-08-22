"""
Data retention job for managing old data according to retention policies.

Implements automated cleanup of:
- Old crawl data beyond retention period
- Processed exports
- Historical proxy data
- Log files and debug information
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml

from src.database.connection import get_db_connection
from src.observability.metrics import MetricsCollector
from src.utils.logger import get_logger
from src.utils.config_loader import ConfigLoader

logger = get_logger(__name__)

class RetentionJob:
    """Manages data retention across all system components."""
    
    def __init__(self, config_path: str = "config/retention_policy.yml"):
        self.config_path = config_path
        self.metrics = MetricsCollector()
        self.config_loader = ConfigLoader()
        self.retention_policies = self._load_retention_config()
    
    def _load_retention_config(self) -> Dict:
        """Load retention policies using ConfigLoader."""
        try:
            config = self.config_loader.load_config_with_env(self.config_path)
            return config.get('retention', self._default_retention_policies())
        except Exception as e:
            logger.warning(f"Failed to load retention config from {self.config_path}: {e}")
            return self._default_retention_policies()
    
    def _default_retention_policies(self) -> Dict:
        """Default retention policies if config file is missing."""
        return {
            "crawl_data": {"days": 90},
            "exports": {"days": 30},
            "proxy_data": {"days": 7},
            "logs": {"days": 14},
            "failed_requests": {"days": 3}
        }
    
    async def run_retention_cleanup(self) -> Dict[str, int]:
        """Execute retention cleanup for all data types."""
        logger.info("Starting retention cleanup job")
        results = {}
        
        try:
            # Clean up crawl data
            results["crawl_data"] = await self._cleanup_crawl_data()
            
            # Clean up exports
            results["exports"] = await self._cleanup_exports()
            
            # Clean up proxy data
            results["proxy_data"] = await self._cleanup_proxy_data()
            
            # Clean up logs
            results["logs"] = await self._cleanup_logs()
            
            # Clean up failed requests
            results["failed_requests"] = await self._cleanup_failed_requests()
            
            # Record metrics
            total_cleaned = sum(results.values())
            self.metrics.record_gauge("retention_cleaned_items", total_cleaned)
            
            logger.info(f"Retention cleanup completed. Cleaned items: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Retention cleanup failed: {e}")
            self.metrics.record_counter("retention_errors", 1)
            raise
    
    async def _cleanup_crawl_data(self) -> int:
        """Clean up old crawl data."""
        retention_days = self.retention_policies["crawl_data"]["days"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        async with get_db_connection() as conn:
            result = await conn.execute("""
                DELETE FROM crawl_results 
                WHERE created_at < $1
                RETURNING id
            """, cutoff_date)
            
            cleaned_count = len(result)
            logger.info(f"Cleaned {cleaned_count} old crawl records older than {retention_days} days")
            return cleaned_count
    
    async def _cleanup_exports(self) -> int:
        """Clean up old export files."""
        retention_days = self.retention_policies["exports"]["days"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        async with get_db_connection() as conn:
            result = await conn.execute("""
                DELETE FROM export_jobs 
                WHERE created_at < $1 AND status = 'completed'
                RETURNING id
            """, cutoff_date)
            
            cleaned_count = len(result)
            logger.info(f"Cleaned {cleaned_count} old export records")
            return cleaned_count
    
    async def _cleanup_proxy_data(self) -> int:
        """Clean up old proxy performance data."""
        retention_days = self.retention_policies["proxy_data"]["days"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        async with get_db_connection() as conn:
            result = await conn.execute("""
                DELETE FROM proxy_metrics 
                WHERE recorded_at < $1
                RETURNING id
            """, cutoff_date)
            
            cleaned_count = len(result)
            logger.info(f"Cleaned {cleaned_count} old proxy metrics")
            return cleaned_count
    
    async def _cleanup_logs(self) -> int:
        """Clean up old log entries."""
        retention_days = self.retention_policies["logs"]["days"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        async with get_db_connection() as conn:
            result = await conn.execute("""
                DELETE FROM application_logs 
                WHERE created_at < $1 AND level NOT IN ('ERROR', 'CRITICAL')
                RETURNING id
            """, cutoff_date)
            
            cleaned_count = len(result)
            logger.info(f"Cleaned {cleaned_count} old log entries")
            return cleaned_count
    
    async def _cleanup_failed_requests(self) -> int:
        """Clean up old failed request data."""
        retention_days = self.retention_policies["failed_requests"]["days"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        async with get_db_connection() as conn:
            result = await conn.execute("""
                DELETE FROM failed_requests 
                WHERE created_at < $1
                RETURNING id
            """, cutoff_date)
            
            cleaned_count = len(result)
            logger.info(f"Cleaned {cleaned_count} failed request records")
            return cleaned_count

async def run_retention_job():
    """Entry point for retention job execution."""
    job = RetentionJob()
    return await job.run_retention_cleanup()