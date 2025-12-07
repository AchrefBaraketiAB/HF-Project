"""Tests for DataObject class."""
import pytest
import pandas as pd
from datetime import datetime
from core.data_object import DataObject


class TestDataObject:
    """Test cases for DataObject."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample DataFrame for testing."""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        data = pd.DataFrame({
            'open': [100 + i for i in range(10)],
            'high': [105 + i for i in range(10)],
            'low': [95 + i for i in range(10)],
            'close': [102 + i for i in range(10)],
            'volume': [1000000 + i * 10000 for i in range(10)]
        }, index=dates)
        return data
    
    @pytest.fixture
    def data_object(self, sample_data):
        """Create DataObject instance for testing."""
        return DataObject(sample_data, 'AAPL', 'yfinance')
    
    def test_init(self, sample_data):
        """Test DataObject initialization."""
        obj = DataObject(sample_data, 'AAPL', 'yfinance')
        assert obj.ticker == 'AAPL'
        assert obj.source == 'yfinance'
        assert len(obj.data) == 10
    
    def test_init_empty_data(self):
        """Test initialization with empty data raises error."""
        empty_df = pd.DataFrame()
        with pytest.raises(ValueError, match="Data cannot be empty"):
            DataObject(empty_df, 'AAPL', 'yfinance')
    
    def test_get_data(self, data_object, sample_data):
        """Test get_data method."""
        result = data_object.get_data()
        pd.testing.assert_frame_equal(result, sample_data)
    
    def test_get_columns(self, data_object):
        """Test get_columns method."""
        result = data_object.get_columns(['high', 'low', 'volume'])
        assert list(result.columns) == ['high', 'low', 'volume']
        assert len(result) == 10
    
    def test_get_columns_missing(self, data_object):
        """Test get_columns with missing columns raises error."""
        with pytest.raises(ValueError, match="Columns not found"):
            data_object.get_columns(['nonexistent'])
    
    def test_filter_data(self, data_object):
        """Test filter_data method."""
        filtered = data_object.filter_data({'close': '>105'})
        assert len(filtered) > 0
        assert all(filtered['close'] > 105)
    
    def test_filter_data_multiple(self, data_object):
        """Test filter_data with multiple conditions."""
        filtered = data_object.filter_data({
            'close': '>105',
            'volume': '>1005000'
        })
        assert len(filtered) > 0
    
    def test_save_to_csv(self, data_object, tmp_path):
        """Test save_to_csv method."""
        filepath = tmp_path / "test_data.csv"
        result_path = data_object.save_to_csv(str(filepath))
        assert result_path == str(filepath)
        assert filepath.exists()
        
        # Verify data can be loaded
        loaded = pd.read_csv(filepath, index_col=0, parse_dates=True)
        assert len(loaded) == 10
    
    def test_get_summary(self, data_object):
        """Test get_summary method."""
        summary = data_object.get_summary()
        assert summary['ticker'] == 'AAPL'
        assert summary['source'] == 'yfinance'
        assert summary['rows'] == 10
        assert 'columns' in summary
        assert 'date_range' in summary
    
    def test_get_latest(self, data_object):
        """Test get_latest method."""
        latest = data_object.get_latest(3)
        assert len(latest) == 3
    
    def test_get_oldest(self, data_object):
        """Test get_oldest method."""
        oldest = data_object.get_oldest(3)
        assert len(oldest) == 3
    
    def test_repr(self, data_object):
        """Test string representation."""
        repr_str = repr(data_object)
        assert 'AAPL' in repr_str
        assert 'yfinance' in repr_str

