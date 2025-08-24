from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
import yaml

class FollowRule(BaseModel):
    selector: str
    match: Optional[str] = None      # glob/substring för URL-filter
    type: Literal["generic","pagination","detail"] = "generic"

class FieldDef(BaseModel):
    name: str
    selector: str
    attr: Optional[str] = None       # t.ex. "href" för länkar
    type: Literal["text","html","attr"] = "text"
    regex: Optional[str] = None

class Actions(BaseModel):
    scroll: bool = False
    scroll_max: int = 0
    wait_ms: int = 0
    click_selector: Optional[str] = None

class RenderSpec(BaseModel):
    enabled: bool = False            # kräver JS-rendering

class Limits(BaseModel):
    max_pages: int = 500
    max_depth: int = 5

class TemplateModel(BaseModel):
    name: str
    start_urls: List[str]
    follow: List[FollowRule] = Field(default_factory=list)
    extract: List[FieldDef] = Field(default_factory=list)
    render: RenderSpec = Field(default_factory=RenderSpec)
    actions: Actions = Field(default_factory=Actions)
    limits: Limits = Field(default_factory=Limits)
    respect_robots: bool = True
    delay_ms: int = 1000

def parse_template_yaml(text: str) -> TemplateModel:
    data = yaml.safe_load(text)
    return TemplateModel(**data)
