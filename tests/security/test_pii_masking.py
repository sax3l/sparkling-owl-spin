import pytest

# Placeholder for PII scrubber
def scrub_pii(msg):
    import re
    return re.sub(r"\d{6}-\d{4}", "[REDACTED]", msg)

@pytest.mark.unit
def test_scrub_pii_masks_personnummer():
    msg = "personnummer=850101-1234 name=Test"
    out = scrub_pii(msg)
    assert "850101-1234" not in out