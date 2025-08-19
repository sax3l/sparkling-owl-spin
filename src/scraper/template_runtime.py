import logging
from bs4 import BeautifulSoup, Tag
from typing import Dict, Any, Tuple, Optional, List
from src.scraper.dsl.schema import ScrapingTemplate, FieldDefinition, Transform
from src.scraper.dsl.transformers import TRANSFORMER_REGISTRY

logger = logging.getLogger(__name__)

class ExtractionResult(BaseModel):
    value: Optional[Any] = None
    raw_value: Optional[str] = None
    selector_used: Optional[str] = None
    error: Optional[str] = None

def _apply_transforms(value: Any, transforms: List[Transform]) -> Any:
    """Applies a list of transformation functions to a value."""
    processed_value = value
    for transform in transforms:
        transformer_func = TRANSFORMER_REGISTRY.get(transform.name)
        if transformer_func:
            processed_value = transformer_func(processed_value, transform.args)
        else:
            logger.warning(f"Unknown transformer '{transform.name}'.")
    return processed_value

def _extract_field(element: Tag, field: FieldDefinition) -> ExtractionResult:
    """Extracts a single field from a DOM element, handling fallbacks and attributes."""
    for selector in field.selectors:
        try:
            node = element.select_one(selector)
            if node:
                raw_value = node.get_text(strip=True) if field.attr == "text" else node.get(field.attr)
                if raw_value is not None:
                    transformed_value = _apply_transforms(raw_value, field.transforms)
                    return ExtractionResult(
                        value=transformed_value,
                        raw_value=raw_value,
                        selector_used=selector
                    )
        except Exception as e:
            logger.error(f"Error applying selector '{selector}' for field '{field.name}': {e}")
            return ExtractionResult(error=str(e))
    
    if field.required:
        logger.warning(f"Required field '{field.name}' could not be found with any selector.")
    return ExtractionResult()

def run_template(html_content: str, template: ScrapingTemplate) -> Tuple[Dict[str, Any], Dict[str, float], Dict[str, Any]]:
    """
    Executes a scraping template against HTML content, applies transformations,
    and calculates Data Quality (DQ) metrics and lineage.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    record: Dict[str, Any] = {}
    lineage: Dict[str, Any] = {}
    
    # --- 1. Extract Single Fields ---
    total_required = sum(1 for f in template.fields if f.required)
    found_required = 0
    
    for field in template.fields:
        result = _extract_field(soup, field)
        lineage[field.name] = result.model_dump(exclude_none=True)
        if result.value is not None:
            record[field.name] = result.value
            if field.required:
                found_required += 1

    # --- 2. Extract Lists/Collections ---
    for list_def in template.lists:
        list_records = []
        list_lineage = []
        container = soup.select_one(list_def.container_selector)
        if not container:
            logger.warning(f"List container '{list_def.container_selector}' not found for list '{list_def.name}'.")
            continue
        
        items = container.select(list_def.item_selector)
        for item_element in items:
            item_record = {}
            item_lineage = {}
            for field in list_def.fields:
                result = _extract_field(item_element, field)
                item_lineage[field.name] = result.model_dump(exclude_none=True)
                if result.value is not None:
                    item_record[field.name] = result.value
            if item_record:
                list_records.append(item_record)
                list_lineage.append(item_lineage)
        
        if list_records:
            record[list_def.name] = list_records
            lineage[list_def.name] = list_lineage

    # --- 3. Data Quality Calculation ---
    completeness = (found_required / total_required) if total_required > 0 else 1.0
    # TODO: Implement validity (regex, type checks) and consistency (cross-field rules)
    validity = 1.0
    consistency = 1.0
    
    # Weights: completeness=0.4, validity=0.4, consistency=0.2
    dq_score = (0.4 * completeness) + (0.4 * validity) + (0.2 * consistency)

    dq_metrics = {
        "completeness": round(completeness, 4),
        "validity": round(validity, 4),
        "consistency": round(consistency, 4),
        "dq_score": round(dq_score, 4)
    }
    
    return record, dq_metrics, lineage