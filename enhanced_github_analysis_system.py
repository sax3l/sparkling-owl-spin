#!/usr/bin/env python3
"""
Enhanced GitHub Repository Analysis System
==========================================

Avancerat system för att systematiskt analysera GitHub repositories
och integrera bästa features i vårt Ultimate Scraping System.

Använder vårt nya Control Center och Configuration Manager för
optimal processning av alla target repositories.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field, asdict
import subprocess
import tempfile
import hashlib
import re

# Våra system
from ultimate_scraping_control_center import UltimateScrapingControlCenter, ScrapeJobConfig, MonitoringLevel
from ultimate_configuration_manager import ConfigurationManager
from single_repo_analyzer import SingleRepositoryAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GitHubRepositoryTarget:
    """Information om ett GitHub repository som ska analyseras."""
    url: str
    name: str
    category: str
    priority: int = 1  # 1=high, 2=medium, 3=low
    expected_features: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class RepositoryAnalysisResult:
    """Resultat från repository-analys."""
    repo_url: str
    repo_name: str
    analysis_timestamp: datetime
    success: bool
    
    # Code Analysis
    total_files_analyzed: int = 0
    languages_found: List[str] = field(default_factory=list)
    key_features_identified: List[str] = field(default_factory=list)
    
    # Integration Assessment
    integration_potential: str = "unknown"  # high, medium, low, none
    recommended_integration_approach: str = ""
    estimated_implementation_effort: str = ""
    
    # Implementation Status
    implemented: bool = False
    integration_file: Optional[str] = None
    test_file: Optional[str] = None
    
    # Metadata
    error_message: Optional[str] = None
    analysis_notes: List[str] = field(default_factory=list)


class EnhancedGitHubAnalysisSystem:
    """
    Enhanced GitHub Analysis System
    ==============================
    
    Systematisk analys av GitHub repositories med fokus på:
    • Proxy och scraping-relaterad funktionalitet
    • Anti-detection tekniker
    • IP rotation och geo-distribution
    • Performance optimering
    • Security och stealth capabilities
    
    Integrerar med vårt Ultimate Scraping System för optimal processing.
    """
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.control_center = None
        self.project_root = Path.cwd()
        self.repo_analyzer = SingleRepositoryAnalyzer(self.project_root)
        
        # Analysis results
        self.analysis_results: Dict[str, RepositoryAnalysisResult] = {}
        self.implementation_log: List[Dict[str, Any]] = []
        
        # Target repositories - Extended list with categories
        self.target_repositories = self._define_target_repositories()
        
    def _define_target_repositories(self) -> List[GitHubRepositoryTarget]:
        """Definiera alla target repositories med kategorisering."""
        
        repos = [
            # === HIGH PRIORITY SCRAPING & PROXY ===
            GitHubRepositoryTarget(
                url="https://github.com/jhao104/proxy_pool",
                name="proxy_pool", 
                category="proxy_management",
                priority=1,
                expected_features=["proxy_fetching", "proxy_validation", "proxy_rotation", "multi_provider"],
                notes="Already analyzed - excellent proxy management system"
            ),
            GitHubRepositoryTarget(
                url="https://github.com/constverum/ProxyBroker", 
                name="ProxyBroker",
                category="proxy_advanced",
                priority=1,
                expected_features=["async_proxy_checking", "geographic_filtering", "protocol_support"],
                notes="Already analyzed - 58 classes, very comprehensive"
            ),
            GitHubRepositoryTarget(
                url="https://github.com/Ge0rg3/requests-ip-rotator",
                name="requests-ip-rotator",
                category="ip_rotation", 
                priority=1,
                expected_features=["aws_api_gateway", "ip_rotation", "session_management"],
                notes="Already analyzed - AWS API Gateway rotation"
            ),
            
            # === ADVANCED SCRAPING SYSTEMS ===
            GitHubRepositoryTarget(
                url="https://github.com/scrapy/scrapy",
                name="scrapy",
                category="scraping_framework",
                priority=1, 
                expected_features=["distributed_scraping", "middleware", "item_pipelines", "async_processing"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/NaiboWang/EasySpider",
                name="EasySpider",
                category="visual_scraping",
                priority=1,
                expected_features=["visual_scraping", "no_code", "browser_automation"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/ScrapeGraphAI/Scrapegraph-ai", 
                name="Scrapegraph-ai",
                category="ai_scraping",
                priority=1,
                expected_features=["ai_powered_scraping", "graph_extraction", "smart_parsing"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/unclecode/crawl4ai",
                name="crawl4ai", 
                category="ai_crawler",
                priority=1,
                expected_features=["ai_crawling", "content_extraction", "llm_integration"]
            ),
            
            # === STEALTH & ANTI-DETECTION ===
            GitHubRepositoryTarget(
                url="https://github.com/AtuboDad/playwright_stealth",
                name="playwright_stealth",
                category="stealth",
                priority=1,
                expected_features=["playwright_stealth", "anti_detection", "browser_fingerprinting"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/ulixee/secret-agent", 
                name="secret-agent",
                category="stealth_browser",
                priority=1,
                expected_features=["stealth_browser", "human_emulation", "detection_evasion"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/tholian-network/stealth",
                name="stealth",
                category="stealth_browser",
                priority=1, 
                expected_features=["privacy_browser", "fingerprint_resistance", "tor_integration"]
            ),
            
            # === CLOUDFLARE & WAF BYPASS ===
            GitHubRepositoryTarget(
                url="https://github.com/FlareSolverr/FlareSolverr",
                name="FlareSolverr",
                category="cloudflare_bypass",
                priority=1,
                expected_features=["cloudflare_bypass", "captcha_solving", "js_challenges"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/sarperavci/CloudflareBypassForScraping",
                name="CloudflareBypassForScraping", 
                category="cloudflare_bypass",
                priority=1,
                expected_features=["cloudflare_bypass", "scraping_optimization"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/solve-cloudflare/cloudflare-bypass",
                name="cloudflare-bypass",
                category="cloudflare_bypass", 
                priority=1,
                expected_features=["cloudflare_bypass", "challenge_solving"]
            ),
            
            # === PROXY MANAGEMENT & ROTATION ===
            GitHubRepositoryTarget(
                url="https://github.com/Python3WebSpider/ProxyPool",
                name="ProxyPool", 
                category="proxy_management",
                priority=2,
                expected_features=["proxy_pool", "validation", "scheduling"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/mubeng/mubeng",
                name="mubeng",
                category="proxy_rotation",
                priority=2,
                expected_features=["proxy_rotation", "load_balancing", "go_implementation"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/markgacoka/selenium-proxy-rotator", 
                name="selenium-proxy-rotator",
                category="proxy_selenium",
                priority=2,
                expected_features=["selenium_proxy", "browser_automation", "proxy_rotation"]
            ),
            
            # === NETWORK & PERFORMANCE ===
            GitHubRepositoryTarget(
                url="https://github.com/juancarlospaco/faster-than-requests",
                name="faster-than-requests",
                category="performance",
                priority=2,
                expected_features=["high_performance", "c_implementation", "speed_optimization"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/n8n-io/n8n",
                name="n8n",
                category="workflow_automation", 
                priority=2,
                expected_features=["workflow_automation", "api_integration", "data_processing"]
            ),
            
            # === SPECIALIZED SCRAPERS ===
            GitHubRepositoryTarget(
                url="https://github.com/gosom/google-maps-scraper",
                name="google-maps-scraper",
                category="specialized_scraper",
                priority=2,
                expected_features=["google_maps", "location_data", "business_info"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/dipu-bd/lightnovel-crawler",
                name="lightnovel-crawler", 
                category="content_scraper",
                priority=2,
                expected_features=["content_extraction", "multi_source", "format_conversion"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/itsOwen/CyberScraper-2077",
                name="CyberScraper-2077",
                category="modern_scraper",
                priority=2, 
                expected_features=["modern_scraping", "cyberpunk_theme", "advanced_features"]
            ),
            
            # === SWEDISH SPECIFIC ===
            GitHubRepositoryTarget(
                url="https://github.com/sch0ld/Biluppgifter-WebScraper",
                name="Biluppgifter-WebScraper",
                category="swedish_vehicle",
                priority=2,
                expected_features=["vehicle_data", "swedish_api", "registration_lookup"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/philipgyllhamn/fordonsuppgifter-api-wrapper",
                name="fordonsuppgifter-api-wrapper", 
                category="swedish_vehicle",
                priority=2,
                expected_features=["vehicle_api", "wrapper_implementation", "swedish_data"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/dunderrrrrr/blocket_api", 
                name="blocket_api",
                category="swedish_marketplace",
                priority=2,
                expected_features=["blocket_scraping", "marketplace_api", "classified_ads"]
            ),
            
            # === SECURITY & TESTING ===
            GitHubRepositoryTarget(
                url="https://github.com/m14r41/PentestingEverything",
                name="PentestingEverything",
                category="security_testing", 
                priority=3,
                expected_features=["penetration_testing", "security_tools", "vulnerability_assessment"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/swisskyrepo/PayloadsAllTheThings",
                name="PayloadsAllTheThings",
                category="security_payloads",
                priority=3,
                expected_features=["security_payloads", "injection_techniques", "bypass_methods"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/wallarm/gotestwaf",
                name="gotestwaf",
                category="waf_testing", 
                priority=3,
                expected_features=["waf_testing", "bypass_techniques", "security_assessment"]
            ),
            
            # === ADDITIONAL TOOLS ===
            GitHubRepositoryTarget(
                url="https://github.com/getmaxun/maxun",
                name="maxun", 
                category="automation_tool",
                priority=3,
                expected_features=["automation", "workflow", "data_extraction"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/D4Vinci/Scrapling",
                name="Scrapling",
                category="scraping_library",
                priority=3,
                expected_features=["python_scraping", "library", "ease_of_use"]
            ),
            GitHubRepositoryTarget(
                url="https://github.com/BruceDone/awesome-crawler", 
                name="awesome-crawler",
                category="resource_collection",
                priority=3,
                expected_features=["crawler_resources", "documentation", "tools_collection"]
            ),
        ]
        
        return repos
        
    async def initialize(self):
        """Initialisera analysis systemet."""
        
        print("🚀 INITIALIZING ENHANCED GITHUB ANALYSIS SYSTEM")
        print("=" * 60)
        
        # Initialisera Control Center
        self.control_center = UltimateScrapingControlCenter()
        await self.control_center.initialize()
        
        print(f"📊 Target repositories: {len(self.target_repositories)}")
        print("✅ System initialized successfully!")
        
    async def run_comprehensive_repository_analysis(self):
        """Kör omfattande analys av alla target repositories."""
        
        print("\n🔍 STARTING COMPREHENSIVE REPOSITORY ANALYSIS")
        print("=" * 60)
        
        # Gruppera repositories efter prioritet
        high_priority = [r for r in self.target_repositories if r.priority == 1]
        medium_priority = [r for r in self.target_repositories if r.priority == 2] 
        low_priority = [r for r in self.target_repositories if r.priority == 3]
        
        print(f"📈 High Priority: {len(high_priority)} repositories")
        print(f"📊 Medium Priority: {len(medium_priority)} repositories")
        print(f"📉 Low Priority: {len(low_priority)} repositories")
        
        # Analysera i prioritetsordning
        all_repos = high_priority + medium_priority + low_priority
        
        for i, repo in enumerate(all_repos):
            print(f"\n{'='*20} ANALYZING {i+1}/{len(all_repos)} {'='*20}")
            print(f"🎯 Repository: {repo.name}")
            print(f"🔗 URL: {repo.url}")
            print(f"📂 Category: {repo.category}")
            print(f"⭐ Priority: {repo.priority}")
            
            try:
                # Utför analys
                result = await self._analyze_single_repository(repo)
                self.analysis_results[repo.url] = result
                
                # Visa resultat
                self._display_analysis_result(result)
                
                # Paus mellan repositories för att inte överbelasta
                if i < len(all_repos) - 1:
                    print("⏳ Pausing 2 seconds before next repository...")
                    await asyncio.sleep(2)
                    
            except Exception as e:
                error_result = RepositoryAnalysisResult(
                    repo_url=repo.url,
                    repo_name=repo.name,
                    analysis_timestamp=datetime.now(),
                    success=False,
                    error_message=str(e)
                )
                self.analysis_results[repo.url] = error_result
                print(f"❌ Analysis failed: {e}")
                
        # Generera sammanfattningsrapport
        await self._generate_comprehensive_analysis_report()
        
    async def _analyze_single_repository(self, repo: GitHubRepositoryTarget) -> RepositoryAnalysisResult:
        """Analysera ett enskilt repository."""
        
        result = RepositoryAnalysisResult(
            repo_url=repo.url,
            repo_name=repo.name,
            analysis_timestamp=datetime.now(),
            success=False
        )
        
        try:
            print(f"🔍 Starting analysis of {repo.name}...")
            
            # Använd vårt befintliga manual analyzer
            # Vi behöver skapa en temporär implementation för att hantera URL direkt
            analysis = await self._analyze_repository_url_directly(repo.url)
            
            if analysis:
                result.success = True
                result.total_files_analyzed = analysis.get("structure_analysis", {}).get("total_files", 0)
                
                # Extrahera språk från kod analys
                code_analysis = analysis.get("code_analysis", {})
                languages_info = code_analysis.get("languages", {})
                result.languages_found = list(languages_info.keys()) if languages_info else []
                
                # Extrahera key features från implementation insights
                insights = analysis.get("implementation_insights", [])
                result.key_features_identified = [insight.get("feature", "unknown") for insight in insights[:10]]
                
                # Bedöm integration potential baserat på kategori och features
                result.integration_potential = self._assess_integration_potential(repo, analysis)
                result.recommended_integration_approach = self._recommend_integration_approach(repo, analysis)
                result.estimated_implementation_effort = self._estimate_implementation_effort(repo, analysis)
                
                # Lägg till analysis notes
                result.analysis_notes = [
                    f"Repository contains {analysis.get('structure_analysis', {}).get('total_files', 0)} files",
                    f"Clone successful: {analysis.get('clone_success', False)}",
                    f"Key files found: {len(analysis.get('key_files', []))}",
                    f"Implementation insights: {len(insights)}",
                    f"Integration complexity: {result.integration_potential}"
                ]
                
            else:
                result.error_message = "Failed to analyze repository structure"
                
        except Exception as e:
            result.error_message = str(e)
            print(f"❌ Error analyzing {repo.name}: {e}")
            
        return result
        
    async def _analyze_repository_url_directly(self, url: str) -> Optional[Dict[str, Any]]:
        """Analysera repository direkt från URL genom att använda git clone."""
        
        import tempfile
        import subprocess
        
        try:
            # Skapa temp directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                repo_name = url.split('/')[-1].replace('.git', '')
                clone_path = temp_path / repo_name
                
                print(f"🔄 Cloning {url}...")
                
                # Clone repository
                result = subprocess.run([
                    'git', 'clone', '--depth', '1', url, str(clone_path)
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    print(f"❌ Failed to clone: {result.stderr}")
                    return None
                    
                # Använd vårt manual analyzer system
                analyzer = SingleRepositoryAnalyzer(self.project_root if hasattr(self, 'project_root') else Path.cwd())
                
                # Skapa basic analysis structure
                analysis = await analyzer._analyze_project_structure(clone_path)
                
                # Lägg till repository info
                analysis["repository"] = {
                    "url": url,
                    "name": repo_name
                }
                analysis["clone_success"] = True
                
                return analysis
                
        except Exception as e:
            print(f"❌ Error analyzing {url}: {e}")
            return None
        
    def _assess_integration_potential(self, repo: GitHubRepositoryTarget, analysis: Dict[str, Any]) -> str:
        """Bedöm integration potential för repository."""
        
        # High potential categories
        high_potential_categories = [
            "proxy_management", "proxy_advanced", "ip_rotation", 
            "stealth", "cloudflare_bypass", "ai_scraping"
        ]
        
        # Medium potential categories  
        medium_potential_categories = [
            "scraping_framework", "performance", "specialized_scraper",
            "modern_scraper", "proxy_rotation"
        ]
        
        if repo.category in high_potential_categories:
            return "high"
        elif repo.category in medium_potential_categories:
            return "medium"
        elif repo.priority <= 2:
            return "medium"
        else:
            return "low"
            
    def _recommend_integration_approach(self, repo: GitHubRepositoryTarget, analysis: Dict[str, Any]) -> str:
        """Rekommendera integration approach."""
        
        approaches = {
            "proxy_management": "Integrate proxy fetching and validation methods into our proxy_pool module",
            "proxy_advanced": "Extract advanced proxy handling classes for our Enhanced Proxy Manager", 
            "ip_rotation": "Implement IP rotation techniques in our IP rotation system",
            "stealth": "Integrate stealth techniques into our anti-detection module",
            "cloudflare_bypass": "Create specialized Cloudflare bypass module",
            "ai_scraping": "Develop AI-powered content extraction capabilities",
            "scraping_framework": "Extract core scraping patterns and middleware concepts",
            "performance": "Integrate performance optimization techniques",
            "swedish_vehicle": "Create specialized Swedish vehicle data module"
        }
        
        return approaches.get(repo.category, "Manual code review and selective feature extraction")
        
    def _estimate_implementation_effort(self, repo: GitHubRepositoryTarget, analysis: Dict[str, Any]) -> str:
        """Uppskatta implementation effort."""
        
        if not analysis or not analysis.get("clone_success"):
            return "unknown"
            
        structure_analysis = analysis.get("structure_analysis", {})
        total_files = structure_analysis.get("total_files", 0)
        code_analysis = analysis.get("code_analysis", {})
        languages = len(code_analysis.get("languages", {}))
        insights = len(analysis.get("implementation_insights", []))
        
        # Beräkna komplexitetspoäng
        complexity_score = (total_files * 0.1) + (languages * 2) + (insights * 0.5)
        
        if complexity_score < 10:
            return "low (1-2 days)"
        elif complexity_score < 25:
            return "medium (3-5 days)" 
        elif complexity_score < 50:
            return "high (1-2 weeks)"
        else:
            return "very high (2+ weeks)"
            
    def _display_analysis_result(self, result: RepositoryAnalysisResult):
        """Visa analysis resultat."""
        
        if result.success:
            print(f"✅ Analysis completed successfully!")
            print(f"   📁 Files analyzed: {result.total_files_analyzed}")
            print(f"   💻 Languages: {', '.join(result.languages_found[:3])}...")
            print(f"   🎯 Key features: {len(result.key_features_identified)}")
            print(f"   📊 Integration potential: {result.integration_potential}")
            print(f"   ⏱️ Estimated effort: {result.estimated_implementation_effort}")
            
            if result.key_features_identified:
                print(f"   🔧 Top features: {', '.join(result.key_features_identified[:3])}")
                
        else:
            print(f"❌ Analysis failed: {result.error_message}")
            
    async def _generate_comprehensive_analysis_report(self):
        """Generera omfattande analysrapport."""
        
        print("\n📄 GENERATING COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 50)
        
        # Statistik
        total_repos = len(self.analysis_results)
        successful_analyses = sum(1 for r in self.analysis_results.values() if r.success)
        failed_analyses = total_repos - successful_analyses
        
        # Gruppera efter integration potential
        high_potential = [r for r in self.analysis_results.values() if r.integration_potential == "high" and r.success]
        medium_potential = [r for r in self.analysis_results.values() if r.integration_potential == "medium" and r.success]
        low_potential = [r for r in self.analysis_results.values() if r.integration_potential == "low" and r.success]
        
        # Skapa rapport
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_repositories_analyzed": total_repos,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": (successful_analyses / total_repos * 100) if total_repos > 0 else 0
            },
            "integration_potential_breakdown": {
                "high_potential": len(high_potential),
                "medium_potential": len(medium_potential), 
                "low_potential": len(low_potential)
            },
            "detailed_results": {}
        }
        
        # Lägg till detaljerade resultat
        for repo_url, result in self.analysis_results.items():
            report["detailed_results"][repo_url] = {
                "repo_name": result.repo_name,
                "success": result.success,
                "analysis_timestamp": result.analysis_timestamp.isoformat() if result.analysis_timestamp else None,
                "total_files_analyzed": result.total_files_analyzed,
                "languages_found": result.languages_found,
                "key_features_identified": result.key_features_identified,
                "integration_potential": result.integration_potential,
                "recommended_integration_approach": result.recommended_integration_approach,
                "estimated_implementation_effort": result.estimated_implementation_effort,
                "error_message": result.error_message,
                "analysis_notes": result.analysis_notes
            }
            
        # Spara rapport
        report_path = Path("reports") / f"github_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Skapa HTML rapport
        await self._generate_html_analysis_report(report, report_path.with_suffix('.html'))
        
        # Visa sammanfattning
        print(f"📊 ANALYSIS SUMMARY:")
        print(f"   Total repositories: {total_repos}")
        print(f"   Successful analyses: {successful_analyses}")
        print(f"   Failed analyses: {failed_analyses}")
        print(f"   Success rate: {report['summary']['success_rate']:.1f}%")
        print(f"\n🎯 INTEGRATION POTENTIAL:")
        print(f"   High potential: {len(high_potential)} repositories")
        print(f"   Medium potential: {len(medium_potential)} repositories") 
        print(f"   Low potential: {len(low_potential)} repositories")
        
        print(f"\n📄 Reports generated:")
        print(f"   JSON: {report_path}")
        print(f"   HTML: {report_path.with_suffix('.html')}")
        
        # Visa high potential repositories
        if high_potential:
            print(f"\n⭐ HIGH POTENTIAL REPOSITORIES:")
            for result in high_potential[:10]:  # Top 10
                print(f"   • {result.repo_name}: {result.estimated_implementation_effort}")
                
    async def _generate_html_analysis_report(self, data: Dict[str, Any], output_path: Path):
        """Generera HTML analysrapport."""
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GitHub Repository Comprehensive Analysis Report</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background-color: #f5f5f5;
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 30px; 
            border-radius: 10px; 
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{ 
            background: white;
            padding: 20px; 
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .repo-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .repo-card {{ 
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #ccc;
        }}
        .repo-card.high {{ border-left-color: #28a745; }}
        .repo-card.medium {{ border-left-color: #ffc107; }}  
        .repo-card.low {{ border-left-color: #6c757d; }}
        .success {{ color: #28a745; font-weight: bold; }}
        .error {{ color: #dc3545; font-weight: bold; }}
        .feature-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin: 10px 0;
        }}
        .feature-tag {{
            background: #e9ecef;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            color: #495057;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats-table th, .stats-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }}
        .stats-table th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        h1, h2 {{ color: #333; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 GitHub Repository Comprehensive Analysis</h1>
        <p class="timestamp">Generated: {data['analysis_timestamp']}</p>
        <p>Systematic analysis of {data['summary']['total_repositories_analyzed']} repositories for integration into Ultimate Scraping System</p>
    </div>
    
    <div class="summary-grid">
        <div class="metric-card">
            <div class="metric-value">{data['summary']['total_repositories_analyzed']}</div>
            <div>Total Repositories</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{data['summary']['successful_analyses']}</div>
            <div>Successful Analyses</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{data['summary']['success_rate']:.1f}%</div>
            <div>Success Rate</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{data['integration_potential_breakdown']['high_potential']}</div>
            <div>High Potential</div>
        </div>
    </div>
    
    <h2>📊 Integration Potential Breakdown</h2>
    <table class="stats-table">
        <tr>
            <th>Potential Level</th>
            <th>Count</th>
            <th>Percentage</th>
        </tr>
        <tr>
            <td>🟢 High Potential</td>
            <td>{data['integration_potential_breakdown']['high_potential']}</td>
            <td>{(data['integration_potential_breakdown']['high_potential'] / max(1, data['summary']['successful_analyses']) * 100):.1f}%</td>
        </tr>
        <tr>
            <td>🟡 Medium Potential</td>
            <td>{data['integration_potential_breakdown']['medium_potential']}</td>
            <td>{(data['integration_potential_breakdown']['medium_potential'] / max(1, data['summary']['successful_analyses']) * 100):.1f}%</td>
        </tr>
        <tr>
            <td>🔘 Low Potential</td>
            <td>{data['integration_potential_breakdown']['low_potential']}</td>
            <td>{(data['integration_potential_breakdown']['low_potential'] / max(1, data['summary']['successful_analyses']) * 100):.1f}%</td>
        </tr>
    </table>
    
    <h2>📁 Repository Analysis Details</h2>
    <div class="repo-grid">
"""
        
        # Lägg till alla repositories
        for repo_url, details in data['detailed_results'].items():
            status_class = "success" if details['success'] else "error"
            potential_class = details.get('integration_potential', 'low')
            
            html_content += f"""
        <div class="repo-card {potential_class}">
            <h3>{details['repo_name']}</h3>
            <div class="{status_class}">
                {'✅ Analyzed Successfully' if details['success'] else '❌ Analysis Failed'}
            </div>
            """
            
            if details['success']:
                html_content += f"""
            <p><strong>Files Analyzed:</strong> {details['total_files_analyzed']}</p>
            <p><strong>Languages:</strong> {', '.join(details['languages_found'][:5])}</p>
            <p><strong>Integration Potential:</strong> 
               <span class="feature-tag {potential_class}">{details['integration_potential'].upper()}</span>
            </p>
            <p><strong>Implementation Effort:</strong> {details['estimated_implementation_effort']}</p>
            
            <div class="feature-list">
                """
                
                for feature in details['key_features_identified'][:10]:
                    html_content += f'<span class="feature-tag">{feature}</span>'
                    
                html_content += """
            </div>
            
            <p><strong>Recommended Approach:</strong></p>
            <p style="font-size: 0.9em; color: #666;">{}</p>
                """.format(details['recommended_integration_approach'])
            else:
                html_content += f"""
            <p class="error">Error: {details.get('error_message', 'Unknown error')}</p>
                """
                
            html_content += """
        </div>
            """
            
        html_content += """
    </div>
    
    <footer style="margin-top: 40px; padding: 20px; text-align: center; color: #666;">
        <p><em>Generated by Enhanced GitHub Analysis System - Ultimate Scraping Architecture</em></p>
    </footer>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    async def get_implementation_recommendations(self) -> Dict[str, List[str]]:
        """Hämta implementation recommendations baserat på analysis."""
        
        recommendations = {
            "immediate_implementation": [],
            "short_term_goals": [], 
            "long_term_projects": [],
            "research_targets": []
        }
        
        # Analysera resultat för rekommendationer
        high_potential = [r for r in self.analysis_results.values() 
                         if r.success and r.integration_potential == "high"]
        
        for result in high_potential:
            if "low" in result.estimated_implementation_effort:
                recommendations["immediate_implementation"].append(
                    f"{result.repo_name}: {result.recommended_integration_approach}"
                )
            elif "medium" in result.estimated_implementation_effort:
                recommendations["short_term_goals"].append(
                    f"{result.repo_name}: {result.recommended_integration_approach}" 
                )
            else:
                recommendations["long_term_projects"].append(
                    f"{result.repo_name}: {result.recommended_integration_approach}"
                )
                
        return recommendations
        
    async def shutdown(self):
        """Stäng ner systemet gracefully."""
        
        if self.control_center:
            await self.control_center.shutdown()
            
        print("🔄 Enhanced GitHub Analysis System shutdown complete")


async def main():
    """Huvudfunktion för att köra GitHub repository analysen."""
    
    analysis_system = EnhancedGitHubAnalysisSystem()
    
    try:
        # Initialisera systemet
        await analysis_system.initialize()
        
        # Kör omfattande analys
        await analysis_system.run_comprehensive_repository_analysis()
        
        # Hämta implementation recommendations
        recommendations = await analysis_system.get_implementation_recommendations()
        
        print("\n🎯 IMPLEMENTATION RECOMMENDATIONS:")
        print("=" * 50)
        
        if recommendations["immediate_implementation"]:
            print("🚀 IMMEDIATE IMPLEMENTATION (Low Effort):")
            for rec in recommendations["immediate_implementation"]:
                print(f"  • {rec}")
                
        if recommendations["short_term_goals"]:
            print("\n📈 SHORT TERM GOALS (Medium Effort):")
            for rec in recommendations["short_term_goals"]:
                print(f"  • {rec}")
                
        if recommendations["long_term_projects"]:
            print("\n🎯 LONG TERM PROJECTS (High Effort):")
            for rec in recommendations["long_term_projects"]:
                print(f"  • {rec}")
                
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        
    finally:
        await analysis_system.shutdown()


if __name__ == "__main__":
    print("🚀 Enhanced GitHub Repository Analysis System")
    print("=" * 60)
    print("Comprehensive analysis of GitHub repositories for Ultimate Scraping System integration")
    print("\nPress Ctrl+C to interrupt at any time")
    print("=" * 60)
    
    asyncio.run(main())
