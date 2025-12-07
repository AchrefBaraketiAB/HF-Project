"""Tests for fetcher classes."""
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from core.enums import FetchingSource
from fetchers.yfinance_fetcher import YFinanceFetcher
from fetchers.binance_fetcher import BinanceFetcher
from fetchers.csv_fetcher import CSVFetcher


class TestYFinanceFetcher:
    """Test cases for YFinanceFetcher."""
    
    @pytest.fixture
    def fetcher(self):
        """Create YFinanceFetcher instance."""
        return YFinanceFetcher()
    
    def test_init(self, fetcher):
        """Test fetcher initialization."""
        assert fetcher.source == FetchingSource.YFINANCE
    
    def test_fetch_basic(self, fetcher):
        """Test basic fetch functionality."""
        # Use a well-known ticker
        data_obj = fetcher.fetch(
            ticker='AAPL',
            date=('2024-01-01', '2024-01-31'),
            column_list=['high', 'low', 'close', 'volume']
        )
        assert data_obj.ticker == 'AAPL'
        assert data_obj.source == 'yfinance'
        assert not data_obj.data.empty
        assert 'high' in data_obj.data.columns
        assert 'low' in data_obj.data.columns
    
    def test_fetch_with_interval(self, fetcher):
        """Test fetch with interval string."""
        data_obj = fetcher.fetch(
            ticker='AAPL',
            date='1mo',
            column_list=['close', 'volume']
        )
        assert not data_obj.data.empty
    
    def test_fetch_invalid_ticker(self, fetcher):
        """Test fetch with invalid ticker."""
        with pytest.raises(ValueError):
            fetcher.fetch(ticker='INVALID_TICKER_XYZ123', date='1mo')


class TestBinanceFetcher:
    """Test cases for BinanceFetcher."""
    
    @pytest.fixture
    def fetcher(self):
        """Create BinanceFetcher instance."""
        return BinanceFetcher()
    
    def test_init(self, fetcher):
        """Test fetcher initialization."""
        assert fetcher.source == FetchingSource.BINANCE
    
    def test_fetch_basic(self, fetcher):
        """Test basic fetch functionality."""
        data_obj = fetcher.fetch(
            ticker='BTCUSDT',
            date=('2024-01-01', '2024-01-31'),
            column_list=['high', 'low', 'close', 'volume'],
            interval='1d'
        )
        assert data_obj.ticker == 'BTCUSDT'
        assert data_obj.source == 'binance'
        assert not data_obj.data.empty
        assert 'high' in data_obj.data.columns
        assert 'low' in data_obj.data.columns
    
    def test_fetch_invalid_ticker(self, fetcher):
        """Test fetch with invalid ticker."""
        with pytest.raises(ValueError):
            fetcher.fetch(ticker='INVALIDPAIR', date='1mo')


class TestBaseFetcher:
    """Test cases for BaseFetcher date parsing."""
    
    def test_parse_date_tuple(self):
        """Test date parsing with tuple."""
        from fetchers.base_fetcher import BaseFetcher
        from core.enums import FetchingSource
        
        class TestFetcher(BaseFetcher):
            def fetch(self, ticker, filter=None, date=None, column_list=None):
                pass
        
        fetcher = TestFetcher(FetchingSource.YFINANCE)
        start, end = fetcher._parse_date(('2024-01-01', '2024-01-31'))
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
    
    def test_parse_date_string(self):
        """Test date parsing with string."""
        from fetchers.base_fetcher import BaseFetcher
        from core.enums import FetchingSource
        
        class TestFetcher(BaseFetcher):
            def fetch(self, ticker, filter=None, date=None, column_list=None):
                pass
        
        fetcher = TestFetcher(FetchingSource.YFINANCE)
        start, end = fetcher._parse_date('2024-01-01')
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
    
    def test_parse_date_interval(self):
        """Test date parsing with interval string."""
        from fetchers.base_fetcher import BaseFetcher
        from core.enums import FetchingSource
        
        class TestFetcher(BaseFetcher):
            def fetch(self, ticker, filter=None, date=None, column_list=None):
                pass
        
        fetcher = TestFetcher(FetchingSource.YFINANCE)
        start, end = fetcher._parse_date('1mo')
        assert start is None
        assert end == '1mo'


class TestCSVFetcher:
    """Test cases for CSVFetcher."""
    
    @pytest.fixture
    def fetcher(self, tmp_path):
        """Create CSVFetcher instance with temporary directory."""
        return CSVFetcher(marketdata_dir=str(tmp_path))
    
    @pytest.fixture
    def sample_csv_file(self, tmp_path):
        """Create a sample CSV file for testing."""
        dates = pd.date_range('2024-01-01', periods=20, freq='D')
        data = pd.DataFrame({
            'open': [100 + i for i in range(20)],
            'high': [105 + i for i in range(20)],
            'low': [95 + i for i in range(20)],
            'close': [102 + i for i in range(20)],
            'volume': [1000000 + i * 10000 for i in range(20)]
        }, index=dates)
        
        csv_path = tmp_path / 'TESTSTOCK.csv'
        data.to_csv(csv_path)
        return csv_path
    
    def test_init(self, fetcher):
        """Test fetcher initialization."""
        assert fetcher.source == FetchingSource.CSV
    
    def test_fetch_basic(self, fetcher, sample_csv_file):
        """Test basic fetch functionality."""
        data_obj = fetcher.fetch(
            ticker='TESTSTOCK',
            column_list=['high', 'low', 'close', 'volume']
        )
        assert data_obj.ticker == 'TESTSTOCK'
        assert data_obj.source == 'csv'
        assert not data_obj.data.empty
        assert 'high' in data_obj.data.columns
        assert 'low' in data_obj.data.columns
    
    def test_fetch_with_filepath(self, fetcher, sample_csv_file):
        """Test fetch with direct filepath."""
        data_obj = fetcher.fetch(
            ticker='TESTSTOCK2',
            filepath=str(sample_csv_file),
            column_list=['close', 'volume']
        )
        assert data_obj.ticker == 'TESTSTOCK2'
        assert not data_obj.data.empty
    
    def test_fetch_with_date_filter(self, fetcher, sample_csv_file):
        """Test fetch with date filtering."""
        start_date = datetime(2024, 1, 5)
        end_date = datetime(2024, 1, 15)
        data_obj = fetcher.fetch(
            ticker='TESTSTOCK',
            date=(start_date, end_date)
        )
        assert not data_obj.data.empty
        assert len(data_obj.data) <= 20
    
    def test_fetch_invalid_ticker(self, fetcher):
        """Test fetch with invalid/nonexistent ticker."""
        with pytest.raises(FileNotFoundError):
            fetcher.fetch(ticker='NONEXISTENT', date='1mo')
    
    def test_fetch_invalid_filepath(self, fetcher):
        """Test fetch with invalid filepath."""
        with pytest.raises(FileNotFoundError):
            fetcher.fetch(ticker='TEST', filepath='/nonexistent/path/file.csv')
    
    def test_list_available_tickers(self, fetcher, sample_csv_file):
        """Test list_available_tickers method."""
        # Create another CSV file
        dates = pd.date_range('2024-01-01', periods=10, freq='D')
        data = pd.DataFrame({'close': [100 + i for i in range(10)]}, index=dates)
        csv_path2 = Path(fetcher.marketdata_dir) / 'ANOTHER.csv'
        data.to_csv(csv_path2)
        
        tickers = fetcher.list_available_tickers()
        assert 'TESTSTOCK' in tickers
        assert 'ANOTHER' in tickers

