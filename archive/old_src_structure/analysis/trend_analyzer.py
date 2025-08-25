"""
Trend Analyzer
==============

Advanced trend analysis engine for the ECaDP platform.
Provides statistical trend detection, forecasting, and pattern analysis.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import asyncio
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import statistics
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    
try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

import warnings

from ..database.manager import DatabaseManager
from ..observability.metrics import metrics_collector

# Suppress sklearn warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    """Trend direction classifications"""
    STRONG_INCREASE = "strong_increase"
    MODERATE_INCREASE = "moderate_increase"
    SLIGHT_INCREASE = "slight_increase"
    STABLE = "stable"
    SLIGHT_DECREASE = "slight_decrease"
    MODERATE_DECREASE = "moderate_decrease"
    STRONG_DECREASE = "strong_decrease"

class TrendSignificance(Enum):
    """Statistical significance levels"""
    HIGHLY_SIGNIFICANT = "highly_significant"  # p < 0.01
    SIGNIFICANT = "significant"  # p < 0.05
    MARGINALLY_SIGNIFICANT = "marginally_significant"  # p < 0.1
    NOT_SIGNIFICANT = "not_significant"  # p >= 0.1

class SeasonalityType(Enum):
    """Types of seasonal patterns"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    NO_SEASONALITY = "no_seasonality"

@dataclass
class TrendStatistics:
    """Statistical measures of a trend"""
    slope: float
    intercept: float
    r_squared: float
    p_value: float
    std_error: float
    confidence_interval: Tuple[float, float]
    direction: TrendDirection
    significance: TrendSignificance

@dataclass
class SeasonalPattern:
    """Seasonal pattern information"""
    type: SeasonalityType
    strength: float  # 0-1 scale
    peak_periods: List[int]
    trough_periods: List[int]
    cycle_length: int
    amplitude: float

@dataclass
class Forecast:
    """Trend forecast results"""
    forecast_horizon: int
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    forecast_accuracy: Optional[float]
    methodology: str

@dataclass
class TrendAnalysisResult:
    """Comprehensive trend analysis result"""
    metric_name: str
    analysis_period: Tuple[datetime, datetime]
    data_points: int
    
    # Core trend analysis
    trend_statistics: TrendStatistics
    seasonal_patterns: List[SeasonalPattern]
    
    # Change point detection
    change_points: List[datetime]
    
    # Forecasting
    forecast: Optional[Forecast]
    
    # Anomaly detection
    anomalies: List[Tuple[datetime, float, str]]
    
    # Insights and recommendations
    insights: List[str]
    recommendations: List[str]
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

