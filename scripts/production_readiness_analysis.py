#!/usr/bin/env python3
"""
Production Readiness Analysis för ECaDP Platform
Analyserar vilka filer som faktiskt behöver implementeras för production enligt Projektbeskrivning.txt
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Any

class ProductionReadinessAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.critical_modules = {
            'anti_bot': {
                'description': 'Anti-bot detection and evasion - CRITICAL for avoiding blocks',
                'priority': 1,
                'production_critical': True
            },
            'crawler': {
                'description': 'Web crawling engine - CORE functionality', 
                'priority': 1,
                'production_critical': True
            },
            'scheduler': {
                'description': 'Job scheduling and orchestration - CORE functionality',
                'priority': 1,
                'production_critical': True
            },
            'scraper': {
                'description': 'Data extraction engine - CORE functionality',
                'priority': 1,
                'production_critical': True
            },
            'proxy_pool': {
                'description': 'Proxy management - CRITICAL for scale',
                'priority': 2,
                'production_critical': True
            },
            'webapp': {
                'description': 'Web interface and API',
                'priority': 2,
                'production_critical': True
            },
            'database': {
                'description': 'Data persistence layer',
                'priority': 2,
                'production_critical': True
            }
        }
        
    def analyze_file_completeness(self, filepath: Path) -> Tuple[str, int, Dict[str, Any]]:
        """Analysera om en Python-fil är en stub eller har riktig implementation"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        except Exception as e:
            return 'error', 0, {'error': str(e)}
        
        if not content:
            return 'empty', 0, {'reason': 'No content'}
        
        # Parse AST för att analysera innehåll
        try:
            tree = ast.parse(content)
        except Exception as e:
            return 'syntax_error', len(content), {'error': str(e)}
        
        # Räkna meningsfull innehåll
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node) if hasattr(ast, 'unparse') else 'import')
        
        meaningful_lines = len(functions) + len(classes) + len(imports)
        
        # Detektera stub-mönster
        pass_count = content.count('pass')
        ellipsis_count = content.count('...')
        todo_count = content.lower().count('todo') + content.lower().count('fixme')
        
        details = {
            'functions': functions,
            'classes': classes,
            'imports': len(imports),
            'pass_count': pass_count,
            'ellipsis_count': ellipsis_count,
            'todo_count': todo_count,
            'meaningful_lines': meaningful_lines
        }
        
        # Klassificera implementationsstatus
        if pass_count > meaningful_lines or ellipsis_count > 0:
            if len(content) < 300:
                return 'stub', len(content), details
        
        if len(content) < 150 and meaningful_lines < 3:
            return 'minimal', len(content), details
        
        if todo_count > 0 and len(content) < 500:
            return 'incomplete', len(content), details
            
        return 'implemented', len(content), details

    def analyze_production_readiness(self) -> Dict[str, Any]:
        """Analysera produktionsreadiness för kritiska moduler"""
        results = {}
        
        for module_name, module_info in self.critical_modules.items():
            module_path = self.project_root / 'src' / module_name
            if not module_path.exists():
                results[module_name] = {
                    'status': 'missing',
                    'description': module_info['description'],
                    'priority': module_info['priority'],
                    'files': []
                }
                continue
            
            files = []
            for filepath in module_path.rglob('*.py'):
                if filepath.name == '__init__.py':
                    continue
                    
                status, size, details = self.analyze_file_completeness(filepath)
                relative_path = filepath.relative_to(module_path)
                
                files.append({
                    'file': str(relative_path),
                    'path': str(filepath),
                    'status': status,
                    'size': size,
                    'details': details,
                    'production_critical': self._is_production_critical(module_name, filepath.name)
                })
            
            # Sortera efter produktionsviktighet och storlek
            files.sort(key=lambda x: (not x['production_critical'], x['size']))
            
            implemented = len([f for f in files if f['status'] == 'implemented'])
            stubs = len([f for f in files if f['status'] in ['stub', 'minimal', 'empty']])
            total = len(files)
            
            results[module_name] = {
                'description': module_info['description'],
                'priority': module_info['priority'],
                'production_critical': module_info['production_critical'],
                'files': files,
                'total_files': total,
                'implemented': implemented,
                'stubs': stubs,
                'implementation_rate': implemented / total * 100 if total > 0 else 0,
                'status': self._calculate_module_status(implemented, total, module_info['priority'])
            }
        
        return results

    def _is_production_critical(self, module_name: str, filename: str) -> bool:
        """Bestäm om en specifik fil är kritisk för production"""
        critical_files = {
            'anti_bot': ['header_generator.py', 'session_manager.py', 'delay_strategy.py'],
            'crawler': ['sitemap_generator.py', 'url_queue.py'],
            'scheduler': ['scheduler.py', 'job_definitions.py'],
            'scraper': ['base_scraper.py', 'http_scraper.py', 'template_runtime.py'],
            'proxy_pool': ['manager.py', 'collector.py', 'validator.py'],
            'webapp': ['app.py', 'api.py'],
            'database': ['models.py', 'manager.py']
        }
        
        return filename in critical_files.get(module_name, [])

    def _calculate_module_status(self, implemented: int, total: int, priority: int) -> str:
        """Beräkna modulens övergripande status"""
        if total == 0:
            return 'empty'
        
        rate = implemented / total
        
        if priority == 1:  # Kritiska moduler
            if rate >= 0.8:
                return 'production_ready'
            elif rate >= 0.5:
                return 'needs_work'
            else:
                return 'critical_missing'
        else:  # Mindre kritiska moduler
            if rate >= 0.7:
                return 'production_ready'
            elif rate >= 0.4:
                return 'needs_work'
            else:
                return 'critical_missing'

    def generate_implementation_plan(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generera en prioriterad implementationsplan"""
        tasks = []
        
        for module_name, module_data in analysis_results.items():
            if module_data['status'] == 'missing':
                tasks.append({
                    'priority': 0,
                    'type': 'create_module',
                    'module': module_name,
                    'description': f"Create missing module: {module_name}",
                    'effort': 'high'
                })
                continue
            
            # Hitta produktionskritiska stub-filer
            critical_stubs = [
                f for f in module_data['files'] 
                if f['production_critical'] and f['status'] in ['stub', 'minimal', 'empty']
            ]
            
            for file_info in critical_stubs:
                tasks.append({
                    'priority': module_data['priority'],
                    'type': 'implement_file',
                    'module': module_name,
                    'file': file_info['file'],
                    'path': file_info['path'],
                    'description': f"Implement {module_name}/{file_info['file']} - {module_data['description']}",
                    'current_size': file_info['size'],
                    'effort': self._estimate_effort(file_info)
                })
        
        # Sortera efter prioritet och effort
        tasks.sort(key=lambda x: (x['priority'], x['effort'] == 'high'))
        
        return tasks

    def _estimate_effort(self, file_info: Dict[str, Any]) -> str:
        """Estimera implementation effort baserat på filstorlek och innehåll"""
        if file_info['size'] < 50:
            return 'high'  # Helt tom, behöver full implementation
        elif file_info['size'] < 200:
            return 'medium'
        else:
            return 'low'  # Redan något innehåll

    def print_analysis_report(self, analysis_results: Dict[str, Any]):
        """Skriv ut en detaljerad analysrapport"""
        print("🎯 PRODUCTION READINESS ANALYSIS")
        print("=" * 50)
        
        # Övergripande status
        total_modules = len(analysis_results)
        ready_modules = len([m for m in analysis_results.values() if m.get('status') == 'production_ready'])
        
        print(f"📊 Overall Status: {ready_modules}/{total_modules} modules production ready")
        print()
        
        # Per modul
        for module_name, data in analysis_results.items():
            status_icon = {
                'production_ready': '🟢',
                'needs_work': '🟡', 
                'critical_missing': '🔴',
                'missing': '❌'
            }.get(data.get('status', 'unknown'), '❓')
            
            print(f"{status_icon} {module_name.upper()} - {data['description']}")
            
            if 'implementation_rate' in data:
                print(f"   📈 Implementation: {data['implemented']}/{data['total_files']} files ({data['implementation_rate']:.1f}%)")
                
                # Visa kritiska stub-filer
                critical_stubs = [
                    f for f in data.get('files', []) 
                    if f['production_critical'] and f['status'] in ['stub', 'minimal', 'empty']
                ]
                
                if critical_stubs:
                    print(f"   🚨 CRITICAL STUBS ({len(critical_stubs)}):")
                    for stub in critical_stubs[:3]:  # Visa top 3
                        print(f"      - {stub['file']} ({stub['status']}, {stub['size']} bytes)")
                    if len(critical_stubs) > 3:
                        print(f"      ... och {len(critical_stubs) - 3} fler")
            
            print()

    def save_detailed_results(self, analysis_results: Dict[str, Any], implementation_plan: List[Dict[str, Any]]):
        """Spara detaljerade resultat till JSON"""
        output = {
            'analysis_timestamp': str(Path(__file__).stat().st_mtime),
            'project_root': str(self.project_root),
            'modules': analysis_results,
            'implementation_plan': implementation_plan,
            'summary': {
                'total_modules': len(analysis_results),
                'production_ready': len([m for m in analysis_results.values() if m.get('status') == 'production_ready']),
                'needs_work': len([m for m in analysis_results.values() if m.get('status') == 'needs_work']),
                'critical_missing': len([m for m in analysis_results.values() if m.get('status') == 'critical_missing']),
                'total_critical_tasks': len([t for t in implementation_plan if t['priority'] == 1])
            }
        }
        
        output_file = self.project_root / 'production_readiness_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Detailed results saved to: {output_file}")

def main():
    project_root = Path(__file__).parent.parent
    analyzer = ProductionReadinessAnalyzer(str(project_root))
    
    print("🔍 Starting Production Readiness Analysis...")
    analysis_results = analyzer.analyze_production_readiness()
    implementation_plan = analyzer.generate_implementation_plan(analysis_results)
    
    analyzer.print_analysis_report(analysis_results)
    
    print("📋 TOP PRIORITY IMPLEMENTATION TASKS:")
    print("=" * 40)
    
    for i, task in enumerate(implementation_plan[:10], 1):
        effort_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[task['effort']]
        print(f"{i:2d}. {effort_icon} {task['description']}")
        if task['type'] == 'implement_file':
            print(f"    📁 {task['path']}")
        print()
    
    analyzer.save_detailed_results(analysis_results, implementation_plan)
    print("✨ Analysis complete!")

if __name__ == "__main__":
    main()
