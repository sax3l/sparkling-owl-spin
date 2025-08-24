#!/usr/bin/env python3
"""
Production Crawler Main Script
Complete implementation demonstrating all crawling system components working together.

This script shows how the following components integrate:
- URL Queue management with Redis
- BFS/DFS crawling strategies
- Database persistence
- Job scheduling
- Real-time monitoring
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

import redis.asyncio as redis

# Import our crawler components
from src.crawler.crawl_coordinator import CrawlCoordinator, CrawlConfiguration, create_crawl_coordinator
from src.crawler.url_queue import URLQueue, QueuedURL
from src.database.crawl_database import create_crawl_service, DatabaseManager
from src.scheduler.simple_scheduler import SimpleScheduler, ScheduledJob, ScheduleType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ProductionCrawlerDemo:
    """
    Complete demonstration of the production crawler system.
    Shows integration of all major components.
    """
    
    def __init__(self):
        self.redis_client = None
        self.db_service = None
        self.scheduler = None
        self.coordinator = None
        
    async def initialize(self):
        """Initialize all system components"""
        print("🚀 Initializing Production Crawler System")
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url("redis://localhost:6379/0")
            await self.redis_client.ping()
            print("✅ Redis connection established")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            print("💡 Please ensure Redis is running on localhost:6379")
            return False
        
        # Initialize database service (using SQLite for demo)
        try:
            database_url = "sqlite+aiosqlite:///./sparkling_owl_crawls.db"
            self.db_service = await create_crawl_service(database_url)
            print("✅ Database service initialized")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
        
        # Initialize scheduler
        try:
            self.scheduler = SimpleScheduler(self.redis_client, max_concurrent_jobs=5)
            await self.scheduler.start()
            print("✅ Job scheduler started")
        except Exception as e:
            print(f"❌ Scheduler initialization failed: {e}")
            return False
        
        print("\n🎯 All systems initialized successfully!\n")
        return True
    
    async def demo_url_queue_management(self):
        """Demonstrate URL queue functionality"""
        console.print(Panel.fit("📋 URL Queue Management Demo", style="bold cyan"))
        
        # Create URL queue
        url_queue = URLQueue(self.redis_client, "demo_queue")
        
        # Add some sample URLs
        sample_urls = [
            "https://example.com",
            "https://httpbin.org/json",
            "https://httpbin.org/html", 
            "https://jsonplaceholder.typicode.com/posts/1",
            "https://jsonplaceholder.typicode.com/users"
        ]
        
        queued_urls = []
        for i, url in enumerate(sample_urls):
            queued_url = QueuedURL(
                url=url,
                priority=i + 1,
                depth=0,
                metadata={"source": "demo"}
            )
            queued_urls.append(queued_url)
        
        # Batch add URLs
        added_count = await url_queue.add_urls_batch(queued_urls)
        console.print(f"➕ Added {added_count} URLs to queue")
        
        # Get queue statistics
        stats = await url_queue.get_queue_stats()
        console.print(f"📊 Queue stats: {stats['total_queued']} queued, {stats['total_seen']} seen")
        
        # Demonstrate getting URLs from queue
        console.print("\n🔄 Processing URLs from queue:")
        for _ in range(min(3, added_count)):
            next_url = await url_queue.get_next_url(domain_delay_seconds=0)
            if next_url:
                console.print(f"   🎯 Next URL: {next_url.url} (priority: {next_url.priority})")
        
        console.print("✅ URL Queue demo completed\n")
    
    async def demo_crawl_coordination(self):
        """Demonstrate crawl coordination with different strategies"""
        console.print(Panel.fit("🕷️ Crawl Coordination Demo", style="bold magenta"))
        
        # Test URLs (using reliable test sites)
        start_urls = [
            "https://httpbin.org/html",
            "https://jsonplaceholder.typicode.com/posts/1"
        ]
        
        # BFS Strategy Demo
        console.print("\n🌊 [bold]BFS Crawling Strategy[/bold]")
        await self._demo_crawl_strategy("bfs", start_urls, max_pages=5)
        
        # DFS Strategy Demo  
        console.print("\n🏔️ [bold]DFS Crawling Strategy[/bold]")
        await self._demo_crawl_strategy("dfs", start_urls, max_pages=5)
        
        # Intelligent Strategy Demo
        console.print("\n🧠 [bold]Intelligent Hybrid Strategy[/bold]")
        await self._demo_crawl_strategy("intelligent", start_urls, max_pages=5)
        
        console.print("✅ Crawl coordination demo completed\n")
    
    async def _demo_crawl_strategy(self, strategy: str, start_urls: List[str], max_pages: int):
        """Demo a specific crawling strategy"""
        try:
            # Create configuration
            config = CrawlConfiguration(
                strategy=strategy,
                max_pages=max_pages,
                max_depth=2,
                max_concurrent=3,
                delay_between_requests=0.5,
                respect_robots_txt=False,  # Skip for demo speed
                use_stealth=False,  # Disable for demo
                use_ai_extraction=False,  # Disable for demo
                use_real_time_monitoring=False  # Disable for demo
            )
            
            # Create coordinator
            coordinator = await create_crawl_coordinator(
                config, 
                self.redis_client, 
                f"demo_{strategy}_queue"
            )
            
            # Start crawl
            with Progress() as progress:
                task = progress.add_task(f"[cyan]Crawling with {strategy.upper()}", total=max_pages)
                
                # Start crawl in background
                crawl_task = asyncio.create_task(coordinator.start_crawl(start_urls))
                
                # Monitor progress
                while not crawl_task.done():
                    status = await coordinator.get_crawl_status()
                    crawled = status['stats']['total_crawled']
                    progress.update(task, completed=min(crawled, max_pages))
                    
                    if crawled >= max_pages:
                        await coordinator.stop_crawl()
                        break
                    
                    await asyncio.sleep(1)
                
                # Wait for completion
                try:
                    await asyncio.wait_for(crawl_task, timeout=30)
                except asyncio.TimeoutError:
                    await coordinator.stop_crawl()
            
            # Get final results
            final_status = await coordinator.get_crawl_status()
            console.print(f"   📊 Crawled: {final_status['stats']['total_crawled']} pages")
            console.print(f"   🔗 Discovered: {final_status['stats']['total_discovered']} URLs")
            console.print(f"   ⚡ Speed: {final_status['stats']['pages_per_second']:.2f} pages/sec")
            
            await coordinator.close()
            
        except Exception as e:
            console.print(f"   ❌ Strategy demo failed: {e}")
    
    async def demo_database_operations(self):
        """Demonstrate database operations"""
        console.print(Panel.fit("💾 Database Operations Demo", style="bold green"))
        
        # Create a crawl job in database
        job_id = await self.db_service.create_crawl_job(
            name="Demo Crawl Job",
            start_urls=["https://example.com", "https://httpbin.org"],
            config={
                "strategy": "bfs",
                "max_pages": 100,
                "max_depth": 3
            }
        )
        console.print(f"➕ Created crawl job: {job_id}")
        
        # Start the job
        await self.db_service.start_crawl_job(job_id)
        console.print("▶️ Started crawl job")
        
        # Simulate saving some crawled pages
        for i in range(3):
            page_id = await self.db_service.save_crawled_page(
                job_id=job_id,
                url=f"https://example.com/page{i+1}",
                html_content=f"<html><body>Demo page {i+1} content</body></html>",
                extracted_data={"title": f"Page {i+1}", "content_length": 100 + i*10},
                metadata={"demo": True, "page_number": i+1}
            )
            console.print(f"   💾 Saved page {i+1}: {page_id}")
        
        # Complete the job with statistics
        await self.db_service.complete_crawl_job(
            job_id,
            stats={
                "total_crawled": 3,
                "total_discovered": 10,
                "pages_per_second": 2.5
            }
        )
        console.print("✅ Completed crawl job")
        
        # Get job statistics
        stats = await self.db_service.get_job_statistics(job_id)
        console.print("\n📊 Job Statistics:")
        console.print(f"   🎯 Name: {stats['name']}")
        console.print(f"   📈 Status: {stats['status']}")
        console.print(f"   📄 Pages crawled: {stats['total_pages_crawled']}")
        console.print(f"   ⏱️ Runtime: {stats['runtime_seconds']:.2f} seconds")
        
        console.print("✅ Database operations demo completed\n")
    
    async def demo_job_scheduling(self):
        """Demonstrate job scheduling functionality"""
        console.print(Panel.fit("⏰ Job Scheduling Demo", style="bold yellow"))
        
        # Create a one-time job
        one_time_job = ScheduledJob(
            id="demo_once",
            name="One-time Demo Job",
            description="Runs once immediately",
            schedule_type=ScheduleType.ONCE,
            start_urls=["https://httpbin.org/json"],
            crawl_config={"strategy": "bfs", "max_pages": 2},
            start_date=datetime.utcnow() + timedelta(seconds=5)
        )
        
        await self.scheduler.schedule_job(one_time_job)
        console.print("📅 Scheduled one-time job (runs in 5 seconds)")
        
        # Create an interval job
        interval_job = ScheduledJob(
            id="demo_interval",
            name="Interval Demo Job", 
            description="Runs every 30 seconds",
            schedule_type=ScheduleType.INTERVAL,
            interval_seconds=30,
            start_urls=["https://httpbin.org/json"],
            crawl_config={"strategy": "bfs", "max_pages": 2},
            max_retries=1
        )
        
        await self.scheduler.schedule_job(interval_job)
        console.print("🔄 Scheduled interval job (every 30 seconds)")
        
        # Monitor jobs for a bit
        console.print("\n🔍 Monitoring scheduled jobs:")
        for i in range(15):  # Monitor for ~15 seconds
            stats = await self.scheduler.get_scheduler_stats()
            jobs = await self.scheduler.list_jobs()
            
            running_count = len([j for j in jobs if j.status.value == "running"])
            pending_count = len([j for j in jobs if j.status.value == "pending"])
            
            console.print(f"   📊 Iteration {i+1}: {running_count} running, {pending_count} pending")
            
            # Show running job details
            for job in jobs:
                if job.status.value == "running":
                    console.print(f"      🏃 Running: {job.name}")
            
            await asyncio.sleep(1)
        
        # Cancel the interval job
        await self.scheduler.cancel_job("demo_interval")
        console.print("🛑 Cancelled interval job")
        
        console.print("✅ Job scheduling demo completed\n")
    
    async def demo_integration_showcase(self):
        """Showcase full system integration"""
        console.print(Panel.fit("🌟 Full System Integration Showcase", style="bold blue"))
        
        # Create a comprehensive crawling job that uses all components
        integration_job = ScheduledJob(
            id="integration_showcase",
            name="Integration Showcase",
            description="Full system demonstration",
            schedule_type=ScheduleType.ONCE,
            start_urls=[
                "https://httpbin.org/html",
                "https://jsonplaceholder.typicode.com/posts"
            ],
            crawl_config={
                "strategy": "intelligent",
                "max_pages": 10,
                "max_depth": 2,
                "max_concurrent": 3,
                "extract_data": True,
                "save_to_database": True
            }
        )
        
        # Schedule the job
        await self.scheduler.schedule_job(integration_job)
        console.print("🚀 Started integration showcase job")
        
        # Create database job to track it
        db_job_id = await self.db_service.create_crawl_job(
            name="Integration Showcase Crawl",
            start_urls=integration_job.start_urls,
            config=integration_job.crawl_config
        )
        
        # Monitor the complete process
        console.print("\n📡 Monitoring full integration...")
        
        start_time = time.time()
        while time.time() - start_time < 30:  # Monitor for 30 seconds max
            # Get scheduler status
            scheduler_stats = await self.scheduler.get_scheduler_stats()
            
            # Get database job status  
            db_stats = await self.db_service.get_job_statistics(db_job_id)
            
            console.print(f"   ⏱️ Time: {int(time.time() - start_time)}s")
            console.print(f"   📊 Scheduler: {scheduler_stats['currently_running']} running")
            console.print(f"   💾 Database: {db_stats.get('status', 'unknown')} status")
            
            await asyncio.sleep(2)
        
        console.print("✅ Integration showcase completed\n")
    
    async def show_final_summary(self):
        """Show final system summary"""
        console.print(Panel.fit("📋 Final System Summary", style="bold white"))
        
        # Scheduler statistics
        scheduler_stats = await self.scheduler.get_scheduler_stats()
        
        table = Table(title="System Components Status", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        table.add_row("Redis Queue", "✅ Active", f"Connected to localhost:6379")
        table.add_row("Database", "✅ Active", f"SQLite database operational")
        table.add_row("Scheduler", "✅ Running", f"{scheduler_stats['jobs_scheduled']} jobs scheduled")
        table.add_row("Crawler", "✅ Ready", "All strategies available")
        
        console.print(table)
        console.print("\n🎯 [bold green]Production crawler system fully operational![/bold green]")
    
    async def cleanup(self):
        """Clean up resources"""
        console.print("\n🧹 Cleaning up resources...")
        
        if self.scheduler:
            await self.scheduler.stop()
        
        if self.redis_client:
            await self.redis_client.close()
        
        console.print("✅ Cleanup completed")

async def main():
    """Main demo function"""
    demo = ProductionCrawlerDemo()
    
    try:
        # Initialize system
        if not await demo.initialize():
            return
        
        # Run component demonstrations
        await demo.demo_url_queue_management()
        await demo.demo_database_operations() 
        await demo.demo_job_scheduling()
        await demo.demo_crawl_coordination()
        await demo.demo_integration_showcase()
        
        # Show final summary
        await demo.show_final_summary()
        
    except KeyboardInterrupt:
        console.print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        console.print(f"\n❌ Demo failed with error: {e}")
        logger.exception("Demo failed")
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the demo
    console.print("""
[bold blue]🕷️ Sparkling Owl Spin Production Crawler Demo[/bold blue]

This demo showcases the complete crawling system with:
• URL Queue management with Redis persistence
• BFS/DFS/Intelligent crawling strategies  
• Database persistence with SQLAlchemy
• Job scheduling with cron-like functionality
• Real-time monitoring and statistics

[yellow]Prerequisites:[/yellow]
• Redis server running on localhost:6379
• Internet connection for test URLs

[green]Starting demo...[/green]
""")
    
    asyncio.run(main())
