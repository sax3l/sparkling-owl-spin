#!/usr/bin/env python3
"""
GitHub Repository Analysis System - Safe Mode
============================================

Säkrare version av GitHub integrationssystemet som:
1. Analyserar repositories utan att integrera kod direkt
2. Genererar rapporter om potentiella integrationer
3. Skapar säkra, manuellt granskningsbara förslag
4. Undviker automatisk kodgenerering som kan innehålla fel
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
import hashlib
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class RepositoryAnalysis:
    """Analys av ett GitHub repository."""
    url: str
    name: str
    description: str
    language: str
    files_analyzed: int
    python_files: int
    javascript_files: int
    key_features: List[str]
    potential_integrations: List[str]
    complexity_score: float
    recommendation: str


class SafeGitHubAnalyzer:
    """
    Säker GitHub repository-analysator som endast analyserar och rapporterar.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.temp_dir = Path(tempfile.mkdtemp(prefix="github_safe_analysis_"))
        self.analysis_log = []
        
        # Fokuserade repositories för första test
        self.target_repositories = [
            "https://github.com/jhao104/proxy_pool",
            "https://github.com/constverum/ProxyBroker", 
            "https://github.com/Python3WebSpider/ProxyPool",
            "https://github.com/Ge0rg3/requests-ip-rotator",
            "https://github.com/markgacoka/selenium-proxy-rotator"
        ]
        
    async def run_safe_analysis(self) -> Dict[str, Any]:
        """
        Kör säker analys av repositories utan kod-integration.
        """
        logger.info("🔍 STARTAR SÄKER GITHUB REPOSITORY ANALYS")
        
        results = {
            "total_repositories": len(self.target_repositories),
            "analyzed": 0,
            "successful_analysis": 0,
            "failed_analysis": 0,
            "analyses": [],
            "summary": {}
        }
        
        for i, repo_url in enumerate(self.target_repositories):
            try:
                logger.info(f"📊 Analyserar repository {i+1}/{len(self.target_repositories)}: {repo_url}")
                
                # Klona repository
                repo_path = await asyncio.wait_for(
                    self._clone_repository(repo_url), 
                    timeout=60
                )
                
                if repo_path:
                    # Analysera utan att integrera
                    analysis = await self._analyze_repository_safe(repo_path, repo_url)
                    
                    if analysis:
                        results["analyses"].append(asdict(analysis))
                        results["successful_analysis"] += 1
                        logger.info(f"✅ Analys klar: {analysis.name} - {analysis.recommendation}")
                    else:
                        results["failed_analysis"] += 1
                        
                    # Rensa upp
                    await self._cleanup_repository(repo_path)
                else:
                    results["failed_analysis"] += 1
                    
                results["analyzed"] += 1
                
            except Exception as e:
                logger.error(f"Fel vid analys av {repo_url}: {e}")
                results["failed_analysis"] += 1
                
        # Generera sammanfattning
        results["summary"] = self._generate_analysis_summary(results["analyses"])
        
        # Spara rapport
        await self._save_analysis_report(results)
        
        return results
        
    async def _clone_repository(self, repo_url: str) -> Optional[Path]:
        """Klona repository till temporär katalog."""
        try:
            repo_name = repo_url.split('/')[-1]
            clone_path = self.temp_dir / repo_name
            
            process = await asyncio.create_subprocess_exec(
                'git', 'clone', '--depth', '1', repo_url, str(clone_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.debug(f"Klonade {repo_name}")
                return clone_path
            else:
                logger.warning(f"Kunde inte klona {repo_name}: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Fel vid kloning av {repo_url}: {e}")
            return None
            
    async def _analyze_repository_safe(self, repo_path: Path, repo_url: str) -> Optional[RepositoryAnalysis]:
        """Säker analys av repository utan kodmodifiering."""
        try:
            repo_name = repo_path.name
            
            # Räkna filer
            python_files = list(repo_path.rglob("*.py"))
            javascript_files = list(repo_path.rglob("*.js"))
            
            # Analysera Python-filer för nyckelord
            key_features = set()
            potential_integrations = []
            total_complexity = 0
            
            for py_file in python_files[:20]:  # Begränsa till 20 filer
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        
                    # Sök efter nyckelord
                    if any(word in content for word in ['proxy', 'rotate']):
                        key_features.add('proxy_management')
                        potential_integrations.append('Proxy pool management')
                        
                    if any(word in content for word in ['scrape', 'crawl', 'spider']):
                        key_features.add('web_scraping')
                        potential_integrations.append('Enhanced web scraping')
                        
                    if any(word in content for word in ['bypass', 'stealth', 'anti-bot']):
                        key_features.add('anti_detection')
                        potential_integrations.append('Anti-detection mechanisms')
                        
                    if any(word in content for word in ['async', 'await']):
                        key_features.add('async_support')
                        potential_integrations.append('Async functionality')
                        
                    # Beräkna komplexitet baserat på filstorlek och innehåll
                    lines = len(content.split('\n'))
                    classes = content.count('class ')
                    functions = content.count('def ')
                    total_complexity += (lines / 1000) + (classes * 2) + functions
                    
                except Exception:
                    continue
                    
            # Läs README för beskrivning
            description = ""
            readme_files = list(repo_path.glob("README*"))
            if readme_files:
                try:
                    with open(readme_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                        description = f.read()[:500]  # Första 500 tecken
                except Exception:
                    pass
                    
            # Avgör rekommendation
            if len(potential_integrations) >= 2 and total_complexity < 50:
                recommendation = "HIGH - Rekommenderas för integration"
            elif len(potential_integrations) >= 1:
                recommendation = "MEDIUM - Kan vara användbar"
            else:
                recommendation = "LOW - Begränsad användbarhet"
                
            return RepositoryAnalysis(
                url=repo_url,
                name=repo_name,
                description=description[:200],
                language="Mixed" if javascript_files else "Python",
                files_analyzed=len(python_files) + len(javascript_files),
                python_files=len(python_files),
                javascript_files=len(javascript_files),
                key_features=list(key_features),
                potential_integrations=list(set(potential_integrations)),
                complexity_score=round(total_complexity, 2),
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Fel vid analys av {repo_path}: {e}")
            return None
            
    def _generate_analysis_summary(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Generera sammanfattning av alla analyser."""
        if not analyses:
            return {"error": "Inga analyser att sammanfatta"}
            
        summary = {
            "total_analyzed": len(analyses),
            "high_priority": len([a for a in analyses if a['recommendation'].startswith('HIGH')]),
            "medium_priority": len([a for a in analyses if a['recommendation'].startswith('MEDIUM')]),
            "low_priority": len([a for a in analyses if a['recommendation'].startswith('LOW')]),
            "top_features": {},
            "recommended_repos": []
        }
        
        # Räkna vanligaste funktioner
        all_features = []
        for analysis in analyses:
            all_features.extend(analysis['key_features'])
            
        feature_counts = {}
        for feature in all_features:
            feature_counts[feature] = feature_counts.get(feature, 0) + 1
            
        summary["top_features"] = dict(sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Top rekommendationer
        high_med_repos = [a for a in analyses if not a['recommendation'].startswith('LOW')]
        summary["recommended_repos"] = sorted(high_med_repos, key=lambda x: len(x['potential_integrations']), reverse=True)[:3]
        
        return summary
        
    async def _cleanup_repository(self, repo_path: Path):
        """Rensa repository med Windows-säker metod."""
        try:
            if repo_path.exists():
                # Enklare cleanup
                import subprocess
                subprocess.run(['rmdir', '/S', '/Q', str(repo_path)], 
                             shell=True, capture_output=True)
        except Exception:
            pass  # Ignorera cleanup-fel
            
    async def _save_analysis_report(self, results: Dict[str, Any]):
        """Spara analysrapport."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON rapport
        json_file = self.project_root / "reports" / f"github_safe_analysis_{timestamp}.json"
        json_file.parent.mkdir(exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        # Human-readable rapport
        txt_file = json_file.with_suffix('.txt')
        await self._generate_readable_report(results, txt_file)
        
        logger.info(f"📊 Rapport sparad: {json_file}")
        
    async def _generate_readable_report(self, results: Dict[str, Any], output_file: Path):
        """Generera läsbar textrapport."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("🔍 GITHUB REPOSITORY ANALYS RAPPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📦 Totalt analyserade: {results['total_repositories']}\n")
            f.write(f"✅ Framgångsrika analyser: {results['successful_analysis']}\n")
            f.write(f"❌ Misslyckade analyser: {results['failed_analysis']}\n\n")
            
            # Sammanfattning
            summary = results.get('summary', {})
            f.write("📊 SAMMANFATTNING:\n")
            f.write(f"🔥 Hög prioritet: {summary.get('high_priority', 0)}\n")
            f.write(f"⚡ Medium prioritet: {summary.get('medium_priority', 0)}\n")
            f.write(f"📝 Låg prioritet: {summary.get('low_priority', 0)}\n\n")
            
            # Top funktioner
            f.write("🎯 VANLIGASTE FUNKTIONER:\n")
            for feature, count in summary.get('top_features', {}).items():
                f.write(f"  • {feature}: {count} repositories\n")
            f.write("\n")
            
            # Detaljerad analys
            f.write("📋 DETALJERAD ANALYS:\n")
            for analysis in results['analyses']:
                f.write(f"\n🔗 {analysis['name']} ({analysis['url']})\n")
                f.write(f"   📊 Rekommendation: {analysis['recommendation']}\n")
                f.write(f"   🐍 Python-filer: {analysis['python_files']}\n")
                f.write(f"   ⚙️  Komplexitet: {analysis['complexity_score']}\n")
                f.write(f"   🎯 Funktioner: {', '.join(analysis['key_features'])}\n")
                f.write(f"   💡 Potentiella integrationer:\n")
                for integration in analysis['potential_integrations']:
                    f.write(f"      - {integration}\n")
                    
            f.write("\n" + "=" * 50 + "\n")
            f.write("🎉 ANALYS KLAR! Granska rapporten för integrationsrekommendationer.\n")


async def main():
    """Kör säker GitHub-analys."""
    project_root = Path(__file__).parent
    
    analyzer = SafeGitHubAnalyzer(project_root)
    
    try:
        logger.info("🚀 Startar säker GitHub Repository-analys")
        results = await analyzer.run_safe_analysis()
        
        logger.info("✅ ANALYS KLAR!")
        logger.info(f"📊 Analyserade: {results['successful_analysis']}/{results['total_repositories']}")
        
        return results
        
    except Exception as e:
        logger.error(f"💥 Kritiskt fel: {e}")
        raise
        
    finally:
        # Cleanup
        try:
            if analyzer.temp_dir.exists():
                shutil.rmtree(analyzer.temp_dir)
        except:
            pass


if __name__ == "__main__":
    results = asyncio.run(main())
    print(f"\n🎉 GitHub Safe Analysis completed!")
    print(f"📊 Analyzed {results['successful_analysis']} repositories successfully")
    print(f"📄 Check reports/ folder for detailed analysis")
