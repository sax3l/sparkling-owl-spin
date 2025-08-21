"""
Tests for Report Generator
=========================

Test suite for the comprehensive report generation engine.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch, mock_open
import tempfile
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.analysis.report_generator import (
    ReportGenerator, ReportType, ReportFormat, ReportData, 
    ReportConfiguration, ReportSection, MetricSummary, 
    ChartConfiguration, EmailConfiguration
)
from src.database.manager import DatabaseManager
from src.analysis.data_analyzer import DataAnalyzer
from src.analysis.quality_checker import QualityChecker  
from src.analysis.trend_analyzer import TrendAnalyzer


class TestReportGenerator:
    """Test cases for ReportGenerator class"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create mock database manager"""
        mock_db = AsyncMock(spec=DatabaseManager)
        return mock_db
    
    @pytest.fixture
    async def mock_analyzers(self, db_manager):
        """Create mock analyzers"""
        data_analyzer = AsyncMock(spec=DataAnalyzer)
        quality_checker = AsyncMock(spec=QualityChecker)
        trend_analyzer = AsyncMock(spec=TrendAnalyzer)
        
        return data_analyzer, quality_checker, trend_analyzer
    
    @pytest.fixture
    async def report_generator(self, db_manager, mock_analyzers):
        """Create ReportGenerator instance with mock dependencies"""
        data_analyzer, quality_checker, trend_analyzer = mock_analyzers
        return ReportGenerator(db_manager, data_analyzer, quality_checker, trend_analyzer)
    
    @pytest.mark.asyncio
    async def test_generate_daily_report_success(self, report_generator, mock_analyzers):
        """Test successful daily report generation"""
        
        data_analyzer, quality_checker, trend_analyzer = mock_analyzers
        
        # Mock analyzer responses
        data_analyzer.analyze_extraction_volume.return_value = {
            'total_extractions': 1500,
            'successful_extractions': 1425,
            'failed_extractions': 75,
            'avg_processing_time': 2.3,
            'hourly_breakdown': [{'hour': i, 'count': 60+i*2} for i in range(24)]
        }
        
        quality_checker.analyze_quality_trends.return_value = {
            'overall_score': 8.5,
            'success_rate': 0.95,
            'data_completeness': 0.92,
            'quality_issues': ['Missing phone numbers in 5% of records'],
            'improvements': 2.5
        }
        
        trend_analyzer.analyze_extraction_trends.return_value = Mock(
            trend_statistics=Mock(
                direction='moderate_increase',
                change_percentage=12.5,
                significance='significant'
            ),
            insights=['Extraction volume increased by 12.5% compared to yesterday'],
            recommendations=['Consider scaling up processing capacity during peak hours']
        )
        
        # Generate report
        target_date = datetime.utcnow().date()
        report = await report_generator.generate_daily_report(target_date)
        
        # Assertions
        assert isinstance(report, ReportData)
        assert report.report_type == ReportType.DAILY
        assert report.title == f"Daily Extraction Report - {target_date}"
        assert len(report.sections) > 0
        
        # Check sections exist
        section_names = [section.title for section in report.sections]
        assert "Executive Summary" in section_names
        assert "Extraction Volume Analysis" in section_names
        assert "Quality Assessment" in section_names
        assert "Trend Analysis" in section_names
        
        # Verify analyzer calls
        data_analyzer.analyze_extraction_volume.assert_called_once()
        quality_checker.analyze_quality_trends.assert_called_once()
        trend_analyzer.analyze_extraction_trends.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_weekly_report_success(self, report_generator, mock_analyzers):
        """Test successful weekly report generation"""
        
        data_analyzer, quality_checker, trend_analyzer = mock_analyzers
        
        # Mock comprehensive weekly data
        data_analyzer.analyze_extraction_patterns.return_value = {
            'daily_totals': [1200, 1300, 1400, 1350, 1450, 800, 900],
            'peak_hours': [9, 10, 11, 14, 15],
            'low_hours': [1, 2, 3, 23],
            'template_breakdown': {
                'company_profile': 4500,
                'person_profile': 2800,
                'vehicle_detail': 1500
            }
        }
        
        quality_checker.generate_quality_report.return_value = {
            'weekly_average_score': 8.7,
            'daily_scores': [8.5, 8.8, 8.9, 8.6, 8.7, 8.2, 8.4],
            'improvement_trends': 'Steady improvement throughout the week',
            'critical_issues': [],
            'recommendations': ['Focus on weekend quality monitoring']
        }
        
        trend_analyzer.compare_template_trends.return_value = {
            'templates_analyzed': 3,
            'results': {
                1: {'template_name': 'Company Profile', 'trend': 'increasing'},
                2: {'template_name': 'Person Profile', 'trend': 'stable'},
                3: {'template_name': 'Vehicle Detail', 'trend': 'decreasing'}
            },
            'insights': ['Company profiles showing strongest growth']
        }
        
        # Generate report
        week_start = datetime.utcnow().date() - timedelta(days=7)
        report = await report_generator.generate_weekly_report(week_start)
        
        # Assertions
        assert report.report_type == ReportType.WEEKLY
        assert "Weekly" in report.title
        assert len(report.sections) >= 4
        
        # Check for weekly-specific sections
        section_names = [section.title for section in report.sections]
        assert "Weekly Summary" in section_names
        assert "Template Performance Comparison" in section_names
    
    @pytest.mark.asyncio
    async def test_generate_monthly_report_success(self, report_generator, mock_analyzers):
        """Test successful monthly report generation"""
        
        data_analyzer, quality_checker, trend_analyzer = mock_analyzers
        
        # Mock monthly aggregated data
        data_analyzer.analyze_monthly_patterns.return_value = {
            'total_extractions': 45000,
            'daily_averages': 1500,
            'best_day': {'date': '2023-01-15', 'count': 2100},
            'worst_day': {'date': '2023-01-02', 'count': 800},
            'growth_rate': 8.5,
            'seasonal_patterns': 'Higher activity mid-month'
        }
        
        quality_checker.analyze_long_term_quality.return_value = {
            'monthly_average': 8.6,
            'quality_trend': 'improving',
            'consistency_score': 0.85,
            'top_issues': ['Incomplete addresses in 3% of records'],
            'quality_milestones': ['Achieved 95% success rate target']
        }
        
        trend_analyzer.analyze_long_term_trends.return_value = {
            'primary_trend': 'strong_growth',
            'growth_rate': 15.2,
            'forecast_next_month': 52000,
            'confidence': 0.87,
            'seasonal_adjustments': 'Account for end-of-month dip'
        }
        
        # Generate report
        month_start = datetime.utcnow().date().replace(day=1)
        report = await report_generator.generate_monthly_report(month_start)
        
        # Assertions
        assert report.report_type == ReportType.MONTHLY
        assert "Monthly" in report.title
        
        # Check for monthly-specific content
        section_names = [section.title for section in report.sections]
        assert "Monthly Performance Overview" in section_names
        assert "Long-term Trends" in section_names
        assert "Forecasting & Planning" in section_names
    
    @pytest.mark.asyncio
    async def test_generate_template_report_success(self, report_generator, mock_analyzers):
        """Test template-specific report generation"""
        
        data_analyzer, quality_checker, trend_analyzer = mock_analyzers
        
        template_id = 1
        template_name = "Company Profile Template"
        
        # Mock template-specific data
        data_analyzer.analyze_template_performance.return_value = {
            'template_id': template_id,
            'template_name': template_name,
            'total_uses': 12500,
            'success_rate': 0.94,
            'avg_processing_time': 2.8,
            'field_extraction_rates': {
                'company_name': 0.99,
                'address': 0.85,
                'phone': 0.78,
                'email': 0.82
            }
        }
        
        quality_checker.analyze_template_quality.return_value = {
            'template_quality_score': 8.4,
            'field_quality_scores': {
                'company_name': 9.2,
                'address': 7.8,
                'phone': 7.5,
                'email': 8.1
            },
            'common_issues': ['Phone format inconsistencies'],
            'improvement_suggestions': ['Add phone number validation']
        }
        
        trend_analyzer.analyze_template_trends.return_value = Mock(
            trend_statistics=Mock(direction='stable', change_percentage=2.1),
            insights=['Template usage has been stable over the past month'],
            recommendations=['Consider optimizing address extraction logic']
        )
        
        # Generate report
        time_range_days = 30
        report = await report_generator.generate_template_report(template_id, time_range_days)
        
        # Assertions
        assert report.report_type == ReportType.TEMPLATE
        assert template_name in report.title
        
        # Check template-specific sections
        section_names = [section.title for section in report.sections]
        assert "Template Overview" in section_names
        assert "Field Extraction Analysis" in section_names
        assert "Quality Assessment" in section_names
    
    @pytest.mark.asyncio
    async def test_export_report_to_json(self, report_generator):
        """Test JSON report export"""
        
        # Create test report data
        report_data = ReportData(
            report_type=ReportType.DAILY,
            title="Test Report",
            generated_at=datetime.utcnow(),
            time_range={"start": "2023-01-01", "end": "2023-01-01"},
            sections=[
                ReportSection(
                    title="Test Section",
                    content="Test content",
                    metrics=[
                        MetricSummary(
                            name="Test Metric",
                            value=100,
                            unit="count",
                            change_percentage=5.0,
                            status="good"
                        )
                    ],
                    charts=[]
                )
            ],
            summary="Test summary",
            key_insights=["Test insight"],
            recommendations=["Test recommendation"]
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            export_path = tmp_file.name
        
        try:
            # Export report
            result = await report_generator.export_report(report_data, export_path, ReportFormat.JSON)
            
            # Assertions
            assert result['success'] is True
            assert result['file_path'] == export_path
            
            # Verify file contents
            with open(export_path, 'r') as f:
                exported_data = json.load(f)
            
            assert exported_data['report_type'] == 'DAILY'
            assert exported_data['title'] == "Test Report"
            assert len(exported_data['sections']) == 1
            
        finally:
            # Cleanup
            Path(export_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_report_to_html(self, report_generator):
        """Test HTML report export"""
        
        # Create test report data
        report_data = ReportData(
            report_type=ReportType.WEEKLY,
            title="Weekly Test Report",
            generated_at=datetime.utcnow(),
            time_range={"start": "2023-01-01", "end": "2023-01-07"},
            sections=[
                ReportSection(
                    title="Summary Section",
                    content="Weekly summary content",
                    metrics=[
                        MetricSummary(
                            name="Total Extractions",
                            value=10500,
                            unit="count",
                            change_percentage=8.5,
                            status="excellent"
                        )
                    ],
                    charts=[
                        ChartConfiguration(
                            chart_type="line",
                            title="Daily Trends",
                            data_source="daily_volumes",
                            x_axis="date",
                            y_axis="count"
                        )
                    ]
                )
            ],
            summary="Strong performance this week",
            key_insights=["8.5% growth over previous week"],
            recommendations=["Continue current optimization efforts"]
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
            export_path = tmp_file.name
        
        try:
            # Export report
            result = await report_generator.export_report(report_data, export_path, ReportFormat.HTML)
            
            # Assertions
            assert result['success'] is True
            assert result['file_path'] == export_path
            
            # Verify HTML structure
            with open(export_path, 'r') as f:
                html_content = f.read()
            
            assert "<html>" in html_content
            assert "Weekly Test Report" in html_content
            assert "Total Extractions" in html_content
            assert "10500" in html_content
            
        finally:
            # Cleanup
            Path(export_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_export_report_to_pdf(self, report_generator):
        """Test PDF report export"""
        
        # Create test report data
        report_data = ReportData(
            report_type=ReportType.MONTHLY,
            title="Monthly Performance Report",
            generated_at=datetime.utcnow(),
            time_range={"start": "2023-01-01", "end": "2023-01-31"},
            sections=[
                ReportSection(
                    title="Executive Summary",
                    content="Monthly performance has exceeded expectations",
                    metrics=[
                        MetricSummary(
                            name="Monthly Total",
                            value=45000,
                            unit="extractions",
                            change_percentage=15.2,
                            status="excellent"
                        )
                    ],
                    charts=[]
                )
            ],
            summary="Outstanding month with significant growth",
            key_insights=["15.2% growth month-over-month"],
            recommendations=["Scale infrastructure for continued growth"]
        )
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            export_path = tmp_file.name
        
        try:
            # Mock PDF generation (since we may not have reportlab installed)
            with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
                mock_canvas_instance = Mock()
                mock_canvas.return_value = mock_canvas_instance
                
                result = await report_generator.export_report(report_data, export_path, ReportFormat.PDF)
                
                # Assertions
                assert result['success'] is True
                assert result['file_path'] == export_path
                
                # Verify canvas methods were called
                assert mock_canvas_instance.drawString.called
                assert mock_canvas_instance.save.called
                
        except ImportError:
            # If reportlab not available, should handle gracefully
            result = await report_generator.export_report(report_data, export_path, ReportFormat.PDF)
            assert result['success'] is False
            assert "PDF generation not available" in result.get('error', '')
            
        finally:
            # Cleanup
            Path(export_path).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_schedule_report_generation(self, report_generator):
        """Test scheduled report generation"""
        
        config = ReportConfiguration(
            report_type=ReportType.DAILY,
            schedule="0 8 * * *",  # Daily at 8 AM
            recipients=["admin@example.com"],
            format=ReportFormat.HTML,
            auto_export=True,
            export_path="/reports/daily"
        )
        
        # Schedule the report
        result = await report_generator.schedule_report(config)
        
        # Assertions
        assert result['success'] is True
        assert 'schedule_id' in result
        assert result['next_run'] is not None
    
    @pytest.mark.asyncio
    async def test_email_report_delivery(self, report_generator):
        """Test email report delivery"""
        
        # Create test report
        report_data = ReportData(
            report_type=ReportType.DAILY,
            title="Daily Report",
            generated_at=datetime.utcnow(),
            time_range={"start": "2023-01-01", "end": "2023-01-01"},
            sections=[],
            summary="Daily summary",
            key_insights=["Test insight"],
            recommendations=["Test recommendation"]
        )
        
        email_config = EmailConfiguration(
            recipients=["test@example.com"],
            subject="Daily Extraction Report",
            body_template="Please find attached the daily report.",
            smtp_host="smtp.example.com",
            smtp_port=587,
            use_tls=True,
            username="reports@example.com",
            password="password123"
        )
        
        # Mock email sending
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value = mock_server
            
            result = await report_generator.send_report_email(report_data, email_config)
            
            # Assertions
            assert result['success'] is True
            assert result['recipients'] == ["test@example.com"]
            
            # Verify SMTP methods were called
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()
    
    def test_create_metric_summary(self, report_generator):
        """Test metric summary creation"""
        
        metric = report_generator._create_metric_summary(
            name="Extraction Count",
            value=1500,
            unit="count",
            previous_value=1400,
            benchmark=1600
        )
        
        # Assertions
        assert isinstance(metric, MetricSummary)
        assert metric.name == "Extraction Count"
        assert metric.value == 1500
        assert metric.unit == "count"
        assert metric.change_percentage == pytest.approx(7.14, rel=1e-2)  # (1500-1400)/1400 * 100
        assert metric.status in ["good", "warning", "critical"]
    
    def test_create_chart_configuration(self, report_generator):
        """Test chart configuration creation"""
        
        chart = report_generator._create_chart_configuration(
            chart_type="bar",
            title="Hourly Distribution",
            data_source="hourly_data",
            x_axis="hour",
            y_axis="count"
        )
        
        # Assertions
        assert isinstance(chart, ChartConfiguration)
        assert chart.chart_type == "bar"
        assert chart.title == "Hourly Distribution"
        assert chart.data_source == "hourly_data"
        assert chart.x_axis == "hour"
        assert chart.y_axis == "count"
    
    def test_determine_metric_status(self, report_generator):
        """Test metric status determination"""
        
        # Test excellent status (above benchmark)
        status = report_generator._determine_metric_status(110, 100, is_higher_better=True)
        assert status == "excellent"
        
        # Test good status (within acceptable range)
        status = report_generator._determine_metric_status(95, 100, is_higher_better=True)
        assert status == "good"
        
        # Test warning status (below threshold)
        status = report_generator._determine_metric_status(80, 100, is_higher_better=True)
        assert status == "warning"
        
        # Test critical status (significantly below threshold)
        status = report_generator._determine_metric_status(60, 100, is_higher_better=True)
        assert status == "critical"
        
        # Test inverse logic (lower is better)
        status = report_generator._determine_metric_status(0.8, 1.0, is_higher_better=False)
        assert status == "excellent"
        
        status = report_generator._determine_metric_status(1.2, 1.0, is_higher_better=False)
        assert status == "warning"
    
    def test_generate_executive_summary(self, report_generator):
        """Test executive summary generation"""
        
        # Mock data for summary generation
        data_analysis = {
            'total_extractions': 15000,
            'success_rate': 0.94,
            'avg_processing_time': 2.1
        }
        
        quality_analysis = {
            'overall_score': 8.7,
            'improvement_percentage': 5.2
        }
        
        trend_analysis = {
            'primary_trend': 'increasing',
            'change_percentage': 12.5
        }
        
        summary = report_generator._generate_executive_summary(
            data_analysis, quality_analysis, trend_analysis
        )
        
        # Assertions
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "15000" in summary or "15,000" in summary  # Should mention total extractions
        assert "94%" in summary  # Should mention success rate
        assert "8.7" in summary  # Should mention quality score
    
    def test_format_number_with_units(self, report_generator):
        """Test number formatting with units"""
        
        # Test small numbers
        formatted = report_generator._format_number(150)
        assert formatted == "150"
        
        # Test thousands
        formatted = report_generator._format_number(1500)
        assert formatted == "1.5K"
        
        # Test millions
        formatted = report_generator._format_number(1500000)
        assert formatted == "1.5M"
        
        # Test with decimals
        formatted = report_generator._format_number(1234567)
        assert formatted == "1.23M"
        
        # Test percentage formatting
        formatted = report_generator._format_percentage(0.945)
        assert formatted == "94.5%"
        
        # Test time formatting
        formatted = report_generator._format_duration(3661)  # 1 hour, 1 minute, 1 second
        assert "1h" in formatted and "1m" in formatted
    
    def test_validate_report_configuration(self, report_generator):
        """Test report configuration validation"""
        
        # Valid configuration
        valid_config = ReportConfiguration(
            report_type=ReportType.DAILY,
            schedule="0 8 * * *",
            recipients=["admin@example.com"],
            format=ReportFormat.HTML
        )
        
        validation_result = report_generator._validate_configuration(valid_config)
        assert validation_result['valid'] is True
        assert len(validation_result['errors']) == 0
        
        # Invalid configuration (invalid email)
        invalid_config = ReportConfiguration(
            report_type=ReportType.DAILY,
            schedule="invalid-cron",
            recipients=["invalid-email"],
            format=ReportFormat.HTML
        )
        
        validation_result = report_generator._validate_configuration(invalid_config)
        assert validation_result['valid'] is False
        assert len(validation_result['errors']) > 0
    
    def test_generate_html_template(self, report_generator):
        """Test HTML template generation"""
        
        report_data = ReportData(
            report_type=ReportType.DAILY,
            title="Test Report",
            generated_at=datetime.utcnow(),
            time_range={"start": "2023-01-01", "end": "2023-01-01"},
            sections=[
                ReportSection(
                    title="Test Section",
                    content="Test content",
                    metrics=[],
                    charts=[]
                )
            ],
            summary="Test summary",
            key_insights=["Insight 1", "Insight 2"],
            recommendations=["Recommendation 1", "Recommendation 2"]
        )
        
        html_content = report_generator._generate_html_template(report_data)
        
        # Assertions
        assert isinstance(html_content, str)
        assert "<html>" in html_content
        assert "<head>" in html_content
        assert "<body>" in html_content
        assert "Test Report" in html_content
        assert "Test Section" in html_content
        assert "Test content" in html_content
        assert "Insight 1" in html_content
        assert "Recommendation 1" in html_content
    
    def test_error_handling_invalid_template(self, report_generator):
        """Test error handling for invalid template ID"""
        
        with pytest.raises(ValueError, match="Template ID must be provided"):
            asyncio.run(report_generator.generate_template_report(None, 30))
    
    def test_error_handling_invalid_date_range(self, report_generator):
        """Test error handling for invalid date ranges"""
        
        future_date = datetime.utcnow().date() + timedelta(days=10)
        
        with pytest.raises(ValueError, match="Date cannot be in the future"):
            asyncio.run(report_generator.generate_daily_report(future_date))
    
    def test_error_handling_unsupported_format(self, report_generator):
        """Test error handling for unsupported export format"""
        
        report_data = ReportData(
            report_type=ReportType.DAILY,
            title="Test Report",
            generated_at=datetime.utcnow(),
            time_range={},
            sections=[],
            summary="",
            key_insights=[],
            recommendations=[]
        )
        
        with pytest.raises(ValueError, match="Unsupported report format"):
            asyncio.run(report_generator.export_report(report_data, "/tmp/test", "UNSUPPORTED_FORMAT"))


if __name__ == '__main__':
    pytest.main([__file__])
