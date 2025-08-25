"""
Scheduler Module - Job scheduling and orchestration.

Provides comprehensive job scheduling including:
- Background job execution
- Cron-based scheduling
- Job monitoring and health checks
- Queue management and prioritization
- Retry logic and error handling
- Job dependencies and workflows

Main Components:
- JobScheduler: Core scheduling functionality
- JobMonitor: Job health and performance monitoring
- JobNotifier: Notification and alerting
- JobDefinitions: Pre-defined job types

Job Types:
- RetentionJob: Data lifecycle and cleanup
- BackupJob: Database backup operations
- ExportJob: Data export and delivery
- DataQualityJob: Quality assurance checks
- RedisSnapshotJob: Cache backup operations
- ErasureWorker: GDPR compliance operations
"""

from .job_scheduler import JobScheduler
from .job_monitor import JobMonitor
from .notifier import NotificationManager as JobNotifier
from .job_definitions import JobDefinition

# Import job types
from .jobs import (
    RetentionJob, BackupSQLJob, ExportJob, 
    DataQualityJob, RedisSnapshotJob, ErasureWorker
)

__all__ = [
    "JobScheduler",
    "JobMonitor", 
    "JobNotifier",
    "JobDefinition",
    "RetentionJob",
    "BackupSQLJob",
    "ExportJob",
    "DataQualityJob", 
    "RedisSnapshotJob",
    "ErasureWorker"
]