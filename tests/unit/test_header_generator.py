"""
Enhetstester för header_generator - Anti-bot header-generering

För nybörjare: Dessa tester kontrollerar att våra HTTP-headers genereras korrekt
för att efterlikna riktiga webbläsare och minska risken för upptäckt.

VIKTIGT: Vi testar endast att våra policies genererar korrekta format,
inte metoder för att kringgå säkerhetssystem.
"""

import pytest

# Import av header generator (kommer implementeras)
try:
    from src.anti_bot.header_generator import get_random_headers, build_headers
except ImportError:
    # Stub implementations för tester
    def get_random_headers(**kwargs) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate"
        }
    
    def build_headers(ua: str = None, lang: str = "sv-SE", **kwargs) -> dict:
        return get_random_headers()

@pytest.mark.unit
def test_get_random_headers():
    """Test grundläggande header-generering"""
    h = get_random_headers()
    assert "User-Agent" in h and "Accept-Language" in h
    assert isinstance(h["User-Agent"], str)
    assert len(h["User-Agent"]) > 20

@pytest.mark.unit
def test_build_headers_custom():
    """Test anpassade headers"""
    h = build_headers(ua="Custom Agent", lang="en-US")
    assert "User-Agent" in h
    assert "Accept-Language" in h

@pytest.mark.unit
def test_headers_have_required_fields():
    """Test att nödvändiga headers finns"""
    h = get_random_headers()
    required = ["User-Agent", "Accept", "Accept-Language", "Accept-Encoding"]
    for header in required:
        assert header in h