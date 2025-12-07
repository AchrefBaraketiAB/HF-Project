"""DataManager class for managing multiple DataObjects."""
from typing import Dict, List, Optional
from pathlib import Path
from core.data_object import DataObject
from utils.logger import Logger


class DataManager:
    """Manager for multiple DataObjects."""
    
    def __init__(self):
        """Initialize DataManager."""
        self._data_objects: Dict[str, DataObject] = {}
        self._logger = Logger()
    
    def add(self, data_obj: DataObject, key: Optional[str] = None):
        """
        Add a DataObject to the manager.
        
        Args:
            data_obj: DataObject to add
            key: Optional key (default: f"{ticker}_{source}")
        """
        if key is None:
            key = f"{data_obj.ticker}_{data_obj.source}"
        
        if key in self._data_objects:
            self._logger.warning(f"Overwriting existing data object with key: {key}")
        
        self._data_objects[key] = data_obj
        self._logger.info(f"Added data object: {key}")
    
    def get(self, key: str) -> Optional[DataObject]:
        """
        Get a DataObject by key.
        
        Args:
            key: Key of the DataObject
        
        Returns:
            DataObject or None if not found
        """
        return self._data_objects.get(key)
    
    def remove(self, key: str) -> bool:
        """
        Remove a DataObject by key.
        
        Args:
            key: Key of the DataObject to remove
        
        Returns:
            True if removed, False if not found
        """
        if key in self._data_objects:
            del self._data_objects[key]
            self._logger.info(f"Removed data object: {key}")
            return True
        return False
    
    def list_keys(self) -> List[str]:
        """Get list of all keys."""
        return list(self._data_objects.keys())
    
    def get_all(self) -> Dict[str, DataObject]:
        """Get all DataObjects."""
        return self._data_objects.copy()
    
    def save_all(self, directory: Optional[str] = None):
        """
        Save all DataObjects to CSV files.
        
        Args:
            directory: Optional directory path (default: marketdata folder)
        """
        if directory is None:
            directory = Path(__file__).parent.parent / "marketdata"
        else:
            directory = Path(directory)
        
        directory.mkdir(parents=True, exist_ok=True)
        
        for key, data_obj in self._data_objects.items():
            filepath = directory / f"{key}.csv"
            data_obj.save_to_csv(str(filepath))
            self._logger.info(f"Saved {key} to {filepath}")
    
    def clear(self):
        """Clear all DataObjects."""
        self._data_objects.clear()
        self._logger.info("Cleared all data objects")
    
    def __len__(self) -> int:
        """Return number of DataObjects."""
        return len(self._data_objects)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DataManager({len(self._data_objects)} objects)"

