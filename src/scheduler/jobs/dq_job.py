"""
Data quality check job for monitoring data integrity.

Provides comprehensive data quality monitoring with
validation rules, metrics, and alerting capabilities.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from src.database.manager import SessionLocal
from src.database.models import ScrapedData, Job
from src.utils.logger import get_logger
from src.utils.metrics import DQ_SCORE

logger = get_logger(__name__)

class QualityLevel(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class QualityCheck:
    """Data quality check result"""
    name: str
    description: str
    passed: bool
    score: float
    details: Dict[str, Any]
    severity: str = "medium"

class DataQualityJob:
    """
    Data quality monitoring job.
    
    Features:
    - Comprehensive data validation
    - Quality scoring and metrics
    - Trend analysis
    - Alerting for quality issues
    - Automated remediation recommendations
    """
    
    def __init__(self):
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 0.95,
            QualityLevel.GOOD: 0.80,
            QualityLevel.FAIR: 0.60,
            QualityLevel.POOR: 0.40,
            QualityLevel.CRITICAL: 0.0
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute data quality check job"""
        try:
            logger.info("Starting data quality check job")
            
            # Get time window for analysis
            hours_back = kwargs.get("hours_back", 24)
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            # Run quality checks
            checks = await self._run_quality_checks(cutoff_time)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(checks)
            quality_level = self._get_quality_level(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(checks, quality_level)
            
            # Update metrics
            DQ_SCORE.set(overall_score)
            
            result = {
                "success": True,
                "overall_score": overall_score,
                "quality_level": quality_level.value,
                "total_checks": len(checks),
                "passed_checks": sum(1 for c in checks if c.passed),
                "failed_checks": sum(1 for c in checks if not c.passed),
                "checks": [self._check_to_dict(c) for c in checks],
                "recommendations": recommendations,
                "analysis_period_hours": hours_back
            }
            
            logger.info(f"Data quality check completed - Score: {overall_score:.2f}, Level: {quality_level.value}")
            return result
            
        except Exception as e:
            logger.error(f"Data quality check failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _run_quality_checks(self, cutoff_time: datetime) -> List[QualityCheck]:
        """Run all data quality checks"""
        checks = []
        
        with SessionLocal() as db:
            # Check 1: Data completeness
            checks.append(await self._check_data_completeness(db, cutoff_time))
            
            # Check 2: Data freshness
            checks.append(await self._check_data_freshness(db, cutoff_time))
            
            # Check 3: Extraction success rate
            checks.append(await self._check_extraction_success_rate(db, cutoff_time))
            
            # Check 4: Data consistency
            checks.append(await self._check_data_consistency(db, cutoff_time))
            
            # Check 5: Field validation
            checks.append(await self._check_field_validation(db, cutoff_time))
            
            # Check 6: Duplicate detection
            checks.append(await self._check_duplicates(db, cutoff_time))
            
            # Check 7: Schema compliance
            checks.append(await self._check_schema_compliance(db, cutoff_time))
        
        return checks
    
    async def _check_data_completeness(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check data completeness - are we missing expected data?"""
        try:
            # Count total records in period
            total_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time
            ).count()
            
            # Count records with non-null critical fields
            complete_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time,
                ScrapedData.data.isnot(None),
                ScrapedData.url.isnot(None)
            ).count()
            
            completeness_rate = complete_records / total_records if total_records > 0 else 1.0
            passed = completeness_rate >= 0.95
            
            return QualityCheck(
                name="data_completeness",
                description="Percentage of records with complete required fields",
                passed=passed,
                score=completeness_rate,
                details={
                    "total_records": total_records,
                    "complete_records": complete_records,
                    "completeness_rate": completeness_rate
                },
                severity="high" if not passed else "low"
            )
            
        except Exception as e:
            return self._error_check("data_completeness", str(e))
    
    async def _check_data_freshness(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check data freshness - is data being updated regularly?"""
        try:
            # Check for recent data
            recent_cutoff = datetime.utcnow() - timedelta(hours=2)
            recent_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= recent_cutoff
            ).count()
            
            # Check for any data in the period
            period_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time
            ).count()
            
            freshness_score = min(1.0, recent_records / max(1, period_records / 12))  # Expect ~1/12 of data in last 2h of 24h
            passed = recent_records > 0
            
            return QualityCheck(
                name="data_freshness",
                description="Data is being updated regularly",
                passed=passed,
                score=freshness_score,
                details={
                    "recent_records": recent_records,
                    "period_records": period_records,
                    "freshness_score": freshness_score
                },
                severity="medium"
            )
            
        except Exception as e:
            return self._error_check("data_freshness", str(e))
    
    async def _check_extraction_success_rate(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check extraction success rate from jobs"""
        try:
            # Count total jobs in period
            total_jobs = db.query(Job).filter(
                Job.created_at >= cutoff_time
            ).count()
            
            # Count successful jobs
            successful_jobs = db.query(Job).filter(
                Job.created_at >= cutoff_time,
                Job.status == "completed"
            ).count()
            
            success_rate = successful_jobs / total_jobs if total_jobs > 0 else 1.0
            passed = success_rate >= 0.80
            
            return QualityCheck(
                name="extraction_success_rate",
                description="Percentage of successful extraction jobs",
                passed=passed,
                score=success_rate,
                details={
                    "total_jobs": total_jobs,
                    "successful_jobs": successful_jobs,
                    "success_rate": success_rate
                },
                severity="high" if not passed else "low"
            )
            
        except Exception as e:
            return self._error_check("extraction_success_rate", str(e))
    
    async def _check_data_consistency(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check data consistency - are field formats consistent?"""
        try:
            # Sample recent records to check consistency
            sample_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time,
                ScrapedData.data.isnot(None)
            ).limit(100).all()
            
            if not sample_records:
                return QualityCheck(
                    name="data_consistency",
                    description="Data field formats are consistent",
                    passed=True,
                    score=1.0,
                    details={"note": "No data to check"},
                    severity="low"
                )
            
            # Check for consistent data structure
            consistent_count = 0
            total_count = len(sample_records)
            
            # Basic consistency checks
            for record in sample_records:
                try:
                    data = record.data
                    if isinstance(data, dict) and len(data) > 0:
                        consistent_count += 1
                except Exception:
                    pass
            
            consistency_rate = consistent_count / total_count
            passed = consistency_rate >= 0.90
            
            return QualityCheck(
                name="data_consistency",
                description="Data field formats are consistent",
                passed=passed,
                score=consistency_rate,
                details={
                    "sample_size": total_count,
                    "consistent_records": consistent_count,
                    "consistency_rate": consistency_rate
                },
                severity="medium"
            )
            
        except Exception as e:
            return self._error_check("data_consistency", str(e))
    
    async def _check_field_validation(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check field validation - are field values valid?"""
        try:
            # Sample records for validation
            sample_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time,
                ScrapedData.data.isnot(None)
            ).limit(50).all()
            
            if not sample_records:
                return QualityCheck(
                    name="field_validation",
                    description="Field values are valid",
                    passed=True,
                    score=1.0,
                    details={"note": "No data to validate"},
                    severity="low"
                )
            
            valid_count = 0
            total_count = len(sample_records)
            
            for record in sample_records:
                try:
                    data = record.data
                    # Basic validation checks
                    if (isinstance(data, dict) and 
                        record.url and 
                        record.url.startswith(('http://', 'https://'))):
                        valid_count += 1
                except Exception:
                    pass
            
            validation_rate = valid_count / total_count
            passed = validation_rate >= 0.85
            
            return QualityCheck(
                name="field_validation",
                description="Field values are valid",
                passed=passed,
                score=validation_rate,
                details={
                    "sample_size": total_count,
                    "valid_records": valid_count,
                    "validation_rate": validation_rate
                },
                severity="medium"
            )
            
        except Exception as e:
            return self._error_check("field_validation", str(e))
    
    async def _check_duplicates(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check for duplicate records"""
        try:
            # Count total records
            total_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time
            ).count()
            
            # Count unique URLs
            unique_urls = db.query(ScrapedData.url).filter(
                ScrapedData.created_at >= cutoff_time
            ).distinct().count()
            
            if total_records == 0:
                duplicate_rate = 0.0
            else:
                duplicate_rate = (total_records - unique_urls) / total_records
            
            uniqueness_rate = 1.0 - duplicate_rate
            passed = duplicate_rate < 0.10  # Less than 10% duplicates
            
            return QualityCheck(
                name="duplicate_detection",
                description="Low rate of duplicate records",
                passed=passed,
                score=uniqueness_rate,
                details={
                    "total_records": total_records,
                    "unique_urls": unique_urls,
                    "duplicate_rate": duplicate_rate,
                    "uniqueness_rate": uniqueness_rate
                },
                severity="medium"
            )
            
        except Exception as e:
            return self._error_check("duplicate_detection", str(e))
    
    async def _check_schema_compliance(self, db, cutoff_time: datetime) -> QualityCheck:
        """Check schema compliance - do records match expected schema?"""
        try:
            # Sample records for schema checking
            sample_records = db.query(ScrapedData).filter(
                ScrapedData.created_at >= cutoff_time,
                ScrapedData.data.isnot(None)
            ).limit(20).all()
            
            if not sample_records:
                return QualityCheck(
                    name="schema_compliance",
                    description="Records comply with expected schema",
                    passed=True,
                    score=1.0,
                    details={"note": "No data to check"},
                    severity="low"
                )
            
            compliant_count = 0
            total_count = len(sample_records)
            
            for record in sample_records:
                try:
                    # Basic schema checks
                    if (hasattr(record, 'id') and 
                        hasattr(record, 'url') and 
                        hasattr(record, 'data') and 
                        hasattr(record, 'created_at')):
                        compliant_count += 1
                except Exception:
                    pass
            
            compliance_rate = compliant_count / total_count
            passed = compliance_rate >= 0.95
            
            return QualityCheck(
                name="schema_compliance",
                description="Records comply with expected schema",
                passed=passed,
                score=compliance_rate,
                details={
                    "sample_size": total_count,
                    "compliant_records": compliant_count,
                    "compliance_rate": compliance_rate
                },
                severity="high" if not passed else "low"
            )
            
        except Exception as e:
            return self._error_check("schema_compliance", str(e))
    
    def _error_check(self, name: str, error: str) -> QualityCheck:
        """Create an error check result"""
        return QualityCheck(
            name=name,
            description=f"Check failed due to error",
            passed=False,
            score=0.0,
            details={"error": error},
            severity="high"
        )
    
    def _calculate_overall_score(self, checks: List[QualityCheck]) -> float:
        """Calculate weighted overall quality score"""
        if not checks:
            return 0.0
        
        # Define weights for different checks
        weights = {
            "data_completeness": 0.25,
            "extraction_success_rate": 0.20,
            "data_freshness": 0.15,
            "data_consistency": 0.15,
            "field_validation": 0.10,
            "duplicate_detection": 0.10,
            "schema_compliance": 0.05
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for check in checks:
            weight = weights.get(check.name, 0.1)  # Default weight
            weighted_sum += check.score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level from score"""
        for level, threshold in self.quality_thresholds.items():
            if score >= threshold:
                return level
        return QualityLevel.CRITICAL
    
    def _generate_recommendations(self, checks: List[QualityCheck], quality_level: QualityLevel) -> List[str]:
        """Generate recommendations based on check results"""
        recommendations = []
        
        for check in checks:
            if not check.passed:
                if check.name == "data_completeness":
                    recommendations.append("Review data extraction templates for missing required fields")
                elif check.name == "data_freshness":
                    recommendations.append("Check crawler scheduling and job execution frequency")
                elif check.name == "extraction_success_rate":
                    recommendations.append("Investigate failed jobs and improve error handling")
                elif check.name == "data_consistency":
                    recommendations.append("Standardize data extraction and validation procedures")
                elif check.name == "field_validation":
                    recommendations.append("Implement stricter field validation rules")
                elif check.name == "duplicate_detection":
                    recommendations.append("Improve URL deduplication and implement data deduplication")
                elif check.name == "schema_compliance":
                    recommendations.append("Review and enforce data schema requirements")
        
        # Add level-specific recommendations
        if quality_level in [QualityLevel.POOR, QualityLevel.CRITICAL]:
            recommendations.append("Consider pausing data collection until quality issues are resolved")
            recommendations.append("Perform manual data audit and validation")
        
        return recommendations
    
    def _check_to_dict(self, check: QualityCheck) -> Dict[str, Any]:
        """Convert QualityCheck to dictionary"""
        return {
            "name": check.name,
            "description": check.description,
            "passed": check.passed,
            "score": check.score,
            "severity": check.severity,
            "details": check.details
        }

# Entry point for scheduler
async def execute_data_quality_job(**kwargs) -> Dict[str, Any]:
    """Execute data quality job - entry point for scheduler"""
    job = DataQualityJob()
    return await job.execute(**kwargs)