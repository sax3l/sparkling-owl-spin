"""
Real-time Performance Monitoring System

Världens mest avancerade monitoring-system för webscraping som övervakar
prestanda, upptäcker anomalier, optimerar resurser och ger prediktiv analys.
"""

import asyncio
import json
import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Union, Callable, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import websockets
import sqlite3

# Internal imports
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MetricType(Enum):
    """Types of metrics to monitor"""
    COUNTER = "counter"          # Incremental values
    GAUGE = "gauge"              # Point-in-time values
    HISTOGRAM = "histogram"      # Distribution of values
    SUMMARY = "summary"          # Statistical summaries
    RATE = "rate"               # Rate of change


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealthStatus(Enum):
    """System health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class MetricValue:
    """Single metric value with metadata"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric definition and storage"""
    name: str
    type: MetricType
    description: str
    unit: str = ""
    values: deque = field(default_factory=lambda: deque(maxlen=10000))
    labels: Dict[str, str] = field(default_factory=dict)
    
    def add_value(self, value: float, labels: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Add a new metric value"""
        self.values.append(MetricValue(
            timestamp=datetime.now(),
            value=value,
            labels=labels or {},
            metadata=metadata or {}
        ))


@dataclass
class Alert:
    """Alert definition"""
    alert_id: str
    name: str
    description: str
    condition: str  # Expression to evaluate
    severity: AlertSeverity
    threshold: float
    duration: timedelta  # How long condition must persist
    labels: Dict[str, str] = field(default_factory=dict)
    active: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class AlertEvent:
    """Alert event instance"""
    event_id: str
    alert: Alert
    triggered_at: datetime
    resolved_at: Optional[datetime]
    duration: Optional[timedelta]
    trigger_value: float
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """System performance snapshot"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_io_bytes: Tuple[int, int]  # sent, received
    active_threads: int
    active_connections: int
    request_rate: float
    error_rate: float
    response_time_avg: float
    queue_sizes: Dict[str, int] = field(default_factory=dict)


class MetricsCollector:
    """Collect system and application metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.collection_interval = 1.0  # seconds
        self.running = False
        self.collection_thread = None
        
        # System metrics
        self._init_system_metrics()
        
        # Network I/O tracking
        self._last_network_io = psutil.net_io_counters()
        self._last_check_time = time.time()
    
    def _init_system_metrics(self):
        """Initialize system metrics"""
        self.register_metric("system_cpu_percent", MetricType.GAUGE, "CPU usage percentage", "%")
        self.register_metric("system_memory_percent", MetricType.GAUGE, "Memory usage percentage", "%")
        self.register_metric("system_memory_used", MetricType.GAUGE, "Memory used in MB", "MB")
        self.register_metric("system_disk_percent", MetricType.GAUGE, "Disk usage percentage", "%")
        self.register_metric("system_network_sent", MetricType.COUNTER, "Network bytes sent", "bytes")
        self.register_metric("system_network_received", MetricType.COUNTER, "Network bytes received", "bytes")
        self.register_metric("system_threads", MetricType.GAUGE, "Active threads count", "count")
        
        # Application metrics
        self.register_metric("requests_total", MetricType.COUNTER, "Total HTTP requests", "count")
        self.register_metric("requests_successful", MetricType.COUNTER, "Successful HTTP requests", "count")
        self.register_metric("requests_failed", MetricType.COUNTER, "Failed HTTP requests", "count")
        self.register_metric("response_time", MetricType.HISTOGRAM, "HTTP response time", "ms")
        self.register_metric("active_connections", MetricType.GAUGE, "Active HTTP connections", "count")
        self.register_metric("queue_size", MetricType.GAUGE, "Queue size", "count")
        self.register_metric("processing_rate", MetricType.RATE, "Items processed per second", "items/s")
        
        # Scraping metrics
        self.register_metric("pages_scraped", MetricType.COUNTER, "Pages scraped successfully", "count")
        self.register_metric("scraping_errors", MetricType.COUNTER, "Scraping errors", "count")
        self.register_metric("data_extracted", MetricType.COUNTER, "Data items extracted", "count")
        self.register_metric("captcha_solved", MetricType.COUNTER, "CAPTCHAs solved", "count")
        self.register_metric("stealth_detection", MetricType.COUNTER, "Stealth detections avoided", "count")
    
    def register_metric(self, name: str, metric_type: MetricType, description: str, unit: str = ""):
        """Register a new metric"""
        self.metrics[name] = Metric(
            name=name,
            type=metric_type,
            description=description,
            unit=unit
        )
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None, metadata: Dict[str, Any] = None):
        """Record a metric value"""
        if name in self.metrics:
            self.metrics[name].add_value(value, labels, metadata)
        else:
            logger.warning(f"Metric not registered: {name}")
    
    def increment_counter(self, name: str, amount: float = 1.0, labels: Dict[str, str] = None):
        """Increment a counter metric"""
        if name in self.metrics and self.metrics[name].type == MetricType.COUNTER:
            current_value = self.get_latest_value(name) or 0
            self.record_metric(name, current_value + amount, labels)
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set a gauge metric value"""
        if name in self.metrics and self.metrics[name].type == MetricType.GAUGE:
            self.record_metric(name, value, labels)
    
    def get_latest_value(self, name: str) -> Optional[float]:
        """Get latest value for a metric"""
        if name in self.metrics and self.metrics[name].values:
            return self.metrics[name].values[-1].value
        return None
    
    def get_metric_history(self, name: str, duration: timedelta = None) -> List[MetricValue]:
        """Get metric history within duration"""
        if name not in self.metrics:
            return []
        
        values = list(self.metrics[name].values)
        
        if duration:
            cutoff_time = datetime.now() - duration
            values = [v for v in values if v.timestamp >= cutoff_time]
        
        return values
    
    def start_collection(self):
        """Start automatic metrics collection"""
        if self.running:
            return
        
        self.running = True
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop automatic metrics collection"""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                self._collect_system_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=None)
        self.set_gauge("system_cpu_percent", cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.set_gauge("system_memory_percent", memory.percent)
        self.set_gauge("system_memory_used", memory.used / 1024 / 1024)  # MB
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.set_gauge("system_disk_percent", disk_percent)
        
        # Network I/O
        current_time = time.time()
        current_io = psutil.net_io_counters()
        
        if hasattr(self, '_last_network_io'):
            time_delta = current_time - self._last_check_time
            if time_delta > 0:
                sent_rate = (current_io.bytes_sent - self._last_network_io.bytes_sent) / time_delta
                recv_rate = (current_io.bytes_recv - self._last_network_io.bytes_recv) / time_delta
                
                self.record_metric("system_network_sent", sent_rate)
                self.record_metric("system_network_received", recv_rate)
        
        self._last_network_io = current_io
        self._last_check_time = current_time
        
        # Thread count
        thread_count = threading.active_count()
        self.set_gauge("system_threads", thread_count)


class AnomalyDetector:
    """Detect anomalies in metrics using statistical methods"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.anomaly_threshold = 2.0  # Standard deviations
    
    def detect_anomalies(self, values: List[float]) -> List[bool]:
        """Detect anomalies using statistical methods"""
        if len(values) < 10:
            return [False] * len(values)
        
        # Calculate rolling statistics
        anomalies = []
        
        for i in range(len(values)):
            start_idx = max(0, i - self.window_size)
            window = values[start_idx:i+1]
            
            if len(window) < 5:
                anomalies.append(False)
                continue
            
            mean = statistics.mean(window)
            stdev = statistics.stdev(window) if len(window) > 1 else 0
            
            if stdev == 0:
                anomalies.append(False)
                continue
            
            z_score = abs((values[i] - mean) / stdev)
            is_anomaly = z_score > self.anomaly_threshold
            anomalies.append(is_anomaly)
        
        return anomalies
    
    def detect_trend_anomalies(self, values: List[float]) -> Dict[str, Any]:
        """Detect trend-based anomalies"""
        if len(values) < 20:
            return {"trend": "insufficient_data", "anomalies": []}
        
        # Calculate trend using linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        # Simple linear regression
        n = len(values)
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        
        slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
        intercept = y_mean - slope * x_mean
        
        # Calculate residuals
        predicted = slope * x + intercept
        residuals = y - predicted
        residual_std = np.std(residuals)
        
        # Identify trend anomalies
        trend_anomalies = []
        for i, residual in enumerate(residuals):
            if abs(residual) > 2 * residual_std:
                trend_anomalies.append(i)
        
        return {
            "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            "slope": slope,
            "r_squared": np.corrcoef(x, y)[0, 1] ** 2 if len(x) > 1 else 0,
            "anomalies": trend_anomalies,
            "anomaly_count": len(trend_anomalies)
        }


class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self):
        self.alerts = {}
        self.alert_events = []
        self.callbacks = defaultdict(list)
        self.running = False
        self.evaluation_thread = None
        self.evaluation_interval = 5.0  # seconds
    
    def register_alert(self, alert: Alert):
        """Register a new alert"""
        self.alerts[alert.alert_id] = alert
        logger.info(f"Alert registered: {alert.name}")
    
    def add_callback(self, severity: AlertSeverity, callback: Callable[[AlertEvent], None]):
        """Add callback for alert events"""
        self.callbacks[severity].append(callback)
    
    def start_monitoring(self, metrics_collector: MetricsCollector):
        """Start alert monitoring"""
        if self.running:
            return
        
        self.running = True
        self.metrics_collector = metrics_collector
        self.evaluation_thread = threading.Thread(
            target=self._evaluation_loop, 
            daemon=True
        )
        self.evaluation_thread.start()
        logger.info("Alert monitoring started")
    
    def stop_monitoring(self):
        """Stop alert monitoring"""
        self.running = False
        if self.evaluation_thread:
            self.evaluation_thread.join(timeout=5)
        logger.info("Alert monitoring stopped")
    
    def _evaluation_loop(self):
        """Main alert evaluation loop"""
        while self.running:
            try:
                self._evaluate_alerts()
                time.sleep(self.evaluation_interval)
            except Exception as e:
                logger.error(f"Error evaluating alerts: {e}")
                time.sleep(self.evaluation_interval)
    
    def _evaluate_alerts(self):
        """Evaluate all active alerts"""
        for alert in self.alerts.values():
            if not alert.active:
                continue
            
            try:
                if self._evaluate_alert_condition(alert):
                    self._trigger_alert(alert)
            except Exception as e:
                logger.error(f"Error evaluating alert {alert.name}: {e}")
    
    def _evaluate_alert_condition(self, alert: Alert) -> bool:
        """Evaluate alert condition"""
        # Simple condition evaluation (can be extended with more complex expressions)
        condition = alert.condition
        
        # Extract metric name and operator from condition
        # Format: "metric_name operator threshold" e.g. "system_cpu_percent > 80"
        parts = condition.split()
        if len(parts) != 3:
            return False
        
        metric_name, operator, threshold_str = parts
        
        try:
            threshold = float(threshold_str)
        except ValueError:
            return False
        
        # Get current metric value
        current_value = self.metrics_collector.get_latest_value(metric_name)
        if current_value is None:
            return False
        
        # Evaluate condition
        if operator == '>':
            return current_value > threshold
        elif operator == '<':
            return current_value < threshold
        elif operator == '>=':
            return current_value >= threshold
        elif operator == '<=':
            return current_value <= threshold
        elif operator == '==':
            return current_value == threshold
        elif operator == '!=':
            return current_value != threshold
        
        return False
    
    def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        now = datetime.now()
        
        # Check if alert was recently triggered (debouncing)
        if alert.last_triggered and (now - alert.last_triggered) < alert.duration:
            return
        
        # Create alert event
        event = AlertEvent(
            event_id=f"alert_{int(time.time() * 1000)}",
            alert=alert,
            triggered_at=now,
            resolved_at=None,
            duration=None,
            trigger_value=self.metrics_collector.get_latest_value(
                alert.condition.split()[0]
            ) or 0,
            message=f"Alert '{alert.name}' triggered: {alert.description}"
        )
        
        self.alert_events.append(event)
        alert.last_triggered = now
        alert.trigger_count += 1
        
        # Execute callbacks
        for callback in self.callbacks[alert.severity]:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error executing alert callback: {e}")
        
        logger.warning(f"Alert triggered: {alert.name} ({alert.severity.value})")


