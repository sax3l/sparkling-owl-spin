"""
PII (Personally Identifiable Information) Scanner

Advanced scanner for detecting and masking PII in text and data structures.
Supports Swedish-specific patterns and GDPR compliance requirements.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SensitivityLevel(Enum):
    """PII sensitivity levels for risk assessment"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PIIMatch:
    """Represents a PII match found in text"""
    pii_type: str
    value: str
    start_pos: int
    end_pos: int
    sensitivity: SensitivityLevel
    confidence: float = 1.0


class PIIScanner:
    """
    Advanced PII scanner with Swedish-specific patterns.
    
    Supports detection and masking of:
    - Swedish personal numbers (personnummer)
    - Email addresses
    - Phone numbers (Swedish format)
    - Credit card numbers
    - IBAN numbers
    - Addresses
    - IP addresses
    - And more...
    """
    
    def __init__(self, custom_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize PII scanner with patterns and sensitivity levels.
        
        Args:
            custom_patterns: Optional custom regex patterns to add
        """
        self.patterns = {
            # Swedish personal numbers (all formats)
            'personnummer': r'\b(?:\d{2})?(\d{6})-(\d{4})\b|\b\d{10}\b|\b\d{12}\b',
            
            # International social security numbers
            'ssn_us': r'\b\d{3}-\d{2}-\d{4}\b',
            'ssn_uk': r'\b[A-Z]{2}\d{6}[A-Z]\b',
            
            # Swedish phone numbers
            'phone_se': r'(?:\+46[-\s]?\d{1,3}[-\s]?\d{6,7}|0\d{1,3}[-\s]?\d{6,7})\b',
            'phone_mobile_se': r'(?:\+46|0)7\d{8}\b',
            
            # International phone numbers  
            'phone_intl': r'\+\d{1,3}[-\s]?\d{4,14}',
            
            # Email addresses
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            
            # Financial information
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
            'swift_bic': r'\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b',
            
            # ID documents
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'driving_license_se': r'\b[A-Z]{2}\d{6}\b',
            
            # Addresses (Swedish specific)
            'address_se': r'\b(?:\d+\s+[A-Za-z\säöåÄÖÅ]+(?:gatan|vägen|stigen|platsen|torget|gård|väg|plan)|[A-Za-z\säöåÄÖÅ]*(?:gatan|vägen|stigen|platsen|torget|gård|väg|plan)\s+\d+)\b',
            'postal_code_se': r'\b\d{3}\s?\d{2}\b',
            
            # Technical identifiers
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'ipv6': r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',
            'mac_address': r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b',
            'uuid': r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b',
            
            # Organization numbers (Swedish)
            'org_number_se': r'\b\d{6}-\d{4}\b',
            
            # Vehicle information
            'license_plate_se': r'\b[A-Z]{3}\s?\d{2}[A-Z0-9]\b',
            'vin_number': r'\b[A-HJ-NPR-Z0-9]{17}\b'
        }
        
        # Add custom patterns if provided
        if custom_patterns:
            self.patterns.update(custom_patterns)
        
        # Sensitivity levels for each PII type
        self.sensitivity_levels = {
            'personnummer': SensitivityLevel.CRITICAL,
            'ssn_us': SensitivityLevel.CRITICAL,
            'ssn_uk': SensitivityLevel.CRITICAL,
            'credit_card': SensitivityLevel.CRITICAL,
            'passport': SensitivityLevel.HIGH,
            'driving_license_se': SensitivityLevel.HIGH,
            'iban': SensitivityLevel.HIGH,
            'swift_bic': SensitivityLevel.HIGH,
            'org_number_se': SensitivityLevel.HIGH,
            'email': SensitivityLevel.MEDIUM,
            'phone_se': SensitivityLevel.MEDIUM,
            'phone_mobile_se': SensitivityLevel.MEDIUM,
            'phone_intl': SensitivityLevel.MEDIUM,
            'address_se': SensitivityLevel.MEDIUM,
            'postal_code_se': SensitivityLevel.MEDIUM,
            'license_plate_se': SensitivityLevel.MEDIUM,
            'vin_number': SensitivityLevel.MEDIUM,
            'ip_address': SensitivityLevel.LOW,
            'ipv6': SensitivityLevel.LOW,
            'mac_address': SensitivityLevel.LOW,
            'uuid': SensitivityLevel.LOW
        }
        
        # Compiled regex patterns for performance
        self._compiled_patterns = {
            pii_type: re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pii_type, pattern in self.patterns.items()
        }
        
        logger.info(f"PII Scanner initialized with {len(self.patterns)} patterns")
    
    def scan_text(self, text: str, include_positions: bool = False) -> Union[Dict[str, List[str]], List[PIIMatch]]:
        """
        Scan text for PII patterns.
        
        Args:
            text: Text to scan for PII
            include_positions: If True, return PIIMatch objects with positions
            
        Returns:
            Dictionary of PII type -> list of matches, or list of PIIMatch objects
        """
        if not text:
            return [] if include_positions else {}
        
        if include_positions:
            matches = []
            for pii_type, compiled_pattern in self._compiled_patterns.items():
                for match in compiled_pattern.finditer(text):
                    pii_match = PIIMatch(
                        pii_type=pii_type,
                        value=match.group(0),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        sensitivity=self.sensitivity_levels.get(pii_type, SensitivityLevel.LOW),
                        confidence=self._calculate_confidence(pii_type, match.group(0))
                    )
                    matches.append(pii_match)
            return matches
        else:
            findings = {}
            for pii_type, compiled_pattern in self._compiled_patterns.items():
                matches = compiled_pattern.findall(text)
                if matches:
                    # Handle tuples from capturing groups
                    if matches and isinstance(matches[0], tuple):
                        matches = ['-'.join(match) if isinstance(match, tuple) else match for match in matches]
                    findings[pii_type] = matches
            return findings
    
    def mask_text(self, text: str, mask_char: str = '*', preserve_format: bool = True) -> str:
        """
        Mask PII in text with specified character or replacement.
        
        Args:
            text: Text to mask
            mask_char: Character to use for masking
            preserve_format: Whether to preserve original format structure
            
        Returns:
            Text with PII masked
        """
        if not text:
            return text
        
        masked_text = text
        
        # Process patterns in order of sensitivity (most sensitive first)
        sorted_patterns = sorted(
            self._compiled_patterns.items(),
            key=lambda x: self.sensitivity_levels.get(x[0], SensitivityLevel.LOW).value,
            reverse=True
        )
        
        for pii_type, compiled_pattern in sorted_patterns:
            masked_text = self._apply_mask(masked_text, pii_type, compiled_pattern, mask_char, preserve_format)
        
        return masked_text
    
    def _apply_mask(self, text: str, pii_type: str, pattern: re.Pattern, mask_char: str, preserve_format: bool) -> str:
        """Apply masking for a specific PII type"""
        
        def create_mask_replacement(match_text: str) -> str:
            """Create appropriate mask replacement for the matched text"""
            if pii_type == 'personnummer':
                return '[PERSONNUMMER]'
            elif pii_type == 'email':
                # Preserve domain for debugging if requested
                if preserve_format and '@' in match_text:
                    domain = match_text.split('@')[1]
                    return f'[EMAIL]@{domain}'
                return '[EMAIL]'
            elif pii_type in ['phone_se', 'phone_mobile_se', 'phone_intl']:
                return '[TELEFON]'
            elif pii_type == 'credit_card':
                if preserve_format and len(match_text) >= 4:
                    # Show last 4 digits
                    cleaned = re.sub(r'[-\s]', '', match_text)
                    return f"****-****-****-{cleaned[-4:]}"
                return '[KREDITKORT]'
            elif pii_type == 'address_se':
                return '[ADRESS]'
            elif pii_type == 'iban':
                if preserve_format and len(match_text) >= 4:
                    return f"[IBAN-{match_text[-4:]}]"
                return '[IBAN]'
            elif pii_type == 'ip_address':
                return '[IP-ADRESS]'
            elif pii_type == 'license_plate_se':
                return '[REGNUMMER]'
            else:
                return f'[{pii_type.upper().replace("_", "-")}]'
        
        return pattern.sub(lambda m: create_mask_replacement(m.group(0)), text)
    
    def anonymize_data(self, data: Any, deep_copy: bool = True) -> Any:
        """
        Recursively anonymize PII in complex data structures.
        
        Args:
            data: Data structure to anonymize
            deep_copy: Whether to create deep copy before anonymization
            
        Returns:
            Anonymized data structure
        """
        import copy
        
        if deep_copy:
            data = copy.deepcopy(data)
        
        if isinstance(data, str):
            return self.mask_text(data)
        elif isinstance(data, dict):
            return {key: self.anonymize_data(value, deep_copy=False) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.anonymize_data(item, deep_copy=False) for item in data]
        elif isinstance(data, tuple):
            return tuple(self.anonymize_data(item, deep_copy=False) for item in data)
        else:
            return data
    
    def get_pii_risk_score(self, text: str) -> float:
        """
        Calculate PII risk score (0-1, higher = more risky).
        
        Args:
            text: Text to analyze
            
        Returns:
            Risk score between 0.0 and 1.0
        """
        if not text:
            return 0.0
        
        findings = self.scan_text(text)
        if not findings:
            return 0.0
        
        risk_score = 0.0
        total_matches = 0
        
        for pii_type, matches in findings.items():
            sensitivity = self.sensitivity_levels.get(pii_type, SensitivityLevel.LOW)
            match_count = len(matches)
            total_matches += match_count
            
            # Weight by sensitivity level
            if sensitivity == SensitivityLevel.CRITICAL:
                risk_score += match_count * 0.5
            elif sensitivity == SensitivityLevel.HIGH:
                risk_score += match_count * 0.3
            elif sensitivity == SensitivityLevel.MEDIUM:
                risk_score += match_count * 0.2
            else:  # LOW
                risk_score += match_count * 0.1
        
        # Normalize by text length and match density
        text_length = len(text.split())
        density_factor = min(1.0, total_matches / max(1, text_length / 100))
        
        return min(1.0, risk_score * (1 + density_factor))
    
    def _calculate_confidence(self, pii_type: str, value: str) -> float:
        """Calculate confidence score for a PII match"""
        # Basic confidence calculation based on pattern complexity
        if pii_type == 'personnummer':
            # Swedish personal number validation (basic Luhn check could be added)
            return 0.95 if re.match(r'\d{6}-\d{4}', value) else 0.8
        elif pii_type == 'email':
            # Basic email validation
            return 0.9 if '@' in value and '.' in value.split('@')[1] else 0.7
        elif pii_type == 'credit_card':
            # Could add Luhn algorithm validation here
            return 0.85
        elif pii_type in ['phone_se', 'phone_mobile_se']:
            return 0.8
        else:
            return 0.75
    
    def validate_pii_match(self, pii_type: str, value: str) -> bool:
        """
        Validate if a PII match is truly valid (reduce false positives).
        
        Args:
            pii_type: Type of PII to validate
            value: Value to validate
            
        Returns:
            True if the match is valid PII
        """
        if pii_type == 'personnummer':
            return self._validate_swedish_personal_number(value)
        elif pii_type == 'credit_card':
            return self._validate_credit_card(value)
        elif pii_type == 'email':
            return self._validate_email(value)
        elif pii_type == 'iban':
            return self._validate_iban(value)
        else:
            return True  # Default to true for other types
    
    def _validate_swedish_personal_number(self, value: str) -> bool:
        """Validate Swedish personal number using Luhn algorithm"""
        # Remove any non-digits
        digits = re.sub(r'\D', '', value)
        
        if len(digits) == 10:
            # YYMMDDXXXX format
            pass
        elif len(digits) == 12:
            # YYYYMMDDXXXX format, take last 10 digits
            digits = digits[-10:]
        else:
            return False
        
        # Basic date validation
        try:
            month = int(digits[2:4])
            day = int(digits[4:6])
            
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):
                return False
        except ValueError:
            return False
        
        # Luhn algorithm validation
        return self._luhn_check(digits)
    
    def _validate_credit_card(self, value: str) -> bool:
        """Validate credit card using Luhn algorithm"""
        digits = re.sub(r'\D', '', value)
        if len(digits) < 13 or len(digits) > 19:
            return False
        return self._luhn_check(digits)
    
    def _validate_email(self, value: str) -> bool:
        """Basic email validation"""
        if '@' not in value:
            return False
        local, domain = value.rsplit('@', 1)
        if not local or not domain:
            return False
        if '.' not in domain:
            return False
        return True
    
    def _validate_iban(self, value: str) -> bool:
        """Basic IBAN validation"""
        # Remove spaces and convert to uppercase
        iban = re.sub(r'\s', '', value.upper())
        
        # Check length (15-34 characters)
        if len(iban) < 15 or len(iban) > 34:
            return False
        
        # Check format (2 letters + 2 digits + alphanumeric)
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z0-9]+$', iban):
            return False
        
        # Could add full IBAN checksum validation here
        return True
    
    def _luhn_check(self, card_number: str) -> bool:
        """Implement Luhn algorithm for validation"""
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10
        
        return luhn_checksum(card_number) == 0
    
    def get_supported_pii_types(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about supported PII types.
        
        Returns:
            Dictionary with PII type information
        """
        return {
            pii_type: {
                'pattern': pattern,
                'sensitivity': self.sensitivity_levels.get(pii_type, SensitivityLevel.LOW).value,
                'description': self._get_pii_description(pii_type)
            }
            for pii_type, pattern in self.patterns.items()
        }
    
    def _get_pii_description(self, pii_type: str) -> str:
        """Get human-readable description for PII type"""
        descriptions = {
            'personnummer': 'Swedish personal identification number',
            'ssn_us': 'US Social Security Number',
            'phone_se': 'Swedish phone number',
            'email': 'Email address',
            'credit_card': 'Credit card number',
            'iban': 'International Bank Account Number',
            'address_se': 'Swedish address',
            'ip_address': 'IP address',
            'license_plate_se': 'Swedish license plate'
        }
        return descriptions.get(pii_type, f'Pattern for {pii_type}')


# Convenience functions for backward compatibility
def scrub_pii(text: str, mask_char: str = '*') -> str:
    """Legacy function for PII scrubbing"""
    scanner = PIIScanner()
    return scanner.mask_text(text, mask_char)


def scan_for_pii(text: str) -> Dict[str, List[str]]:
    """Legacy function for PII scanning"""
    scanner = PIIScanner()
    return scanner.scan_text(text)
