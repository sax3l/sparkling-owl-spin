import time
import random

def apply_delay(min_delay: int = 1, max_delay: int = 5):
    """Applies a random delay to be respectful to servers."""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

# TODO: Implement more sophisticated strategies like adaptive backoff.