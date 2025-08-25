#!/usr/bin/env python3
"""
Phase 3 Complete Structure Validation Script
Validates the complete pyramid structure according to Swedish reorganization instructions
"""

import os
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime


class CompleteStructureValidator:
    """Validates the complete reorganized structure"""
    
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.validation_results = {
            "phase": "Phase 3 - Complete Structure Validation",
            "timestamp": datetime.now().isoformat(),
            "validations": {},
            "summary": {}
        }
        
        # Complete pyramid structure as specified in Swedish instructions
        self.required_structure = {
            "core/": [
                "orchestrator.py",
                "utils/helpers.py"
            ],
            "engines/": [
                "bypass/aws_ip_rotator.py",
                "bypass/test_aws_rotator.py",
                "scraping/web_scraper.py",
                "processing/__init__.py", 
                "storage/__init__.py"
            ],
            "agents/": [
                "__init__.py",
                "crew/"
            ],
            "processing/": [
                "__init__.py"
            ],
            "api/": [
                "rest/server.py",
                "rest/health.py", 
                "rest/monitoring.py",
                "rest/proxy_api.py",
                "websocket/",
                "graphql/"
            ],
            "config/": [
                "services.yaml",
                "env.example",
                "pre-commit-config.yaml"
            ],
            "vendors/": [],
            "sandbox/": [],
            "integrations/": [
                "swedish/__init__.py"
            ],
            "shared/": [
                "models/base.py",
                "utils/helpers.py",
                "types/"
            ],
            "tests/": [
                "unit/",
                "integration/"
            ],
            "deployment/": [
                "docker/compose.yml",
                "docker/compose-backend.yml", 
                "docker/compose-complete-v4.yml",
                "docker/Dockerfile"
            ],
            "docs/": [
                "getting-started/",
                "api-reference/",
                "examples/"
            ]
        }
        
        # Files that should be consolidated/removed
        self.removed_files = [
            "config.yaml",
            "config/local.yaml",
            "api/server.py",
            "api/main.py", 
            "api/app.py",
            "main_pyramid.py",
            "scrapers/",
            "utils/",
            "aws_ip_rotator_integration.py"  # Should use engines/bypass/aws_ip_rotator.py
        ]
        
    def validate_complete_structure(self) -> Dict[str, Any]:
        """Validate the complete pyramid structure"""
        
        results = {
            "category": "Complete Pyramid Structure",
            "expected_dirs": 0,
            "found_dirs": 0,
            "expected_files": 0,
            "found_files": 0,
            "missing_items": [],
            "status": "PASS"
        }
        
        for dir_path, expected_files in self.required_structure.items():
            dir_full_path = os.path.join(self.root_path, dir_path)
            results["expected_dirs"] += 1
            
            if os.path.isdir(dir_full_path):
                results["found_dirs"] += 1
                
                # Check files in directory
                for file_path in expected_files:
                    results["expected_files"] += 1
                    file_full_path = os.path.join(self.root_path, dir_path, file_path)
                    
                    if os.path.exists(file_full_path):
                        results["found_files"] += 1
                    else:
                        results["missing_items"].append(f"{dir_path}{file_path}")
            else:
                results["missing_items"].append(dir_path)
        
        if results["missing_items"]:
            results["status"] = "FAIL"
        
        return results
    
    def validate_file_consolidation(self) -> Dict[str, Any]:
        """Validate that files have been properly consolidated"""
        
        results = {
            "category": "File Consolidation and Cleanup",
            "expected_removed": len(self.removed_files),
            "actually_removed": 0,
            "still_exists": [],
            "consolidation_success": [],
            "status": "PASS"
        }
        
        # Check removed files
        for file_path in self.removed_files:
            full_path = os.path.join(self.root_path, file_path)
            if not os.path.exists(full_path):
                results["actually_removed"] += 1
            else:
                results["still_exists"].append(file_path)
        
        # Check consolidation success
        consolidations = [
            ("config/services.yaml", "Configuration consolidated"),
            ("core/utils/helpers.py", "Utilities consolidated"),
            ("engines/scraping/web_scraper.py", "Scraper consolidated"),
            ("api/rest/server.py", "API server consolidated")
        ]
        
        for file_path, description in consolidations:
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["consolidation_success"].append(f"{file_path}: {description}")
        
        if results["still_exists"]:
            results["status"] = "PARTIAL"
        
        return results
    
    def validate_swedish_integration(self) -> Dict[str, Any]:
        """Validate Swedish integration setup"""
        
        swedish_files = [
            "integrations/swedish/__init__.py",
            "test_aws_integration.py"  # Should be updated for new structure
        ]
        
        results = {
            "category": "Swedish Integration",
            "expected_files": len(swedish_files),
            "found_files": 0,
            "missing_files": [],
            "integration_features": [],
            "status": "PASS"
        }
        
        for file_path in swedish_files:
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["found_files"] += 1
                
                # Check for Swedish integration features
                if file_path == "integrations/swedish/__init__.py":
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'personnummer' in content:
                                results["integration_features"].append("Personnummer validation")
                            if 'organisationsnummer' in content:
                                results["integration_features"].append("Organisationsnummer validation")
                            if 'swedish_domains' in content:
                                results["integration_features"].append("Swedish domain detection")
                    except Exception as e:
                        pass
            else:
                results["missing_files"].append(file_path)
        
        if results["missing_files"]:
            results["status"] = "FAIL"
        
        return results
    
    def validate_service_integration(self) -> Dict[str, Any]:
        """Validate service integration and imports"""
        
        key_services = [
            "engines/bypass/aws_ip_rotator.py",
            "engines/scraping/web_scraper.py", 
            "agents/__init__.py",
            "processing/__init__.py",
            "integrations/swedish/__init__.py"
        ]
        
        results = {
            "category": "Service Integration",
            "expected_services": len(key_services),
            "found_services": 0,
            "import_issues": [],
            "service_features": [],
            "status": "PASS"
        }
        
        for service_path in key_services:
            full_path = os.path.join(self.root_path, service_path)
            if os.path.exists(full_path):
                results["found_services"] += 1
                
                # Check for proper imports and service patterns
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        if 'from shared.models.base import BaseService' in content:
                            results["service_features"].append(f"{service_path}: BaseService inheritance")
                        
                        if 'async def start(' in content:
                            results["service_features"].append(f"{service_path}: Async service lifecycle")
                        
                        if 'ServiceStatus' in content:
                            results["service_features"].append(f"{service_path}: Service status management")
                            
                except Exception as e:
                    results["import_issues"].append(f"{service_path}: {str(e)}")
            else:
                results["import_issues"].append(f"Missing service: {service_path}")
        
        if results["import_issues"]:
            results["status"] = "PARTIAL"
        
        return results
    
    def validate_documentation_structure(self) -> Dict[str, Any]:
        """Validate documentation structure"""
        
        doc_dirs = [
            "docs/getting-started/",
            "docs/api-reference/",
            "docs/examples/"
        ]
        
        results = {
            "category": "Documentation Structure",
            "expected_dirs": len(doc_dirs),
            "found_dirs": 0,
            "missing_dirs": [],
            "status": "PASS"
        }
        
        for doc_dir in doc_dirs:
            full_path = os.path.join(self.root_path, doc_dir)
            if os.path.isdir(full_path):
                results["found_dirs"] += 1
            else:
                results["missing_dirs"].append(doc_dir)
        
        if results["missing_dirs"]:
            results["status"] = "FAIL"
        
        return results
    
    def run_validation(self) -> Dict[str, Any]:
        """Run complete structure validation"""
        print("🔍 Running Complete Structure Validation...")
        print(f"📁 Root path: {self.root_path}")
        print("=" * 70)
        
        # Run all validation checks
        validations = [
            ("complete_structure", self.validate_complete_structure),
            ("file_consolidation", self.validate_file_consolidation),
            ("swedish_integration", self.validate_swedish_integration),
            ("service_integration", self.validate_service_integration),
            ("documentation_structure", self.validate_documentation_structure)
        ]
        
        total_checks = 0
        passed_checks = 0
        
        for check_name, check_func in validations:
            result = check_func()
            self.validation_results["validations"][check_name] = result
            
            total_checks += 1
            if result["status"] in ["PASS", "PARTIAL"]:
                passed_checks += 1
            
            # Print result
            status_emoji = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
            print(f"{status_emoji} {result['category']}: {result['status']}")
            
            # Print details
            if result.get("missing_items"):
                for missing in result["missing_items"][:5]:  # Show first 5
                    print(f"   📄 Missing: {missing}")
                if len(result["missing_items"]) > 5:
                    print(f"   ... and {len(result['missing_items']) - 5} more")
            
            if result.get("missing_files"):
                for missing in result["missing_files"]:
                    print(f"   📄 Missing: {missing}")
            
            if result.get("missing_dirs"):
                for missing in result["missing_dirs"]:
                    print(f"   📁 Missing: {missing}")
            
            if result.get("still_exists"):
                for exists in result["still_exists"][:3]:
                    print(f"   🗑️ Should be removed: {exists}")
            
            if result.get("consolidation_success"):
                for success in result["consolidation_success"][:3]:
                    print(f"   ✅ {success}")
            
            if result.get("service_features"):
                for feature in result["service_features"][:3]:
                    print(f"   🔧 {feature}")
            
            if result.get("integration_features"):
                for feature in result["integration_features"]:
                    print(f"   🇸🇪 {feature}")
            
            print()
        
        # Generate summary
        success_rate = (passed_checks / total_checks) * 100
        self.validation_results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "success_rate": success_rate,
            "overall_status": "PASS" if success_rate >= 80 else "FAIL",
            "pyramid_structure_complete": success_rate >= 90
        }
        
        print("=" * 70)
        print(f"📊 Complete Structure Validation Summary:")
        print(f"   Total checks: {total_checks}")
        print(f"   Passed: {passed_checks}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        status_emoji = "✅" if success_rate >= 80 else "❌"
        structure_emoji = "🏗️" if success_rate >= 90 else "⚠️"
        
        print(f"   {status_emoji} Overall status: {self.validation_results['summary']['overall_status']}")
        print(f"   {structure_emoji} Pyramid structure: {'COMPLETE' if success_rate >= 90 else 'PARTIAL'}")
        
        return self.validation_results
    
    def save_results(self, output_file: str = "complete_structure_validation.json"):
        """Save validation results to file"""
        output_path = os.path.join(self.root_path, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Complete validation results saved to: {output_path}")


def main():
    """Main validation function"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    validator = CompleteStructureValidator(root_path)
    results = validator.run_validation()
    validator.save_results()
    
    return results["summary"]["overall_status"] == "PASS"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
