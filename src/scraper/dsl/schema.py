from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

class Transform(BaseModel):
    name: Literal["strip", "regex_extract", "to_decimal", "date_parse", "map_values"]
    args: Dict[str, Any] = {}

class FieldDefinition(BaseModel):
    name: str
    type: Literal["string", "number", "date", "boolean"]
    selector: str  # CSS or XPath
    attr: str = "text"  # e.g., 'text', 'href', or other attribute
    required: bool = False
    transforms: List[Transform] = []
    validate: Dict[str, Any] = {}
    cross_field: List[str] = []

class ScrapingTemplate(BaseModel):
    id: str
    version: int
    entity_type: str
    fields: List[FieldDefinition]