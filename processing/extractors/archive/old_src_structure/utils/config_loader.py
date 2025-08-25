"""
Configuration loading and management utilities.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import re
from copy import deepcopy
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Handles loading, validation, and management of configuration files."""
    
    def __init__(self):
        """Initialize the configuration loader."""
        self._config_cache = {}
        self._hot_reload_enabled = False
        self._watched_files = {}
    
    def load_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from a file.
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
            
        Returns:
            Dict containing configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file format is invalid
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
            
            logger.info(f"Loaded configuration from {config_path}")
            return config or {}
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    def load_config_with_env(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration with environment variable substitution.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Dict with environment variables substituted
        """
        config = self.load_config(config_path)
        return self._substitute_env_vars(config)
    
    def _substitute_env_vars(self, obj: Any) -> Any:
        """Recursively substitute environment variables in configuration.
        
        Supports syntax: ${VAR_NAME} and ${VAR_NAME:default_value}
        """
        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            return self._substitute_env_var_string(obj)
        else:
            return obj
    
    def _substitute_env_var_string(self, value: str) -> str:
        """Substitute environment variables in a string."""
        def replacer(match):
            var_expr = match.group(1)
            if ':' in var_expr:
                var_name, default = var_expr.split(':', 1)
                return os.getenv(var_name, default)
            else:
                var_value = os.getenv(var_expr)
                if var_value is None:
                    raise ValueError(f"Environment variable '{var_expr}' not found and no default provided")
                return var_value
        
        return re.sub(r'\$\{([^}]+)\}', replacer, value)
    
    def validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate configuration against a schema.
        
        Args:
            config: Configuration to validate
            schema: JSON schema for validation
            
        Returns:
            True if valid, False otherwise
        """
        try:
            import jsonschema
            jsonschema.validate(config, schema)
            return True
        except (ImportError, jsonschema.ValidationError):
            return False
    
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Configuration to merge in
            
        Returns:
            Merged configuration
        """
        merged = deepcopy(base_config)
        self._deep_merge(merged, override_config)
        return merged
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Recursively merge dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = deepcopy(value)
    
    def decrypt_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt encrypted values in configuration.
        
        Supports encrypted values with prefix 'encrypted:'
        """
        return self._decrypt_recursive(deepcopy(config))
    
    def _decrypt_recursive(self, obj: Any) -> Any:
        """Recursively decrypt configuration values."""
        if isinstance(obj, dict):
            return {key: self._decrypt_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._decrypt_recursive(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('encrypted:'):
            return self.decrypt_value(obj)
        else:
            return obj
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a single encrypted value.
        
        Args:
            encrypted_value: String in format 'encrypted:type:data'
            
        Returns:
            Decrypted value
        """
        parts = encrypted_value.split(':', 2)
        if len(parts) != 3 or parts[0] != 'encrypted':
            return encrypted_value
        
        encryption_type, encrypted_data = parts[1], parts[2]
        
        if encryption_type == 'base64':
            import base64
            return base64.b64decode(encrypted_data).decode('utf-8')
        elif encryption_type == 'aes':
            # Placeholder for AES decryption
            return f"decrypted_from_{encrypted_data[:8]}"
        else:
            logger.warning(f"Unknown encryption type: {encryption_type}")
            return encrypted_value
    
    def enable_hot_reload(self, config_path: Union[str, Path]) -> None:
        """Enable hot reloading for a configuration file."""
        config_path = Path(config_path)
        self._hot_reload_enabled = True
        self._watched_files[str(config_path)] = config_path.stat().st_mtime
        self._config_cache[str(config_path)] = self.load_config(config_path)
    
    def reload_if_changed(self) -> bool:
        """Check if any watched files have changed and reload if needed.
        
        Returns:
            True if any files were reloaded
        """
        if not self._hot_reload_enabled:
            return False
        
        reloaded = False
        for file_path, last_mtime in self._watched_files.items():
            current_mtime = Path(file_path).stat().st_mtime
            if current_mtime > last_mtime:
                self._config_cache[file_path] = self.load_config(file_path)
                self._watched_files[file_path] = current_mtime
                reloaded = True
                logger.info(f"Reloaded configuration from {file_path}")
        
        return reloaded
    
    def get_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Get cached configuration or load if not cached.
        
        Args:
            config_path: Path to config file (uses first cached if None)
            
        Returns:
            Configuration dictionary
        """
        if config_path is None:
            if not self._config_cache:
                raise ValueError("No configuration loaded")
            return next(iter(self._config_cache.values()))
        
        if config_path not in self._config_cache:
            self._config_cache[config_path] = self.load_config(config_path)
        
        return self._config_cache[config_path]
