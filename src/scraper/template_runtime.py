import logging
from bs4 import BeautifulSoup, Tag
from typing import Dict, Any, Tuple, Optional, List
from src.scraper.dsl.schema import ScrapingTemplate, FieldDefinition, Transform, Validator
from src.scraper.dsl.transformers import TRANSFORMER_REGISTRY
from src.utils.validators import VALIDATOR_REGISTRY

logger = logging.getLogger(__name__)

def _apply_transforms(value: Any, transforms: List[Transform]) -> Any:
    for transform in transforms:
        func = TRANSFORMER_REGISTRY.get(transform.name)
        if func: value = func(value, transform.args)
    return value

def _apply_validators(value: Any, validators: List[Validator]) -> bool:
    for validator in validators:
        func = VALIDATOR_REGISTRY.get(validator.name)
        if func and not func(value, validator.args):
            return False
    return True

def _extract_field(element: Tag, field: FieldDefinition) -> Tuple[Optional[Any], Dict]:
    for selector_obj in field.selectors:
        selector_type, selector = next(iter(selector_obj.items()))
        try:
            node = element.select_one(selector) if selector_type == "css" else element.find(xpath=selector) # Note: BeautifulSoup has limited XPath
            if node:
                raw_value = node.get_text(strip=True)
                transformed = _apply_transforms(raw_value, field.transform)
                if _apply_validators(transformed, field.validate):
                    lineage = {"raw": raw_value, "selector": selector, "valid": True}
                    return transformed, lineage
        except Exception as e:
            logger.error(f"Selector '{selector}' failed for field '{field.name}': {e}")
    
    lineage = {"raw": None, "selector": None, "valid": False}
    return None, lineage

def run_template(html_content: str, template: ScrapingTemplate) -> Tuple[Dict, Dict, Dict]:
    soup = BeautifulSoup(html_content, 'html.parser')
    record: Dict[str, Any] = {}
    lineage: Dict[str, Any] = {}
    
    # Extract single fields
    for field in template.fields:
        value, field_lineage = _extract_field(soup, field)
        if value is not None:
            record[field.name] = value
        lineage[field.name] = field_lineage

    # Extract relations/groups
    for relation in template.relations:
        group_name = relation.group
        list_records = []
        list_lineage = []
        
        container_selector_obj = relation.repeat.by[0]
        container_selector_type, container_selector = next(iter(container_selector_obj.items()))
        
        items = soup.select(container_selector)
        for item_element in items:
            item_record, item_lineage = {}, {}
            for field in relation.repeat.captures:
                value, field_lineage = _extract_field(item_element, field)
                if value is not None:
                    item_record[field.name] = value
                item_lineage[field.name] = field_lineage
            
            if item_record:
                list_records.append(item_record)
                list_lineage.append(item_lineage)
        
        if list_records:
            record[group_name] = list_records
            lineage[group_name] = list_lineage

    # Simplified DQ metrics for now
    dq_metrics = {"completeness": 1.0, "validity": 1.0, "consistency": 1.0, "dq_score": 1.0}
    
    return record, dq_metrics, lineage