class PerformanceAnalyzer:
    """Analyze system performance and provide insights"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.anomaly_detector = AnomalyDetector()
    
    def get_performance_snapshot(self) -> PerformanceSnapshot:
        """Get current performance snapshot"""
        return PerformanceSnapshot(
            timestamp=datetime.now(),
            cpu_percent=self.metrics_collector.get_latest_value("system_cpu_percent") or 0,
            memory_percent=self.metrics_collector.get_latest_value("system_memory_percent") or 0,
            memory_used_mb=self.metrics_collector.get_latest_value("system_memory_used") or 0,
            disk_usage_percent=self.metrics_collector.get_latest_value("system_disk_percent") or 0,
            network_io_bytes=(
                self.metrics_collector.get_latest_value("system_network_sent") or 0,
                self.metrics_collector.get_latest_value("system_network_received") or 0
            ),
            active_threads=int(self.metrics_collector.get_latest_value("system_threads") or 0),
            active_connections=int(self.metrics_collector.get_latest_value("active_connections") or 0),
            request_rate=self.metrics_collector.get_latest_value("processing_rate") or 0,
            error_rate=self._calculate_error_rate(),
            response_time_avg=self._calculate_avg_response_time()
        )
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        total_requests = self.metrics_collector.get_latest_value("requests_total") or 0
        failed_requests = self.metrics_collector.get_latest_value("requests_failed") or 0
        
        if total_requests == 0:
            return 0.0
        
        return (failed_requests / total_requests) * 100
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        history = self.metrics_collector.get_metric_history(
            "response_time", 
            timedelta(minutes=5)
        )
        
        if not history:
            return 0.0
        
        return statistics.mean([v.value for v in history])
    
    def analyze_performance_trends(self, duration: timedelta = timedelta(hours=1)) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        key_metrics = [
            "system_cpu_percent",
            "system_memory_percent", 
            "response_time",
            "requests_total",
            "processing_rate"
        ]
        
        analysis = {}
        
        for metric_name in key_metrics:
            history = self.metrics_collector.get_metric_history(metric_name, duration)
            if not history:
                continue
            
            values = [v.value for v in history]
            
            # Basic statistics
            analysis[metric_name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
                "median": statistics.median(values),
                "stdev": statistics.stdev(values) if len(values) > 1 else 0
            }
            
            # Anomaly detection
            anomalies = self.anomaly_detector.detect_anomalies(values)
            trend_analysis = self.anomaly_detector.detect_trend_anomalies(values)
            
            analysis[metric_name]["anomalies"] = {
                "count": sum(anomalies),
                "percentage": (sum(anomalies) / len(anomalies)) * 100 if anomalies else 0,
                "trend": trend_analysis
            }
        
        return analysis
    
    def get_health_status(self) -> Tuple[HealthStatus, List[str]]:
        """Determine overall system health"""
        snapshot = self.get_performance_snapshot()
        issues = []
        
        # Check CPU usage
        if snapshot.cpu_percent > 90:
            issues.append(f"High CPU usage: {snapshot.cpu_percent:.1f}%")
        elif snapshot.cpu_percent > 80:
            issues.append(f"Elevated CPU usage: {snapshot.cpu_percent:.1f}%")
        
        # Check memory usage
        if snapshot.memory_percent > 95:
            issues.append(f"Critical memory usage: {snapshot.memory_percent:.1f}%")
        elif snapshot.memory_percent > 85:
            issues.append(f"High memory usage: {snapshot.memory_percent:.1f}%")
        
        # Check error rate
        if snapshot.error_rate > 50:
            issues.append(f"Critical error rate: {snapshot.error_rate:.1f}%")
        elif snapshot.error_rate > 10:
            issues.append(f"High error rate: {snapshot.error_rate:.1f}%")
        
        # Check response time
        if snapshot.response_time_avg > 10000:  # 10 seconds
            issues.append(f"Very slow response times: {snapshot.response_time_avg:.0f}ms")
        elif snapshot.response_time_avg > 5000:  # 5 seconds
            issues.append(f"Slow response times: {snapshot.response_time_avg:.0f}ms")
        
        # Determine health status
        critical_issues = [i for i in issues if "Critical" in i or "Very" in i]
        high_issues = [i for i in issues if "High" in i and "Critical" not in i]
        
        if critical_issues:
            return HealthStatus.CRITICAL, issues
        elif len(high_issues) >= 2:
            return HealthStatus.UNHEALTHY, issues
        elif high_issues or len(issues) >= 3:
            return HealthStatus.DEGRADED, issues
        else:
            return HealthStatus.HEALTHY, issues


class RealTimeMonitoringSystem:
    """
    Main real-time monitoring system that coordinates all monitoring components
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.performance_analyzer = PerformanceAnalyzer(self.metrics_collector)
        
        # WebSocket server for real-time updates
        self.websocket_server = None
        self.websocket_port = 8765
        self.connected_clients = set()
        
        # Data persistence
        self.db_path = "monitoring.db"
        self._init_database()
        
        # Setup default alerts
        self._setup_default_alerts()
        
        logger.info("Real-time Monitoring System initialized")
    
    def _init_database(self):
        """Initialize monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                name TEXT,
                value REAL,
                labels TEXT,
                metadata TEXT
            )
        ''')
        
        # Alert events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE,
                alert_name TEXT,
                severity TEXT,
                triggered_at DATETIME,
                resolved_at DATETIME,
                trigger_value REAL,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _setup_default_alerts(self):
        """Setup default system alerts"""
        
        # High CPU usage
        self.alert_manager.register_alert(Alert(
            alert_id="high_cpu",
            name="High CPU Usage",
            description="CPU usage above 80% for extended period",
            condition="system_cpu_percent > 80",
            severity=AlertSeverity.WARNING,
            threshold=80.0,
            duration=timedelta(minutes=5)
        ))
        
        # Critical CPU usage
        self.alert_manager.register_alert(Alert(
            alert_id="critical_cpu",
            name="Critical CPU Usage",
            description="CPU usage above 95%",
            condition="system_cpu_percent > 95",
            severity=AlertSeverity.CRITICAL,
            threshold=95.0,
            duration=timedelta(minutes=1)
        ))
        
        # High memory usage
        self.alert_manager.register_alert(Alert(
            alert_id="high_memory",
            name="High Memory Usage",
            description="Memory usage above 85%",
            condition="system_memory_percent > 85",
            severity=AlertSeverity.WARNING,
            threshold=85.0,
            duration=timedelta(minutes=5)
        ))
        
        # High error rate
        self.alert_manager.register_alert(Alert(
            alert_id="high_error_rate",
            name="High Error Rate",
            description="Error rate above 10%",
            condition="requests_failed > 10",
            severity=AlertSeverity.ERROR,
            threshold=10.0,
            duration=timedelta(minutes=2)
        ))
        
        # Slow response times
        self.alert_manager.register_alert(Alert(
            alert_id="slow_response",
            name="Slow Response Times",
            description="Average response time above 5 seconds",
            condition="response_time > 5000",
            severity=AlertSeverity.WARNING,
            threshold=5000.0,
            duration=timedelta(minutes=3)
        ))
    
    async def start(self):
        """Start the monitoring system"""
        # Start metrics collection
        self.metrics_collector.start_collection()
        
        # Start alert monitoring
        self.alert_manager.start_monitoring(self.metrics_collector)
        
        # Setup alert callbacks
        self.alert_manager.add_callback(AlertSeverity.CRITICAL, self._handle_critical_alert)
        self.alert_manager.add_callback(AlertSeverity.ERROR, self._handle_error_alert)
        self.alert_manager.add_callback(AlertSeverity.WARNING, self._handle_warning_alert)
        
        # Start WebSocket server
        await self._start_websocket_server()
        
        logger.info("Real-time Monitoring System started")
    
    async def stop(self):
        """Stop the monitoring system"""
        self.metrics_collector.stop_collection()
        self.alert_manager.stop_monitoring()
        
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        logger.info("Real-time Monitoring System stopped")
    
    async def _start_websocket_server(self):
        """Start WebSocket server for real-time updates"""
        try:
            self.websocket_server = await websockets.serve(
                self._handle_websocket_connection,
                "localhost",
                self.websocket_port
            )
            logger.info(f"WebSocket server started on port {self.websocket_port}")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
    
    async def _handle_websocket_connection(self, websocket, path):
        """Handle WebSocket client connections"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            # Send initial data
            await self._send_initial_data(websocket)
            
            # Keep connection alive and handle messages
            async for message in websocket:
                await self._handle_websocket_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def _send_initial_data(self, websocket):
        """Send initial monitoring data to client"""
        snapshot = self.performance_analyzer.get_performance_snapshot()
        health_status, issues = self.performance_analyzer.get_health_status()
        
        initial_data = {
            "type": "initial_data",
            "snapshot": asdict(snapshot),
            "health_status": health_status.value,
            "health_issues": issues,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(initial_data))
    
    async def _handle_websocket_message(self, websocket, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "get_metrics":
                await self._send_metrics_data(websocket, data.get("metric_names", []))
            elif message_type == "get_alerts":
                await self._send_alerts_data(websocket)
            elif message_type == "get_performance_analysis":
                await self._send_performance_analysis(websocket)
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            await websocket.send(json.dumps({"error": str(e)}))
    
    async def _send_metrics_data(self, websocket, metric_names: List[str]):
        """Send metrics data to client"""
        metrics_data = {}
        
        for name in metric_names:
            history = self.metrics_collector.get_metric_history(
                name, 
                timedelta(minutes=30)
            )
            
            if history:
                metrics_data[name] = [
                    {
                        "timestamp": v.timestamp.isoformat(),
                        "value": v.value,
                        "labels": v.labels
                    }
                    for v in history
                ]
        
        response = {
            "type": "metrics_data",
            "data": metrics_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(response))
    
    async def _send_alerts_data(self, websocket):
        """Send alerts data to client"""
        active_alerts = [
            {
                "alert_id": alert.alert_id,
                "name": alert.name,
                "severity": alert.severity.value,
                "description": alert.description,
                "last_triggered": alert.last_triggered.isoformat() if alert.last_triggered else None,
                "trigger_count": alert.trigger_count
            }
            for alert in self.alert_manager.alerts.values()
            if alert.active
        ]
        
        recent_events = [
            {
                "event_id": event.event_id,
                "alert_name": event.alert.name,
                "severity": event.alert.severity.value,
                "triggered_at": event.triggered_at.isoformat(),
                "message": event.message,
                "trigger_value": event.trigger_value
            }
            for event in self.alert_manager.alert_events[-20:]  # Last 20 events
        ]
        
        response = {
            "type": "alerts_data",
            "active_alerts": active_alerts,
            "recent_events": recent_events,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(response))
    
    async def _send_performance_analysis(self, websocket):
        """Send performance analysis to client"""
        analysis = self.performance_analyzer.analyze_performance_trends(
            timedelta(hours=1)
        )
        
        health_status, issues = self.performance_analyzer.get_health_status()
        
        response = {
            "type": "performance_analysis",
            "analysis": analysis,
            "health_status": health_status.value,
            "health_issues": issues,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(response))
    
    def _handle_critical_alert(self, event: AlertEvent):
        """Handle critical alert events"""
        logger.critical(f"CRITICAL ALERT: {event.message}")
        # Could integrate with external alerting systems (email, Slack, PagerDuty, etc.)
        
        # Broadcast to WebSocket clients
        asyncio.create_task(self._broadcast_alert(event))
    
    def _handle_error_alert(self, event: AlertEvent):
        """Handle error alert events"""
        logger.error(f"ERROR ALERT: {event.message}")
        asyncio.create_task(self._broadcast_alert(event))
    
    def _handle_warning_alert(self, event: AlertEvent):
        """Handle warning alert events"""
        logger.warning(f"WARNING ALERT: {event.message}")
        asyncio.create_task(self._broadcast_alert(event))
    
    async def _broadcast_alert(self, event: AlertEvent):
        """Broadcast alert to all connected clients"""
        if not self.connected_clients:
            return
        
        alert_data = {
            "type": "alert_event",
            "event_id": event.event_id,
            "alert_name": event.alert.name,
            "severity": event.alert.severity.value,
            "message": event.message,
            "trigger_value": event.trigger_value,
            "triggered_at": event.triggered_at.isoformat()
        }
        
        message = json.dumps(alert_data)
        
        # Send to all connected clients
        disconnected_clients = set()
        for client in self.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected_clients
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        snapshot = self.performance_analyzer.get_performance_snapshot()
        health_status, issues = self.performance_analyzer.get_health_status()
        
        # Get recent metrics
        key_metrics = {}
        for metric_name in ["system_cpu_percent", "system_memory_percent", "response_time"]:
            latest_value = self.metrics_collector.get_latest_value(metric_name)
            if latest_value is not None:
                key_metrics[metric_name] = latest_value
        
        # Get active alerts
        active_alerts = len([a for a in self.alert_manager.alerts.values() 
                            if a.active and a.last_triggered])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_status": health_status.value,
            "health_issues": issues,
            "snapshot": asdict(snapshot),
            "key_metrics": key_metrics,
            "active_alerts": active_alerts,
            "total_metrics": len(self.metrics_collector.metrics),
            "connected_clients": len(self.connected_clients)
        }
    
    # Public API methods for external integration
    def record_request(self, url: str, response_time: float, status_code: int, success: bool):
        """Record HTTP request metrics"""
        self.metrics_collector.increment_counter("requests_total")
        
        if success:
            self.metrics_collector.increment_counter("requests_successful")
        else:
            self.metrics_collector.increment_counter("requests_failed")
        
        self.metrics_collector.record_metric(
            "response_time", 
            response_time,
            labels={"url": url, "status": str(status_code)}
        )
    
    def record_scraping_success(self, url: str, items_extracted: int):
        """Record successful scraping operation"""
        self.metrics_collector.increment_counter("pages_scraped")
        self.metrics_collector.increment_counter("data_extracted", items_extracted)
    
    def record_scraping_error(self, url: str, error_type: str):
        """Record scraping error"""
        self.metrics_collector.increment_counter(
            "scraping_errors",
            labels={"url": url, "error_type": error_type}
        )
    
    def record_captcha_solved(self, service: str, solve_time: float):
        """Record CAPTCHA solving"""
        self.metrics_collector.increment_counter(
            "captcha_solved",
            labels={"service": service}
        )
    
    def record_stealth_detection_avoided(self, detection_type: str):
        """Record stealth detection avoided"""
        self.metrics_collector.increment_counter(
            "stealth_detection",
            labels={"detection_type": detection_type}
        )


