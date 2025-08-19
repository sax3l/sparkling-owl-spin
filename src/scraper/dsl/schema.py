from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional

class Transform(BaseModel):
    """Defines a data transformation step."""
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)

class Validator(BaseModel):
    """Defines a data validation rule."""
    name: str
    args: Dict[str, Any] = Field(default_factory=dict)

class DBMapping(BaseModel):
    """Defines how a field maps to a database table and column."""
    table: str
    column: str

class ComputeDefinition(BaseModel):
    """Defines how to compute a field from another."""
    from_field: str = Field(..., alias="from")
    apply: List[Transform]

class PrivacyDefinition(BaseModel):
    """Defines privacy and sensitivity settings for a field."""
    sensitivity: Literal["none", "low", "medium", "high", "pii"]
    storage: Literal["plaintext", "encrypted_at_rest", "tokenized"]

class FieldDefinition(BaseModel):
    """Defines how to extract, transform, and validate a single data field."""
    name: str
    type: Literal["string", "number", "date", "boolean", "array"]
    required: bool = False
    selectors: List[Dict[Literal["css", "xpath"], str]] = Field(default_factory=list)
    transform: List[Transform] = Field(default_factory=list)
    validate: List[Validator] = Field(default_factory=list)
    target: Optional[DBMapping] = None
    error_policy: Literal["drop_field", "use_default", "fail_record"] = "drop_field"
    default_value: Optional[Any] = None
    compute: Optional[ComputeDefinition] = None
    privacy: Optional[PrivacyDefinition] = None

class Repeater(BaseModel):
    """Defines how to iterate over a list of elements."""
    by: List[Dict[Literal["css", "xpath"], str]]
    captures: List[FieldDefinition]

class GroupDefinition(BaseModel):
    """Defines extraction for a group of repeating items (a list or table)."""
    group: str
    repeat: Repeater
    link: Dict[str, Any]

class Scope(BaseModel):
    domains: List[str]
    url_patterns: List[str]

class MergePolicy(BaseModel):
    """Defines how to merge data from multiple sources."""
    trust_order: List[str] = Field(default_factory=list)
    overwrite: Dict[str, Any] = Field(default_factory=dict)

class Policy(BaseModel):
    transport: Literal["http", "browser", "auto"] = "auto"
    max_retries: int = 2
    respect_robots: bool = True
    delay_profile: str = "default"
    merge: Optional[MergePolicy] = None

class UpsertConfig(BaseModel):
    key: List[str]
    strategy: Literal["insert_only", "update", "merge"] = "update"

class Output(BaseModel):
    primary_table: str
    upsert: UpsertConfig

class QualityGates(BaseModel):
    min_validity: float = 0.95
    min_coverage: float = 0.90

class ScrapingTemplate(BaseModel):
    """The root model for a scraping template."""
    template_id: str
    version: str
    extends: Optional[str] = None
    scope: Scope
    policy: Policy
    output: Output
    quality: Optional[QualityGates] = None
    macros: Optional[Dict[str, List[Transform]]] = None
    fields: List[FieldDefinition] = Field(default_factory=list)
    relations: List[GroupDefinition] = Field(default_factory=list)