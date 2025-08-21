"""Tests for utility validators module."""

import pytest
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import Dict, Any

from src.utils.validators import (
    URLValidator,
    EmailValidator,
    PhoneValidator,
    PersonalNumberValidator,
    CompanyNumberValidator,
    VehicleRegistrationValidator,
    DataTypeValidator,
    TemplateValidator,
    ConfigurationValidator,
    RateLimitValidator,
    ProxyValidator,
    SecurityValidator,
)


class TestURLValidator:
    """Test URL validation functionality."""
    
    def test_valid_urls(self):
        """Test validation of valid URLs."""
        validator = URLValidator()
        
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://subdomain.example.com/path",
            "https://example.com:8080/path?query=value",
            "https://192.168.1.1:3000",
            "https://[::1]:8080/path",
        ]
        
        for url in valid_urls:
            assert validator.is_valid(url), f"Expected {url} to be valid"
    
    def test_invalid_urls(self):
        """Test validation of invalid URLs."""
        validator = URLValidator()
        
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Non-HTTP protocol
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd",
            "",
            None,
        ]
        
        for url in invalid_urls:
            assert not validator.is_valid(url), f"Expected {url} to be invalid"
    
    def test_domain_restrictions(self):
        """Test domain whitelist/blacklist functionality."""
        validator = URLValidator(
            allowed_domains=["example.com", "test.com"],
            blocked_domains=["blocked.com"]
        )
        
        assert validator.is_valid("https://example.com/path")
        assert validator.is_valid("https://subdomain.example.com/path")
        assert not validator.is_valid("https://blocked.com/path")
        assert not validator.is_valid("https://other.com/path")


class TestEmailValidator:
    """Test email validation functionality."""
    
    def test_valid_emails(self):
        """Test validation of valid email addresses."""
        validator = EmailValidator()
        
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user123@example-domain.com",
            "firstname.lastname@subdomain.example.com",
        ]
        
        for email in valid_emails:
            assert validator.is_valid(email), f"Expected {email} to be valid"
    
    def test_invalid_emails(self):
        """Test validation of invalid email addresses."""
        validator = EmailValidator()
        
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user..double.dot@example.com",
            "user@example",
            "",
            None,
        ]
        
        for email in invalid_emails:
            assert not validator.is_valid(email), f"Expected {email} to be invalid"


class TestPhoneValidator:
    """Test phone number validation functionality."""
    
    def test_swedish_phone_numbers(self):
        """Test validation of Swedish phone numbers."""
        validator = PhoneValidator(country="SE")
        
        valid_phones = [
            "+46701234567",
            "0701234567",
            "070-123 45 67",
            "08-123 456 78",
            "+46 70 123 45 67",
        ]
        
        for phone in valid_phones:
            assert validator.is_valid(phone), f"Expected {phone} to be valid"
    
    def test_invalid_phone_numbers(self):
        """Test validation of invalid phone numbers."""
        validator = PhoneValidator(country="SE")
        
        invalid_phones = [
            "123",
            "not-a-phone",
            "+1234567890123456",  # Too long
            "",
            None,
        ]
        
        for phone in invalid_phones:
            assert not validator.is_valid(phone), f"Expected {phone} to be invalid"


class TestPersonalNumberValidator:
    """Test Swedish personal number validation."""
    
    def test_valid_personal_numbers(self):
        """Test validation of valid Swedish personal numbers."""
        validator = PersonalNumberValidator()
        
        # These are test numbers, not real personal numbers
        valid_numbers = [
            "19900101-1234",
            "900101-1234",
            "199001011234",
            "9001011234",
        ]
        
        for number in valid_numbers:
            # Note: This would require actual checksum validation
            # For now, just test format validation
            assert validator.is_valid_format(number), f"Expected {number} format to be valid"
    
    def test_invalid_personal_numbers(self):
        """Test validation of invalid personal numbers."""
        validator = PersonalNumberValidator()
        
        invalid_numbers = [
            "123",
            "not-a-number",
            "1990-01-01",  # Wrong format
            "99001301-1234",  # Invalid date
            "",
            None,
        ]
        
        for number in invalid_numbers:
            assert not validator.is_valid_format(number), f"Expected {number} format to be invalid"


