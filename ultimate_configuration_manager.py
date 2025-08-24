#!/usr/bin/env python3
"""
Ultimate Scraping Configuration Manager
=======================================

Centraliserad konfigurationshantering för hela scraping-arkitekturen.
Alla inställningar kan styras härifrån för maximal flexibilitet.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import yaml

# Default configuration paths
CONFIG_DIR = Path("config")
USER_CONFIG_FILE = CONFIG_DIR / "user_settings.json"
SYSTEM_CONFIG_FILE = CONFIG_DIR / "system_settings.json"
PROXY_CONFIG_FILE = CONFIG_DIR / "proxy_settings.json"
MONITORING_CONFIG_FILE = CONFIG_DIR / "monitoring_settings.json"


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(Enum):
    """Output formats för rapporter."""
    JSON = "json"
    CSV = "csv"
    HTML = "html"
    XML = "xml"
    MARKDOWN = "markdown"


@dataclass
class ProxySettings:
    """Proxy-relaterade inställningar."""
    
    # Proxy Broker Settings
    enable_proxy_broker: bool = True
    max_proxies_in_pool: int = 100
    proxy_discovery_interval: int = 300  # seconds
    proxy_validation_timeout: float = 10.0
    proxy_validation_interval: int = 60  # seconds
    
    # Proxy Sources
    enabled_proxy_sources: List[str] = field(default_factory=lambda: [
        "freeproxy",
        "proxylist", 
        "spys",
        "hidemy",
        "proxyscrape"
    ])
    
    # Proxy Schemes
    enabled_proxy_schemes: List[str] = field(default_factory=lambda: [
        "HTTP", "HTTPS", "SOCKS4", "SOCKS5"
    ])
    
    # IP Rotation Settings
    enable_ip_rotation: bool = True
    max_ip_endpoints: int = 20
    ip_rotation_regions: List[str] = field(default_factory=lambda: [
        "us-east-1", "us-west-1", "us-west-2",
        "eu-west-1", "eu-central-1", 
        "ap-southeast-1", "ap-northeast-1"
    ])
    ip_rotation_delay: float = 0.0
    ip_health_check_interval: int = 30
    
    # Enhanced Proxy Settings
    enable_enhanced_proxy: bool = False
    enhanced_proxy_priority_schemes: List[str] = field(default_factory=lambda: ["HTTPS", "SOCKS5"])
    enhanced_proxy_max_concurrent: int = 50
    
    # Proxy Quality Settings
    min_proxy_speed: float = 1.0  # seconds
    max_proxy_failures: int = 5
    proxy_blacklist_duration: int = 3600  # seconds
    
    # Geolocation Settings
    preferred_countries: List[str] = field(default_factory=lambda: ["US", "UK", "DE", "NL", "SE"])
    blocked_countries: List[str] = field(default_factory=lambda: ["CN", "RU"])


@dataclass
class ScrapingSettings:
    """Scraping-relaterade inställningar."""
    
    # Request Settings
    default_timeout: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 1.5
    retry_backoff_max: float = 60.0
    
    # Concurrency Settings
    max_concurrent_requests: int = 50
    max_concurrent_per_domain: int = 5
    global_delay: float = 0.1
    domain_specific_delays: Dict[str, float] = field(default_factory=dict)
    
    # User Agents
    rotate_user_agents: bool = True
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0"
    ])
    
    # Headers
    default_headers: Dict[str, str] = field(default_factory=lambda: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    })
    
    # Anti-Bot Settings
    enable_anti_bot_measures: bool = True
    randomize_headers: bool = True
    randomize_request_order: bool = True
    simulate_human_behavior: bool = True
    min_human_delay: float = 0.5
    max_human_delay: float = 3.0
    
    # Session Management
    enable_session_persistence: bool = True
    max_session_lifetime: int = 3600  # seconds
    enable_cookie_jar: bool = True
    
    # Content Processing
    follow_redirects: bool = True
    max_redirects: int = 10
    decode_content: bool = True
    verify_ssl: bool = True
    
    # JavaScript Execution
    enable_javascript: bool = False
    javascript_timeout: float = 10.0
    enable_screenshots: bool = False
    screenshot_format: str = "PNG"


@dataclass 
class MonitoringSettings:
    """Monitoring och observability-inställningar."""
    
    # General Monitoring
    enable_monitoring: bool = True
    monitoring_level: str = "comprehensive"  # minimal, standard, comprehensive, extreme
    metrics_collection_interval: int = 5  # seconds
    
    # Logging Settings
    log_level: LogLevel = LogLevel.INFO
    enable_file_logging: bool = True
    log_rotation_size: int = 10 * 1024 * 1024  # 10MB
    log_retention_days: int = 30
    log_directory: str = "logs"
    
    # Performance Monitoring
    enable_performance_profiling: bool = True
    enable_memory_monitoring: bool = True
    enable_cpu_monitoring: bool = True
    enable_network_monitoring: bool = True
    
    # Metrics Export
    enable_metrics_export: bool = True
    metrics_export_format: str = "prometheus"  # prometheus, influxdb, custom
    metrics_export_endpoint: Optional[str] = None
    metrics_export_interval: int = 60  # seconds
    
    # Alerting
    enable_alerting: bool = True
    alert_channels: List[str] = field(default_factory=lambda: ["console", "file"])
    email_alerts: bool = False
    email_smtp_server: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    
    # Health Checks
    enable_health_checks: bool = True
    health_check_interval: int = 30  # seconds
    health_check_timeout: float = 5.0
    
    # System Thresholds
    cpu_usage_warning_threshold: float = 80.0
    cpu_usage_critical_threshold: float = 95.0
    memory_usage_warning_threshold: float = 80.0
    memory_usage_critical_threshold: float = 95.0
    error_rate_warning_threshold: float = 10.0  # percent
    error_rate_critical_threshold: float = 25.0  # percent
    
    # Dashboard Settings
    enable_realtime_dashboard: bool = True
    dashboard_refresh_interval: int = 2  # seconds
    dashboard_history_length: int = 100  # data points


@dataclass
class BudgetSettings:
    """Budget och kostnadskontroll-inställningar."""
    
    # Budget Limits
    enable_budget_control: bool = True
    daily_budget_limit: float = 100.0  # USD
    hourly_budget_limit: float = 10.0  # USD
    cost_per_request: float = 0.001  # USD
    
    # Cost Tracking
    enable_cost_tracking: bool = True
    cost_breakdown_by_system: bool = True
    cost_breakdown_by_job: bool = True
    cost_breakdown_by_proxy: bool = True
    
    # Budget Alerts
    enable_budget_alerts: bool = True
    budget_warning_threshold: float = 80.0  # percent of limit
    budget_critical_threshold: float = 95.0  # percent of limit
    auto_pause_on_budget_exceeded: bool = True
    
    # Cost Optimization
    enable_cost_optimization: bool = True
    prefer_cheaper_systems: bool = False
    max_cost_per_successful_request: float = 0.01  # USD


@dataclass
class OutputSettings:
    """Output och rapportering-inställningar."""
    
    # General Output
    enable_output_saving: bool = True
    output_directory: str = "results"
    default_output_format: OutputFormat = OutputFormat.JSON
    
    # File Naming
    include_timestamp_in_filename: bool = True
    include_job_id_in_filename: bool = True
    custom_filename_template: Optional[str] = None
    
    # Content Settings
    save_response_headers: bool = True
    save_response_metadata: bool = True
    save_error_details: bool = True
    compress_large_responses: bool = True
    max_uncompressed_size: int = 1024 * 1024  # 1MB
    
    # Report Generation
    enable_automatic_reports: bool = True
    report_generation_interval: int = 3600  # seconds
    report_formats: List[OutputFormat] = field(default_factory=lambda: [
        OutputFormat.JSON, OutputFormat.HTML
    ])
    
    # Real-time Updates
    enable_realtime_updates: bool = True
    realtime_update_interval: int = 10  # seconds
    
    # Export Settings
    enable_data_export: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "excel", "parquet"])
    
    # Database Integration
    enable_database_storage: bool = False
    database_url: Optional[str] = None
    database_table_prefix: str = "scraping_"


@dataclass
class SystemSettings:
    """System-nivå inställningar."""
    
    # General System
    system_name: str = "Ultimate Scraping System"
    system_version: str = "1.0.0"
    debug_mode: bool = False
    
    # Threading och Async
    max_worker_threads: int = 50
    async_event_loop_policy: str = "default"  # default, uvloop, asyncio
    
    # Resource Limits
    max_memory_usage_mb: int = 2048
    max_cpu_cores_usage: int = 0  # 0 = no limit
    max_open_files: int = 1000
    
    # Temporary Files
    temp_directory: str = "temp"
    clean_temp_on_startup: bool = True
    clean_temp_on_shutdown: bool = True
    
    # Security
    enable_https_only: bool = False
    ssl_verification: bool = True
    allow_insecure_ssl: bool = False
    
    # Networking
    dns_servers: List[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])
    tcp_keepalive: bool = True
    connection_pool_size: int = 100
    
    # Cache Settings
    enable_caching: bool = True
    cache_directory: str = "cache"
    cache_max_size_mb: int = 500
    cache_ttl: int = 3600  # seconds


@dataclass
class UltimateScrapingConfiguration:
    """Huvudkonfigurationsklass som innehåller alla inställningar."""
    
    proxy_settings: ProxySettings = field(default_factory=ProxySettings)
    scraping_settings: ScrapingSettings = field(default_factory=ScrapingSettings)
    monitoring_settings: MonitoringSettings = field(default_factory=MonitoringSettings)
    budget_settings: BudgetSettings = field(default_factory=BudgetSettings)
    output_settings: OutputSettings = field(default_factory=OutputSettings)
    system_settings: SystemSettings = field(default_factory=SystemSettings)
    
    # Metadata
    config_version: str = "1.0.0"
    last_updated: Optional[str] = None
    created_by: str = "Ultimate Scraping Control Center"


class ConfigurationManager:
    """
    Configuration Manager för Ultimate Scraping System
    ==================================================
    
    Hanterar alla konfigurationer för systemet:
    • Ladda och spara konfigurationer
    • Validera inställningar
    • Dynamiska uppdateringar
    • Environment variable support
    • Configuration templates
    """
    
    def __init__(self, config_dir: Path = CONFIG_DIR):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.current_config: Optional[UltimateScrapingConfiguration] = None
        
    def create_default_config(self) -> UltimateScrapingConfiguration:
        """Skapa standardkonfiguration."""
        return UltimateScrapingConfiguration()
        
    def load_config(self, config_file: Optional[Path] = None) -> UltimateScrapingConfiguration:
        """Ladda konfiguration från fil."""
        
        if config_file is None:
            config_file = self.config_dir / "ultimate_config.json"
            
        if not config_file.exists():
            # Skapa standardkonfiguration
            config = self.create_default_config()
            self.save_config(config, config_file)
            return config
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Konvertera till configuration objekt
            config = self._dict_to_config(data)
            self.current_config = config
            
            return config
            
        except Exception as e:
            print(f"Error loading config: {e}")
            # Fallback till standardkonfiguration
            return self.create_default_config()
            
    def save_config(self, config: UltimateScrapingConfiguration, 
                   config_file: Optional[Path] = None) -> bool:
        """Spara konfiguration till fil."""
        
        if config_file is None:
            config_file = self.config_dir / "ultimate_config.json"
            
        try:
            # Update timestamp
            from datetime import datetime
            config.last_updated = datetime.now().isoformat()
            
            # Convert to dict
            data = asdict(config)
            
            # Save to file
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.current_config = config
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
            
    def _dict_to_config(self, data: Dict[str, Any]) -> UltimateScrapingConfiguration:
        """Konvertera dictionary till configuration objekt."""
        
        # Helper för att konvertera enum values
        def convert_enum_values(obj_dict: Dict[str, Any], enum_mapping: Dict[str, Any]):
            for key, enum_class in enum_mapping.items():
                if key in obj_dict and isinstance(obj_dict[key], str):
                    try:
                        obj_dict[key] = enum_class(obj_dict[key])
                    except ValueError:
                        pass  # Keep original value if enum conversion fails
                        
        # Convert monitoring settings
        monitoring_data = data.get('monitoring_settings', {})
        convert_enum_values(monitoring_data, {'log_level': LogLevel})
        
        # Convert output settings  
        output_data = data.get('output_settings', {})
        convert_enum_values(output_data, {'default_output_format': OutputFormat})
        
        # Handle enum lists
        if 'report_formats' in output_data:
            report_formats = []
            for format_str in output_data['report_formats']:
                try:
                    report_formats.append(OutputFormat(format_str))
                except ValueError:
                    pass
            output_data['report_formats'] = report_formats
            
        # Create configuration object
        config = UltimateScrapingConfiguration(
            proxy_settings=ProxySettings(**data.get('proxy_settings', {})),
            scraping_settings=ScrapingSettings(**data.get('scraping_settings', {})),
            monitoring_settings=MonitoringSettings(**monitoring_data),
            budget_settings=BudgetSettings(**data.get('budget_settings', {})),
            output_settings=OutputSettings(**output_data),
            system_settings=SystemSettings(**data.get('system_settings', {})),
            config_version=data.get('config_version', '1.0.0'),
            last_updated=data.get('last_updated'),
            created_by=data.get('created_by', 'Ultimate Scraping Control Center')
        )
        
        return config
        
    def update_config_section(self, section: str, updates: Dict[str, Any]) -> bool:
        """Uppdatera en specifik sektion av konfigurationen."""
        
        if self.current_config is None:
            self.current_config = self.load_config()
            
        try:
            if section == "proxy":
                for key, value in updates.items():
                    if hasattr(self.current_config.proxy_settings, key):
                        setattr(self.current_config.proxy_settings, key, value)
                        
            elif section == "scraping":
                for key, value in updates.items():
                    if hasattr(self.current_config.scraping_settings, key):
                        setattr(self.current_config.scraping_settings, key, value)
                        
            elif section == "monitoring":
                for key, value in updates.items():
                    if hasattr(self.current_config.monitoring_settings, key):
                        setattr(self.current_config.monitoring_settings, key, value)
                        
            elif section == "budget":
                for key, value in updates.items():
                    if hasattr(self.current_config.budget_settings, key):
                        setattr(self.current_config.budget_settings, key, value)
                        
            elif section == "output":
                for key, value in updates.items():
                    if hasattr(self.current_config.output_settings, key):
                        setattr(self.current_config.output_settings, key, value)
                        
            elif section == "system":
                for key, value in updates.items():
                    if hasattr(self.current_config.system_settings, key):
                        setattr(self.current_config.system_settings, key, value)
                        
            # Save updated configuration
            return self.save_config(self.current_config)
            
        except Exception as e:
            print(f"Error updating config section {section}: {e}")
            return False
            
    def get_config_section(self, section: str) -> Optional[Any]:
        """Hämta en specifik konfigurationssektion."""
        
        if self.current_config is None:
            self.current_config = self.load_config()
            
        section_map = {
            "proxy": self.current_config.proxy_settings,
            "scraping": self.current_config.scraping_settings,
            "monitoring": self.current_config.monitoring_settings,
            "budget": self.current_config.budget_settings,
            "output": self.current_config.output_settings,
            "system": self.current_config.system_settings
        }
        
        return section_map.get(section)
        
    def validate_config(self, config: UltimateScrapingConfiguration) -> List[str]:
        """Validera konfiguration och returnera eventuella fel."""
        
        errors = []
        
        # Validate proxy settings
        proxy = config.proxy_settings
        if proxy.max_proxies_in_pool <= 0:
            errors.append("max_proxies_in_pool must be greater than 0")
        if proxy.proxy_validation_timeout <= 0:
            errors.append("proxy_validation_timeout must be greater than 0")
            
        # Validate scraping settings
        scraping = config.scraping_settings
        if scraping.default_timeout <= 0:
            errors.append("default_timeout must be greater than 0")
        if scraping.max_concurrent_requests <= 0:
            errors.append("max_concurrent_requests must be greater than 0")
            
        # Validate monitoring settings
        monitoring = config.monitoring_settings
        if monitoring.metrics_collection_interval <= 0:
            errors.append("metrics_collection_interval must be greater than 0")
            
        # Validate budget settings
        budget = config.budget_settings
        if budget.enable_budget_control:
            if budget.daily_budget_limit <= 0:
                errors.append("daily_budget_limit must be greater than 0 when budget control is enabled")
                
        # Validate system settings
        system = config.system_settings
        if system.max_memory_usage_mb <= 0:
            errors.append("max_memory_usage_mb must be greater than 0")
            
        return errors
        
    def create_config_template(self, template_name: str = "default") -> bool:
        """Skapa konfigurationstemplate för olika användningsfall."""
        
        templates = {
            "default": self._create_default_template(),
            "high_performance": self._create_high_performance_template(),
            "low_resource": self._create_low_resource_template(),
            "debug": self._create_debug_template(),
            "production": self._create_production_template()
        }
        
        if template_name not in templates:
            return False
            
        template_file = self.config_dir / f"template_{template_name}.json"
        return self.save_config(templates[template_name], template_file)
        
    def _create_default_template(self) -> UltimateScrapingConfiguration:
        """Standard template."""
        return UltimateScrapingConfiguration()
        
    def _create_high_performance_template(self) -> UltimateScrapingConfiguration:
        """High performance template."""
        config = UltimateScrapingConfiguration()
        
        # Increase concurrency
        config.scraping_settings.max_concurrent_requests = 100
        config.scraping_settings.max_concurrent_per_domain = 20
        config.scraping_settings.global_delay = 0.0
        
        # More proxies
        config.proxy_settings.max_proxies_in_pool = 200
        config.proxy_settings.max_ip_endpoints = 50
        
        # Reduced monitoring for performance
        config.monitoring_settings.monitoring_level = "standard"
        config.monitoring_settings.enable_performance_profiling = False
        
        return config
        
    def _create_low_resource_template(self) -> UltimateScrapingConfiguration:
        """Low resource template."""
        config = UltimateScrapingConfiguration()
        
        # Reduce concurrency
        config.scraping_settings.max_concurrent_requests = 5
        config.scraping_settings.max_concurrent_per_domain = 2
        
        # Fewer proxies
        config.proxy_settings.max_proxies_in_pool = 20
        config.proxy_settings.max_ip_endpoints = 5
        
        # Minimal monitoring
        config.monitoring_settings.monitoring_level = "minimal"
        config.monitoring_settings.enable_performance_profiling = False
        config.monitoring_settings.enable_realtime_dashboard = False
        
        # Lower resource limits
        config.system_settings.max_memory_usage_mb = 512
        config.system_settings.max_worker_threads = 10
        
        return config
        
    def _create_debug_template(self) -> UltimateScrapingConfiguration:
        """Debug template."""
        config = UltimateScrapingConfiguration()
        
        # Enable debug mode
        config.system_settings.debug_mode = True
        config.monitoring_settings.log_level = LogLevel.DEBUG
        config.monitoring_settings.monitoring_level = "extreme"
        config.monitoring_settings.enable_performance_profiling = True
        
        # Conservative settings for debugging
        config.scraping_settings.max_concurrent_requests = 5
        config.scraping_settings.global_delay = 1.0
        
        return config
        
    def _create_production_template(self) -> UltimateScrapingConfiguration:
        """Production template."""
        config = UltimateScrapingConfiguration()
        
        # Production-ready settings
        config.monitoring_settings.log_level = LogLevel.INFO
        config.monitoring_settings.enable_alerting = True
        config.monitoring_settings.enable_metrics_export = True
        
        # Enable all systems
        config.proxy_settings.enable_proxy_broker = True
        config.proxy_settings.enable_ip_rotation = True
        
        # Budget control
        config.budget_settings.enable_budget_control = True
        config.budget_settings.enable_budget_alerts = True
        
        # Reliable settings
        config.scraping_settings.max_retries = 5
        config.scraping_settings.verify_ssl = True
        
        return config
        
    def export_config_schema(self) -> Dict[str, Any]:
        """Exportera configuration schema för validering."""
        
        def get_field_info(cls):
            fields = {}
            for field_name, field_obj in cls.__dataclass_fields__.items():
                field_type = str(field_obj.type)
                field_default = field_obj.default if field_obj.default != field_obj.default_factory else None
                
                fields[field_name] = {
                    "type": field_type,
                    "default": field_default,
                    "required": field_obj.default == field_obj.default_factory
                }
            return fields
            
        schema = {
            "proxy_settings": get_field_info(ProxySettings),
            "scraping_settings": get_field_info(ScrapingSettings),
            "monitoring_settings": get_field_info(MonitoringSettings),
            "budget_settings": get_field_info(BudgetSettings),
            "output_settings": get_field_info(OutputSettings),
            "system_settings": get_field_info(SystemSettings)
        }
        
        return schema
        
    def load_from_environment(self) -> Dict[str, Any]:
        """Ladda konfigurationer från environment variables."""
        
        env_config = {}
        
        # Environment variable mappings
        env_mappings = {
            "SCRAPING_MAX_CONCURRENT": ("scraping_settings", "max_concurrent_requests", int),
            "SCRAPING_TIMEOUT": ("scraping_settings", "default_timeout", float),
            "PROXY_MAX_POOL_SIZE": ("proxy_settings", "max_proxies_in_pool", int),
            "MONITORING_LEVEL": ("monitoring_settings", "monitoring_level", str),
            "BUDGET_DAILY_LIMIT": ("budget_settings", "daily_budget_limit", float),
            "LOG_LEVEL": ("monitoring_settings", "log_level", str),
            "DEBUG_MODE": ("system_settings", "debug_mode", bool)
        }
        
        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = type_func(value)
                    if section not in env_config:
                        env_config[section] = {}
                    env_config[section][key] = converted_value
                except ValueError:
                    print(f"Invalid value for {env_var}: {value}")
                    
        return env_config
        
    def apply_environment_overrides(self) -> bool:
        """Applicera environment variable overrides på current config."""
        
        env_config = self.load_from_environment()
        
        if not env_config:
            return True
            
        try:
            for section, updates in env_config.items():
                self.update_config_section(section, updates)
            return True
        except Exception as e:
            print(f"Error applying environment overrides: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_current_config() -> UltimateScrapingConfiguration:
    """Hämta aktuell konfiguration."""
    return config_manager.load_config()


def update_config(section: str, updates: Dict[str, Any]) -> bool:
    """Uppdatera konfiguration."""
    return config_manager.update_config_section(section, updates)


def save_current_config() -> bool:
    """Spara aktuell konfiguration."""
    if config_manager.current_config:
        return config_manager.save_config(config_manager.current_config)
    return False


# CLI interface för konfigurationshantering
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ultimate Scraping Configuration Manager")
    parser.add_argument("--create-template", choices=["default", "high_performance", "low_resource", "debug", "production"],
                       help="Create configuration template")
    parser.add_argument("--validate", action="store_true", help="Validate current configuration")
    parser.add_argument("--export-schema", action="store_true", help="Export configuration schema")
    parser.add_argument("--show-config", action="store_true", help="Show current configuration")
    
    args = parser.parse_args()
    
    manager = ConfigurationManager()
    
    if args.create_template:
        success = manager.create_config_template(args.create_template)
        print(f"Template '{args.create_template}' {'created' if success else 'failed to create'}")
        
    elif args.validate:
        config = manager.load_config()
        errors = manager.validate_config(config)
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("Configuration is valid")
            
    elif args.export_schema:
        schema = manager.export_config_schema()
        schema_file = CONFIG_DIR / "config_schema.json"
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=2)
        print(f"Schema exported to {schema_file}")
        
    elif args.show_config:
        config = manager.load_config()
        print(json.dumps(asdict(config), indent=2, default=str))
        
    else:
        print("Creating default configuration...")
        config = manager.create_default_config()
        success = manager.save_config(config)
        print(f"Default configuration {'created' if success else 'failed to create'}")
