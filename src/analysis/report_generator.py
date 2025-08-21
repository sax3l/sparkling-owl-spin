"""
Report Generator
===============

Comprehensive report generation engine for the ECaDP platform.
Generates professional analysis reports in multiple formats with data visualization.
"""

import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
import asyncio
import json
import base64
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import io
import tempfile

# Import analysis components
from .data_analyzer import DataAnalyzer, AnalysisResult
from .quality_checker import QualityChecker, QualityReport, QualityDimension
from .trend_analyzer import TrendAnalyzer, TrendAnalysisResult

from ..database.manager import DatabaseManager
from ..observability.metrics import metrics_collector

logger = logging.getLogger(__name__)

class ReportFormat(Enum):
    """Report output formats"""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    MARKDOWN = "markdown"
    CSV = "csv"

class ReportType(Enum):
    """Types of reports"""
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYSIS = "detailed_analysis"
    QUALITY_ASSESSMENT = "quality_assessment"
    TREND_ANALYSIS = "trend_analysis"
    PERFORMANCE_REVIEW = "performance_review"
    COMPARATIVE_ANALYSIS = "comparative_analysis"

@dataclass
class ReportSection:
    """A section within a report"""
    title: str
    content: str
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ReportMetadata:
    """Report metadata and configuration"""
    title: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    generated_by: str
    template_id: Optional[int] = None
    time_period: Optional[Tuple[datetime, datetime]] = None
    data_sources: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GeneratedReport:
    """Complete generated report"""
    metadata: ReportMetadata
    sections: List[ReportSection]
    summary: Dict[str, Any]
    content: Union[str, bytes]  # Report content in specified format
    file_path: Optional[str] = None
    size_bytes: int = 0

