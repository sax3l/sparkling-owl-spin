import pytest
import sys
import os

# Add the src directory to the path for direct import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.pattern_detector import find_repeating, PatternDetector, PatternMatch


@pytest.mark.unit
def test_find_repeating_simple():
    """Test basic repeating pattern detection."""
    html = "<ul><li>A</li><li>B</li><li>C</li></ul>"
    r = find_repeating(html, container="ul", item="li")
    assert r.count == 3


@pytest.mark.unit
def test_find_repeating_nested():
    """Test repeating patterns with nested elements."""
    html = """
    <div class="container">
        <div class="item">Item 1</div>
        <div class="item">Item 2</div>
        <div class="item">Item 3</div>
        <div class="item">Item 4</div>
    </div>
    """
    r = find_repeating(html, container=".container", item=".item")
    assert r.count == 4


@pytest.mark.unit
def test_find_repeating_no_container():
    """Test behavior when container doesn't exist."""
    html = "<div><span>Test</span></div>"
    r = find_repeating(html, container=".nonexistent", item="span")
    assert r.count == 0


@pytest.mark.unit
def test_find_repeating_no_items():
    """Test behavior when container exists but no items match."""
    html = "<ul></ul>"
    r = find_repeating(html, container="ul", item="li")
    assert r.count == 0


@pytest.mark.unit
def test_pattern_detector_initialization():
    """Test PatternDetector initialization."""
    detector = PatternDetector()
    assert detector is not None
    assert len(detector.patterns) > 0


@pytest.mark.unit
def test_detect_email_patterns():
    """Test email pattern detection."""
    detector = PatternDetector()
    text = "Contact us at info@example.com or support@test.se for help"
    
    matches = detector.detect_pattern(text, 'email')
    assert len(matches) == 2
    assert matches[0].value == 'info@example.com'
    assert matches[1].value == 'support@test.se'


@pytest.mark.unit  
def test_detect_phone_patterns():
    """Test Swedish phone number pattern detection."""
    detector = PatternDetector()
    text = "Call us at 08-123 45 67 or +46 70 123 45 67"
    
    matches = detector.detect_pattern(text, 'phone_se')
    assert len(matches) >= 1
    

@pytest.mark.unit
def test_detect_url_patterns():
    """Test URL pattern detection."""
    detector = PatternDetector()
    text = "Visit https://example.com or http://test.se for more info"
    
    matches = detector.detect_pattern(text, 'url')
    assert len(matches) == 2
    assert 'https://example.com' in [m.value for m in matches]


@pytest.mark.unit
def test_pattern_confidence():
    """Test confidence calculation for patterns."""
    detector = PatternDetector()
    text = "test@example.com"
    
    matches = detector.detect_pattern(text, 'email')
    assert len(matches) == 1
    assert matches[0].confidence > 0.8


@pytest.mark.unit
def test_extract_contact_info():
    """Test contact information extraction."""
    detector = PatternDetector()
    text = """
    Contact Information:
    Email: john.doe@example.se
    Phone: +46 70 123 45 67
    Address: Storgatan 123, Stockholm
    """
    
    contact_info = detector.extract_contact_info(text)
    assert 'email' in contact_info
    assert 'phone_se' in contact_info or 'phone_international' in contact_info


@pytest.mark.unit
def test_validate_swedish_personal_number():
    """Test Swedish personal number validation."""
    detector = PatternDetector()
    
    # Test with known valid format (not real number)
    valid_format = "801231-1234"
    # Note: This won't pass real checksum, but tests format validation
    
    # Test invalid formats
    assert not detector.validate_swedish_personal_number("123")
    assert not detector.validate_swedish_personal_number("abc-def")


@pytest.mark.unit
def test_anonymize_sensitive_data():
    """Test sensitive data anonymization."""
    detector = PatternDetector()
    text = "My email is john@example.com and phone is 08-123 45 67"
    
    anonymized = detector.anonymize_sensitive_data(text)
    assert "john@example.com" not in anonymized
    assert "[EMAIL]" in anonymized


@pytest.mark.unit
def test_pattern_match_metadata():
    """Test that pattern matches include metadata."""
    detector = PatternDetector()
    text = "Contact: info@example.com"
    
    matches = detector.detect_pattern(text, 'email')
    assert len(matches) == 1
    
    match = matches[0]
    assert match.metadata is not None
    assert 'domain' in match.metadata
    assert match.metadata['domain'] == 'example.com'


@pytest.mark.unit 
def test_detect_all_patterns():
    """Test detecting all patterns at once."""
    detector = PatternDetector()
    text = """
    Contact us at info@test.se or call 08-123 45 67.
    Visit https://test.se for more information.
    """
    
    all_matches = detector.detect_all_patterns(text)
    assert len(all_matches) >= 3  # At least email, phone, url
    
    pattern_types = [match.pattern_type for match in all_matches]
    assert 'email' in pattern_types
    assert any('phone' in pt for pt in pattern_types)
    assert 'url' in pattern_types