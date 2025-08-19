import pytest
from src.anti_bot.delay_strategy import apply_delay
import time

@pytest.mark.unit
def test_delay_strategy_range():
    # This is a simple test to ensure the function runs without error
    # A more complex test would involve mocking time.sleep
    start = time.time()
    apply_delay(0.01, 0.02)
    end = time.time()
    assert end - start >= 0.01