class ReportGenerator:
    """
    Comprehensive report generation engine
    
    Features:
    - Multiple report types (executive, detailed, quality, trend analysis)
    - Multiple output formats (HTML, PDF, JSON, Markdown)
    - Data visualization integration
    - Automated insights and recommendations
    - Template-based report generation
    - Batch report processing
    - Report scheduling and delivery
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Initialize analysis engines
        self.data_analyzer = DataAnalyzer(db_manager)
        self.quality_checker = QualityChecker(db_manager)
        self.trend_analyzer = TrendAnalyzer(db_manager)
        
        # Report configuration
        self.report_templates_dir = Path("data/templates/reports")
        self.output_dir = Path("data/exports")
        self.chart_config = {
            'width': 800,
            'height': 400,
            'theme': 'professional'
        }
        
        # Ensure directories exist
        self.report_templates_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_executive_summary(self, template_id: Optional[int] = None,
                                       time_range_days: int = 30,
                                       format: ReportFormat = ReportFormat.HTML) -> GeneratedReport:
        """Generate executive summary report"""
        
        metadata = ReportMetadata(
            title=f"Executive Summary - {datetime.utcnow().strftime('%Y-%m-%d')}",
            report_type=ReportType.EXECUTIVE_SUMMARY,
            format=format,
            generated_at=datetime.utcnow(),
            generated_by="ECaDP Report Generator",
            template_id=template_id,
            time_period=(datetime.utcnow() - timedelta(days=time_range_days), datetime.utcnow()),
            data_sources=["extractions", "templates", "quality_metrics"],
            parameters={"time_range_days": time_range_days}
        )
        
        # Gather key metrics
        sections = []
        
        # 1. Overview Section
        overview_section = await self._generate_overview_section(template_id, time_range_days)
        sections.append(overview_section)
        
        # 2. Performance Highlights
        performance_section = await self._generate_performance_highlights(template_id, time_range_days)
        sections.append(performance_section)
        
        # 3. Quality Summary
        quality_section = await self._generate_quality_summary(template_id)
        sections.append(quality_section)
        
        # 4. Key Insights
        insights_section = await self._generate_key_insights(template_id, time_range_days)
        sections.append(insights_section)
        
        # 5. Recommendations
        recommendations_section = await self._generate_recommendations_section(template_id, time_range_days)
        sections.append(recommendations_section)
        
        # Generate summary
        summary = self._generate_report_summary(sections)
        
        # Render report in specified format
        content = await self._render_report(metadata, sections, format)
        
        return GeneratedReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            content=content,
            size_bytes=len(content) if isinstance(content, (str, bytes)) else 0
        )
    
    async def generate_detailed_analysis(self, template_id: Optional[int] = None,
                                       time_range_days: int = 90,
                                       format: ReportFormat = ReportFormat.HTML) -> GeneratedReport:
        """Generate detailed analysis report"""
        
        metadata = ReportMetadata(
            title=f"Detailed Analysis Report - {datetime.utcnow().strftime('%Y-%m-%d')}",
            report_type=ReportType.DETAILED_ANALYSIS,
            format=format,
            generated_at=datetime.utcnow(),
            generated_by="ECaDP Report Generator",
            template_id=template_id,
            time_period=(datetime.utcnow() - timedelta(days=time_range_days), datetime.utcnow()),
            data_sources=["extractions", "templates", "quality_metrics", "performance_data"],
            parameters={"time_range_days": time_range_days}
        )
        
        sections = []
        
        # 1. Data Analysis
        data_analysis = await self.data_analyzer.analyze_extraction_patterns(time_range_days)
        sections.append(self._create_section_from_analysis("Data Extraction Analysis", data_analysis))
        
        # 2. Performance Analysis
        performance_analysis = await self.data_analyzer.analyze_performance_trends(time_range_days)
        sections.append(self._create_section_from_analysis("Performance Analysis", performance_analysis))
        
        # 3. Completeness Analysis
        completeness_analysis = await self.data_analyzer.analyze_data_completeness(template_id)
        sections.append(self._create_section_from_analysis("Data Completeness", completeness_analysis))
        
        # 4. Quality Metrics
        quality_metrics = await self.data_analyzer.analyze_data_quality_metrics(template_id)
        sections.append(self._create_section_from_analysis("Quality Metrics", quality_metrics))
        
        # 5. Trend Analysis
        trend_analysis = await self.trend_analyzer.analyze_extraction_trends(time_range_days, template_id)
        sections.append(self._create_section_from_trend_analysis("Trend Analysis", trend_analysis))
        
        summary = self._generate_report_summary(sections)
        content = await self._render_report(metadata, sections, format)
        
        return GeneratedReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            content=content,
            size_bytes=len(content) if isinstance(content, (str, bytes)) else 0
        )
    
    async def generate_quality_assessment(self, template_id: Optional[int] = None,
                                        format: ReportFormat = ReportFormat.HTML) -> GeneratedReport:
        """Generate quality assessment report"""
        
        metadata = ReportMetadata(
            title=f"Data Quality Assessment - {datetime.utcnow().strftime('%Y-%m-%d')}",
            report_type=ReportType.QUALITY_ASSESSMENT,
            format=format,
            generated_at=datetime.utcnow(),
            generated_by="ECaDP Report Generator",
            template_id=template_id,
            data_sources=["extractions", "templates", "quality_rules"],
            parameters={"template_id": template_id}
        )
        
        # Perform comprehensive quality assessment
        quality_report = await self.quality_checker.assess_quality(template_id)
        
        sections = []
        
        # 1. Quality Overview
        overview_section = self._create_quality_overview_section(quality_report)
        sections.append(overview_section)
        
        # 2. Quality Dimensions
        dimensions_section = self._create_quality_dimensions_section(quality_report)
        sections.append(dimensions_section)
        
        # 3. Field Analysis
        field_analysis_section = self._create_field_analysis_section(quality_report)
        sections.append(field_analysis_section)
        
        # 4. Issues and Violations
        issues_section = self._create_issues_section(quality_report)
        sections.append(issues_section)
        
        # 5. Quality Trends
        if template_id:
            trends = await self.quality_checker.get_quality_trends(template_id)
            if trends.get('trend_available'):
                trends_section = self._create_quality_trends_section(trends)
                sections.append(trends_section)
        
        summary = self._generate_quality_summary_dict(quality_report)
        content = await self._render_report(metadata, sections, format)
        
        return GeneratedReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            content=content,
            size_bytes=len(content) if isinstance(content, (str, bytes)) else 0
        )
    
    async def generate_comparative_analysis(self, time_range_days: int = 90,
                                          format: ReportFormat = ReportFormat.HTML) -> GeneratedReport:
        """Generate comparative analysis across templates"""
        
        metadata = ReportMetadata(
            title=f"Comparative Template Analysis - {datetime.utcnow().strftime('%Y-%m-%d')}",
            report_type=ReportType.COMPARATIVE_ANALYSIS,
            format=format,
            generated_at=datetime.utcnow(),
            generated_by="ECaDP Report Generator",
            time_period=(datetime.utcnow() - timedelta(days=time_range_days), datetime.utcnow()),
            data_sources=["extractions", "templates", "performance_data"],
            parameters={"time_range_days": time_range_days}
        )
        
        # Perform comparative analysis
        comparison_results = await self.trend_analyzer.compare_template_trends(time_range_days)
        
        sections = []
        
        # 1. Overview
        overview_section = self._create_comparison_overview_section(comparison_results)
        sections.append(overview_section)
        
        # 2. Performance Comparison
        performance_section = self._create_performance_comparison_section(comparison_results)
        sections.append(performance_section)
        
        # 3. Template Rankings
        rankings_section = self._create_template_rankings_section(comparison_results)
        sections.append(rankings_section)
        
        # 4. Insights and Recommendations
        insights_section = self._create_comparative_insights_section(comparison_results)
        sections.append(insights_section)
        
        summary = self._generate_comparative_summary(comparison_results)
        content = await self._render_report(metadata, sections, format)
        
        return GeneratedReport(
            metadata=metadata,
            sections=sections,
            summary=summary,
            content=content,
            size_bytes=len(content) if isinstance(content, (str, bytes)) else 0
        )
    
    async def _generate_overview_section(self, template_id: Optional[int], time_range_days: int) -> ReportSection:
        """Generate overview section"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get basic statistics
        if template_id:
            query = """
            SELECT 
                COUNT(*) as total_extractions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_extractions,
                AVG(processing_time) as avg_processing_time,
                t.name as template_name
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.created_at >= %s AND e.template_id = %s
            GROUP BY t.name
            """
            params = (cutoff_date, template_id)
        else:
            query = """
            SELECT 
                COUNT(*) as total_extractions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_extractions,
                AVG(processing_time) as avg_processing_time
            FROM extractions
            WHERE created_at >= %s
            """
            params = (cutoff_date,)
        
        result = await self.db_manager.fetch_one(query, params)
        
        if not result:
            return ReportSection(
                title="Overview",
                content="No data available for the specified period.",
                insights=["No extraction data found for analysis"]
            )
        
        total = result['total_extractions'] or 0
        successful = result['successful_extractions'] or 0
        success_rate = (successful / total * 100) if total > 0 else 0
        avg_time = result['avg_processing_time'] or 0
        
        content = f"""
        **Data Overview ({time_range_days} days)**
        
        - **Total Extractions**: {total:,}
        - **Successful Extractions**: {successful:,}
        - **Success Rate**: {success_rate:.1f}%
        - **Average Processing Time**: {avg_time:.2f} seconds
        """
        
        if template_id and 'template_name' in result:
            content = f"**Template**: {result['template_name']}\n\n" + content
        
        insights = []
        if success_rate < 90:
            insights.append(f"Success rate ({success_rate:.1f}%) is below target (90%)")
        if avg_time > 5:
            insights.append(f"Average processing time ({avg_time:.1f}s) exceeds recommended threshold")
        
        return ReportSection(
            title="Overview",
            content=content,
            insights=insights
        )
    
    async def _generate_performance_highlights(self, template_id: Optional[int], time_range_days: int) -> ReportSection:
        """Generate performance highlights section"""
        
        # Analyze performance trends
        performance_analysis = await self.data_analyzer.analyze_performance_trends(time_range_days)
        
        content = "**Performance Highlights**\n\n"
        
        if performance_analysis.results:
            trends = performance_analysis.results
            
            if 'processing_time' in trends:
                pt_trend = trends['processing_time']
                improvement = pt_trend.get('improvement_percentage', 0)
                
                if improvement > 5:
                    content += f"✅ Processing time improved by {improvement:.1f}%\n"
                elif improvement < -5:
                    content += f"⚠️ Processing time degraded by {abs(improvement):.1f}%\n"
                else:
                    content += f"📊 Processing time remained stable\n"
            
            if 'volume' in trends:
                volume_trend = trends['volume']
                growth = volume_trend.get('growth_rate', 0)
                
                if growth > 10:
                    content += f"📈 High volume growth: {growth:.1f}%\n"
                elif growth > 0:
                    content += f"📊 Moderate volume growth: {growth:.1f}%\n"
                else:
                    content += f"📉 Volume declined by {abs(growth):.1f}%\n"
        
        return ReportSection(
            title="Performance Highlights",
            content=content,
            insights=performance_analysis.insights
        )
    
    async def _generate_quality_summary(self, template_id: Optional[int]) -> ReportSection:
        """Generate quality summary section"""
        
        quality_analysis = await self.data_analyzer.analyze_data_quality_metrics(template_id)
        
        content = "**Data Quality Summary**\n\n"
        
        if quality_analysis.results:
            for template_name, quality_data in quality_analysis.results.items():
                scores = quality_data.get('scores', {})
                overall = scores.get('overall', 0)
                
                status_emoji = "✅" if overall >= 90 else "⚠️" if overall >= 70 else "❌"
                content += f"{status_emoji} **{template_name}**: {overall:.1f}% overall quality\n"
                
                # Quality dimensions
                completeness = scores.get('completeness', 0)
                consistency = scores.get('consistency', 0)
                uniqueness = scores.get('uniqueness', 0)
                
                content += f"  - Completeness: {completeness:.1f}%\n"
                content += f"  - Consistency: {consistency:.1f}%\n"
                content += f"  - Uniqueness: {uniqueness:.1f}%\n\n"
        
        return ReportSection(
            title="Quality Summary",
            content=content,
            insights=quality_analysis.insights
        )
    
    async def _generate_key_insights(self, template_id: Optional[int], time_range_days: int) -> ReportSection:
        """Generate key insights section"""
        
        # Gather insights from multiple analyses
        all_insights = []
        
        # Data patterns
        patterns_analysis = await self.data_analyzer.analyze_extraction_patterns(time_range_days)
        all_insights.extend(patterns_analysis.insights)
        
        # Performance trends
        performance_analysis = await self.data_analyzer.analyze_performance_trends(time_range_days)
        all_insights.extend(performance_analysis.insights)
        
        # Quality insights
        quality_analysis = await self.data_analyzer.analyze_data_quality_metrics(template_id)
        all_insights.extend(quality_analysis.insights)
        
        # Prioritize and format insights
        priority_insights = []
        normal_insights = []
        
        for insight in all_insights:
            if any(word in insight.lower() for word in ['critical', 'high', 'low', 'declining', 'error']):
                priority_insights.append(insight)
            else:
                normal_insights.append(insight)
        
        content = "**Key Insights**\n\n"
        
        if priority_insights:
            content += "**Priority Items:**\n"
            for insight in priority_insights[:5]:  # Top 5 priority insights
                content += f"🔴 {insight}\n"
            content += "\n"
        
        if normal_insights:
            content += "**Additional Insights:**\n"
            for insight in normal_insights[:5]:  # Top 5 normal insights
                content += f"💡 {insight}\n"
        
        return ReportSection(
            title="Key Insights",
            content=content,
            insights=priority_insights + normal_insights
        )
    
    async def _generate_recommendations_section(self, template_id: Optional[int], time_range_days: int) -> ReportSection:
        """Generate recommendations section"""
        
        # Gather recommendations from multiple analyses
        all_recommendations = []
        
        analyses = [
            await self.data_analyzer.analyze_extraction_patterns(time_range_days),
            await self.data_analyzer.analyze_performance_trends(time_range_days),
            await self.data_analyzer.analyze_data_quality_metrics(template_id)
        ]
        
        for analysis in analyses:
            if hasattr(analysis, 'results') and analysis.results:
                # Extract recommendations from analysis results
                pass  # Recommendations would be generated by each analyzer
        
        # Generate summary recommendations
        summary_insights = await self.data_analyzer.generate_insights_summary(analyses)
        if 'recommendations' in summary_insights:
            all_recommendations.extend(summary_insights['recommendations'])
        
        content = "**Recommendations**\n\n"
        
        if all_recommendations:
            for i, recommendation in enumerate(all_recommendations[:10], 1):
                content += f"{i}. {recommendation}\n"
        else:
            content += "No specific recommendations at this time. Continue monitoring performance metrics.\n"
        
        return ReportSection(
            title="Recommendations",
            content=content,
            recommendations=all_recommendations
        )
    
    def _create_section_from_analysis(self, title: str, analysis: AnalysisResult) -> ReportSection:
        """Create report section from analysis result"""
        
        content = f"**{title}**\n\n"
        content += f"Analysis conducted on {analysis.data_points:,} data points.\n"
        content += f"Confidence Score: {analysis.confidence_score:.1%}\n\n"
        
        if analysis.results:
            content += "**Key Findings:**\n"
            for key, value in analysis.results.items():
                if isinstance(value, dict):
                    content += f"- **{key.replace('_', ' ').title()}**:\n"
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            content += f"  - {sub_key.replace('_', ' ').title()}: {sub_value}\n"
                else:
                    content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        return ReportSection(
            title=title,
            content=content,
            insights=analysis.insights
        )
    
    def _create_section_from_trend_analysis(self, title: str, trend_analysis: TrendAnalysisResult) -> ReportSection:
        """Create report section from trend analysis result"""
        
        content = f"**{title}**\n\n"
        content += f"Analysis Period: {trend_analysis.analysis_period[0].strftime('%Y-%m-%d')} to {trend_analysis.analysis_period[1].strftime('%Y-%m-%d')}\n"
        content += f"Data Points: {trend_analysis.data_points:,}\n\n"
        
        # Trend statistics
        stats = trend_analysis.trend_statistics
        content += f"**Trend Direction**: {stats.direction.value.replace('_', ' ').title()}\n"
        content += f"**Statistical Significance**: {stats.significance.value.replace('_', ' ').title()}\n"
        content += f"**R-squared**: {stats.r_squared:.3f}\n\n"
        
        # Seasonal patterns
        if trend_analysis.seasonal_patterns:
            content += "**Seasonal Patterns Detected:**\n"
            for pattern in trend_analysis.seasonal_patterns:
                content += f"- {pattern.type.value.title()} seasonality (strength: {pattern.strength:.1%})\n"
        
        return ReportSection(
            title=title,
            content=content,
            insights=trend_analysis.insights,
            recommendations=trend_analysis.recommendations
        )
    
    def _create_quality_overview_section(self, quality_report: QualityReport) -> ReportSection:
        """Create quality overview section"""
        
        content = f"**Quality Assessment Overview**\n\n"
        content += f"**Template**: {quality_report.template_name}\n"
        content += f"**Assessment Date**: {quality_report.assessment_date.strftime('%Y-%m-%d %H:%M')}\n"
        content += f"**Records Analyzed**: {quality_report.records_analyzed:,}\n\n"
        
        content += f"**Overall Quality Score**: {quality_report.overall_quality_score:.1f}%\n\n"
        
        # Quality grade
        score = quality_report.overall_quality_score
        if score >= 95:
            grade = "A+ (Excellent)"
        elif score >= 90:
            grade = "A (Very Good)"
        elif score >= 80:
            grade = "B (Good)"
        elif score >= 70:
            grade = "C (Fair)"
        elif score >= 60:
            grade = "D (Poor)"
        else:
            grade = "F (Critical)"
        
        content += f"**Quality Grade**: {grade}\n"
        
        return ReportSection(
            title="Quality Overview",
            content=content,
            insights=[f"Overall quality score: {score:.1f}%"]
        )
    
    def _create_quality_dimensions_section(self, quality_report: QualityReport) -> ReportSection:
        """Create quality dimensions section"""
        
        content = "**Quality Dimensions Analysis**\n\n"
        
        for dimension, score in quality_report.quality_scores.items():
            status = "✅" if score >= 90 else "⚠️" if score >= 70 else "❌"
            content += f"{status} **{dimension.value.title()}**: {score:.1f}%\n"
        
        return ReportSection(
            title="Quality Dimensions",
            content=content
        )
    
    def _create_field_analysis_section(self, quality_report: QualityReport) -> ReportSection:
        """Create field analysis section"""
        
        content = "**Field-Level Analysis**\n\n"
        
        for field_name, metrics in quality_report.field_metrics.items():
            total = metrics.get('total_values', 0)
            if total == 0:
                continue
            
            null_rate = (metrics.get('null_count', 0) / total) * 100
            valid_rate = (metrics.get('valid_count', 0) / total) * 100
            
            content += f"**{field_name}**:\n"
            content += f"  - Completeness: {100 - null_rate:.1f}%\n"
            content += f"  - Validity: {valid_rate:.1f}%\n"
            content += f"  - Total Values: {total:,}\n\n"
        
        return ReportSection(
            title="Field Analysis",
            content=content
        )
    
    def _create_issues_section(self, quality_report: QualityReport) -> ReportSection:
        """Create issues section"""
        
        content = "**Quality Issues**\n\n"
        
        if quality_report.issues:
            content += f"**Total Issues Found**: {len(quality_report.issues)}\n\n"
            
            # Group by severity
            critical_issues = [i for i in quality_report.issues if i.severity.value == 'critical']
            high_issues = [i for i in quality_report.issues if i.severity.value == 'high']
            
            if critical_issues:
                content += f"**Critical Issues ({len(critical_issues)})**:\n"
                for issue in critical_issues[:5]:  # Show top 5
                    content += f"- {issue.description}\n"
                content += "\n"
            
            if high_issues:
                content += f"**High Priority Issues ({len(high_issues)})**:\n"
                for issue in high_issues[:5]:  # Show top 5
                    content += f"- {issue.description}\n"
        else:
            content += "No quality issues detected.\n"
        
        return ReportSection(
            title="Quality Issues",
            content=content
        )
    
    def _create_quality_trends_section(self, trends: Dict[str, Any]) -> ReportSection:
        """Create quality trends section"""
        
        content = "**Quality Trends**\n\n"
        
        if trends.get('trend_available'):
            trends_data = trends['trends']
            
            overall_trend = trends_data.get('overall', {})
            trend_direction = overall_trend.get('trend', 'stable')
            change_pct = overall_trend.get('change_percentage', 0)
            
            if trend_direction == 'improving':
                content += f"📈 Overall quality is improving (+{change_pct:.1f}%)\n"
            elif trend_direction == 'declining':
                content += f"📉 Overall quality is declining ({change_pct:.1f}%)\n"
            else:
                content += f"📊 Overall quality is stable\n"
            
            content += "\n**Dimension Trends:**\n"
            for dim_name, dim_data in trends_data.items():
                if dim_name == 'overall':
                    continue
                
                dim_trend = dim_data.get('trend', 'stable')
                if dim_trend != 'stable':
                    trend_emoji = "📈" if dim_trend == 'improving' else "📉"
                    content += f"{trend_emoji} {dim_name.title()}: {dim_trend}\n"
        
        return ReportSection(
            title="Quality Trends",
            content=content
        )
    
    def _create_comparison_overview_section(self, comparison_results: Dict[str, Any]) -> ReportSection:
        """Create comparison overview section"""
        
        content = "**Template Comparison Overview**\n\n"
        
        if 'error' in comparison_results:
            content += f"Error: {comparison_results['error']}\n"
            return ReportSection(title="Comparison Overview", content=content)
        
        period = comparison_results.get('analysis_period', {})
        templates_count = comparison_results.get('templates_analyzed', 0)
        
        content += f"**Analysis Period**: {period.get('days', 0)} days\n"
        content += f"**Templates Analyzed**: {templates_count}\n\n"
        
        insights = comparison_results.get('insights', [])
        if insights:
            content += "**Key Findings:**\n"
            for insight in insights:
                content += f"- {insight}\n"
        
        return ReportSection(
            title="Comparison Overview",
            content=content,
            insights=insights
        )
    
    def _create_performance_comparison_section(self, comparison_results: Dict[str, Any]) -> ReportSection:
        """Create performance comparison section"""
        
        content = "**Performance Comparison**\n\n"
        
        results = comparison_results.get('results', {})
        
        if results:
            # Sort by volume for comparison
            sorted_templates = sorted(
                results.items(),
                key=lambda x: x[1]['current_metrics']['daily_volume'],
                reverse=True
            )
            
            content += "**Volume Leaders:**\n"
            for template_id, data in sorted_templates[:5]:
                name = data['template_name']
                volume = data['current_metrics']['daily_volume']
                content += f"- {name}: {volume:,} extractions/day\n"
        
        return ReportSection(
            title="Performance Comparison",
            content=content
        )
    
    def _create_template_rankings_section(self, comparison_results: Dict[str, Any]) -> ReportSection:
        """Create template rankings section"""
        
        content = "**Template Rankings**\n\n"
        
        results = comparison_results.get('results', {})
        
        if results:
            # Rank by overall performance score (combination of factors)
            ranked_templates = []
            
            for template_id, data in results.items():
                metrics = data['current_metrics']
                volume = metrics.get('daily_volume', 0)
                success_rate = metrics.get('success_rate', 0)
                
                # Simple ranking score
                score = (volume * 0.3) + (success_rate * 0.7)
                
                ranked_templates.append({
                    'name': data['template_name'],
                    'score': score,
                    'volume': volume,
                    'success_rate': success_rate
                })
            
            ranked_templates.sort(key=lambda x: x['score'], reverse=True)
            
            content += "**Overall Rankings:**\n"
            for i, template in enumerate(ranked_templates[:10], 1):
                content += f"{i}. **{template['name']}**\n"
                content += f"   - Daily Volume: {template['volume']:,}\n"
                content += f"   - Success Rate: {template['success_rate']:.1f}%\n\n"
        
        return ReportSection(
            title="Template Rankings",
            content=content
        )
    
    def _create_comparative_insights_section(self, comparison_results: Dict[str, Any]) -> ReportSection:
        """Create comparative insights section"""
        
        insights = comparison_results.get('insights', [])
        
        content = "**Comparative Insights & Recommendations**\n\n"
        
        if insights:
            content += "**Key Insights:**\n"
            for insight in insights:
                content += f"💡 {insight}\n"
        
        # Generate recommendations based on results
        results = comparison_results.get('results', {})
        recommendations = []
        
        if results:
            # Find templates with declining performance
            declining = [
                data['template_name'] for data in results.values()
                if data['trends']['volume'] and 'decrease' in data['trends']['volume']['direction']
            ]
            
            if declining:
                recommendations.append(f"Review declining templates: {', '.join(declining[:3])}")
        
        if recommendations:
            content += "\n**Recommendations:**\n"
            for rec in recommendations:
                content += f"🔧 {rec}\n"
        
        return ReportSection(
            title="Insights & Recommendations",
            content=content,
            insights=insights,
            recommendations=recommendations
        )
    
    def _generate_report_summary(self, sections: List[ReportSection]) -> Dict[str, Any]:
        """Generate summary statistics for the report"""
        
        total_insights = sum(len(section.insights) for section in sections)
        total_recommendations = sum(len(section.recommendations) for section in sections)
        
        return {
            'sections_count': len(sections),
            'total_insights': total_insights,
            'total_recommendations': total_recommendations,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_quality_summary_dict(self, quality_report: QualityReport) -> Dict[str, Any]:
        """Generate quality summary dictionary"""
        
        return {
            'overall_score': quality_report.overall_quality_score,
            'records_analyzed': quality_report.records_analyzed,
            'issues_found': len(quality_report.issues),
            'quality_dimensions': {
                dim.value: score for dim, score in quality_report.quality_scores.items()
            }
        }
    
    def _generate_comparative_summary(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comparative summary dictionary"""
        
        return {
            'templates_analyzed': comparison_results.get('templates_analyzed', 0),
            'analysis_period_days': comparison_results.get('analysis_period', {}).get('days', 0),
            'insights_count': len(comparison_results.get('insights', []))
        }
    
    async def _render_report(self, metadata: ReportMetadata, sections: List[ReportSection], 
                           format: ReportFormat) -> Union[str, bytes]:
        """Render report in the specified format"""
        
        if format == ReportFormat.HTML:
            return self._render_html_report(metadata, sections)
        elif format == ReportFormat.MARKDOWN:
            return self._render_markdown_report(metadata, sections)
        elif format == ReportFormat.JSON:
            return self._render_json_report(metadata, sections)
        else:
            # Default to markdown
            return self._render_markdown_report(metadata, sections)
    
    def _render_html_report(self, metadata: ReportMetadata, sections: List[ReportSection]) -> str:
        """Render report as HTML"""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{metadata.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .metadata {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }}
                .insight {{ background: #e8f4fd; padding: 10px; margin: 10px 0; border-left: 3px solid #3498db; }}
                .recommendation {{ background: #f0f9ff; padding: 10px; margin: 10px 0; border-left: 3px solid #10b981; }}
                pre {{ background: #f4f4f4; padding: 15px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>{metadata.title}</h1>
            
            <div class="metadata">
                <strong>Generated:</strong> {metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>Report Type:</strong> {metadata.report_type.value.replace('_', ' ').title()}<br>
                <strong>Format:</strong> {metadata.format.value.upper()}
        """
        
        if metadata.time_period:
            start, end = metadata.time_period
            html += f"<br><strong>Period:</strong> {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
        
        html += "</div>\n\n"
        
        for section in sections:
            html += f"<h2>{section.title}</h2>\n"
            
            # Convert markdown-style content to HTML
            content_html = section.content.replace('\n', '<br>')
            content_html = content_html.replace('**', '<strong>').replace('**', '</strong>')
            html += f"<div>{content_html}</div>\n"
            
            if section.insights:
                html += "<h3>Insights</h3>\n"
                for insight in section.insights:
                    html += f'<div class="insight">💡 {insight}</div>\n'
            
            if section.recommendations:
                html += "<h3>Recommendations</h3>\n"
                for rec in section.recommendations:
                    html += f'<div class="recommendation">🔧 {rec}</div>\n'
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _render_markdown_report(self, metadata: ReportMetadata, sections: List[ReportSection]) -> str:
        """Render report as Markdown"""
        
        markdown = f"# {metadata.title}\n\n"
        
        # Metadata section
        markdown += "## Report Information\n\n"
        markdown += f"- **Generated**: {metadata.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown += f"- **Report Type**: {metadata.report_type.value.replace('_', ' ').title()}\n"
        markdown += f"- **Format**: {metadata.format.value.upper()}\n"
        
        if metadata.time_period:
            start, end = metadata.time_period
            markdown += f"- **Period**: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}\n"
        
        markdown += "\n---\n\n"
        
        # Sections
        for section in sections:
            markdown += f"## {section.title}\n\n"
            markdown += f"{section.content}\n\n"
            
            if section.insights:
                markdown += "### 💡 Insights\n\n"
                for insight in section.insights:
                    markdown += f"- {insight}\n"
                markdown += "\n"
            
            if section.recommendations:
                markdown += "### 🔧 Recommendations\n\n"
                for rec in section.recommendations:
                    markdown += f"- {rec}\n"
                markdown += "\n"
            
            markdown += "---\n\n"
        
        return markdown
    
    def _render_json_report(self, metadata: ReportMetadata, sections: List[ReportSection]) -> str:
        """Render report as JSON"""
        
        report_data = {
            'metadata': {
                'title': metadata.title,
                'report_type': metadata.report_type.value,
                'format': metadata.format.value,
                'generated_at': metadata.generated_at.isoformat(),
                'generated_by': metadata.generated_by,
                'template_id': metadata.template_id,
                'time_period': [
                    metadata.time_period[0].isoformat(),
                    metadata.time_period[1].isoformat()
                ] if metadata.time_period else None,
                'data_sources': metadata.data_sources,
                'parameters': metadata.parameters
            },
            'sections': [
                {
                    'title': section.title,
                    'content': section.content,
                    'charts': section.charts,
                    'tables': section.tables,
                    'insights': section.insights,
                    'recommendations': section.recommendations
                }
                for section in sections
            ]
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    async def save_report(self, report: GeneratedReport, filename: Optional[str] = None) -> str:
        """Save report to file and return file path"""
        
        if not filename:
            timestamp = report.metadata.generated_at.strftime('%Y%m%d_%H%M%S')
            template_suffix = f"_template_{report.metadata.template_id}" if report.metadata.template_id else ""
            filename = f"{report.metadata.report_type.value}_{timestamp}{template_suffix}.{report.metadata.format.value}"
        
        file_path = self.output_dir / filename
        
        # Write content based on format
        if report.metadata.format in [ReportFormat.HTML, ReportFormat.MARKDOWN, ReportFormat.JSON]:
            mode = 'w'
            encoding = 'utf-8'
        else:
            mode = 'wb'
            encoding = None
        
        with open(file_path, mode, encoding=encoding) as f:
            f.write(report.content)
        
        logger.info(f"Report saved: {file_path}")
        return str(file_path)
    
    async def generate_scheduled_reports(self) -> List[GeneratedReport]:
        """Generate scheduled reports for all templates"""
        
        # Get all active templates
        query = "SELECT id, name FROM templates WHERE active = true"
        templates = await self.db_manager.fetch_all(query)
        
        reports = []
        
        for template in templates:
            template_id = template['id']
            
            try:
                # Generate executive summary for each template
                report = await self.generate_executive_summary(
                    template_id=template_id,
                    time_range_days=7,  # Weekly reports
                    format=ReportFormat.HTML
                )
                
                # Save report
                await self.save_report(report)
                reports.append(report)
                
                logger.info(f"Generated scheduled report for template {template_id}")
                
            except Exception as e:
                logger.error(f"Failed to generate report for template {template_id}: {e}")
        
        return reports
