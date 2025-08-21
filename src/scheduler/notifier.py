"""
Notification system for ECaDP scheduler.

Handles notifications for job status changes, alerts, and system events.
"""

import asyncio
import json
import smtplib
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from pathlib import Path

import requests
from src.utils.logger import get_logger

logger = get_logger(__name__)

class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class NotificationChannel(Enum):
    """Available notification channels"""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"
    LOG = "log"

@dataclass
class NotificationConfig:
    """Configuration for notification channels"""
    enabled: bool = True
    channels: List[NotificationChannel] = field(default_factory=list)
    
    # Email configuration
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    email_from: Optional[str] = None
    email_to: List[str] = field(default_factory=list)
    
    # Webhook configuration
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    
    # Slack configuration
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None
    
    # Discord configuration
    discord_webhook_url: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_hour: int = 100
    min_level: NotificationType = NotificationType.INFO

@dataclass
class Notification:
    """A notification message"""
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'message': self.message,
            'type': self.notification_type.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

class NotificationManager:
    """
    Manages notifications across multiple channels.
    
    Features:
    - Multiple notification channels
    - Rate limiting
    - Template-based messages
    - Retry logic
    - Notification history
    """
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.notification_history: List[Notification] = []
        self.rate_limit_counter = {}
        self.custom_handlers: Dict[str, Callable] = {}
        
    async def send_notification(self, notification: Notification) -> bool:
        """Send a notification through configured channels"""
        if not self.config.enabled:
            logger.debug("Notifications disabled, skipping")
            return False
            
        # Check rate limiting
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, dropping notification")
            return False
            
        # Check minimum level
        if self._should_skip_notification(notification):
            logger.debug(f"Notification below minimum level, skipping: {notification.title}")
            return False
        
        # Store in history
        self.notification_history.append(notification)
        
        # Send through each configured channel
        success = True
        for channel in self.config.channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email(notification)
                elif channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook(notification)
                elif channel == NotificationChannel.SLACK:
                    await self._send_slack(notification)
                elif channel == NotificationChannel.DISCORD:
                    await self._send_discord(notification)
                elif channel == NotificationChannel.LOG:
                    self._send_log(notification)
                    
            except Exception as e:
                logger.error(f"Failed to send notification via {channel.value}: {e}")
                success = False
        
        return success
    
    async def send_job_notification(self, 
                                  job_id: str,
                                  job_type: str,
                                  status: str,
                                  message: str = "",
                                  error: Optional[str] = None) -> bool:
        """Send a job status notification"""
        # Determine notification type based on status
        notification_type = NotificationType.INFO
        if status in ['failed', 'error']:
            notification_type = NotificationType.ERROR
        elif status in ['warning', 'timeout']:
            notification_type = NotificationType.WARNING
        elif status == 'completed':
            notification_type = NotificationType.INFO
            
        title = f"Job {status.title()}: {job_type}"
        full_message = f"Job {job_id} ({job_type}) has {status}."
        
        if message:
            full_message += f"\n\nDetails: {message}"
            
        if error:
            full_message += f"\n\nError: {error}"
        
        notification = Notification(
            title=title,
            message=full_message,
            notification_type=notification_type,
            metadata={
                'job_id': job_id,
                'job_type': job_type,
                'status': status,
                'error': error
            }
        )
        
        return await self.send_notification(notification)
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Send an alert notification"""
        alert_type = alert_data.get('type', 'unknown')
        message = alert_data.get('message', 'Alert triggered')
        
        notification_type = NotificationType.WARNING
        if alert_type in ['job_failed', 'high_error_rate', 'system_critical']:
            notification_type = NotificationType.ERROR
        elif alert_type in ['long_duration', 'performance_degraded']:
            notification_type = NotificationType.WARNING
            
        notification = Notification(
            title=f"Alert: {alert_type.replace('_', ' ').title()}",
            message=message,
            notification_type=notification_type,
            metadata=alert_data
        )
        
        return await self.send_notification(notification)
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_hour = datetime.utcnow().hour
        
        if current_hour not in self.rate_limit_counter:
            self.rate_limit_counter = {current_hour: 0}  # Reset counter
            
        if self.rate_limit_counter[current_hour] >= self.config.rate_limit_per_hour:
            return False
            
        self.rate_limit_counter[current_hour] += 1
        return True
    
    def _should_skip_notification(self, notification: Notification) -> bool:
        """Check if notification should be skipped based on level"""
        level_priority = {
            NotificationType.INFO: 1,
            NotificationType.WARNING: 2,
            NotificationType.ERROR: 3,
            NotificationType.CRITICAL: 4
        }
        
        return level_priority[notification.notification_type] < level_priority[self.config.min_level]
    
    async def _send_email(self, notification: Notification):
        """Send email notification"""
        if not all([self.config.smtp_host, self.config.email_from, self.config.email_to]):
            logger.warning("Email configuration incomplete, skipping email notification")
            return
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(self.config.email_to)
            msg['Subject'] = f"[ECaDP] {notification.title}"
            
            # Email body
            body = f"""
{notification.message}

