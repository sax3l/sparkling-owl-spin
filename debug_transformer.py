import sys
sys.path.append('.')

try:
    from src.scraper.dsl.transformers import regex_extract
    
    text = "Pris: 12 345 kr"
    config = {"pattern": r"(\d[\d\s]+)"}
    result = regex_extract(text, config)
    print(f"Result: '{result}'")
    print(f"Length: {len(result)}")
    print(f"Expected: '12 345'")
    print(f"Match: {result == '12 345'}")
    
except ImportError as e:
    print(f"Import error: {e}")
