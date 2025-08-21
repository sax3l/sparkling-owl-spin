# Template Development Guide

Learn how to create powerful extraction templates for the scraping platform.

## Template Basics

Templates define how to extract data from web pages using CSS selectors, XPath expressions, and data transformations.

### Template Structure

```yaml
name: "company_profile_v2"
version: "2.0"
description: "Extract comprehensive company information"
author: "Your Name"
created: "2025-08-21"

# Required fields that must be extracted
required_fields:
  - company_name
  - website_url

# Data extraction rules
selectors:
  company_name: "h1, .company-name, [data-company-name]"
  description: ".company-description, .about, .overview"
  industry: ".industry, .sector"
  size: ".company-size, .employees"
  location: ".location, .address"
  phone: "a[href^='tel:'], .phone"
  email: "a[href^='mailto:'], .email"
  social_links:
    facebook: "a[href*='facebook.com']::attr(href)"
    linkedin: "a[href*='linkedin.com']::attr(href)"
    twitter: "a[href*='twitter.com']::attr(href)"

# Data transformations
transformations:
  phone: "phone_number"
  email: "email_address"
  description: "clean_text"
  size: "employee_count"
  social_links: "nested_object"

# Validation rules
validation:
  company_name:
    required: true
    min_length: 2
    max_length: 200
  email:
    format: "email"
  phone:
    format: "phone"

# Fallback strategies
fallbacks:
  company_name:
    - "title"
    - "meta[property='og:title']::attr(content)"
    - "h1"
  description:
    - "meta[name='description']::attr(content)"
    - "meta[property='og:description']::attr(content)"
```

## Selector Types

### CSS Selectors

Most common and readable:

```yaml
selectors:
  title: "h1"                           # Element selector
  subtitle: ".subtitle"                 # Class selector
  link: "#main-link"                    # ID selector
  price: "[data-price]"                 # Attribute selector
  image: "img.product::attr(src)"       # Attribute extraction
  text: "p.description::text"           # Text content
```

### XPath Expressions

More powerful for complex selections:

```yaml
selectors:
  company_name: "//h1[contains(@class, 'company')]/text()"
  description: "//div[@class='about']//p[position()<=3]"
  phone: "//a[starts-with(@href, 'tel:')]/@href"
  table_data: "//table[@class='data']//tr[position()>1]"
```

### Multiple Selectors

Use arrays to try multiple selectors:

```yaml
selectors:
  title:
    - "h1.main-title"
    - "h1"
    - ".page-title"
    - "title"
```

## Data Transformations

Transform extracted data into the desired format:

```yaml
transformations:
  # Clean and normalize text
  description: "clean_text"
  
  # Convert to specific data types
  price: "currency"
  date: "date"
  phone: "phone_number"
  email: "email_address"
  
  # Extract numbers
  employee_count: "extract_number"
  
  # Regular expressions
  company_id: "regex:([A-Z]{2}\\d{6})"
  
  # Custom transformations
  full_name: "join(' ')"
  tags: "split(',')"
  
  # Nested object handling
  contact:
    phone: "phone_number"
    email: "email_address"
```

### Built-in Transformations

- `clean_text` - Remove extra whitespace and special characters
- `currency` - Parse currency values
- `date` - Parse dates in various formats
- `phone_number` - Normalize phone numbers
- `email_address` - Validate and normalize email addresses
- `extract_number` - Extract numeric values
- `url` - Normalize URLs
- `boolean` - Convert to true/false
- `list` - Convert to array/list

## Advanced Features

### Conditional Extraction

Extract different data based on page structure:

```yaml
conditional:
  - condition: "exists(.product-page)"
    selectors:
      type: "product"
      name: ".product-title"
      price: ".product-price"
  
  - condition: "exists(.company-page)"
    selectors:
      type: "company"
      name: ".company-name"
      industry: ".company-industry"
```

### Dynamic Selectors

Use extracted data in selectors:

```yaml
selectors:
  company_name: "h1"
  logo: "img[alt*='{{ company_name }}']::attr(src)"
  related_links: "a[href*='{{ domain }}']"
```

### Pagination Handling

Handle multi-page data extraction:

```yaml
pagination:
  enabled: true
  next_page_selector: "a.next-page, .pagination-next"
  max_pages: 10
  delay: 2  # seconds between pages
```

### JavaScript Support

For pages requiring JavaScript execution:

```yaml
javascript:
  enabled: true
  wait_for: ".dynamic-content"
  timeout: 30
  custom_script: |
    // Custom JavaScript to execute
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(resolve => setTimeout(resolve, 2000));
```

## Testing Templates

### Template Validation

```bash
# Validate template syntax
python scripts/validate_template.py templates/my_template.yaml

# Test against sample URLs
python scripts/test_template.py templates/my_template.yaml \
  --url "https://example.com" \
  --output test_results.json
```

### Template Testing Framework

```python
# tests/test_my_template.py
import pytest
from src.scraper.template_extractor import TemplateExtractor

def test_company_profile_template():
    extractor = TemplateExtractor()
    
    with open('tests/fixtures/company_page.html') as f:
        html_content = f.read()
    
    with open('templates/company_profile_v2.yaml') as f:
        template = yaml.safe_load(f)
    
    result = extractor.extract(html_content, template)
    
    assert result['company_name'] == "Example Corp"
    assert '@' in result['email']
    assert len(result['description']) > 50
```

## Template Performance

### Optimization Tips

1. **Use specific selectors** - Avoid overly broad selectors
2. **Minimize XPath complexity** - Simple selectors are faster
3. **Cache templates** - Templates are compiled and cached
4. **Test with real data** - Validate against actual websites

### Performance Monitoring

```yaml
# Add performance metadata
performance:
  max_execution_time: 30  # seconds
  memory_limit: 256  # MB
  selector_timeout: 5  # seconds per selector
```

## Template Versioning

### Version Management

```yaml
name: "company_profile"
version: "2.1"
changelog:
  - version: "2.1"
    date: "2025-08-21"
    changes:
      - "Added social media link extraction"
      - "Improved phone number validation"
  - version: "2.0"
    date: "2025-07-15"
    changes:
      - "Complete template rewrite"
      - "Added conditional extraction"
```

### Migration Strategies

```yaml
# templates/company_profile_v2.yaml
migration:
  from_version: "1.0"
  field_mappings:
    company_title: "company_name"  # Renamed field
    company_info: "description"    # Renamed field
  deprecated_fields:
    - "old_field_name"
```

## Best Practices

1. **Start simple** - Begin with basic selectors
2. **Use fallbacks** - Always provide alternative selectors
3. **Validate data** - Add validation rules for critical fields
4. **Test thoroughly** - Test with multiple websites
5. **Document changes** - Keep detailed changelogs
6. **Monitor performance** - Track extraction success rates

## Template Library

Browse our template library at: [templates.scrapingplatform.com](https://templates.scrapingplatform.com)

- Industry-specific templates
- Popular website templates
- Community-contributed templates
- Template marketplace
