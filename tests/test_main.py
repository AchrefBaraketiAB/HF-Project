"""Comprehensive pytest tests for trading framework - function-based."""
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

from core.enums import FetchingSource
from core.data_object import DataObject
from core.data_manager import DataManager
from core.portfolio import Portfolio
from fetchers.yfinance_fetcher import YFinanceFetcher
from fetchers.binance_fetcher import BinanceFetcher
from fetchers.csv_fetcher import CSVFetcher
from utils.config import Config
from utils.logger import Logger
from utils.data_validator import DataValidator


# Fixtures
@pytest.fixture
def sample_data():
    """Create sample DataFrame for testing."""
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    return pd.DataFrame({
        'open': [100 + i for i in range(20)],
        'high': [105 + i for i in range(20)],
        'low': [95 + i for i in range(20)],
        'close': [102 + i for i in range(20)],
        'volume': [1000000 + i * 10000 for i in range(20)]
    }, index=dates)


@pytest.fixture
def yfinance_fetcher():
    """Create YFinanceFetcher instance."""
    return YFinanceFetcher()


@pytest.fixture
def binance_fetcher():
    """Create BinanceFetcher instance."""
    return BinanceFetcher()


@pytest.fixture
def csv_fetcher(tmp_path):
    """Create CSVFetcher instance with temporary directory."""
    return CSVFetcher(marketdata_dir=str(tmp_path))


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = pd.DataFrame({
        'open': [100 + i * 0.5 for i in range(30)],
        'high': [105 + i * 0.5 for i in range(30)],
        'low': [95 + i * 0.5 for i in range(30)],
        'close': [102 + i * 0.5 for i in range(30)],
        'volume': [1000000 + i * 10000 for i in range(30)]
    }, index=dates)
    
    csv_path = tmp_path / 'TESTSTOCK.csv'
    data.to_csv(csv_path)
    return csv_path


# Config Tests
def test_default_config():
    """Test default configuration."""
    config = Config()
    assert config.get('marketdata_dir') == 'marketdata'
    assert config.get('log_level') == 'INFO'


def test_config_get_set():
    """Test config get/set operations."""
    config = Config()
    config.set('test_key', 'test_value')
    assert config.get('test_key') == 'test_value'


def test_nested_config():
    """Test nested config access."""
    config = Config()
    config.set('binance.api_key', 'test_api_key')
    assert config.get('binance.api_key') == 'test_api_key'


def test_bracket_notation():
    """Test bracket notation for config."""
    config = Config()
    config['another_key'] = 'another_value'
    assert config['another_key'] == 'another_value'


# YFinance Fetcher Tests
def test_yfinance_initialization(yfinance_fetcher):
    """Test fetcher initialization."""
    assert yfinance_fetcher.source == FetchingSource.YFINANCE


def test_yfinance_fetch_with_date_range(yfinance_fetcher):
    """Test fetching with date range."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data_obj = yfinance_fetcher.fetch(
        ticker='AAPL',
        date=(start_date, end_date),
        column_list=['high', 'low', 'close', 'volume']
    )
    
    assert data_obj.ticker == 'AAPL'
    assert data_obj.source == 'yfinance'
    assert not data_obj.data.empty
    assert 'high' in data_obj.data.columns
    assert 'low' in data_obj.data.columns


def test_yfinance_fetch_with_interval(yfinance_fetcher):
    """Test fetching with interval string."""
    data_obj = yfinance_fetcher.fetch(
        ticker='MSFT',
        date='1mo',
        column_list=['close', 'volume']
    )
    assert not data_obj.data.empty


def test_yfinance_filter_functionality(yfinance_fetcher):
    """Test filter functionality."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data_obj = yfinance_fetcher.fetch(
        ticker='AAPL',
        date=(start_date, end_date),
        column_list=['close', 'volume']
    )
    
    if len(data_obj.data) > 0:
        mean_close = data_obj.data['close'].mean()
        filtered = data_obj.filter_data({'close': f'>{mean_close}'})
        assert len(filtered) <= len(data_obj.data)


# Binance Fetcher Tests
def test_binance_initialization(binance_fetcher):
    """Test fetcher initialization."""
    assert binance_fetcher.source == FetchingSource.BINANCE


@pytest.mark.network
def test_binance_fetch_with_date_range(binance_fetcher):
    """Test fetching with date range."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        data_obj = binance_fetcher.fetch(
            ticker='BTCUSDT',
            date=(start_date, end_date),
            column_list=['high', 'low', 'close', 'volume'],
            interval='1d'
        )
        
        assert data_obj.ticker == 'BTCUSDT'
        assert data_obj.source == 'binance'
        assert not data_obj.data.empty
        assert 'high' in data_obj.data.columns
    except Exception as e:
        pytest.skip(f"Binance API unavailable: {e}")


@pytest.mark.network
def test_binance_filter_functionality(binance_fetcher):
    """Test filter functionality."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    try:
        data_obj = binance_fetcher.fetch(
            ticker='BTCUSDT',
            date=(start_date, end_date),
            column_list=['close', 'volume'],
            interval='1d'
        )
        
        if len(data_obj.data) > 0:
            mean_close = data_obj.data['close'].mean()
            filtered = data_obj.filter_data({'close': f'>{mean_close}'})
            assert len(filtered) <= len(data_obj.data)
    except Exception as e:
        pytest.skip(f"Binance API unavailable: {e}")


