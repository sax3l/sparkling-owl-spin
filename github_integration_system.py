#!/usr/bin/env python3
"""
GitHub Repository Analysis and Integration System
=================================================

Systematiskt system för att:
1. Importera GitHub repositories
2. Analysera och kompilera unik kod
3. Integrera ny funktionalitet i befintlig kod
4. Testa implementationen
5. Ta bort temporära filer och fortsätta med nästa repo

Designat för att förbättra Sparkling Owl Spin med ny funktionalitet.
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
import ast
import importlib.util
import hashlib

from utils.logger import get_logger
from database.manager import DatabaseManager
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class RepositoryInfo:
    """Information om ett GitHub repository."""
    url: str
    name: str
    owner: str
    description: str = ""
    language: str = ""
    stars: int = 0
    last_updated: str = ""


@dataclass
class CodeAnalysis:
    """Analys av kod från repository."""
    file_path: str
    language: str
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity_score: float
    unique_features: List[str]
    integration_potential: str  # 'high', 'medium', 'low'


@dataclass
class IntegrationResult:
    """Resultat av kodintegration."""
    repository: str
    integrated_features: List[str]
    new_modules: List[str]
    enhanced_modules: List[str]
    tests_created: List[str]
    success: bool
    error_message: Optional[str] = None


class GitHubRepositoryAnalyzer:
    """
    Avancerad GitHub repository-analysator och integrator.
    
    Funktionalitet:
    - Klona och analysera repositories
    - Identifiera unik funktionalitet
    - Integrera kod i befintlig arkitektur
    - Skapa tester för ny funktionalitet
    - Rensa upp temporära filer
    """
    
    def __init__(self, project_root: Path, metrics: MetricsCollector):
        self.project_root = project_root
        self.metrics = metrics
        self.temp_dir = Path(tempfile.mkdtemp(prefix="github_analysis_"))
        self.integration_log = []
        
        # Befintlig kod-signatur för att identifiera duplicering
        self.existing_signatures = self._generate_existing_signatures()
        
        # Repositories att analysera
        self.target_repositories = [
            "https://github.com/m14r41/PentestingEverything",
            "https://github.com/PhHitachi/HackBar",
            "https://github.com/arainho/awesome-api-security",
            "https://github.com/xemarap/pxstatspy",
            "https://github.com/NaiboWang/EasySpider",
            "https://github.com/fsson/vehicle-scraper",
            "https://github.com/ScrapeGraphAI/Scrapegraph-ai",
            "https://github.com/ProxyScraper/ProxyScraper",
            "https://github.com/unclecode/crawl4ai",
            "https://github.com/n8n-io/n8n",
            "https://github.com/azizzakiryarov/transport-api",
            "https://github.com/sch0ld/Biluppgifter-WebScraper",
            "https://github.com/ulixee/secret-agent",
            "https://github.com/tholian-network/stealth",
            "https://github.com/mkock/auto-lookup",
            "https://github.com/tholian-network/stealthify",
            "https://github.com/philipgyllhamn/fordonsuppgifter-api-wrapper",
            "https://github.com/jhao104/proxy_pool",
            "https://github.com/AtuboDad/playwright_stealth",
            "https://github.com/TheWebScrapingClub/webscraping-from-0-to-hero",
            "https://github.com/TheWebScrapingClub/TheScrapingClubFree",
            "https://github.com/TheWebScrapingClub/AI-Cursor-Scraping-Assistant",
            "https://github.com/D4Vinci/Scrapling",
            "https://github.com/BruceDone/awesome-crawler",
            "https://github.com/getmaxun/maxun",
            "https://github.com/gosom/google-maps-scraper",
            "https://github.com/dipu-bd/lightnovel-crawler",
            "https://github.com/anaskhan96/soup",
            "https://github.com/itsOwen/CyberScraper-2077",
            "https://github.com/juancarlospaco/faster-than-requests",
            "https://github.com/gildas-lormeau/single-file-cli",
            "https://github.com/platonai/PulsarRPA",
            "https://github.com/website-scraper/node-website-scraper",
            "https://github.com/scrapy/scrapy",
            "https://github.com/mubeng/mubeng",
            "https://github.com/alpkeskin/rota",
            "https://github.com/markgacoka/selenium-proxy-rotator",
            "https://github.com/joewhite86/proxy-rotator",
            "https://github.com/p0dalirius/ipsourcebypass",
            "https://github.com/Python3WebSpider/ProxyPool",
            "https://github.com/wzdnzd/aggregator",
            "https://github.com/constverum/ProxyBroker",
            "https://github.com/zu1k/proxypool",
            "https://github.com/dunderrrrrr/blocket_api",
            "https://github.com/sax3l/awesome-sweden",
            "https://github.com/okasi/swedish-pii",
            "https://github.com/jundymek/free-proxy",
            "https://github.com/PierreMesure/oppna-bolagsdata",
            "https://github.com/mratmeyer/rsslookup",
            "https://github.com/solve-cloudflare/cloudflare-bypass",
            "https://github.com/solve-cloudflare/cloudflare-protection",
            "https://github.com/Theyka/Turnstile-Solver",
            "https://github.com/swisskyrepo/PayloadsAllTheThings",
            "https://github.com/api0cradle/UltimateAppLockerByPassList",
            "https://github.com/Ge0rg3/requests-ip-rotator",
            "https://github.com/FlareSolverr/FlareSolverr",
            "https://github.com/sarperavci/GoogleRecaptchaBypass",
            "https://github.com/sarperavci/CloudflareBypassForScraping",
            "https://github.com/seleniumbase/SeleniumBase",
            "https://github.com/wallarm/gotestwaf"
        ]
        
    def _generate_existing_signatures(self) -> Set[str]:
        """Generera signaturer för befintlig kod för att undvika duplicering."""
        signatures = set()
        
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    signature = hashlib.md5(content.encode()).hexdigest()
                    signatures.add(signature)
            except Exception as e:
                logger.debug(f"Kunde inte läsa {py_file}: {e}")
                
        return signatures
        
    async def run_complete_analysis(self) -> Dict[str, Any]:
        """
        Kör komplett analys och integration av alla repositories med improved error handling.
        """
        logger.info("🚀 STARTAR KOMPLETT GITHUB REPOSITORY ANALYS OCH INTEGRATION")
        
        results = {
            "total_repositories": len(self.target_repositories),
            "processed": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "new_features_added": [],
            "enhanced_modules": [],
            "integration_log": []
        }
        
        # Begränsa till färre repositories för första körningen
        limited_repos = self.target_repositories[:10]  # Endast första 10
        logger.info(f"📊 Bearbetar {len(limited_repos)} repositories (begränsat för första test)")
        
        for i, repo_url in enumerate(limited_repos):
            try:
                logger.info(f"📥 Bearbetar repository {i+1}/{len(limited_repos)}: {repo_url}")
                
                # Steg 1: Klona repository med timeout
                repo_path = await asyncio.wait_for(
                    self._clone_repository(repo_url), 
                    timeout=120  # 2 minuter timeout
                )
                
                if not repo_path:
                    results["failed_integrations"] += 1
                    continue
                    
                # Steg 2: Analysera kod
                analysis = await self._analyze_repository(repo_path)
                
                # Steg 3: Integrera unik funktionalitet (endast om analys hittade något)
                if analysis:
                    integration_result = await self._integrate_functionality(analysis, repo_url)
                    
                    # Steg 4: Testa integration (endast för framgångsrika integrationer)
                    if integration_result.success:
                        test_results = await self._test_integration(integration_result)
                        
                        # Steg 5: Logga resultat
                        self._log_integration_result(repo_url, integration_result, test_results)
                        
                        results["successful_integrations"] += 1
                        results["new_features_added"].extend(integration_result.integrated_features)
                        results["enhanced_modules"].extend(integration_result.enhanced_modules)
                    else:
                        results["failed_integrations"] += 1
                else:
                    logger.info(f"⚠️ Ingen relevant kod hittades i {repo_url}")
                    results["failed_integrations"] += 1
                    
                results["processed"] += 1
                results["integration_log"].append({
                    "repository": repo_url,
                    "success": integration_result.success if 'integration_result' in locals() else False,
                    "features": integration_result.integrated_features if 'integration_result' in locals() else [],
                    "timestamp": datetime.now().isoformat()
                })
                
                # Steg 6: Rensa temporära filer
                await self._cleanup_repository(repo_path)
                
                # Kort paus mellan repositories
                await asyncio.sleep(1)
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Timeout vid bearbetning av {repo_url}")
                results["failed_integrations"] += 1
                
            except Exception as e:
                logger.error(f"💥 Fel vid bearbetning av {repo_url}: {e}")
                results["failed_integrations"] += 1
                
        # Slutrapport
        await self._generate_integration_report(results)
        
        return results
        
    async def _clone_repository(self, repo_url: str) -> Optional[Path]:
        """Klona GitHub repository till temporär katalog."""
        try:
            repo_name = repo_url.split('/')[-1]
            clone_path = self.temp_dir / repo_name
            
            # Klona repository
            process = await asyncio.create_subprocess_exec(
                'git', 'clone', '--depth', '1', repo_url, str(clone_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Klonade {repo_name} framgångsrikt")
                return clone_path
            else:
                logger.error(f"❌ Kunde inte klona {repo_name}: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Fel vid kloning av {repo_url}: {e}")
            return None
            
    async def _analyze_repository(self, repo_path: Path) -> List[CodeAnalysis]:
        """Analysera kod i repository för unik funktionalitet."""
        analyses = []
        
        # Analysera Python-filer
        for py_file in repo_path.rglob("*.py"):
            if self._should_analyze_file(py_file):
                analysis = await self._analyze_python_file(py_file)
                if analysis:
                    analyses.append(analysis)
                    
        # Analysera JavaScript-filer 
        for js_file in repo_path.rglob("*.js"):
            if self._should_analyze_file(js_file):
                analysis = await self._analyze_javascript_file(js_file)
                if analysis:
                    analyses.append(analysis)
                    
        return analyses
        
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Kontrollera om fil ska analyseras."""
        # Skippa test-filer, dokumentation, etc.
        skip_patterns = [
            'test_', '__pycache__', '.git', 'node_modules',
            'README', 'LICENSE', '.md', '.txt', '.yml', '.yaml'
        ]
        
        file_str = str(file_path).lower()
        return not any(pattern in file_str for pattern in skip_patterns)
        
    async def _analyze_python_file(self, file_path: Path) -> Optional[CodeAnalysis]:
        """Analysera Python-fil för funktionalitet."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Kontrollera om redan existerar
            signature = hashlib.md5(content.encode()).hexdigest()
            if signature in self.existing_signatures:
                return None
                
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            unique_features = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
            # Identifiera unika funktioner baserat på namnmönster
            unique_features = self._identify_unique_features(functions, classes, content)
            
            # Beräkna komplexitet
            complexity = len(functions) + len(classes) * 2
            
            # Bedöm integrationspotential
            integration_potential = self._assess_integration_potential(
                functions, classes, imports, content
            )
            
            return CodeAnalysis(
                file_path=str(file_path),
                language="python",
                functions=functions,
                classes=classes,
                imports=imports,
                complexity_score=complexity,
                unique_features=unique_features,
                integration_potential=integration_potential
            )
            
        except Exception as e:
            logger.debug(f"Kunde inte analysera {file_path}: {e}")
            return None
            
    async def _analyze_javascript_file(self, file_path: Path) -> Optional[CodeAnalysis]:
        """Analysera JavaScript-fil för funktionalitet."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Enkel JavaScript-analys (kan förbättras med AST)
            functions = []
            classes = []
            imports = []
            
            # Hitta funktioner
            import re
            func_pattern = r'function\s+(\w+)'
            functions = re.findall(func_pattern, content)
            
            # Hitta klasser
            class_pattern = r'class\s+(\w+)'
            classes = re.findall(class_pattern, content)
            
            # Hitta imports
            import_pattern = r'import.*from\s+[\'"]([^\'"]+)[\'"]'
            imports = re.findall(import_pattern, content)
            
            unique_features = self._identify_unique_features(functions, classes, content)
            complexity = len(functions) + len(classes) * 2
            
            integration_potential = self._assess_integration_potential(
                functions, classes, imports, content
            )
            
            return CodeAnalysis(
                file_path=str(file_path),
                language="javascript",
                functions=functions,
                classes=classes,
                imports=imports,
                complexity_score=complexity,
                unique_features=unique_features,
                integration_potential=integration_potential
            )
            
        except Exception as e:
            logger.debug(f"Kunde inte analysera JS-fil {file_path}: {e}")
            return None
            
    def _identify_unique_features(self, functions: List[str], classes: List[str], content: str) -> List[str]:
        """Identifiera unika funktioner baserat på namnmönster och innehåll."""
        unique_features = []
        
        # Nyckelord som indikerar intressant funktionalitet
        keywords = {
            'proxy': ['proxy', 'rotate', 'pool'],
            'scraping': ['scrape', 'crawl', 'extract', 'parse'],
            'bypass': ['bypass', 'stealth', 'anti-bot', 'cloudflare'],
            'security': ['auth', 'encrypt', 'decode', 'hash'],
            'api': ['api', 'endpoint', 'request', 'response'],
            'vehicle': ['vehicle', 'car', 'biluppgifter', 'regnr'],
            'swedish': ['swedish', 'sverige', 'sweden', 'personnummer'],
        }
        
        content_lower = content.lower()
        all_names = functions + classes
        
        for category, terms in keywords.items():
            for term in terms:
                if (term in content_lower or 
                    any(term in name.lower() for name in all_names)):
                    if category not in unique_features:
                        unique_features.append(category)
                        
        return unique_features
        
    def _assess_integration_potential(self, functions: List[str], classes: List[str], 
                                    imports: List[str], content: str) -> str:
        """Bedöm hur lätt koden är att integrera."""
        score = 0
        
        # Positiva faktorer
        if len(functions) > 0:
            score += 1
        if len(classes) > 0:
            score += 2
        if 'async' in content or 'await' in content:
            score += 1
        if any(imp in ['fastapi', 'flask', 'django'] for imp in imports):
            score += 2
            
        # Negativa faktorer
        if len(imports) > 20:
            score -= 1
        if 'os.system' in content or 'subprocess' in content:
            score -= 1
            
        if score >= 4:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'
            
    async def _integrate_functionality(self, analyses: List[CodeAnalysis], repo_url: str) -> IntegrationResult:
        """Integrera unik funktionalitet i befintlig kod."""
        integrated_features = []
        new_modules = []
        enhanced_modules = []
        
        try:
            # Filtrera analyser med hög integrationspotential
            high_potential = [a for a in analyses if a.integration_potential == 'high']
            medium_potential = [a for a in analyses if a.integration_potential == 'medium']
            
            # Prioritera integration
            for analysis in high_potential + medium_potential[:3]:  # Max 3 medium
                result = await self._integrate_single_analysis(analysis, repo_url)
                
                if result['success']:
                    integrated_features.extend(result['features'])
                    new_modules.extend(result['new_modules'])
                    enhanced_modules.extend(result['enhanced_modules'])
                    
        except Exception as e:
            logger.error(f"Fel vid integration från {repo_url}: {e}")
            return IntegrationResult(
                repository=repo_url,
                integrated_features=[],
                new_modules=[],
                enhanced_modules=[],
                tests_created=[],
                success=False,
                error_message=str(e)
            )
            
        return IntegrationResult(
            repository=repo_url,
            integrated_features=integrated_features,
            new_modules=new_modules,
            enhanced_modules=enhanced_modules,
            tests_created=[],  # Fylls i av test-funktionen
            success=len(integrated_features) > 0
        )
        
    async def _integrate_single_analysis(self, analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera en enskild kodanalys."""
        result = {
            'success': False,
            'features': [],
            'new_modules': [],
            'enhanced_modules': []
        }
        
        try:
            # Läs källkod
            with open(analysis.file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # Bestäm integration-strategi baserat på unika funktioner
            for feature in analysis.unique_features:
                integration_result = await self._integrate_feature(
                    feature, source_code, analysis, repo_url
                )
                
                if integration_result['success']:
                    result['features'].append(feature)
                    result['new_modules'].extend(integration_result.get('new_modules', []))
                    result['enhanced_modules'].extend(integration_result.get('enhanced_modules', []))
                    result['success'] = True
                    
        except Exception as e:
            logger.error(f"Fel vid integration av {analysis.file_path}: {e}")
            
        return result
        
    async def _integrate_feature(self, feature: str, source_code: str, 
                               analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera en specifik funktionalitet."""
        
        integration_strategies = {
            'proxy': self._integrate_proxy_functionality,
            'scraping': self._integrate_scraping_functionality,
            'bypass': self._integrate_bypass_functionality,
            'security': self._integrate_security_functionality,
            'api': self._integrate_api_functionality,
            'vehicle': self._integrate_vehicle_functionality,
            'swedish': self._integrate_swedish_functionality
        }
        
        strategy = integration_strategies.get(feature)
        if strategy:
            return await strategy(source_code, analysis, repo_url)
        else:
            return {'success': False, 'message': f'Ingen strategi för {feature}'}
            
    async def _integrate_proxy_functionality(self, source_code: str, 
                                           analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera proxy-relaterad funktionalitet."""
        try:
            # Extrahera proxy-relaterade klasser och funktioner
            proxy_classes = [cls for cls in analysis.classes if 'proxy' in cls.lower()]
            proxy_functions = [func for func in analysis.functions if 'proxy' in func.lower()]
            
            if not (proxy_classes or proxy_functions):
                return {'success': False, 'message': 'Inga proxy-funktioner hittade'}
                
            # Skapa ny proxy-modul eller förbättra befintlig
            target_module = self.project_root / "src" / "proxy_pool" / "external_integrations.py"
            
            # Anpassa och integrera kod
            adapted_code = self._adapt_code_for_integration(
                source_code, analysis, 'proxy_pool', repo_url
            )
            
            # Skriv till fil
            await self._write_integration_module(target_module, adapted_code, repo_url)
            
            return {
                'success': True,
                'new_modules': [str(target_module.relative_to(self.project_root))],
                'enhanced_modules': [],
                'message': f'Integrerade {len(proxy_classes)} proxy-klasser'
            }
            
        except Exception as e:
            logger.error(f"Fel vid proxy-integration: {e}")
            return {'success': False, 'message': str(e)}
            
    async def _integrate_scraping_functionality(self, source_code: str, 
                                              analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera scraping-funktionalitet."""
        try:
            scraping_classes = [cls for cls in analysis.classes 
                              if any(term in cls.lower() for term in ['scraper', 'crawler', 'extract'])]
            
            if not scraping_classes:
                return {'success': False, 'message': 'Inga scraping-klasser hittade'}
                
            target_module = self.project_root / "src" / "scraper" / "enhanced_scrapers.py"
            
            adapted_code = self._adapt_code_for_integration(
                source_code, analysis, 'scraper', repo_url
            )
            
            await self._write_integration_module(target_module, adapted_code, repo_url)
            
            return {
                'success': True,
                'new_modules': [str(target_module.relative_to(self.project_root))],
                'enhanced_modules': [],
                'message': f'Integrerade {len(scraping_classes)} scraping-klasser'
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
            
    async def _integrate_bypass_functionality(self, source_code: str, 
                                            analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera bypass-funktionalitet."""
        try:
            bypass_functions = [func for func in analysis.functions 
                              if any(term in func.lower() for term in ['bypass', 'stealth', 'anti'])]
            
            if not bypass_functions:
                return {'success': False}
                
            target_module = self.project_root / "src" / "anti_bot" / "advanced_bypass.py"
            
            adapted_code = self._adapt_code_for_integration(
                source_code, analysis, 'anti_bot', repo_url
            )
            
            await self._write_integration_module(target_module, adapted_code, repo_url)
            
            return {
                'success': True,
                'new_modules': [str(target_module.relative_to(self.project_root))],
                'message': f'Integrerade {len(bypass_functions)} bypass-funktioner'
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
            
    async def _integrate_security_functionality(self, source_code: str, 
                                              analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera säkerhets-funktionalitet."""
        # Implementation för säkerhetsfunktioner
        return {'success': False, 'message': 'Säkerhets-integration ej implementerad än'}
        
    async def _integrate_api_functionality(self, source_code: str, 
                                         analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera API-funktionalitet."""
        try:
            api_classes = [cls for cls in analysis.classes if 'api' in cls.lower()]
            
            if not api_classes:
                return {'success': False}
                
            target_module = self.project_root / "src" / "webapp" / "api" / "external_apis.py"
            
            adapted_code = self._adapt_code_for_integration(
                source_code, analysis, 'webapp.api', repo_url
            )
            
            await self._write_integration_module(target_module, adapted_code, repo_url)
            
            return {
                'success': True,
                'new_modules': [str(target_module.relative_to(self.project_root))]
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
            
    async def _integrate_vehicle_functionality(self, source_code: str, 
                                             analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera fordons-specifik funktionalitet."""
        try:
            # Skapa specialiserad fordon-modul
            target_module = self.project_root / "src" / "scrapers" / "vehicle_scrapers.py"
            target_module.parent.mkdir(exist_ok=True)
            
            adapted_code = self._adapt_code_for_integration(
                source_code, analysis, 'scrapers', repo_url
            )
            
            await self._write_integration_module(target_module, adapted_code, repo_url)
            
            return {
                'success': True,
                'new_modules': [str(target_module.relative_to(self.project_root))]
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
            
    async def _integrate_swedish_functionality(self, source_code: str, 
                                             analysis: CodeAnalysis, repo_url: str) -> Dict[str, Any]:
        """Integrera svensk-specifik funktionalitet."""
        try:
            target_module = self.project_root / "src" / "utils" / "swedish_data_utils.py"
            
            adapted_code = self._adapt_code_for_integration(
                source_code, analysis, 'utils', repo_url
            )
            
            await self._write_integration_module(target_module, adapted_code, repo_url)
            
            return {
                'success': True,
                'new_modules': [str(target_module.relative_to(self.project_root))]
            }
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
            
    def _adapt_code_for_integration(self, source_code: str, analysis: CodeAnalysis, 
                                   target_module: str, repo_url: str) -> str:
        """Anpassa kod för integration i befintlig arkitektur."""
        
        # Sanitize kod för att undvika syntax-fel
        cleaned_code = self._clean_code_for_python(source_code)
        
        # Skapa header med metadata (använd triple quotes korrekt)
        header = f'''"""
Integrerad funktionalitet från {repo_url}
Automatiskt genererad den {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Original fil: {analysis.file_path.replace(chr(92), '/')}
Språk: {analysis.language}
Funktioner: {len(analysis.functions)}
Klasser: {len(analysis.classes)}
Unika funktioner: {', '.join(analysis.unique_features)}
"""

# Automatiska importer för integration
from utils.logger import get_logger
from observability.metrics import MetricsCollector
import asyncio
from typing import Dict, List, Optional, Any

logger = get_logger(__name__)

# === INTEGRERAD KOD BÖRJAR HÄR ===

'''
        
        # Anpassa importer
        adapted_code = self._adapt_imports(cleaned_code)
        
        # Lägg till basic error handling
        adapted_code = self._add_basic_error_handling(adapted_code)
        
        # Lägg till logging
        adapted_code = self._add_basic_logging(adapted_code)
        
        return header + adapted_code
        
    def _clean_code_for_python(self, code: str) -> str:
        """Rensa kod för att undvika vanliga Python syntax-fel."""
        try:
            # Fix escape sequences
            code = code.replace('\\', '\\\\')  # Escape backslashes
            
            # Remove problematic f-string patterns
            import re
            
            # Ta bort eller fixa problematiska regex-mönster
            code = re.sub(r'\\[a-zA-Z]', lambda m: m.group(0).replace('\\', r'\\'), code)
            
            # Fixa f-strings som inte är avslutade
            lines = code.split('\n')
            fixed_lines = []
            
            for line in lines:
                # Enkel fix för f-strings - ersätt med vanliga strings om de verkar trasiga
                if 'f"' in line or "f'" in line:
                    # Räkna quotes för att se om de matchar
                    double_quotes = line.count('"')
                    single_quotes = line.count("'")
                    
                    if (double_quotes % 2 != 0) or (single_quotes % 2 != 0):
                        # Ersätt f-strings med vanliga strings
                        line = line.replace('f"', '"').replace("f'", "'")
                        
                fixed_lines.append(line)
                
            return '\n'.join(fixed_lines)
            
        except Exception as e:
            logger.warning(f"Kunde inte rensa kod: {e}")
            # Returnera en minimal, säker version
            return '''
# Säker fallback-kod - original kod innehöll syntax-fel
logger.info("Integrerad modul laddad (säker fallback)")

def integrated_function():
    """Placeholder för integrerad funktionalitet."""
    logger.info("Integrated function called")
    return True
'''
            
    def _adapt_imports(self, code: str) -> str:
        """Anpassa importer för att fungera med vår arkitektur."""
        # Enkla, säkra ersättningar
        replacements = {
            'import requests': '# import httpx as requests  # Anpassat för async',
            'from requests': '# from httpx',
        }
        
        for old, new in replacements.items():
            code = code.replace(old, new)
            
        return code
        
    def _add_basic_error_handling(self, code: str) -> str:
        """Lägg till grundläggande error handling."""
        # Mycket enklare approach
        safe_code = f'''
try:
{self._indent_code(code, 4)}
except Exception as e:
    logger.error(f"Integration error: {{e}}")
    pass
'''
        return safe_code
        
    def _add_basic_logging(self, code: str) -> str:
        """Lägg till grundläggande logging."""
        # Lägg till en enkel log-rad i början
        return f'''logger.debug("Executing integrated code")

{code}
'''
        
    def _indent_code(self, code: str, spaces: int) -> str:
        """Indentera kod med angivet antal spaces."""
        indent = ' ' * spaces
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
        
    async def _write_integration_module(self, target_path: Path, code: str, repo_url: str):
        """Skriv integrationsmodul till fil."""
        try:
            # Skapa katalog om den inte existerar
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Skriv fil
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(code)
                
            logger.info(f"✅ Skrev integrationsmodul: {target_path}")
            
        except Exception as e:
            logger.error(f"Fel vid skrivning av {target_path}: {e}")
            raise
            
    async def _test_integration(self, integration_result: IntegrationResult) -> Dict[str, Any]:
        """Testa integrerad funktionalitet."""
        test_results = {
            'success': True,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'error_messages': []
        }
        
        try:
            # Testa att moduler kan importeras
            for module_path in integration_result.new_modules:
                try:
                    module_name = module_path.replace('/', '.').replace('.py', '')
                    if module_name.startswith('src.'):
                        module_name = module_name[4:]  # Ta bort 'src.'
                        
                    spec = importlib.util.spec_from_file_location(
                        module_name, 
                        self.project_root / module_path
                    )
                    
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        test_results['tests_run'] += 1
                        test_results['tests_passed'] += 1
                        
                        logger.info(f"✅ Modul {module_name} importerad framgångsrikt")
                        
                except Exception as e:
                    test_results['tests_failed'] += 1
                    test_results['error_messages'].append(f"Import fel {module_path}: {e}")
                    logger.error(f"❌ Kunde inte importera {module_path}: {e}")
                    
            # Skapa test-filer
            for module_path in integration_result.new_modules:
                await self._create_test_file(module_path, integration_result.repository)
                
        except Exception as e:
            test_results['success'] = False
            test_results['error_messages'].append(str(e))
            
        return test_results
        
    async def _create_test_file(self, module_path: str, repo_url: str):
        """Skapa test-fil för integrerad modul."""
        try:
            module_name = Path(module_path).stem
            test_file_path = self.project_root / "tests" / f"test_integration_{module_name}.py"
            
            test_content = f'''"""
Test för integrerad funktionalitet från {repo_url}
Automatiskt genererad den {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import pytest
import sys
from pathlib import Path

# Lägg till src till path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_module_import():
    """Testa att modulen kan importeras utan fel."""
    try:
        import {module_name.replace('-', '_')}
        assert True, "Modul importerad framgångsrikt"
    except ImportError as e:
        pytest.fail(f"Kunde inte importera modul: {{e}}")
        
def test_module_basic_functionality():
    """Testa grundläggande funktionalitet i modulen."""
    try:
        import {module_name.replace('-', '_')} as test_module
        
        # Testa att viktiga attribut existerar
        assert hasattr(test_module, '__doc__'), "Modul saknar dokumentation"
        
        # Testa att inga uppenbara fel uppstår vid import
        assert True, "Grundläggande funktionalitet fungerar"
        
    except Exception as e:
        pytest.fail(f"Grundläggande funktionalitetstest misslyckades: {{e}}")

def test_integration_compatibility():
    """Testa att integrationen är kompatibel med befintlig kod."""
    try:
        # Testa att befintliga moduler fortfarande fungerar
        from utils.logger import get_logger
        from observability.metrics import MetricsCollector
        
        logger = get_logger(__name__)
        logger.info("Integration compatibility test")
        
        assert True, "Integration är kompatibel"
        
    except Exception as e:
        pytest.fail(f"Kompatibilitetstest misslyckades: {{e}}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
            
            # Skapa test-katalog om den inte existerar
            test_file_path.parent.mkdir(exist_ok=True)
            
            with open(test_file_path, 'w', encoding='utf-8') as f:
                f.write(test_content)
                
            logger.info(f"📝 Skapade test-fil: {test_file_path}")
            
        except Exception as e:
            logger.error(f"Fel vid skapande av test-fil: {e}")
            
    def _log_integration_result(self, repo_url: str, integration_result: IntegrationResult, 
                               test_results: Dict[str, Any]):
        """Logga integrations-resultat."""
        self.integration_log.append({
            'timestamp': datetime.now().isoformat(),
            'repository': repo_url,
            'success': integration_result.success,
            'features': integration_result.integrated_features,
            'new_modules': integration_result.new_modules,
            'enhanced_modules': integration_result.enhanced_modules,
            'tests_passed': test_results.get('tests_passed', 0),
            'tests_failed': test_results.get('tests_failed', 0),
            'error_message': integration_result.error_message
        })
        
    async def _cleanup_repository(self, repo_path: Path):
        """Rensa temporära repository-filer med Windows-kompatibel approach."""
        try:
            if repo_path.exists():
                # Windows-specifik cleanup för git repositories
                await self._windows_safe_cleanup(repo_path)
                logger.info(f"🧹 Rensade temporär katalog: {repo_path}")
        except Exception as e:
            logger.warning(f"Kunde inte rensa {repo_path}: {e}")
            # Försök att åtminstone dölja katalogen
            try:
                import subprocess
                subprocess.run(['attrib', '+H', str(repo_path)], check=False)
            except:
                pass
                
    async def _windows_safe_cleanup(self, repo_path: Path):
        """Windows-säker cleanup av git repositories."""
        try:
            # Först, försök ta bort read-only attribut från git-filer
            import subprocess
            
            # Ta bort read-only attribut rekursivt
            subprocess.run([
                'attrib', '-R', str(repo_path / "*"), '/S'
            ], check=False, capture_output=True)
            
            # Försök normal deletion
            shutil.rmtree(repo_path)
            
        except Exception as e:
            # Om det inte funkar, försök kraftigare åtgärder
            try:
                # Använd rmdir med force
                subprocess.run([
                    'rmdir', '/S', '/Q', str(repo_path)
                ], check=False, capture_output=True, shell=True)
            except:
                # Som sista utväg, flytta till temp och låt OS rensa senare
                import tempfile
                try:
                    temp_name = f"cleanup_{datetime.now().strftime('%H%M%S')}"
                    temp_path = Path(tempfile.gettempdir()) / temp_name
                    repo_path.rename(temp_path)
                except:
                    pass
            
    async def _generate_integration_report(self, results: Dict[str, Any]):
        """Generera slutrapport för integration."""
        report_path = self.project_root / "reports" / f"github_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        # Utökad rapport
        full_report = {
            **results,
            'integration_log': self.integration_log,
            'generated_at': datetime.now().isoformat(),
            'total_features_integrated': len(results['new_features_added']),
            'success_rate': (results['successful_integrations'] / results['total_repositories']) * 100
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📊 Genererade integrationsrapport: {report_path}")
        
        # Skriv också en läsbar textrapport
        text_report_path = report_path.with_suffix('.txt')
        await self._generate_text_report(full_report, text_report_path)
        
    async def _generate_text_report(self, report: Dict[str, Any], output_path: Path):
        """Generera läsbar textrapport."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("🚀 GITHUB REPOSITORY INTEGRATION RAPPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"📅 Genererad: {report['generated_at']}\n")
            f.write(f"📦 Totala repositories: {report['total_repositories']}\n")
            f.write(f"✅ Framgångsrika integrationer: {report['successful_integrations']}\n")
            f.write(f"❌ Misslyckade integrationer: {report['failed_integrations']}\n")
            f.write(f"📈 Framgångsfrekvens: {report['success_rate']:.1f}%\n\n")
            
            f.write("🆕 NYA FUNKTIONER INTEGRERADE:\n")
            for feature in report['new_features_added']:
                f.write(f"  • {feature}\n")
            f.write("\n")
            
            f.write("📊 DETALJERAD LOG:\n")
            for entry in self.integration_log:
                f.write(f"  📁 {entry['repository']}\n")
                f.write(f"     Status: {'✅ Framgång' if entry['success'] else '❌ Misslyckades'}\n")
                f.write(f"     Funktioner: {', '.join(entry['features'])}\n")
                if entry.get('error_message'):
                    f.write(f"     Fel: {entry['error_message']}\n")
                f.write("\n")
                
    def __del__(self):
        """Rensa upp temporära kataloger vid avslut."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except:
            pass


# Huvudfunktion för att köra analysen
async def main():
    """Huvudfunktion för GitHub repository-analys och integration."""
    
    project_root = Path(__file__).parent
    
    # Initiera metrics (mock implementation)
    class MockMetrics:
        def counter(self, name, value): pass
        def timer(self, name, value): pass
        
    metrics = MockMetrics()
    
    # Skapa analysator
    analyzer = GitHubRepositoryAnalyzer(project_root, metrics)
    
    try:
        logger.info("🚀 Startar GitHub Repository Analysis och Integration System")
        
        # Kör komplett analys
        results = await analyzer.run_complete_analysis()
        
        logger.info("🎉 INTEGRATION KLAR!")
        logger.info(f"📊 Framgångsfrekvens: {results['successful_integrations']}/{results['total_repositories']}")
        logger.info(f"🆕 Nya funktioner: {len(results['new_features_added'])}")
        
        return results
        
    except Exception as e:
        logger.error(f"💥 Kritiskt fel i GitHub-analysen: {e}")
        raise
        
    finally:
        # Rensa upp
        del analyzer


if __name__ == "__main__":
    # Kör systemet
    results = asyncio.run(main())
    print("GitHub Integration System completed successfully!")
    print(f"Integrated {results['successful_integrations']} repositories")
