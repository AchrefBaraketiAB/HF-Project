# Testing Guide - Using pytest

The trading framework now uses **pytest** for all testing. This provides better test organization, fixtures, and reporting.

## Quick Start

### Run All Tests

```bash
python main.py
```

This runs all pytest tests with verbose output.

### Run Tests Directly with pytest

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
```

## Test Organization

### Test Files

- `tests/test_main.py` - Comprehensive tests for all framework features
- `tests/test_data_object.py` - DataObject specific tests
- `tests/test_fetchers.py` - Fetcher classes tests
- `tests/test_data_manager.py` - DataManager tests
- `tests/test_portfolio.py` - Portfolio management tests
- `tests/test_utils.py` - Utility classes tests

### Test Classes in test_main.py

1. **TestConfig** - Configuration management
2. **TestYFinanceFetcher** - Stock data fetching
3. **TestBinanceFetcher** - Crypto data fetching (marked with `@pytest.mark.network`)
4. **TestCSVFetcher** - Local CSV file fetching
5. **TestDataObject** - Data manipulation and filtering
6. **TestDataManager** - Managing multiple data objects
7. **TestPortfolio** - Portfolio management
8. **TestDataValidator** - Data validation utilities

## Advanced Usage

### Skip Network Tests

Some tests require network access (Binance/YFinance APIs). Skip them when offline:

```bash
# Using main.py
python main.py --skip-network

# Using pytest directly
pytest tests/ -m "not network"
```

### Run with Coverage

```bash
# Using main.py
python main.py --coverage

# Using pytest directly
pytest tests/ --cov=core --cov=fetchers --cov=utils --cov-report=html
```

### Run Specific Test

```bash
# Using main.py
python main.py --test TestYFinanceFetcher::test_fetch_with_date_range

# Using pytest directly
pytest tests/test_main.py::TestYFinanceFetcher::test_fetch_with_date_range
```

## Test Markers

Tests are marked for categorization:

- `@pytest.mark.network` - Requires network access
- `@pytest.mark.slow` - Slow running tests
- `@pytest.mark.integration` - Integration tests

## Pytest Configuration

Configuration is in `pytest.ini`:

- Test discovery patterns
- Default output options
- Markers definition
- Coverage settings

## Test Results

When you run `python main.py`, you'll see:

```
108 passed, 4 warnings in 8.94s
```

All tests should pass. Warnings are typically from network tests that are skipped when APIs are unavailable.

## Writing New Tests

To add new tests, follow this pattern:

```python
import pytest
from core.data_object import DataObject

class TestMyFeature:
    """Test my new feature."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        # ... create test data
        return data
    
    def test_feature_name(self, sample_data):
        """Test description."""
        # Arrange
        obj = DataObject(sample_data, 'TEST', 'test')
        
        # Act
        result = obj.some_method()
        
        # Assert
        assert result is not None
```

## Benefits of pytest

1. **Fixtures** - Reusable test data setup
2. **Parametrization** - Run same test with different inputs
3. **Markers** - Categorize and filter tests
4. **Better reporting** - Detailed test output
5. **Plugins** - Extend with coverage, profiling, etc.
6. **Standard** - Industry standard testing framework

## Migration from Custom Test Class

The old `TradingFrameworkTester` class has been replaced with pytest. All tests are now in `tests/test_main.py` using pytest's test structure.

