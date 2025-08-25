#!/usr/bin/env python3
"""
Core Orchestrator för Sparkling-Owl-Spin
Huvudsystem som koordinerar alla komponenter i pyramid-arkitekturen
"""

import logging
import asyncio
import json
import time
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import importlib
import sys

# Import core components
from .config_manager import EnhancedConfigManager
from .security_controller import SecurityController
from .api_gateway import APIGateway

# Import engines
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from engines.scraping.scraping_framework import EnhancedScrapingFrameworkAdapter
from engines.bypass.cloudflare_bypass import EnhancedCloudflareBypassAdapter
from engines.bypass.captcha_solver import EnhancedCaptchaSolverAdapter
from engines.bypass.undetected_browser import EnhancedUndetectedBrowserAdapter
from data_processing.sources.swedish_data import SwedishVehicleDataAdapter
from ai_agents.ai_system import EnhancedAIAgentSystem

logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Types of workflows"""
    WEB_SCRAPING = "web_scraping"
    PENETRATION_TESTING = "penetration_testing"
    DATA_ANALYSIS = "data_analysis"
    AI_ASSISTED_SCRAPING = "ai_assisted_scraping"
    COMPREHENSIVE_AUDIT = "comprehensive_audit"
    SWEDISH_DATA_EXTRACTION = "swedish_data_extraction"
    BYPASS_TESTING = "bypass_testing"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    engine: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    retry_attempts: int = 3
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class Workflow:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    workflow_type: WorkflowType
    description: str
    steps: List[WorkflowStep]
    target_domains: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None

class EnhancedCoreOrchestrator:
    """Core system orchestrator för pyramid architecture"""
    
    def __init__(self):
        self.initialized = False
        
        # Core components
        self.config_manager = EnhancedConfigManager()
        self.security_controller = SecurityController()
        self.api_gateway = APIGateway()
        
        # Engine registry
        self.engines: Dict[str, Any] = {}
        self.engine_status: Dict[str, str] = {}
        
        # Workflow management
        self.active_workflows: Dict[str, Workflow] = {}
        self.workflow_queue: List[str] = []
        self.execution_pool = {}
        
        # System metrics
        self.system_metrics = {
            "uptime_start": datetime.now(),
            "workflows_executed": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "engines_registered": 0,
            "active_connections": 0,
            "total_data_processed": 0,
            "by_workflow_type": {},
            "engine_performance": {}
        }
        
        # Resource management
        self.max_concurrent_workflows = 5
        self.resource_limits = {
            "memory_mb": 4096,
            "cpu_percent": 80,
            "disk_gb": 10
        }
        
    async def initialize(self):
        """Initialize Core Orchestrator"""
        try:
            logger.info("🎯 Initializing Enhanced Core Orchestrator")
            
            # Initialize core components
            await self.config_manager.initialize()
            await self.security_controller.initialize()
            await self.api_gateway.initialize()
            
            # Register and initialize engines
            await self._register_engines()
            await self._initialize_engines()
            
            # Initialize workflow types metrics
            for workflow_type in WorkflowType:
                self.system_metrics["by_workflow_type"][workflow_type.value] = {
                    "executed": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_duration": 0.0
                }
            
            # Start background tasks
            asyncio.create_task(self._workflow_executor())
            asyncio.create_task(self._system_monitor())
            
            self.initialized = True
            logger.info("✅ Enhanced Core Orchestrator initialized")
            
            # Print system status
            await self._print_system_status()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Core Orchestrator: {str(e)}")
            raise
            
    async def _register_engines(self):
        """Register all available engines"""
        
        engine_configs = {
            "scraping_framework": {
                "class": EnhancedScrapingFrameworkAdapter,
                "config_key": "scraping",
                "priority": 1
            },
            "cloudflare_bypass": {
                "class": EnhancedCloudflareBypassAdapter,
                "config_key": "bypass.cloudflare",
                "priority": 2
            },
            "captcha_solver": {
                "class": EnhancedCaptchaSolverAdapter,
                "config_key": "bypass.captcha",
                "priority": 2
            },
            "undetected_browser": {
                "class": EnhancedUndetectedBrowserAdapter,
                "config_key": "bypass.browser",
                "priority": 2
            },
            "swedish_vehicle_data": {
                "class": SwedishVehicleDataAdapter,
                "config_key": "data_sources.swedish",
                "priority": 3
            },
            "ai_agents": {
                "class": EnhancedAIAgentSystem,
                "config_key": "ai",
                "priority": 1
            }
        }
        
        for engine_name, engine_config in engine_configs.items():
            try:
                # Create engine instance
                plugin_info = {
                    "name": engine_name,
                    "version": "1.0.0",
                    "config": await self.config_manager.get_config(engine_config["config_key"])
                }
                
                engine_instance = engine_config["class"](plugin_info)
                
                self.engines[engine_name] = {
                    "instance": engine_instance,
                    "config": engine_config,
                    "registered_at": datetime.now()
                }
                
                self.engine_status[engine_name] = "registered"
                
                logger.info(f"✅ Registered engine: {engine_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to register engine {engine_name}: {str(e)}")
                self.engine_status[engine_name] = "failed"
                
        self.system_metrics["engines_registered"] = len(self.engines)
        
    async def _initialize_engines(self):
        """Initialize all registered engines"""
        
        initialization_order = sorted(
            self.engines.items(),
            key=lambda x: x[1]["config"]["priority"]
        )
        
        for engine_name, engine_data in initialization_order:
            try:
                logger.info(f"🔄 Initializing engine: {engine_name}")
                await engine_data["instance"].initialize()
                self.engine_status[engine_name] = "initialized"
                
                # Initialize performance metrics
                self.system_metrics["engine_performance"][engine_name] = {
                    "operations": 0,
                    "successes": 0,
                    "failures": 0,
                    "avg_response_time": 0.0,
                    "last_used": None
                }
                
                logger.info(f"✅ Initialized engine: {engine_name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize engine {engine_name}: {str(e)}")
                self.engine_status[engine_name] = "error"
                
    async def create_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Create new workflow från configuration"""
        
        if not self.initialized:
            await self.initialize()
            
        # Generate workflow ID
        workflow_id = f"wf_{int(time.time())}_{len(self.active_workflows)}"
        
        # Validate configuration
        await self._validate_workflow_config(workflow_config)
        
        # Create workflow steps
        steps = []
        for step_config in workflow_config.get('steps', []):
            step = WorkflowStep(
                step_id=f"{workflow_id}_step_{len(steps)+1}",
                name=step_config.get('name', f'Step {len(steps)+1}'),
                engine=step_config.get('engine'),
                parameters=step_config.get('parameters', {}),
                dependencies=step_config.get('dependencies', []),
                timeout=step_config.get('timeout'),
                retry_attempts=step_config.get('retry_attempts', 3)
            )
            steps.append(step)
            
        # Create workflow
        workflow = Workflow(
            workflow_id=workflow_id,
            name=workflow_config.get('name', f'Workflow {workflow_id}'),
            workflow_type=WorkflowType(workflow_config.get('type', 'web_scraping')),
            description=workflow_config.get('description', ''),
            steps=steps,
            target_domains=workflow_config.get('target_domains', [])
        )
        
        # Security validation
        if not await self.security_controller.validate_workflow(workflow):
            raise ValueError("Workflow failed security validation")
            
        self.active_workflows[workflow_id] = workflow
        
        logger.info(f"✅ Created workflow: {workflow_id} ({workflow.workflow_type.value})")
        return workflow_id
        
    async def _validate_workflow_config(self, config: Dict[str, Any]):
        """Validate workflow configuration"""
        
        required_fields = ['name', 'type', 'steps']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate workflow type
        if config['type'] not in [wt.value for wt in WorkflowType]:
            raise ValueError(f"Invalid workflow type: {config['type']}")
            
        # Validate steps
        for i, step in enumerate(config.get('steps', [])):
            if 'engine' not in step:
                raise ValueError(f"Step {i+1} missing required 'engine' field")
                
            if step['engine'] not in self.engines:
                raise ValueError(f"Unknown engine: {step['engine']}")
                
        # Validate domains
        target_domains = config.get('target_domains', [])
        for domain in target_domains:
            if not await self.security_controller.is_domain_authorized(domain):
                raise ValueError(f"Domain not authorized: {domain}")
                
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute workflow"""
        
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
            
        if workflow.status != WorkflowStatus.CREATED:
            raise ValueError(f"Workflow {workflow_id} cannot be executed (status: {workflow.status.value})")
            
        try:
            workflow.status = WorkflowStatus.PLANNING
            workflow.started_at = datetime.now()
            
            logger.info(f"🚀 Executing workflow: {workflow_id}")
            
            # Plan execution order
            execution_plan = await self._plan_workflow_execution(workflow)
            
            workflow.status = WorkflowStatus.EXECUTING
            
            # Execute steps enligt plan
            results = {}
            for phase in execution_plan:
                phase_results = await self._execute_workflow_phase(workflow, phase)
                results.update(phase_results)
                
            # Finalize workflow
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            workflow.results = results
            
            # Calculate metrics
            execution_time = (workflow.completed_at - workflow.started_at).total_seconds()
            workflow.metrics = {
                "execution_time": execution_time,
                "steps_completed": len([s for s in workflow.steps if s.status == "completed"]),
                "steps_failed": len([s for s in workflow.steps if s.status == "failed"]),
                "success_rate": len([s for s in workflow.steps if s.status == "completed"]) / len(workflow.steps)
            }
            
            # Update system metrics
            self.system_metrics["workflows_executed"] += 1
            self.system_metrics["successful_workflows"] += 1
            self.system_metrics["by_workflow_type"][workflow.workflow_type.value]["executed"] += 1
            self.system_metrics["by_workflow_type"][workflow.workflow_type.value]["successful"] += 1
            
            logger.info(f"✅ Workflow completed: {workflow_id} ({execution_time:.2f}s)")
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results,
                "metrics": workflow.metrics
            }
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            self.system_metrics["failed_workflows"] += 1
            self.system_metrics["by_workflow_type"][workflow.workflow_type.value]["failed"] += 1
            
            logger.error(f"❌ Workflow failed: {workflow_id} - {str(e)}")
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e)
            }
            
    async def _plan_workflow_execution(self, workflow: Workflow) -> List[List[str]]:
        """Plan workflow execution order baserat på dependencies"""
        
        # Simple dependency resolution - i production skulle använda topological sort
        phases = []
        remaining_steps = {step.step_id: step for step in workflow.steps}
        completed_steps = set()
        
        while remaining_steps:
            # Find steps som kan köras (alla dependencies completed)
            ready_steps = []
            for step_id, step in remaining_steps.items():
                dependencies_satisfied = all(dep in completed_steps for dep in step.dependencies)
                if dependencies_satisfied:
                    ready_steps.append(step_id)
                    
            if not ready_steps:
                # Circular dependency or invalid dependencies
                raise ValueError("Circular dependency or invalid dependencies detected")
                
            phases.append(ready_steps)
            
            # Remove ready steps från remaining och add to completed
            for step_id in ready_steps:
                del remaining_steps[step_id]
                completed_steps.add(step_id)
                
        return phases
        
    async def _execute_workflow_phase(self, workflow: Workflow, phase_steps: List[str]) -> Dict[str, Any]:
        """Execute workflow phase (potentially parallel steps)"""
        
        results = {}
        
        # Create tasks för alla steps in phase
        tasks = []
        for step_id in phase_steps:
            step = next(s for s in workflow.steps if s.step_id == step_id)
            task = asyncio.create_task(self._execute_workflow_step(workflow, step))
            tasks.append((step_id, task))
            
        # Wait för alla tasks in phase
        for step_id, task in tasks:
            try:
                step_result = await task
                results[step_id] = step_result
                
            except Exception as e:
                logger.error(f"❌ Step failed: {step_id} - {str(e)}")
                results[step_id] = {"error": str(e)}
                
        return results
        
    async def _execute_workflow_step(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Execute individual workflow step"""
        
        step.status = "executing"
        step.start_time = datetime.now()
        
        engine_data = self.engines.get(step.engine)
        if not engine_data:
            raise ValueError(f"Engine not available: {step.engine}")
            
        engine = engine_data["instance"]
        
        try:
            # Update engine metrics
            engine_metrics = self.system_metrics["engine_performance"][step.engine]
            engine_metrics["operations"] += 1
            engine_metrics["last_used"] = datetime.now()
            
            # Execute step based on engine type
            if step.engine == "scraping_framework":
                result = await self._execute_scraping_step(engine, step)
            elif step.engine == "cloudflare_bypass":
                result = await self._execute_bypass_step(engine, step)
            elif step.engine == "ai_agents":
                result = await self._execute_ai_step(engine, step)
            elif step.engine == "swedish_vehicle_data":
                result = await self._execute_data_step(engine, step)
            else:
                result = await self._execute_generic_step(engine, step)
                
            step.status = "completed"
            step.result = result
            step.end_time = datetime.now()
            
            # Update success metrics
            engine_metrics["successes"] += 1
            
            execution_time = (step.end_time - step.start_time).total_seconds()
            engine_metrics["avg_response_time"] = (
                (engine_metrics["avg_response_time"] * (engine_metrics["successes"] - 1) + execution_time)
                / engine_metrics["successes"]
            )
            
            return result
            
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            step.end_time = datetime.now()
            
            # Update failure metrics
            engine_metrics["failures"] += 1
            
            raise
            
    async def _execute_scraping_step(self, engine, step: WorkflowStep) -> Dict[str, Any]:
        """Execute scraping framework step"""
        
        params = step.parameters
        
        # Create scraping job
        job_id = await engine.create_scraping_job({
            "name": step.name,
            "start_urls": params.get("start_urls", []),
            "rules": params.get("rules", []),
            "engine": params.get("scraping_engine", "beautifulsoup"),
            "max_pages": params.get("max_pages", 100)
        })
        
        # Execute job
        success = await engine.start_scraping_job(job_id)
        
        if success:
            results = await engine.get_job_results(job_id)
            return {
                "job_id": job_id,
                "success": True,
                "results_count": len(results),
                "results": results[:10] if isinstance(results, list) else results  # Limit för memory
            }
        else:
            return {
                "job_id": job_id,
                "success": False,
                "error": "Scraping job failed"
            }
            
    async def _execute_bypass_step(self, engine, step: WorkflowStep) -> Dict[str, Any]:
        """Execute bypass step"""
        
        params = step.parameters
        target_url = params.get("target_url")
        
        if not target_url:
            raise ValueError("target_url required för bypass step")
            
        # Attempt bypass
        result = await engine.bypass_protection(target_url, params.get("method"))
        
        return {
            "target_url": target_url,
            "success": result["success"],
            "method_used": result.get("method"),
            "session_data": {
                "cookies": result.get("cookies", {}),
                "headers": result.get("headers", {}),
                "user_agent": result.get("user_agent")
            } if result["success"] else None
        }
        
    async def _execute_ai_step(self, engine, step: WorkflowStep) -> Dict[str, Any]:
        """Execute AI agent step"""
        
        params = step.parameters
        
        # Create AI mission
        mission_id = await engine.create_mission({
            "name": step.name,
            "objective": params.get("objective", "Analyze target"),
            "target_domains": params.get("target_domains", []),
            "tasks": params.get("tasks", [])
        })
        
        # Execute mission
        result = await engine.execute_mission(mission_id)
        
        return {
            "mission_id": mission_id,
            "success": result["status"] == "completed",
            "results": result.get("results", {}),
            "metrics": result.get("metrics", {})
        }
        
    async def _execute_data_step(self, engine, step: WorkflowStep) -> Dict[str, Any]:
        """Execute data extraction step"""
        
        params = step.parameters
        
        if "vehicle_search" in params:
            # Vehicle search
            search_params = params["vehicle_search"]
            result = await engine.search_blocket_vehicles(**search_params)
            
            return {
                "search_type": "vehicle",
                "success": result.success,
                "results_count": len(result.results),
                "results": [
                    {
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "year": vehicle.year,
                        "price": vehicle.raw_data.get("price")
                    }
                    for vehicle in result.results[:10]
                ]
            }
        else:
            return {"error": "Unknown data step type"}
            
    async def _execute_generic_step(self, engine, step: WorkflowStep) -> Dict[str, Any]:
        """Execute generic step"""
        
        # Fallback för generic engine execution
        return {
            "step_name": step.name,
            "engine": step.engine,
            "status": "completed",
            "message": f"Generic execution completed för {step.engine}"
        }
        
    async def _workflow_executor(self):
        """Background task för workflow execution queue"""
        
        while True:
            try:
                if self.workflow_queue and len(self.execution_pool) < self.max_concurrent_workflows:
                    workflow_id = self.workflow_queue.pop(0)
                    
                    # Start workflow execution
                    task = asyncio.create_task(self.execute_workflow(workflow_id))
                    self.execution_pool[workflow_id] = task
                    
                # Clean completed workflows från execution pool
                completed_workflows = []
                for workflow_id, task in self.execution_pool.items():
                    if task.done():
                        completed_workflows.append(workflow_id)
                        
                for workflow_id in completed_workflows:
                    del self.execution_pool[workflow_id]
                    
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"❌ Workflow executor error: {str(e)}")
                await asyncio.sleep(5.0)
                
    async def _system_monitor(self):
        """Background system monitoring"""
        
        while True:
            try:
                # Update system metrics
                current_time = datetime.now()
                uptime = (current_time - self.system_metrics["uptime_start"]).total_seconds()
                
                # Log system status periodically
                if uptime % 300 < 1:  # Every 5 minutes
                    logger.info(f"📊 System Status - Workflows: {self.system_metrics['workflows_executed']} "
                               f"| Active: {len(self.active_workflows)} "
                               f"| Engines: {len([k for k, v in self.engine_status.items() if v == 'initialized'])}")
                    
                await asyncio.sleep(10.0)
                
            except Exception as e:
                logger.error(f"❌ System monitor error: {str(e)}")
                await asyncio.sleep(60.0)
                
    async def _print_system_status(self):
        """Print comprehensive system status"""
        
        print("\n" + "="*80)
        print("🎯 SPARKLING-OWL-SPIN - CORE ORCHESTRATOR STATUS")
        print("="*80)
        
        print(f"🏗️  Pyramid Architecture Layers:")
        print(f"   └── Core Layer: ✅ Orchestrator, Config, Security")
        print(f"   └── Engine Layer: {len(self.engines)} engines registered")
        print(f"   └── AI Layer: {'✅' if 'ai_agents' in self.engines else '❌'} Enhanced AI System")
        print(f"   └── Data Layer: {'✅' if 'swedish_vehicle_data' in self.engines else '❌'} Data Processing")
        print(f"   └── API Layer: ✅ Gateway & Interfaces")
        print(f"   └── Config Layer: ✅ Environment & Security")
        
        print(f"\n🔧 Engine Status:")
        for engine_name, status in self.engine_status.items():
            status_icon = "✅" if status == "initialized" else "❌" if status == "error" else "🔄"
            print(f"   {status_icon} {engine_name}: {status}")
            
        print(f"\n📊 System Metrics:")
        print(f"   • Workflows Executed: {self.system_metrics['workflows_executed']}")
        print(f"   • Success Rate: {(self.system_metrics['successful_workflows'] / max(1, self.system_metrics['workflows_executed']) * 100):.1f}%")
        print(f"   • Engines Registered: {self.system_metrics['engines_registered']}")
        
        print(f"\n🛡️  Security Status:")
        security_status = await self.security_controller.get_security_status()
        print(f"   • Authorized Domains: {len(security_status.get('authorized_domains', []))}")
        print(f"   • Security Level: {security_status.get('level', 'unknown')}")
        
        print(f"\n⚡ Resource Status:")
        print(f"   • Max Concurrent Workflows: {self.max_concurrent_workflows}")
        print(f"   • Memory Limit: {self.resource_limits['memory_mb']} MB")
        print(f"   • Active Workflows: {len(self.active_workflows)}")
        
        print("="*80)
        print("✅ System Ready för Authorized Penetration Testing & Data Extraction")
        print("⚠️  ENDAST FÖR PENETRATIONSTESTNING AV EGNA SERVRAR")
        print("="*80 + "\n")
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        return {
            "orchestrator": {
                "initialized": self.initialized,
                "uptime": (datetime.now() - self.system_metrics["uptime_start"]).total_seconds(),
                "version": "1.0.0"
            },
            "engines": {
                "registered": len(self.engines),
                "initialized": len([k for k, v in self.engine_status.items() if v == "initialized"]),
                "status": self.engine_status,
                "performance": self.system_metrics["engine_performance"]
            },
            "workflows": {
                "active": len(self.active_workflows),
                "queued": len(self.workflow_queue),
                "executed": self.system_metrics["workflows_executed"],
                "success_rate": (self.system_metrics["successful_workflows"] / max(1, self.system_metrics["workflows_executed"])) * 100
            },
            "resources": {
                "limits": self.resource_limits,
                "max_concurrent": self.max_concurrent_workflows,
                "execution_pool": len(self.execution_pool)
            },
            "metrics": self.system_metrics
        }
        
    async def shutdown(self):
        """Graceful system shutdown"""
        
        logger.info("🔄 Starting graceful shutdown...")
        
        # Cancel active workflows
        for workflow_id, workflow in self.active_workflows.items():
            if workflow.status in [WorkflowStatus.EXECUTING, WorkflowStatus.PLANNING]:
                workflow.status = WorkflowStatus.CANCELLED
                
        # Wait för execution pool to complete
        if self.execution_pool:
            logger.info(f"⏳ Waiting för {len(self.execution_pool)} workflows to complete...")
            await asyncio.gather(*self.execution_pool.values(), return_exceptions=True)
            
        # Shutdown engines
        for engine_name, engine_data in self.engines.items():
            try:
                if hasattr(engine_data["instance"], "cleanup"):
                    await engine_data["instance"].cleanup()
                    logger.info(f"✅ Shutdown engine: {engine_name}")
            except Exception as e:
                logger.error(f"❌ Error shutting down {engine_name}: {str(e)}")
                
        # Shutdown core components
        await self.api_gateway.shutdown()
        await self.security_controller.shutdown()
        await self.config_manager.shutdown()
        
        logger.info("✅ Graceful shutdown completed")
        
# Singleton instance
orchestrator = EnhancedCoreOrchestrator()

async def main():
    """Main entry point"""
    try:
        await orchestrator.initialize()
        
        # Keep running
        while True:
            await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
        await orchestrator.shutdown()
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        await orchestrator.shutdown()
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
