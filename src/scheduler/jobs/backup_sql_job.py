"""
SQL backup job for automated database backups.

Provides comprehensive database backup functionality with
rotation, compression, and storage management.
"""

import os
import subprocess
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

class SQLBackupJob:
    """
    SQL backup job for database maintenance.
    
    Features:
    - Automated PostgreSQL backups
    - Backup rotation and retention
    - Compression and storage optimization
    - Error handling and notifications
    """
    
    def __init__(self,
                 backup_dir: str = "data/backups",
                 retention_days: int = 30,
                 compress: bool = True,
                 max_backups: int = 50):
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.compress = compress
        self.max_backups = max_backups
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute SQL backup job"""
        try:
            logger.info("Starting SQL backup job")
            
            # Get database configuration
            db_config = self._get_db_config(**kwargs)
            
            # Generate backup filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            # Create backup
            backup_size = await self._create_backup(db_config, backup_path)
            
            # Compress if enabled
            if self.compress:
                compressed_path = await self._compress_backup(backup_path)
                backup_path.unlink()  # Remove uncompressed version
                backup_path = compressed_path
                backup_filename = compressed_path.name
            
            # Clean old backups
            cleaned_count = await self._cleanup_old_backups()
            
            result = {
                "success": True,
                "backup_file": backup_filename,
                "backup_size": backup_size,
                "cleaned_backups": cleaned_count,
                "backup_path": str(backup_path)
            }
            
            logger.info(f"SQL backup completed: {backup_filename}")
            return result
            
        except Exception as e:
            logger.error(f"SQL backup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_db_config(self, **kwargs) -> Dict[str, str]:
        """Get database configuration"""
        # Default configuration - would typically come from environment or config
        return {
            "host": kwargs.get("host", os.getenv("DB_HOST", "localhost")),
            "port": kwargs.get("port", os.getenv("DB_PORT", "5432")),
            "database": kwargs.get("database", os.getenv("DB_NAME", "ecadp")),
            "username": kwargs.get("username", os.getenv("DB_USER", "postgres")),
            "password": kwargs.get("password", os.getenv("DB_PASSWORD", ""))
        }
    
    async def _create_backup(self, db_config: Dict[str, str], backup_path: Path) -> int:
        """Create database backup using pg_dump"""
        try:
            # Construct pg_dump command
            cmd = [
                "pg_dump",
                "-h", db_config["host"],
                "-p", db_config["port"],
                "-U", db_config["username"],
                "-d", db_config["database"],
                "--no-password",
                "--verbose",
                "--clean",
                "--create",
                "-f", str(backup_path)
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            if db_config["password"]:
                env["PGPASSWORD"] = db_config["password"]
            
            # Execute backup
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
            
            # Return backup file size
            return backup_path.stat().st_size
            
        except subprocess.TimeoutExpired:
            raise Exception("Backup timeout - process took too long")
        except FileNotFoundError:
            raise Exception("pg_dump not found - PostgreSQL client tools required")
        except Exception as e:
            if backup_path.exists():
                backup_path.unlink()  # Clean up partial backup
            raise
    
    async def _compress_backup(self, backup_path: Path) -> Path:
        """Compress backup file using gzip"""
        compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
        
        try:
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"Compressed backup: {backup_path.name} -> {compressed_path.name}")
            return compressed_path
            
        except Exception as e:
            if compressed_path.exists():
                compressed_path.unlink()
            raise Exception(f"Compression failed: {e}")
    
    async def _cleanup_old_backups(self) -> int:
        """Clean up old backup files based on retention policy"""
        if not self.backup_dir.exists():
            return 0
        
        cleaned_count = 0
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # Get all backup files
        backup_files = list(self.backup_dir.glob("backup_*.sql*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Remove files older than retention period
        for backup_file in backup_files:
            file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                try:
                    backup_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Removed old backup: {backup_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove {backup_file.name}: {e}")
        
        # Also enforce max backup count
        if len(backup_files) > self.max_backups:
            files_to_remove = backup_files[self.max_backups:]
            for backup_file in files_to_remove:
                try:
                    backup_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Removed excess backup: {backup_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove {backup_file.name}: {e}")
        
        return cleaned_count
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        if not self.backup_dir.exists():
            return {"total_backups": 0, "total_size": 0}
        
        backup_files = list(self.backup_dir.glob("backup_*.sql*"))
        total_size = sum(f.stat().st_size for f in backup_files)
        
        # Get oldest and newest
        if backup_files:
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            oldest = datetime.fromtimestamp(backup_files[0].stat().st_mtime)
            newest = datetime.fromtimestamp(backup_files[-1].stat().st_mtime)
        else:
            oldest = newest = None
        
        return {
            "total_backups": len(backup_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_backup": oldest.isoformat() if oldest else None,
            "newest_backup": newest.isoformat() if newest else None
        }

# Entry point for scheduler
async def execute_sql_backup_job(**kwargs) -> Dict[str, Any]:
    """Execute SQL backup job - entry point for scheduler"""
    job = SQLBackupJob()
    return await job.execute(**kwargs)