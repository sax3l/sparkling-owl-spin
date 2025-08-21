"""
Metrics collection and observability for the crawler application.

Provides:
- Performance metrics tracking
- Business metrics collection  
- System health monitoring
- Custom metric types
- Integration with monitoring systems
"""

import time
import asyncio
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import threading
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)

class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Metric:
    """Individual metric data point."""
    name: str
    value: Union[int, float]
    metric_type: MetricType
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    
class MetricsCollector:
    """Central metrics collection and management."""
    
    def __init__(self, flush_interval: int = 60):
        self.flush_interval = flush_interval
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        self._running = False
        self._flush_task = None
    
    def start(self):
        """Start the metrics collector background tasks."""
        if self._running:
            return
        
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
        logger.info("Metrics collector started")
    
    async def stop(self):
        """Stop the metrics collector."""
        self._running = False
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Final flush
        await self._flush_metrics()
        logger.info("Metrics collector stopped")
    
    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Record a counter metric (monotonically increasing)."""
        with self._lock:
            key = self._metric_key(name, labels)
            self.counters[key] += value
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.COUNTER,
                timestamp=datetime.utcnow(),
                labels=labels or {}
            )
            self.metrics[name].append(metric)
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a gauge metric (can go up or down)."""
        with self._lock:
            key = self._metric_key(name, labels)
            self.gauges[key] = value
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.GAUGE,
                timestamp=datetime.utcnow(),
                labels=labels or {}
            )
            self.metrics[name].append(metric)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric (distribution of values)."""
        with self._lock:
            key = self._metric_key(name, labels)
            self.histograms[key].append(value)
            
            metric = Metric(
                name=name,
                value=value,
                metric_type=MetricType.HISTOGRAM,
                timestamp=datetime.utcnow(),
                labels=labels or {}
            )
            self.metrics[name].append(metric)
    
    def record_timer(self, name: str, duration: float, labels: Optional[Dict[str, str]] = None):
        """Record a timer metric (duration of operations)."""
        with self._lock:
            key = self._metric_key(name, labels)
            self.timers[key].append(duration)
            
            metric = Metric(
                name=name,
                value=duration,
                metric_type=MetricType.TIMER,
                timestamp=datetime.utcnow(),
                labels=labels or {}
            )
            self.metrics[name].append(metric)
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current counter value."""
        key = self._metric_key(name, labels)
        return self.counters.get(key, 0.0)
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """Get current gauge value."""
        key = self._metric_key(name, labels)
        return self.gauges.get(key)
    
    def get_histogram_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get histogram statistics (min, max, avg, percentiles)."""
        key = self._metric_key(name, labels)
        values = list(self.histograms[key])
        
        if not values:
            return {}
        
        values.sort()
        n = len(values)
        
        return {
            "count": n,
            "min": values[0],
            "max": values[-1],
            "avg": sum(values) / n,
            "p50": values[n // 2],
            "p90": values[int(n * 0.9)] if n > 10 else values[-1],
            "p95": values[int(n * 0.95)] if n > 20 else values[-1],
            "p99": values[int(n * 0.99)] if n > 100 else values[-1]
        }
    
    def get_timer_stats(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get timer statistics."""
        key = self._metric_key(name, labels)
        return self.get_histogram_stats(name, labels)  # Same logic
    
    def _metric_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        """Generate a unique key for a metric with labels."""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    async def _flush_loop(self):
        """Background task to periodically flush metrics."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics flush loop: {e}")
    
    async def _flush_metrics(self):
        """Flush metrics to storage/monitoring systems."""
        with self._lock:
            if not any(self.metrics.values()):
                return
            
            # Prepare metrics for export
            export_data = self._prepare_export_data()
            
            # Clear old metrics (keep recent for debugging)
            self._cleanup_old_metrics()
        
        # Send to monitoring systems (Prometheus, etc.)
        await self._export_to_prometheus(export_data)
        await self._export_to_logging(export_data)
    
    def _prepare_export_data(self) -> Dict[str, Any]:
        """Prepare metrics data for export."""
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {},
            "timers": {}
        }
        
        # Calculate histogram statistics
        for name, values in self.histograms.items():
            if values:
                export_data["histograms"][name] = self._calculate_stats(list(values))
        
        # Calculate timer statistics  
        for name, values in self.timers.items():
            if values:
                export_data["timers"][name] = self._calculate_stats(values)
        
        return export_data
    
    def _calculate_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistics for a list of values."""
        if not values:
            return {}
        
        values.sort()
        n = len(values)
        
        return {
            "count": n,
            "sum": sum(values),
            "min": values[0],
            "max": values[-1],
            "avg": sum(values) / n,
            "p50": values[n // 2],
            "p90": values[int(n * 0.9)] if n > 10 else values[-1],
            "p95": values[int(n * 0.95)] if n > 20 else values[-1],
            "p99": values[int(n * 0.99)] if n > 100 else values[-1]
        }
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory leaks."""
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        
        for name, metric_list in self.metrics.items():
            # Keep only recent metrics
            self.metrics[name] = [
                m for m in metric_list 
                if m.timestamp > cutoff_time
            ]
    
    async def _export_to_prometheus(self, data: Dict[str, Any]):
        """Export metrics to Prometheus format."""
        # In a real implementation, this would write to a Prometheus push gateway
        # or update metrics that Prometheus scrapes
        logger.debug("Exporting metrics to Prometheus format")
    
    async def _export_to_logging(self, data: Dict[str, Any]):
        """Export metrics to structured logs."""
        logger.info("Metrics summary", extra={
            "metrics": data,
            "event_type": "metrics_flush"
        })

# Context manager for timing operations
class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, metrics_collector: MetricsCollector, name: str, 
                 labels: Optional[Dict[str, str]] = None):
        self.metrics_collector = metrics_collector
        self.name = name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time
            self.metrics_collector.record_timer(self.name, duration, self.labels)

# Decorator for timing functions
def timed_function(metrics_collector: MetricsCollector, name: Optional[str] = None):
    """Decorator to time function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            timer_name = name or f"function.{func.__name__}"
            with Timer(metrics_collector, timer_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Business-specific metrics
class CrawlerMetrics:
    """Crawler-specific business metrics."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def record_page_scraped(self, site: str, template: str, success: bool):
        """Record a page scraping attempt."""
        labels = {"site": site, "template": template, "status": "success" if success else "failed"}
        self.metrics.record_counter("pages_scraped_total", 1.0, labels)
    
    def record_proxy_usage(self, proxy_id: str, success: bool, response_time: float):
        """Record proxy usage metrics."""
        labels = {"proxy_id": proxy_id, "status": "success" if success else "failed"}
        self.metrics.record_counter("proxy_requests_total", 1.0, labels)
        
        if success:
            self.metrics.record_timer("proxy_response_time", response_time, {"proxy_id": proxy_id})
    
    def record_data_quality(self, site: str, template: str, completeness_score: float):
        """Record data quality metrics."""
        labels = {"site": site, "template": template}
        self.metrics.record_gauge("data_quality_score", completeness_score, labels)
    
    def record_template_drift(self, site: str, template: str, drift_score: float):
        """Record template drift detection."""
        labels = {"site": site, "template": template}
        self.metrics.record_gauge("template_drift_score", drift_score, labels)
        
        if drift_score > 0.7:  # High drift threshold
            self.metrics.record_counter("template_drift_alerts", 1.0, labels)

# Global metrics instance
_metrics_instance: Optional[MetricsCollector] = None

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_instance
    
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
        _metrics_instance.start()
    
    return _metrics_instance

async def shutdown_metrics():
    """Shutdown the global metrics collector."""
    global _metrics_instance
    
    if _metrics_instance:
        await _metrics_instance.stop()
        _metrics_instance = None
