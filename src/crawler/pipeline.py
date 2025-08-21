"""
Main scraping pipeline coordination.
"""
import asyncio
import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from src.scraper.base_scraper import BaseScraper
from src.scraper.http_scraper import HTTPScraper
from src.scraper.selenium_scraper import SeleniumScraper
from src.exporters.base import BaseExporter
from src.exporters.json_exporter import JSONExporter
from src.exporters.csv_exporter import CSVExporter
from src.utils.validators import DataValidator
from src.proxy_pool.manager import ProxyManager

logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class PipelineConfig:
    """Configuration for scraping pipeline."""
    url: str
    template: str
    export_formats: List[str] = None
    use_proxy_rotation: bool = False
    retry_count: int = 3
    rate_limit: float = 1.0
    timeout: int = 30
    validate_data: bool = True


@dataclass
class PipelineResult:
    """Result from pipeline execution."""
    status: PipelineStatus
    data: Optional[Dict[str, Any]] = None
    exports: Optional[List[str]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    retries_used: int = 0


class ScrapingPipeline:
    """Coordinates the complete scraping pipeline."""
    
    def __init__(self, rate_limit: float = 1.0):
        """Initialize the scraping pipeline.
        
        Args:
            rate_limit: Minimum seconds between requests
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.proxy_manager = None
        self.data_validator = DataValidator()
        
        # Initialize scrapers
        self.scrapers = {
            'http': HTTPScraper(),
            'selenium': SeleniumScraper()
        }
        
        # Initialize exporters
        self.exporters = {
            'json': JSONExporter(),
            'csv': CSVExporter()
        }
    
    async def execute(self, config: Union[Dict[str, Any], PipelineConfig]) -> Dict[str, Any]:
        """Execute the scraping pipeline asynchronously.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Pipeline execution result
        """
        if isinstance(config, dict):
            config = PipelineConfig(**config)
        
        start_time = time.time()
        result = PipelineResult(status=PipelineStatus.RUNNING)
        
        try:
            # Apply rate limiting
            await self._apply_rate_limit()
            
            # Get proxy if needed
            proxy_config = None
            if config.use_proxy_rotation:
                proxy_config = await self._get_proxy()
            
            # Execute scraping with retries
            scraped_data = None
            for attempt in range(config.retry_count):
                try:
                    scraped_data = await self._scrape_data(
                        config.url, 
                        config.template,
                        proxy_config,
                        config.timeout
                    )
                    break
                except Exception as e:
                    result.retries_used = attempt + 1
                    if attempt == config.retry_count - 1:
                        raise e
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            # Validate data if required
            if config.validate_data and scraped_data:
                is_valid = self.validate_scraped_data(scraped_data, config.template)
                if not is_valid:
                    raise ValueError("Scraped data failed validation")
            
            # Export data
            export_results = []
            if config.export_formats:
                for format_name in config.export_formats:
                    export_path = await self._export_data(scraped_data, format_name)
                    export_results.append(export_path)
            
            # Prepare success result
            result.status = PipelineStatus.SUCCESS
            result.data = scraped_data
            result.exports = export_results
            result.execution_time = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            result.status = PipelineStatus.ERROR
            result.error_message = str(e)
            result.execution_time = time.time() - start_time
        
        return result.__dict__
    
    def execute_sync(self, config: Union[Dict[str, Any], PipelineConfig]) -> Dict[str, Any]:
        """Execute the pipeline synchronously.
        
        Args:
            config: Pipeline configuration
            
        Returns:
            Pipeline execution result
        """
        return asyncio.run(self.execute(config))
    
    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            await asyncio.sleep(self.rate_limit - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _get_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from proxy manager."""
        if not self.proxy_manager:
            self.proxy_manager = ProxyManager()
        
        return self.proxy_manager.get_next_proxy()
    
    async def _scrape_data(self, url: str, template: str, proxy_config: Optional[Dict[str, str]], timeout: int) -> Dict[str, Any]:
        """Scrape data from the given URL.
        
        Args:
            url: URL to scrape
            template: Template to use for extraction
            proxy_config: Proxy configuration
            timeout: Request timeout
            
        Returns:
            Scraped data
        """
        # Choose scraper based on requirements
        scraper = self._choose_scraper(template)
        
        # Configure scraper
        if proxy_config:
            scraper.set_proxies(proxy_config)
        
        scraper.timeout = timeout
        
        # Perform scraping
        return await scraper.scrape_async(url, template)
    
    def _choose_scraper(self, template: str) -> BaseScraper:
        """Choose appropriate scraper based on template requirements."""
        # For now, default to HTTP scraper
        # In future, could analyze template to determine if JS rendering needed
        return self.scrapers['http']
    
    async def _export_data(self, data: Dict[str, Any], format_name: str) -> str:
        """Export data in the specified format.
        
        Args:
            data: Data to export
            format_name: Export format
            
        Returns:
            Path to exported file
        """
        if format_name not in self.exporters:
            raise ValueError(f"Unsupported export format: {format_name}")
        
        exporter = self.exporters[format_name]
        export_path = f"exports/{int(time.time())}.{format_name}"
        
        await exporter.export_async(data, export_path)
        return export_path
    
    def validate_scraped_data(self, data: Dict[str, Any], template: str) -> bool:
        """Validate scraped data against template requirements.
        
        Args:
            data: Scraped data to validate
            template: Template name
            
        Returns:
            True if data is valid
        """
        return self.data_validator.validate_template_data(data, template)
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline execution statistics."""
        return {
            "total_executions": getattr(self, '_total_executions', 0),
            "success_rate": getattr(self, '_success_rate', 0.0),
            "average_execution_time": getattr(self, '_avg_execution_time', 0.0),
            "active_proxies": len(self.proxy_manager.get_active_proxies()) if self.proxy_manager else 0
        }
