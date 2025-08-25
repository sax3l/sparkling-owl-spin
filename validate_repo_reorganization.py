#!/usr/bin/env python3
"""
Repository Reorganization Validation Script
Validerar att alla git repos är flyttade till rätt platser enligt specifikationen
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoReorganizationValidator:
    """Validerar repository reorganization"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "validation_status": "UNKNOWN",
            "vendors_structure": {},
            "engines_structure": {},
            "integrations_structure": {},
            "sandbox_structure": {},
            "docs_structure": {},
            "requirements_consolidation": {},
            "removed_repos": [],
            "issues": [],
            "recommendations": []
        }
        
    def validate_vendors_structure(self) -> Dict[str, Any]:
        """Validerar vendors-mappen struktur"""
        
        vendors_path = self.project_root / "vendors"
        expected_vendors = [
            "flaresolverr",
            "cloudscraper", 
            "undetected-chromedriver",
            "proxy_pool",
            "crawlee",
            "scrapy",
            "crewAI",
            "Adala",
            "langroid",
            "tika",
            "trafilatura",
            "vanna"
        ]
        
        results = {
            "exists": vendors_path.exists(),
            "expected_vendors": expected_vendors,
            "found_vendors": [],
            "missing_vendors": [],
            "extra_vendors": []
        }
        
        if vendors_path.exists():
            found_vendors = [d.name for d in vendors_path.iterdir() if d.is_dir()]
            results["found_vendors"] = found_vendors
            
            # Check missing vendors
            results["missing_vendors"] = [v for v in expected_vendors if v not in found_vendors]
            
            # Check extra vendors
            results["extra_vendors"] = [v for v in found_vendors if v not in expected_vendors]
            
            if results["missing_vendors"]:
                self.validation_results["issues"].append(
                    f"Missing vendors: {', '.join(results['missing_vendors'])}"
                )
                
            if results["extra_vendors"]:
                self.validation_results["recommendations"].append(
                    f"Extra vendors found (consider organizing): {', '.join(results['extra_vendors'])}"
                )
                
        else:
            self.validation_results["issues"].append("Vendors directory does not exist")
            
        return results
        
    def validate_engines_structure(self) -> Dict[str, Any]:
        """Validerar engines-mappen struktur"""
        
        engines_path = self.project_root / "engines"
        expected_structure = {
            "bypass": [
                "cloudflare_bypass.py",
                "captcha_solver.py", 
                "tls_fingerprinting.py",
                "waf_bypass.py"
            ],
            "scraping": [
                "crawlee_engine.py",
                "scrapy_engine.py",
                "playwright_engine.py",
                "proxy_manager.py"
            ],
            "pentesting": [
                "vulnerability_scanner.py",
                "exploit_manager.py",
                "osint_tools.py",
                "phishing_detector.py"
            ]
        }
        
        results = {
            "exists": engines_path.exists(),
            "structure_validation": {}
        }
        
        if engines_path.exists():
            for category, expected_files in expected_structure.items():
                category_path = engines_path / category
                category_results = {
                    "exists": category_path.exists(),
                    "expected_files": expected_files,
                    "found_files": [],
                    "missing_files": [],
                    "extra_files": []
                }
                
                if category_path.exists():
                    found_files = [f.name for f in category_path.iterdir() if f.is_file() and f.suffix == '.py']
                    category_results["found_files"] = found_files
                    category_results["missing_files"] = [f for f in expected_files if f not in found_files]
                    category_results["extra_files"] = [f for f in found_files if f not in expected_files]
                    
                    if category_results["missing_files"]:
                        self.validation_results["issues"].append(
                            f"Missing {category} engine files: {', '.join(category_results['missing_files'])}"
                        )
                        
                else:
                    self.validation_results["issues"].append(f"Engines/{category} directory does not exist")
                    
                results["structure_validation"][category] = category_results
                
        else:
            self.validation_results["issues"].append("Engines directory does not exist")
            
        return results
        
    def validate_integrations_structure(self) -> Dict[str, Any]:
        """Validerar integrations-mappen struktur"""
        
        integrations_path = self.project_root / "integrations" / "swedish"
        expected_files = [
            "blocket_api.py",
            "vehicle_data.py",
            "company_data.py",
            "pii_detector.py"
        ]
        
        results = {
            "exists": integrations_path.exists(),
            "expected_files": expected_files,
            "found_files": [],
            "missing_files": [],
            "extra_files": []
        }
        
        if integrations_path.exists():
            found_files = [f.name for f in integrations_path.iterdir() if f.is_file() and f.suffix == '.py']
            results["found_files"] = found_files
            results["missing_files"] = [f for f in expected_files if f not in found_files]
            results["extra_files"] = [f for f in found_files if f not in expected_files]
            
            if results["missing_files"]:
                self.validation_results["issues"].append(
                    f"Missing Swedish integration files: {', '.join(results['missing_files'])}"
                )
                
        else:
            self.validation_results["issues"].append("Integrations/swedish directory does not exist")
            
        return results
        
    def validate_sandbox_structure(self) -> Dict[str, Any]:
        """Validerar sandbox-mappen struktur"""
        
        sandbox_path = self.project_root / "sandbox"
        expected_subdirs = [
            "exploit_tools",
            "osint_tools", 
            "phishing_tools",
            "research"
        ]
        
        results = {
            "exists": sandbox_path.exists(),
            "expected_subdirs": expected_subdirs,
            "found_subdirs": [],
            "missing_subdirs": [],
            "extra_subdirs": []
        }
        
        if sandbox_path.exists():
            found_subdirs = [d.name for d in sandbox_path.iterdir() if d.is_dir()]
            results["found_subdirs"] = found_subdirs
            results["missing_subdirs"] = [d for d in expected_subdirs if d not in found_subdirs]
            results["extra_subdirs"] = [d for d in found_subdirs if d not in expected_subdirs]
            
            if results["missing_subdirs"]:
                self.validation_results["recommendations"].append(
                    f"Consider creating sandbox subdirs: {', '.join(results['missing_subdirs'])}"
                )
                
        else:
            self.validation_results["issues"].append("Sandbox directory does not exist")
            
        return results
        
    def validate_docs_structure(self) -> Dict[str, Any]:
        """Validerar docs-mappen struktur"""
        
        docs_path = self.project_root / "docs"
        expected_subdirs = [
            "pentesting",
            "security"
        ]
        
        expected_docs = {
            "pentesting": ["PayloadsAllTheThings", "AllAboutBugBounty"],
            "security": ["awesome-api-security"]
        }
        
        results = {
            "exists": docs_path.exists(),
            "structure_validation": {}
        }
        
        if docs_path.exists():
            for subdir in expected_subdirs:
                subdir_path = docs_path / subdir
                subdir_results = {
                    "exists": subdir_path.exists(),
                    "expected_docs": expected_docs.get(subdir, []),
                    "found_docs": []
                }
                
                if subdir_path.exists():
                    found_docs = [d.name for d in subdir_path.iterdir() if d.is_dir()]
                    subdir_results["found_docs"] = found_docs
                    
                results["structure_validation"][subdir] = subdir_results
                
        else:
            self.validation_results["recommendations"].append("Consider creating docs directory structure")
            
        return results
        
    def validate_requirements_consolidation(self) -> Dict[str, Any]:
        """Validerar requirements-filernas konsolidering"""
        
        old_requirements = [
            "requirements.txt",
            "requirements_backend.txt",
            "requirements_dev.txt", 
            "requirements_production.txt",
            "requirements_revolutionary.txt"
        ]
        
        consolidated_file = self.project_root / "requirements_consolidated.txt"
        
        results = {
            "consolidated_file_exists": consolidated_file.exists(),
            "old_files_removed": [],
            "old_files_remaining": []
        }
        
        for req_file in old_requirements:
            file_path = self.project_root / req_file
            if file_path.exists():
                results["old_files_remaining"].append(req_file)
            else:
                results["old_files_removed"].append(req_file)
                
        if results["old_files_remaining"]:
            self.validation_results["issues"].append(
                f"Old requirements files still exist: {', '.join(results['old_files_remaining'])}"
            )
            
        if not results["consolidated_file_exists"]:
            self.validation_results["issues"].append("Consolidated requirements file does not exist")
            
        return results
        
    def check_removed_repositories(self) -> List[str]:
        """Kontrollerar att repositorys som ska raderas är borttagna"""
        
        repos_to_remove = [
            "2captcha-python",
            "nopecha-extension", 
            "CaptchaHarvester",
            "azuretls-client",
            "CycleTLS",
            "bypass-403",
            "bypasswaf",
            "rengine",
            "adversarial-robustness-toolbox"
        ]
        
        remaining_repos = []
        
        for repo in repos_to_remove:
            repo_path = self.project_root / repo
            if repo_path.exists():
                remaining_repos.append(repo)
                
        if remaining_repos:
            self.validation_results["issues"].append(
                f"Repositories that should be removed still exist: {', '.join(remaining_repos)}"
            )
            
        return remaining_repos
        
    def run_full_validation(self) -> Dict[str, Any]:
        """Kör full validering av repository reorganization"""
        
        logger.info("🔍 Starting repository reorganization validation...")
        
        # Validera alla strukturer
        self.validation_results["vendors_structure"] = self.validate_vendors_structure()
        self.validation_results["engines_structure"] = self.validate_engines_structure()
        self.validation_results["integrations_structure"] = self.validate_integrations_structure()
        self.validation_results["sandbox_structure"] = self.validate_sandbox_structure()
        self.validation_results["docs_structure"] = self.validate_docs_structure()
        self.validation_results["requirements_consolidation"] = self.validate_requirements_consolidation()
        self.validation_results["removed_repos"] = self.check_removed_repositories()
        
        # Bestäm övergripande status
        if not self.validation_results["issues"]:
            self.validation_results["validation_status"] = "SUCCESS"
            logger.info("✅ Repository reorganization validation completed successfully!")
        elif len(self.validation_results["issues"]) <= 2:
            self.validation_results["validation_status"] = "WARNING"  
            logger.warning("⚠️ Repository reorganization validation completed with warnings")
        else:
            self.validation_results["validation_status"] = "FAILED"
            logger.error("❌ Repository reorganization validation failed")
            
        # Skriv ut sammanfattning
        self.print_validation_summary()
        
        return self.validation_results
        
    def print_validation_summary(self):
        """Skriv ut validerings-sammanfattning"""
        
        print("\n" + "="*80)
        print("🦉 SPARKLING-OWL-SPIN REPOSITORY REORGANIZATION VALIDATION")
        print("="*80)
        
        print(f"📅 Validation Time: {self.validation_results['timestamp']}")
        print(f"📁 Project Root: {self.validation_results['project_root']}")
        print(f"🎯 Status: {self.validation_results['validation_status']}")
        
        # Vendors
        vendors = self.validation_results["vendors_structure"]
        if vendors["exists"]:
            print(f"📦 Vendors: {len(vendors['found_vendors'])}/{len(vendors['expected_vendors'])} repos found")
        else:
            print("📦 Vendors: ❌ Directory not found")
            
        # Engines
        engines = self.validation_results["engines_structure"]
        if engines["exists"]:
            print(f"⚙️ Engines: Structure validation completed")
        else:
            print("⚙️ Engines: ❌ Directory not found")
            
        # Requirements
        req_consolidated = self.validation_results["requirements_consolidation"]["consolidated_file_exists"]
        old_removed = len(self.validation_results["requirements_consolidation"]["old_files_removed"])
        print(f"📋 Requirements: {'✅' if req_consolidated else '❌'} Consolidated, {old_removed} old files removed")
        
        # Issues
        if self.validation_results["issues"]:
            print(f"\n❌ Issues Found ({len(self.validation_results['issues'])}):")
            for issue in self.validation_results["issues"]:
                print(f"   • {issue}")
                
        # Recommendations  
        if self.validation_results["recommendations"]:
            print(f"\n💡 Recommendations ({len(self.validation_results['recommendations'])}):")
            for rec in self.validation_results["recommendations"]:
                print(f"   • {rec}")
                
        print("="*80)
        
    def save_validation_report(self, filename: str = None):
        """Spara validerings-rapport till fil"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repo_reorganization_validation_{timestamp}.json"
            
        report_path = self.project_root / filename
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
                
            logger.info(f"💾 Validation report saved: {filename}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"❌ Failed to save validation report: {str(e)}")
            return None

def main():
    """Main function"""
    
    # Automatisk detektering av project root
    current_dir = Path(__file__).parent
    
    # Kör validering
    validator = RepoReorganizationValidator(str(current_dir))
    results = validator.run_full_validation()
    
    # Spara rapport
    validator.save_validation_report()
    
    # Exit med rätt kod
    if results["validation_status"] == "SUCCESS":
        exit(0)
    elif results["validation_status"] == "WARNING":
        exit(1)
    else:
        exit(2)

if __name__ == "__main__":
    main()
