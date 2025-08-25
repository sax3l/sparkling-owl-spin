#!/usr/bin/env python3
"""
AI Agents - Base agent system for intelligent task execution
Following pyramid architecture with Swedish integration capabilities
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from shared.models.base import BaseService, ServiceStatus
from shared.utils.helpers import get_logger


class BaseAgent(BaseService, ABC):
    """Base class for all AI agents in the system"""
    
    def __init__(self, agent_id: str, agent_name: str, capabilities: List[str] = None):
        super().__init__(agent_id, agent_name)
        
        self.capabilities = capabilities or []
        self.logger = get_logger(f"agent.{agent_id}")
        self.tasks_completed = 0
        self.last_task_timestamp: Optional[datetime] = None
        
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task and return results"""
        pass
    
    @abstractmethod
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if the agent can handle this task"""
        pass
    
    async def start(self) -> None:
        """Start the AI agent"""
        self.status = ServiceStatus.STARTING
        self.logger.info(f"Starting AI agent: {self.name}")
        
        try:
            await self._initialize_agent()
            self.status = ServiceStatus.RUNNING
            self.logger.info(f"✅ AI agent {self.name} started successfully")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to start AI agent {self.name}: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the AI agent"""
        self.status = ServiceStatus.STOPPING
        self.logger.info(f"Stopping AI agent: {self.name}")
        
        try:
            await self._cleanup_agent()
            self.status = ServiceStatus.STOPPED
            self.logger.info(f"✅ AI agent {self.name} stopped successfully")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to stop AI agent {self.name}: {e}")
    
    async def _initialize_agent(self) -> None:
        """Initialize agent-specific resources"""
        # Override in subclasses
        pass
    
    async def _cleanup_agent(self) -> None:
        """Cleanup agent-specific resources"""
        # Override in subclasses
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent_id': self.service_id,
            'agent_name': self.name,
            'status': self.status.value,
            'capabilities': self.capabilities,
            'tasks_completed': self.tasks_completed,
            'last_task_timestamp': self.last_task_timestamp.isoformat() if self.last_task_timestamp else None
        }


class AgentOrchestrator(BaseService):
    """Orchestrates multiple AI agents for complex task execution"""
    
    def __init__(self):
        super().__init__("agent_orchestrator", "AI Agent Orchestrator")
        
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = get_logger(__name__)
        
    async def start(self) -> None:
        """Start the agent orchestrator"""
        self.status = ServiceStatus.STARTING
        self.logger.info("Starting Agent Orchestrator...")
        
        try:
            # Initialize registered agents
            for agent in self.agents.values():
                await agent.start()
            
            self.status = ServiceStatus.RUNNING
            self.logger.info("✅ Agent Orchestrator started")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to start Agent Orchestrator: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the agent orchestrator"""
        self.status = ServiceStatus.STOPPING
        self.logger.info("Stopping Agent Orchestrator...")
        
        try:
            # Stop all agents
            for agent in self.agents.values():
                await agent.stop()
            
            self.status = ServiceStatus.STOPPED
            self.logger.info("✅ Agent Orchestrator stopped")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to stop Agent Orchestrator: {e}")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an AI agent"""
        self.agents[agent.service_id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.service_id})")
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an AI agent"""
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            self.logger.info(f"Unregistered agent: {agent.name} ({agent_id})")
            return True
        return False
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the most suitable agent"""
        
        task_type = task.get('type', 'unknown')
        required_capabilities = task.get('capabilities', [])
        
        # Find suitable agents
        suitable_agents = []
        for agent in self.agents.values():
            if await agent.validate_task(task):
                # Check if agent has required capabilities
                if all(cap in agent.capabilities for cap in required_capabilities):
                    suitable_agents.append(agent)
        
        if not suitable_agents:
            return {
                'success': False,
                'error': f'No suitable agent found for task type: {task_type}',
                'task_id': task.get('id', 'unknown')
            }
        
        # Select the best agent (for now, just use the first one)
        selected_agent = suitable_agents[0]
        
        try:
            self.logger.info(f"Executing task {task.get('id', 'unknown')} with agent {selected_agent.name}")
            
            result = await selected_agent.execute_task(task)
            
            # Update agent statistics
            selected_agent.tasks_completed += 1
            selected_agent.last_task_timestamp = datetime.now()
            
            return {
                'success': True,
                'result': result,
                'agent_id': selected_agent.service_id,
                'agent_name': selected_agent.name,
                'task_id': task.get('id', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'agent_id': selected_agent.service_id,
                'task_id': task.get('id', 'unknown')
            }
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents with their capabilities"""
        return [
            {
                'agent_id': agent.service_id,
                'agent_name': agent.name,
                'status': agent.status.value,
                'capabilities': agent.capabilities,
                'tasks_completed': agent.tasks_completed
            }
            for agent in self.agents.values()
        ]


# Example agent implementations
class WebScrapingAgent(BaseAgent):
    """AI agent specialized in web scraping tasks"""
    
    def __init__(self):
        super().__init__(
            "web_scraping_agent",
            "Web Scraping AI Agent",
            capabilities=["web_scraping", "data_extraction", "content_analysis"]
        )
    
    async def validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate if this agent can handle web scraping tasks"""
        return task.get('type') in ['web_scraping', 'data_extraction', 'url_analysis']
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web scraping task"""
        task_type = task.get('type')
        
        if task_type == 'web_scraping':
            return await self._handle_web_scraping(task)
        elif task_type == 'data_extraction':
            return await self._handle_data_extraction(task)
        elif task_type == 'url_analysis':
            return await self._handle_url_analysis(task)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _handle_web_scraping(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web scraping task"""
        url = task.get('url')
        extraction_rules = task.get('extraction_rules', {})
        
        # This would integrate with the web scraper engine
        return {
            'task_type': 'web_scraping',
            'url': url,
            'extracted_data': {},  # Would contain actual scraped data
            'timestamp': datetime.now().isoformat(),
            'agent_processing': 'Web scraping task completed'
        }
    
    async def _handle_data_extraction(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data extraction task"""
        content = task.get('content', '')
        extraction_schema = task.get('schema', {})
        
        return {
            'task_type': 'data_extraction',
            'extracted_fields': {},  # Would contain extracted data
            'schema_compliance': True,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _handle_url_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle URL analysis task"""
        url = task.get('url')
        
        return {
            'task_type': 'url_analysis',
            'url': url,
            'analysis_result': {
                'domain': 'extracted_domain',
                'technology_stack': [],
                'anti_bot_measures': [],
                'scraping_difficulty': 'medium'
            },
            'timestamp': datetime.now().isoformat()
        }
