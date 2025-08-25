#!/usr/bin/env python3
"""
ECaDP Project Structure Analysis
Compares actual implementation against ideal structure from Projektbeskrivning.txt Chapter 24.1
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, asdict

@dataclass
class AnalysisResult:
    total_files: int
    implemented_files: int
    stub_files: int
    missing_files: int
    implementation_percentage: float
    critical_missing: List[str]
    priority_recommendations: List[str]

class ProjectAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = {}
        
    def analyze_directory_structure(self) -> Dict:
        """Analyze the current directory structure"""
        structure = {}
        for root, dirs, files in os.walk(self.project_root):
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path == '.':
                rel_path = ''
            
            structure[rel_path] = {
                'directories': dirs.copy(),
                'files': files.copy(),
                'total_files': len(files),
                'python_files': [f for f in files if f.endswith('.py')],
                'config_files': [f for f in files if f.endswith(('.yml', '.yaml', '.json', '.toml'))],
                'doc_files': [f for f in files if f.endswith(('.md', '.rst', '.txt'))]
            }
        
        return structure
    
    def analyze_code_implementation(self) -> Dict:
        """Analyze implementation status of Python modules"""
        src_path = self.project_root / 'src'
        if not src_path.exists():
            return {'error': 'src directory not found'}
        
        modules = {}
        for module_dir in src_path.iterdir():
            if module_dir.is_dir() and not module_dir.name.startswith('__'):
                module_info = self._analyze_module(module_dir)
                modules[module_dir.name] = module_info
        
        return modules
    
    def _analyze_module(self, module_path: Path) -> Dict:
        """Analyze a single module's implementation status"""
        files = list(module_path.glob('**/*.py'))
        
        analysis = {
            'total_files': len(files),
            'files': {},
            'implementation_status': 'unknown'
        }
        
        implemented_count = 0
        stub_count = 0
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check implementation status
                lines = content.split('\n')
                non_empty_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                
                is_stub = False
                if len(non_empty_lines) <= 3:  # Very minimal files
                    is_stub = True
                elif 'TODO' in content and 'pass' in content:
                    is_stub = True
                elif content.count('pass') > content.count('def') + content.count('class'):
                    is_stub = True
                
                file_info = {
                    'path': str(file_path.relative_to(self.project_root)),
                    'lines': len(lines),
                    'non_empty_lines': len(non_empty_lines),
                    'is_stub': is_stub,
                    'has_todos': 'TODO' in content,
                    'has_classes': 'class ' in content,
                    'has_functions': 'def ' in content,
                    'imports': len([line for line in lines if line.strip().startswith(('import ', 'from '))])
                }
                
                if is_stub:
                    stub_count += 1
                else:
                    implemented_count += 1
                
                analysis['files'][file_path.name] = file_info
                
            except Exception as e:
                analysis['files'][file_path.name] = {'error': str(e)}
        
        # Determine overall module status
        if implemented_count == 0:
            analysis['implementation_status'] = 'stub'
        elif stub_count == 0:
            analysis['implementation_status'] = 'implemented'
        else:
            analysis['implementation_status'] = 'partial'
        
        analysis['implemented_files'] = implemented_count
        analysis['stub_files'] = stub_count
        
        return analysis
    
    def check_critical_files(self) -> Dict:
        """Check for existence of critical project files"""
        critical_files = {
            # Core Python modules
            'src/__init__.py': 'Core package initialization',
            'src/utils/__init__.py': 'Utilities module',
            'src/proxy_pool/__init__.py': 'Proxy pool management',
            'src/anti_bot/__init__.py': 'Anti-bot detection',
            'src/crawler/__init__.py': 'Web crawler engine',
            'src/scraper/__init__.py': 'Data scraper',
            'src/database/__init__.py': 'Database layer',
            'src/scheduler/__init__.py': 'Task scheduler',
            'src/webapp/__init__.py': 'Web application',
            'src/analysis/__init__.py': 'Data analysis',
            
            # Configuration
            'config/app_config.yml': 'Main application configuration',
            'config/logging.yml': 'Logging configuration',
            'config/anti_bot.yml': 'Anti-bot configuration',
            
            # Infrastructure
            'docker/Dockerfile': 'Docker container definition',
            'docker/docker-compose.yml': 'Docker composition',
            'k8s/helm/Chart.yaml': 'Kubernetes Helm chart',
            
            # Database
            'supabase/migrations/001_initial_schema.sql': 'Database schema',
            
            # Testing
            'tests/conftest.py': 'Test configuration',
            'tests/unit/__init__.py': 'Unit tests',
            'tests/integration/__init__.py': 'Integration tests',
            
            # Documentation
            'docs/api_documentation.md': 'API documentation',
            'docs/architecture.md': 'Architecture documentation',
            'README.md': 'Project readme'
        }
        
        status = {}
        for file_path, description in critical_files.items():
            full_path = self.project_root / file_path
            status[file_path] = {
                'exists': full_path.exists(),
                'description': description,
                'is_directory': full_path.is_dir() if full_path.exists() else False,
                'size': full_path.stat().st_size if full_path.exists() and full_path.is_file() else 0
            }
        
        return status
    
    def generate_recommendations(self, code_analysis: Dict, critical_files: Dict) -> List[str]:
        """Generate prioritized implementation recommendations"""
        recommendations = []
        
        # Check for completely missing modules
        stub_modules = [name for name, info in code_analysis.items() 
                       if info.get('implementation_status') == 'stub']
        
        if stub_modules:
            recommendations.append(f"🚨 CRITICAL: Implement core modules: {', '.join(stub_modules[:3])}")
        
        # Check for missing critical files
        missing_critical = [path for path, info in critical_files.items() 
                           if not info['exists']]
        
        if missing_critical:
            recommendations.append(f"📋 HIGH: Create missing critical files: {len(missing_critical)} files")
        
        # Check database setup
        if not critical_files.get('supabase/migrations/001_initial_schema.sql', {}).get('exists'):
            recommendations.append("🗄️ HIGH: Set up database schema and migrations")
        
        # Check testing setup
        test_files = [path for path in critical_files.keys() if 'test' in path]
        missing_tests = [path for path in test_files if not critical_files[path]['exists']]
        if missing_tests:
            recommendations.append("🧪 MEDIUM: Set up testing infrastructure")
        
        # Check documentation
        doc_files = [path for path in critical_files.keys() if path.startswith('docs/')]
        missing_docs = [path for path in doc_files if not critical_files[path]['exists']]
        if missing_docs:
            recommendations.append("📚 MEDIUM: Complete project documentation")
        
        return recommendations[:10]  # Top 10 recommendations
    
    def run_complete_analysis(self) -> Dict:
        """Run complete project analysis"""
        print("🔍 Starting ECaDP Project Structure Analysis...")
        
        # 1. Directory structure
        print("📁 Analyzing directory structure...")
        dir_structure = self.analyze_directory_structure()
        
        # 2. Code implementation
        print("🐍 Analyzing Python code implementation...")
        code_analysis = self.analyze_code_implementation()
        
        # 3. Critical files
        print("📋 Checking critical files...")
        critical_files = self.check_critical_files()
        
        # 4. Generate recommendations
        print("💡 Generating recommendations...")
        recommendations = self.generate_recommendations(code_analysis, critical_files)
        
        # 5. Calculate overall metrics
        total_files = sum(info.get('total_files', 0) for info in code_analysis.values())
        implemented_files = sum(info.get('implemented_files', 0) for info in code_analysis.values())
        stub_files = sum(info.get('stub_files', 0) for info in code_analysis.values())
        
        implementation_percentage = (implemented_files / total_files * 100) if total_files > 0 else 0
        
        result = AnalysisResult(
            total_files=total_files,
            implemented_files=implemented_files,
            stub_files=stub_files,
            missing_files=len([path for path, info in critical_files.items() if not info['exists']]),
            implementation_percentage=implementation_percentage,
            critical_missing=[path for path, info in critical_files.items() if not info['exists']],
            priority_recommendations=recommendations
        )
        
        return {
            'summary': asdict(result),
            'directory_structure': dir_structure,
            'code_analysis': code_analysis,
            'critical_files': critical_files,
            'recommendations': recommendations
        }

