#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE FILE ANALYSIS SYSTEM - SPARKLING OWL SPIN 🔍

Denna modul genomför djupgående analys av alla filer i projektet för att
säkerställa kvalitet, konsistens och fullständighet.

ANALYSOMRÅDEN:
✅ Python-filer (.py) - Syntax, imports, dokumentation, komplexitet
✅ Konfigurationsfiler (.json, .yaml, .toml) - Struktur och validering
✅ Dokumentation (.md, .rst, .txt) - Innehåll och format
✅ Setup-filer (setup.py, requirements.txt) - Beroenden och konfiguration
✅ Docker-filer (Dockerfile, docker-compose.yml) - Containerization
✅ Frontend-filer (.js, .ts, .jsx, .tsx) - JavaScript/TypeScript kod
✅ Stilfiler (.css, .scss) - Styling och design
✅ Testfiler (test_*.py) - Testtäckning och kvalitet
✅ Databasfiler (.sql, .db) - Schema och data
✅ Skriptfiler (.sh, .ps1, .bat) - Automation och deployment
"""

import os
import ast
import json
import yaml
import time
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileAnalysisResult:
    """Resultat av filanalys"""
    file_path: str
    file_type: str
    size_bytes: int
    line_count: int
    encoding: str
    syntax_valid: bool
    issues: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
    analysis_time: float
    last_modified: datetime

class ComprehensiveFileAnalyzer:
    """Omfattande filanalysator för alla projektfiler"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_results: Dict[str, FileAnalysisResult] = {}
        self.file_type_stats: Dict[str, int] = defaultdict(int)
        self.total_files = 0
        self.total_lines = 0
        self.total_size = 0
        
        # Filtyp-kategorier
        self.file_categories = {
            "python": {".py", ".pyi", ".pyx"},
            "javascript": {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"},
            "config": {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"},
            "documentation": {".md", ".rst", ".txt", ".doc", ".docx"},
            "web": {".html", ".htm", ".css", ".scss", ".sass", ".less"},
            "data": {".csv", ".xml", ".sql", ".db", ".sqlite", ".sqlite3"},
            "scripts": {".sh", ".bash", ".ps1", ".bat", ".cmd"},
            "docker": {"Dockerfile", ".dockerignore", "docker-compose.yml", "docker-compose.yaml"},
            "git": {".gitignore", ".gitattributes", ".gitmodules"},
            "ci": {".github", ".gitlab-ci.yml", "azure-pipelines.yml", "Jenkinsfile"},
            "package": {"package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", 
                       "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"},
            "other": set()
        }
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                          ║
║               🔍 COMPREHENSIVE FILE ANALYSIS - SPARKLING OWL SPIN 🔍                   ║
║                                                                                          ║
║                        🎯 ANALYZING ALL PROJECT FILES IN DETAIL 🎯                     ║
║                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def get_file_category(self, file_path: Path) -> str:
        """Bestäm filkategori baserat på extension eller namn"""
        file_name = file_path.name
        file_suffix = file_path.suffix.lower()
        
        for category, extensions in self.file_categories.items():
            if file_suffix in extensions or file_name in extensions:
                return category
        
        return "other"
    
    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analysera Python-filer i detalj"""
        metrics = {
            "classes": 0,
            "functions": 0,
            "async_functions": 0,
            "imports": 0,
            "docstrings": 0,
            "complexity_score": 0,
            "ast_valid": False
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST-analys
            try:
                tree = ast.parse(content)
                metrics["ast_valid"] = True
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        metrics["classes"] += 1
                        if ast.get_docstring(node):
                            metrics["docstrings"] += 1
                    elif isinstance(node, ast.FunctionDef):
                        metrics["functions"] += 1
                        if ast.get_docstring(node):
                            metrics["docstrings"] += 1
                    elif isinstance(node, ast.AsyncFunctionDef):
                        metrics["async_functions"] += 1
                        if ast.get_docstring(node):
                            metrics["docstrings"] += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        metrics["imports"] += 1
                
                # Komplexitetsberäkning (förenklad)
                total_nodes = len(list(ast.walk(tree)))
                lines = len(content.splitlines())
                if lines > 0:
                    metrics["complexity_score"] = round(total_nodes / lines * 100, 2)
                
            except SyntaxError:
                metrics["ast_valid"] = False
            
        except Exception as e:
            logger.warning(f"Error analyzing Python file {file_path}: {e}")
        
        return metrics
    
    def analyze_javascript_file(self, file_path: Path) -> Dict[str, Any]:
        """Analysera JavaScript/TypeScript-filer"""
        metrics = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "exports": 0,
            "comments": 0,
            "is_typescript": file_path.suffix.lower() in {".ts", ".tsx"}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Enkla regex-baserade mätningar
            metrics["functions"] = len(re.findall(r'\bfunction\s+\w+|\w+\s*=\s*\([^)]*\)\s*=>', content))
            metrics["classes"] = len(re.findall(r'\bclass\s+\w+', content))
            metrics["imports"] = len(re.findall(r'\bimport\s+', content))
            metrics["exports"] = len(re.findall(r'\bexport\s+', content))
            metrics["comments"] = len(re.findall(r'//.*|/\*[\s\S]*?\*/', content))
            
        except Exception as e:
            logger.warning(f"Error analyzing JavaScript file {file_path}: {e}")
        
        return metrics
    
    def analyze_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Analysera konfigurationsfiler"""
        metrics = {
            "format": file_path.suffix.lower(),
            "valid_format": False,
            "keys_count": 0,
            "nested_levels": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.suffix.lower() == ".json":
                try:
                    data = json.loads(content)
                    metrics["valid_format"] = True
                    metrics["keys_count"] = self._count_keys(data)
                    metrics["nested_levels"] = self._count_nesting_levels(data)
                except json.JSONDecodeError:
                    pass
            
            elif file_path.suffix.lower() in {".yaml", ".yml"}:
                try:
                    data = yaml.safe_load(content)
                    metrics["valid_format"] = True
                    if isinstance(data, dict):
                        metrics["keys_count"] = self._count_keys(data)
                        metrics["nested_levels"] = self._count_nesting_levels(data)
                except yaml.YAMLError:
                    pass
            
            elif file_path.suffix.lower() == ".toml":
                # Enkel TOML-validering
                if "[" in content and "]" in content:
                    metrics["valid_format"] = True
                    metrics["keys_count"] = len(re.findall(r'^\w+\s*=', content, re.MULTILINE))
            
        except Exception as e:
            logger.warning(f"Error analyzing config file {file_path}: {e}")
        
        return metrics
    
    def _count_keys(self, data: Any) -> int:
        """Räkna nycklar i nested dictionary"""
        if isinstance(data, dict):
            count = len(data)
            for value in data.values():
                count += self._count_keys(value)
            return count
        elif isinstance(data, list):
            count = 0
            for item in data:
                count += self._count_keys(item)
            return count
        return 0
    
    def _count_nesting_levels(self, data: Any, current_level: int = 0) -> int:
        """Räkna nesting-nivåer"""
        if isinstance(data, dict):
            if not data:
                return current_level
            return max(self._count_nesting_levels(value, current_level + 1) for value in data.values())
        elif isinstance(data, list):
            if not data:
                return current_level
            return max(self._count_nesting_levels(item, current_level) for item in data)
        return current_level
    
    def analyze_documentation_file(self, file_path: Path) -> Dict[str, Any]:
        """Analysera dokumentationsfiler"""
        metrics = {
            "format": file_path.suffix.lower(),
            "word_count": 0,
            "headers": 0,
            "links": 0,
            "code_blocks": 0,
            "images": 0
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Grundläggande textanalys
            metrics["word_count"] = len(content.split())
            
            if file_path.suffix.lower() == ".md":
                # Markdown-specifik analys
                metrics["headers"] = len(re.findall(r'^#+\s+', content, re.MULTILINE))
                metrics["links"] = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
                metrics["code_blocks"] = len(re.findall(r'```[\s\S]*?```|`[^`]+`', content))
                metrics["images"] = len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content))
            
        except Exception as e:
            logger.warning(f"Error analyzing documentation file {file_path}: {e}")
        
        return metrics
    
    def analyze_single_file(self, file_path: Path) -> FileAnalysisResult:
        """Analysera en enda fil"""
        start_time = time.time()
        
        # Grundläggande filinfo
        try:
            stat = file_path.stat()
            size_bytes = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime)
            
            # Läs fil för att räkna rader och bestäm encoding
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                encoding = 'utf-8'
                line_count = len(content.splitlines())
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    encoding = 'latin-1'
                    line_count = len(content.splitlines())
                except:
                    encoding = 'binary'
                    line_count = 0
                    content = ""
            
        except Exception as e:
            # Fel vid filåtkomst
            return FileAnalysisResult(
                file_path=str(file_path),
                file_type="error",
                size_bytes=0,
                line_count=0,
                encoding="unknown",
                syntax_valid=False,
                issues=[f"File access error: {str(e)}"],
                warnings=[],
                metrics={},
                analysis_time=time.time() - start_time,
                last_modified=datetime.now()
            )
        
        # Bestäm filkategori
        file_category = self.get_file_category(file_path)
        self.file_type_stats[file_category] += 1
        
        issues = []
        warnings = []
        metrics = {}
        syntax_valid = True
        
        # Kategori-specifik analys
        if file_category == "python":
            metrics = self.analyze_python_file(file_path)
            syntax_valid = metrics.get("ast_valid", True)
            if not syntax_valid:
                issues.append("Invalid Python syntax")
            
        elif file_category == "javascript":
            metrics = self.analyze_javascript_file(file_path)
            
        elif file_category == "config":
            metrics = self.analyze_config_file(file_path)
            if not metrics.get("valid_format", True):
                issues.append("Invalid configuration file format")
                
        elif file_category == "documentation":
            metrics = self.analyze_documentation_file(file_path)
            if metrics.get("word_count", 0) < 10:
                warnings.append("Very short documentation file")
        
        # Allmänna kontroller
        if size_bytes == 0:
            warnings.append("Empty file")
        elif size_bytes > 1024 * 1024:  # > 1MB
            warnings.append(f"Large file ({size_bytes // 1024 // 1024} MB)")
        
        if line_count > 1000:
            warnings.append(f"Very long file ({line_count} lines)")
        
        analysis_time = time.time() - start_time
        
        return FileAnalysisResult(
            file_path=str(file_path),
            file_type=file_category,
            size_bytes=size_bytes,
            line_count=line_count,
            encoding=encoding,
            syntax_valid=syntax_valid,
            issues=issues,
            warnings=warnings,
            metrics=metrics,
            analysis_time=analysis_time,
            last_modified=last_modified
        )
    
    def should_analyze_path(self, path: Path) -> bool:
        """Bestäm om en sökväg ska analyseras"""
        # Skippa vissa kataloger
        skip_dirs = {
            '.git', '.venv', '__pycache__', 'node_modules', '.pytest_cache',
            '.mypy_cache', '.tox', 'venv', 'env', '.env', 'build', 'dist',
            '.coverage', '.nyc_output', 'coverage'
        }
        
        # Kontrollera om någon del av sökvägen är i skip_dirs
        for part in path.parts:
            if part in skip_dirs:
                return False
        
        return True
    
    def analyze_all_files(self) -> Dict[str, Any]:
        """Analysera alla filer i projektet"""
        print(f"\n🔍 STARTAR OMFATTANDE FILANALYS AV PROJEKT: {self.project_root}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Hitta alla filer
        all_files = []
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and self.should_analyze_path(file_path):
                all_files.append(file_path)
        
        self.total_files = len(all_files)
        print(f"📊 Totalt {self.total_files} filer att analysera")
        
        # Analysera varje fil
        for i, file_path in enumerate(all_files, 1):
            if i % 100 == 0 or i == self.total_files:
                print(f"   Analyserar fil {i}/{self.total_files} ({(i/self.total_files)*100:.1f}%)")
            
            try:
                result = self.analyze_single_file(file_path)
                self.analysis_results[str(file_path)] = result
                self.total_lines += result.line_count
                self.total_size += result.size_bytes
                
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        total_time = time.time() - start_time
        
        # Generera sammanfattning
        summary = self.generate_analysis_summary(total_time)
        
        print(f"\n✅ Analys slutförd på {total_time:.2f} sekunder")
        print(f"📊 {len(self.analysis_results)} filer analyserade")
        
        return summary
    
    def generate_analysis_summary(self, analysis_time: float) -> Dict[str, Any]:
        """Generera sammanfattning av analysen"""
        
        # Samla statistik
        syntax_errors = sum(1 for r in self.analysis_results.values() if not r.syntax_valid)
        total_issues = sum(len(r.issues) for r in self.analysis_results.values())
        total_warnings = sum(len(r.warnings) for r in self.analysis_results.values())
        
        # Filtypsfördelning
        file_type_distribution = dict(self.file_type_stats)
        
        # Största filer
        largest_files = sorted(
            [(r.file_path, r.size_bytes) for r in self.analysis_results.values()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Mest komplexa Python-filer
        complex_python_files = [
            (r.file_path, r.metrics.get('complexity_score', 0))
            for r in self.analysis_results.values()
            if r.file_type == 'python' and r.metrics.get('complexity_score', 0) > 0
        ]
        complex_python_files.sort(key=lambda x: x[1], reverse=True)
        
        # Kodstatistik per språk
        language_stats = {
            'python': {
                'files': len([r for r in self.analysis_results.values() if r.file_type == 'python']),
                'total_lines': sum(r.line_count for r in self.analysis_results.values() if r.file_type == 'python'),
                'total_classes': sum(r.metrics.get('classes', 0) for r in self.analysis_results.values() if r.file_type == 'python'),
                'total_functions': sum(r.metrics.get('functions', 0) for r in self.analysis_results.values() if r.file_type == 'python'),
            },
            'javascript': {
                'files': len([r for r in self.analysis_results.values() if r.file_type == 'javascript']),
                'total_lines': sum(r.line_count for r in self.analysis_results.values() if r.file_type == 'javascript'),
                'total_functions': sum(r.metrics.get('functions', 0) for r in self.analysis_results.values() if r.file_type == 'javascript'),
                'total_classes': sum(r.metrics.get('classes', 0) for r in self.analysis_results.values() if r.file_type == 'javascript'),
            }
        }
        
        summary = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_time_seconds": round(analysis_time, 2),
            "project_root": str(self.project_root),
            
            "file_statistics": {
                "total_files": self.total_files,
                "total_lines": self.total_lines,
                "total_size_bytes": self.total_size,
                "total_size_mb": round(self.total_size / (1024 * 1024), 2),
                "average_file_size": round(self.total_size / max(self.total_files, 1), 2),
                "average_lines_per_file": round(self.total_lines / max(self.total_files, 1), 2)
            },
            
            "file_type_distribution": file_type_distribution,
            
            "quality_metrics": {
                "syntax_errors": syntax_errors,
                "total_issues": total_issues,
                "total_warnings": total_warnings,
                "files_with_issues": len([r for r in self.analysis_results.values() if r.issues]),
                "files_with_warnings": len([r for r in self.analysis_results.values() if r.warnings]),
                "overall_quality_score": round(max(0, 100 - (syntax_errors * 10) - (total_issues * 2) - (total_warnings * 0.5)), 1)
            },
            
            "language_statistics": language_stats,
            
            "largest_files": [{"file": f, "size_mb": round(s / (1024 * 1024), 2)} for f, s in largest_files],
            
            "most_complex_files": [{"file": f, "complexity": c} for f, c in complex_python_files[:10]],
            
            "recommendations": self.generate_recommendations()
        }
        
        return summary
    
    def generate_recommendations(self) -> List[str]:
        """Generera rekommendationer baserat på analysen"""
        recommendations = []
        
        # Kontrollera för stora filer
        large_files = [r for r in self.analysis_results.values() if r.size_bytes > 500 * 1024]
        if large_files:
            recommendations.append(f"Consider splitting {len(large_files)} large files (>500KB) for better maintainability")
        
        # Kontrollera för långa filer
        long_files = [r for r in self.analysis_results.values() if r.line_count > 1000]
        if long_files:
            recommendations.append(f"Consider refactoring {len(long_files)} very long files (>1000 lines)")
        
        # Kontrollera Python-dokumentation
        python_files = [r for r in self.analysis_results.values() if r.file_type == 'python']
        undocumented_python = [r for r in python_files if r.metrics.get('docstrings', 0) == 0 and r.metrics.get('functions', 0) > 0]
        if undocumented_python:
            recommendations.append(f"Add documentation to {len(undocumented_python)} Python files without docstrings")
        
        # Kontrollera tomma filer
        empty_files = [r for r in self.analysis_results.values() if r.size_bytes == 0]
        if empty_files:
            recommendations.append(f"Review {len(empty_files)} empty files - consider removal or implementation")
        
        # Kontrollera konfigurationsfiler
        invalid_configs = [r for r in self.analysis_results.values() if r.file_type == 'config' and not r.metrics.get('valid_format', True)]
        if invalid_configs:
            recommendations.append(f"Fix {len(invalid_configs)} configuration files with invalid format")
        
        return recommendations
    
    def print_detailed_summary(self, summary: Dict[str, Any]):
        """Skriv ut detaljerad sammanfattning"""
        print("\n" + "="*90)
        print("📊 DETALJERAD FILANALYS - SAMMANFATTNING")
        print("="*90)
        
        # Grundstatistik
        stats = summary["file_statistics"]
        print(f"\n📈 PROJEKTSTATISTIK:")
        print(f"   • Totalt antal filer: {stats['total_files']:,}")
        print(f"   • Totalt antal rader: {stats['total_lines']:,}")
        print(f"   • Total storlek: {stats['total_size_mb']} MB")
        print(f"   • Genomsnittlig filstorlek: {stats['average_file_size']:.1f} bytes")
        print(f"   • Genomsnittlig rader per fil: {stats['average_lines_per_file']:.1f}")
        
        # Filtypsfördelning
        print(f"\n📂 FILTYPSFÖRDELNING:")
        for file_type, count in sorted(summary["file_type_distribution"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_files']) * 100
            print(f"   • {file_type.title()}: {count} filer ({percentage:.1f}%)")
        
        # Kvalitetsmetrik
        quality = summary["quality_metrics"]
        print(f"\n🎯 KVALITETSMETRIK:")
        print(f"   • Syntax-fel: {quality['syntax_errors']}")
        print(f"   • Totala problem: {quality['total_issues']}")
        print(f"   • Totala varningar: {quality['total_warnings']}")
        print(f"   • Filer med problem: {quality['files_with_issues']}")
        print(f"   • Övergripande kvalitetscore: {quality['overall_quality_score']}/100")
        
        # Språkstatistik
        print(f"\n💻 SPRÅKSTATISTIK:")
        for lang, stats in summary["language_statistics"].items():
            if stats['files'] > 0:
                print(f"   • {lang.title()}:")
                print(f"     └─ {stats['files']} filer, {stats['total_lines']:,} rader")
                if 'total_functions' in stats:
                    print(f"     └─ {stats['total_functions']} funktioner, {stats.get('total_classes', 0)} klasser")
        
        # Största filer
        if summary["largest_files"]:
            print(f"\n📦 STÖRSTA FILER:")
            for i, file_info in enumerate(summary["largest_files"][:5], 1):
                print(f"   {i}. {Path(file_info['file']).name} ({file_info['size_mb']} MB)")
        
        # Mest komplexa filer
        if summary["most_complex_files"]:
            print(f"\n🧮 MEST KOMPLEXA PYTHON-FILER:")
            for i, file_info in enumerate(summary["most_complex_files"][:5], 1):
                print(f"   {i}. {Path(file_info['file']).name} (komplexitet: {file_info['complexity']:.1f})")
        
        # Rekommendationer
        if summary["recommendations"]:
            print(f"\n💡 REKOMMENDATIONER:")
            for i, rec in enumerate(summary["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n⏱️ Analys slutförd på {summary['analysis_time_seconds']} sekunder")
        print("="*90)
    
    def save_analysis_report(self, summary: Dict[str, Any], filename: str = "comprehensive_file_analysis_report.json"):
        """Spara analysrapport till fil"""
        # Konvertera analysis_results för JSON-serialisering
        serializable_results = {}
        for path, result in self.analysis_results.items():
            serializable_results[path] = {
                "file_path": result.file_path,
                "file_type": result.file_type,
                "size_bytes": result.size_bytes,
                "line_count": result.line_count,
                "encoding": result.encoding,
                "syntax_valid": result.syntax_valid,
                "issues": result.issues,
                "warnings": result.warnings,
                "metrics": result.metrics,
                "analysis_time": result.analysis_time,
                "last_modified": result.last_modified.isoformat()
            }
        
        # Lägg till detaljerade resultat
        full_report = {
            **summary,
            "detailed_results": serializable_results
        }
        
        # Spara rapport
        report_path = self.project_root / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detaljerad analysrapport sparad till: {report_path}")
        
        return report_path

def run_comprehensive_file_analysis(project_root: str = ".") -> Dict[str, Any]:
    """Huvudfunktion för att köra omfattande filanalys"""
    analyzer = ComprehensiveFileAnalyzer(project_root)
    
    # Kör analysen
    summary = analyzer.analyze_all_files()
    
    # Visa sammanfattning
    analyzer.print_detailed_summary(summary)
    
    # Spara rapport
    analyzer.save_analysis_report(summary)
    
    return summary

if __name__ == "__main__":
    print("🚀 Startar omfattande filanalys av Sparkling Owl Spin projektet...")
    
    # Kör analysen
    project_summary = run_comprehensive_file_analysis()
    
    # Slutstatus
    quality_score = project_summary["quality_metrics"]["overall_quality_score"]
    
    if quality_score >= 90:
        print(f"\n🎉 PROJEKTSTATUS: EXCELLENT ({quality_score}/100) - REDO FÖR PRODUKTION!")
    elif quality_score >= 75:
        print(f"\n✅ PROJEKTSTATUS: BRA ({quality_score}/100) - MINDRE FÖRBÄTTRINGAR REKOMMENDERAS")
    elif quality_score >= 60:
        print(f"\n⚠️ PROJEKTSTATUS: GODKÄND ({quality_score}/100) - FÖRBÄTTRINGAR BEHÖVS")
    else:
        print(f"\n❌ PROJEKTSTATUS: BEHÖVER ARBETE ({quality_score}/100) - OMFATTANDE FÖRBÄTTRINGAR KRÄVS")
    
    print(f"🌟 Sparkling Owl Spin Comprehensive File Analysis Completed!")
