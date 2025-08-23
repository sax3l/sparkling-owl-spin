"""
Data processing and export system
Handles data transformation, validation, and export to multiple formats
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import asyncio
import json
import csv
import xml.etree.ElementTree as ET
from io import StringIO, BytesIO
import logging
from dataclasses import dataclass
import pandas as pd

class ExportFormat(Enum):
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
    XML = "xml"
    PARQUET = "parquet"
    JSONL = "jsonl"  # JSON Lines
    SQL = "sql"

class DataValidationLevel(Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"

@dataclass
class ExportConfig:
    format: ExportFormat
    destination: str  # file path, URL, database connection
    compression: Optional[str] = None  # gzip, zip, bz2
    chunk_size: int = 10000  # For large datasets
    include_metadata: bool = True
    filter_rules: List[Dict] = None
    transformation_rules: List[Dict] = None

@dataclass
class ValidationRule:
    field: str
    rule_type: str  # required, type, range, regex, custom
    parameters: Dict[str, Any]
    severity: str = "error"  # error, warning, info

class DataProcessor:
    """Advanced data processing pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.transformation_functions = {
            'trim': lambda x: x.strip() if isinstance(x, str) else x,
            'lower': lambda x: x.lower() if isinstance(x, str) else x,
            'upper': lambda x: x.upper() if isinstance(x, str) else x,
            'remove_html': self._remove_html_tags,
            'extract_numbers': self._extract_numbers,
            'parse_date': self._parse_date,
            'clean_price': self._clean_price,
            'normalize_url': self._normalize_url
        }
    
    async def process_crawl_results(self, 
                                   results: List[Dict[str, Any]], 
                                   processing_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process crawl results with transformation and validation"""
        processed_results = []
        
        validation_rules = processing_config.get('validation_rules', [])
        transformation_rules = processing_config.get('transformation_rules', [])
        deduplication = processing_config.get('deduplication', {})
        
        # Apply transformations
        for result in results:
            processed_result = await self._apply_transformations(result, transformation_rules)
            processed_results.append(processed_result)
        
        # Validate data
        validated_results = []
        for result in processed_results:
            validation_errors = await self._validate_result(result, validation_rules)
            result['_validation_errors'] = validation_errors
            
            # Include or exclude based on validation level
            validation_level = processing_config.get('validation_level', DataValidationLevel.MODERATE)
            if self._should_include_result(result, validation_level):
                validated_results.append(result)
        
        # Remove duplicates
        if deduplication.get('enabled', False):
            validated_results = await self._deduplicate_results(validated_results, deduplication)
        
        return validated_results
    
    async def _apply_transformations(self, result: Dict[str, Any], transformation_rules: List[Dict]) -> Dict[str, Any]:
        """Apply transformation rules to a single result"""
        transformed_result = result.copy()
        
        for rule in transformation_rules:
            field = rule.get('field')
            function_name = rule.get('function')
            parameters = rule.get('parameters', {})
            
            if field in transformed_result and function_name in self.transformation_functions:
                try:
                    transformation_func = self.transformation_functions[function_name]
                    if parameters:
                        transformed_result[field] = transformation_func(transformed_result[field], **parameters)
                    else:
                        transformed_result[field] = transformation_func(transformed_result[field])
                except Exception as e:
                    self.logger.warning(f"Transformation failed for {field}: {e}")
        
        return transformed_result
    
    async def _validate_result(self, result: Dict[str, Any], validation_rules: List[ValidationRule]) -> List[str]:
        """Validate single result against rules"""
        errors = []
        
        for rule in validation_rules:
            field_value = result.get(rule.field)
            
            try:
                if rule.rule_type == "required" and not field_value:
                    errors.append(f"Required field '{rule.field}' is missing")
                
                elif rule.rule_type == "type":
                    expected_type = rule.parameters.get('type')
                    if field_value is not None and not isinstance(field_value, eval(expected_type)):
                        errors.append(f"Field '{rule.field}' has wrong type")
                
                elif rule.rule_type == "range":
                    min_val = rule.parameters.get('min')
                    max_val = rule.parameters.get('max')
                    if isinstance(field_value, (int, float)):
                        if min_val is not None and field_value < min_val:
                            errors.append(f"Field '{rule.field}' below minimum value")
                        if max_val is not None and field_value > max_val:
                            errors.append(f"Field '{rule.field}' above maximum value")
                
                elif rule.rule_type == "regex":
                    import re
                    pattern = rule.parameters.get('pattern')
                    if field_value and not re.match(pattern, str(field_value)):
                        errors.append(f"Field '{rule.field}' does not match pattern")
                
                elif rule.rule_type == "custom":
                    # Custom validation function
                    validation_func = rule.parameters.get('function')
                    if callable(validation_func) and not validation_func(field_value):
                        errors.append(f"Custom validation failed for '{rule.field}'")
            
            except Exception as e:
                errors.append(f"Validation error for '{rule.field}': {e}")
        
        return errors
    
    def _should_include_result(self, result: Dict[str, Any], validation_level: DataValidationLevel) -> bool:
        """Determine if result should be included based on validation level"""
        errors = result.get('_validation_errors', [])
        
        if validation_level == DataValidationLevel.STRICT:
            return len(errors) == 0
        elif validation_level == DataValidationLevel.MODERATE:
            # Allow warnings but not errors
            critical_errors = [e for e in errors if 'Required field' in e or 'wrong type' in e]
            return len(critical_errors) == 0
        else:  # LENIENT
            return True
    
    async def _deduplicate_results(self, results: List[Dict[str, Any]], dedup_config: Dict) -> List[Dict[str, Any]]:
        """Remove duplicate results"""
        key_fields = dedup_config.get('key_fields', [])
        strategy = dedup_config.get('strategy', 'first')  # first, last, merge
        
        if not key_fields:
            return results
        
        seen_keys = {}
        deduplicated = []
        
        for result in results:
            # Generate key from specified fields
            key_values = tuple(result.get(field) for field in key_fields)
            
            if key_values not in seen_keys:
                seen_keys[key_values] = len(deduplicated)
                deduplicated.append(result)
            else:
                existing_index = seen_keys[key_values]
                if strategy == 'last':
                    deduplicated[existing_index] = result
                elif strategy == 'merge':
                    # Merge non-None values
                    for key, value in result.items():
                        if value is not None:
                            deduplicated[existing_index][key] = value
        
        return deduplicated
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text"""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text) if text else text
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text"""
        import re
        if not text:
            return []
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return [float(n) for n in numbers]
    
    def _parse_date(self, date_str: str, format_hint: str = None) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        formats_to_try = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f'
        ]
        
        if format_hint:
            formats_to_try.insert(0, format_hint)
        
        for fmt in formats_to_try:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def _clean_price(self, price_str: str) -> Optional[float]:
        """Clean and extract price from text"""
        if not price_str:
            return None
        
        import re
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[^\d.,]', '', price_str)
        # Handle different decimal separators
        cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _normalize_url(self, url: str, base_url: str = None) -> str:
        """Normalize URL"""
        if not url:
            return url
        
        # Add protocol if missing
        if url.startswith('//'):
            url = 'https:' + url
        elif not url.startswith(('http://', 'https://')):
            if base_url:
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            else:
                url = 'https://' + url
        
        return url

class DataExporter:
    """Multi-format data export system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def export_data(self, data: List[Dict[str, Any]], config: ExportConfig) -> str:
        """Export data in specified format"""
        
        # Apply filters if specified
        if config.filter_rules:
            data = self._apply_filters(data, config.filter_rules)
        
        # Apply transformations if specified
        if config.transformation_rules:
            processor = DataProcessor()
            data = await processor.process_crawl_results(data, {
                'transformation_rules': config.transformation_rules
            })
        
        # Add metadata if requested
        if config.include_metadata:
            export_metadata = {
                'exported_at': datetime.now().isoformat(),
                'total_records': len(data),
                'export_format': config.format.value,
                'export_config': {
                    'compression': config.compression,
                    'chunk_size': config.chunk_size
                }
            }
        
        # Export based on format
        if config.format == ExportFormat.JSON:
            return await self._export_json(data, config, export_metadata if config.include_metadata else None)
        elif config.format == ExportFormat.CSV:
            return await self._export_csv(data, config)
        elif config.format == ExportFormat.XLSX:
            return await self._export_xlsx(data, config)
        elif config.format == ExportFormat.XML:
            return await self._export_xml(data, config)
        elif config.format == ExportFormat.JSONL:
            return await self._export_jsonl(data, config)
        elif config.format == ExportFormat.SQL:
            return await self._export_sql(data, config)
        else:
            raise ValueError(f"Unsupported export format: {config.format}")
    
    async def _export_json(self, data: List[Dict], config: ExportConfig, metadata: Dict = None) -> str:
        """Export to JSON format"""
        output = {
            'data': data
        }
        
        if metadata:
            output['metadata'] = metadata
        
        json_str = json.dumps(output, indent=2, default=str, ensure_ascii=False)
        
        if config.destination:
            await self._write_file(json_str, config.destination, config.compression)
            return config.destination
        else:
            return json_str
    
    async def _export_csv(self, data: List[Dict], config: ExportConfig) -> str:
        """Export to CSV format"""
        if not data:
            return ""
        
        # Get all unique field names
        fieldnames = set()
        for row in data:
            fieldnames.update(row.keys())
        fieldnames = sorted(list(fieldnames))
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in data:
            # Convert complex objects to strings
            clean_row = {}
            for key, value in row.items():
                if isinstance(value, (dict, list)):
                    clean_row[key] = json.dumps(value, ensure_ascii=False)
                else:
                    clean_row[key] = value
            writer.writerow(clean_row)
        
        csv_content = output.getvalue()
        output.close()
        
        if config.destination:
            await self._write_file(csv_content, config.destination, config.compression)
            return config.destination
        else:
            return csv_content
    
    async def _export_xlsx(self, data: List[Dict], config: ExportConfig) -> str:
        """Export to Excel format"""
        if not data:
            return ""
        
        # Convert to DataFrame for easier Excel export
        df = pd.DataFrame(data)
        
        # Create Excel writer
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        excel_content = output.getvalue()
        output.close()
        
        if config.destination:
            await self._write_binary_file(excel_content, config.destination, config.compression)
            return config.destination
        else:
            return excel_content
    
    async def _export_xml(self, data: List[Dict], config: ExportConfig) -> str:
        """Export to XML format"""
        root = ET.Element('data')
        
        for i, item in enumerate(data):
            item_element = ET.SubElement(root, 'item', id=str(i))
            
            for key, value in item.items():
                field_element = ET.SubElement(item_element, key)
                if isinstance(value, (dict, list)):
                    field_element.text = json.dumps(value, ensure_ascii=False)
                else:
                    field_element.text = str(value) if value is not None else ""
        
        xml_str = ET.tostring(root, encoding='unicode')
        
        if config.destination:
            await self._write_file(xml_str, config.destination, config.compression)
            return config.destination
        else:
            return xml_str
    
    async def _export_jsonl(self, data: List[Dict], config: ExportConfig) -> str:
        """Export to JSON Lines format"""
        lines = []
        for item in data:
            lines.append(json.dumps(item, ensure_ascii=False, default=str))
        
        jsonl_content = '\n'.join(lines)
        
        if config.destination:
            await self._write_file(jsonl_content, config.destination, config.compression)
            return config.destination
        else:
            return jsonl_content
    
    async def _export_sql(self, data: List[Dict], config: ExportConfig) -> str:
        """Export as SQL INSERT statements"""
        if not data:
            return ""
        
        table_name = config.destination or 'crawl_data'
        statements = []
        
        # Get column names from first row
        columns = list(data[0].keys())
        
        for item in data:
            values = []
            for col in columns:
                value = item.get(col)
                if value is None:
                    values.append('NULL')
                elif isinstance(value, str):
                    # Escape single quotes
                    escaped_value = value.replace("'", "''")
                    values.append(f"'{escaped_value}'")
                elif isinstance(value, (dict, list)):
                    json_value = json.dumps(value, ensure_ascii=False).replace("'", "''")
                    values.append(f"'{json_value}'")
                else:
                    values.append(str(value))
            
            statement = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});"
            statements.append(statement)
        
        sql_content = '\n'.join(statements)
        
        if config.destination and config.destination != table_name:
            await self._write_file(sql_content, config.destination, config.compression)
            return config.destination
        else:
            return sql_content
    
    def _apply_filters(self, data: List[Dict], filter_rules: List[Dict]) -> List[Dict]:
        """Apply filter rules to data"""
        filtered_data = []
        
        for item in data:
            include_item = True
            
            for rule in filter_rules:
                field = rule.get('field')
                operator = rule.get('operator')  # eq, ne, gt, lt, contains, regex
                value = rule.get('value')
                
                item_value = item.get(field)
                
                if operator == 'eq' and item_value != value:
                    include_item = False
                    break
                elif operator == 'ne' and item_value == value:
                    include_item = False
                    break
                elif operator == 'gt' and (item_value is None or item_value <= value):
                    include_item = False
                    break
                elif operator == 'lt' and (item_value is None or item_value >= value):
                    include_item = False
                    break
                elif operator == 'contains' and (item_value is None or value not in str(item_value)):
                    include_item = False
                    break
                elif operator == 'regex':
                    import re
                    if item_value is None or not re.search(value, str(item_value)):
                        include_item = False
                        break
            
            if include_item:
                filtered_data.append(item)
        
        return filtered_data
    
    async def _write_file(self, content: str, path: str, compression: Optional[str] = None):
        """Write text content to file"""
        if compression == 'gzip':
            import gzip
            with gzip.open(path + '.gz', 'wt', encoding='utf-8') as f:
                f.write(content)
        elif compression == 'bz2':
            import bz2
            with bz2.open(path + '.bz2', 'wt', encoding='utf-8') as f:
                f.write(content)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    async def _write_binary_file(self, content: bytes, path: str, compression: Optional[str] = None):
        """Write binary content to file"""
        if compression == 'gzip':
            import gzip
            with gzip.open(path + '.gz', 'wb') as f:
                f.write(content)
        elif compression == 'bz2':
            import bz2
            with bz2.open(path + '.bz2', 'wb') as f:
                f.write(content)
        else:
            with open(path, 'wb') as f:
                f.write(content)
