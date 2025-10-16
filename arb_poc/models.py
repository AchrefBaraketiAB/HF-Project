from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketBar:
    symbol: str
    open_time_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time_ms: int


@dataclass
class TriangularSnapshot:
    open_time_ms: int
    bnbusdt_close: Optional[float]
    btcusdt_close: Optional[float]
    bnbbtc_close: Optional[float]
