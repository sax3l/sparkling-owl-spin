"""
Template validation utilities for scraping templates.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from pydantic import BaseModel, Field, validator


class ValidationLevel(str, Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationResult(BaseModel):
    """Template validation result."""
    is_valid: bool = Field(..., description="Whether template is valid")
    score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


class SelectorValidator:
    """Validator for CSS and XPath selectors."""
    
    @staticmethod
    def validate_css_selector(selector: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CSS selector syntax.
        
        Args:
            selector: CSS selector string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not selector or not isinstance(selector, str):
            return False, "Selector cannot be empty"
        
        # Basic CSS selector patterns
        css_patterns = [
            r'^[a-zA-Z][a-zA-Z0-9_-]*$',  # Element selector
            r'^\.[a-zA-Z][a-zA-Z0-9_-]*$',  # Class selector
            r'^#[a-zA-Z][a-zA-Z0-9_-]*$',  # ID selector
            r'^\[[a-zA-Z][a-zA-Z0-9_-]*\]$',  # Attribute selector
            r'^\[[a-zA-Z][a-zA-Z0-9_-]*=["\'][^"\']*["\']\]$',  # Attribute value selector
        ]
        
        # Check for common invalid patterns
        invalid_patterns = [
            r'^\d',  # Starts with number
            r'[<>{}]',  # Contains invalid characters
            r'\s{2,}',  # Multiple consecutive spaces
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, selector):
                return False, f"Invalid CSS selector syntax: {selector}"
        
        # Check if it matches any valid pattern for simple selectors
        simple_selector = selector.split()[0] if ' ' in selector else selector
        
        for pattern in css_patterns:
            if re.match(pattern, simple_selector):
                return True, None
        
        # Allow complex selectors (combinators, pseudo-classes, etc.)
        if any(char in selector for char in [' ', '>', '+', '~', ':', '[']):
            return True, None
        
        return False, f"Unrecognized CSS selector pattern: {selector}"
    
    @staticmethod
    def validate_xpath_selector(selector: str) -> Tuple[bool, Optional[str]]:
        """
        Validate XPath selector syntax.
        
        Args:
            selector: XPath selector string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not selector or not isinstance(selector, str):
            return False, "XPath selector cannot be empty"
        
        # Basic XPath validation
        if not selector.startswith(('/', './', '//')):
            return False, "XPath must start with /, ./, or //"
        
        # Check for balanced brackets
        if selector.count('[') != selector.count(']'):
            return False, "Unbalanced square brackets in XPath"
        
        if selector.count('(') != selector.count(')'):
            return False, "Unbalanced parentheses in XPath"
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '{', '}']
        for char in invalid_chars:
            if char in selector:
                return False, f"Invalid character '{char}' in XPath"
        
        return True, None


