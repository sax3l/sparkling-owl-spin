"""
Data Quality Checker
===================

Comprehensive data quality assessment and validation engine.
Provides detailed quality metrics, validation rules, and quality scoring.
"""

import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from datetime import datetime, timedelta
import asyncio
import json
import re
from dataclasses import dataclass, field
from collections import defaultdict, Counter
from enum import Enum
import statistics

from ..database.manager import DatabaseManager
from ..observability.metrics import metrics_collector

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Data quality dimensions"""
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"

class QualitySeverity(Enum):
    """Quality issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class QualityRule:
    """Data quality validation rule"""
    name: str
    dimension: QualityDimension
    description: str
    severity: QualitySeverity
    field_pattern: str = "*"  # Glob pattern for field names
    validation_func: callable = None
    expected_values: Optional[Set] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    regex_pattern: Optional[str] = None
    required: bool = False

@dataclass
class QualityIssue:
    """Data quality issue"""
    rule_name: str
    dimension: QualityDimension
    severity: QualitySeverity
    field_name: str
    description: str
    value: Any
    record_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    template_id: Optional[int]
    template_name: str
    assessment_date: datetime
    total_records: int
    records_analyzed: int
    
    # Quality scores by dimension (0-100)
    quality_scores: Dict[QualityDimension, float]
    overall_quality_score: float
    
    # Detailed metrics
    field_metrics: Dict[str, Dict[str, Any]]
    issues: List[QualityIssue]
    rule_violations: Dict[str, int]
    
    # Recommendations
    recommendations: List[str]
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

