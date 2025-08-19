import os
import asyncio
import httpx
import uvloop
from typing import Dict, Any, List
from urllib.parse import urlparse

from src.observability.instrumentation import (
    init_tracer, configure_logging, start_metrics_server, set_context,
    traced_span, retryable, TransientHTTPError,
    report_extraction_success, QUEUE_DEPTH
)

SERVICE = "scraper"
METRICS_PORT = int(os.getenv("METRICS_PORT", "9102"))

# ------------------------
# HTTP-läge (snabbt)
# ------------------------
@retryable(service=SERVICE, mode="http", domain=None)
def http_fetch(url: str, headers=None, proxy=None) -> str:
    with httpx.Client(http2=True, follow_redirects=True, timeout=25) as client:
        r = client.get(url, headers=headers, proxies=proxy)
        if r.status_code >= 500:
            raise TransientHTTPError(status_code=r.status_code, msg=f"server error {r.status_code}")
        if r.status_code in (403, 429):
            e = Exception(f"policy/block {r.status_code}")
            setattr(e, "status_code", r.status_code)
            raise e
        r.raise_for_status()
        return r.text

def parse_with_selectors(html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
    # Demo: ersätt med lxml/BS4 + robusta XPath/CSS-hanterare
    # Returnerar fiktiva värden för exempel
    data = {}
    for field, sel in selectors.items():
        # här hade du hittat elementet via sel; vi simulerar:
        data[field] = f"dummy_value_for_{field}"
    return data

def validate_fields(data: Dict[str, Any]) -> float:
    # Räkna enkel "validitetsratio" (i verkligheten: regex/typkontroller per fält)
    if not data:
        return 0.0
    valid = sum(1 for v in data.values() if v is not None and v != "")
    return valid / len(data)

# ------------------------
# Browser-läge (Playwright hooks)
# ------------------------
async def browser_fetch(url: str, steps: List[Dict[str, Any]] = None) -> str:
    """
    Minimal Playwright-exempel (utan stealth här).
    steps: [{"action": "click", "selector": "..."},
            {"action": "type", "selector": "...", "text": "..."},
            {"action": "wait", "selector": "..."}]
    """
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="sv-SE")
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # utför enkla steg
        if steps:
            for s in steps:
                act = s.get("action")
                sel = s.get("selector")
                if act == "click":
                    await page.click(sel, timeout=15000)
                elif act == "type":
                    await page.fill(sel, s.get("text",""), timeout=15000)
                elif act == "wait":
                    await page.wait_for_selector(sel, timeout=30000)
                elif act == "scroll_bottom":
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1200)

        html = await page.content()
        await context.close()
        await browser.close()
        return html

# ------------------------
# Körning
# ------------------------
def run_http(urls: List[str], selectors: Dict[str, str], template: str, proxy=None):
    tracer = init_tracer(service_name=SERVICE)
    log = configure_logging(service_name=SERVICE)
    start_metrics_server(METRICS_PORT)

    set_context(run_id=os.getenv("RUN_ID","run_local"),
                job_id=os.getenv("JOB_ID","job_scrape_http"),
                template=template,
                mode="http")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Scraper/1.0)",
        "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    for i, url in enumerate(urls, 1):
        domain = urlparse(url).netloc
        set_context(domain=domain)
        QUEUE_DEPTH.labels(service=SERVICE, queue="scraper_http").set(len(urls) - i)

        with traced_span(tracer, "http_fetch", {"url": url, "domain": domain, "mode": "http"}):
            try:
                html = http_fetch(url, headers=headers, proxy=proxy)
                log.info("fetched_http", url=url, status="ok")
            except Exception as e:
                log.warning("fetch_failed_http", url=url, error=str(e))
                continue

        with traced_span(tracer, "parse_extract", {"template": template}):
            try:
                data = parse_with_selectors(html, selectors)
                validity = validate_fields(data)
                report_extraction_success(SERVICE, domain, template, validity_ratio=validity)
                log.info("extracted", url=url, template=template, validity=round(validity,3))
            except Exception as e:
                log.warning("parse_failed", url=url, error=str(e))

def run_browser(urls: List[str], selectors: Dict[str, str], template: str, steps: List[Dict[str, Any]] = None):
    tracer = init_tracer(service_name=SERVICE)
    log = configure_logging(service_name=SERVICE)
    start_metrics_server(METRICS_PORT)

    set_context(run_id=os.getenv("RUN_ID","run_local"),
                job_id=os.getenv("JOB_ID","job_scrape_browser"),
                template=template,
                mode="browser")

    async def _run():
        for i, url in enumerate(urls, 1):
            domain = urlparse(url).netloc
            set_context(domain=domain)
            QUEUE_DEPTH.labels(service=SERVICE, queue="scraper_browser").set(len(urls) - i)

            # Tracing runt browser-steg
            with traced_span(tracer, "browser_nav", {"url": url, "domain": domain, "mode": "browser"},):
                try:
                    html = await browser_fetch(url, steps=steps)
                    log.info("fetched_browser", url=url, status="ok")
                except Exception as e:
                    log.warning("browser_failed", url=url, error=str(e))
                    continue

            with traced_span(tracer, "parse_extract", {"template": template}):
                try:
                    data = parse_with_selectors(html, selectors)
                    validity = validate_fields(data)
                    report_extraction_success(SERVICE, domain, template, validity_ratio=validity)
                    log.info("extracted", url=url, template=template, validity=round(validity,3))
                except Exception as e:
                    log.warning("parse_failed", url=url, error=str(e))

    try:
        uvloop.install()
    except Exception:
        pass
    asyncio.run(_run())

if __name__ == "__main__":
    # Exempel: kör HTTP-läge på två URL:er
    urls = [
        os.getenv("URL1", "https://example.com/"),
        os.getenv("URL2", "https://example.com/about")
    ]
    selectors = {
        "title": "//title",   # i produktion: riktiga XPath/CSS
        "h1": "//h1[1]"
    }
    mode = os.getenv("MODE", "http")
    if mode == "http":
        run_http(urls, selectors, template="demo_template_v1")
    else:
        steps = [
            {"action": "wait", "selector": "body"},
            {"action": "scroll_bottom"}
        ]
        run_browser(urls, selectors, template="demo_template_v1", steps=steps)