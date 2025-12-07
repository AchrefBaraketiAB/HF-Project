"""Configuration management for trading framework."""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the trading framework."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to JSON config file
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
        else:
            self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration."""
        self._config = {
            'marketdata_dir': 'marketdata',
            'log_level': 'INFO',
            'log_file': 'trading_framework.log',
            'binance': {
                'api_key': os.getenv('BINANCE_API_KEY', ''),
                'api_secret': os.getenv('BINANCE_API_SECRET', '')
            },
            'yfinance': {
                'timeout': 10
            },
            'cache_enabled': True,
            'cache_ttl': 3600  # 1 hour in seconds
        }
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file."""
        with open(config_file, 'r') as f:
            file_config = json.load(f)
            self._config.update(file_config)
    
    def save_to_file(self, config_file: Optional[str] = None):
        """Save configuration to JSON file."""
        filepath = config_file or self.config_file
        if not filepath:
            raise ValueError("No config file specified")
        
        with open(filepath, 'w') as f:
            json.dump(self._config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'binance.api_key')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using bracket notation."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any):
        """Set configuration value using bracket notation."""
        self.set(key, value)

