"""
Tests for Trend Analyzer
========================

Test suite for the advanced trend analysis engine.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import numpy as np
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.trend_analyzer import (
    TrendAnalyzer, TrendAnalysisResult, TrendDirection, TrendSignificance,
    TrendStatistics, SeasonalPattern, SeasonalityType, Forecast
)
from src.database.manager import DatabaseManager


class TestTrendAnalyzer:
    """Test cases for TrendAnalyzer class"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager"""
        mock_db = AsyncMock(spec=DatabaseManager)
        return mock_db
    
    @pytest.fixture
    async def trend_analyzer(self, db_manager):
        """Create TrendAnalyzer instance with mock database"""
        return TrendAnalyzer(db_manager)
    
    @pytest.mark.asyncio
    async def test_analyze_extraction_trends_success(self, trend_analyzer, db_manager):
        """Test successful extraction trends analysis"""
        
        # Mock database response with upward trend
        base_date = datetime.utcnow() - timedelta(days=30)
        mock_data = []
        
        for i in range(30):
            mock_data.append({
                'date': base_date + timedelta(days=i),
                'extraction_count': 100 + i * 2,  # Increasing trend
                'avg_processing_time': 2.0 - i * 0.01,  # Decreasing time (improving)
                'success_rate': 0.95 + i * 0.001  # Slightly improving
            })
        
        db_manager.fetch_all.return_value = mock_data
        
        # Run analysis
        result = await trend_analyzer.analyze_extraction_trends(time_range_days=30, template_id=1)
        
        # Assertions
        assert isinstance(result, TrendAnalysisResult)
        assert result.metric_name == "extraction_volume"
        assert result.data_points == 30
        
        # Check trend statistics
        stats = result.trend_statistics
        assert isinstance(stats, TrendStatistics)
        assert stats.slope > 0  # Should detect increasing trend
        assert 0 <= stats.r_squared <= 1
        assert 0 <= stats.p_value <= 1
        
        # Should have generated insights
        assert len(result.insights) > 0
        assert len(result.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_extraction_trends_insufficient_data(self, trend_analyzer, db_manager):
        """Test analysis with insufficient data"""
        
        # Mock database response with minimal data
        mock_data = [
            {
                'date': datetime.utcnow(),
                'extraction_count': 100,
                'avg_processing_time': 2.0,
                'success_rate': 0.95
            }
        ]
        
        db_manager.fetch_all.return_value = mock_data
        
        # Run analysis
        result = await trend_analyzer.analyze_extraction_trends(time_range_days=30)
        
        # Assertions
        assert result.data_points == 1
        assert "Insufficient data" in result.insights[0]
        assert result.metadata.get('insufficient_data') is True
    
    @pytest.mark.asyncio
    async def test_analyze_performance_trends(self, trend_analyzer, db_manager):
        """Test performance trends analysis"""
        
        # Mock hourly performance data with degrading trend
        base_date = datetime.utcnow() - timedelta(days=7)
        mock_data = []
        
        for i in range(168):  # 7 days * 24 hours
            mock_data.append({
                'hour': base_date + timedelta(hours=i),
                'avg_processing_time': 1.0 + i * 0.01,  # Gradually increasing (degrading)
                'extraction_count': 50 - i * 0.1  # Decreasing volume
            })
        
        db_manager.fetch_all.return_value = mock_data
        
        # Run analysis
        result = await trend_analyzer.analyze_performance_trends(time_range_days=7, template_id=1)
        
        # Assertions
        assert result.metric_name == "processing_performance"
        assert result.data_points == 168
        
        # Should detect degrading performance trend
        stats = result.trend_statistics
        assert stats.slope > 0  # Processing time increasing (bad trend)
        assert stats.direction in [TrendDirection.SLIGHT_INCREASE, TrendDirection.MODERATE_INCREASE, TrendDirection.STRONG_INCREASE]
    
    @pytest.mark.asyncio
    async def test_analyze_quality_trends(self, trend_analyzer, db_manager):
        """Test quality trends analysis"""
        
        # Mock daily quality data
        base_date = datetime.utcnow() - timedelta(days=30)
        mock_data = []
        
        for i in range(30):
            mock_data.append({
                'date': base_date + timedelta(days=i),
                'success_rate': 0.95 - i * 0.005,  # Declining quality
                'total_extractions': 100
            })
        
        db_manager.fetch_all.return_value = mock_data
        
        # Run analysis
        result = await trend_analyzer.analyze_quality_trends(time_range_days=30, template_id=1)
        
        # Assertions
        assert result.metric_name == "quality_trends"
        assert result.data_points == 30
        
        # Should detect declining quality trend
        stats = result.trend_statistics
        assert stats.slope < 0  # Quality decreasing
        assert stats.direction in [TrendDirection.SLIGHT_DECREASE, TrendDirection.MODERATE_DECREASE, TrendDirection.STRONG_DECREASE]
    
    @pytest.mark.asyncio
    async def test_compare_template_trends(self, trend_analyzer, db_manager):
        """Test template comparison analysis"""
        
        # Mock comparative data for multiple templates
        base_date = datetime.utcnow() - timedelta(days=30)
        mock_data = []
        
        for template_id in [1, 2, 3]:
            for i in range(30):
                # Template 1: Growing, Template 2: Stable, Template 3: Declining
                volume_multiplier = 1.1 if template_id == 1 else (1.0 if template_id == 2 else 0.9)
                
                mock_data.append({
                    'template_id': template_id,
                    'template_name': f'Template {template_id}',
                    'date': base_date + timedelta(days=i),
                    'extraction_count': int(100 * (volume_multiplier ** i)),
                    'avg_processing_time': 2.0 + (template_id - 2) * 0.5,
                    'success_rate': 0.95 - (template_id - 1) * 0.05
                })
        
        db_manager.fetch_all.return_value = mock_data
        
        # Run analysis
        result = await trend_analyzer.compare_template_trends(time_range_days=30)
        
        # Assertions
        assert 'templates_analyzed' in result
        assert result['templates_analyzed'] == 3
        assert 'results' in result
        assert 'insights' in result
        
        # Check individual template results
        results = result['results']
        assert len(results) == 3
        
        for template_id, template_result in results.items():
            assert 'template_name' in template_result
            assert 'trends' in template_result
            assert 'current_metrics' in template_result
    
    def test_calculate_trend_statistics(self, trend_analyzer):
        """Test trend statistics calculation"""
        
        # Create test data with known trend
        timestamps = [datetime.utcnow() - timedelta(days=i) for i in range(10, 0, -1)]
        values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])  # Strong increasing trend
        
        stats = trend_analyzer._calculate_trend_statistics(values, timestamps)
        
        # Assertions
        assert isinstance(stats, TrendStatistics)
        assert stats.slope > 0  # Positive slope for increasing trend
        assert stats.r_squared > 0.9  # Should have high R-squared for linear data
        assert stats.p_value < 0.05  # Should be statistically significant
        assert stats.direction in [TrendDirection.STRONG_INCREASE, TrendDirection.MODERATE_INCREASE]
        assert stats.significance in [TrendSignificance.SIGNIFICANT, TrendSignificance.HIGHLY_SIGNIFICANT]
    
    def test_classify_trend_direction(self, trend_analyzer):
        """Test trend direction classification"""
        
        # Test strong increase
        direction = trend_analyzer._classify_trend_direction(0.1, 10)  # 10% increase per unit
        assert direction == TrendDirection.STRONG_INCREASE
        
        # Test moderate increase
        direction = trend_analyzer._classify_trend_direction(0.03, 10)  # 3% increase per unit
        assert direction == TrendDirection.MODERATE_INCREASE
        
        # Test slight increase
        direction = trend_analyzer._classify_trend_direction(0.008, 10)  # 0.8% increase per unit
        assert direction == TrendDirection.SLIGHT_INCREASE
        
        # Test stable
        direction = trend_analyzer._classify_trend_direction(0.001, 10)  # 0.1% increase per unit
        assert direction == TrendDirection.STABLE
        
        # Test decreases
        direction = trend_analyzer._classify_trend_direction(-0.008, 10)
        assert direction == TrendDirection.SLIGHT_DECREASE
        
        direction = trend_analyzer._classify_trend_direction(-0.03, 10)
        assert direction == TrendDirection.MODERATE_DECREASE
        
        direction = trend_analyzer._classify_trend_direction(-0.1, 10)
        assert direction == TrendDirection.STRONG_DECREASE
    
    def test_determine_significance(self, trend_analyzer):
        """Test statistical significance determination"""
        
        # Test highly significant
        significance = trend_analyzer._determine_significance(0.005)
        assert significance == TrendSignificance.HIGHLY_SIGNIFICANT
        
        # Test significant
        significance = trend_analyzer._determine_significance(0.03)
        assert significance == TrendSignificance.SIGNIFICANT
        
        # Test marginally significant
        significance = trend_analyzer._determine_significance(0.08)
        assert significance == TrendSignificance.MARGINALLY_SIGNIFICANT
        
        # Test not significant
        significance = trend_analyzer._determine_significance(0.15)
        assert significance == TrendSignificance.NOT_SIGNIFICANT
    
    def test_detect_seasonal_patterns(self, trend_analyzer):
        """Test seasonal pattern detection"""
        
        # Create test data with weekly pattern (higher on weekdays)
        timestamps = []
        values = []
        base_date = datetime(2023, 1, 1)  # Start on a Sunday
        
        for i in range(28):  # 4 weeks
            timestamp = base_date + timedelta(days=i)
            timestamps.append(timestamp)
            
            # Higher values on weekdays (Monday-Friday)
            if timestamp.weekday() < 5:  # Monday=0, Friday=4
                values.append(100 + np.random.normal(0, 5))
            else:  # Weekend
                values.append(50 + np.random.normal(0, 5))
        
        patterns = trend_analyzer._detect_seasonal_patterns(np.array(values), timestamps)
        
        # Should detect weekly seasonality
        weekly_patterns = [p for p in patterns if p.type == SeasonalityType.WEEKLY]
        assert len(weekly_patterns) > 0
        
        if len(weekly_patterns) > 0:
            pattern = weekly_patterns[0]
            assert pattern.strength > 0
            assert pattern.cycle_length == 7
    
    def test_detect_change_points(self, trend_analyzer):
        """Test change point detection"""
        
        # Create data with a clear change point
        timestamps = [datetime.utcnow() - timedelta(days=i) for i in range(30, 0, -1)]
        
        # First half: stable around 10, second half: stable around 20
        values = np.concatenate([
            np.full(15, 10) + np.random.normal(0, 0.5, 15),
            np.full(15, 20) + np.random.normal(0, 0.5, 15)
        ])
        
        change_points = trend_analyzer._detect_change_points(values, timestamps)
        
        # Should detect at least one change point
        assert len(change_points) > 0
    
    def test_detect_anomalies_in_trend(self, trend_analyzer):
        """Test anomaly detection in trends"""
        
        # Create mostly normal data with one clear anomaly
        timestamps = [datetime.utcnow() - timedelta(days=i) for i in range(20, 0, -1)]
        values = np.full(20, 10) + np.random.normal(0, 1, 20)
        values[10] = 50  # Clear anomaly
        
        anomalies = trend_analyzer._detect_anomalies_in_trend(values, timestamps)
        
        # Should detect the anomaly
        assert len(anomalies) > 0
        
        # The anomaly should be marked as a spike
        anomaly_descriptions = [anomaly[2] for anomaly in anomalies]
        assert any("spike" in desc.lower() for desc in anomaly_descriptions)
    
    def test_generate_forecast(self, trend_analyzer):
        """Test forecast generation"""
        
        # Create trending data
        timestamps = [datetime.utcnow() - timedelta(days=i) for i in range(30, 0, -1)]
        values = np.array([i + np.random.normal(0, 0.1) for i in range(30)])  # Linear trend with noise
        
        forecast = trend_analyzer._generate_forecast(values, timestamps, horizon=7)
        
        if forecast is not None:  # May be None if sklearn not available
            assert isinstance(forecast, Forecast)
            assert forecast.forecast_horizon == 7
            assert len(forecast.predicted_values) == 7
            assert len(forecast.confidence_intervals) == 7
            assert 0 <= forecast.forecast_accuracy <= 1
            
            # Predictions should continue the trend
            last_actual = values[-1]
            first_prediction = forecast.predicted_values[0]
            assert abs(first_prediction - last_actual) < 10  # Reasonable continuation
    
    def test_generate_trend_insights(self, trend_analyzer):
        """Test trend insights generation"""
        
        # Create mock trend statistics
        trend_stats = TrendStatistics(
            slope=0.5,
            intercept=10.0,
            r_squared=0.85,
            p_value=0.01,
            std_error=0.1,
            confidence_interval=(0.3, 0.7),
            direction=TrendDirection.MODERATE_INCREASE,
            significance=TrendSignificance.HIGHLY_SIGNIFICANT
        )
        
        # Create mock seasonal patterns
        seasonal_patterns = [
            SeasonalPattern(
                type=SeasonalityType.WEEKLY,
                strength=0.4,
                peak_periods=[1, 2, 3],  # Weekdays
                trough_periods=[5, 6],   # Weekend
                cycle_length=7,
                amplitude=20.0
            )
        ]
        
        change_points = [datetime.utcnow() - timedelta(days=15)]
        anomalies = [(datetime.utcnow() - timedelta(days=5), 100.0, "Statistical spike")]
        
        insights = trend_analyzer._generate_trend_insights(
            trend_stats, seasonal_patterns, change_points, anomalies
        )
        
        # Assertions
        assert len(insights) > 0
        
        # Should mention statistical significance
        significance_insights = [i for i in insights if "significant" in i.lower()]
        assert len(significance_insights) > 0
        
        # Should mention seasonality
        seasonal_insights = [i for i in insights if "seasonality" in i.lower()]
        assert len(seasonal_insights) > 0
        
        # Should mention change points
        change_insights = [i for i in insights if "change" in i.lower()]
        assert len(change_insights) > 0
        
        # Should mention anomalies
        anomaly_insights = [i for i in insights if "anomal" in i.lower()]
        assert len(anomaly_insights) > 0
    
    def test_generate_trend_recommendations(self, trend_analyzer):
        """Test trend recommendations generation"""
        
        # Mock declining trend
        declining_stats = TrendStatistics(
            slope=-0.5,
            intercept=100.0,
            r_squared=0.8,
            p_value=0.01,
            std_error=0.1,
            confidence_interval=(-0.7, -0.3),
            direction=TrendDirection.STRONG_DECREASE,
            significance=TrendSignificance.HIGHLY_SIGNIFICANT
        )
        
        # Mock seasonal patterns
        seasonal_patterns = [
            SeasonalPattern(
                type=SeasonalityType.DAILY,
                strength=0.3,
                peak_periods=[9, 10, 11],  # Peak hours
                trough_periods=[1, 2, 3],  # Low hours
                cycle_length=24,
                amplitude=15.0
            )
        ]
        
        # Mock good forecast
        forecast = Forecast(
            forecast_horizon=7,
            predicted_values=[95, 90, 85, 80, 75, 70, 65],
            confidence_intervals=[(90, 100), (85, 95), (80, 90), (75, 85), (70, 80), (65, 75), (60, 70)],
            forecast_accuracy=0.85,
            methodology="Linear Regression"
        )
        
        recommendations = trend_analyzer._generate_trend_recommendations(
            declining_stats, seasonal_patterns, forecast
        )
        
        # Assertions
        assert len(recommendations) > 0
        
        # Should recommend investigation for declining trend
        decline_recs = [r for r in recommendations if "declining" in r.lower() or "investigate" in r.lower()]
        assert len(decline_recs) > 0
        
        # Should recommend resource scheduling for daily patterns
        resource_recs = [r for r in recommendations if "resource" in r.lower() or "schedule" in r.lower()]
        assert len(resource_recs) > 0
        
        # Should recommend using forecast for planning
        forecast_recs = [r for r in recommendations if "forecast" in r.lower() or "planning" in r.lower()]
        assert len(forecast_recs) > 0
    
    def test_calculate_simple_trend(self, trend_analyzer):
        """Test simple trend calculation for comparison"""
        
        # Test increasing trend
        increasing_values = [10, 15, 20, 25, 30]
        trend = trend_analyzer._calculate_simple_trend(increasing_values)
        
        assert trend['direction'] == 'strong_increase'
        assert trend['change_percentage'] == 200.0  # (30-10)/10 * 100
        assert trend['first_value'] == 10
        assert trend['last_value'] == 30
        
        # Test stable trend
        stable_values = [20, 21, 19, 20, 20]
        trend = trend_analyzer._calculate_simple_trend(stable_values)
        
        assert trend['direction'] == 'stable'
        assert abs(trend['change_percentage']) < 5
        
        # Test declining trend
        declining_values = [100, 80, 60, 40, 20]
        trend = trend_analyzer._calculate_simple_trend(declining_values)
        
        assert trend['direction'] == 'strong_decrease'
        assert trend['change_percentage'] == -80.0  # (20-100)/100 * 100
    
    def test_generate_comparative_insights(self, trend_analyzer):
        """Test comparative insights generation"""
        
        # Mock comparison results
        comparison_results = {
            1: {
                'template_name': 'Template A',
                'trends': {
                    'volume': {'direction': 'strong_increase', 'change_percentage': 25.0}
                }
            },
            2: {
                'template_name': 'Template B',
                'trends': {
                    'volume': {'direction': 'moderate_decrease', 'change_percentage': -15.0}
                }
            },
            3: {
                'template_name': 'Template C',
                'trends': {
                    'volume': {'direction': 'stable', 'change_percentage': 2.0}
                }
            }
        }
        
        insights = trend_analyzer._generate_comparative_insights(comparison_results)
        
        # Assertions
        assert len(insights) > 0
        
        # Should identify best and worst performers
        performance_insights = [i for i in insights if "best performing" in i.lower() or "worst performing" in i.lower()]
        assert len(performance_insights) >= 2  # Should have best and worst
    
    def test_configuration_validation(self, trend_analyzer):
        """Test configuration validation"""
        
        # Test default configuration
        assert trend_analyzer.min_data_points == 10
        assert isinstance(trend_analyzer.significance_levels, dict)
        assert isinstance(trend_analyzer.trend_thresholds, dict)
        
        # Test significance levels
        assert TrendSignificance.HIGHLY_SIGNIFICANT in trend_analyzer.significance_levels
        assert TrendSignificance.SIGNIFICANT in trend_analyzer.significance_levels
        
        # Test trend thresholds
        assert 'strong' in trend_analyzer.trend_thresholds
        assert 'moderate' in trend_analyzer.trend_thresholds
        assert 'slight' in trend_analyzer.trend_thresholds


if __name__ == '__main__':
    pytest.main([__file__])
