"""
Sparkling-Owl-Spin Architecture - Main Entry Point
Revolutionary Ultimate System v4.0 - Enhanced with AI Agents & Pentest Capabilities

The Four-Layer Sparkling-Owl-Spin Pyramid:
1. Orchestration & AI Layer (sparkling-owl-spin/crewAI/fastagency): The Brain. Makes decisions.
2. Execution & Acquisition Layer (Crawlee/Playwright/Scrapy): The Body. Executes tasks.
3. Resistance & Bypass Layer (FlareSolverr/proxy_pool/undetected-chromedriver): Shield and lubricant.
4. Processing & Analysis Layer (trafilatura/OpenNRE/PayloadsAllTheThings): The senses.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sparkling_owl_spin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OperationMode(Enum):
    """Operation modes for the system"""
    SCRAPING = "scraping"
    PENTEST = "pentest"
    OSINT = "osint"
    HYBRID = "hybrid"

class AgentRole(Enum):
    """AI Agent roles in the system"""
    CHIEF_SCRAPING_OFFICER = "chief_scraping_officer"
    HEAD_OF_SECURITY = "head_of_security"
    DATA_SCIENTIST = "data_scientist"
    BYPASS_SPECIALIST = "bypass_specialist"
    OSINT_ANALYST = "osint_analyst"

@dataclass
class SparklengOwlConfig:
    """Main configuration for Sparkling-Owl-Spin"""
    operation_mode: OperationMode = OperationMode.HYBRID
    target_domains: List[str] = None
    active_agents: List[AgentRole] = None
    stealth_level: int = 5  # 1-10 scale
    enable_bypass: bool = True
    enable_captcha_solving: bool = True
    proxy_rotation: bool = True
    save_evidence: bool = True
    
    def __post_init__(self):
        if self.target_domains is None:
            self.target_domains = []
        if self.active_agents is None:
            self.active_agents = [
                AgentRole.CHIEF_SCRAPING_OFFICER,
                AgentRole.HEAD_OF_SECURITY,
                AgentRole.DATA_SCIENTIST
            ]

class SparklengOwlSpin:
    """
    Main orchestrator for the Sparkling-Owl-Spin system
    Coordinates all layers of the pyramid architecture
    """
    
    def __init__(self, config: SparklengOwlConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Layer managers (initialized during setup)
        self.orchestration_layer = None
        self.execution_layer = None
        self.bypass_layer = None
        self.analysis_layer = None
        
        # State tracking
        self.active_operations = {}
        self.discovered_assets = {}
        self.security_findings = {}
        
    async def initialize(self):
        """Initialize all system layers"""
        self.logger.info("🚀 Initializing Sparkling-Owl-Spin System")
        
        # Initialize layers in dependency order
        await self._init_bypass_layer()
        await self._init_execution_layer()
        await self._init_analysis_layer()
        await self._init_orchestration_layer()
        
        self.logger.info("✅ All system layers initialized successfully")
        
    async def _init_bypass_layer(self):
        """Initialize bypass and stealth layer"""
        from layers.bypass_layer import BypassLayer
        self.bypass_layer = BypassLayer(self.config)
        await self.bypass_layer.initialize()
        
    async def _init_execution_layer(self):
        """Initialize execution and acquisition layer"""
        from layers.execution_layer import ExecutionLayer
        self.execution_layer = ExecutionLayer(self.config, self.bypass_layer)
        await self.execution_layer.initialize()
        
    async def _init_analysis_layer(self):
        """Initialize processing and analysis layer"""
        from layers.analysis_layer import AnalysisLayer
        self.analysis_layer = AnalysisLayer(self.config)
        await self.analysis_layer.initialize()
        
    async def _init_orchestration_layer(self):
        """Initialize AI orchestration layer"""
        from layers.orchestration_layer import OrchestrationLayer
        self.orchestration_layer = OrchestrationLayer(
            self.config, 
            self.execution_layer, 
            self.bypass_layer, 
            self.analysis_layer
        )
        await self.orchestration_layer.initialize()
        
    async def execute_mission(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete mission using all system layers
        """
        self.logger.info(f"🎯 Starting mission: {mission.get('name', 'Unnamed')}")
        
        # Route to appropriate handler based on operation mode
        if self.config.operation_mode == OperationMode.SCRAPING:
            return await self._execute_scraping_mission(mission)
        elif self.config.operation_mode == OperationMode.PENTEST:
            return await self._execute_pentest_mission(mission)
        elif self.config.operation_mode == OperationMode.OSINT:
            return await self._execute_osint_mission(mission)
        else:  # HYBRID
            return await self._execute_hybrid_mission(mission)
            
    async def _execute_scraping_mission(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pure scraping mission"""
        results = {
            'mission_type': 'scraping',
            'targets_processed': [],
            'data_extracted': {},
            'errors': []
        }
        
        # Let AI orchestrator plan the mission
        plan = await self.orchestration_layer.plan_scraping_mission(mission)
        
        # Execute each step of the plan
        for step in plan['steps']:
            try:
                step_result = await self.execution_layer.execute_step(step)
                results['targets_processed'].append(step['target'])
                
                # Process extracted data
                processed_data = await self.analysis_layer.process_scraped_data(
                    step_result['data']
                )
                results['data_extracted'][step['target']] = processed_data
                
            except Exception as e:
                self.logger.error(f"Error in scraping step {step['target']}: {str(e)}")
                results['errors'].append({
                    'target': step['target'],
                    'error': str(e)
                })
                
        return results
        
    async def _execute_pentest_mission(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """Execute penetration testing mission"""
        results = {
            'mission_type': 'pentest',
            'targets_tested': [],
            'vulnerabilities_found': [],
            'security_assessment': {},
            'errors': []
        }
        
        # Let AI orchestrator plan the pentest
        plan = await self.orchestration_layer.plan_pentest_mission(mission)
        
        # Execute reconnaissance phase
        recon_data = await self._execute_reconnaissance(plan['targets'])
        
        # Execute vulnerability assessment
        for target in plan['targets']:
            try:
                vuln_results = await self._assess_target_vulnerabilities(
                    target, recon_data.get(target, {})
                )
                results['targets_tested'].append(target)
                results['vulnerabilities_found'].extend(vuln_results)
                
            except Exception as e:
                self.logger.error(f"Error in pentest step {target}: {str(e)}")
                results['errors'].append({
                    'target': target,
                    'error': str(e)
                })
                
        # Generate security assessment
        results['security_assessment'] = await self.analysis_layer.generate_security_report(
            results['vulnerabilities_found']
        )
        
        return results
        
    async def _execute_osint_mission(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """Execute OSINT (Open Source Intelligence) mission"""
        results = {
            'mission_type': 'osint',
            'intelligence_gathered': {},
            'entities_discovered': [],
            'relationships_mapped': [],
            'errors': []
        }
        
        # Let AI orchestrator plan OSINT operations
        plan = await self.orchestration_layer.plan_osint_mission(mission)
        
        # Execute intelligence gathering
        for operation in plan['operations']:
            try:
                intel_data = await self.execution_layer.gather_intelligence(operation)
                results['intelligence_gathered'][operation['type']] = intel_data
                
                # Extract entities and relationships
                entities = await self.analysis_layer.extract_entities(intel_data)
                relationships = await self.analysis_layer.map_relationships(entities)
                
                results['entities_discovered'].extend(entities)
                results['relationships_mapped'].extend(relationships)
                
            except Exception as e:
                self.logger.error(f"Error in OSINT operation {operation['type']}: {str(e)}")
                results['errors'].append({
                    'operation': operation['type'],
                    'error': str(e)
                })
                
        return results
        
    async def _execute_hybrid_mission(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """Execute hybrid mission combining all capabilities"""
        results = {
            'mission_type': 'hybrid',
            'scraping_results': {},
            'pentest_results': {},
            'osint_results': {},
            'integrated_analysis': {},
            'errors': []
        }
        
        # Execute all mission types in parallel where possible
        tasks = []
        
        if mission.get('enable_scraping', True):
            tasks.append(self._execute_scraping_mission(mission))
            
        if mission.get('enable_pentest', True):
            tasks.append(self._execute_pentest_mission(mission))
            
        if mission.get('enable_osint', True):
            tasks.append(self._execute_osint_mission(mission))
            
        # Execute tasks and collect results
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, task_result in enumerate(task_results):
            if isinstance(task_result, Exception):
                results['errors'].append({
                    'task': f"task_{i}",
                    'error': str(task_result)
                })
            else:
                if task_result['mission_type'] == 'scraping':
                    results['scraping_results'] = task_result
                elif task_result['mission_type'] == 'pentest':
                    results['pentest_results'] = task_result
                elif task_result['mission_type'] == 'osint':
                    results['osint_results'] = task_result
                    
        # Generate integrated analysis
        results['integrated_analysis'] = await self.analysis_layer.create_integrated_report(
            results['scraping_results'],
            results['pentest_results'],
            results['osint_results']
        )
        
        return results
        
    async def _execute_reconnaissance(self, targets: List[str]) -> Dict[str, Any]:
        """Execute reconnaissance phase for pentest"""
        recon_results = {}
        
        for target in targets:
            try:
                # Use OSINT tools for initial reconnaissance
                recon_data = await self.execution_layer.perform_reconnaissance(target)
                recon_results[target] = recon_data
                
            except Exception as e:
                self.logger.error(f"Reconnaissance failed for {target}: {str(e)}")
                recon_results[target] = {'error': str(e)}
                
        return recon_results
        
    async def _assess_target_vulnerabilities(self, target: str, recon_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess vulnerabilities for a specific target"""
        vulnerabilities = []
        
        # Let Head of Security agent plan the assessment
        assessment_plan = await self.orchestration_layer.plan_vulnerability_assessment(
            target, recon_data
        )
        
        # Execute vulnerability tests
        for test in assessment_plan['tests']:
            try:
                result = await self.execution_layer.execute_vulnerability_test(test)
                if result.get('vulnerable', False):
                    vulnerabilities.append({
                        'target': target,
                        'vulnerability_type': test['type'],
                        'severity': result.get('severity', 'unknown'),
                        'description': result.get('description', ''),
                        'proof_of_concept': result.get('poc', ''),
                        'remediation': result.get('remediation', '')
                    })
                    
            except Exception as e:
                self.logger.error(f"Vulnerability test failed for {target}: {str(e)}")
                
        return vulnerabilities
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'system_healthy': True,
            'active_operations': len(self.active_operations),
            'layer_status': {},
            'resource_usage': {},
            'errors': []
        }
        
        # Check each layer status
        try:
            if self.bypass_layer:
                status['layer_status']['bypass'] = await self.bypass_layer.get_status()
            if self.execution_layer:
                status['layer_status']['execution'] = await self.execution_layer.get_status()
            if self.analysis_layer:
                status['layer_status']['analysis'] = await self.analysis_layer.get_status()
            if self.orchestration_layer:
                status['layer_status']['orchestration'] = await self.orchestration_layer.get_status()
                
        except Exception as e:
            status['system_healthy'] = False
            status['errors'].append(str(e))
            
        return status
        
    async def cleanup(self):
        """Cleanup all system resources"""
        self.logger.info("🧹 Cleaning up Sparkling-Owl-Spin System")
        
        cleanup_tasks = []
        
        if self.orchestration_layer:
            cleanup_tasks.append(self.orchestration_layer.cleanup())
        if self.analysis_layer:
            cleanup_tasks.append(self.analysis_layer.cleanup())
        if self.execution_layer:
            cleanup_tasks.append(self.execution_layer.cleanup())
        if self.bypass_layer:
            cleanup_tasks.append(self.bypass_layer.cleanup())
            
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        self.logger.info("✅ System cleanup completed")

# Factory function for easy instantiation
def create_sparkling_owl_spin(config: Optional[SparklengOwlConfig] = None) -> SparklengOwlSpin:
    """Create and return a configured Sparkling-Owl-Spin instance"""
    if config is None:
        config = SparklengOwlConfig()
    return SparklengOwlSpin(config)

# Example usage
async def main():
    """Example main function"""
    config = SparklengOwlConfig(
        operation_mode=OperationMode.HYBRID,
        target_domains=['example.com'],
        stealth_level=8
    )
    
    system = create_sparkling_owl_spin(config)
    
    try:
        await system.initialize()
        
        # Example mission
        mission = {
            'name': 'Comprehensive Security Assessment',
            'targets': ['https://example.com'],
            'objectives': ['data_extraction', 'vulnerability_assessment', 'intelligence_gathering'],
            'constraints': {
                'respect_robots_txt': True,
                'max_requests_per_minute': 10,
                'enable_evidence_collection': True
            }
        }
        
        results = await system.execute_mission(mission)
        print(f"Mission completed with {len(results.get('errors', []))} errors")
        
    finally:
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
