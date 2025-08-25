#!/usr/bin/env python3
"""
File Organization Validation Script

Validates the pyramid architecture file organization:
- Checks directory structure 
- Validates file locations
- Verifies import statements
- Reports any issues or inconsistencies
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast
import importlib.util
import json
from datetime import datetime

# Expected directory structure for pyramid architecture
EXPECTED_STRUCTURE = {
    'core': {
        'orchestration': ['main.py'],
        'utils': ['__init__.py', 'orchestration.py', 'config_manager.py', 'health_checker.py'],
        'models': []
    },
    'shared': {
        'models': ['__init__.py', 'base.py'],
        'utils': ['__init__.py', 'helpers.py'],
        'types': [],
        'libraries': [],
        'scripts': []
    },
    'engines': {
        'scraping': ['__init__.py', 'core_framework.py'],
        'pentesting': ['__init__.py', 'osint_framework.py'],
        'bypass': []
    },
    'agents': {
        'crew': ['__init__.py', 'scraping_specialist.py'],
        'coordination': []
    },
    'processing': {
        'data': [],
        'analysis': [],
        'export': []
    },
    'integrations': {
        'swedish': [],
        'external': []
    },
    'api': {
        'rest': ['__init__.py', 'crawler_api.py', 'revolutionary_api.py', 'health_api.py'],
        'graphql': []
    },
    'deployment': {
        'docker': [],
        'kubernetes': [],
        'scripts': ['start_backend.py', 'start_platform.ps1', 'start_platform.sh']
    },
    'config': {
        'environments': [],
        'templates': ['config_template.py'],
        'setup': ['pyramid_setup.py'],
        'services.yaml': None  # File in config root
    },
    'docs': {
        'getting-started': [],
        'api-reference': [],
        'examples': []
    }
}

class PyramidValidator:
    """Validates pyramid architecture organization"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def validate_structure(self) -> Dict[str, any]:
        """Validate the complete pyramid structure"""
        
        print("🔍 Validating Pyramid Architecture Structure...")
        print(f"📁 Project Root: {self.project_root}")
        print("-" * 60)
        
        # Check directory structure
        self._check_directory_structure()
        
        # Check core files
        self._check_core_files()
        
        # Check file organization
        self._check_file_organization()
        
        # Check imports (basic)
        self._check_basic_imports()
        
        # Generate report
        return self._generate_report()
    
    def _check_directory_structure(self):
        """Check if expected directories exist"""
        
        print("📂 Checking Directory Structure...")
        
        def check_dir_recursive(expected: Dict, current_path: Path, level: int = 0):
            indent = "  " * level
            
            for dir_name, contents in expected.items():
                if dir_name.endswith('.yaml') or dir_name.endswith('.py'):
                    # This is a file, not a directory
                    file_path = current_path / dir_name
                    self.total_checks += 1
                    
                    if file_path.exists():
                        print(f"{indent}✅ {dir_name}")
                        self.success_count += 1
                    else:
                        print(f"{indent}❌ {dir_name} (missing)")
                        self.issues.append(f"Missing file: {file_path}")
                    continue
                
                dir_path = current_path / dir_name
                self.total_checks += 1
                
                if dir_path.exists() and dir_path.is_dir():
                    print(f"{indent}✅ {dir_name}/")
                    self.success_count += 1
                    
                    # Check contents
                    if isinstance(contents, dict):
                        check_dir_recursive(contents, dir_path, level + 1)
                    elif isinstance(contents, list):
                        for file_name in contents:
                            file_path = dir_path / file_name
                            self.total_checks += 1
                            
                            if file_path.exists():
                                print(f"{indent}  ✅ {file_name}")
                                self.success_count += 1
                            else:
                                print(f"{indent}  ❌ {file_name} (missing)")
                                self.issues.append(f"Missing file: {file_path}")
                else:
                    print(f"{indent}❌ {dir_name}/ (missing directory)")
                    self.issues.append(f"Missing directory: {dir_path}")
        
        check_dir_recursive(EXPECTED_STRUCTURE, self.project_root)
        print()
    
    def _check_core_files(self):
        """Check critical core files"""
        
        print("🏗️ Checking Core Files...")
        
        critical_files = [
            'core/orchestration/main.py',
            'shared/models/base.py',
            'shared/utils/helpers.py',
            'config/services.yaml'
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            self.total_checks += 1
            
            if full_path.exists():
                # Check if file is not empty
                if full_path.stat().st_size > 0:
                    print(f"✅ {file_path}")
                    self.success_count += 1
                else:
                    print(f"⚠️  {file_path} (empty)")
                    self.warnings.append(f"Empty file: {file_path}")
            else:
                print(f"❌ {file_path} (missing)")
                self.issues.append(f"Critical file missing: {file_path}")
        
        print()
    
    def _check_file_organization(self):
        """Check if files are in correct locations"""
        
        print("📋 Checking File Organization...")
        
        # Check for files that should have been moved
        old_locations = {
            'api/crawler.py': 'Should be moved to api/rest/crawler_api.py',
            'api/revolutionary-crawler.py': 'Should be moved to api/rest/revolutionary_api.py',
            'config_template.py': 'Should be moved to config/templates/',
            'setup_pyramid_config.py': 'Should be moved to config/setup/',
            'scripts/': 'Should be moved to shared/scripts/',
            'lib/': 'Should be moved to shared/libraries/'
        }
        
        for old_path, suggestion in old_locations.items():
            full_path = self.project_root / old_path
            self.total_checks += 1
            
            if full_path.exists():
                print(f"⚠️  {old_path} still exists - {suggestion}")
                self.warnings.append(f"File not moved: {old_path} - {suggestion}")
            else:
                print(f"✅ {old_path} correctly moved")
                self.success_count += 1
        
        print()
    
    def _check_basic_imports(self):
        """Check basic import statements in key files"""
        
        print("🔗 Checking Import Statements...")
        
        import_checks = [
            {
                'file': 'core/orchestration/main.py',
                'expected_imports': ['fastapi', 'shared.models.base', 'shared.utils.helpers']
            },
            {
                'file': 'api/rest/health_api.py',
                'expected_imports': ['fastapi', 'core.utils.orchestration']
            }
        ]
        
        for check in import_checks:
            file_path = self.project_root / check['file']
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic string check for imports (not AST parsing for simplicity)
                for expected_import in check['expected_imports']:
                    self.total_checks += 1
                    
                    # Check if import exists (basic string search)
                    import_variants = [
                        f"import {expected_import}",
                        f"from {expected_import}",
                        expected_import.replace('.', '/')  # path-style check
                    ]
                    
                    found = any(variant in content for variant in import_variants)
                    
                    if found:
                        print(f"✅ {check['file']}: {expected_import}")
                        self.success_count += 1
                    else:
                        print(f"⚠️  {check['file']}: {expected_import} (may need updating)")
                        self.warnings.append(f"Import may need updating in {check['file']}: {expected_import}")
                        
            except Exception as e:
                print(f"❌ Error checking {check['file']}: {e}")
                self.issues.append(f"Could not check imports in {check['file']}: {e}")
        
        print()
    
    def _generate_report(self) -> Dict[str, any]:
        """Generate validation report"""
        
        success_rate = (self.success_count / self.total_checks * 100) if self.total_checks > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'total_checks': self.total_checks,
            'successful_checks': self.success_count,
            'success_rate': round(success_rate, 2),
            'issues': self.issues,
            'warnings': self.warnings,
            'status': 'PASSED' if len(self.issues) == 0 else 'FAILED'
        }
        
        return report


def main():
    """Main validation function"""
    
    # Get project root (current directory)
    project_root = Path.cwd()
    
    # Initialize validator
    validator = PyramidValidator(project_root)
    
    # Run validation
    report = validator.validate_structure()
    
    # Print summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total Checks: {report['total_checks']}")
    print(f"Successful: {report['successful_checks']}")
    print(f"Success Rate: {report['success_rate']}%")
    print(f"Issues: {len(report['issues'])}")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"Status: {report['status']}")
    print()
    
    # Print issues
    if report['issues']:
        print("🚨 ISSUES FOUND:")
        for i, issue in enumerate(report['issues'], 1):
            print(f"  {i}. {issue}")
        print()
    
    # Print warnings  
    if report['warnings']:
        print("⚠️  WARNINGS:")
        for i, warning in enumerate(report['warnings'], 1):
            print(f"  {i}. {warning}")
        print()
    
    # Save report
    report_file = project_root / 'pyramid_validation_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Full report saved to: {report_file}")
    
    # Return exit code
    return 0 if report['status'] == 'PASSED' else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
