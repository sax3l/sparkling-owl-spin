"""
Tests for template extractor functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper.template_extractor import TemplateExtractor


class TestTemplateExtractor:
    """Test cases for TemplateExtractor class."""
    
    def test_template_extractor_initialization(self):
        """Test that TemplateExtractor initializes correctly."""
        extractor = TemplateExtractor()
        assert extractor is not None
    
    def test_extract_with_xpath_selector(self):
        """Test extraction using XPath selectors."""
        extractor = TemplateExtractor()
        
        # Mock HTML content
        html_content = """
        <html>
            <body>
                <div class="company">
                    <h1>Test Company</h1>
                    <p class="description">A test company description</p>
                </div>
            </body>
        </html>
        """
        
        template = {
            "selectors": {
                "company_name": "//h1/text()",
                "description": "//p[@class='description']/text()"
            }
        }
        
        result = extractor.extract(html_content, template)
        
        assert "company_name" in result
        assert "description" in result
    
    def test_extract_with_css_selector(self):
        """Test extraction using CSS selectors."""
        extractor = TemplateExtractor()
        
        html_content = """
        <html>
            <body>
                <div class="product">
                    <span class="name">Product Name</span>
                    <span class="price">$99.99</span>
                </div>
            </body>
        </html>
        """
        
        template = {
            "selectors": {
                "product_name": ".name",
                "price": ".price"
            }
        }
        
        result = extractor.extract(html_content, template)
        
        assert "product_name" in result
        assert "price" in result
    
    def test_extract_handles_missing_elements(self):
        """Test that extraction handles missing elements gracefully."""
        extractor = TemplateExtractor()
        
        html_content = "<html><body><p>Simple content</p></body></html>"
        
        template = {
            "selectors": {
                "missing_element": "//div[@class='nonexistent']",
                "another_missing": ".not-found"
            }
        }
        
        result = extractor.extract(html_content, template)
        
        # Should return empty values for missing elements
        assert result.get("missing_element") is None or result.get("missing_element") == ""
        assert result.get("another_missing") is None or result.get("another_missing") == ""
    
    def test_extract_with_transformations(self):
        """Test extraction with data transformations."""
        extractor = TemplateExtractor()
        
        html_content = """
        <div class="data">
            <span class="amount">  $1,234.56  </span>
            <span class="date">2025-08-21T10:30:00Z</span>
        </div>
        """
        
        template = {
            "selectors": {
                "amount": ".amount",
                "date": ".date"
            },
            "transformations": {
                "amount": "strip,currency",
                "date": "strip,datetime"
            }
        }
        
        result = extractor.extract(html_content, template)
        
        assert "amount" in result
        assert "date" in result
    
    def test_validate_template_structure(self):
        """Test template structure validation."""
        extractor = TemplateExtractor()
        
        # Valid template
        valid_template = {
            "selectors": {
                "title": "//h1/text()"
            }
        }
        assert extractor.validate_template(valid_template) is True
        
        # Invalid template - missing selectors
        invalid_template = {
            "metadata": {"version": "1.0"}
        }
        assert extractor.validate_template(invalid_template) is False
    
    def test_extract_multiple_elements(self):
        """Test extraction of multiple elements with same selector."""
        extractor = TemplateExtractor()
        
        html_content = """
        <ul>
            <li class="item">Item 1</li>
            <li class="item">Item 2</li>
            <li class="item">Item 3</li>
        </ul>
        """
        
        template = {
            "selectors": {
                "items": "//li[@class='item']/text()"
            },
            "multiple": ["items"]
        }
        
        result = extractor.extract(html_content, template)
        
        assert "items" in result
        assert isinstance(result["items"], list)
        assert len(result["items"]) == 3