# Factory function
def create_monitoring_system() -> RealTimeMonitoringSystem:
    """Factory function to create monitoring system"""
    return RealTimeMonitoringSystem()


# Example usage
async def example_monitoring():
    """Example of monitoring system usage"""
    
    # Create monitoring system
    monitor = create_monitoring_system()
    
    try:
        # Start monitoring
        await monitor.start()
        
        # Simulate some activity
        for i in range(10):
            # Record some sample metrics
            monitor.record_request(
                f"https://example.com/page{i}",
                response_time=500 + i * 100,
                status_code=200 if i < 8 else 500,
                success=i < 8
            )
            
            if i < 8:
                monitor.record_scraping_success(
                    f"https://example.com/page{i}",
                    items_extracted=10 + i
                )
            else:
                monitor.record_scraping_error(
                    f"https://example.com/page{i}",
                    error_type="timeout"
                )
            
            await asyncio.sleep(1)
        
        # Get system status
        status = monitor.get_system_status()
        print("\n📊 System Status:")
        print(f"Health: {status['health_status']}")
        print(f"CPU: {status['snapshot']['cpu_percent']:.1f}%")
        print(f"Memory: {status['snapshot']['memory_percent']:.1f}%")
        print(f"Active Alerts: {status['active_alerts']}")
        print(f"Connected Clients: {status['connected_clients']}")
        
        # Keep monitoring for a bit
        print("\n🔄 Monitoring for 30 seconds...")
        await asyncio.sleep(30)
        
    finally:
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(example_monitoring())
