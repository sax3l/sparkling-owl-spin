"""
Revolutionary Main System
The world's most advanced unblockable scraping system
Integrates all components for completely undetectable scraping
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
import json
from datetime import datetime

from .revolutionary_crawler import RevolutionaryCrawler
from .proxy_rotator import ProxyRotator
from .stealth_engine import StealthEngine
from .captcha_solver import CaptchaSolver, CaptchaTask
from .session_manager import SessionManager

@dataclass
class ScrapingTask:
    """Complete scraping task configuration"""
    name: str
    start_urls: List[str]
    crawl_method: str = "intelligent"  # bfs, dfs, priority, intelligent
    max_pages: int = 10000
    max_depth: int = 10
    target_patterns: List[str] = None
    avoid_patterns: List[str] = None
    
    # Anti-detection settings
    stealth_level: str = "maximum"
    proxy_rotation: bool = True
    session_management: bool = True
    captcha_solving: bool = True
    
    # Output settings
    output_format: str = "json"
    output_path: str = "results"
    
    def __post_init__(self):
        if self.target_patterns is None:
            self.target_patterns = []
        if self.avoid_patterns is None:
            self.avoid_patterns = []

class RevolutionaryScrapingSystem:
    """
    The world's most advanced unblockable scraping system
    Integrates all revolutionary components for maximum effectiveness
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize all components
        self.crawler = None
        self.proxy_rotator = None
        self.stealth_engine = None
        self.captcha_solver = None
        self.session_manager = None
        
        # System state
        self.initialized = False
        self.active_tasks: Dict[str, asyncio.Task] = {}
        
        # Statistics
        self.system_stats = {
            'tasks_completed': 0,
            'total_pages_scraped': 0,
            'total_captchas_solved': 0,
            'total_proxies_used': 0,
            'total_sessions_created': 0,
            'system_start_time': None,
            'uptime': 0
        }
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('Revolutionary Scraper')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler
            file_handler = logging.FileHandler('revolutionary_scraper.log')
            file_handler.setLevel(logging.DEBUG)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
            logger.addHandler(file_handler)
            
        return logger
    
    async def initialize(self):
        """Initialize all system components"""
        if self.initialized:
            return
            
        self.logger.info("🚀 Initializing Revolutionary Scraping System...")
        self.system_stats['system_start_time'] = datetime.now()
        
        try:
            # Initialize proxy rotator first (needed by other components)
            self.logger.info("📡 Initializing Proxy Rotation System...")
            proxy_config = self.config.get('proxy_rotator', {})
            self.proxy_rotator = ProxyRotator(proxy_config)
            await self.proxy_rotator.initialize()
            
            # Initialize stealth engine
            self.logger.info("🥷 Initializing Stealth Engine...")
            stealth_config = self.config.get('stealth_engine', {})
            self.stealth_engine = StealthEngine(stealth_config)
            await self.stealth_engine.initialize()
            
            # Initialize session manager
            self.logger.info("🔄 Initializing Session Manager...")
            session_config = self.config.get('session_manager', {})
            self.session_manager = SessionManager(session_config)
            await self.session_manager.initialize()
            
            # Initialize CAPTCHA solver
            self.logger.info("🧩 Initializing CAPTCHA Solver...")
            captcha_config = self.config.get('captcha_solver', {})
            self.captcha_solver = CaptchaSolver(captcha_config)
            
            # Initialize crawler
            self.logger.info("🕷️ Initializing Revolutionary Crawler...")
            crawler_config = self.config.get('crawler', {})
            self.crawler = RevolutionaryCrawler(crawler_config)
            
            self.initialized = True
            self.logger.info("✅ Revolutionary Scraping System fully initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ System initialization failed: {e}")
            raise
    
    async def execute_scraping_task(self, task: ScrapingTask) -> Dict[str, Any]:
        """
        Execute a complete scraping task with all revolutionary features
        """
        if not self.initialized:
            await self.initialize()
            
        self.logger.info(f"🎯 Starting revolutionary scraping task: {task.name}")
        start_time = time.time()
        
        try:
            # Execute task with full system integration
            results = await self._execute_task_with_full_integration(task)
            
            # Process and save results
            processed_results = await self._process_results(results, task)
            
            execution_time = time.time() - start_time
            self.system_stats['tasks_completed'] += 1
            
            self.logger.info(f"✅ Task '{task.name}' completed successfully in {execution_time:.2f}s")
            self.logger.info(f"📊 Scraped {len(results)} pages with {processed_results['total_data_points']} data points")
            
            return {
                'task_name': task.name,
                'success': True,
                'execution_time': execution_time,
                'pages_scraped': len(results),
                'data_points': processed_results['total_data_points'],
                'captchas_solved': processed_results['captchas_solved'],
                'proxies_used': processed_results['proxies_used'],
                'sessions_used': processed_results['sessions_used'],
                'results_path': processed_results['output_path']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Task '{task.name}' failed: {e}")
            return {
                'task_name': task.name,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }
    
    async def _execute_task_with_full_integration(self, task: ScrapingTask) -> List[Dict]:
        """
        Execute task with full system integration
        """
        results = []
        
        # Determine optimal crawling strategy
        if task.crawl_method == "intelligent":
            crawl_method = await self._determine_optimal_crawl_method(task.start_urls)
        else:
            crawl_method = task.crawl_method
            
        self.logger.info(f"📈 Using {crawl_method} crawling strategy")
        
        # Execute crawling with integrated components
        if crawl_method == "bfs":
            results = await self.crawler.crawl_bfs(task.start_urls, self.session_manager)
        elif crawl_method == "dfs":
            results = await self.crawler.crawl_dfs(task.start_urls, self.session_manager)
        elif crawl_method == "priority":
            results = await self.crawler.crawl_priority_based(task.start_urls, self.session_manager)
        else:
            # Intelligent hybrid approach
            results = await self._intelligent_hybrid_crawl(task)
            
        return results
    
    async def _intelligent_hybrid_crawl(self, task: ScrapingTask) -> List[Dict]:
        """
        Intelligent hybrid crawling combining all strategies
        """
        all_results = []
        
        # Phase 1: BFS for broad discovery (25% of budget)
        bfs_budget = max(1, task.max_pages // 4)
        self.logger.info(f"🔍 Phase 1: BFS exploration ({bfs_budget} pages)")
        
        bfs_task_config = {**self.crawler.config, 'max_pages': bfs_budget}
        bfs_crawler = RevolutionaryCrawler(bfs_task_config)
        bfs_results = await bfs_crawler.crawl_bfs(task.start_urls[:3], self.session_manager)
        all_results.extend(bfs_results)
        
        # Phase 2: Priority-based for high-value targets (50% of budget)
        priority_budget = max(1, task.max_pages // 2)
        self.logger.info(f"🎯 Phase 2: Priority-based targeting ({priority_budget} pages)")
        
        # Extract high-value URLs from BFS results
        high_value_urls = self._extract_high_value_urls(bfs_results, task.target_patterns)
        
        priority_task_config = {**self.crawler.config, 'max_pages': priority_budget}
        priority_crawler = RevolutionaryCrawler(priority_task_config)
        priority_results = await priority_crawler.crawl_priority_based(
            high_value_urls[:10], self.session_manager
        )
        all_results.extend(priority_results)
        
        # Phase 3: DFS for deep exploration (25% of budget)
        remaining_budget = task.max_pages - len(all_results)
        if remaining_budget > 0:
            self.logger.info(f"⛏️ Phase 3: DFS deep exploration ({remaining_budget} pages)")
            
            # Select promising deep URLs
            deep_urls = self._extract_deep_exploration_urls(all_results)
            
            dfs_task_config = {**self.crawler.config, 'max_pages': remaining_budget}
            dfs_crawler = RevolutionaryCrawler(dfs_task_config)
            dfs_results = await dfs_crawler.crawl_dfs(deep_urls[:5], self.session_manager)
            all_results.extend(dfs_results)
        
        return all_results[:task.max_pages]
    
    async def _determine_optimal_crawl_method(self, start_urls: List[str]) -> str:
        """
        Determine optimal crawling method based on URL analysis
        """
        # Analyze URL structure and content
        url_analysis = await self._analyze_start_urls(start_urls[:3])
        
        # Decision logic based on analysis
        if url_analysis['site_complexity'] > 0.8:
            return "priority"  # Complex sites benefit from prioritization
        elif url_analysis['depth_indicators'] > 0.7:
            return "dfs"  # Deep sites benefit from depth-first
        elif url_analysis['breadth_indicators'] > 0.7:
            return "bfs"  # Broad sites benefit from breadth-first
        else:
            return "intelligent"  # Use hybrid approach
    
    async def _analyze_start_urls(self, urls: List[str]) -> Dict[str, float]:
        """
        Analyze start URLs to determine site characteristics
        """
        analysis = {
            'site_complexity': 0.5,
            'depth_indicators': 0.5,
            'breadth_indicators': 0.5
        }
        
        for url in urls:
            # Simple heuristics based on URL structure
            if '/category/' in url or '/section/' in url:
                analysis['breadth_indicators'] += 0.2
            if '/product/' in url or '/item/' in url or '/detail/' in url:
                analysis['depth_indicators'] += 0.2
            if '?' in url or len(url) > 100:
                analysis['site_complexity'] += 0.2
        
        # Normalize scores
        for key in analysis:
            analysis[key] = min(1.0, analysis[key])
        
        return analysis
    
    def _extract_high_value_urls(self, results: List[Dict], patterns: List[str]) -> List[str]:
        """
        Extract high-value URLs from crawl results
        """
        high_value_urls = []
        
        for result in results:
            url = result.get('url', '')
            links = result.get('links', [])
            
            # Check if current URL matches patterns
            for pattern in patterns:
                if pattern.lower() in url.lower():
                    high_value_urls.append(url)
                    break
            
            # Check links for pattern matches
            for link in links:
                for pattern in patterns:
                    if pattern.lower() in link.lower():
                        high_value_urls.append(link)
                        break
        
        return list(set(high_value_urls))  # Remove duplicates
    
    def _extract_deep_exploration_urls(self, results: List[Dict]) -> List[str]:
        """
        Extract URLs suitable for deep exploration
        """
        deep_urls = []
        
        for result in results:
            # Look for URLs that suggest deeper content
            links = result.get('links', [])
            for link in links:
                # Heuristics for deep content
                if any(indicator in link.lower() for indicator in 
                       ['/archive/', '/history/', '/details/', '/full/', '/complete/']):
                    deep_urls.append(link)
                    
                # URLs with parameters often lead to deeper content
                if '?' in link and len(link.split('/')) > 4:
                    deep_urls.append(link)
        
        return list(set(deep_urls))
    
    async def _process_results(self, results: List[Dict], task: ScrapingTask) -> Dict[str, Any]:
        """
        Process and analyze scraping results
        """
        total_data_points = 0
        captchas_solved = 0
        proxies_used = 0
        sessions_used = 0
        
        # Analyze results
        for result in results:
            # Count data points (simplified)
            total_data_points += len(result.get('links', []))
            total_data_points += len(result.get('forms', []))
            total_data_points += len(result.get('images', []))
        
        # Get system statistics
        if self.captcha_solver:
            captcha_stats = self.captcha_solver.get_solving_statistics()
            captchas_solved = captcha_stats.get('successful_solves', 0)
        
        if self.proxy_rotator:
            proxy_stats = self.proxy_rotator.get_proxy_statistics()
            proxies_used = proxy_stats.get('healthy_proxies', 0)
        
        if self.session_manager:
            session_stats = self.session_manager.get_session_statistics()
            sessions_used = session_stats.get('active_sessions', 0)
        
        # Save results
        output_path = await self._save_results(results, task)
        
        return {
            'total_data_points': total_data_points,
            'captchas_solved': captchas_solved,
            'proxies_used': proxies_used,
            'sessions_used': sessions_used,
            'output_path': output_path
        }
    
    async def _save_results(self, results: List[Dict], task: ScrapingTask) -> str:
        """
        Save scraping results to file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task.name}_{timestamp}.{task.output_format}"
        output_path = f"{task.output_path}/{filename}"
        
        # Create output directory if needed
        import os
        os.makedirs(task.output_path, exist_ok=True)
        
        # Save results
        if task.output_format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        elif task.output_format.lower() == 'csv':
            # Convert to CSV (simplified)
            import pandas as pd
            df = pd.json_normalize(results)
            df.to_csv(output_path, index=False)
        
        self.logger.info(f"💾 Results saved to: {output_path}")
        return output_path
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        """
        status = {
            'initialized': self.initialized,
            'uptime': (datetime.now() - self.system_stats['system_start_time']).total_seconds() 
                     if self.system_stats['system_start_time'] else 0,
            'active_tasks': len(self.active_tasks),
            'system_stats': self.system_stats
        }
        
        # Component status
        if self.proxy_rotator:
            status['proxy_status'] = self.proxy_rotator.get_proxy_statistics()
            
        if self.session_manager:
            status['session_status'] = self.session_manager.get_session_statistics()
            
        if self.captcha_solver:
            status['captcha_status'] = self.captcha_solver.get_solving_statistics()
            
        return status
    
    async def run_continuous_scraping(self, tasks: List[ScrapingTask], 
                                    concurrent_tasks: int = 3) -> List[Dict[str, Any]]:
        """
        Run multiple scraping tasks continuously
        """
        self.logger.info(f"🚀 Starting continuous scraping with {len(tasks)} tasks")
        
        # Create semaphore to limit concurrent tasks
        semaphore = asyncio.Semaphore(concurrent_tasks)
        
        async def execute_single_task(task: ScrapingTask) -> Dict[str, Any]:
            async with semaphore:
                return await self.execute_scraping_task(task)
        
        # Execute all tasks
        task_coroutines = [execute_single_task(task) for task in tasks]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        
        # Process results
        successful_tasks = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed_tasks = [r for r in results if not (isinstance(r, dict) and r.get('success'))]
        
        self.logger.info(f"✅ Continuous scraping completed: {len(successful_tasks)} successful, {len(failed_tasks)} failed")
        
        return results
    
    async def shutdown(self):
        """
        Gracefully shutdown the system
        """
        self.logger.info("🛑 Shutting down Revolutionary Scraping System...")
        
        # Cancel active tasks
        for task_id, task in self.active_tasks.items():
            task.cancel()
            self.logger.info(f"Cancelled task: {task_id}")
        
        # Shutdown components
        if self.session_manager:
            await self.session_manager.close()
            
        if self.stealth_engine:
            await self.stealth_engine.close()
            
        if self.captcha_solver:
            await self.captcha_solver.close()
            
        self.logger.info("✅ System shutdown complete")

# Example usage and configuration
def create_revolutionary_config() -> Dict[str, Any]:
    """
    Create comprehensive configuration for revolutionary scraping
    """
    return {
        'crawler': {
            'max_depth': 10,
            'max_pages': 10000,
            'concurrent_requests': 50,
            'crawl_delay': 1.0,
            'retry_attempts': 5,
            'randomize_crawl_order': True,
            'adaptive_delays': True,
            'intelligent_filtering': True
        },
        'proxy_rotator': {
            'rotation_strategy': 'intelligent',
            'max_consecutive_failures': 5,
            'health_check_interval': 300,
            'geographic_targeting': True,
            'sticky_sessions': True,
            'bright_data': {
                'enabled': False,  # Set to True with real credentials
                'username': 'your-username',
                'password': 'your-password',
                'countries': ['US', 'GB', 'DE', 'SE']
            },
            '2captcha': {
                'enabled': False,  # Set to True with real API key
                'api_key': 'your-api-key'
            }
        },
        'stealth_engine': {
            'stealth_level': 'maximum',
            'randomize_fingerprints': True,
            'emulate_human_behavior': True,
            'webdriver_patches': True,
            'canvas_spoofing': True,
            'webgl_spoofing': True,
            'audio_spoofing': True,
            'mouse_movements': True,
            'typing_delays': True,
            'scroll_behavior': True
        },
        'captcha_solver': {
            'primary_strategy': 'service_based',
            'fallback_strategies': ['ocr', 'pattern_matching'],
            'max_solving_time': 120,
            'avoidance_enabled': True,
            '2captcha': {
                'enabled': False,  # Set to True with real API key
                'api_key': 'your-2captcha-api-key'
            },
            'ocr_preprocessing': True
        },
        'session_manager': {
            'max_sessions_per_domain': 5,
            'session_timeout': 3600,
            'max_requests_per_session': 1000,
            'enable_session_rotation': True,
            'enable_cookie_persistence': True,
            'geo_consistency': True,
            'rate_limiting': True
        }
    }

# Example task creation
def create_example_task() -> ScrapingTask:
    """
    Create an example scraping task
    """
    return ScrapingTask(
        name="example_comprehensive_scrape",
        start_urls=[
            "https://example.com/products",
            "https://example.com/categories",
            "https://example.com/search?q=data"
        ],
        crawl_method="intelligent",
        max_pages=1000,
        max_depth=5,
        target_patterns=["product", "item", "detail", "category"],
        avoid_patterns=["login", "register", "cart", "checkout"],
        stealth_level="maximum",
        proxy_rotation=True,
        session_management=True,
        captcha_solving=True,
        output_format="json",
        output_path="results"
    )
