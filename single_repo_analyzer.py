#!/usr/bin/env python3
"""
Single Repository Deep Analysis System
=====================================

Manuell, djupgående analys av en GitHub repository i taget.
Fokuserar på att förstå hur funktionalitet implementeras för
att sedan manuellt implementera den bästa koden.

Workflow:
1. Välj en repository
2. Djupanalysera koden
3. Extrahera nyckelfunktionalitet
4. Skapa implementationsplan
5. Manuell kodning baserat på analysen
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
import ast
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SingleRepositoryAnalyzer:
    """
    Djupanalyserar en GitHub repository för manuell implementation.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.temp_dir = Path(tempfile.mkdtemp(prefix="single_repo_analysis_"))
        
        # Prioriterade repositories för analys
        self.priority_repositories = [
            {
                "url": "https://github.com/jhao104/proxy_pool",
                "focus": "Proxy pool management architecture", 
                "why": "Välstrukturat proxy pool system med scheduler och validator"
            },
            {
                "url": "https://github.com/Ge0rg3/requests-ip-rotator",
                "focus": "IP rotation för requests",
                "why": "Enkel, elegant IP rotation med AWS integration"
            },
            {
                "url": "https://github.com/constverum/ProxyBroker", 
                "focus": "Avancerad proxy broker",
                "why": "Sofistikerad async proxy management"
            },
            {
                "url": "https://github.com/markgacoka/selenium-proxy-rotator",
                "focus": "Selenium proxy rotation",
                "why": "Specifikt för WebDriver proxy switching"
            },
            {
                "url": "https://github.com/FlareSolverr/FlareSolverr",
                "focus": "Cloudflare bypass",
                "why": "Professionell anti-detection service"
            }
        ]
        
    async def analyze_single_repository(self, repo_index: int = 0) -> Dict[str, Any]:
        """
        Analysera en specifik repository djupt.
        """
        if repo_index >= len(self.priority_repositories):
            logger.error(f"Repository index {repo_index} utanför range (0-{len(self.priority_repositories)-1})")
            return {}
            
        repo_info = self.priority_repositories[repo_index]
        repo_url = repo_info["url"]
        
        logger.info(f"🔍 DJUPANALYSERAR: {repo_url}")
        logger.info(f"🎯 Fokus: {repo_info['focus']}")
        logger.info(f"💡 Varför: {repo_info['why']}")
        
        analysis = {
            "repository": repo_info,
            "clone_success": False,
            "structure_analysis": {},
            "code_analysis": {},
            "key_files": [],
            "implementation_insights": [],
            "manual_implementation_plan": {},
            "code_examples": []
        }
        
        try:
            # Steg 1: Klona repository
            repo_path = await self._clone_repository(repo_url)
            if not repo_path:
                return analysis
                
            analysis["clone_success"] = True
            
            # Steg 2: Analysera projektstruktur
            analysis["structure_analysis"] = await self._analyze_project_structure(repo_path)
            
            # Steg 3: Djupanalys av nyckelfiler
            analysis["code_analysis"] = await self._deep_code_analysis(repo_path)
            
            # Steg 4: Identifiera nyckelfiler
            analysis["key_files"] = await self._identify_key_files(repo_path)
            
            # Steg 5: Extrahera implementationsinsikter
            analysis["implementation_insights"] = await self._extract_implementation_insights(repo_path)
            
            # Steg 6: Skapa implementationsplan
            analysis["manual_implementation_plan"] = self._create_implementation_plan(analysis)
            
            # Steg 7: Extrahera kodexempel
            analysis["code_examples"] = await self._extract_code_examples(repo_path)
            
            # Spara analys
            await self._save_deep_analysis(analysis, repo_index)
            
            # Cleanup
            await self._cleanup_repository(repo_path)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Fel vid analys av {repo_url}: {e}")
            return analysis
            
    async def _clone_repository(self, repo_url: str) -> Optional[Path]:
        """Klona repository för analys."""
        try:
            repo_name = repo_url.split('/')[-1]
            clone_path = self.temp_dir / repo_name
            
            logger.info(f"📥 Klonar {repo_name}...")
            
            process = await asyncio.create_subprocess_exec(
                'git', 'clone', repo_url, str(clone_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ Klonade {repo_name}")
                return clone_path
            else:
                logger.error(f"❌ Kunde inte klona {repo_name}: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Kloning misslyckades: {e}")
            return None
            
    async def _analyze_project_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Analysera projektets struktur och organisation."""
        
        structure = {
            "total_files": 0,
            "python_files": 0,
            "javascript_files": 0,
            "config_files": [],
            "documentation": [],
            "directory_structure": {},
            "main_modules": [],
            "test_files": [],
            "setup_files": []
        }
        
        try:
            # Räkna filer per typ
            all_files = list(repo_path.rglob("*"))
            structure["total_files"] = len([f for f in all_files if f.is_file()])
            
            python_files = list(repo_path.rglob("*.py"))
            structure["python_files"] = len(python_files)
            
            js_files = list(repo_path.rglob("*.js"))
            structure["javascript_files"] = len(js_files)
            
            # Identifiera viktiga filer
            for file_path in all_files:
                if not file_path.is_file():
                    continue
                    
                file_name = file_path.name.lower()
                
                # Config files
                if file_name in ['config.py', 'settings.py', 'config.json', 'package.json', 
                               'requirements.txt', 'pyproject.toml', 'setup.py']:
                    structure["config_files"].append(str(file_path.relative_to(repo_path)))
                    
                # Documentation
                if file_name.startswith('readme') or file_name.endswith('.md'):
                    structure["documentation"].append(str(file_path.relative_to(repo_path)))
                    
                # Test files
                if 'test' in file_name or file_name.startswith('test_'):
                    structure["test_files"].append(str(file_path.relative_to(repo_path)))
                    
                # Setup files
                if file_name in ['setup.py', 'main.py', 'app.py', '__init__.py']:
                    structure["setup_files"].append(str(file_path.relative_to(repo_path)))
                    
            # Huvudmoduler (Python filer i root eller viktiga kataloger)
            for py_file in python_files:
                rel_path = py_file.relative_to(repo_path)
                if (len(rel_path.parts) <= 2 and 
                    py_file.name not in ['setup.py', '__init__.py'] and
                    'test' not in py_file.name.lower()):
                    structure["main_modules"].append(str(rel_path))
                    
            # Directory structure (första 2 nivåerna)
            for item in repo_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    structure["directory_structure"][item.name] = [
                        child.name for child in item.iterdir() 
                        if not child.name.startswith('.')
                    ][:10]  # Max 10 items per directory
                    
        except Exception as e:
            logger.error(f"Struktur-analys fel: {e}")
            
        return structure
        
    async def _deep_code_analysis(self, repo_path: Path) -> Dict[str, Any]:
        """Djup kodanalys för att förstå implementationen."""
        
        analysis = {
            "classes_found": [],
            "key_functions": [],
            "design_patterns": [],
            "dependencies": [],
            "async_usage": False,
            "database_usage": False,
            "api_endpoints": [],
            "configuration_patterns": [],
            "error_handling_patterns": [],
            "logging_patterns": []
        }
        
        try:
            python_files = list(repo_path.rglob("*.py"))[:20]  # Begränsa till 20 filer
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # AST analys
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            analysis["classes_found"].append({
                                "name": node.name,
                                "file": str(py_file.relative_to(repo_path)),
                                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)][:5]
                            })
                            
                        elif isinstance(node, ast.FunctionDef):
                            if not node.name.startswith('_'):  # Publika funktioner
                                analysis["key_functions"].append({
                                    "name": node.name,
                                    "file": str(py_file.relative_to(repo_path)),
                                    "args": len(node.args.args),
                                    "is_async": isinstance(node, ast.AsyncFunctionDef)
                                })
                                
                        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    analysis["dependencies"].append(alias.name)
                            else:
                                if node.module:
                                    analysis["dependencies"].append(node.module)
                                    
                    # Textanalys för mönster
                    content_lower = content.lower()
                    
                    if 'async ' in content or 'await ' in content:
                        analysis["async_usage"] = True
                        
                    if any(db in content_lower for db in ['sqlite', 'mysql', 'postgres', 'mongodb']):
                        analysis["database_usage"] = True
                        
                    # API endpoints
                    import re
                    api_patterns = re.findall(r'@app\.route\([\'"]([^\'"]+)', content)
                    analysis["api_endpoints"].extend(api_patterns)
                    
                    # Flask/FastAPI patterns
                    if '@app.route' in content or '@router.' in content:
                        analysis["design_patterns"].append("REST API")
                        
                    # Konfigurationsmönster
                    if 'config' in content_lower or 'settings' in content_lower:
                        analysis["configuration_patterns"].append(str(py_file.relative_to(repo_path)))
                        
                    # Error handling
                    if 'try:' in content and 'except' in content:
                        analysis["error_handling_patterns"].append(str(py_file.relative_to(repo_path)))
                        
                    # Logging
                    if any(log in content_lower for log in ['logging', 'logger', 'log.']):
                        analysis["logging_patterns"].append(str(py_file.relative_to(repo_path)))
                        
                except Exception as e:
                    logger.debug(f"Kunde inte analysera {py_file}: {e}")
                    continue
                    
            # Rensa duplicates
            analysis["dependencies"] = list(set(analysis["dependencies"]))[:20]
            analysis["design_patterns"] = list(set(analysis["design_patterns"]))
            
        except Exception as e:
            logger.error(f"Kod-analys fel: {e}")
            
        return analysis
        
    async def _identify_key_files(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Identifiera de viktigaste filerna för implementation."""
        
        key_files = []
        
        try:
            python_files = list(repo_path.rglob("*.py"))
            
            # Ranking baserat på filnamn och innehåll
            file_scores = []
            
            for py_file in python_files:
                score = 0
                file_name = py_file.name.lower()
                
                # Score baserat på filnamn
                if any(keyword in file_name for keyword in ['main', 'core', 'manager', 'pool', 'proxy']):
                    score += 10
                if any(keyword in file_name for keyword in ['api', 'server', 'client']):
                    score += 8
                if any(keyword in file_name for keyword in ['util', 'helper', 'config']):
                    score += 5
                if file_name.startswith('test_') or 'test' in file_name:
                    score -= 5
                    
                # Score baserat på filstorlek och komplexitet
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    lines = len(content.split('\n'))
                    classes = content.count('class ')
                    functions = content.count('def ')
                    
                    # Bonus för lagom komplexitet
                    if 50 <= lines <= 500:
                        score += 5
                    if classes >= 1:
                        score += classes * 3
                    if functions >= 2:
                        score += functions
                        
                    file_scores.append({
                        'file': py_file,
                        'score': score,
                        'lines': lines,
                        'classes': classes,
                        'functions': functions,
                        'content_preview': content[:200]
                    })
                    
                except Exception:
                    continue
                    
            # Sortera och ta top 10
            file_scores.sort(key=lambda x: x['score'], reverse=True)
            
            for file_info in file_scores[:10]:
                key_files.append({
                    'path': str(file_info['file'].relative_to(repo_path)),
                    'score': file_info['score'],
                    'lines': file_info['lines'],
                    'classes': file_info['classes'],
                    'functions': file_info['functions'],
                    'preview': file_info['content_preview'].replace('\n', ' ')[:150]
                })
                
        except Exception as e:
            logger.error(f"Key files analys fel: {e}")
            
        return key_files
        
    async def _extract_implementation_insights(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Extrahera konkreta implementationsinsikter."""
        
        insights = []
        
        try:
            # Läs README för övergripande insikter
            readme_files = list(repo_path.glob("README*"))
            if readme_files:
                try:
                    with open(readme_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                        readme_content = f.read()
                        
                    insights.append({
                        'type': 'documentation',
                        'title': 'README Insights',
                        'content': readme_content[:1000],
                        'importance': 'high'
                    })
                except Exception:
                    pass
                    
            # Analysera huvudfiler för implementation patterns
            main_files = ['main.py', 'app.py', 'server.py', '__init__.py']
            
            for main_file in main_files:
                file_path = repo_path / main_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        insights.append({
                            'type': 'main_code',
                            'title': f'{main_file} Implementation',
                            'content': content[:800],
                            'importance': 'high'
                        })
                    except Exception:
                        continue
                        
            # Konfigurationsfiler
            config_files = ['config.py', 'settings.py', 'config.json']
            
            for config_file in config_files:
                file_path = repo_path / config_file
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        insights.append({
                            'type': 'configuration',
                            'title': f'{config_file} Configuration',
                            'content': content[:500],
                            'importance': 'medium'
                        })
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.error(f"Implementation insights fel: {e}")
            
        return insights
        
    def _create_implementation_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Skapa en detaljerad implementationsplan baserat på analysen."""
        
        repo_info = analysis["repository"]
        structure = analysis["structure_analysis"]
        code_analysis = analysis["code_analysis"]
        
        plan = {
            'repository_focus': repo_info["focus"],
            'implementation_approach': self._determine_implementation_approach(analysis),
            'key_components_to_extract': self._identify_components_to_extract(analysis),
            'integration_points': self._identify_integration_points(analysis),
            'step_by_step_plan': self._create_step_by_step_plan(analysis),
            'potential_challenges': self._identify_challenges(analysis),
            'success_metrics': self._define_success_metrics(analysis)
        }
        
        return plan
        
    def _determine_implementation_approach(self, analysis: Dict[str, Any]) -> str:
        """Bestäm den bästa implementationsstrategin."""
        
        code_analysis = analysis["code_analysis"]
        
        if code_analysis.get("async_usage"):
            return "async_integration"
        elif len(code_analysis.get("classes_found", [])) > 5:
            return "class_based_architecture"
        elif code_analysis.get("api_endpoints"):
            return "api_service_integration"
        else:
            return "utility_functions"
            
    def _identify_components_to_extract(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifiera vilka komponenter som ska extraheras."""
        
        components = []
        classes = analysis["code_analysis"].get("classes_found", [])
        
        for cls in classes[:5]:  # Top 5 klasser
            components.append(f"Class: {cls['name']} - {cls['file']}")
            
        functions = analysis["code_analysis"].get("key_functions", [])
        for func in functions[:5]:  # Top 5 funktioner
            components.append(f"Function: {func['name']} - {func['file']}")
            
        return components
        
    def _identify_integration_points(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifiera integrationspunkter i vårt system."""
        
        focus = analysis["repository"]["focus"].lower()
        points = []
        
        if "proxy" in focus:
            points.extend([
                "src/proxy_pool/manager.py - Enhance ProxyPoolManager",
                "src/proxy_pool/validator.py - Add new validation methods",
                "src/proxy_pool/ - New rotation strategies"
            ])
        elif "selenium" in focus:
            points.extend([
                "src/scraper/webdriver_scraper.py - Add proxy rotation",
                "src/utils/ - New Selenium utilities"
            ])
        elif "bypass" in focus or "cloudflare" in focus:
            points.extend([
                "src/anti_bot/ - New bypass techniques",
                "src/scraper/ - Enhanced anti-detection"
            ])
            
        return points
        
    def _create_step_by_step_plan(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """Skapa steg-för-steg implementationsplan."""
        
        steps = [
            {
                "step": 1,
                "title": "Manuell kodgranskning",
                "description": "Granska nyckelfiler och förstå arkitekturen",
                "time_estimate": "1-2 timmar"
            },
            {
                "step": 2,
                "title": "Extrahera kärnfunktionalitet",
                "description": "Identifiera och extrahera de viktigaste funktionerna",
                "time_estimate": "2-3 timmar"
            },
            {
                "step": 3,
                "title": "Anpassa för vår arkitektur",
                "description": "Modifiera kod för att passa vårt system",
                "time_estimate": "2-4 timmar"
            },
            {
                "step": 4,
                "title": "Skapa tester",
                "description": "Utveckla omfattande tester",
                "time_estimate": "1-2 timmar"
            },
            {
                "step": 5,
                "title": "Integration och validering",
                "description": "Integrera med befintligt system",
                "time_estimate": "2-3 timmar"
            }
        ]
        
        return steps
        
    def _identify_challenges(self, analysis: Dict[str, Any]) -> List[str]:
        """Identifiera potentiella utmaningar."""
        
        challenges = []
        code_analysis = analysis["code_analysis"]
        
        if code_analysis.get("async_usage"):
            challenges.append("Async/await integration med befintlig sync kod")
            
        if len(code_analysis.get("dependencies", [])) > 10:
            challenges.append("Många externa beroenden att hantera")
            
        if code_analysis.get("database_usage"):
            challenges.append("Databasintegration och migration")
            
        challenges.append("Säkerställa kompatibilitet med befintlig kod")
        challenges.append("Prestanda-optimering efter integration")
        
        return challenges
        
    def _define_success_metrics(self, analysis: Dict[str, Any]) -> List[str]:
        """Definiera framgångsmått."""
        
        return [
            "All existing functionality works after integration",
            "New functionality performs as expected",
            "No memory leaks or performance degradation",
            "All tests pass",
            "Code coverage maintains current levels"
        ]
        
    async def _extract_code_examples(self, repo_path: Path) -> List[Dict[str, Any]]:
        """Extrahera konkreta kodexempel för implementationshhjälp."""
        
        examples = []
        
        try:
            key_files = ['main.py', 'app.py', 'manager.py', 'client.py', 'server.py']
            
            for file_name in key_files:
                for py_file in repo_path.rglob(file_name):
                    try:
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        # Extrahera klasser
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                class_start = node.lineno - 1
                                class_lines = content.split('\n')[class_start:class_start + 30]
                                
                                examples.append({
                                    'type': 'class',
                                    'name': node.name,
                                    'file': str(py_file.relative_to(repo_path)),
                                    'code': '\n'.join(class_lines)
                                })
                                
                            elif isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                                func_start = node.lineno - 1
                                func_lines = content.split('\n')[func_start:func_start + 20]
                                
                                examples.append({
                                    'type': 'function',
                                    'name': node.name,
                                    'file': str(py_file.relative_to(repo_path)),
                                    'code': '\n'.join(func_lines)
                                })
                                
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.error(f"Code examples fel: {e}")
            
        return examples[:10]  # Top 10 examples
        
    async def _save_deep_analysis(self, analysis: Dict[str, Any], repo_index: int):
        """Spara djupanalys till fil."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        repo_name = analysis["repository"]["url"].split('/')[-1]
        
        # JSON rapport
        json_file = self.project_root / "reports" / f"deep_analysis_{repo_name}_{timestamp}.json"
        json_file.parent.mkdir(exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            
        # Human-readable rapport
        txt_file = json_file.with_suffix('.txt')
        await self._generate_readable_analysis_report(analysis, txt_file)
        
        logger.info(f"📊 Djupanalys sparad: {json_file}")
        
    async def _generate_readable_analysis_report(self, analysis: Dict[str, Any], output_file: Path):
        """Generera läsbar analysrapport."""
        
        repo_info = analysis["repository"]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("🔍 DJUPANALYS RAPPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"📦 Repository: {repo_info['url']}\n")
            f.write(f"🎯 Fokus: {repo_info['focus']}\n")
            f.write(f"💡 Varför: {repo_info['why']}\n\n")
            
            # Struktur
            structure = analysis.get("structure_analysis", {})
            f.write("📁 PROJEKTSTRUKTUR:\n")
            f.write(f"  📄 Totala filer: {structure.get('total_files', 0)}\n")
            f.write(f"  🐍 Python filer: {structure.get('python_files', 0)}\n")
            f.write(f"  📋 Huvudmoduler: {len(structure.get('main_modules', []))}\n\n")
            
            # Kod-analys
            code_analysis = analysis.get("code_analysis", {})
            f.write("💻 KOD-ANALYS:\n")
            f.write(f"  🏗️  Klasser: {len(code_analysis.get('classes_found', []))}\n")
            f.write(f"  ⚡ Funktioner: {len(code_analysis.get('key_functions', []))}\n")
            f.write(f"  🔄 Async support: {'✅' if code_analysis.get('async_usage') else '❌'}\n")
            f.write(f"  🗄️  Databas: {'✅' if code_analysis.get('database_usage') else '❌'}\n\n")
            
            # Viktiga klasser
            f.write("🏗️  VIKTIGA KLASSER:\n")
            for cls in code_analysis.get('classes_found', [])[:5]:
                f.write(f"  • {cls['name']} ({cls['file']})\n")
                f.write(f"    Metoder: {', '.join(cls['methods'])}\n")
            f.write("\n")
            
            # Nyckelfiler
            f.write("📋 NYCKELFILER:\n")
            for key_file in analysis.get("key_files", [])[:5]:
                f.write(f"  📄 {key_file['path']} (Score: {key_file['score']})\n")
                f.write(f"     {key_file['lines']} linjer, {key_file['classes']} klasser\n")
            f.write("\n")
            
            # Implementationsplan
            plan = analysis.get("manual_implementation_plan", {})
            f.write("📋 IMPLEMENTATIONSPLAN:\n")
            f.write(f"  🎯 Approach: {plan.get('implementation_approach', 'N/A')}\n\n")
            
            # Steg-för-steg
            f.write("👣 IMPLEMENTATIONSSTEG:\n")
            for step in plan.get("step_by_step_plan", []):
                f.write(f"  {step['step']}. {step['title']}\n")
                f.write(f"     {step['description']}\n")
                f.write(f"     ⏱️  {step['time_estimate']}\n\n")
                
            # Utmaningar
            f.write("⚠️  UTMANINGAR:\n")
            for challenge in plan.get("potential_challenges", []):
                f.write(f"  • {challenge}\n")
            f.write("\n")
            
            # Kodexempel
            f.write("💡 KODEXEMPEL:\n")
            for example in analysis.get("code_examples", [])[:3]:
                f.write(f"\n📝 {example['type'].title()}: {example['name']}\n")
                f.write(f"📄 Fil: {example['file']}\n")
                f.write("```python\n")
                f.write(example['code'][:500])
                f.write("\n```\n")
                
    async def _cleanup_repository(self, repo_path: Path):
        """Rensa repository."""
        try:
            shutil.rmtree(repo_path)
        except Exception:
            pass
            
    def list_available_repositories(self):
        """Lista tillgängliga repositories för analys."""
        print("🔍 TILLGÄNGLIGA REPOSITORIES FÖR DJUPANALYS:")
        print("=" * 60)
        
        for i, repo in enumerate(self.priority_repositories):
            print(f"\n{i}. {repo['url']}")
            print(f"   🎯 Fokus: {repo['focus']}")
            print(f"   💡 Varför: {repo['why']}")
            
        print(f"\n📋 Använd: python {__file__} <index> för att analysera")
        print("   Exempel: python single_repo_analyzer.py 0")


async def main():
    """Huvudfunktion."""
    
    project_root = Path(__file__).parent
    analyzer = SingleRepositoryAnalyzer(project_root)
    
    if len(sys.argv) < 2:
        analyzer.list_available_repositories()
        return
        
    try:
        repo_index = int(sys.argv[1])
    except (ValueError, IndexError):
        print("❌ Ogiltigt repository index")
        analyzer.list_available_repositories()
        return
        
    print(f"🔍 STARTAR DJUPANALYS AV REPOSITORY {repo_index}")
    
    try:
        analysis = await analyzer.analyze_single_repository(repo_index)
        
        if analysis.get("clone_success"):
            print("✅ DJUPANALYS KLAR!")
            print(f"📊 Analyserade {len(analysis.get('key_files', []))} nyckelfiler")
            print(f"🏗️  Hittade {len(analysis.get('code_analysis', {}).get('classes_found', []))} klasser")
            print("📄 Kontrollera reports/ för detaljerad rapport")
        else:
            print("❌ Djupanalys misslyckades")
            
    except Exception as e:
        print(f"💥 Fel: {e}")
        

if __name__ == "__main__":
    asyncio.run(main())
