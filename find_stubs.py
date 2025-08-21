import json

# Load analysis results with UTF-8 encoding
with open('analysis_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find stub files from the code_analysis section
code_analysis = data.get('code_analysis', {})
stub_files = []

for module_name, module_data in code_analysis.items():
    if isinstance(module_data, dict) and 'files' in module_data:
        for filename, file_data in module_data['files'].items():
            if isinstance(file_data, dict) and file_data.get('is_stub'):
                stub_files.append({
                    'path': file_data.get('path', f"{module_name}/{filename}"),
                    'filename': filename,
                    'module': module_name
                })

print("Remaining stub files:")
for stub in stub_files:
    print(f"  {stub['path']}")
    
print(f"\nTotal stub files: {len(stub_files)}")

# Also check summary for stub count
summary = data.get('summary', {})
print(f"Summary shows {summary.get('stub_files', 0)} stub files")
