#!/usr/bin/env python3
"""
Enhanced Configuration Manager för Sparkling-Owl-Spin
Hanterar all konfiguration över hela systemet enligt pyramid-arkitekturen
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from cryptography.fernet import Fernet
import base64
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ConfigValidationRule:
    """Configuration validation rule"""
    path: str
    required: bool = True
    data_type: type = str
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None

@dataclass
class ConfigEnvironment:
    """Configuration environment setup"""
    name: str
    config_dir: Path
    secrets_file: Path
    validation_rules: List[ConfigValidationRule] = field(default_factory=list)
    encryption_key: Optional[str] = None
    last_loaded: Optional[datetime] = None
    checksum: Optional[str] = None

class EnhancedConfigManager:
    """Enhanced configuration manager för pyramid architecture"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.config_dir = self.base_path / "config"
        self.secrets_dir = self.base_path / "secrets"
        
        # Create directories om de inte existerar
        self.config_dir.mkdir(exist_ok=True)
        self.secrets_dir.mkdir(exist_ok=True, mode=0o700)
        
        # Configuration storage
        self.configs: Dict[str, Dict[str, Any]] = {}
        self.secrets: Dict[str, Any] = {}
        self.environments: Dict[str, ConfigEnvironment] = {}
        
        # Current environment
        self.current_environment = os.getenv("SPARKLING_ENV", "development")
        
        # Encryption för secrets
        self.encryption_key = None
        self._initialize_encryption()
        
        # Configuration validation rules
        self.validation_rules = {}
        self._setup_validation_rules()
        
        # File watchers för auto-reload
        self.watched_files = set()
        self.file_checksums = {}
        
        self.initialized = False
        
    def _initialize_encryption(self):
        """Initialize encryption för secrets"""
        try:
            key_file = self.secrets_dir / ".encryption_key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                # Generate new encryption key
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                    
                # Secure permissions
                os.chmod(key_file, 0o600)
                logger.info("🔐 Generated new encryption key för secrets")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption: {str(e)}")
            raise
            
    def _setup_validation_rules(self):
        """Setup configuration validation rules"""
        
        # Core system rules
        self.validation_rules["core"] = [
            ConfigValidationRule("log_level", data_type=str, allowed_values=["DEBUG", "INFO", "WARNING", "ERROR"]),
            ConfigValidationRule("max_workers", data_type=int, min_value=1, max_value=20),
            ConfigValidationRule("timeout", data_type=int, min_value=10, max_value=3600),
        ]
        
        # Security rules
        self.validation_rules["security"] = [
            ConfigValidationRule("authorized_domains", data_type=list, required=True),
            ConfigValidationRule("rate_limit", data_type=int, min_value=1, max_value=1000),
            ConfigValidationRule("security_level", data_type=str, allowed_values=["low", "medium", "high"]),
        ]
        
        # Database rules
        self.validation_rules["database"] = [
            ConfigValidationRule("host", data_type=str, required=True),
            ConfigValidationRule("port", data_type=int, min_value=1, max_value=65535),
            ConfigValidationRule("max_connections", data_type=int, min_value=1, max_value=100),
        ]
        
        # API rules
        self.validation_rules["api"] = [
            ConfigValidationRule("host", data_type=str, required=True),
            ConfigValidationRule("port", data_type=int, min_value=1024, max_value=65535),
            ConfigValidationRule("cors_origins", data_type=list),
        ]
        
        # AI agent rules
        self.validation_rules["ai"] = [
            ConfigValidationRule("openai.api_key", data_type=str, required=False),
            ConfigValidationRule("max_agents", data_type=int, min_value=1, max_value=10),
            ConfigValidationRule("default_model", data_type=str),
        ]
        
        # Scraping framework rules
        self.validation_rules["scraping"] = [
            ConfigValidationRule("max_concurrent_requests", data_type=int, min_value=1, max_value=50),
            ConfigValidationRule("request_delay", data_type=float, min_value=0.1, max_value=10.0),
            ConfigValidationRule("user_agents", data_type=list, required=True),
        ]
        
        # Bypass tools rules
        self.validation_rules["bypass"] = [
            ConfigValidationRule("cloudflare.flaresolverr_url", data_type=str),
            ConfigValidationRule("captcha.twocaptcha_api_key", data_type=str, required=False),
            ConfigValidationRule("browser.headless", data_type=bool),
        ]
        
        # Data sources rules
        self.validation_rules["data_sources"] = [
            ConfigValidationRule("swedish.blocket_api_key", data_type=str, required=False),
            ConfigValidationRule("swedish.max_results", data_type=int, min_value=1, max_value=10000),
        ]
        
    async def initialize(self):
        """Initialize configuration manager"""
        try:
            logger.info("🔧 Initializing Enhanced Configuration Manager")
            
            # Setup environments
            await self._setup_environments()
            
            # Load configurations
            await self._load_all_configurations()
            
            # Validate configurations
            await self._validate_all_configurations()
            
            # Start file watching
            asyncio.create_task(self._watch_config_files())
            
            self.initialized = True
            logger.info("✅ Enhanced Configuration Manager initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Configuration Manager: {str(e)}")
            raise
            
    async def _setup_environments(self):
        """Setup configuration environments"""
        
        environments = ["development", "testing", "production"]
        
        for env_name in environments:
            env_config_dir = self.config_dir / env_name
            env_config_dir.mkdir(exist_ok=True)
            
            secrets_file = self.secrets_dir / f"{env_name}_secrets.json"
            
            self.environments[env_name] = ConfigEnvironment(
                name=env_name,
                config_dir=env_config_dir,
                secrets_file=secrets_file,
                validation_rules=[]
            )
            
        logger.info(f"✅ Setup {len(environments)} configuration environments")
        
    async def _load_all_configurations(self):
        """Load all configurations för current environment"""
        
        current_env = self.environments[self.current_environment]
        config_files = [
            "core.yml",
            "security.yml", 
            "database.yml",
            "api.yml",
            "ai.yml",
            "scraping.yml",
            "bypass.yml",
            "data_sources.yml"
        ]
        
        for config_file in config_files:
            config_path = current_env.config_dir / config_file
            
            if config_path.exists():
                config_key = config_file.split('.')[0]
                self.configs[config_key] = await self._load_config_file(config_path)
                self.watched_files.add(str(config_path))
                
                logger.info(f"✅ Loaded config: {config_key}")
            else:
                # Create default configuration
                config_key = config_file.split('.')[0]
                default_config = self._get_default_config(config_key)
                await self._save_config_file(config_path, default_config)
                self.configs[config_key] = default_config
                
                logger.info(f"✅ Created default config: {config_key}")
                
        # Load secrets
        await self._load_secrets()
        
    def _get_default_config(self, config_key: str) -> Dict[str, Any]:
        """Get default configuration för given key"""
        
        defaults = {
            "core": {
                "log_level": "INFO",
                "max_workers": 4,
                "timeout": 300,
                "debug": False,
                "metrics_enabled": True
            },
            "security": {
                "authorized_domains": [
                    "localhost",
                    "127.0.0.1",
                    "*.test.example.com",
                    "*.localhost"
                ],
                "rate_limit": 100,
                "security_level": "medium",
                "require_domain_authorization": True,
                "log_all_requests": True,
                "block_suspicious_requests": True
            },
            "database": {
                "type": "sqlite",
                "host": "localhost",
                "port": 5432,
                "name": "sparkling_owl_spin",
                "max_connections": 20,
                "pool_size": 10,
                "timeout": 30
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                "max_request_size": "10MB",
                "rate_limit": 1000,
                "enable_docs": True
            },
            "ai": {
                "openai": {
                    "api_key": "${OPENAI_API_KEY}",
                    "model": "gpt-4",
                    "max_tokens": 2000,
                    "temperature": 0.7
                },
                "max_agents": 5,
                "default_model": "gpt-4",
                "crew_max_execution_time": 1800,
                "enable_memory": True,
                "verbose": False
            },
            "scraping": {
                "max_concurrent_requests": 10,
                "request_delay": 1.0,
                "max_retries": 3,
                "timeout": 30,
                "respect_robots_txt": True,
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                ],
                "engines": {
                    "beautifulsoup": {"enabled": True},
                    "scrapy": {"enabled": True, "concurrent_requests": 16},
                    "playwright": {"enabled": True, "headless": True},
                    "crawlee": {"enabled": False}
                }
            },
            "bypass": {
                "cloudflare": {
                    "flaresolverr_url": "http://localhost:8191",
                    "cloudscraper_enabled": True,
                    "auto_retry": True,
                    "max_retries": 3
                },
                "captcha": {
                    "twocaptcha_api_key": "${TWOCAPTCHA_API_KEY}",
                    "capmonster_api_key": "${CAPMONSTER_API_KEY}",
                    "nopecha_api_key": "${NOPECHA_API_KEY}",
                    "local_ocr_enabled": True,
                    "default_service": "2captcha"
                },
                "browser": {
                    "undetected_chrome": True,
                    "headless": True,
                    "user_data_dir": "./browser_profiles",
                    "max_instances": 3,
                    "stealth_mode": True
                }
            },
            "data_sources": {
                "swedish": {
                    "blocket_api_key": "${BLOCKET_API_KEY}",
                    "bytbil_enabled": True,
                    "max_results": 1000,
                    "cache_ttl": 3600,
                    "regions": ["all"],
                    "categories": ["cars", "motorcycles", "boats"]
                }
            }
        }
        
        return defaults.get(config_key, {})
        
    async def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yml', '.yaml']:
                    config = yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {file_path.suffix}")
                    
            # Calculate checksum för file watching
            self.file_checksums[str(file_path)] = await self._calculate_file_checksum(file_path)
            
            # Resolve environment variables
            config = self._resolve_environment_variables(config)
            
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to load config file {file_path}: {str(e)}")
            return {}
            
    async def _save_config_file(self, file_path: Path, config: Dict[str, Any]):
        """Save configuration file"""
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                elif file_path.suffix.lower() == '.json':
                    json.dump(config, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            logger.error(f"❌ Failed to save config file {file_path}: {str(e)}")
            raise
            
    def _resolve_environment_variables(self, config: Any) -> Any:
        """Resolve environment variables in configuration"""
        
        if isinstance(config, dict):
            return {k: self._resolve_environment_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_environment_variables(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            # Resolve environment variable
            env_var = config[2:-1]
            return os.getenv(env_var, config)  # Return original if env var inte finns
        else:
            return config
            
    async def _load_secrets(self):
        """Load encrypted secrets"""
        
        current_env = self.environments[self.current_environment]
        
        if current_env.secrets_file.exists():
            try:
                cipher = Fernet(self.encryption_key)
                
                with open(current_env.secrets_file, 'rb') as f:
                    encrypted_data = f.read()
                    
                decrypted_data = cipher.decrypt(encrypted_data)
                self.secrets = json.loads(decrypted_data.decode('utf-8'))
                
                logger.info(f"✅ Loaded {len(self.secrets)} secrets")
                
            except Exception as e:
                logger.error(f"❌ Failed to load secrets: {str(e)}")
                self.secrets = {}
        else:
            # Create empty secrets file
            await self._save_secrets()
            
    async def _save_secrets(self):
        """Save encrypted secrets"""
        
        current_env = self.environments[self.current_environment]
        
        try:
            cipher = Fernet(self.encryption_key)
            
            secrets_json = json.dumps(self.secrets, indent=2)
            encrypted_data = cipher.encrypt(secrets_json.encode('utf-8'))
            
            with open(current_env.secrets_file, 'wb') as f:
                f.write(encrypted_data)
                
            # Secure permissions
            os.chmod(current_env.secrets_file, 0o600)
            
        except Exception as e:
            logger.error(f"❌ Failed to save secrets: {str(e)}")
            raise
            
    async def _validate_all_configurations(self):
        """Validate all configurations"""
        
        validation_errors = []
        
        for config_key, config_data in self.configs.items():
            if config_key in self.validation_rules:
                errors = await self._validate_config(config_key, config_data)
                validation_errors.extend(errors)
                
        if validation_errors:
            logger.warning(f"⚠️  Configuration validation warnings: {len(validation_errors)}")
            for error in validation_errors:
                logger.warning(f"   • {error}")
        else:
            logger.info("✅ All configurations validated successfully")
            
    async def _validate_config(self, config_key: str, config_data: Dict[str, Any]) -> List[str]:
        """Validate single configuration"""
        
        errors = []
        rules = self.validation_rules.get(config_key, [])
        
        for rule in rules:
            try:
                # Get value från nested path
                value = self._get_nested_value(config_data, rule.path)
                
                if value is None:
                    if rule.required:
                        errors.append(f"{config_key}.{rule.path} is required but missing")
                    continue
                    
                # Type validation
                if not isinstance(value, rule.data_type):
                    errors.append(f"{config_key}.{rule.path} should be {rule.data_type.__name__}, got {type(value).__name__}")
                    continue
                    
                # Value range validation
                if rule.min_value is not None and value < rule.min_value:
                    errors.append(f"{config_key}.{rule.path} should be >= {rule.min_value}, got {value}")
                    
                if rule.max_value is not None and value > rule.max_value:
                    errors.append(f"{config_key}.{rule.path} should be <= {rule.max_value}, got {value}")
                    
                # Allowed values validation
                if rule.allowed_values is not None and value not in rule.allowed_values:
                    errors.append(f"{config_key}.{rule.path} should be one of {rule.allowed_values}, got {value}")
                    
            except Exception as e:
                errors.append(f"Validation error för {config_key}.{rule.path}: {str(e)}")
                
        return errors
        
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value från nested dictionary path"""
        
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
                
        return current
        
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set value in nested dictionary path"""
        
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
            
        current[keys[-1]] = value
        
    async def get_config(self, path: str, default: Any = None) -> Any:
        """Get configuration value by path"""
        
        if not self.initialized:
            await self.initialize()
            
        try:
            # Check if path starts med known config key
            parts = path.split('.')
            config_key = parts[0]
            
            if config_key in self.configs:
                if len(parts) == 1:
                    return self.configs[config_key]
                else:
                    remaining_path = '.'.join(parts[1:])
                    return self._get_nested_value(self.configs[config_key], remaining_path) or default
            else:
                # Search alla configs
                for config_data in self.configs.values():
                    value = self._get_nested_value(config_data, path)
                    if value is not None:
                        return value
                        
                return default
                
        except Exception as e:
            logger.error(f"❌ Failed to get config {path}: {str(e)}")
            return default
            
    async def set_config(self, path: str, value: Any):
        """Set configuration value by path"""
        
        parts = path.split('.')
        config_key = parts[0]
        
        if config_key not in self.configs:
            self.configs[config_key] = {}
            
        if len(parts) == 1:
            self.configs[config_key] = value
        else:
            remaining_path = '.'.join(parts[1:])
            self._set_nested_value(self.configs[config_key], remaining_path, value)
            
        # Save to file
        current_env = self.environments[self.current_environment]
        config_file = current_env.config_dir / f"{config_key}.yml"
        await self._save_config_file(config_file, self.configs[config_key])
        
    async def get_secret(self, key: str, default: Any = None) -> Any:
        """Get encrypted secret value"""
        
        if not self.initialized:
            await self.initialize()
            
        return self.secrets.get(key, default)
        
    async def set_secret(self, key: str, value: Any):
        """Set encrypted secret value"""
        
        self.secrets[key] = value
        await self._save_secrets()
        
    async def delete_secret(self, key: str):
        """Delete encrypted secret"""
        
        if key in self.secrets:
            del self.secrets[key]
            await self._save_secrets()
            
    async def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all configurations"""
        
        if not self.initialized:
            await self.initialize()
            
        return self.configs.copy()
        
    async def reload_config(self, config_key: str):
        """Reload specific configuration"""
        
        current_env = self.environments[self.current_environment]
        config_file = current_env.config_dir / f"{config_key}.yml"
        
        if config_file.exists():
            self.configs[config_key] = await self._load_config_file(config_file)
            logger.info(f"✅ Reloaded config: {config_key}")
        else:
            logger.warning(f"⚠️  Config file inte found: {config_file}")
            
    async def _watch_config_files(self):
        """Watch configuration files för changes"""
        
        while True:
            try:
                for file_path in self.watched_files.copy():
                    if os.path.exists(file_path):
                        new_checksum = await self._calculate_file_checksum(Path(file_path))
                        old_checksum = self.file_checksums.get(file_path)
                        
                        if new_checksum != old_checksum:
                            logger.info(f"🔄 Config file changed: {file_path}")
                            
                            # Extract config key från file path
                            config_key = Path(file_path).stem
                            await self.reload_config(config_key)
                            
                            self.file_checksums[file_path] = new_checksum
                            
                await asyncio.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Config file watcher error: {str(e)}")
                await asyncio.sleep(30.0)
                
    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate file checksum för change detection"""
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                return hashlib.md5(file_content).hexdigest()
        except Exception:
            return ""
            
    def export_config(self, output_path: str, include_secrets: bool = False):
        """Export all configurations to file"""
        
        export_data = {
            "environment": self.current_environment,
            "exported_at": datetime.now().isoformat(),
            "configs": self.configs
        }
        
        if include_secrets:
            export_data["secrets"] = self.secrets
            
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Exported configuration to: {output_path}")
        
    def import_config(self, import_path: str, merge: bool = True):
        """Import configurations från file"""
        
        with open(import_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
            
        if merge:
            # Merge med existing configs
            for key, config in import_data.get("configs", {}).items():
                if key in self.configs:
                    self.configs[key].update(config)
                else:
                    self.configs[key] = config
        else:
            # Replace all configs
            self.configs = import_data.get("configs", {})
            
        if "secrets" in import_data:
            if merge:
                self.secrets.update(import_data["secrets"])
            else:
                self.secrets = import_data["secrets"]
                
        logger.info(f"✅ Imported configuration från: {import_path}")
        
    def get_status(self) -> Dict[str, Any]:
        """Get configuration manager status"""
        
        return {
            "initialized": self.initialized,
            "current_environment": self.current_environment,
            "configs_loaded": len(self.configs),
            "secrets_loaded": len(self.secrets),
            "environments": list(self.environments.keys()),
            "watched_files": len(self.watched_files),
            "validation_rules": {k: len(v) for k, v in self.validation_rules.items()}
        }
        
    async def shutdown(self):
        """Shutdown configuration manager"""
        
        logger.info("🔄 Shutting down Configuration Manager...")
        
        # Save alla pending configs
        for config_key, config_data in self.configs.items():
            current_env = self.environments[self.current_environment]
            config_file = current_env.config_dir / f"{config_key}.yml"
            try:
                await self._save_config_file(config_file, config_data)
            except Exception as e:
                logger.error(f"❌ Failed to save config {config_key}: {str(e)}")
                
        # Save secrets
        await self._save_secrets()
        
        self.initialized = False
        logger.info("✅ Configuration Manager shutdown complete")
