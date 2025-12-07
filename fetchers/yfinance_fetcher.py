"""YFinance fetcher for stock market data."""
import yfinance as yf
import pandas as pd
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from core.enums import FetchingSource
from core.data_object import DataObject
from fetchers.base_fetcher import BaseFetcher


class YFinanceFetcher(BaseFetcher):
    """Fetcher for stock data using yfinance."""
    
    def __init__(self):
        """Initialize YFinance fetcher."""
        super().__init__(FetchingSource.YFINANCE)
    
    def fetch(
        self,
        ticker: str,
        filter: Optional[Dict[str, Any]] = None,
        date: Optional[Union[date, datetime, str, tuple]] = None,
        column_list: Optional[List[str]] = None
    ) -> DataObject:
        """
        Fetch stock data from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL')
            filter: Optional filter dictionary (applied after fetching)
            date: Date or date interval
            column_list: List of columns to return (default: all available)
                        Common columns: 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'
        
        Returns:
            DataObject containing the fetched data
        """
        # Parse date input
        start_date, end_date = self._parse_date(date)
        
        # Fetch data using yfinance
        if isinstance(end_date, str):
            # Interval string (e.g., '1d', '1mo')
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(period=end_date)
        else:
            # Date range
            ticker_obj = yf.Ticker(ticker)
            data = ticker_obj.history(start=start_date, end=end_date)
        
        if data.empty:
            raise ValueError(f"No data found for ticker: {ticker}")
        
        # Standardize column names to lowercase
        data.columns = [col.lower().replace(' ', '_') for col in data.columns]
        
        # Handle duplicate adj_close columns (adj_close and adj close both become adj_close)
        if 'adj_close' in data.columns:
            # Drop any duplicate columns, keeping the first occurrence
            data = data.loc[:, ~data.columns.duplicated()]
        
        # Apply column filter if specified
        if column_list:
            # Map common column names
            column_mapping = {
                'high': 'high',
                'low': 'low',
                'open': 'open',
                'close': 'close',
                'volume': 'volume',
                'adj_close': 'adj_close',
                'adj close': 'adj_close'
            }
            
            mapped_columns = []
            for col in column_list:
                col_lower = col.lower()
                if col_lower in column_mapping:
                    mapped_col = column_mapping[col_lower]
                    if mapped_col in data.columns:
                        mapped_columns.append(mapped_col)
                elif col_lower in data.columns:
                    mapped_columns.append(col_lower)
            
            if not mapped_columns:
                raise ValueError(f"None of the specified columns found: {column_list}")
            
            data = data[mapped_columns]
        
        # Create DataObject
        data_obj = DataObject(data, ticker, self.source.value)
        
        # Apply filter if specified
        if filter:
            filtered_data = data_obj.filter_data(filter)
            data_obj = DataObject(filtered_data, ticker, self.source.value)
        
        return data_obj

