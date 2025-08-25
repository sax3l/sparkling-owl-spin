#!/usr/bin/env python3
"""
Configuration Manager - Centralized configuration management

Provides configuration loading, validation, and management:
- Environment-specific configurations
- Configuration merging and inheritance
- Runtime configuration updates
- Configuration validation
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import logging
from datetime import datetime

from shared.utils.helpers import load_config, save_config, merge_configs, get_env_var

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
class ConfigManager:
    """Centralized configuration manager for pyramid architecture"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path(__file__).parent.parent.parent / 'config'
        self._configs: Dict[str, Any] = {}
        self._watchers: List[callable] = []
        self._logger = logging.getLogger(__name__)
        
        # Load base configuration
        self._load_base_config()
    
    def _load_base_config(self) -> None:
        """Load base configuration files"""
        try:
            # Load main services.yaml
            services_config = self.config_dir / 'services.yaml'
            if services_config.exists():
                self._configs['services'] = load_config(services_config)
                self._logger.info("Loaded services configuration")
            
            # Load environment-specific configs
            env = get_env_var('ENVIRONMENT', 'development')
            env_config = self.config_dir / 'environments' / f'{env}.yaml'
            
            if env_config.exists():
                self._configs['environment'] = load_config(env_config)
                self._logger.info(f"Loaded {env} environment configuration")
            else:
                self._logger.warning(f"Environment config not found: {env_config}")
                
        except Exception as e:
            self._logger.error(f"Failed to load base configuration: {e}")
    
    def get_config(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            if section not in self._configs:
                self._logger.warning(f"Configuration section not found: {section}")
                return default
            
            config_section = self._configs[section]
            
            if key is None:
                return config_section
            
            # Support nested key access with dot notation
            keys = key.split('.')
            value = config_section
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self._logger.error(f"Error getting config {section}.{key}: {e}")
            return default
    
    def set_config(self, section: str, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            if section not in self._configs:
                self._configs[section] = {}
            
            # Support nested key setting with dot notation
            keys = key.split('.')
            config_section = self._configs[section]
            
            # Navigate to the nested location
            for k in keys[:-1]:
                if k not in config_section:
                    config_section[k] = {}
                config_section = config_section[k]
            
            # Set the value
            config_section[keys[-1]] = value
            
            # Notify watchers
            self._notify_watchers(section, key, value)
            
            self._logger.info(f"Set config {section}.{key} = {value}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error setting config {section}.{key}: {e}")
            return False
    
    def merge_config(self, section: str, new_config: Dict[str, Any]) -> bool:
        """Merge new configuration with existing"""
        try:
            if section not in self._configs:
                self._configs[section] = {}
            
            self._configs[section] = merge_configs(self._configs[section], new_config)
            
            # Notify watchers
            self._notify_watchers(section, None, new_config)
            
            self._logger.info(f"Merged configuration for section: {section}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error merging config for {section}: {e}")
            return False
    
    def validate_config(self, section: Optional[str] = None) -> ConfigValidationResult:
        """Validate configuration"""
        errors = []
        warnings = []
        
        try:
            configs_to_validate = {section: self._configs[section]} if section else self._configs
            
            for config_section, config_data in configs_to_validate.items():
                if config_section == 'services':
                    # Validate services configuration
                    service_errors, service_warnings = self._validate_services_config(config_data)
                    errors.extend(service_errors)
                    warnings.extend(service_warnings)
                
                elif config_section == 'environment':
                    # Validate environment configuration
                    env_errors, env_warnings = self._validate_environment_config(config_data)
                    errors.extend(env_errors)
                    warnings.extend(env_warnings)
            
            return ConfigValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            self._logger.error(f"Configuration validation failed: {e}")
            return ConfigValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[]
            )
    
    def _validate_services_config(self, config: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validate services configuration"""
        errors = []
        warnings = []
        
        # Check required sections
        required_sections = ['orchestration', 'engines', 'agents']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing required section: {section}")
        
        # Validate orchestration config
        if 'orchestration' in config:
            orchestration = config['orchestration']
            if 'host' not in orchestration:
                warnings.append("Orchestration host not specified, using default")
            if 'port' not in orchestration:
                warnings.append("Orchestration port not specified, using default")
        
        return errors, warnings
    
    def _validate_environment_config(self, config: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validate environment configuration"""
        errors = []
        warnings = []
        
        # Basic environment validation
        if not config:
            warnings.append("Empty environment configuration")
        
        return errors, warnings
    
    def reload_config(self, section: Optional[str] = None) -> bool:
        """Reload configuration from files"""
        try:
            if section:
                # Reload specific section
                if section == 'services':
                    services_config = self.config_dir / 'services.yaml'
                    if services_config.exists():
                        self._configs['services'] = load_config(services_config)
                elif section == 'environment':
                    env = get_env_var('ENVIRONMENT', 'development')
                    env_config = self.config_dir / 'environments' / f'{env}.yaml'
                    if env_config.exists():
                        self._configs['environment'] = load_config(env_config)
            else:
                # Reload all
                self._load_base_config()
            
            self._logger.info(f"Reloaded configuration: {section or 'all'}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def save_config(self, section: str, file_path: Optional[Path] = None) -> bool:
        """Save configuration to file"""
        try:
            if section not in self._configs:
                self._logger.error(f"Configuration section not found: {section}")
                return False
            
            if file_path is None:
                if section == 'services':
                    file_path = self.config_dir / 'services.yaml'
                else:
                    env = get_env_var('ENVIRONMENT', 'development')
                    file_path = self.config_dir / 'environments' / f'{env}.yaml'
            
            save_config(self._configs[section], file_path)
            self._logger.info(f"Saved configuration {section} to {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save configuration: {e}")
            return False
    
    def watch_config(self, callback: callable) -> None:
        """Add configuration change watcher"""
        self._watchers.append(callback)
    
    def _notify_watchers(self, section: str, key: Optional[str], value: Any) -> None:
        """Notify configuration watchers of changes"""
        for watcher in self._watchers:
            try:
                watcher(section, key, value)
            except Exception as e:
                self._logger.error(f"Config watcher error: {e}")
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for a specific service"""
        services_config = self.get_config('services', default={})
        
        # Check in engines
        if 'engines' in services_config:
            for engine_type, engines in services_config['engines'].items():
                if isinstance(engines, dict) and service_name in engines:
                    return engines[service_name]
        
        # Check in agents
        if 'agents' in services_config:
            for agent_type, agents in services_config['agents'].items():
                if isinstance(agents, dict) and service_name in agents:
                    return agents[service_name]
        
        # Check in other sections
        for section_name, section_config in services_config.items():
            if isinstance(section_config, dict) and service_name in section_config:
                return section_config[service_name]
        
        return {}
    
    def list_services(self) -> List[str]:
        """List all configured services"""
        services = []
        services_config = self.get_config('services', default={})
        
        def extract_services(config: Dict[str, Any], prefix: str = ""):
            for key, value in config.items():
                if isinstance(value, dict):
                    # If this looks like a service config (has enabled, host, port, etc.)
                    if any(service_key in value for service_key in ['enabled', 'host', 'port', 'config']):
                        service_name = f"{prefix}.{key}" if prefix else key
                        services.append(service_name)
                    else:
                        # Recurse into nested structure
                        new_prefix = f"{prefix}.{key}" if prefix else key
                        extract_services(value, new_prefix)
        
        extract_services(services_config)
        return services
    
    def export_config(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Export all configuration to a single file"""
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'environment': get_env_var('ENVIRONMENT', 'development'),
                'configs': self._configs.copy()
            }
            
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                self._logger.info(f"Configuration exported to {output_file}")
            
            return export_data
            
        except Exception as e:
            self._logger.error(f"Failed to export configuration: {e}")
            return {}


# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