def main():
    """Main analysis function"""
    project_root = os.getcwd()
    analyzer = ProjectAnalyzer(project_root)
    
    try:
        results = analyzer.run_complete_analysis()
        
        # Print summary
        print("\n" + "="*80)
        print("📊 ECaDP PROJECT ANALYSIS SUMMARY")
        print("="*80)
        
        summary = results['summary']
        print(f"📁 Total Python files: {summary['total_files']}")
        print(f"✅ Implemented files: {summary['implemented_files']}")
        print(f"⚠️  Stub files: {summary['stub_files']}")
        print(f"❌ Missing critical files: {summary['missing_files']}")
        print(f"📈 Implementation progress: {summary['implementation_percentage']:.1f}%")
        
        print(f"\n🚨 CRITICAL MISSING FILES ({len(summary['critical_missing'])}):")
        for file_path in summary['critical_missing'][:10]:
            print(f"   • {file_path}")
        
        print(f"\n💡 PRIORITY RECOMMENDATIONS:")
        for i, rec in enumerate(summary['priority_recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n📋 MODULE IMPLEMENTATION STATUS:")
        for module, info in results['code_analysis'].items():
            status = info.get('implementation_status', 'unknown')
            emoji = {"implemented": "✅", "partial": "🔄", "stub": "⚠️", "unknown": "❓"}
            print(f"   {emoji.get(status, '❓')} {module}: {status} ({info.get('implemented_files', 0)}/{info.get('total_files', 0)} files)")
        
        # Save detailed results
        output_file = Path(project_root) / 'analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        print("\n✨ Analysis complete!")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
