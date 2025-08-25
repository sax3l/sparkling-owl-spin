"""
Notification Service

Centralized notification system for the ECaDP platform.
Handles email, Slack, webhook, and in-app notifications.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

import httpx
from jinja2 import Environment, FileSystemLoader

from src.settings import get_settings
from src.database.manager import DatabaseManager
from src.database.models import NotificationChannel, NotificationHistory, User
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    JOB_PAUSED = "job_paused"
    EXPORT_READY = "export_ready"
    DQ_ALERT = "data_quality_alert"
    SYSTEM_ALERT = "system_alert"
    QUOTA_WARNING = "quota_warning"
    PROXY_DOWN = "proxy_down"
    RETENTION_EXECUTED = "retention_executed"
    PRIVACY_REQUEST = "privacy_request"


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SMS = "sms"


@dataclass
class NotificationContext:
    """Context data for notification templates."""
    job_id: Optional[str] = None
    job_type: Optional[str] = None
    project_name: Optional[str] = None
    user_email: Optional[str] = None
    error_message: Optional[str] = None
    duration: Optional[str] = None
    items_processed: Optional[int] = None
    export_url: Optional[str] = None
    dq_score: Optional[float] = None
    threshold: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class NotificationService:
    """Service for sending notifications across multiple channels."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        
        # Initialize template engine
        self.template_env = Environment(
            loader=FileSystemLoader('templates/notifications')
        )
        
        # HTTP client for webhooks and Slack
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def send_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext,
        channels: List[NotificationChannel],
        recipients: Optional[List[str]] = None,
        priority: str = "normal"
    ):
        """Send notification to specified channels."""
        logger.info(f"Sending {notification_type.value} notification to {len(channels)} channels")
        
        # Get notification configuration
        config = self._get_notification_config(notification_type)
        
        if not config.get('enabled', True):
            logger.debug(f"Notifications disabled for {notification_type.value}")
            return
        
        tasks = []
        for channel in channels:
            if channel == NotificationChannel.EMAIL and recipients:
                tasks.append(self._send_email_notification(notification_type, context, recipients))
            elif channel == NotificationChannel.SLACK:
                tasks.append(self._send_slack_notification(notification_type, context))
            elif channel == NotificationChannel.WEBHOOK:
                tasks.append(self._send_webhook_notification(notification_type, context))
            elif channel == NotificationChannel.IN_APP and recipients:
                tasks.append(self._send_in_app_notification(notification_type, context, recipients))
        
        # Execute all notifications concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to send notification via {channels[i].value}: {result}")
                else:
                    logger.debug(f"Successfully sent notification via {channels[i].value}")
    
    async def _send_email_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext,
        recipients: List[str]
    ):
        """Send email notification."""
        if not self.settings.smtp_enabled:
            logger.warning("SMTP not configured, skipping email notification")
            return
        
        try:
            # Load email template
            template = self.template_env.get_template(f'{notification_type.value}_email.html')
            html_content = template.render(**context.__dict__)
            
            subject_template = self.template_env.get_template(f'{notification_type.value}_subject.txt')
            subject = subject_template.render(**context.__dict__)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.settings.smtp_from
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send to each recipient
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                if self.settings.smtp_tls:
                    server.starttls()
                if self.settings.smtp_username:
                    server.login(self.settings.smtp_username, self.settings.smtp_password)
                
                for recipient in recipients:
                    msg['To'] = recipient
                    server.send_message(msg)
                    logger.debug(f"Sent email notification to {recipient}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            raise
    
    async def _send_slack_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext
    ):
        """Send Slack notification."""
        if not self.settings.slack_webhook_url:
            logger.warning("Slack webhook not configured, skipping Slack notification")
            return
        
        try:
            # Load Slack template
            template = self.template_env.get_template(f'{notification_type.value}_slack.json')
            slack_payload = template.render(**context.__dict__)
            
            # Send to Slack
            response = await self.http_client.post(
                self.settings.slack_webhook_url,
                json=json.loads(slack_payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            logger.debug("Sent Slack notification successfully")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            raise
    
    async def _send_webhook_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext
    ):
        """Send webhook notification."""
        webhook_urls = self._get_webhook_urls(notification_type)
        
        if not webhook_urls:
            logger.debug("No webhook URLs configured for this notification type")
            return
        
        try:
            payload = {
                'type': notification_type.value,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context.__dict__
            }
            
            for webhook_url in webhook_urls:
                response = await self.http_client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'X-ECaDP-Event': notification_type.value
                    }
                )
                response.raise_for_status()
                logger.debug(f"Sent webhook notification to {webhook_url}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            raise
    
    async def _send_in_app_notification(
        self,
        notification_type: NotificationType,
        context: NotificationContext,
        recipients: List[str]
    ):
        """Send in-app notification."""
        try:
            async with self.db_manager.get_session() as session:
                for recipient_email in recipients:
                    # Find user
                    user = session.query(User).filter(User.email == recipient_email).first()
                    if not user:
                        logger.warning(f"User not found: {recipient_email}")
                        continue
                    
                    # Create notification record
                    notification = NotificationHistory(
                        user_id=user.id,
                        type=notification_type.value,
                        title=self._get_notification_title(notification_type, context),
                        message=self._get_notification_message(notification_type, context),
                        metadata=context.metadata,
                        created_at=datetime.utcnow(),
                        read=False
                    )
                    
                    session.add(notification)
                
                await session.commit()
                logger.debug(f"Created in-app notifications for {len(recipients)} users")
                
        except Exception as e:
            logger.error(f"Failed to create in-app notifications: {e}")
            raise
    
    def _get_notification_config(self, notification_type: NotificationType) -> Dict[str, Any]:
        """Get configuration for notification type."""
        # This would typically come from database or config files
        default_config = {
            'enabled': True,
            'channels': ['email', 'in_app'],
            'priority': 'normal',
            'throttle_minutes': 5  # Minimum time between same notifications
        }
        
        # Specific configs for different notification types
        configs = {
            NotificationType.JOB_FAILED: {
                'enabled': True,
                'channels': ['email', 'slack', 'in_app'],
                'priority': 'high'
            },
            NotificationType.DQ_ALERT: {
                'enabled': True,
                'channels': ['email', 'slack'],
                'priority': 'high'
            },
            NotificationType.SYSTEM_ALERT: {
                'enabled': True,
                'channels': ['email', 'slack', 'webhook'],
                'priority': 'critical'
            }
        }
        
        return configs.get(notification_type, default_config)
    
    def _get_webhook_urls(self, notification_type: NotificationType) -> List[str]:
        """Get webhook URLs for notification type."""
        # This would typically come from database configuration
        return getattr(self.settings, f'webhook_urls_{notification_type.value}', [])
    
    def _get_notification_title(self, notification_type: NotificationType, context: NotificationContext) -> str:
        """Get notification title."""
        titles = {
            NotificationType.JOB_COMPLETED: f"Job {context.job_id} completed successfully",
            NotificationType.JOB_FAILED: f"Job {context.job_id} failed",
            NotificationType.EXPORT_READY: f"Export ready for download",
            NotificationType.DQ_ALERT: f"Data quality alert for {context.project_name}",
        }
        return titles.get(notification_type, f"ECaDP Notification: {notification_type.value}")
    
    def _get_notification_message(self, notification_type: NotificationType, context: NotificationContext) -> str:
        """Get notification message."""
        if notification_type == NotificationType.JOB_COMPLETED:
            return f"Job {context.job_id} has completed successfully. Processed {context.items_processed} items in {context.duration}."
        elif notification_type == NotificationType.JOB_FAILED:
            return f"Job {context.job_id} has failed: {context.error_message}"
        elif notification_type == NotificationType.DQ_ALERT:
            return f"Data quality score ({context.dq_score:.2f}) is below threshold ({context.threshold:.2f}) for project {context.project_name}."
        else:
            return f"ECaDP notification: {notification_type.value}"
    
    async def close(self):
        """Clean up resources."""
        await self.http_client.aclose()


# Global notification service instance
_notification_service = None

def get_notification_service() -> NotificationService:
    """Get the global notification service instance."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


# Convenience functions for common notifications
async def notify_job_completed(job_id: str, job_type: str, duration: str, items_processed: int, user_email: str):
    """Send job completed notification."""
    service = get_notification_service()
    context = NotificationContext(
        job_id=job_id,
        job_type=job_type,
        duration=duration,
        items_processed=items_processed,
        user_email=user_email
    )
    await service.send_notification(
        NotificationType.JOB_COMPLETED,
        context,
        [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        [user_email]
    )


async def notify_job_failed(job_id: str, job_type: str, error_message: str, user_email: str):
    """Send job failed notification."""
    service = get_notification_service()
    context = NotificationContext(
        job_id=job_id,
        job_type=job_type,
        error_message=error_message,
        user_email=user_email
    )
    await service.send_notification(
        NotificationType.JOB_FAILED,
        context,
        [NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.IN_APP],
        [user_email]
    )


async def notify_export_ready(export_url: str, user_email: str):
    """Send export ready notification."""
    service = get_notification_service()
    context = NotificationContext(
        export_url=export_url,
        user_email=user_email
    )
    await service.send_notification(
        NotificationType.EXPORT_READY,
        context,
        [NotificationChannel.EMAIL, NotificationChannel.IN_APP],
        [user_email]
    )


async def notify_dq_alert(project_name: str, dq_score: float, threshold: float, user_email: str):
    """Send data quality alert notification."""
    service = get_notification_service()
    context = NotificationContext(
        project_name=project_name,
        dq_score=dq_score,
        threshold=threshold,
        user_email=user_email
    )
    await service.send_notification(
        NotificationType.DQ_ALERT,
        context,
        [NotificationChannel.EMAIL, NotificationChannel.SLACK],
        [user_email]
    )