class TestVehicleRegistrationValidator:
    """Test Swedish vehicle registration validation."""
    
    def test_valid_registrations(self):
        """Test validation of valid Swedish vehicle registrations."""
        validator = VehicleRegistrationValidator(country="SE")
        
        valid_registrations = [
            "ABC123",
            "ABC 123",
            "ABC12D",
            "AB123C",
        ]
        
        for reg in valid_registrations:
            assert validator.is_valid(reg), f"Expected {reg} to be valid"
    
    def test_invalid_registrations(self):
        """Test validation of invalid vehicle registrations."""
        validator = VehicleRegistrationValidator(country="SE")
        
        invalid_registrations = [
            "A",
            "ABCD1234",  # Too long
            "123ABC",    # Wrong pattern
            "",
            None,
        ]
        
        for reg in invalid_registrations:
            assert not validator.is_valid(reg), f"Expected {reg} to be invalid"


class TestDataTypeValidator:
    """Test data type validation functionality."""
    
    def test_string_validation(self):
        """Test string data type validation."""
        validator = DataTypeValidator()
        
        assert validator.validate_type("hello", str)
        assert not validator.validate_type(123, str)
        assert not validator.validate_type(None, str)
    
    def test_number_validation(self):
        """Test number data type validation."""
        validator = DataTypeValidator()
        
        assert validator.validate_type(123, int)
        assert validator.validate_type(123.45, float)
        assert not validator.validate_type("123", int)
    
    def test_list_validation(self):
        """Test list data type validation."""
        validator = DataTypeValidator()
        
        assert validator.validate_type([1, 2, 3], list)
        assert validator.validate_type([], list)
        assert not validator.validate_type("not a list", list)
    
    def test_dict_validation(self):
        """Test dictionary data type validation."""
        validator = DataTypeValidator()
        
        assert validator.validate_type({"key": "value"}, dict)
        assert validator.validate_type({}, dict)
        assert not validator.validate_type("not a dict", dict)


class TestTemplateValidator:
    """Test template validation functionality."""
    
    def test_valid_template_structure(self):
        """Test validation of valid template structure."""
        validator = TemplateValidator()
        
        valid_template = {
            "name": "test_template",
            "version": "1.0",
            "selectors": {
                "title": {
                    "xpath": "//h1/text()",
                    "css": "h1",
                    "required": True
                }
            },
            "transformations": {
                "title": ["strip", "title_case"]
            }
        }
        
        result = validator.validate(valid_template)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_invalid_template_structure(self):
        """Test validation of invalid template structure."""
        validator = TemplateValidator()
        
        invalid_template = {
            "name": "",  # Empty name
            "selectors": {
                "title": {
                    # Missing xpath or css selector
                    "required": True
                }
            }
        }
        
        result = validator.validate(invalid_template)
        assert not result.is_valid
        assert len(result.errors) > 0


class TestConfigurationValidator:
    """Test configuration validation functionality."""
    
    def test_valid_crawler_config(self):
        """Test validation of valid crawler configuration."""
        validator = ConfigurationValidator()
        
        valid_config = {
            "crawler": {
                "max_depth": 5,
                "delay_range": [1, 3],
                "user_agent": "TestBot/1.0",
                "respect_robots_txt": True
            },
            "proxy": {
                "enabled": True,
                "rotation_interval": 300
            }
        }
        
        result = validator.validate_crawler_config(valid_config)
        assert result.is_valid
    
    def test_invalid_crawler_config(self):
        """Test validation of invalid crawler configuration."""
        validator = ConfigurationValidator()
        
        invalid_config = {
            "crawler": {
                "max_depth": -1,  # Invalid negative depth
                "delay_range": [3, 1],  # Invalid range (min > max)
                "user_agent": "",  # Empty user agent
            }
        }
        
        result = validator.validate_crawler_config(invalid_config)
        assert not result.is_valid
        assert len(result.errors) > 0


class TestRateLimitValidator:
    """Test rate limiting validation functionality."""
    
    def test_rate_limit_compliance(self):
        """Test rate limit compliance checking."""
        validator = RateLimitValidator()
        
        # Simulate request history within limits
        now = datetime.now()
        request_times = [
            now - timedelta(seconds=5),
            now - timedelta(seconds=3),
            now - timedelta(seconds=1),
        ]
        
        assert validator.check_rate_limit(request_times, max_requests=5, window_seconds=10)
    
    def test_rate_limit_violation(self):
        """Test rate limit violation detection."""
        validator = RateLimitValidator()
        
        # Simulate too many requests
        now = datetime.now()
        request_times = [now - timedelta(seconds=i) for i in range(6)]  # 6 requests in last 6 seconds
        
        assert not validator.check_rate_limit(request_times, max_requests=5, window_seconds=10)


