"""DataObject class for handling market data."""
import pandas as pd
from typing import Optional, List, Dict, Any
from pathlib import Path


class DataObject:
    """Class to handle and manipulate market data."""
    
    def __init__(self, data: pd.DataFrame, ticker: str, source: str):
        """
        Initialize DataObject.
        
        Args:
            data: DataFrame containing market data
            ticker: Ticker symbol
            source: Data source (e.g., 'yfinance', 'binance')
        """
        self._data = data.copy()
        self._ticker = ticker
        self._source = source
        self._validate_data()
    
    @property
    def data(self) -> pd.DataFrame:
        """Get the data DataFrame."""
        return self._data
    
    @property
    def ticker(self) -> str:
        """Get the ticker symbol."""
        return self._ticker
    
    @property
    def source(self) -> str:
        """Get the data source."""
        return self._source
    
    def _validate_data(self):
        """Validate that data is a non-empty DataFrame."""
        if not isinstance(self._data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        if self._data.empty:
            raise ValueError("Data cannot be empty")
    
    def get_data(self) -> pd.DataFrame:
        """Return the full DataFrame."""
        return self._data.copy()
    
    def get_columns(self, column_list: List[str]) -> pd.DataFrame:
        """
        Return specified columns from the data.
        
        Args:
            column_list: List of column names to return
            
        Returns:
            DataFrame with specified columns
        """
        missing_cols = [col for col in column_list if col not in self._data.columns]
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")
        return self._data[column_list].copy()
    
    def filter_data(self, filter_dict: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter data based on conditions.
        
        Args:
            filter_dict: Dictionary with column names as keys and filter conditions as values
                         e.g., {'close': '>100', 'volume': '>1000000'}
            
        Returns:
            Filtered DataFrame
        """
        filtered_data = self._data.copy()
        
        for column, condition in filter_dict.items():
            if column not in filtered_data.columns:
                raise ValueError(f"Column '{column}' not found in data")
            
            # Parse condition (e.g., '>100', '<=50', '==200')
            if isinstance(condition, str):
                if condition.startswith('>='):
                    value = float(condition[2:])
                    filtered_data = filtered_data[filtered_data[column] >= value]
                elif condition.startswith('<='):
                    value = float(condition[2:])
                    filtered_data = filtered_data[filtered_data[column] <= value]
                elif condition.startswith('>'):
                    value = float(condition[1:])
                    filtered_data = filtered_data[filtered_data[column] > value]
                elif condition.startswith('<'):
                    value = float(condition[1:])
                    filtered_data = filtered_data[filtered_data[column] < value]
                elif condition.startswith('=='):
                    value = float(condition[2:])
                    filtered_data = filtered_data[filtered_data[column] == value]
                else:
                    raise ValueError(f"Invalid filter condition: {condition}")
            else:
                # Direct value comparison
                filtered_data = filtered_data[filtered_data[column] == condition]
        
        return filtered_data
    
    def save_to_csv(self, filepath: Optional[str] = None) -> str:
        """
        Save data to CSV file.
        
        Args:
            filepath: Optional filepath. If None, generates default path.
            
        Returns:
            Path to saved file
        """
        if filepath is None:
            marketdata_dir = Path(__file__).parent.parent / "marketdata"
            marketdata_dir.mkdir(exist_ok=True)
            filename = f"{self._ticker}_{self._source}_{self._data.index[0]}_{self._data.index[-1]}.csv"
            filepath = marketdata_dir / filename
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        self._data.to_csv(filepath)
        return str(filepath)
    
    def load_from_csv(self, filepath: str) -> 'DataObject':
        """
        Load data from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            New DataObject instance
        """
        data = pd.read_csv(filepath, index_col=0, parse_dates=True)
        return DataObject(data, self._ticker, self._source)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the data.
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            'ticker': self._ticker,
            'source': self._source,
            'rows': len(self._data),
            'columns': list(self._data.columns),
            'date_range': (str(self._data.index[0]), str(self._data.index[-1])),
            'statistics': self._data.describe().to_dict()
        }
    
    def get_latest(self, n: int = 1) -> pd.DataFrame:
        """
        Get latest n rows.
        
        Args:
            n: Number of rows to return
        
        Returns:
            DataFrame with latest n rows
        """
        return self._data.tail(n).copy()
    
    def get_oldest(self, n: int = 1) -> pd.DataFrame:
        """
        Get oldest n rows.
        
        Args:
            n: Number of rows to return
        
        Returns:
            DataFrame with oldest n rows
        """
        return self._data.head(n).copy()
    
    def __repr__(self) -> str:
        """String representation of DataObject."""
        return f"DataObject(ticker={self._ticker}, source={self._source}, rows={len(self._data)})"

