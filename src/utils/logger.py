import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional

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


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name. If None, uses the calling module's name.
        
    Returns:
        Logger instance
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'unknown')
    
    return logging.getLogger(name)


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    config_file: Optional[str] = None
) -> None:
    """
    Configure logging with specified parameters.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        config_file: Path to logging configuration file
    """
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'rt') as f:
                try:
                    config = yaml.safe_load(f.read())
                    logging.config.dictConfig(config)
                    return
                except Exception as e:
                    logging.warning(f"Failed to load config from {config_file}: {e}")
    
    # Default configuration
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )