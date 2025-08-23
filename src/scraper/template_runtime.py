from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable, Iterable, Union
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
import json
import csv

import yaml
from lxml import html as lxml_html
from lxml.cssselect import CSSSelector
from dateutil import parser as date_parser

try:
    import httpx
except ImportError:
    httpx = None

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
except ImportError:
    Engine = None  # type: ignore

from src.scraper.dsl.schema import ScrapingTemplate as TemplateDefinition, FieldDef, Transform, Validator


# ----------------------------- Feltyper ---------------------------------------

class TemplateRuntimeError(Exception):
    pass

class ValidationError(TemplateRuntimeError):
    def __init__(self, field: str, msg: str) -> None:
        super().__init__(f"[{field}] {msg}")
        self.field = field
        self.msg = msg

class SelectorError(TemplateRuntimeError):
    pass


# ----------------------------- Loader ----------------------------------------

def load_template(path: Union[str, Path]) -> TemplateDefinition:
    p = Path(path)
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    return TemplateDefinition.model_validate(data)


# ----------------------------- Fetchers --------------------------------------

class Fetcher:
    def fetch(self, url: str) -> str:
        raise NotImplementedError

class HttpxFetcher(Fetcher):
    def __init__(self, timeout: float = 20.0, headers: Optional[Dict[str, str]] = None):
        if httpx is None:
            raise RuntimeError("httpx not installed; install httpx to use HttpxFetcher")
        self.timeout = timeout
        self.headers = headers or {"User-Agent": "TemplateRuntime/1.0"}

    def fetch(self, url: str) -> str:
        resp = httpx.get(url, timeout=self.timeout, headers=self.headers)
        resp.raise_for_status()
        return resp.text

class FileFetcher(Fetcher):
    """Läser lokala filer: url form 'file:///abs/path.html' eller 'tests/synthetic/foo.html'."""
    def fetch(self, url: str) -> str:
        if url.startswith("file://"):
            path = url[7:]
        else:
            path = url
        return Path(path).read_text(encoding="utf-8")

class InlineFetcher(Fetcher):
    """Används i tester – en dict url->html."""
    def __init__(self, mapping: Dict[str, str]): self.mapping = mapping
    def fetch(self, url: str) -> str:
        if url not in self.mapping:
            raise TemplateRuntimeError(f"inline url missing: {url}")
        return self.mapping[url]


# ----------------------------- Writers ---------------------------------------

class Writer:
    def write_batch(self, rows: List[Dict[str, Any]]) -> None:
        raise NotImplementedError

class JsonlWriter(Writer):
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.fh = self.path.open("a", encoding="utf-8")

    def write_batch(self, rows: List[Dict[str, Any]]) -> None:
        for r in rows:
            self.fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        self.fh.flush()

    def close(self): 
        try: self.fh.close()
        except: pass

class CsvWriter(Writer):
    def __init__(self, path: Union[str, Path], fieldnames: List[str]):
        self.path = Path(path)
        self.fieldnames = fieldnames
        self._init_file()

    def _init_file(self):
        new = not self.path.exists()
        self.fh = self.path.open("a", encoding="utf-8", newline="")
        self.writer = csv.DictWriter(self.fh, fieldnames=self.fieldnames)
        if new:
            self.writer.writeheader()

    def write_batch(self, rows: List[Dict[str, Any]]) -> None:
        for r in rows:
            self.writer.writerow({k: r.get(k, "") for k in self.fieldnames})
        self.fh.flush()

    def close(self):
        try: self.fh.close()
        except: pass

class SqlAlchemyWriter(Writer):
    """Minimal INSERT via SQLAlchemy text() till tabell med kolumner som matchar fält-namnen."""
    def __init__(self, engine: "Engine", table: str, extra_static: Optional[Dict[str, Any]] = None):
        if engine is None:
            raise RuntimeError("SQLAlchemy not installed/engine missing")
        self.engine = engine
        self.table = table
        self.extra = extra_static or {}

    def write_batch(self, rows: List[Dict[str, Any]]) -> None:
        if not rows: return
        with self.engine.begin() as conn:
            for r in rows:
                payload = {**r, **self.extra}
                cols = ", ".join(payload.keys())
                vals = ", ".join([f":{k}" for k in payload.keys()])
                stmt = text(f"INSERT INTO {self.table} ({cols}) VALUES ({vals})")
                conn.execute(stmt, payload)


