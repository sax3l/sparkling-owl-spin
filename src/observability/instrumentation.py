import os
import time
import json
import socket
import contextvars
from typing import Optional, Callable, Any, Dict
from urllib.parse import urlparse

import structlog
from prometheus_client import (
    Counter, Histogram, Gauge, CollectorRegistry,
    start_http_server
)

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    # If OTLP exporter is not available, use a dummy exporter
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter as OTLPSpanExporter
    OTLP_AVAILABLE = False

# Retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# -----------------------------
# Kontext (run_id, job_id, domän, template)
# -----------------------------
cv_run_id = contextvars.ContextVar("run_id", default=None)
cv_job_id = contextvars.ContextVar("job_id", default=None)
cv_domain = contextvars.ContextVar("domain", default=None)
cv_template = contextvars.ContextVar("template", default=None)
cv_mode = contextvars.ContextVar("mode", default=None)  # http | browser
cv_request_id = contextvars.ContextVar("request_id", default=None) # New: Request ID

def set_context(run_id: Optional[str]=None, job_id: Optional[str]=None,
                domain: Optional[str]=None, template: Optional[str]=None,
                mode: Optional[str]=None, request_id: Optional[str]=None):
    if run_id is not None: cv_run_id.set(run_id)
    if job_id is not None: cv_job_id.set(job_id)
    if domain is not None: cv_domain.set(domain)
    if template is not None: cv_template.set(template)
    if mode is not None: cv_mode.set(mode)
    if request_id is not None: cv_request_id.set(request_id)

def get_context() -> Dict[str, Optional[str]]:
    return {
        "run_id": cv_run_id.get(),
        "job_id": cv_job_id.get(),
        "domain": cv_domain.get(),
        "template": cv_template.get(),
        "mode": cv_mode.get(),
        "request_id": cv_request_id.get(), # Include request_id
    }

# -----------------------------
# Prometheus-metrics (låga kardinaliteter!)
# -----------------------------
REGISTRY = CollectorRegistry(auto_describe=True)

REQUESTS_TOTAL = Counter(
    "requests_total",
    "Antal HTTP/Browser-förfrågningar",
    labelnames=("service", "mode", "domain", "code"),
    registry=REGISTRY,
)
RETRIES_TOTAL = Counter(
    "retries_total",
    "Antal retrier per domän och läge",
    labelnames=("service", "mode", "domain"),
    registry=REGISTRY,
)
REQUEST_DURATION = Histogram(
    "request_duration_seconds",
    "Duration per förfrågan",
    labelnames=("service", "mode", "domain"),
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
    registry=REGISTRY,
)
EXTRACTIONS_OK_TOTAL = Counter(
    "extractions_ok_total",
    "Lyckade extraktioner (fält satta utan valideringsfel)",
    labelnames=("service", "domain", "template"),
    registry=REGISTRY,
)
DQ_VALIDITY_RATIO = Gauge(
    "dq_validity_ratio",
    "Andel fält som passerar typ/regex per mall",
    labelnames=("service", "domain", "template"),
    registry=REGISTRY,
)
QUEUE_DEPTH = Gauge(
    "queue_depth",
    "Ködjup (crawl/ scrape)",
    labelnames=("service", "queue"),
    registry=REGISTRY,
)

# -----------------------------
# JSON-loggning (structlog) med trace-korrelation
# -----------------------------
def _get_trace_ids():
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.is_valid:
        trace_id = format(ctx.trace_id, "032x")
        span_id = format(ctx.span_id, "016x")
        return trace_id, span_id
    return None, None

def add_otlp_ids(_, __, event_dict):
    trace_id, span_id = _get_trace_ids()
    if trace_id:
        event_dict["trace_id"] = trace_id
        event_dict["span_id"] = span_id
    return event_dict

def add_context(_, __, event_dict):
    ctx = get_context()
    for k, v in ctx.items():
        if v: event_dict[k] = v
    return event_dict

def redact_sensitive(_, __, event_dict):
    # maska potentiellt känsliga fält om de råkar loggas
    for key in ("personal_number", "session_cookie", "password", "api_key"):
        if key in event_dict:
            val = event_dict[key]
            event_dict[key] = f"***{str(val)[-4:]}" if val else "***"
    return event_dict

