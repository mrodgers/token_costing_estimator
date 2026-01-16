#!/usr/bin/env python3
"""
Configuration management module for Token Costing Estimator.

This module provides functionality to load default values from a configuration file,
allowing users to customize default parameters without modifying the source code.
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigurationError(Exception):
    """Custom exception for configuration-related errors."""
    pass


def load_config(config_file: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration settings from a JSON file.
    
    Args:
        config_file: Path to the configuration file (default: "config.json")
        
    Returns:
        Dict[str, Any]: Configuration dictionary with default values
        
    Raises:
        ConfigurationError: If configuration file is invalid or contains errors
    """
    # Default configuration values
    default_config = {
        "default_prompts_per_shift": 50,
        "default_multiplier": 5,
        "default_avg_tokens_per_call": 2000,
        "default_token_cost_per_thousand": 0.06,
        "default_doctors_per_shift": 10,
        "default_shifts_per_day": 3,
        "application_settings": {
            "enable_pricing_display": True,
            "enable_export_prompts": True,
            "export_timestamp_format": "%Y%m%d_%H%M%S"
        }
    }
    
    # If config file doesn't exist, return defaults
    if not os.path.exists(config_file):
        return default_config
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        # Validate that user_config is a dictionary
        if not isinstance(user_config, dict):
            raise ConfigurationError(f"Configuration file '{config_file}' must contain a JSON object")
        
        # Merge user configuration with defaults
        config = default_config.copy()
        
        # Update main configuration values
        for key, value in user_config.items():
            if key in default_config:
                # Validate numeric values
                if key.startswith("default_") and key != "default_token_cost_per_thousand":
                    if not isinstance(value, (int, float)) or value <= 0:
                        raise ConfigurationError(f"Configuration value '{key}' must be a positive number, got {value}")
                elif key == "default_token_cost_per_thousand":
                    if not isinstance(value, (int, float)) or value <= 0:
                        raise ConfigurationError(f"Configuration value '{key}' must be a positive number, got {value}")
                
                config[key] = value
            elif key == "application_settings" and isinstance(value, dict):
                # Merge application settings
                config["application_settings"].update(value)
            else:
                # Allow additional custom configuration keys
                config[key] = value
        
        return config
        
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in configuration file '{config_file}': {e}")
    except IOError as e:
        raise ConfigurationError(f"Failed to read configuration file '{config_file}': {e}")


def create_sample_config(config_file: str = "config.json") -> None:
    """
    Create a sample configuration file with default values and documentation.
    
    Args:
        config_file: Path where the sample configuration file will be created
        
    Raises:
        IOError: If the file cannot be created
    """
    sample_config = {
        "_comment": "Token Costing Estimator Configuration File",
        "_description": "Customize default values for the cost calculator. All numeric values must be positive.",
        
        "default_prompts_per_shift": 50,
        "default_multiplier": 5,
        "default_avg_tokens_per_call": 2000,
        "default_token_cost_per_thousand": 0.06,
        "default_doctors_per_shift": 10,
        "default_shifts_per_day": 3,
        
        "application_settings": {
            "_comment": "Application behavior settings",
            "enable_pricing_display": True,
            "enable_export_prompts": True,
            "export_timestamp_format": "%Y%m%d_%H%M%S"
        },
        
        "_usage_notes": [
            "Modify the default_ values to change the default parameters used in interactive mode",
            "All default_ values must be positive numbers",
            "The token_cost_per_thousand should reflect current OpenAI pricing",
            "Application settings control various features of the calculator"
        ]
    }
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise IOError(f"Failed to create sample configuration file '{config_file}': {e}")


def get_config_value(config: Dict[str, Any], key: str, fallback: Any = None) -> Any:
    """
    Safely retrieve a configuration value with fallback support.
    
    Args:
        config: Configuration dictionary
        key: Configuration key to retrieve
        fallback: Fallback value if key is not found
        
    Returns:
        Any: Configuration value or fallback
    """
    return config.get(key, fallback)


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that a configuration dictionary contains valid values.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ConfigurationError: If configuration contains invalid values
    """
    required_keys = [
        "default_prompts_per_shift",
        "default_multiplier", 
        "default_avg_tokens_per_call",
        "default_token_cost_per_thousand",
        "default_doctors_per_shift",
        "default_shifts_per_day"
    ]
    
    for key in required_keys:
        if key not in config:
            raise ConfigurationError(f"Missing required configuration key: {key}")
        
        value = config[key]
        if not isinstance(value, (int, float)) or value <= 0:
            raise ConfigurationError(f"Configuration value '{key}' must be a positive number, got {value}")
    
    return True


if __name__ == "__main__":
    # Command-line utility for configuration management
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-sample":
        try:
            create_sample_config()
            print("✅ Sample configuration file 'config.json' created successfully!")
            print("Edit this file to customize your default values.")
        except IOError as e:
            print(f"❌ Failed to create sample configuration: {e}")
            sys.exit(1)
    else:
        # Test configuration loading
        try:
            config = load_config()
            print("✅ Configuration loaded successfully!")
            print("Current configuration:")
            for key, value in config.items():
                if not key.startswith("_") and key != "application_settings":
                    print(f"  {key}: {value}")
        except ConfigurationError as e:
            print(f"❌ Configuration error: {e}")
            sys.exit(1)
