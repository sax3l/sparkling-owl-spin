"""
Integration tests for the complete scraping pipeline.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from src.scraper.base_scraper import BaseScraper
from src.exporters.base import BaseExporter


class TestScrapingPipeline:
    """Test cases for the complete scraping pipeline."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_scraping_pipeline(self):
        """Test the complete scraping pipeline from start to finish."""
        # Mock components
        with patch('src.scraper.http_scraper.HTTPScraper') as mock_scraper:
            with patch('src.exporters.json_exporter.JSONExporter') as mock_exporter:
                # Setup mock scraper
                mock_scraper_instance = MagicMock()
                mock_scraper.return_value = mock_scraper_instance
                mock_scraper_instance.scrape.return_value = {
                    "company_name": "Test Company",
                    "description": "A test company",
                    "employees": 100
                }
                
                # Setup mock exporter
                mock_exporter_instance = MagicMock()
                mock_exporter.return_value = mock_exporter_instance
                mock_exporter_instance.export.return_value = True
                
                # Create pipeline
                from src.crawler.pipeline import ScrapingPipeline
                pipeline = ScrapingPipeline()
                
                # Execute pipeline
                result = await pipeline.execute({
                    "url": "https://example.com",
                    "template": "company_profile_v1",
                    "export_format": "json"
                })
                
                # Verify results
                assert result["status"] == "success"
                assert "data" in result
                mock_scraper_instance.scrape.assert_called_once()
                mock_exporter_instance.export.assert_called_once()
    
    def test_pipeline_with_multiple_exporters(self):
        """Test pipeline with multiple export formats."""
        from src.crawler.pipeline import ScrapingPipeline
        
        pipeline = ScrapingPipeline()
        
        with patch.multiple(
            'src.exporters',
            csv_exporter=MagicMock(),
            json_exporter=MagicMock(),
            excel_exporter=MagicMock()
        ):
            config = {
                "url": "https://example.com",
                "template": "company_profile_v1",
                "export_formats": ["csv", "json", "excel"]
            }
            
            result = pipeline.execute_sync(config)
            
            assert result["status"] == "success"
            assert len(result["exports"]) == 3
    
    def test_pipeline_error_handling(self):
        """Test pipeline error handling and recovery."""
        from src.crawler.pipeline import ScrapingPipeline
        
        pipeline = ScrapingPipeline()
        
        with patch('src.scraper.http_scraper.HTTPScraper') as mock_scraper:
            # Simulate scraper failure
            mock_scraper_instance = MagicMock()
            mock_scraper.return_value = mock_scraper_instance
            mock_scraper_instance.scrape.side_effect = Exception("Network error")
            
            config = {
                "url": "https://example.com",
                "template": "company_profile_v1",
                "retry_count": 3
            }
            
            result = pipeline.execute_sync(config)
            
            assert result["status"] == "error"
            assert "Network error" in result["error_message"]
            # Should have tried 3 times
            assert mock_scraper_instance.scrape.call_count == 3
    
    def test_pipeline_with_data_validation(self):
        """Test pipeline with data validation steps."""
        from src.crawler.pipeline import ScrapingPipeline
        
        pipeline = ScrapingPipeline()
        
        # Valid data
        valid_data = {
            "company_name": "Valid Company",
            "email": "contact@valid.com",
            "phone": "+1-555-0123"
        }
        
        # Invalid data
        invalid_data = {
            "company_name": "",  # Empty name
            "email": "invalid-email",  # Invalid email format
            "phone": "123"  # Invalid phone format
        }
        
        assert pipeline.validate_scraped_data(valid_data, "company_profile_v1") is True
        assert pipeline.validate_scraped_data(invalid_data, "company_profile_v1") is False
    
    def test_pipeline_with_proxy_rotation(self):
        """Test pipeline with proxy rotation."""
        from src.crawler.pipeline import ScrapingPipeline
        
        pipeline = ScrapingPipeline()
        
        with patch('src.proxy_pool.manager.ProxyManager') as mock_proxy_manager:
            mock_manager = MagicMock()
            mock_proxy_manager.return_value = mock_manager
            mock_manager.get_next_proxy.return_value = {
                "http": "http://proxy1.example.com:8080",
                "https": "https://proxy1.example.com:8080"
            }
            
            config = {
                "url": "https://example.com",
                "template": "company_profile_v1",
                "use_proxy_rotation": True
            }
            
            pipeline.execute_sync(config)
            
            # Verify proxy was requested
            mock_manager.get_next_proxy.assert_called_once()
    
    def test_pipeline_rate_limiting(self):
        """Test pipeline respects rate limiting."""
        import time
        from src.crawler.pipeline import ScrapingPipeline
        
        pipeline = ScrapingPipeline(rate_limit=1.0)  # 1 second between requests
        
        urls = [
            "https://example1.com",
            "https://example2.com", 
            "https://example3.com"
        ]
        
        start_time = time.time()
        
        with patch('src.scraper.http_scraper.HTTPScraper') as mock_scraper:
            mock_scraper_instance = MagicMock()
            mock_scraper.return_value = mock_scraper_instance
            mock_scraper_instance.scrape.return_value = {"data": "test"}
            
            for url in urls:
                pipeline.execute_sync({
                    "url": url,
                    "template": "company_profile_v1"
                })
        
        elapsed_time = time.time() - start_time
        
        # Should take at least 2 seconds (2 delays between 3 requests)
        assert elapsed_time >= 2.0