# ----------------------------- Extractor -------------------------------------

def _css_select(root, selector: str) -> List[Any]:
    sel = CSSSelector(selector)
    return sel(root)

def _xpath_select(root, selector: str) -> List[Any]:
    return root.xpath(selector)

def _node_attr(node, attr: str) -> Any:
    if attr == "text":
        # concatenated text content
        return "".join(node.itertext())
    return node.get(attr)

# ---- transform helpers -------------------------------------------------------

def _apply_transform(value: Any, t: Transform) -> Any:
    ttype = t.__class__.__name__
    if value is None:
        # låt vissa transformations returnera None op, andra kan skapa default
        if ttype in ("TransformNullIf", "TransformMap"):
            pass
        else:
            return None

    if ttype == "TransformStrip":
        return value.strip() if isinstance(value, str) else value

    if ttype == "TransformUpper":
        return value.upper() if isinstance(value, str) else value

    if ttype == "TransformLower":
        return value.lower() if isinstance(value, str) else value

    if ttype == "TransformTitle":
        return value.title() if isinstance(value, str) else value

    if ttype == "TransformNormalizeWhitespace":
        if isinstance(value, str):
            return re.sub(r"\s+", " ", value).strip()
        return value

    if ttype == "TransformNullIf":
        return None if value == t.equals else value

    if ttype == "TransformRegexExtract":
        if not isinstance(value, str): return value
        m = re.search(t.pattern, value)
        return m.group(t.group) if m else None

    if ttype == "TransformRegexSub":
        if not isinstance(value, str): return value
        return re.sub(t.pattern, t.repl, value)

    if ttype == "TransformToInt":
        if value is None or value == "": return None
        try: return int(str(value))
        except ValueError: return None

    if ttype == "TransformToFloat":
        if value is None or value == "": return None
        try: return float(str(value).replace(",", "."))
        except ValueError: return None

    if ttype == "TransformParseDate":
        if value in (None, ""): return None
        if isinstance(value, datetime): return value
        # försök form för form
        for fmt in t.formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue
        # fallback: dateutil
        try:
            return date_parser.parse(str(value))
        except Exception:
            return None

    if ttype == "TransformMap":
        if value in t.mapping:
            return t.mapping[value]
        return value

    return value

def _run_transforms(value: Any, transforms: List[Transform]) -> Any:
    out = value
    for t in transforms:
        out = _apply_transform(out, t)
    return out

# ---- validators --------------------------------------------------------------

def _run_validators(name: str, value: Any, validators: List[Validator], required_flag: bool):
    if required_flag and (value is None or (isinstance(value, str) and value.strip() == "")):
        raise ValidationError(name, "required field missing")

    for v in validators:
        vtype = v.__class__.__name__

        if vtype == "ValidatorRegex":
            if value is None: continue
            if not isinstance(value, str):
                raise ValidationError(name, "regex validator requires string")
            if not re.search(v.pattern, value):
                raise ValidationError(name, f"regex mismatch: {v.pattern}")

        elif vtype == "ValidatorLengthRange":
            if value is None: continue
            if not isinstance(value, (str, list, tuple)):
                raise ValidationError(name, "length_range requires str or list")
            ln = len(value)
            if v.min is not None and ln < v.min:
                raise ValidationError(name, f"length < {v.min}")
            if v.max is not None and ln > v.max:
                raise ValidationError(name, f"length > {v.max}")

        elif vtype == "ValidatorNumericRange":
            if value is None: continue
            try:
                num = float(value)
            except Exception:
                raise ValidationError(name, "numeric_range requires numeric")
            if v.min is not None and num < v.min:
                raise ValidationError(name, f"value < {v.min}")
            if v.max is not None and num > v.max:
                raise ValidationError(name, f"value > {v.max}")

        elif vtype == "ValidatorEnum":
            if value is None: continue
            if value not in v.values:
                raise ValidationError(name, f"value not in enum: {v.values}")

        elif vtype == "ValidatorRequired":
            if value is None or (isinstance(value, str) and value.strip() == ""):
                raise ValidationError(name, "required")

# ---- postprocessors ----------------------------------------------------------

