import os
import asyncio
import httpx
import uvloop

from urllib.parse import urljoin, urlparse
from collections import deque

from src.observability.instrumentation import (
    init_tracer, configure_logging, start_metrics_server,
    set_context, traced_span, retryable, TransientHTTPError,
    QUEUE_DEPTH
)

SERVICE = "crawler"
DEFAULT_START_URL = "https://example.com/"
METRICS_PORT = int(os.getenv("METRICS_PORT", "9101"))

def same_host(u1: str, u2: str) -> bool:
    try:
        return urlparse(u1).netloc == urlparse(u2).netloc
    except Exception:
        return True

@retryable(service=SERVICE, mode="http", domain=None)
def fetch(client: httpx.Client, url: str, headers=None, proxy=None) -> str:
    # Enkel HTTP GET med klassificering av fel
    r = client.get(url, headers=headers, proxies=proxy, timeout=20)
    if r.status_code >= 500:
        raise TransientHTTPError(status_code=r.status_code, msg=f"server error {r.status_code}")
    if r.status_code in (403, 429):
        # policyfel → låt gå igenom utan retry här, men registreras i metrics
        e = Exception(f"policy/block {r.status_code}")
        setattr(e, "status_code", r.status_code)
        raise e
    r.raise_for_status()
    return r.text

def extract_links(base_url: str, html: str) -> list[str]:
    # Minimal länk-utvinning (byt till lxml/BS4 i skarp drift)
    import re
    links = re.findall(r'href="([^"]+)"', html)
    full = []
    for h in links:
        full.append(urljoin(base_url, h))
    # filtrera bort fragment/mailto mm.
    clean = [u for u in full if u.startswith("http")]
    return clean

def crawl(start_url: str, max_pages: int = 200, per_host_limit: int = 1, proxy=None):
    tracer = init_tracer(service_name=SERVICE)
    log = configure_logging(service_name=SERVICE)
    start_metrics_server(METRICS_PORT)

    set_context(run_id=os.getenv("RUN_ID", "run_local"),
                job_id=os.getenv("JOB_ID", "job_crawl"),
                domain=urlparse(start_url).netloc,
                mode="http")

    visited = set()
    q = deque([start_url])

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Crawler/1.0; +https://example.org/bot)",
        "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    with httpx.Client(http2=True, follow_redirects=True) as client:
        pages = 0
        while q and pages < max_pages:
            QUEUE_DEPTH.labels(service=SERVICE, queue="crawler").set(len(q))
            url = q.popleft()
            if url in visited:
                continue
            if not same_host(start_url, url):
                continue

            set_context(domain=urlparse(url).netloc)  # uppdatera kontext per URL

            with traced_span(tracer, "crawl_fetch", {
                "url": url, "domain": urlparse(url).netloc, "mode": "http"
            }):
                try:
                    html = fetch(client, url, headers=headers, proxy=proxy)
                    visited.add(url)
                    pages += 1
                    log.info("fetched", url=url, status="ok", pages=pages)
                except Exception as e:
                    log.warning("fetch_failed", url=url, error=str(e))
                    continue

            # Extract länkar (enkelt) och lägg i kön
            with traced_span(tracer, "crawl_extract_links", {"url": url}):
                try:
                    links = extract_links(url, html)
                    for u in links:
                        if u not in visited:
                            q.append(u)
                    log.info("links_extracted", url=url, count=len(links))
                except Exception as e:
                    log.warning("link_extract_failed", url=url, error=str(e))

    log.info("crawl_finished", pages=len(visited))

if __name__ == "__main__":
    try:
        uvloop.install()
    except Exception:
        pass
    start = os.getenv("START_URL", DEFAULT_START_URL)
    crawl(start_url=start, max_pages=int(os.getenv("MAX_PAGES", "200")))