"""
Analysis Module
===============

Comprehensive data analysis capabilities for the ECaDP platform.
Provides data quality assessment, trend analysis, and report generation.
"""

# Legacy imports (maintain compatibility)
from .data_quality import DataQualityAnalyzer, DataQualityMetrics
from .similarity_analysis import SimilarityAnalyzer, SimilarityResult

# New comprehensive analysis components
from .data_analyzer import DataAnalyzer, AnalysisResult
from .quality_checker import (
    QualityChecker, 
    QualityReport, 
    QualityRule, 
    QualityIssue, 
    QualityDimension, 
    QualitySeverity
)
from .trend_analyzer import (
    TrendAnalyzer, 
    TrendAnalysisResult, 
    TrendDirection, 
    TrendSignificance, 
    TrendStatistics,
    SeasonalPattern,
    SeasonalityType,
    Forecast
)
from .report_generator import (
    ReportGenerator, 
    GeneratedReport, 
    ReportSection, 
    ReportMetadata, 
    ReportType, 
    ReportFormat
)

# Legacy compatibility
try:
    from .reports import ReportGenerator as LegacyReportGenerator, ReportType as LegacyReportType
except ImportError:
    # If legacy reports module doesn't exist, use new implementation
    LegacyReportGenerator = ReportGenerator
    LegacyReportType = ReportType

__all__ = [
    # Legacy components (for compatibility)
    "DataQualityAnalyzer",
    "DataQualityMetrics", 
    "SimilarityAnalyzer",
    "SimilarityResult",
    
    # New comprehensive analysis components
    'DataAnalyzer',
    'AnalysisResult',
    
    # Quality Assessment
    'QualityChecker',
    'QualityReport',
    'QualityRule',
    'QualityIssue',
    'QualityDimension',
    'QualitySeverity',
    
    # Trend Analysis
    'TrendAnalyzer',
    'TrendAnalysisResult',
    'TrendDirection',
    'TrendSignificance',
    'TrendStatistics',
    'SeasonalPattern',
    'SeasonalityType',
    'Forecast',
    
    # Report Generation
    'ReportGenerator',
    'GeneratedReport',
    'ReportSection',
    'ReportMetadata',
    'ReportType',
    'ReportFormat',
    
    # Legacy aliases
    'LegacyReportGenerator',
    'LegacyReportType'
]