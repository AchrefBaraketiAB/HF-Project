# Trading Framework - Complete Usage Guide

## Step-by-Step Guide to Using main.py

### Step 1: Install Dependencies

First, make sure you have all required packages installed:

```bash
# Navigate to the project directory
cd /Users/achrefbaraketi/Documents/trading-framework

# Install dependencies
pip install -r requirements.txt
```

**Required packages:**
- pandas >= 2.0.0
- yfinance >= 0.2.0
- python-binance >= 1.0.0
- numpy >= 1.24.0
- pytest >= 7.4.0

### Step 2: Verify Installation

Check that Python can import the modules:

```bash
python -c "from core.enums import FetchingSource; print('✓ Imports working')"
```

### Step 3: Run the Main Test Suite

Execute the comprehensive test suite:

```bash
python main.py
```

### Step 4: Understanding the Output

The main.py script runs 8 comprehensive tests. Here's what each test does:

#### TEST 1: Configuration Management
- Tests the Config class
- Verifies default settings
- Tests get/set operations
- Tests nested configuration access

**Expected Output:**
```
✓ Default config loaded successfully
✓ Config get/set works correctly
✓ Nested config access works correctly
✓ Bracket notation works correctly
```

#### TEST 2: YFinance Fetcher (Stock Data)
- Tests fetching stock data from Yahoo Finance
- Fetches AAPL data for the last 30 days
- Tests date range and interval fetching
- Tests data filtering

**Expected Output:**
```
✓ YFinanceFetcher initialized correctly
Fetching AAPL data for January 2024...
✓ Fetched X rows of AAPL data
  Columns: ['high', 'low', 'close', 'volume']
  Date range: 2024-01-XX to 2024-01-XX
```

**Note:** This test requires internet connection. If it fails, check your network.

#### TEST 3: Binance Fetcher (Crypto Data)
- Tests fetching cryptocurrency data from Binance
- Fetches BTCUSDT data
- Tests date filtering

**Expected Output:**
```
✓ BinanceFetcher initialized correctly
Fetching BTCUSDT data for last 30 days...
✓ Fetched X rows of BTCUSDT data
```

**Note:** This may show a warning if Binance API is unavailable. This is normal and won't fail the test.

#### TEST 4: CSV Fetcher (Local File Data)
- Tests fetching data from local CSV files
- Creates a sample CSV file automatically
- Tests auto-file detection
- Tests direct filepath specification
- Tests date filtering on CSV data

**Expected Output:**
```
✓ CSVFetcher initialized correctly
Creating sample CSV file for testing...
✓ Created sample CSV: marketdata/TESTSTOCK.csv
✓ Fetched X rows from CSV
✓ Date filtering works: X rows in date range
✓ Available tickers: ['TESTSTOCK']
```

#### TEST 5: DataObject Class
- Tests all DataObject methods
- Tests data retrieval, filtering, and manipulation
- Tests CSV saving

**Expected Output:**
```
✓ DataObject created successfully
✓ get_data() works correctly
✓ get_columns() works correctly
✓ filter_data() works correctly
✓ get_summary() works correctly
✓ save_to_csv() works correctly
```

#### TEST 6: DataManager Class
- Tests managing multiple DataObjects
- Tests add, get, remove operations
- Tests saving all data objects

**Expected Output:**
```
✓ DataManager initialized
✓ Added 2 data objects
✓ get() works correctly
✓ list_keys() works correctly
✓ save_all() works correctly
```

#### TEST 7: Portfolio Management
- Tests portfolio operations
- Tests opening/closing positions
- Tests PnL calculations

**Expected Output:**
```
✓ Portfolio initialized with $100,000
✓ Opened position: 10 shares of AAPL @ $100
✓ Total portfolio value: $100,100.00
✓ Total PnL: $100.00
✓ Return percentage: 0.10%
```

#### TEST 8: Data Validation
- Tests data validation utilities
- Tests OHLCV validation
- Tests missing value detection

**Expected Output:**
```
✓ validate_ohlcv() works correctly for valid data
✓ check_missing_values() works correctly
✓ check_duplicates() works correctly
✓ validate_date_range() works correctly
```

### Step 5: Review Test Summary

At the end, you'll see a summary:

```
================================================================================
TEST SUMMARY
================================================================================

✓ Passed: 8
  - Config Management
  - YFinance Fetcher
  - Binance Fetcher
  - CSV Fetcher
  - DataObject
  - DataManager
  - Portfolio
  - DataValidator

Success Rate: 100.0%
================================================================================
```

