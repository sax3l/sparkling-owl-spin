from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def normalize_url(base: str, href: str) -> str | None:
    if not href: return None
    url = urljoin(base, href)
    p = urlparse(url)
    if p.scheme in ("http","https"):
        return url
    return None

def find_links(html: str, base_url: str, selector: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    urls = []
    for a in soup.select(selector):
        href = a.get("href")
        n = normalize_url(base_url, href)
        if n: urls.append(n)
    return urls
