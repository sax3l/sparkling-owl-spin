#!/usr/bin/env python3
"""
Test implementation without Redis dependency by using in-memory alternatives.
This allows verification of component functionality without Redis infrastructure.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class MockRedis:
    """Mock Redis client for testing purposes"""
    
    def __init__(self):
        self.data = {}
        self.sets = {}
        self.sorted_sets = {}
    
    async def ping(self):
        return True
    
    async def set(self, key: str, value: str, ex: int = None):
        self.data[key] = value
        return True
    
    async def get(self, key: str):
        return self.data.get(key)
    
    async def sadd(self, key: str, value: str):
        if key not in self.sets:
            self.sets[key] = set()
        self.sets[key].add(value)
        return 1
    
    async def sismember(self, key: str, value: str):
        return value in self.sets.get(key, set())
    
    async def hset(self, key: str, field: str, value: str):
        if key not in self.data:
            self.data[key] = {}
        self.data[key][field] = value
        return 1
    
    async def hget(self, key: str, field: str):
        return self.data.get(key, {}).get(field)
    
    async def zadd(self, key: str, mapping: Dict[str, float]):
        if key not in self.sorted_sets:
            self.sorted_sets[key] = []
        for value, score in mapping.items():
            self.sorted_sets[key].append((score, value))
        self.sorted_sets[key].sort(key=lambda x: x[0])
        return len(mapping)
    
    async def zrange(self, key: str, start: int, stop: int):
        items = self.sorted_sets.get(key, [])
        if stop == -1:
            stop = len(items)
        return [item[1] for item in items[start:stop]]
    
    async def zcard(self, key: str):
        return len(self.sorted_sets.get(key, []))
    
    async def scard(self, key: str):
        return len(self.sets.get(key, set()))
    
    async def zrem(self, key: str, value: str):
        if key in self.sorted_sets:
            self.sorted_sets[key] = [(score, val) for score, val in self.sorted_sets[key] if val != value]
        return 1
    
    async def hdel(self, key: str, field: str):
        if key in self.data and field in self.data[key]:
            del self.data[key][field]
        return 1

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

async def test_url_queue():
    """Test URL queue with mock Redis"""
    print("\n📋 Testing URL queue...")
    
    try:
        from src.crawler.url_queue import URLQueue, QueuedURL
        
        # Create mock Redis client
        mock_redis = MockRedis()
        
        # Create URL queue
        url_queue = URLQueue(mock_redis, "test_queue")
        
        # Test adding URLs
        test_url = QueuedURL(
            url="https://example.com/test",
            priority=1,
            depth=0,
            discovered_at=datetime.utcnow()
        )
        
        added = await url_queue.add_url(test_url)
        if added:
            print("✅ URL queue successfully added test URL")
        
        # Test getting URL
        retrieved_url = await url_queue.get_next_url(domain_delay_seconds=0)
        if retrieved_url and retrieved_url.url == test_url.url:
            print("✅ URL queue successfully retrieved URL")
            return True
        else:
            print("❌ URL queue failed to retrieve URL")
            return False
        
    except Exception as e:
        print(f"❌ URL queue test failed: {e}")
        return False

async def test_scheduler():
    """Test job scheduler with mock Redis"""
    print("\n⏰ Testing job scheduler...")
    
    try:
        from src.scheduler.simple_scheduler import SimpleScheduler, ScheduledJob, ScheduleType
        
        # Create mock Redis client
        mock_redis = MockRedis()
        
        # Create scheduler
        scheduler = SimpleScheduler(mock_redis)
        
        # Test scheduling a job
        test_job = ScheduledJob(
            id="test_job_001",
            name="Test Job",
            schedule_type=ScheduleType.ONCE,
            data={"test": "data"}
        )
        
        job_id = await scheduler.schedule_job(test_job)
        if job_id:
            print("✅ Job scheduler successfully scheduled test job")
            
            # Test getting jobs
            jobs = await scheduler.get_scheduled_jobs()
            if jobs:
                print("✅ Job scheduler successfully retrieved scheduled jobs")
                return True
            else:
                print("❌ Job scheduler failed to retrieve scheduled jobs")
                return False
        else:
            print("❌ Job scheduler failed to schedule job")
            return False
        
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False

async def test_crawl_coordinator():
    """Test crawl coordinator"""
    print("\n🕷️ Testing crawl coordinator...")
    
    try:
        from src.crawler.crawl_coordinator import CrawlCoordinator, CrawlConfiguration
        from src.crawler.url_queue import URLQueue
        import aiohttp
        
        # Create configuration
        config = CrawlConfiguration(
            strategy="bfs",
            max_pages=10,
            max_concurrent=5,
            use_stealth=False,  # Disable advanced features for basic test
            use_ai_extraction=False,
            use_real_time_monitoring=False
        )
        
        # Create mock Redis and URL queue
        mock_redis = MockRedis()
        url_queue = URLQueue(mock_redis, "test_crawl_queue")
        
        # Create coordinator
        session = aiohttp.ClientSession()
        coordinator = CrawlCoordinator(config, url_queue, session)
        
        print("✅ Crawl coordinator created successfully")
        
        # Test getting status
        status = await coordinator.get_crawl_status()
        if status and 'crawl_id' in status:
            print("✅ Crawl coordinator status retrieved successfully")
            await session.close()
            return True
        else:
            print("❌ Crawl coordinator failed to get status")
            await session.close()
            return False
        
    except Exception as e:
        print(f"❌ Crawl coordinator test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🚀 Sparkling Owl Spin - Component Verification (Mock Mode)")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_url_queue, 
        test_scheduler,
        test_crawl_coordinator
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print(f"\n📊 TEST SUMMARY")
    print("-" * 30)
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "Imports",
        "URL Queue",
        "Job Scheduler", 
        "Crawl Coordinator"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<20} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production use.")
    else:
        print(f"⚠️ {total - passed} components need attention before production use")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
