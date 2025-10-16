from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import requests
import pandas as pd

BINANCE_API_BASE = "https://api.binance.com"


@dataclass
class Kline:
    open_time: int  # ms
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int  # ms


def _klines_request(symbol: str, interval: str, start_time_ms: int, end_time_ms: Optional[int], limit: int = 1000) -> List[List[Any]]:
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time_ms,
        "limit": limit,
    }
    if end_time_ms is not None:
        params["endTime"] = end_time_ms

    url = f"{BINANCE_API_BASE}/api/v3/klines"
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_klines(symbol: str, interval: str, start_dt: datetime, end_dt: datetime, request_pause_s: float = 0.1) -> pd.DataFrame:
    """
    Fetch klines for a symbol and interval between start_dt and end_dt (UTC).

    Returns DataFrame with columns: [open_time, open, high, low, close, volume, close_time]
    """
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    else:
        start_dt = start_dt.astimezone(timezone.utc)

    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    else:
        end_dt = end_dt.astimezone(timezone.utc)

    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)

    all_rows: List[List[Any]] = []
    last_ms = start_ms

    while True:
        batch = _klines_request(symbol, interval, last_ms, end_ms, limit=1000)
        if not batch:
            break
        all_rows.extend(batch)
        last_open_time = batch[-1][0]
        # move to next minute after last open_time to avoid duplicates
        last_ms = int(last_open_time) + 1
        if batch[-1][6] >= end_ms or last_ms > end_ms:
            break
        time.sleep(request_pause_s)

    if not all_rows:
        return pd.DataFrame(columns=["open_time","open","high","low","close","volume","close_time"]).astype({
            "open_time": "int64",
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "float64",
            "close_time": "int64",
        })

    records = []
    for r in all_rows:
        # Binance kline schema
        # [
        #   0 Open time, 1 Open, 2 High, 3 Low, 4 Close, 5 Volume,
        #   6 Close time, 7 Quote asset volume, 8 Number of trades,
        #   9 Taker buy base asset volume, 10 Taker buy quote asset volume, 11 Ignore
        # ]
        records.append({
            "open_time": int(r[0]),
            "open": float(r[1]),
            "high": float(r[2]),
            "low": float(r[3]),
            "close": float(r[4]),
            "volume": float(r[5]),
            "close_time": int(r[6]),
        })

    df = pd.DataFrame.from_records(records)
    df = df.drop_duplicates(subset=["open_time"]).sort_values("open_time").reset_index(drop=True)
    return df


def fetch_klines_cached(symbol: str, interval: str, start_dt: datetime, end_dt: datetime, cache_path: str, request_pause_s: float = 0.1) -> pd.DataFrame:
    """Fetch klines and cache to CSV at cache_path. If file exists, load from cache."""
    try:
        return pd.read_csv(cache_path)
    except FileNotFoundError:
        pass

    df = fetch_klines(symbol, interval, start_dt, end_dt, request_pause_s=request_pause_s)
    df.to_csv(cache_path, index=False)
    return df
