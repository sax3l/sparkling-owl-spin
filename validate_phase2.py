#!/usr/bin/env python3
"""
Phase 2 Reorganization Validation Script
Validates the completed file reorganization according to Swedish instructions
"""

import os
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime


class ReorganizationValidator:
    """Validates Phase 2 reorganization completion"""
    
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.validation_results = {
            "phase": "Phase 2 - File Reorganization",
            "timestamp": datetime.now().isoformat(),
            "validations": {},
            "summary": {}
        }
        
    def validate_docker_reorganization(self) -> Dict[str, Any]:
        """Validate Docker file reorganization"""
        docker_files = {
            "deployment/docker/compose.yml": "docker-compose.yml moved",
            "deployment/docker/compose-backend.yml": "docker-compose.backend.yml moved", 
            "deployment/docker/compose-complete-v4.yml": "docker-compose-complete-v4.yml moved"
        }
        
        results = {
            "category": "Docker File Reorganization",
            "expected_files": len(docker_files),
            "found_files": 0,
            "missing_files": [],
            "status": "PASS"
        }
        
        for file_path, description in docker_files.items():
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["found_files"] += 1
            else:
                results["missing_files"].append(f"{file_path} ({description})")
        
        if results["missing_files"]:
            results["status"] = "FAIL"
            
        return results
    
    def validate_config_reorganization(self) -> Dict[str, Any]:
        """Validate configuration file reorganization"""
        config_files = {
            "config/env.example": ".env.example moved",
            "config/pre-commit-config.yaml": ".pre-commit-config.yaml moved",
            "config/services.yaml": "Consolidated config file"
        }
        
        results = {
            "category": "Configuration File Reorganization", 
            "expected_files": len(config_files),
            "found_files": 0,
            "missing_files": [],
            "status": "PASS"
        }
        
        for file_path, description in config_files.items():
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["found_files"] += 1
            else:
                results["missing_files"].append(f"{file_path} ({description})")
        
        if results["missing_files"]:
            results["status"] = "FAIL"
            
        return results
    
    def validate_api_reorganization(self) -> Dict[str, Any]:
        """Validate API file reorganization"""
        api_files = {
            "api/rest/health.py": "api/health.py moved",
            "api/rest/monitoring.py": "api/monitoring.py moved",
            "api/rest/proxy_api.py": "api/proxy.py moved and renamed",
            "api/rest/server.py": "Consolidated API server"
        }
        
        results = {
            "category": "API File Reorganization",
            "expected_files": len(api_files),
            "found_files": 0,
            "missing_files": [],
            "status": "PASS"
        }
        
        for file_path, description in api_files.items():
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["found_files"] += 1
            else:
                results["missing_files"].append(f"{file_path} ({description})")
        
        if results["missing_files"]:
            results["status"] = "FAIL"
            
        return results
    
    def validate_core_reorganization(self) -> Dict[str, Any]:
        """Validate core file reorganization"""
        core_files = {
            "core/orchestrator.py": "main_pyramid.py moved",
            "core/utils/helpers.py": "Consolidated utility functions"
        }
        
        results = {
            "category": "Core File Reorganization",
            "expected_files": len(core_files),
            "found_files": 0,
            "missing_files": [],
            "status": "PASS"
        }
        
        for file_path, description in core_files.items():
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["found_files"] += 1
            else:
                results["missing_files"].append(f"{file_path} ({description})")
        
        if results["missing_files"]:
            results["status"] = "FAIL"
            
        return results
    
    def validate_engines_integration(self) -> Dict[str, Any]:
        """Validate engine service integration"""
        engine_files = {
            "engines/bypass/aws_ip_rotator.py": "AWS IP Rotator service",
            "engines/bypass/test_aws_rotator.py": "AWS IP Rotator tests",
            "engines/scraping/web_scraper.py": "Consolidated web scraper"
        }
        
        results = {
            "category": "Engine Service Integration",
            "expected_files": len(engine_files),
            "found_files": 0,
            "missing_files": [],
            "status": "PASS"
        }
        
        for file_path, description in engine_files.items():
            full_path = os.path.join(self.root_path, file_path)
            if os.path.exists(full_path):
                results["found_files"] += 1
            else:
                results["missing_files"].append(f"{file_path} ({description})")
        
        if results["missing_files"]:
            results["status"] = "FAIL"
            
        return results
    
    def validate_cleanup_operations(self) -> Dict[str, Any]:
        """Validate cleanup operations"""
        removed_files = [
            "config.yaml",
            "config/local.yaml", 
            "api/server.py",
            "api/main.py",
            "api/app.py",
            "main_pyramid.py",
            "scrapers/",
            "utils/"
        ]
        
        results = {
            "category": "Cleanup Operations",
            "expected_removed": len(removed_files),
            "actually_removed": 0,
            "still_exists": [],
            "status": "PASS"
        }
        
        for file_path in removed_files:
            full_path = os.path.join(self.root_path, file_path)
            if not os.path.exists(full_path):
                results["actually_removed"] += 1
            else:
                results["still_exists"].append(file_path)
        
        if results["still_exists"]:
            results["status"] = "PARTIAL"
            
        return results
    
    def validate_pyramid_structure(self) -> Dict[str, Any]:
        """Validate pyramid directory structure"""
        pyramid_dirs = [
            "core/",
            "engines/",
            "engines/bypass/",
            "engines/scraping/", 
            "engines/processing/",
            "engines/storage/",
            "api/",
            "api/rest/",
            "shared/",
            "shared/models/",
            "shared/utils/",
            "deployment/",
            "deployment/docker/",
            "config/"
        ]
        
        results = {
            "category": "Pyramid Structure Validation",
            "expected_dirs": len(pyramid_dirs),
            "found_dirs": 0,
            "missing_dirs": [],
            "status": "PASS"
        }
        
        for dir_path in pyramid_dirs:
            full_path = os.path.join(self.root_path, dir_path)
            if os.path.isdir(full_path):
                results["found_dirs"] += 1
            else:
                results["missing_dirs"].append(dir_path)
        
        if results["missing_dirs"]:
            results["status"] = "FAIL"
            
        return results
    
    def run_validation(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🔍 Running Phase 2 Reorganization Validation...")
        print(f"📁 Root path: {self.root_path}")
        print("=" * 60)
        
        # Run all validation checks
        validations = [
            ("docker_reorganization", self.validate_docker_reorganization),
            ("config_reorganization", self.validate_config_reorganization), 
            ("api_reorganization", self.validate_api_reorganization),
            ("core_reorganization", self.validate_core_reorganization),
            ("engines_integration", self.validate_engines_integration),
            ("cleanup_operations", self.validate_cleanup_operations),
            ("pyramid_structure", self.validate_pyramid_structure)
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
            
            if result.get("missing_files"):
                for missing in result["missing_files"]:
                    print(f"   📄 Missing: {missing}")
                    
            if result.get("missing_dirs"):
                for missing in result["missing_dirs"]:
                    print(f"   📁 Missing: {missing}")
                    
            if result.get("still_exists"):
                for exists in result["still_exists"]:
                    print(f"   🗑️ Should be removed: {exists}")
            
            print()
        
        # Generate summary
        success_rate = (passed_checks / total_checks) * 100
        self.validation_results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks, 
            "success_rate": success_rate,
            "overall_status": "PASS" if success_rate >= 80 else "FAIL"
        }
        
        print("=" * 60)
        print(f"📊 Validation Summary:")
        print(f"   Total checks: {total_checks}")
        print(f"   Passed: {passed_checks}")
        print(f"   Success rate: {success_rate:.1f}%")
        
        status_emoji = "✅" if success_rate >= 80 else "❌"
        print(f"   {status_emoji} Overall status: {self.validation_results['summary']['overall_status']}")
        
        return self.validation_results
    
    def save_results(self, output_file: str = "phase2_validation_results.json"):
        """Save validation results to file"""
        output_path = os.path.join(self.root_path, output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Validation results saved to: {output_path}")


def main():
    """Main validation function"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    
    validator = ReorganizationValidator(root_path)
    results = validator.run_validation()
    validator.save_results()
    
    return results["summary"]["overall_status"] == "PASS"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
