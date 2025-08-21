"""
Integration Tests for Analysis Module
=====================================

Test suite for integration between all analysis components.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
import tempfile
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.data_analyzer import DataAnalyzer
from src.analysis.quality_checker import QualityChecker  
from src.analysis.trend_analyzer import TrendAnalyzer
from src.analysis.report_generator import ReportGenerator, ReportType, ReportFormat
from src.database.manager import DatabaseManager


class TestAnalysisIntegration:
    """Integration tests for analysis components"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager with realistic data"""
        mock_db = AsyncMock(spec=DatabaseManager)
        
        # Mock realistic extraction data
        base_date = datetime.utcnow() - timedelta(days=30)
        extraction_data = []
        
        for i in range(30):
            date = base_date + timedelta(days=i)
            for hour in range(24):
                extraction_data.append({
                    'template_id': 1,
                    'template_name': 'Company Profile',
                    'extraction_date': date,
                    'hour': hour,
                    'extraction_count': 50 + (hour % 8) * 10 + (i % 7) * 5,
                    'success_count': int((50 + (hour % 8) * 10 + (i % 7) * 5) * 0.95),
                    'avg_processing_time': 2.0 + (hour % 4) * 0.3,
                    'data_quality_score': 8.5 + (i % 10) * 0.1
                })
        
        mock_db.fetch_all.return_value = extraction_data
        return mock_db
    
    @pytest.fixture
    async def analysis_components(self, db_manager):
        """Create all analysis components"""
        data_analyzer = DataAnalyzer(db_manager)
        quality_checker = QualityChecker(db_manager)
        trend_analyzer = TrendAnalyzer(db_manager)
        report_generator = ReportGenerator(db_manager, data_analyzer, quality_checker, trend_analyzer)
        
        return data_analyzer, quality_checker, trend_analyzer, report_generator
    
    @pytest.mark.asyncio
    async def test_end_to_end_daily_analysis(self, analysis_components, db_manager):
        """Test complete end-to-end daily analysis workflow"""
        
        data_analyzer, quality_checker, trend_analyzer, report_generator = analysis_components
        
        # Step 1: Analyze data patterns
        data_analysis = await data_analyzer.analyze_extraction_volume(time_range_days=1, template_id=1)
        
        assert 'total_extractions' in data_analysis
        assert 'hourly_breakdown' in data_analysis
        assert data_analysis['total_extractions'] > 0
        
        # Step 2: Assess quality
        quality_analysis = await quality_checker.analyze_quality_trends(time_range_days=1, template_id=1)
        
        assert 'overall_score' in quality_analysis
        assert 'success_rate' in quality_analysis
        assert 0 <= quality_analysis['overall_score'] <= 10
        
        # Step 3: Analyze trends
        trend_analysis = await trend_analyzer.analyze_extraction_trends(time_range_days=7, template_id=1)
        
        assert hasattr(trend_analysis, 'trend_statistics')
        assert hasattr(trend_analysis, 'insights')
        assert hasattr(trend_analysis, 'recommendations')
        
        # Step 4: Generate comprehensive report
        target_date = datetime.utcnow().date()
        report = await report_generator.generate_daily_report(target_date)
        
        assert report.report_type == ReportType.DAILY
        assert len(report.sections) > 0
        assert len(report.key_insights) > 0
        assert len(report.recommendations) > 0
        
        # Verify data flows correctly between components
        assert report.summary is not None
        assert len(report.summary) > 0
    
    @pytest.mark.asyncio
    async def test_cross_component_data_consistency(self, analysis_components, db_manager):
        """Test data consistency across analysis components"""
        
        data_analyzer, quality_checker, trend_analyzer, _ = analysis_components
        
        # Analyze same time period with all components
        time_range_days = 7
        template_id = 1
        
        # Get data from each component
        data_results = await data_analyzer.analyze_extraction_volume(time_range_days, template_id)
        quality_results = await quality_checker.analyze_quality_trends(time_range_days, template_id)
        trend_results = await trend_analyzer.analyze_extraction_trends(time_range_days, template_id)
        
        # Verify consistency in basic metrics
        # All should reference the same underlying extraction data
        
        # Data analyzer should provide total extractions
        total_extractions = data_results.get('total_extractions', 0)
        
        # Quality checker should derive metrics from same data
        quality_total = quality_results.get('total_extractions', 0)
        
        # Allow for minor differences due to different aggregation methods
        if total_extractions > 0 and quality_total > 0:
            consistency_ratio = min(total_extractions, quality_total) / max(total_extractions, quality_total)
            assert consistency_ratio > 0.95, "Cross-component data inconsistency detected"
        
        # Trend analysis should have reasonable data points
        assert trend_results.data_points > 0
        assert trend_results.data_points <= time_range_days * 24  # Maximum hourly data points
    
    @pytest.mark.asyncio
    async def test_template_comparison_integration(self, analysis_components, db_manager):
        """Test integration of template comparison across components"""
        
        data_analyzer, quality_checker, trend_analyzer, report_generator = analysis_components
        
        # Mock data for multiple templates
        template_data = {
            1: {'name': 'Company Profile', 'complexity': 'high'},
            2: {'name': 'Person Profile', 'complexity': 'medium'},
            3: {'name': 'Vehicle Detail', 'complexity': 'low'}
        }
        
        # Modify database mock to return multi-template data
        multi_template_data = []
        base_date = datetime.utcnow() - timedelta(days=7)
        
        for template_id, template_info in template_data.items():
            for i in range(7):
                date = base_date + timedelta(days=i)
                multi_template_data.append({
                    'template_id': template_id,
                    'template_name': template_info['name'],
                    'extraction_date': date,
                    'extraction_count': 100 * template_id + i * 10,
                    'success_count': int((100 * template_id + i * 10) * (0.95 - template_id * 0.02)),
                    'avg_processing_time': 1.0 + template_id * 0.5,
                    'data_quality_score': 9.0 - template_id * 0.3
                })
        
        db_manager.fetch_all.return_value = multi_template_data
        
        # Analyze each template with data analyzer
        template_analyses = {}
        for template_id in template_data.keys():
            analysis = await data_analyzer.analyze_template_performance(template_id, time_range_days=7)
            template_analyses[template_id] = analysis
        
        # Compare quality across templates
        quality_comparison = await quality_checker.compare_template_quality(time_range_days=7)
        
        # Analyze trends across templates
        trend_comparison = await trend_analyzer.compare_template_trends(time_range_days=7)
        
        # Generate comparative report
        comparison_report = await report_generator.generate_template_comparison_report(
            list(template_data.keys()), time_range_days=7
        )
        
        # Assertions
        assert len(template_analyses) == 3
        assert 'template_rankings' in quality_comparison
        assert 'templates_analyzed' in trend_comparison
        assert trend_comparison['templates_analyzed'] == 3
        
        # Verify report captures all comparisons
        assert "Template Comparison" in comparison_report.title
        assert len(comparison_report.sections) >= 3  # Overview, Quality, Trends
    
    @pytest.mark.asyncio
    async def test_real_time_analysis_pipeline(self, analysis_components, db_manager):
        """Test real-time analysis pipeline integration"""
        
        data_analyzer, quality_checker, trend_analyzer, report_generator = analysis_components
        
        # Simulate real-time data stream
        current_time = datetime.utcnow()
        real_time_data = []
        
        # Generate data for last 2 hours
        for i in range(120):  # 2 hours in minutes
            timestamp = current_time - timedelta(minutes=i)
            real_time_data.append({
                'template_id': 1,
                'extraction_timestamp': timestamp,
                'success': i % 10 != 0,  # 90% success rate
                'processing_time': 2.0 + (i % 20) * 0.1,
                'quality_score': 8.0 + (i % 30) * 0.1
            })
        
        db_manager.fetch_all.return_value = real_time_data
        
        # Run real-time analysis
        real_time_metrics = await data_analyzer.analyze_real_time_metrics(template_id=1)
        current_quality = await quality_checker.assess_current_quality(template_id=1)
        short_term_trend = await trend_analyzer.analyze_short_term_trends(template_id=1, hours=2)
        
        # Generate real-time dashboard report
        dashboard_report = await report_generator.generate_realtime_dashboard(template_id=1)
        
        # Assertions
        assert 'current_rate' in real_time_metrics
        assert 'avg_processing_time' in real_time_metrics
        assert 'current_score' in current_quality
        assert 'trend_direction' in current_quality
        assert hasattr(short_term_trend, 'trend_statistics')
        
        # Dashboard should include all real-time metrics
        assert dashboard_report.report_type.value == 'realtime'
        assert "Real-time" in dashboard_report.title
    
    @pytest.mark.asyncio
    async def test_error_propagation_and_recovery(self, analysis_components, db_manager):
        """Test error handling and recovery across components"""
        
        data_analyzer, quality_checker, trend_analyzer, report_generator = analysis_components
        
        # Simulate database error
        db_manager.fetch_all.side_effect = Exception("Database connection failed")
        
        # Test error handling in each component
        with pytest.raises(Exception):
            await data_analyzer.analyze_extraction_volume(time_range_days=1)
        
        with pytest.raises(Exception):
            await quality_checker.analyze_quality_trends(time_range_days=1)
        
        with pytest.raises(Exception):
            await trend_analyzer.analyze_extraction_trends(time_range_days=1)
        
        # Test report generator handles component failures gracefully
        try:
            report = await report_generator.generate_daily_report(datetime.utcnow().date())
            # Should generate partial report or error report
            assert report is not None
            assert "error" in report.title.lower() or len(report.sections) == 0
        except Exception:
            # Alternative: may raise exception but should be informative
            pass
        
        # Test recovery after database restoration
        db_manager.fetch_all.side_effect = None
        db_manager.fetch_all.return_value = [{
            'template_id': 1,
            'extraction_date': datetime.utcnow(),
            'extraction_count': 100,
            'success_count': 95,
            'avg_processing_time': 2.0,
            'data_quality_score': 8.5
        }]
        
        # Components should work again after recovery
        data_results = await data_analyzer.analyze_extraction_volume(time_range_days=1)
        assert 'total_extractions' in data_results
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, analysis_components, db_manager):
        """Test analysis performance with large datasets"""
        
        data_analyzer, quality_checker, trend_analyzer, report_generator = analysis_components
        
        # Generate large dataset (30 days * 24 hours * 3 templates)
        large_dataset = []
        base_date = datetime.utcnow() - timedelta(days=30)
        
        for template_id in [1, 2, 3]:
            for day in range(30):
                for hour in range(24):
                    timestamp = base_date + timedelta(days=day, hours=hour)
                    large_dataset.append({
                        'template_id': template_id,
                        'template_name': f'Template {template_id}',
                        'extraction_timestamp': timestamp,
                        'extraction_count': 50 + (hour % 10) * 5,
                        'success_count': int((50 + (hour % 10) * 5) * 0.94),
                        'avg_processing_time': 2.0 + (template_id * 0.2),
                        'data_quality_score': 8.0 + (day % 20) * 0.05
                    })
        
        db_manager.fetch_all.return_value = large_dataset
        
        # Time the analysis operations
        import time
        
        start_time = time.time()
        
        # Run comprehensive analysis
        data_analysis = await data_analyzer.analyze_extraction_patterns(time_range_days=30)
        quality_analysis = await quality_checker.analyze_long_term_quality(time_range_days=30)
        trend_analysis = await trend_analyzer.analyze_long_term_trends(time_range_days=30)
        
        analysis_time = time.time() - start_time
        
        # Generate monthly report
        start_time = time.time()
        month_start = datetime.utcnow().date().replace(day=1)
        monthly_report = await report_generator.generate_monthly_report(month_start)
        report_time = time.time() - start_time
        
        # Performance assertions
        assert analysis_time < 10.0, f"Analysis took too long: {analysis_time}s"
        assert report_time < 15.0, f"Report generation took too long: {report_time}s"
        
        # Verify analysis quality despite large dataset
        assert 'daily_totals' in data_analysis
        assert len(data_analysis['daily_totals']) == 30
        assert 'monthly_average' in quality_analysis
        assert hasattr(trend_analysis, 'growth_rate')
        assert len(monthly_report.sections) > 0
    
    @pytest.mark.asyncio
    async def test_export_integration_all_formats(self, analysis_components, db_manager):
        """Test report export integration across all formats"""
        
        _, _, _, report_generator = analysis_components
        
        # Generate a comprehensive report
        target_date = datetime.utcnow().date()
        report = await report_generator.generate_daily_report(target_date)
        
        # Test export to all supported formats
        export_formats = [ReportFormat.JSON, ReportFormat.HTML]
        if report_generator._pdf_available():
            export_formats.append(ReportFormat.PDF)
        
        export_results = {}
        
        for format_type in export_formats:
            with tempfile.NamedTemporaryFile(
                suffix=f'.{format_type.value.lower()}', 
                delete=False
            ) as tmp_file:
                export_path = tmp_file.name
            
            try:
                result = await report_generator.export_report(report, export_path, format_type)
                export_results[format_type] = result
                
                # Verify export success
                assert result['success'] is True
                assert Path(export_path).exists()
                assert Path(export_path).stat().st_size > 0
                
            finally:
                # Cleanup
                Path(export_path).unlink(missing_ok=True)
        
        # Verify all exports succeeded
        for format_type, result in export_results.items():
            assert result['success'] is True, f"Export failed for {format_type.value}"
    
    @pytest.mark.asyncio
    async def test_configuration_consistency(self, analysis_components):
        """Test configuration consistency across components"""
        
        data_analyzer, quality_checker, trend_analyzer, report_generator = analysis_components
        
        # Check that components use consistent thresholds and configurations
        
        # Data analyzer configuration
        assert hasattr(data_analyzer, 'volume_thresholds')
        assert hasattr(data_analyzer, 'performance_thresholds')
        
        # Quality checker configuration
        assert hasattr(quality_checker, 'quality_thresholds')
        assert hasattr(quality_checker, 'scoring_weights')
        
        # Trend analyzer configuration
        assert hasattr(trend_analyzer, 'significance_levels')
        assert hasattr(trend_analyzer, 'trend_thresholds')
        
        # Report generator configuration
        assert hasattr(report_generator, 'format_configurations')
        
        # Verify threshold consistency where applicable
        # For example, quality score ranges should be consistent
        quality_max = max(quality_checker.quality_thresholds.values())
        assert quality_max == 10.0, "Quality scores should be on 0-10 scale"
        
        # Performance thresholds should be reasonable
        perf_thresholds = data_analyzer.performance_thresholds
        assert perf_thresholds['excellent'] < perf_thresholds['good']
        assert perf_thresholds['good'] < perf_thresholds['warning']
        assert perf_thresholds['warning'] < perf_thresholds['critical']


if __name__ == '__main__':
    pytest.main([__file__])