def configure_logging(service_name: str, env: str = None):
    env = env or os.getenv("ENV", "production")
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso", key="ts"),
            add_otlp_ids,
            add_context,
            redact_sensitive,
            structlog.processors.add_log_level,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(sort_keys=False)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            # INFO default; sätt DEBUG via ENV om du vill
            20
        ),
        context_class=dict,
        cache_logger_on_first_use=True,
    )
    logger = structlog.get_logger().bind(service=service_name, env=env, host=socket.gethostname())
    return logger

# -----------------------------
# OpenTelemetry-tracing init
# -----------------------------
def init_tracer(service_name: str, version: str = "1.0.0", env: str = None):
    env = env or os.getenv("ENV", "production")
    resource = Resource.create({
        "service.name": service_name,
        "service.version": version,
        "deployment.environment": env,
    })
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"), insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)

# -----------------------------
# Exponera /metrics (startar egen HTTP-server i processen)
# -----------------------------
def start_metrics_server(port: int):
    # Prometheus Python startar en separat tråd som lyssnar på porten
    start_http_server(port, registry=REGISTRY)

# -----------------------------
# Hjälp: mät & logga en "förfrågan"
# -----------------------------
def _domain_from_url(url: str) -> str:
    try:
        return urlparse(url).netloc or "unknown"
    except Exception:
        return "unknown"

def measure_request(service: str, mode: str, domain: Optional[str], fn: Callable[[], Any]):
    """
    Mät varaktighet + öka counters. 'fn' ska kasta undantag vid fel.
    Returnerar fn:s resultat.
    """
    domain = domain or cv_domain.get() or "unknown"
    cv_mode.set(mode)
    start = time.perf_counter()
    status_code = "200"
    err = None
    try:
        res = fn()
        return res
    except Exception as e:
        err = e
        # klassificera simpelt: (du kan utöka efter egna exceptiontyper)
        status_code = getattr(e, "status_code", None) or getattr(e, "code", None) or "500"
        raise
    finally:
        dur = time.perf_counter() - start
        REQUEST_DURATION.labels(service=service, mode=mode, domain=domain).observe(dur)
        REQUESTS_TOTAL.labels(service=service, mode=mode, domain=domain, code=str(status_code)).inc()

# -----------------------------
# Hjälp: retries (exponentiell backoff)
# -----------------------------
class TransientHTTPError(Exception):
    def __init__(self, status_code=502, msg="transient"):
        super().__init__(msg)
        self.status_code = status_code

def retryable(service: str, mode: str, domain: Optional[str]):
    def decorator(fn):
        @retry(
            reraise=True,
            retry=retry_if_exception_type(TransientHTTPError),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=10),
            stop=stop_after_attempt(5)
        )
        def wrapper(*args, **kwargs):
            try:
                return measure_request(service, mode, domain, lambda: fn(*args, **kwargs))
            except TransientHTTPError:
                RETRIES_TOTAL.labels(service=service, mode=mode, domain=domain or cv_domain.get() or "unknown").inc()
                raise
        return wrapper
    return decorator

# -----------------------------
# Hjälp: DQ
# -----------------------------
def report_extraction_success(service: str, domain: str, template: str, validity_ratio: float = None):
    EXTRACTIONS_OK_TOTAL.labels(service=service, domain=domain, template=template).inc()
    if validity_ratio is not None:
        DQ_VALIDITY_RATIO.labels(service=service, domain=domain, template=template).set(validity_ratio)

# -----------------------------
# Tracing-span helper
# -----------------------------
def traced_span(tracer, name: str, attributes: Optional[Dict[str, Any]] = None, kind: SpanKind = SpanKind.INTERNAL):
    class _SpanCtx:
        def __enter__(self):
            self._span = tracer.start_span(name, kind=kind)
            if attributes:
                for k, v in attributes.items():
                    try:
                        self._span.set_attribute(k, v)
                    except Exception:
                        pass
            self._ctx = trace.use_span(self._span, end_on_exit=True)
            self._ctx.__enter__()
            return self._span
        def __exit__(self, exc_type, exc, tb):
            self._ctx.__exit__(exc_type, exc, tb)
    return _SpanCtx()