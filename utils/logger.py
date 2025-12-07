"""Logging utility for trading framework."""
import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Logger utility for the trading framework."""
    
    _instance: Optional['Logger'] = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for Logger."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, name: str = 'trading_framework', log_file: Optional[str] = None, log_level: str = 'INFO'):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_file: Optional log file path
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if self._initialized:
            return
        
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        self._logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self._logger.addHandler(console_handler)
        
        # File handler (if specified)
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_format = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_format)
            self._logger.addHandler(file_handler)
        
        self._initialized = True
    
    def debug(self, message: str):
        """Log debug message."""
        self._logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self._logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self._logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self._logger.error(message)
    
    def critical(self, message: str):
        """Log critical message."""
        self._logger.critical(message)

