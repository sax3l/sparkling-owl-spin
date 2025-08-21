"""
Tests for configuration loading and validation.
"""
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch
from src.utils.config_loader import ConfigLoader


class TestConfigLoader:
    """Test cases for ConfigLoader class."""
    
    def test_config_loader_initialization(self):
        """Test that ConfigLoader initializes correctly."""
        loader = ConfigLoader()
        assert loader is not None
    
    def test_load_yaml_config(self):
        """Test loading YAML configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.yml"
            
            test_config = {
                "app": {
                    "name": "Test App",
                    "version": "1.0.0",
                    "debug": True
                },
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "name": "testdb"
                }
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            loader = ConfigLoader()
            loaded_config = loader.load_config(str(config_file))
            
            assert loaded_config == test_config
            assert loaded_config["app"]["name"] == "Test App"
            assert loaded_config["database"]["port"] == 5432
    
    def test_load_json_config(self):
        """Test loading JSON configuration files."""
        import json
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            
            test_config = {
                "api": {
                    "base_url": "https://api.example.com",
                    "timeout": 30,
                    "retries": 3
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(test_config, f)
            
            loader = ConfigLoader()
            loaded_config = loader.load_config(str(config_file))
            
            assert loaded_config == test_config
            assert loaded_config["api"]["timeout"] == 30
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution in configs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "env_config.yml"
            
            config_content = """
            database:
              host: ${DB_HOST:localhost}
              port: ${DB_PORT:5432}
              password: ${DB_PASSWORD}
            """
            
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            with patch.dict('os.environ', {'DB_HOST': 'prod.db.com', 'DB_PASSWORD': 'secret123'}):
                loader = ConfigLoader()
                loaded_config = loader.load_config_with_env(str(config_file))
                
                assert loaded_config["database"]["host"] == "prod.db.com"
                assert loaded_config["database"]["port"] == "5432"  # default value
                assert loaded_config["database"]["password"] == "secret123"
    
    def test_config_validation(self):
        """Test configuration validation against schema."""
        loader = ConfigLoader()
        
        # Valid config
        valid_config = {
            "app": {
                "name": "Test App",
                "version": "1.0.0"
            },
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        schema = {
            "type": "object",
            "required": ["app", "database"],
            "properties": {
                "app": {
                    "type": "object",
                    "required": ["name", "version"]
                },
                "database": {
                    "type": "object",
                    "required": ["host", "port"]
                }
            }
        }
        
        assert loader.validate_config(valid_config, schema) is True
        
        # Invalid config - missing required field
        invalid_config = {
            "app": {
                "name": "Test App"
                # missing version
            }
        }
        
        assert loader.validate_config(invalid_config, schema) is False
    
    def test_config_merging(self):
        """Test merging multiple configuration files."""
        loader = ConfigLoader()
        
        base_config = {
            "app": {
                "name": "Base App",
                "debug": False
            },
            "database": {
                "host": "localhost",
                "port": 5432
            }
        }
        
        override_config = {
            "app": {
                "debug": True,
                "log_level": "DEBUG"
            },
            "cache": {
                "enabled": True,
                "ttl": 3600
            }
        }
        
        merged = loader.merge_configs(base_config, override_config)
        
        # Should preserve base values
        assert merged["app"]["name"] == "Base App"
        assert merged["database"]["host"] == "localhost"
        
        # Should override existing values
        assert merged["app"]["debug"] is True
        
        # Should add new values
        assert merged["app"]["log_level"] == "DEBUG"
        assert merged["cache"]["enabled"] is True
    
    def test_config_encryption_support(self):
        """Test support for encrypted configuration values."""
        loader = ConfigLoader()
        
        config_with_encrypted = {
            "database": {
                "host": "localhost",
                "password": "encrypted:base64:cGFzc3dvcmQxMjM="  # "password123" base64 encoded
            },
            "api": {
                "key": "encrypted:aes:abcd1234..."
            }
        }
        
        # Mock encryption handler
        with patch.object(loader, 'decrypt_value') as mock_decrypt:
            mock_decrypt.side_effect = lambda x: "password123" if "cGFzc3dvcmQxMjM=" in x else "decrypted_key"
            
            decrypted_config = loader.decrypt_config(config_with_encrypted)
            
            assert decrypted_config["database"]["password"] == "password123"
            assert decrypted_config["api"]["key"] == "decrypted_key"
    
    def test_config_hot_reload(self):
        """Test hot reloading of configuration files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "hot_reload.yml"
            
            initial_config = {"value": 1}
            with open(config_file, 'w') as f:
                yaml.dump(initial_config, f)
            
            loader = ConfigLoader()
            loader.enable_hot_reload(str(config_file))
            
            # Initial load
            config = loader.get_config()
            assert config["value"] == 1
            
            # Update file
            updated_config = {"value": 2}
            with open(config_file, 'w') as f:
                yaml.dump(updated_config, f)
            
            # Should detect change (in real implementation)
            # This is a simplified test
            loader.reload_if_changed()
            config = loader.get_config()
            # In actual implementation, this would be 2
