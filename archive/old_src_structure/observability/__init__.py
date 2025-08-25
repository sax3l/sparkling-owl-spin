"""
Observability Module
===================

Comprehensive observability and monitoring for the ECaDP platform.

This module provides:
- Metrics collection and export
- System instrumentation
- Performance monitoring
- Health checks
"""

from .metrics import (
    MetricsCollector,
    MetricPoint,
    MetricSeries,
    TimingContext,
    metrics_collector,
    time_operation,
    get_metrics_collector
)

try:
    from .instrumentation import (
        InstrumentedSession,
        instrument_function,
        create_instrumented_session
    )
    INSTRUMENTATION_AVAILABLE = True
except ImportError:
    INSTRUMENTATION_AVAILABLE = False

__all__ = [
    # Metrics
    "MetricsCollector",
    "MetricPoint", 
    "MetricSeries",
    "TimingContext",
    "metrics_collector",
    "time_operation",
    "get_metrics_collector",
]

# Add instrumentation if available
if INSTRUMENTATION_AVAILABLE:
    __all__.extend([
        "InstrumentedSession",
        "instrument_function",
        "create_instrumented_session"
    ])
