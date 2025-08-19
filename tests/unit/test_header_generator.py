import pytest
from src.anti_bot.header_generator import get_random_headers

@pytest.mark.unit
def test_build_headers_minimal():
    h = get_random_headers()
    assert "User-Agent" in h and "Accept-Language" in h