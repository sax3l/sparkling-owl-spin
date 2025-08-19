from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

class Transform(BaseModel):
    """Defines a data transformation step to be applied to an extracted value."""
    name: Literal[
        "strip", "regex_extract", "to_decimal", "to_int", "date_parse", "map_values",
        "normalize_postal_code", "normalize_reg_nr", "validate_org_nr"
    ]
    args: Dict[str, Any] = Field(default_factory=dict)

class DBMapping(BaseModel):
    """Defines how a field maps to a database table and column."""
    table: str
    column: str
    is_relation_key: bool = False

class FieldDefinition(BaseModel):
    """Defines how to extract, transform, and validate a single data field."""
    name: str
    description: Optional[str] = None
    type: Literal["string", "number", "date", "boolean", "array"]
    selectors: List[str] = Field(..., min_length=1)  # List of CSS/XPath selectors for fallback
    attr: str = "text"  # e.g., 'text', 'href', or other attribute
    required: bool = False
    transforms: List[Transform] = Field(default_factory=list)
    validate: Dict[str, Any] = Field(default_factory=dict) # e.g., {"matches_regex": "^[A-Z]{3}"}
    cross_field_rules: List[str] = Field(default_factory=list)
    db_map: Optional[DBMapping] = None

class ListDefinition(BaseModel):
    """Defines extraction for a list of repeating items (e.g., search results, table rows)."""
    name: str
    container_selector: str # Selector for the list container (e.g., 'ul#items')
    item_selector: str # Selector for a single item within the container (e.g., 'li.item')
    fields: List[FieldDefinition] # Fields to extract relative to each item

class ScrapingTemplate(BaseModel):
    """
    The root model for a scraping template, defining all extraction logic for a page type.
    """
    template_id: str
    version: int
    entity_type: str
    url_pattern: str # Regex to match URLs this template applies to
    fields: List[FieldDefinition] = Field(default_factory=list)
    lists: List[ListDefinition] = Field(default_factory=list)