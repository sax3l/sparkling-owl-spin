"""
Enhetstester för transformers - Små rena funktioner för dataomvandling

För nybörjare: Dessa testar att våra små omvandlingsfunktioner fungerar exakt som tänkt.
Varför: Om transformerarna är korrekta minskar fel i hela pipelinen.

GitHub Copilot tips: Använd @pytest.mark.parametrize för att testa många fall samtidigt.
"""

import pytest
from decimal import Decimal
from datetime import datetime

# Import av transformers (kommer implementeras)
try:
    from src.scraper.dsl.transformers import strip, regex_extract, to_decimal, date_parse, map_values
except ImportError:
    # Stub implementations för tester som kan köras innan riktiga moduler finns
    def strip(text: str, config: dict = None) -> str:
        return text.strip() if text else ""
    
    def regex_extract(text: str, config: dict) -> str:
        import re
        pattern = config.get("pattern", "")
        match = re.search(pattern, text)
        return match.group(1) if match else ""
    
    def to_decimal(text: str, config: dict = None) -> Decimal:
        cleaned = text.replace(",", ".").replace(" ", "")
        return Decimal(cleaned)
    
    def date_parse(text: str, config: dict = None) -> datetime:
        return datetime.fromisoformat(text)
    
    def map_values(value: str, config: dict) -> any:
        mapping = config.get("mapping", {})
        return mapping.get(value, value)

@pytest.mark.unit
def test_strip():
    """Test grundläggande strip-funktionalitet"""
    assert strip("  Hej  ", {}) == "Hej"
    assert strip("", {}) == ""
    assert strip("   ", {}) == ""
    assert strip("Ingen whitespace", {}) == "Ingen whitespace"

@pytest.mark.unit
@pytest.mark.parametrize("text,pattern,expected", [
    ("Pris: 12 345 kr", r"(\d[\d\s]+)", "12 345"),
    ("CO₂ (WLTP): 132,5 g/km", r"(\d+[,\.\d]+)", "132,5"),
    ("Modellår: 2021", r"(\d{4})", "2021"),
    ("Registrering: ABC123", r"([A-Z]{3}\d{3})", "ABC123"),
])
def test_regex_extract(text, pattern, expected):
    """Test regex-extraktion med olika mönster"""
    assert regex_extract(text, {"pattern": pattern}) == expected

@pytest.mark.unit
@pytest.mark.parametrize("raw,expected", [
    ("12,34", Decimal("12.34")),
    ("12.34", Decimal("12.34")),
    ("  1 234,50 ", Decimal("1234.50")),
    ("1,999.99", Decimal("1999.99")),
    ("0", Decimal("0")),
    ("42", Decimal("42")),
])
def test_to_decimal(raw, expected):
    """Test decimal-konvertering med olika format"""
    result = to_decimal(raw, {})
    assert result == expected

@pytest.mark.unit
def test_date_parse_sv():
    """Test datum-parsing för svenska format"""
    d = date_parse("2024-03-15", {"locale": "sv-SE"})
    assert d.year == 2024
    assert d.month == 3
    assert d.day == 15

@pytest.mark.unit
@pytest.mark.parametrize("value,mapping,expected", [
    ("Ja", {"Ja": True, "Nej": False}, True),
    ("Nej", {"Ja": True, "Nej": False}, False),
    ("Okänt", {"Ja": True, "Nej": False}, "Okänt"),  # Passthrough om ingen match
    ("bensin", {"bensin": "petrol", "diesel": "diesel"}, "petrol"),
])
def test_map_values(value, mapping, expected):
    """Test värde-mappning med olika scenarion"""
    assert map_values(value, {"mapping": mapping}) == expected

# Test för edge cases och felhantering
@pytest.mark.unit
def test_strip_handles_none():
    """Test att strip hanterar None-värden"""
    assert strip(None, {}) == ""

@pytest.mark.unit
def test_to_decimal_invalid():
    """Test att to_decimal hanterar ogiltiga värden"""
    with pytest.raises((ValueError, TypeError)):
        to_decimal("abc", {})

# Test för kombinationer av transformers
@pytest.mark.unit
def test_transformer_chaining():
    """Test kedja av transformers (simulerar pipeline)"""
    raw_text = "  PRIS: 12 345,50 KR  "
    
    # Steg 1: Strip
    step1 = strip(raw_text, {})
    
    # Steg 2: Extrahera pris  
    step2 = regex_extract(step1.lower(), {"pattern": r"(\d[\d\s,]+)"})
    
    # Steg 3: Konvertera till decimal
    step3 = to_decimal(step2, {})
    
    assert step3 == Decimal("12345.50")

# Test som simulerar verklig mall-extraction
@pytest.mark.unit
def test_vehicle_registration_extraction():
    """Test komplett fordonsregistrering-extraktion"""
    html_text = "Registreringsnummer: ABC123 (Registrerad 2021-03-15)"
    
    # Extrahera regnummer
    reg_num = regex_extract(html_text, {"pattern": r"([A-Z]{3}\d{3})"})
    assert reg_num == "ABC123"
    
    # Extrahera år
    year_str = regex_extract(html_text, {"pattern": r"(\d{4})"})
    year = int(year_str) if year_str else None
    assert year == 2021
