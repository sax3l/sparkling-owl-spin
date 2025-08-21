"""
Erasure worker job for GDPR compliance and data deletion.

Implements:
- Cascading data deletion across all systems
- GDPR right-to-be-forgotten requests
- Data anonymization and pseudonymization
- Audit trail for deletion operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import json
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)

class ErasureType(Enum):
    """Types of data erasure operations."""
    GDPR_REQUEST = "gdpr_request"
    RETENTION_CLEANUP = "retention_cleanup"
    MANUAL_DELETION = "manual_deletion"
    ANONYMIZATION = "anonymization"

class ErasureStatus(Enum):
    """Status of erasure operations."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"

class ErasureWorker:
    """Manages data erasure operations across all system components."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.deletion_order = [
            "exports",
            "crawl_results", 
            "proxy_logs",
            "cache_entries",
            "session_data",
            "user_profiles",
            "audit_logs"
        ]
    
    def _default_config(self) -> Dict:
        """Default erasure configuration."""
        return {
            "batch_size": 1000,
            "max_retries": 3,
            "cascade_delay_ms": 100,
            "verification_enabled": True,
            "audit_trail": True
        }
    
    async def process_erasure_request(self, request_id: str, entity_type: str, 
                                    entity_id: str, erasure_type: ErasureType) -> Dict:
        """Process a data erasure request."""
        logger.info(f"Processing erasure request {request_id} for {entity_type}:{entity_id}")
        
        operation_log = {
            "request_id": request_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "erasure_type": erasure_type.value,
            "started_at": datetime.utcnow(),
            "status": ErasureStatus.IN_PROGRESS.value,
            "deleted_records": {},
            "errors": []
        }
        
        try:
            # Update status to in progress
            await self._update_erasure_status(request_id, ErasureStatus.IN_PROGRESS)
            
            # Perform cascading deletion
            deletion_results = await self._cascade_delete(entity_type, entity_id)
            operation_log["deleted_records"] = deletion_results
            
            # Verify deletion if enabled
            if self.config["verification_enabled"]:
                verification_results = await self._verify_deletion(entity_type, entity_id)
                operation_log["verification"] = verification_results
                
                if not verification_results["complete"]:
                    operation_log["status"] = ErasureStatus.PARTIAL.value
                    logger.warning(f"Partial deletion for {request_id}: {verification_results}")
                else:
                    operation_log["status"] = ErasureStatus.COMPLETED.value
            else:
                operation_log["status"] = ErasureStatus.COMPLETED.value
            
            operation_log["completed_at"] = datetime.utcnow()
            
            # Update final status
            await self._update_erasure_status(request_id, 
                                            ErasureStatus(operation_log["status"]))
            
            # Log audit trail
            if self.config["audit_trail"]:
                await self._log_audit_trail(operation_log)
            
            logger.info(f"Erasure request {request_id} completed with status: {operation_log['status']}")
            return operation_log
            
        except Exception as e:
            operation_log["status"] = ErasureStatus.FAILED.value
            operation_log["errors"].append(str(e))
            operation_log["completed_at"] = datetime.utcnow()
            
            await self._update_erasure_status(request_id, ErasureStatus.FAILED)
            logger.error(f"Erasure request {request_id} failed: {e}")
            return operation_log
    
    async def _cascade_delete(self, entity_type: str, entity_id: str) -> Dict[str, int]:
        """Perform cascading deletion across all data stores."""
        deletion_results = {}
        
        for table in self.deletion_order:
            try:
                count = await self._delete_from_table(table, entity_type, entity_id)
                deletion_results[table] = count
                
                # Small delay to prevent overwhelming the database
                await asyncio.sleep(self.config["cascade_delay_ms"] / 1000)
                
            except Exception as e:
                logger.error(f"Failed to delete from {table}: {e}")
                deletion_results[table] = -1  # Indicate error
        
        # Delete from Redis cache
        cache_count = await self._delete_from_cache(entity_type, entity_id)
        deletion_results["cache"] = cache_count
        
        # Delete from S3 if applicable
        s3_count = await self._delete_from_s3(entity_type, entity_id)
        deletion_results["s3_objects"] = s3_count
        
        return deletion_results
    
    async def _delete_from_table(self, table: str, entity_type: str, entity_id: str) -> int:
        """Delete records from a specific database table."""
        # This would use the actual database connection
        # For now, simulating the operation
        
        delete_queries = {
            "exports": f"DELETE FROM exports WHERE {entity_type}_id = $1",
            "crawl_results": f"DELETE FROM crawl_results WHERE {entity_type}_id = $1",
            "proxy_logs": f"DELETE FROM proxy_logs WHERE {entity_type}_id = $1",
            "cache_entries": f"DELETE FROM cache_entries WHERE entity_type = $1 AND entity_id = $2",
            "session_data": f"DELETE FROM session_data WHERE {entity_type}_id = $1",
            "user_profiles": f"DELETE FROM user_profiles WHERE id = $1" if entity_type == "user" else "SELECT 0",
            "audit_logs": f"DELETE FROM audit_logs WHERE {entity_type}_id = $1"
        }
        
        query = delete_queries.get(table)
        if not query or query.startswith("SELECT"):
            return 0
        
        # Simulate database deletion
        logger.info(f"Executing deletion from {table} for {entity_type}:{entity_id}")
        
        # In a real implementation, this would execute the SQL query
        # and return the number of affected rows
        simulated_count = 5  # Placeholder
        
        return simulated_count
    
    async def _delete_from_cache(self, entity_type: str, entity_id: str) -> int:
        """Delete cache entries for the entity."""
        cache_patterns = [
            f"cache:{entity_type}:{entity_id}:*",
            f"session:{entity_type}:{entity_id}",
            f"proxy:assignment:{entity_type}:{entity_id}",
            f"rate_limit:{entity_type}:{entity_id}"
        ]
        
        total_deleted = 0
        
        # In a real implementation, this would use Redis
        for pattern in cache_patterns:
            # Simulate cache deletion
            logger.info(f"Deleting cache entries matching: {pattern}")
            simulated_count = 3  # Placeholder
            total_deleted += simulated_count
        
        return total_deleted
    
    async def _delete_from_s3(self, entity_type: str, entity_id: str) -> int:
        """Delete S3 objects for the entity."""
        s3_prefixes = [
            f"exports/{entity_type}/{entity_id}/",
            f"raw_data/{entity_type}/{entity_id}/",
            f"processed/{entity_type}/{entity_id}/"
        ]
        
        total_deleted = 0
        
        # In a real implementation, this would use boto3
        for prefix in s3_prefixes:
            logger.info(f"Deleting S3 objects with prefix: {prefix}")
            simulated_count = 2  # Placeholder
            total_deleted += simulated_count
        
        return total_deleted
    
    async def _verify_deletion(self, entity_type: str, entity_id: str) -> Dict:
        """Verify that all data has been properly deleted."""
        verification_results = {
            "complete": True,
            "remaining_records": {},
            "checked_at": datetime.utcnow()
        }
        
        # Check each data store for remaining records
        for table in self.deletion_order:
            count = await self._count_remaining_records(table, entity_type, entity_id)
            if count > 0:
                verification_results["complete"] = False
                verification_results["remaining_records"][table] = count
        
        # Check cache
        cache_count = await self._count_remaining_cache_entries(entity_type, entity_id)
        if cache_count > 0:
            verification_results["complete"] = False
            verification_results["remaining_records"]["cache"] = cache_count
        
        return verification_results
    
    async def _count_remaining_records(self, table: str, entity_type: str, entity_id: str) -> int:
        """Count remaining records in a table after deletion."""
        # In a real implementation, this would query the database
        # For now, simulating verification
        return 0  # Assume deletion was successful
    
    async def _count_remaining_cache_entries(self, entity_type: str, entity_id: str) -> int:
        """Count remaining cache entries after deletion."""
        # In a real implementation, this would query Redis
        return 0  # Assume deletion was successful
    
    async def _update_erasure_status(self, request_id: str, status: ErasureStatus):
        """Update the status of an erasure request."""
        # In a real implementation, this would update the database
        logger.info(f"Updating erasure request {request_id} status to {status.value}")
    
    async def _log_audit_trail(self, operation_log: Dict):
        """Log the erasure operation for audit purposes."""
        audit_entry = {
            "operation_type": "data_erasure",
            "timestamp": datetime.utcnow(),
            "details": operation_log
        }
        
        # In a real implementation, this would write to audit log storage
        logger.info(f"Audit trail logged for erasure request {operation_log['request_id']}")
    
    async def process_batch_erasure(self, requests: List[Dict]) -> List[Dict]:
        """Process multiple erasure requests in batch."""
        logger.info(f"Processing batch erasure of {len(requests)} requests")
        
        results = []
        batch_size = self.config["batch_size"]
        
        # Process in batches to avoid overwhelming the system
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            batch_tasks = []
            
            for request in batch:
                task = self.process_erasure_request(
                    request["request_id"],
                    request["entity_type"],
                    request["entity_id"],
                    ErasureType(request["erasure_type"])
                )
                batch_tasks.append(task)
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Brief pause between batches
            await asyncio.sleep(1)
        
        logger.info(f"Completed batch erasure processing: {len(results)} results")
        return results

async def run_erasure_worker(requests: List[Dict]) -> List[Dict]:
    """Entry point for erasure worker job execution."""
    worker = ErasureWorker()
    if len(requests) == 1:
        request = requests[0]
        result = await worker.process_erasure_request(
            request["request_id"],
            request["entity_type"], 
            request["entity_id"],
            ErasureType(request["erasure_type"])
        )
        return [result]
    else:
        return await worker.process_batch_erasure(requests)