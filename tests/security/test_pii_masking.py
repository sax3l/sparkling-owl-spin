import pytest
import re
from typing import Dict, Any, List, Tuple


class PIIScanner:
    """Advanced PII (Personally Identifiable Information) scanner and masker"""
    
    def __init__(self):
        self.patterns = {
            # Swedish patterns
            'personnummer': r'\b\d{6}-\d{4}\b|\b\d{8}-\d{4}\b|\b\d{10}\b|\b\d{12}\b',
            'ssn_us': r'\b\d{3}-\d{2}-\d{4}\b',
            'phone_se': r'\b0\d{1,3}[-\s]?\d{6,8}\b|\b\+46[-\s]?\d{1,3}[-\s]?\d{6,8}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b',
            'passport': r'\b[A-Z]{1,2}\d{6,9}\b',
            'address': r'\b\d+\s+[A-Za-z\s]+(?:gatan|vägen|stigen|platsen|torget)\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'mac_address': r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b'
        }
        
        self.sensitivity_levels = {
            'personnummer': 'high',
            'ssn_us': 'high', 
            'credit_card': 'high',
            'passport': 'high',
            'email': 'medium',
            'phone_se': 'medium',
            'iban': 'high',
            'address': 'medium',
            'ip_address': 'low',
            'mac_address': 'low'
        }
    
    def scan_text(self, text: str) -> Dict[str, List[str]]:
        """Scan text for PII patterns"""
        findings = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                findings[pii_type] = matches
                
        return findings
    
    def mask_text(self, text: str, mask_char: str = '*') -> str:
        """Mask PII in text with specified character"""
        masked_text = text
        
        for pii_type, pattern in self.patterns.items():
            if pii_type == 'personnummer':
                # Special handling for Swedish personal numbers
                masked_text = re.sub(pattern, '[PERSONNUMMER]', masked_text)
            elif pii_type == 'email':
                # Keep domain for debugging, mask local part
                masked_text = re.sub(
                    r'\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b',
                    r'[EMAIL]@\2', 
                    masked_text,
                    flags=re.IGNORECASE
                )
            elif pii_type == 'phone_se':
                masked_text = re.sub(pattern, '[TELEFON]', masked_text, flags=re.IGNORECASE)
            elif pii_type == 'credit_card':
                # Mask all but last 4 digits
                def mask_cc(match):
                    cc = re.sub(r'[-\s]', '', match.group(0))
                    return f"****-****-****-{cc[-4:]}"
                masked_text = re.sub(pattern, mask_cc, masked_text)
            else:
                # Generic masking
                masked_text = re.sub(pattern, f'[{pii_type.upper()}]', masked_text, flags=re.IGNORECASE)
                
        return masked_text
    
    def anonymize_data(self, data: Any) -> Any:
        """Recursively anonymize PII in complex data structures"""
        if isinstance(data, str):
            return self.mask_text(data)
        elif isinstance(data, dict):
            return {key: self.anonymize_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.anonymize_data(item) for item in data]
        else:
            return data
    
    def get_pii_risk_score(self, text: str) -> float:
        """Calculate PII risk score (0-1, higher = more risky)"""
        findings = self.scan_text(text)
        if not findings:
            return 0.0
        
        risk_score = 0.0
        for pii_type, matches in findings.items():
            sensitivity = self.sensitivity_levels.get(pii_type, 'low')
            match_count = len(matches)
            
            if sensitivity == 'high':
                risk_score += match_count * 0.4
            elif sensitivity == 'medium':
                risk_score += match_count * 0.2
            else:  # low
                risk_score += match_count * 0.1
        
        return min(1.0, risk_score)


# Legacy function for backward compatibility
def scrub_pii(msg: str) -> str:
    """Legacy PII scrubbing function"""
    scanner = PIIScanner()
    return scanner.mask_text(msg)


@pytest.fixture
def pii_scanner():
    """Fixture providing PII scanner instance"""
    return PIIScanner()


@pytest.fixture
def sample_pii_data():
    """Sample data containing various PII types"""
    return {
        'text_with_pii': "Kund John Doe, personnummer 850101-1234, bor på Storgatan 123, telefon 08-123456, email john.doe@example.com",
        'clean_text': "Detta är ren text utan personuppgifter",
        'mixed_data': {
            'user': {
                'name': 'Anna Svensson',
                'ssn': '920315-4567',
                'email': 'anna.svensson@company.se',
                'address': 'Kungsgatan 45'
            },
            'transaction': {
                'card': '4532-1234-5678-9012',
                'amount': 1500.00
            }
        }
    }


@pytest.mark.security
def test_scrub_pii_masks_personnummer():
    """Test basic personnummer masking"""
    msg = "personnummer=850101-1234 name=Test"
    result = scrub_pii(msg)
    
    assert "850101-1234" not in result
    assert "[PERSONNUMMER]" in result
    assert "name=Test" in result


@pytest.mark.security
def test_pii_scanner_detects_swedish_patterns(pii_scanner):
    """Test PII scanner detects Swedish-specific patterns"""
    text = "Personnummer: 850101-1234, telefon: 08-1234567"
    
    findings = pii_scanner.scan_text(text)
    
    assert 'personnummer' in findings
    assert '850101-1234' in findings['personnummer']
    assert 'phone_se' in findings
    assert '08-1234567' in findings['phone_se']


