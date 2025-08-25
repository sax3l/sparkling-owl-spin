import csv
import json
import os
from pathlib import Path
from typing import List, Dict, Any

class CSVExporter:
    def __init__(self, output_dir: str = "data/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_results(self, job_id: int, results: List[Dict[str, Any]]) -> str:
        """Export results to CSV file"""
        filename = f"job_{job_id}_results.csv"
        filepath = self.output_dir / filename
        
        if not results:
            return str(filepath)
        
        # Extract all possible fieldnames from all results
        fieldnames = set()
        for result in results:
            if isinstance(result.get('data'), dict):
                fieldnames.update(result['data'].keys())
        fieldnames = ['url'] + sorted(fieldnames)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                row = {'url': result.get('url', '')}
                if isinstance(result.get('data'), dict):
                    row.update(result['data'])
                writer.writerow(row)
        
        return str(filepath)
    
    def export_json(self, job_id: int, results: List[Dict[str, Any]]) -> str:
        """Export results to JSON file"""
        filename = f"job_{job_id}_results.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(results, jsonfile, indent=2, ensure_ascii=False)
        
        return str(filepath)
