"""
Privacy Service

Handles GDPR/privacy compliance including PII detection, data erasure,
data portability, and privacy request management.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from src.settings import get_settings
from src.database.manager import DatabaseManager
from src.database.models import (
    PrivacyRequest, ExtractedItem, User, Job, PIIScanResult,
    PrivacyRequestType, PrivacyRequestStatus
)
from src.services.notification_service import get_notification_service, NotificationType, NotificationContext
from src.utils.logger import get_logger
from src.exporters.json_exporter import JsonExporter

logger = get_logger(__name__)


class PIIType(Enum):
    """Types of personally identifiable information."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    NAME = "name"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"


@dataclass
class PIIMatch:
    """A detected PII match in content."""
    pii_type: PIIType
    value: str
    confidence: float
    start_pos: int
    end_pos: int
    context: str  # Surrounding text


class PIIDetector:
    """Detects PII in text content."""
    
    def __init__(self):
        # Regex patterns for different PII types
        self.patterns = {
            PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            PIIType.PHONE: re.compile(r'\b(?:\+1[-.]?)?\s*\(?[0-9]{3}\)?[-.]?\s*[0-9]{3}[-.]?\s*[0-9]{4}\b'),
            PIIType.SSN: re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            PIIType.CREDIT_CARD: re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'),
            PIIType.IP_ADDRESS: re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
        }
        
        # Common name patterns (simplified)
        self.name_patterns = [
            re.compile(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'),  # First Last
            re.compile(r'\b[A-Z][a-z]+, [A-Z][a-z]+\b'),  # Last, First
        ]
    
    def detect_pii(self, text: str, max_context_chars: int = 50) -> List[PIIMatch]:
        """Detect PII in text content."""
        matches = []
        
        # Check regex patterns
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                context_start = max(0, match.start() - max_context_chars)
                context_end = min(len(text), match.end() + max_context_chars)
                context = text[context_start:context_end]
                
                matches.append(PIIMatch(
                    pii_type=pii_type,
                    value=match.group(),
                    confidence=0.9,  # High confidence for regex matches
                    start_pos=match.start(),
                    end_pos=match.end(),
                    context=context
                ))
        
        # Check name patterns (lower confidence)
        for pattern in self.name_patterns:
            for match in pattern.finditer(text):
                # Skip common non-names
                potential_name = match.group()
                if self._is_likely_name(potential_name):
                    context_start = max(0, match.start() - max_context_chars)
                    context_end = min(len(text), match.end() + max_context_chars)
                    context = text[context_start:context_end]
                    
                    matches.append(PIIMatch(
                        pii_type=PIIType.NAME,
                        value=potential_name,
                        confidence=0.6,  # Lower confidence for name detection
                        start_pos=match.start(),
                        end_pos=match.end(),
                        context=context
                    ))
        
        return matches
    
    def _is_likely_name(self, text: str) -> bool:
        """Check if text is likely a person's name."""
        # Skip common non-name patterns
        skip_patterns = [
            'New York', 'Los Angeles', 'San Francisco', 'United States',
            'Google Inc', 'Microsoft Corp', 'Apple Inc',
            'Monday Tuesday', 'January February'
        ]
        
        return not any(pattern.lower() in text.lower() for pattern in skip_patterns)


class PrivacyService:
    """Service for handling privacy requests and PII management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.db_manager = DatabaseManager()
        self.pii_detector = PIIDetector()
        self.notification_service = get_notification_service()
    
    async def create_privacy_request(
        self,
        request_type: PrivacyRequestType,
        subject_reference: str,
        contact_email: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new privacy request."""
        logger.info(f"Creating privacy request: {request_type.value} for {subject_reference}")
        
        async with self.db_manager.get_session() as session:
            request = PrivacyRequest(
                type=request_type,
                subject_reference=subject_reference,
                contact_email=contact_email,
                description=description or "",
                status=PrivacyRequestStatus.PENDING,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            session.add(request)
            await session.commit()
            
            # Send notification
            await self._notify_privacy_request_created(request)
            
            return str(request.id)
    
    async def process_erasure_request(self, request_id: str) -> Dict[str, Any]:
        """Process a data erasure request."""
        logger.info(f"Processing erasure request: {request_id}")
        
        async with self.db_manager.get_session() as session:
            request = session.query(PrivacyRequest).filter(
                PrivacyRequest.id == request_id
            ).first()
            
            if not request:
                raise Exception(f"Privacy request {request_id} not found")
            
            if request.type != PrivacyRequestType.ERASURE:
                raise Exception(f"Request {request_id} is not an erasure request")
            
            # Update status
            request.status = PrivacyRequestStatus.IN_PROGRESS
            await session.commit()
            
            try:
                # Find all data related to the subject
                erased_records = await self._erase_subject_data(
                    request.subject_reference,
                    session
                )
                
                # Update request with results
                request.status = PrivacyRequestStatus.COMPLETED
                request.finished_at = datetime.utcnow()
                request.result = {
                    "erased_records": erased_records,
                    "completed_at": datetime.utcnow().isoformat()
                }
                await session.commit()
                
                # Send completion notification
                await self._notify_privacy_request_completed(request)
                
                logger.info(f"Completed erasure request {request_id}: {erased_records} records erased")
                
                return {
                    "status": "completed",
                    "erased_records": erased_records
                }
                
            except Exception as e:
                logger.error(f"Failed to process erasure request {request_id}: {e}")
                
                request.status = PrivacyRequestStatus.FAILED
                request.result = {"error": str(e)}
                await session.commit()
                
                raise
    
    async def process_portability_request(self, request_id: str) -> Dict[str, Any]:
        """Process a data portability request."""
        logger.info(f"Processing portability request: {request_id}")
        
        async with self.db_manager.get_session() as session:
            request = session.query(PrivacyRequest).filter(
                PrivacyRequest.id == request_id
            ).first()
            
            if not request:
                raise Exception(f"Privacy request {request_id} not found")
            
            if request.type != PrivacyRequestType.PORTABILITY:
                raise Exception(f"Request {request_id} is not a portability request")
            
            # Update status
            request.status = PrivacyRequestStatus.IN_PROGRESS
            await session.commit()
            
            try:
                # Export all data related to the subject
                export_data = await self._export_subject_data(
                    request.subject_reference,
                    session
                )
                
                # Create export file
                export_filename = f"privacy_export_{request_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                export_path = f"data/exports/privacy/{export_filename}"
                
                exporter = JsonExporter()
                await exporter.export_data(export_data, export_path)
                
                # Update request
                request.status = PrivacyRequestStatus.COMPLETED
                request.finished_at = datetime.utcnow()
                request.result = {
                    "export_file": export_path,
                    "record_count": len(export_data),
                    "completed_at": datetime.utcnow().isoformat()
                }
                await session.commit()
                
                # Send completion notification
                await self._notify_privacy_request_completed(request)
                
                logger.info(f"Completed portability request {request_id}: {len(export_data)} records exported")
                
                return {
                    "status": "completed",
                    "export_file": export_path,
                    "record_count": len(export_data)
                }
                
            except Exception as e:
                logger.error(f"Failed to process portability request {request_id}: {e}")
                
                request.status = PrivacyRequestStatus.FAILED
                request.result = {"error": str(e)}
                await session.commit()
                
                raise
    
    async def scan_pii(self, item_id: Optional[str] = None, job_id: Optional[str] = None) -> Dict[str, Any]:
        """Scan for PII in extracted items."""
        logger.info(f"Starting PII scan - item_id: {item_id}, job_id: {job_id}")
        
        scan_results = []
        items_scanned = 0
        pii_found = 0
        
        async with self.db_manager.get_session() as session:
            # Build query
            query = session.query(ExtractedItem)
            
            if item_id:
                query = query.filter(ExtractedItem.id == item_id)
            elif job_id:
                query = query.filter(ExtractedItem.job_id == job_id)
            else:
                # Scan recent items (last 24 hours)
                since = datetime.utcnow() - timedelta(hours=24)
                query = query.filter(ExtractedItem.created_at >= since)
            
            items = query.all()
            
            for item in items:
                items_scanned += 1
                
                # Convert item data to text for scanning
                item_text = self._extract_text_from_item(item)
                
                # Detect PII
                pii_matches = self.pii_detector.detect_pii(item_text)
                
                if pii_matches:
                    pii_found += 1
                    
                    # Save scan results
                    for match in pii_matches:
                        scan_result = PIIScanResult(
                            item_id=item.id,
                            pii_type=match.pii_type.value,
                            snippet=match.context,
                            confidence=match.confidence,
                            created_at=datetime.utcnow()
                        )
                        session.add(scan_result)
                        
                        scan_results.append({
                            "item_id": item.id,
                            "pii_type": match.pii_type.value,
                            "confidence": match.confidence,
                            "snippet": match.context
                        })
            
            await session.commit()
        
        logger.info(f"PII scan completed: {items_scanned} items scanned, {pii_found} items with PII found")
        
        return {
            "items_scanned": items_scanned,
            "items_with_pii": pii_found,
            "pii_matches": len(scan_results),
            "results": scan_results
        }
    
    async def _erase_subject_data(self, subject_reference: str, session: Session) -> int:
        """Erase all data related to a subject."""
        erased_count = 0
        
        # Find items that contain the subject reference
        items = session.query(ExtractedItem).all()
        
        for item in items:
            item_text = self._extract_text_from_item(item)
            
            # Check if this item contains the subject reference
            if subject_reference.lower() in item_text.lower():
                # Mark for erasure or actually delete
                if self.settings.privacy_soft_delete:
                    item.payload_json = {"erased": True, "erased_at": datetime.utcnow().isoformat()}
                else:
                    session.delete(item)
                
                erased_count += 1
        
        # Also erase PII scan results
        pii_results = session.query(PIIScanResult).join(ExtractedItem).filter(
            ExtractedItem.payload_json.contains(subject_reference)
        ).all()
        
        for result in pii_results:
            session.delete(result)
        
        return erased_count
    
    async def _export_subject_data(self, subject_reference: str, session: Session) -> List[Dict[str, Any]]:
        """Export all data related to a subject."""
        export_data = []
        
        # Find items that contain the subject reference
        items = session.query(ExtractedItem).all()
        
        for item in items:
            item_text = self._extract_text_from_item(item)
            
            # Check if this item contains the subject reference
            if subject_reference.lower() in item_text.lower():
                export_data.append({
                    "id": str(item.id),
                    "job_id": str(item.job_id),
                    "template_id": str(item.template_id) if item.template_id else None,
                    "item_key": item.item_key,
                    "data": item.payload_json,
                    "created_at": item.created_at.isoformat(),
                    "source_url": item.lineage_json.get("url") if item.lineage_json else None
                })
        
        return export_data
    
    def _extract_text_from_item(self, item: ExtractedItem) -> str:
        """Extract text content from an extracted item for scanning."""
        if not item.payload_json:
            return ""
        
        # Convert JSON to text
        if isinstance(item.payload_json, dict):
            text_parts = []
            for key, value in item.payload_json.items():
                if isinstance(value, (str, int, float)):
                    text_parts.append(str(value))
                elif isinstance(value, list):
                    text_parts.extend(str(v) for v in value if isinstance(v, (str, int, float)))
            return " ".join(text_parts)
        else:
            return str(item.payload_json)
    
    async def _notify_privacy_request_created(self, request: PrivacyRequest):
        """Send notification when privacy request is created."""
        context = NotificationContext(
            user_email=request.contact_email,
            metadata={
                "request_id": str(request.id),
                "request_type": request.type.value,
                "subject_reference": request.subject_reference
            }
        )
        
        await self.notification_service.send_notification(
            NotificationType.PRIVACY_REQUEST,
            context,
            [],  # No specific channels, handled by admin
            []
        )
    
    async def _notify_privacy_request_completed(self, request: PrivacyRequest):
        """Send notification when privacy request is completed."""
        context = NotificationContext(
            user_email=request.contact_email,
            metadata={
                "request_id": str(request.id),
                "request_type": request.type.value,
                "completed_at": request.finished_at.isoformat() if request.finished_at else None
            }
        )
        
        await self.notification_service.send_notification(
            NotificationType.PRIVACY_REQUEST,
            context,
            [],
            [request.contact_email]
        )


# Global service instance
_privacy_service = None

def get_privacy_service() -> PrivacyService:
    """Get the global privacy service instance."""
    global _privacy_service
    if _privacy_service is None:
        _privacy_service = PrivacyService()
    return _privacy_service
