"""
Scraper DSL Module - Domain-specific language for data extraction.

Provides a powerful DSL for defining data extraction templates including:
- Field definitions and selectors
- Data transformations and validators
- Cross-field rules and dependencies
- Template versioning and metadata
- Runtime execution engine

Main Components:
- TemplateDSL: Core DSL parser and validator
- FieldTransformer: Data transformation pipeline
- ValidationRule: Field and cross-field validation
- TemplateSchema: Template definition schema
"""

from .schema import TemplateDSL, TemplateSchema, FieldDefinition
from .transformers import FieldTransformer, TransformationPipeline
from .validators import ValidationRule, CrossFieldValidator

__all__ = [
    "TemplateDSL",
    "TemplateSchema", 
    "FieldDefinition",
    "FieldTransformer",
    "TransformationPipeline",
    "ValidationRule",
    "CrossFieldValidator"
]