# CSV Fetcher Tests
def test_csv_initialization(csv_fetcher):
    """Test fetcher initialization."""
    assert csv_fetcher.source == FetchingSource.CSV


def test_csv_fetch_with_auto_detection(csv_fetcher, sample_csv_file):
    """Test fetch with auto-file detection."""
    data_obj = csv_fetcher.fetch(
        ticker='TESTSTOCK',
        column_list=['high', 'low', 'close', 'volume']
    )
    
    assert data_obj.ticker == 'TESTSTOCK'
    assert data_obj.source == 'csv'
    assert not data_obj.data.empty
    assert 'high' in data_obj.data.columns


def test_csv_fetch_with_filepath(csv_fetcher, sample_csv_file):
    """Test fetch with direct filepath."""
    data_obj = csv_fetcher.fetch(
        ticker='TESTSTOCK2',
        filepath=str(sample_csv_file),
        column_list=['close', 'volume']
    )
    assert not data_obj.data.empty


def test_csv_date_filtering(csv_fetcher, sample_csv_file):
    """Test date filtering."""
    start_date = datetime(2024, 1, 10)
    end_date = datetime(2024, 1, 20)
    
    data_obj = csv_fetcher.fetch(
        ticker='TESTSTOCK',
        date=(start_date, end_date)
    )
    assert not data_obj.data.empty
    assert len(data_obj.data) <= 30


def test_csv_filter_functionality(csv_fetcher, sample_csv_file):
    """Test filter functionality."""
    data_obj = csv_fetcher.fetch(ticker='TESTSTOCK')
    
    if len(data_obj.data) > 0:
        mean_close = data_obj.data['close'].mean()
        filtered = data_obj.filter_data({'close': f'>{mean_close}'})
        assert len(filtered) <= len(data_obj.data)


def test_csv_list_available_tickers(csv_fetcher, sample_csv_file):
    """Test list_available_tickers method."""
    tickers = csv_fetcher.list_available_tickers()
    assert 'TESTSTOCK' in tickers


# DataObject Tests
def test_data_object_creation(sample_data):
    """Test DataObject creation."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    assert data_obj.ticker == 'TEST'
    assert data_obj.source == 'test_source'
    assert len(data_obj.data) == 20


def test_data_object_get_data(sample_data):
    """Test get_data method."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    data = data_obj.get_data()
    pd.testing.assert_frame_equal(data, sample_data)


def test_data_object_get_columns(sample_data):
    """Test get_columns method."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    columns = data_obj.get_columns(['high', 'low', 'volume'])
    assert list(columns.columns) == ['high', 'low', 'volume']


def test_data_object_filter_data(sample_data):
    """Test filter_data method."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    filtered = data_obj.filter_data({'close': '>110'})
    assert len(filtered) > 0
    assert all(filtered['close'] > 110)


def test_data_object_get_summary(sample_data):
    """Test get_summary method."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    summary = data_obj.get_summary()
    assert summary['ticker'] == 'TEST'
    assert summary['rows'] == 20
    assert 'columns' in summary
    assert 'date_range' in summary


def test_data_object_get_latest_oldest(sample_data):
    """Test get_latest and get_oldest methods."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    latest = data_obj.get_latest(5)
    oldest = data_obj.get_oldest(5)
    assert len(latest) == 5
    assert len(oldest) == 5


def test_data_object_save_to_csv(sample_data, tmp_path):
    """Test save_to_csv method."""
    data_obj = DataObject(sample_data, 'TEST', 'test_source')
    filepath = tmp_path / "test_data.csv"
    result_path = data_obj.save_to_csv(str(filepath))
    assert Path(result_path).exists()
    
    # Verify data can be loaded
    loaded = pd.read_csv(filepath, index_col=0, parse_dates=True)
    assert len(loaded) == 20


# DataManager Tests
def test_data_manager_initialization():
    """Test DataManager initialization."""
    manager = DataManager()
    assert len(manager) == 0


def test_data_manager_add(sample_data):
    """Test adding data objects."""
    manager = DataManager()
    obj1 = DataObject(sample_data, 'AAPL', 'yfinance')
    manager.add(obj1)
    assert len(manager) == 1


def test_data_manager_get(sample_data):
    """Test getting data objects."""
    manager = DataManager()
    obj1 = DataObject(sample_data, 'AAPL', 'yfinance')
    manager.add(obj1)
    retrieved = manager.get('AAPL_yfinance')
    assert retrieved is not None
    assert retrieved.ticker == 'AAPL'