---
Timestamp: {notification.timestamp.isoformat()}
Type: {notification.notification_type.value}
            """
            
            if notification.metadata:
                body += f"\nMetadata: {json.dumps(notification.metadata, indent=2)}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.smtp_use_tls:
                    server.starttls()
                if self.config.smtp_username and self.config.smtp_password:
                    server.login(self.config.smtp_username, self.config.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email notification sent: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            raise
    
    async def _send_webhook(self, notification: Notification):
        """Send webhook notification"""
        if not self.config.webhook_url:
            logger.warning("Webhook URL not configured, skipping webhook notification")
            return
            
        try:
            payload = notification.to_dict()
            
            headers = {'Content-Type': 'application/json'}
            if self.config.webhook_secret:
                headers['X-Webhook-Secret'] = self.config.webhook_secret
            
            async with asyncio.timeout(10):
                # Using requests in a thread to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        self.config.webhook_url,
                        json=payload,
                        headers=headers,
                        timeout=10
                    )
                )
                
            response.raise_for_status()
            logger.info(f"Webhook notification sent: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            raise
    
    async def _send_slack(self, notification: Notification):
        """Send Slack notification"""
        if not self.config.slack_webhook_url:
            logger.warning("Slack webhook URL not configured, skipping Slack notification")
            return
            
        try:
            # Create Slack payload
            color_map = {
                NotificationType.INFO: "good",
                NotificationType.WARNING: "warning",
                NotificationType.ERROR: "danger",
                NotificationType.CRITICAL: "danger"
            }
            
            payload = {
                "channel": self.config.slack_channel,
                "attachments": [{
                    "color": color_map.get(notification.notification_type, "good"),
                    "title": notification.title,
                    "text": notification.message,
                    "timestamp": int(notification.timestamp.timestamp()),
                    "fields": [
                        {
                            "title": "Type",
                            "value": notification.notification_type.value,
                            "short": True
                        }
                    ]
                }]
            }
            
            # Add metadata fields
            for key, value in notification.metadata.items():
                if len(payload["attachments"][0]["fields"]) < 10:  # Slack limit
                    payload["attachments"][0]["fields"].append({
                        "title": key.replace('_', ' ').title(),
                        "value": str(value),
                        "short": True
                    })
            
            async with asyncio.timeout(10):
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        self.config.slack_webhook_url,
                        json=payload,
                        timeout=10
                    )
                )
                
            response.raise_for_status()
            logger.info(f"Slack notification sent: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            raise
    
    async def _send_discord(self, notification: Notification):
        """Send Discord notification"""
        if not self.config.discord_webhook_url:
            logger.warning("Discord webhook URL not configured, skipping Discord notification")
            return
            
        try:
            # Create Discord embed
            color_map = {
                NotificationType.INFO: 0x3498db,      # Blue
                NotificationType.WARNING: 0xf39c12,   # Orange
                NotificationType.ERROR: 0xe74c3c,     # Red
                NotificationType.CRITICAL: 0x992d22   # Dark red
            }
            
            embed = {
                "title": notification.title,
                "description": notification.message,
                "color": color_map.get(notification.notification_type, 0x3498db),
                "timestamp": notification.timestamp.isoformat(),
                "fields": []
            }
            
            # Add metadata as fields
            for key, value in notification.metadata.items():
                if len(embed["fields"]) < 25:  # Discord limit
                    embed["fields"].append({
                        "name": key.replace('_', ' ').title(),
                        "value": str(value),
                        "inline": True
                    })
            
            payload = {"embeds": [embed]}
            
            async with asyncio.timeout(10):
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.post(
                        self.config.discord_webhook_url,
                        json=payload,
                        timeout=10
                    )
                )
                
            response.raise_for_status()
            logger.info(f"Discord notification sent: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            raise
    
    def _send_log(self, notification: Notification):
        """Send notification to logger"""
        log_level_map = {
            NotificationType.INFO: logger.info,
            NotificationType.WARNING: logger.warning,
            NotificationType.ERROR: logger.error,
            NotificationType.CRITICAL: logger.critical
        }
        
        log_func = log_level_map.get(notification.notification_type, logger.info)
        log_func(f"NOTIFICATION - {notification.title}: {notification.message}")
    
    def add_custom_handler(self, name: str, handler: Callable[[Notification], None]):
        """Add a custom notification handler"""
        self.custom_handlers[name] = handler
        logger.info(f"Added custom notification handler: {name}")
    
    def get_notification_history(self, 
                               limit: int = 100,
                               notification_type: Optional[NotificationType] = None) -> List[Notification]:
        """Get notification history"""
        history = self.notification_history
        
        if notification_type:
            history = [n for n in history if n.notification_type == notification_type]
            
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def clear_history(self, older_than_hours: int = 168):  # 1 week default
        """Clear old notification history"""
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        self.notification_history = [
            n for n in self.notification_history 
            if n.timestamp > cutoff_time
        ]
        logger.info(f"Cleared notification history older than {older_than_hours} hours")