"""
Advanced crawler engine with AI-powered extraction
Combines Firecrawl's AI capabilities with Crawlee's performance
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass
import hashlib
import re

class ExtractionMethod(Enum):
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    AI_EXTRACTION = "ai_extraction"
    HYBRID = "hybrid"

class CrawlStrategy(Enum):
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    SMART_CRAWL = "smart_crawl"  # AI-guided crawling

@dataclass
class ExtractionRule:
    name: str
    selector: str
    extraction_method: ExtractionMethod
    data_type: str  # text, number, date, url, email, etc.
    required: bool = True
    multiple: bool = False
    post_process: Optional[str] = None  # regex, transform function
    ai_instruction: Optional[str] = None  # For AI extraction

@dataclass
class CrawlTemplate:
    id: str
    name: str
    description: str
    target_patterns: List[str]  # URL patterns
    extraction_rules: List[ExtractionRule]
    pagination_config: Dict[str, Any]
    crawl_strategy: CrawlStrategy
    anti_bot_config: Dict[str, Any]
    validation_rules: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class CrawlResult:
    def __init__(self, url: str, template_id: str):
        self.url = url
        self.template_id = template_id
        self.data: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.extracted_at = datetime.now()
        self.success = False
        self.errors: List[str] = []
        self.processing_time = 0.0

class AIExtractor:
    """AI-powered content extraction matching Firecrawl capabilities"""
    
    def __init__(self):
        self.model_configs = {
            'text_extraction': {
                'model': 'gpt-4-turbo',
                'temperature': 0.1,
                'max_tokens': 2000
            },
            'structured_data': {
                'model': 'gpt-4',
                'temperature': 0.0,
                'max_tokens': 1000
            }
        }
    
    async def extract_with_ai(self, html_content: str, instruction: str, schema: Dict = None) -> Dict[str, Any]:
        """Extract structured data using AI"""
        prompt = self._build_extraction_prompt(html_content, instruction, schema)
        
        # This would integrate with OpenAI API or similar
        # For now, returning mock structure
        return {
            'extracted_data': {},
            'confidence_score': 0.85,
            'extraction_method': 'ai',
            'processing_time': 1.2
        }
    
    def _build_extraction_prompt(self, html: str, instruction: str, schema: Dict = None) -> str:
        """Build optimized prompt for content extraction"""
        base_prompt = f"""
        Extract structured data from the following HTML content based on these instructions:
        {instruction}
        
        HTML Content:
        {html[:5000]}  # Truncate for token efficiency
        
        Return the data in JSON format.
        """
        
        if schema:
            base_prompt += f"\nRequired schema: {json.dumps(schema, indent=2)}"
        
        return base_prompt

class SmartSelector:
    """Intelligent selector generation like Browse AI"""
    
    def __init__(self):
        self.selector_patterns = {
            'title': ['h1', 'h2', '.title', '#title', '[data-testid*="title"]'],
            'price': ['.price', '.cost', '[data-price]', '.amount', '.value'],
            'description': ['.description', '.desc', '.summary', '.content'],
            'image': ['img[src]', '.image img', 'picture img'],
            'link': ['a[href]', '.link', '.url']
        }
    
    async def suggest_selectors(self, html_content: str, data_type: str) -> List[Dict[str, Any]]:
        """Suggest optimal selectors for data extraction"""
        suggestions = []
        
        if data_type in self.selector_patterns:
            patterns = self.selector_patterns[data_type]
            for pattern in patterns:
                suggestions.append({
                    'selector': pattern,
                    'confidence': self._calculate_confidence(html_content, pattern),
                    'method': ExtractionMethod.CSS_SELECTOR,
                    'preview': self._get_preview_data(html_content, pattern)
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_confidence(self, html: str, selector: str) -> float:
        """Calculate confidence score for selector"""
        # Mock implementation - would use DOM analysis
        return 0.8
    
    def _get_preview_data(self, html: str, selector: str) -> str:
        """Get preview of data that would be extracted"""
        # Mock implementation
        return "Sample extracted data"

class CrawlerEngine:
    """Main crawler engine with enterprise features"""
    
    def __init__(self):
        self.ai_extractor = AIExtractor()
        self.smart_selector = SmartSelector()
        self.logger = logging.getLogger(__name__)
        self.session_pool = {}
        self.rate_limiter = {}
    
    async def execute_crawl(self, template: CrawlTemplate, urls: List[str], config: Dict[str, Any]) -> List[CrawlResult]:
        """Execute crawl job with given template and URLs"""
        results = []
        
        for url in urls:
            try:
                result = await self._crawl_single_url(url, template, config)
                results.append(result)
                
                # Rate limiting
                await self._apply_rate_limit(url, config)
                
            except Exception as e:
                self.logger.error(f"Failed to crawl {url}: {e}")
                error_result = CrawlResult(url, template.id)
                error_result.errors.append(str(e))
                results.append(error_result)
        
        return results
    
    async def _crawl_single_url(self, url: str, template: CrawlTemplate, config: Dict[str, Any]) -> CrawlResult:
        """Crawl single URL with template"""
        result = CrawlResult(url, template.id)
        start_time = datetime.now()
        
        try:
            # Fetch page content
            html_content = await self._fetch_page(url, config)
            
            # Extract data using template rules
            for rule in template.extraction_rules:
                extracted_value = await self._extract_data(html_content, rule)
                if extracted_value is not None:
                    result.data[rule.name] = extracted_value
                elif rule.required:
                    result.errors.append(f"Required field '{rule.name}' not found")
            
            # Validate extracted data
            validation_errors = await self._validate_data(result.data, template.validation_rules)
            result.errors.extend(validation_errors)
            
            result.success = len(result.errors) == 0
            result.processing_time = (datetime.now() - start_time).total_seconds()
            
        except Exception as e:
            result.errors.append(f"Crawl failed: {str(e)}")
            result.success = False
        
        return result
    
    async def _fetch_page(self, url: str, config: Dict[str, Any]) -> str:
        """Fetch page content with anti-bot protection"""
        # This would integrate with proxy manager and anti-bot service
        # Mock implementation for now
        return "<html><body>Sample content</body></html>"
    
    async def _extract_data(self, html: str, rule: ExtractionRule) -> Any:
        """Extract data based on extraction rule"""
        if rule.extraction_method == ExtractionMethod.AI_EXTRACTION:
            ai_result = await self.ai_extractor.extract_with_ai(
                html, 
                rule.ai_instruction or f"Extract {rule.name}",
                {'type': rule.data_type, 'multiple': rule.multiple}
            )
            return ai_result.get('extracted_data')
        
        elif rule.extraction_method == ExtractionMethod.CSS_SELECTOR:
            # Mock CSS selector extraction
            return f"Extracted value for {rule.name}"
        
        elif rule.extraction_method == ExtractionMethod.XPATH:
            # Mock XPath extraction
            return f"XPath extracted value for {rule.name}"
        
        elif rule.extraction_method == ExtractionMethod.HYBRID:
            # Try CSS first, fallback to AI
            css_result = await self._extract_with_css(html, rule.selector)
            if css_result:
                return css_result
            else:
                ai_result = await self.ai_extractor.extract_with_ai(html, rule.ai_instruction)
                return ai_result.get('extracted_data')
        
        return None
    
    async def _extract_with_css(self, html: str, selector: str) -> Any:
        """Extract using CSS selector"""
        # Mock implementation
        return "CSS extracted value"
    
    async def _validate_data(self, data: Dict[str, Any], validation_rules: List[Dict[str, Any]]) -> List[str]:
        """Validate extracted data"""
        errors = []
        
        for rule in validation_rules:
            field = rule.get('field')
            rule_type = rule.get('type')
            
            if field in data:
                value = data[field]
                
                if rule_type == 'regex' and not re.match(rule.get('pattern', ''), str(value)):
                    errors.append(f"Field {field} does not match pattern")
                elif rule_type == 'type' and not isinstance(value, eval(rule.get('expected_type', 'str'))):
                    errors.append(f"Field {field} has wrong type")
                elif rule_type == 'range':
                    min_val, max_val = rule.get('min'), rule.get('max')
                    if min_val is not None and value < min_val:
                        errors.append(f"Field {field} below minimum value")
                    if max_val is not None and value > max_val:
                        errors.append(f"Field {field} above maximum value")
        
        return errors
    
    async def _apply_rate_limit(self, url: str, config: Dict[str, Any]):
        """Apply rate limiting per domain"""
        domain = self._extract_domain(url)
        rate_limit = config.get('rate_limit', 1.0)  # requests per second
        
        last_request = self.rate_limiter.get(domain, datetime.min)
        time_since_last = (datetime.now() - last_request).total_seconds()
        
        if time_since_last < (1.0 / rate_limit):
            sleep_time = (1.0 / rate_limit) - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.rate_limiter[domain] = datetime.now()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import urllib.parse
        return urllib.parse.urlparse(url).netloc

class TemplateWizard:
    """No-code template creation like Octoparse"""
    
    def __init__(self):
        self.smart_selector = SmartSelector()
    
    async def create_template_from_example(self, example_url: str, sample_data: Dict[str, Any]) -> CrawlTemplate:
        """Create template by analyzing example page and data"""
        
        # Fetch example page
        html_content = await self._fetch_example_page(example_url)
        
        # Generate extraction rules
        extraction_rules = []
        for field_name, sample_value in sample_data.items():
            suggestions = await self.smart_selector.suggest_selectors(
                html_content, 
                self._infer_data_type(sample_value)
            )
            
            if suggestions:
                best_suggestion = suggestions[0]
                rule = ExtractionRule(
                    name=field_name,
                    selector=best_suggestion['selector'],
                    extraction_method=best_suggestion['method'],
                    data_type=self._infer_data_type(sample_value),
                    required=True
                )
                extraction_rules.append(rule)
        
        # Create template
        template = CrawlTemplate(
            id=hashlib.md5(f"{example_url}{datetime.now()}".encode()).hexdigest(),
            name=f"Auto-generated template for {example_url}",
            description="Template created using AI wizard",
            target_patterns=[example_url],
            extraction_rules=extraction_rules,
            pagination_config={},
            crawl_strategy=CrawlStrategy.SMART_CRAWL,
            anti_bot_config={'enabled': True},
            validation_rules=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return template
    
    async def _fetch_example_page(self, url: str) -> str:
        """Fetch example page for analysis"""
        # Mock implementation
        return "<html><body>Example content</body></html>"
    
    def _infer_data_type(self, value: Any) -> str:
        """Infer data type from sample value"""
        if isinstance(value, int):
            return "number"
        elif isinstance(value, float):
            return "decimal"
        elif isinstance(value, str):
            if "@" in value:
                return "email"
            elif value.startswith("http"):
                return "url"
            elif re.match(r'^\d{4}-\d{2}-\d{2}', value):
                return "date"
            else:
                return "text"
        else:
            return "text"
