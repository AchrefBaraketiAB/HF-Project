"""Binance fetcher for cryptocurrency market data."""
import pandas as pd
from binance.client import Client
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from core.enums import FetchingSource
from core.data_object import DataObject
from fetchers.base_fetcher import BaseFetcher


class BinanceFetcher(BaseFetcher):
    """Fetcher for cryptocurrency data using Binance API."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Binance fetcher.
        
        Args:
            api_key: Optional Binance API key (for authenticated requests)
            api_secret: Optional Binance API secret (for authenticated requests)
        """
        super().__init__(FetchingSource.BINANCE)
        self._client = Client(api_key, api_secret) if api_key and api_secret else Client()
    
    def fetch(
        self,
        ticker: str,
        filter: Optional[Dict[str, Any]] = None,
        date: Optional[Union[date, datetime, str, tuple]] = None,
        column_list: Optional[List[str]] = None,
        interval: str = '1d'
    ) -> DataObject:
        """
        Fetch cryptocurrency data from Binance.
        
        Args:
            ticker: Cryptocurrency pair (e.g., 'BTCUSDT', 'ETHUSDT', 'BNBUSDT')
            filter: Optional filter dictionary (applied after fetching)
            date: Date or date range
            column_list: List of columns to return (default: all available)
                        Common columns: 'open', 'high', 'low', 'close', 'volume', 'quote_volume'
            interval: Kline interval (default: '1d')
                     Options: '1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M'
        
        Returns:
            DataObject containing the fetched data
        """
        # Parse date input
        start_date, end_date = self._parse_date(date)
        
        # Convert dates to milliseconds timestamp for Binance API
        if isinstance(end_date, str):
            # If end_date is an interval string, use it as period
            # For Binance, we'll use a default period
            start_timestamp = None
            end_timestamp = None
        else:
            start_timestamp = int(start_date.timestamp() * 1000) if start_date else None
            end_timestamp = int(end_date.timestamp() * 1000) if end_date else None
        
        # Fetch klines from Binance
        try:
            klines = self._client.get_klines(
                symbol=ticker.upper(),
                interval=interval,
                startTime=start_timestamp,
                endTime=end_timestamp
            )
        except Exception as e:
            raise ValueError(f"Error fetching data from Binance for {ticker}: {str(e)}")
        
        if not klines:
            raise ValueError(f"No data found for ticker: {ticker}")
        
        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Convert timestamp to datetime index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Convert numeric columns
        numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Select columns
        if column_list:
            # Map common column names
            column_mapping = {
                'high': 'high',
                'low': 'low',
                'open': 'open',
                'close': 'close',
                'volume': 'volume',
                'quote_volume': 'quote_volume'
            }
            
            mapped_columns = []
            for col in column_list:
                col_lower = col.lower()
                if col_lower in column_mapping:
                    mapped_col = column_mapping[col_lower]
                    if mapped_col in df.columns:
                        mapped_columns.append(mapped_col)
                elif col_lower in df.columns:
                    mapped_columns.append(col_lower)
            
            if not mapped_columns:
                raise ValueError(f"None of the specified columns found: {column_list}")
            
            df = df[mapped_columns]
        else:
            # Default: return OHLCV
            df = df[['open', 'high', 'low', 'close', 'volume']]
        
        # Create DataObject
        data_obj = DataObject(df, ticker, self.source.value)
        
        # Apply filter if specified
        if filter:
            filtered_data = data_obj.filter_data(filter)
            data_obj = DataObject(filtered_data, ticker, self.source.value)
        
        return data_obj

