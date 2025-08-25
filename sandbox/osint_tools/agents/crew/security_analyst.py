#!/usr/bin/env python3
"""
Security Analyst Agent
AI-agent specialiserad på säkerhetsanalys med integration av rengine, adversarial-robustness-toolbox
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import re

# Import local pentesting engines
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'engines', 'pentesting'))

try:
    from vulnerability_scanner import VulnerabilityScanner, VulnerabilityType, ScanLevel
    from exploit_manager import ExploitManager, ExploitType, ExploitTarget, TargetType
    from osint_engine import OSINTEngine, OSINTType, OSINTTarget
except ImportError:
    # Fallback if engines not available
    VulnerabilityScanner = None
    ExploitManager = None
    OSINTEngine = None

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AnalysisType(Enum):
    """Types of security analysis"""
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    PENETRATION_TESTING = "penetration_testing"
    THREAT_MODELING = "threat_modeling"
    RISK_ASSESSMENT = "risk_assessment"
    COMPLIANCE_CHECK = "compliance_check"
    INCIDENT_ANALYSIS = "incident_analysis"
    THREAT_INTELLIGENCE = "threat_intelligence"

class ComplianceFramework(Enum):
    """Security compliance frameworks"""
    OWASP_TOP_10 = "owasp_top_10"
    NIST = "nist"
    ISO_27001 = "iso_27001"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    SOC2 = "soc2"

@dataclass
class SecurityTarget:
    """Target for security analysis"""
    target_id: str
    target_type: str  # web_app, network, host, api, etc.
    primary_url: str
    additional_endpoints: List[str] = field(default_factory=list)
    credentials: Dict[str, str] = field(default_factory=dict)
    scope_restrictions: List[str] = field(default_factory=list)
    business_context: str = ""

@dataclass 
class SecurityFinding:
    """Security finding/vulnerability"""
    finding_id: str
    title: str
    description: str
    threat_level: ThreatLevel
    category: str
    cwe_id: str = ""
    cvss_score: float = 0.0
    affected_assets: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    remediation: str = ""
    references: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class SecurityAnalysisResult:
    """Result from security analysis"""
    analysis_id: str
    target: SecurityTarget
    analysis_type: AnalysisType
    findings: List[SecurityFinding] = field(default_factory=list)
    risk_score: float = 0.0
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    success: bool = False

class SecurityAnalystAgent:
    """AI-powered security analyst with advanced analysis capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agent_id = self._generate_agent_id()
        self.knowledge_base = {}
        self.analysis_history = []
        self.active_analyses = {}
        
        # Initialize security engines
        self.vulnerability_scanner = VulnerabilityScanner() if VulnerabilityScanner else None
        self.exploit_manager = ExploitManager() if ExploitManager else None
        self.osint_engine = OSINTEngine() if OSINTEngine else None
        
        # Threat intelligence database (simplified)
        self.threat_db = self._initialize_threat_database()
        
        # Compliance frameworks
        self.compliance_frameworks = self._load_compliance_frameworks()
        
        logger.info(f"Security Analyst Agent {self.agent_id} initialized")
    
    def _initialize_threat_database(self) -> Dict[str, Any]:
        """Initialize threat intelligence database"""
        return {
            'known_vulnerabilities': {},
            'attack_patterns': {},
            'threat_actors': {},
            'indicators_of_compromise': {},
            'mitigation_strategies': {}
        }
    
    def _load_compliance_frameworks(self) -> Dict[ComplianceFramework, Dict[str, Any]]:
        """Load compliance framework definitions"""
        return {
            ComplianceFramework.OWASP_TOP_10: {
                'name': 'OWASP Top 10',
                'categories': [
                    'A01:2021 - Broken Access Control',
                    'A02:2021 - Cryptographic Failures', 
                    'A03:2021 - Injection',
                    'A04:2021 - Insecure Design',
                    'A05:2021 - Security Misconfiguration',
                    'A06:2021 - Vulnerable and Outdated Components',
                    'A07:2021 - Identification and Authentication Failures',
                    'A08:2021 - Software and Data Integrity Failures',
                    'A09:2021 - Security Logging and Monitoring Failures',
                    'A10:2021 - Server-Side Request Forgery'
                ]
            },
            ComplianceFramework.NIST: {
                'name': 'NIST Cybersecurity Framework',
                'functions': ['Identify', 'Protect', 'Detect', 'Respond', 'Recover']
            }
        }
    
    async def conduct_security_analysis(self, 
                                      target: SecurityTarget, 
                                      analysis_type: AnalysisType = AnalysisType.VULNERABILITY_ASSESSMENT) -> SecurityAnalysisResult:
        """Conduct comprehensive security analysis"""
        
        analysis_id = self._generate_analysis_id(target)
        
        result = SecurityAnalysisResult(
            analysis_id=analysis_id,
            target=target,
            analysis_type=analysis_type,
            start_time=datetime.now()
        )
        
        self.active_analyses[analysis_id] = result
        
        try:
            if analysis_type == AnalysisType.VULNERABILITY_ASSESSMENT:
                result = await self._conduct_vulnerability_assessment(result)
            elif analysis_type == AnalysisType.PENETRATION_TESTING:
                result = await self._conduct_penetration_testing(result)
            elif analysis_type == AnalysisType.THREAT_MODELING:
                result = await self._conduct_threat_modeling(result)
            elif analysis_type == AnalysisType.RISK_ASSESSMENT:
                result = await self._conduct_risk_assessment(result)
            elif analysis_type == AnalysisType.COMPLIANCE_CHECK:
                result = await self._conduct_compliance_check(result)
            elif analysis_type == AnalysisType.THREAT_INTELLIGENCE:
                result = await self._gather_threat_intelligence(result)
            else:
                result.recommendations.append(f"Analysis type {analysis_type} not yet implemented")
            
            # Calculate overall risk score
            result.risk_score = self._calculate_risk_score(result.findings)
            
            # Generate recommendations
            result.recommendations.extend(self._generate_security_recommendations(result))
            
            # AI-powered analysis enhancement
            result = await self._enhance_analysis_with_ai(result)
            
            result.success = True
            
        except Exception as e:
            logger.error(f"Security analysis failed: {e}")
            result.recommendations.append(f"Analysis failed: {str(e)}")
        
        finally:
            result.end_time = datetime.now()
            self.analysis_history.append(result)
            if analysis_id in self.active_analyses:
                del self.active_analyses[analysis_id]
        
        return result
    
    async def _conduct_vulnerability_assessment(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Conduct comprehensive vulnerability assessment"""
        
        if not self.vulnerability_scanner:
            result.recommendations.append("Vulnerability scanner not available")
            return result
        
        try:
            # Scan primary target
            scan_result = await self.vulnerability_scanner.scan_target(
                result.target.primary_url,
                ScanLevel.ACTIVE
            )
            
            # Convert scan results to security findings
            for vuln in scan_result.vulnerabilities:
                finding = SecurityFinding(
                    finding_id=self._generate_finding_id(),
                    title=vuln.title,
                    description=vuln.description,
                    threat_level=self._map_severity_to_threat_level(vuln.severity.value),
                    category=vuln.vuln_type.value,
                    cwe_id=vuln.cwe_id,
                    cvss_score=vuln.cvss_score,
                    affected_assets=[result.target.primary_url],
                    evidence=[vuln.evidence] if vuln.evidence else [],
                    remediation=vuln.remediation,
                    detected_at=vuln.timestamp
                )
                result.findings.append(finding)
            
            # Scan additional endpoints
            for endpoint in result.target.additional_endpoints:
                try:
                    endpoint_scan = await self.vulnerability_scanner.scan_target(endpoint, ScanLevel.PASSIVE)
                    
                    for vuln in endpoint_scan.vulnerabilities:
                        finding = SecurityFinding(
                            finding_id=self._generate_finding_id(),
                            title=f"[{endpoint}] {vuln.title}",
                            description=vuln.description,
                            threat_level=self._map_severity_to_threat_level(vuln.severity.value),
                            category=vuln.vuln_type.value,
                            affected_assets=[endpoint],
                            evidence=[vuln.evidence] if vuln.evidence else [],
                            remediation=vuln.remediation
                        )
                        result.findings.append(finding)
                        
                except Exception as e:
                    logger.warning(f"Failed to scan endpoint {endpoint}: {e}")
            
            result.metadata['vulnerability_scan'] = {
                'primary_scan_duration': scan_result.scan_duration,
                'requests_made': scan_result.requests_made,
                'pages_scanned': scan_result.pages_scanned
            }
            
        except Exception as e:
            logger.error(f"Vulnerability assessment failed: {e}")
            result.recommendations.append(f"Vulnerability assessment error: {str(e)}")
        
        return result
    
    async def _conduct_penetration_testing(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Conduct ethical penetration testing"""
        
        if not self.exploit_manager:
            result.recommendations.append("Exploit manager not available")
            return result
        
        try:
            # Create exploit target
            from urllib.parse import urlparse
            parsed = urlparse(result.target.primary_url)
            
            exploit_target = ExploitTarget(
                target_id=result.target.target_id,
                target_type=TargetType.WEB_APPLICATION,
                host=parsed.hostname,
                port=parsed.port or (443 if parsed.scheme == 'https' else 80)
            )
            
            # Get available exploit modules
            available_modules = self.exploit_manager.get_available_modules(ExploitType.WEB_APPLICATION)
            
            # Execute safe exploits only
            safe_modules = [
                'sql_injection_basic',
                'xss_reflected',
                'path_traversal'
            ]
            
            for module_id in safe_modules:
                if any(m.module_id == module_id for m in available_modules):
                    try:
                        exploit_result = await self.exploit_manager.execute_exploit(
                            module_id, 
                            exploit_target
                        )
                        
                        if exploit_result.status.value == 'success':
                            finding = SecurityFinding(
                                finding_id=self._generate_finding_id(),
                                title=f"Exploitable Vulnerability: {module_id.replace('_', ' ').title()}",
                                description=f"Successfully exploited {module_id}",
                                threat_level=ThreatLevel.HIGH,
                                category="exploitable_vulnerability",
                                affected_assets=[result.target.primary_url],
                                evidence=[exploit_result.output],
                                remediation=exploit_result.remediation_notes
                            )
                            result.findings.append(finding)
                            
                    except Exception as e:
                        logger.warning(f"Exploit {module_id} failed: {e}")
            
            result.metadata['penetration_testing'] = {
                'modules_tested': safe_modules,
                'successful_exploits': len([f for f in result.findings if 'exploitable' in f.category.lower()])
            }
            
        except Exception as e:
            logger.error(f"Penetration testing failed: {e}")
            result.recommendations.append(f"Penetration testing error: {str(e)}")
        
        return result
    
    async def _conduct_threat_modeling(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Conduct threat modeling analysis"""
        
        # STRIDE threat modeling
        stride_threats = {
            'Spoofing': 'Authentication-based threats',
            'Tampering': 'Data integrity threats', 
            'Repudiation': 'Non-repudiation threats',
            'Information Disclosure': 'Confidentiality threats',
            'Denial of Service': 'Availability threats',
            'Elevation of Privilege': 'Authorization threats'
        }
        
        # Analyze application architecture (simplified)
        architecture_components = self._analyze_application_architecture(result.target)
        
        for component in architecture_components:
            for threat_type, description in stride_threats.items():
                # Generate potential threats for each component
                finding = SecurityFinding(
                    finding_id=self._generate_finding_id(),
                    title=f"Potential {threat_type} Threat",
                    description=f"{description} affecting {component}",
                    threat_level=ThreatLevel.MEDIUM,
                    category="threat_model",
                    affected_assets=[component],
                    remediation=f"Implement controls to mitigate {threat_type.lower()} threats"
                )
                result.findings.append(finding)
        
        result.metadata['threat_modeling'] = {
            'methodology': 'STRIDE',
            'components_analyzed': len(architecture_components),
            'threat_categories': list(stride_threats.keys())
        }
        
        return result
    
    def _analyze_application_architecture(self, target: SecurityTarget) -> List[str]:
        """Analyze application architecture components"""
        
        # Simplified architecture analysis
        components = [
            f"Web Application ({target.primary_url})",
            "Database Layer",
            "Authentication System",
            "Session Management",
            "Input Validation Layer"
        ]
        
        # Add endpoint-specific components
        for endpoint in target.additional_endpoints:
            if '/api/' in endpoint:
                components.append(f"API Endpoint ({endpoint})")
            elif '/admin' in endpoint:
                components.append(f"Administrative Interface ({endpoint})")
        
        return components
    
    async def _conduct_risk_assessment(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Conduct quantitative risk assessment"""
        
        # Business impact analysis
        business_impacts = {
            'data_breach': {'probability': 0.3, 'impact': 8, 'description': 'Confidential data exposure'},
            'service_disruption': {'probability': 0.2, 'impact': 6, 'description': 'Service availability loss'},
            'reputation_damage': {'probability': 0.4, 'impact': 7, 'description': 'Brand reputation impact'},
            'compliance_violation': {'probability': 0.25, 'impact': 9, 'description': 'Regulatory non-compliance'}
        }
        
        total_risk = 0
        
        for risk_type, details in business_impacts.items():
            risk_score = details['probability'] * details['impact']
            total_risk += risk_score
            
            # Create risk finding
            threat_level = ThreatLevel.HIGH if risk_score > 5 else ThreatLevel.MEDIUM
            
            finding = SecurityFinding(
                finding_id=self._generate_finding_id(),
                title=f"Business Risk: {risk_type.replace('_', ' ').title()}",
                description=details['description'],
                threat_level=threat_level,
                category="business_risk",
                affected_assets=[result.target.business_context or "Business Operations"],
                remediation=f"Implement controls to reduce {risk_type} probability and impact"
            )
            result.findings.append(finding)
        
        result.metadata['risk_assessment'] = {
            'methodology': 'Quantitative Risk Analysis',
            'total_risk_score': total_risk,
            'risk_categories': list(business_impacts.keys())
        }
        
        return result
    
    async def _conduct_compliance_check(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Check compliance against security frameworks"""
        
        # Check OWASP Top 10 compliance
        owasp_categories = self.compliance_frameworks[ComplianceFramework.OWASP_TOP_10]['categories']
        
        # Map findings to OWASP categories
        owasp_coverage = {}
        for category in owasp_categories:
            owasp_coverage[category] = False
        
        for finding in result.findings:
            # Simple mapping based on finding category
            if 'injection' in finding.category.lower():
                owasp_coverage['A03:2021 - Injection'] = True
            elif 'xss' in finding.category.lower():
                owasp_coverage['A03:2021 - Injection'] = True  # XSS is also injection
            elif 'access_control' in finding.category.lower():
                owasp_coverage['A01:2021 - Broken Access Control'] = True
            elif 'misconfiguration' in finding.category.lower():
                owasp_coverage['A05:2021 - Security Misconfiguration'] = True
        
        # Generate compliance findings
        for category, compliant in owasp_coverage.items():
            if not compliant:
                finding = SecurityFinding(
                    finding_id=self._generate_finding_id(),
                    title=f"OWASP Compliance Gap: {category}",
                    description=f"No evidence of protection against {category}",
                    threat_level=ThreatLevel.MEDIUM,
                    category="compliance_gap",
                    remediation=f"Implement controls for {category}"
                )
                result.findings.append(finding)
        
        result.compliance_status[ComplianceFramework.OWASP_TOP_10.value] = all(owasp_coverage.values())
        
        result.metadata['compliance_check'] = {
            'frameworks_checked': ['OWASP Top 10'],
            'owasp_coverage': owasp_coverage
        }
        
        return result
    
    async def _gather_threat_intelligence(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Gather threat intelligence for target"""
        
        if not self.osint_engine:
            result.recommendations.append("OSINT engine not available for threat intelligence")
            return result
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(result.target.primary_url).netloc
            
            # Create OSINT target
            osint_target = OSINTTarget(
                target_id=result.target.target_id,
                target_type='domain',
                value=domain,
                scope_restrictions=['no_personal_info']
            )
            
            # Gather intelligence
            osint_operation = await self.osint_engine.start_operation(osint_target)
            
            # Convert OSINT results to security findings
            for osint_result in osint_operation.results:
                if osint_result.sensitivity.value in ['sensitive', 'confidential']:
                    finding = SecurityFinding(
                        finding_id=self._generate_finding_id(),
                        title=f"Information Disclosure: {osint_result.osint_type.value.replace('_', ' ').title()}",
                        description=f"Publicly exposed information: {osint_result.osint_type.value}",
                        threat_level=ThreatLevel.LOW,
                        category="information_disclosure",
                        affected_assets=[domain],
                        evidence=[str(osint_result.data)],
                        remediation="Review and restrict public information exposure"
                    )
                    result.findings.append(finding)
            
            result.metadata['threat_intelligence'] = {
                'osint_operation_id': osint_operation.operation_id,
                'intelligence_sources': len(osint_operation.results),
                'domain_analyzed': domain
            }
            
        except Exception as e:
            logger.error(f"Threat intelligence gathering failed: {e}")
            result.recommendations.append(f"Threat intelligence error: {str(e)}")
        
        return result
    
    async def _enhance_analysis_with_ai(self, result: SecurityAnalysisResult) -> SecurityAnalysisResult:
        """Enhance analysis using AI reasoning"""
        
        # AI-powered correlation of findings
        correlated_findings = self._correlate_findings(result.findings)
        
        for correlation in correlated_findings:
            finding = SecurityFinding(
                finding_id=self._generate_finding_id(),
                title=f"Correlated Risk: {correlation['title']}",
                description=correlation['description'],
                threat_level=correlation['threat_level'],
                category="ai_analysis",
                affected_assets=correlation['affected_assets'],
                remediation=correlation['remediation']
            )
            result.findings.append(finding)
        
        # AI-powered prioritization
        result.findings = self._prioritize_findings_with_ai(result.findings)
        
        # Generate AI insights
        ai_insights = self._generate_ai_insights(result)
        result.recommendations.extend(ai_insights)
        
        result.metadata['ai_enhancement'] = {
            'correlations_found': len(correlated_findings),
            'findings_prioritized': True,
            'insights_generated': len(ai_insights)
        }
        
        return result
    
    def _correlate_findings(self, findings: List[SecurityFinding]) -> List[Dict[str, Any]]:
        """Use AI to correlate related findings"""
        
        correlations = []
        
        # Look for SQL injection + weak authentication = high risk
        sql_injection = [f for f in findings if 'injection' in f.category.lower()]
        auth_issues = [f for f in findings if 'authentication' in f.category.lower()]
        
        if sql_injection and auth_issues:
            correlations.append({
                'title': 'SQL Injection with Weak Authentication',
                'description': 'Combination of SQL injection and authentication weaknesses increases attack success probability',
                'threat_level': ThreatLevel.CRITICAL,
                'affected_assets': list(set([asset for f in sql_injection + auth_issues for asset in f.affected_assets])),
                'remediation': 'Immediately fix SQL injection vulnerabilities and strengthen authentication mechanisms'
            })
        
        # Look for information disclosure + enumeration = reconnaissance risk
        info_disclosure = [f for f in findings if 'disclosure' in f.category.lower()]
        if len(info_disclosure) > 2:
            correlations.append({
                'title': 'Multiple Information Disclosure Points',
                'description': 'Multiple information disclosure vulnerabilities enable comprehensive reconnaissance',
                'threat_level': ThreatLevel.MEDIUM,
                'affected_assets': list(set([asset for f in info_disclosure for asset in f.affected_assets])),
                'remediation': 'Reduce information exposure across all identified disclosure points'
            })
        
        return correlations
    
    def _prioritize_findings_with_ai(self, findings: List[SecurityFinding]) -> List[SecurityFinding]:
        """Use AI to prioritize findings by actual risk"""
        
        # Simple AI prioritization based on multiple factors
        def calculate_priority_score(finding):
            score = 0
            
            # Base score from threat level
            threat_scores = {
                ThreatLevel.CRITICAL: 10,
                ThreatLevel.HIGH: 7,
                ThreatLevel.MEDIUM: 4,
                ThreatLevel.LOW: 2,
                ThreatLevel.INFO: 1
            }
            score += threat_scores.get(finding.threat_level, 0)
            
            # Bonus for exploitable vulnerabilities
            if 'exploitable' in finding.category.lower():
                score += 5
            
            # Bonus for public-facing assets
            if any('http' in asset for asset in finding.affected_assets):
                score += 3
            
            # Bonus for multiple affected assets
            score += len(finding.affected_assets)
            
            return score
        
        # Sort by priority score (descending)
        return sorted(findings, key=calculate_priority_score, reverse=True)
    
    def _generate_ai_insights(self, result: SecurityAnalysisResult) -> List[str]:
        """Generate AI-powered insights"""
        
        insights = []
        
        # Analyze finding patterns
        categories = [f.category for f in result.findings]
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Most common vulnerability type
        if category_counts:
            most_common = max(category_counts.items(), key=lambda x: x[1])
            insights.append(
                f"Most prevalent vulnerability type: {most_common[0]} ({most_common[1]} instances). "
                f"Consider focused remediation efforts."
            )
        
        # Risk distribution analysis
        threat_levels = [f.threat_level for f in result.findings]
        critical_high = len([t for t in threat_levels if t in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]])
        
        if critical_high > len(result.findings) * 0.3:  # More than 30% are critical/high
            insights.append(
                "High concentration of critical/high severity findings suggests systemic security issues. "
                "Recommend comprehensive security review."
            )
        
        # Timeline analysis
        recent_findings = [
            f for f in result.findings 
            if (datetime.now() - f.detected_at).days < 1
        ]
        
        if len(recent_findings) == len(result.findings):
            insights.append(
                "All findings are new, indicating potential recent changes or first-time assessment. "
                "Establish baseline and monitor for changes."
            )
        
        return insights
    
    def _map_severity_to_threat_level(self, severity: str) -> ThreatLevel:
        """Map severity string to threat level enum"""
        mapping = {
            'critical': ThreatLevel.CRITICAL,
            'high': ThreatLevel.HIGH,
            'medium': ThreatLevel.MEDIUM, 
            'low': ThreatLevel.LOW,
            'info': ThreatLevel.INFO
        }
        return mapping.get(severity.lower(), ThreatLevel.MEDIUM)
    
    def _calculate_risk_score(self, findings: List[SecurityFinding]) -> float:
        """Calculate overall risk score"""
        
        if not findings:
            return 0.0
        
        # Weight findings by threat level
        weights = {
            ThreatLevel.CRITICAL: 10,
            ThreatLevel.HIGH: 7,
            ThreatLevel.MEDIUM: 4,
            ThreatLevel.LOW: 2,
            ThreatLevel.INFO: 1
        }
        
        total_score = sum(weights.get(f.threat_level, 0) for f in findings)
        max_possible = len(findings) * weights[ThreatLevel.CRITICAL]
        
        return (total_score / max_possible) * 10 if max_possible > 0 else 0.0
    
    def _generate_security_recommendations(self, result: SecurityAnalysisResult) -> List[str]:
        """Generate security recommendations based on findings"""
        
        recommendations = []
        
        # Category-based recommendations
        categories = set(f.category for f in result.findings)
        
        if 'injection' in ' '.join(categories).lower():
            recommendations.append("Implement input validation and parameterized queries to prevent injection attacks")
        
        if 'authentication' in ' '.join(categories).lower():
            recommendations.append("Strengthen authentication mechanisms with multi-factor authentication")
        
        if 'misconfiguration' in ' '.join(categories).lower():
            recommendations.append("Review and harden security configurations following security best practices")
        
        # Risk-based recommendations
        if result.risk_score > 7:
            recommendations.append("HIGH PRIORITY: Immediate attention required due to critical security risks")
        elif result.risk_score > 4:
            recommendations.append("MEDIUM PRIORITY: Address security issues within planned maintenance cycles")
        
        # Compliance-based recommendations
        if not result.compliance_status.get('owasp_top_10', True):
            recommendations.append("Achieve OWASP Top 10 compliance to address common web application risks")
        
        return recommendations
    
    def generate_executive_summary(self, analysis_id: str) -> Dict[str, Any]:
        """Generate executive summary of security analysis"""
        
        # Find analysis result
        result = None
        for analysis in self.analysis_history:
            if analysis.analysis_id == analysis_id:
                result = analysis
                break
        
        if not result:
            return {'error': 'Analysis not found'}
        
        # Calculate metrics
        critical_findings = [f for f in result.findings if f.threat_level == ThreatLevel.CRITICAL]
        high_findings = [f for f in result.findings if f.threat_level == ThreatLevel.HIGH]
        
        summary = {
            'analysis_id': analysis_id,
            'target': result.target.primary_url,
            'analysis_type': result.analysis_type.value,
            'executive_summary': {
                'overall_risk_rating': self._get_risk_rating(result.risk_score),
                'total_findings': len(result.findings),
                'critical_issues': len(critical_findings),
                'high_priority_issues': len(high_findings),
                'compliance_status': 'COMPLIANT' if all(result.compliance_status.values()) else 'NON-COMPLIANT'
            },
            'top_risks': [
                {
                    'title': f.title,
                    'threat_level': f.threat_level.value,
                    'remediation': f.remediation[:100] + '...' if len(f.remediation) > 100 else f.remediation
                } for f in result.findings[:5]  # Top 5 risks
            ],
            'recommendations': result.recommendations[:3],  # Top 3 recommendations
            'analysis_metadata': {
                'duration': str(result.end_time - result.start_time) if result.end_time else 'N/A',
                'success': result.success
            }
        }
        
        return summary
    
    def _get_risk_rating(self, risk_score: float) -> str:
        """Convert risk score to rating"""
        if risk_score >= 8:
            return 'CRITICAL'
        elif risk_score >= 6:
            return 'HIGH'
        elif risk_score >= 4:
            return 'MEDIUM'
        elif risk_score >= 2:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def get_analysis_history(self, target_url: str = None) -> List[SecurityAnalysisResult]:
        """Get analysis history, optionally filtered by target"""
        
        if target_url:
            return [a for a in self.analysis_history if a.target.primary_url == target_url]
        return self.analysis_history
    
    def _generate_agent_id(self) -> str:
        """Generate unique agent ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"security_agent_{timestamp}".encode()).hexdigest()[:12]
    
    def _generate_analysis_id(self, target: SecurityTarget) -> str:
        """Generate unique analysis ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"{target.target_id}_{timestamp}".encode()).hexdigest()[:16]
    
    def _generate_finding_id(self) -> str:
        """Generate unique finding ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"finding_{timestamp}".encode()).hexdigest()[:12]

# Convenience functions
async def quick_security_scan(target_url: str) -> SecurityAnalysisResult:
    """Quick security scan with vulnerability assessment"""
    
    agent = SecurityAnalystAgent()
    
    target = SecurityTarget(
        target_id=f"quick_scan_{datetime.now().timestamp()}",
        target_type='web_application',
        primary_url=target_url
    )
    
    return await agent.conduct_security_analysis(target, AnalysisType.VULNERABILITY_ASSESSMENT)

async def comprehensive_security_analysis(target_url: str, 
                                        additional_endpoints: List[str] = None) -> SecurityAnalysisResult:
    """Comprehensive security analysis including multiple assessment types"""
    
    agent = SecurityAnalystAgent()
    
    target = SecurityTarget(
        target_id=f"comprehensive_{datetime.now().timestamp()}",
        target_type='web_application',
        primary_url=target_url,
        additional_endpoints=additional_endpoints or []
    )
    
    # Start with vulnerability assessment
    result = await agent.conduct_security_analysis(target, AnalysisType.VULNERABILITY_ASSESSMENT)
    
    # Add threat intelligence
    threat_intel = await agent.conduct_security_analysis(target, AnalysisType.THREAT_INTELLIGENCE)
    result.findings.extend(threat_intel.findings)
    
    return result

if __name__ == "__main__":
    # Test security analyst agent
    async def test_security_agent():
        agent = SecurityAnalystAgent()
        
        # Quick security scan
        result = await quick_security_scan("https://httpbin.org")
        print(f"Security analysis completed: {result.success}")
        print(f"Findings: {len(result.findings)}")
        print(f"Risk score: {result.risk_score:.2f}")
        
        # Generate executive summary
        summary = agent.generate_executive_summary(result.analysis_id)
        print(f"Executive summary: {summary['executive_summary']}")
    
    asyncio.run(test_security_agent())
