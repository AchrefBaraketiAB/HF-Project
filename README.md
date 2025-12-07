# Trading Framework

A comprehensive Python trading framework for fetching, managing, and analyzing market data from multiple sources (Yahoo Finance for stocks, Binance for crypto).

## Features

- **Multi-source data fetching**: YFinance (stocks), Binance (crypto), and CSV (local files)
- **DataObject class**: Powerful data manipulation and filtering
- **DataManager**: Manage multiple data objects
- **Portfolio management**: Track positions and performance
- **Data validation**: Ensure data quality
- **CSV storage**: Save and load data easily
- **Local testing**: Test with CSV files without API calls
- **Comprehensive testing**: Full test suite included

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) For Binance API, set environment variables:
```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
```

## Quick Start

### Run All Tests

```bash
python main.py
```

This will run all pytest tests with verbose output.

### Run Tests with pytest Directly

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_main.py

# Run specific test class
pytest tests/test_main.py::TestYFinanceFetcher

# Run specific test method
pytest tests/test_main.py::TestYFinanceFetcher::test_fetch_with_date_range

# Skip network tests (Binance/YFinance API)
pytest tests/ -m "not network"

# Run with coverage
pytest tests/ --cov=core --cov=fetchers --cov=utils
```

### Basic Usage Example

```python
from fetchers.yfinance_fetcher import YFinanceFetcher
from fetchers.binance_fetcher import BinanceFetcher
from fetchers.csv_fetcher import CSVFetcher
from datetime import datetime, timedelta

# Fetch stock data
yf_fetcher = YFinanceFetcher()
data = yf_fetcher.fetch(
    ticker='AAPL',
    date=('2024-01-01', '2024-01-31'),
    column_list=['high', 'low', 'close', 'volume']
)

# Fetch crypto data
binance_fetcher = BinanceFetcher()
crypto_data = binance_fetcher.fetch(
    ticker='BTCUSDT',
    date='1mo',
    column_list=['high', 'low', 'close', 'volume'],
    interval='1d'
)

# Fetch from local CSV file (for testing)
csv_fetcher = CSVFetcher()
csv_data = csv_fetcher.fetch(
    ticker='AAPL',  # Will look for AAPL.csv or AAPL_*.csv in marketdata/
    column_list=['high', 'low', 'close', 'volume']
)

# Or specify direct filepath
csv_data2 = csv_fetcher.fetch(
    ticker='AAPL',
    filepath='marketdata/AAPL_2024.csv',
    column_list=['close', 'volume']
)

# Use DataObject methods
filtered = data.filter_data({'close': '>150'})
summary = data.get_summary()
data.save_to_csv()
```

## Project Structure

```
trading-framework/
├── core/               # Core classes
│   ├── data_object.py  # DataObject class
│   ├── data_manager.py # DataManager class
│   ├── portfolio.py    # Portfolio management
│   ├── strategy.py     # Base strategy class
│   └── enums.py        # Enums (FetchingSource)
├── fetchers/           # Data fetchers
│   ├── base_fetcher.py # Base fetcher class
│   ├── yfinance_fetcher.py
│   ├── binance_fetcher.py
│   └── csv_fetcher.py  # CSV file fetcher (for local testing)
├── utils/              # Utilities
│   ├── config.py       # Configuration
│   ├── logger.py       # Logging
│   └── data_validator.py
├── tests/              # Test suite
├── marketdata/         # CSV data storage
├── main.py             # Main test runner
└── requirements.txt    # Dependencies
```

## API Reference

### Fetchers

All fetchers support:
- `ticker`: Symbol (e.g., 'AAPL', 'BTCUSDT')
- `filter`: Optional filter dict (e.g., {'close': '>100'})
- `date`: Date range or interval ('1mo', '1y', or tuple of dates)
- `column_list`: List of columns to return

**CSVFetcher** additionally supports:
- `filepath`: Direct path to CSV file (optional, auto-detects from ticker if not provided)
- `list_available_tickers()`: List all available tickers in marketdata directory

CSV files should be placed in the `marketdata/` directory with naming patterns:
- `{ticker}.csv`
- `{ticker}_*.csv`
- `{ticker}_*_*.csv`

### DataObject

- `get_data()`: Get full DataFrame
- `get_columns(column_list)`: Get specific columns
- `filter_data(filter_dict)`: Filter data
- `save_to_csv(filepath)`: Save to CSV
- `get_summary()`: Get data summary
- `get_latest(n)`: Get latest n rows
- `get_oldest(n)`: Get oldest n rows

### Portfolio

- `open_position(ticker, quantity, price, time)`: Open position
- `close_position(ticker, quantity, price, time)`: Close position
- `get_total_value(current_prices)`: Get total portfolio value
- `get_total_pnl(current_prices)`: Get total profit/loss
- `get_return_pct(current_prices)`: Get return percentage

## Testing

The framework includes comprehensive tests:

- **main.py**: Run all feature tests with detailed output
- **pytest tests/**: Run unit tests with pytest

## License

MIT License

