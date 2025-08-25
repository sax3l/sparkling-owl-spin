"""
Scraping Specialist Agent for Sparkling Owl Spin
Advanced web scraping agent with multi-engine support
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json

from core.base_classes import BaseAgent, Priority
from core.registry import get_registry
from engines.scraping.requests_engine import RequestsEngine
from engines.scraping.selenium_engine import SeleniumEngine
from engines.scraping.playwright_engine import PlaywrightEngine
from engines.processing.scheduler import get_scheduler

logger = logging.getLogger(__name__)

class ScrapingSpecialist(BaseAgent):
    """
    Specialized agent for web scraping operations
    Omdöpt från scraping_agent.py enligt pyramidarkitekturen
    """
    
    def __init__(self, agent_id: str = "scraping_specialist"):
        capabilities = [
            "web_scraping",
            "data_extraction", 
            "dom_parsing",
            "javascript_rendering",
            "content_analysis",
            "url_discovery"
        ]
        
        super().__init__(
            agent_id=agent_id,
            name="Scraping Specialist",
            capabilities=capabilities
        )
        
        # Available engines
        self.engines: Dict[str, Any] = {}
        self.default_engine = "requests"
        self.fallback_engines = ["selenium", "playwright"]
        
        # Configuration
        self.max_retries = 3
        self.timeout = 30
        self.concurrent_limit = 5
        self.current_tasks_count = 0
        
        # Performance tracking
        self.engine_performance = {
            'requests': {'success_rate': 0.95, 'avg_time': 2.3},
            'selenium': {'success_rate': 0.90, 'avg_time': 8.1},
            'playwright': {'success_rate': 0.92, 'avg_time': 6.7}
        }
        
    async def start(self) -> bool:
        """Start the scraping specialist"""
        success = await super().start()
        if success:
            await self._initialize_engines()
        return success
        
    async def _initialize_engines(self):
        """Initialize scraping engines"""
        try:
            registry = await get_registry()
            
            # Initialize requests engine
            requests_engine = RequestsEngine("requests_engine", "Requests Scraping Engine")
            await registry.register_service(requests_engine)
            await requests_engine.start()
            self.engines['requests'] = requests_engine
            
            # Initialize selenium engine
            selenium_engine = SeleniumEngine("selenium_engine", "Selenium Scraping Engine")
            await registry.register_service(selenium_engine)
            await selenium_engine.start()
            self.engines['selenium'] = selenium_engine
            
            # Initialize playwright engine
            playwright_engine = PlaywrightEngine("playwright_engine", "Playwright Scraping Engine")
            await registry.register_service(playwright_engine)
            await playwright_engine.start()
            self.engines['playwright'] = playwright_engine
            
            self.logger.info(f"Initialized {len(self.engines)} scraping engines")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize engines: {e}")
            
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a scraping task"""
        task_start = datetime.utcnow()
        task_id = task.get('id', 'unknown')
        
        try:
            # Validate task
            if not await self._validate_task(task):
                return {
                    'status': 'failed',
                    'error': 'Invalid task format',
                    'task_id': task_id
                }
                
            # Check concurrency limit
            if self.current_tasks_count >= self.concurrent_limit:
                return {
                    'status': 'queued',
                    'message': 'Agent at concurrent limit',
                    'task_id': task_id
                }
                
            self.current_tasks_count += 1
            self.current_task = task
            
            # Extract task parameters
            url = task['data']['url']
            extraction_config = task['data'].get('extraction_config', {})
            preferred_engine = task['data'].get('engine', self.default_engine)
            
            # Execute scraping with engine fallback
            result = await self._execute_with_fallback(
                url, extraction_config, preferred_engine, task_id
            )
            
            # Update performance metrics
            execution_time = (datetime.utcnow() - task_start).total_seconds()
            self.performance_metrics['tasks_completed'] += 1
            current_avg = self.performance_metrics['average_execution_time']
            total_tasks = self.performance_metrics['tasks_completed']
            self.performance_metrics['average_execution_time'] = (
                (current_avg * (total_tasks - 1)) + execution_time
            ) / total_tasks
            
            return {
                'status': 'completed',
                'result': result,
                'task_id': task_id,
                'execution_time': execution_time,
                'engine_used': result.get('engine_used', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.performance_metrics['tasks_failed'] += 1
            return {
                'status': 'failed',
                'error': str(e),
                'task_id': task_id
            }
        finally:
            self.current_tasks_count = max(0, self.current_tasks_count - 1)
            self.current_task = None
            
    async def _execute_with_fallback(self, url: str, extraction_config: Dict[str, Any], 
                                   preferred_engine: str, task_id: str) -> Dict[str, Any]:
        """Execute scraping with engine fallback strategy"""
        
        # Determine engine order
        engines_to_try = [preferred_engine]
        for fallback in self.fallback_engines:
            if fallback != preferred_engine:
                engines_to_try.append(fallback)
                
        last_error = None
        
        for engine_name in engines_to_try:
            if engine_name not in self.engines:
                self.logger.warning(f"Engine {engine_name} not available")
                continue
                
            engine = self.engines[engine_name]
            if not engine.is_available:
                continue
                
            try:
                self.logger.info(f"Attempting scraping with {engine_name} for {url}")
                
                # Prepare engine-specific configuration
                engine_config = {
                    'url': url,
                    'extraction_rules': extraction_config,
                    'timeout': self.timeout,
                    'task_id': task_id
                }
                
                # Execute scraping
                result = await engine.process(url, engine_config)
                
                if result and result.get('success'):
                    # Update engine performance
                    perf = self.engine_performance.get(engine_name, {})
                    perf['last_success'] = datetime.utcnow().isoformat()
                    result['engine_used'] = engine_name
                    
                    self.logger.info(f"Successfully scraped {url} with {engine_name}")
                    return result
                else:
                    raise Exception(f"Engine {engine_name} returned unsuccessful result")
                    
            except Exception as e:
                last_error = e
                self.logger.warning(f"Engine {engine_name} failed for {url}: {e}")
                
                # Update engine performance
                perf = self.engine_performance.get(engine_name, {})
                perf['last_failure'] = datetime.utcnow().isoformat()
                perf['last_error'] = str(e)
                
                continue
                
        # All engines failed
        raise Exception(f"All scraping engines failed. Last error: {last_error}")
        
    async def _validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate task format and requirements"""
        
        # Check required fields
        if 'data' not in task:
            return False
            
        data = task['data']
        if 'url' not in data:
            return False
            
        # Validate URL format
        url = data['url']
        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            return False
            
        return True
        
    async def discover_urls(self, base_url: str, max_depth: int = 2) -> List[str]:
        """Discover URLs from a base URL"""
        
        try:
            scheduler = await get_scheduler()
            
            # Add initial URL to scheduler
            task_id = await scheduler.add_url(
                url=base_url,
                depth=0,
                priority=Priority.NORMAL,
                metadata={'discovery_task': True}
            )
            
            discovered_urls = []
            processed_count = 0
            max_urls = 100  # Limit to prevent runaway discovery
            
            while not scheduler.is_empty() and processed_count < max_urls:
                # Get next URL to process
                crawl_task = await scheduler.get_next_task()
                if not crawl_task:
                    await asyncio.sleep(0.1)
                    continue
                    
                if crawl_task.depth > max_depth:
                    await scheduler.mark_task_completed(crawl_task.id)
                    continue
                    
                try:
                    # Extract URLs from this page
                    result = await self._execute_with_fallback(
                        crawl_task.url,
                        {'links': 'a[href]'},
                        'requests',
                        crawl_task.id
                    )
                    
                    if result.get('success') and result.get('data'):
                        # Extract discovered links
                        links = result['data'].get('links', [])
                        new_urls = []
                        
                        for link in links:
                            if isinstance(link, dict) and 'href' in link:
                                href = link['href']
                                # Convert relative URLs to absolute
                                if href.startswith('/'):
                                    from urllib.parse import urljoin
                                    href = urljoin(crawl_task.url, href)
                                elif not href.startswith(('http://', 'https://')):
                                    continue
                                    
                                new_urls.append(href)
                                discovered_urls.append(href)
                                
                        # Mark task completed and add discovered URLs
                        await scheduler.mark_task_completed(
                            crawl_task.id, 
                            result, 
                            new_urls
                        )
                        
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.error(f"URL discovery failed for {crawl_task.url}: {e}")
                    await scheduler.mark_task_failed(crawl_task.id, str(e), retry=False)
                    
            return list(set(discovered_urls))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"URL discovery process failed: {e}")
            return []
            
    async def analyze_site_structure(self, url: str) -> Dict[str, Any]:
        """Analyze the structure of a website"""
        
        try:
            # Use advanced extraction to analyze site structure
            extraction_config = {
                'title': 'title',
                'headings': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
                'navigation': 'nav a[href]',
                'footer_links': 'footer a[href]',
                'images': 'img[src]',
                'scripts': 'script[src]',
                'stylesheets': 'link[rel="stylesheet"][href]',
                'meta_description': 'meta[name="description"]',
                'meta_keywords': 'meta[name="keywords"]'
            }
            
            result = await self._execute_with_fallback(
                url, extraction_config, 'playwright', f"structure_analysis_{url}"
            )
            
            if result.get('success'):
                data = result.get('data', {})
                
                # Analyze the extracted data
                analysis = {
                    'url': url,
                    'title': data.get('title', ''),
                    'heading_structure': self._analyze_headings(data.get('headings', [])),
                    'navigation_complexity': len(data.get('navigation', [])),
                    'footer_links_count': len(data.get('footer_links', [])),
                    'media_richness': {
                        'images': len(data.get('images', [])),
                        'scripts': len(data.get('scripts', [])),
                        'stylesheets': len(data.get('stylesheets', []))
                    },
                    'seo_elements': {
                        'has_description': bool(data.get('meta_description')),
                        'has_keywords': bool(data.get('meta_keywords')),
                        'title_length': len(data.get('title', ''))
                    },
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'engine_used': result.get('engine_used')
                }
                
                return analysis
            else:
                raise Exception("Site structure analysis failed")
                
        except Exception as e:
            self.logger.error(f"Site structure analysis failed for {url}: {e}")
            return {'error': str(e), 'url': url}
            
    def _analyze_headings(self, headings: List[Any]) -> Dict[str, Any]:
        """Analyze heading structure for SEO and content organization"""
        
        heading_counts = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        total_headings = len(headings)
        
        for heading in headings:
            if isinstance(heading, dict) and 'tag' in heading:
                tag = heading['tag'].lower()
                if tag in heading_counts:
                    heading_counts[tag] += 1
                    
        return {
            'total_headings': total_headings,
            'heading_distribution': heading_counts,
            'has_h1': heading_counts['h1'] > 0,
            'multiple_h1': heading_counts['h1'] > 1,
            'hierarchy_depth': max([int(h[1]) for h in heading_counts.keys() if heading_counts[h] > 0] + [0])
        }
        
    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Get detailed agent statistics"""
        
        base_stats = await self.health_check()
        
        # Add scraping-specific statistics
        base_stats.update({
            'engine_performance': self.engine_performance,
            'available_engines': list(self.engines.keys()),
            'concurrent_limit': self.concurrent_limit,
            'current_tasks': self.current_tasks_count,
            'default_engine': self.default_engine,
            'fallback_engines': self.fallback_engines
        })
        
        return base_stats
