#!/usr/bin/env python3
"""
🚀 REVOLUTIONARY ULTIMATE INTEGRATED SYSTEM v4.0 🚀
====================================================

Den ultimata integrationen av alla högprioriterade komponenter:

🛡️ ANTI-BOT DEFENSE SYSTEM:
- Smart triage: requests → cloudscraper → FlareSolverr → undetected-chrome
- Automatisk CAPTCHA-lösning (2captcha, NopeCHA)
- TLS/JA3 fingerprinting med azuretls
- Intelligent retry och fallback logik

📄 CONTENT EXTRACTION PIPELINE:
- HTML → trafilatura (boilerplate removal, clean text)  
- PDF → Tika/PyMuPDF (layout, tables, OCR)
- Entity extraction (dates, amounts, measurements)
- Fuzzy deduplication med RapidFuzz

⚙️ INTELLIGENT CONFIGURATION:
- Per-domain policies (YAML-baserad)
- Quality control & monitoring  
- Rate limiting & performance tuning
- Feature flags & environment overrides

🎯 UNIFIED SCRAPING INTERFACE:
- Async/await support för high performance
- Comprehensive error handling & logging
- Real-time metrics & monitoring
- Production-ready architecture
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, AsyncIterator
from urllib.parse import urlparse, urljoin
import json
from pathlib import Path

# Import our revolutionary components
from .anti_bot_system import (
    RevolutionaryAntiBotSystem,
    AntiBotConfig,
    AntiDetectionMethod,
    CaptchaProvider,
    ScrapingResult
)

from .content_extraction_system import (
    RevolutionaryContentExtractor,
    ExtractionConfig,
    ExtractedContent,
    ContentType
)

from .system_configuration import (
    ConfigurationManager,
    GlobalConfig,
    DomainPolicy,
    get_config,
    get_domain_policy,
    setup_logging
)

# Core libraries
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass 
class ScrapingTask:
    """Individual scraping task"""
    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    priority: int = 0
    max_retries: int = 3
    timeout: int = 30
    
    # Policy overrides
    force_engine: Optional[str] = None
    force_extraction_method: Optional[str] = None
    
    # Metadata
    task_id: Optional[str] = None
    created_at: Optional[datetime] = None
    domain: Optional[str] = None


@dataclass
class ScrapingTaskResult:
    """Complete scraping task result"""
    task: ScrapingTask
    success: bool = False
    
    # Anti-bot results
    scraping_result: Optional[ScrapingResult] = None
    
    # Content extraction results
    extracted_content: Optional[ExtractedContent] = None
    
    # Performance metrics
    total_time: float = 0.0
    attempts: int = 0
    
    # Quality assessment
    quality_score: float = 0.0
    is_duplicate: bool = False
    
    # Error handling
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    completed_at: Optional[datetime] = None


class RevolutionaryUltimateSystem:
    """
    Revolutionary Ultimate Integrated Scraping System
    
    Combines all components into a unified, production-ready system:
    - Anti-bot defense with intelligent escalation
    - Advanced content extraction with quality scoring
    - Per-domain policy management
    - Real-time monitoring & metrics
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_manager = ConfigurationManager(config_path)
        self.config = self.config_manager.load_config()
        
        # Setup logging
        setup_logging(self.config)
        
        # Initialize components
        self.anti_bot_system = None
        self.content_extractor = None
        
        # Performance tracking
        self.metrics = {
            'tasks_processed': 0,
            'tasks_successful': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0,
            'average_quality_score': 0.0,
            'duplicates_detected': 0,
            'methods_used': {},
            'domains_processed': set(),
            'errors': {}
        }
        
        # Task queue (simple in-memory for now)
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: List[ScrapingTaskResult] = []
        
        logger.info(f"🚀 Revolutionary Ultimate System v{self.config.version} initialized")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_components()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._cleanup_components()
    
    async def _initialize_components(self):
        """Initialize all system components"""
        logger.info("⚙️  Initializing system components...")
        
        # Initialize anti-bot system
        anti_bot_config = AntiBotConfig(
            flaresolverr_url=self.config.flaresolverr_url,
            twocaptcha_api_key=self.config.twocaptcha_api_key,
            nopecha_api_key=self.config.nopecha_api_key,
            captcha_provider=CaptchaProvider.AUTO if self.config.twocaptcha_api_key else CaptchaProvider.NONE
        )
        
        self.anti_bot_system = RevolutionaryAntiBotSystem(anti_bot_config)
        
        # Initialize content extractor
        extraction_config = ExtractionConfig(
            tika_server_url=self.config.tika_server_url,
            extract_entities=self.config.features.get('entity_recognition', True),
            enable_deduplication=self.config.content_deduplication,
            similarity_threshold=self.config.similarity_threshold
        )
        
        self.content_extractor = RevolutionaryContentExtractor(extraction_config)
        
        logger.info("✅ All components initialized successfully")
    
    async def _cleanup_components(self):
        """Cleanup system components"""
        if self.anti_bot_system:
            await self.anti_bot_system.__aexit__(None, None, None)
        
        logger.info("🧹 System components cleaned up")
    
    def add_task(self, url: str, **kwargs) -> str:
        """Add scraping task to queue"""
        
        # Parse domain from URL
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Create task
        task = ScrapingTask(
            url=url,
            domain=domain,
            task_id=f"task_{int(time.time() * 1000)}_{len(self.results)}",
            created_at=datetime.now(),
            **kwargs
        )
        
        # Add to queue (non-blocking)
        self.task_queue.put_nowait(task)
        
        logger.info(f"📝 Added task {task.task_id} for {domain}")
        return task.task_id
    
    def add_tasks(self, urls: List[str], **kwargs) -> List[str]:
        """Add multiple tasks to queue"""
        task_ids = []
        for url in urls:
            task_id = self.add_task(url, **kwargs)
            task_ids.append(task_id)
        return task_ids
    
    async def process_task(self, task: ScrapingTask) -> ScrapingTaskResult:
        """Process individual scraping task"""
        
        start_time = time.time()
        result = ScrapingTaskResult(task=task)
        
        try:
            logger.info(f"🔄 Processing task {task.task_id}: {task.url}")
            
            # Get domain policy
            domain_policy = self.config_manager.get_domain_policy(task.domain)
            
            # Step 1: Anti-bot scraping
            scraping_result = await self._perform_anti_bot_scraping(task, domain_policy)
            result.scraping_result = scraping_result
            result.attempts = scraping_result.attempts if scraping_result else 0
            
            if not scraping_result or not scraping_result.success:
                result.error = scraping_result.error if scraping_result else "Anti-bot scraping failed"
                return result
            
            # Step 2: Content extraction
            extracted_content = await self._perform_content_extraction(
                scraping_result, task, domain_policy
            )
            result.extracted_content = extracted_content
            
            if not extracted_content or not extracted_content.success:
                result.error = extracted_content.error if extracted_content else "Content extraction failed"
                return result
            
            # Step 3: Quality assessment
            result.quality_score = extracted_content.quality_score
            result.is_duplicate = any(
                "duplicate" in warning.lower() 
                for warning in extracted_content.warnings
            )
            
            # Success criteria
            min_quality = domain_policy.min_quality
            if result.quality_score >= min_quality:
                result.success = True
                logger.info(f"✅ Task {task.task_id} completed successfully "
                           f"(quality: {result.quality_score:.2f})")
            else:
                result.error = f"Quality score {result.quality_score:.2f} below threshold {min_quality}"
                logger.warning(f"⚠️  Task {task.task_id} failed quality check")
            
        except Exception as e:
            result.error = f"Task processing error: {str(e)}"
            logger.error(f"❌ Task {task.task_id} failed: {e}")
        
        finally:
            result.total_time = time.time() - start_time
            result.completed_at = datetime.now()
            
            # Update metrics
            self._update_metrics(result)
        
        return result
    
    async def _perform_anti_bot_scraping(self, task: ScrapingTask, 
                                       domain_policy: DomainPolicy) -> Optional[ScrapingResult]:
        """Perform anti-bot scraping based on domain policy"""
        
        try:
            # Override anti-bot config based on domain policy
            if domain_policy.engine != "auto":
                # Force specific method based on policy
                if domain_policy.engine == "requests":
                    method_priority = [AntiDetectionMethod.REQUESTS]
                elif domain_policy.engine == "cloudscraper":
                    method_priority = [AntiDetectionMethod.CLOUDSCRAPER]
                elif domain_policy.engine == "undetected_chrome":
                    method_priority = [AntiDetectionMethod.UNDETECTED_CHROME]
                elif domain_policy.engine == "playwright":
                    method_priority = [AntiDetectionMethod.PLAYWRIGHT_STEALTH]
                else:
                    method_priority = self.anti_bot_system.config.method_priority
                
                # Temporarily override method priority
                original_priority = self.anti_bot_system.config.method_priority
                self.anti_bot_system.config.method_priority = method_priority
            
            # Prepare headers
            headers = task.headers or {}
            if domain_policy.custom_headers:
                headers.update(domain_policy.custom_headers)
            
            # Perform scraping
            result = await self.anti_bot_system.scrape(
                url=task.url,
                method=task.method,
                headers=headers,
                data=task.data
            )
            
            # Restore original priority if changed
            if domain_policy.engine != "auto":
                self.anti_bot_system.config.method_priority = original_priority
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Anti-bot scraping failed: {e}")
            return None
    
    async def _perform_content_extraction(self, scraping_result: ScrapingResult,
                                        task: ScrapingTask, 
                                        domain_policy: DomainPolicy) -> Optional[ExtractedContent]:
        """Perform content extraction based on domain policy"""
        
        try:
            content = scraping_result.content
            if not content:
                return ExtractedContent(
                    success=False,
                    error="No content to extract"
                )
            
            # Force extraction method based on policy
            force_method = None
            if domain_policy.extract_html == "trafilatura":
                from .content_extraction_system import ExtractionMethod
                force_method = ExtractionMethod.TRAFILATURA
            elif domain_policy.extract_html == "beautifulsoup":
                from .content_extraction_system import ExtractionMethod
                force_method = ExtractionMethod.BEAUTIFULSOUP
            
            # Extract content
            result = await self.content_extractor.extract(
                content=content,
                url=task.url,
                content_type="text/html",  # Assume HTML for now
                force_method=force_method
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {e}")
            return ExtractedContent(
                success=False,
                error=f"Content extraction error: {str(e)}"
            )
    
    def _update_metrics(self, result: ScrapingTaskResult):
        """Update performance metrics"""
        self.metrics['tasks_processed'] += 1
        
        if result.success:
            self.metrics['tasks_successful'] += 1
        else:
            self.metrics['tasks_failed'] += 1
        
        self.metrics['total_processing_time'] += result.total_time
        
        if result.quality_score > 0:
            # Running average
            current_avg = self.metrics['average_quality_score']
            successful_tasks = self.metrics['tasks_successful']
            if successful_tasks > 1:
                self.metrics['average_quality_score'] = (
                    (current_avg * (successful_tasks - 1) + result.quality_score) / successful_tasks
                )
            else:
                self.metrics['average_quality_score'] = result.quality_score
        
        if result.is_duplicate:
            self.metrics['duplicates_detected'] += 1
        
        # Track methods used
        if result.scraping_result and result.scraping_result.method_used:
            method = result.scraping_result.method_used.value
            self.metrics['methods_used'][method] = self.metrics['methods_used'].get(method, 0) + 1
        
        # Track domains
        if result.task.domain:
            self.metrics['domains_processed'].add(result.task.domain)
        
        # Track errors
        if result.error:
            error_key = result.error[:50]  # Truncate for grouping
            self.metrics['errors'][error_key] = self.metrics['errors'].get(error_key, 0) + 1
    
    async def process_queue(self, max_concurrent: Optional[int] = None) -> List[ScrapingTaskResult]:
        """Process all tasks in queue concurrently"""
        
        concurrent_limit = max_concurrent or self.config.max_concurrent_domains
        
        logger.info(f"🔄 Processing queue with {concurrent_limit} concurrent tasks...")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def process_with_semaphore(task: ScrapingTask) -> ScrapingTaskResult:
            async with semaphore:
                return await self.process_task(task)
        
        # Collect all tasks
        tasks = []
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get_nowait()
                tasks.append(task)
            except asyncio.QueueEmpty:
                break
        
        if not tasks:
            logger.warning("⚠️  No tasks in queue")
            return []
        
        logger.info(f"📋 Processing {len(tasks)} tasks...")
        
        # Process all tasks concurrently
        results = await asyncio.gather(
            *[process_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Handle results and exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ScrapingTaskResult(
                    task=tasks[i],
                    success=False,
                    error=f"Processing exception: {str(result)}"
                )
                processed_results.append(error_result)
                logger.error(f"❌ Task {tasks[i].task_id} raised exception: {result}")
            else:
                processed_results.append(result)
        
        # Store results
        self.results.extend(processed_results)
        
        # Log summary
        successful = sum(1 for r in processed_results if r.success)
        failed = len(processed_results) - successful
        total_time = sum(r.total_time for r in processed_results)
        avg_time = total_time / len(processed_results) if processed_results else 0
        
        logger.info(f"✅ Queue processing complete: {successful} successful, {failed} failed")
        logger.info(f"⏱️  Total time: {total_time:.2f}s, Average: {avg_time:.2f}s per task")
        
        return processed_results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        metrics = self.metrics.copy()
        
        # Convert set to count
        metrics['unique_domains'] = len(metrics['domains_processed'])
        del metrics['domains_processed']  # Don't expose the actual set
        
        # Calculate additional metrics
        if metrics['tasks_processed'] > 0:
            metrics['success_rate'] = metrics['tasks_successful'] / metrics['tasks_processed']
            metrics['failure_rate'] = metrics['tasks_failed'] / metrics['tasks_processed']
            metrics['duplicate_rate'] = metrics['duplicates_detected'] / metrics['tasks_processed']
            metrics['average_time_per_task'] = metrics['total_processing_time'] / metrics['tasks_processed']
        else:
            metrics['success_rate'] = 0.0
            metrics['failure_rate'] = 0.0
            metrics['duplicate_rate'] = 0.0
            metrics['average_time_per_task'] = 0.0
        
        return metrics
    
    def print_metrics(self):
        """Print formatted metrics to console"""
        metrics = self.get_metrics()
        
        print(f"\n🚀 Revolutionary Ultimate System Metrics")
        print(f"{'='*50}")
        print(f"📊 Tasks processed: {metrics['tasks_processed']}")
        print(f"✅ Success rate: {metrics['success_rate']:.1%}")
        print(f"❌ Failure rate: {metrics['failure_rate']:.1%}")
        print(f"🔄 Duplicate rate: {metrics['duplicate_rate']:.1%}")
        print(f"⭐ Average quality: {metrics['average_quality_score']:.2f}")
        print(f"⏱️  Average time per task: {metrics['average_time_per_task']:.2f}s")
        print(f"🌐 Unique domains: {metrics['unique_domains']}")
        
        if metrics['methods_used']:
            print(f"\n🛡️ Methods used:")
            for method, count in metrics['methods_used'].items():
                print(f"  • {method}: {count}")
        
        if metrics['errors']:
            print(f"\n❌ Top errors:")
            sorted_errors = sorted(metrics['errors'].items(), key=lambda x: x[1], reverse=True)
            for error, count in sorted_errors[:5]:
                print(f"  • {error}: {count}")
    
    async def scrape_urls(self, urls: List[str], **kwargs) -> List[ScrapingTaskResult]:
        """Convenience method to scrape multiple URLs"""
        
        # Add tasks
        task_ids = self.add_tasks(urls, **kwargs)
        
        # Process queue
        results = await self.process_queue()
        
        return results
    
    async def scrape_url(self, url: str, **kwargs) -> ScrapingTaskResult:
        """Convenience method to scrape single URL"""
        
        results = await self.scrape_urls([url], **kwargs)
        return results[0] if results else ScrapingTaskResult(
            task=ScrapingTask(url=url),
            success=False,
            error="No result returned"
        )


# Example usage and testing
async def main():
    """Example usage of the Revolutionary Ultimate System"""
    
    # Initialize system
    async with RevolutionaryUltimateSystem() as scraper:
        
        # Test URLs
        test_urls = [
            "https://httpbin.org/get",
            "https://httpbin.org/html",
            "https://example.com",
            # Add more URLs to test different scenarios
        ]
        
        print(f"🧪 Testing Revolutionary Ultimate System with {len(test_urls)} URLs")
        
        # Scrape URLs
        results = await scraper.scrape_urls(test_urls)
        
        # Print results
        for result in results:
            if result.success:
                print(f"✅ {result.task.url} - Quality: {result.quality_score:.2f}")
                if result.extracted_content:
                    print(f"   📝 Text: {len(result.extracted_content.text or '')} chars")
                    if result.extracted_content.entities:
                        print(f"   🏷️  Entities: {len(result.extracted_content.entities)}")
            else:
                print(f"❌ {result.task.url} - Error: {result.error}")
        
        # Print metrics
        scraper.print_metrics()


if __name__ == "__main__":
    asyncio.run(main())
