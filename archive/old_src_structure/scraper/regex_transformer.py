"""
Regex transformation utilities for data processing.

Provides powerful regex-based text transformation, cleaning,
and data extraction capabilities.
"""

import re
import json
from typing import Dict, List, Optional, Any, Union, Pattern, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)

class TransformationType(Enum):
    """Types of regex transformations"""
    EXTRACT = "extract"
    REPLACE = "replace"
    SPLIT = "split"
    VALIDATE = "validate"
    CLEAN = "clean"
    FORMAT = "format"

@dataclass
class RegexRule:
    """A regex transformation rule"""
    name: str
    pattern: Union[str, Pattern]
    transformation_type: TransformationType
    replacement: Optional[str] = None
    flags: int = 0
    description: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.pattern, str):
            self.pattern = re.compile(self.pattern, self.flags)

class RegexTransformer:
    """
    Advanced regex-based text transformer.
    
    Features:
    - Multiple transformation types
    - Rule-based processing
    - Custom pattern libraries
    - Validation and cleaning
    - Format standardization
    """
    
    def __init__(self):
        self.rules: Dict[str, RegexRule] = {}
        self.compiled_patterns: Dict[str, Pattern] = {}
        
        # Initialize common patterns
        self._initialize_common_patterns()
        
        # Initialize default cleaning rules
        self._initialize_cleaning_rules()
    
    def _initialize_common_patterns(self):
        """Initialize commonly used regex patterns"""
        common_patterns = {
            # Contact information
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?\d{1,4}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            
            # Numbers and dates
            'integer': r'-?\d+',
            'float': r'-?\d+\.?\d*',
            'currency': r'[\$€£¥]?\s*\d+(?:[,\.]?\d{3})*(?:[,\.]\d{2})?',
            'date_iso': r'\d{4}-\d{2}-\d{2}',
            'date_us': r'\d{1,2}/\d{1,2}/\d{4}',
            'date_eu': r'\d{1,2}\.\d{1,2}\.\d{4}',
            'time': r'\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AaPp][Mm])?',
            
            # Identifiers
            'ipv4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'mac_address': r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})',
            'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            
            # Text patterns
            'word': r'\b\w+\b',
            'sentence': r'[A-Z][^.!?]*[.!?]',
            'hashtag': r'#\w+',
            'mention': r'@\w+',
            'html_tag': r'<[^>]+>',
            'whitespace': r'\s+',
            
            # Special characters
            'non_ascii': r'[^\x00-\x7F]',
            'punctuation': r'[^\w\s]',
            'digits_only': r'\d+',
            'letters_only': r'[A-Za-z]+',
        }
        
        for name, pattern in common_patterns.items():
            self.compiled_patterns[name] = re.compile(pattern, re.IGNORECASE)
    
    def _initialize_cleaning_rules(self):
        """Initialize default text cleaning rules"""
        cleaning_rules = [
            RegexRule(
                name="remove_html_tags",
                pattern=r'<[^>]+>',
                transformation_type=TransformationType.REPLACE,
                replacement='',
                description="Remove HTML tags"
            ),
            RegexRule(
                name="normalize_whitespace",
                pattern=r'\s+',
                transformation_type=TransformationType.REPLACE,
                replacement=' ',
                description="Normalize whitespace to single spaces"
            ),
            RegexRule(
                name="remove_extra_newlines",
                pattern=r'\n{2,}',
                transformation_type=TransformationType.REPLACE,
                replacement='\n',
                description="Remove multiple consecutive newlines"
            ),
            RegexRule(
                name="remove_non_printable",
                pattern=r'[\x00-\x1F\x7F]',
                transformation_type=TransformationType.REPLACE,
                replacement='',
                description="Remove non-printable characters"
            ),
            RegexRule(
                name="trim_whitespace",
                pattern=r'^\s+|\s+$',
                transformation_type=TransformationType.REPLACE,
                replacement='',
                description="Trim leading and trailing whitespace"
            )
        ]
        
        for rule in cleaning_rules:
            self.add_rule(rule)
    
    def add_rule(self, rule: RegexRule):
        """Add a transformation rule"""
        self.rules[rule.name] = rule
        logger.debug(f"Added regex rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a transformation rule"""
        if rule_name in self.rules:
            del self.rules[rule_name]
            logger.debug(f"Removed regex rule: {rule_name}")
            return True
        return False
    
    def extract(self, text: str, pattern: Union[str, Pattern], group: int = 0) -> List[str]:
        """
        Extract matches from text using regex.
        
        Args:
            text: Input text
            pattern: Regex pattern
            group: Group number to extract (0 for full match)
            
        Returns:
            List of extracted matches
        """
        if isinstance(pattern, str):
            if pattern in self.compiled_patterns:
                regex = self.compiled_patterns[pattern]
            else:
                regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = pattern
        
        matches = regex.finditer(text)
        
        if group == 0:
            return [match.group() for match in matches]
        else:
            return [match.group(group) for match in matches if len(match.groups()) >= group]
    
    def extract_all_groups(self, text: str, pattern: Union[str, Pattern]) -> List[Tuple]:
        """Extract all groups from matches"""
        if isinstance(pattern, str):
            if pattern in self.compiled_patterns:
                regex = self.compiled_patterns[pattern]
            else:
                regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = pattern
        
        return [match.groups() for match in regex.finditer(text)]
    
    def extract_named_groups(self, text: str, pattern: Union[str, Pattern]) -> List[Dict[str, str]]:
        """Extract named groups from matches"""
        if isinstance(pattern, str):
            regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = pattern
        
        return [match.groupdict() for match in regex.finditer(text)]
    
    def replace(self, text: str, pattern: Union[str, Pattern], replacement: str) -> str:
        """
        Replace matches in text.
        
        Args:
            text: Input text
            pattern: Regex pattern
            replacement: Replacement string
            
        Returns:
            Text with replacements applied
        """
        if isinstance(pattern, str):
            if pattern in self.compiled_patterns:
                regex = self.compiled_patterns[pattern]
            else:
                regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = pattern
        
        return regex.sub(replacement, text)
    
    def split(self, text: str, pattern: Union[str, Pattern]) -> List[str]:
        """Split text using regex pattern"""
        if isinstance(pattern, str):
            if pattern in self.compiled_patterns:
                regex = self.compiled_patterns[pattern]
            else:
                regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = pattern
        
        return regex.split(text)
    
    def validate(self, text: str, pattern: Union[str, Pattern]) -> bool:
        """Validate text against regex pattern"""
        if isinstance(pattern, str):
            if pattern in self.compiled_patterns:
                regex = self.compiled_patterns[pattern]
            else:
                regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = pattern
        
        return bool(regex.fullmatch(text))
    
    def clean_text(self, text: str, rule_names: Optional[List[str]] = None) -> str:
        """
        Clean text using specified rules.
        
        Args:
            text: Input text
            rule_names: List of rule names to apply (None for all cleaning rules)
            
        Returns:
            Cleaned text
        """
        if rule_names is None:
            # Apply default cleaning rules
            rule_names = [
                "remove_html_tags",
                "normalize_whitespace", 
                "remove_extra_newlines",
                "remove_non_printable",
                "trim_whitespace"
            ]
        
        result = text
        
        for rule_name in rule_names:
            if rule_name in self.rules:
                rule = self.rules[rule_name]
                if rule.transformation_type == TransformationType.REPLACE:
                    result = rule.pattern.sub(rule.replacement or '', result)
        
        return result
    
    def apply_rule(self, text: str, rule_name: str, **kwargs) -> Any:
        """Apply a specific transformation rule"""
        if rule_name not in self.rules:
            raise ValueError(f"Rule '{rule_name}' not found")
        
        rule = self.rules[rule_name]
        
        if rule.transformation_type == TransformationType.EXTRACT:
            group = kwargs.get('group', 0)
            return self.extract(text, rule.pattern, group)
        
        elif rule.transformation_type == TransformationType.REPLACE:
            replacement = kwargs.get('replacement', rule.replacement or '')
            return self.replace(text, rule.pattern, replacement)
        
        elif rule.transformation_type == TransformationType.SPLIT:
            return self.split(text, rule.pattern)
        
        elif rule.transformation_type == TransformationType.VALIDATE:
            return self.validate(text, rule.pattern)
        
        elif rule.transformation_type == TransformationType.CLEAN:
            return self.clean_text(text, [rule_name])
        
        else:
            raise ValueError(f"Unsupported transformation type: {rule.transformation_type}")
    
    def batch_transform(self, texts: List[str], transformations: List[Dict[str, Any]]) -> List[str]:
        """
        Apply multiple transformations to a batch of texts.
        
        Args:
            texts: List of input texts
            transformations: List of transformation configs
            
        Returns:
            List of transformed texts
        """
        results = []
        
        for text in texts:
            result = text
            
            for transform in transformations:
                if 'rule_name' in transform:
                    # Apply named rule
                    result = self.apply_rule(result, transform['rule_name'], **transform.get('kwargs', {}))
                
                elif 'pattern' in transform:
                    # Apply inline transformation
                    transform_type = transform.get('type', 'replace')
                    pattern = transform['pattern']
                    
                    if transform_type == 'extract':
                        extracted = self.extract(result, pattern, transform.get('group', 0))
                        result = ' '.join(extracted) if extracted else ''
                    
                    elif transform_type == 'replace':
                        replacement = transform.get('replacement', '')
                        result = self.replace(result, pattern, replacement)
                    
                    elif transform_type == 'split':
                        parts = self.split(result, pattern)
                        result = transform.get('join_char', ' ').join(parts)
            
            results.append(result)
        
        return results
    
    def extract_structured_data(self, text: str, extraction_config: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract structured data from text using multiple patterns.
        
        Args:
            text: Input text
            extraction_config: Dict mapping field names to patterns
            
        Returns:
            Extracted structured data
        """
        data = {}
        
        for field_name, pattern in extraction_config.items():
            try:
                if isinstance(pattern, dict):
                    # Complex extraction with options
                    pattern_str = pattern['pattern']
                    extract_type = pattern.get('type', 'first')
                    group = pattern.get('group', 0)
                    
                    matches = self.extract(text, pattern_str, group)
                    
                    if extract_type == 'first':
                        data[field_name] = matches[0] if matches else None
                    elif extract_type == 'last':
                        data[field_name] = matches[-1] if matches else None
                    elif extract_type == 'all':
                        data[field_name] = matches
                    elif extract_type == 'count':
                        data[field_name] = len(matches)
                
                else:
                    # Simple pattern extraction
                    matches = self.extract(text, pattern)
                    data[field_name] = matches[0] if matches else None
            
            except Exception as e:
                logger.warning(f"Failed to extract field '{field_name}': {e}")
                data[field_name] = None
        
        return data
    
    def normalize_text(self, text: str, normalization_rules: Optional[List[str]] = None) -> str:
        """
        Normalize text using common normalization patterns.
        
        Args:
            text: Input text
            normalization_rules: List of normalization rules to apply
            
        Returns:
            Normalized text
        """
        if normalization_rules is None:
            normalization_rules = [
                'lowercase',
                'remove_punctuation', 
                'normalize_whitespace',
                'trim'
            ]
        
        result = text
        
        for rule in normalization_rules:
            if rule == 'lowercase':
                result = result.lower()
            elif rule == 'uppercase':
                result = result.upper()
            elif rule == 'remove_punctuation':
                result = self.replace(result, 'punctuation', '')
            elif rule == 'remove_digits':
                result = self.replace(result, 'digits_only', '')
            elif rule == 'remove_non_ascii':
                result = self.replace(result, 'non_ascii', '')
            elif rule == 'normalize_whitespace':
                result = self.replace(result, 'whitespace', ' ')
            elif rule == 'trim':
                result = result.strip()
        
        return result
    
    def format_phone_number(self, phone: str, format_type: str = 'international') -> Optional[str]:
        """Format phone number using regex"""
        # Extract digits only
        digits = self.extract(phone, r'\d', 0)
        digits_str = ''.join(digits)
        
        if len(digits_str) < 10:
            return None
        
        if format_type == 'international':
            if len(digits_str) == 10:
                return f"+1-{digits_str[:3]}-{digits_str[3:6]}-{digits_str[6:]}"
            elif len(digits_str) == 11 and digits_str.startswith('1'):
                return f"+{digits_str[0]}-{digits_str[1:4]}-{digits_str[4:7]}-{digits_str[7:]}"
        
        elif format_type == 'us':
            if len(digits_str) == 10:
                return f"({digits_str[:3]}) {digits_str[3:6]}-{digits_str[6:]}"
            elif len(digits_str) == 11 and digits_str.startswith('1'):
                return f"({digits_str[1:4]}) {digits_str[4:7]}-{digits_str[7:]}"
        
        return None
    
    def format_currency(self, amount: str, currency_symbol: str = '$') -> Optional[str]:
        """Format currency amount"""
        # Extract numeric value
        numeric_matches = self.extract(amount, r'\d+(?:[.,]\d{2})?')
        
        if not numeric_matches:
            return None
        
        numeric_str = numeric_matches[0].replace(',', '')
        
        try:
            value = float(numeric_str)
            return f"{currency_symbol}{value:,.2f}"
        except ValueError:
            return None
    
    def get_pattern_library(self) -> Dict[str, str]:
        """Get available pattern library"""
        return {name: pattern.pattern for name, pattern in self.compiled_patterns.items()}
    
    def get_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all transformation rules"""
        return {
            name: {
                'pattern': rule.pattern.pattern,
                'type': rule.transformation_type.value,
                'replacement': rule.replacement,
                'description': rule.description
            }
            for name, rule in self.rules.items()
        }