class TemplateValidator:
    """Main template validator."""
    
    def __init__(self):
        self.selector_validator = SelectorValidator()
    
    def validate_template(self, template_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a complete template.
        
        Args:
            template_data: Template data dictionary
            
        Returns:
            ValidationResult: Validation results
        """
        errors = []
        warnings = []
        suggestions = []
        score = 1.0
        
        # Validate required fields
        required_fields = ['name', 'selectors']
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
                score -= 0.2
        
        # Validate template name
        if 'name' in template_data:
            name_result = self._validate_name(template_data['name'])
            if not name_result[0]:
                errors.append(name_result[1])
                score -= 0.1
        
        # Validate selectors
        if 'selectors' in template_data:
            selector_results = self._validate_selectors(template_data['selectors'])
            errors.extend(selector_results['errors'])
            warnings.extend(selector_results['warnings'])
            suggestions.extend(selector_results['suggestions'])
            score -= len(selector_results['errors']) * 0.1
            score -= len(selector_results['warnings']) * 0.05
        
        # Validate transformations if present
        if 'transformations' in template_data:
            transform_results = self._validate_transformations(template_data['transformations'])
            errors.extend(transform_results['errors'])
            warnings.extend(transform_results['warnings'])
            score -= len(transform_results['errors']) * 0.05
        
        # Validate validation rules if present
        if 'validation_rules' in template_data:
            rules_results = self._validate_validation_rules(template_data['validation_rules'])
            errors.extend(rules_results['errors'])
            warnings.extend(rules_results['warnings'])
        
        # Check for completeness
        completeness_score = self._calculate_completeness_score(template_data)
        score = (score + completeness_score) / 2
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            score=score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_name(self, name: str) -> Tuple[bool, Optional[str]]:
        """Validate template name."""
        if not name or not isinstance(name, str):
            return False, "Template name cannot be empty"
        
        if len(name) < 3:
            return False, "Template name must be at least 3 characters"
        
        if len(name) > 100:
            return False, "Template name cannot exceed 100 characters"
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False, "Template name can only contain letters, numbers, hyphens, and underscores"
        
        return True, None
    
    def _validate_selectors(self, selectors: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate template selectors."""
        errors = []
        warnings = []
        suggestions = []
        
        if not isinstance(selectors, dict):
            errors.append("Selectors must be a dictionary")
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        if not selectors:
            errors.append("Template must have at least one selector")
            return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
        
        for field_name, selector_config in selectors.items():
            field_errors, field_warnings, field_suggestions = self._validate_field_selector(
                field_name, selector_config
            )
            errors.extend(field_errors)
            warnings.extend(field_warnings)
            suggestions.extend(field_suggestions)
        
        return {'errors': errors, 'warnings': warnings, 'suggestions': suggestions}
    
    def _validate_field_selector(
        self, 
        field_name: str, 
        selector_config: Any
    ) -> Tuple[List[str], List[str], List[str]]:
        """Validate a single field selector."""
        errors = []
        warnings = []
        suggestions = []
        
        if isinstance(selector_config, str):
            # Simple string selector
            is_valid, error = self.selector_validator.validate_css_selector(selector_config)
            if not is_valid:
                errors.append(f"Field '{field_name}': {error}")
        
        elif isinstance(selector_config, dict):
            # Complex selector configuration
            if 'css' in selector_config:
                is_valid, error = self.selector_validator.validate_css_selector(selector_config['css'])
                if not is_valid:
                    errors.append(f"Field '{field_name}' CSS: {error}")
            
            if 'xpath' in selector_config:
                is_valid, error = self.selector_validator.validate_xpath_selector(selector_config['xpath'])
                if not is_valid:
                    errors.append(f"Field '{field_name}' XPath: {error}")
            
            if 'css' not in selector_config and 'xpath' not in selector_config:
                errors.append(f"Field '{field_name}': Must have either 'css' or 'xpath' selector")
            
            # Check for optional properties
            if 'attribute' in selector_config:
                attr = selector_config['attribute']
                if not isinstance(attr, str) or not attr:
                    warnings.append(f"Field '{field_name}': Invalid attribute specification")
            
            if 'multiple' in selector_config:
                if not isinstance(selector_config['multiple'], bool):
                    warnings.append(f"Field '{field_name}': 'multiple' should be a boolean")
            
            # Suggest improvements
            if 'css' in selector_config and 'xpath' in selector_config:
                suggestions.append(f"Field '{field_name}': Consider using only CSS or XPath, not both")
        
        else:
            errors.append(f"Field '{field_name}': Selector must be a string or object")
        
        return errors, warnings, suggestions
    
    def _validate_transformations(self, transformations: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate template transformations."""
        errors = []
        warnings = []
        
        if not isinstance(transformations, dict):
            errors.append("Transformations must be a dictionary")
            return {'errors': errors, 'warnings': warnings}
        
        valid_transformations = [
            'trim', 'lowercase', 'uppercase', 'regex_extract', 'regex_replace',
            'split', 'join', 'to_number', 'to_date', 'url_resolve'
        ]
        
        for field_name, transform_config in transformations.items():
            if isinstance(transform_config, list):
                for i, transform in enumerate(transform_config):
                    if isinstance(transform, dict):
                        transform_type = transform.get('type')
                        if transform_type not in valid_transformations:
                            errors.append(
                                f"Field '{field_name}' transformation {i}: "
                                f"Unknown transformation type '{transform_type}'"
                            )
                    else:
                        warnings.append(
                            f"Field '{field_name}' transformation {i}: "
                            "Should be an object with 'type' property"
                        )
            else:
                warnings.append(f"Field '{field_name}': Transformations should be an array")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _validate_validation_rules(self, validation_rules: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate template validation rules."""
        errors = []
        warnings = []
        
        if not isinstance(validation_rules, dict):
            errors.append("Validation rules must be a dictionary")
            return {'errors': errors, 'warnings': warnings}
        
        valid_rule_types = [
            'required', 'min_length', 'max_length', 'pattern', 'min_value', 'max_value',
            'data_type', 'url_format', 'email_format', 'date_format'
        ]
        
        for field_name, rules in validation_rules.items():
            if isinstance(rules, dict):
                for rule_type, rule_value in rules.items():
                    if rule_type not in valid_rule_types:
                        warnings.append(
                            f"Field '{field_name}': Unknown validation rule '{rule_type}'"
                        )
            else:
                warnings.append(f"Field '{field_name}': Validation rules should be an object")
        
        return {'errors': errors, 'warnings': warnings}
    
    def _calculate_completeness_score(self, template_data: Dict[str, Any]) -> float:
        """Calculate template completeness score."""
        score = 0.0
        max_score = 1.0
        
        # Basic required fields (0.4 points)
        if 'name' in template_data:
            score += 0.1
        if 'description' in template_data:
            score += 0.1
        if 'selectors' in template_data:
            score += 0.2
        
        # Optional but valuable fields (0.3 points)
        if 'category' in template_data:
            score += 0.1
        if 'version' in template_data:
            score += 0.05
        if 'metadata' in template_data:
            score += 0.05
        if 'transformations' in template_data:
            score += 0.1
        
        # Advanced features (0.3 points)
        if 'validation_rules' in template_data:
            score += 0.15
        if 'examples' in template_data:
            score += 0.1
        if 'documentation' in template_data:
            score += 0.05
        
        return min(score, max_score)


def validate_template(template_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a template and return results.
    
    Args:
        template_data: Template data dictionary
        
    Returns:
        ValidationResult: Validation results
    """
    validator = TemplateValidator()
    return validator.validate_template(template_data)


def validate_selector(selector: str, selector_type: str = "css") -> Tuple[bool, Optional[str]]:
    """
    Validate a single selector.
    
    Args:
        selector: Selector string
        selector_type: Type of selector ("css" or "xpath")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = SelectorValidator()
    
    if selector_type.lower() == "css":
        return validator.validate_css_selector(selector)
    elif selector_type.lower() == "xpath":
        return validator.validate_xpath_selector(selector)
    else:
        return False, f"Unknown selector type: {selector_type}"


def suggest_improvements(template_data: Dict[str, Any]) -> List[str]:
    """
    Suggest improvements for a template.
    
    Args:
        template_data: Template data dictionary
        
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    # Check for missing fields
    if 'description' not in template_data:
        suggestions.append("Add a description to help users understand the template purpose")
    
    if 'category' not in template_data:
        suggestions.append("Add a category to help organize templates")
    
    if 'examples' not in template_data:
        suggestions.append("Add example URLs to help users test the template")
    
    # Check selectors
    if 'selectors' in template_data:
        selectors = template_data['selectors']
        if len(selectors) == 1:
            suggestions.append("Consider adding more fields to extract more comprehensive data")
        
        # Check for overly specific selectors
        for field_name, selector_config in selectors.items():
            if isinstance(selector_config, str):
                selector = selector_config
            elif isinstance(selector_config, dict) and 'css' in selector_config:
                selector = selector_config['css']
            else:
                continue
            
            # Check for overly specific class selectors
            if selector.count('.') > 3:
                suggestions.append(
                    f"Field '{field_name}': Selector might be too specific, "
                    "consider using fewer class names"
                )
    
    # Check for transformations
    if 'transformations' not in template_data:
        suggestions.append("Consider adding data transformations to clean and format extracted data")
    
    # Check for validation rules
    if 'validation_rules' not in template_data:
        suggestions.append("Add validation rules to ensure data quality")
    
    return suggestions
