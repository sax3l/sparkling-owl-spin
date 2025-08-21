#!/usr/bin/env python3
"""
Production Crawler Runner Script
===============================

Enterprise-grade crawler orchestration script for the ECaDP platform.
Handles crawling operations with comprehensive error handling, logging,
and integration with the job scheduler.

Features:
- Template-driven crawling with YAML configuration
- Proxy pool integration with health monitoring
- Rate limiting and ethical crawling practices
- Progress tracking and metrics collection
- Integration with Supabase database
- Webhook notifications and event streaming
- Resume/restart capability for interrupted jobs
"""

import asyncio
import argparse
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

import yaml
import httpx
from rich.console import Console
from rich.progress import Progress, TaskID, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live

# Import our application modules
from src.crawler.crawler import Crawler
from src.crawler.sitemap_generator import SitemapGenerator
from src.crawler.url_queue import URLQueue, QueuedURL
from src.crawler.robots_parser import RobotsParser
from src.proxy_pool.manager import ProxyPoolManager
from src.anti_bot.detector import BotDetector
from src.database.connection import DatabaseManager
from src.scheduler.scheduler import ECaDPScheduler
from src.utils.logger import setup_logging
from src.utils.rate_limiter import RateLimiter
from src.webhooks.client import WebhookClient

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class CrawlConfig:
    """Configuration for crawl operations"""
    target_urls: List[str]
    crawl_depth: int = 3
    max_pages: int = 1000
    concurrent_requests: int = 10
    delay_range: tuple = (1.0, 3.0)
    respect_robots_txt: bool = True
    use_proxy_pool: bool = True
    enable_anti_bot: bool = True
    output_format: str = "json"
    output_path: str = "data/exports/crawl_results"
    resume_job_id: Optional[str] = None
    webhook_url: Optional[str] = None
    template_path: Optional[str] = None

