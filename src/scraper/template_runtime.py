import logging
from bs4 import BeautifulSoup
from src.scraper.dsl.schema import ScrapingTemplate
from src.scraper.dsl.transformers import TRANSFORMER_REGISTRY

logger = logging.getLogger(__name__)

def run_template(html_content: str, template: ScrapingTemplate) -> tuple[dict, dict]:
    """
    Executes a scraping template against HTML content, applies transformations,
    and calculates Data Quality (DQ) metrics.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    record = {}
    
    total_required = sum(1 for f in template.fields if f.required)
    found_required = 0
    
    for field in template.fields:
        try:
            element = soup.select_one(field.selector)
            if not element:
                if field.required:
                    logger.warning(f"Required field '{field.name}' with selector '{field.selector}' not found.")
                continue

            if field.required:
                found_required += 1

            raw_value = element.get_text(strip=True) if field.attr == "text" else element.get(field.attr)
            
            processed_value = raw_value
            for transform in field.transforms:
                transformer_func = TRANSFORMER_REGISTRY.get(transform.name)
                if transformer_func:
                    processed_value = transformer_func(processed_value, transform.args)
                else:
                    logger.warning(f"Unknown transformer '{transform.name}' for field '{field.name}'.")
            
            record[field.name] = processed_value

        except Exception as e:
            logger.error(f"Error processing field '{field.name}': {e}", exc_info=True)

    # --- Data Quality Calculation ---
    completeness = (found_required / total_required) if total_required > 0 else 1.0
    # TODO: Implement validity and consistency checks based on field.validate and field.cross_field
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