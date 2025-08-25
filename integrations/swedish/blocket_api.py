#!/usr/bin/env python3
"""
Enhanced Blocket API Integration för Sparkling-Owl-Spin
Extraherat från: dunderrrrrr/blocket_api
Integrerat från: vendors/blocket_api
"""

import logging
import asyncio
import aiohttp
import json
import time
import random
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re
import urllib.parse

logger = logging.getLogger(__name__)

class BlocketCategory(Enum):
    """Blocket categories"""
    BILAR = "bilar"
    MC_MOPED = "mc_moped"  
    HUSDJUR = "husdjur"
    BOSTAD = "bostad"
    JOBB = "jobb"
    FOR_HEMMET = "for_hemmet"
    PERSONLIGT = "personligt"
    ELEKTRONIK = "elektronik"
    HOBBY_FRITID = "hobby_fritid"
    VERKTYG_TRADGARD = "verktyg_tradgard"
    BARNPRYLAR = "barnprylar"
    SPORT_FRITID = "sport_fritid"
    KLADER_ACCESSOARER = "klader_accessoarer"

class BlocketRegion(Enum):
    """Swedish regions"""
    STOCKHOLM = "stockholm"
    GOTEBORG = "goteborg"
    MALMO = "malmo"
    UPPSALA = "uppsala"
    VASTERAS = "vasteras"
    OREBRO = "orebro"
    LINKOPING = "linkoping"
    HELSINGBORG = "helsingborg"
    JONKOPING = "jonkoping"
    NORRKOPING = "norrkoping"
    LUND = "lund"
    UMEA = "umea"
    GAVLE = "gavle"
    BORAS = "boras"
    SODERTALJE = "sodertalje"
    ESKILSTUNA = "eskilstuna"

@dataclass
class BlocketSearchParams:
    """Blocket search parameters"""
    query: Optional[str] = None
    category: Optional[BlocketCategory] = None
    region: Optional[BlocketRegion] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    sort_order: str = "time_desc"  # time_desc, time_asc, price_desc, price_asc
    page: int = 1
    per_page: int = 50
    include_images: bool = True
    include_description: bool = True
    filters: Optional[Dict[str, Any]] = None

@dataclass
class BlocketListing:
    """Blocket listing data"""
    id: str
    title: str
    price: Optional[int]
    description: str
    location: str
    region: str
    category: str
    subcategory: Optional[str]
    posted_date: datetime
    images: List[str]
    seller_info: Dict[str, Any]
    url: str
    phone: Optional[str] = None
    email: Optional[str] = None
    features: Dict[str, Any] = None
    condition: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[int] = None  # För bilar
    size: Optional[str] = None
    views: Optional[int] = None
    favorites: Optional[int] = None

