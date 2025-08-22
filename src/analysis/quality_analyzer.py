"""
Data quality analyzer for ECaDP platform.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class QualityMetric:
    """Data quality metric result."""
    name: str
    value: float
    threshold: float
    passed: bool
    details: Dict[str, Any]


@dataclass
class QualityReport:
    """Data quality report."""
    dataset_name: str
    timestamp: datetime
    total_records: int
    metrics: List[QualityMetric]
    overall_score: float
    passed: bool
    
    @property
    def failed_metrics(self) -> List[QualityMetric]:
        """Get metrics that failed threshold."""
        return [m for m in self.metrics if not m.passed]


class DataQualityAnalyzer:
    """Analyzes data quality across different dimensions."""
    
    def __init__(self):
        self.default_thresholds = {
            'completeness': 0.95,
            'validity': 0.90,
            'consistency': 0.85,
            'accuracy': 0.80,
            'uniqueness': 0.99
        }
    
    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        column_rules: Optional[Dict[str, Dict[str, Any]]] = None,
        thresholds: Optional[Dict[str, float]] = None
    ) -> QualityReport:
        """
        Analyze data quality of a pandas DataFrame.
        
        Args:
            df: DataFrame to analyze
            dataset_name: Name of the dataset
            column_rules: Column-specific validation rules
            thresholds: Quality thresholds
            
        Returns:
            QualityReport with analysis results
        """
        thresholds = {**self.default_thresholds, **(thresholds or {})}
        column_rules = column_rules or {}
        
        metrics = []
        
        # Completeness analysis
        completeness = self._analyze_completeness(df)
        metrics.append(QualityMetric(
            name="completeness",
            value=completeness['overall'],
            threshold=thresholds['completeness'],
            passed=completeness['overall'] >= thresholds['completeness'],
            details=completeness
        ))
        
        # Validity analysis
        validity = self._analyze_validity(df, column_rules)
        metrics.append(QualityMetric(
            name="validity",
            value=validity['overall'],
            threshold=thresholds['validity'],
            passed=validity['overall'] >= thresholds['validity'],
            details=validity
        ))
        
        # Consistency analysis
        consistency = self._analyze_consistency(df)
        metrics.append(QualityMetric(
            name="consistency",
            value=consistency['overall'],
            threshold=thresholds['consistency'],
            passed=consistency['overall'] >= thresholds['consistency'],
            details=consistency
        ))
        
        # Uniqueness analysis
        uniqueness = self._analyze_uniqueness(df)
        metrics.append(QualityMetric(
            name="uniqueness",
            value=uniqueness['overall'],
            threshold=thresholds['uniqueness'],
            passed=uniqueness['overall'] >= thresholds['uniqueness'],
            details=uniqueness
        ))
        
        # Calculate overall score
        overall_score = np.mean([m.value for m in metrics])
        overall_passed = all(m.passed for m in metrics)
        
        return QualityReport(
            dataset_name=dataset_name,
            timestamp=datetime.utcnow(),
            total_records=len(df),
            metrics=metrics,
            overall_score=overall_score,
            passed=overall_passed
        )
    
    def _analyze_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data completeness."""
        total_cells = df.size
        missing_cells = df.isnull().sum().sum()
        
        completeness_by_column = {}
        for col in df.columns:
            col_completeness = 1 - (df[col].isnull().sum() / len(df))
            completeness_by_column[col] = col_completeness
        
        overall_completeness = 1 - (missing_cells / total_cells)
        
        return {
            'overall': overall_completeness,
            'by_column': completeness_by_column,
            'missing_cells': missing_cells,
            'total_cells': total_cells
        }
    
    def _analyze_validity(
        self,
        df: pd.DataFrame,
        column_rules: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze data validity based on rules."""
        validity_by_column = {}
        total_valid = 0
        total_checked = 0
        
        for col in df.columns:
            if col not in column_rules:
                continue
            
            rules = column_rules[col]
            valid_count = 0
            checked_count = len(df[col].dropna())
            
            # Check different rule types
            if 'pattern' in rules:
                pattern = re.compile(rules['pattern'])
                valid_mask = df[col].dropna().str.match(pattern, na=False)
                valid_count += valid_mask.sum()
            
            if 'min_length' in rules:
                valid_mask = df[col].dropna().str.len() >= rules['min_length']
                valid_count += valid_mask.sum()
                checked_count = len(df[col].dropna())
            
            if 'max_length' in rules:
                valid_mask = df[col].dropna().str.len() <= rules['max_length']
                valid_count += valid_mask.sum()
            
            if 'allowed_values' in rules:
                valid_mask = df[col].dropna().isin(rules['allowed_values'])
                valid_count += valid_mask.sum()
            
            if 'numeric_range' in rules:
                min_val, max_val = rules['numeric_range']
                valid_mask = (
                    (df[col].dropna() >= min_val) & 
                    (df[col].dropna() <= max_val)
                )
                valid_count += valid_mask.sum()
            
            if checked_count > 0:
                validity_by_column[col] = valid_count / checked_count
                total_valid += valid_count
                total_checked += checked_count
        
        overall_validity = total_valid / total_checked if total_checked > 0 else 1.0
        
        return {
            'overall': overall_validity,
            'by_column': validity_by_column,
            'total_valid': total_valid,
            'total_checked': total_checked
        }
    
    def _analyze_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data consistency."""
        consistency_issues = []
        
        # Check for inconsistent formats in string columns
        string_columns = df.select_dtypes(include=['object']).columns
        format_consistency = {}
        
        for col in string_columns:
            if df[col].dtype == 'object':
                # Check case consistency
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    # Check for mixed case
                    has_upper = non_null_values.str.isupper().any()
                    has_lower = non_null_values.str.islower().any()
                    has_title = non_null_values.str.istitle().any()
                    
                    case_variations = sum([has_upper, has_lower, has_title])
                    
                    # Check for whitespace inconsistencies
                    has_leading_space = non_null_values.str.startswith(' ').any()
                    has_trailing_space = non_null_values.str.endswith(' ').any()
                    
                    consistency_score = 1.0
                    if case_variations > 1:
                        consistency_score -= 0.3
                    if has_leading_space or has_trailing_space:
                        consistency_score -= 0.2
                    
                    format_consistency[col] = max(0.0, consistency_score)
        
        # Check for date format consistency
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            # All datetime columns are already consistent by nature
            format_consistency[col] = 1.0
        
        overall_consistency = np.mean(list(format_consistency.values())) if format_consistency else 1.0
        
        return {
            'overall': overall_consistency,
            'by_column': format_consistency,
            'issues': consistency_issues
        }
    
    def _analyze_uniqueness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data uniqueness."""
        uniqueness_by_column = {}
        
        for col in df.columns:
            total_values = len(df[col].dropna())
            unique_values = df[col].nunique()
            
            if total_values > 0:
                uniqueness_by_column[col] = unique_values / total_values
            else:
                uniqueness_by_column[col] = 1.0
        
        # Overall uniqueness (weighted by column importance)
        overall_uniqueness = np.mean(list(uniqueness_by_column.values()))
        
        # Find duplicate rows
        duplicate_rows = df.duplicated().sum()
        row_uniqueness = 1 - (duplicate_rows / len(df)) if len(df) > 0 else 1.0
        
        return {
            'overall': min(overall_uniqueness, row_uniqueness),
            'by_column': uniqueness_by_column,
            'row_uniqueness': row_uniqueness,
            'duplicate_rows': duplicate_rows
        }
    
    def generate_recommendations(self, report: QualityReport) -> List[str]:
        """Generate recommendations based on quality report."""
        recommendations = []
        
        for metric in report.failed_metrics:
            if metric.name == 'completeness':
                recommendations.append(
                    f"Improve data completeness: {metric.value:.2%} < {metric.threshold:.2%}. "
                    f"Focus on columns with high missing rates."
                )
            
            elif metric.name == 'validity':
                recommendations.append(
                    f"Improve data validity: {metric.value:.2%} < {metric.threshold:.2%}. "
                    f"Review validation rules and data entry processes."
                )
            
            elif metric.name == 'consistency':
                recommendations.append(
                    f"Improve data consistency: {metric.value:.2%} < {metric.threshold:.2%}. "
                    f"Standardize data formats and entry procedures."
                )
            
            elif metric.name == 'uniqueness':
                recommendations.append(
                    f"Improve data uniqueness: {metric.value:.2%} < {metric.threshold:.2%}. "
                    f"Remove duplicate records and implement deduplication logic."
                )
        
        if not recommendations:
            recommendations.append("Data quality is within acceptable thresholds.")
        
        return recommendations
