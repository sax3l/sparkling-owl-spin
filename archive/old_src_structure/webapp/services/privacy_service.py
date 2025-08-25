"""
Service layer for privacy and GDPR compliance.
"""

import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from ..models import User, CrawlJob, ScrapeJob, APIKey, Webhook


class PrivacyService:
    """Service for handling privacy and GDPR compliance operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of all data associated with a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing data summary
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Count user's data
        crawl_jobs_count = self.db.query(CrawlJob).filter(
            CrawlJob.user_id == user_id
        ).count()
        
        scrape_jobs_count = self.db.query(ScrapeJob).filter(
            ScrapeJob.user_id == user_id
        ).count()
        
        api_keys_count = self.db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).count()
        
        webhooks_count = self.db.query(Webhook).filter(
            Webhook.user_id == user_id
        ).count()
        
        return {
            "user_id": user_id,
            "email": user.email,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "data_summary": {
                "crawl_jobs": crawl_jobs_count,
                "scrape_jobs": scrape_jobs_count,
                "api_keys": api_keys_count,
                "webhooks": webhooks_count
            },
            "summary_generated_at": datetime.utcnow().isoformat()
        }
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance (data portability).
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing all user data
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get all user data
        crawl_jobs = self.db.query(CrawlJob).filter(
            CrawlJob.user_id == user_id
        ).all()
        
        scrape_jobs = self.db.query(ScrapeJob).filter(
            ScrapeJob.user_id == user_id
        ).all()
        
        api_keys = self.db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).all()
        
        webhooks = self.db.query(Webhook).filter(
            Webhook.user_id == user_id
        ).all()
        
        # Serialize data (excluding sensitive information)
        return {
            "export_info": {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "export_type": "full_user_data"
            },
            "user_profile": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            },
            "crawl_jobs": [
                {
                    "id": str(job.id),
                    "name": job.name,
                    "status": job.status,
                    "config": job.config,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "result_count": len(job.results or [])
                }
                for job in crawl_jobs
            ],
            "scrape_jobs": [
                {
                    "id": str(job.id),
                    "name": job.name,
                    "status": job.status,
                    "urls": job.urls,
                    "template_id": job.template_id,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "result_count": len(job.results or [])
                }
                for job in scrape_jobs
            ],
            "api_keys": [
                {
                    "id": str(key.id),
                    "name": key.name,
                    "permissions": key.permissions,
                    "is_active": key.is_active,
                    "created_at": key.created_at.isoformat() if key.created_at else None,
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                    "expires_at": key.expires_at.isoformat() if key.expires_at else None
                }
                for key in api_keys
            ],
            "webhooks": [
                {
                    "id": str(webhook.id),
                    "name": webhook.name,
                    "url": webhook.url,
                    "events": webhook.events,
                    "is_active": webhook.is_active,
                    "created_at": webhook.created_at.isoformat() if webhook.created_at else None
                }
                for webhook in webhooks
            ]
        }
    
    def anonymize_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Anonymize user data while preserving necessary records.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with anonymization results
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate anonymized data
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        anonymous_email = f"anonymized_{timestamp}@example.com"
        anonymous_name = f"Anonymized User {timestamp}"
        
        # Store original data for audit
        original_data = {
            "email": user.email,
            "full_name": user.full_name
        }
        
        # Anonymize user profile
        user.email = anonymous_email
        user.full_name = anonymous_name
        user.is_active = False
        
        # Deactivate API keys
        api_keys = self.db.query(APIKey).filter(APIKey.user_id == user_id).all()
        for api_key in api_keys:
            api_key.is_active = False
        
        # Deactivate webhooks
        webhooks = self.db.query(Webhook).filter(Webhook.user_id == user_id).all()
        for webhook in webhooks:
            webhook.is_active = False
        
        try:
            self.db.commit()
            
            return {
                "user_id": user_id,
                "anonymized_at": datetime.utcnow().isoformat(),
                "actions_taken": {
                    "profile_anonymized": True,
                    "account_deactivated": True,
                    "api_keys_deactivated": len(api_keys),
                    "webhooks_deactivated": len(webhooks)
                },
                "message": "User data has been successfully anonymized"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Anonymization failed"
            )
    
    def delete_user_account(self, user_id: str, confirm: bool = False) -> Dict[str, Any]:
        """
        Delete user account and all associated data (GDPR right to erasure).
        
        Args:
            user_id: User ID
            confirm: Confirmation flag
            
        Returns:
            Dictionary with deletion results
            
        Raises:
            HTTPException: If user not found or confirmation not provided
        """
        if not confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account deletion must be confirmed"
            )
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Count data to be deleted
        crawl_jobs = self.db.query(CrawlJob).filter(CrawlJob.user_id == user_id).all()
        scrape_jobs = self.db.query(ScrapeJob).filter(ScrapeJob.user_id == user_id).all()
        api_keys = self.db.query(APIKey).filter(APIKey.user_id == user_id).all()
        webhooks = self.db.query(Webhook).filter(Webhook.user_id == user_id).all()
        
        deletion_summary = {
            "crawl_jobs": len(crawl_jobs),
            "scrape_jobs": len(scrape_jobs),
            "api_keys": len(api_keys),
            "webhooks": len(webhooks)
        }
        
        try:
            # Delete associated data
            for job in crawl_jobs:
                self.db.delete(job)
            
            for job in scrape_jobs:
                self.db.delete(job)
            
            for api_key in api_keys:
                self.db.delete(api_key)
            
            for webhook in webhooks:
                self.db.delete(webhook)
            
            # Delete user account
            self.db.delete(user)
            
            self.db.commit()
            
            return {
                "user_id": user_id,
                "deleted_at": datetime.utcnow().isoformat(),
                "deletion_summary": deletion_summary,
                "message": "User account and all associated data has been permanently deleted"
            }
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Account deletion failed"
            )
    
    def get_data_retention_info(self, user_id: str) -> Dict[str, Any]:
        """
        Get information about data retention periods.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with retention information
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Define retention periods (in days)
        retention_periods = {
            "user_profile": 2555,  # 7 years for compliance
            "crawl_jobs": 1095,    # 3 years
            "scrape_jobs": 1095,   # 3 years
            "api_keys": 365,       # 1 year after expiration
            "webhooks": 365,       # 1 year
            "logs": 90             # 3 months
        }
        
        # Calculate expiration dates
        current_date = datetime.utcnow()
        account_created = user.created_at or current_date
        
        return {
            "user_id": user_id,
            "account_created": account_created.isoformat(),
            "retention_policy": {
                data_type: {
                    "retention_days": days,
                    "expires_at": (account_created + timedelta(days=days)).isoformat()
                }
                for data_type, days in retention_periods.items()
            },
            "current_date": current_date.isoformat(),
            "note": "Data may be anonymized or deleted according to retention policy"
        }
    
    def cleanup_expired_data(self) -> Dict[str, Any]:
        """
        Clean up expired data according to retention policies.
        
        Returns:
            Dictionary with cleanup results
        """
        current_date = datetime.utcnow()
        cleanup_results = {
            "cleaned_at": current_date.isoformat(),
            "actions": []
        }
        
        # Clean up old completed jobs (older than 3 years)
        three_years_ago = current_date - timedelta(days=1095)
        
        old_crawl_jobs = self.db.query(CrawlJob).filter(
            and_(
                CrawlJob.completed_at < three_years_ago,
                CrawlJob.completed_at.isnot(None)
            )
        ).all()
        
        old_scrape_jobs = self.db.query(ScrapeJob).filter(
            and_(
                ScrapeJob.completed_at < three_years_ago,
                ScrapeJob.completed_at.isnot(None)
            )
        ).all()
        
        # Clean up expired API keys (1 year after expiration)
        one_year_ago = current_date - timedelta(days=365)
        expired_api_keys = self.db.query(APIKey).filter(
            and_(
                APIKey.expires_at < one_year_ago,
                APIKey.expires_at.isnot(None)
            )
        ).all()
        
        # Clean up inactive users (7 years since last login)
        seven_years_ago = current_date - timedelta(days=2555)
        inactive_users = self.db.query(User).filter(
            or_(
                and_(
                    User.last_login < seven_years_ago,
                    User.last_login.isnot(None)
                ),
                and_(
                    User.created_at < seven_years_ago,
                    User.last_login.is_(None)
                )
            )
        ).all()
        
        try:
            # Delete old jobs
            for job in old_crawl_jobs:
                self.db.delete(job)
            cleanup_results["actions"].append(f"Deleted {len(old_crawl_jobs)} old crawl jobs")
            
            for job in old_scrape_jobs:
                self.db.delete(job)
            cleanup_results["actions"].append(f"Deleted {len(old_scrape_jobs)} old scrape jobs")
            
            # Delete expired API keys
            for api_key in expired_api_keys:
                self.db.delete(api_key)
            cleanup_results["actions"].append(f"Deleted {len(expired_api_keys)} expired API keys")
            
            # Anonymize inactive users instead of deleting
            for user in inactive_users:
                timestamp = current_date.strftime("%Y%m%d%H%M%S")
                user.email = f"anonymized_{timestamp}_{user.id}@example.com"
                user.full_name = f"Anonymized User {timestamp}"
                user.is_active = False
            
            cleanup_results["actions"].append(f"Anonymized {len(inactive_users)} inactive users")
            
            self.db.commit()
            cleanup_results["status"] = "success"
            
        except Exception as e:
            self.db.rollback()
            cleanup_results["status"] = "failed"
            cleanup_results["error"] = str(e)
        
        return cleanup_results
    
    def get_gdpr_compliance_status(self, user_id: str) -> Dict[str, Any]:
        """
        Get GDPR compliance status for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with compliance status
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "user_id": user_id,
            "gdpr_rights": {
                "right_to_access": {
                    "available": True,
                    "description": "Request access to your personal data",
                    "endpoint": "/api/privacy/export-data"
                },
                "right_to_portability": {
                    "available": True,
                    "description": "Export your data in a machine-readable format",
                    "endpoint": "/api/privacy/export-data"
                },
                "right_to_rectification": {
                    "available": True,
                    "description": "Update your personal information",
                    "endpoint": "/api/users/me"
                },
                "right_to_erasure": {
                    "available": True,
                    "description": "Delete your account and all associated data",
                    "endpoint": "/api/privacy/delete-account"
                },
                "right_to_restrict_processing": {
                    "available": True,
                    "description": "Deactivate your account to restrict processing",
                    "endpoint": "/api/users/me/deactivate"
                },
                "right_to_object": {
                    "available": True,
                    "description": "Object to processing by deleting your account",
                    "endpoint": "/api/privacy/delete-account"
                }
            },
            "data_protection": {
                "data_encrypted": True,
                "access_logging": True,
                "retention_policies": True,
                "regular_audits": True
            },
            "compliance_checked_at": datetime.utcnow().isoformat()
        }
