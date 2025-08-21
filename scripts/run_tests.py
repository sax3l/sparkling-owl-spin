"""
Huvudtestskript för ECaDP-testsviten

För nybörjare: Detta skript kör alla tester i korrekt ordning:
1. Unit-tester (snabba, isolerade)
2. Integration-tester (databas, Redis, etc)
3. E2E-tester (webbläsare, syntetiska sajter)

Användning:
    python run_tests.py [--type TYPE] [--verbose] [--stop-on-fail]
    
    --type: unit|integration|e2e|all (default: all)
    --verbose: Visa detaljerad output
    --stop-on-fail: Stoppa vid första fel
    --coverage: Kör med code coverage
"""

import subprocess
import sys
import time
import argparse
import json
from pathlib import Path
import os


class TestRunner:
    """Klass för att hantera testkörning"""
    
    def __init__(self, verbose=False, stop_on_fail=False, coverage=False):
        self.verbose = verbose
        self.stop_on_fail = stop_on_fail
        self.coverage = coverage
        self.results = {
            'unit': {'status': 'not_run', 'duration': 0, 'tests': 0, 'failures': 0},
            'integration': {'status': 'not_run', 'duration': 0, 'tests': 0, 'failures': 0},
            'e2e': {'status': 'not_run', 'duration': 0, 'tests': 0, 'failures': 0}
        }
        
        # Hitta projektroten
        self.project_root = Path(__file__).parent.parent
        self.tests_dir = self.project_root / "tests"
    
    def run_command(self, cmd, cwd=None):
        """Kör kommando och returnera resultat"""
        if self.verbose:
            print(f"📋 Kör: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=not self.verbose,
                text=True,
                timeout=300  # 5 minuter timeout
            )
            return result
        except subprocess.TimeoutExpired:
            print("⏰ Kommando tog för lång tid (timeout)")
            return None
        except Exception as e:
            print(f"❌ Fel vid körning av kommando: {e}")
            return None
    
    def check_prerequisites(self):
        """Kontrollera att alla förutsättningar är uppfyllda"""
        print("🔍 Kontrollerar förutsättningar...")
        
        # Kontrollera pytest
        result = self.run_command("pytest --version")
        if not result or result.returncode != 0:
            print("❌ pytest är inte installerat")
            print("   Installera med: pip install pytest")
            return False
        
        if self.verbose:
            print(f"✅ pytest: {result.stdout.strip()}")
        
        # Kontrollera att testkataloger finns
        required_dirs = [
            self.tests_dir / "unit",
            self.tests_dir / "integration", 
            self.tests_dir / "e2e"
        ]
        
        for test_dir in required_dirs:
            if not test_dir.exists():
                print(f"❌ Testkatalog saknas: {test_dir}")
                return False
        
        print("✅ Alla förutsättningar uppfyllda")
        return True
    
    def run_unit_tests(self):
        """Kör unit-tester"""
        print("\n🧪 Kör Unit-tester...")
        print("=" * 40)
        
        start_time = time.time()
        
        # Bygg pytest-kommando
        cmd_parts = ["pytest", "tests/unit/"]
        
        if self.verbose:
            cmd_parts.append("-v")
        else:
            cmd_parts.append("-q")
        
        if self.stop_on_fail:
            cmd_parts.append("-x")
        
        # Lägg till markers
        cmd_parts.extend(["-m", "unit"])
        
        # Lägg till JSON-rapport
        cmd_parts.extend(["--json-report", "--json-report-file=test_results_unit.json"])
        
        if self.coverage:
            cmd_parts.extend([
                "--cov=src", 
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov/unit"
            ])
        
        cmd = " ".join(cmd_parts)
        result = self.run_command(cmd)
        
        duration = time.time() - start_time
        self.results['unit']['duration'] = duration
        
        if result is None:
            self.results['unit']['status'] = 'timeout'
            return False
        elif result.returncode == 0:
            self.results['unit']['status'] = 'passed'
            print(f"✅ Unit-tester slutförda på {duration:.1f}s")
            return True
        else:
            self.results['unit']['status'] = 'failed'
            print(f"❌ Unit-tester misslyckades på {duration:.1f}s")
            if not self.verbose:
                print("🔍 Kör med --verbose för mer detaljer")
            return False
    
    def run_integration_tests(self):
        """Kör integrationstester"""
        print("\n🔗 Kör Integration-tester...")
        print("=" * 40)
        
        start_time = time.time()
        
        # Bygg pytest-kommando
        cmd_parts = ["pytest", "tests/integration/"]
        
        if self.verbose:
            cmd_parts.append("-v")
        else:
            cmd_parts.append("-q")
        
        if self.stop_on_fail:
            cmd_parts.append("-x")
        
        # Lägg till markers
        cmd_parts.extend(["-m", "integration"])
        
        # Lägg till JSON-rapport
        cmd_parts.extend(["--json-report", "--json-report-file=test_results_integration.json"])
        
        if self.coverage:
            cmd_parts.extend([
                "--cov=src", 
                "--cov-append",
                "--cov-report=html:htmlcov/integration"
            ])
        
        cmd = " ".join(cmd_parts)
        result = self.run_command(cmd)
        
        duration = time.time() - start_time
        self.results['integration']['duration'] = duration
        
        if result is None:
            self.results['integration']['status'] = 'timeout'
            return False
        elif result.returncode == 0:
            self.results['integration']['status'] = 'passed'
            print(f"✅ Integration-tester slutförda på {duration:.1f}s")
            return True
        else:
            self.results['integration']['status'] = 'failed'
            print(f"❌ Integration-tester misslyckades på {duration:.1f}s")
            return False
    
    def check_synthetic_services(self):
        """Kontrollera att syntetiska tjänster körs"""
        print("🔍 Kontrollerar syntetiska tjänster...")
        
        services = [
            ("Static List", "http://localhost:8081"),
            ("Infinite Scroll", "http://localhost:8082"), 
            ("Form Flow", "http://localhost:8083")
        ]
        
        all_running = True
        
        for service_name, url in services:
            try:
                import urllib.request
                with urllib.request.urlopen(url, timeout=5) as response:
                    if response.status == 200:
                        if self.verbose:
                            print(f"✅ {service_name} körs")
                    else:
                        print(f"❌ {service_name} svarar med status {response.status}")
                        all_running = False
            except Exception as e:
                print(f"❌ {service_name} är inte tillgänglig: {e}")
                all_running = False
        
        if not all_running:
            print("\n💡 Starta syntetiska tjänster med:")
            print("   python scripts/start_synthetic_services.py")
            return False
        
        print("✅ Alla syntetiska tjänster körs")
        return True
    
    def run_e2e_tests(self):
        """Kör E2E-tester"""
        print("\n🌐 Kör E2E-tester...")
        print("=" * 40)
        
        # Kontrollera syntetiska tjänster först
        if not self.check_synthetic_services():
            self.results['e2e']['status'] = 'skipped'
            return False
        
        start_time = time.time()
        
        # Bygg pytest-kommando
        cmd_parts = ["pytest", "tests/e2e/"]
        
        if self.verbose:
            cmd_parts.append("-v")
        else:
            cmd_parts.append("-q")
        
        if self.stop_on_fail:
            cmd_parts.append("-x")
        
        # Lägg till markers
        cmd_parts.extend(["-m", "e2e"])
        
        # Lägg till JSON-rapport
        cmd_parts.extend(["--json-report", "--json-report-file=test_results_e2e.json"])
        
        # E2E-tester behöver längre timeout
        cmd_parts.extend(["--timeout=60"])
        
        cmd = " ".join(cmd_parts)
        result = self.run_command(cmd)
        
        duration = time.time() - start_time
        self.results['e2e']['duration'] = duration
        
        if result is None:
            self.results['e2e']['status'] = 'timeout'
            return False
        elif result.returncode == 0:
            self.results['e2e']['status'] = 'passed'
            print(f"✅ E2E-tester slutförda på {duration:.1f}s")
            return True
        else:
            self.results['e2e']['status'] = 'failed'
            print(f"❌ E2E-tester misslyckades på {duration:.1f}s")
            return False
    
    def show_summary(self):
        """Visa sammanfattning av testresultat"""
        print("\n" + "=" * 60)
        print("📊 TESTSAMMANFATTNING")
        print("=" * 60)
        
        total_duration = sum(r['duration'] for r in self.results.values())
        total_tests = sum(r['tests'] for r in self.results.values())
        total_failures = sum(r['failures'] for r in self.results.values())
        
        for test_type, result in self.results.items():
            status_icon = {
                'passed': '✅',
                'failed': '❌', 
                'skipped': '⏭️',
                'timeout': '⏰',
                'not_run': '⚪'
            }.get(result['status'], '❓')
            
            print(f"{status_icon} {test_type.upper():12} {result['status']:10} ({result['duration']:.1f}s)")
        
        print("-" * 60)
        print(f"⏱️  Total tid: {total_duration:.1f}s")
        
        if total_failures > 0:
            print(f"❌ {total_failures} test(er) misslyckades")
        else:
            print("✅ Alla tester lyckades!")
        
        print("=" * 60)
        
        # Visa coverage-rapport om aktiverad
        if self.coverage:
            print("\n📈 Coverage-rapporter finns i htmlcov/")
        
        # Visa JSON-rapporter
        json_files = [
            "test_results_unit.json",
            "test_results_integration.json", 
            "test_results_e2e.json"
        ]
        
        existing_json = [f for f in json_files if Path(f).exists()]
        if existing_json:
            print(f"\n📄 JSON-rapporter: {', '.join(existing_json)}")
    
    def run_all_tests(self):
        """Kör alla tester i ordning"""
        print("🧪 ECaDP Test Suite")
        print("=" * 60)
        
        if not self.check_prerequisites():
            return False
        
        success = True
        
        # Unit-tester (snabbast, kör alltid först)
        if not self.run_unit_tests():
            success = False
            if self.stop_on_fail:
                print("🛑 Stoppar på unit-test fel")
                self.show_summary()
                return False
        
        # Integration-tester
        if not self.run_integration_tests():
            success = False
            if self.stop_on_fail:
                print("🛑 Stoppar på integration-test fel")
                self.show_summary()
                return False
        
        # E2E-tester (längsamst, kör sist)
        if not self.run_e2e_tests():
            success = False
        
        self.show_summary()
        return success


def main():
    parser = argparse.ArgumentParser(
        description="ECaDP Test Suite - Kör alla automatiska tester"
    )
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "e2e", "all"],
        default="all",
        help="Typ av tester att köra (default: all)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Visa detaljerad output"
    )
    parser.add_argument(
        "--stop-on-fail", "-x",
        action="store_true", 
        help="Stoppa vid första fel"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Kör med code coverage analys"
    )
    
    args = parser.parse_args()
    
    # Sätt working directory till projektroten
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    runner = TestRunner(
        verbose=args.verbose,
        stop_on_fail=args.stop_on_fail,
        coverage=args.coverage
    )
    
    try:
        if args.type == "all":
            success = runner.run_all_tests()
        elif args.type == "unit":
            success = runner.run_unit_tests()
        elif args.type == "integration":
            success = runner.run_integration_tests()
        elif args.type == "e2e":
            success = runner.run_e2e_tests()
        else:
            print(f"❌ Okänd testtyp: {args.type}")
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n🛑 Testrun avbruten av användare")
        return 1
    except Exception as e:
        print(f"\n❌ Oväntat fel: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