class EnhancedBlocketAPI:
    """Enhanced Blocket API med full funktionalitet"""
    
    def __init__(self, plugin_info=None):
        self.plugin_info = plugin_info
        self.initialized = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Blocket endpoints
        self.base_url = "https://www.blocket.se"
        self.api_base = "https://api.blocket.se"
        self.search_endpoint = "/search_bff/v2/search"
        self.details_endpoint = "/item_bff/v2/item"
        
        # Request headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "sv-SE,sv;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }
        
        # Rate limiting
        self.request_delay = 2.0  # Seconds between requests
        self.last_request_time = 0.0
        
        # Category mappings
        self.category_mappings = {
            BlocketCategory.BILAR: {"id": "bilar", "name": "Bilar"},
            BlocketCategory.MC_MOPED: {"id": "mc_moped", "name": "MC & Moped"},
            BlocketCategory.HUSDJUR: {"id": "husdjur", "name": "Husdjur"},
            BlocketCategory.BOSTAD: {"id": "bostad", "name": "Bostad"},
            BlocketCategory.JOBB: {"id": "jobb", "name": "Jobb"},
            BlocketCategory.FOR_HEMMET: {"id": "for_hemmet", "name": "För hemmet"},
            BlocketCategory.PERSONLIGT: {"id": "personligt", "name": "Personligt"},
            BlocketCategory.ELEKTRONIK: {"id": "elektronik", "name": "Elektronik"},
            BlocketCategory.HOBBY_FRITID: {"id": "hobby_fritid", "name": "Hobby & Fritid"}
        }
        
        # Region mappings
        self.region_mappings = {
            BlocketRegion.STOCKHOLM: {"id": "1", "name": "Stockholm"},
            BlocketRegion.GOTEBORG: {"id": "14", "name": "Göteborg"},
            BlocketRegion.MALMO: {"id": "12", "name": "Malmö"},
            BlocketRegion.UPPSALA: {"id": "3", "name": "Uppsala"},
            BlocketRegion.VASTERAS: {"id": "19", "name": "Västerås"},
            BlocketRegion.OREBRO: {"id": "18", "name": "Örebro"},
            BlocketRegion.LINKOPING: {"id": "5", "name": "Linköping"}
        }
        
        # Statistics
        self.stats = {
            "total_searches": 0,
            "total_listings_found": 0,
            "total_details_fetched": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0,
            "by_category": {},
            "by_region": {},
            "cached_results": 0
        }
        
        # Result cache
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(minutes=30)
        
    async def initialize(self):
        """Initialize Blocket API"""
        try:
            logger.info("🛒 Initializing Enhanced Blocket API")
            
            # Create aiohttp session
            connector = aiohttp.TCPConnector(
                limit=20,
                limit_per_host=5,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=self.headers
            )
            
            # Initialize statistics
            for category in BlocketCategory:
                self.stats["by_category"][category.value] = {
                    "searches": 0,
                    "listings_found": 0
                }
                
            for region in BlocketRegion:
                self.stats["by_region"][region.value] = {
                    "searches": 0,
                    "listings_found": 0
                }
                
            self.initialized = True
            logger.info("✅ Enhanced Blocket API initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Blocket API: {str(e)}")
            raise
            
    async def search_listings(self, params: BlocketSearchParams) -> List[BlocketListing]:
        """Search Blocket listings"""
        
        if not self.initialized:
            await self.initialize()
            
        # Rate limiting
        await self._enforce_rate_limit()
        
        # Build search URL
        search_url = self._build_search_url(params)
        
        # Check cache first
        cache_key = f"search_{hash(str(params))}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if datetime.now() - cache_entry["timestamp"] < self.cache_ttl:
                logger.debug(f"🗄️ Using cached results for search")
                self.stats["cached_results"] += 1
                return cache_entry["data"]
                
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Searching Blocket: {params.query or 'all'} in {params.category.value if params.category else 'all categories'}")
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    listings = await self._parse_search_results(data)
                    
                    # Update statistics
                    self.stats["total_searches"] += 1
                    self.stats["total_listings_found"] += len(listings)
                    
                    response_time = time.time() - start_time
                    self.stats["avg_response_time"] = (
                        (self.stats["avg_response_time"] * (self.stats["total_searches"] - 1) + response_time)
                        / self.stats["total_searches"]
                    )
                    
                    if params.category:
                        self.stats["by_category"][params.category.value]["searches"] += 1
                        self.stats["by_category"][params.category.value]["listings_found"] += len(listings)
                        
                    if params.region:
                        self.stats["by_region"][params.region.value]["searches"] += 1
                        self.stats["by_region"][params.region.value]["listings_found"] += len(listings)
                        
                    # Cache results
                    self.cache[cache_key] = {
                        "data": listings,
                        "timestamp": datetime.now()
                    }
                    
                    logger.info(f"✅ Found {len(listings)} listings ({response_time:.2f}s)")
                    return listings
                    
                else:
                    self.stats["failed_requests"] += 1
                    logger.error(f"❌ Blocket search failed: HTTP {response.status}")
                    return []
                    
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Blocket search error: {str(e)}")
            return []
            
    def _build_search_url(self, params: BlocketSearchParams) -> str:
        """Build Blocket search URL"""
        
        url_params = {
            "page": params.page,
            "size": params.per_page,
            "sort": params.sort_order
        }
        
        if params.query:
            url_params["q"] = params.query
            
        if params.category:
            category_data = self.category_mappings.get(params.category)
            if category_data:
                url_params["ca"] = category_data["id"]
                
        if params.region:
            region_data = self.region_mappings.get(params.region)
            if region_data:
                url_params["st"] = region_data["id"]
                
        if params.min_price is not None:
            url_params["min_price"] = params.min_price
            
        if params.max_price is not None:
            url_params["max_price"] = params.max_price
            
        if params.min_year is not None:
            url_params["min_year"] = params.min_year
            
        if params.max_year is not None:
            url_params["max_year"] = params.max_year
            
        # Add custom filters
        if params.filters:
            url_params.update(params.filters)
            
        # Build URL
        query_string = urllib.parse.urlencode(url_params)
        return f"{self.api_base}{self.search_endpoint}?{query_string}"
        
    async def _parse_search_results(self, data: Dict[str, Any]) -> List[BlocketListing]:
        """Parse Blocket search results"""
        
        listings = []
        
        try:
            # Extract listings from API response
            items = data.get("data", {}).get("list", [])
            
            for item in items:
                listing = BlocketListing(
                    id=item.get("list_id", ""),
                    title=item.get("subject", ""),
                    price=item.get("price", {}).get("value") if item.get("price") else None,
                    description=item.get("body", ""),
                    location=item.get("location", {}).get("name", ""),
                    region=item.get("region", {}).get("name", ""),
                    category=item.get("category", {}).get("name", ""),
                    subcategory=item.get("subcategory", {}).get("name"),
                    posted_date=self._parse_date(item.get("list_time")),
                    images=self._extract_images(item.get("images", [])),
                    seller_info=self._extract_seller_info(item),
                    url=f"{self.base_url}/annons/{item.get('list_id', '')}"
                )
                
                # Extract additional fields for specific categories
                if "car" in item.get("category", {}).get("name", "").lower():
                    listing.year = item.get("year")
                    listing.mileage = item.get("mileage")
                    listing.brand = item.get("brand")
                    listing.model = item.get("model")
                    
                # Extract features
                listing.features = item.get("parameters", {})
                
                # Extract condition
                listing.condition = item.get("condition")
                
                # Extract stats
                listing.views = item.get("views")
                listing.favorites = item.get("favorites")
                
                listings.append(listing)
                
        except Exception as e:
            logger.error(f"❌ Error parsing search results: {str(e)}")
            
        return listings
        
    async def get_listing_details(self, listing_id: str) -> Optional[BlocketListing]:
        """Get detailed information for a specific listing"""
        
        if not self.initialized:
            await self.initialize()
            
        # Rate limiting
        await self._enforce_rate_limit()
        
        # Check cache
        cache_key = f"details_{listing_id}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if datetime.now() - cache_entry["timestamp"] < self.cache_ttl:
                logger.debug(f"🗄️ Using cached details for listing {listing_id}")
                self.stats["cached_results"] += 1
                return cache_entry["data"]
                
        try:
            details_url = f"{self.api_base}{self.details_endpoint}/{listing_id}"
            
            async with self.session.get(details_url) as response:
                if response.status == 200:
                    data = await response.json()
                    listing = await self._parse_listing_details(data)
                    
                    if listing:
                        # Update statistics
                        self.stats["total_details_fetched"] += 1
                        
                        # Cache result
                        self.cache[cache_key] = {
                            "data": listing,
                            "timestamp": datetime.now()
                        }
                        
                        logger.debug(f"✅ Fetched details for listing {listing_id}")
                        return listing
                    else:
                        logger.warning(f"⚠️ Could not parse details for listing {listing_id}")
                        return None
                        
                else:
                    self.stats["failed_requests"] += 1
                    logger.error(f"❌ Failed to get listing details: HTTP {response.status}")
                    return None
                    
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Error getting listing details: {str(e)}")
            return None
            
    async def _parse_listing_details(self, data: Dict[str, Any]) -> Optional[BlocketListing]:
        """Parse detailed listing information"""
        
        try:
            item = data.get("data", {})
            
            listing = BlocketListing(
                id=item.get("list_id", ""),
                title=item.get("subject", ""),
                price=item.get("price", {}).get("value") if item.get("price") else None,
                description=item.get("body", ""),
                location=item.get("location", {}).get("name", ""),
                region=item.get("region", {}).get("name", ""),
                category=item.get("category", {}).get("name", ""),
                subcategory=item.get("subcategory", {}).get("name"),
                posted_date=self._parse_date(item.get("list_time")),
                images=self._extract_images(item.get("images", [])),
                seller_info=self._extract_seller_info(item),
                url=f"{self.base_url}/annons/{item.get('list_id', '')}"
            )
            
            # Extract contact information (if available)
            contact_info = item.get("contact_info", {})
            listing.phone = contact_info.get("phone")
            listing.email = contact_info.get("email")
            
            # Extract additional details
            listing.features = item.get("parameters", {})
            listing.condition = item.get("condition")
            listing.brand = item.get("brand")
            listing.model = item.get("model")
            listing.year = item.get("year")
            listing.mileage = item.get("mileage")
            listing.size = item.get("size")
            listing.views = item.get("views")
            listing.favorites = item.get("favorites")
            
            return listing
            
        except Exception as e:
            logger.error(f"❌ Error parsing listing details: {str(e)}")
            return None
            
    def _parse_date(self, date_str: str) -> datetime:
        """Parse Blocket date string"""
        
        try:
            # Blocket uses various date formats
            if isinstance(date_str, str):
                # Try ISO format first
                if "T" in date_str:
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    # Try other common formats
                    import dateutil.parser
                    return dateutil.parser.parse(date_str)
            else:
                return datetime.now()
                
        except Exception:
            return datetime.now()
            
    def _extract_images(self, images_data: List[Dict[str, Any]]) -> List[str]:
        """Extract image URLs"""
        
        image_urls = []
        
        for img in images_data:
            if isinstance(img, dict):
                url = img.get("url") or img.get("src")
                if url:
                    # Ensure full URL
                    if url.startswith("//"):
                        url = "https:" + url
                    elif url.startswith("/"):
                        url = self.base_url + url
                        
                    image_urls.append(url)
                    
        return image_urls
        
    def _extract_seller_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract seller information"""
        
        seller_info = {}
        
        seller_data = item.get("seller", {})
        if seller_data:
            seller_info.update({
                "name": seller_data.get("name"),
                "id": seller_data.get("id"),
                "type": seller_data.get("type"),  # private, company
                "verified": seller_data.get("verified", False),
                "rating": seller_data.get("rating"),
                "total_ads": seller_data.get("total_ads"),
                "member_since": seller_data.get("member_since")
            })
            
        return seller_info
        
    async def _enforce_rate_limit(self):
        """Enforce rate limiting"""
        
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.request_delay:
            sleep_time = self.request_delay - elapsed
            logger.debug(f"⏱️ Rate limiting: sleeping {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    async def search_cars(self, 
                        brand: Optional[str] = None,
                        model: Optional[str] = None,
                        min_year: Optional[int] = None,
                        max_year: Optional[int] = None,
                        min_price: Optional[int] = None,
                        max_price: Optional[int] = None,
                        max_mileage: Optional[int] = None,
                        region: Optional[BlocketRegion] = None) -> List[BlocketListing]:
        """Specialized car search"""
        
        params = BlocketSearchParams(
            category=BlocketCategory.BILAR,
            min_year=min_year,
            max_year=max_year,
            min_price=min_price,
            max_price=max_price,
            region=region,
            filters={}
        )
        
        # Build car-specific query
        query_parts = []
        if brand:
            query_parts.append(brand)
        if model:
            query_parts.append(model)
            
        if query_parts:
            params.query = " ".join(query_parts)
            
        if max_mileage:
            params.filters["max_mileage"] = max_mileage
            
        return await self.search_listings(params)
        
    async def search_jobs(self,
                        title: Optional[str] = None,
                        company: Optional[str] = None,
                        region: Optional[BlocketRegion] = None,
                        employment_type: Optional[str] = None) -> List[BlocketListing]:
        """Specialized job search"""
        
        query_parts = []
        if title:
            query_parts.append(title)
        if company:
            query_parts.append(company)
            
        params = BlocketSearchParams(
            category=BlocketCategory.JOBB,
            query=" ".join(query_parts) if query_parts else None,
            region=region,
            filters={}
        )
        
        if employment_type:
            params.filters["employment_type"] = employment_type
            
        return await self.search_listings(params)
        
    async def search_housing(self,
                           housing_type: Optional[str] = None,
                           min_rooms: Optional[int] = None,
                           max_rooms: Optional[int] = None,
                           min_rent: Optional[int] = None,
                           max_rent: Optional[int] = None,
                           region: Optional[BlocketRegion] = None) -> List[BlocketListing]:
        """Specialized housing search"""
        
        params = BlocketSearchParams(
            category=BlocketCategory.BOSTAD,
            query=housing_type,
            min_price=min_rent,
            max_price=max_rent,
            region=region,
            filters={}
        )
        
        if min_rooms:
            params.filters["min_rooms"] = min_rooms
        if max_rooms:
            params.filters["max_rooms"] = max_rooms
            
        return await self.search_listings(params)
        
    def get_blocket_statistics(self) -> Dict[str, Any]:
        """Get comprehensive Blocket API statistics"""
        
        return {
            "total_searches": self.stats["total_searches"],
            "total_listings_found": self.stats["total_listings_found"],
            "total_details_fetched": self.stats["total_details_fetched"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (
                (self.stats["total_searches"] - self.stats["failed_requests"]) / 
                max(1, self.stats["total_searches"])
            ) * 100,
            "avg_response_time": self.stats["avg_response_time"],
            "by_category": self.stats["by_category"],
            "by_region": self.stats["by_region"],
            "cached_results": self.stats["cached_results"],
            "cache_size": len(self.cache),
            "available_categories": [c.value for c in BlocketCategory],
            "available_regions": [r.value for r in BlocketRegion]
        }
        
    async def cleanup(self):
        """Cleanup Blocket API"""
        logger.info("🧹 Cleaning up Enhanced Blocket API")
        
        if self.session:
            await self.session.close()
            
        self.cache.clear()
        self.stats.clear()
        
        self.initialized = False
        logger.info("✅ Enhanced Blocket API cleanup completed")

# Alias för pyramid architecture compatibility
BlocketAPI = EnhancedBlocketAPI
