from __future__ import annotations

from typing import List, Literal, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
import re


SelectorType = Literal["css", "xpath"]

# ---- Transform-typer ---------------------------------------------------------

class TransformStrip(BaseModel):
    type: Literal["strip"]

class TransformUpper(BaseModel):
    type: Literal["upper"]

class TransformLower(BaseModel):
    type: Literal["lower"]

class TransformTitle(BaseModel):
    type: Literal["title"]

class TransformNormalizeWhitespace(BaseModel):
    type: Literal["normalize_whitespace"]

class TransformNullIf(BaseModel):
    type: Literal["null_if"]
    equals: str

class TransformRegexExtract(BaseModel):
    type: Literal["regex_extract"]
    pattern: str
    group: int = 1

class TransformRegexSub(BaseModel):
    type: Literal["regex_sub"]
    pattern: str
    repl: str

class TransformToInt(BaseModel):
    type: Literal["to_int"]

class TransformToFloat(BaseModel):
    type: Literal["to_float"]

class TransformParseDate(BaseModel):
    type: Literal["parse_date"]
    formats: List[str] = Field(default_factory=lambda: ["%Y-%m-%d"])

class TransformMap(BaseModel):
    type: Literal["map"]
    mapping: Dict[str, Any]  # str->val (val kan vara str/int/bool)

Transform = Union[
    TransformStrip,
    TransformUpper,
    TransformLower,
    TransformTitle,
    TransformNormalizeWhitespace,
    TransformNullIf,
    TransformRegexExtract,
    TransformRegexSub,
    TransformToInt,
    TransformToFloat,
    TransformParseDate,
    TransformMap,
]

# ---- Validator-typer ---------------------------------------------------------

class ValidatorRequired(BaseModel):
    type: Literal["required"]

class ValidatorRegex(BaseModel):
    type: Literal["regex"]
    pattern: str

class ValidatorLengthRange(BaseModel):
    type: Literal["length_range"]
    min: Optional[int] = None
    max: Optional[int] = None

class ValidatorNumericRange(BaseModel):
    type: Literal["numeric_range"]
    min: Optional[float] = None
    max: Optional[float] = None

class ValidatorEnum(BaseModel):
    type: Literal["enum"]
    values: List[str]

Validator = Union[
    ValidatorRequired, ValidatorRegex, ValidatorLengthRange, ValidatorNumericRange, ValidatorEnum
]

# ---- Fältdefinition ----------------------------------------------------------

class FieldDef(BaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    selector: str
    selector_type: SelectorType = "css"
    attr: str = "text"     # "text" eller t.ex. "href", "content"
    multi: bool = False
    required: bool = False
    transforms: List[Transform] = Field(default_factory=list)
    validators: List[Validator] = Field(default_factory=list)

    @field_validator("selector")
    @classmethod
    def selector_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("selector cannot be empty")
        return v

# ---- Post-processors ---------------------------------------------------------

class PostEnsureFields(BaseModel):
    type: Literal["ensure_fields"]
    fields: List[str]

PostProcessor = Union[PostEnsureFields]

# ---- Samples -----------------------------------------------------------------

class TemplateSamples(BaseModel):
    sample_urls: List[str] = Field(default_factory=list)
    sample_htmls: List[str] = Field(default_factory=list)

# ---- Top-level Template -------------------------------------------------------

class ScrapingTemplate(BaseModel):
    template_id: str = Field(..., pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    version: str
    domain: Optional[str] = None
    entity: Optional[str] = None
    url_pattern: Optional[str] = None
    requires_js: bool = False
    fields: List[FieldDef]
    postprocessors: List[PostProcessor] = Field(default_factory=list)
    samples: TemplateSamples = Field(default_factory=TemplateSamples)

    @model_validator(mode="after")
    def validate_url_pattern(self):
        if self.url_pattern:
            try:
                re.compile(self.url_pattern)
            except re.error as e:
                raise ValueError(f"Invalid url_pattern regex: {e}")
        return self

    def json_schema(self) -> Dict[str, Any]:
        # Bekvämlighetsmetod ifall du vill exponera JSON Schema
        return self.model_json_schema()


# Alias for backward compatibility
FieldTemplate = FieldDef
TemplateDSL = ScrapingTemplate
TemplateSchema = ScrapingTemplate
FieldDefinition = FieldDef