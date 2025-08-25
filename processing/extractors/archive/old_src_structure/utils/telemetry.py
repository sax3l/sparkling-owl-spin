from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from typing import Dict, Any, Optional
import time


class TelemetryCollector:
    """Telemetry collector for performance monitoring and metrics."""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
        self.metrics = {}
    
    def start_span(self, name: str, **kwargs) -> trace.Span:
        """Start a new trace span."""
        return self.tracer.start_span(name, **kwargs)
    
    def record_metric(self, name: str, value: Any, tags: Optional[Dict[str, str]] = None):
        """Record a metric value."""
        self.metrics[name] = {
            'value': value,
            'timestamp': time.time(),
            'tags': tags or {}
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        return self.metrics.copy()


def setup_telemetry(app):
    """Configures OpenTelemetry for the application."""
    resource = Resource(attributes={
        "service.name": "ECaDP"
    })

    # For demonstration, we'll export to the console.
    # In production, this would be an OTLPExporter.
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(span_processor)
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)