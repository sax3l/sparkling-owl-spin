from bs4 import BeautifulSoup
import re
from .template_dsl import FieldDef

def extract_fields(html: str, fields: list[FieldDef]) -> dict:
    soup = BeautifulSoup(html, "lxml")
    out = {}
    for f in fields:
        el = soup.select_one(f.selector)
        if not el:
            out[f.name] = None
            continue
        if f.type == "text":
            val = el.get_text(strip=True)
        elif f.type == "html":
            val = str(el)
        elif f.type == "attr":
            val = el.get(f.attr or "href")
        else:
            val = el.get_text(strip=True)
        if f.regex and val:
            m = re.search(f.regex, val)
            val = m.group(1) if m else val
        out[f.name] = val
    return out
