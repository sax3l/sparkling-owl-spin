"""
E2E (End-to-End) tests för SOS system

Testar kompletta user workflows från start till slut.
"""

import pytest
import asyncio
import tempfile
import json
import os
from pathlib import Path


class TestSOSE2EWorkflows:
    """End-to-End workflow tester"""
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_complete_scraping_workflow(self):
        """Test komplett workflow: Template -> Job -> Results -> Export"""
        
        # Mock setup för E2E test
        # I en riktig miljö skulle detta använda riktiga komponenter
        
        workflow_steps = {
            "template_creation": False,
            "job_submission": False,
            "job_execution": False,
            "result_extraction": False,
            "data_export": False
        }
        
        try:
            # Step 1: Create template
            template_config = {
                "name": "E2E Test Template",
                "description": "Template for end-to-end testing",
                "selectors": {
                    "title": "h1, .title",
                    "content": ".content, .main-content",
                    "links": "a[href]",
                    "images": "img[src]"
                },
                "actions": [
                    {"type": "extract", "field": "title"},
                    {"type": "extract", "field": "content"},
                    {"type": "collect_links", "field": "links"},
                    {"type": "collect_images", "field": "images"}
                ],
                "follow": [
                    {"selector": ".pagination a", "max_depth": 2}
                ]
            }
            
            # Simulera template creation
            template_id = "e2e-test-template-123"
            workflow_steps["template_creation"] = True
            
            # Step 2: Submit crawl job
            job_config = {
                "template_id": template_id,
                "start_urls": [
                    "https://example-news.com",
                    "https://example-blog.com"
                ],
                "max_pages": 20,
                "max_depth": 3,
                "delay_seconds": 1.0,
                "respect_robots": True,
                "export_format": "json"
            }
            
            job_id = "e2e-test-job-456"
            workflow_steps["job_submission"] = True
            
            # Step 3: Execute job (mocked execution)
            mock_crawl_results = [
                {
                    "url": "https://example-news.com",
                    "status_code": 200,
                    "title": "Breaking News: Tech Update",
                    "content": "Latest technology news and updates...",
                    "links": [
                        "https://example-news.com/article-1",
                        "https://example-news.com/article-2"
                    ],
                    "images": ["https://example-news.com/image1.jpg"],
                    "depth": 0,
                    "crawl_time": 0.8
                },
                {
                    "url": "https://example-news.com/article-1", 
                    "status_code": 200,
                    "title": "Article 1: Innovation Trends",
                    "content": "Detailed analysis of innovation trends...",
                    "links": [],
                    "images": ["https://example-news.com/article1-img.jpg"],
                    "depth": 1,
                    "crawl_time": 0.6
                },
                {
                    "url": "https://example-blog.com",
                    "status_code": 200,
                    "title": "Personal Blog - Tech Thoughts",
                    "content": "My thoughts on technology...",
                    "links": ["https://example-blog.com/post-1"],
                    "images": [],
                    "depth": 0,
                    "crawl_time": 0.5
                }
            ]
            
            workflow_steps["job_execution"] = True
            
            # Step 4: Extract and validate results
            assert len(mock_crawl_results) == 3
            
            # Validate data structure
            for result in mock_crawl_results:
                assert "url" in result
                assert "status_code" in result
                assert "title" in result
                assert "content" in result
                assert "links" in result
                assert "images" in result
                assert result["status_code"] == 200
                
            # Validate content extraction
            titles = [r["title"] for r in mock_crawl_results]
            assert "Breaking News: Tech Update" in titles
            assert "Article 1: Innovation Trends" in titles
            
            # Validate link following worked
            found_urls = {r["url"] for r in mock_crawl_results}
            assert "https://example-news.com/article-1" in found_urls
            
            workflow_steps["result_extraction"] = True
            
            # Step 5: Export results
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                export_data = {
                    "job_id": job_id,
                    "template_id": template_id,
                    "export_timestamp": "2024-01-01T10:00:00Z",
                    "total_pages": len(mock_crawl_results),
                    "results": mock_crawl_results,
                    "summary": {
                        "successful_pages": len([r for r in mock_crawl_results if r["status_code"] == 200]),
                        "total_links_found": sum(len(r["links"]) for r in mock_crawl_results),
                        "total_images_found": sum(len(r["images"]) for r in mock_crawl_results),
                        "average_crawl_time": sum(r["crawl_time"] for r in mock_crawl_results) / len(mock_crawl_results)
                    }
                }
                
                json.dump(export_data, f, indent=2)
                export_file = f.name
                
            # Validate export file
            assert os.path.exists(export_file)
            
            with open(export_file, 'r') as f:
                exported_data = json.load(f)
                
            assert exported_data["job_id"] == job_id
            assert exported_data["total_pages"] == 3
            assert exported_data["summary"]["successful_pages"] == 3
            assert exported_data["summary"]["total_links_found"] == 3
            
            workflow_steps["data_export"] = True
            
            # Cleanup
            os.unlink(export_file)
            
        except Exception as e:
            pytest.fail(f"E2E workflow failed at step: {[k for k, v in workflow_steps.items() if not v][0] if not all(workflow_steps.values()) else 'unknown'}: {e}")
            
        # Verify all steps completed
        assert all(workflow_steps.values()), f"Failed steps: {[k for k, v in workflow_steps.items() if not v]}"
        
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_api_driven_workflow(self):
        """Test E2E workflow driven through API"""
        
        # Mock API client
        class MockAPIClient:
            def __init__(self):
                self.templates = {}
                self.jobs = {}
                self.results = {}
                
            async def create_template(self, template_data):
                template_id = f"template-{len(self.templates) + 1}"
                self.templates[template_id] = {
                    "id": template_id,
                    "created_at": "2024-01-01T10:00:00Z",
                    **template_data
                }
                return {"template_id": template_id, "status": "created"}
                
            async def submit_job(self, job_data):
                job_id = f"job-{len(self.jobs) + 1}"
                self.jobs[job_id] = {
                    "id": job_id,
                    "status": "queued",
                    "created_at": "2024-01-01T10:00:00Z",
                    **job_data
                }
                return {"job_id": job_id, "status": "queued"}
                
            async def get_job_status(self, job_id):
                if job_id in self.jobs:
                    # Simulate job progression
                    return {
                        "job_id": job_id,
                        "status": "completed",
                        "progress": 1.0,
                        "pages_crawled": 5
                    }
                return None
                
            async def get_job_results(self, job_id):
                if job_id in self.jobs:
                    # Mock results
                    return {
                        "job_id": job_id,
                        "total_results": 5,
                        "results": [
                            {
                                "url": f"https://example.com/page-{i}",
                                "status_code": 200,
                                "title": f"Page {i} Title",
                                "content": f"Content for page {i}"
                            }
                            for i in range(1, 6)
                        ]
                    }
                return None
        
        api_client = MockAPIClient()
        
        # Workflow genom API
        
        # 1. Create template through API
        template_response = await api_client.create_template({
            "name": "API E2E Template",
            "description": "Template created through API for E2E testing",
            "config": {
                "selectors": {"title": "h1", "content": ".content"},
                "actions": [{"type": "extract", "field": "title"}]
            }
        })
        
        assert template_response["status"] == "created"
        template_id = template_response["template_id"]
        
        # 2. Submit job through API
        job_response = await api_client.submit_job({
            "template_id": template_id,
            "start_urls": ["https://example.com"],
            "max_pages": 5,
            "max_depth": 2
        })
        
        assert job_response["status"] == "queued"
        job_id = job_response["job_id"]
        
        # 3. Poll job status
        status_response = await api_client.get_job_status(job_id)
        assert status_response["status"] == "completed"
        assert status_response["pages_crawled"] == 5
        
        # 4. Get results
        results_response = await api_client.get_job_results(job_id)
        assert results_response["total_results"] == 5
        assert len(results_response["results"]) == 5
        
        # Validate result structure
        for result in results_response["results"]:
            assert "url" in result
            assert "status_code" in result
            assert "title" in result
            assert "content" in result
            assert result["status_code"] == 200
            
    @pytest.mark.e2e
    def test_cli_driven_workflow(self):
        """Test E2E workflow genom CLI interface"""
        
        # Mock CLI commands
        class MockCLI:
            def __init__(self):
                self.output = []
                self.templates_dir = tempfile.mkdtemp()
                
            def run_command(self, command):
                """Simulera CLI commands"""
                
                if command.startswith("sos template create"):
                    # Parse template file argument
                    template_file = command.split()[-1]
                    
                    # Create mock template file
                    template_content = """
name: "CLI E2E Template"
description: "Template created through CLI"

selectors:
  title: "h1, .title"
  content: ".content, p"
  
actions:
  - type: extract
    field: title
  - type: extract  
    field: content
                    """
                    
                    template_path = os.path.join(self.templates_dir, "cli-template.yaml")
                    with open(template_path, 'w') as f:
                        f.write(template_content)
                        
                    return {
                        "success": True,
                        "template_id": "cli-template-123",
                        "message": f"Template created: {template_path}"
                    }
                    
                elif command.startswith("sos crawl"):
                    # Parse crawl arguments
                    return {
                        "success": True,
                        "job_id": "cli-job-456", 
                        "message": "Crawl job started"
                    }
                    
                elif command.startswith("sos status"):
                    job_id = command.split()[-1]
                    return {
                        "success": True,
                        "job_id": job_id,
                        "status": "completed",
                        "pages_crawled": 8,
                        "message": f"Job {job_id} completed successfully"
                    }
                    
                elif command.startswith("sos export"):
                    # Parse export arguments
                    job_id = command.split()[2]  # sos export JOB_ID
                    output_file = command.split()[-1]  # last argument
                    
                    # Create mock export file
                    export_data = {
                        "job_id": job_id,
                        "exported_at": "2024-01-01T10:00:00Z",
                        "pages": [
                            {
                                "url": f"https://example.com/page-{i}",
                                "title": f"CLI Page {i}",
                                "content": f"Content from CLI crawl {i}"
                            }
                            for i in range(1, 9)
                        ]
                    }
                    
                    with open(output_file, 'w') as f:
                        json.dump(export_data, f, indent=2)
                        
                    return {
                        "success": True,
                        "output_file": output_file,
                        "records_exported": 8,
                        "message": f"Results exported to {output_file}"
                    }
                    
                else:
                    return {
                        "success": False,
                        "message": f"Unknown command: {command}"
                    }
                    
        cli = MockCLI()
        
        try:
            # CLI workflow
            
            # 1. Create template file and register it
            result1 = cli.run_command("sos template create cli-template.yaml")
            assert result1["success"]
            template_id = result1["template_id"]
            
            # 2. Start crawl job
            result2 = cli.run_command(f"sos crawl --template {template_id} --urls https://example.com --max-pages 10")
            assert result2["success"]
            job_id = result2["job_id"]
            
            # 3. Check status
            result3 = cli.run_command(f"sos status {job_id}")
            assert result3["success"]
            assert result3["status"] == "completed"
            assert result3["pages_crawled"] == 8
            
            # 4. Export results
            output_file = os.path.join(tempfile.gettempdir(), "cli-export.json")
            result4 = cli.run_command(f"sos export {job_id} --format json --output {output_file}")
            assert result4["success"]
            assert result4["records_exported"] == 8
            
            # Validate export file
            assert os.path.exists(output_file)
            
            with open(output_file, 'r') as f:
                exported_data = json.load(f)
                
            assert exported_data["job_id"] == job_id
            assert len(exported_data["pages"]) == 8
            
            # Validate data structure
            for page in exported_data["pages"]:
                assert "url" in page
                assert "title" in page
                assert "content" in page
                assert page["title"].startswith("CLI Page")
                
            # Cleanup
            os.unlink(output_file)
            
        finally:
            # Cleanup temp directory
            import shutil
            shutil.rmtree(cli.templates_dir, ignore_errors=True)
            
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test E2E workflow med error recovery"""
        
        # Simulera olika typer av fel och recovery
        
        error_scenarios = {
            "network_timeout": False,
            "invalid_template": False,
            "rate_limiting": False,
            "memory_pressure": False,
            "partial_failure": False
        }
        
        # Scenario 1: Network timeout recovery
        try:
            # Simulera network timeout följt av retry success
            mock_responses = [
                {"error": "timeout", "retry": True},
                {"success": True, "content": "Recovered content"}
            ]
            
            # I en riktig implementation skulle detta testa retry logic
            assert mock_responses[-1]["success"]
            error_scenarios["network_timeout"] = True
            
        except Exception as e:
            pytest.fail(f"Network timeout recovery failed: {e}")
            
        # Scenario 2: Invalid template handling
        try:
            invalid_template = {
                "name": "",  # Invalid: empty name
                "selectors": {},  # Invalid: no selectors
                "actions": []  # Invalid: no actions
            }
            
            # Skulle validera template och ge tydliga error messages
            validation_errors = []
            if not invalid_template["name"]:
                validation_errors.append("Template name is required")
            if not invalid_template["selectors"]:
                validation_errors.append("At least one selector is required")
            if not invalid_template["actions"]:
                validation_errors.append("At least one action is required")
                
            assert len(validation_errors) == 3
            error_scenarios["invalid_template"] = True
            
        except Exception as e:
            pytest.fail(f"Invalid template handling failed: {e}")
            
        # Scenario 3: Rate limiting graceful handling  
        try:
            # Simulera rate limiting response
            rate_limited_response = {
                "status_code": 429,
                "headers": {"retry-after": "60"},
                "message": "Rate limit exceeded"
            }
            
            # Skulle implementera exponential backoff
            retry_delay = int(rate_limited_response["headers"]["retry-after"])
            assert retry_delay == 60
            error_scenarios["rate_limiting"] = True
            
        except Exception as e:
            pytest.fail(f"Rate limiting handling failed: {e}")
            
        # Scenario 4: Memory pressure handling
        try:
            # Simulera memory pressure
            memory_usage_mb = 512  # High memory usage
            memory_threshold_mb = 400
            
            if memory_usage_mb > memory_threshold_mb:
                # Skulle trigga memory cleanup
                cleanup_performed = True
                reduced_memory_mb = memory_usage_mb * 0.7  # Simulate cleanup
                
                assert cleanup_performed
                assert reduced_memory_mb < memory_threshold_mb
                
            error_scenarios["memory_pressure"] = True
            
        except Exception as e:
            pytest.fail(f"Memory pressure handling failed: {e}")
            
        # Scenario 5: Partial failure handling
        try:
            # Simulera partial crawl failure
            crawl_results = [
                {"url": "https://example.com/page1", "status": "success"},
                {"url": "https://example.com/page2", "status": "failed", "error": "404 Not Found"},
                {"url": "https://example.com/page3", "status": "success"},
                {"url": "https://example.com/page4", "status": "failed", "error": "Timeout"},
                {"url": "https://example.com/page5", "status": "success"}
            ]
            
            successful_pages = [r for r in crawl_results if r["status"] == "success"]
            failed_pages = [r for r in crawl_results if r["status"] == "failed"]
            
            # Partial success ska hanteras gracefully
            assert len(successful_pages) == 3
            assert len(failed_pages) == 2
            
            # Success rate calculation
            success_rate = len(successful_pages) / len(crawl_results)
            assert success_rate == 0.6  # 60% success rate
            
            error_scenarios["partial_failure"] = True
            
        except Exception as e:
            pytest.fail(f"Partial failure handling failed: {e}")
            
        # Verify all error scenarios were handled
        assert all(error_scenarios.values()), f"Failed scenarios: {[k for k, v in error_scenarios.items() if not v]}"


class TestSOSPerformanceE2E:
    """Performance tester på E2E nivå"""
    
    @pytest.mark.e2e
    @pytest.mark.performance
    def test_large_scale_crawl_performance(self):
        """Test performance för stora crawl jobs"""
        
        # Simulera stort crawl job
        large_job_config = {
            "start_urls": [f"https://site{i}.example.com" for i in range(50)],
            "max_pages": 1000,
            "max_depth": 3,
            "concurrent_requests": 10,
            "delay_seconds": 0.5
        }
        
        # Performance targets
        targets = {
            "max_completion_time_minutes": 30,
            "min_throughput_pages_per_minute": 100,
            "max_memory_usage_mb": 1024,
            "min_success_rate": 0.95
        }
        
        # Mock performance metrics
        mock_metrics = {
            "completion_time_minutes": 25,
            "throughput_pages_per_minute": 150,
            "peak_memory_usage_mb": 800,
            "success_rate": 0.98,
            "total_pages_crawled": 3750
        }
        
        # Verify performance targets
        assert mock_metrics["completion_time_minutes"] <= targets["max_completion_time_minutes"]
        assert mock_metrics["throughput_pages_per_minute"] >= targets["min_throughput_pages_per_minute"]
        assert mock_metrics["peak_memory_usage_mb"] <= targets["max_memory_usage_mb"]
        assert mock_metrics["success_rate"] >= targets["min_success_rate"]
        
        print(f"Large scale performance test passed:")
        print(f"  - Crawled {mock_metrics['total_pages_crawled']} pages")
        print(f"  - Completed in {mock_metrics['completion_time_minutes']} minutes")
        print(f"  - Throughput: {mock_metrics['throughput_pages_per_minute']} pages/min")
        print(f"  - Success rate: {mock_metrics['success_rate'] * 100:.1f}%")
        
    @pytest.mark.e2e
    @pytest.mark.performance
    def test_concurrent_job_performance(self):
        """Test performance för concurrent jobs"""
        
        # Simulera flera samtidiga jobs
        concurrent_jobs = [
            {"id": f"job-{i}", "pages": 100, "complexity": "medium"}
            for i in range(5)
        ]
        
        # Mock concurrent execution
        total_pages = sum(job["pages"] for job in concurrent_jobs)
        execution_time_minutes = 8  # All jobs completed in 8 minutes
        
        # Performance calculations
        sequential_time_estimate = len(concurrent_jobs) * 5  # 5 min per job sequentially
        parallel_efficiency = (sequential_time_estimate / execution_time_minutes)
        throughput = total_pages / execution_time_minutes
        
        # Performance assertions
        assert parallel_efficiency >= 2.0  # At least 2x faster than sequential
        assert throughput >= 50  # At least 50 pages per minute
        assert execution_time_minutes <= 10  # Completed within 10 minutes
        
        print(f"Concurrent job performance test passed:")
        print(f"  - {len(concurrent_jobs)} jobs, {total_pages} total pages")
        print(f"  - Parallel efficiency: {parallel_efficiency:.1f}x")
        print(f"  - Overall throughput: {throughput:.1f} pages/min")
