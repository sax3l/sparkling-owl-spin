"""
System Integration Test Suite
============================

Comprehensive test suite to verify system integrity after cleanup and test creation.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestSystemIntegrity:
    """Tests to verify system integrity after duplicate removal and test creation"""
    
    def test_no_duplicate_metrics_files(self):
        """Verify that duplicate metrics files have been removed"""
        
        project_root = Path(__file__).parent.parent
        
        # Check that metrics_new.py no longer exists
        metrics_new_path = project_root / "src" / "observability" / "metrics_new.py"
        assert not metrics_new_path.exists(), "Duplicate metrics_new.py should have been removed"
        
        # Check that original metrics.py still exists
        metrics_path = project_root / "src" / "observability" / "metrics.py"
        assert metrics_path.exists(), "Original metrics.py should still exist"
    
    def test_analysis_module_imports(self):
        """Test that all analysis modules can be imported successfully"""
        
        # Set mock environment variable to avoid database connection error
        import os
        original_db_url = os.environ.get('SUPABASE_DB_URL')
        os.environ['SUPABASE_DB_URL'] = 'postgresql://mock:mock@localhost/mock'
        
        try:
            # Test data analyzer import
            try:
                from src.analysis.data_analyzer import DataAnalyzer
                assert DataAnalyzer is not None
            except ImportError as e:
                pytest.fail(f"Failed to import DataAnalyzer: {e}")
            
            # Test quality checker import  
            try:
                from src.analysis.quality_checker import QualityChecker
                assert QualityChecker is not None
            except ImportError as e:
                pytest.fail(f"Failed to import QualityChecker: {e}")
            
            # Test trend analyzer import
            try:
                from src.analysis.trend_analyzer import TrendAnalyzer
                assert TrendAnalyzer is not None
            except ImportError as e:
                pytest.fail(f"Failed to import TrendAnalyzer: {e}")
            
            # Test report generator import
            try:
                from src.analysis.report_generator import ReportGenerator
                assert ReportGenerator is not None
            except ImportError as e:
                pytest.fail(f"Failed to import ReportGenerator: {e}")
        
        finally:
            # Restore original environment
            if original_db_url is not None:
                os.environ['SUPABASE_DB_URL'] = original_db_url
            elif 'SUPABASE_DB_URL' in os.environ:
                del os.environ['SUPABASE_DB_URL']
    
    def test_test_files_exist(self):
        """Verify that all required test files have been created"""
        
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
            
            # Verify file has content (not empty)
            assert test_path.stat().st_size > 1000, f"Test file {test_file} appears to be too small/empty"
        
        # Check integration test file
        integration_test_path = tests_integration_dir / "test_analysis_integration.py"
        assert integration_test_path.exists(), "Integration test file is missing"
        assert integration_test_path.stat().st_size > 2000, "Integration test file appears to be too small"
    
    def test_exporters_alias_relationship(self):
        """Verify that sheets_exporter alias relationship is maintained"""
        
        project_root = Path(__file__).parent.parent
        exporters_dir = project_root / "src" / "exporters"
        
        # Check that both files exist
        google_sheets_path = exporters_dir / "google_sheets_exporter.py"
        sheets_path = exporters_dir / "sheets_exporter.py"
        
        assert google_sheets_path.exists(), "google_sheets_exporter.py should exist"
        assert sheets_path.exists(), "sheets_exporter.py should exist"
        
        # Verify they are different files (not duplicates)
        google_sheets_size = google_sheets_path.stat().st_size
        sheets_size = sheets_path.stat().st_size
        
        # sheets_exporter.py should be smaller (it's an alias/import file)
        assert sheets_size < google_sheets_size, "sheets_exporter.py should be smaller than google_sheets_exporter.py"
    
    def test_database_manager_uniqueness(self):
        """Verify that there's only one DatabaseManager implementation"""
        
        # Set mock environment variable to avoid database connection error
        import os
        original_db_url = os.environ.get('SUPABASE_DB_URL')
        os.environ['SUPABASE_DB_URL'] = 'postgresql://mock:mock@localhost/mock'
        
        try:
            from src.database.manager import DatabaseManager
            assert DatabaseManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import DatabaseManager: {e}")
        finally:
            # Restore original environment
            if original_db_url is not None:
                os.environ['SUPABASE_DB_URL'] = original_db_url
            elif 'SUPABASE_DB_URL' in os.environ:
                del os.environ['SUPABASE_DB_URL']
        
        # Verify no conflicting implementations
        try:
            from src.webapp.database import DatabaseManager as WebappDatabaseManager
            pytest.fail("Found conflicting DatabaseManager in webapp.database - this should not exist")
        except ImportError:
            # This is expected - there should be no DatabaseManager in webapp.database
            pass
    
    def test_validation_functions_consistency(self):
        """Test that validation functions work consistently"""
        
        # Set mock environment variable
        import os
        original_db_url = os.environ.get('SUPABASE_DB_URL')
        os.environ['SUPABASE_DB_URL'] = 'postgresql://mock:mock@localhost/mock'
        
        try:
            from src.webapp.utils.validation import validate_template, TemplateValidator
            
            # Test data
            test_template = {
                'name': 'Test Template',
                'selectors': {
                    'title': 'h1',
                    'content': '.content'
                }
            }
            
            # Test both approaches
            validator_instance = TemplateValidator()
            result1 = validator_instance.validate_template(test_template)
            result2 = validate_template(test_template)
            
            # Results should be consistent
            assert result1.is_valid == result2.is_valid
            assert abs(result1.score - result2.score) < 0.01  # Allow small floating point differences
            
        except ImportError as e:
            pytest.fail(f"Failed to import validation functions: {e}")
        finally:
            # Restore original environment
            if original_db_url is not None:
                os.environ['SUPABASE_DB_URL'] = original_db_url
            elif 'SUPABASE_DB_URL' in os.environ:
                del os.environ['SUPABASE_DB_URL']
    
    def test_utils_functions_no_conflicts(self):
        """Test that utility functions don't conflict with each other"""
        
        # Set mock environment variable
        import os
        original_db_url = os.environ.get('SUPABASE_DB_URL')
        os.environ['SUPABASE_DB_URL'] = 'postgresql://mock:mock@localhost/mock'
        
        try:
            # Test sanitization functions
            from src.utils.validators import get_validator
            from src.webapp.utils.security import SecurityUtils
            
            # Create test instances
            validator = get_validator('url')
            security_utils = SecurityUtils()
            
            # Test that they work independently
            assert validator is not None
            assert security_utils is not None
            
            # Test sanitization functions handle same input differently (as expected)
            test_input = "<script>alert('test')</script>Hello World"
            
            # This should work without conflicts
            sanitized_by_security = security_utils.sanitize_string(test_input)
            
            # Both should handle the input but with different approaches
            assert sanitized_by_security != test_input  # Should be modified
            
        except ImportError as e:
            pytest.fail(f"Failed to import utils functions: {e}")
        finally:
            # Restore original environment
            if original_db_url is not None:
                os.environ['SUPABASE_DB_URL'] = original_db_url
            elif 'SUPABASE_DB_URL' in os.environ:
                del os.environ['SUPABASE_DB_URL']
    
    def test_analysis_components_integration(self):
        """Test that analysis components can be instantiated together"""
        
        from unittest.mock import AsyncMock
        
        # Set mock environment variable
        import os
        original_db_url = os.environ.get('SUPABASE_DB_URL')
        os.environ['SUPABASE_DB_URL'] = 'postgresql://mock:mock@localhost/mock'
        
        try:
            from src.analysis.data_analyzer import DataAnalyzer
            from src.analysis.quality_checker import QualityChecker
            from src.analysis.trend_analyzer import TrendAnalyzer
            from src.analysis.report_generator import ReportGenerator
            from src.database.manager import DatabaseManager
            
            # Create mock database manager
            mock_db = AsyncMock(spec=DatabaseManager)
            
            # Create all components
            data_analyzer = DataAnalyzer(mock_db)
            quality_checker = QualityChecker(mock_db)
            trend_analyzer = TrendAnalyzer(mock_db)
            report_generator = ReportGenerator(mock_db, data_analyzer, quality_checker, trend_analyzer)
            
            # Verify they were created successfully
            assert data_analyzer is not None
            assert quality_checker is not None
            assert trend_analyzer is not None
            assert report_generator is not None
            
            # Verify they have expected methods
            assert hasattr(data_analyzer, 'analyze_extraction_volume')
            assert hasattr(quality_checker, 'assess_quality')
            assert hasattr(trend_analyzer, 'analyze_extraction_trends')
            assert hasattr(report_generator, 'generate_daily_report')
            
        except Exception as e:
            pytest.fail(f"Failed to integrate analysis components: {e}")
        finally:
            # Restore original environment
            if original_db_url is not None:
                os.environ['SUPABASE_DB_URL'] = original_db_url
            elif 'SUPABASE_DB_URL' in os.environ:
                del os.environ['SUPABASE_DB_URL']
    
    def test_project_structure_integrity(self):
        """Test that the project structure is intact after cleanup"""
        
        project_root = Path(__file__).parent.parent
        
        # Check key directories exist
        required_dirs = [
            "src",
            "src/analysis", 
            "src/database",
            "src/exporters",
            "src/utils",
            "src/webapp",
            "tests",
            "tests/unit",
            "tests/integration"
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            assert full_path.exists() and full_path.is_dir(), f"Required directory {dir_path} is missing"
        
        # Check key files exist
        required_files = [
            "src/__init__.py",
            "src/analysis/__init__.py",
            "src/database/__init__.py",
            "src/exporters/__init__.py",
            "pyproject.toml",
            "requirements.txt"
        ]
        
        for file_path in required_files:
            full_path = project_root / file_path
            assert full_path.exists() and full_path.is_file(), f"Required file {file_path} is missing"


if __name__ == '__main__':
    pytest.main([__file__])
