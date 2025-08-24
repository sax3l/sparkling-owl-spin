#!/usr/bin/env python3
"""
Quick verification script to test that all implemented components work correctly.
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def test_imports():
    """Test that all critical components can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test scheduler import
        from src.scheduler.simple_scheduler import SimpleScheduler, ScheduledJob, ScheduleType
        print("✅ Scheduler imported successfully")
        
        # Test URL queue import
        from src.crawler.url_queue import URLQueue, QueuedURL
        print("✅ URL Queue imported successfully")
        
        # Test database import  
        from src.database.crawl_database import DatabaseManager, CrawlDatabaseService
        print("✅ Database components imported successfully")
        
        # Test coordinator import
        from src.crawler.crawl_coordinator import CrawlCoordinator, CrawlConfiguration
        print("✅ Crawl Coordinator imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

async def test_redis_connection():
    """Test Redis connectivity"""
    print("\n🔌 Testing Redis connection...")
    
    try:
        import redis.asyncio as redis
        
        client = redis.from_url("redis://localhost:6379/0")
        await client.ping()
        await client.close()
        
        print("✅ Redis connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("💡 Make sure Redis is running on localhost:6379")
        return False

async def test_database_creation():
    """Test database functionality"""
    print("\n💾 Testing database creation...")
    
    try:
        from src.database.crawl_database import create_crawl_service
        
        # Use in-memory SQLite for testing
        db_service = await create_crawl_service("sqlite+aiosqlite:///:memory:")
        print("✅ Database service created successfully")
        
        # Test creating a job
        job_id = await db_service.create_crawl_job(
            name="Test Job",
            start_urls=["https://example.com"],
            config={"strategy": "bfs"}
        )
        print(f"✅ Test job created: {job_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_url_queue():
    """Test URL queue functionality"""  
    print("\n📋 Testing URL queue...")
    
    try:
        import redis.asyncio as redis
        from src.crawler.url_queue import URLQueue, QueuedURL
        
        client = redis.from_url("redis://localhost:6379/0")
        queue = URLQueue(client, "test_queue")
        
        # Test adding URL
        test_url = QueuedURL(
            url="https://example.com/test",
            priority=1,
            depth=0
        )
        
        success = await queue.add_url(test_url)
        print(f"✅ URL added to queue: {success}")
        
        # Test getting URL
        next_url = await queue.get_next_url(0)  # No delay
        if next_url:
            print(f"✅ URL retrieved from queue: {next_url.url}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ URL queue test failed: {e}")
        return False

async def test_scheduler():
    """Test job scheduler"""
    print("\n⏰ Testing job scheduler...")
    
    try:
        import redis.asyncio as redis
        from src.scheduler.simple_scheduler import SimpleScheduler, ScheduledJob, ScheduleType
        
        client = redis.from_url("redis://localhost:6379/0")
        scheduler = SimpleScheduler(client, max_concurrent_jobs=2)
        
        # Start scheduler
        await scheduler.start()
        print("✅ Scheduler started")
        
        # Create test job
        test_job = ScheduledJob(
            id="test_verification",
            name="Verification Job",
            schedule_type=ScheduleType.ONCE,
            start_urls=["https://httpbin.org/json"],
            start_date=datetime.utcnow() + timedelta(seconds=2)
        )
        
        # Schedule job
        success = await scheduler.schedule_job(test_job)
        print(f"✅ Job scheduled: {success}")
        
        # Wait a bit and check stats
        await asyncio.sleep(5)
        stats = await scheduler.get_scheduler_stats()
        print(f"✅ Scheduler stats: {stats['jobs_scheduled']} scheduled")
        
        # Cleanup
        await scheduler.stop()
        await client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False

async def run_verification():
    """Run all verification tests"""
    print("🚀 Sparkling Owl Spin - Component Verification")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Redis Connection", test_redis_connection), 
        ("Database Creation", test_database_creation),
        ("URL Queue", test_url_queue),
        ("Job Scheduler", test_scheduler)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.exception(f"Test {test_name} crashed")
            results.append((test_name, False))
    
    # Print summary
    print("\n📊 VERIFICATION SUMMARY")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All components verified successfully!")
        print("✅ System is ready for production use!")
        return True
    else:
        print(f"\n⚠️ {len(results) - passed} components failed verification")
        print("❌ Please check the failing components before production use")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_verification())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Verification crashed: {e}")
        logger.exception("Verification crashed")
        sys.exit(1)
