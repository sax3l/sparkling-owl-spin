"""
Data Analyzer
=============

Comprehensive data analysis engine for the ECaDP platform.
Provides statistical analysis, pattern detection, and insights generation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import asyncio
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

from ..database.manager import DatabaseManager
from ..observability.metrics import metrics_collector

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Result of data analysis"""
    analysis_type: str
    timestamp: datetime
    data_points: int
    results: Dict[str, Any]
    insights: List[str]
    confidence_score: float
    metadata: Dict[str, Any]

class DataAnalyzer:
    """
    Comprehensive data analysis engine
    
    Features:
    - Statistical analysis of extracted data
    - Pattern detection and anomaly identification
    - Performance trend analysis
    - Data quality assessment
    - Insight generation
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Analysis configuration
        self.min_data_points = 10
        self.confidence_threshold = 0.7
        self.anomaly_threshold = 2.0  # Standard deviations
        
        # Cache for analysis results
        self.analysis_cache = {}
        self.cache_duration = timedelta(hours=1)
    
    async def analyze_extraction_patterns(self, time_range_days: int = 30) -> AnalysisResult:
        """Analyze patterns in data extraction"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get extraction data
        query = """
        SELECT 
            e.id,
            e.template_id,
            e.status,
            e.data,
            e.processing_time,
            e.created_at,
            t.name as template_name,
            t.version as template_version
        FROM extractions e
        JOIN templates t ON e.template_id = t.id
        WHERE e.created_at >= %s
        ORDER BY e.created_at
        """
        
        extractions = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        if len(extractions) < self.min_data_points:
            return AnalysisResult(
                analysis_type="extraction_patterns",
                timestamp=datetime.utcnow(),
                data_points=len(extractions),
                results={},
                insights=[f"Insufficient data: only {len(extractions)} extractions found"],
                confidence_score=0.0,
                metadata={"time_range_days": time_range_days}
            )
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(extractions)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['processing_time'] = pd.to_numeric(df['processing_time'], errors='coerce')
        
        # Analyze patterns
        patterns = {}
        insights = []
        
        # 1. Extraction volume patterns
        daily_counts = df.groupby(df['created_at'].dt.date).size()
        patterns['daily_extraction_stats'] = {
            'mean': float(daily_counts.mean()),
            'std': float(daily_counts.std()),
            'min': int(daily_counts.min()),
            'max': int(daily_counts.max()),
            'trend': self._calculate_trend(daily_counts.values)
        }
        
        if patterns['daily_extraction_stats']['trend'] > 0.1:
            insights.append("Extraction volume is increasing over time")
        elif patterns['daily_extraction_stats']['trend'] < -0.1:
            insights.append("Extraction volume is decreasing over time")
        
        # 2. Success rate patterns
        success_rate = (df['status'] == 'completed').mean()
        patterns['success_rate'] = float(success_rate)
        
        if success_rate < 0.8:
            insights.append(f"Low success rate detected: {success_rate:.1%}")
        
        # 3. Processing time patterns
        if df['processing_time'].notna().any():
            processing_times = df['processing_time'].dropna()
            patterns['processing_time_stats'] = {
                'mean': float(processing_times.mean()),
                'median': float(processing_times.median()),
                'std': float(processing_times.std()),
                'p95': float(processing_times.quantile(0.95))
            }
            
            # Detect anomalies in processing time
            anomalies = self._detect_anomalies(processing_times.values)
            if len(anomalies) > 0:
                patterns['processing_time_anomalies'] = len(anomalies)
                insights.append(f"Detected {len(anomalies)} processing time anomalies")
        
        # 4. Template usage patterns
        template_usage = df['template_name'].value_counts()
        patterns['template_usage'] = {
            'most_used': template_usage.index[0] if len(template_usage) > 0 else None,
            'usage_distribution': template_usage.to_dict(),
            'template_count': len(template_usage)
        }
        
        # 5. Hourly patterns
        hourly_counts = df.groupby(df['created_at'].dt.hour).size()
        peak_hour = hourly_counts.idxmax()
        patterns['hourly_patterns'] = {
            'peak_hour': int(peak_hour),
            'peak_count': int(hourly_counts.max()),
            'distribution': hourly_counts.to_dict()
        }
        
        insights.append(f"Peak extraction hour: {peak_hour}:00")
        
        # Calculate confidence score
        confidence = min(1.0, len(extractions) / 100)  # More data = higher confidence
        
        return AnalysisResult(
            analysis_type="extraction_patterns",
            timestamp=datetime.utcnow(),
            data_points=len(extractions),
            results=patterns,
            insights=insights,
            confidence_score=confidence,
            metadata={"time_range_days": time_range_days}
        )
    
    async def analyze_data_completeness(self, template_id: Optional[int] = None) -> AnalysisResult:
        """Analyze completeness of extracted data"""
        
        # Build query based on whether template_id is specified
        if template_id:
            query = """
            SELECT e.data, t.fields, t.name as template_name
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.template_id = %s AND e.status = 'completed'
            ORDER BY e.created_at DESC
            LIMIT 1000
            """
            params = (template_id,)
        else:
            query = """
            SELECT e.data, t.fields, t.name as template_name
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.status = 'completed'
            ORDER BY e.created_at DESC
            LIMIT 1000
            """
            params = ()
        
        extractions = await self.db_manager.fetch_all(query, params)
        
        if len(extractions) < self.min_data_points:
            return AnalysisResult(
                analysis_type="data_completeness",
                timestamp=datetime.utcnow(),
                data_points=len(extractions),
                results={},
                insights=["Insufficient data for completeness analysis"],
                confidence_score=0.0,
                metadata={"template_id": template_id}
            )
        
        # Analyze completeness by template
        completeness_results = {}
        insights = []
        
        for extraction in extractions:
            template_name = extraction['template_name']
            data = extraction.get('data', {})
            expected_fields = extraction.get('fields', {})
            
            if template_name not in completeness_results:
                completeness_results[template_name] = {
                    'total_extractions': 0,
                    'field_completeness': defaultdict(int),
                    'expected_fields': set(),
                    'average_completeness': 0.0
                }
            
            result = completeness_results[template_name]
            result['total_extractions'] += 1
            
            # Add expected fields
            if isinstance(expected_fields, dict):
                result['expected_fields'].update(expected_fields.keys())
            
            # Check field completeness
            extracted_fields = set(data.keys()) if isinstance(data, dict) else set()
            
            for field in result['expected_fields']:
                if field in extracted_fields and data.get(field) is not None:
                    result['field_completeness'][field] += 1
        
        # Calculate completeness percentages
        overall_completeness = []
        
        for template_name, result in completeness_results.items():
            total = result['total_extractions']
            
            if total > 0:
                # Calculate per-field completeness
                field_percentages = {}
                for field, count in result['field_completeness'].items():
                    percentage = (count / total) * 100
                    field_percentages[field] = percentage
                
                # Calculate average completeness
                if field_percentages:
                    avg_completeness = sum(field_percentages.values()) / len(field_percentages)
                    result['average_completeness'] = avg_completeness
                    result['field_completeness_percentages'] = field_percentages
                    overall_completeness.append(avg_completeness)
                    
                    # Generate insights
                    if avg_completeness < 70:
                        insights.append(f"Low completeness for {template_name}: {avg_completeness:.1f}%")
                    
                    # Identify problematic fields
                    low_completeness_fields = [
                        field for field, pct in field_percentages.items() if pct < 50
                    ]
                    if low_completeness_fields:
                        insights.append(f"Fields with low completeness in {template_name}: {', '.join(low_completeness_fields)}")
        
        # Overall statistics
        if overall_completeness:
            overall_avg = sum(overall_completeness) / len(overall_completeness)
            insights.append(f"Overall average completeness: {overall_avg:.1f}%")
        
        confidence = min(1.0, len(extractions) / 50)
        
        return AnalysisResult(
            analysis_type="data_completeness",
            timestamp=datetime.utcnow(),
            data_points=len(extractions),
            results=completeness_results,
            insights=insights,
            confidence_score=confidence,
            metadata={"template_id": template_id}
        )
    
    async def analyze_performance_trends(self, time_range_days: int = 30) -> AnalysisResult:
        """Analyze performance trends over time"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get performance data
        query = """
        SELECT 
            DATE(created_at) as date,
            AVG(processing_time) as avg_processing_time,
            COUNT(*) as extraction_count,
            AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate,
            template_id
        FROM extractions
        WHERE created_at >= %s AND processing_time IS NOT NULL
        GROUP BY DATE(created_at), template_id
        ORDER BY date
        """
        
        performance_data = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        if len(performance_data) < self.min_data_points:
            return AnalysisResult(
                analysis_type="performance_trends",
                timestamp=datetime.utcnow(),
                data_points=len(performance_data),
                results={},
                insights=["Insufficient data for trend analysis"],
                confidence_score=0.0,
                metadata={"time_range_days": time_range_days}
            )
        
        # Convert to DataFrame
        df = pd.DataFrame(performance_data)
        df['date'] = pd.to_datetime(df['date'])
        
        trends = {}
        insights = []
        
        # 1. Processing time trends
        daily_avg_time = df.groupby('date')['avg_processing_time'].mean()
        processing_time_trend = self._calculate_trend(daily_avg_time.values)
        
        trends['processing_time'] = {
            'trend_slope': processing_time_trend,
            'current_avg': float(daily_avg_time.iloc[-1]) if len(daily_avg_time) > 0 else 0,
            'initial_avg': float(daily_avg_time.iloc[0]) if len(daily_avg_time) > 0 else 0,
            'improvement_percentage': self._calculate_improvement(daily_avg_time.values)
        }
        
        if processing_time_trend > 0.1:
            insights.append("Processing time is increasing (performance degrading)")
        elif processing_time_trend < -0.1:
            insights.append("Processing time is decreasing (performance improving)")
        
        # 2. Volume trends
        daily_volume = df.groupby('date')['extraction_count'].sum()
        volume_trend = self._calculate_trend(daily_volume.values)
        
        trends['volume'] = {
            'trend_slope': volume_trend,
            'current_avg': float(daily_volume.iloc[-1]) if len(daily_volume) > 0 else 0,
            'growth_rate': volume_trend * 100  # Percentage
        }
        
        if volume_trend > 0.1:
            insights.append("Extraction volume is growing")
        elif volume_trend < -0.1:
            insights.append("Extraction volume is declining")
        
        # 3. Success rate trends
        daily_success_rate = df.groupby('date')['success_rate'].mean()
        success_trend = self._calculate_trend(daily_success_rate.values)
        
        trends['success_rate'] = {
            'trend_slope': success_trend,
            'current_rate': float(daily_success_rate.iloc[-1]) if len(daily_success_rate) > 0 else 0,
            'average_rate': float(daily_success_rate.mean())
        }
        
        if success_trend < -0.05:
            insights.append("Success rate is declining")
        elif success_trend > 0.05:
            insights.append("Success rate is improving")
        
        # 4. Identify performance bottlenecks
        bottlenecks = []
        
        # High processing time templates
        avg_time_by_template = df.groupby('template_id')['avg_processing_time'].mean()
        slow_templates = avg_time_by_template[avg_time_by_template > avg_time_by_template.quantile(0.9)]
        
        if len(slow_templates) > 0:
            bottlenecks.extend([f"Template {tid} has high processing time" for tid in slow_templates.index])
        
        trends['bottlenecks'] = bottlenecks
        insights.extend(bottlenecks)
        
        confidence = min(1.0, len(performance_data) / 30)
        
        return AnalysisResult(
            analysis_type="performance_trends",
            timestamp=datetime.utcnow(),
            data_points=len(performance_data),
            results=trends,
            insights=insights,
            confidence_score=confidence,
            metadata={"time_range_days": time_range_days}
        )
    
    async def analyze_data_quality_metrics(self, template_id: Optional[int] = None) -> AnalysisResult:
        """Analyze data quality metrics"""
        
        # Get recent extractions
        if template_id:
            query = """
            SELECT e.*, t.name as template_name, t.fields
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.template_id = %s AND e.status = 'completed'
            ORDER BY e.created_at DESC
            LIMIT 500
            """
            params = (template_id,)
        else:
            query = """
            SELECT e.*, t.name as template_name, t.fields
            FROM extractions e
            JOIN templates t ON e.template_id = t.id
            WHERE e.status = 'completed'
            ORDER BY e.created_at DESC
            LIMIT 500
            """
            params = ()
        
        extractions = await self.db_manager.fetch_all(query, params)
        
        if len(extractions) < self.min_data_points:
            return AnalysisResult(
                analysis_type="data_quality",
                timestamp=datetime.utcnow(),
                data_points=len(extractions),
                results={},
                insights=["Insufficient data for quality analysis"],
                confidence_score=0.0,
                metadata={"template_id": template_id}
            )
        
        quality_metrics = {}
        insights = []
        
        for extraction in extractions:
            template_name = extraction['template_name']
            data = extraction.get('data', {})
            
            if template_name not in quality_metrics:
                quality_metrics[template_name] = {
                    'total_records': 0,
                    'null_values': defaultdict(int),
                    'empty_strings': defaultdict(int),
                    'data_types': defaultdict(lambda: defaultdict(int)),
                    'value_lengths': defaultdict(list),
                    'duplicate_detection': defaultdict(set)
                }
            
            metrics = quality_metrics[template_name]
            metrics['total_records'] += 1
            
            if isinstance(data, dict):
                for field, value in data.items():
                    # Check for null/empty values
                    if value is None:
                        metrics['null_values'][field] += 1
                    elif isinstance(value, str) and value.strip() == '':
                        metrics['empty_strings'][field] += 1
                    
                    # Track data types
                    value_type = type(value).__name__
                    metrics['data_types'][field][value_type] += 1
                    
                    # Track value lengths for strings
                    if isinstance(value, str):
                        metrics['value_lengths'][field].append(len(value))
                    
                    # Track for duplicate detection
                    if value is not None:
                        metrics['duplicate_detection'][field].add(str(value))
        
        # Calculate quality scores
        quality_results = {}
        
        for template_name, metrics in quality_metrics.items():
            total = metrics['total_records']
            
            if total > 0:
                quality_score = {}
                
                # Calculate completeness (inverse of null rate)
                null_rates = {
                    field: (count / total) * 100
                    for field, count in metrics['null_values'].items()
                }
                avg_completeness = 100 - (sum(null_rates.values()) / len(null_rates)) if null_rates else 100
                quality_score['completeness'] = avg_completeness
                
                # Calculate consistency (dominant data type percentage)
                consistency_scores = []
                for field, type_counts in metrics['data_types'].items():
                    if type_counts:
                        dominant_type_count = max(type_counts.values())
                        consistency = (dominant_type_count / total) * 100
                        consistency_scores.append(consistency)
                
                avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 100
                quality_score['consistency'] = avg_consistency
                
                # Calculate uniqueness (for applicable fields)
                uniqueness_scores = []
                for field, unique_values in metrics['duplicate_detection'].items():
                    uniqueness = (len(unique_values) / total) * 100
                    uniqueness_scores.append(min(100, uniqueness))  # Cap at 100%
                
                avg_uniqueness = sum(uniqueness_scores) / len(uniqueness_scores) if uniqueness_scores else 100
                quality_score['uniqueness'] = avg_uniqueness
                
                # Overall quality score (weighted average)
                overall_quality = (
                    avg_completeness * 0.4 +
                    avg_consistency * 0.3 +
                    avg_uniqueness * 0.3
                )
                quality_score['overall'] = overall_quality
                
                quality_results[template_name] = {
                    'scores': quality_score,
                    'details': {
                        'null_rates': null_rates,
                        'total_records': total,
                        'field_analysis': {
                            field: {
                                'avg_length': statistics.mean(lengths) if lengths else 0,
                                'unique_values': len(metrics['duplicate_detection'][field])
                            }
                            for field, lengths in metrics['value_lengths'].items()
                        }
                    }
                }
                
                # Generate insights
                if overall_quality < 70:
                    insights.append(f"Low overall quality for {template_name}: {overall_quality:.1f}%")
                
                if avg_completeness < 80:
                    insights.append(f"Completeness issues in {template_name}: {avg_completeness:.1f}%")
                
                if avg_consistency < 90:
                    insights.append(f"Data type inconsistencies in {template_name}: {avg_consistency:.1f}%")
        
        confidence = min(1.0, len(extractions) / 100)
        
        return AnalysisResult(
            analysis_type="data_quality",
            timestamp=datetime.utcnow(),
            data_points=len(extractions),
            results=quality_results,
            insights=insights,
            confidence_score=confidence,
            metadata={"template_id": template_id}
        )
    
    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calculate trend slope using linear regression"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        
        try:
            # Calculate linear trend
            slope = np.polyfit(x, values, 1)[0]
            
            # Normalize by the mean to get relative trend
            mean_value = np.mean(values)
            if mean_value != 0:
                normalized_slope = slope / mean_value
            else:
                normalized_slope = 0.0
            
            return float(normalized_slope)
        except:
            return 0.0
    
    def _calculate_improvement(self, values: np.ndarray) -> float:
        """Calculate improvement percentage from first to last value"""
        if len(values) < 2:
            return 0.0
        
        first, last = values[0], values[-1]
        
        if first != 0:
            improvement = ((first - last) / first) * 100  # Positive = improvement (time decreased)
        else:
            improvement = 0.0
        
        return float(improvement)
    
    def _detect_anomalies(self, values: np.ndarray, threshold: float = None) -> List[int]:
        """Detect anomalies using standard deviation method"""
        if threshold is None:
            threshold = self.anomaly_threshold
        
        if len(values) < 3:
            return []
        
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return []
        
        anomalies = []
        for i, value in enumerate(values):
            z_score = abs((value - mean_val) / std_val)
            if z_score > threshold:
                anomalies.append(i)
        
        return anomalies
    
    async def generate_insights_summary(self, analyses: List[AnalysisResult]) -> Dict[str, Any]:
        """Generate a comprehensive insights summary from multiple analyses"""
        
        all_insights = []
        high_confidence_insights = []
        
        analysis_summary = {
            'total_analyses': len(analyses),
            'successful_analyses': 0,
            'total_data_points': 0,
            'average_confidence': 0.0
        }
        
        for analysis in analyses:
            analysis_summary['total_data_points'] += analysis.data_points
            
            if analysis.results:
                analysis_summary['successful_analyses'] += 1
            
            all_insights.extend(analysis.insights)
            
            if analysis.confidence_score >= self.confidence_threshold:
                high_confidence_insights.extend(analysis.insights)
        
        if len(analyses) > 0:
            analysis_summary['average_confidence'] = sum(a.confidence_score for a in analyses) / len(analyses)
        
        # Categorize insights
        categorized_insights = {
            'performance': [i for i in all_insights if any(word in i.lower() for word in ['processing', 'time', 'performance', 'slow'])],
            'quality': [i for i in all_insights if any(word in i.lower() for word in ['quality', 'completeness', 'consistency', 'null'])],
            'volume': [i for i in all_insights if any(word in i.lower() for word in ['volume', 'extraction', 'count'])],
            'trends': [i for i in all_insights if any(word in i.lower() for word in ['increasing', 'decreasing', 'trend', 'growing'])]
        }
        
        return {
            'summary': analysis_summary,
            'all_insights': all_insights,
            'high_confidence_insights': high_confidence_insights,
            'categorized_insights': categorized_insights,
            'recommendations': self._generate_recommendations(categorized_insights)
        }
    
    def _generate_recommendations(self, categorized_insights: Dict[str, List[str]]) -> List[str]:
        """Generate actionable recommendations based on insights"""
        
        recommendations = []
        
        # Performance recommendations
        if categorized_insights['performance']:
            recommendations.append("Consider optimizing slow templates or increasing processing resources")
        
        # Quality recommendations
        if categorized_insights['quality']:
            recommendations.append("Review template selectors for fields with low completeness")
            recommendations.append("Implement data validation rules to improve consistency")
        
        # Volume recommendations
        if any('declining' in insight.lower() for insight in categorized_insights['volume']):
            recommendations.append("Investigate causes of declining extraction volume")
        
        # Trend recommendations
        if any('degrading' in insight.lower() for insight in categorized_insights['trends']):
            recommendations.append("Monitor system resources and consider scaling infrastructure")
        
        return recommendations
