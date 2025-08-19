import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging():
    """
    Sets up logging based on the configuration file in config/logging.yml.
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "logging.yml"
    if config_path.exists():
        with open(config_path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
                logging.info("Logging configured successfully.")
            except Exception as e:
                logging.basicConfig(level=logging.INFO)
                logging.error(f"Error configuring logging: {e}. Falling back to basic config.")
    else:
        logging.basicConfig(level=logging.INFO)
        logging.warning("logging.yml not found. Using basic logging configuration.")