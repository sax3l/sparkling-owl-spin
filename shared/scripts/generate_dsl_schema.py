import json
from pathlib import Path
import sys
from src.scraper.dsl.schema import ScrapingTemplate

def generate_schema():
    """
    Generates a JSON Schema from the ScrapingTemplate Pydantic model
    and saves it to the docs/ directory.
    """
    print("Generating JSON Schema for the scraping DSL...")
    
    try:
        schema = ScrapingTemplate.model_json_schema()
        output_path = Path("docs/dsl.schema.json")
        
        output_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
        
        print(f"✅ Successfully wrote schema to {output_path}")
        print("This file can be used to provide real-time validation in editors like VSCode.")
    except Exception as e:
        print(f"❌ Failed to generate schema: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    generate_schema()