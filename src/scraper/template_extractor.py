"""
Template-based data extraction for ECaDP platform.

Implements intelligent data extraction using templates with selectors,
validation, transformation, and error handling.
"""

import re
import json
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag, NavigableString
from lxml import html, etree
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from utils.logger import get_logger
from scraper.dsl.schema import ScrapingTemplate, FieldTemplate, SelectorType
from scraper.dsl.transformers import apply_transformation

logger = get_logger(__name__)

@dataclass
class ExtractionResult:
    """Result of data extraction"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    extraction_time: float = 0.0
    extracted_fields: int = 0
    total_fields: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate extraction success rate"""
        if self.total_fields == 0:
            return 0.0
        return self.extracted_fields / self.total_fields

@dataclass
class FieldExtractionResult:
    """Result of extracting a single field"""
    field_name: str
    success: bool
    value: Any = None
    error: Optional[str] = None
    selector_used: Optional[str] = None
    transformation_applied: Optional[str] = None

class TemplateExtractor:
    """
    Template-based data extractor supporting multiple selector types and validation.
    
    Features:
    - CSS and XPath selectors
    - BeautifulSoup and lxml parsers
    - Selenium WebDriver integration
    - Data transformation and validation
    - Error handling and recovery
    - Performance optimization
    """
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0
        }
    
    def extract_data(self, 
                    html_content: Union[str, BeautifulSoup, WebElement],
                    template: ScrapingTemplate,
                    base_url: Optional[str] = None) -> ExtractionResult:
        """
        Extract data from HTML content using a template.
        
        Args:
            html_content: HTML string, BeautifulSoup object, or WebElement
            template: Scraping template defining extraction rules
            base_url: Base URL for resolving relative URLs
            
        Returns:
            ExtractionResult with extracted data and metadata
        """
        start_time = datetime.utcnow()
        result = ExtractionResult(success=False, total_fields=len(template.fields))
        
        try:
            # Prepare parsers
            soup = self._prepare_soup(html_content)
            lxml_tree = self._prepare_lxml(html_content)
            
            # Extract each field
            for field_name, field_template in template.fields.items():
                field_result = self._extract_field(
                    field_name, 
                    field_template, 
                    soup, 
                    lxml_tree, 
                    html_content,
                    base_url or self.base_url
                )
                
                if field_result.success:
                    result.data[field_name] = field_result.value
                    result.extracted_fields += 1
                else:
                    if field_result.error:
                        if field_template.required:
                            result.errors.append(f"{field_name}: {field_result.error}")
                        else:
                            result.warnings.append(f"{field_name}: {field_result.error}")
            
            # Calculate final success
            result.success = (
                result.extracted_fields > 0 and
                len(result.errors) == 0
            )
            
            # Update stats
            self.extraction_stats['total_extractions'] += 1
            if result.success:
                self.extraction_stats['successful_extractions'] += 1
            else:
                self.extraction_stats['failed_extractions'] += 1
            
        except Exception as e:
            result.errors.append(f"Extraction failed: {str(e)}")
            logger.error(f"Template extraction failed: {e}")
        
        # Calculate extraction time
        end_time = datetime.utcnow()
        result.extraction_time = (end_time - start_time).total_seconds()
        
        logger.debug(f"Extracted {result.extracted_fields}/{result.total_fields} fields in {result.extraction_time:.3f}s")
        return result
    
    def _extract_field(self,
                      field_name: str,
                      field_template: FieldTemplate,
                      soup: BeautifulSoup,
                      lxml_tree: html.HtmlElement,
                      selenium_element: Union[str, WebElement],
                      base_url: Optional[str]) -> FieldExtractionResult:
        """Extract a single field using multiple selector strategies"""
        
        # Try each selector in order
        for selector_config in field_template.selectors:
            try:
                value = None
                
                if selector_config.type == SelectorType.CSS:
                    value = self._extract_with_css(selector_config.value, soup, field_template)
                elif selector_config.type == SelectorType.XPATH:
                    value = self._extract_with_xpath(selector_config.value, lxml_tree, field_template)
                elif selector_config.type == SelectorType.REGEX:
                    if isinstance(selenium_element, str):
                        value = self._extract_with_regex(selector_config.value, selenium_element)
                elif selector_config.type == SelectorType.JSON_PATH:
                    if isinstance(selenium_element, str):
                        value = self._extract_with_jsonpath(selector_config.value, selenium_element)
                
                # If we got a value, process it
                if value is not None:
                    # Apply transformations
                    processed_value = self._apply_transformations(value, field_template, base_url)
                    
                    # Validate
                    if self._validate_field_value(processed_value, field_template):
                        return FieldExtractionResult(
                            field_name=field_name,
                            success=True,
                            value=processed_value,
                            selector_used=selector_config.value,
                            transformation_applied=str(field_template.transformations) if field_template.transformations else None
                        )
                
            except Exception as e:
                logger.debug(f"Selector {selector_config.value} failed for {field_name}: {e}")
                continue
        
        # All selectors failed
        error_msg = f"All selectors failed for field '{field_name}'"
        if field_template.default is not None:
            return FieldExtractionResult(
                field_name=field_name,
                success=True,
                value=field_template.default,
                error="Used default value"
            )
        
        return FieldExtractionResult(
            field_name=field_name,
            success=False,
            error=error_msg
        )
    
    def _prepare_soup(self, html_content: Union[str, BeautifulSoup, WebElement]) -> BeautifulSoup:
        """Prepare BeautifulSoup parser"""
        if isinstance(html_content, BeautifulSoup):
            return html_content
        elif isinstance(html_content, WebElement):
            return BeautifulSoup(html_content.get_attribute('outerHTML'), 'html.parser')
        else:
            return BeautifulSoup(html_content, 'html.parser')
    
    def _prepare_lxml(self, html_content: Union[str, BeautifulSoup, WebElement]) -> html.HtmlElement:
        """Prepare lxml parser"""
        if isinstance(html_content, BeautifulSoup):
            html_str = str(html_content)
        elif isinstance(html_content, WebElement):
            html_str = html_content.get_attribute('outerHTML')
        else:
            html_str = html_content
        
        return html.fromstring(html_str)
    
    def _extract_with_css(self, selector: str, soup: BeautifulSoup, field_template: FieldTemplate) -> Any:
        """Extract using CSS selector with BeautifulSoup"""
        elements = soup.select(selector)
        
        if not elements:
            return None
        
        if field_template.multiple:
            results = []
            for element in elements:
                value = self._extract_element_value(element, field_template.attribute)
                if value is not None:
                    results.append(value)
            return results if results else None
        else:
            return self._extract_element_value(elements[0], field_template.attribute)
    
    def _extract_with_xpath(self, selector: str, tree: html.HtmlElement, field_template: FieldTemplate) -> Any:
        """Extract using XPath selector with lxml"""
        try:
            elements = tree.xpath(selector)
            
            if not elements:
                return None
            
            if field_template.multiple:
                results = []
                for element in elements:
                    value = self._extract_lxml_value(element, field_template.attribute)
                    if value is not None:
                        results.append(value)
                return results if results else None
            else:
                return self._extract_lxml_value(elements[0], field_template.attribute)
                
        except etree.XPathEvalError as e:
            logger.debug(f"XPath error: {e}")
            return None
    
    def _extract_with_regex(self, pattern: str, text: str) -> Optional[str]:
        """Extract using regex pattern"""
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1) if match.groups() else match.group(0)
            return None
        except re.error as e:
            logger.debug(f"Regex error: {e}")
            return None
    
    def _extract_with_jsonpath(self, path: str, text: str) -> Any:
        """Extract using JSONPath (for JSON responses)"""
        try:
            # Try to parse as JSON
            data = json.loads(text)
            
            # Simple JSONPath implementation
            keys = path.strip('$').split('.')
            result = data
            
            for key in keys:
                if key.startswith('[') and key.endswith(']'):
                    # Array index
                    index = int(key[1:-1])
                    result = result[index]
                else:
                    # Object key
                    result = result[key]
            
            return result
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.debug(f"JSONPath extraction failed: {e}")
            return None
    
    def _extract_element_value(self, element: Union[Tag, NavigableString], attribute: Optional[str]) -> Optional[str]:
        """Extract value from BeautifulSoup element"""
        if isinstance(element, NavigableString):
            return str(element).strip()
        
        if attribute:
            if attribute == 'text':
                return element.get_text().strip()
            elif attribute == 'html':
                return str(element)
            else:
                return element.get(attribute)
        else:
            return element.get_text().strip()
    
    def _extract_lxml_value(self, element: Any, attribute: Optional[str]) -> Optional[str]:
        """Extract value from lxml element"""
        if isinstance(element, str):
            return element.strip()
        
        if hasattr(element, 'text_content'):
            if attribute:
                if attribute == 'text':
                    return element.text_content().strip()
                elif attribute == 'html':
                    return html.tostring(element, encoding='unicode')
                else:
                    return element.get(attribute)
            else:
                return element.text_content().strip()
        
        return str(element).strip() if element else None
    
    def _apply_transformations(self, 
                             value: Any, 
                             field_template: FieldTemplate, 
                             base_url: Optional[str]) -> Any:
        """Apply transformations to extracted value"""
        if not field_template.transformations:
            return value
        
        result = value
        
        for transformation in field_template.transformations:
            try:
                result = apply_transformation(transformation, result, base_url)
            except Exception as e:
                logger.warning(f"Transformation {transformation.type} failed: {e}")
                # Continue with original value
                break
        
        return result
    
    def _validate_field_value(self, value: Any, field_template: FieldTemplate) -> bool:
        """Validate extracted field value"""
        if value is None:
            return not field_template.required
        
        # Type validation
        if field_template.data_type:
            try:
                if field_template.data_type == 'string':
                    if not isinstance(value, str):
                        return False
                elif field_template.data_type == 'integer':
                    int(value)
                elif field_template.data_type == 'float':
                    float(value)
                elif field_template.data_type == 'boolean':
                    if not isinstance(value, bool):
                        return False
                elif field_template.data_type == 'url':
                    # Basic URL validation
                    parsed = urlparse(str(value))
                    if not parsed.scheme or not parsed.netloc:
                        return False
            except (ValueError, TypeError):
                return False
        
        # Custom validation rules
        if field_template.validation:
            for rule in field_template.validation:
                if rule.type == 'min_length':
                    if len(str(value)) < rule.value:
                        return False
                elif rule.type == 'max_length':
                    if len(str(value)) > rule.value:
                        return False
                elif rule.type == 'regex':
                    if not re.match(rule.value, str(value)):
                        return False
                elif rule.type == 'range':
                    try:
                        num_value = float(value)
                        min_val, max_val = rule.value
                        if not (min_val <= num_value <= max_val):
                            return False
                    except (ValueError, TypeError):
                        return False
        
        return True
    
    def extract_multiple_templates(self,
                                  html_content: Union[str, BeautifulSoup],
                                  templates: Dict[str, ScrapingTemplate],
                                  base_url: Optional[str] = None) -> Dict[str, ExtractionResult]:
        """Extract data using multiple templates"""
        results = {}
        
        for template_name, template in templates.items():
            result = self.extract_data(html_content, template, base_url)
            results[template_name] = result
            
        return results
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        total = self.extraction_stats['total_extractions']
        success_rate = (
            self.extraction_stats['successful_extractions'] / total
            if total > 0 else 0.0
        )
        
        return {
            'total_extractions': total,
            'successful_extractions': self.extraction_stats['successful_extractions'],
            'failed_extractions': self.extraction_stats['failed_extractions'],
            'success_rate': success_rate
        }
    
    def reset_stats(self):
        """Reset extraction statistics"""
        self.extraction_stats = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0
        }