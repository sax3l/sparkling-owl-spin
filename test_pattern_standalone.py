#!/usr/bin/env python3
"""
Standalone test for pattern detector functionality
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import just the pattern detector module directly  
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pattern_detector", 
    src_path / "utils" / "pattern_detector.py"
)
pattern_detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pattern_detector)

def test_find_repeating():
    """Test the find_repeating function"""
    html = "<ul><li>A</li><li>B</li><li>C</li></ul>"
    result = pattern_detector.find_repeating(html, "ul", "li")
    
    print(f"✓ find_repeating test: Found {result.count} items (expected 3)")
    assert result.count == 3
    
def test_pattern_detector_class():
    """Test the PatternDetector class"""
    detector = pattern_detector.PatternDetector()
    text = "Contact us at info@example.com or support@test.se for help"
    
    matches = detector.detect_pattern(text, 'email')
    print(f"✓ email detection test: Found {len(matches)} emails (expected 2)")
    assert len(matches) == 2
    
    print("✓ Email matches:")
    for match in matches:
        print(f"  - {match.value} (confidence: {match.confidence:.2f})")

def test_phone_detection():
    """Test phone number detection"""
    detector = pattern_detector.PatternDetector()
    text = "Call us at 08-123 45 67 or +46 70 123 45 67"
    
    matches = detector.detect_pattern(text, 'phone_se')
    print(f"✓ phone detection test: Found {len(matches)} Swedish phone numbers")
    
    for match in matches:
        print(f"  - {match.value} (confidence: {match.confidence:.2f})")

if __name__ == "__main__":
    print("🧪 Testing Pattern Detector...")
    print("=" * 50)
    
    try:
        test_find_repeating()
        test_pattern_detector_class()
        test_phone_detection()
        
        print("=" * 50)
        print("✅ All pattern detector tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
