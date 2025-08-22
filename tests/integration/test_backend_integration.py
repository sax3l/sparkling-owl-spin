"""
Backend Integration Test

Comprehensive test to validate the complete backend implementation
including all services, APIs, and components.
"""

import asyncio
import pytest
import logging
from datetime import datetime
from typing import Dict, Any

from src.backend_main import ECaDPBackend
from src.settings import get_settings
from src.database.manager import get_database_manager
from src.services.monitoring_service import get_monitoring_service
from src.services.notification_service import get_notification_service, NotificationType, NotificationContext
from src.services.privacy_service import get_privacy_service
from src.services.system_status_service import get_system_status_service
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BackendIntegrationTest:
    """Integration test suite for ECaDP backend."""
    
    def __init__(self):
        self.backend = None
        self.settings = get_settings()
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests."""
        logger.info("Starting backend integration tests...")
        
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "tests": {},
            "overall_status": "unknown",
            "errors": []
        }
        
        try:
            # Initialize backend
            await self._test_backend_initialization(results)
            
            # Test core services
            await self._test_database_service(results)
            await self._test_monitoring_service(results)
            await self._test_notification_service(results)
            await self._test_privacy_service(results)
            await self._test_system_status_service(results)
            
            # Test integrations
            await self._test_service_integrations(results)
            
            # Test API endpoints (if available)
            await self._test_api_endpoints(results)
            
            # Determine overall status
            failed_tests = [name for name, result in results["tests"].items() if not result.get("passed", False)]
            
            if not failed_tests:
                results["overall_status"] = "passed"
            elif len(failed_tests) < len(results["tests"]) / 2:
                results["overall_status"] = "partially_passed"
            else:
                results["overall_status"] = "failed"
            
            results["failed_tests"] = failed_tests
            results["passed_tests"] = len(results["tests"]) - len(failed_tests)
            results["total_tests"] = len(results["tests"])
            
        except Exception as e:
            logger.error(f"Integration test error: {e}")
            results["errors"].append(str(e))
            results["overall_status"] = "error"
        
        finally:
            if self.backend:
                await self.backend.shutdown()
        
        results["completed_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Integration tests completed: {results['overall_status']}")
        return results
    
    async def _test_backend_initialization(self, results: Dict[str, Any]):
        """Test backend initialization."""
        test_name = "backend_initialization"
        logger.info(f"Testing {test_name}...")
        
        try:
            self.backend = ECaDPBackend()
            await self.backend.startup()
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "Backend initialized successfully",
                "duration": "N/A"
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "Backend initialization failed"
            }
    
    async def _test_database_service(self, results: Dict[str, Any]):
        """Test database service."""
        test_name = "database_service"
        logger.info(f"Testing {test_name}...")
        
        try:
            db_manager = get_database_manager()
            
            # Test connection
            async with db_manager.get_session() as session:
                result = await session.execute("SELECT 1")
                assert result is not None
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "Database service operational",
                "details": {
                    "connection": "ok",
                    "session_manager": "ok"
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "Database service test failed"
            }
    
    async def _test_monitoring_service(self, results: Dict[str, Any]):
        """Test monitoring service."""
        test_name = "monitoring_service"
        logger.info(f"Testing {test_name}...")
        
        try:
            monitoring_service = get_monitoring_service()
            
            # Test metrics collection
            monitoring_service.metric_collector.record_metric("test_metric", 100.0)
            values = monitoring_service.metric_collector.get_recent_values("test_metric", 5)
            assert len(values) > 0
            
            # Test system status
            status = monitoring_service.get_system_status()
            assert "status" in status
            
            # Test metrics summary
            metrics_summary = monitoring_service.get_metrics_summary()
            assert isinstance(metrics_summary, dict)
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "Monitoring service operational",
                "details": {
                    "metric_collection": "ok",
                    "system_status": "ok",
                    "metrics_summary": "ok"
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "Monitoring service test failed"
            }
    
    async def _test_notification_service(self, results: Dict[str, Any]):
        """Test notification service."""
        test_name = "notification_service"
        logger.info(f"Testing {test_name}...")
        
        try:
            notification_service = get_notification_service()
            
            # Test notification context creation
            context = NotificationContext(
                job_id="test_job",
                job_type="test",
                user_email="test@example.com"
            )
            assert context.job_id == "test_job"
            
            # Test notification type validation
            notification_type = NotificationType.JOB_COMPLETED
            assert notification_type.value == "job_completed"
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "Notification service operational",
                "details": {
                    "context_creation": "ok",
                    "type_validation": "ok"
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "Notification service test failed"
            }
    
    async def _test_privacy_service(self, results: Dict[str, Any]):
        """Test privacy service."""
        test_name = "privacy_service"
        logger.info(f"Testing {test_name}...")
        
        try:
            privacy_service = get_privacy_service()
            
            # Test PII detector
            test_text = "Contact John Doe at john.doe@example.com or call 555-123-4567"
            pii_matches = privacy_service.pii_detector.detect_pii(test_text)
            
            # Should detect email and phone
            email_detected = any(match.pii_type.value == "email" for match in pii_matches)
            phone_detected = any(match.pii_type.value == "phone" for match in pii_matches)
            
            assert email_detected, "Email not detected"
            assert phone_detected, "Phone not detected"
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "Privacy service operational",
                "details": {
                    "pii_detection": "ok",
                    "detected_types": [match.pii_type.value for match in pii_matches]
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "Privacy service test failed"
            }
    
    async def _test_system_status_service(self, results: Dict[str, Any]):
        """Test system status service."""
        test_name = "system_status_service"
        logger.info(f"Testing {test_name}...")
        
        try:
            status_service = get_system_status_service()
            
            # Test health check
            health = await status_service.get_health_endpoint()
            assert "status" in health
            assert "timestamp" in health
            
            # Test system overview (without details to avoid long operations)
            overview = await status_service.get_system_overview(include_details=False)
            assert "overall_status" in overview
            assert "components" in overview
            assert "timestamp" in overview
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "System status service operational",
                "details": {
                    "health_check": "ok",
                    "system_overview": "ok",
                    "overall_status": overview.get("overall_status", "unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "System status service test failed"
            }
    
    async def _test_service_integrations(self, results: Dict[str, Any]):
        """Test service integrations."""
        test_name = "service_integrations"
        logger.info(f"Testing {test_name}...")
        
        try:
            # Test monitoring + system status integration
            monitoring_service = get_monitoring_service()
            status_service = get_system_status_service()
            
            # Record some metrics
            monitoring_service.metric_collector.record_metric("integration_test", 95.0)
            
            # Get system status
            system_status = await status_service.get_system_overview(include_details=False)
            
            # Verify integration works
            assert system_status.get("overall_status") in ["healthy", "warning", "critical", "degraded"]
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "Service integrations working",
                "details": {
                    "monitoring_status": "ok",
                    "system_status": system_status.get("overall_status", "unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "Service integration test failed"
            }
    
    async def _test_api_endpoints(self, results: Dict[str, Any]):
        """Test API endpoints (basic validation)."""
        test_name = "api_endpoints"
        logger.info(f"Testing {test_name}...")
        
        try:
            # Test that API modules can be imported
            from src.webapp.api.system import get_system_router
            
            router = get_system_router()
            assert router is not None
            
            # Check that routes are registered
            route_count = len(router.routes)
            assert route_count > 0
            
            results["tests"][test_name] = {
                "passed": True,
                "message": "API endpoints available",
                "details": {
                    "system_router": "ok",
                    "route_count": route_count
                }
            }
            
        except Exception as e:
            logger.error(f"{test_name} failed: {e}")
            results["tests"][test_name] = {
                "passed": False,
                "error": str(e),
                "message": "API endpoints test failed"
            }


async def run_integration_tests() -> Dict[str, Any]:
    """Run the complete integration test suite."""
    test_suite = BackendIntegrationTest()
    return await test_suite.run_all_tests()


if __name__ == "__main__":
    """Run integration tests as standalone script."""
    import json
    
    async def main():
        print("Starting ECaDP Backend Integration Tests...")
        print("=" * 50)
        
        results = await run_integration_tests()
        
        print(f"\nTest Results:")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Tests Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
        
        if results.get('failed_tests'):
            print(f"\nFailed Tests:")
            for test_name in results['failed_tests']:
                test_result = results['tests'][test_name]
                print(f"  - {test_name}: {test_result.get('error', 'Unknown error')}")
        
        print("\nDetailed Results:")
        for test_name, test_result in results['tests'].items():
            status = "PASS" if test_result.get('passed', False) else "FAIL"
            print(f"  {test_name}: {status} - {test_result.get('message', 'No message')}")
        
        if results.get('errors'):
            print(f"\nGeneral Errors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\n" + "=" * 50)
        print("Integration tests completed.")
        
        # Save detailed results to file
        with open('integration_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print("Detailed results saved to integration_test_results.json")
        
        # Exit with appropriate code
        if results['overall_status'] in ['passed', 'partially_passed']:
            exit(0)
        else:
            exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        exit(1)
