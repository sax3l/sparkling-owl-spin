def run_template(html_content: str, template: dict) -> tuple:
    """
    Executes the scraping process for a given HTML and template.
    Loader -> Extractor -> Writer
    """
    # 1. Load HTML (already provided)
    # 2. Extract data using template_extractor
    # 3. Transform data using dsl.transformers
    # 4. Validate data
    # 5. Write to database via database.manager
    # 6. Return (record, dq_metrics)
    
    print("Running template...")
    record = {"data": "extracted_data"} # Placeholder
    dq_metrics = {"completeness": 0.95} # Placeholder
    
    return (record, dq_metrics)