from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

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


class APIContract(BaseModel):
    """Contract for API endpoints and their requirements."""
    
    endpoint: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    parameters: Dict[str, Any] = {}
    required_fields: List[str] = []
    response_schema: Optional[Dict[str, Any]] = None
    rate_limit: Optional[int] = None
    timeout: int = 30
    retries: int = 3
    authentication_required: bool = False


class DataContract(BaseModel):
    """Contract for data validation and transformation."""
    
    name: str
    version: str = "1.0"
    schema: Dict[str, Any]
    required_fields: List[str] = []
    optional_fields: List[str] = []
    transformations: List[Dict[str, Any]] = []
    validations: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }