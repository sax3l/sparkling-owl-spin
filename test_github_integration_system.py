#!/usr/bin/env python3
"""
GitHub Integration System Validator
===================================

Testar och validerar GitHub Integration System för att säkerställa att:
1. Systemet kan analysera repositories korrekt
2. Kod-integration fungerar som förväntat  
3. Tester skapas och körs framgångsrikt
4. Cleanup-processen fungerar
5. Rapporter genereras korrekt

Detta är ett kritiskt test som måste passeras innan systemet används på riktigt.
"""

import sys
import os
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
from datetime import datetime
from typing import Dict, Any, List

# Lägg till src till path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import lokalt för test
sys.path.insert(0, str(project_root))

try:
    from github_integration_system import (
        GitHubRepositoryAnalyzer, 
        RepositoryInfo, 
        CodeAnalysis, 
        IntegrationResult
    )
except ImportError as e:
    print(f"❌ Kunde inte importera GitHub Integration System: {e}")
    sys.exit(1)


class GitHubIntegrationSystemValidator:
    """
    Omfattande validator för GitHub Integration System.
    """
    
    def __init__(self):
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Skapa mock projekt-struktur
        self.test_project_root = Path(tempfile.mkdtemp(prefix="github_integration_test_"))
        self._setup_test_project_structure()
        
        # Mock repositories för test
        self.test_repositories = [
            "https://github.com/test/simple-scraper",
            "https://github.com/test/proxy-rotator", 
            "https://github.com/test/bypass-tools"
        ]
        
    def _setup_test_project_structure(self):
        """Skapa test projekt-struktur som liknar riktig struktur."""
        
        # Skapa grundläggande katalogstruktur
        directories = [
            "src/utils",
            "src/database", 
            "src/observability",
            "src/proxy_pool",
            "src/scraper",
            "src/anti_bot",
            "src/webapp/api",
            "src/scrapers",
            "tests",
            "reports"
        ]
        
        for directory in directories:
            (self.test_project_root / directory).mkdir(parents=True, exist_ok=True)
            
        # Skapa mock-moduler
        mock_files = {
            "src/utils/logger.py": self._create_mock_logger(),
            "src/database/manager.py": self._create_mock_database_manager(),
            "src/observability/metrics.py": self._create_mock_metrics(),
            "src/utils/__init__.py": "",
            "src/database/__init__.py": "",
            "src/observability/__init__.py": "",
            "src/__init__.py": ""
        }
        
        for file_path, content in mock_files.items():
            full_path = self.test_project_root / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
    def _create_mock_logger(self) -> str:
        """Skapa mock logger-modul."""
        return '''
def get_logger(name):
    import logging
    return logging.getLogger(name)
'''
    
    def _create_mock_database_manager(self) -> str:
        """Skapa mock database manager."""
        return '''
class DatabaseManager:
    def __init__(self):
        pass
        
    async def connect(self):
        pass
'''
    
    def _create_mock_metrics(self) -> str:
        """Skapa mock metrics-modul."""
        return '''
class MetricsCollector:
    def counter(self, name, value):
        pass
        
    def timer(self, name, value):
        pass
'''
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Kör alla valideringstester."""
        
        print("🧪 STARTAR GITHUB INTEGRATION SYSTEM VALIDATION")
        print("=" * 60)
        
        test_methods = [
            self._test_analyzer_initialization,
            self._test_repository_cloning,
            self._test_code_analysis,
            self._test_feature_identification,
            self._test_integration_strategies,
            self._test_code_adaptation,
            self._test_module_writing,
            self._test_integration_testing,
            self._test_cleanup_process,
            self._test_report_generation,
            self._test_complete_workflow,
            self._test_error_handling,
            self._test_performance_characteristics
        ]
        
        for test_method in test_methods:
            await self._run_single_test(test_method)
            
        # Sammanfattning
        success_rate = (self.test_results['passed_tests'] / 
                       self.test_results['total_tests']) * 100
                       
        print("\n" + "=" * 60)
        print("📊 TESTRESULTAT SAMMANFATTNING")
        print("=" * 60)
        print(f"✅ Godkända tester: {self.test_results['passed_tests']}")
        print(f"❌ Misslyckade tester: {self.test_results['failed_tests']}")
        print(f"📈 Framgångsfrekvens: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 VALIDATION GODKÄND - Systemet är redo för användning!")
        elif success_rate >= 70:
            print("⚠️ VALIDATION DELVIS GODKÄND - Vissa förbättringar rekommenderas")
        else:
            print("❌ VALIDATION MISSLYCKAD - Systemet behöver betydande förbättringar")
            
        return self.test_results
        
    async def _run_single_test(self, test_method):
        """Kör ett enskilt test."""
        test_name = test_method.__name__
        self.test_results['total_tests'] += 1
        
        try:
            print(f"\n🧪 Kör test: {test_name}")
            result = await test_method()
            
            if result.get('success', False):
                self.test_results['passed_tests'] += 1
                print(f"✅ {test_name} - GODKÄNT")
            else:
                self.test_results['failed_tests'] += 1
                print(f"❌ {test_name} - MISSLYCKADES: {result.get('message', 'Okänt fel')}")
                
            self.test_results['test_details'].append({
                'test_name': test_name,
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.test_results['failed_tests'] += 1
            print(f"💥 {test_name} - KRITISKT FEL: {e}")
            
            self.test_results['test_details'].append({
                'test_name': test_name,
                'success': False,
                'message': f"Kritiskt fel: {e}",
                'timestamp': datetime.now().isoformat()
            })
            
    async def _test_analyzer_initialization(self) -> Dict[str, Any]:
        """Testa att analyzern kan initialiseras korrekt."""
        try:
            # Mock metrics
            mock_metrics = Mock()
            mock_metrics.counter = Mock()
            mock_metrics.timer = Mock()
            
            # Skapa analyzer
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Kontrollera att viktiga attribut finns
            assert hasattr(analyzer, 'project_root')
            assert hasattr(analyzer, 'metrics')
            assert hasattr(analyzer, 'target_repositories')
            assert hasattr(analyzer, 'temp_dir')
            
            # Kontrollera att temp_dir skapades
            assert analyzer.temp_dir.exists()
            
            return {
                'success': True,
                'message': 'Analyzer initialiserad framgångsrikt'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Initialization misslyckades: {e}'
            }
            
    async def _test_repository_cloning(self) -> Dict[str, Any]:
        """Testa repository-kloning (mockad)."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Mock git clone-processen
            with patch('asyncio.create_subprocess_exec') as mock_subprocess:
                # Mock framgångsrikt resultat
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b'success', b'')
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process
                
                # Testa kloning
                result = await analyzer._clone_repository("https://github.com/test/repo")
                
                # Kontrollera resultat
                assert result is not None
                assert isinstance(result, Path)
                
                return {
                    'success': True,
                    'message': 'Repository-kloning fungerar'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Repository-kloning misslyckades: {e}'
            }
            
    async def _test_code_analysis(self) -> Dict[str, Any]:
        """Testa kod-analys funktionalitet."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Skapa test-kod för analys
            test_code = '''
import requests
import asyncio

class ProxyRotator:
    """En enkel proxy rotator."""
    
    def __init__(self, proxies):
        self.proxies = proxies
        
    async def get_next_proxy(self):
        """Hämta nästa proxy."""
        return self.proxies[0]
        
def scrape_url(url, proxy=None):
    """Scrapa en URL."""
    return requests.get(url, proxies=proxy)
'''
            
            # Skapa temporär testfil
            test_file = analyzer.temp_dir / "test_code.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_code)
                
            # Analysera filen
            analysis = await analyzer._analyze_python_file(test_file)
            
            # Kontrollera analys
            assert analysis is not None
            assert isinstance(analysis, CodeAnalysis)
            assert 'ProxyRotator' in analysis.classes
            assert 'get_next_proxy' in analysis.functions or 'scrape_url' in analysis.functions
            assert 'proxy' in analysis.unique_features
            
            return {
                'success': True,
                'message': f'Kod-analys fungerar - Hittade {len(analysis.classes)} klasser och {len(analysis.functions)} funktioner'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Kod-analys misslyckades: {e}'
            }
            
    async def _test_feature_identification(self) -> Dict[str, Any]:
        """Testa identifiering av unika funktioner."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Test med olika typer av funktionsnamn
            test_cases = [
                (['proxy_rotate', 'get_proxy'], ['ProxyManager'], 'proxy code', ['proxy']),
                (['scrape_data', 'extract_info'], ['WebScraper'], 'scraping system', ['scraping']),
                (['bypass_cloudflare', 'stealth_mode'], ['AntiBot'], 'cloudflare bypass', ['bypass']),
                (['swedish_lookup', 'personnummer_check'], ['SwedishData'], 'sweden data', ['swedish'])
            ]
            
            for functions, classes, content, expected_features in test_cases:
                features = analyzer._identify_unique_features(functions, classes, content)
                
                # Kontrollera att förväntade funktioner identifierades
                for expected in expected_features:
                    assert expected in features, f"Förväntad funktion '{expected}' inte identifierad"
                    
            return {
                'success': True,
                'message': 'Funktionsidentifiering fungerar korrekt'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Funktionsidentifiering misslyckades: {e}'
            }
            
    async def _test_integration_strategies(self) -> Dict[str, Any]:
        """Testa olika integrationsstrategier."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Test proxy integration
            test_code = 'class ProxyPool: pass'
            analysis = CodeAnalysis(
                file_path="/test/proxy.py",
                language="python",
                functions=['rotate_proxy'],
                classes=['ProxyPool'],
                imports=['requests'],
                complexity_score=3,
                unique_features=['proxy'],
                integration_potential='high'
            )
            
            result = await analyzer._integrate_proxy_functionality(test_code, analysis, "https://github.com/test/proxy")
            assert result['success'] == True
            
            return {
                'success': True,
                'message': 'Integrationsstrategier fungerar'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Integrationsstrategier misslyckades: {e}'
            }
            
    async def _test_code_adaptation(self) -> Dict[str, Any]:
        """Testa kodanpassning för integration."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            test_code = '''
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()
'''
            
            analysis = CodeAnalysis(
                file_path="/test/fetcher.py",
                language="python", 
                functions=['fetch_data'],
                classes=[],
                imports=['requests'],
                complexity_score=1,
                unique_features=['api'],
                integration_potential='medium'
            )
            
            adapted = analyzer._adapt_code_for_integration(
                test_code, analysis, 'utils', 'https://github.com/test/fetcher'
            )
            
            # Kontrollera att anpassningar gjordes
            assert 'utils.logger import get_logger' in adapted
            assert 'observability.metrics import MetricsCollector' in adapted
            assert 'Integrerad funktionalitet från' in adapted
            
            return {
                'success': True,
                'message': 'Kodanpassning fungerar'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Kodanpassning misslyckades: {e}'
            }
            
    async def _test_module_writing(self) -> Dict[str, Any]:
        """Testa skrivning av integrationsmoduler."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            test_code = '# Test integration module\nprint("Hello integration")'
            target_path = self.test_project_root / "src" / "test_integration.py"
            
            await analyzer._write_integration_module(
                target_path, test_code, "https://github.com/test/module"
            )
            
            # Kontrollera att filen skapades
            assert target_path.exists()
            
            # Kontrollera innehåll
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '# Test integration module' in content
                
            return {
                'success': True,
                'message': 'Modul-skrivning fungerar'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Modul-skrivning misslyckades: {e}'
            }
            
    async def _test_integration_testing(self) -> Dict[str, Any]:
        """Testa att integration-tester skapas och körs."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Skapa mock integration result
            integration_result = IntegrationResult(
                repository="https://github.com/test/module",
                integrated_features=['test_feature'],
                new_modules=['src/test_integration.py'],
                enhanced_modules=[],
                tests_created=[],
                success=True
            )
            
            # Skapa modulen som ska testas
            test_module_path = self.test_project_root / "src" / "test_integration.py"
            with open(test_module_path, 'w', encoding='utf-8') as f:
                f.write('# Simple test module\ndef test_function(): return True')
                
            # Testa integration
            test_results = await analyzer._test_integration(integration_result)
            
            # Kontrollera resultat
            assert test_results['tests_run'] > 0
            
            return {
                'success': True,
                'message': f"Integration-test fungerar - Körde {test_results['tests_run']} tester"
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Integration-test misslyckades: {e}'
            }
            
    async def _test_cleanup_process(self) -> Dict[str, Any]:
        """Testa cleanup-processen."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Skapa temporär katalog att rensa
            temp_repo = analyzer.temp_dir / "test_cleanup"
            temp_repo.mkdir()
            
            # Lägg till några filer
            test_file = temp_repo / "test.txt"
            with open(test_file, 'w') as f:
                f.write("test content")
                
            # Kontrollera att katalogen existerar
            assert temp_repo.exists()
            assert test_file.exists()
            
            # Rensa upp
            await analyzer._cleanup_repository(temp_repo)
            
            # Kontrollera att katalogen rensats
            assert not temp_repo.exists()
            
            return {
                'success': True,
                'message': 'Cleanup-process fungerar'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Cleanup-process misslyckades: {e}'
            }
            
    async def _test_report_generation(self) -> Dict[str, Any]:
        """Testa rapportgenerering."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Mock resultat för rapport
            test_results = {
                'total_repositories': 5,
                'processed': 5,
                'successful_integrations': 4,
                'failed_integrations': 1,
                'new_features_added': ['proxy', 'scraping'],
                'enhanced_modules': ['proxy_pool'],
                'integration_log': []
            }
            
            # Generera rapport
            await analyzer._generate_integration_report(test_results)
            
            # Kontrollera att rapportfiler skapades
            report_dir = self.test_project_root / "reports"
            json_reports = list(report_dir.glob("github_integration_report_*.json"))
            txt_reports = list(report_dir.glob("github_integration_report_*.txt"))
            
            assert len(json_reports) > 0, "Ingen JSON-rapport skapad"
            assert len(txt_reports) > 0, "Ingen text-rapport skapad"
            
            return {
                'success': True,
                'message': 'Rapportgenerering fungerar'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Rapportgenerering misslyckades: {e}'
            }
            
    async def _test_complete_workflow(self) -> Dict[str, Any]:
        """Testa komplett arbetsflöde (mockad)."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Mock alla externa beroenden
            with patch.object(analyzer, '_clone_repository') as mock_clone, \
                 patch.object(analyzer, '_analyze_repository') as mock_analyze, \
                 patch.object(analyzer, '_integrate_functionality') as mock_integrate, \
                 patch.object(analyzer, '_test_integration') as mock_test, \
                 patch.object(analyzer, '_cleanup_repository') as mock_cleanup:
                
                # Setup mocks
                mock_clone.return_value = self.test_project_root / "mock_repo"
                mock_analyze.return_value = [
                    CodeAnalysis(
                        file_path="/mock/proxy.py",
                        language="python",
                        functions=['rotate'],
                        classes=['ProxyRotator'],
                        imports=['requests'],
                        complexity_score=5,
                        unique_features=['proxy'],
                        integration_potential='high'
                    )
                ]
                mock_integrate.return_value = IntegrationResult(
                    repository="https://github.com/test/proxy",
                    integrated_features=['proxy'],
                    new_modules=['src/proxy_integration.py'],
                    enhanced_modules=[],
                    tests_created=[],
                    success=True
                )
                mock_test.return_value = {
                    'success': True,
                    'tests_run': 2,
                    'tests_passed': 2,
                    'tests_failed': 0
                }
                
                # Kör workflow med begränsat antal repos för test
                original_repos = analyzer.target_repositories
                analyzer.target_repositories = analyzer.target_repositories[:2]  # Endast 2 repos för test
                
                try:
                    results = await analyzer.run_complete_analysis()
                    
                    # Kontrollera resultat
                    assert results['total_repositories'] == 2
                    assert results['processed'] == 2
                    
                    return {
                        'success': True,
                        'message': f"Komplett workflow fungerar - Bearbetade {results['processed']} repositories"
                    }
                finally:
                    analyzer.target_repositories = original_repos
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'Komplett workflow misslyckades: {e}'
            }
            
    async def _test_error_handling(self) -> Dict[str, Any]:
        """Testa error handling."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Testa med ogiltig repository URL
            result = await analyzer._clone_repository("invalid://not.a.repo")
            assert result is None  # Ska returnera None vid fel
            
            # Testa med ogiltig fil för analys
            result = await analyzer._analyze_python_file(Path("/nonexistent/file.py"))
            assert result is None  # Ska returnera None vid fel
            
            return {
                'success': True,
                'message': 'Error handling fungerar'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error handling misslyckades: {e}'
            }
            
    async def _test_performance_characteristics(self) -> Dict[str, Any]:
        """Testa prestanda-karakteristik."""
        try:
            mock_metrics = Mock()
            analyzer = GitHubRepositoryAnalyzer(self.test_project_root, mock_metrics)
            
            # Testa att signatur-generering är effektiv
            start_time = datetime.now()
            signatures = analyzer._generate_existing_signatures()
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # Ska vara snabb (under 5 sekunder för normal projektstorlek)
            assert duration < 5.0, f"Signatur-generering för långsam: {duration}s"
            assert isinstance(signatures, set)
            
            return {
                'success': True,
                'message': f'Prestanda OK - Signatur-generering tog {duration:.2f}s'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Prestanda-test misslyckades: {e}'
            }
            
    def cleanup(self):
        """Rensa test-kataloger."""
        try:
            if self.test_project_root.exists():
                shutil.rmtree(self.test_project_root)
                print(f"🧹 Rensade test-katalog: {self.test_project_root}")
        except Exception as e:
            print(f"⚠️ Kunde inte rensa test-katalog: {e}")


async def main():
    """Huvudfunktion för validering."""
    
    validator = GitHubIntegrationSystemValidator()
    
    try:
        # Kör alla tester
        results = await validator.run_all_tests()
        
        # Spara testresultat
        results_file = Path("github_integration_test_results.json")
        import json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print(f"\n📄 Testresultat sparade i: {results_file}")
        
        # Returnera exit code baserat på resultat
        success_rate = (results['passed_tests'] / results['total_tests']) * 100
        
        if success_rate >= 90:
            return 0  # Success
        elif success_rate >= 70:
            return 1  # Warning
        else:
            return 2  # Failure
            
    except Exception as e:
        print(f"💥 Kritiskt fel under validering: {e}")
        return 3
        
    finally:
        validator.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
