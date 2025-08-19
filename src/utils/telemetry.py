from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

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