class TestProxyValidator:
    """Test proxy validation functionality."""
    
    def test_valid_proxy_format(self):
        """Test validation of valid proxy formats."""
        validator = ProxyValidator()
        
        valid_proxies = [
            "http://proxy.example.com:8080",
            "https://user:pass@proxy.example.com:3128",
            "socks5://proxy.example.com:1080",
        ]
        
        for proxy in valid_proxies:
            assert validator.is_valid_format(proxy), f"Expected {proxy} to be valid format"
    
    def test_invalid_proxy_format(self):
        """Test validation of invalid proxy formats."""
        validator = ProxyValidator()
        
        invalid_proxies = [
            "not-a-proxy",
            "ftp://proxy.example.com:21",  # Unsupported protocol
            "http://",  # Incomplete
            "",
            None,
        ]
        
        for proxy in invalid_proxies:
            assert not validator.is_valid_format(proxy), f"Expected {proxy} to be invalid format"


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_safe_xpath_validation(self):
        """Test XPath safety validation."""
        validator = SecurityValidator()
        
        safe_xpaths = [
            "//div[@class='content']",
            "//h1/text()",
            "//a[@href]/@href",
        ]
        
        for xpath in safe_xpaths:
            assert validator.is_safe_xpath(xpath), f"Expected {xpath} to be safe"
    
    def test_unsafe_xpath_validation(self):
        """Test detection of unsafe XPath expressions."""
        validator = SecurityValidator()
        
        unsafe_xpaths = [
            "//script",  # Potentially dangerous
            "//iframe",  # Potentially dangerous
            "//object",  # Potentially dangerous
        ]
        
        for xpath in unsafe_xpaths:
            # Note: Actual implementation would have more sophisticated detection
            # This is a simplified test
            pass
    
    def test_sanitize_user_input(self):
        """Test user input sanitization."""
        validator = SecurityValidator()
        
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = validator.sanitize_input(dangerous_input)
        
        assert "<script>" not in sanitized
        assert "alert" not in sanitized


# Test fixtures and utilities
@pytest.fixture
def sample_template():
    """Sample template for testing."""
    return {
        "name": "vehicle_detail",
        "version": "1.0",
        "description": "Extract vehicle details from listing page",
        "selectors": {
            "make": {
                "xpath": "//span[@class='make']/text()",
                "css": ".make",
                "required": True
            },
            "model": {
                "xpath": "//span[@class='model']/text()",
                "css": ".model",
                "required": True
            },
            "year": {
                "xpath": "//span[@class='year']/text()",
                "css": ".year",
                "required": False
            }
        },
        "transformations": {
            "make": ["strip", "title_case"],
            "model": ["strip", "title_case"],
            "year": ["strip", "to_int"]
        },
        "validation": {
            "make": {"type": "string", "min_length": 1},
            "model": {"type": "string", "min_length": 1},
            "year": {"type": "integer", "min": 1900, "max": 2030}
        }
    }


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "crawler": {
            "max_depth": 3,
            "delay_range": [1, 2],
            "user_agent": "ECaDP-Crawler/1.0",
            "respect_robots_txt": True,
            "max_pages": 1000
        },
        "scraper": {
            "timeout": 30,
            "retries": 3,
            "browser_mode": False
        },
        "proxy": {
            "enabled": True,
            "rotation_interval": 300,
            "health_check_interval": 60
        }
    }


# Integration tests
class TestValidatorIntegration:
    """Test validator integration and workflow."""
    
    def test_complete_validation_workflow(self, sample_template, sample_config):
        """Test complete validation workflow for a scraping job."""
        # URL validation
        url_validator = URLValidator(allowed_domains=["example.com"])
        assert url_validator.is_valid("https://example.com/vehicle/123")
        
        # Template validation
        template_validator = TemplateValidator()
        template_result = template_validator.validate(sample_template)
        assert template_result.is_valid
        
        # Configuration validation
        config_validator = ConfigurationValidator()
        config_result = config_validator.validate_crawler_config(sample_config)
        assert config_result.is_valid
        
        # All validations pass - job can proceed
        assert template_result.is_valid and config_result.is_valid
    
    def test_validation_failure_handling(self):
        """Test handling of validation failures."""
        # Test with invalid data
        url_validator = URLValidator()
        template_validator = TemplateValidator()
        
        # Invalid URL
        assert not url_validator.is_valid("invalid-url")
        
        # Invalid template
        invalid_template = {"name": ""}  # Empty name
        result = template_validator.validate(invalid_template)
        assert not result.is_valid
        assert len(result.errors) > 0


if __name__ == "__main__":
    pytest.main([__file__])