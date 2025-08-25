#!/usr/bin/env python3
"""
🦉 Sparkling-Owl-Spin Vendor Analysis & Integration Verification
================================================================

Analyserar alla vendors för att säkerställa enhetlig integration i pyramid-systemet.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set

class VendorAnalyzer:
    """Analyserar vendor-implementation och integration"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.vendors_path = self.project_root / "vendors"
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "vendor_analysis": {},
            "integration_status": {},
            "recommendations": [],
            "critical_issues": [],
            "summary": {}
        }
    
    def analyze_all_vendors(self) -> Dict[str, Any]:
        """Huvudanalys av alla vendors"""
        
        print("🔍 Analyserar Vendor-struktur...")
        
        # Förväntade core vendors (från pyramid-arkitektur)
        expected_core_vendors = {
            "flaresolverr": {"type": "cloudflare_bypass", "priority": "critical"},
            "undetected-chromedriver": {"type": "stealth_browser", "priority": "critical"},
            "proxy_pool": {"type": "proxy_management", "priority": "critical"},
            "crawlee": {"type": "crawling_engine", "priority": "high"},
            "scrapy": {"type": "scraping_framework", "priority": "high"},
            "crewAI": {"type": "ai_orchestration", "priority": "critical"},
            "playwright_stealth": {"type": "stealth_browser", "priority": "high"},
            "SeleniumBase": {"type": "browser_automation", "priority": "medium"},
            "Scrapegraph-ai": {"type": "ai_scraping", "priority": "high"},
            "langroid": {"type": "llm_framework", "priority": "medium"},
            "tika": {"type": "document_processing", "priority": "medium"},
            "trafilatura": {"type": "content_extraction", "priority": "medium"},
            "vanna": {"type": "sql_ai", "priority": "low"},
            "Adala": {"type": "ai_agents", "priority": "medium"}
        }
        
        # AI/ML Enhancement vendors
        ai_enhancement_vendors = {
            "crawl4ai": {"type": "ai_crawling", "priority": "high"},
            "secret-agent": {"type": "stealth_browser", "priority": "high"},
            "localGPT": {"type": "local_llm", "priority": "medium"},
            "react-agent": {"type": "ai_automation", "priority": "low"},
            "AgentVerse": {"type": "multi_agent", "priority": "low"},
            "fastagency": {"type": "fast_agents", "priority": "low"}
        }
        
        # Utility & Support vendors
        utility_vendors = {
            "fake-useragent": {"type": "anti_detection", "priority": "medium"},
            "requests-ip-rotator": {"type": "ip_rotation", "priority": "high"},
            "mubeng": {"type": "proxy_checker", "priority": "medium"},
            "zenrows-python-sdk": {"type": "commercial_api", "priority": "low"},
            "stealth": {"type": "stealth_library", "priority": "medium"},
            "aider": {"type": "development_tool", "priority": "low"},
            "sweep": {"type": "code_assistant", "priority": "low"}
        }
        
        # Advanced/Specialized vendors
        specialized_vendors = {
            "Cloudflare-Solver-": {"type": "cloudflare_bypass", "priority": "medium"},
            "cloudflare-protection": {"type": "cloudflare_analysis", "priority": "low"},
            "CyberScraper-2077": {"type": "advanced_scraper", "priority": "low"},
            "EasySpider": {"type": "visual_scraper", "priority": "low"},
            "PulsarRPA": {"type": "rpa_automation", "priority": "low"},
            "Scrapling": {"type": "scraping_library", "priority": "medium"},
            "scrapy-playwright": {"type": "scrapy_extension", "priority": "medium"}
        }
        
        # Cross-language vendors
        crosslang_vendors = {
            "jsoup": {"type": "java_html_parser", "priority": "low"},
            "colly": {"type": "go_scraper", "priority": "low"},
            "cheerio": {"type": "nodejs_parser", "priority": "low"}
        }
        
        all_expected_vendors = {
            **expected_core_vendors,
            **ai_enhancement_vendors, 
            **utility_vendors,
            **specialized_vendors,
            **crosslang_vendors
        }
        
        # Analysera faktiska vendors
        found_vendors = []
        if self.vendors_path.exists():
            found_vendors = [d.name for d in self.vendors_path.iterdir() if d.is_dir()]
        
        # Kategorisera vendors
        critical_vendors = [v for v, info in all_expected_vendors.items() if info["priority"] == "critical"]
        high_priority_vendors = [v for v, info in all_expected_vendors.items() if info["priority"] == "high"]
        
        # Analysresultat
        missing_vendors = [v for v in all_expected_vendors.keys() if v not in found_vendors]
        extra_vendors = [v for v in found_vendors if v not in all_expected_vendors]
        
        # Kritiska saknade vendors
        missing_critical = [v for v in critical_vendors if v not in found_vendors]
        missing_high = [v for v in high_priority_vendors if v not in found_vendors]
        
        self.analysis_results["vendor_analysis"] = {
            "expected_vendors": len(all_expected_vendors),
            "found_vendors": len(found_vendors),
            "missing_vendors": missing_vendors,
            "extra_vendors": extra_vendors,
            "critical_missing": missing_critical,
            "high_priority_missing": missing_high,
            "vendor_categories": {
                "core": list(expected_core_vendors.keys()),
                "ai_enhancement": list(ai_enhancement_vendors.keys()),
                "utility": list(utility_vendors.keys()),
                "specialized": list(specialized_vendors.keys()),
                "crosslang": list(crosslang_vendors.keys())
            }
        }
        
        return self.analysis_results
    
    def check_vendor_integrations(self) -> Dict[str, Any]:
        """Kontrollerar integration av vendors i systemet"""
        
        print("🔗 Kontrollerar vendor-integrations...")
        
        integrations = {}
        
        # Kontrollera import-statements i kärnfiler
        core_files_to_check = [
            "engines/core/orchestrator.py",
            "engines/scraping/revolutionary/core/proxy_rotator.py", 
            "revolutionary_scraper/unified_revolutionary_system.py",
            "backend/main.py",
            "core/orchestration/sparkling_owl_spin.py"
        ]
        
        for file_path in core_files_to_check:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Leta efter vendor-imports
                    vendor_imports = []
                    for line in content.split('\n'):
                        if 'import' in line and any(vendor in line.lower() for vendor in 
                            ['scrapy', 'playwright', 'selenium', 'requests', 'crewai', 'langroid']):
                            vendor_imports.append(line.strip())
                    
                    if vendor_imports:
                        integrations[file_path] = vendor_imports
                        
                except Exception as e:
                    integrations[file_path] = f"Error reading: {e}"
        
        self.analysis_results["integration_status"] = integrations
        return integrations
    
    def generate_recommendations(self) -> List[str]:
        """Genererar rekommendationer för vendor-förbättringar"""
        
        recommendations = []
        
        # Kritiska saknade vendors
        missing_critical = self.analysis_results["vendor_analysis"].get("critical_missing", [])
        if missing_critical:
            recommendations.append(f"🚨 KRITISKT: Saknade kritiska vendors: {', '.join(missing_critical)}")
        
        # Dubbletter av samma funktionalitet
        found_vendors = [d.name for d in self.vendors_path.iterdir() if d.is_dir()]
        
        # Cloudflare-duplikation
        cloudflare_vendors = [v for v in found_vendors if 'cloudflare' in v.lower()]
        if len(cloudflare_vendors) > 2:
            recommendations.append(f"⚠️ Flera Cloudflare-lösningar: {cloudflare_vendors}. Konsolidera till 1-2 st.")
        
        # Browser automation-duplikation  
        browser_vendors = [v for v in found_vendors if any(term in v.lower() for term in 
                          ['selenium', 'playwright', 'chrome', 'stealth'])]
        if len(browser_vendors) > 3:
            recommendations.append(f"⚠️ Många browser-lösningar: {browser_vendors}. Utvärdera användning.")
        
        # AI/LLM-duplikation
        ai_vendors = [v for v in found_vendors if any(term in v.lower() for term in 
                     ['ai', 'gpt', 'llm', 'agent', 'crew'])]
        if len(ai_vendors) > 4:
            recommendations.append(f"⚠️ Många AI-lösningar: {ai_vendors}. Koordinera användning.")
        
        # Organisationsrekommendationer
        recommendations.append("📁 Skapa vendor-kategorier: core/, ai/, utility/, specialized/")
        recommendations.append("📋 Implementera vendor-init system för lazy loading")
        recommendations.append("🔧 Skapa enhetlig vendor-konfiguration i config/vendors.yaml")
        recommendations.append("🧪 Lägg till vendor-integrationstester")
        
        self.analysis_results["recommendations"] = recommendations
        return recommendations
    
    def create_vendor_summary(self) -> Dict[str, Any]:
        """Skapar sammanfattning av vendor-analysen"""
        
        vendor_analysis = self.analysis_results["vendor_analysis"]
        
        # Beräkna täckning
        expected = vendor_analysis["expected_vendors"]
        found = vendor_analysis["found_vendors"] 
        coverage = (found / expected) * 100 if expected > 0 else 0
        
        # Status-klassificering
        if coverage >= 95:
            status = "EXCELLENT ✅"
        elif coverage >= 85:
            status = "GOOD ✅"
        elif coverage >= 70:
            status = "ACCEPTABLE ⚠️"
        else:
            status = "NEEDS_IMPROVEMENT ❌"
        
        summary = {
            "overall_status": status,
            "vendor_coverage": f"{coverage:.1f}%",
            "total_vendors": len([d.name for d in self.vendors_path.iterdir() if d.is_dir()]),
            "critical_issues": len(vendor_analysis.get("critical_missing", [])),
            "integration_files": len(self.analysis_results["integration_status"]),
            "recommendations_count": len(self.analysis_results["recommendations"])
        }
        
        self.analysis_results["summary"] = summary
        return summary
    
    def save_analysis_report(self):
        """Sparar analysrapporten"""
        
        report_path = self.project_root / "VENDOR_ANALYSIS_REPORT.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Analysrapport sparad: {report_path}")
    
    def print_analysis_summary(self):
        """Skriver ut analyssammanfattning"""
        
        print("\n" + "="*70)
        print("🦉 SPARKLING-OWL-SPIN VENDOR ANALYSIS SUMMARY")
        print("="*70)
        
        summary = self.analysis_results["summary"]
        vendor_analysis = self.analysis_results["vendor_analysis"]
        
        print(f"\n📊 OVERALL STATUS: {summary['overall_status']}")
        print(f"📈 Vendor Coverage: {summary['vendor_coverage']}")
        print(f"📦 Total Vendors: {summary['total_vendors']}")
        print(f"🚨 Critical Issues: {summary['critical_issues']}")
        print(f"🔗 Integration Files: {summary['integration_files']}")
        
        # Kritiska saknade
        if vendor_analysis.get("critical_missing"):
            print(f"\n🚨 CRITICAL MISSING VENDORS:")
            for vendor in vendor_analysis["critical_missing"]:
                print(f"   ❌ {vendor}")
        
        # Högt prioriterade saknade
        if vendor_analysis.get("high_priority_missing"):
            print(f"\n⚠️ HIGH PRIORITY MISSING VENDORS:")
            for vendor in vendor_analysis["high_priority_missing"]:
                print(f"   ⚠️ {vendor}")
        
        # Extra vendors
        if vendor_analysis.get("extra_vendors"):
            print(f"\n➕ EXTRA VENDORS (not in spec):")
            for vendor in vendor_analysis["extra_vendors"][:10]:  # Visa första 10
                print(f"   ➕ {vendor}")
            if len(vendor_analysis["extra_vendors"]) > 10:
                print(f"   ... and {len(vendor_analysis['extra_vendors']) - 10} more")
        
        # Rekommendationer
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in self.analysis_results["recommendations"]:
            print(f"   {rec}")
        
        print("\n" + "="*70)

def main():
    """Huvudfunktion"""
    
    project_root = Path(__file__).parent
    analyzer = VendorAnalyzer(str(project_root))
    
    # Kör fullständig analys
    analyzer.analyze_all_vendors()
    analyzer.check_vendor_integrations()
    analyzer.generate_recommendations()
    analyzer.create_vendor_summary()
    
    # Presentera resultat
    analyzer.print_analysis_summary()
    analyzer.save_analysis_report()

if __name__ == "__main__":
    main()
