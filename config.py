#!/usr/bin/env python3
"""
Configuration Management for AI Assistant

Centralized configuration handling with environment variable support.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """
    Configuration manager for AI Assistant
    
    Handles loading and managing configuration from multiple sources:
    - Environment variables
    - Configuration files
    - Default values
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self._defaults = {
            # Voice settings
            "voice": {
                "wake_words": ["hey assistant", "spark", "computer"],
                "confidence_threshold": 0.7,
                "sample_rate": 16000,
                "chunk_size": 1024,
                "enable_tts": True,
                "tts_voice_rate": 200,
            },
            
            # LLM settings
            "llm": {
                "base_url": "http://localhost:11434",
                "model": "llama3.2",
                "timeout": 20.0,
                "enabled": False,
            },
            
            # API settings
            "api": {
                "openweather_api_key": None,
                "enable_weather": False,
            },
            
            # System settings
            "system": {
                "log_level": "INFO",
                "enable_analytics": True,
                "auto_save_logs": True,
                "max_log_files": 10,
            },
            
            # GUI settings
            "gui": {
                "theme": "dark",
                "window_size": "800x600",
                "enable_notifications": True,
            }
        }
        
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from files and environment variables"""
        config = self._defaults.copy()
        
        # Load from config file if it exists
        config_file = self.config_dir / "assistant_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    config = self._merge_configs(config, file_config)
                self.logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                self.logger.error(f"Failed to load config file: {e}")
        
        # Override with environment variables
        config = self._load_env_overrides(config)
        
        return config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _load_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration overrides from environment variables"""
        # LLM settings
        if os.getenv("LLM_BASE_URL"):
            config["llm"]["base_url"] = os.getenv("LLM_BASE_URL")
        if os.getenv("LLM_MODEL"):
            config["llm"]["model"] = os.getenv("LLM_MODEL")
        if os.getenv("LLM_ENABLED"):
            config["llm"]["enabled"] = os.getenv("LLM_ENABLED").lower() == "true"
        
        # API settings
        if os.getenv("OPENWEATHER_API_KEY"):
            config["api"]["openweather_api_key"] = os.getenv("OPENWEATHER_API_KEY")
            config["api"]["enable_weather"] = True
        
        # System settings
        if os.getenv("LOG_LEVEL"):
            config["system"]["log_level"] = os.getenv("LOG_LEVEL")
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'voice.wake_words')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'voice.wake_words')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
    
    def save(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            config_file = self.config_dir / "assistant_config.json"
            with open(config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            self.logger.info(f"Configuration saved to {config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self._config = self._defaults.copy()
        self.logger.info("Configuration reset to defaults")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return self._config.copy()


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


if __name__ == "__main__":
    # Test configuration
    config = Config()
    
    print("🔧 AI Assistant Configuration")
    print("=" * 40)
    
    # Display current config
    print("\n📋 Current Configuration:")
    for section, settings in config.get_all().items():
        print(f"\n[{section}]")
        for key, value in settings.items():
            print(f"  {key}: {value}")
    
    # Test getting values
    print(f"\n🎤 Wake words: {config.get('voice.wake_words')}")
    print(f"🤖 LLM model: {config.get('llm.model')}")
    print(f"🌡️  Weather enabled: {config.get('api.enable_weather')}")
    
    print("\n✅ Configuration system working!")