class QualityChecker:
    """
    Comprehensive data quality assessment engine
    
    Features:
    - Multi-dimensional quality assessment
    - Configurable validation rules
    - Automated quality scoring
    - Issue detection and reporting
    - Quality trend monitoring
    - Customizable quality thresholds
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Quality configuration
        self.quality_thresholds = {
            QualityDimension.COMPLETENESS: 90.0,
            QualityDimension.ACCURACY: 95.0,
            QualityDimension.CONSISTENCY: 90.0,
            QualityDimension.VALIDITY: 95.0,
            QualityDimension.UNIQUENESS: 85.0,
            QualityDimension.TIMELINESS: 80.0
        }
        
        # Default quality rules
        self.quality_rules: List[QualityRule] = []
        self._initialize_default_rules()
        
        # Cache for template-specific rules
        self.template_rules_cache = {}
        
        # Metrics tracking
        self.quality_history = defaultdict(list)
    
    def _initialize_default_rules(self):
        """Initialize default quality validation rules"""
        
        # Completeness rules
        self.quality_rules.extend([
            QualityRule(
                name="required_field_present",
                dimension=QualityDimension.COMPLETENESS,
                description="Required fields must be present and non-null",
                severity=QualitySeverity.CRITICAL,
                required=True
            ),
            QualityRule(
                name="non_empty_string",
                dimension=QualityDimension.COMPLETENESS,
                description="String fields should not be empty",
                severity=QualitySeverity.HIGH,
                validation_func=lambda x: isinstance(x, str) and x.strip() != ""
            )
        ])
        
        # Validity rules
        self.quality_rules.extend([
            QualityRule(
                name="email_format",
                dimension=QualityDimension.VALIDITY,
                description="Email fields must have valid format",
                severity=QualitySeverity.HIGH,
                field_pattern="*email*",
                regex_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            ),
            QualityRule(
                name="phone_format",
                dimension=QualityDimension.VALIDITY,
                description="Phone fields must have valid format",
                severity=QualitySeverity.MEDIUM,
                field_pattern="*phone*",
                regex_pattern=r'^[\+]?[1-9]?[\d\s\-\(\)]{7,15}$'
            ),
            QualityRule(
                name="url_format",
                dimension=QualityDimension.VALIDITY,
                description="URL fields must have valid format",
                severity=QualitySeverity.MEDIUM,
                field_pattern="*url*",
                regex_pattern=r'^https?:\/\/[^\s/$.?#].[^\s]*$'
            ),
            QualityRule(
                name="date_format",
                dimension=QualityDimension.VALIDITY,
                description="Date fields must have valid format",
                severity=QualitySeverity.HIGH,
                field_pattern="*date*",
                validation_func=self._validate_date_format
            )
        ])
        
        # Consistency rules
        self.quality_rules.extend([
            QualityRule(
                name="consistent_data_type",
                dimension=QualityDimension.CONSISTENCY,
                description="Fields should have consistent data types",
                severity=QualitySeverity.MEDIUM
            ),
            QualityRule(
                name="consistent_format",
                dimension=QualityDimension.CONSISTENCY,
                description="Similar fields should have consistent formats",
                severity=QualitySeverity.LOW
            )
        ])
        
        # Length validation rules
        self.quality_rules.extend([
            QualityRule(
                name="reasonable_string_length",
                dimension=QualityDimension.VALIDITY,
                description="String fields should have reasonable length",
                severity=QualitySeverity.LOW,
                min_length=1,
                max_length=10000
            ),
            QualityRule(
                name="title_length",
                dimension=QualityDimension.VALIDITY,
                description="Title fields should have reasonable length",
                severity=QualitySeverity.MEDIUM,
                field_pattern="*title*",
                min_length=3,
                max_length=200
            ),
            QualityRule(
                name="name_length",
                dimension=QualityDimension.VALIDITY,
                description="Name fields should have reasonable length",
                severity=QualitySeverity.MEDIUM,
                field_pattern="*name*",
                min_length=2,
                max_length=100
            )
        ])
    
    def add_custom_rule(self, rule: QualityRule):
        """Add a custom quality rule"""
        self.quality_rules.append(rule)
        logger.info(f"Added custom quality rule: {rule.name}")
    
    def add_template_specific_rules(self, template_id: int, rules: List[QualityRule]):
        """Add template-specific quality rules"""
        self.template_rules_cache[template_id] = rules
        logger.info(f"Added {len(rules)} template-specific rules for template {template_id}")
    
    async def assess_quality(self, template_id: Optional[int] = None, limit: int = 1000) -> QualityReport:
        """Perform comprehensive quality assessment"""
        
        # Get extraction data
        if template_id:
            query = """
            SELECT e.id, e.data, e.created_at, t.name as template_name, t.fields
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.template_id = %s AND e.status = 'completed'
            ORDER BY e.created_at DESC
            LIMIT %s
            """
            params = (template_id, limit)
        else:
            # Assess quality across all templates
            query = """
            SELECT e.id, e.data, e.created_at, t.name as template_name, t.fields, e.template_id
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.status = 'completed'
            ORDER BY e.created_at DESC
            LIMIT %s
            """
            params = (limit,)
        
        extractions = await self.db_manager.fetch_all(query, params)
        
        if not extractions:
            return QualityReport(
                template_id=template_id,
                template_name="No data",
                assessment_date=datetime.utcnow(),
                total_records=0,
                records_analyzed=0,
                quality_scores={dim: 0.0 for dim in QualityDimension},
                overall_quality_score=0.0,
                field_metrics={},
                issues=[],
                rule_violations={},
                recommendations=["No data available for quality assessment"]
            )
        
        # Get template information
        template_name = extractions[0]['template_name']
        if not template_id and 'template_id' in extractions[0]:
            template_id = extractions[0]['template_id']
        
        # Collect field information from template
        expected_fields = set()
        if extractions[0].get('fields'):
            fields_config = extractions[0]['fields']
            if isinstance(fields_config, dict):
                expected_fields.update(fields_config.keys())
        
        # Get applicable rules
        applicable_rules = self._get_applicable_rules(template_id)
        
        # Perform quality assessment
        quality_metrics = self._initialize_quality_metrics(expected_fields)
        issues = []
        
        for extraction in extractions:
            record_id = str(extraction['id'])
            data = extraction.get('data', {})
            
            if not isinstance(data, dict):
                continue
            
            # Assess each field
            for field_name, value in data.items():
                field_issues = self._assess_field_quality(
                    field_name, value, applicable_rules, record_id
                )
                issues.extend(field_issues)
                
                # Update field metrics
                self._update_field_metrics(quality_metrics['field_metrics'], field_name, value, field_issues)
            
            # Check for missing required fields
            for field_name in expected_fields:
                if field_name not in data:
                    issues.append(QualityIssue(
                        rule_name="required_field_present",
                        dimension=QualityDimension.COMPLETENESS,
                        severity=QualitySeverity.CRITICAL,
                        field_name=field_name,
                        description=f"Required field '{field_name}' is missing",
                        value=None,
                        record_id=record_id
                    ))
        
        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(quality_metrics, issues, len(extractions))
        overall_score = self._calculate_overall_score(quality_scores)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(quality_scores, issues, quality_metrics)
        
        # Count rule violations
        rule_violations = Counter(issue.rule_name for issue in issues)
        
        # Record metrics
        await self._record_quality_metrics(template_id, quality_scores, overall_score)
        
        return QualityReport(
            template_id=template_id,
            template_name=template_name,
            assessment_date=datetime.utcnow(),
            total_records=len(extractions),
            records_analyzed=len(extractions),
            quality_scores=quality_scores,
            overall_quality_score=overall_score,
            field_metrics=quality_metrics['field_metrics'],
            issues=issues,
            rule_violations=dict(rule_violations),
            recommendations=recommendations,
            metadata={
                'rules_applied': len(applicable_rules),
                'expected_fields': list(expected_fields)
            }
        )
    
    def _get_applicable_rules(self, template_id: Optional[int]) -> List[QualityRule]:
        """Get applicable quality rules for a template"""
        rules = self.quality_rules.copy()
        
        # Add template-specific rules
        if template_id and template_id in self.template_rules_cache:
            rules.extend(self.template_rules_cache[template_id])
        
        return rules
    
    def _initialize_quality_metrics(self, expected_fields: Set[str]) -> Dict[str, Any]:
        """Initialize quality metrics structure"""
        return {
            'field_metrics': {
                field: {
                    'total_values': 0,
                    'null_count': 0,
                    'empty_count': 0,
                    'valid_count': 0,
                    'invalid_count': 0,
                    'data_types': defaultdict(int),
                    'length_stats': [],
                    'unique_values': set(),
                    'issues_count': 0
                }
                for field in expected_fields
            },
            'dimension_metrics': {
                dim: {
                    'total_checks': 0,
                    'passed_checks': 0,
                    'failed_checks': 0,
                    'critical_failures': 0
                }
                for dim in QualityDimension
            }
        }
    
    def _assess_field_quality(self, field_name: str, value: Any, rules: List[QualityRule], record_id: str) -> List[QualityIssue]:
        """Assess quality of a single field value"""
        issues = []
        
        for rule in rules:
            # Check if rule applies to this field
            if not self._rule_applies_to_field(rule, field_name):
                continue
            
            issue = self._apply_quality_rule(rule, field_name, value, record_id)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _rule_applies_to_field(self, rule: QualityRule, field_name: str) -> bool:
        """Check if a rule applies to a specific field"""
        if rule.field_pattern == "*":
            return True
        
        # Simple glob pattern matching
        pattern = rule.field_pattern.lower()
        field_lower = field_name.lower()
        
        if pattern.startswith("*") and pattern.endswith("*"):
            # Contains pattern
            return pattern[1:-1] in field_lower
        elif pattern.startswith("*"):
            # Ends with pattern
            return field_lower.endswith(pattern[1:])
        elif pattern.endswith("*"):
            # Starts with pattern
            return field_lower.startswith(pattern[:-1])
        else:
            # Exact match
            return pattern == field_lower
    
    def _apply_quality_rule(self, rule: QualityRule, field_name: str, value: Any, record_id: str) -> Optional[QualityIssue]:
        """Apply a quality rule to a field value"""
        
        # Handle null values
        if value is None:
            if rule.required:
                return QualityIssue(
                    rule_name=rule.name,
                    dimension=rule.dimension,
                    severity=rule.severity,
                    field_name=field_name,
                    description=f"Required field '{field_name}' is null",
                    value=value,
                    record_id=record_id
                )
            return None
        
        # Custom validation function
        if rule.validation_func:
            try:
                if not rule.validation_func(value):
                    return QualityIssue(
                        rule_name=rule.name,
                        dimension=rule.dimension,
                        severity=rule.severity,
                        field_name=field_name,
                        description=f"Field '{field_name}' failed validation: {rule.description}",
                        value=value,
                        record_id=record_id
                    )
            except Exception as e:
                logger.warning(f"Validation function error for rule {rule.name}: {e}")
        
        # Regex pattern validation
        if rule.regex_pattern and isinstance(value, str):
            if not re.match(rule.regex_pattern, value):
                return QualityIssue(
                    rule_name=rule.name,
                    dimension=rule.dimension,
                    severity=rule.severity,
                    field_name=field_name,
                    description=f"Field '{field_name}' does not match expected pattern",
                    value=value,
                    record_id=record_id
                )
        
        # Length validation
        if isinstance(value, str):
            length = len(value)
            if rule.min_length and length < rule.min_length:
                return QualityIssue(
                    rule_name=rule.name,
                    dimension=rule.dimension,
                    severity=rule.severity,
                    field_name=field_name,
                    description=f"Field '{field_name}' is too short (min: {rule.min_length})",
                    value=value,
                    record_id=record_id
                )
            if rule.max_length and length > rule.max_length:
                return QualityIssue(
                    rule_name=rule.name,
                    dimension=rule.dimension,
                    severity=rule.severity,
                    field_name=field_name,
                    description=f"Field '{field_name}' is too long (max: {rule.max_length})",
                    value=value,
                    record_id=record_id
                )
        
        # Expected values validation
        if rule.expected_values and value not in rule.expected_values:
            return QualityIssue(
                rule_name=rule.name,
                dimension=rule.dimension,
                severity=rule.severity,
                field_name=field_name,
                description=f"Field '{field_name}' has unexpected value",
                value=value,
                record_id=record_id
            )
        
        return None
    
    def _update_field_metrics(self, field_metrics: Dict[str, Dict], field_name: str, value: Any, issues: List[QualityIssue]):
        """Update field-level quality metrics"""
        
        # Initialize field metrics if not exists
        if field_name not in field_metrics:
            field_metrics[field_name] = {
                'total_values': 0,
                'null_count': 0,
                'empty_count': 0,
                'valid_count': 0,
                'invalid_count': 0,
                'data_types': defaultdict(int),
                'length_stats': [],
                'unique_values': set(),
                'issues_count': 0
            }
        
        metrics = field_metrics[field_name]
        metrics['total_values'] += 1
        
        # Handle null values
        if value is None:
            metrics['null_count'] += 1
            return
        
        # Handle empty strings
        if isinstance(value, str) and value.strip() == '':
            metrics['empty_count'] += 1
        
        # Track data types
        metrics['data_types'][type(value).__name__] += 1
        
        # Track string lengths
        if isinstance(value, str):
            metrics['length_stats'].append(len(value))
        
        # Track unique values (up to a limit)
        if len(metrics['unique_values']) < 1000:
            metrics['unique_values'].add(str(value)[:100])  # Truncate long values
        
        # Count issues
        metrics['issues_count'] += len(issues)
        
        # Determine if value is valid
        if issues:
            metrics['invalid_count'] += 1
        else:
            metrics['valid_count'] += 1
    
    def _calculate_quality_scores(self, quality_metrics: Dict, issues: List[QualityIssue], total_records: int) -> Dict[QualityDimension, float]:
        """Calculate quality scores by dimension"""
        
        scores = {}
        
        # Group issues by dimension
        issues_by_dimension = defaultdict(list)
        for issue in issues:
            issues_by_dimension[issue.dimension].append(issue)
        
        for dimension in QualityDimension:
            dimension_issues = issues_by_dimension[dimension]
            
            if dimension == QualityDimension.COMPLETENESS:
                # Calculate completeness based on null/empty values
                total_values = sum(
                    metrics['total_values'] 
                    for metrics in quality_metrics['field_metrics'].values()
                )
                missing_values = sum(
                    metrics['null_count'] + metrics['empty_count']
                    for metrics in quality_metrics['field_metrics'].values()
                )
                
                if total_values > 0:
                    completeness = ((total_values - missing_values) / total_values) * 100
                else:
                    completeness = 100.0
                
                scores[dimension] = max(0.0, completeness)
            
            elif dimension == QualityDimension.VALIDITY:
                # Calculate validity based on validation failures
                total_values = sum(
                    metrics['total_values'] 
                    for metrics in quality_metrics['field_metrics'].values()
                )
                invalid_values = sum(
                    metrics['invalid_count']
                    for metrics in quality_metrics['field_metrics'].values()
                )
                
                if total_values > 0:
                    validity = ((total_values - invalid_values) / total_values) * 100
                else:
                    validity = 100.0
                
                scores[dimension] = max(0.0, validity)
            
            elif dimension == QualityDimension.CONSISTENCY:
                # Calculate consistency based on data type consistency
                consistency_scores = []
                
                for field_metrics in quality_metrics['field_metrics'].values():
                    if field_metrics['total_values'] > 0:
                        # Find dominant data type
                        type_counts = field_metrics['data_types']
                        if type_counts:
                            max_count = max(type_counts.values())
                            consistency = (max_count / field_metrics['total_values']) * 100
                            consistency_scores.append(consistency)
                
                if consistency_scores:
                    avg_consistency = sum(consistency_scores) / len(consistency_scores)
                else:
                    avg_consistency = 100.0
                
                scores[dimension] = max(0.0, avg_consistency)
            
            elif dimension == QualityDimension.UNIQUENESS:
                # Calculate uniqueness based on unique value ratios
                uniqueness_scores = []
                
                for field_metrics in quality_metrics['field_metrics'].values():
                    if field_metrics['total_values'] > 0:
                        unique_count = len(field_metrics['unique_values'])
                        # Cap uniqueness at 100% (can't have more unique values than total)
                        uniqueness = min(100.0, (unique_count / field_metrics['total_values']) * 100)
                        uniqueness_scores.append(uniqueness)
                
                if uniqueness_scores:
                    avg_uniqueness = sum(uniqueness_scores) / len(uniqueness_scores)
                else:
                    avg_uniqueness = 100.0
                
                scores[dimension] = max(0.0, avg_uniqueness)
            
            else:
                # For other dimensions, calculate based on issue ratio
                if total_records > 0:
                    error_rate = len(dimension_issues) / total_records
                    score = max(0.0, (1 - error_rate) * 100)
                else:
                    score = 100.0
                
                scores[dimension] = score
        
        return scores
    
    def _calculate_overall_score(self, quality_scores: Dict[QualityDimension, float]) -> float:
        """Calculate overall quality score with weighted dimensions"""
        
        # Dimension weights (should sum to 1.0)
        weights = {
            QualityDimension.COMPLETENESS: 0.25,
            QualityDimension.ACCURACY: 0.20,
            QualityDimension.CONSISTENCY: 0.20,
            QualityDimension.VALIDITY: 0.20,
            QualityDimension.UNIQUENESS: 0.10,
            QualityDimension.TIMELINESS: 0.05
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for dimension, score in quality_scores.items():
            weight = weights.get(dimension, 0.1)
            weighted_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return 0.0
    
    def _generate_recommendations(self, quality_scores: Dict[QualityDimension, float], 
                                 issues: List[QualityIssue], 
                                 quality_metrics: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations"""
        
        recommendations = []
        
        # Check each dimension against thresholds
        for dimension, score in quality_scores.items():
            threshold = self.quality_thresholds.get(dimension, 80.0)
            
            if score < threshold:
                if dimension == QualityDimension.COMPLETENESS:
                    recommendations.append(f"Improve data completeness: currently {score:.1f}% (target: {threshold:.1f}%)")
                    recommendations.append("Review extraction selectors for fields with high null rates")
                
                elif dimension == QualityDimension.VALIDITY:
                    recommendations.append(f"Improve data validity: currently {score:.1f}% (target: {threshold:.1f}%)")
                    recommendations.append("Implement stricter validation rules for format-sensitive fields")
                
                elif dimension == QualityDimension.CONSISTENCY:
                    recommendations.append(f"Improve data consistency: currently {score:.1f}% (target: {threshold:.1f}%)")
                    recommendations.append("Standardize data extraction to ensure consistent formats")
                
                elif dimension == QualityDimension.UNIQUENESS:
                    recommendations.append(f"Improve data uniqueness: currently {score:.1f}% (target: {threshold:.1f}%)")
                    recommendations.append("Check for duplicate extraction logic or data sources")
        
        # Analyze common issues
        issue_counts = Counter(issue.rule_name for issue in issues)
        
        if issue_counts:
            most_common_issue = issue_counts.most_common(1)[0]
            recommendations.append(f"Address most common issue: {most_common_issue[0]} ({most_common_issue[1]} occurrences)")
        
        # Field-specific recommendations
        for field_name, metrics in quality_metrics['field_metrics'].items():
            if metrics['total_values'] > 0:
                null_rate = (metrics['null_count'] / metrics['total_values']) * 100
                
                if null_rate > 20:
                    recommendations.append(f"Field '{field_name}' has high null rate ({null_rate:.1f}%)")
        
        return recommendations
    
    def _validate_date_format(self, value: Any) -> bool:
        """Validate date format"""
        if not isinstance(value, str):
            return False
        
        # Try common date formats
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ'
        ]
        
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    async def _record_quality_metrics(self, template_id: Optional[int], 
                                     quality_scores: Dict[QualityDimension, float], 
                                     overall_score: float):
        """Record quality metrics for monitoring"""
        
        try:
            # Record in observability system
            if metrics_collector:
                for dimension, score in quality_scores.items():
                    metrics_collector.record_metric(
                        f"quality_score_{dimension.value}",
                        score,
                        tags={"template_id": str(template_id)} if template_id else {}
                    )
                
                metrics_collector.record_metric(
                    "quality_score_overall",
                    overall_score,
                    tags={"template_id": str(template_id)} if template_id else {}
                )
            
            # Store in local history
            self.quality_history[template_id or 'global'].append({
                'timestamp': datetime.utcnow(),
                'quality_scores': quality_scores,
                'overall_score': overall_score
            })
            
            # Keep only recent history (last 100 entries)
            if len(self.quality_history[template_id or 'global']) > 100:
                self.quality_history[template_id or 'global'] = \
                    self.quality_history[template_id or 'global'][-100:]
        
        except Exception as e:
            logger.warning(f"Failed to record quality metrics: {e}")
    
    async def get_quality_trends(self, template_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """Get quality trends over time"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get historical quality data
        history = self.quality_history.get(template_id or 'global', [])
        recent_history = [
            entry for entry in history 
            if entry['timestamp'] >= cutoff_date
        ]
        
        if len(recent_history) < 2:
            return {
                'trend_available': False,
                'message': 'Insufficient historical data for trend analysis'
            }
        
        # Calculate trends
        trends = {}
        
        # Overall score trend
        overall_scores = [entry['overall_score'] for entry in recent_history]
        trends['overall'] = {
            'current': overall_scores[-1],
            'trend': self._calculate_trend_direction(overall_scores),
            'change_percentage': self._calculate_percentage_change(overall_scores)
        }
        
        # Dimension trends
        for dimension in QualityDimension:
            dimension_scores = [
                entry['quality_scores'].get(dimension, 0) 
                for entry in recent_history
            ]
            
            trends[dimension.value] = {
                'current': dimension_scores[-1],
                'trend': self._calculate_trend_direction(dimension_scores),
                'change_percentage': self._calculate_percentage_change(dimension_scores)
            }
        
        return {
            'trend_available': True,
            'period_days': days,
            'data_points': len(recent_history),
            'trends': trends,
            'recommendations': self._generate_trend_recommendations(trends)
        }
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values"""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 'stable'
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.1:
            return 'improving'
        elif slope < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_percentage_change(self, values: List[float]) -> float:
        """Calculate percentage change from first to last value"""
        if len(values) < 2 or values[0] == 0:
            return 0.0
        
        return ((values[-1] - values[0]) / values[0]) * 100
    
    def _generate_trend_recommendations(self, trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on quality trends"""
        
        recommendations = []
        
        overall_trend = trends.get('overall', {})
        if overall_trend.get('trend') == 'declining':
            recommendations.append("Overall quality is declining - review extraction processes")
        
        for dimension_name, trend_data in trends.items():
            if dimension_name == 'overall':
                continue
            
            if trend_data.get('trend') == 'declining':
                recommendations.append(f"{dimension_name.title()} quality is declining - focus improvement efforts")
        
        return recommendations
