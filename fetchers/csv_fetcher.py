"""CSV fetcher for local market data files."""
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from core.enums import FetchingSource
from core.data_object import DataObject
from fetchers.base_fetcher import BaseFetcher
from utils.logger import Logger


class CSVFetcher(BaseFetcher):
    """Fetcher for market data from local CSV files."""
    
    def __init__(self, marketdata_dir: Optional[str] = None):
        """
        Initialize CSV fetcher.
        
        Args:
            marketdata_dir: Optional directory path for CSV files (default: 'marketdata' folder)
        """
        super().__init__(FetchingSource.CSV)
        if marketdata_dir is None:
            # Default to marketdata folder in project root
            self._marketdata_dir = Path(__file__).parent.parent / "marketdata"
        else:
            self._marketdata_dir = Path(marketdata_dir)
        
        self._marketdata_dir.mkdir(parents=True, exist_ok=True)
        self._logger = Logger()
    
    @property
    def marketdata_dir(self) -> Path:
        """Get the marketdata directory path."""
        return self._marketdata_dir
    
    def fetch(
        self,
        ticker: str,
        filter: Optional[Dict[str, Any]] = None,
        date: Optional[Union[date, datetime, str, tuple]] = None,
        column_list: Optional[List[str]] = None,
        filepath: Optional[str] = None
    ) -> DataObject:
        """
        Fetch market data from CSV file.
        
        Args:
            ticker: Ticker symbol (used to find CSV file if filepath not provided)
            filter: Optional filter dictionary (applied after fetching)
            date: Date or date range for filtering data
            column_list: List of columns to return (e.g., ['high', 'low', 'volume', 'close'])
            filepath: Optional direct path to CSV file. If not provided, searches for files
                     matching pattern: {ticker}*.csv or {ticker}_{source}_*.csv in marketdata_dir
        
        Returns:
            DataObject containing the fetched data
        """
        # Find CSV file
        if filepath:
            csv_path = Path(filepath)
            if not csv_path.exists():
                raise FileNotFoundError(f"CSV file not found: {filepath}")
        else:
            csv_path = self._find_csv_file(ticker)
            if csv_path is None:
                raise FileNotFoundError(
                    f"No CSV file found for ticker '{ticker}' in {self._marketdata_dir}. "
                    f"Expected filename pattern: {ticker}*.csv or {ticker}_*_*.csv"
                )
        
        self._logger.info(f"Loading CSV file: {csv_path}")
        
        # Load CSV file
        try:
            # Try to parse index as datetime
            data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        except Exception as e:
            # If that fails, try without parse_dates
            try:
                data = pd.read_csv(csv_path, index_col=0)
                # Try to convert index to datetime
                if not isinstance(data.index, pd.DatetimeIndex):
                    data.index = pd.to_datetime(data.index, errors='coerce')
            except Exception as e2:
                raise ValueError(f"Error reading CSV file {csv_path}: {str(e2)}")
        
        if data.empty:
            raise ValueError(f"CSV file is empty: {csv_path}")
        
        # Standardize column names to lowercase
        data.columns = [col.lower().replace(' ', '_') for col in data.columns]
        
        # Handle duplicate adj_close columns (adj_close and adj close both become adj_close)
        if 'adj_close' in data.columns:
            # Drop any duplicate columns, keeping the first occurrence
            data = data.loc[:, ~data.columns.duplicated()]
        
        # Apply date filtering if specified
        if date is not None:
            start_date, end_date = self._parse_date(date)
            
            if isinstance(end_date, str):
                # Interval string - not applicable for CSV, use all data
                self._logger.warning(f"Interval string '{end_date}' not applicable for CSV files, using all data")
            else:
                # Filter by date range
                if isinstance(data.index, pd.DatetimeIndex):
                    if start_date:
                        data = data[data.index >= start_date]
                    if end_date:
                        data = data[data.index <= end_date]
                    
                    if data.empty:
                        raise ValueError(
                            f"No data found in date range {start_date} to {end_date} for ticker {ticker}"
                        )
        
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
                'adj close': 'adj_close',
                'quote_volume': 'quote_volume',
                'quote volume': 'quote_volume'
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
                available_cols = list(data.columns)
                raise ValueError(
                    f"None of the specified columns found: {column_list}. "
                    f"Available columns: {available_cols}"
                )
            
            data = data[mapped_columns]
        
        # Create DataObject
        data_obj = DataObject(data, ticker, self.source.value)
        
        # Apply filter if specified
        if filter:
            filtered_data = data_obj.filter_data(filter)
            data_obj = DataObject(filtered_data, ticker, self.source.value)
        
        self._logger.info(f"Loaded {len(data_obj.data)} rows for ticker {ticker}")
        return data_obj
    
    def _find_csv_file(self, ticker: str) -> Optional[Path]:
        """
        Find CSV file for given ticker.
        
        Args:
            ticker: Ticker symbol
        
        Returns:
            Path to CSV file or None if not found
        """
        # Search patterns (in order of preference):
        # 1. {ticker}.csv
        # 2. {ticker}_*.csv
        # 3. {ticker}_*_*.csv
        
        patterns = [
            f"{ticker}.csv",
            f"{ticker}_*.csv",
            f"{ticker}_*_*.csv"
        ]
        
        for pattern in patterns:
            matches = list(self._marketdata_dir.glob(pattern))
            if matches:
                # Return the first match (or most recent if multiple)
                if len(matches) > 1:
                    # Sort by modification time, return most recent
                    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                return matches[0]
        
        return None
    
    def list_available_tickers(self) -> List[str]:
        """
        List all available tickers in the marketdata directory.
        
        Returns:
            List of ticker symbols (extracted from CSV filenames)
        """
        csv_files = list(self._marketdata_dir.glob("*.csv"))
        tickers = set()
        
        for csv_file in csv_files:
            # Extract ticker from filename
            # Patterns: {ticker}.csv, {ticker}_*.csv, {ticker}_*_*.csv
            name = csv_file.stem  # filename without extension
            if '_' in name:
                ticker = name.split('_')[0]
            else:
                ticker = name
            tickers.add(ticker)
        
        return sorted(list(tickers))

