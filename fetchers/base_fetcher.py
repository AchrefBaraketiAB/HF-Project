"""Base fetcher class for market data."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from core.enums import FetchingSource
from core.data_object import DataObject


class BaseFetcher(ABC):
    """Abstract base class for data fetchers."""
    
    def __init__(self, source: FetchingSource):
        """
        Initialize base fetcher.
        
        Args:
            source: FetchingSource enum value
        """
        self._source = source
    
    @property
    def source(self) -> FetchingSource:
        """Get the fetching source."""
        return self._source
    
    @abstractmethod
    def fetch(
        self,
        ticker: str,
        filter: Optional[Dict[str, Any]] = None,
        date: Optional[Union[date, datetime, str, tuple]] = None,
        column_list: Optional[List[str]] = None
    ) -> DataObject:
        """
        Fetch market data.
        
        Args:
            ticker: Ticker symbol (e.g., 'AAPL', 'BTCUSDT')
            filter: Optional filter dictionary for data filtering
            date: Date or date interval. Can be:
                  - Single date (date, datetime, or 'YYYY-MM-DD' string)
                  - Tuple/list of two dates for range (start, end)
                  - String interval like '1d', '1mo', '1y'
            column_list: List of columns to return (e.g., ['high', 'low', 'volume', 'close'])
        
        Returns:
            DataObject containing the fetched data
        """
        pass
    
    def _parse_date(self, date_input: Optional[Union[date, datetime, str, tuple]]) -> tuple:
        """
        Parse date input into start and end dates.
        
        Args:
            date_input: Date input in various formats
        
        Returns:
            Tuple of (start_date, end_date) as datetime objects
        """
        if date_input is None:
            # Default: last 1 year
            end_date = datetime.now()
            start_date = datetime(end_date.year - 1, end_date.month, end_date.day)
            return start_date, end_date
        
        if isinstance(date_input, tuple) or isinstance(date_input, list):
            if len(date_input) != 2:
                raise ValueError("Date range must be a tuple/list of 2 dates")
            start = self._to_datetime(date_input[0])
            end = self._to_datetime(date_input[1])
            return start, end
        
        if isinstance(date_input, str):
            # Check if it's an interval string (e.g., '1d', '1mo', '1y', '1h', '1m')
            # Valid intervals: 1d, 5d, 1mo, 3mo, 1y, 1h, 1m, etc.
            interval_suffixes = ['d', 'w', 'mo', 'y', 'h', 'm']
            # Check if string ends with a valid interval suffix
            is_interval = False
            for suffix in interval_suffixes:
                if date_input.endswith(suffix) and len(date_input) <= 5:  # Max length like "12mo"
                    # Check that the prefix is numeric
                    prefix = date_input[:-len(suffix)]
                    if prefix.isdigit():
                        is_interval = True
                        break
            
            if is_interval:
                return None, date_input  # Return as interval string
            # Otherwise treat as single date
            single_date = self._to_datetime(date_input)
            return single_date, datetime.now()
        
        # Single date object
        single_date = self._to_datetime(date_input)
        return single_date, datetime.now()
    
    def _to_datetime(self, date_input: Union[date, datetime, str]) -> datetime:
        """Convert various date formats to datetime."""
        if isinstance(date_input, datetime):
            return date_input
        if isinstance(date_input, date):
            return datetime.combine(date_input, datetime.min.time())
        if isinstance(date_input, str):
            try:
                return datetime.strptime(date_input, '%Y-%m-%d')
            except ValueError:
                try:
                    return datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_input}")
        raise ValueError(f"Cannot convert {type(date_input)} to datetime")

