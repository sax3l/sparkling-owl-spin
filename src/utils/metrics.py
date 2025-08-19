from prometheus_client import Counter, Histogram

REQUESTS_TOTAL = Counter(
    'requests_total',
    'Total number of requests processed',
    ['mode', 'domain', 'status_code']
)

EXTRACTIONS_OK_TOTAL = Counter(
    'extractions_ok_total',
    'Total number of successful extractions',
    ['domain', 'template']
)

RETRIES_TOTAL = Counter(
    'retries_total',
    'Total number of retries attempted',
    ['domain', 'mode']
)

REQUEST_DURATION_SECONDS = Histogram(
    'request_duration_seconds',
    'Request latency',
    ['mode', 'domain']
)

DQ_SCORE = Histogram(
    'dq_score',
    'Data Quality score distribution',
    ['domain', 'template']
)