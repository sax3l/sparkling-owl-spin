"""
Unit tests för SOS Scheduler

Testar async job scheduling, queue management, och worker coordination.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta

from sos.scheduler.manager import SchedulerManager, JobStatus, ScheduledJob


class TestSchedulerManager:
    """Test suite för SchedulerManager"""
    
    @pytest.fixture
    def scheduler(self):
        """Skapa scheduler för testing"""
        return SchedulerManager(max_workers=2)
        
    @pytest.fixture
    def mock_crawl_engine(self):
        """Mock crawl engine"""
        engine = AsyncMock()
        return engine
        
    def test_scheduler_initialization(self):
        """Test skapande av SchedulerManager"""
        scheduler = SchedulerManager(max_workers=5)
        
        assert scheduler.max_workers == 5
        assert len(scheduler.job_queue) == 0
        assert len(scheduler.running_jobs) == 0
        assert len(scheduler.completed_jobs) == 0
        
    @pytest.mark.asyncio
    async def test_submit_single_job(self, scheduler, mock_crawl_engine):
        """Test submission av ett enda job"""
        
        # Mock job
        job_config = {
            "id": "test-job-1",
            "start_urls": ["https://example.com"],
            "max_pages": 10
        }
        
        job_id = await scheduler.submit_job(job_config, mock_crawl_engine)
        
        assert job_id == "test-job-1"
        assert len(scheduler.job_queue) == 1
        
        # Verifiera job properties
        scheduled_job = scheduler.job_queue[0]
        assert scheduled_job.id == "test-job-1"
        assert scheduled_job.status == JobStatus.QUEUED
        assert scheduled_job.crawl_engine == mock_crawl_engine
        
    @pytest.mark.asyncio
    async def test_run_single_job(self, scheduler, mock_crawl_engine):
        """Test körning av ett enda job"""
        
        # Mock crawl results
        mock_results = [
            Mock(url="https://example.com", status_code=200, content="Test content")
        ]
        mock_crawl_engine.crawl.return_value = mock_results
        
        # Submit job
        job_config = {
            "id": "test-job-1",
            "start_urls": ["https://example.com"],
            "max_pages": 1
        }
        
        job_id = await scheduler.submit_job(job_config, mock_crawl_engine)
        
        # Starta scheduler
        scheduler_task = asyncio.create_task(scheduler.start())
        
        # Vänta lite för att job ska processas
        await asyncio.sleep(0.1)
        
        # Stoppa scheduler
        await scheduler.stop()
        await scheduler_task
        
        # Verifiera att job kördes
        assert len(scheduler.completed_jobs) == 1
        completed_job = scheduler.completed_jobs[0]
        assert completed_job.id == job_id
        assert completed_job.status == JobStatus.COMPLETED
        assert len(completed_job.results) == 1
        
    @pytest.mark.asyncio
    async def test_concurrent_job_execution(self, mock_crawl_engine):
        """Test concurrent execution av flera jobb"""
        
        scheduler = SchedulerManager(max_workers=2)  # 2 workers
        
        # Mock som tar tid att köra
        async def slow_crawl(job):
            await asyncio.sleep(0.1)
            return [Mock(url=job.start_urls[0], status_code=200)]
            
        mock_crawl_engine.crawl.side_effect = slow_crawl
        
        # Submit flera jobb
        job_configs = [
            {"id": f"job-{i}", "start_urls": [f"https://example{i}.com"], "max_pages": 1}
            for i in range(3)
        ]
        
        for config in job_configs:
            await scheduler.submit_job(config, mock_crawl_engine)
            
        assert len(scheduler.job_queue) == 3
        
        # Starta scheduler
        start_time = asyncio.get_event_loop().time()
        scheduler_task = asyncio.create_task(scheduler.start())
        
        # Vänta tills alla jobb är klara
        while len(scheduler.completed_jobs) < 3:
            await asyncio.sleep(0.01)
            
        end_time = asyncio.get_event_loop().time()
        
        await scheduler.stop()
        await scheduler_task
        
        # Med 2 workers ska 3 jobb ta mindre tid än sekventiellt
        sequential_time = 3 * 0.1  # 3 jobb * 0.1s vardera
        actual_time = end_time - start_time
        
        # Ska vara snabbare än sekventiell execution (med marginal för overhead)
        assert actual_time < sequential_time * 0.8
        assert len(scheduler.completed_jobs) == 3
        
    @pytest.mark.asyncio
    async def test_job_priority_handling(self, scheduler, mock_crawl_engine):
        """Test hantering av job prioritet"""
        
        mock_crawl_engine.crawl.return_value = [Mock()]
        
        # Submit jobb med olika prioriteter
        await scheduler.submit_job({
            "id": "low-priority",
            "start_urls": ["https://example.com"],
            "priority": 1
        }, mock_crawl_engine)
        
        await scheduler.submit_job({
            "id": "high-priority", 
            "start_urls": ["https://example.com"],
            "priority": 10
        }, mock_crawl_engine)
        
        await scheduler.submit_job({
            "id": "medium-priority",
            "start_urls": ["https://example.com"], 
            "priority": 5
        }, mock_crawl_engine)
        
        # Jobs ska sorteras efter prioritet
        sorted_jobs = sorted(scheduler.job_queue, key=lambda j: j.priority, reverse=True)
        
        assert sorted_jobs[0].id == "high-priority"
        assert sorted_jobs[1].id == "medium-priority" 
        assert sorted_jobs[2].id == "low-priority"
        
    @pytest.mark.asyncio
    async def test_job_error_handling(self, scheduler, mock_crawl_engine):
        """Test error handling under job execution"""
        
        # Mock som kastar exception
        mock_crawl_engine.crawl.side_effect = Exception("Crawl failed")
        
        job_config = {
            "id": "error-job",
            "start_urls": ["https://example.com"],
            "max_pages": 1
        }
        
        await scheduler.submit_job(job_config, mock_crawl_engine)
        
        # Starta och stoppa scheduler
        scheduler_task = asyncio.create_task(scheduler.start())
        await asyncio.sleep(0.1)
        await scheduler.stop()
        await scheduler_task
        
        # Job ska markeras som failed
        assert len(scheduler.completed_jobs) == 1
        failed_job = scheduler.completed_jobs[0]
        assert failed_job.status == JobStatus.FAILED
        assert "Crawl failed" in failed_job.error_message
        
    @pytest.mark.asyncio
    async def test_get_job_status(self, scheduler, mock_crawl_engine):
        """Test hämtning av job status"""
        
        mock_crawl_engine.crawl.return_value = []
        
        # Submit job
        job_id = await scheduler.submit_job({
            "id": "status-test-job",
            "start_urls": ["https://example.com"]
        }, mock_crawl_engine)
        
        # Check initial status
        status = scheduler.get_job_status(job_id)
        assert status == JobStatus.QUEUED
        
        # Start processing
        scheduler_task = asyncio.create_task(scheduler.start())
        await asyncio.sleep(0.1)
        
        # Status ska ha ändrats
        final_status = scheduler.get_job_status(job_id)
        assert final_status in [JobStatus.RUNNING, JobStatus.COMPLETED]
        
        await scheduler.stop()
        await scheduler_task
        
    @pytest.mark.asyncio
    async def test_get_job_results(self, scheduler, mock_crawl_engine):
        """Test hämtning av job results"""
        
        expected_results = [
            Mock(url="https://example.com/page1", status_code=200),
            Mock(url="https://example.com/page2", status_code=200)
        ]
        mock_crawl_engine.crawl.return_value = expected_results
        
        job_id = await scheduler.submit_job({
            "id": "results-test-job", 
            "start_urls": ["https://example.com"]
        }, mock_crawl_engine)
        
        # Innan processing - inga results
        results = scheduler.get_job_results(job_id)
        assert results == []
        
        # Run job
        scheduler_task = asyncio.create_task(scheduler.start())
        await asyncio.sleep(0.1)
        await scheduler.stop()
        await scheduler_task
        
        # Efter processing - ska ha results
        results = scheduler.get_job_results(job_id)
        assert len(results) == 2
        assert results == expected_results
        
    def test_job_queue_capacity(self, scheduler):
        """Test job queue capacity management"""
        
        # Default capacity
        assert scheduler.max_queue_size == 1000  # Default
        
        # Custom capacity
        limited_scheduler = SchedulerManager(max_workers=1, max_queue_size=2)
        assert limited_scheduler.max_queue_size == 2


class TestScheduledJob:
    """Test suite för ScheduledJob"""
    
    def test_scheduled_job_creation(self):
        """Test skapande av ScheduledJob"""
        
        job_config = {
            "id": "test-job",
            "start_urls": ["https://example.com"],
            "max_pages": 50,
            "priority": 5
        }
        
        mock_engine = Mock()
        
        job = ScheduledJob(
            id="test-job",
            config=job_config,
            crawl_engine=mock_engine,
            priority=5
        )
        
        assert job.id == "test-job"
        assert job.config == job_config
        assert job.crawl_engine == mock_engine
        assert job.priority == 5
        assert job.status == JobStatus.QUEUED
        assert job.created_at is not None
        assert job.results == []
        
    def test_job_status_transitions(self):
        """Test job status transitions"""
        
        job = ScheduledJob("test", {}, Mock())
        
        # Initial state
        assert job.status == JobStatus.QUEUED
        
        # Transition to running
        job.status = JobStatus.RUNNING
        assert job.status == JobStatus.RUNNING
        assert job.started_at is None  # Should be set externally
        
        # Transition to completed
        job.status = JobStatus.COMPLETED
        assert job.status == JobStatus.COMPLETED
        
    def test_job_priority_default(self):
        """Test default job priority"""
        
        job = ScheduledJob("test", {}, Mock())
        assert job.priority == 0  # Default priority
        
        high_priority_job = ScheduledJob("test", {}, Mock(), priority=10)
        assert high_priority_job.priority == 10


class TestJobStatus:
    """Test suite för JobStatus enum"""
    
    def test_job_status_values(self):
        """Test JobStatus enum values"""
        
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.RUNNING.value == "running" 
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"
        
    def test_job_status_comparison(self):
        """Test JobStatus comparison och equality"""
        
        assert JobStatus.QUEUED == JobStatus.QUEUED
        assert JobStatus.QUEUED != JobStatus.RUNNING
        
        # String comparison
        assert JobStatus.QUEUED.value == "queued"
        assert JobStatus.RUNNING.value == "running"
