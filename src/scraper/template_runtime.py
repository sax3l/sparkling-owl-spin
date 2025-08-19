import logging
from bs4 import BeautifulSoup, Tag
from typing import Dict, Any, Tuple, Optional
from src.scraper.dsl.schema import ScrapingTemplate, FieldDefinition
from src.scraper.dsl.transformers import TRANSFORMER_REGISTRY

logger = logging.getLogger(__name__)

def _apply_transforms(value: Any, transforms: list) -> Any:
    """Applies a list of transformation functions to a value."""
    processed_value = value
    for transform in transforms:
        transformer_func = TRANSFORMER_REGISTRY.get(transform.name)
        if transformer_func:
            processed_value = transformer_func(processed_value, transform.args)
        else:
            logger.warning(f"Unknown transformer '{transform.name}'.")
    return processed_value

def _extract_field(element: Tag, field: FieldDefinition) -> Optional[Any]:
    """Extracts a single field from a DOM element, handling fallbacks and attributes."""
    for selector in field.selectors:
        try:
            node = element.select_one(selector)
            if node:
                raw_value = node.get_text(strip=True) if field.attr == "text" else node.get(field.attr)
                if raw_value is not None:
                    return _apply_transforms(raw_value, field.transforms)
        except Exception as e:
            logger.error(f"Error applying selector '{selector}' for field '{field.name}': {e}")
    
    if field.required:
        logger.warning(f"Required field '{field.name}' could not be found with any selector.")
    return None

def run_template(html_content: str, template: ScrapingTemplate) -> Tuple[Dict[str, Any], Dict[str, float]]:
    """
    Executes a scraping template against HTML content, applies transformations,
    and calculates Data Quality (DQ) metrics.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    record: Dict[str, Any] = {}
    
    # --- 1. Extract Single Fields ---
    total_required = sum(1 for f in template.fields if f.required)
    found_required = 0
    
    for field in template.fields:
        value = _extract_field(soup, field)
        if value is not None:
            record[field.name] = value
            if field.required:
                found_required += 1

    # --- 2. Extract Lists/Collections ---
    for list_def in template.lists:
        record[list_def.name] = []
        container = soup.select_one(list_def.container_selector)
        if not container:
            logger.warning(f"List container '{list_def.container_selector}' not found for list '{list_def.name}'.")
            continue
        
        items = container.select(list_def.item_selector)
        for item_element in items:
            item_record = {}
            for field in list_def.fields:
                value = _extract_field(item_element, field)
                if value is not None:
                    item_record[field.name] = value
            if item_record:
                record[list_def.name].append(item_record)

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
    
    return record, dq_metrics