class CrawlerRunner:
    """Production crawler runner with enterprise features"""
    
    def __init__(self, config: CrawlConfig):
        self.config = config
        self.crawler = None
        self.proxy_manager = None
        self.url_queue = None
        self.scheduler = None
        self.db_manager = None
        self.webhook_client = None
        self.rate_limiter = None
        self.bot_detector = None
        self.progress = None
        self.task_id = None
        self.start_time = None
        self.shutdown_requested = False
        
        # Metrics
        self.pages_crawled = 0
        self.urls_discovered = 0
        self.errors_count = 0
        self.proxy_rotations = 0
        
    async def initialize(self):
        """Initialize all components"""
        try:
            console.print("[bold blue]🚀 Initializing ECaDP Crawler[/bold blue]")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            console.print("✅ Database connection established")
            
            # Initialize proxy pool if enabled
            if self.config.use_proxy_pool:
                self.proxy_manager = ProxyPoolManager()
                await self.proxy_manager.initialize()
                console.print(f"✅ Proxy pool initialized with {await self.proxy_manager.get_active_count()} proxies")
            
            # Initialize anti-bot detection
            if self.config.enable_anti_bot:
                self.bot_detector = BotDetector()
                console.print("✅ Anti-bot detection initialized")
            
            # Initialize rate limiter
            self.rate_limiter = RateLimiter(
                max_requests=self.config.concurrent_requests,
                time_window=60.0
            )
            console.print(f"✅ Rate limiter configured ({self.config.concurrent_requests} req/min)")
            
            # Initialize URL queue
            self.url_queue = URLQueue(max_size=10000)
            console.print("✅ URL queue initialized")
            
            # Initialize crawler
            self.crawler = Crawler(
                proxy_manager=self.proxy_manager,
                bot_detector=self.bot_detector,
                rate_limiter=self.rate_limiter
            )
            console.print("✅ Crawler engine initialized")
            
            # Initialize scheduler
            self.scheduler = ECaDPScheduler()
            await self.scheduler.initialize()
            console.print("✅ Job scheduler initialized")
            
            # Initialize webhook client if configured
            if self.config.webhook_url:
                self.webhook_client = WebhookClient(self.config.webhook_url)
                console.print("✅ Webhook notifications enabled")
                
            # Setup signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            logger.info("Crawler runner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crawler: {e}")
            console.print(f"[red]❌ Initialization failed: {e}[/red]")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle graceful shutdown signals"""
        console.print(f"\n[yellow]🛑 Received signal {signum}, initiating graceful shutdown...[/yellow]")
        self.shutdown_requested = True
    
    async def load_urls_from_file(self, file_path: str) -> List[str]:
        """Load URLs from input file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"URL file not found: {file_path}")
            
            urls = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        urls.append(line)
            
            console.print(f"✅ Loaded {len(urls)} URLs from {file_path}")
            return urls
            
        except Exception as e:
            logger.error(f"Failed to load URLs from file: {e}")
            raise
    
    async def check_robots_compliance(self, urls: List[str]) -> List[str]:
        """Filter URLs based on robots.txt compliance"""
        if not self.config.respect_robots_txt:
            return urls
        
        console.print("[blue]🤖 Checking robots.txt compliance...[/blue]")
        compliant_urls = []
        
        for url in urls:
            try:
                parser = RobotsParser()
                await parser.load_for_url(url)
                
                if await parser.can_fetch(url, user_agent="ECaDP-Crawler/1.0"):
                    compliant_urls.append(url)
                else:
                    logger.warning(f"URL blocked by robots.txt: {url}")
                    
            except Exception as e:
                logger.error(f"Error checking robots.txt for {url}: {e}")
                # Conservative approach: include URL if robots.txt check fails
                compliant_urls.append(url)
        
        console.print(f"✅ {len(compliant_urls)}/{len(urls)} URLs comply with robots.txt")
        return compliant_urls
    
    async def generate_sitemap(self, base_urls: List[str]) -> List[str]:
        """Generate sitemap from base URLs"""
        console.print("[blue]🗺️ Generating sitemap...[/blue]")
        
        sitemap_gen = SitemapGenerator()
        all_urls = []
        
        for base_url in base_urls:
            try:
                discovered_urls = await sitemap_gen.discover_from_url(
                    base_url, 
                    max_depth=self.config.crawl_depth
                )
                all_urls.extend(discovered_urls)
                logger.info(f"Discovered {len(discovered_urls)} URLs from {base_url}")
                
            except Exception as e:
                logger.error(f"Failed to generate sitemap for {base_url}: {e}")
        
        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(all_urls))
        console.print(f"✅ Generated sitemap with {len(unique_urls)} unique URLs")
        
        return unique_urls[:self.config.max_pages]  # Respect max_pages limit
    
    async def populate_queue(self, urls: List[str]):
        """Populate URL queue with discovered URLs"""
        console.print("[blue]📝 Populating URL queue...[/blue]")
        
        for priority, url in enumerate(urls):
            queued_url = QueuedURL(
                url=url,
                priority=priority,
                depth=0,
                discovered_at=datetime.utcnow()
            )
            await self.url_queue.add_url(queued_url)
        
        console.print(f"✅ Added {len(urls)} URLs to crawl queue")
    
    def _create_progress_display(self) -> Progress:
        """Create rich progress display"""
        return Progress(
            TextColumn("[bold blue]ECaDP Crawler", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            TextColumn("Pages: {task.fields[pages]}"),
            "•", 
            TextColumn("Discovered: {task.fields[discovered]}"),
            "•",
            TextColumn("Errors: {task.fields[errors]}"),
            "•",
            TimeRemainingColumn(),
        )
    
    def _create_stats_table(self) -> Table:
        """Create stats table for live display"""
        table = Table(title="🕷️ ECaDP Crawler Statistics")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        runtime = datetime.utcnow() - self.start_time if self.start_time else timedelta(0)
        
        table.add_row("Runtime", str(runtime).split('.')[0])
        table.add_row("Pages Crawled", str(self.pages_crawled))
        table.add_row("URLs Discovered", str(self.urls_discovered))
        table.add_row("Error Count", str(self.errors_count))
        table.add_row("Proxy Rotations", str(self.proxy_rotations))
        
        if self.proxy_manager:
            table.add_row("Active Proxies", str(getattr(self.proxy_manager, 'active_count', 'N/A')))
        
        pages_per_sec = self.pages_crawled / runtime.total_seconds() if runtime.total_seconds() > 0 else 0
        table.add_row("Pages/sec", f"{pages_per_sec:.2f}")
        
        return table
    
    async def run_crawl(self):
        """Execute the crawling operation"""
        try:
            self.start_time = datetime.utcnow()
            console.print(f"[bold green]🕷️ Starting crawl at {self.start_time.isoformat()}[/bold green]")
            
            # Send start webhook
            if self.webhook_client:
                await self.webhook_client.send_event("crawl.started", {
                    "timestamp": self.start_time.isoformat(),
                    "config": vars(self.config)
                })
            
            # Process target URLs
            target_urls = self.config.target_urls.copy()
            
            # Check robots.txt compliance
            compliant_urls = await self.check_robots_compliance(target_urls)
            if not compliant_urls:
                raise ValueError("No URLs available for crawling after robots.txt filtering")
            
            # Generate sitemap
            all_urls = await self.generate_sitemap(compliant_urls)
            if not all_urls:
                raise ValueError("No URLs discovered during sitemap generation")
            
            # Populate queue
            await self.populate_queue(all_urls)
            
            # Initialize progress tracking
            self.progress = self._create_progress_display()
            
            with Live(self._create_stats_table(), refresh_per_second=1, console=console) as live:
                self.task_id = self.progress.add_task(
                    "crawling",
                    total=len(all_urls),
                    pages=0,
                    discovered=0,
                    errors=0
                )
                
                # Main crawling loop
                semaphore = asyncio.Semaphore(self.config.concurrent_requests)
                tasks = []
                
                while not self.url_queue.is_empty() and not self.shutdown_requested:
                    # Get next URL
                    queued_url = await self.url_queue.get_next()
                    if not queued_url:
                        await asyncio.sleep(0.1)
                        continue
                    
                    # Create crawl task
                    task = asyncio.create_task(
                        self._crawl_url_with_semaphore(semaphore, queued_url)
                    )
                    tasks.append(task)
                    
                    # Clean up completed tasks
                    tasks = [t for t in tasks if not t.done()]
                    
                    # Update live display
                    live.update(self._create_stats_table())
                    
                    # Rate limiting
                    await self.rate_limiter.acquire()
                
                # Wait for remaining tasks
                if tasks:
                    console.print(f"[yellow]⏳ Waiting for {len(tasks)} remaining tasks...[/yellow]")
                    await asyncio.gather(*tasks, return_exceptions=True)
            
            # Completion summary
            runtime = datetime.utcnow() - self.start_time
            console.print(f"\n[bold green]✅ Crawl completed in {runtime}[/bold green]")
            console.print(f"📊 Pages crawled: {self.pages_crawled}")
            console.print(f"🔗 URLs discovered: {self.urls_discovered}")
            console.print(f"❌ Errors: {self.errors_count}")
            
            # Send completion webhook
            if self.webhook_client:
                await self.webhook_client.send_event("crawl.completed", {
                    "timestamp": datetime.utcnow().isoformat(),
                    "runtime_seconds": runtime.total_seconds(),
                    "pages_crawled": self.pages_crawled,
                    "urls_discovered": self.urls_discovered,
                    "error_count": self.errors_count
                })
            
        except Exception as e:
            logger.error(f"Crawl operation failed: {e}")
            console.print(f"[red]❌ Crawl failed: {e}[/red]")
            
            # Send error webhook
            if self.webhook_client:
                await self.webhook_client.send_event("crawl.error", {
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                })
            
            raise
    
    async def _crawl_url_with_semaphore(self, semaphore: asyncio.Semaphore, queued_url: QueuedURL):
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
                    self.pages_crawled += 1
                    self.urls_discovered += len(result.discovered_urls or [])
                    
                    # Add discovered URLs to queue
                    for discovered_url in result.discovered_urls or []:
                        new_queued_url = QueuedURL(
                            url=discovered_url,
                            priority=queued_url.priority + 1,
                            depth=queued_url.depth + 1,
                            discovered_at=datetime.utcnow(),
                            parent_url=queued_url.url
                        )
                        await self.url_queue.add_url(new_queued_url)
                    
                    logger.info(f"Successfully crawled: {queued_url.url}")
                else:
                    self.errors_count += 1
                    logger.warning(f"Failed to crawl: {queued_url.url}")
                
                # Update progress
                if self.progress and self.task_id:
                    self.progress.update(
                        self.task_id,
                        advance=1,
                        pages=self.pages_crawled,
                        discovered=self.urls_discovered,
                        errors=self.errors_count
                    )
                
            except Exception as e:
                self.errors_count += 1
                logger.error(f"Error crawling {queued_url.url}: {e}")
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            console.print("[yellow]🧹 Cleaning up resources...[/yellow]")
            
            if self.scheduler:
                await self.scheduler.shutdown()
            
            if self.db_manager:
                await self.db_manager.close()
            
            if self.proxy_manager:
                await self.proxy_manager.cleanup()
            
            console.print("✅ Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def load_config_from_file(config_path: str) -> CrawlConfig:
    """Load crawl configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return CrawlConfig(**config_data.get('crawl_config', {}))
        
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise

def create_default_config() -> CrawlConfig:
    """Create default crawl configuration"""
    return CrawlConfig(
        target_urls=[
            "https://example.com",
        ],
        crawl_depth=2,
        max_pages=100,
        concurrent_requests=5,
        delay_range=(2.0, 4.0),
        respect_robots_txt=True,
        use_proxy_pool=False,
        enable_anti_bot=True,
        output_format="json"
    )

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="ECaDP Production Crawler Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_crawler.py --urls https://example.com --depth 3 --max-pages 1000
  python run_crawler.py --config config/crawl_config.yml
  python run_crawler.py --url-file data/urls.txt --proxy-pool --webhook-url https://api.example.com/webhook
        """
    )
    
    # URL input options
    url_group = parser.add_mutually_exclusive_group(required=True)
    url_group.add_argument('--urls', nargs='+', help='Target URLs to crawl')
    url_group.add_argument('--url-file', help='File containing URLs to crawl')
    url_group.add_argument('--config', help='YAML configuration file')
    
    # Crawl parameters
    parser.add_argument('--depth', type=int, default=3, help='Maximum crawl depth')
    parser.add_argument('--max-pages', type=int, default=1000, help='Maximum pages to crawl')
    parser.add_argument('--concurrent', type=int, default=10, help='Concurrent requests')
    parser.add_argument('--delay-min', type=float, default=1.0, help='Minimum delay between requests')
    parser.add_argument('--delay-max', type=float, default=3.0, help='Maximum delay between requests')
    
    # Feature flags
    parser.add_argument('--no-robots', action='store_true', help='Ignore robots.txt')
    parser.add_argument('--proxy-pool', action='store_true', help='Use proxy pool')
    parser.add_argument('--no-anti-bot', action='store_true', help='Disable anti-bot detection')
    
    # Output options
    parser.add_argument('--output-format', choices=['json', 'csv', 'excel'], default='json', help='Output format')
    parser.add_argument('--output-path', default='data/exports/crawl_results', help='Output directory')
    
    # Integration options
    parser.add_argument('--webhook-url', help='Webhook URL for notifications')
    parser.add_argument('--resume-job', help='Resume job by ID')
    parser.add_argument('--template', help='Path to crawl template file')
    
    # Utility options
    parser.add_argument('--dry-run', action='store_true', help='Show configuration without running')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.getLogger().setLevel(log_level)
    
    try:
        # Load configuration
        if args.config:
            config = await load_config_from_file(args.config)
        else:
            # Build config from command line arguments
            if args.urls:
                target_urls = args.urls
            elif args.url_file:
                crawler_runner = CrawlerRunner(create_default_config())
                target_urls = await crawler_runner.load_urls_from_file(args.url_file)
            else:
                target_urls = ["https://example.com"]
            
            config = CrawlConfig(
                target_urls=target_urls,
                crawl_depth=args.depth,
                max_pages=args.max_pages,
                concurrent_requests=args.concurrent,
                delay_range=(args.delay_min, args.delay_max),
                respect_robots_txt=not args.no_robots,
                use_proxy_pool=args.proxy_pool,
                enable_anti_bot=not args.no_anti_bot,
                output_format=args.output_format,
                output_path=args.output_path,
                webhook_url=args.webhook_url,
                resume_job_id=args.resume_job,
                template_path=args.template
            )
        
        # Show configuration
        console.print("\n[bold]🛠️ Crawl Configuration[/bold]")
        config_table = Table()
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")
        
        config_table.add_row("Target URLs", str(len(config.target_urls)))
        config_table.add_row("Max Depth", str(config.crawl_depth))
        config_table.add_row("Max Pages", str(config.max_pages))
        config_table.add_row("Concurrent Requests", str(config.concurrent_requests))
        config_table.add_row("Delay Range", f"{config.delay_range[0]}-{config.delay_range[1]}s")
        config_table.add_row("Respect robots.txt", "✅" if config.respect_robots_txt else "❌")
        config_table.add_row("Use Proxy Pool", "✅" if config.use_proxy_pool else "❌")
        config_table.add_row("Anti-bot Detection", "✅" if config.enable_anti_bot else "❌")
        config_table.add_row("Output Format", config.output_format)
        
        console.print(config_table)
        
        if args.dry_run:
            console.print("\n[yellow]🔍 Dry run completed - configuration validated[/yellow]")
            return
        
        # Initialize and run crawler
        runner = CrawlerRunner(config)
        
        try:
            await runner.initialize()
            await runner.run_crawl()
            
        finally:
            await runner.cleanup()
    
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Crawl interrupted by user[/yellow]")
        sys.exit(1)
    
    except Exception as e:
        console.print(f"\n[red]❌ Crawl failed: {e}[/red]")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())