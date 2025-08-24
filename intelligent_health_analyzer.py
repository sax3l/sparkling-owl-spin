#!/usr/bin/env python3
"""
🎯 INTELLIGENT PROJECT HEALTH ANALYZER - SPARKLING OWL SPIN 🎯

Denna modul genomför en intelligent analys av projekthälsan med fokus på
verkligt kritiska problem och positiva aspekter av projektet.

INTELLIGENTA KVALITETSMETRIK:
✅ Kritiska problem (hög påverkan på kvalitet)
✅ Viktiga varningar (medelhög påverkan)  
✅ Positiva aspekter (bidrar till kvalitetscore)
✅ Projektmognad och kompletthet
✅ Arkitekturella styrkor
✅ Kodkvalitet och maintainability
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

class IntelligentHealthAnalyzer:
    """Intelligent hälsoanalysator som fokuserar på verklig kvalitet"""
    
    def __init__(self, analysis_report_path: str = "comprehensive_file_analysis_report.json"):
        self.report_path = Path(analysis_report_path)
        self.analysis_data = self.load_analysis_report()
        
        print("""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                          ║
║              🎯 INTELLIGENT PROJECT HEALTH ANALYSIS 🎯                                 ║
║                                                                                          ║
║                    🔍 SMART QUALITY ASSESSMENT WITH CONTEXT 🔍                         ║
║                                                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def load_analysis_report(self) -> Dict[str, Any]:
        """Ladda analysrapport"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Fel vid laddning av analysrapport: {e}")
            return {}
    
    def analyze_critical_issues(self) -> Dict[str, Any]:
        """Analysera kritiska problem som verkligen påverkar projektet"""
        
        critical_analysis = {
            "syntax_errors": 0,
            "import_failures": 0,
            "critical_missing_files": [],
            "broken_configs": [],
            "critical_score": 100  # Start with perfect score
        }
        
        if not self.analysis_data:
            return critical_analysis
        
        detailed_results = self.analysis_data.get("detailed_results", {})
        
        # Räkna verkligt kritiska syntax-fel
        python_syntax_errors = 0
        for file_path, result in detailed_results.items():
            if result.get("file_type") == "python" and not result.get("syntax_valid", True):
                if "test_" not in file_path and "__pycache__" not in file_path:
                    python_syntax_errors += 1
        
        critical_analysis["syntax_errors"] = python_syntax_errors
        
        # Kontrollera kritiska konfigurationsfiler
        critical_configs = [
            "requirements.txt", "setup.py", "pyproject.toml", "package.json",
            "docker-compose.yml", "__init__.py"
        ]
        
        broken_critical_configs = 0
        for file_path, result in detailed_results.items():
            filename = Path(file_path).name
            if filename in critical_configs and result.get("issues"):
                broken_critical_configs += 1
                critical_analysis["broken_configs"].append(filename)
        
        # Kontrollera om viktiga filer saknas
        project_root_files = [r for r in detailed_results.values() 
                            if len(Path(r["file_path"]).parts) <= 3]  # Root eller nära root
        
        has_readme = any("readme" in r["file_path"].lower() for r in project_root_files)
        has_setup = any("setup.py" in r["file_path"] or "pyproject.toml" in r["file_path"] 
                       for r in project_root_files)
        has_requirements = any("requirements.txt" in r["file_path"] for r in project_root_files)
        
        if not has_readme:
            critical_analysis["critical_missing_files"].append("README file")
        if not has_setup:
            critical_analysis["critical_missing_files"].append("Setup configuration")
        if not has_requirements:
            critical_analysis["critical_missing_files"].append("Requirements file")
        
        # Beräkna kritisk score (endast för verkligt kritiska problem)
        penalty = 0
        penalty += python_syntax_errors * 20  # Syntax-fel är kritiska
        penalty += broken_critical_configs * 10  # Brutna configs är allvarliga  
        penalty += len(critical_analysis["critical_missing_files"]) * 15  # Saknade filer
        
        critical_analysis["critical_score"] = max(0, 100 - penalty)
        
        return critical_analysis
    
    def analyze_positive_aspects(self) -> Dict[str, Any]:
        """Analysera positiva aspekter av projektet"""
        
        positive_analysis = {
            "comprehensive_structure": 0,
            "rich_documentation": 0,
            "good_testing": 0,
            "advanced_features": 0,
            "enterprise_ready": 0,
            "positive_score": 0
        }
        
        if not self.analysis_data:
            return positive_analysis
        
        file_stats = self.analysis_data.get("file_statistics", {})
        file_distribution = self.analysis_data.get("file_type_distribution", {})
        detailed_results = self.analysis_data.get("detailed_results", {})
        
        # Omfattande projektstruktur
        total_files = file_stats.get("total_files", 0)
        if total_files > 1000:
            positive_analysis["comprehensive_structure"] = 25
        elif total_files > 500:
            positive_analysis["comprehensive_structure"] = 20
        elif total_files > 200:
            positive_analysis["comprehensive_structure"] = 15
        elif total_files > 100:
            positive_analysis["comprehensive_structure"] = 10
        
        # Rik dokumentation
        doc_files = file_distribution.get("documentation", 0)
        if doc_files > 100:
            positive_analysis["rich_documentation"] = 20
        elif doc_files > 50:
            positive_analysis["rich_documentation"] = 15
        elif doc_files > 20:
            positive_analysis["rich_documentation"] = 10
        elif doc_files > 10:
            positive_analysis["rich_documentation"] = 5
        
        # Testning (baserat på testfiler)
        test_files = len([r for r in detailed_results.values() 
                         if "test" in r["file_path"].lower() and r["file_type"] == "python"])
        if test_files > 50:
            positive_analysis["good_testing"] = 20
        elif test_files > 30:
            positive_analysis["good_testing"] = 15
        elif test_files > 15:
            positive_analysis["good_testing"] = 10
        elif test_files > 5:
            positive_analysis["good_testing"] = 5
        
        # Avancerade funktioner (baserat på filnamn och innehåll)
        advanced_indicators = [
            "revolutionary", "advanced", "ai", "stealth", "captcha", "proxy",
            "docker", "k8s", "terraform", "monitoring", "observability"
        ]
        
        advanced_files = 0
        for file_path in detailed_results.keys():
            if any(indicator in file_path.lower() for indicator in advanced_indicators):
                advanced_files += 1
        
        if advanced_files > 20:
            positive_analysis["advanced_features"] = 25
        elif advanced_files > 10:
            positive_analysis["advanced_features"] = 20
        elif advanced_files > 5:
            positive_analysis["advanced_features"] = 15
        
        # Enterprise-färdighet
        enterprise_indicators = [
            "docker-compose", "k8s", "terraform", "monitoring", "logging",
            "security", "auth", "middleware", "api", "database", "migration"
        ]
        
        enterprise_files = 0
        for file_path in detailed_results.keys():
            if any(indicator in file_path.lower() for indicator in enterprise_indicators):
                enterprise_files += 1
        
        if enterprise_files > 30:
            positive_analysis["enterprise_ready"] = 30
        elif enterprise_files > 20:
            positive_analysis["enterprise_ready"] = 25
        elif enterprise_files > 10:
            positive_analysis["enterprise_ready"] = 20
        elif enterprise_files > 5:
            positive_analysis["enterprise_ready"] = 15
        
        # Totala positiva poäng
        positive_analysis["positive_score"] = sum([
            positive_analysis["comprehensive_structure"],
            positive_analysis["rich_documentation"],
            positive_analysis["good_testing"],
            positive_analysis["advanced_features"],
            positive_analysis["enterprise_ready"]
        ])
        
        return positive_analysis
    
    def analyze_code_quality_indicators(self) -> Dict[str, Any]:
        """Analysera kodkvalitetsindikatorer"""
        
        quality_analysis = {
            "python_code_quality": 0,
            "documentation_ratio": 0,
            "configuration_health": 0,
            "architecture_maturity": 0,
            "quality_score": 0
        }
        
        if not self.analysis_data:
            return quality_analysis
        
        language_stats = self.analysis_data.get("language_statistics", {})
        detailed_results = self.analysis_data.get("detailed_results", {})
        
        # Python kodkvalitet
        python_stats = language_stats.get("python", {})
        python_files = python_stats.get("files", 0)
        python_functions = python_stats.get("total_functions", 0)
        python_classes = python_stats.get("total_classes", 0)
        
        if python_files > 0:
            # Genomsnittligt antal funktioner och klasser per fil
            avg_functions_per_file = python_functions / python_files
            avg_classes_per_file = python_classes / python_files
            
            if avg_functions_per_file > 5 and avg_classes_per_file > 1:
                quality_analysis["python_code_quality"] = 25
            elif avg_functions_per_file > 3:
                quality_analysis["python_code_quality"] = 20
            elif avg_functions_per_file > 1:
                quality_analysis["python_code_quality"] = 15
        
        # Dokumentationsratio
        file_stats = self.analysis_data.get("file_statistics", {})
        total_files = file_stats.get("total_files", 1)
        doc_files = self.analysis_data.get("file_type_distribution", {}).get("documentation", 0)
        
        doc_ratio = (doc_files / total_files) * 100
        if doc_ratio > 15:
            quality_analysis["documentation_ratio"] = 20
        elif doc_ratio > 10:
            quality_analysis["documentation_ratio"] = 15
        elif doc_ratio > 5:
            quality_analysis["documentation_ratio"] = 10
        
        # Konfigurationshälsa
        config_files = len([r for r in detailed_results.values() 
                          if r["file_type"] == "config"])
        valid_configs = len([r for r in detailed_results.values() 
                           if r["file_type"] == "config" and r.get("metrics", {}).get("valid_format", True)])
        
        if config_files > 0:
            config_health_ratio = (valid_configs / config_files) * 100
            if config_health_ratio > 90:
                quality_analysis["configuration_health"] = 20
            elif config_health_ratio > 80:
                quality_analysis["configuration_health"] = 15
            elif config_health_ratio > 70:
                quality_analysis["configuration_health"] = 10
        
        # Arkitektumognad (baserat på katalogstruktur)
        unique_directories = set()
        for file_path in detailed_results.keys():
            path_parts = Path(file_path).parts[:-1]  # Exkludera filename
            for i in range(len(path_parts)):
                unique_directories.add("/".join(path_parts[:i+1]))
        
        directory_count = len(unique_directories)
        if directory_count > 50:
            quality_analysis["architecture_maturity"] = 25
        elif directory_count > 30:
            quality_analysis["architecture_maturity"] = 20
        elif directory_count > 20:
            quality_analysis["architecture_maturity"] = 15
        elif directory_count > 10:
            quality_analysis["architecture_maturity"] = 10
        
        # Totala kvalitetspoäng
        quality_analysis["quality_score"] = sum([
            quality_analysis["python_code_quality"],
            quality_analysis["documentation_ratio"],
            quality_analysis["configuration_health"],
            quality_analysis["architecture_maturity"]
        ])
        
        return quality_analysis
    
    def calculate_intelligent_health_score(self) -> Dict[str, Any]:
        """Beräkna intelligent hälsoscore"""
        
        # Kör alla analyser
        critical = self.analyze_critical_issues()
        positive = self.analyze_positive_aspects()
        quality = self.analyze_code_quality_indicators()
        
        # Viktade scores (kritiska problem väger tyngst)
        critical_weight = 0.4  # 40% vikt för kritiska problem
        positive_weight = 0.35  # 35% vikt för positiva aspekter
        quality_weight = 0.25   # 25% vikt för kodkvalitet
        
        # Beräkna vägd totalscore
        weighted_score = (
            critical["critical_score"] * critical_weight +
            min(positive["positive_score"], 100) * positive_weight +
            quality["quality_score"] * quality_weight
        )
        
        # Bestäm hälsostatus
        if weighted_score >= 85:
            health_status = "🌟 EXCELLENT"
            health_description = "Projektet är i utmärkt skick och redo för produktion"
        elif weighted_score >= 75:
            health_status = "✅ VERY GOOD"
            health_description = "Projektet är i mycket bra skick med endast mindre förbättringar"
        elif weighted_score >= 65:
            health_status = "👍 GOOD"
            health_description = "Projektet är i bra skick med några förbättringsområden"
        elif weighted_score >= 50:
            health_status = "⚠️ FAIR"
            health_description = "Projektet är fungerande men behöver förbättringar"
        else:
            health_status = "❌ NEEDS WORK"
            health_description = "Projektet behöver betydande förbättringar"
        
        return {
            "intelligent_health_score": round(weighted_score, 1),
            "health_status": health_status,
            "health_description": health_description,
            "critical_analysis": critical,
            "positive_analysis": positive,
            "quality_analysis": quality,
            "score_breakdown": {
                "critical_component": round(critical["critical_score"] * critical_weight, 1),
                "positive_component": round(min(positive["positive_score"], 100) * positive_weight, 1),
                "quality_component": round(quality["quality_score"] * quality_weight, 1)
            }
        }
    
    def generate_intelligent_recommendations(self, health_data: Dict[str, Any]) -> List[str]:
        """Generera intelligenta rekommendationer"""
        recommendations = []
        
        critical = health_data["critical_analysis"]
        positive = health_data["positive_analysis"]
        quality = health_data["quality_analysis"]
        
        # Kritiska rekommendationer först
        if critical["syntax_errors"] > 0:
            recommendations.append(f"🚨 KRITISKT: Fix {critical['syntax_errors']} Python syntax errors immediately")
        
        if critical["broken_configs"]:
            recommendations.append(f"🔧 HIGH PRIORITY: Repair broken configuration files: {', '.join(critical['broken_configs'])}")
        
        if critical["critical_missing_files"]:
            recommendations.append(f"📝 IMPORTANT: Add missing critical files: {', '.join(critical['critical_missing_files'])}")
        
        # Kvalitetsförbättringar
        if quality["python_code_quality"] < 20:
            recommendations.append("💻 Improve Python code structure with more functions and classes per file")
        
        if quality["documentation_ratio"] < 15:
            recommendations.append("📚 Increase documentation coverage - add more .md files and docstrings")
        
        if quality["configuration_health"] < 15:
            recommendations.append("⚙️ Validate and fix configuration file formats")
        
        # Positiva förstärkningar
        if positive["comprehensive_structure"] >= 20:
            recommendations.append("🎉 STRENGTH: Excellent project structure with comprehensive file organization")
        
        if positive["advanced_features"] >= 20:
            recommendations.append("🚀 STRENGTH: Rich advanced features including AI, stealth, and enterprise capabilities")
        
        if positive["enterprise_ready"] >= 25:
            recommendations.append("🏢 STRENGTH: Enterprise-ready architecture with proper infrastructure components")
        
        # Optimeringsförslag
        if health_data["intelligent_health_score"] > 75:
            recommendations.append("✨ Consider adding automated testing and CI/CD pipelines for production readiness")
        
        return recommendations
    
    def print_intelligent_health_report(self, health_data: Dict[str, Any]):
        """Skriv ut intelligent hälsorapport"""
        
        print("\n" + "="*90)
        print("🎯 INTELLIGENT PROJECT HEALTH REPORT - SPARKLING OWL SPIN")
        print("="*90)
        
        # Huvudresultat
        score = health_data["intelligent_health_score"]
        status = health_data["health_status"]
        description = health_data["health_description"]
        
        print(f"\n🏆 ÖVERGRIPANDE HÄLSOSTATUS:")
        print(f"   • Score: {score}/100")
        print(f"   • Status: {status}")
        print(f"   • Beskrivning: {description}")
        
        # Score-breakdown
        breakdown = health_data["score_breakdown"]
        print(f"\n📊 SCORE-BREAKDOWN:")
        print(f"   • Kritiska problem (40%): {breakdown['critical_component']}/40")
        print(f"   • Positiva aspekter (35%): {breakdown['positive_component']}/35")
        print(f"   • Kodkvalitet (25%): {breakdown['quality_component']}/25")
        
        # Kritisk analys
        critical = health_data["critical_analysis"]
        print(f"\n🚨 KRITISKA PROBLEM:")
        print(f"   • Syntax-fel: {critical['syntax_errors']}")
        print(f"   • Brutna configs: {len(critical['broken_configs'])}")
        print(f"   • Saknade kritiska filer: {len(critical['critical_missing_files'])}")
        print(f"   • Kritisk score: {critical['critical_score']}/100")
        
        # Positiva aspekter
        positive = health_data["positive_analysis"]
        print(f"\n✨ POSITIVA ASPEKTER:")
        print(f"   • Omfattande struktur: {positive['comprehensive_structure']}/25")
        print(f"   • Rik dokumentation: {positive['rich_documentation']}/20")
        print(f"   • Testning: {positive['good_testing']}/20")
        print(f"   • Avancerade funktioner: {positive['advanced_features']}/25")
        print(f"   • Enterprise-färdighet: {positive['enterprise_ready']}/30")
        print(f"   • Totala positiva poäng: {positive['positive_score']}/120")
        
        # Kodkvalitet
        quality = health_data["quality_analysis"]
        print(f"\n💻 KODKVALITET:")
        print(f"   • Python kodkvalitet: {quality['python_code_quality']}/25")
        print(f"   • Dokumentationsratio: {quality['documentation_ratio']}/20")
        print(f"   • Konfigurationshälsa: {quality['configuration_health']}/20")
        print(f"   • Arkitekturmognad: {quality['architecture_maturity']}/25")
        print(f"   • Kvalitetscore: {quality['quality_score']}/90")
        
        print("="*90)
    
    def save_intelligent_health_report(self, health_data: Dict[str, Any]) -> Path:
        """Spara intelligent hälsorapport"""
        
        # Lägg till metadata
        full_report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "analyzer_version": "1.0.0",
            "project_name": "Sparkling Owl Spin",
            **health_data
        }
        
        # Spara rapport
        report_path = Path("intelligent_health_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Intelligent hälsorapport sparad till: {report_path}")
        return report_path
    
    def run_intelligent_analysis(self) -> Dict[str, Any]:
        """Kör intelligent hälsoanalys"""
        
        print(f"🔍 Analyserar projekthälsa baserat på {len(self.analysis_data.get('detailed_results', {}))} filer...")
        
        start_time = time.time()
        
        # Beräkna intelligent hälsa
        health_data = self.calculate_intelligent_health_score()
        
        # Generera intelligenta rekommendationer
        recommendations = self.generate_intelligent_recommendations(health_data)
        health_data["intelligent_recommendations"] = recommendations
        
        analysis_time = time.time() - start_time
        health_data["analysis_time"] = round(analysis_time, 2)
        
        # Visa rapport
        self.print_intelligent_health_report(health_data)
        
        # Visa rekommendationer
        if recommendations:
            print(f"\n💡 INTELLIGENTA REKOMMENDATIONER:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print(f"\n⏱️ Intelligent analys slutförd på {analysis_time:.2f} sekunder")
        
        # Spara rapport
        self.save_intelligent_health_report(health_data)
        
        return health_data

def run_intelligent_health_analysis() -> Dict[str, Any]:
    """Huvudfunktion för intelligent hälsoanalys"""
    
    analyzer = IntelligentHealthAnalyzer()
    health_data = analyzer.run_intelligent_analysis()
    
    # Slutstatus
    score = health_data["intelligent_health_score"]
    status = health_data["health_status"]
    
    print(f"\n" + "="*90)
    print(f"🎯 SLUTLIG BEDÖMNING: {status} ({score}/100)")
    print(f"🌟 {health_data['health_description']}")
    print("="*90)
    
    return health_data

if __name__ == "__main__":
    print("🚀 Startar intelligent hälsoanalys av Sparkling Owl Spin...")
    
    # Kör intelligent analys
    health_result = run_intelligent_health_analysis()
    
    print(f"🎉 Sparkling Owl Spin Intelligent Health Analysis Completed Successfully!")