@pytest.mark.security
def test_pii_scanner_masks_multiple_types(pii_scanner, sample_pii_data):
    """Test PII scanner masks multiple PII types correctly"""
    text = sample_pii_data['text_with_pii']
    
    masked = pii_scanner.mask_text(text)
    
    # Should not contain original PII
    assert "850101-1234" not in masked
    assert "Storgatan 123" not in masked
    assert "john.doe@example.com" not in masked
    
    # Should contain masked placeholders
    assert "[PERSONNUMMER]" in masked
    assert "[ADDRESS]" in masked
    assert "[EMAIL]" in masked


@pytest.mark.security
def test_pii_scanner_handles_nested_data(pii_scanner, sample_pii_data):
    """Test PII scanner can anonymize nested data structures"""
    original_data = sample_pii_data['mixed_data']
    
    anonymized = pii_scanner.anonymize_data(original_data)
    
    # Check that structure is preserved
    assert 'user' in anonymized
    assert 'transaction' in anonymized
    
    # Check that PII is masked
    assert anonymized['user']['ssn'] == '[PERSONNUMMER]'
    assert '[EMAIL]' in anonymized['user']['email']
    assert anonymized['transaction']['card'] == '****-****-****-9012'
    
    # Check that non-PII data is preserved
    assert anonymized['transaction']['amount'] == 1500.00


@pytest.mark.security
def test_pii_risk_score_calculation(pii_scanner):
    """Test PII risk score calculation"""
    # No PII
    clean_text = "This is clean text without any personal information"
    assert pii_scanner.get_pii_risk_score(clean_text) == 0.0
    
    # Medium risk PII
    medium_risk = "Contact: john@company.com, phone: 08-123456"
    medium_score = pii_scanner.get_pii_risk_score(medium_risk)
    assert 0.3 < medium_score < 0.6
    
    # High risk PII
    high_risk = "SSN: 850101-1234, Credit card: 4532-1234-5678-9012"
    high_score = pii_scanner.get_pii_risk_score(high_risk)
    assert high_score > 0.7


@pytest.mark.security
def test_pii_scanner_preserves_non_pii(pii_scanner):
    """Test that non-PII content is preserved during masking"""
    text = "Order ID: ABC123, Amount: $499.99, Status: Processing"
    
    masked = pii_scanner.mask_text(text)
    
    # Should be unchanged as it contains no PII
    assert masked == text


@pytest.mark.security
def test_email_masking_preserves_domain(pii_scanner):
    """Test that email masking preserves domain for debugging"""
    text = "Support email: support@company.com and admin@internal.org"
    
    masked = pii_scanner.mask_text(text)
    
    # Should preserve domains but mask local parts
    assert "company.com" in masked
    assert "internal.org" in masked
    assert "support" not in masked
    assert "admin" not in masked


@pytest.mark.security
def test_credit_card_partial_masking(pii_scanner):
    """Test that credit card numbers are partially masked"""
    text = "Card number: 4532 1234 5678 9012"
    
    masked = pii_scanner.mask_text(text)
    
    # Should show last 4 digits
    assert "9012" in masked
    # Should mask first 12 digits
    assert "4532" not in masked
    assert "1234" not in masked
    assert "5678" not in masked


@pytest.mark.security
def test_ip_address_detection(pii_scanner):
    """Test IP address detection and masking"""
    text = "Server IP: 192.168.1.100, External: 203.0.113.42"
    
    findings = pii_scanner.scan_text(text)
    masked = pii_scanner.mask_text(text)
    
    assert 'ip_address' in findings
    assert len(findings['ip_address']) == 2
    assert "192.168.1.100" not in masked
    assert "[IP_ADDRESS]" in masked


@pytest.mark.security
@pytest.mark.parametrize("pii_type,test_value,should_detect", [
    ('personnummer', '850101-1234', True),
    ('personnummer', '19850101-1234', True), 
    ('personnummer', '8501011234', True),
    ('personnummer', '123-456', False),  # Too short
    ('email', 'test@domain.com', True),
    ('email', 'invalid-email', False),
    ('phone_se', '08-123456', True),
    ('phone_se', '+46-8-123456', True),
    ('phone_se', '123', False),  # Too short
    ('credit_card', '4532-1234-5678-9012', True),
    ('credit_card', '4532 1234 5678 9012', True),
    ('credit_card', '1234', False),  # Too short
])
def test_pii_pattern_validation(pii_scanner, pii_type, test_value, should_detect):
    """Parameterized test for PII pattern validation"""
    findings = pii_scanner.scan_text(test_value)
    
    if should_detect:
        assert pii_type in findings, f"Should detect {pii_type} in '{test_value}'"
        assert test_value in findings[pii_type], f"Should find exact match for {test_value}"
    else:
        assert pii_type not in findings or test_value not in findings.get(pii_type, []), \
            f"Should not detect {pii_type} in '{test_value}'"


@pytest.mark.security
def test_pii_scanner_performance():
    """Test PII scanner performance with large text"""
    import time
    
    # Generate large text with scattered PII
    large_text = "Normal text " * 1000
    large_text += "Personal info: 850101-1234, john@company.com, 08-123456"
    large_text += "More normal text " * 1000
    
    scanner = PIIScanner()
    
    start_time = time.time()
    findings = scanner.scan_text(large_text)
    scan_time = time.time() - start_time
    
    start_time = time.time()
    masked = scanner.mask_text(large_text)
    mask_time = time.time() - start_time
    
    # Performance assertions (should be fast)
    assert scan_time < 0.1, f"PII scanning too slow: {scan_time:.3f}s"
    assert mask_time < 0.1, f"PII masking too slow: {mask_time:.3f}s"
    
    # Verify PII was found and masked
    assert len(findings) > 0
    assert "[PERSONNUMMER]" in masked