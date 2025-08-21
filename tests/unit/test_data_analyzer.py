"""
Tests for Data Analyzer
=======================

Test suite for the comprehensive data analysis engine.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import pandas as pd
import numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.data_analyzer import DataAnalyzer, AnalysisResult
from src.database.manager import DatabaseManager


class TestDataAnalyzer:
    """Test cases for DataAnalyzer class"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager"""
        mock_db = AsyncMock(spec=DatabaseManager)
        return mock_db
    
    @pytest.fixture
    async def data_analyzer(self, db_manager):
        """Create DataAnalyzer instance with mock database"""
        return DataAnalyzer(db_manager)
    
    @pytest.mark.asyncio
    async def test_analyze_extraction_patterns_success(self, data_analyzer, db_manager):
        """Test successful extraction patterns analysis"""
        
        # Mock database response
        mock_extractions = [
            {
                'id': 1,
                'template_id': 1,
                'status': 'completed',
                'data': {'title': 'Test', 'content': 'Content'},
                'processing_time': 1.5,
                'created_at': datetime.utcnow() - timedelta(days=1),
                'template_name': 'test_template',
                'template_version': '1.0'
            },
            {
                'id': 2,
                'template_id': 1,
                'status': 'completed',
                'data': {'title': 'Test 2', 'content': 'Content 2'},
                'processing_time': 2.0,
                'created_at': datetime.utcnow(),
                'template_name': 'test_template',
                'template_version': '1.0'
            }
        ] * 10  # Create 20 records
        
        db_manager.fetch_all.return_value = mock_extractions
        
        # Run analysis
        result = await data_analyzer.analyze_extraction_patterns(time_range_days=30)
        
        # Assertions
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "extraction_patterns"
        assert result.data_points == 20
        assert result.confidence_score > 0
        assert len(result.insights) > 0
        assert 'daily_extraction_stats' in result.results
        
        # Verify database call
        db_manager.fetch_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_extraction_patterns_insufficient_data(self, data_analyzer, db_manager):
        """Test analysis with insufficient data"""
        
        # Mock database response with minimal data
        mock_extractions = [
            {
                'id': 1,
                'template_id': 1,
                'status': 'completed',
                'data': {'title': 'Test'},
                'processing_time': 1.5,
                'created_at': datetime.utcnow(),
                'template_name': 'test_template',
                'template_version': '1.0'
            }
        ]
        
        db_manager.fetch_all.return_value = mock_extractions
        
        # Run analysis
        result = await data_analyzer.analyze_extraction_patterns(time_range_days=30)
        
        # Assertions
        assert result.confidence_score == 0.0
        assert "Insufficient data" in result.insights[0]
    
    @pytest.mark.asyncio
    async def test_analyze_data_completeness(self, data_analyzer, db_manager):
        """Test data completeness analysis"""
        
        # Mock database response
        mock_extractions = [
            {
                'template_name': 'test_template',
                'data': {'title': 'Test', 'content': 'Content', 'url': 'http://example.com'},
                'fields': {'title': {}, 'content': {}, 'url': {}, 'description': {}}
            },
            {
                'template_name': 'test_template',
                'data': {'title': 'Test 2', 'content': ''},  # Missing description and url, empty content
                'fields': {'title': {}, 'content': {}, 'url': {}, 'description': {}}
            }
        ] * 10  # Create 20 records
        
        db_manager.fetch_all.return_value = mock_extractions
        
        # Run analysis
        result = await data_analyzer.analyze_data_completeness(template_id=1)
        
        # Assertions
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "data_completeness"
        assert 'test_template' in result.results
        
        template_result = result.results['test_template']
        assert 'average_completeness' in template_result
        assert 'field_completeness_percentages' in template_result
    
    @pytest.mark.asyncio
    async def test_analyze_performance_trends(self, data_analyzer, db_manager):
        """Test performance trends analysis"""
        
        # Mock database response
        base_date = datetime.utcnow() - timedelta(days=10)
        mock_performance_data = []
        
        for i in range(30):
            mock_performance_data.append({
                'date': base_date + timedelta(days=i),
                'avg_processing_time': 1.0 + (i * 0.1),  # Increasing trend
                'extraction_count': 100 + (i * 5),  # Growing volume
                'success_rate': 0.95 - (i * 0.01),  # Declining success rate
                'template_id': 1
            })
        
        db_manager.fetch_all.return_value = mock_performance_data
        
        # Run analysis
        result = await data_analyzer.analyze_performance_trends(time_range_days=30)
        
        # Assertions
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "performance_trends"
        assert 'processing_time' in result.results
        assert 'volume' in result.results
        assert 'success_rate' in result.results
        
        # Check trend detection
        processing_time_trend = result.results['processing_time']
        assert 'trend_slope' in processing_time_trend
        assert processing_time_trend['trend_slope'] > 0  # Should detect increasing trend
    
    @pytest.mark.asyncio
    async def test_analyze_data_quality_metrics(self, data_analyzer, db_manager):
        """Test data quality metrics analysis"""
        
        # Mock database response
        mock_extractions = []
        for i in range(50):
            data = {'title': f'Title {i}', 'content': f'Content {i}'}
            if i % 5 == 0:  # Every 5th record has null content
                data['content'] = None
            if i % 10 == 0:  # Every 10th record has empty title
                data['title'] = ''
            
            mock_extractions.append({
                'template_name': 'test_template',
                'data': data,
                'fields': {'title': {}, 'content': {}}
            })
        
        db_manager.fetch_all.return_value = mock_extractions
        
        # Run analysis
        result = await data_analyzer.analyze_data_quality_metrics(template_id=1)
        
        # Assertions
        assert isinstance(result, AnalysisResult)
        assert result.analysis_type == "data_quality"
        assert 'test_template' in result.results
        
        template_result = result.results['test_template']
        assert 'scores' in template_result
        scores = template_result['scores']
        assert 'completeness' in scores
        assert 'consistency' in scores
        assert 'uniqueness' in scores
        assert 'overall' in scores
        
        # Quality scores should be between 0 and 100
        for score in scores.values():
            assert 0 <= score <= 100
    
    @pytest.mark.asyncio
    async def test_generate_insights_summary(self, data_analyzer):
        """Test insights summary generation"""
        
        # Create mock analysis results
        analysis_results = [
            AnalysisResult(
                analysis_type="test_analysis_1",
                timestamp=datetime.utcnow(),
                data_points=100,
                results={'metric': 'value'},
                insights=['Insight 1', 'Performance issue detected'],
                confidence_score=0.8,
                metadata={}
            ),
            AnalysisResult(
                analysis_type="test_analysis_2",
                timestamp=datetime.utcnow(),
                data_points=50,
                results={'metric': 'value'},
                insights=['Quality issue found', 'Volume increasing'],
                confidence_score=0.9,
                metadata={}
            )
        ]
        
        # Run summary generation
        summary = await data_analyzer.generate_insights_summary(analysis_results)
        
        # Assertions
        assert 'summary' in summary
        assert 'all_insights' in summary
        assert 'high_confidence_insights' in summary
        assert 'categorized_insights' in summary
        assert 'recommendations' in summary
        
        assert summary['summary']['total_analyses'] == 2
        assert summary['summary']['successful_analyses'] == 2
        assert summary['summary']['total_data_points'] == 150
        
        # Check categorization
        categorized = summary['categorized_insights']
        assert 'performance' in categorized
        assert 'quality' in categorized
        assert 'volume' in categorized
        
        # Performance category should contain the performance insight
        assert any('Performance' in insight for insight in categorized['performance'])
    
    def test_calculate_trend(self, data_analyzer):
        """Test trend calculation method"""
        
        # Test increasing trend
        increasing_values = np.array([1, 2, 3, 4, 5])
        trend = data_analyzer._calculate_trend(increasing_values)
        assert trend > 0
        
        # Test decreasing trend
        decreasing_values = np.array([5, 4, 3, 2, 1])
        trend = data_analyzer._calculate_trend(decreasing_values)
        assert trend < 0
        
        # Test stable trend
        stable_values = np.array([3, 3, 3, 3, 3])
        trend = data_analyzer._calculate_trend(stable_values)
        assert abs(trend) < 0.1  # Should be close to 0
    
    def test_detect_anomalies(self, data_analyzer):
        """Test anomaly detection method"""
        
        # Create values with anomalies
        normal_values = np.array([1, 2, 1, 2, 1, 2, 1, 2])
        anomaly_values = np.array([1, 2, 1, 2, 10, 2, 1, 2])  # 10 is anomaly
        
        # Test normal values
        anomalies = data_analyzer._detect_anomalies(normal_values)
        assert len(anomalies) == 0
        
        # Test values with anomaly
        anomalies = data_analyzer._detect_anomalies(anomaly_values)
        assert len(anomalies) > 0
        assert 4 in anomalies  # Index of anomaly value
    
    def test_calculate_improvement(self, data_analyzer):
        """Test improvement calculation method"""
        
        # Test improvement (time decreased)
        time_values = np.array([5.0, 4.0, 3.0, 2.0])
        improvement = data_analyzer._calculate_improvement(time_values)
        assert improvement > 0  # Positive improvement
        
        # Test degradation (time increased)
        time_values = np.array([2.0, 3.0, 4.0, 5.0])
        improvement = data_analyzer._calculate_improvement(time_values)
        assert improvement < 0  # Negative improvement (degradation)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, data_analyzer, db_manager):
        """Test error handling in analysis methods"""
        
        # Mock database error
        db_manager.fetch_all.side_effect = Exception("Database connection failed")
        
        # The method should handle the error gracefully
        with pytest.raises(Exception):
            await data_analyzer.analyze_extraction_patterns(time_range_days=30)
    
    def test_configuration_validation(self, data_analyzer):
        """Test configuration validation"""
        
        # Test default configuration
        assert data_analyzer.min_data_points == 10
        assert data_analyzer.confidence_threshold == 0.7
        assert data_analyzer.anomaly_threshold == 2.0
        
        # Test cache initialization
        assert isinstance(data_analyzer.analysis_cache, dict)
        assert isinstance(data_analyzer.cache_duration, timedelta)


if __name__ == '__main__':
    pytest.main([__file__])