def _run_postprocessors(row: Dict[str, Any], template: TemplateDefinition):
    for p in template.postprocessors:
        ptype = p.__class__.__name__
        if ptype == "PostEnsureFields":
            missing = [f for f in p.fields if (row.get(f) in (None, "", []))]
            if missing:
                raise ValidationError("__row__", f"missing required fields: {missing}")

# ---- core extraction ---------------------------------------------------------

def extract_fields_from_html(html: str, template: TemplateDefinition, url: Optional[str] = None) -> Dict[str, Any]:
    root = lxml_html.fromstring(html)

    result: Dict[str, Any] = {}
    for f in template.fields:
        try:
            # välj nodes
            if f.selector_type == "css":
                nodes = _css_select(root, f.selector)
            else:
                nodes = _xpath_select(root, f.selector)
        except Exception as e:
            raise SelectorError(f"Invalid selector for field '{f.name}': {e}")

        # attr/innerText
        if f.multi:
            values = []
            for n in nodes:
                val = _node_attr(n, f.attr)
                val = _run_transforms(val, f.transforms)
                values.append(val)
            # ev. rensa None
            values = [v for v in values if v not in (None, "")]
            value = values
        else:
            n = nodes[0] if nodes else None
            value = _node_attr(n, f.attr) if n is not None else None
            value = _run_transforms(value, f.transforms)

        # validera fältet
        _run_validators(f.name, value, f.validators, f.required)

        result[f.name] = value

    # postprocessors på hela raden
    _run_postprocessors(result, template)

    # metadata
    result["_extracted_at"] = datetime.utcnow().isoformat() + "Z"
    if url: result["_source_url"] = url
    result["_template_id"] = template.template_id
    result["_template_version"] = template.version

    return result


# ----------------------------- Körning över URL-listor -----------------------

@dataclass
class RunConfig:
    batch_size: int = 200
    stop_on_validation_error: bool = False

def run_template_over_urls(
    urls: Iterable[str],
    template: TemplateDefinition,
    fetcher: Fetcher,
    writer: Writer,
    config: Optional[RunConfig] = None
) -> Dict[str, Any]:
    cfg = config or RunConfig()
    batch: List[Dict[str, Any]] = []
    stats = {"processed": 0, "written": 0, "failed": 0}

    for url in urls:
        try:
            html = fetcher.fetch(url)
            row = extract_fields_from_html(html, template, url=url)
            batch.append(row)
            stats["processed"] += 1
        except ValidationError as ve:
            stats["failed"] += 1
            if cfg.stop_on_validation_error:
                raise
        except Exception:
            stats["failed"] += 1

        if len(batch) >= cfg.batch_size:
            writer.write_batch(batch)
            stats["written"] += len(batch)
            batch.clear()

    if batch:
        writer.write_batch(batch)
        stats["written"] += len(batch)

    # rensa writer om den har close()
    if hasattr(writer, "close"):
        try: writer.close()  # type: ignore
        except: pass

    return stats


class TemplateRuntime:
    """Runtime executor for template processing operations."""
    
    def __init__(self, fetcher: Fetcher = None, writer: Writer = None):
        self.fetcher = fetcher or HttpxFetcher()
        self.writer = writer
    
    def run_template(self, template, urls, config: RunConfig = None):
        """Execute template processing on URLs."""
        config = config or RunConfig()
        
        try:
            # Use the run_template_over_urls function
            return run_template_over_urls(
                template=template, 
                urls=urls if isinstance(urls, list) else [urls],
                fetcher=self.fetcher,
                writer=self.writer,
                cfg=config
            )
        except Exception as e:
            print(f"Template runtime execution failed: {e}")
            raise TemplateRuntimeError(f"Runtime execution failed: {e}")
    
    def extract_fields(self, template, html: str, url: str = None):
        """Extract fields from HTML using template."""
        try:
            return extract_fields_from_html(html, template, url)
        except Exception as e:
            print(f"Field extraction failed: {e}")
            raise TemplateRuntimeError(f"Field extraction failed: {e}")


# Convenience function alias for backward compatibility
def run_template(template, url: str, fetcher: Fetcher = None, writer: Writer = None, cfg: RunConfig = None):
    """Run template on a single URL."""
    runtime = TemplateRuntime(fetcher, writer)
    return runtime.run_template(template, [url], cfg)