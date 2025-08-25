#!/usr/bin/env python3
"""
Swedish Integration Module
Specialized integration for Swedish websites, regulations, and data formats
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import logging

from shared.models.base import BaseService, ServiceStatus
from shared.utils.helpers import get_logger


class SwedishIntegration(BaseService):
    """Integration service for Swedish-specific functionality"""
    
    def __init__(self):
        super().__init__("swedish_integration", "Swedish Integration Service")
        
        self.logger = get_logger(__name__)
        
        # Swedish-specific configurations
        self.swedish_domains = [
            '.se', 'regeringen.se', 'riksdag.se', 'skatteverket.se',
            'bolagsverket.se', 'domstol.se', 'migrationsverket.se'
        ]
        
        self.swedish_data_formats = {
            'personnummer': r'^\d{6,8}[-]?\d{4}$',
            'organisationsnummer': r'^\d{6}-\d{4}$',
            'plusgiro': r'^\d{1,8}-\d{1}$',
            'bankgiro': r'^\d{3,4}-\d{4}$'
        }
        
        self.swedish_regulations = {
            'gdpr': 'EU General Data Protection Regulation',
            'pul': 'Personuppgiftslagen (outdated but relevant)',
            'offentlighetsprincipen': 'Swedish Public Access Principle'
        }
    
    async def start(self) -> None:
        """Start Swedish integration service"""
        self.status = ServiceStatus.STARTING
        self.logger.info("Starting Swedish Integration service...")
        
        try:
            await self._load_swedish_configurations()
            
            self.status = ServiceStatus.RUNNING
            self.logger.info("✅ Swedish Integration service started")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to start Swedish Integration service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop Swedish integration service"""
        self.status = ServiceStatus.STOPPING
        self.logger.info("Stopping Swedish Integration service...")
        
        try:
            self.status = ServiceStatus.STOPPED
            self.logger.info("✅ Swedish Integration service stopped")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to stop Swedish Integration service: {e}")
    
    async def _load_swedish_configurations(self) -> None:
        """Load Swedish-specific configurations and data"""
        self.logger.info("Loading Swedish configurations...")
        
        # Load Swedish holidays
        self.swedish_holidays = await self._load_swedish_holidays()
        
        # Load Swedish postal codes
        self.swedish_postal_codes = await self._load_swedish_postal_codes()
        
        # Load Swedish municipality codes
        self.swedish_municipalities = await self._load_swedish_municipalities()
        
        self.logger.info("Swedish configurations loaded successfully")
    
    async def _load_swedish_holidays(self) -> Dict[str, str]:
        """Load Swedish holidays"""
        return {
            'nyårsdagen': '2025-01-01',
            'trettondedag_jul': '2025-01-06',
            'långfredagen': '2025-04-18',  # Varies each year
            'annandag_påsk': '2025-04-21',  # Varies each year
            'första_maj': '2025-05-01',
            'kristi_himmelfärds_dag': '2025-05-29',  # Varies each year
            'nationaldagen': '2025-06-06',
            'midsommarafton': '2025-06-20',  # Varies each year
            'alla_helgons_dag': '2025-11-01',  # First Saturday after Oct 30
            'julafton': '2025-12-24',
            'juldagen': '2025-12-25',
            'annandag_jul': '2025-12-26'
        }
    
    async def _load_swedish_postal_codes(self) -> Dict[str, str]:
        """Load Swedish postal code mapping"""
        return {
            '100': 'Stockholm',
            '200': 'Malmö',
            '300': 'Göteborg',
            '400': 'Uppsala',
            '500': 'Västerås',
            # Would contain full mapping in production
        }
    
    async def _load_swedish_municipalities(self) -> Dict[str, str]:
        """Load Swedish municipality codes"""
        return {
            '0114': 'Upplands Väsby',
            '0115': 'Vallentuna',
            '0117': 'Österåker',
            '0120': 'Värmdö',
            '0123': 'Järfälla',
            # Would contain full mapping in production
        }
    
    def is_swedish_domain(self, url: str) -> bool:
        """Check if URL belongs to a Swedish domain"""
        return any(domain in url.lower() for domain in self.swedish_domains)
    
    def validate_personnummer(self, personnummer: str) -> Dict[str, Any]:
        """Validate Swedish personal number (personnummer)"""
        
        # Remove any spaces or hyphens
        cleaned = re.sub(r'[-\s]', '', personnummer)
        
        if len(cleaned) == 10:
            # Add century for 10-digit format
            if int(cleaned[:2]) > 25:  # Assuming born before 2025
                cleaned = '19' + cleaned
            else:
                cleaned = '20' + cleaned
        
        if len(cleaned) != 12:
            return {'valid': False, 'error': 'Invalid length'}
        
        # Extract parts
        year = int(cleaned[:4])
        month = int(cleaned[4:6])
        day = int(cleaned[6:8])
        control_digit = int(cleaned[11])
        
        # Validate date parts
        if not (1 <= month <= 12):
            return {'valid': False, 'error': 'Invalid month'}
        
        if not (1 <= day <= 31):
            return {'valid': False, 'error': 'Invalid day'}
        
        if year < 1900 or year > datetime.now().year:
            return {'valid': False, 'error': 'Invalid year'}
        
        # Luhn algorithm validation
        digits = [int(d) for d in cleaned[:10]]
        checksum = 0
        
        for i, digit in enumerate(digits):
            if i % 2 == 1:  # Every second digit
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10
            checksum += digit
        
        expected_control = (10 - (checksum % 10)) % 10
        
        if control_digit != expected_control:
            return {'valid': False, 'error': 'Invalid control digit'}
        
        return {
            'valid': True,
            'formatted': f"{cleaned[:8]}-{cleaned[8:]}",
            'birth_date': f"{year}-{month:02d}-{day:02d}",
            'gender': 'male' if int(cleaned[10]) % 2 == 1 else 'female'
        }
    
    def validate_organisationsnummer(self, orgnr: str) -> Dict[str, Any]:
        """Validate Swedish organization number"""
        
        # Remove any spaces or hyphens
        cleaned = re.sub(r'[-\s]', '', orgnr)
        
        if len(cleaned) != 10:
            return {'valid': False, 'error': 'Invalid length'}
        
        # Check format (should start with certain digits)
        first_two = int(cleaned[:2])
        if first_two < 16:
            return {'valid': False, 'error': 'Invalid organization number format'}
        
        # Luhn algorithm validation
        digits = [int(d) for d in cleaned]
        checksum = 0
        
        for i, digit in enumerate(digits[:-1]):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit = digit // 10 + digit % 10
            checksum += digit
        
        expected_control = (10 - (checksum % 10)) % 10
        control_digit = digits[-1]
        
        if control_digit != expected_control:
            return {'valid': False, 'error': 'Invalid control digit'}
        
        return {
            'valid': True,
            'formatted': f"{cleaned[:6]}-{cleaned[6:]}",
            'type': self._get_organization_type(cleaned[:2])
        }
    
    def _get_organization_type(self, prefix: str) -> str:
        """Get organization type based on prefix"""
        prefix_int = int(prefix)
        
        if 16 <= prefix_int <= 17:
            return 'Aktiebolag'
        elif prefix_int == 18:
            return 'Kommanditbolag'
        elif prefix_int == 19:
            return 'Öppet bolag'
        elif 20 <= prefix_int <= 25:
            return 'Statlig myndighet'
        elif 26 <= prefix_int <= 28:
            return 'Kommun/Landsting'
        elif prefix_int == 29:
            return 'Församling'
        else:
            return 'Okänd'
    
    def extract_swedish_addresses(self, text: str) -> List[Dict[str, Any]]:
        """Extract Swedish addresses from text"""
        
        # Swedish address pattern
        address_pattern = r'([A-ZÅÄÖ][a-zåäö\s]+(?:gata|vägen|torget|plan|backe|gränd|allé|stråket))\s*(\d+[A-Z]?),?\s*(\d{3}\s?\d{2})\s+([A-ZÅÄÖ][a-zåäö\s]+)'
        
        addresses = []
        matches = re.finditer(address_pattern, text)
        
        for match in matches:
            street = match.group(1).strip()
            number = match.group(2).strip()
            postal_code = match.group(3).replace(' ', '')
            city = match.group(4).strip()
            
            addresses.append({
                'street': street,
                'number': number,
                'postal_code': postal_code,
                'city': city,
                'full_address': f"{street} {number}, {postal_code[:3]} {postal_code[3:]} {city}"
            })
        
        return addresses
    
    def is_swedish_holiday(self, date_str: str) -> bool:
        """Check if a date is a Swedish holiday"""
        return date_str in self.swedish_holidays.values()
    
    def get_swedish_holiday_name(self, date_str: str) -> Optional[str]:
        """Get Swedish holiday name for a date"""
        for holiday_name, holiday_date in self.swedish_holidays.items():
            if holiday_date == date_str:
                return holiday_name.replace('_', ' ').title()
        return None
    
    def format_swedish_currency(self, amount: float) -> str:
        """Format amount as Swedish currency"""
        return f"{amount:,.2f} kr".replace(',', ' ')
    
    def get_compliance_requirements(self, domain: str) -> Dict[str, Any]:
        """Get compliance requirements for Swedish domains"""
        
        compliance = {
            'gdpr_applicable': True,
            'swedish_law_applicable': self.is_swedish_domain(domain),
            'data_retention_limits': True,
            'cookie_consent_required': True,
            'age_verification_required': False
        }
        
        if self.is_swedish_domain(domain):
            compliance.update({
                'offentlighetsprincipen_applicable': 'regeringen.se' in domain or 'riksdag.se' in domain,
                'language_requirements': 'Swedish',
                'accessibility_standards': 'WCAG 2.1 AA',
                'contact_information_required': True
            })
        
        return compliance
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get Swedish integration statistics"""
        return {
            'service_status': self.status.value,
            'supported_domains': len(self.swedish_domains),
            'supported_data_formats': len(self.swedish_data_formats),
            'loaded_holidays': len(getattr(self, 'swedish_holidays', {})),
            'loaded_postal_codes': len(getattr(self, 'swedish_postal_codes', {})),
            'loaded_municipalities': len(getattr(self, 'swedish_municipalities', {}))
        }
