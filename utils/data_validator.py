"""Data validation utilities for trading framework."""
import pandas as pd
from typing import List, Optional, Dict, Any


class DataValidator:
    """Utility class for validating market data."""
    
    @staticmethod
    def validate_ohlcv(data: pd.DataFrame) -> bool:
        """
        Validate that DataFrame contains required OHLCV columns.
        
        Args:
            data: DataFrame to validate
        
        Returns:
            True if valid, raises ValueError if not
        """
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required OHLCV columns: {missing_cols}")
        
        # Check for negative values in price columns
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if (data[col] < 0).any():
                raise ValueError(f"Negative values found in {col} column")
        
        # Check high >= low
        if (data['high'] < data['low']).any():
            raise ValueError("High price cannot be less than low price")
        
        # Check high >= open and high >= close
        if (data['high'] < data['open']).any() or (data['high'] < data['close']).any():
            raise ValueError("High price must be >= open and close prices")
        
        # Check low <= open and low <= close
        if (data['low'] > data['open']).any() or (data['low'] > data['close']).any():
            raise ValueError("Low price must be <= open and close prices")
        
        # Check volume >= 0
        if (data['volume'] < 0).any():
            raise ValueError("Volume cannot be negative")
        
        return True
    
    @staticmethod
    def check_missing_values(data: pd.DataFrame, columns: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Check for missing values in DataFrame.
        
        Args:
            data: DataFrame to check
            columns: Optional list of columns to check (default: all)
        
        Returns:
            Dictionary with column names as keys and missing value counts as values
        """
        if columns is None:
            columns = data.columns.tolist()
        
        missing = {}
        for col in columns:
            if col in data.columns:
                missing[col] = data[col].isna().sum()
        
        return missing
    
    @staticmethod
    def check_duplicates(data: pd.DataFrame) -> int:
        """
        Check for duplicate rows in DataFrame.
        
        Args:
            data: DataFrame to check
        
        Returns:
            Number of duplicate rows
        """
        return data.duplicated().sum()
    
    @staticmethod
    def validate_date_range(data: pd.DataFrame, min_date: Optional[pd.Timestamp] = None, 
                           max_date: Optional[pd.Timestamp] = None) -> bool:
        """
        Validate that data is within specified date range.
        
        Args:
            data: DataFrame with datetime index
            min_date: Minimum allowed date
            max_date: Maximum allowed date
        
        Returns:
            True if valid, raises ValueError if not
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have a DatetimeIndex")
        
        if min_date and data.index.min() < min_date:
            raise ValueError(f"Data contains dates before {min_date}")
        
        if max_date and data.index.max() > max_date:
            raise ValueError(f"Data contains dates after {max_date}")
        
        return True

