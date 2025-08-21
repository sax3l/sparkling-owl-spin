#!/usr/bin/env python3
"""
ECaDP Production Scheduler Service
=================================

Enterprise-grade scheduler orchestration service for the ECaDP platform.
Manages job scheduling, worker coordination, and system orchestration.

Features:
- APScheduler-based job orchestration
- Distributed job management with Redis backend
- Job monitoring and failure recovery
- Dynamic scaling and load balancing
- Health monitoring and alerting
- Integration with Supabase database
- Webhook notifications and event streaming
- Graceful shutdown and job persistence
"""

import asyncio
import argparse
import logging
import signal
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

import yaml
import redis.asyncio as redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import our application modules
from src.scheduler.scheduler import ECaDPScheduler
from src.scheduler.jobs.crawl_job import CrawlJob
from src.scheduler.jobs.scrape_job import ScrapeJob
from src.scheduler.jobs.proxy_update_job import ProxyUpdateJob
from src.scheduler.jobs.backup_job import BackupJob
from src.database.connection import DatabaseManager
from src.proxy_pool.manager import ProxyPoolManager
from src.utils.logger import setup_logging
from src.webhooks.client import WebhookClient
from src.observability.metrics import MetricsCollector

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class SchedulerConfig:
    """Configuration for scheduler service"""
    redis_url: str = "redis://localhost:6379/0"
    max_workers: int = 10
    job_defaults: Dict[str, Any] = None
    timezone: str = "UTC"
    enable_monitoring: bool = True
    webhook_url: Optional[str] = None
    metrics_port: int = 8080
    health_check_interval: int = 60
    job_persistence: bool = True
    coalesce_jobs: bool = True
    max_instances: int = 3
    
    def __post_init__(self):
        if self.job_defaults is None:
            self.job_defaults = {
                'coalesce': self.coalesce_jobs,
                'max_instances': self.max_instances,
                'misfire_grace_time': 300  # 5 minutes
            }

