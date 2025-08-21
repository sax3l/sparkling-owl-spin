"""
Tests for Quality Checker
=========================

Test suite for the comprehensive data quality assessment engine.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.quality_checker import (
    QualityChecker, QualityReport, QualityRule, QualityIssue,
    QualityDimension, QualitySeverity
)
from src.database.manager import DatabaseManager


class TestQualityChecker:
    """Test cases for QualityChecker class"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager"""
        mock_db = AsyncMock(spec=DatabaseManager)
        return mock_db
    
    @pytest.fixture
    async def quality_checker(self, db_manager):
        """Create QualityChecker instance with mock database"""
        return QualityChecker(db_manager)
    
    @pytest.mark.asyncio
    async def test_assess_quality_success(self, quality_checker, db_manager):
        """Test successful quality assessment"""
        
        # Mock database response
        mock_extractions = []
        for i in range(100):
            data = {
                'title': f'Title {i}',
                'content': f'Content for item {i}',
                'email': f'user{i}@example.com',
                'url': f'https://example.com/item{i}'
            }
            
            # Introduce some quality issues
            if i % 10 == 0:  # 10% null titles
                data['title'] = None
            if i % 15 == 0:  # Some invalid emails
                data['email'] = 'invalid-email'
            if i % 20 == 0:  # Some invalid URLs
                data['url'] = 'not-a-url'
            
            mock_extractions.append({
                'id': i,
                'data': data,
                'created_at': datetime.utcnow() - timedelta(days=1),
                'template_name': 'test_template',
                'fields': {'title': {}, 'content': {}, 'email': {}, 'url': {}}
            })
        
        db_manager.fetch_all.return_value = mock_extractions
        
        # Run quality assessment
        report = await quality_checker.assess_quality(template_id=1)
        
        # Assertions
        assert isinstance(report, QualityReport)
        assert report.template_id == 1
        assert report.template_name == 'test_template'
        assert report.total_records == 100
        assert report.records_analyzed == 100
        
        # Check quality scores
        assert 0 <= report.overall_quality_score <= 100
        for dimension, score in report.quality_scores.items():
            assert isinstance(dimension, QualityDimension)
            assert 0 <= score <= 100
        
        # Should have some issues due to our test data
        assert len(report.issues) > 0
        
        # Should have field metrics
        assert 'title' in report.field_metrics
        assert 'email' in report.field_metrics
        assert 'url' in report.field_metrics
        
        # Should have recommendations
        assert len(report.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_assess_quality_no_data(self, quality_checker, db_manager):
        """Test quality assessment with no data"""
        
        db_manager.fetch_all.return_value = []
        
        # Run quality assessment
        report = await quality_checker.assess_quality(template_id=1)
        
        # Assertions
        assert report.total_records == 0
        assert report.records_analyzed == 0
        assert report.overall_quality_score == 0.0
        assert "No data available" in report.recommendations[0]
    
    def test_add_custom_rule(self, quality_checker):
        """Test adding custom quality rules"""
        
        # Create custom rule
        custom_rule = QualityRule(
            name="custom_test_rule",
            dimension=QualityDimension.VALIDITY,
            description="Test custom rule",
            severity=QualitySeverity.HIGH,
            field_pattern="*test*",
            validation_func=lambda x: isinstance(x, str) and len(x) > 5
        )
        
        initial_count = len(quality_checker.quality_rules)
        quality_checker.add_custom_rule(custom_rule)
        
        # Assertions
        assert len(quality_checker.quality_rules) == initial_count + 1
        assert custom_rule in quality_checker.quality_rules
    
    def test_add_template_specific_rules(self, quality_checker):
        """Test adding template-specific rules"""
        
        template_id = 123
        template_rules = [
            QualityRule(
                name="template_specific_rule",
                dimension=QualityDimension.COMPLETENESS,
                description="Template specific rule",
                severity=QualitySeverity.CRITICAL,
                required=True
            )
        ]
        
        quality_checker.add_template_specific_rules(template_id, template_rules)
        
        # Assertions
        assert template_id in quality_checker.template_rules_cache
        assert quality_checker.template_rules_cache[template_id] == template_rules
    
    def test_rule_applies_to_field(self, quality_checker):
        """Test rule field pattern matching"""
        
        # Test wildcard pattern
        rule_wildcard = QualityRule(
            name="wildcard_rule",
            dimension=QualityDimension.VALIDITY,
            description="Wildcard rule",
            severity=QualitySeverity.LOW,
            field_pattern="*"
        )
        
        assert quality_checker._rule_applies_to_field(rule_wildcard, "any_field")
        
        # Test contains pattern
        rule_contains = QualityRule(
            name="contains_rule",
            dimension=QualityDimension.VALIDITY,
            description="Contains rule",
            severity=QualitySeverity.LOW,
            field_pattern="*email*"
        )
        
        assert quality_checker._rule_applies_to_field(rule_contains, "user_email")
        assert quality_checker._rule_applies_to_field(rule_contains, "email_address")
        assert not quality_checker._rule_applies_to_field(rule_contains, "phone_number")
        
        # Test starts with pattern
        rule_starts = QualityRule(
            name="starts_rule",
            dimension=QualityDimension.VALIDITY,
            description="Starts rule",
            severity=QualitySeverity.LOW,
            field_pattern="user_*"
        )
        
        assert quality_checker._rule_applies_to_field(rule_starts, "user_name")
        assert quality_checker._rule_applies_to_field(rule_starts, "user_email")
        assert not quality_checker._rule_applies_to_field(rule_starts, "admin_name")
    
    def test_apply_quality_rule(self, quality_checker):
        """Test applying individual quality rules"""
        
        # Test required field rule
        required_rule = QualityRule(
            name="required_field",
            dimension=QualityDimension.COMPLETENESS,
            description="Field is required",
            severity=QualitySeverity.CRITICAL,
            required=True
        )
        
        # Test with null value
        issue = quality_checker._apply_quality_rule(
            required_rule, "title", None, "record_1"
        )
        assert issue is not None
        assert issue.severity == QualitySeverity.CRITICAL
        assert "is null" in issue.description
        
        # Test with valid value
        issue = quality_checker._apply_quality_rule(
            required_rule, "title", "Valid Title", "record_1"
        )
        assert issue is None
        
        # Test regex pattern rule
        email_rule = QualityRule(
            name="email_format",
            dimension=QualityDimension.VALIDITY,
            description="Email format validation",
            severity=QualitySeverity.HIGH,
            regex_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Test with invalid email
        issue = quality_checker._apply_quality_rule(
            email_rule, "email", "invalid-email", "record_1"
        )
        assert issue is not None
        assert issue.severity == QualitySeverity.HIGH
        
        # Test with valid email
        issue = quality_checker._apply_quality_rule(
            email_rule, "email", "user@example.com", "record_1"
        )
        assert issue is None
        
        # Test length validation rule
        length_rule = QualityRule(
            name="title_length",
            dimension=QualityDimension.VALIDITY,
            description="Title length validation",
            severity=QualitySeverity.MEDIUM,
            min_length=3,
            max_length=100
        )
        
        # Test too short
        issue = quality_checker._apply_quality_rule(
            length_rule, "title", "Hi", "record_1"
        )
        assert issue is not None
        assert "too short" in issue.description
        
        # Test too long
        long_title = "A" * 150
        issue = quality_checker._apply_quality_rule(
            length_rule, "title", long_title, "record_1"
        )
        assert issue is not None
        assert "too long" in issue.description
        
        # Test valid length
        issue = quality_checker._apply_quality_rule(
            length_rule, "title", "Valid Title", "record_1"
        )
        assert issue is None
    
    def test_validate_date_format(self, quality_checker):
        """Test date format validation"""
        
        # Test valid date formats
        valid_dates = [
            "2023-01-01",
            "2023-01-01 12:30:45",
            "01/01/2023",
            "2023-01-01T12:30:45",
            "2023-01-01T12:30:45Z"
        ]
        
        for date_str in valid_dates:
            assert quality_checker._validate_date_format(date_str), f"Failed for {date_str}"
        
        # Test invalid date formats
        invalid_dates = [
            "not-a-date",
            "2023-13-01",  # Invalid month
            "2023-01-32",  # Invalid day
            "123",
            "",
            None
        ]
        
        for date_str in invalid_dates:
            assert not quality_checker._validate_date_format(date_str), f"Should fail for {date_str}"
    
    def test_calculate_quality_scores(self, quality_checker):
        """Test quality score calculation"""
        
        # Create mock quality metrics
        quality_metrics = {
            'field_metrics': {
                'title': {
                    'total_values': 100,
                    'null_count': 10,
                    'empty_count': 5,
                    'valid_count': 85,
                    'invalid_count': 15,
                    'data_types': {'str': 90, 'NoneType': 10},
                    'unique_values': set(f'title_{i}' for i in range(80))
                },
                'email': {
                    'total_values': 100,
                    'null_count': 5,
                    'empty_count': 0,
                    'valid_count': 90,
                    'invalid_count': 10,
                    'data_types': {'str': 95, 'NoneType': 5},
                    'unique_values': set(f'email_{i}@example.com' for i in range(95))
                }
            }
        }
        
        # Create some issues
        issues = [
            QualityIssue(
                rule_name="test_rule",
                dimension=QualityDimension.COMPLETENESS,
                severity=QualitySeverity.HIGH,
                field_name="title",
                description="Test issue",
                value=None
            )
        ] * 15  # 15 completeness issues
        
        scores = quality_checker._calculate_quality_scores(quality_metrics, issues, 100)
        
        # Assertions
        assert QualityDimension.COMPLETENESS in scores
        assert QualityDimension.VALIDITY in scores
        assert QualityDimension.CONSISTENCY in scores
        assert QualityDimension.UNIQUENESS in scores
        
        # All scores should be between 0 and 100
        for score in scores.values():
            assert 0 <= score <= 100
        
        # Completeness should reflect the null/empty values
        completeness_score = scores[QualityDimension.COMPLETENESS]
        expected_completeness = ((200 - 20) / 200) * 100  # Total values - missing values
        assert abs(completeness_score - expected_completeness) < 1
    
    def test_calculate_overall_score(self, quality_checker):
        """Test overall quality score calculation"""
        
        # Test with various dimension scores
        quality_scores = {
            QualityDimension.COMPLETENESS: 90.0,
            QualityDimension.VALIDITY: 85.0,
            QualityDimension.CONSISTENCY: 95.0,
            QualityDimension.UNIQUENESS: 80.0,
            QualityDimension.ACCURACY: 88.0,
            QualityDimension.TIMELINESS: 92.0
        }
        
        overall_score = quality_checker._calculate_overall_score(quality_scores)
        
        # Should be weighted average
        assert 0 <= overall_score <= 100
        assert 80 <= overall_score <= 95  # Should be in reasonable range
    
    @pytest.mark.asyncio
    async def test_get_quality_trends(self, quality_checker):
        """Test quality trends analysis"""
        
        # Populate quality history
        template_id = 1
        base_date = datetime.utcnow()
        
        for i in range(10):
            quality_checker.quality_history[template_id].append({
                'timestamp': base_date - timedelta(days=i),
                'quality_scores': {
                    QualityDimension.COMPLETENESS: 90 - i,  # Declining trend
                    QualityDimension.VALIDITY: 85 + i * 0.5   # Improving trend
                },
                'overall_score': 87 - i * 0.3
            })
        
        # Get trends
        trends = await quality_checker.get_quality_trends(template_id, days=30)
        
        # Assertions
        assert trends['trend_available']
        assert 'trends' in trends
        assert 'overall' in trends['trends']
        
        overall_trend = trends['trends']['overall']
        assert 'trend' in overall_trend
        assert 'change_percentage' in overall_trend
        
        # Should detect declining overall trend
        assert overall_trend['trend'] in ['declining', 'stable']
    
    def test_calculate_trend_direction(self, quality_checker):
        """Test trend direction calculation"""
        
        # Test improving trend
        improving_values = [70, 75, 80, 85, 90]
        trend = quality_checker._calculate_trend_direction(improving_values)
        assert trend == 'improving'
        
        # Test declining trend
        declining_values = [90, 85, 80, 75, 70]
        trend = quality_checker._calculate_trend_direction(declining_values)
        assert trend == 'declining'
        
        # Test stable trend
        stable_values = [85, 86, 84, 85, 85]
        trend = quality_checker._calculate_trend_direction(stable_values)
        assert trend == 'stable'
    
    def test_calculate_percentage_change(self, quality_checker):
        """Test percentage change calculation"""
        
        # Test improvement
        values = [80, 85, 90]
        change = quality_checker._calculate_percentage_change(values)
        assert change == 12.5  # (90-80)/80 * 100
        
        # Test degradation
        values = [90, 85, 80]
        change = quality_checker._calculate_percentage_change(values)
        assert change == -11.11  # (80-90)/90 * 100, approximately
        
        # Test no change
        values = [85, 85]
        change = quality_checker._calculate_percentage_change(values)
        assert change == 0.0
    
    def test_generate_trend_recommendations(self, quality_checker):
        """Test trend-based recommendations generation"""
        
        # Mock trends with declining overall quality
        trends = {
            'overall': {'trend': 'declining', 'change_percentage': -15.0},
            'completeness': {'trend': 'declining', 'change_percentage': -10.0},
            'validity': {'trend': 'stable', 'change_percentage': 2.0}
        }
        
        recommendations = quality_checker._generate_trend_recommendations(trends)
        
        # Should generate recommendations for declining trends
        assert len(recommendations) > 0
        assert any('declining' in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_record_quality_metrics(self, quality_checker):
        """Test quality metrics recording"""
        
        template_id = 1
        quality_scores = {
            QualityDimension.COMPLETENESS: 85.0,
            QualityDimension.VALIDITY: 90.0
        }
        overall_score = 87.5
        
        # This should not raise an exception
        await quality_checker._record_quality_metrics(template_id, quality_scores, overall_score)
        
        # Check if recorded in local history
        assert template_id in quality_checker.quality_history
        history = quality_checker.quality_history[template_id]
        assert len(history) > 0
        
        latest_entry = history[-1]
        assert latest_entry['overall_score'] == overall_score
        assert latest_entry['quality_scores'] == quality_scores
    
    def test_quality_thresholds_configuration(self, quality_checker):
        """Test quality thresholds configuration"""
        
        # Test default thresholds
        assert QualityDimension.COMPLETENESS in quality_checker.quality_thresholds
        assert QualityDimension.VALIDITY in quality_checker.quality_thresholds
        
        # All thresholds should be reasonable values
        for threshold in quality_checker.quality_thresholds.values():
            assert 0 <= threshold <= 100
    
    def test_default_rules_initialization(self, quality_checker):
        """Test that default quality rules are properly initialized"""
        
        # Should have default rules
        assert len(quality_checker.quality_rules) > 0
        
        # Check for expected rule types
        rule_names = [rule.name for rule in quality_checker.quality_rules]
        
        expected_rules = [
            'required_field_present',
            'non_empty_string',
            'email_format',
            'phone_format',
            'url_format',
            'date_format'
        ]
        
        for expected_rule in expected_rules:
            assert expected_rule in rule_names


if __name__ == '__main__':
    pytest.main([__file__])
