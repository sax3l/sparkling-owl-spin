from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List

class ProxyDescriptor(BaseModel):
    host: str
    port: int
    scheme: str = "http"     # http/https/socks5
    region: Optional[str] = None
    latency_ms: Optional[int] = None
    quality: Optional[float] = None
    premium: bool = False
    id: Optional[str] = None  # internt ID hos proxypoolen

class FetchPolicy(BaseModel):
    transport: str           # "http" | "browser"
    user_agent_family: str   # "chrome", "firefox" ...
    delay_ms_range: tuple[int,int]
    reuse_session_s: int
    fingerprint_profile: Optional[str] = None

class UrlTask(BaseModel):
    url: HttpUrl
    referrer: Optional[HttpUrl] = None
    depth: int = 0
    template_hint: Optional[str] = None
    policy_profile: Optional[str] = None

class ExtractField(BaseModel):
    name: str
    selector_css: Optional[str] = None
    selector_xpath: Optional[str] = None
    dtype: str               # "str" | "int" | "decimal" | "date" | "enum" | "json"
    regex: Optional[str] = None
    required: bool = False

class TemplateSpec(BaseModel):
    key: str                 # "vehicle.detail.v1"
    fields: List[ExtractField]
    render_mode: str         # "http" | "browser" | "auto"
    postprocessors: Dict[str, Any] = {}