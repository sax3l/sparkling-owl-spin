"""
Metrics Collection System
========================

Comprehensive metrics collection and monitoring for the ECaDP platform.
Supports Prometheus metrics, custom counters, histograms, and gauges.
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import asyncio
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, Summary, Info,
        CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available. Install with: pip install prometheus_client")

@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class MetricSeries:
    """Time series of metric points"""
    name: str
    metric_type: str
    description: str
    points: deque = field(default_factory=lambda: deque(maxlen=1000))
    labels: Dict[str, str] = field(default_factory=dict)
    
    def add_point(self, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Add a new metric point"""
        point = MetricPoint(
            timestamp=datetime.utcnow(),
            value=value,
            labels=labels or {}
        )
        self.points.append(point)

class MetricsCollector:
    """
    Comprehensive metrics collection system
    
    Features:
    - Prometheus integration (if available)
    - Custom metric storage
    - System metrics collection
    - Application metrics tracking
    - Export capabilities
    """
    
    def __init__(self, 
                 enable_prometheus: bool = True,
                 enable_system_metrics: bool = True,
                 collection_interval: int = 30):
        
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.enable_system_metrics = enable_system_metrics and PSUTIL_AVAILABLE
        self.collection_interval = collection_interval
        
        # Custom metrics storage
        self.metrics: Dict[str, MetricSeries] = {}
        self.lock = threading.RLock()
        
        # Prometheus registry and metrics
        if self.enable_prometheus:
            self.registry = CollectorRegistry()
            self._init_prometheus_metrics()
        
        # System metrics collection
        self._last_cpu_percent = 0
        self._last_network_io = None
        self._last_disk_io = None
        
        # Background collection task
        self._collection_task = None
        self._running = False
        
        # Initialize built-in metrics
        self._init_builtin_metrics()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        if not self.enable_prometheus:
            return
        
        # System metrics
        self.cpu_usage = Gauge(
            'ecadp_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'ecadp_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'ecadp_disk_usage_percent',
            'Disk usage percentage',
            ['device'],
            registry=self.registry
        )
        
        # Application metrics
        self.http_requests_total = Counter(
            'ecadp_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'ecadp_http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.job_duration = Histogram(
            'ecadp_job_duration_seconds',
            'Job execution duration',
            ['job_type', 'status'],
            registry=self.registry
        )
        
        self.job_counter = Counter(
            'ecadp_jobs_total',
            'Total jobs executed',
            ['job_type', 'status'],
            registry=self.registry
        )
        
        self.crawler_requests = Counter(
            'ecadp_crawler_requests_total',
            'Total crawler requests',
            ['domain', 'status'],
            registry=self.registry
        )
        
        self.scraper_extractions = Counter(
            'ecadp_scraper_extractions_total',
            'Total data extractions',
            ['template', 'status'],
            registry=self.registry
        )
        
        self.proxy_usage = Gauge(
            'ecadp_proxy_pool_size',
            'Current proxy pool size',
            ['status'],
            registry=self.registry
        )
        
        self.webhook_events = Counter(
            'ecadp_webhook_events_total',
            'Total webhook events',
            ['event_type', 'status'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connections = Gauge(
            'ecadp_db_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'ecadp_db_query_duration_seconds',
            'Database query duration',
            ['operation'],
            registry=self.registry
        )
    
    def _init_builtin_metrics(self):
        """Initialize built-in metric series"""
        builtin_metrics = [
            ('system_cpu_percent', 'gauge', 'System CPU usage percentage'),
            ('system_memory_bytes', 'gauge', 'System memory usage in bytes'),
            ('system_disk_percent', 'gauge', 'System disk usage percentage'),
            ('http_requests_count', 'counter', 'HTTP requests count'),
            ('http_response_time_ms', 'histogram', 'HTTP response time in milliseconds'),
            ('job_execution_count', 'counter', 'Job execution count'),
            ('job_execution_time_ms', 'histogram', 'Job execution time in milliseconds'),
            ('crawler_requests_count', 'counter', 'Crawler requests count'),
            ('scraper_extractions_count', 'counter', 'Scraper extractions count'),
            ('webhook_events_count', 'counter', 'Webhook events count'),
            ('error_count', 'counter', 'Error count'),
            ('active_users', 'gauge', 'Active users count'),
        ]
        
        for name, metric_type, description in builtin_metrics:
            self.metrics[name] = MetricSeries(
                name=name,
                metric_type=metric_type,
                description=description
            )
    
    def start_collection(self):
        """Start background metrics collection"""
        if self._running:
            return
        
        self._running = True
        if self.enable_system_metrics:
            self._collection_task = asyncio.create_task(self._collection_loop())
    
    def stop_collection(self):
        """Stop background metrics collection"""
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
    
    async def _collection_loop(self):
        """Background collection loop"""
        while self._running:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def _collect_system_metrics(self):
        """Collect system metrics"""
        if not PSUTIL_AVAILABLE:
            return
            
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_gauge('system_cpu_percent', cpu_percent)
            
            if self.enable_prometheus:
                self.cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.record_gauge('system_memory_bytes', memory.used)
            
            if self.enable_prometheus:
                self.memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_gauge('system_disk_percent', disk_percent)
            
            if self.enable_prometheus:
                self.disk_usage.labels(device='/').set(disk_percent)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def record_counter(self, name: str, value: Union[int, float] = 1, labels: Optional[Dict[str, str]] = None):
        """Record a counter metric"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = MetricSeries(
                    name=name,
                    metric_type='counter',
                    description=f'Counter metric: {name}'
                )
            
            # For counters, we increment the last value
            last_value = 0
            if self.metrics[name].points:
                last_value = self.metrics[name].points[-1].value
            
            self.metrics[name].add_point(last_value + value, labels)
    
    def record_gauge(self, name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Record a gauge metric"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = MetricSeries(
                    name=name,
                    metric_type='gauge',
                    description=f'Gauge metric: {name}'
                )
            
            self.metrics[name].add_point(value, labels)
    
    def record_histogram(self, name: str, value: Union[int, float], labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric"""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = MetricSeries(
                    name=name,
                    metric_type='histogram',
                    description=f'Histogram metric: {name}'
                )
            
            self.metrics[name].add_point(value, labels)
    
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a counter by 1"""
        self.record_counter(name, 1, labels)
    
    def time_function(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        """Decorator to time function execution"""
        def decorator(func):
            if asyncio.iscoroutinefunction(func):
                async def async_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    finally:
                        duration = (time.time() - start_time) * 1000  # Convert to ms
                        self.record_histogram(metric_name, duration, labels)
                return async_wrapper
            else:
                def sync_wrapper(*args, **kwargs):
                    start_time = time.time()
                    try:
                        result = func(*args, **kwargs)
                        return result
                    finally:
                        duration = (time.time() - start_time) * 1000  # Convert to ms
                        self.record_histogram(metric_name, duration, labels)
                return sync_wrapper
        return decorator
    
    # Application-specific metric methods
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        labels = {'method': method, 'endpoint': endpoint, 'status': str(status_code)}
        
        self.record_counter('http_requests_count', labels=labels)
        self.record_histogram('http_response_time_ms', duration * 1000, labels)
        
        if self.enable_prometheus:
            self.http_requests_total.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
            self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_job_execution(self, job_type: str, status: str, duration: float):
        """Record job execution metrics"""
        labels = {'job_type': job_type, 'status': status}
        
        self.record_counter('job_execution_count', labels=labels)
        self.record_histogram('job_execution_time_ms', duration * 1000, labels)
        
        if self.enable_prometheus:
            self.job_counter.labels(job_type=job_type, status=status).inc()
            self.job_duration.labels(job_type=job_type, status=status).observe(duration)
    
    def record_crawler_request(self, domain: str, status: str):
        """Record crawler request metrics"""
        labels = {'domain': domain, 'status': status}
        
        self.record_counter('crawler_requests_count', labels=labels)
        
        if self.enable_prometheus:
            self.crawler_requests.labels(domain=domain, status=status).inc()
    
    def record_scraper_extraction(self, template: str, status: str, records_count: int = 1):
        """Record scraper extraction metrics"""
        labels = {'template': template, 'status': status}
        
        self.record_counter('scraper_extractions_count', records_count, labels)
        
        if self.enable_prometheus:
            self.scraper_extractions.labels(template=template, status=status).inc(records_count)
    
    def record_webhook_event(self, event_type: str, status: str):
        """Record webhook event metrics"""
        labels = {'event_type': event_type, 'status': status}
        
        self.record_counter('webhook_events_count', labels=labels)
        
        if self.enable_prometheus:
            self.webhook_events.labels(event_type=event_type, status=status).inc()
    
    def update_proxy_pool_size(self, active_count: int, total_count: int):
        """Update proxy pool metrics"""
        self.record_gauge('proxy_pool_active', active_count)
        self.record_gauge('proxy_pool_total', total_count)
        
        if self.enable_prometheus:
            self.proxy_usage.labels(status='active').set(active_count)
            self.proxy_usage.labels(status='total').set(total_count)
    
    def update_active_users(self, count: int):
        """Update active users count"""
        self.record_gauge('active_users', count)
    
    def record_error(self, error_type: str, component: str):
        """Record error metrics"""
        labels = {'error_type': error_type, 'component': component}
        self.record_counter('error_count', labels=labels)
    
    # Export and query methods
    
    def get_metric(self, name: str) -> Optional[MetricSeries]:
        """Get a specific metric series"""
        return self.metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, MetricSeries]:
        """Get all metric series"""
        with self.lock:
            return dict(self.metrics)
    
    def get_metric_summary(self, name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        metric = self.get_metric(name)
        if not metric:
            return {}
        
        # Filter points within time window
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent_points = [p for p in metric.points if p.timestamp > cutoff]
        
        if not recent_points:
            return {"name": name, "points": 0}
        
        values = [p.value for p in recent_points]
        
        summary = {
            "name": name,
            "type": metric.metric_type,
            "points": len(recent_points),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "window_minutes": window_minutes
        }
        
        # Add additional stats for histograms
        if metric.metric_type == 'histogram':
            sorted_values = sorted(values)
            count = len(sorted_values)
            
            summary.update({
                "p50": sorted_values[int(count * 0.5)],
                "p95": sorted_values[int(count * 0.95)],
                "p99": sorted_values[int(count * 0.99)]
            })
        
        return summary
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        if not self.enable_prometheus:
            return "# Prometheus not available\n"
        
        return generate_latest(self.registry).decode('utf-8')
    
    def export_json(self, window_minutes: int = 60) -> Dict[str, Any]:
        """Export metrics as JSON"""
        export_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "window_minutes": window_minutes,
            "metrics": {}
        }
        
        for name in self.metrics:
            export_data["metrics"][name] = self.get_metric_summary(name, window_minutes)
        
        return export_data
    
    def clear_old_metrics(self, max_age_hours: int = 24):
        """Clear old metric points"""
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        with self.lock:
            for metric in self.metrics.values():
                # Filter out old points
                metric.points = deque(
                    [p for p in metric.points if p.timestamp > cutoff],
                    maxlen=metric.points.maxlen
                )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status based on metrics"""
        health = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # CPU check
        cpu_metric = self.get_metric('system_cpu_percent')
        if cpu_metric and cpu_metric.points:
            cpu_value = cpu_metric.points[-1].value
            health["checks"]["cpu"] = {
                "status": "healthy" if cpu_value < 80 else "warning" if cpu_value < 95 else "unhealthy",
                "value": cpu_value,
                "unit": "percent"
            }
            if cpu_value >= 80:
                health["status"] = "warning" if cpu_value < 95 else "unhealthy"
        
        # Memory check
        memory_metric = self.get_metric('system_memory_bytes')
        if memory_metric and memory_metric.points:
            memory_bytes = memory_metric.points[-1].value
            memory_gb = memory_bytes / (1024**3)
            
            # Simple threshold - adjust based on your system
            memory_threshold_gb = 8  # 8GB threshold
            memory_status = "healthy" if memory_gb < memory_threshold_gb else "warning"
            
            health["checks"]["memory"] = {
                "status": memory_status,
                "value": memory_gb,
                "unit": "GB"
            }
            if memory_status != "healthy":
                health["status"] = memory_status
        
        # Error rate check
        error_metric = self.get_metric('error_count')
        if error_metric and error_metric.points:
            recent_errors = len([p for p in error_metric.points 
                               if p.timestamp > datetime.utcnow() - timedelta(minutes=10)])
            
            error_status = "healthy" if recent_errors < 10 else "warning" if recent_errors < 50 else "unhealthy"
            health["checks"]["errors"] = {
                "status": error_status,
                "value": recent_errors,
                "unit": "count_per_10min"
            }
            if error_status != "healthy":
                health["status"] = error_status
        
        return health


# Global metrics collector instance
metrics_collector = MetricsCollector()

# Context managers for timing operations

class TimingContext:
    """Context manager for timing operations"""
    
    def __init__(self, metric_name: str, labels: Optional[Dict[str, str]] = None):
        self.metric_name = metric_name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = (time.time() - self.start_time) * 1000  # Convert to ms
            metrics_collector.record_histogram(self.metric_name, duration, self.labels)

def time_operation(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Create a timing context manager"""
    return TimingContext(metric_name, labels)

# Convenience functions
def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return metrics_collector