### Step 6: Troubleshooting

#### Issue: ModuleNotFoundError
**Solution:**
```bash
pip install -r requirements.txt
```

#### Issue: YFinance test fails
**Possible causes:**
- No internet connection
- Yahoo Finance API temporarily unavailable
- Rate limiting

**Solution:** This is expected occasionally. The test will show a failure but won't crash.

#### Issue: Binance test shows warning
**This is normal!** Binance API may require authentication or may be rate-limited. The test handles this gracefully.

#### Issue: CSV test fails
**Check:**
- `marketdata/` directory exists
- You have write permissions
- No file conflicts

### Step 7: Running Individual Tests

You can also run individual test methods by modifying main.py or using pytest:

```bash
# Run all unit tests with pytest
pytest tests/

# Run specific test file
pytest tests/test_data_object.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=fetchers --cov=utils
```

### Step 8: Using the Framework in Your Code

After running the tests, you can use the framework in your own code:

```python
from fetchers.csv_fetcher import CSVFetcher
from core.data_object import DataObject

# Create fetcher
fetcher = CSVFetcher()

# Fetch data
data = fetcher.fetch(
    ticker='AAPL',
    column_list=['high', 'low', 'close', 'volume']
)

# Use the data
filtered = data.filter_data({'close': '>150'})
summary = data.get_summary()
print(summary)
```

### Step 9: Creating Your Own CSV Files for Testing

1. Save data to CSV using DataObject:
```python
from fetchers.yfinance_fetcher import YFinanceFetcher

fetcher = YFinanceFetcher()
data = fetcher.fetch(ticker='AAPL', date='1mo')
data.save_to_csv('marketdata/AAPL.csv')
```

2. Or create manually:
```python
import pandas as pd

dates = pd.date_range('2024-01-01', periods=30, freq='D')
df = pd.DataFrame({
    'open': [100 + i for i in range(30)],
    'high': [105 + i for i in range(30)],
    'low': [95 + i for i in range(30)],
    'close': [102 + i for i in range(30)],
    'volume': [1000000 + i * 10000 for i in range(30)]
}, index=dates)

df.to_csv('marketdata/MYTICKER.csv')
```

3. Then use CSVFetcher:
```python
from fetchers.csv_fetcher import CSVFetcher

fetcher = CSVFetcher()
data = fetcher.fetch(ticker='MYTICKER')
```

### Step 10: Advanced Usage

#### Custom Market Data Directory
```python
from fetchers.csv_fetcher import CSVFetcher

# Use custom directory
fetcher = CSVFetcher(marketdata_dir='/path/to/my/data')
data = fetcher.fetch(ticker='AAPL')
```

#### List Available CSV Files
```python
from fetchers.csv_fetcher import CSVFetcher

fetcher = CSVFetcher()
tickers = fetcher.list_available_tickers()
print(f"Available tickers: {tickers}")
```

#### Combine Multiple Data Sources
```python
from fetchers.yfinance_fetcher import YFinanceFetcher
from fetchers.csv_fetcher import CSVFetcher
from core.data_manager import DataManager

manager = DataManager()

# Fetch from API
yf_fetcher = YFinanceFetcher()
api_data = yf_fetcher.fetch(ticker='AAPL', date='1mo')
manager.add(api_data)

# Fetch from CSV
csv_fetcher = CSVFetcher()
csv_data = csv_fetcher.fetch(ticker='AAPL')
manager.add(csv_data, 'AAPL_csv')

# Save all
manager.save_all()
```

## Quick Reference

### Command Line Usage

```bash
# Run all tests
python main.py

# Run unit tests
pytest tests/

# Run specific test
pytest tests/test_data_object.py::TestDataObject::test_get_data

# Run with output
pytest tests/ -v -s
```

### Common Operations

```python
# Fetch data
data = fetcher.fetch(ticker='AAPL', column_list=['close', 'volume'])

# Filter data
filtered = data.filter_data({'close': '>100', 'volume': '>1000000'})

# Get summary
summary = data.get_summary()

# Save to CSV
data.save_to_csv()

# Get latest data
latest = data.get_latest(10)
```

## Next Steps

1. ✅ Run `python main.py` to verify everything works
2. ✅ Review the test output to understand each feature
3. ✅ Create your own CSV files for local testing
4. ✅ Start building your trading strategies using the framework

## Support

If you encounter issues:
1. Check the error messages in the test output
2. Verify all dependencies are installed
3. Check network connection for API-based tests
4. Review the README.md for API documentation