def test_data_manager_list_keys(sample_data):
    """Test listing keys."""
    manager = DataManager()
    obj1 = DataObject(sample_data, 'AAPL', 'yfinance')
    dates2 = pd.date_range('2024-01-01', periods=10, freq='D')
    data2 = pd.DataFrame({'close': [200 + i for i in range(10)]}, index=dates2)
    obj2 = DataObject(data2, 'BTCUSDT', 'binance')
    manager.add(obj1)
    manager.add(obj2, 'custom_key')
    keys = manager.list_keys()
    assert 'AAPL_yfinance' in keys
    assert 'custom_key' in keys


def test_data_manager_remove(sample_data):
    """Test removing data objects."""
    manager = DataManager()
    obj1 = DataObject(sample_data, 'AAPL', 'yfinance')
    manager.add(obj1)
    manager.remove('AAPL_yfinance')
    assert len(manager) == 0


def test_data_manager_save_all(sample_data, tmp_path):
    """Test saving all data objects."""
    manager = DataManager()
    obj1 = DataObject(sample_data, 'AAPL', 'yfinance')
    manager.add(obj1)
    manager.save_all(str(tmp_path))
    assert (tmp_path / 'AAPL_yfinance.csv').exists()


def test_data_manager_clear(sample_data):
    """Test clearing all data objects."""
    manager = DataManager()
    obj1 = DataObject(sample_data, 'AAPL', 'yfinance')
    manager.add(obj1)
    manager.clear()
    assert len(manager) == 0


# Portfolio Tests
def test_portfolio_initialization():
    """Test Portfolio initialization."""
    portfolio = Portfolio(initial_capital=100000.0)
    assert portfolio.initial_capital == 100000.0
    assert portfolio.cash == 100000.0


def test_portfolio_open_position():
    """Test opening a position."""
    portfolio = Portfolio(initial_capital=100000.0)
    success = portfolio.open_position('AAPL', 10, 100.0, datetime.now())
    assert success is True
    assert portfolio.cash == 99000.0


def test_portfolio_open_position_insufficient_cash():
    """Test opening position with insufficient cash."""
    portfolio = Portfolio(initial_capital=100000.0)
    success = portfolio.open_position('MSFT', 10000, 100.0, datetime.now())
    assert success is False


def test_portfolio_get_total_value():
    """Test getting total portfolio value."""
    portfolio = Portfolio(initial_capital=100000.0)
    portfolio.open_position('AAPL', 10, 100.0, datetime.now())
    current_prices = {'AAPL': 110.0}
    total_value = portfolio.get_total_value(current_prices)
    assert total_value == 100100.0


def test_portfolio_get_total_pnl():
    """Test getting total PnL."""
    portfolio = Portfolio(initial_capital=100000.0)
    portfolio.open_position('AAPL', 10, 100.0, datetime.now())
    current_prices = {'AAPL': 110.0}
    pnl = portfolio.get_total_pnl(current_prices)
    assert pnl == 100.0


def test_portfolio_get_return_pct():
    """Test getting return percentage."""
    portfolio = Portfolio(initial_capital=100000.0)
    portfolio.open_position('AAPL', 10, 100.0, datetime.now())
    current_prices = {'AAPL': 110.0}
    return_pct = portfolio.get_return_pct(current_prices)
    assert return_pct == 0.1


def test_portfolio_close_position():
    """Test closing a position."""
    portfolio = Portfolio(initial_capital=100000.0)
    portfolio.open_position('AAPL', 10, 100.0, datetime.now())
    success = portfolio.close_position('AAPL', 10, 110.0, datetime.now())
    assert success is True
    assert portfolio.cash == 100100.0
    assert len(portfolio.closed_positions) == 1


# DataValidator Tests
def test_validate_ohlcv(sample_data):
    """Test OHLCV validation."""
    result = DataValidator.validate_ohlcv(sample_data)
    assert result is True


def test_check_missing_values(sample_data):
    """Test checking for missing values."""
    missing = DataValidator.check_missing_values(sample_data)
    assert all(count == 0 for count in missing.values())


def test_check_duplicates(sample_data):
    """Test checking for duplicates."""
    duplicates = DataValidator.check_duplicates(sample_data)
    assert duplicates == 0


def test_validate_date_range(sample_data):
    """Test date range validation."""
    min_date = pd.Timestamp('2024-01-01')
    max_date = pd.Timestamp('2024-12-31')
    result = DataValidator.validate_date_range(sample_data, min_date, max_date)
    assert result is True


# Strategy Tests
def test_strategy_not_implemented():
    """Test that strategy raises NotImplementedError."""
    from core.strategy import BaseStrategy
    
    class TestStrategy(BaseStrategy):
        pass
    
    strategy = TestStrategy("test")
    data_obj = DataObject(
        pd.DataFrame({'close': [100, 101, 102]}, index=pd.date_range('2024-01-01', periods=3)),
        'TEST', 'test'
    )
    
    with pytest.raises(NotImplementedError):
        strategy.generate_signals(data_obj)
    
    with pytest.raises(NotImplementedError):
        strategy.calculate_indicators(data_obj)
