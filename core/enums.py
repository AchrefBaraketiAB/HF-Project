"""Enums for trading framework."""
from enum import Enum


class FetchingSource(Enum):
    """Enum for data fetching sources."""
    YFINANCE = "yfinance"
    BINANCE = "binance"
    CSV = "csv"

