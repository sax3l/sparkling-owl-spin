import pytest

# Placeholder for metrics
class Counter:
    def __init__(self): self.value = 0
    def inc(self): self.value += 1
COUNTERS = {"scrape_success": Counter()}

@pytest.mark.unit
def test_counter_inc():
    before = COUNTERS["scrape_success"].value
    COUNTERS["scrape_success"].inc()
    assert COUNTERS["scrape_success"].value == before + 1