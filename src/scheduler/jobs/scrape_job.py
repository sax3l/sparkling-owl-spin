"""
Scrape Job Implementation
=========================

Implementation of scrape jobs for the ECaDP scheduler.
Handles data scraping operations with template-driven extraction,
comprehensive configuration, monitoring, and error handling.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import yaml

from src.scraper.base_scraper import BaseScraper
from src.scraper.http_scraper import HttpScraper
from src.scraper.selenium_scraper import SeleniumScraper
from src.scraper.template_runtime import TemplateRuntime
from src.scraper.dsl.schema import ScrapingTemplate
from src.proxy_pool.manager import ProxyPoolManager
from src.anti_bot.detector import BotDetector
from src.database.connection import DatabaseManager
from src.utils.rate_limiter import RateLimiter
from src.webhooks.client import WebhookClient
from src.exporters.json_exporter import JsonExporter
from src.exporters.csv_exporter import CsvExporter
from src.exporters.excel_exporter import ExcelExporter

logger = logging.getLogger(__name__)

@dataclass
class ScrapeJobConfig:
    """Configuration for scrape jobs"""
    urls: List[str]
    template_path: Optional[str] = None
    template_content: Optional[Dict[str, Any]] = None
    scraper_type: str = "http"  # "http", "selenium", "auto"
    output_format: str = "json"  # "json", "csv", "excel"
    output_path: str = "data/exports/scrape_results"
    use_proxy_pool: bool = True
    enable_anti_bot: bool = True
    concurrent_requests: int = 5
    delay_range: tuple = (1.0, 3.0)
    retry_attempts: int = 3
    timeout: int = 30
    user_agent: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    follow_redirects: bool = True
    render_javascript: bool = False
    wait_for_elements: List[str] = field(default_factory=list)
    webhook_url: Optional[str] = None
    quality_checks: bool = True
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    transformations: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ScrapeJobResult:
    """Result of a scrape job execution"""
    job_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    urls_processed: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    errors: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    extracted_data: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ScrapeJob:
    """
    Scrape job implementation for ECaDP scheduler
    
    Handles the execution of data scraping tasks with template-driven
    extraction, comprehensive configuration, monitoring, and error handling.
    """
    
    def __init__(self, config: Union[ScrapeJobConfig, Dict[str, Any]], job_id: Optional[str] = None):
        if isinstance(config, dict):
            self.config = ScrapeJobConfig(**config)
        else:
            self.config = config
            
        self.job_id = job_id or f"scrape_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Components
        self.scraper = None
        self.template_runtime = None
        self.template = None
        self.proxy_manager = None
        self.bot_detector = None
        self.rate_limiter = None
        self.db_manager = None
        self.webhook_client = None
        self.exporter = None
        
        # Execution state
        self.result = ScrapeJobResult(
            job_id=self.job_id,
            status="pending",
            start_time=datetime.utcnow()
        )
    
    async def initialize(self):
        """Initialize job components"""
        try:
            logger.info(f"Initializing scrape job {self.job_id}")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Load and validate template
            await self._load_template()
            
            # Initialize proxy pool if enabled
            if self.config.use_proxy_pool:
                self.proxy_manager = ProxyPoolManager()
                await self.proxy_manager.initialize()
                logger.info(f"Proxy pool initialized with {await self.proxy_manager.get_active_count()} proxies")
            
            # Initialize anti-bot detection
            if self.config.enable_anti_bot:
                self.bot_detector = BotDetector()
                logger.info("Anti-bot detection initialized")
            
            # Initialize rate limiter
            self.rate_limiter = RateLimiter(
                max_requests=self.config.concurrent_requests,
                time_window=60.0
            )
            
            # Initialize scraper based on type
            await self._initialize_scraper()
            
            # Initialize template runtime
            if self.template:
                self.template_runtime = TemplateRuntime(self.template)
                logger.info("Template runtime initialized")
            
            # Initialize webhook client if configured
            if self.config.webhook_url:
                self.webhook_client = WebhookClient(self.config.webhook_url)
            
            # Initialize exporter
            await self._initialize_exporter()
            
            logger.info(f"Scrape job {self.job_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scrape job {self.job_id}: {e}")
            self.result.status = "failed"
            self.result.errors.append(f"Initialization failed: {str(e)}")
            raise
    
    async def _load_template(self):
        """Load and validate scraping template"""
        try:
            if self.config.template_content:
                # Use provided template content
                self.template = ScrapingTemplate(**self.config.template_content)
                logger.info("Template loaded from provided content")
                
            elif self.config.template_path:
                # Load template from file
                template_path = Path(self.config.template_path)
                if not template_path.exists():
                    raise FileNotFoundError(f"Template file not found: {template_path}")
                
                with open(template_path, 'r', encoding='utf-8') as f:
                    if template_path.suffix.lower() in ['.yml', '.yaml']:
                        template_data = yaml.safe_load(f)
                    else:
                        template_data = json.load(f)
                
                self.template = ScrapingTemplate(**template_data)
                logger.info(f"Template loaded from file: {template_path}")
                
            else:
                # Use auto-detection mode (no template)
                logger.info("No template specified, using auto-detection mode")
                
        except Exception as e:
            logger.error(f"Failed to load template for job {self.job_id}: {e}")
            raise
    
    async def _initialize_scraper(self):
        """Initialize the appropriate scraper based on configuration"""
        try:
            scraper_kwargs = {
                'proxy_manager': self.proxy_manager,
                'bot_detector': self.bot_detector,
                'rate_limiter': self.rate_limiter,
                'timeout': self.config.timeout,
                'retry_attempts': self.config.retry_attempts,
                'user_agent': self.config.user_agent,
                'headers': self.config.headers,
                'cookies': self.config.cookies
            }
            
            if self.config.scraper_type == "selenium" or self.config.render_javascript:
                self.scraper = SeleniumScraper(**scraper_kwargs)
                logger.info("Selenium scraper initialized")
                
            elif self.config.scraper_type == "http":
                self.scraper = HttpScraper(**scraper_kwargs)
                logger.info("HTTP scraper initialized")
                
            elif self.config.scraper_type == "auto":
                # Start with HTTP, upgrade to Selenium if needed
                self.scraper = HttpScraper(**scraper_kwargs)
                logger.info("Auto scraper initialized (starting with HTTP)")
                
            else:
                raise ValueError(f"Unsupported scraper type: {self.config.scraper_type}")
                
        except Exception as e:
            logger.error(f"Failed to initialize scraper for job {self.job_id}: {e}")
            raise
    
    async def _initialize_exporter(self):
        """Initialize the appropriate exporter based on output format"""
        try:
            output_dir = Path(self.config.output_path) / self.job_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if self.config.output_format == "json":
                self.exporter = JsonExporter(output_dir / "results.json")
            elif self.config.output_format == "csv":
                self.exporter = CsvExporter(output_dir / "results.csv")
            elif self.config.output_format == "excel":
                self.exporter = ExcelExporter(output_dir / "results.xlsx")
            else:
                raise ValueError(f"Unsupported output format: {self.config.output_format}")
                
            logger.info(f"Exporter initialized for format: {self.config.output_format}")
            
        except Exception as e:
            logger.error(f"Failed to initialize exporter for job {self.job_id}: {e}")
            raise
    
    async def scrape_urls(self):
        """Execute the scraping process"""
        try:
            logger.info(f"Starting scrape execution for job {self.job_id}")
            
            semaphore = asyncio.Semaphore(self.config.concurrent_requests)
            tasks = []
            
            for url in self.config.urls:
                task = asyncio.create_task(
                    self._scrape_single_url(semaphore, url)
                )
                tasks.append(task)
            
            # Execute all scraping tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                url = self.config.urls[i]
                
                if isinstance(result, Exception):
                    error_msg = f"Error scraping {url}: {str(result)}"
                    self.result.errors.append(error_msg)
                    self.result.failed_extractions += 1
                    logger.error(error_msg)
                elif result:
                    self.result.extracted_data.append({
                        'url': url,
                        'timestamp': datetime.utcnow().isoformat(),
                        'data': result
                    })
                    self.result.successful_extractions += 1
                    logger.debug(f"Successfully scraped: {url}")
                else:
                    self.result.failed_extractions += 1
                    logger.warning(f"No data extracted from: {url}")
            
            self.result.urls_processed = len(self.config.urls)
            
            logger.info(f"Scrape execution completed for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Scrape execution failed for job {self.job_id}: {e}")
            raise
    
    async def _scrape_single_url(self, semaphore: asyncio.Semaphore, url: str):
        """Scrape a single URL with semaphore protection"""
        async with semaphore:
            try:
                # Rate limiting
                await self.rate_limiter.acquire()
                
                # Perform scraping
                if self.template_runtime:
                    # Template-driven extraction
                    result = await self.template_runtime.extract_from_url(url, self.scraper)
                else:
                    # Auto-detection mode
                    result = await self.scraper.scrape(url)
                
                # Apply quality checks if enabled
                if self.config.quality_checks and result:
                    result = await self._apply_quality_checks(url, result)
                
                # Apply transformations if configured
                if self.config.transformations and result:
                    result = await self._apply_transformations(result)
                
                return result
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                raise
    
    async def _apply_quality_checks(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quality checks to extracted data"""
        try:
            # Check for required fields
            required_fields = self.config.validation_rules.get('required_fields', [])
            for field in required_fields:
                if field not in data or not data[field]:
                    logger.warning(f"Missing required field '{field}' for URL: {url}")
            
            # Check minimum data length
            min_length = self.config.validation_rules.get('min_data_length', 0)
            data_text = ' '.join(str(v) for v in data.values() if v)
            if len(data_text) < min_length:
                logger.warning(f"Insufficient data length for URL: {url}")
            
            # Apply custom validation rules
            custom_rules = self.config.validation_rules.get('custom_rules', [])
            for rule in custom_rules:
                # Implement custom validation logic here
                pass
            
            return data
            
        except Exception as e:
            logger.error(f"Quality check failed for {url}: {e}")
            return data
    
    async def _apply_transformations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data transformations"""
        try:
            result = data.copy()
            
            for transformation in self.config.transformations:
                transform_type = transformation.get('type')
                
                if transform_type == 'normalize_text':
                    # Text normalization
                    for field in transformation.get('fields', []):
                        if field in result and isinstance(result[field], str):
                            result[field] = result[field].strip().lower()
                
                elif transform_type == 'extract_numbers':
                    # Extract numeric values
                    import re
                    for field in transformation.get('fields', []):
                        if field in result and isinstance(result[field], str):
                            numbers = re.findall(r'\d+\.?\d*', result[field])
                            if numbers:
                                result[f"{field}_numeric"] = float(numbers[0])
                
                elif transform_type == 'date_parsing':
                    # Parse dates
                    from dateutil import parser
                    for field in transformation.get('fields', []):
                        if field in result and isinstance(result[field], str):
                            try:
                                parsed_date = parser.parse(result[field])
                                result[f"{field}_parsed"] = parsed_date.isoformat()
                            except Exception:
                                pass
                
                # Add more transformation types as needed
            
            return result
            
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            return data
    
    async def export_data(self):
        """Export extracted data using configured exporter"""
        try:
            if not self.result.extracted_data:
                logger.warning(f"No data to export for job {self.job_id}")
                return
            
            logger.info(f"Exporting {len(self.result.extracted_data)} items for job {self.job_id}")
            
            # Prepare data for export
            export_data = []
            for item in self.result.extracted_data:
                flattened_item = {
                    'url': item['url'],
                    'timestamp': item['timestamp'],
                    **item['data']
                }
                export_data.append(flattened_item)
            
            # Export data
            output_file = await self.exporter.export(export_data)
            self.result.output_files.append(output_file)
            
            logger.info(f"Data exported to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export data for job {self.job_id}: {e}")
            raise
    
    async def generate_report(self):
        """Generate scrape job report"""
        try:
            logger.info(f"Generating report for scrape job {self.job_id}")
            
            # Update result statistics
            self.result.statistics = {
                'urls_processed': self.result.urls_processed,
                'successful_extractions': self.result.successful_extractions,
                'failed_extractions': self.result.failed_extractions,
                'success_rate': (self.result.successful_extractions / max(1, self.result.urls_processed)) * 100,
                'error_count': len(self.result.errors),
                'data_items_extracted': len(self.result.extracted_data),
                'runtime_seconds': (datetime.utcnow() - self.result.start_time).total_seconds()
            }
            
            # Create report directory
            report_dir = Path(self.config.output_path) / self.job_id
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate JSON report
            report_path = report_dir / "report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'job_id': self.result.job_id,
                    'status': self.result.status,
                    'start_time': self.result.start_time.isoformat(),
                    'end_time': self.result.end_time.isoformat() if self.result.end_time else None,
                    'statistics': self.result.statistics,
                    'errors': self.result.errors,
                    'output_files': self.result.output_files,
                    'config': {
                        'urls': self.config.urls,
                        'template_path': self.config.template_path,
                        'scraper_type': self.config.scraper_type,
                        'output_format': self.config.output_format,
                        'concurrent_requests': self.config.concurrent_requests
                    },
                    'sample_data': self.result.extracted_data[:5]  # First 5 items as sample
                }, f, indent=2)
            
            self.result.output_files.append(str(report_path))
            
            logger.info(f"Report generated for job {self.job_id}: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report for job {self.job_id}: {e}")
    
    async def send_notifications(self):
        """Send job completion notifications"""
        try:
            if self.webhook_client:
                notification_data = {
                    'job_id': self.result.job_id,
                    'status': self.result.status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'statistics': self.result.statistics,
                    'output_files': self.result.output_files[:10]  # Limit to prevent large payloads
                }
                
                event_type = f"scrape_job.{self.result.status}"
                await self.webhook_client.send_event(event_type, notification_data)
                
                logger.info(f"Sent notification for job {self.job_id}")
                
        except Exception as e:
            logger.error(f"Failed to send notifications for job {self.job_id}: {e}")
    
    async def cleanup(self):
        """Clean up job resources"""
        try:
            logger.info(f"Cleaning up scrape job {self.job_id}")
            
            if self.scraper:
                await self.scraper.close()
            
            if self.db_manager:
                await self.db_manager.close()
            
            if self.proxy_manager:
                await self.proxy_manager.cleanup()
            
            logger.info(f"Cleanup completed for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup for job {self.job_id}: {e}")
    
    async def execute(self) -> ScrapeJobResult:
        """
        Execute the scrape job
        
        Returns:
            ScrapeJobResult: Result of the job execution
        """
        try:
            logger.info(f"Starting execution of scrape job {self.job_id}")
            self.result.status = "running"
            self.result.start_time = datetime.utcnow()
            
            # Initialize components
            await self.initialize()
            
            # Validate URLs
            if not self.config.urls:
                raise ValueError("No URLs provided for scraping")
            
            # Execute scraping
            await self.scrape_urls()
            
            # Export data
            await self.export_data()
            
            # Mark as completed
            self.result.status = "completed"
            self.result.end_time = datetime.utcnow()
            
            # Generate report
            await self.generate_report()
            
            # Send notifications
            await self.send_notifications()
            
            logger.info(f"Scrape job {self.job_id} completed successfully")
            logger.info(f"Statistics: {self.result.statistics}")
            
            return self.result
            
        except Exception as e:
            logger.error(f"Scrape job {self.job_id} failed: {e}")
            
            self.result.status = "failed"
            self.result.end_time = datetime.utcnow()
            self.result.errors.append(f"Job execution failed: {str(e)}")
            
            # Try to generate report even for failed jobs
            try:
                await self.generate_report()
                await self.send_notifications()
            except Exception as report_error:
                logger.error(f"Failed to generate failure report: {report_error}")
            
            return self.result
            
        finally:
            # Always cleanup
            try:
                await self.cleanup()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")

# Convenience functions for common job patterns

async def create_simple_scrape_job(urls: List[str], template_path: str, **kwargs) -> ScrapeJob:
    """Create a simple scrape job with template"""
    config = ScrapeJobConfig(urls=urls, template_path=template_path, **kwargs)
    return ScrapeJob(config)

async def create_auto_scrape_job(urls: List[str], **kwargs) -> ScrapeJob:
    """Create an auto-detection scrape job"""
    config = ScrapeJobConfig(
        urls=urls,
        scraper_type="auto",
        template_path=None,
        **kwargs
    )
    return ScrapeJob(config)

async def create_browser_scrape_job(urls: List[str], template_path: str, **kwargs) -> ScrapeJob:
    """Create a browser-based scrape job for JavaScript-heavy sites"""
    config = ScrapeJobConfig(
        urls=urls,
        template_path=template_path,
        scraper_type="selenium",
        render_javascript=True,
        concurrent_requests=2,  # Lower concurrency for browser jobs
        **kwargs
    )
    return ScrapeJob(config)
