"""Configuration utility for managing stage configurations.

This module provides functionality for loading, validating, and accessing
configuration settings for different pipeline stages.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml
from pydantic import BaseModel, ValidationError

class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""
    pass

def load_config(
    config_path: Union[str, Path],
    schema_model: Optional[type[BaseModel]] = None
) -> Dict[str, Any]:
    """Load and optionally validate configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration YAML file
        schema_model: Optional Pydantic model for validation
        
    Returns:
        Dict containing the configuration
        
    Raises:
        ConfigurationError: If loading or validation fails
        
    Examples:
        >>> from pydantic import BaseModel
        >>> class MyConfig(BaseModel):
        ...     name: str
        ...     threshold: float
        >>> config = load_config("config/stage1.yaml", MyConfig)
    """
    try:
        config_path = Path(config_path)
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
            
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        if schema_model:
            try:
                validated = schema_model(**config)
                config = validated.model_dump()
            except ValidationError as e:
                raise ConfigurationError(f"Configuration validation failed: {e}")
                
        return config
        
    except Exception as e:
        raise ConfigurationError(f"Error loading configuration: {e}")

def get_stage_config(
    stage_name: str,
    base_path: Optional[Union[str, Path]] = None,
    schema_model: Optional[type[BaseModel]] = None
) -> Dict[str, Any]:
    """Load configuration for a specific pipeline stage.
    
    Args:
        stage_name: Name of the stage
        base_path: Optional base path for config files
        schema_model: Optional Pydantic model for validation
        
    Returns:
        Dict containing the stage configuration
        
    Examples:
        >>> config = get_stage_config("stage1", base_path="config")
    """
    if not base_path:
        base_path = os.getenv("CONFIG_PATH", "config")
    
    config_path = Path(base_path) / f"{stage_name}.yaml"
    return load_config(config_path, schema_model) 