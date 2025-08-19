import logging
from bs4 import BeautifulSoup, Tag
from typing import Dict, Any, Tuple, Optional, List
from src.scraper.dsl.schema import ScrapingTemplate, FieldDef, Transform, Validator
from src.scraper.dsl.transformers import TRANSFORMER_REGISTRY
from src.utils.validators import VALIDATOR_REGISTRY

logger = logging.getLogger(__name__)

def _apply_transforms(value: Any, transforms: List[Transform]) -> Any:
    """Applies a list of transform operations to a value."""
    current_value = value
    for transform in transforms:
        # The transform object is now a Pydantic model itself
        func = TRANSFORMER_REGISTRY.get(transform.type)
        if func:
            # Pass the model's dict as args
            current_value = func(current_value, transform.model_dump())
    return current_value

def _apply_validators(value: Any, validators: List[Validator]) -> bool:
    """Applies a list of validation rules to a value."""
    for validator in validators:
        func = VALIDATOR_REGISTRY.get(validator.type)
        if func and not func(value, validator.model_dump()):
            logger.warning(f"Validation failed for value '{value}' with rule '{validator.type}'")
            return False
    return True

def _extract_field(element: Tag, field: FieldDef) -> Tuple[Optional[Any], Dict]:
    """Extracts, transforms, and validates a single field from a DOM element."""
    nodes = []
    if field.selector_type == "css":
        nodes = element.select(field.selector)
    # Add elif for xpath here if needed
    
    if not nodes:
        return None, {"raw": None, "selector": field.selector, "valid": False}

    if not field.multi:
        raw_value = nodes[0].get_text(strip=True) if field.attr == 'text' else nodes[0].get(field.attr)
        transformed = _apply_transforms(raw_value, field.transforms)
        if _apply_validators(transformed, field.validators):
            lineage = {"raw": raw_value, "selector": field.selector, "valid": True}
            return transformed, lineage
    else:
        results = []
        for node in nodes:
            raw_value = node.get_text(strip=True) if field.attr == 'text' else node.get(field.attr)
            transformed = _apply_transforms(raw_value, field.transforms)
            if _apply_validators(transformed, field.validators):
                results.append(transformed)
        return results, {"raw": f"{len(results)} items", "selector": field.selector, "valid": True}

    return None, {"raw": None, "selector": field.selector, "valid": False}


def run_template(html_content: str, template: ScrapingTemplate) -> Tuple[Dict, Dict, Dict]:
    soup = BeautifulSoup(html_content, 'html.parser')
    record: Dict[str, Any] = {}
    lineage: Dict[str, Any] = {}
    
    for field in template.fields:
        value, field_lineage = _extract_field(soup, field)
        if value is not None:
            record[field.name] = value
        elif field.required:
            logger.error(f"Required field '{field.name}' could not be extracted.")
            # Handle error policy here in a real implementation
        lineage[field.name] = field_lineage

    # Simplified DQ metrics for now
    valid_fields = sum(1 for l in lineage.values() if l.get("valid"))
    total_fields = len(template.fields)
    completeness = valid_fields / total_fields if total_fields > 0 else 0
    
    dq_metrics = {"completeness": completeness, "validity": 1.0, "consistency": 1.0, "dq_score": completeness}
    
    return record, dq_metrics, lineage