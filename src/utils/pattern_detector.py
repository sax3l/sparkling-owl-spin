"""
Pattern detection utilities for ECaDP platform.

Detects common patterns like phone numbers, emails, addresses, etc.
"""

import re
import logging
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PatternMatch:
    """Represents a detected pattern match."""
    pattern_type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str = ""
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class PatternDetector:
    """Detects various patterns in text content."""
    
    def __init__(self):
        self.patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for different data types."""
        return {
            # Email patterns
            'email': re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                re.IGNORECASE
            ),
            
            # Swedish phone numbers
            'phone_se': re.compile(
                r'(?:\+46|0046|0)[\s-]?(?:7[0-9]|[1-9][0-9])[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}',
                re.IGNORECASE
            ),
            
            # International phone numbers
            'phone_international': re.compile(
                r'(?:\+[1-9]\d{1,14}|00[1-9]\d{1,14})',
                re.IGNORECASE
            ),
            
            # Swedish organization numbers
            'org_number_se': re.compile(
                r'\b(?:\d{6}[-\s]?\d{4}|\d{10})\b'
            ),
            
            # Swedish personal numbers (personnummer)
            'personal_number_se': re.compile(
                r'\b(?:19|20)?\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])[-\s]?\d{4}\b'
            ),
            
            # URLs
            'url': re.compile(
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
                re.IGNORECASE
            ),
            
            # Swedish postal codes
            'postal_code_se': re.compile(
                r'\b\d{3}\s?\d{2}\b'
            ),
            
            # Credit card numbers (basic pattern)
            'credit_card': re.compile(
                r'\b(?:\d{4}[\s-]?){3}\d{4}\b'
            ),
            
            # IBAN
            'iban': re.compile(
                r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,28}\b',
                re.IGNORECASE
            ),
            
            # Swedish bank account numbers
            'bank_account_se': re.compile(
                r'\b\d{4}[-\s]?\d{7,10}\b'
            ),
            
            # License plates (Swedish format)
            'license_plate_se': re.compile(
                r'\b[A-Z]{3}\s?\d{3}\b',
                re.IGNORECASE
            ),
            
            # Dates (various formats)
            'date': re.compile(
                r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
            ),
            
            # Times
            'time': re.compile(
                r'\b(?:[01]?\d|2[0-3]):[0-5]\d(?::[0-5]\d)?\b'
            ),
            
            # IP addresses
            'ip_address': re.compile(
                r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
            ),
            
            # MAC addresses
            'mac_address': re.compile(
                r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b'
            ),
            
            # Swedish addresses (simplified)
            'address_se': re.compile(
                r'(?:[A-ZÅÄÖ][a-zåäö]+(?:gatan|vägen|stigen|torget|platsen|plan)\s+\d+)',
                re.IGNORECASE
            )
        }
    
    def detect_all_patterns(self, text: str, context_length: int = 50) -> List[PatternMatch]:
        """Detect all patterns in the given text."""
        matches = []
        
        for pattern_type, pattern in self.patterns.items():
            pattern_matches = self.detect_pattern(text, pattern_type, context_length)
            matches.extend(pattern_matches)
        
        # Sort by position
        matches.sort(key=lambda x: x.start_pos)
        
        return matches
    
    def detect_pattern(self, text: str, pattern_type: str, context_length: int = 50) -> List[PatternMatch]:
        """Detect specific pattern in text."""
        if pattern_type not in self.patterns:
            logger.warning(f"Unknown pattern type: {pattern_type}")
            return []
        
        pattern = self.patterns[pattern_type]
        matches = []
        
        for match in pattern.finditer(text):
            start_pos = match.start()
            end_pos = match.end()
            value = match.group().strip()
            
            # Extract context
            context_start = max(0, start_pos - context_length)
            context_end = min(len(text), end_pos + context_length)
            context = text[context_start:context_end].strip()
            
            # Calculate confidence
            confidence = self._calculate_confidence(value, pattern_type)
            
            # Add metadata
            metadata = self._extract_metadata(value, pattern_type)
            
            pattern_match = PatternMatch(
                pattern_type=pattern_type,
                value=value,
                confidence=confidence,
                start_pos=start_pos,
                end_pos=end_pos,
                context=context,
                metadata=metadata
            )
            
            matches.append(pattern_match)
        
        return matches
    
    def _calculate_confidence(self, value: str, pattern_type: str) -> float:
        """Calculate confidence score for a pattern match."""
        base_confidence = 0.8
        
        # Adjust confidence based on pattern type and value characteristics
        if pattern_type == 'email':
            # Higher confidence for common domains
            if any(domain in value.lower() for domain in ['.com', '.se', '.org', '.net']):
                return min(1.0, base_confidence + 0.15)
            return base_confidence
        
        elif pattern_type == 'phone_se':
            # Remove formatting to check length
            clean_number = re.sub(r'[\s-]', '', value)
            if len(clean_number) in [10, 13]:  # Valid Swedish phone lengths
                return min(1.0, base_confidence + 0.1)
            return base_confidence - 0.2
        
        elif pattern_type == 'org_number_se':
            # Check checksum for Swedish org numbers (simplified)
            clean_number = re.sub(r'[\s-]', '', value)
            if len(clean_number) == 10:
                return min(1.0, base_confidence + 0.15)
            return base_confidence - 0.1
        
        elif pattern_type == 'url':
            # Higher confidence for complete URLs
            if value.startswith(('http://', 'https://')):
                return min(1.0, base_confidence + 0.1)
            return base_confidence - 0.1
        
        return base_confidence
    
    def _extract_metadata(self, value: str, pattern_type: str) -> Dict:
        """Extract additional metadata for pattern matches."""
        metadata = {}
        
        if pattern_type == 'email':
            parts = value.split('@')
            if len(parts) == 2:
                metadata['local_part'] = parts[0]
                metadata['domain'] = parts[1]
                metadata['domain_extension'] = parts[1].split('.')[-1] if '.' in parts[1] else ''
        
        elif pattern_type in ['phone_se', 'phone_international']:
            clean_number = re.sub(r'[\s-+]', '', value)
            metadata['clean_number'] = clean_number
            metadata['length'] = len(clean_number)
            if pattern_type == 'phone_se':
                metadata['country_code'] = 'SE'
        
        elif pattern_type == 'url':
            metadata['protocol'] = 'https' if value.startswith('https') else 'http'
            # Extract domain
            match = re.search(r'://([^/]+)', value)
            if match:
                metadata['domain'] = match.group(1)
        
        elif pattern_type == 'date':
            # Try to parse date format
            if '/' in value:
                metadata['format'] = 'slash_separated'
            elif '-' in value:
                metadata['format'] = 'dash_separated'
        
        return metadata
    
    def extract_contact_info(self, text: str) -> Dict[str, List[PatternMatch]]:
        """Extract all contact-related information."""
        contact_patterns = ['email', 'phone_se', 'phone_international', 'address_se']
        contact_info = {}
        
        for pattern_type in contact_patterns:
            matches = self.detect_pattern(text, pattern_type)
            if matches:
                contact_info[pattern_type] = matches
        
        return contact_info
    
    def extract_financial_info(self, text: str) -> Dict[str, List[PatternMatch]]:
        """Extract financial-related information."""
        financial_patterns = ['credit_card', 'iban', 'bank_account_se', 'org_number_se']
        financial_info = {}
        
        for pattern_type in financial_patterns:
            matches = self.detect_pattern(text, pattern_type)
            if matches:
                financial_info[pattern_type] = matches
        
        return financial_info
    
    def extract_identification_info(self, text: str) -> Dict[str, List[PatternMatch]]:
        """Extract identification-related information."""
        id_patterns = ['personal_number_se', 'org_number_se', 'license_plate_se']
        id_info = {}
        
        for pattern_type in id_patterns:
            matches = self.detect_pattern(text, pattern_type)
            if matches:
                id_info[pattern_type] = matches
        
        return id_info
    
    def validate_swedish_org_number(self, org_number: str) -> bool:
        """Validate Swedish organization number using checksum."""
        # Remove formatting
        clean_number = re.sub(r'[\s-]', '', org_number)
        
        if len(clean_number) != 10:
            return False
        
        try:
            # Simplified checksum validation (Luhn algorithm variant)
            digits = [int(d) for d in clean_number]
            checksum = 0
            
            for i in range(9):
                weight = 2 if i % 2 == 0 else 1
                product = digits[i] * weight
                checksum += product if product < 10 else product - 9
            
            return (checksum % 10 == 0 and digits[9] == 0) or ((10 - (checksum % 10)) % 10 == digits[9])
        
        except (ValueError, IndexError):
            return False
    
    def validate_swedish_personal_number(self, personal_number: str) -> bool:
        """Validate Swedish personal number (personnummer)."""
        # Remove formatting
        clean_number = re.sub(r'[\s-]', '', personal_number)
        
        # Handle both 10 and 12 digit formats
        if len(clean_number) == 12:
            clean_number = clean_number[2:]  # Remove century digits
        elif len(clean_number) != 10:
            return False
        
        try:
            # Check date validity (basic)
            month = int(clean_number[2:4])
            day = int(clean_number[4:6])
            
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            
            # Luhn algorithm for checksum
            digits = [int(d) for d in clean_number]
            checksum = 0
            
            for i in range(9):
                weight = 2 if i % 2 == 0 else 1
                product = digits[i] * weight
                checksum += product if product < 10 else product - 9
            
            return (10 - (checksum % 10)) % 10 == digits[9]
        
        except (ValueError, IndexError):
            return False
    
    def anonymize_sensitive_data(self, text: str, patterns_to_anonymize: List[str] = None) -> str:
        """Replace sensitive data with placeholder values."""
        if patterns_to_anonymize is None:
            patterns_to_anonymize = ['email', 'phone_se', 'personal_number_se', 'credit_card']
        
        anonymized_text = text
        
        for pattern_type in patterns_to_anonymize:
            matches = self.detect_pattern(text, pattern_type)
            
            # Replace matches with placeholders (in reverse order to maintain positions)
            for match in reversed(matches):
                placeholder = f"[{pattern_type.upper()}]"
                anonymized_text = (
                    anonymized_text[:match.start_pos] + 
                    placeholder + 
                    anonymized_text[match.end_pos:]
                )
        
        return anonymized_text

# Global detector instance
_detector = None

def get_pattern_detector() -> PatternDetector:
    """Get global pattern detector instance."""
    global _detector
    if _detector is None:
        _detector = PatternDetector()
    return _detector

# Convenience functions
def detect_emails(text: str) -> List[PatternMatch]:
    """Convenience function to detect emails."""
    return get_pattern_detector().detect_pattern(text, 'email')

def detect_phone_numbers(text: str) -> List[PatternMatch]:
    """Convenience function to detect phone numbers."""
    detector = get_pattern_detector()
    swedish_phones = detector.detect_pattern(text, 'phone_se')
    international_phones = detector.detect_pattern(text, 'phone_international')
    return swedish_phones + international_phones

def detect_all(text: str) -> List[PatternMatch]:
    """Convenience function to detect all patterns."""
    return get_pattern_detector().detect_all_patterns(text)

__all__ = [
    "PatternMatch", "PatternDetector", "get_pattern_detector",
    "detect_emails", "detect_phone_numbers", "detect_all"
]