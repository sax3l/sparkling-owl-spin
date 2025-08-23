#!/usr/bin/env python3
"""
Advanced Code Quality Analyzer
Analyzes all code to ensure it's as intelligent and well-developed as possible
Tests coding patterns, performance optimizations, and architectural quality
"""

import ast
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import re
import time
from datetime import datetime
import json

class CodeQualityAnalyzer:
    """
    World-class code quality analyzer that ensures our platform
    uses the most intelligent and well-developed patterns
    """
    
    def __init__(self):
        self.results = {
            "analysis_start": datetime.now().isoformat(),
            "total_files": 0,
            "analyzed_files": 0,
            "code_quality_score": 0.0,
            "intelligence_metrics": {},
            "architectural_patterns": {},
            "performance_optimizations": {},
            "issues_found": [],
            "recommendations": []
        }
        
        # Define intelligent patterns to look for
        self.intelligence_patterns = {
            "async_patterns": {
                "weight": 20,
                "patterns": [
                    r"async def\s+\w+",
                    r"await\s+\w+",
                    r"asyncio\.",
                    r"aiohttp\.",
                    r"AsyncGenerator",
                    r"@asynccontextmanager"
                ]
            },
            "ai_ml_patterns": {
                "weight": 25,
                "patterns": [
                    r"machine.learning",
                    r"AI.powered",
                    r"prediction",
                    r"optimization",
                    r"intelligence",
                    r"neural",
                    r"algorithm",
                    r"heuristic"
                ]
            },
            "performance_patterns": {
                "weight": 20,
                "patterns": [
                    r"@lru_cache",
                    r"concurrent\.futures",
                    r"ThreadPoolExecutor",
                    r"ProcessPoolExecutor", 
                    r"asyncio\.gather",
                    r"batch_process",
                    r"bulk_insert",
                    r"connection.*pool"
                ]
            },
            "architecture_patterns": {
                "weight": 15,
                "patterns": [
                    r"@dataclass",
                    r"from\s+typing\s+import",
                    r"Optional\[",
                    r"List\[",
                    r"Dict\[",
                    r"Union\[",
                    r"Protocol",
                    r"ABC"
                ]
            },
            "error_handling": {
                "weight": 10,
                "patterns": [
                    r"try:",
                    r"except\s+\w+",
                    r"finally:",
                    r"raise\s+\w+",
                    r"logging\.",
                    r"logger\.",
                    r"validation"
                ]
            },
            "testing_patterns": {
                "weight": 10,
                "patterns": [
                    r"@pytest\.",
                    r"def test_",
                    r"assert\s+",
                    r"mock\.",
                    r"@patch",
                    r"fixture"
                ]
            }
        }
        
        # Define anti-patterns (things that reduce quality)
        self.anti_patterns = [
            r"print\(",  # Should use logging
            r"time\.sleep\(",  # Should use async sleep
            r"eval\(",  # Security risk
            r"exec\(",  # Security risk
            r"input\(",  # Blocking in production code
            r"os\.system\(",  # Should use subprocess
        ]
    
    def print_status(self, message: str, status: str = "INFO"):
        """Print formatted status message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\\033[94m",    # Blue
            "SUCCESS": "\\033[92m", # Green  
            "ERROR": "\\033[91m",   # Red
            "WARNING": "\\033[93m", # Yellow
            "RESET": "\\033[0m"
        }
        color = colors.get(status, colors["INFO"])
        print(f"{color}[{timestamp}] {status}: {message}{colors['RESET']}")
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for code quality."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_metrics = {
                "file_path": str(file_path),
                "lines_of_code": len(content.split('\\n')),
                "size_bytes": len(content),
                "intelligence_score": 0,
                "pattern_matches": {},
                "anti_pattern_matches": [],
                "complexity_indicators": {},
                "documentation_quality": 0
            }
            
            # Check for intelligent patterns
            total_intelligence = 0
            max_possible_intelligence = 0
            
            for category, config in self.intelligence_patterns.items():
                matches = []
                for pattern in config["patterns"]:
                    pattern_matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    matches.extend(pattern_matches)
                
                file_metrics["pattern_matches"][category] = len(matches)
                
                # Calculate weighted intelligence score
                category_score = min(10, len(matches)) * (config["weight"] / 10)
                total_intelligence += category_score
                max_possible_intelligence += config["weight"]
            
            # Check for anti-patterns
            for pattern in self.anti_patterns:
                anti_matches = re.findall(pattern, content, re.IGNORECASE)
                if anti_matches:
                    file_metrics["anti_pattern_matches"].append({
                        "pattern": pattern,
                        "matches": len(anti_matches)
                    })
                    total_intelligence -= len(anti_matches) * 5  # Penalty
            
            # Documentation quality
            docstring_matches = re.findall(r'"""[^"]*"""', content, re.MULTILINE | re.DOTALL)
            comment_matches = re.findall(r'#.*', content)
            doc_score = min(10, len(docstring_matches) * 2 + len(comment_matches) * 0.1)
            file_metrics["documentation_quality"] = doc_score
            
            # Calculate complexity indicators
            try:
                tree = ast.parse(content)
                complexity_visitor = ComplexityVisitor()
                complexity_visitor.visit(tree)
                file_metrics["complexity_indicators"] = {
                    "classes": complexity_visitor.classes,
                    "functions": complexity_visitor.functions,
                    "async_functions": complexity_visitor.async_functions,
                    "decorators": complexity_visitor.decorators,
                    "imports": complexity_visitor.imports
                }
            except SyntaxError:
                file_metrics["complexity_indicators"] = {"syntax_error": True}
            
            # Final intelligence score (0-100)
            file_metrics["intelligence_score"] = min(100, 
                (total_intelligence / max_possible_intelligence * 70) + 
                (doc_score * 3)
            ) if max_possible_intelligence > 0 else doc_score * 10
            
            return file_metrics
            
        except Exception as e:
            return {
                "file_path": str(file_path),
                "error": str(e),
                "intelligence_score": 0
            }
    
    def analyze_architecture(self, files: List[Path]) -> Dict[str, Any]:
        """Analyze overall architectural patterns."""
        arch_metrics = {
            "layered_architecture": 0,
            "separation_of_concerns": 0,
            "dependency_management": 0,
            "configuration_management": 0,
            "api_design": 0
        }
        
        # Check for layered architecture
        layer_dirs = ["api", "backend", "frontend", "src", "tests", "config"]
        found_layers = sum(1 for layer in layer_dirs if any(layer in str(f) for f in files))
        arch_metrics["layered_architecture"] = (found_layers / len(layer_dirs)) * 100
        
        # Check API design patterns
        api_files = [f for f in files if "api" in str(f).lower()]
        if api_files:
            api_patterns = 0
            for api_file in api_files[:5]:  # Sample first 5 API files
                try:
                    with open(api_file) as f:
                        content = f.read()
                        if "async def" in content: api_patterns += 1
                        if "FastAPI" in content or "flask" in content.lower(): api_patterns += 1
                        if "Pydantic" in content or "BaseModel" in content: api_patterns += 1
                        if "router" in content.lower(): api_patterns += 1
                except:
                    continue
            arch_metrics["api_design"] = min(100, (api_patterns / 4) * 100)
        
        return arch_metrics
    
    def generate_recommendations(self, file_results: List[Dict[str, Any]]) -> List[str]:
        """Generate intelligent recommendations for code improvement."""
        recommendations = []
        
        # Analyze common issues
        low_score_files = [f for f in file_results if f.get("intelligence_score", 0) < 50]
        
        if low_score_files:
            recommendations.append(
                f"🔧 {len(low_score_files)} files have low intelligence scores. "
                "Consider adding async patterns, type hints, and better error handling."
            )
        
        # Check for missing async patterns
        sync_heavy_files = [
            f for f in file_results 
            if f.get("pattern_matches", {}).get("async_patterns", 0) == 0 
            and f.get("lines_of_code", 0) > 50
        ]
        
        if sync_heavy_files:
            recommendations.append(
                f"⚡ {len(sync_heavy_files)} files lack async patterns. "
                "Modern high-performance applications should use async/await extensively."
            )
        
        # Check for missing AI/ML patterns
        non_ai_files = [
            f for f in file_results 
            if f.get("pattern_matches", {}).get("ai_ml_patterns", 0) == 0
            and "api" in f.get("file_path", "").lower()
        ]
        
        if non_ai_files:
            recommendations.append(
                f"🧠 {len(non_ai_files)} API files lack AI/ML intelligence patterns. "
                "Add intelligent algorithms, optimization, and predictive features."
            )
        
        return recommendations
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis."""
        start_time = time.time()
        
        self.print_status("🔍 Starting Advanced Code Quality Analysis", "INFO")
        self.print_status("Analyzing intelligence and architectural patterns", "INFO")
        
        # Find all Python files
        python_files = []
        for ext in ["*.py"]:
            python_files.extend(Path(".").rglob(ext))
        
        # Filter out unimportant files
        important_files = [
            f for f in python_files 
            if not any(skip in str(f) for skip in [
                "__pycache__", ".venv", "node_modules", ".git", 
                "venv", "env", ".pytest_cache"
            ])
        ]
        
        self.results["total_files"] = len(important_files)
        
        file_results = []
        total_intelligence = 0
        
        self.print_status(f"Analyzing {len(important_files)} Python files...", "INFO")
        
        # Analyze each file
        for i, file_path in enumerate(important_files):
            if i % 10 == 0:  # Progress update
                progress = (i / len(important_files)) * 100
                self.print_status(f"Progress: {progress:.1f}% ({i}/{len(important_files)})", "INFO")
            
            file_metrics = self.analyze_file(file_path)
            file_results.append(file_metrics)
            total_intelligence += file_metrics.get("intelligence_score", 0)
            
            if file_metrics.get("intelligence_score", 0) > 80:
                self.print_status(f"✨ Excellent: {file_path.name} (Score: {file_metrics['intelligence_score']:.1f})", "SUCCESS")
            elif file_metrics.get("intelligence_score", 0) < 30:
                self.print_status(f"⚠️  Needs improvement: {file_path.name} (Score: {file_metrics['intelligence_score']:.1f})", "WARNING")
        
        # Calculate overall metrics
        self.results["analyzed_files"] = len(file_results)
        self.results["code_quality_score"] = total_intelligence / len(file_results) if file_results else 0
        
        # Architectural analysis
        arch_metrics = self.analyze_architecture(important_files)
        self.results["architectural_patterns"] = arch_metrics
        
        # Generate recommendations
        recommendations = self.generate_recommendations(file_results)
        self.results["recommendations"] = recommendations
        
        # Performance analysis
        high_perf_files = [
            f for f in file_results 
            if f.get("pattern_matches", {}).get("performance_patterns", 0) > 0
        ]
        self.results["performance_optimizations"] = {
            "files_with_optimizations": len(high_perf_files),
            "optimization_coverage": (len(high_perf_files) / len(file_results)) * 100 if file_results else 0
        }
        
        # Analysis duration
        duration = time.time() - start_time
        self.results["analysis_duration"] = duration
        
        # Generate final report
        self._generate_final_report(file_results)
        
        return self.results
    
    def _generate_final_report(self, file_results: List[Dict[str, Any]]):
        """Generate comprehensive final report."""
        self.print_status("\\n" + "="*80, "INFO")
        self.print_status("🎯 ADVANCED CODE QUALITY ANALYSIS RESULTS", "SUCCESS")
        self.print_status("="*80, "INFO")
        
        score = self.results["code_quality_score"]
        
        if score >= 85:
            self.print_status(f"🌟 WORLD-CLASS CODE: {score:.1f}/100", "SUCCESS")
            self.print_status("🚀 Code quality beats all industry standards!", "SUCCESS")
        elif score >= 70:
            self.print_status(f"⚡ EXCELLENT CODE: {score:.1f}/100", "SUCCESS") 
            self.print_status("🎯 High-quality, production-ready codebase", "INFO")
        elif score >= 55:
            self.print_status(f"✅ GOOD CODE: {score:.1f}/100", "INFO")
            self.print_status("🔧 Some optimizations recommended", "WARNING")
        else:
            self.print_status(f"⚠️  NEEDS IMPROVEMENT: {score:.1f}/100", "WARNING")
            self.print_status("🛠️  Significant enhancements needed", "ERROR")
        
        # Detailed metrics
        arch_score = sum(self.results["architectural_patterns"].values()) / len(self.results["architectural_patterns"])
        perf_score = self.results["performance_optimizations"]["optimization_coverage"]
        
        self.print_status(f"🏗️  Architecture Score: {arch_score:.1f}/100", "INFO")
        self.print_status(f"⚡ Performance Score: {perf_score:.1f}/100", "INFO")
        self.print_status(f"📊 Files Analyzed: {self.results['analyzed_files']}/{self.results['total_files']}", "INFO")
        self.print_status(f"⏱️  Analysis Time: {self.results['analysis_duration']:.2f}s", "INFO")
        
        # Top performing files
        top_files = sorted(file_results, key=lambda x: x.get("intelligence_score", 0), reverse=True)[:5]
        self.print_status("\\n🏆 TOP PERFORMING FILES:", "SUCCESS")
        for i, file_info in enumerate(top_files, 1):
            score = file_info.get("intelligence_score", 0)
            name = Path(file_info["file_path"]).name
            self.print_status(f"  {i}. {name} - {score:.1f}/100", "SUCCESS")
        
        # Recommendations
        if self.results["recommendations"]:
            self.print_status("\\n💡 INTELLIGENT RECOMMENDATIONS:", "INFO")
            for i, rec in enumerate(self.results["recommendations"], 1):
                self.print_status(f"  {i}. {rec}", "WARNING")
        
        # Save detailed results
        with open("code_quality_analysis.json", "w") as f:
            json.dump({
                **self.results,
                "file_details": file_results
            }, f, indent=2, default=str)
        
        self.print_status("\\n📄 Detailed analysis saved to code_quality_analysis.json", "INFO")
        self.print_status("="*80, "INFO")


class ComplexityVisitor(ast.NodeVisitor):
    """AST visitor to calculate code complexity metrics."""
    
    def __init__(self):
        self.classes = 0
        self.functions = 0
        self.async_functions = 0
        self.decorators = 0
        self.imports = 0
    
    def visit_ClassDef(self, node):
        self.classes += 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.functions += 1
        self.decorators += len(node.decorator_list)
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        self.async_functions += 1
        self.decorators += len(node.decorator_list)
        self.generic_visit(node)
    
    def visit_Import(self, node):
        self.imports += 1
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.imports += 1
        self.generic_visit(node)


def main():
    """Run the advanced code quality analyzer."""
    analyzer = CodeQualityAnalyzer()
    results = analyzer.analyze_project()
    
    # Exit with appropriate code
    if results["code_quality_score"] >= 70:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
