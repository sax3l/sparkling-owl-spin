"""
Real-time monitoring and analytics system
Provides comprehensive monitoring like Browse AI and Apify
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import asyncio
import json
import logging
from dataclasses import dataclass, field
from collections import deque, defaultdict
import time

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Alert:
    id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Metric:
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self, max_history: int = 10000):
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.current_values: Dict[str, float] = {}
        self.counters: Dict[str, float] = defaultdict(float)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    def record_metric(self, metric: Metric):
        """Record a single metric"""
        self.metrics_history[metric.name].append(metric)
        self.current_values[metric.name] = metric.value
        
        if metric.metric_type == MetricType.COUNTER:
            self.counters[metric.name] += metric.value
        elif metric.metric_type == MetricType.TIMER:
            self.timers[metric.name].append(metric.value)
            # Keep only last 1000 timer measurements
            if len(self.timers[metric.name]) > 1000:
                self.timers[metric.name] = self.timers[metric.name][-1000:]
    
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.COUNTER,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
    
    def set_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        metric = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
    
    def record_time(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timing metric"""
        metric = Metric(
            name=name,
            value=duration,
            metric_type=MetricType.TIMER,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self.record_metric(metric)
    
    def get_metric_summary(self, name: str, time_window: timedelta = None) -> Dict[str, Any]:
        """Get summary statistics for a metric"""
        if name not in self.metrics_history:
            return {}
        
        metrics = list(self.metrics_history[name])
        
        # Filter by time window if specified
        if time_window:
            cutoff_time = datetime.now() - time_window
            metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        if not metrics:
            return {}
        
        values = [m.value for m in metrics]
        
        summary = {
            'count': len(values),
            'current': values[-1] if values else None,
            'min': min(values) if values else None,
            'max': max(values) if values else None,
            'avg': sum(values) / len(values) if values else None,
            'sum': sum(values) if values else None,
            'latest_timestamp': metrics[-1].timestamp.isoformat()
        }
        
        # Calculate percentiles for timers
        if metrics[0].metric_type == MetricType.TIMER and values:
            sorted_values = sorted(values)
            n = len(sorted_values)
            summary.update({
                'p50': sorted_values[int(n * 0.5)],
                'p95': sorted_values[int(n * 0.95)],
                'p99': sorted_values[int(n * 0.99)]
            })
        
        return summary

class CrawlMonitor:
    """Monitor crawl jobs and system health"""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerts: List[Alert] = []
        self.job_stats: Dict[str, Dict] = {}
        self.system_stats: Dict[str, Any] = {}
        self.alert_rules: List[Dict] = []
        self.logger = logging.getLogger(__name__)
    
    async def start_job_monitoring(self, job_id: str):
        """Start monitoring a crawl job"""
        self.job_stats[job_id] = {
            'start_time': datetime.now(),
            'pages_crawled': 0,
            'pages_failed': 0,
            'data_extracted': 0,
            'avg_response_time': 0.0,
            'current_status': 'running',
            'proxy_rotations': 0,
            'errors': []
        }
        
        self.metrics.increment_counter('jobs_started')
        self.logger.info(f"Started monitoring job {job_id}")
    
    def update_job_progress(self, job_id: str, **updates):
        """Update job progress metrics"""
        if job_id not in self.job_stats:
            return
        
        stats = self.job_stats[job_id]
        
        for key, value in updates.items():
            if key in stats:
                if key in ['pages_crawled', 'pages_failed', 'data_extracted', 'proxy_rotations']:
                    stats[key] += value
                    self.metrics.increment_counter(f'job_{key}', value)
                else:
                    stats[key] = value
        
        # Calculate success rate
        total_pages = stats['pages_crawled'] + stats['pages_failed']
        if total_pages > 0:
            success_rate = stats['pages_crawled'] / total_pages
            self.metrics.set_gauge(f'job_success_rate_{job_id}', success_rate)
        
        # Update runtime
        runtime = (datetime.now() - stats['start_time']).total_seconds()
        self.metrics.set_gauge(f'job_runtime_{job_id}', runtime)
    
    def add_job_error(self, job_id: str, error: str):
        """Add error to job monitoring"""
        if job_id in self.job_stats:
            self.job_stats[job_id]['errors'].append({
                'timestamp': datetime.now(),
                'error': error
            })
            
            # Keep only last 100 errors
            if len(self.job_stats[job_id]['errors']) > 100:
                self.job_stats[job_id]['errors'] = self.job_stats[job_id]['errors'][-100:]
            
            self.metrics.increment_counter('job_errors')
            
            # Check if alert should be triggered
            self._check_error_threshold(job_id)
    
    def complete_job_monitoring(self, job_id: str, success: bool = True):
        """Complete job monitoring"""
        if job_id not in self.job_stats:
            return
        
        stats = self.job_stats[job_id]
        stats['end_time'] = datetime.now()
        stats['current_status'] = 'completed' if success else 'failed'
        
        runtime = (stats['end_time'] - stats['start_time']).total_seconds()
        self.metrics.record_time('job_duration', runtime)
        
        if success:
            self.metrics.increment_counter('jobs_completed')
        else:
            self.metrics.increment_counter('jobs_failed')
        
        # Generate completion report
        self._generate_job_report(job_id)
    
    async def monitor_system_health(self) -> Dict[str, Any]:
        """Monitor overall system health"""
        import psutil
        
        # CPU and memory usage
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        self.metrics.set_gauge('system_cpu_percent', cpu_percent)
        self.metrics.set_gauge('system_memory_percent', memory.percent)
        self.metrics.set_gauge('system_disk_percent', disk.percent)
        
        # Network statistics
        network = psutil.net_io_counters()
        self.metrics.set_gauge('network_bytes_sent', network.bytes_sent)
        self.metrics.set_gauge('network_bytes_recv', network.bytes_recv)
        
        # Active job count
        active_jobs = len([j for j in self.job_stats.values() if j['current_status'] == 'running'])
        self.metrics.set_gauge('active_jobs', active_jobs)
        
        health_status = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'disk_usage': disk.percent,
            'active_jobs': active_jobs,
            'total_jobs': len(self.job_stats),
            'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'warning'
        }
        
        self.system_stats = health_status
        return health_status
    
    def add_alert_rule(self, rule: Dict[str, Any]):
        """Add alerting rule"""
        self.alert_rules.append(rule)
    
    def check_alerts(self):
        """Check all alert rules"""
        for rule in self.alert_rules:
            self._evaluate_alert_rule(rule)
    
    def _evaluate_alert_rule(self, rule: Dict[str, Any]):
        """Evaluate single alert rule"""
        metric_name = rule.get('metric')
        condition = rule.get('condition')  # gt, lt, eq
        threshold = rule.get('threshold')
        level = AlertLevel(rule.get('level', 'warning'))
        
        if metric_name in self.metrics.current_values:
            current_value = self.metrics.current_values[metric_name]
            
            should_alert = False
            if condition == 'gt' and current_value > threshold:
                should_alert = True
            elif condition == 'lt' and current_value < threshold:
                should_alert = True
            elif condition == 'eq' and current_value == threshold:
                should_alert = True
            
            if should_alert:
                alert = Alert(
                    id=f"alert_{metric_name}_{int(time.time())}",
                    level=level,
                    title=f"{metric_name} threshold exceeded",
                    message=f"{metric_name} is {current_value}, threshold: {threshold}",
                    source="monitoring_system",
                    timestamp=datetime.now(),
                    metadata={'rule': rule, 'current_value': current_value}
                )
                self.alerts.append(alert)
                self.logger.warning(f"Alert triggered: {alert.title}")
    
    def _check_error_threshold(self, job_id: str):
        """Check if job error threshold is exceeded"""
        stats = self.job_stats[job_id]
        error_count = len(stats['errors'])
        
        if error_count >= 10:  # Configurable threshold
            alert = Alert(
                id=f"job_errors_{job_id}_{int(time.time())}",
                level=AlertLevel.ERROR,
                title=f"High error rate in job {job_id}",
                message=f"Job {job_id} has {error_count} errors",
                source=f"job_{job_id}",
                timestamp=datetime.now(),
                metadata={'job_id': job_id, 'error_count': error_count}
            )
            self.alerts.append(alert)
    
    def _generate_job_report(self, job_id: str):
        """Generate job completion report"""
        stats = self.job_stats[job_id]
        runtime = (stats['end_time'] - stats['start_time']).total_seconds()
        
        report = {
            'job_id': job_id,
            'status': stats['current_status'],
            'runtime_seconds': runtime,
            'pages_crawled': stats['pages_crawled'],
            'pages_failed': stats['pages_failed'],
            'data_extracted': stats['data_extracted'],
            'success_rate': stats['pages_crawled'] / (stats['pages_crawled'] + stats['pages_failed']) if (stats['pages_crawled'] + stats['pages_failed']) > 0 else 0,
            'error_count': len(stats['errors']),
            'proxy_rotations': stats['proxy_rotations'],
            'avg_pages_per_minute': (stats['pages_crawled'] / runtime) * 60 if runtime > 0 else 0
        }
        
        self.logger.info(f"Job {job_id} completed: {json.dumps(report, indent=2)}")
        return report
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        # Active jobs overview
        active_jobs = {
            job_id: {
                'status': stats['current_status'],
                'runtime': (datetime.now() - stats['start_time']).total_seconds(),
                'progress': {
                    'crawled': stats['pages_crawled'],
                    'failed': stats['pages_failed'],
                    'success_rate': stats['pages_crawled'] / (stats['pages_crawled'] + stats['pages_failed']) if (stats['pages_crawled'] + stats['pages_failed']) > 0 else 0
                }
            }
            for job_id, stats in self.job_stats.items()
            if stats['current_status'] == 'running'
        }
        
        # Recent alerts (last 24 hours)
        recent_alerts = [
            {
                'id': alert.id,
                'level': alert.level.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved
            }
            for alert in self.alerts
            if alert.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        # System metrics
        system_metrics = {
            'cpu_usage': self.metrics.current_values.get('system_cpu_percent', 0),
            'memory_usage': self.metrics.current_values.get('system_memory_percent', 0),
            'disk_usage': self.metrics.current_values.get('system_disk_percent', 0),
            'active_jobs_count': self.metrics.current_values.get('active_jobs', 0)
        }
        
        # Performance metrics (last hour)
        performance_metrics = {
            'jobs_started': self.metrics.get_metric_summary('jobs_started', timedelta(hours=1)),
            'jobs_completed': self.metrics.get_metric_summary('jobs_completed', timedelta(hours=1)),
            'pages_crawled': self.metrics.get_metric_summary('job_pages_crawled', timedelta(hours=1)),
            'avg_response_time': self.metrics.get_metric_summary('response_time', timedelta(hours=1))
        }
        
        return {
            'active_jobs': active_jobs,
            'recent_alerts': recent_alerts,
            'system_metrics': system_metrics,
            'performance_metrics': performance_metrics,
            'timestamp': datetime.now().isoformat()
        }

class RealTimeNotifier:
    """Real-time notification system"""
    
    def __init__(self):
        self.websocket_clients: List = []
        self.notification_channels = {
            'email': [],
            'slack': [],
            'webhook': []
        }
        self.logger = logging.getLogger(__name__)
    
    async def subscribe_websocket(self, websocket):
        """Subscribe websocket client for real-time updates"""
        self.websocket_clients.append(websocket)
        self.logger.info(f"WebSocket client subscribed, total: {len(self.websocket_clients)}")
    
    async def unsubscribe_websocket(self, websocket):
        """Unsubscribe websocket client"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
            self.logger.info(f"WebSocket client unsubscribed, total: {len(self.websocket_clients)}")
    
    async def broadcast_update(self, update_type: str, data: Dict[str, Any]):
        """Broadcast update to all WebSocket clients"""
        message = {
            'type': update_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Remove disconnected clients
        active_clients = []
        for client in self.websocket_clients:
            try:
                await client.send(json.dumps(message))
                active_clients.append(client)
            except Exception as e:
                self.logger.warning(f"Failed to send to WebSocket client: {e}")
        
        self.websocket_clients = active_clients
    
    async def send_alert_notification(self, alert: Alert):
        """Send alert through configured notification channels"""
        # WebSocket notification
        await self.broadcast_update('alert', {
            'id': alert.id,
            'level': alert.level.value,
            'title': alert.title,
            'message': alert.message,
            'source': alert.source,
            'timestamp': alert.timestamp.isoformat()
        })
        
        # Email notifications (implement based on config)
        if alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            await self._send_email_alert(alert)
        
        # Slack notifications
        await self._send_slack_alert(alert)
        
        # Webhook notifications
        await self._send_webhook_alert(alert)
    
    async def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        # Implement email sending logic
        self.logger.info(f"Would send email alert: {alert.title}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Send Slack alert"""
        # Implement Slack webhook logic
        self.logger.info(f"Would send Slack alert: {alert.title}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert"""
        # Implement webhook logic
        self.logger.info(f"Would send webhook alert: {alert.title}")
