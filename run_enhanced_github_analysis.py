#!/usr/bin/env python3
"""
Run Enhanced GitHub Analysis
===========================

Startar den förbättrade GitHub repository analysen med full integration
mot vårt Ultimate Scraping System.
"""

import asyncio
import sys
from pathlib import Path

# Lägg till projektrot till path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from enhanced_github_analysis_system import EnhancedGitHubAnalysisSystem

async def main():
    """Kör den förbättrade GitHub analysen."""
    
    print("🚀 STARTING ENHANCED GITHUB REPOSITORY ANALYSIS")
    print("=" * 60)
    print("🎯 Target: Comprehensive analysis of ALL GitHub repositories")
    print("🔧 System: Ultimate Scraping System Integration")
    print("📊 Features: Advanced categorization, priority analysis, integration assessment")
    print("=" * 60)
    
    try:
        # Skapa och kör analysis system
        analysis_system = EnhancedGitHubAnalysisSystem()
        
        # Kör komplett analys
        await analysis_system.initialize()
        await analysis_system.run_comprehensive_repository_analysis()
        
        print("\n🎉 ENHANCED GITHUB ANALYSIS COMPLETED!")
        print("📄 Check the generated reports in the 'reports' directory")
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        try:
            await analysis_system.shutdown()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
