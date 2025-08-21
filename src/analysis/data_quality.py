"""
Data Quality Analysis Module for ECaDP Platform.

Provides comprehensive data quality assessment for scraped data
including completeness, accuracy, consistency, and validity metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import re
import json
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 70-89%
    FAIR = "fair"           # 50-69%
    POOR = "poor"           # 0-49%
    UNKNOWN = "unknown"


@dataclass
class DataQualityMetrics:
    """Data quality metrics for a dataset or record."""
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.UNKNOWN
    
    # Detailed metrics
    total_fields: int = 0
    populated_fields: int = 0
    valid_fields: int = 0
    inconsistent_fields: List[str] = field(default_factory=list)
    invalid_fields: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    
    # Metadata
    assessed_at: datetime = field(default_factory=datetime.now)
    assessment_rules: Dict[str, Any] = field(default_factory=dict)


class DataQualityAnalyzer:
    """
    Analyzes data quality for scraped records.
    
    Provides methods to assess completeness, accuracy, consistency,
    and validity of extracted data according to configurable rules.
    """
    
    def __init__(self, quality_rules: Optional[Dict[str, Any]] = None):
        """
        Initialize the data quality analyzer.
        
        Args:
            quality_rules: Dictionary of field-specific quality rules
        """
        self.quality_rules = quality_rules or self._get_default_rules()
        
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default quality assessment rules."""
        return {
            "required_fields": [
                "name", "full_name", "registration_number", 
                "make", "model", "organization_number"
            ],
            "email_pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "phone_pattern": r'^[\+]?[1-9][\d]{0,15}$',
            "registration_pattern": r'^[A-Z]{3}\s?\d{3}$',  # Swedish format
            "organization_number_pattern": r'^\d{6}-\d{4}$',  # Swedish format
            "vin_pattern": r'^[A-HJ-NPR-Z0-9]{17}$',
            "postal_code_pattern": r'^\d{3}\s?\d{2}$',  # Swedish format
            "year_range": (1886, datetime.now().year + 2),
            "max_string_length": 1000,
            "consistency_checks": {
                "name_variants": ["name", "full_name", "company_name"],
                "contact_info": ["email", "phone", "website"],
                "location_info": ["city", "postal_code", "country"]
            }
        }
    
    def analyze_record(self, record: Dict[str, Any], 
                      record_type: str = "general") -> DataQualityMetrics:
        """
        Analyze data quality for a single record.
        
        Args:
            record: Dictionary containing the record data
            record_type: Type of record (person, company, vehicle)
            
        Returns:
            DataQualityMetrics object with assessment results
        """
        metrics = DataQualityMetrics()
        
        # Count total fields
        metrics.total_fields = len(record)
        
        # Assess completeness
        metrics.completeness_score = self._assess_completeness(record, metrics)
        
        # Assess validity
        metrics.validity_score = self._assess_validity(record, metrics)
        
        # Assess consistency
        metrics.consistency_score = self._assess_consistency(record, metrics)
        
        # For accuracy, we'd need reference data - using validity as proxy
        metrics.accuracy_score = metrics.validity_score
        
        # Calculate overall score
        metrics.overall_score = self._calculate_overall_score(metrics)
        
        # Determine quality level
        metrics.quality_level = self._determine_quality_level(metrics.overall_score)
        
        return metrics
    
    def _assess_completeness(self, record: Dict[str, Any], 
                           metrics: DataQualityMetrics) -> float:
        """Assess completeness of the record."""
        populated_count = 0
        
        for field, value in record.items():
            if self._is_populated(value):
                populated_count += 1
            else:
                metrics.missing_fields.append(field)
        
        metrics.populated_fields = populated_count
        
        if metrics.total_fields == 0:
            return 0.0
            
        return (populated_count / metrics.total_fields) * 100
    
    def _assess_validity(self, record: Dict[str, Any], 
                        metrics: DataQualityMetrics) -> float:
        """Assess validity of field values."""
        valid_count = 0
        total_populated = metrics.populated_fields
        
        for field, value in record.items():
            if not self._is_populated(value):
                continue
                
            if self._is_valid_field(field, value):
                valid_count += 1
            else:
                metrics.invalid_fields.append(field)
        
        metrics.valid_fields = valid_count
        
        if total_populated == 0:
            return 100.0  # No fields to validate
            
        return (valid_count / total_populated) * 100
    
    def _assess_consistency(self, record: Dict[str, Any], 
                          metrics: DataQualityMetrics) -> float:
        """Assess internal consistency of the record."""
        consistency_issues = 0
        consistency_checks = 0
        
        # Check name consistency
        name_fields = self.quality_rules["consistency_checks"]["name_variants"]
        name_values = [record.get(field) for field in name_fields 
                      if self._is_populated(record.get(field))]
        
        if len(name_values) > 1:
            consistency_checks += 1
            if not self._are_names_consistent(name_values):
                consistency_issues += 1
                metrics.inconsistent_fields.extend(name_fields)
        
        # Check date consistency (e.g., start_date <= end_date)
        if (self._is_populated(record.get('start_date')) and 
            self._is_populated(record.get('end_date'))):
            consistency_checks += 1
            try:
                start = self._parse_date(record['start_date'])
                end = self._parse_date(record['end_date'])
                if start and end and start > end:
                    consistency_issues += 1
                    metrics.inconsistent_fields.extend(['start_date', 'end_date'])
            except Exception:
                pass
        
        if consistency_checks == 0:
            return 100.0
            
        return ((consistency_checks - consistency_issues) / consistency_checks) * 100
    
    def _is_populated(self, value: Any) -> bool:
        """Check if a field value is populated."""
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
    
    def _is_valid_field(self, field: str, value: Any) -> bool:
        """Check if a field value is valid according to rules."""
        if not self._is_populated(value):
            return True  # Empty fields are not invalid, just incomplete
        
        try:
            # Convert to string for pattern matching
            str_value = str(value).strip()
            
            # Email validation
            if 'email' in field.lower():
                return bool(re.match(self.quality_rules["email_pattern"], str_value))
            
            # Phone validation
            if 'phone' in field.lower():
                return bool(re.match(self.quality_rules["phone_pattern"], 
                                   re.sub(r'[\s\-\(\)]', '', str_value)))
            
            # Registration number validation
            if field in ['registration_number', 'reg_number']:
                return bool(re.match(self.quality_rules["registration_pattern"], 
                                   str_value.upper()))
            
            # Organization number validation
            if field in ['organization_number', 'org_number']:
                return bool(re.match(self.quality_rules["organization_number_pattern"], 
                                   str_value))
            
            # VIN validation
            if field in ['vin_number', 'vin']:
                return bool(re.match(self.quality_rules["vin_pattern"], 
                                   str_value.upper()))
            
            # Postal code validation
            if field in ['postal_code', 'zip_code']:
                return bool(re.match(self.quality_rules["postal_code_pattern"], 
                                   str_value))
            
            # Year validation
            if field in ['year', 'model_year', 'manufacture_year']:
                try:
                    year = int(value)
                    min_year, max_year = self.quality_rules["year_range"]
                    return min_year <= year <= max_year
                except (ValueError, TypeError):
                    return False
            
            # String length validation
            if isinstance(value, str):
                return len(str_value) <= self.quality_rules["max_string_length"]
            
            # Default: assume valid if no specific rule
            return True
            
        except Exception as e:
            logger.warning(f"Error validating field {field}: {e}")
            return False
    
    def _are_names_consistent(self, names: List[str]) -> bool:
        """Check if name variants are consistent."""
        if len(names) <= 1:
            return True
        
        # Normalize names for comparison
        normalized = [self._normalize_name(name) for name in names]
        
        # Check if any name is a subset of another
        for i, name1 in enumerate(normalized):
            for j, name2 in enumerate(normalized):
                if i != j:
                    if name1 in name2 or name2 in name1:
                        return True
        
        # Check similarity threshold
        return self._calculate_name_similarity(normalized) > 0.7
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison."""
        return re.sub(r'[^\w\s]', '', name.lower()).strip()
    
    def _calculate_name_similarity(self, names: List[str]) -> float:
        """Calculate similarity between names."""
        # Simple Jaccard similarity for now
        if len(names) < 2:
            return 1.0
        
        words1 = set(names[0].split())
        words2 = set(names[1].split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if len(union) == 0:
            return 0.0
        
        return len(intersection) / len(union)
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats."""
        if isinstance(date_value, date):
            return date_value
        if isinstance(date_value, datetime):
            return date_value.date()
        
        if isinstance(date_value, str):
            # Try common date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt).date()
                except ValueError:
                    continue
        
        return None
    
    def _calculate_overall_score(self, metrics: DataQualityMetrics) -> float:
        """Calculate overall quality score."""
        # Weighted average of different quality dimensions
        weights = {
            'completeness': 0.3,
            'validity': 0.3,
            'accuracy': 0.2,
            'consistency': 0.2
        }
        
        overall = (
            metrics.completeness_score * weights['completeness'] +
            metrics.validity_score * weights['validity'] +
            metrics.accuracy_score * weights['accuracy'] +
            metrics.consistency_score * weights['consistency']
        )
        
        return round(overall, 2)
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on overall score."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 70:
            return QualityLevel.GOOD
        elif score >= 50:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    def analyze_batch(self, records: List[Dict[str, Any]], 
                     record_type: str = "general") -> List[DataQualityMetrics]:
        """
        Analyze data quality for a batch of records.
        
        Args:
            records: List of record dictionaries
            record_type: Type of records
            
        Returns:
            List of DataQualityMetrics objects
        """
        return [self.analyze_record(record, record_type) for record in records]
    
    def generate_summary_report(self, metrics_list: List[DataQualityMetrics]) -> Dict[str, Any]:
        """
        Generate a summary report from multiple quality assessments.
        
        Args:
            metrics_list: List of DataQualityMetrics objects
            
        Returns:
            Summary report dictionary
        """
        if not metrics_list:
            return {"error": "No metrics to summarize"}
        
        total_records = len(metrics_list)
        
        # Calculate averages
        avg_completeness = sum(m.completeness_score for m in metrics_list) / total_records
        avg_validity = sum(m.validity_score for m in metrics_list) / total_records
        avg_consistency = sum(m.consistency_score for m in metrics_list) / total_records
        avg_overall = sum(m.overall_score for m in metrics_list) / total_records
        
        # Count quality levels
        quality_distribution = {}
        for level in QualityLevel:
            count = sum(1 for m in metrics_list if m.quality_level == level)
            quality_distribution[level.value] = count
        
        # Find common issues
        all_invalid_fields = []
        all_missing_fields = []
        all_inconsistent_fields = []
        
        for metrics in metrics_list:
            all_invalid_fields.extend(metrics.invalid_fields)
            all_missing_fields.extend(metrics.missing_fields)
            all_inconsistent_fields.extend(metrics.inconsistent_fields)
        
        # Count field issues
        invalid_field_counts = {}
        missing_field_counts = {}
        inconsistent_field_counts = {}
        
        for field in all_invalid_fields:
            invalid_field_counts[field] = invalid_field_counts.get(field, 0) + 1
        
        for field in all_missing_fields:
            missing_field_counts[field] = missing_field_counts.get(field, 0) + 1
            
        for field in all_inconsistent_fields:
            inconsistent_field_counts[field] = inconsistent_field_counts.get(field, 0) + 1
        
        return {
            "summary": {
                "total_records": total_records,
                "average_scores": {
                    "completeness": round(avg_completeness, 2),
                    "validity": round(avg_validity, 2),
                    "consistency": round(avg_consistency, 2),
                    "overall": round(avg_overall, 2)
                },
                "quality_distribution": quality_distribution
            },
            "common_issues": {
                "most_invalid_fields": dict(sorted(invalid_field_counts.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10]),
                "most_missing_fields": dict(sorted(missing_field_counts.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10]),
                "most_inconsistent_fields": dict(sorted(inconsistent_field_counts.items(), 
                                                       key=lambda x: x[1], reverse=True)[:10])
            },
            "generated_at": datetime.now().isoformat()
        }