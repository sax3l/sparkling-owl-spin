#!/usr/bin/env python3
"""
Swedish Company Data Adapter för Sparkling-Owl-Spin  
Integration med svenska företagsregister och företagsdatabaser
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
from urllib.parse import urljoin, urlencode

logger = logging.getLogger(__name__)

class CompanyDataSource(Enum):
    """Company data sources"""
    BOLAGSVERKET = "bolagsverket"
    ALLABOLAG = "allabolag"
    RATSIT = "ratsit"
    HITTA = "hitta"
    UC = "uc"  # UC AB
    MOCK = "mock"

class CompanyType(Enum):
    """Company types"""
    AB = "aktiebolag"  # Aktiebolag
    HB = "handelsbolag"  # Handelsbolag
    KB = "kommanditbolag"  # Kommanditbolag
    EK = "enskild_firma"  # Enskild firma
    BRF = "bostadsratt"  # Bostadsrättsförening
    EKONOMISK_FORENING = "ekonomisk_forening"
    STIFTELSE = "stiftelse"
    IDEELL_FORENING = "ideell_forening"
    OTHER = "övrigt"

class CompanyStatus(Enum):
    """Company status"""
    ACTIVE = "aktiv"
    INACTIVE = "vilande"
    LIQUIDATION = "under_likvidation"
    BANKRUPT = "konkurs"
    DISSOLVED = "upplöst"
    UNKNOWN = "okänt"

@dataclass
class CompanyAddress:
    """Company address information"""
    street: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    municipality: Optional[str] = None
    county: Optional[str] = None
    country: str = "Sverige"
    
    @property
    def full_address(self) -> str:
        """Get full formatted address"""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.postal_code and self.city:
            parts.append(f"{self.postal_code} {self.city}")
        elif self.city:
            parts.append(self.city)
        return ", ".join(parts)

@dataclass
class CompanyFinancials:
    """Company financial information"""
    revenue: Optional[int] = None  # Omsättning
    profit: Optional[int] = None   # Vinst
    employees: Optional[int] = None # Antal anställda
    equity: Optional[int] = None   # Eget kapital
    assets: Optional[int] = None   # Tillgångar
    year: Optional[int] = None     # År för uppgifterna
    currency: str = "SEK"

@dataclass
class CompanyInfo:
    """Company information"""
    org_number: str
    name: str
    company_type: Optional[CompanyType] = None
    status: Optional[CompanyStatus] = None
    registration_date: Optional[datetime] = None
    address: Optional[CompanyAddress] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    industry_code: Optional[str] = None  # SNI-kod
    industry_description: Optional[str] = None
    ceo_name: Optional[str] = None
    board_members: List[str] = field(default_factory=list)
    financials: Optional[CompanyFinancials] = None
    vat_registered: Optional[bool] = None
    f_tax_registered: Optional[bool] = None
    source: Optional[CompanyDataSource] = None
    last_updated: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age_years(self) -> Optional[int]:
        """Calculate company age in years"""
        if self.registration_date:
            return (datetime.now() - self.registration_date).days // 365
        return None
        
    @property
    def is_active(self) -> bool:
        """Check if company is active"""
        return self.status == CompanyStatus.ACTIVE

@dataclass
class CompanySearchResult:
    """Company search result"""
    query: str
    results: List[CompanyInfo]
    source: CompanyDataSource
    search_time: datetime
    total_results: int
    success: bool
    error_message: Optional[str] = None

class SwedishCompanyDataAdapter:
    """Swedish Company Data integration för company information lookup"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API endpoints (mock URLs - real ones would require proper authentication)
        self.endpoints = {
            CompanyDataSource.BOLAGSVERKET: "https://data.bolagsverket.se/api/",
            CompanyDataSource.ALLABOLAG: "https://www.allabolag.se/api/",
            CompanyDataSource.RATSIT: "https://www.ratsit.se/api/",
            CompanyDataSource.HITTA: "https://www.hitta.se/api/",
            CompanyDataSource.UC: "https://www.uc.se/api/"
        }
        
        # Rate limiting
        self.request_delays = {
            CompanyDataSource.BOLAGSVERKET: 2.0,  # Official API - be respectful
            CompanyDataSource.ALLABOLAG: 1.0,
            CompanyDataSource.RATSIT: 1.0,
            CompanyDataSource.HITTA: 0.5,
            CompanyDataSource.UC: 1.5
        }
        
        # Statistics
        self.stats = {
            "total_lookups": 0,
            "successful_lookups": 0,
            "failed_lookups": 0,
            "by_source": {},
            "by_company_type": {},
            "by_status": {},
            "cache_hits": 0,
            "api_errors": 0
        }
        
        # Simple cache
        self.cache = {}
        self.cache_ttl = 7200  # 2 hours (company data changes less frequently)
        
    async def initialize(self):
        """Initialize Swedish Company Data adapter"""
        try:
            logger.info("🏢 Initializing Swedish Company Data Adapter")
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Sparkling-Owl-Spin/1.0 (Company Data Lookup)',
                    'Accept': 'application/json',
                    'Accept-Language': 'sv-SE,sv;q=0.9,en;q=0.8'
                }
            )
            
            # Initialize statistics
            for source in CompanyDataSource:
                self.stats["by_source"][source.value] = {
                    "requests": 0,
                    "successes": 0,
                    "failures": 0
                }
                
            for company_type in CompanyType:
                self.stats["by_company_type"][company_type.value] = 0
                
            for status in CompanyStatus:
                self.stats["by_status"][status.value] = 0
            
            # Test connection to available APIs
            await self._test_api_connectivity()
            
            self.initialized = True
            logger.info("✅ Swedish Company Data Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Swedish Company Data: {str(e)}")
            # Create mock session för fallback
            self.session = aiohttp.ClientSession()
            self.initialized = True
            
    async def _test_api_connectivity(self):
        """Test connectivity to company data APIs"""
        logger.info("🔗 Testing company data API connectivity...")
        
        for source, endpoint in self.endpoints.items():
            try:
                # Mock test - just log
                logger.info(f"📡 {source.value}: {endpoint} (mock - not actually tested)")
                await asyncio.sleep(0.1)  # Simulate network delay
                
            except Exception as e:
                logger.warning(f"⚠️ API {source.value} not accessible: {str(e)}")
                
    async def lookup_company(self, identifier: str, 
                           preferred_sources: List[CompanyDataSource] = None) -> CompanySearchResult:
        """Look up company by organization number or name"""
        
        if not self.initialized:
            await self.initialize()
            
        # Determine lookup type and normalize identifier
        if self._is_org_number(identifier):
            org_number = self._normalize_org_number(identifier)
            search_key = f"org:{org_number}"
        else:
            # Company name search
            company_name = identifier.strip()
            search_key = f"name:{company_name.lower()}"
            
        # Check cache first
        cache_key = f"company:{search_key}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if datetime.now() - cached_result["timestamp"] < timedelta(seconds=self.cache_ttl):
                self.stats["cache_hits"] += 1
                logger.debug(f"💾 Cache hit för company: {identifier}")
                return cached_result["data"]
                
        # Determine sources to try
        sources_to_try = preferred_sources or [
            CompanyDataSource.BOLAGSVERKET,
            CompanyDataSource.ALLABOLAG,
            CompanyDataSource.RATSIT,
            CompanyDataSource.MOCK  # Always fallback to mock
        ]
        
        self.stats["total_lookups"] += 1
        
        # Try each source until we get results
        for source in sources_to_try:
            try:
                result = await self._lookup_from_source(identifier, source)
                
                if result.success and result.results:
                    # Cache successful result
                    self.cache[cache_key] = {
                        "data": result,
                        "timestamp": datetime.now()
                    }
                    
                    self.stats["successful_lookups"] += 1
                    self.stats["by_source"][source.value]["successes"] += 1
                    
                    # Update statistics
                    for company in result.results:
                        if company.company_type:
                            self.stats["by_company_type"][company.company_type.value] += 1
                        if company.status:
                            self.stats["by_status"][company.status.value] += 1
                            
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Error looking up company från {source.value}: {str(e)}")
                self.stats["by_source"][source.value]["failures"] += 1
                continue
                
        # All sources failed
        self.stats["failed_lookups"] += 1
        return CompanySearchResult(
            query=identifier,
            results=[],
            source=CompanyDataSource.MOCK,
            search_time=datetime.now(),
            total_results=0,
            success=False,
            error_message="No company data found från any source"
        )
        
    async def _lookup_from_source(self, identifier: str, 
                                source: CompanyDataSource) -> CompanySearchResult:
        """Look up company från specific source"""
        
        self.stats["by_source"][source.value]["requests"] += 1
        
        if source == CompanyDataSource.MOCK:
            return await self._mock_company_lookup(identifier)
        elif source == CompanyDataSource.BOLAGSVERKET:
            return await self._lookup_bolagsverket(identifier)
        elif source == CompanyDataSource.ALLABOLAG:
            return await self._lookup_allabolag(identifier)
        elif source == CompanyDataSource.RATSIT:
            return await self._lookup_ratsit(identifier)
        elif source == CompanyDataSource.HITTA:
            return await self._lookup_hitta(identifier)
        elif source == CompanyDataSource.UC:
            return await self._lookup_uc(identifier)
        else:
            return CompanySearchResult(
                query=identifier,
                results=[],
                source=source,
                search_time=datetime.now(),
                total_results=0,
                success=False,
                error_message=f"Unsupported source: {source}"
            )
            
    async def _mock_company_lookup(self, identifier: str) -> CompanySearchResult:
        """Mock company lookup för testing"""
        
        await asyncio.sleep(0.3)  # Simulate API delay
        
        # Mock company database
        mock_companies = {
            "556016-0680": CompanyInfo(
                org_number="556016-0680",
                name="Spotify Technology S.A.",
                company_type=CompanyType.AB,
                status=CompanyStatus.ACTIVE,
                registration_date=datetime(2006, 4, 23),
                address=CompanyAddress(
                    street="Birger Jarlsgatan 61",
                    postal_code="113 56",
                    city="Stockholm",
                    municipality="Stockholm",
                    county="Stockholms län"
                ),
                phone="+46 8 553 424 00",
                website="https://www.spotify.com",
                industry_code="62.01",
                industry_description="Dataprogrammering",
                ceo_name="Daniel Ek",
                board_members=["Martin Lorentzon", "Cristina Stenbeck"],
                financials=CompanyFinancials(
                    revenue=50000000000,  # 50 miljarder SEK
                    profit=2000000000,    # 2 miljarder SEK
                    employees=6600,
                    year=2023
                ),
                vat_registered=True,
                f_tax_registered=True,
                source=CompanyDataSource.MOCK
            ),
            "556036-0793": CompanyInfo(
                org_number="556036-0793", 
                name="King Digital Entertainment AB",
                company_type=CompanyType.AB,
                status=CompanyStatus.ACTIVE,
                registration_date=datetime(2003, 7, 15),
                address=CompanyAddress(
                    street="Sveavägen 44",
                    postal_code="111 34",
                    city="Stockholm",
                    municipality="Stockholm", 
                    county="Stockholms län"
                ),
                website="https://www.king.com",
                industry_code="58.21",
                industry_description="Utgivning av datorspel",
                ceo_name="Riccardo Zacconi",
                financials=CompanyFinancials(
                    revenue=20000000000,  # 20 miljarder SEK
                    employees=2000,
                    year=2023
                ),
                vat_registered=True,
                f_tax_registered=True,
                source=CompanyDataSource.MOCK
            ),
            "556467-4652": CompanyInfo(
                org_number="556467-4652",
                name="Klarna Holding AB",
                company_type=CompanyType.AB,
                status=CompanyStatus.ACTIVE,
                registration_date=datetime(2005, 2, 25),
                address=CompanyAddress(
                    street="Sveavägen 46",
                    postal_code="111 34", 
                    city="Stockholm",
                    municipality="Stockholm",
                    county="Stockholms län"
                ),
                website="https://www.klarna.com",
                industry_code="66.19",
                industry_description="Övrig finansiell verksamhet",
                ceo_name="Sebastian Siemiatkowski",
                financials=CompanyFinancials(
                    revenue=15000000000,  # 15 miljarder SEK
                    employees=4500,
                    year=2023
                ),
                vat_registered=True,
                f_tax_registered=True,
                source=CompanyDataSource.MOCK
            )
        }
        
        # Check if identifier matches any org number
        if self._is_org_number(identifier):
            org_number = self._normalize_org_number(identifier)
            if org_number in mock_companies:
                company = mock_companies[org_number]
                return CompanySearchResult(
                    query=identifier,
                    results=[company],
                    source=CompanyDataSource.MOCK,
                    search_time=datetime.now(),
                    total_results=1,
                    success=True
                )
        else:
            # Name search
            name_query = identifier.lower()
            matching_companies = []
            
            for company in mock_companies.values():
                if name_query in company.name.lower():
                    matching_companies.append(company)
                    
            if matching_companies:
                return CompanySearchResult(
                    query=identifier,
                    results=matching_companies,
                    source=CompanyDataSource.MOCK,
                    search_time=datetime.now(),
                    total_results=len(matching_companies),
                    success=True
                )
        
        # No match found - create generic mock company
        if self._is_org_number(identifier):
            org_number = self._normalize_org_number(identifier)
            mock_company = CompanyInfo(
                org_number=org_number,
                name=f"Mock Företag AB ({org_number})",
                company_type=CompanyType.AB,
                status=CompanyStatus.ACTIVE,
                registration_date=datetime(2010, 1, 1),
                address=CompanyAddress(
                    street="Testgatan 1",
                    postal_code="123 45",
                    city="Stockholm"
                ),
                industry_description="Testverksamhet",
                source=CompanyDataSource.MOCK
            )
        else:
            # Name-based mock
            mock_company = CompanyInfo(
                org_number="123456-7890",
                name=identifier,
                company_type=CompanyType.AB,
                status=CompanyStatus.ACTIVE,
                source=CompanyDataSource.MOCK
            )
            
        return CompanySearchResult(
            query=identifier,
            results=[mock_company],
            source=CompanyDataSource.MOCK,
            search_time=datetime.now(),
            total_results=1,
            success=True
        )
        
    async def _lookup_bolagsverket(self, identifier: str) -> CompanySearchResult:
        """Look up company från Bolagsverket API (mock implementation)"""
        
        await asyncio.sleep(1.5)  # Simulate API delay
        
        # In real implementation, this would call Bolagsverket's open data API
        # For now, simulate API response
        
        return await self._mock_company_lookup(identifier)
        
    async def _lookup_allabolag(self, identifier: str) -> CompanySearchResult:
        """Look up company från Allabolag.se (mock implementation)"""
        
        await asyncio.sleep(0.8)  # Simulate API delay
        
        return await self._mock_company_lookup(identifier)
        
    async def _lookup_ratsit(self, identifier: str) -> CompanySearchResult:
        """Look up company från Ratsit.se (mock implementation)"""
        
        await asyncio.sleep(0.7)  # Simulate API delay
        
        return await self._mock_company_lookup(identifier)
        
    async def _lookup_hitta(self, identifier: str) -> CompanySearchResult:
        """Look up company från Hitta.se (mock implementation)"""
        
        await asyncio.sleep(0.5)  # Simulate API delay
        
        return await self._mock_company_lookup(identifier)
        
    async def _lookup_uc(self, identifier: str) -> CompanySearchResult:
        """Look up company från UC.se (mock implementation)"""
        
        await asyncio.sleep(1.0)  # Simulate API delay
        
        return await self._mock_company_lookup(identifier)
        
    def _is_org_number(self, identifier: str) -> bool:
        """Check if identifier is a Swedish organization number"""
        # Swedish org number: XXXXXX-XXXX (10 digits with dash)
        normalized = re.sub(r'\s+', '', identifier)
        pattern = r'^\d{6}-?\d{4}$'
        return bool(re.match(pattern, normalized))
        
    def _normalize_org_number(self, org_number: str) -> str:
        """Normalize Swedish organization number"""
        # Remove spaces and ensure dash format
        normalized = re.sub(r'\s+', '', org_number)
        if len(normalized) == 10 and '-' not in normalized:
            # Add dash: 1234567890 -> 123456-7890
            return f"{normalized[:6]}-{normalized[6:]}"
        return normalized
        
    def _validate_org_number(self, org_number: str) -> bool:
        """Validate Swedish organization number using Luhn algorithm"""
        try:
            # Remove dash and convert to digits
            digits = re.sub(r'[^0-9]', '', org_number)
            if len(digits) != 10:
                return False
                
            # Apply Luhn algorithm
            sum_digits = 0
            for i, digit in enumerate(digits[:-1]):  # Exclude check digit
                n = int(digit)
                if i % 2 == 0:  # Even positions (0-indexed)
                    n *= 2
                    if n > 9:
                        n = n // 10 + n % 10
                sum_digits += n
                
            check_digit = (10 - (sum_digits % 10)) % 10
            return check_digit == int(digits[-1])
            
        except (ValueError, IndexError):
            return False
            
    async def search_companies_by_name(self, name: str, 
                                     limit: int = 10) -> CompanySearchResult:
        """Search companies by name"""
        
        # Use the main lookup method with name
        return await self.lookup_company(name)
        
    async def search_companies_by_industry(self, industry_code: str,
                                         municipality: str = None,
                                         limit: int = 50) -> CompanySearchResult:
        """Search companies by industry code (SNI)"""
        
        # Mock search by industry
        await asyncio.sleep(0.5)
        
        mock_results = []
        
        # Create some mock companies för different industries
        if industry_code.startswith("62"):  # IT/Programming
            mock_results.extend([
                CompanyInfo(
                    org_number="123456-1001", 
                    name="Tech Solutions AB",
                    company_type=CompanyType.AB,
                    status=CompanyStatus.ACTIVE,
                    industry_code=industry_code,
                    industry_description="Dataprogrammering",
                    address=CompanyAddress(city=municipality or "Stockholm"),
                    source=CompanyDataSource.MOCK
                ),
                CompanyInfo(
                    org_number="123456-1002",
                    name="Software Development HB", 
                    company_type=CompanyType.HB,
                    status=CompanyStatus.ACTIVE,
                    industry_code=industry_code,
                    industry_description="Dataprogrammering",
                    address=CompanyAddress(city=municipality or "Göteborg"),
                    source=CompanyDataSource.MOCK
                )
            ])
            
        return CompanySearchResult(
            query=f"industry:{industry_code}",
            results=mock_results[:limit],
            source=CompanyDataSource.MOCK,
            search_time=datetime.now(),
            total_results=len(mock_results),
            success=True
        )
        
    async def batch_lookup(self, identifiers: List[str],
                          max_concurrent: int = 3) -> Dict[str, CompanySearchResult]:
        """Look up multiple companies concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def lookup_with_semaphore(identifier):
            async with semaphore:
                return identifier, await self.lookup_company(identifier)
                
        # Create tasks
        tasks = [lookup_with_semaphore(identifier) for identifier in identifiers]
        
        # Execute with concurrency limit
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        batch_results = {}
        for result in results:
            if isinstance(result, tuple):
                identifier, search_result = result
                batch_results[identifier] = search_result
            else:
                logger.error(f"❌ Batch lookup error: {str(result)}")
                
        return batch_results
        
    def get_company_statistics(self) -> Dict[str, Any]:
        """Get company lookup statistics"""
        return {
            "total_lookups": self.stats["total_lookups"],
            "successful_lookups": self.stats["successful_lookups"],
            "failed_lookups": self.stats["failed_lookups"],
            "success_rate": (
                self.stats["successful_lookups"] / max(1, self.stats["total_lookups"])
            ) * 100,
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": (
                self.stats["cache_hits"] / max(1, self.stats["total_lookups"])
            ) * 100,
            "by_source": self.stats["by_source"],
            "by_company_type": self.stats["by_company_type"],
            "by_status": self.stats["by_status"],
            "cache_size": len(self.cache)
        }
        
    def get_cached_companies(self) -> List[CompanyInfo]:
        """Get all cached companies"""
        cached_companies = []
        for cache_entry in self.cache.values():
            search_result = cache_entry["data"]
            cached_companies.extend(search_result.results)
        return cached_companies
        
    def clear_cache(self, older_than_hours: int = 0):
        """Clear company cache"""
        if older_than_hours == 0:
            cleared = len(self.cache)
            self.cache.clear()
        else:
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            old_keys = [
                key for key, value in self.cache.items()
                if value["timestamp"] < cutoff_time
            ]
            for key in old_keys:
                del self.cache[key]
            cleared = len(old_keys)
            
        logger.info(f"🧹 Cleared {cleared} company cache entries")
        
    async def export_company_data(self, format: str = "json") -> str:
        """Export cached company data"""
        
        cached_companies = self.get_cached_companies()
        
        if format.lower() == "json":
            company_data = []
            for company in cached_companies:
                data = {
                    "org_number": company.org_number,
                    "name": company.name,
                    "company_type": company.company_type.value if company.company_type else None,
                    "status": company.status.value if company.status else None,
                    "registration_date": company.registration_date.isoformat() if company.registration_date else None,
                    "address": {
                        "street": company.address.street if company.address else None,
                        "postal_code": company.address.postal_code if company.address else None,
                        "city": company.address.city if company.address else None,
                        "municipality": company.address.municipality if company.address else None,
                        "county": company.address.county if company.address else None,
                        "full_address": company.address.full_address if company.address else None
                    } if company.address else None,
                    "phone": company.phone,
                    "email": company.email,
                    "website": company.website,
                    "industry_code": company.industry_code,
                    "industry_description": company.industry_description,
                    "ceo_name": company.ceo_name,
                    "board_members": company.board_members,
                    "financials": {
                        "revenue": company.financials.revenue if company.financials else None,
                        "profit": company.financials.profit if company.financials else None,
                        "employees": company.financials.employees if company.financials else None,
                        "equity": company.financials.equity if company.financials else None,
                        "assets": company.financials.assets if company.financials else None,
                        "year": company.financials.year if company.financials else None
                    } if company.financials else None,
                    "vat_registered": company.vat_registered,
                    "f_tax_registered": company.f_tax_registered,
                    "source": company.source.value if company.source else None,
                    "last_updated": company.last_updated.isoformat(),
                    "age_years": company.age_years,
                    "is_active": company.is_active
                }
                company_data.append(data)
                
            return json.dumps(company_data, indent=2, ensure_ascii=False)
            
        else:
            return json.dumps({"error": f"Unsupported format: {format}"})
            
    async def cleanup(self):
        """Cleanup Swedish Company Data adapter"""
        logger.info("🧹 Cleaning up Swedish Company Data Adapter")
        
        if self.session:
            await self.session.close()
            
        self.cache.clear()
        self.stats.clear()
        self.initialized = False
        logger.info("✅ Swedish Company Data Adapter cleanup completed")
