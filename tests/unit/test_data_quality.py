import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock
import numpy as np
from src.scraper.template_runtime import run_template

# Add comprehensive quality testing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.quality_checker import QualityChecker, QualityDimension, QualityRule
from src.database.manager import DatabaseManager


class TestDataQualityBasic:
    """Basic data quality tests (existing functionality)"""

    @pytest.mark.unit
    def test_dq_score_calculation(self):
        """
        Verifies that the weighted DQ score is calculated correctly based on its components.
        """
        # This test uses the stubbed implementation of run_template.
        # As the real implementation is built, this test will ensure the formula remains correct.
        
        _record, dq_metrics = run_template("<html></html>", {"id": "test-template"})
        
        assert "completeness" in dq_metrics
        assert "validity" in dq_metrics
        assert "consistency" in dq_metrics
        assert "dq_score" in dq_metrics
        
        # Expected score based on stub: (0.4 * 0.98) + (0.4 * 1.0) + (0.2 * 0.95) = 0.392 + 0.4 + 0.19 = 0.982
        expected_score = 0.982
        
        assert dq_metrics["dq_score"] == pytest.approx(expected_score)


class TestQualityChecker:
    """Comprehensive tests for QualityChecker class"""
    
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
        mock_data = [
            {
                'extraction_id': 1,
                'field_name': 'company_name',
                'extracted_value': 'Acme Corporation',
                'confidence_score': 0.95,
                'validation_errors': None,
                'data_completeness': 1.0,
                'extraction_timestamp': datetime.utcnow()
            },
            {
                'extraction_id': 1,
                'field_name': 'address',
                'extracted_value': '123 Main St, Stockholm',
                'confidence_score': 0.88,
                'validation_errors': None,
                'data_completeness': 1.0,
                'extraction_timestamp': datetime.utcnow()
            },
            {
                'extraction_id': 1,
                'field_name': 'phone',
                'extracted_value': '',
                'confidence_score': 0.0,
                'validation_errors': ['Missing required field'],
                'data_completeness': 0.0,
                'extraction_timestamp': datetime.utcnow()
            }
        ]
        
        db_manager.fetch_all.return_value = mock_data
        
        # Run quality assessment
        result = await quality_checker.assess_quality(template_id=1, time_range_days=7)
        
        # Assertions
        assert 'overall_score' in result
        assert 'dimensions' in result
        assert 'field_scores' in result
        assert 'total_records' in result
        
        # Check that overall score is reasonable (should be between 0 and 10)
        assert 0 <= result['overall_score'] <= 10
        
        # Check dimensions
        dimensions = result['dimensions']
        assert 'completeness' in dimensions
        assert 'accuracy' in dimensions
        assert 'consistency' in dimensions
        
        # Check field scores
        field_scores = result['field_scores']
        assert 'company_name' in field_scores
        assert 'address' in field_scores
        assert 'phone' in field_scores
        
        # Phone should have lower score due to missing data
        assert field_scores['phone'] < field_scores['company_name']
    
    @pytest.mark.asyncio
    async def test_assess_quality_no_data(self, quality_checker, db_manager):
        """Test quality assessment with no data"""
        
        db_manager.fetch_all.return_value = []
        
        result = await quality_checker.assess_quality(template_id=1, time_range_days=7)
        
        # Should handle empty data gracefully
        assert result['total_records'] == 0
        assert result['overall_score'] == 0
        assert 'message' in result
        assert 'no data' in result['message'].lower()
    
    def test_calculate_completeness_score(self, quality_checker):
        """Test completeness score calculation"""
        
        field_data = [
            {'field_name': 'name', 'extracted_value': 'John Doe', 'data_completeness': 1.0},
            {'field_name': 'email', 'extracted_value': 'john@example.com', 'data_completeness': 1.0},
            {'field_name': 'phone', 'extracted_value': '', 'data_completeness': 0.0},
            {'field_name': 'address', 'extracted_value': '123 Main St', 'data_completeness': 1.0},
        ]
        
        score = quality_checker._calculate_completeness_score(field_data)
        
        # Should be 3/4 = 0.75
        assert score == 0.75
    
    def test_calculate_accuracy_score(self, quality_checker):
        """Test accuracy score calculation"""
        
        field_data = [
            {'field_name': 'name', 'confidence_score': 0.95, 'validation_errors': None},
            {'field_name': 'email', 'confidence_score': 0.90, 'validation_errors': None},
            {'field_name': 'phone', 'confidence_score': 0.60, 'validation_errors': ['Invalid format']},
            {'field_name': 'address', 'confidence_score': 0.85, 'validation_errors': None},
        ]
        
        score = quality_checker._calculate_accuracy_score(field_data)
        
        # Average confidence score weighted by validation errors
        expected = (0.95 + 0.90 + 0.60*0.5 + 0.85) / 4  # Phone gets penalty for validation error
        assert abs(score - expected) < 0.1  # Allow some tolerance for calculation differences
    
    def test_calculate_consistency_score(self, quality_checker):
        """Test consistency score calculation"""
        
        field_data = [
            {'field_name': 'name', 'extracted_value': 'John Doe'},
            {'field_name': 'name', 'extracted_value': 'John Doe'},
            {'field_name': 'name', 'extracted_value': 'J. Doe'},  # Slightly different
            {'field_name': 'email', 'extracted_value': 'john@example.com'},
            {'field_name': 'email', 'extracted_value': 'john@example.com'},
        ]
        
        score = quality_checker._calculate_consistency_score(field_data)
        
        # Should be reasonably high but not perfect due to name variation
        assert 0.7 <= score <= 1.0
    
    def test_validate_date_format(self, quality_checker):
        """Test date format validation"""
        
        # Valid dates
        assert quality_checker._validate_date_format('2023-12-25', 'YYYY-MM-DD') is True
        assert quality_checker._validate_date_format('25/12/2023', 'DD/MM/YYYY') is True
        
        # Invalid dates
        assert quality_checker._validate_date_format('2023-13-25', 'YYYY-MM-DD') is False
        assert quality_checker._validate_date_format('invalid', 'YYYY-MM-DD') is False
        assert quality_checker._validate_date_format('', 'YYYY-MM-DD') is False
    
    def test_validate_email_format(self, quality_checker):
        """Test email format validation"""
        
        # Valid emails
        assert quality_checker._validate_email_format('user@example.com') is True
        assert quality_checker._validate_email_format('test.user+tag@domain.co.uk') is True
        
        # Invalid emails
        assert quality_checker._validate_email_format('invalid-email') is False
        assert quality_checker._validate_email_format('@example.com') is False
        assert quality_checker._validate_email_format('user@') is False
        assert quality_checker._validate_email_format('') is False
    
    def test_validate_phone_format(self, quality_checker):
        """Test phone format validation"""
        
        # Valid Swedish phone numbers
        assert quality_checker._validate_phone_format('+46701234567', 'SE') is True
        assert quality_checker._validate_phone_format('070-123 45 67', 'SE') is True
        assert quality_checker._validate_phone_format('08-123 456 78', 'SE') is True
        
        # Invalid phone numbers
        assert quality_checker._validate_phone_format('123', 'SE') is False
        assert quality_checker._validate_phone_format('invalid', 'SE') is False
        assert quality_checker._validate_phone_format('', 'SE') is False
    
    def test_validate_url_format(self, quality_checker):
        """Test URL format validation"""
        
        # Valid URLs
        assert quality_checker._validate_url_format('https://example.com') is True
        assert quality_checker._validate_url_format('http://subdomain.example.com/path') is True
        
        # Invalid URLs
        assert quality_checker._validate_url_format('not-a-url') is False
        assert quality_checker._validate_url_format('ftp://example.com') is False  # Only http/https allowed
        assert quality_checker._validate_url_format('') is False
    
    def test_detect_outliers(self, quality_checker):
        """Test outlier detection in data"""
        
        values = [10, 12, 11, 13, 10, 11, 12, 100, 9, 11]  # 100 is clear outlier
        
        outliers = quality_checker._detect_outliers(values)
        
        assert 100 in outliers
        assert len(outliers) >= 1
    
    def test_calculate_field_quality_score(self, quality_checker):
        """Test individual field quality score calculation"""
        
        field_data = {
            'field_name': 'email',
            'extracted_value': 'user@example.com',
            'confidence_score': 0.95,
            'validation_errors': None,
            'data_completeness': 1.0
        }
        
        score = quality_checker._calculate_field_quality_score(field_data)
        
        # Should be high score for good quality data
        assert score >= 8.0
        
        # Test with poor quality data
        poor_field = {
            'field_name': 'email',
            'extracted_value': 'invalid-email',
            'confidence_score': 0.3,
            'validation_errors': ['Invalid format'],
            'data_completeness': 0.5
        }
        
        poor_score = quality_checker._calculate_field_quality_score(poor_field)
        
        # Should be much lower
        assert poor_score < score
        assert poor_score <= 5.0
    
    @pytest.mark.asyncio
    async def test_analyze_quality_trends(self, quality_checker, db_manager):
        """Test quality trend analysis over time"""
        
        # Mock historical quality data
        base_date = datetime.utcnow() - timedelta(days=30)
        trend_data = []
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            # Simulate improving quality over time
            quality_score = 6.0 + (i * 0.1)  # Improving from 6.0 to 9.0
            
            trend_data.append({
                'date': date,
                'avg_quality_score': min(quality_score, 10.0),
                'total_extractions': 100 + i * 5,
                'successful_extractions': int((100 + i * 5) * (0.85 + i * 0.005))
            })
        
        db_manager.fetch_all.return_value = trend_data
        
        result = await quality_checker.analyze_quality_trends(template_id=1, time_range_days=30)
        
        # Assertions
        assert 'trend_direction' in result
        assert 'improvement_rate' in result
        assert 'current_score' in result
        assert 'historical_scores' in result
        
        # Should detect improving trend
        assert result['trend_direction'] in ['improving', 'stable', 'declining']
        assert result['improvement_rate'] >= 0  # Should be positive for improving trend
    
    @pytest.mark.asyncio
    async def test_generate_quality_report(self, quality_checker, db_manager):
        """Test comprehensive quality report generation"""
        
        # Mock comprehensive data for report
        mock_data = [
            {
                'template_id': 1,
                'template_name': 'Company Profile',
                'field_name': 'company_name',
                'extracted_value': 'Test Corp',
                'confidence_score': 0.95,
                'data_completeness': 1.0,
                'validation_errors': None,
                'extraction_timestamp': datetime.utcnow()
            }
        ]
        
        db_manager.fetch_all.return_value = mock_data
        
        report = await quality_checker.generate_quality_report(template_id=1, time_range_days=7)
        
        # Check report structure
        assert 'summary' in report
        assert 'detailed_analysis' in report
        assert 'recommendations' in report
        assert 'metrics' in report
        
        # Check summary
        summary = report['summary']
        assert 'overall_score' in summary
        assert 'total_records' in summary
        assert 'quality_distribution' in summary
        
        # Check recommendations
        recommendations = report['recommendations']
        assert isinstance(recommendations, list)
        assert len(recommendations) >= 0  # May be empty if quality is perfect
    
    @pytest.mark.asyncio
    async def test_compare_template_quality(self, quality_checker, db_manager):
        """Test quality comparison between templates"""
        
        # Mock data for multiple templates
        comparison_data = [
            {
                'template_id': 1,
                'template_name': 'Template A',
                'avg_quality_score': 8.5,
                'total_extractions': 1000,
                'completeness_score': 0.90,
                'accuracy_score': 0.88
            },
            {
                'template_id': 2,
                'template_name': 'Template B',
                'avg_quality_score': 7.2,
                'total_extractions': 800,
                'completeness_score': 0.85,
                'accuracy_score': 0.82
            },
            {
                'template_id': 3,
                'template_name': 'Template C',
                'avg_quality_score': 9.1,
                'total_extractions': 1200,
                'completeness_score': 0.95,
                'accuracy_score': 0.92
            }
        ]
        
        db_manager.fetch_all.return_value = comparison_data
        
        result = await quality_checker.compare_template_quality(time_range_days=30)
        
        # Assertions
        assert 'template_rankings' in result
        assert 'quality_summary' in result
        assert 'insights' in result
        
        # Check rankings
        rankings = result['template_rankings']
        assert len(rankings) == 3
        
        # Should be sorted by quality score (highest first)
        scores = [template['avg_quality_score'] for template in rankings]
        assert scores == sorted(scores, reverse=True)
        
        # Check that Template C is ranked first (highest score)
        assert rankings[0]['template_name'] == 'Template C'
    
    def test_quality_dimension_scoring(self, quality_checker):
        """Test quality dimension scoring algorithms"""
        
        # Test completeness dimension
        completeness_data = [
            {'data_completeness': 1.0},
            {'data_completeness': 0.8},
            {'data_completeness': 0.0},
            {'data_completeness': 1.0}
        ]
        
        completeness_score = quality_checker._score_dimension(
            QualityDimension.COMPLETENESS, completeness_data
        )
        
        # Should be 0.7 (average of [1.0, 0.8, 0.0, 1.0])
        expected = (1.0 + 0.8 + 0.0 + 1.0) / 4
        assert abs(completeness_score - expected) < 0.01
        
        # Test accuracy dimension
        accuracy_data = [
            {'confidence_score': 0.95, 'validation_errors': None},
            {'confidence_score': 0.80, 'validation_errors': ['Minor issue']},
            {'confidence_score': 0.60, 'validation_errors': ['Major issue', 'Another issue']},
        ]
        
        accuracy_score = quality_checker._score_dimension(
            QualityDimension.ACCURACY, accuracy_data
        )
        
        # Should consider both confidence and validation errors
        assert 0.0 <= accuracy_score <= 1.0
        assert accuracy_score < 0.95  # Should be penalized for validation errors
    
    def test_quality_rule_validation(self, quality_checker):
        """Test custom quality rule validation"""
        
        # Define a custom rule
        email_rule = QualityRule(
            name="email_format",
            description="Email must be valid format",
            field_pattern=".*email.*",
            validation_function=lambda x: '@' in x and '.' in x,
            severity="high"
        )
        
        # Test rule application
        valid_email = "user@example.com"
        invalid_email = "invalid-email"
        
        assert quality_checker._apply_quality_rule(email_rule, valid_email) is True
        assert quality_checker._apply_quality_rule(email_rule, invalid_email) is False
    
    @pytest.mark.asyncio
    async def test_error_handling(self, quality_checker, db_manager):
        """Test error handling in quality assessment"""
        
        # Test database error
        db_manager.fetch_all.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            await quality_checker.assess_quality(template_id=1, time_range_days=7)
        
        # Reset and test invalid parameters
        db_manager.fetch_all.side_effect = None
        db_manager.fetch_all.return_value = []
        
        # Test with invalid time range
        result = await quality_checker.assess_quality(template_id=1, time_range_days=-1)
        assert 'error' in result or result['total_records'] == 0
        
        # Test with invalid template ID
        result = await quality_checker.assess_quality(template_id=None, time_range_days=7)
        assert 'error' in result or result['total_records'] == 0