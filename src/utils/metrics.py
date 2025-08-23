from prometheus_client import Counter, Histogram, CollectorRegistry, REGISTRY
from typing import Dict, Any, Optional
import time

# Check if metrics are already registered to prevent duplication
def create_counter_safe(name, description, labels, registry=REGISTRY):
    """Create a counter safely, avoiding duplication."""
    try:
        # Try to create the counter
        return Counter(name, description, labels, registry=registry)
    except ValueError:
        # If already exists, get from registry
        for collector in registry._collector_to_names:
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        # If not found, create with different registry
        custom_registry = CollectorRegistry()
        return Counter(name, description, labels, registry=custom_registry)

REQUESTS_TOTAL = create_counter_safe(
    'requests_total',
    'Total number of requests processed',
    ['mode', 'domain', 'status_code']
)

EXTRACTIONS_OK_TOTAL = create_counter_safe(
    'extractions_ok_total',
    'Total number of successful extractions',
    ['domain', 'template']
)

RETRIES_TOTAL = create_counter_safe(
    'retries_total',
    'Total number of retries attempted',
    ['domain', 'mode']
)

def create_histogram_safe(name, description, labels, registry=REGISTRY):
    """Create a histogram safely, avoiding duplication."""
    try:
        return Histogram(name, description, labels, registry=registry)
    except ValueError:
        # If already exists, get from registry
        for collector in registry._collector_to_names:
            if hasattr(collector, '_name') and collector._name == name:
                return collector
        # If not found, create with different registry
        custom_registry = CollectorRegistry()
        return Histogram(name, description, labels, registry=custom_registry)

REQUEST_DURATION_SECONDS = create_histogram_safe(
    'request_duration_seconds',
    'Request latency',
    ['mode', 'domain']
)

DQ_SCORE = create_histogram_safe(
    'dq_score',
    'Data Quality score distribution',
    ['domain', 'template']
)


class MetricsHelper:
    """Helper class for recording and managing metrics."""
    
    def __init__(self):
        self.request_timer = {}
    
    def record_request(self, mode: str, domain: str, status_code: str):
        """Record a request metric."""
        REQUESTS_TOTAL.labels(mode=mode, domain=domain, status_code=status_code).inc()
    
    def record_extraction(self, domain: str, template: str):
        """Record a successful extraction metric."""
        EXTRACTIONS_OK_TOTAL.labels(domain=domain, template=template).inc()
    
    def record_retry(self, domain: str, mode: str):
        """Record a retry attempt metric."""
        RETRIES_TOTAL.labels(domain=domain, mode=mode).inc()
    
    def start_request_timer(self, request_id: str):
        """Start timing a request."""
        self.request_timer[request_id] = time.time()
    
    def end_request_timer(self, request_id: str, mode: str, domain: str):
        """End timing a request and record the duration."""
        if request_id in self.request_timer:
            duration = time.time() - self.request_timer[request_id]
            REQUEST_DURATION_SECONDS.labels(mode=mode, domain=domain).observe(duration)
            del self.request_timer[request_id]
    
    def record_data_quality(self, domain: str, template: str, score: float):
        """Record a data quality score."""
        DQ_SCORE.labels(domain=domain, template=template).observe(score)