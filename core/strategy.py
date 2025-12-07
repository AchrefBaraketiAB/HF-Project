"""Base strategy class for trading strategies."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.data_object import DataObject
from utils.logger import Logger


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
        """
        self._name = name
        self._logger = Logger()
    
    @property
    def name(self) -> str:
        """Get the strategy name."""
        return self._name
    
    def generate_signals(self, data: DataObject) -> Dict[str, Any]:
        """
        Generate trading signals from data.
        
        Args:
            data: DataObject containing market data
        
        Returns:
            Dictionary with signals (e.g., {'buy': [...], 'sell': [...]})
        """
        raise NotImplementedError("Subclasses must implement generate_signals method")
    
    def calculate_indicators(self, data: DataObject) -> DataObject:
        """
        Calculate technical indicators.
        
        Args:
            data: DataObject containing market data
        
        Returns:
            DataObject with added indicator columns
        """
        raise NotImplementedError("Subclasses must implement calculate_indicators method")
    
    def validate_data(self, data: DataObject) -> bool:
        """
        Validate data before processing.
        
        Args:
            data: DataObject to validate
        
        Returns:
            True if valid
        """
        if data.data.empty:
            raise ValueError("Data is empty")
        return True

