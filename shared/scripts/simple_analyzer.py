#!/usr/bin/env python3
"""
Simple structure analyzer that counts files manually.
"""

import os
from pathlib import Path

def count_files_simple():
    """Count files by scanning directories."""
    project_root = Path(__file__).parent.parent
    
    # Define expected counts per category
    expected_counts = {
        "root": 24,
        "config": 18,
        "docs": 55,
        "docker": 44,
        "iac": 40,
        "src_webapp": 38,
        "src_crawler": 11,
        "src_scraper": 22,
        "src_exporters": 11,
        "src_complete": 105,
        "frontend": 47,
        "data": 12,
        "scripts": 22,
        "tests_complete": 80,
        "observability": 10,
        "sdk": 24,
        "supabase": 13,
        "api_clients": 4,
        "github_workflows": 21,
        "examples": 7,
        "notebooks": 2,
        "legal": 4,
        "bin": 4,
        "monitoring": 14,
        "extension": 10,
        "infra": 28,
        "clients": 2,
        "lovable": 3,
        "ops": 10,
        "generated": 2
    }
    
    # Count existing files by directory
    existing_counts = {}
    
    # Root files
    root_files = [f for f in os.listdir(project_root) if os.path.isfile(project_root / f)]
    existing_counts["root"] = len(root_files)
    
    # Count other directories
    for category in ["config", "docs", "docker", "src", "frontend", "data", "scripts", 
                     "tests", "observability", "sdk", "supabase", "bin", "monitoring", 
                     "extension", "infra", "clients", "lovable", "ops", "generated"]:
        
        dir_path = project_root / category
        if dir_path.exists():
            # Count all files recursively
            file_count = sum(1 for _ in dir_path.rglob("*") if _.is_file())
            existing_counts[category] = file_count
        else:
            existing_counts[category] = 0
    
    # Special handling for exporters
    exporters_path = project_root / "src" / "exporters"
    if exporters_path.exists():
        existing_counts["src_exporters"] = sum(1 for _ in exporters_path.rglob("*") if _.is_file())
    else:
        existing_counts["src_exporters"] = 0
    
    # Special handling for .github workflows
    github_path = project_root / ".github"
    if github_path.exists():
        existing_counts["github_workflows"] = sum(1 for _ in github_path.rglob("*") if _.is_file())
    else:
        existing_counts["github_workflows"] = 0
    
    # Special handling for iac
    iac_path = project_root / "iac"
    if iac_path.exists():
        existing_counts["iac"] = sum(1 for _ in iac_path.rglob("*") if _.is_file())
    else:
        existing_counts["iac"] = 0
    
    # Special handling for api_clients
    api_clients_path = project_root / "api_clients"
    if api_clients_path.exists():
        existing_counts["api_clients"] = sum(1 for _ in api_clients_path.rglob("*") if _.is_file())
    else:
        existing_counts["api_clients"] = 0
    
    # Special handling for examples
    examples_path = project_root / "examples"
    if examples_path.exists():
        existing_counts["examples"] = sum(1 for _ in examples_path.rglob("*") if _.is_file())
    else:
        existing_counts["examples"] = 0
    
    # Special handling for notebooks
    notebooks_path = project_root / "notebooks"
    if notebooks_path.exists():
        existing_counts["notebooks"] = sum(1 for _ in notebooks_path.rglob("*") if _.is_file())
    else:
        existing_counts["notebooks"] = 0
    
    # Special handling for legal
    legal_path = project_root / "legal"
    if legal_path.exists():
        existing_counts["legal"] = sum(1 for _ in legal_path.rglob("*") if _.is_file())
    else:
        existing_counts["legal"] = 0
    
    # Calculate totals
    total_expected = sum(expected_counts.values())
    total_existing = sum(existing_counts.values())
    completion_percentage = (total_existing / total_expected * 100) if total_expected > 0 else 0
    
    print("=" * 80)
    print("SIMPLE PROJECT STRUCTURE ANALYSIS")
    print("=" * 80)
    print(f"Total expected files: {total_expected}")
    print(f"Total existing files: {total_existing}")
    print(f"Completion: {completion_percentage:.1f}%")
    print()
    
    print("COMPLETION BY CATEGORY:")
    print("-" * 80)
    for category in sorted(expected_counts.keys()):
        expected = expected_counts[category]
        existing = existing_counts.get(category, 0)
        category_percentage = (existing / expected * 100) if expected > 0 else 0
        missing = expected - existing
        
        status_icon = "✅" if category_percentage == 100 else "🟡" if category_percentage >= 50 else "❌"
        print(f"{status_icon} {category:20} {existing:3d}/{expected:3d} ({category_percentage:5.1f}%) - {missing} missing")

if __name__ == "__main__":
    count_files_simple()
