"""Tests for DataManager class."""
import pytest
import pandas as pd
from core.data_manager import DataManager
from core.data_object import DataObject


class TestDataManager:
    """Test cases for DataManager."""
    
    @pytest.fixture
    def manager(self):
        """Create DataManager instance."""
        return DataManager()
    
    @pytest.fixture
    def sample_data_object(self):
        """Create sample DataObject."""
        data = pd.DataFrame({
            'open': [100, 101, 102],
            'close': [102, 103, 104],
            'volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3))
        return DataObject(data, 'AAPL', 'yfinance')
    
    def test_init(self, manager):
        """Test DataManager initialization."""
        assert len(manager) == 0
    
    def test_add(self, manager, sample_data_object):
        """Test adding DataObject."""
        manager.add(sample_data_object)
        assert len(manager) == 1
    
    def test_add_with_key(self, manager, sample_data_object):
        """Test adding DataObject with custom key."""
        manager.add(sample_data_object, 'custom_key')
        assert manager.get('custom_key') is not None
    
    def test_get(self, manager, sample_data_object):
        """Test getting DataObject."""
        manager.add(sample_data_object)
        obj = manager.get('AAPL_yfinance')
        assert obj is not None
        assert obj.ticker == 'AAPL'
    
    def test_get_nonexistent(self, manager):
        """Test getting nonexistent DataObject."""
        assert manager.get('nonexistent') is None
    
    def test_remove(self, manager, sample_data_object):
        """Test removing DataObject."""
        manager.add(sample_data_object)
        assert manager.remove('AAPL_yfinance') is True
        assert len(manager) == 0
    
    def test_remove_nonexistent(self, manager):
        """Test removing nonexistent DataObject."""
        assert manager.remove('nonexistent') is False
    
    def test_list_keys(self, manager, sample_data_object):
        """Test listing keys."""
        manager.add(sample_data_object)
        keys = manager.list_keys()
        assert 'AAPL_yfinance' in keys
    
    def test_clear(self, manager, sample_data_object):
        """Test clearing all DataObjects."""
        manager.add(sample_data_object)
        manager.clear()
        assert len(manager) == 0
    
    def test_save_all(self, manager, sample_data_object, tmp_path):
        """Test saving all DataObjects."""
        manager.add(sample_data_object)
        manager.save_all(str(tmp_path))
        assert (tmp_path / 'AAPL_yfinance.csv').exists()
    
    def test_repr(self, manager, sample_data_object):
        """Test string representation."""
        manager.add(sample_data_object)
        repr_str = repr(manager)
        assert 'DataManager' in repr_str
        assert '1' in repr_str

