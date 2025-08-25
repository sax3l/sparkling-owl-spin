#!/usr/bin/env python3
"""
Data Scientist Agent
AI-agent specialiserad på dataanalys och maskininlärning för crawling och säkerhetsdata
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import re
from collections import defaultdict, Counter
import statistics

# Attempt to import ML libraries
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.ensemble import IsolationForest
    sklearn_available = True
except ImportError:
    sklearn_available = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    matplotlib_available = True
except ImportError:
    matplotlib_available = False

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of data analysis"""
    EXPLORATORY_DATA_ANALYSIS = "exploratory_data_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"
    ANOMALY_DETECTION = "anomaly_detection"
    CLUSTERING_ANALYSIS = "clustering_analysis"
    TREND_ANALYSIS = "trend_analysis"
    PREDICTIVE_MODELING = "predictive_modeling"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NETWORK_ANALYSIS = "network_analysis"
    TIME_SERIES_ANALYSIS = "time_series_analysis"

class DataSource(Enum):
    """Data sources for analysis"""
    SCRAPED_DATA = "scraped_data"
    SECURITY_LOGS = "security_logs"
    VULNERABILITY_DATA = "vulnerability_data"
    CRAWL_METRICS = "crawl_metrics"
    USER_BEHAVIOR = "user_behavior"
    NETWORK_TRAFFIC = "network_traffic"
    THREAT_INTELLIGENCE = "threat_intelligence"

