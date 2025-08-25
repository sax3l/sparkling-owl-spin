#!/usr/bin/env python3
"""
Final Validation Script for Pyramid Architecture Reorganization
Verifierar att alla nya komponenter fungerar korrekt
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pyramid_validation")

async def validate_core_architecture():
    """Validate core architecture components"""
    logger.info("🏗️ Validating Core Architecture...")
    
    results = {}
    
    try:
        # Test base classes import
        from core.base_classes import (
            BaseService, BaseAgent, BaseEngine, BaseScheduler, 
            ServiceStatus, Priority, TaskRequest, TaskResponse
        )
        results['base_classes'] = "✅ Successfully imported all base classes"
        
        # Test service instantiation
        class TestService(BaseService):
            async def start(self):
                return True
            async def stop(self):
                return True
            async def health_check(self):
                return {'status': 'healthy'}
                
        test_service = TestService("test_service")
        results['service_creation'] = "✅ BaseService instantiation works"
        
        # Test agent instantiation
        class TestAgent(BaseAgent):
            async def execute_task(self, task):
                return {'status': 'completed'}
                
        test_agent = TestAgent("test_agent", "Test Agent", ["testing"])
        results['agent_creation'] = "✅ BaseAgent instantiation works"
        
        # Test engine instantiation
        class TestEngine(BaseEngine):
            async def process(self, data, config=None):
                return {'processed': data}
            async def validate_config(self, config):
                return True
                
        test_engine = TestEngine("test_engine", "Test Engine", "test")
        results['engine_creation'] = "✅ BaseEngine instantiation works"
        
    except Exception as e:
        results['core_error'] = f"❌ Core architecture validation failed: {e}"
        
    return results

async def validate_registry_system():
    """Validate service registry functionality"""
    logger.info("📋 Validating Service Registry...")
    
    results = {}
    
    try:
        from core.registry import ServiceRegistry, get_registry
        from core.base_classes import BaseService
        
        # Test registry creation
        registry = ServiceRegistry()
        results['registry_creation'] = "✅ ServiceRegistry instantiation works"
        
        # Test service registration
        class MockService(BaseService):
            async def start(self):
                self.status = ServiceStatus.RUNNING
                return True
            async def stop(self):
                self.status = ServiceStatus.STOPPED
                return True
            async def health_check(self):
                return {'status': 'healthy'}
                
        from core.base_classes import ServiceStatus
        mock_service = MockService("mock_service")
        await registry.register_service(mock_service)
        
        # Test service retrieval
        retrieved = await registry.get_service("mock_service")
        if retrieved and retrieved.name == "mock_service":
            results['service_registration'] = "✅ Service registration and retrieval works"
        else:
            results['service_registration'] = "❌ Service registration failed"
            
        # Test registry stats
        stats = await registry.get_registry_stats()
        if stats and 'total_services' in stats:
            results['registry_stats'] = "✅ Registry statistics work"
        else:
            results['registry_stats'] = "❌ Registry statistics failed"
            
    except Exception as e:
        results['registry_error'] = f"❌ Registry validation failed: {e}"
        
    return results

async def validate_scheduler_system():
    """Validate scheduler functionality"""
    logger.info("⏰ Validating Scheduler System...")
    
    results = {}
    
    try:
        # Import scheduler classes
        from engines.processing.scheduler import EnhancedBFSScheduler, CrawlTask, Priority
        
        # Test scheduler creation
        scheduler = EnhancedBFSScheduler("test_scheduler")
        results['scheduler_creation'] = "✅ EnhancedBFSScheduler instantiation works"
        
        # Test URL addition
        task_id = await scheduler.add_url("https://example.com", depth=0, priority=Priority.NORMAL)
        if task_id:
            results['url_addition'] = "✅ URL addition works"
        else:
            results['url_addition'] = "❌ URL addition failed"
            
        # Test task retrieval
        task = await scheduler.get_next_task()
        if task and task.url == "https://example.com":
            results['task_retrieval'] = "✅ Task retrieval works"
            # Mark task as completed
            await scheduler.mark_task_completed(task.id, {'success': True})
            results['task_completion'] = "✅ Task completion works"
        else:
            results['task_retrieval'] = "❌ Task retrieval failed"
            
        # Test statistics
        stats = await scheduler.get_detailed_stats()
        if stats and 'total_scheduled' in stats:
            results['scheduler_stats'] = "✅ Scheduler statistics work"
        else:
            results['scheduler_stats'] = "❌ Scheduler statistics failed"
            
    except Exception as e:
        results['scheduler_error'] = f"❌ Scheduler validation failed: {e}"
        
    return results

async def validate_agent_system():
    """Validate agent system functionality"""
    logger.info("🤖 Validating Agent System...")
    
    results = {}
    
    try:
        # Test scraping specialist
        try:
            from agents.scraping_specialist import ScrapingSpecialist
            specialist = ScrapingSpecialist("test_specialist")
            results['scraping_specialist'] = "✅ ScrapingSpecialist instantiation works"
            
            # Test capabilities
            if "web_scraping" in specialist.capabilities:
                results['specialist_capabilities'] = "✅ Specialist capabilities work"
            else:
                results['specialist_capabilities'] = "❌ Specialist capabilities missing"
                
        except Exception as e:
            results['scraping_specialist'] = f"❌ ScrapingSpecialist failed: {e}"
            
        # Test security analyst
        try:
            from agents.security_analyst import SecurityAnalyst
            analyst = SecurityAnalyst("test_analyst")
            results['security_analyst'] = "✅ SecurityAnalyst instantiation works"
            
            # Test capabilities
            if "security_analysis" in analyst.capabilities:
                results['analyst_capabilities'] = "✅ Analyst capabilities work"
            else:
                results['analyst_capabilities'] = "❌ Analyst capabilities missing"
                
        except Exception as e:
            results['security_analyst'] = f"❌ SecurityAnalyst failed: {e}"
            
    except Exception as e:
        results['agent_error'] = f"❌ Agent system validation failed: {e}"
        
    return results

async def validate_configuration():
    """Validate configuration system"""
    logger.info("⚙️ Validating Configuration System...")
    
    results = {}
    
    try:
        import yaml
        config_path = Path("config/default.yaml")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            if config:
                results['config_loading'] = "✅ Configuration file loads successfully"
                
                # Check main sections
                required_sections = ['agents', 'scraping', 'security', 'core']
                missing_sections = [s for s in required_sections if s not in config]
                
                if not missing_sections:
                    results['config_sections'] = "✅ All required configuration sections present"
                else:
                    results['config_sections'] = f"❌ Missing sections: {missing_sections}"
                    
                # Check agent configurations
                if 'agents' in config and 'scraping_specialist' in config['agents']:
                    results['agent_config'] = "✅ Agent configurations present"
                else:
                    results['agent_config'] = "❌ Agent configurations missing"
                    
            else:
                results['config_loading'] = "❌ Configuration file is empty"
        else:
            results['config_loading'] = "❌ Configuration file not found"
            
    except Exception as e:
        results['config_error'] = f"❌ Configuration validation failed: {e}"
        
    return results

async def validate_file_structure():
    """Validate file structure and organization"""
    logger.info("📁 Validating File Structure...")
    
    results = {}
    
    # Check core files
    core_files = [
        "core/base_classes.py",
        "core/registry.py",
        "core/__init__.py"
    ]
    
    missing_core = [f for f in core_files if not Path(f).exists()]
    if not missing_core:
        results['core_files'] = "✅ All core files present"
    else:
        results['core_files'] = f"❌ Missing core files: {missing_core}"
        
    # Check agent files
    agent_files = [
        "agents/scraping_specialist.py",
        "agents/security_analyst.py",
        "agents/__init__.py"
    ]
    
    missing_agents = [f for f in agent_files if not Path(f).exists()]
    if not missing_agents:
        results['agent_files'] = "✅ All agent files present"
    else:
        results['agent_files'] = f"❌ Missing agent files: {missing_agents}"
        
    # Check engine files
    engine_files = [
        "engines/processing/scheduler.py",
        "engines/__init__.py"
    ]
    
    missing_engines = [f for f in engine_files if not Path(f).exists()]
    if not missing_engines:
        results['engine_files'] = "✅ Engine files present"
    else:
        results['engine_files'] = f"❌ Missing engine files: {missing_engines}"
        
    # Check configuration
    config_files = [
        "config/default.yaml"
    ]
    
    missing_config = [f for f in config_files if not Path(f).exists()]
    if not missing_config:
        results['config_files'] = "✅ Configuration files present"
    else:
        results['config_files'] = f"❌ Missing config files: {missing_config}"
        
    # Check documentation
    doc_files = [
        "COMPLETE_DOCUMENTATION_CONSOLIDATED.md",
        "COMPLETE_PROJECT_SUMMARY.md",
        "PYRAMID_REORGANIZATION_COMPLETE.md"
    ]
    
    missing_docs = [f for f in doc_files if not Path(f).exists()]
    if not missing_docs:
        results['documentation'] = "✅ All documentation files present"
    else:
        results['documentation'] = f"❌ Missing documentation: {missing_docs}"
        
    return results

async def main():
    """Main validation function"""
    logger.info("🚀 Starting Pyramid Architecture Validation...")
    
    all_results = {}
    
    # Run all validations
    validations = [
        ("File Structure", validate_file_structure()),
        ("Configuration", validate_configuration()),
        ("Core Architecture", validate_core_architecture()),
        ("Registry System", validate_registry_system()),
        ("Scheduler System", validate_scheduler_system()),
        ("Agent System", validate_agent_system())
    ]
    
    for name, validation_coro in validations:
        try:
            results = await validation_coro
            all_results[name] = results
        except Exception as e:
            all_results[name] = {"validation_error": f"❌ {name} validation crashed: {e}"}
    
    # Print results
    print("\n" + "="*80)
    print("🏗️ PYRAMID ARCHITECTURE VALIDATION REPORT")
    print("="*80)
    
    total_tests = 0
    passed_tests = 0
    
    for section_name, section_results in all_results.items():
        print(f"\n📋 {section_name}:")
        print("-" * (len(section_name) + 4))
        
        for test_name, result in section_results.items():
            print(f"  {result}")
            total_tests += 1
            if result.startswith("✅"):
                passed_tests += 1
    
    # Summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n🎉 PYRAMID ARCHITECTURE VALIDATION: EXCELLENT! 🎉")
        status = "EXCELLENT"
    elif success_rate >= 75:
        print(f"\n✅ PYRAMID ARCHITECTURE VALIDATION: GOOD!")
        status = "GOOD"
    elif success_rate >= 50:
        print(f"\n⚠️ PYRAMID ARCHITECTURE VALIDATION: NEEDS WORK")
        status = "NEEDS_WORK"
    else:
        print(f"\n❌ PYRAMID ARCHITECTURE VALIDATION: FAILED")
        status = "FAILED"
    
    # Save results to file
    import json
    with open("pyramid_validation_results.json", "w") as f:
        json.dump({
            "timestamp": str(asyncio.get_event_loop().time()),
            "status": status,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "detailed_results": all_results
        }, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: pyramid_validation_results.json")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