class TrendAnalyzer:
    """
    Advanced trend analysis engine
    
    Features:
    - Statistical trend detection with significance testing
    - Seasonal pattern recognition
    - Change point detection
    - Time series forecasting
    - Anomaly detection in trends
    - Multi-metric comparative analysis
    - Confidence intervals and uncertainty quantification
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
        # Analysis configuration
        self.min_data_points = 10
        self.significance_levels = {
            TrendSignificance.HIGHLY_SIGNIFICANT: 0.01,
            TrendSignificance.SIGNIFICANT: 0.05,
            TrendSignificance.MARGINALLY_SIGNIFICANT: 0.1
        }
        
        # Trend classification thresholds
        self.trend_thresholds = {
            'strong': 0.05,  # 5% change per period
            'moderate': 0.02,  # 2% change per period
            'slight': 0.005   # 0.5% change per period
        }
        
        # Seasonality detection parameters
        self.seasonality_min_strength = 0.1
        self.seasonality_confidence = 0.95
    
    async def analyze_extraction_trends(self, time_range_days: int = 90, 
                                      template_id: Optional[int] = None) -> TrendAnalysisResult:
        """Analyze trends in extraction volume and performance"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get daily extraction data
        if template_id:
            query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as extraction_count,
                AVG(processing_time) as avg_processing_time,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate
            FROM extractions
            WHERE created_at >= %s AND template_id = %s
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            params = (cutoff_date, template_id)
        else:
            query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as extraction_count,
                AVG(processing_time) as avg_processing_time,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate
            FROM extractions
            WHERE created_at >= %s
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            params = (cutoff_date,)
        
        data = await self.db_manager.fetch_all(query, params)
        
        if len(data) < self.min_data_points:
            return self._create_insufficient_data_result("extraction_volume", cutoff_date, len(data))
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Analyze extraction volume trends
        return await self._analyze_time_series(
            df['extraction_count'].values,
            df.index.to_pydatetime(),
            "extraction_volume",
            template_id
        )
    
    async def analyze_performance_trends(self, time_range_days: int = 90,
                                       template_id: Optional[int] = None) -> TrendAnalysisResult:
        """Analyze trends in processing performance"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get hourly performance data
        if template_id:
            query = """
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                AVG(processing_time) as avg_processing_time,
                COUNT(*) as extraction_count
            FROM extractions
            WHERE created_at >= %s AND template_id = %s AND processing_time IS NOT NULL
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
            """
            params = (cutoff_date, template_id)
        else:
            query = """
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                AVG(processing_time) as avg_processing_time,
                COUNT(*) as extraction_count
            FROM extractions
            WHERE created_at >= %s AND processing_time IS NOT NULL
            GROUP BY DATE_TRUNC('hour', created_at)
            ORDER BY hour
            """
            params = (cutoff_date,)
        
        data = await self.db_manager.fetch_all(query, params)
        
        if len(data) < self.min_data_points:
            return self._create_insufficient_data_result("processing_performance", cutoff_date, len(data))
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['hour'] = pd.to_datetime(df['hour'])
        df.set_index('hour', inplace=True)
        
        # Analyze processing time trends
        return await self._analyze_time_series(
            df['avg_processing_time'].values,
            df.index.to_pydatetime(),
            "processing_performance",
            template_id
        )
    
    async def analyze_quality_trends(self, time_range_days: int = 90,
                                   template_id: Optional[int] = None) -> TrendAnalysisResult:
        """Analyze trends in data quality metrics"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get daily quality metrics (approximated from extraction success rates)
        if template_id:
            query = """
            SELECT 
                DATE(created_at) as date,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate,
                COUNT(*) as total_extractions
            FROM extractions
            WHERE created_at >= %s AND template_id = %s
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            params = (cutoff_date, template_id)
        else:
            query = """
            SELECT 
                DATE(created_at) as date,
                AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate,
                COUNT(*) as total_extractions
            FROM extractions
            WHERE created_at >= %s
            GROUP BY DATE(created_at)
            ORDER BY date
            """
            params = (cutoff_date,)
        
        data = await self.db_manager.fetch_all(query, params)
        
        if len(data) < self.min_data_points:
            return self._create_insufficient_data_result("quality_trends", cutoff_date, len(data))
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Convert success rate to percentage
        success_rate_pct = df['success_rate'].values * 100
        
        return await self._analyze_time_series(
            success_rate_pct,
            df.index.to_pydatetime(),
            "quality_trends",
            template_id
        )
    
    async def compare_template_trends(self, time_range_days: int = 90) -> Dict[str, Any]:
        """Compare trends across different templates"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=time_range_days)
        
        # Get template performance data
        query = """
        SELECT 
            t.id as template_id,
            t.name as template_name,
            DATE(e.created_at) as date,
            COUNT(*) as extraction_count,
            AVG(e.processing_time) as avg_processing_time,
            AVG(CASE WHEN e.status = 'completed' THEN 1 ELSE 0 END) as success_rate
        FROM extractions e
        JOIN templates t ON e.template_id = t.id
        WHERE e.created_at >= %s
        GROUP BY t.id, t.name, DATE(e.created_at)
        ORDER BY t.id, date
        """
        
        data = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        if not data:
            return {'error': 'No data available for comparison'}
        
        # Group by template
        template_data = defaultdict(list)
        for row in data:
            template_data[row['template_id']].append(row)
        
        # Analyze trends for each template
        comparison_results = {}
        
        for template_id, template_rows in template_data.items():
            if len(template_rows) < self.min_data_points:
                continue
            
            template_name = template_rows[0]['template_name']
            
            # Extract metrics
            dates = [row['date'] for row in template_rows]
            volumes = [row['extraction_count'] for row in template_rows]
            processing_times = [row['avg_processing_time'] for row in template_rows if row['avg_processing_time']]
            success_rates = [row['success_rate'] * 100 for row in template_rows]
            
            # Analyze volume trend
            volume_trend = self._calculate_simple_trend(volumes)
            
            # Analyze performance trend
            performance_trend = None
            if processing_times:
                performance_trend = self._calculate_simple_trend(processing_times)
            
            # Analyze quality trend
            quality_trend = self._calculate_simple_trend(success_rates)
            
            comparison_results[template_id] = {
                'template_name': template_name,
                'data_points': len(template_rows),
                'trends': {
                    'volume': volume_trend,
                    'performance': performance_trend,
                    'quality': quality_trend
                },
                'current_metrics': {
                    'daily_volume': volumes[-1] if volumes else 0,
                    'avg_processing_time': processing_times[-1] if processing_times else None,
                    'success_rate': success_rates[-1] if success_rates else 0
                }
            }
        
        # Generate comparative insights
        insights = self._generate_comparative_insights(comparison_results)
        
        return {
            'analysis_period': {
                'start': cutoff_date.isoformat(),
                'end': datetime.utcnow().isoformat(),
                'days': time_range_days
            },
            'templates_analyzed': len(comparison_results),
            'results': comparison_results,
            'insights': insights
        }
    
    async def _analyze_time_series(self, values: np.ndarray, timestamps: List[datetime],
                                 metric_name: str, template_id: Optional[int] = None) -> TrendAnalysisResult:
        """Perform comprehensive time series analysis"""
        
        # Basic statistics
        if len(values) < self.min_data_points:
            return self._create_insufficient_data_result(metric_name, timestamps[0], len(values))
        
        # 1. Trend Analysis
        trend_stats = self._calculate_trend_statistics(values, timestamps)
        
        # 2. Seasonal Pattern Detection
        seasonal_patterns = self._detect_seasonal_patterns(values, timestamps)
        
        # 3. Change Point Detection
        change_points = self._detect_change_points(values, timestamps)
        
        # 4. Anomaly Detection
        anomalies = self._detect_anomalies_in_trend(values, timestamps)
        
        # 5. Forecasting
        forecast = self._generate_forecast(values, timestamps)
        
        # 6. Generate Insights
        insights = self._generate_trend_insights(trend_stats, seasonal_patterns, change_points, anomalies)
        
        # 7. Generate Recommendations
        recommendations = self._generate_trend_recommendations(trend_stats, seasonal_patterns, forecast)
        
        return TrendAnalysisResult(
            metric_name=metric_name,
            analysis_period=(timestamps[0], timestamps[-1]),
            data_points=len(values),
            trend_statistics=trend_stats,
            seasonal_patterns=seasonal_patterns,
            change_points=change_points,
            forecast=forecast,
            anomalies=anomalies,
            insights=insights,
            recommendations=recommendations,
            metadata={
                'template_id': template_id,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def _calculate_trend_statistics(self, values: np.ndarray, timestamps: List[datetime]) -> TrendStatistics:
        """Calculate comprehensive trend statistics"""
        
        # Convert timestamps to numeric values (days since first timestamp)
        first_timestamp = timestamps[0]
        x = np.array([(ts - first_timestamp).days for ts in timestamps])
        y = values
        
        if SCIPY_AVAILABLE:
            # Linear regression using scipy
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        else:
            # Fallback: simple linear regression
            n = len(x)
            if n < 2:
                slope, intercept, r_value, p_value, std_err = 0, 0, 0, 1, 0
            else:
                sum_x = np.sum(x)
                sum_y = np.sum(y)
                sum_xy = np.sum(x * y)
                sum_x2 = np.sum(x * x)
                sum_y2 = np.sum(y * y)
                
                denom = n * sum_x2 - sum_x * sum_x
                if denom == 0:
                    slope, intercept = 0, np.mean(y)
                else:
                    slope = (n * sum_xy - sum_x * sum_y) / denom
                    intercept = (sum_y - slope * sum_x) / n
                
                # Calculate correlation coefficient
                y_mean = np.mean(y)
                ss_tot = np.sum((y - y_mean) ** 2)
                ss_res = np.sum((y - (slope * x + intercept)) ** 2)
                
                if ss_tot == 0:
                    r_value = 0
                else:
                    r_value = np.sqrt(1 - (ss_res / ss_tot))
                
                # Simple p-value estimation (not as accurate as scipy)
                p_value = 0.05 if abs(r_value) > 0.5 else 0.5
                std_err = 0.1 * abs(slope) if slope != 0 else 0.01
        
        # Confidence interval for slope
        if SCIPY_AVAILABLE:
            t_val = stats.t.ppf(0.975, len(x) - 2)  # 95% confidence
        else:
            t_val = 1.96  # Approximation for large samples
        
        margin_error = t_val * std_err
        conf_interval = (slope - margin_error, slope + margin_error)
        
        # Classify trend direction
        direction = self._classify_trend_direction(slope, np.mean(y))
        
        # Determine significance
        significance = self._determine_significance(p_value)
        
        return TrendStatistics(
            slope=slope,
            intercept=intercept,
            r_squared=r_value ** 2,
            p_value=p_value,
            std_error=std_err,
            confidence_interval=conf_interval,
            direction=direction,
            significance=significance
        )
    
    def _classify_trend_direction(self, slope: float, mean_value: float) -> TrendDirection:
        """Classify trend direction based on slope and magnitude"""
        
        if mean_value == 0:
            return TrendDirection.STABLE
        
        # Calculate relative slope (percentage change per unit time)
        relative_slope = slope / mean_value
        
        if relative_slope > self.trend_thresholds['strong']:
            return TrendDirection.STRONG_INCREASE
        elif relative_slope > self.trend_thresholds['moderate']:
            return TrendDirection.MODERATE_INCREASE
        elif relative_slope > self.trend_thresholds['slight']:
            return TrendDirection.SLIGHT_INCREASE
        elif relative_slope < -self.trend_thresholds['strong']:
            return TrendDirection.STRONG_DECREASE
        elif relative_slope < -self.trend_thresholds['moderate']:
            return TrendDirection.MODERATE_DECREASE
        elif relative_slope < -self.trend_thresholds['slight']:
            return TrendDirection.SLIGHT_DECREASE
        else:
            return TrendDirection.STABLE
    
    def _determine_significance(self, p_value: float) -> TrendSignificance:
        """Determine statistical significance of trend"""
        
        if p_value < self.significance_levels[TrendSignificance.HIGHLY_SIGNIFICANT]:
            return TrendSignificance.HIGHLY_SIGNIFICANT
        elif p_value < self.significance_levels[TrendSignificance.SIGNIFICANT]:
            return TrendSignificance.SIGNIFICANT
        elif p_value < self.significance_levels[TrendSignificance.MARGINALLY_SIGNIFICANT]:
            return TrendSignificance.MARGINALLY_SIGNIFICANT
        else:
            return TrendSignificance.NOT_SIGNIFICANT
    
    def _detect_seasonal_patterns(self, values: np.ndarray, timestamps: List[datetime]) -> List[SeasonalPattern]:
        """Detect seasonal patterns in the time series"""
        
        patterns = []
        
        if len(values) < 14:  # Need at least 2 weeks of data
            return patterns
        
        # Convert to pandas Series for easier analysis
        ts_series = pd.Series(values, index=pd.to_datetime(timestamps))
        
        # Daily seasonality (if we have hourly data)
        if len(values) > 48:  # At least 2 days of hourly data
            daily_pattern = self._analyze_daily_seasonality(ts_series)
            if daily_pattern:
                patterns.append(daily_pattern)
        
        # Weekly seasonality
        if len(values) > 14:  # At least 2 weeks
            weekly_pattern = self._analyze_weekly_seasonality(ts_series)
            if weekly_pattern:
                patterns.append(weekly_pattern)
        
        return patterns
    
    def _analyze_daily_seasonality(self, ts_series: pd.Series) -> Optional[SeasonalPattern]:
        """Analyze daily seasonal patterns"""
        
        try:
            # Group by hour of day
            hourly_means = ts_series.groupby(ts_series.index.hour).mean()
            
            if len(hourly_means) < 12:  # Need data for at least half the day
                return None
            
            # Calculate seasonality strength using coefficient of variation
            strength = hourly_means.std() / hourly_means.mean() if hourly_means.mean() > 0 else 0
            
            if strength < self.seasonality_min_strength:
                return None
            
            # Find peak and trough hours
            peak_hours = hourly_means.nlargest(3).index.tolist()
            trough_hours = hourly_means.nsmallest(3).index.tolist()
            
            return SeasonalPattern(
                type=SeasonalityType.DAILY,
                strength=min(1.0, strength),
                peak_periods=peak_hours,
                trough_periods=trough_hours,
                cycle_length=24,
                amplitude=hourly_means.max() - hourly_means.min()
            )
        
        except Exception as e:
            logger.warning(f"Error analyzing daily seasonality: {e}")
            return None
    
    def _analyze_weekly_seasonality(self, ts_series: pd.Series) -> Optional[SeasonalPattern]:
        """Analyze weekly seasonal patterns"""
        
        try:
            # Group by day of week
            daily_means = ts_series.groupby(ts_series.index.dayofweek).mean()
            
            if len(daily_means) < 5:  # Need data for at least 5 days
                return None
            
            # Calculate seasonality strength
            strength = daily_means.std() / daily_means.mean() if daily_means.mean() > 0 else 0
            
            if strength < self.seasonality_min_strength:
                return None
            
            # Find peak and trough days (0=Monday, 6=Sunday)
            peak_days = daily_means.nlargest(2).index.tolist()
            trough_days = daily_means.nsmallest(2).index.tolist()
            
            return SeasonalPattern(
                type=SeasonalityType.WEEKLY,
                strength=min(1.0, strength),
                peak_periods=peak_days,
                trough_periods=trough_days,
                cycle_length=7,
                amplitude=daily_means.max() - daily_means.min()
            )
        
        except Exception as e:
            logger.warning(f"Error analyzing weekly seasonality: {e}")
            return None
    
    def _detect_change_points(self, values: np.ndarray, timestamps: List[datetime]) -> List[datetime]:
        """Detect significant change points in the time series"""
        
        change_points = []
        
        if len(values) < 20:  # Need sufficient data
            return change_points
        
        # Simple change point detection using moving averages
        window_size = max(5, len(values) // 10)
        
        # Calculate moving averages
        ma_before = []
        ma_after = []
        
        for i in range(window_size, len(values) - window_size):
            before = np.mean(values[i-window_size:i])
            after = np.mean(values[i:i+window_size])
            ma_before.append(before)
            ma_after.append(after)
        
        # Detect significant changes
        for i, (before, after) in enumerate(zip(ma_before, ma_after)):
            if before > 0:  # Avoid division by zero
                change_magnitude = abs(after - before) / before
                
                if change_magnitude > 0.2:  # 20% change threshold
                    change_point_idx = i + window_size
                    if change_point_idx < len(timestamps):
                        change_points.append(timestamps[change_point_idx])
        
        return change_points
    
    def _detect_anomalies_in_trend(self, values: np.ndarray, timestamps: List[datetime]) -> List[Tuple[datetime, float, str]]:
        """Detect anomalies in the trend"""
        
        anomalies = []
        
        if len(values) < 10:
            return anomalies
        
        # Use modified Z-score for anomaly detection
        median = np.median(values)
        mad = np.median(np.abs(values - median))
        
        if mad == 0:
            return anomalies
        
        modified_z_scores = 0.6745 * (values - median) / mad
        
        # Threshold for anomaly detection
        threshold = 3.5
        
        for i, (timestamp, value, z_score) in enumerate(zip(timestamps, values, modified_z_scores)):
            if abs(z_score) > threshold:
                anomaly_type = "spike" if z_score > 0 else "dip"
                anomalies.append((timestamp, value, f"Statistical {anomaly_type} (z-score: {z_score:.2f})"))
        
        return anomalies
    
    def _generate_forecast(self, values: np.ndarray, timestamps: List[datetime], 
                          horizon: int = 7) -> Optional[Forecast]:
        """Generate trend forecast"""
        
        if len(values) < 10:
            return None
        
        try:
            # Prepare data for forecasting
            x = np.arange(len(values)).reshape(-1, 1)
            y = values
            
            if SKLEARN_AVAILABLE:
                # Use scikit-learn linear regression
                model = LinearRegression()
                model.fit(x, y)
                
                # Generate forecast
                future_x = np.arange(len(values), len(values) + horizon).reshape(-1, 1)
                predicted_values = model.predict(future_x).tolist()
                
                # Calculate prediction intervals
                residuals = y - model.predict(x)
                residual_std = np.std(residuals)
                
                # Calculate R² as forecast accuracy measure
                forecast_accuracy = model.score(x, y)
                methodology = "Linear Regression (scikit-learn)"
            
            else:
                # Fallback: simple linear extrapolation
                if len(values) < 2:
                    return None
                
                # Simple linear trend
                x_simple = np.arange(len(values))
                slope = np.polyfit(x_simple, y, 1)[0]
                intercept = np.polyfit(x_simple, y, 1)[1]
                
                # Generate forecast
                future_x_simple = np.arange(len(values), len(values) + horizon)
                predicted_values = [slope * x + intercept for x in future_x_simple]
                
                # Simple residual calculation
                predicted_current = [slope * x + intercept for x in x_simple]
                residuals = y - np.array(predicted_current)
                residual_std = np.std(residuals)
                
                # Simple R² calculation
                y_mean = np.mean(y)
                ss_tot = np.sum((y - y_mean) ** 2)
                ss_res = np.sum(residuals ** 2)
                forecast_accuracy = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                methodology = "Simple Linear Extrapolation"
            
            # Calculate confidence intervals
            confidence_intervals = []
            for pred in predicted_values:
                lower = pred - 1.96 * residual_std  # 95% confidence interval
                upper = pred + 1.96 * residual_std
                confidence_intervals.append((lower, upper))
            
            return Forecast(
                forecast_horizon=horizon,
                predicted_values=predicted_values,
                confidence_intervals=confidence_intervals,
                forecast_accuracy=forecast_accuracy,
                methodology=methodology
            )
        
        except Exception as e:
            logger.warning(f"Error generating forecast: {e}")
            return None
    
    def _generate_trend_insights(self, trend_stats: TrendStatistics, 
                               seasonal_patterns: List[SeasonalPattern],
                               change_points: List[datetime],
                               anomalies: List[Tuple[datetime, float, str]]) -> List[str]:
        """Generate insights from trend analysis"""
        
        insights = []
        
        # Trend direction insights
        if trend_stats.significance in [TrendSignificance.SIGNIFICANT, TrendSignificance.HIGHLY_SIGNIFICANT]:
            direction_text = trend_stats.direction.value.replace('_', ' ').title()
            confidence = "high" if trend_stats.significance == TrendSignificance.HIGHLY_SIGNIFICANT else "moderate"
            insights.append(f"Statistically significant {direction_text.lower()} trend detected (confidence: {confidence})")
        
        # R-squared insight
        if trend_stats.r_squared > 0.7:
            insights.append(f"Strong trend pattern explains {trend_stats.r_squared:.1%} of the variance")
        elif trend_stats.r_squared > 0.3:
            insights.append(f"Moderate trend pattern explains {trend_stats.r_squared:.1%} of the variance")
        
        # Seasonal pattern insights
        for pattern in seasonal_patterns:
            if pattern.strength > 0.3:
                insights.append(f"Strong {pattern.type.value} seasonality detected (strength: {pattern.strength:.1%})")
        
        # Change point insights
        if len(change_points) > 0:
            insights.append(f"Detected {len(change_points)} significant change points in the trend")
        
        # Anomaly insights
        if len(anomalies) > 0:
            insights.append(f"Identified {len(anomalies)} anomalous data points")
        
        return insights
    
    def _generate_trend_recommendations(self, trend_stats: TrendStatistics,
                                      seasonal_patterns: List[SeasonalPattern],
                                      forecast: Optional[Forecast]) -> List[str]:
        """Generate actionable recommendations based on trend analysis"""
        
        recommendations = []
        
        # Trend-based recommendations
        if trend_stats.direction in [TrendDirection.STRONG_DECREASE, TrendDirection.MODERATE_DECREASE]:
            if trend_stats.significance in [TrendSignificance.SIGNIFICANT, TrendSignificance.HIGHLY_SIGNIFICANT]:
                recommendations.append("Investigate causes of declining trend and implement corrective measures")
        
        elif trend_stats.direction in [TrendDirection.STRONG_INCREASE, TrendDirection.MODERATE_INCREASE]:
            recommendations.append("Monitor capacity to handle continued growth")
        
        # Seasonality-based recommendations
        for pattern in seasonal_patterns:
            if pattern.strength > 0.2:
                if pattern.type == SeasonalityType.DAILY:
                    recommendations.append("Schedule resource allocation based on daily usage patterns")
                elif pattern.type == SeasonalityType.WEEKLY:
                    recommendations.append("Plan maintenance activities during low-activity periods")
        
        # Forecast-based recommendations
        if forecast and forecast.forecast_accuracy > 0.6:
            recommendations.append("Use forecasting model for capacity planning and resource allocation")
        
        return recommendations
    
    def _calculate_simple_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate simple trend metrics for comparison"""
        
        if len(values) < 2:
            return {'direction': 'insufficient_data', 'change_percentage': 0.0}
        
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            change_percentage = 0.0
        else:
            change_percentage = ((last_value - first_value) / first_value) * 100
        
        # Classify direction
        if change_percentage > 10:
            direction = 'strong_increase'
        elif change_percentage > 2:
            direction = 'moderate_increase'
        elif change_percentage > -2:
            direction = 'stable'
        elif change_percentage > -10:
            direction = 'moderate_decrease'
        else:
            direction = 'strong_decrease'
        
        return {
            'direction': direction,
            'change_percentage': change_percentage,
            'first_value': first_value,
            'last_value': last_value
        }
    
    def _generate_comparative_insights(self, comparison_results: Dict[int, Dict[str, Any]]) -> List[str]:
        """Generate insights from template comparison"""
        
        insights = []
        
        if not comparison_results:
            return insights
        
        # Analyze volume trends
        volume_trends = [result['trends']['volume']['direction'] for result in comparison_results.values() 
                        if result['trends']['volume']]
        
        growing_templates = sum(1 for trend in volume_trends if 'increase' in trend)
        declining_templates = sum(1 for trend in volume_trends if 'decrease' in trend)
        
        if growing_templates > declining_templates:
            insights.append(f"{growing_templates} templates showing growth vs {declining_templates} declining")
        elif declining_templates > growing_templates:
            insights.append(f"{declining_templates} templates declining vs {growing_templates} growing")
        
        # Find best and worst performers
        volume_changes = {
            tid: result['trends']['volume']['change_percentage']
            for tid, result in comparison_results.items()
            if result['trends']['volume']
        }
        
        if volume_changes:
            best_performer = max(volume_changes.items(), key=lambda x: x[1])
            worst_performer = min(volume_changes.items(), key=lambda x: x[1])
            
            insights.append(f"Best performing template: {comparison_results[best_performer[0]]['template_name']} (+{best_performer[1]:.1f}%)")
            insights.append(f"Worst performing template: {comparison_results[worst_performer[0]]['template_name']} ({worst_performer[1]:.1f}%)")
        
        return insights
    
    def _create_insufficient_data_result(self, metric_name: str, start_date: datetime, 
                                       data_points: int) -> TrendAnalysisResult:
        """Create result for insufficient data scenarios"""
        
        return TrendAnalysisResult(
            metric_name=metric_name,
            analysis_period=(start_date, datetime.utcnow()),
            data_points=data_points,
            trend_statistics=TrendStatistics(
                slope=0.0,
                intercept=0.0,
                r_squared=0.0,
                p_value=1.0,
                std_error=0.0,
                confidence_interval=(0.0, 0.0),
                direction=TrendDirection.STABLE,
                significance=TrendSignificance.NOT_SIGNIFICANT
            ),
            seasonal_patterns=[],
            change_points=[],
            forecast=None,
            anomalies=[],
            insights=[f"Insufficient data for trend analysis: only {data_points} data points available"],
            recommendations=["Collect more data over a longer time period for meaningful trend analysis"],
            metadata={'insufficient_data': True}
        )
