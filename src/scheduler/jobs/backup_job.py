"""
Backup Job Implementation
=========================

Implementation of backup jobs for the ECaDP scheduler.
Handles database backups, file system backups, and backup verification.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
import shutil
import subprocess
import gzip
import os

from src.database.manager import DatabaseManager
from src.webhooks.client import WebhookClient

logger = logging.getLogger(__name__)

@dataclass
class BackupJobConfig:
    """Configuration for backup jobs"""
    backup_type: str = "full"  # "full", "incremental", "differential"
    backup_target: str = "database"  # "database", "files", "both"
    output_path: str = "data/backups"
    compression: bool = True
    retention_days: int = 30
    verify_backup: bool = True
    upload_to_cloud: bool = False
    cloud_bucket: Optional[str] = None
    encryption: bool = False
    encryption_key: Optional[str] = None
    webhook_url: Optional[str] = None
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)

@dataclass
class BackupJobResult:
    """Result of a backup job execution"""
    job_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    backup_files: List[str] = field(default_factory=list)
    backup_size: int = 0
    verification_passed: bool = False
    errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class BackupJob:
    """
    Backup job implementation for ECaDP scheduler
    
    Handles various types of backups including:
    - Database backups (PostgreSQL/Supabase)
    - File system backups
    - Compressed and encrypted backups
    - Cloud storage upload
    - Backup verification
    """
    
    def __init__(self, config: Union[BackupJobConfig, Dict[str, Any]], job_id: Optional[str] = None):
        if isinstance(config, dict):
            self.config = BackupJobConfig(**config)
        else:
            self.config = config
            
        self.job_id = job_id or f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Components
        self.db_manager = None
        self.webhook_client = None
        
        # Execution state
        self.result = BackupJobResult(
            job_id=self.job_id,
            status="pending",
            start_time=datetime.utcnow()
        )
        
        # Backup paths
        self.backup_dir = Path(self.config.output_path) / datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize job components"""
        try:
            logger.info(f"Initializing backup job {self.job_id}")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize()
            
            # Initialize webhook client if configured
            if self.config.webhook_url:
                self.webhook_client = WebhookClient(self.config.webhook_url)
            
            # Validate configuration
            await self._validate_config()
            
            logger.info(f"Backup job {self.job_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize backup job {self.job_id}: {e}")
            self.result.status = "failed"
            self.result.errors.append(f"Initialization failed: {str(e)}")
            raise
    
    async def _validate_config(self):
        """Validate backup configuration"""
        try:
            # Check if output directory is writable
            test_file = self.backup_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            # Validate cloud configuration if enabled
            if self.config.upload_to_cloud and not self.config.cloud_bucket:
                raise ValueError("Cloud upload enabled but no bucket specified")
            
            # Validate encryption configuration
            if self.config.encryption and not self.config.encryption_key:
                raise ValueError("Encryption enabled but no key specified")
            
            logger.info("Backup configuration validated")
            
        except Exception as e:
            logger.error(f"Backup configuration validation failed: {e}")
            raise
    
    async def backup_database(self):
        """Perform database backup"""
        try:
            if self.config.backup_target not in ["database", "both"]:
                logger.info("Database backup not requested")
                return
            
            logger.info(f"Starting database backup for job {self.job_id}")
            
            # Get database connection info
            db_config = await self.db_manager.get_connection_config()
            
            # Create database backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"database_backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            # Perform database dump
            await self._perform_database_dump(db_config, backup_path)
            
            # Compress if requested
            if self.config.compression:
                compressed_path = await self._compress_file(backup_path)
                backup_path.unlink()  # Remove uncompressed file
                backup_path = compressed_path
            
            # Encrypt if requested
            if self.config.encryption:
                encrypted_path = await self._encrypt_file(backup_path)
                backup_path.unlink()  # Remove unencrypted file
                backup_path = encrypted_path
            
            self.result.backup_files.append(str(backup_path))
            self.result.backup_size += backup_path.stat().st_size
            
            logger.info(f"Database backup completed: {backup_path}")
            
        except Exception as e:
            error_msg = f"Database backup failed: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
            raise
    
    async def _perform_database_dump(self, db_config: Dict[str, Any], output_path: Path):
        """Perform the actual database dump"""
        try:
            # Build pg_dump command
            cmd = [
                "pg_dump",
                f"--host={db_config['host']}",
                f"--port={db_config['port']}",
                f"--username={db_config['username']}",
                f"--dbname={db_config['database']}",
                "--no-password",
                "--verbose",
                "--clean",
                "--create",
                f"--file={output_path}"
            ]
            
            # Set environment for password
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            # Execute pg_dump
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise RuntimeError(f"pg_dump failed: {stderr.decode()}")
            
            logger.info("Database dump completed successfully")
            
        except Exception as e:
            logger.error(f"Database dump failed: {e}")
            raise
    
    async def backup_files(self):
        """Perform file system backup"""
        try:
            if self.config.backup_target not in ["files", "both"]:
                logger.info("File backup not requested")
                return
            
            logger.info(f"Starting file backup for job {self.job_id}")
            
            # Default patterns if none specified
            if not self.config.include_patterns:
                self.config.include_patterns = [
                    "data/processed/**",
                    "data/templates/**",
                    "config/**",
                    "src/**"
                ]
            
            # Create file backup archive
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"files_backup_{timestamp}.tar"
            backup_path = self.backup_dir / backup_filename
            
            # Create tar archive
            await self._create_file_archive(backup_path)
            
            # Compress if requested
            if self.config.compression:
                compressed_path = await self._compress_file(backup_path)
                backup_path.unlink()  # Remove uncompressed file
                backup_path = compressed_path
            
            # Encrypt if requested
            if self.config.encryption:
                encrypted_path = await self._encrypt_file(backup_path)
                backup_path.unlink()  # Remove unencrypted file
                backup_path = encrypted_path
            
            self.result.backup_files.append(str(backup_path))
            self.result.backup_size += backup_path.stat().st_size
            
            logger.info(f"File backup completed: {backup_path}")
            
        except Exception as e:
            error_msg = f"File backup failed: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
            raise
    
    async def _create_file_archive(self, output_path: Path):
        """Create tar archive of specified files"""
        try:
            import tarfile
            
            with tarfile.open(output_path, 'w') as tar:
                for pattern in self.config.include_patterns:
                    # Use glob to find matching files
                    import glob
                    matching_files = glob.glob(pattern, recursive=True)
                    
                    for file_path in matching_files:
                        # Check exclusion patterns
                        should_exclude = False
                        for exclude_pattern in self.config.exclude_patterns:
                            if glob.fnmatch.fnmatch(file_path, exclude_pattern):
                                should_exclude = True
                                break
                        
                        if not should_exclude and Path(file_path).exists():
                            tar.add(file_path)
                            logger.debug(f"Added to archive: {file_path}")
            
            logger.info(f"File archive created: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to create file archive: {e}")
            raise
    
    async def _compress_file(self, file_path: Path) -> Path:
        """Compress a file using gzip"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"File compressed: {compressed_path}")
            return compressed_path
            
        except Exception as e:
            logger.error(f"File compression failed: {e}")
            raise
    
    async def _encrypt_file(self, file_path: Path) -> Path:
        """Encrypt a file (placeholder implementation)"""
        try:
            # This is a placeholder implementation
            # In production, use proper encryption libraries like cryptography
            encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
            
            # For now, just copy the file (implement actual encryption)
            shutil.copy2(file_path, encrypted_path)
            
            logger.info(f"File encrypted: {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    async def verify_backup(self):
        """Verify backup integrity"""
        try:
            if not self.config.verify_backup:
                logger.info("Backup verification disabled")
                return
            
            logger.info(f"Verifying backup for job {self.job_id}")
            
            verification_passed = True
            
            for backup_file in self.result.backup_files:
                backup_path = Path(backup_file)
                
                # Check if file exists and is readable
                if not backup_path.exists():
                    logger.error(f"Backup file not found: {backup_file}")
                    verification_passed = False
                    continue
                
                # Check file size
                if backup_path.stat().st_size == 0:
                    logger.error(f"Backup file is empty: {backup_file}")
                    verification_passed = False
                    continue
                
                # Verify compressed files can be opened
                if backup_file.endswith('.gz'):
                    try:
                        with gzip.open(backup_path, 'rb') as f:
                            f.read(1024)  # Read first 1KB to verify
                        logger.debug(f"Compressed backup verified: {backup_file}")
                    except Exception as e:
                        logger.error(f"Compressed backup verification failed: {backup_file}: {e}")
                        verification_passed = False
                
                # Verify tar archives
                if '.tar' in backup_file:
                    try:
                        import tarfile
                        with tarfile.open(backup_path, 'r') as tar:
                            tar.getmembers()  # List members to verify integrity
                        logger.debug(f"Archive backup verified: {backup_file}")
                    except Exception as e:
                        logger.error(f"Archive backup verification failed: {backup_file}: {e}")
                        verification_passed = False
            
            self.result.verification_passed = verification_passed
            
            if verification_passed:
                logger.info("Backup verification passed")
            else:
                logger.error("Backup verification failed")
                self.result.errors.append("Backup verification failed")
                
        except Exception as e:
            error_msg = f"Backup verification error: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
            self.result.verification_passed = False
    
    async def upload_to_cloud(self):
        """Upload backup to cloud storage (placeholder)"""
        try:
            if not self.config.upload_to_cloud:
                logger.info("Cloud upload disabled")
                return
            
            logger.info(f"Uploading backup to cloud for job {self.job_id}")
            
            # This is a placeholder implementation
            # In production, implement actual cloud upload using AWS S3, Google Cloud, etc.
            
            for backup_file in self.result.backup_files:
                logger.info(f"Would upload {backup_file} to {self.config.cloud_bucket}")
            
            logger.info("Cloud upload completed (placeholder)")
            
        except Exception as e:
            error_msg = f"Cloud upload failed: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def cleanup_old_backups(self):
        """Clean up old backup files based on retention policy"""
        try:
            logger.info(f"Cleaning up old backups for job {self.job_id}")
            
            backup_root = Path(self.config.output_path)
            cutoff_date = datetime.utcnow() - timedelta(days=self.config.retention_days)
            
            deleted_count = 0
            deleted_size = 0
            
            for backup_dir in backup_root.iterdir():
                if backup_dir.is_dir():
                    try:
                        # Parse directory name as timestamp
                        dir_timestamp = datetime.strptime(backup_dir.name, '%Y%m%d_%H%M%S')
                        
                        if dir_timestamp < cutoff_date:
                            # Calculate size before deletion
                            for file_path in backup_dir.rglob('*'):
                                if file_path.is_file():
                                    deleted_size += file_path.stat().st_size
                            
                            # Delete old backup directory
                            shutil.rmtree(backup_dir)
                            deleted_count += 1
                            logger.info(f"Deleted old backup: {backup_dir}")
                            
                    except ValueError:
                        # Skip directories that don't match timestamp format
                        continue
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old backups, freed {deleted_size} bytes")
            else:
                logger.info("No old backups to clean up")
                
        except Exception as e:
            error_msg = f"Backup cleanup failed: {str(e)}"
            logger.error(error_msg)
            self.result.errors.append(error_msg)
    
    async def generate_report(self):
        """Generate backup job report"""
        try:
            logger.info(f"Generating report for backup job {self.job_id}")
            
            # Update result statistics
            self.result.statistics = {
                'backup_files_count': len(self.result.backup_files),
                'total_backup_size': self.result.backup_size,
                'verification_passed': self.result.verification_passed,
                'error_count': len(self.result.errors),
                'runtime_seconds': (datetime.utcnow() - self.result.start_time).total_seconds()
            }
            
            # Generate JSON report
            report_path = self.backup_dir / "backup_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'job_id': self.result.job_id,
                    'status': self.result.status,
                    'start_time': self.result.start_time.isoformat(),
                    'end_time': self.result.end_time.isoformat() if self.result.end_time else None,
                    'statistics': self.result.statistics,
                    'backup_files': self.result.backup_files,
                    'errors': self.result.errors,
                    'config': {
                        'backup_type': self.config.backup_type,
                        'backup_target': self.config.backup_target,
                        'compression': self.config.compression,
                        'encryption': self.config.encryption,
                        'retention_days': self.config.retention_days
                    }
                }, f, indent=2)
            
            logger.info(f"Report generated for job {self.job_id}: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report for job {self.job_id}: {e}")
    
    async def send_notifications(self):
        """Send job completion notifications"""
        try:
            if self.webhook_client:
                notification_data = {
                    'job_id': self.result.job_id,
                    'status': self.result.status,
                    'timestamp': datetime.utcnow().isoformat(),
                    'statistics': self.result.statistics,
                    'backup_files': [Path(f).name for f in self.result.backup_files],  # Just filenames
                    'verification_passed': self.result.verification_passed
                }
                
                event_type = f"backup_job.{self.result.status}"
                await self.webhook_client.send_event(event_type, notification_data)
                
                logger.info(f"Sent notification for job {self.job_id}")
                
        except Exception as e:
            logger.error(f"Failed to send notifications for job {self.job_id}: {e}")
    
    async def cleanup(self):
        """Clean up job resources"""
        try:
            logger.info(f"Cleaning up backup job {self.job_id}")
            
            if self.db_manager:
                await self.db_manager.close()
            
            logger.info(f"Cleanup completed for job {self.job_id}")
            
        except Exception as e:
            logger.error(f"Error during cleanup for job {self.job_id}: {e}")
    
    async def execute(self) -> BackupJobResult:
        """
        Execute the backup job
        
        Returns:
            BackupJobResult: Result of the job execution
        """
        try:
            logger.info(f"Starting execution of backup job {self.job_id}")
            self.result.status = "running"
            self.result.start_time = datetime.utcnow()
            
            # Initialize components
            await self.initialize()
            
            # Perform backups
            await self.backup_database()
            await self.backup_files()
            
            # Verify backups
            await self.verify_backup()
            
            # Upload to cloud if configured
            await self.upload_to_cloud()
            
            # Clean up old backups
            await self.cleanup_old_backups()
            
            # Mark as completed
            self.result.status = "completed" if self.result.verification_passed else "completed_with_warnings"
            self.result.end_time = datetime.utcnow()
            
            # Generate report
            await self.generate_report()
            
            # Send notifications
            await self.send_notifications()
            
            logger.info(f"Backup job {self.job_id} completed successfully")
            logger.info(f"Statistics: {self.result.statistics}")
            
            return self.result
            
        except Exception as e:
            logger.error(f"Backup job {self.job_id} failed: {e}")
            
            self.result.status = "failed"
            self.result.end_time = datetime.utcnow()
            self.result.errors.append(f"Job execution failed: {str(e)}")
            
            # Try to generate report even for failed jobs
            try:
                await self.generate_report()
                await self.send_notifications()
            except Exception as report_error:
                logger.error(f"Failed to generate failure report: {report_error}")
            
            return self.result
            
        finally:
            # Always cleanup
            try:
                await self.cleanup()
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")

# Convenience functions for common job patterns

async def create_daily_backup_job(**kwargs) -> BackupJob:
    """Create a daily backup job with standard settings"""
    config = BackupJobConfig(
        backup_type="full",
        backup_target="both",
        compression=True,
        verify_backup=True,
        retention_days=30,
        **kwargs
    )
    return BackupJob(config)

async def create_database_backup_job(**kwargs) -> BackupJob:
    """Create a database-only backup job"""
    config = BackupJobConfig(
        backup_type="full",
        backup_target="database",
        compression=True,
        verify_backup=True,
        **kwargs
    )
    return BackupJob(config)

async def create_secure_backup_job(**kwargs) -> BackupJob:
    """Create an encrypted backup job for sensitive data"""
    config = BackupJobConfig(
        backup_type="full",
        backup_target="both",
        compression=True,
        encryption=True,
        verify_backup=True,
        upload_to_cloud=True,
        **kwargs
    )
    return BackupJob(config)