class ModelType(Enum):
    """Machine learning model types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    NATURAL_LANGUAGE_PROCESSING = "nlp"
    TIME_SERIES_FORECASTING = "time_series"

@dataclass
class DatasetInfo:
    """Information about a dataset"""
    dataset_id: str
    name: str
    description: str
    source: DataSource
    size: int
    columns: List[str]
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AnalysisRequest:
    """Request for data analysis"""
    request_id: str
    dataset_id: str
    analysis_type: AnalysisType
    parameters: Dict[str, Any] = field(default_factory=dict)
    target_columns: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    output_format: str = "json"  # json, csv, plot
    priority: int = 1  # 1=low, 5=high

@dataclass
class AnalysisResult:
    """Result from data analysis"""
    result_id: str
    request_id: str
    analysis_type: AnalysisType
    success: bool
    insights: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    visualizations: List[str] = field(default_factory=list)
    models: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

class DataScientistAgent:
    """AI-powered data scientist with advanced analytics capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agent_id = self._generate_agent_id()
        self.datasets = {}
        self.analysis_history = []
        self.trained_models = {}
        self.insights_db = {}
        
        # Check ML library availability
        self.ml_enabled = sklearn_available
        self.viz_enabled = matplotlib_available
        
        if not self.ml_enabled:
            logger.warning("scikit-learn not available - ML capabilities limited")
        if not self.viz_enabled:
            logger.warning("matplotlib not available - visualization capabilities limited")
        
        logger.info(f"Data Scientist Agent {self.agent_id} initialized")
    
    async def register_dataset(self, 
                             dataset_id: str,
                             name: str,
                             data: Union[pd.DataFrame, Dict, List],
                             source: DataSource,
                             description: str = "") -> DatasetInfo:
        """Register a new dataset for analysis"""
        
        # Convert data to DataFrame if needed
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Unsupported data format")
        
        # Analyze dataset structure
        dataset_info = DatasetInfo(
            dataset_id=dataset_id,
            name=name,
            description=description,
            source=source,
            size=len(df),
            columns=list(df.columns),
            data_types={col: str(dtype) for col, dtype in df.dtypes.items()},
            missing_values={col: df[col].isnull().sum() for col in df.columns}
        )
        
        # Store dataset
        self.datasets[dataset_id] = {
            'info': dataset_info,
            'data': df
        }
        
        logger.info(f"Registered dataset {dataset_id} with {len(df)} records and {len(df.columns)} columns")
        
        return dataset_info
    
    async def analyze_data(self, request: AnalysisRequest) -> AnalysisResult:
        """Perform data analysis based on request"""
        
        start_time = asyncio.get_event_loop().time()
        
        result = AnalysisResult(
            result_id=self._generate_result_id(),
            request_id=request.request_id,
            analysis_type=request.analysis_type,
            success=False
        )
        
        try:
            # Get dataset
            if request.dataset_id not in self.datasets:
                raise ValueError(f"Dataset {request.dataset_id} not found")
            
            df = self.datasets[request.dataset_id]['data'].copy()
            
            # Apply filters if specified
            if request.filters:
                df = self._apply_filters(df, request.filters)
            
            # Route to appropriate analysis method
            if request.analysis_type == AnalysisType.EXPLORATORY_DATA_ANALYSIS:
                result = await self._exploratory_data_analysis(df, result, request)
            elif request.analysis_type == AnalysisType.PATTERN_RECOGNITION:
                result = await self._pattern_recognition(df, result, request)
            elif request.analysis_type == AnalysisType.ANOMALY_DETECTION:
                result = await self._anomaly_detection(df, result, request)
            elif request.analysis_type == AnalysisType.CLUSTERING_ANALYSIS:
                result = await self._clustering_analysis(df, result, request)
            elif request.analysis_type == AnalysisType.TREND_ANALYSIS:
                result = await self._trend_analysis(df, result, request)
            elif request.analysis_type == AnalysisType.SENTIMENT_ANALYSIS:
                result = await self._sentiment_analysis(df, result, request)
            elif request.analysis_type == AnalysisType.TIME_SERIES_ANALYSIS:
                result = await self._time_series_analysis(df, result, request)
            else:
                result.insights.append(f"Analysis type {request.analysis_type} not yet implemented")
            
            # Generate AI insights
            result = await self._generate_ai_insights(df, result, request)
            
            result.success = True
            
        except Exception as e:
            logger.error(f"Data analysis failed: {e}")
            result.insights.append(f"Analysis failed: {str(e)}")
        
        finally:
            result.execution_time = asyncio.get_event_loop().time() - start_time
            self.analysis_history.append(result)
        
        return result
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataset"""
        
        filtered_df = df.copy()
        
        for column, filter_value in filters.items():
            if column not in filtered_df.columns:
                continue
                
            if isinstance(filter_value, dict):
                # Range filter
                if 'min' in filter_value:
                    filtered_df = filtered_df[filtered_df[column] >= filter_value['min']]
                if 'max' in filter_value:
                    filtered_df = filtered_df[filtered_df[column] <= filter_value['max']]
            elif isinstance(filter_value, list):
                # Include filter
                filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
            else:
                # Exact match filter
                filtered_df = filtered_df[filtered_df[column] == filter_value]
        
        return filtered_df
    
    async def _exploratory_data_analysis(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform exploratory data analysis"""
        
        # Basic statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) > 0:
            desc_stats = df[numeric_columns].describe()
            
            result.metrics['mean_values'] = desc_stats.loc['mean'].to_dict()
            result.metrics['median_values'] = df[numeric_columns].median().to_dict()
            result.metrics['std_values'] = desc_stats.loc['std'].to_dict()
        
        # Data quality assessment
        total_rows = len(df)
        missing_data = df.isnull().sum()
        
        result.metrics['total_rows'] = total_rows
        result.metrics['total_columns'] = len(df.columns)
        result.metrics['missing_data_percentage'] = (missing_data.sum() / (total_rows * len(df.columns))) * 100
        
        # Generate insights
        insights = []
        
        # Missing data insights
        high_missing_cols = missing_data[missing_data > total_rows * 0.1].index
        if len(high_missing_cols) > 0:
            insights.append(f"High missing data in columns: {', '.join(high_missing_cols)} (>10%)")
        
        # Data distribution insights
        for col in numeric_columns[:5]:  # Analyze top 5 numeric columns
            skewness = df[col].skew()
            if abs(skewness) > 1:
                insights.append(f"Column '{col}' is highly skewed ({skewness:.2f})")
        
        # Correlation insights
        if len(numeric_columns) > 1:
            correlation_matrix = df[numeric_columns].corr()
            high_corr_pairs = []
            
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # High correlation threshold
                        high_corr_pairs.append((correlation_matrix.columns[i], 
                                              correlation_matrix.columns[j], 
                                              corr_value))
            
            if high_corr_pairs:
                for col1, col2, corr in high_corr_pairs[:3]:  # Top 3
                    insights.append(f"High correlation between '{col1}' and '{col2}' ({corr:.3f})")
        
        # Unique values insights
        for col in df.select_dtypes(include=['object']).columns[:5]:
            unique_count = df[col].nunique()
            if unique_count == 1:
                insights.append(f"Column '{col}' has only one unique value")
            elif unique_count / total_rows < 0.01:  # Very few unique values
                insights.append(f"Column '{col}' has very few unique values ({unique_count})")
        
        result.insights = insights
        result.confidence_score = 0.9  # High confidence for basic statistics
        
        return result
    
    async def _pattern_recognition(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform pattern recognition analysis"""
        
        insights = []
        patterns_found = {}
        
        # Frequency patterns
        for column in df.select_dtypes(include=['object']).columns[:10]:
            value_counts = df[column].value_counts()
            
            # Top patterns
            top_values = value_counts.head(3)
            if len(top_values) > 0:
                patterns_found[f'{column}_top_values'] = top_values.to_dict()
                
                # Check for dominant pattern (>50%)
                if top_values.iloc[0] / len(df) > 0.5:
                    insights.append(f"Dominant pattern in '{column}': '{top_values.index[0]}' appears in {top_values.iloc[0]/len(df)*100:.1f}% of records")
        
        # Numerical patterns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns[:5]:
            # Check for round numbers (ending in 0 or 5)
            if df[column].dtype in ['int64', 'float64']:
                round_numbers = df[column] % 10 == 0
                round_percentage = round_numbers.sum() / len(df) * 100
                
                if round_percentage > 30:  # More than 30% are round numbers
                    insights.append(f"Pattern detected in '{column}': {round_percentage:.1f}% are round numbers (ending in 0)")
        
        # Time-based patterns (if datetime columns exist)
        datetime_columns = df.select_dtypes(include=['datetime64']).columns
        
        for column in datetime_columns:
            # Day of week patterns
            if hasattr(df[column], 'dt'):
                day_counts = df[column].dt.dayofweek.value_counts()
                most_common_day = day_counts.index[0]
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                insights.append(f"Time pattern in '{column}': Most common day is {day_names[most_common_day]} ({day_counts.iloc[0]} occurrences)")
        
        # Sequential patterns
        if 'id' in df.columns or any('id' in col.lower() for col in df.columns):
            id_cols = [col for col in df.columns if 'id' in col.lower()]
            for id_col in id_cols[:2]:  # Check top 2 ID columns
                if df[id_col].dtype in ['int64']:
                    # Check if IDs are sequential
                    sorted_ids = df[id_col].sort_values().diff().dropna()
                    if (sorted_ids == 1).sum() / len(sorted_ids) > 0.8:  # 80% are incremental by 1
                        insights.append(f"Sequential pattern detected in '{id_col}': IDs are mostly consecutive")
        
        result.insights = insights
        result.metrics = patterns_found
        result.confidence_score = 0.7  # Moderate confidence for pattern recognition
        
        return result
    
    async def _anomaly_detection(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform anomaly detection"""
        
        insights = []
        anomalies_found = {}
        
        if not self.ml_enabled:
            insights.append("Advanced anomaly detection requires scikit-learn - using basic statistical methods")
            
            # Statistical anomaly detection
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns[:5]:
                # Z-score based anomalies
                mean_val = df[column].mean()
                std_val = df[column].std()
                
                if std_val > 0:
                    z_scores = abs((df[column] - mean_val) / std_val)
                    anomalies = z_scores > 3  # More than 3 standard deviations
                    
                    anomaly_count = anomalies.sum()
                    if anomaly_count > 0:
                        insights.append(f"Statistical anomalies in '{column}': {anomaly_count} values beyond 3 standard deviations")
                        anomalies_found[f'{column}_anomalies'] = anomaly_count
            
            result.confidence_score = 0.6  # Lower confidence with basic methods
        
        else:
            # Advanced ML-based anomaly detection
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) >= 2:
                # Prepare data
                X = df[numeric_columns].fillna(df[numeric_columns].mean())
                
                # Standardize features
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Isolation Forest for anomaly detection
                isolation_forest = IsolationForest(contamination=0.1, random_state=42)
                anomaly_predictions = isolation_forest.fit_predict(X_scaled)
                
                # Count anomalies
                anomaly_count = (anomaly_predictions == -1).sum()
                anomaly_percentage = (anomaly_count / len(df)) * 100
                
                insights.append(f"ML-based anomaly detection: {anomaly_count} anomalies detected ({anomaly_percentage:.2f}%)")
                
                # Store anomaly indices
                anomaly_indices = df.index[anomaly_predictions == -1].tolist()
                anomalies_found['anomaly_indices'] = anomaly_indices[:10]  # Top 10
                anomalies_found['total_anomalies'] = anomaly_count
                
                result.confidence_score = 0.85  # High confidence with ML methods
        
        # Text-based anomaly detection for string columns
        text_columns = df.select_dtypes(include=['object']).columns
        
        for column in text_columns[:3]:
            # Check for unusually long/short strings
            lengths = df[column].astype(str).str.len()
            mean_length = lengths.mean()
            std_length = lengths.std()
            
            if std_length > 0:
                length_anomalies = abs(lengths - mean_length) > 2 * std_length
                length_anomaly_count = length_anomalies.sum()
                
                if length_anomaly_count > 0:
                    insights.append(f"Text length anomalies in '{column}': {length_anomaly_count} values with unusual length")
        
        result.insights = insights
        result.metrics = anomalies_found
        
        return result
    
    async def _clustering_analysis(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform clustering analysis"""
        
        insights = []
        clustering_results = {}
        
        if not self.ml_enabled:
            insights.append("Clustering analysis requires scikit-learn - functionality limited")
            result.confidence_score = 0.3
        else:
            # Prepare numeric data for clustering
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) < 2:
                insights.append("Clustering requires at least 2 numeric columns")
                result.confidence_score = 0.2
            else:
                # Fill missing values and standardize
                X = df[numeric_columns].fillna(df[numeric_columns].mean())
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                # Determine optimal number of clusters using elbow method
                max_clusters = min(10, len(df) // 10)  # Reasonable upper limit
                
                if max_clusters >= 2:
                    inertias = []
                    silhouette_scores = []
                    
                    for k in range(2, max_clusters + 1):
                        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                        cluster_labels = kmeans.fit_predict(X_scaled)
                        
                        inertias.append(kmeans.inertia_)
                        sil_score = silhouette_score(X_scaled, cluster_labels)
                        silhouette_scores.append(sil_score)
                    
                    # Choose best k based on silhouette score
                    best_k = range(2, max_clusters + 1)[np.argmax(silhouette_scores)]
                    best_silhouette = max(silhouette_scores)
                    
                    # Final clustering with best k
                    final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
                    cluster_labels = final_kmeans.fit_predict(X_scaled)
                    
                    # Analyze clusters
                    cluster_info = {}
                    for cluster_id in range(best_k):
                        cluster_mask = cluster_labels == cluster_id
                        cluster_size = cluster_mask.sum()
                        cluster_data = df[cluster_mask]
                        
                        # Cluster characteristics
                        cluster_info[f'cluster_{cluster_id}'] = {
                            'size': int(cluster_size),
                            'percentage': float(cluster_size / len(df) * 100),
                            'characteristics': {}
                        }
                        
                        # Find distinguishing features for each cluster
                        for col in numeric_columns:
                            cluster_mean = cluster_data[col].mean()
                            overall_mean = df[col].mean()
                            if abs(cluster_mean - overall_mean) > df[col].std():
                                cluster_info[f'cluster_{cluster_id}']['characteristics'][col] = {
                                    'cluster_mean': float(cluster_mean),
                                    'overall_mean': float(overall_mean),
                                    'difference': float(cluster_mean - overall_mean)
                                }
                    
                    insights.append(f"Identified {best_k} distinct clusters with silhouette score {best_silhouette:.3f}")
                    
                    # Cluster size insights
                    cluster_sizes = [info['size'] for info in cluster_info.values()]
                    largest_cluster = max(cluster_sizes)
                    smallest_cluster = min(cluster_sizes)
                    
                    if largest_cluster / smallest_cluster > 3:  # Imbalanced clusters
                        insights.append(f"Clusters are imbalanced: largest has {largest_cluster} members, smallest has {smallest_cluster}")
                    
                    clustering_results['clusters'] = cluster_info
                    clustering_results['optimal_k'] = best_k
                    clustering_results['silhouette_score'] = float(best_silhouette)
                    
                    result.confidence_score = min(0.9, best_silhouette + 0.4)  # Higher silhouette = higher confidence
                
                else:
                    insights.append("Dataset too small for meaningful clustering analysis")
                    result.confidence_score = 0.2
        
        result.insights = insights
        result.metrics = clustering_results
        
        return result
    
    async def _trend_analysis(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform trend analysis"""
        
        insights = []
        trend_metrics = {}
        
        # Look for datetime columns
        datetime_columns = df.select_dtypes(include=['datetime64']).columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(datetime_columns) == 0:
            # Try to find date-like string columns
            for col in df.select_dtypes(include=['object']).columns:
                if any(keyword in col.lower() for keyword in ['date', 'time', 'created', 'updated']):
                    try:
                        df[col] = pd.to_datetime(df[col])
                        datetime_columns = [col]
                        break
                    except:
                        continue
        
        if len(datetime_columns) == 0:
            insights.append("No datetime columns found - performing sequence-based trend analysis")
            
            # Sequence-based trends for numeric columns
            for column in numeric_columns[:3]:
                values = df[column].dropna()
                if len(values) > 2:
                    # Calculate trend using linear regression
                    x = np.arange(len(values))
                    coeffs = np.polyfit(x, values, 1)
                    trend_slope = coeffs[0]
                    
                    if abs(trend_slope) > values.std() * 0.1:  # Significant trend
                        direction = "increasing" if trend_slope > 0 else "decreasing"
                        insights.append(f"Trend in '{column}': {direction} by {abs(trend_slope):.4f} per record")
                        trend_metrics[f'{column}_trend_slope'] = float(trend_slope)
        else:
            # Time-based trend analysis
            time_col = datetime_columns[0]
            df_sorted = df.sort_values(time_col)
            
            for column in numeric_columns[:5]:
                # Group by time periods for trend analysis
                df_sorted['time_period'] = df_sorted[time_col].dt.floor('D')  # Daily periods
                daily_stats = df_sorted.groupby('time_period')[column].agg(['mean', 'count']).reset_index()
                
                if len(daily_stats) > 2:
                    # Calculate trend
                    x = np.arange(len(daily_stats))
                    y = daily_stats['mean'].values
                    
                    coeffs = np.polyfit(x, y, 1)
                    trend_slope = coeffs[0]
                    
                    if abs(trend_slope) > y.std() * 0.1:
                        direction = "increasing" if trend_slope > 0 else "decreasing"
                        insights.append(f"Daily trend in '{column}': {direction} by {abs(trend_slope):.4f} per day")
                        trend_metrics[f'{column}_daily_trend'] = float(trend_slope)
                
                # Seasonal patterns (if enough data)
                if len(df_sorted) > 30:  # At least 30 data points
                    df_sorted['hour'] = df_sorted[time_col].dt.hour
                    df_sorted['day_of_week'] = df_sorted[time_col].dt.dayofweek
                    
                    # Hourly patterns
                    hourly_mean = df_sorted.groupby('hour')[column].mean()
                    peak_hour = hourly_mean.idxmax()
                    insights.append(f"Peak activity in '{column}' at hour {peak_hour}")
                    
                    # Weekly patterns
                    weekly_mean = df_sorted.groupby('day_of_week')[column].mean()
                    peak_day = weekly_mean.idxmax()
                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    insights.append(f"Peak activity in '{column}' on {day_names[peak_day]}")
        
        result.insights = insights
        result.metrics = trend_metrics
        result.confidence_score = 0.75 if len(datetime_columns) > 0 else 0.6
        
        return result
    
    async def _sentiment_analysis(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform basic sentiment analysis on text columns"""
        
        insights = []
        sentiment_metrics = {}
        
        # Simple sentiment analysis using word lists (since we don't have nltk/textblob)
        positive_words = ['good', 'great', 'excellent', 'awesome', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best', 'perfect']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting', 'annoying', 'stupid', 'useless', 'disappointing']
        
        text_columns = df.select_dtypes(include=['object']).columns
        
        for column in text_columns[:3]:  # Analyze up to 3 text columns
            if df[column].dtype == 'object':
                # Calculate sentiment scores
                sentiments = []
                
                for text in df[column].dropna():
                    if isinstance(text, str):
                        text_lower = text.lower()
                        positive_count = sum(1 for word in positive_words if word in text_lower)
                        negative_count = sum(1 for word in negative_words if word in text_lower)
                        
                        if positive_count > negative_count:
                            sentiment = 1  # Positive
                        elif negative_count > positive_count:
                            sentiment = -1  # Negative
                        else:
                            sentiment = 0  # Neutral
                        
                        sentiments.append(sentiment)
                
                if sentiments:
                    positive_ratio = sentiments.count(1) / len(sentiments)
                    negative_ratio = sentiments.count(-1) / len(sentiments)
                    neutral_ratio = sentiments.count(0) / len(sentiments)
                    
                    insights.append(f"Sentiment in '{column}': {positive_ratio*100:.1f}% positive, {negative_ratio*100:.1f}% negative, {neutral_ratio*100:.1f}% neutral")
                    
                    sentiment_metrics[f'{column}_sentiment'] = {
                        'positive_ratio': float(positive_ratio),
                        'negative_ratio': float(negative_ratio),
                        'neutral_ratio': float(neutral_ratio)
                    }
                    
                    # Overall sentiment insight
                    if positive_ratio > 0.6:
                        insights.append(f"Overall sentiment in '{column}' is predominantly positive")
                    elif negative_ratio > 0.6:
                        insights.append(f"Overall sentiment in '{column}' is predominantly negative")
                    else:
                        insights.append(f"Sentiment in '{column}' is mixed or neutral")
        
        result.insights = insights
        result.metrics = sentiment_metrics
        result.confidence_score = 0.5  # Basic sentiment analysis has moderate confidence
        
        return result
    
    async def _time_series_analysis(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Perform time series analysis"""
        
        insights = []
        ts_metrics = {}
        
        # Find datetime columns
        datetime_columns = df.select_dtypes(include=['datetime64']).columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(datetime_columns) == 0:
            insights.append("No datetime columns found for time series analysis")
            result.confidence_score = 0.2
            return result
        
        time_col = datetime_columns[0]
        df_sorted = df.sort_values(time_col)
        
        for metric_col in numeric_columns[:3]:
            # Basic time series statistics
            ts_data = df_sorted.set_index(time_col)[metric_col].dropna()
            
            if len(ts_data) > 10:
                # Calculate basic metrics
                ts_metrics[f'{metric_col}_mean'] = float(ts_data.mean())
                ts_metrics[f'{metric_col}_std'] = float(ts_data.std())
                ts_metrics[f'{metric_col}_min'] = float(ts_data.min())
                ts_metrics[f'{metric_col}_max'] = float(ts_data.max())
                
                # Detect seasonality (basic)
                if len(ts_data) > 50:
                    # Check for weekly patterns
                    ts_data_with_dow = ts_data.copy()
                    ts_data_with_dow.index = pd.to_datetime(ts_data_with_dow.index)
                    
                    weekly_stats = ts_data_with_dow.groupby(ts_data_with_dow.index.dayofweek).mean()
                    weekly_variation = weekly_stats.std() / weekly_stats.mean()
                    
                    if weekly_variation > 0.1:  # 10% variation
                        insights.append(f"Weekly seasonality detected in '{metric_col}' (variation: {weekly_variation:.2f})")
                
                # Volatility analysis
                returns = ts_data.pct_change().dropna()
                if len(returns) > 1:
                    volatility = returns.std()
                    ts_metrics[f'{metric_col}_volatility'] = float(volatility)
                    
                    if volatility > 0.1:  # High volatility
                        insights.append(f"High volatility in '{metric_col}': {volatility:.3f}")
                
                # Trend analysis
                x = np.arange(len(ts_data))
                coeffs = np.polyfit(x, ts_data.values, 1)
                trend_slope = coeffs[0]
                
                if abs(trend_slope) > ts_data.std() * 0.01:  # Significant trend
                    direction = "upward" if trend_slope > 0 else "downward"
                    insights.append(f"Long-term {direction} trend in '{metric_col}'")
                    ts_metrics[f'{metric_col}_trend'] = float(trend_slope)
        
        result.insights = insights
        result.metrics = ts_metrics
        result.confidence_score = 0.8 if len(datetime_columns) > 0 and len(numeric_columns) > 0 else 0.4
        
        return result
    
    async def _generate_ai_insights(self, df: pd.DataFrame, result: AnalysisResult, request: AnalysisRequest) -> AnalysisResult:
        """Generate additional AI-powered insights"""
        
        ai_insights = []
        
        # Data quality insights
        data_quality_score = self._calculate_data_quality_score(df)
        result.metrics['data_quality_score'] = data_quality_score
        
        if data_quality_score < 0.7:
            ai_insights.append(f"Data quality is moderate ({data_quality_score:.2f}/1.0) - consider data cleaning")
        elif data_quality_score > 0.9:
            ai_insights.append(f"Excellent data quality ({data_quality_score:.2f}/1.0)")
        
        # Dimensionality insights
        n_features = len(df.columns)
        n_samples = len(df)
        
        if n_features > n_samples:
            ai_insights.append("High-dimensional data detected - consider feature selection or dimensionality reduction")
        
        # Imbalance detection for categorical variables
        for column in df.select_dtypes(include=['object']).columns[:5]:
            value_counts = df[column].value_counts()
            if len(value_counts) > 1:
                imbalance_ratio = value_counts.iloc[0] / value_counts.iloc[1]
                if imbalance_ratio > 10:  # Highly imbalanced
                    ai_insights.append(f"Class imbalance detected in '{column}': dominant class is {imbalance_ratio:.1f}x more frequent")
        
        # Recommend analysis types based on data characteristics
        recommendations = []
        
        if len(df.select_dtypes(include=[np.number]).columns) >= 3:
            recommendations.append("Consider clustering analysis to identify natural groupings")
            recommendations.append("Anomaly detection could help identify outliers")
        
        if len(df.select_dtypes(include=['datetime64']).columns) > 0:
            recommendations.append("Time series analysis could reveal temporal patterns")
        
        if len(df.select_dtypes(include=['object']).columns) > 0:
            recommendations.append("Text analysis could extract insights from categorical data")
        
        result.insights.extend(ai_insights)
        result.recommendations.extend(recommendations)
        
        return result
    
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score"""
        
        scores = []
        
        # Completeness score (missing data)
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        scores.append(completeness)
        
        # Consistency score (data types)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        consistency = 1.0  # Default to perfect consistency
        
        for col in numeric_cols:
            # Check for infinite values
            if np.isinf(df[col]).any():
                consistency -= 0.1
        
        scores.append(max(0, consistency))
        
        # Uniqueness score (for potential ID columns)
        uniqueness = 1.0
        for col in df.columns:
            if 'id' in col.lower():
                duplicate_ratio = df[col].duplicated().sum() / len(df)
                uniqueness = min(uniqueness, 1 - duplicate_ratio)
        
        scores.append(uniqueness)
        
        return np.mean(scores)
    
    def get_dataset_summary(self, dataset_id: str) -> Dict[str, Any]:
        """Get summary of registered dataset"""
        
        if dataset_id not in self.datasets:
            return {'error': 'Dataset not found'}
        
        dataset_info = self.datasets[dataset_id]['info']
        df = self.datasets[dataset_id]['data']
        
        # Calculate additional summary statistics
        summary = {
            'basic_info': {
                'dataset_id': dataset_info.dataset_id,
                'name': dataset_info.name,
                'description': dataset_info.description,
                'source': dataset_info.source.value,
                'size': dataset_info.size,
                'columns': len(dataset_info.columns),
                'created_at': dataset_info.created_at.isoformat()
            },
            'data_types': dataset_info.data_types,
            'missing_values': dataset_info.missing_values,
            'column_details': {}
        }
        
        # Add column-specific details
        for column in df.columns:
            col_info = {
                'type': str(df[column].dtype),
                'unique_values': int(df[column].nunique()),
                'missing_count': int(df[column].isnull().sum())
            }
            
            if df[column].dtype in [np.number]:
                col_info.update({
                    'mean': float(df[column].mean()),
                    'std': float(df[column].std()),
                    'min': float(df[column].min()),
                    'max': float(df[column].max())
                })
            
            summary['column_details'][column] = col_info
        
        return summary
    
    def generate_analysis_report(self, request_id: str) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        # Find analysis result
        analysis_result = None
        for result in self.analysis_history:
            if result.request_id == request_id:
                analysis_result = result
                break
        
        if not analysis_result:
            return {'error': 'Analysis result not found'}
        
        report = {
            'analysis_summary': {
                'request_id': request_id,
                'analysis_type': analysis_result.analysis_type.value,
                'success': analysis_result.success,
                'execution_time': analysis_result.execution_time,
                'confidence_score': analysis_result.confidence_score
            },
            'key_insights': analysis_result.insights,
            'metrics': analysis_result.metrics,
            'recommendations': analysis_result.recommendations,
            'generated_at': datetime.now().isoformat()
        }
        
        # Add interpretation based on analysis type
        if analysis_result.analysis_type == AnalysisType.CLUSTERING_ANALYSIS:
            if 'clusters' in analysis_result.metrics:
                cluster_count = len(analysis_result.metrics['clusters'])
                report['interpretation'] = f"Data naturally segments into {cluster_count} distinct groups"
        
        elif analysis_result.analysis_type == AnalysisType.ANOMALY_DETECTION:
            if 'total_anomalies' in analysis_result.metrics:
                anomaly_count = analysis_result.metrics['total_anomalies']
                report['interpretation'] = f"Identified {anomaly_count} anomalous data points requiring investigation"
        
        return report
    
    def _generate_agent_id(self) -> str:
        """Generate unique agent ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"data_scientist_{timestamp}".encode()).hexdigest()[:12]
    
    def _generate_result_id(self) -> str:
        """Generate unique result ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"analysis_{timestamp}".encode()).hexdigest()[:12]

# Convenience functions
async def quick_data_analysis(data: Union[pd.DataFrame, List[Dict]], 
                            analysis_type: AnalysisType = AnalysisType.EXPLORATORY_DATA_ANALYSIS) -> AnalysisResult:
    """Quick data analysis with automatic setup"""
    
    agent = DataScientistAgent()
    
    # Register dataset
    dataset_id = f"quick_analysis_{datetime.now().timestamp()}"
    await agent.register_dataset(
        dataset_id=dataset_id,
        name="Quick Analysis Dataset",
        data=data,
        source=DataSource.SCRAPED_DATA,
        description="Dataset for quick analysis"
    )
    
    # Create analysis request
    request = AnalysisRequest(
        request_id=f"quick_request_{datetime.now().timestamp()}",
        dataset_id=dataset_id,
        analysis_type=analysis_type
    )
    
    # Perform analysis
    return await agent.analyze_data(request)

async def comprehensive_data_analysis(data: Union[pd.DataFrame, List[Dict]]) -> List[AnalysisResult]:
    """Comprehensive analysis with multiple analysis types"""
    
    agent = DataScientistAgent()
    
    # Register dataset
    dataset_id = f"comprehensive_{datetime.now().timestamp()}"
    await agent.register_dataset(
        dataset_id=dataset_id,
        name="Comprehensive Analysis Dataset", 
        data=data,
        source=DataSource.SCRAPED_DATA,
        description="Dataset for comprehensive analysis"
    )
    
    # Run multiple analyses
    analysis_types = [
        AnalysisType.EXPLORATORY_DATA_ANALYSIS,
        AnalysisType.PATTERN_RECOGNITION,
        AnalysisType.ANOMALY_DETECTION,
        AnalysisType.TREND_ANALYSIS
    ]
    
    results = []
    for analysis_type in analysis_types:
        request = AnalysisRequest(
            request_id=f"{analysis_type.value}_{datetime.now().timestamp()}",
            dataset_id=dataset_id,
            analysis_type=analysis_type
        )
        
        result = await agent.analyze_data(request)
        results.append(result)
    
    return results

if __name__ == "__main__":
    # Test data scientist agent
    async def test_data_scientist():
        # Create sample data
        sample_data = [
            {'value': 10, 'category': 'A', 'timestamp': '2024-01-01'},
            {'value': 15, 'category': 'B', 'timestamp': '2024-01-02'},
            {'value': 8, 'category': 'A', 'timestamp': '2024-01-03'},
            {'value': 20, 'category': 'C', 'timestamp': '2024-01-04'},
            {'value': 12, 'category': 'B', 'timestamp': '2024-01-05'}
        ]
        
        # Quick analysis
        result = await quick_data_analysis(sample_data)
        print(f"Analysis completed: {result.success}")
        print(f"Insights: {result.insights}")
        print(f"Metrics: {result.metrics}")
    
    asyncio.run(test_data_scientist())
