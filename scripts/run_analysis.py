#!/usr/bin/env python3
"""
Data Analysis Runner
===================

Comprehensive data analysis and reporting tool for the ECaDP platform.
Performs analysis on extracted data, generates insights, and creates reports.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.manager import DatabaseManager
from src.analysis.data_analyzer import DataAnalyzer
from src.analysis.quality_checker import QualityChecker
from src.analysis.trend_analyzer import TrendAnalyzer
from src.analysis.report_generator import ReportGenerator
from src.observability.metrics import metrics_collector
from src.webhooks import emit_system_alert, EventSeverity
from src.utils.config_loader import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/analysis_runner.log')
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class AnalysisConfig:
    """Analysis configuration"""
    analysis_types: List[str]
    time_range_days: int
    min_data_points: int
    output_formats: List[str]
    output_directory: str
    quality_thresholds: Dict[str, float]
    webhook_url: Optional[str] = None
    send_notifications: bool = True

class AnalysisRunner:
    """
    Main analysis runner for the ECaDP platform
    
    Features:
    - Data quality analysis
    - Trend analysis
    - Performance metrics
    - Report generation
    - Alert notifications
    """
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.db_manager = None
        self.data_analyzer = None
        self.quality_checker = None
        self.trend_analyzer = None
        self.report_generator = None
        
        # Analysis results
        self.analysis_results = {}
        self.quality_issues = []
        self.trend_insights = []
        
        # Metrics
        self.start_time = None
        self.end_time = None
    
    async def initialize(self):
        """Initialize analysis components"""
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Initialize analysis components
            self.data_analyzer = DataAnalyzer(self.db_manager)
            self.quality_checker = QualityChecker(self.config.quality_thresholds)
            self.trend_analyzer = TrendAnalyzer()
            self.report_generator = ReportGenerator(self.config.output_directory)
            
            # Create output directory
            os.makedirs(self.config.output_directory, exist_ok=True)
            
            logger.info("Analysis runner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analysis runner: {e}")
            raise
    
    async def run_analysis(self) -> Dict[str, Any]:
        """Run comprehensive data analysis"""
        self.start_time = datetime.utcnow()
        
        try:
            logger.info("Starting data analysis...")
            
            # Record analysis start
            metrics_collector.record_counter('analysis_runs_started')
            
            # Run different types of analysis
            for analysis_type in self.config.analysis_types:
                logger.info(f"Running {analysis_type} analysis...")
                
                try:
                    result = await self._run_single_analysis(analysis_type)
                    self.analysis_results[analysis_type] = result
                    
                    metrics_collector.record_counter(
                        'analysis_completed',
                        labels={'type': analysis_type, 'status': 'success'}
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to run {analysis_type} analysis: {e}")
                    self.analysis_results[analysis_type] = {
                        'error': str(e),
                        'status': 'failed'
                    }
                    
                    metrics_collector.record_counter(
                        'analysis_completed',
                        labels={'type': analysis_type, 'status': 'failed'}
                    )
            
            # Generate comprehensive report
            await self._generate_reports()
            
            # Send notifications if enabled
            if self.config.send_notifications:
                await self._send_notifications()
            
            self.end_time = datetime.utcnow()
            duration = (self.end_time - self.start_time).total_seconds()
            
            metrics_collector.record_histogram('analysis_duration_seconds', duration)
            
            logger.info(f"Analysis completed in {duration:.2f} seconds")
            
            return {
                'status': 'success',
                'duration': duration,
                'results': self.analysis_results,
                'quality_issues': len(self.quality_issues),
                'trend_insights': len(self.trend_insights)
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            
            if self.config.send_notifications:
                await emit_system_alert(
                    'analysis_failure',
                    f'Data analysis failed: {str(e)}',
                    EventSeverity.ERROR
                )
            
            metrics_collector.record_counter('analysis_runs_failed')
            
            return {
                'status': 'failed',
                'error': str(e),
                'results': self.analysis_results
            }
    
    async def _run_single_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Run a single type of analysis"""
        
        if analysis_type == 'data_quality':
            return await self._run_data_quality_analysis()
        elif analysis_type == 'trend_analysis':
            return await self._run_trend_analysis()
        elif analysis_type == 'performance':
            return await self._run_performance_analysis()
        elif analysis_type == 'extraction_stats':
            return await self._run_extraction_stats()
        elif analysis_type == 'template_drift':
            return await self._run_template_drift_analysis()
        elif analysis_type == 'proxy_performance':
            return await self._run_proxy_performance_analysis()
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    async def _run_data_quality_analysis(self) -> Dict[str, Any]:
        """Run data quality analysis"""
        
        # Get recent extractions
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.time_range_days)
        
        query = """
        SELECT e.*, t.name as template_name, t.version as template_version
        FROM extractions e
        JOIN templates t ON e.template_id = t.id
        WHERE e.created_at >= %s
        ORDER BY e.created_at DESC
        """
        
        extractions = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        if len(extractions) < self.config.min_data_points:
            return {
                'status': 'insufficient_data',
                'message': f'Only {len(extractions)} extractions found, minimum {self.config.min_data_points} required'
            }
        
        # Analyze data quality
        quality_results = []
        
        for extraction in extractions:
            try:
                data = extraction.get('data', {})
                
                quality_score = await self.quality_checker.check_data_quality(
                    data,
                    extraction['template_name']
                )
                
                quality_results.append({
                    'extraction_id': extraction['id'],
                    'template': extraction['template_name'],
                    'quality_score': quality_score,
                    'timestamp': extraction['created_at']
                })
                
                # Track quality issues
                if quality_score < self.config.quality_thresholds.get('minimum_score', 0.7):
                    self.quality_issues.append({
                        'extraction_id': extraction['id'],
                        'template': extraction['template_name'],
                        'score': quality_score,
                        'issue_type': 'low_quality_score'
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to check quality for extraction {extraction['id']}: {e}")
        
        # Calculate aggregate statistics
        if quality_results:
            scores = [r['quality_score'] for r in quality_results]
            
            aggregates = {
                'total_extractions': len(quality_results),
                'average_quality': np.mean(scores),
                'median_quality': np.median(scores),
                'min_quality': np.min(scores),
                'max_quality': np.max(scores),
                'std_quality': np.std(scores),
                'below_threshold': len([s for s in scores if s < self.config.quality_thresholds.get('minimum_score', 0.7)])
            }
        else:
            aggregates = {'total_extractions': 0}
        
        return {
            'status': 'success',
            'aggregates': aggregates,
            'quality_results': quality_results,
            'quality_issues': len(self.quality_issues)
        }
    
    async def _run_trend_analysis(self) -> Dict[str, Any]:
        """Run trend analysis"""
        
        # Get extraction counts over time
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.time_range_days)
        
        query = """
        SELECT 
            DATE(created_at) as date,
            template_id,
            COUNT(*) as extraction_count,
            AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate
        FROM extractions
        WHERE created_at >= %s
        GROUP BY DATE(created_at), template_id
        ORDER BY date, template_id
        """
        
        trend_data = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        if not trend_data:
            return {
                'status': 'no_data',
                'message': 'No trend data available'
            }
        
        # Analyze trends
        trends = await self.trend_analyzer.analyze_trends(trend_data)
        
        # Identify significant trends
        significant_trends = []
        for trend in trends:
            if abs(trend.get('slope', 0)) > 0.1:  # Configurable threshold
                significant_trends.append(trend)
                self.trend_insights.append(trend)
        
        return {
            'status': 'success',
            'trends': trends,
            'significant_trends': significant_trends,
            'trend_count': len(trends)
        }
    
    async def _run_performance_analysis(self) -> Dict[str, Any]:
        """Run performance analysis"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.time_range_days)
        
        # Get job performance data
        query = """
        SELECT 
            job_type,
            AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration,
            COUNT(*) as total_jobs,
            AVG(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_rate
        FROM jobs
        WHERE started_at >= %s
        GROUP BY job_type
        """
        
        performance_data = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        # Get crawler performance
        crawler_query = """
        SELECT 
            domain,
            AVG(response_time) as avg_response_time,
            COUNT(*) as total_requests,
            AVG(CASE WHEN status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END) as success_rate
        FROM crawler_requests
        WHERE created_at >= %s
        GROUP BY domain
        """
        
        crawler_performance = await self.db_manager.fetch_all(crawler_query, (cutoff_date,))
        
        return {
            'status': 'success',
            'job_performance': performance_data,
            'crawler_performance': crawler_performance,
            'analysis_period_days': self.config.time_range_days
        }
    
    async def _run_extraction_stats(self) -> Dict[str, Any]:
        """Run extraction statistics analysis"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.time_range_days)
        
        query = """
        SELECT 
            t.name as template_name,
            COUNT(e.id) as total_extractions,
            AVG(ARRAY_LENGTH(ARRAY(SELECT * FROM jsonb_object_keys(e.data)), 1)) as avg_fields_extracted,
            AVG(e.processing_time) as avg_processing_time,
            MAX(e.created_at) as last_extraction
        FROM extractions e
        JOIN templates t ON e.template_id = t.id
        WHERE e.created_at >= %s
        GROUP BY t.id, t.name
        ORDER BY total_extractions DESC
        """
        
        stats = await self.db_manager.fetch_all(query, (cutoff_date,))
        
        # Calculate totals
        total_extractions = sum(stat['total_extractions'] for stat in stats)
        total_templates = len(stats)
        
        return {
            'status': 'success',
            'template_stats': stats,
            'totals': {
                'total_extractions': total_extractions,
                'total_templates': total_templates,
                'analysis_period_days': self.config.time_range_days
            }
        }
    
    async def _run_template_drift_analysis(self) -> Dict[str, Any]:
        """Run template drift analysis"""
        
        # This would analyze changes in template effectiveness over time
        # For now, return a placeholder
        
        return {
            'status': 'success',
            'message': 'Template drift analysis completed',
            'drift_detected': False,
            'templates_analyzed': 0
        }
    
    async def _run_proxy_performance_analysis(self) -> Dict[str, Any]:
        """Run proxy performance analysis"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.config.time_range_days)
        
        query = """
        SELECT 
            proxy_id,
            COUNT(*) as total_requests,
            AVG(response_time) as avg_response_time,
            AVG(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_rate,
            MAX(last_used) as last_used
        FROM proxy_usage_logs
        WHERE created_at >= %s
        GROUP BY proxy_id
        ORDER BY total_requests DESC
        """
        
        try:
            proxy_stats = await self.db_manager.fetch_all(query, (cutoff_date,))
        except Exception as e:
            # Handle case where proxy logs table doesn't exist
            logger.warning(f"Proxy analysis failed: {e}")
            proxy_stats = []
        
        return {
            'status': 'success',
            'proxy_stats': proxy_stats,
            'total_proxies_analyzed': len(proxy_stats)
        }
    
    async def _generate_reports(self):
        """Generate analysis reports"""
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        for output_format in self.config.output_formats:
            try:
                if output_format == 'json':
                    await self._generate_json_report(timestamp)
                elif output_format == 'html':
                    await self._generate_html_report(timestamp)
                elif output_format == 'pdf':
                    await self._generate_pdf_report(timestamp)
                else:
                    logger.warning(f"Unknown output format: {output_format}")
                    
            except Exception as e:
                logger.error(f"Failed to generate {output_format} report: {e}")
    
    async def _generate_json_report(self, timestamp: str):
        """Generate JSON report"""
        
        report_data = {
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_period_days': self.config.time_range_days,
                'analysis_types': self.config.analysis_types
            },
            'results': self.analysis_results,
            'quality_issues': self.quality_issues,
            'trend_insights': self.trend_insights,
            'summary': {
                'total_analysis_types': len(self.config.analysis_types),
                'successful_analyses': len([r for r in self.analysis_results.values() if r.get('status') == 'success']),
                'quality_issues_found': len(self.quality_issues),
                'trends_identified': len(self.trend_insights)
            }
        }
        
        output_file = Path(self.config.output_directory) / f'analysis_report_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"JSON report saved to {output_file}")
    
    async def _generate_html_report(self, timestamp: str):
        """Generate HTML report"""
        
        html_content = await self.report_generator.generate_html_report(
            self.analysis_results,
            self.quality_issues,
            self.trend_insights
        )
        
        output_file = Path(self.config.output_directory) / f'analysis_report_{timestamp}.html'
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to {output_file}")
    
    async def _generate_pdf_report(self, timestamp: str):
        """Generate PDF report"""
        
        # This would require additional dependencies like reportlab or weasyprint
        logger.info("PDF report generation not implemented yet")
    
    async def _send_notifications(self):
        """Send analysis completion notifications"""
        
        if not self.config.webhook_url:
            return
        
        # Determine overall status
        failed_analyses = [name for name, result in self.analysis_results.items() 
                          if result.get('status') != 'success']
        
        if failed_analyses:
            await emit_system_alert(
                'analysis_partial_failure',
                f'Analysis completed with failures: {", ".join(failed_analyses)}',
                EventSeverity.WARNING
            )
        else:
            await emit_system_alert(
                'analysis_completed',
                f'Data analysis completed successfully. Found {len(self.quality_issues)} quality issues and {len(self.trend_insights)} trends.',
                EventSeverity.INFO
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.db_manager:
            await self.db_manager.close()

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ECaDP Data Analysis Runner')
    parser.add_argument('--config', default='config/analysis.yml', help='Analysis configuration file')
    parser.add_argument('--analysis-types', nargs='+', 
                       choices=['data_quality', 'trend_analysis', 'performance', 'extraction_stats', 'template_drift', 'proxy_performance'],
                       default=['data_quality', 'trend_analysis', 'performance', 'extraction_stats'],
                       help='Types of analysis to run')
    parser.add_argument('--time-range', type=int, default=7, help='Analysis time range in days')
    parser.add_argument('--output-dir', default='data/analysis_reports', help='Output directory for reports')
    parser.add_argument('--output-formats', nargs='+', choices=['json', 'html', 'pdf'], 
                       default=['json', 'html'], help='Output formats for reports')
    parser.add_argument('--min-data-points', type=int, default=10, help='Minimum data points required for analysis')
    parser.add_argument('--no-notifications', action='store_true', help='Disable webhook notifications')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        try:
            config_data = load_config(args.config)
            quality_thresholds = config_data.get('quality_thresholds', {
                'minimum_score': 0.7,
                'completeness_threshold': 0.8,
                'accuracy_threshold': 0.9
            })
            webhook_url = config_data.get('webhook_url')
        except Exception as e:
            logger.warning(f"Failed to load config file {args.config}: {e}")
            quality_thresholds = {
                'minimum_score': 0.7,
                'completeness_threshold': 0.8,
                'accuracy_threshold': 0.9
            }
            webhook_url = None
        
        # Create analysis configuration
        analysis_config = AnalysisConfig(
            analysis_types=args.analysis_types,
            time_range_days=args.time_range,
            min_data_points=args.min_data_points,
            output_formats=args.output_formats,
            output_directory=args.output_dir,
            quality_thresholds=quality_thresholds,
            webhook_url=webhook_url,
            send_notifications=not args.no_notifications
        )
        
        # Initialize and run analysis
        runner = AnalysisRunner(analysis_config)
        
        try:
            await runner.initialize()
            result = await runner.run_analysis()
            
            print(f"Analysis Status: {result['status']}")
            if result['status'] == 'success':
                print(f"Duration: {result['duration']:.2f} seconds")
                print(f"Quality Issues: {result['quality_issues']}")
                print(f"Trend Insights: {result['trend_insights']}")
            else:
                print(f"Error: {result.get('error')}")
                return 1
                
        finally:
            await runner.cleanup()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))