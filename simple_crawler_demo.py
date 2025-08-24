#!/usr/bin/env python3
"""
Production Crawler Main Script - Simple Version
Complete implementation demonstrating all crawling system components.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

import redis.asyncio as redis

# Import our crawler components
from src.scheduler.simple_scheduler import SimpleScheduler, ScheduledJob, ScheduleType

logger = logging.getLogger(__name__)

async def demo_simple_components():
    """Simple demonstration of core components"""
    
    print("🚀 Production Crawler System Demo")
    print("=" * 50)
    
    # 1. Redis Connection Demo
    print("\n📡 Testing Redis Connection...")
    try:
        redis_client = redis.from_url("redis://localhost:6379/0")
        await redis_client.ping()
        print("✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Please start Redis with: redis-server")
        return
    
    # 2. Simple Scheduler Demo
    print("\n⏰ Testing Job Scheduler...")
    scheduler = SimpleScheduler(redis_client, max_concurrent_jobs=3)
    await scheduler.start()
    print("✅ Scheduler started")
    
    # Create a simple job
    test_job = ScheduledJob(
        id="test_job_1",
        name="Test Crawl Job",
        description="Simple test job",
        schedule_type=ScheduleType.ONCE,
        start_urls=["https://httpbin.org/json", "https://httpbin.org/html"],
        crawl_config={
            "strategy": "bfs",
            "max_pages": 5,
            "max_depth": 2
        },
        start_date=datetime.utcnow() + timedelta(seconds=2)
    )
    
    # Schedule the job
    success = await scheduler.schedule_job(test_job)
    if success:
        print("✅ Job scheduled successfully")
    else:
        print("❌ Job scheduling failed")
    
    # Monitor for a bit
    print("\n🔍 Monitoring job execution...")
    for i in range(10):
        stats = await scheduler.get_scheduler_stats()
        jobs = await scheduler.list_jobs()
        
        running_jobs = [j for j in jobs if j.status.value == "running"]
        completed_jobs = [j for j in jobs if j.status.value == "completed"]
        
        print(f"   [{i+1:2d}] Running: {len(running_jobs)}, Completed: {len(completed_jobs)}")
        
        if running_jobs:
            for job in running_jobs:
                print(f"        🏃 {job.name}")
        
        await asyncio.sleep(2)
    
    # Show final stats
    final_stats = await scheduler.get_scheduler_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Jobs scheduled: {final_stats['jobs_scheduled']}")
    print(f"   Jobs completed: {final_stats['jobs_completed']}")
    print(f"   Jobs failed: {final_stats['jobs_failed']}")
    
    # Cleanup
    await scheduler.stop()
    await redis_client.close()
    
    print("\n✅ Demo completed successfully!")

async def demo_url_queue():
    """Simple URL queue demonstration"""
    print("\n📋 URL Queue Demo")
    print("-" * 30)
    
    redis_client = redis.from_url("redis://localhost:6379/0")
    
    # Import here to avoid circular imports
    from src.crawler.url_queue import URLQueue, QueuedURL
    
    queue = URLQueue(redis_client, "demo_queue")
    
    # Add some URLs
    test_urls = [
        "https://example.com",
        "https://httpbin.org/json",
        "https://httpbin.org/html"
    ]
    
    print(f"➕ Adding {len(test_urls)} URLs to queue...")
    
    queued_urls = []
    for i, url in enumerate(test_urls):
        queued_url = QueuedURL(
            url=url,
            priority=i + 1,
            depth=0
        )
        queued_urls.append(queued_url)
    
    added = await queue.add_urls_batch(queued_urls)
    print(f"✅ Added {added} URLs successfully")
    
    # Get stats
    stats = await queue.get_queue_stats()
    print(f"📊 Queue has {stats['total_queued']} URLs queued")
    
    # Process a few
    print("🔄 Processing URLs:")
    for i in range(min(3, added)):
        next_url = await queue.get_next_url(domain_delay_seconds=0)
        if next_url:
            print(f"   {i+1}. {next_url.url} (priority: {next_url.priority})")
    
    await redis_client.close()
    print("✅ URL Queue demo completed")

async def demo_database():
    """Simple database demonstration"""
    print("\n💾 Database Demo")
    print("-" * 20)
    
    try:
        from src.database.crawl_database import create_crawl_service
        
        # Create database service with SQLite
        db_service = await create_crawl_service("sqlite+aiosqlite:///./demo_crawls.db")
        print("✅ Database initialized")
        
        # Create a job
        job_id = await db_service.create_crawl_job(
            name="Demo Database Job",
            start_urls=["https://example.com"],
            config={"strategy": "bfs", "max_pages": 10}
        )
        print(f"➕ Created job: {job_id}")
        
        # Start it
        await db_service.start_crawl_job(job_id)
        print("▶️ Job started")
        
        # Add some fake pages
        for i in range(3):
            await db_service.save_crawled_page(
                job_id=job_id,
                url=f"https://example.com/page{i+1}",
                html_content=f"<html>Page {i+1}</html>",
                extracted_data={"title": f"Page {i+1}"}
            )
        print("💾 Saved 3 pages")
        
        # Complete job
        await db_service.complete_crawl_job(job_id, {
            "total_crawled": 3,
            "total_discovered": 5
        })
        print("✅ Job completed")
        
        # Get stats
        stats = await db_service.get_job_statistics(job_id)
        print(f"📊 Job '{stats['name']}' crawled {stats['total_pages_crawled']} pages")
        
    except Exception as e:
        print(f"❌ Database demo failed: {e}")
        logger.exception("Database demo error")

async def main():
    """Run all demos"""
    print("""
🕷️ Sparkling Owl Spin Production Crawler Demo

This demonstrates:
• Job scheduling system
• URL queue management  
• Database operations
• Component integration

Prerequisites:
• Redis server running on localhost:6379

Starting demos...
""")
    
    try:
        # Run individual component demos
        await demo_simple_components()
        await demo_url_queue() 
        await demo_database()
        
        print("\n🎯 All demos completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.exception("Demo failed")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Run the demos
    asyncio.run(main())
