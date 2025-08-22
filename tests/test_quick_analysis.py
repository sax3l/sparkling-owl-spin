"""
Quick Analysis Import Test
=========================

Test analysis modules without database dependencies.
"""

def test_analysis_files_exist():
    """Test that analysis module files exist and are readable"""
    
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    analysis_dir = project_root / "src" / "analysis"
    
    # Check that analysis directory exists
    assert analysis_dir.exists() and analysis_dir.is_dir()
    
    # Check required analysis files
    required_files = [
        "data_analyzer.py",
        "quality_checker.py", 
        "trend_analyzer.py",
        "report_generator.py"
    ]
    
    for file_name in required_files:
        file_path = analysis_dir / file_name
        assert file_path.exists(), f"Analysis file {file_name} is missing"
        assert file_path.stat().st_size > 1000, f"Analysis file {file_name} appears to be too small"
        
        # Check that the file contains expected class definitions
        content = file_path.read_text(encoding='utf-8')
        class_name = file_name.replace('.py', '').replace('_', ' ').title().replace(' ', '')
        assert f"class {class_name}" in content, f"Class {class_name} not found in {file_name}"


def test_test_files_exist():
    """Test that test files exist for all analysis modules"""
    
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    tests_unit_dir = project_root / "tests" / "unit"
    tests_integration_dir = project_root / "tests" / "integration"
    
    # Check unit test files
    required_unit_tests = [
        "test_data_analyzer.py",
        "test_quality_checker.py", 
        "test_trend_analyzer.py",
        "test_report_generator.py"
    ]
    
    for test_file in required_unit_tests:
        test_path = tests_unit_dir / test_file
        assert test_path.exists(), f"Required unit test file {test_file} is missing"
        assert test_path.stat().st_size > 1000, f"Test file {test_file} appears to be too small"
        
        # Check that test file contains test classes
        content = test_path.read_text(encoding='utf-8')
        assert "class Test" in content, f"No test class found in {test_file}"
        assert "pytest" in content, f"No pytest usage found in {test_file}"
    
    # Check integration test file
    integration_test_path = tests_integration_dir / "test_analysis_integration.py"
    assert integration_test_path.exists(), "Integration test file is missing"
    assert integration_test_path.stat().st_size > 2000, "Integration test file appears to be too small"


def test_duplicate_metrics_removed():
    """Test that duplicate metrics file has been removed"""
    
    from pathlib import Path
    
    project_root = Path(__file__).parent.parent
    
    # Check that metrics_new.py no longer exists
    metrics_new_path = project_root / "src" / "observability" / "metrics_new.py"
    assert not metrics_new_path.exists(), "Duplicate metrics_new.py should have been removed"
    
    # Check that original metrics.py still exists
    metrics_path = project_root / "src" / "observability" / "metrics.py"
    assert metrics_path.exists(), "Original metrics.py should still exist"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__])
