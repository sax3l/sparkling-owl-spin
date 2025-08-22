"""
Crawl Job Implementation
========================

Implementation of crawl jobs for the ECaDP scheduler.
Handles web crawling operations with comprehensive configuration,
monitoring, and error handling capabilities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml

from src.crawler.crawler import Crawler
from src.crawler.sitemap_generator import SitemapGenerator
from src.crawler.url_queue import URLQueue, QueuedURL
from src.proxy_pool.manager import ProxyPoolManager
from src.anti_bot.detector import BotDetector
from src.database.manager import DatabaseManager
from src.utils.rate_limiter import RateLimiter
from src.webhooks.client import WebhookClient

logger = logging.getLogger(__name__)

@dataclass
class CrawlJobConfig:
    """Configuration for crawl jobs"""
    urls: List[str]
    crawl_depth: int = 3
    max_pages: int = 1000
    concurrent_requests: int = 10
    delay_range: tuple = (1.0, 3.0)
    respect_robots_txt: bool = True
    use_proxy_pool: bool = True
    enable_anti_bot: bool = True
    output_format: str = "json"
    output_path: str = "data/exports/crawl_results"
    template_path: Optional[str] = None
    webhook_url: Optional[str] = None
    retry_attempts: int = 3
    timeout: int = 30
    user_agent: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    follow_redirects: bool = True
    extract_links: bool = True
    extract_content: bool = True
    save_html: bool = False
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class CrawlJobResult:
    """Result of a crawl job execution"""
    job_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    pages_crawled: int = 0
    urls_discovered: int = 0
    errors: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CrawlJob:
    """
    Crawl job implementation for ECaDP scheduler
    
    Handles the execution of web crawling tasks with comprehensive
    configuration, monitoring, and error handling.
    """
    
    def __init__(self, config: Union[CrawlJobConfig, Dict[str, Any]], job_id: Optional[str] = None):
        if isinstance(config, dict):
            self.config = CrawlJobConfig(**config)
        else:
            self.config = config
            
        self.job_id = job_id or f"crawl_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Components
        self.crawler = None
        self.proxy_manager = None
        self.bot_detector = None
        self.rate_limiter = None
        self.url_queue = None
        self.db_manager = None
        self.webhook_client = None
        
        # Execution state
        self.result = CrawlJobResult(
            job_id=self.job_id,
            status="pending",
            start_time=datetime.utcnow()
        )
    
    async def initialize(self):
        """Initialize job components"""
        try:
            logger.info(f"Initializing crawl job {self.job_id}")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Initialize proxy pool if enabled
            if self.config.use_proxy_pool:
                self.proxy_manager = ProxyPoolManager()
                await self.proxy_manager.initialize()
                logger.info(f"Proxy pool initialized with {await self.proxy_manager.get_active_count()} proxies")
            
            # Initialize anti-bot detection
            if self.config.enable_anti_bot:
                self.bot_detector = BotDetector()
                logger.info("Anti-bot detection initialized")
            
            # Initialize rate limiter
            self.rate_limiter = RateLimiter(
                max_requests=self.config.concurrent_requests,
                time_window=60.0
            )
            
            # Initialize URL queue
            self.url_queue = URLQueue(max_size=10000)
            
            # Initialize crawler
            self.crawler = Crawler(
                proxy_manager=self.proxy_manager,
                bot_detector=self.bot_detector,
                rate_limiter=self.rate_limiter
            )
            
            # Initialize webhook client if configured
            if self.config.webhook_url:
                self.webhook_client = WebhookClient(self.config.webhook_url)
            
            logger.info(f"Crawl job {self.job_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crawl job {self.job_id}: {e}")
            self.result.status = "failed"
            self.result.errors.append(f"Initialization failed: {str(e)}")
            raise
    
    async def prepare_urls(self) -> List[str]:
        """Prepare and validate URLs for crawling"""
        try:
            logger.info(f"Preparing URLs for crawl job {self.job_id}")
            
            all_urls = []
            
            # Process each target URL
            for url in self.config.urls:
                # Generate sitemap if needed
                if self.config.crawl_depth > 0:
                    sitemap_gen = SitemapGenerator()
                    discovered_urls = await sitemap_gen.discover_from_url(
                        url,
                        max_depth=self.config.crawl_depth
                    )
                    all_urls.extend(discovered_urls)
                else:
                    all_urls.append(url)
            
            # Remove duplicates while preserving order
            unique_urls = list(dict.fromkeys(all_urls))
            
            # Apply max_pages limit
            final_urls = unique_urls[:self.config.max_pages]
            
            logger.info(f"Prepared {len(final_urls)} URLs for crawling")
            return final_urls
            
        except Exception as e:
            logger.error(f"Failed to prepare URLs for job {self.job_id}: {e}")
            raise
    
    async def populate_queue(self, urls: List[str]):
        """Populate URL queue with prepared URLs"""
        try:
            logger.info(f"Populating queue for crawl job {self.job_id}")
            
            for priority, url in enumerate(urls):
                queued_url = QueuedURL(
                    url=url,
                    priority=priority,
                    depth=0,
                    discovered_at=datetime.utcnow(),
                    metadata={'job_id': self.job_id}
                )
                await self.url_queue.add_url(queued_url)
            
            logger.info(f"Added {len(urls)} URLs to queue for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Failed to populate queue for job {self.job_id}: {e}")
            raise
    
    async def crawl_urls(self):
        """Execute the crawling process"""
        try:
            logger.info(f"Starting crawl execution for job {self.job_id}")
            
            semaphore = asyncio.Semaphore(self.config.concurrent_requests)
            tasks = []
            
            while not self.url_queue.is_empty():
                # Get next URL
                queued_url = await self.url_queue.get_next()
                if not queued_url:
                    await asyncio.sleep(0.1)
                    continue
                
                # Create crawl task
                task = asyncio.create_task(
                    self._crawl_single_url(semaphore, queued_url)
                )
                tasks.append(task)
                
                # Clean up completed tasks
                tasks = [t for t in tasks if not t.done()]
                
                # Rate limiting
                await self.rate_limiter.acquire()
            
            # Wait for remaining tasks
            if tasks:
                logger.info(f"Waiting for {len(tasks)} remaining crawl tasks")
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(f"Crawl execution completed for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Crawl execution failed for job {self.job_id}: {e}")
            raise
    
    async def _crawl_single_url(self, semaphore: asyncio.Semaphore, queued_url: QueuedURL):
        """Crawl a single URL with semaphore protection"""
        async with semaphore:
            try:
                # Perform the actual crawl
                result = await self.crawler.crawl_url(
                    url=queued_url.url,
                    depth=queued_url.depth,
                    max_depth=self.config.crawl_depth
                )
                
                if result and result.success:
                    self.result.pages_crawled += 1
                    
                    # Process discovered URLs
                    if result.discovered_urls:
                        self.result.urls_discovered += len(result.discovered_urls)
                        
                        # Add new URLs to queue if within depth limit
                        for discovered_url in result.discovered_urls:
                            if queued_url.depth + 1 <= self.config.crawl_depth:
                                new_queued_url = QueuedURL(
                                    url=discovered_url,
                                    priority=queued_url.priority + 1,
                                    depth=queued_url.depth + 1,
                                    discovered_at=datetime.utcnow(),
                                    parent_url=queued_url.url,
                                    metadata={'job_id': self.job_id}
                                )
                                await self.url_queue.add_url(new_queued_url)
                    
                    # Store result if configured
                    if self.config.save_html and result.content:
                        await self._store_page_content(queued_url.url, result.content)
                    
                    logger.debug(f"Successfully crawled: {queued_url.url}")
                    
                else:
                    error_msg = f"Failed to crawl: {queued_url.url}"
                    self.result.errors.append(error_msg)
                    logger.warning(error_msg)
                
            except Exception as e:
                error_msg = f"Error crawling {queued_url.url}: {str(e)}"
                self.result.errors.append(error_msg)
                logger.error(error_msg)
    
    async def _store_page_content(self, url: str, content: str):
        """Store page content to filesystem"""
        try:
            output_dir = Path(self.config.output_path) / self.job_id / "html"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create safe filename from URL
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()
            filename = f"{url_hash}.html"
            
            file_path = output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if str(file_path) not in self.result.output_files:
                self.result.output_files.append(str(file_path))
                
        except Exception as e:
            logger.error(f"Failed to store content for {url}: {e}")
    
    async def generate_report(self):
        """Generate crawl job report"""
        try:
            logger.info(f"Generating report for crawl job {self.job_id}")
            
            # Update result statistics
            self.result.statistics = {
                'pages_crawled': self.result.pages_crawled,
                'urls_discovered': self.result.urls_discovered,
                'error_count': len(self.result.errors),
                'success_rate': (self.result.pages_crawled / max(1, len(self.config.urls))) * 100,
                'runtime_seconds': (datetime.utcnow() - self.result.start_time).total_seconds()
            }
            
            # Create report directory
            report_dir = Path(self.config.output_path) / self.job_id
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
                    'output_files': self.result.output_files,
                    'config': {
                        'urls': self.config.urls,
                        'crawl_depth': self.config.crawl_depth,
                        'max_pages': self.config.max_pages,
                        'concurrent_requests': self.config.concurrent_requests
                    }
                }, f, indent=2)
            
            self.result.output_files.append(str(report_path))
            
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
                    'output_files': self.result.output_files[:10]  # Limit to prevent large payloads
                }
                
                event_type = f"crawl_job.{self.result.status}"
                await self.webhook_client.send_event(event_type, notification_data)
                
                logger.info(f"Sent notification for job {self.job_id}")
                
        except Exception as e:
            logger.error(f"Failed to send notifications for job {self.job_id}: {e}")
    
    async def cleanup(self):
        """Clean up job resources"""
        try:
            logger.info(f"Cleaning up crawl job {self.job_id}")
            
            if self.db_manager:
                await self.db_manager.close()
            
            if self.proxy_manager:
                await self.proxy_manager.cleanup()
            
            logger.info(f"Cleanup completed for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup for job {self.job_id}: {e}")
    
    async def execute(self) -> CrawlJobResult:
        """
        Execute the crawl job
        
        Returns:
            CrawlJobResult: Result of the job execution
        """
        try:
            logger.info(f"Starting execution of crawl job {self.job_id}")
            self.result.status = "running"
            self.result.start_time = datetime.utcnow()
            
            # Initialize components
            await self.initialize()
            
            # Prepare URLs
            urls = await self.prepare_urls()
            if not urls:
                raise ValueError("No URLs available for crawling")
            
            # Populate queue
            await self.populate_queue(urls)
            
            # Execute crawling
            await self.crawl_urls()
            
            # Mark as completed
            self.result.status = "completed"
            self.result.end_time = datetime.utcnow()
            
            # Generate report
            await self.generate_report()
            
            # Send notifications
            await self.send_notifications()
            
            logger.info(f"Crawl job {self.job_id} completed successfully")
            logger.info(f"Statistics: {self.result.statistics}")
            
            return self.result
            
        except Exception as e:
            logger.error(f"Crawl job {self.job_id} failed: {e}")
            
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

async def create_simple_crawl_job(urls: List[str], **kwargs) -> CrawlJob:
    """Create a simple crawl job with default configuration"""
    config = CrawlJobConfig(urls=urls, **kwargs)
    return CrawlJob(config)

async def create_deep_crawl_job(urls: List[str], depth: int = 5, **kwargs) -> CrawlJob:
    """Create a deep crawl job with extended depth"""
    config = CrawlJobConfig(
        urls=urls,
        crawl_depth=depth,
        max_pages=10000,
        concurrent_requests=5,  # Lower concurrency for deep crawls
        **kwargs
    )
    return CrawlJob(config)

async def create_fast_crawl_job(urls: List[str], **kwargs) -> CrawlJob:
    """Create a fast crawl job with high concurrency"""
    config = CrawlJobConfig(
        urls=urls,
        crawl_depth=2,
        max_pages=1000,
        concurrent_requests=20,
        delay_range=(0.5, 1.0),
        **kwargs
    )
    return CrawlJob(config)
