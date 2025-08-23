try:
    from src.scraper.dsl.transformers import regex_extract, to_decimal
    print('Import successful')
    
    # Test regex_extract
    result = regex_extract("Pris: 12 345 kr", {"pattern": r"(\d[\d\s]+)"})
    print(f'regex_extract result: "{result}"')
    
    # Test to_decimal
    result2 = to_decimal("1,999.99", {})
    print(f'to_decimal result: {result2}')
    
except Exception as e:
    print(f'Import failed: {e}')
