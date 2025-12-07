"""Tests for utility classes."""
import pytest
import pandas as pd
from pathlib import Path
from utils.config import Config
from utils.data_validator import DataValidator
from core.data_object import DataObject


class TestConfig:
    """Test cases for Config class."""
    
    def test_init_default(self):
        """Test Config initialization with defaults."""
        config = Config()
        assert config.get('marketdata_dir') == 'marketdata'
        assert config.get('log_level') == 'INFO'
    
    def test_get_set(self):
        """Test get and set methods."""
        config = Config()
        config.set('test_key', 'test_value')
        assert config.get('test_key') == 'test_value'
    
    def test_get_nested(self):
        """Test getting nested config values."""
        config = Config()
        api_key = config.get('binance.api_key')
        assert api_key is not None
    
    def test_set_nested(self):
        """Test setting nested config values."""
        config = Config()
        config.set('binance.api_key', 'test_key')
        assert config.get('binance.api_key') == 'test_key'
    
    def test_bracket_notation(self):
        """Test bracket notation for config access."""
        config = Config()
        config['test'] = 'value'
        assert config['test'] == 'value'


class TestDataValidator:
    """Test cases for DataValidator."""
    
    @pytest.fixture
    def valid_ohlcv_data(self):
        """Create valid OHLCV data."""
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        return pd.DataFrame({
            'open': [100 + i for i in range(10)],
            'high': [105 + i for i in range(10)],
            'low': [95 + i for i in range(10)],
            'close': [102 + i for i in range(10)],
            'volume': [1000000 + i * 10000 for i in range(10)]
        }, index=dates)
    
    def test_validate_ohlcv_valid(self, valid_ohlcv_data):
        """Test validation of valid OHLCV data."""
        assert DataValidator.validate_ohlcv(valid_ohlcv_data) is True
    
    def test_validate_ohlcv_missing_column(self, valid_ohlcv_data):
        """Test validation with missing column."""
        invalid_data = valid_ohlcv_data.drop(columns=['high'])
        with pytest.raises(ValueError, match="Missing required OHLCV columns"):
            DataValidator.validate_ohlcv(invalid_data)
    
    def test_validate_ohlcv_negative_price(self, valid_ohlcv_data):
        """Test validation with negative price."""
        invalid_data = valid_ohlcv_data.copy()
        invalid_data.loc[0, 'close'] = -10
        with pytest.raises(ValueError, match="Negative values found"):
            DataValidator.validate_ohlcv(invalid_data)
    
    def test_validate_ohlcv_high_low_invalid(self, valid_ohlcv_data):
        """Test validation with high < low."""
        invalid_data = valid_ohlcv_data.copy()
        invalid_data.loc[0, 'high'] = 90
        invalid_data.loc[0, 'low'] = 100
        with pytest.raises(ValueError, match="High price cannot be less than low price"):
            DataValidator.validate_ohlcv(invalid_data)
    
    def test_check_missing_values(self, valid_ohlcv_data):
        """Test checking for missing values."""
        data_with_nulls = valid_ohlcv_data.copy()
        data_with_nulls.loc[0, 'close'] = None
        missing = DataValidator.check_missing_values(data_with_nulls)
        assert missing['close'] == 1
    
    def test_check_duplicates(self, valid_ohlcv_data):
        """Test checking for duplicates."""
        data_with_dup = pd.concat([valid_ohlcv_data, valid_ohlcv_data.iloc[[0]]])
        duplicates = DataValidator.check_duplicates(data_with_dup)
        assert duplicates == 1
    
    def test_validate_date_range(self, valid_ohlcv_data):
        """Test date range validation."""
        min_date = pd.Timestamp('2024-01-01')
        max_date = pd.Timestamp('2024-12-31')
        assert DataValidator.validate_date_range(valid_ohlcv_data, min_date, max_date) is True
    
    def test_validate_date_range_invalid(self, valid_ohlcv_data):
        """Test date range validation with invalid range."""
        min_date = pd.Timestamp('2025-01-01')
        with pytest.raises(ValueError, match="Data contains dates before"):
            DataValidator.validate_date_range(valid_ohlcv_data, min_date)