class SchedulerService:
    """Production scheduler service with enterprise features"""
    
    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.scheduler = None
        self.redis_client = None
        self.db_manager = None
        self.proxy_manager = None
        self.webhook_client = None
        self.metrics_collector = None
        self.ecadp_scheduler = None
        
        # Service state
        self.start_time = None
        self.shutdown_requested = False
        self.jobs_executed = 0
        self.jobs_failed = 0
        self.last_health_check = None
        
        # Statistics
        self.stats = {
            'jobs_scheduled': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'jobs_missed': 0,
            'active_jobs': 0,
            'queue_size': 0
        }
    
    async def initialize(self):
        """Initialize scheduler service and all components"""
        try:
            console.print("[bold blue]🚀 Initializing ECaDP Scheduler Service[/bold blue]")
            self.start_time = datetime.utcnow()
            
            # Initialize Redis connection
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            console.print("✅ Redis connection established")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            console.print("✅ Database connection established")
            
            # Initialize proxy pool manager
            self.proxy_manager = ProxyPoolManager()
            await self.proxy_manager.initialize()
            console.print("✅ Proxy pool manager initialized")
            
            # Initialize webhook client
            if self.config.webhook_url:
                self.webhook_client = WebhookClient(self.config.webhook_url)
                console.print("✅ Webhook notifications enabled")
            
            # Initialize metrics collector
            if self.config.enable_monitoring:
                self.metrics_collector = MetricsCollector(port=self.config.metrics_port)
                await self.metrics_collector.start()
                console.print(f"✅ Metrics collection started on port {self.config.metrics_port}")
            
            # Initialize ECaDP scheduler
            self.ecadp_scheduler = ECaDPScheduler()
            await self.ecadp_scheduler.initialize()
            console.print("✅ ECaDP scheduler core initialized")
            
            # Configure APScheduler
            await self._configure_scheduler()
            console.print("✅ APScheduler configured")
            
            # Setup signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Schedule system jobs
            await self._schedule_system_jobs()
            console.print("✅ System jobs scheduled")
            
            logger.info("Scheduler service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler service: {e}")
            console.print(f"[red]❌ Initialization failed: {e}[/red]")
            raise
    
    async def _configure_scheduler(self):
        """Configure APScheduler with Redis backend"""
        # Configure job store
        jobstores = {
            'default': RedisJobStore(
                host=self.redis_client.connection_pool.connection_kwargs['host'],
                port=self.redis_client.connection_pool.connection_kwargs['port'],
                db=self.redis_client.connection_pool.connection_kwargs['db']
            )
        }
        
        # Configure executors
        executors = {
            'default': AsyncIOExecutor(max_workers=self.config.max_workers),
        }
        
        # Create scheduler
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=self.config.job_defaults,
            timezone=self.config.timezone
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
        
        # Start scheduler
        self.scheduler.start()
        logger.info("APScheduler started successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown signals"""
        console.print(f"\n[yellow]🛑 Received signal {signum}, initiating graceful shutdown...[/yellow]")
        self.shutdown_requested = True
    
    async def _job_listener(self, event):
        """Handle job execution events"""
        try:
            job_id = event.job_id
            
            if event.code == EVENT_JOB_EXECUTED:
                self.stats['jobs_completed'] += 1
                self.jobs_executed += 1
                logger.info(f"Job {job_id} executed successfully")
                
                if self.webhook_client:
                    await self.webhook_client.send_event("job.completed", {
                        "job_id": job_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "execution_time": getattr(event, 'runtime', 0)
                    })
            
            elif event.code == EVENT_JOB_ERROR:
                self.stats['jobs_failed'] += 1
                self.jobs_failed += 1
                logger.error(f"Job {job_id} failed: {event.exception}")
                
                if self.webhook_client:
                    await self.webhook_client.send_event("job.failed", {
                        "job_id": job_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": str(event.exception)
                    })
            
            elif event.code == EVENT_JOB_MISSED:
                self.stats['jobs_missed'] += 1
                logger.warning(f"Job {job_id} missed execution")
                
                if self.webhook_client:
                    await self.webhook_client.send_event("job.missed", {
                        "job_id": job_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            # Update metrics
            if self.metrics_collector:
                await self.metrics_collector.update_job_metrics(event)
                
        except Exception as e:
            logger.error(f"Error in job listener: {e}")
    
    async def _schedule_system_jobs(self):
        """Schedule essential system maintenance jobs"""
        
        # Health check job
        self.scheduler.add_job(
            self._health_check_job,
            'interval',
            seconds=self.config.health_check_interval,
            id='system_health_check',
            name='System Health Check',
            replace_existing=True
        )
        
        # Proxy pool update job (every 15 minutes)
        self.scheduler.add_job(
            self._proxy_update_job,
            'interval',
            minutes=15,
            id='proxy_pool_update',
            name='Proxy Pool Update',
            replace_existing=True
        )
        
        # Database backup job (daily at 2 AM)
        self.scheduler.add_job(
            self._backup_job,
            'cron',
            hour=2,
            minute=0,
            id='daily_backup',
            name='Daily Database Backup',
            replace_existing=True
        )
        
        # Cleanup old jobs (daily at 3 AM)
        self.scheduler.add_job(
            self._cleanup_job,
            'cron',
            hour=3,
            minute=0,
            id='daily_cleanup',
            name='Daily Cleanup',
            replace_existing=True
        )
        
        # Statistics aggregation (every hour)
        self.scheduler.add_job(
            self._stats_aggregation_job,
            'interval',
            hours=1,
            id='stats_aggregation',
            name='Statistics Aggregation',
            replace_existing=True
        )
        
        logger.info("System jobs scheduled successfully")
    
    async def _health_check_job(self):
        """Perform system health check"""
        try:
            self.last_health_check = datetime.utcnow()
            
            # Check Redis connection
            await self.redis_client.ping()
            
            # Check database connection
            await self.db_manager.health_check()
            
            # Check proxy manager
            if self.proxy_manager:
                proxy_health = await self.proxy_manager.health_check()
                if not proxy_health.get('healthy', False):
                    logger.warning("Proxy pool health check failed")
            
            # Update scheduler statistics
            self.stats['active_jobs'] = len(self.scheduler.get_jobs())
            
            logger.debug("Health check completed successfully")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            if self.webhook_client:
                await self.webhook_client.send_event("health.check.failed", {
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                })
    
    async def _proxy_update_job(self):
        """Update proxy pool"""
        try:
            if self.proxy_manager:
                result = await self.proxy_manager.update_pool()
                logger.info(f"Proxy pool updated: {result}")
                
        except Exception as e:
            logger.error(f"Proxy update job failed: {e}")
    
    async def _backup_job(self):
        """Perform database backup"""
        try:
            backup_job = BackupJob()
            result = await backup_job.execute()
            logger.info(f"Backup job completed: {result}")
            
        except Exception as e:
            logger.error(f"Backup job failed: {e}")
    
    async def _cleanup_job(self):
        """Clean up old job data"""
        try:
            # Clean up old job executions from database
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            await self.db_manager.cleanup_old_jobs(cutoff_date)
            logger.info("Job cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup job failed: {e}")
    
    async def _stats_aggregation_job(self):
        """Aggregate and store statistics"""
        try:
            # Store current statistics
            stats_data = {
                **self.stats,
                'timestamp': datetime.utcnow().isoformat(),
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds()
            }
            
            await self.redis_client.lpush('scheduler_stats', json.dumps(stats_data))
            await self.redis_client.ltrim('scheduler_stats', 0, 1000)  # Keep last 1000 entries
            
            logger.debug("Statistics aggregated successfully")
            
        except Exception as e:
            logger.error(f"Statistics aggregation failed: {e}")
    
    def _create_status_display(self) -> Table:
        """Create status display table"""
        table = Table(title="🕰️ ECaDP Scheduler Service Status")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        uptime = datetime.utcnow() - self.start_time if self.start_time else timedelta(0)
        
        table.add_row("Service Status", "🟢 Running")
        table.add_row("Uptime", str(uptime).split('.')[0])
        table.add_row("Active Jobs", str(len(self.scheduler.get_jobs()) if self.scheduler else 0))
        table.add_row("Jobs Executed", str(self.jobs_executed))
        table.add_row("Jobs Failed", str(self.jobs_failed))
        table.add_row("Last Health Check", 
                     self.last_health_check.strftime('%H:%M:%S') if self.last_health_check else 'Never')
        
        if self.proxy_manager:
            table.add_row("Active Proxies", str(getattr(self.proxy_manager, 'active_count', 'N/A')))
        
        return table
    
    def _create_jobs_table(self) -> Table:
        """Create jobs overview table"""
        table = Table(title="📋 Scheduled Jobs")
        table.add_column("Job ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Next Run", style="yellow")
        table.add_column("Status", style="magenta")
        
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'None'
                table.add_row(
                    job.id,
                    job.name or 'Unknown',
                    next_run,
                    "⏰ Scheduled"
                )
        
        return table
    
    async def schedule_crawl_job(self, job_config: Dict[str, Any]) -> str:
        """Schedule a new crawl job"""
        try:
            crawl_job = CrawlJob(
                urls=job_config['urls'],
                crawl_depth=job_config.get('depth', 3),
                max_pages=job_config.get('max_pages', 1000)
            )
            
            job_id = f"crawl_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            if job_config.get('schedule'):
                # Scheduled job
                self.scheduler.add_job(
                    crawl_job.execute,
                    trigger=job_config['schedule']['trigger'],
                    **job_config['schedule'].get('kwargs', {}),
                    id=job_id,
                    name=f"Crawl Job: {job_config.get('name', 'Unnamed')}",
                    replace_existing=True
                )
            else:
                # Immediate job
                self.scheduler.add_job(
                    crawl_job.execute,
                    id=job_id,
                    name=f"Crawl Job: {job_config.get('name', 'Unnamed')}"
                )
            
            self.stats['jobs_scheduled'] += 1
            logger.info(f"Crawl job scheduled: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to schedule crawl job: {e}")
            raise
    
    async def schedule_scrape_job(self, job_config: Dict[str, Any]) -> str:
        """Schedule a new scrape job"""
        try:
            scrape_job = ScrapeJob(
                urls=job_config['urls'],
                template_path=job_config.get('template_path'),
                output_format=job_config.get('output_format', 'json')
            )
            
            job_id = f"scrape_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            if job_config.get('schedule'):
                # Scheduled job
                self.scheduler.add_job(
                    scrape_job.execute,
                    trigger=job_config['schedule']['trigger'],
                    **job_config['schedule'].get('kwargs', {}),
                    id=job_id,
                    name=f"Scrape Job: {job_config.get('name', 'Unnamed')}",
                    replace_existing=True
                )
            else:
                # Immediate job
                self.scheduler.add_job(
                    scrape_job.execute,
                    id=job_id,
                    name=f"Scrape Job: {job_config.get('name', 'Unnamed')}"
                )
            
            self.stats['jobs_scheduled'] += 1
            logger.info(f"Scrape job scheduled: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to schedule scrape job: {e}")
            raise
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job cancelled: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'kwargs': job.kwargs,
                    'trigger': str(job.trigger)
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get job status for {job_id}: {e}")
            return None
    
    async def run_service(self):
        """Run the scheduler service"""
        try:
            console.print(f"[bold green]🕰️ ECaDP Scheduler Service started at {self.start_time.isoformat()}[/bold green]")
            
            # Send startup webhook
            if self.webhook_client:
                await self.webhook_client.send_event("scheduler.started", {
                    "timestamp": self.start_time.isoformat(),
                    "config": asdict(self.config)
                })
            
            # Main service loop with live display
            with Live(self._create_status_display(), refresh_per_second=1, console=console) as live:
                while not self.shutdown_requested:
                    # Update display
                    live.update(self._create_status_display())
                    
                    # Sleep briefly
                    await asyncio.sleep(1)
            
            console.print(f"\n[bold yellow]🛑 Scheduler service shutting down...[/bold yellow]")
            
        except Exception as e:
            logger.error(f"Scheduler service error: {e}")
            console.print(f"[red]❌ Service error: {e}[/red]")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            console.print("[yellow]🧹 Cleaning up scheduler service...[/yellow]")
            
            # Shutdown scheduler
            if self.scheduler:
                self.scheduler.shutdown(wait=True)
                console.print("✅ APScheduler stopped")
            
            # Close ECaDP scheduler
            if self.ecadp_scheduler:
                await self.ecadp_scheduler.shutdown()
                console.print("✅ ECaDP scheduler closed")
            
            # Close database connection
            if self.db_manager:
                await self.db_manager.close()
                console.print("✅ Database connection closed")
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
                console.print("✅ Redis connection closed")
            
            # Stop metrics collector
            if self.metrics_collector:
                await self.metrics_collector.stop()
                console.print("✅ Metrics collection stopped")
            
            # Send shutdown webhook
            if self.webhook_client:
                await self.webhook_client.send_event("scheduler.stopped", {
                    "timestamp": datetime.utcnow().isoformat(),
                    "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                    "stats": self.stats
                })
            
            console.print("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def load_config_from_file(config_path: str) -> SchedulerConfig:
    """Load scheduler configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return SchedulerConfig(**config_data.get('scheduler_config', {}))
        
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise

def create_default_config() -> SchedulerConfig:
    """Create default scheduler configuration"""
    return SchedulerConfig(
        redis_url="redis://localhost:6379/0",
        max_workers=10,
        timezone="UTC",
        enable_monitoring=True
    )

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ECaDP Production Scheduler Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_scheduler.py --redis-url redis://localhost:6379/0
  python start_scheduler.py --config config/scheduler_config.yml
  python start_scheduler.py --max-workers 20 --webhook-url https://api.example.com/webhook
        """
    )
    
    # Configuration options
    parser.add_argument('--config', help='YAML configuration file')
    parser.add_argument('--redis-url', default='redis://localhost:6379/0', help='Redis URL for job store')
    parser.add_argument('--max-workers', type=int, default=10, help='Maximum worker threads')
    parser.add_argument('--timezone', default='UTC', help='Scheduler timezone')
    
    # Monitoring options
    parser.add_argument('--webhook-url', help='Webhook URL for notifications')
    parser.add_argument('--metrics-port', type=int, default=8080, help='Metrics server port')
    parser.add_argument('--no-monitoring', action='store_true', help='Disable metrics collection')
    
    # Service options
    parser.add_argument('--health-interval', type=int, default=60, help='Health check interval (seconds)')
    parser.add_argument('--no-persistence', action='store_true', help='Disable job persistence')
    
    # Utility options
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true', help='Show configuration without starting')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    try:
        # Load configuration
        if args.config:
            config = await load_config_from_file(args.config)
        else:
            config = SchedulerConfig(
                redis_url=args.redis_url,
                max_workers=args.max_workers,
                timezone=args.timezone,
                webhook_url=args.webhook_url,
                metrics_port=args.metrics_port,
                enable_monitoring=not args.no_monitoring,
                health_check_interval=args.health_interval,
                job_persistence=not args.no_persistence
            )
        
        # Show configuration
        console.print("\n[bold]🛠️ Scheduler Configuration[/bold]")
        config_table = Table()
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("Redis URL", config.redis_url)
        config_table.add_row("Max Workers", str(config.max_workers))
        config_table.add_row("Timezone", config.timezone)
        config_table.add_row("Monitoring", "✅" if config.enable_monitoring else "❌")
        config_table.add_row("Job Persistence", "✅" if config.job_persistence else "❌")
        config_table.add_row("Health Check Interval", f"{config.health_check_interval}s")
        
        if config.webhook_url:
            config_table.add_row("Webhook URL", config.webhook_url)
        
        console.print(config_table)
        
        if args.dry_run:
            console.print("\n[yellow]🔍 Dry run completed - configuration validated[/yellow]")
            return
        
        # Initialize and run service
        service = SchedulerService(config)
        
        try:
            await service.initialize()
            await service.run_service()
            
        finally:
            await service.cleanup()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Service interrupted by user[/yellow]")
        sys.exit(1)
    
    except Exception as e:
        console.print(f"\n[red]❌ Service failed: {e}[/red]")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())