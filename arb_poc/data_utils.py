from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import pandas as pd

from .binance_client import fetch_klines_cached
from .vision import fetch_klines_vision_cached


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def year_range_utc(year: int) -> Tuple[datetime, datetime]:
    start = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    # end is now if requested year is current year; else end of year
    now = datetime.now(timezone.utc)
    if year == now.year:
        end = now
    else:
        end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    return start, end


def load_three_markets(symbol_bnbusdt: str, symbol_btcusdt: str, symbol_bnbbtc: str, start_dt: datetime, end_dt: datetime, data_dir: str = "data/raw", request_pause_s: float = 0.1) -> pd.DataFrame:
    ensure_dir(data_dir)
    # Cache file names include date range for reproducibility
    def cache_path(symbol: str) -> str:
        return str(Path(data_dir) / f"{symbol}_1m_{start_dt.date()}_{end_dt.date()}.csv")

    # Try public REST; if blocked (451/429), fallback to Binance Vision monthly archives
    try:
        df_bnbusdt = fetch_klines_cached(symbol_bnbusdt, "1m", start_dt, end_dt, cache_path(symbol_bnbusdt), request_pause_s)
        df_btcusdt = fetch_klines_cached(symbol_btcusdt, "1m", start_dt, end_dt, cache_path(symbol_btcusdt), request_pause_s)
        df_bnbbtc = fetch_klines_cached(symbol_bnbbtc, "1m", start_dt, end_dt, cache_path(symbol_bnbbtc), request_pause_s)
        # Basic sanity check; if empty, fallback
        if len(df_bnbusdt) == 0 or len(df_btcusdt) == 0 or len(df_bnbbtc) == 0:
            raise RuntimeError("empty from REST, fallback to vision")
    except Exception:
        df_bnbusdt = fetch_klines_vision_cached(symbol_bnbusdt, "1m", start_dt, end_dt, cache_path(symbol_bnbusdt))
        df_btcusdt = fetch_klines_vision_cached(symbol_btcusdt, "1m", start_dt, end_dt, cache_path(symbol_btcusdt))
        df_bnbbtc = fetch_klines_vision_cached(symbol_bnbbtc, "1m", start_dt, end_dt, cache_path(symbol_bnbbtc))

    # Align on open_time
    def prep(df: pd.DataFrame, name: str) -> pd.DataFrame:
        out = df[["open_time", "close"]].rename(columns={"open_time": "open_time_ms", "close": name})
        out["open_time_ms"] = out["open_time_ms"].astype("int64")
        return out

    a = prep(df_bnbusdt, "BNBUSDT_close")
    b = prep(df_btcusdt, "BTCUSDT_close")
    c = prep(df_bnbbtc, "BNBBTC_close")

    merged = a.merge(b, on="open_time_ms", how="outer").merge(c, on="open_time_ms", how="outer")
    merged = merged.sort_values("open_time_ms").reset_index(drop=True)

    # Drop rows where any of the three is missing to keep fully aligned samples
    merged = merged.dropna(subset=["BNBUSDT_close", "BTCUSDT_close", "BNBBTC_close"]).reset_index(drop=True)

    # Add helpful timestamp columns
    merged["timestamp"] = pd.to_datetime(merged["open_time_ms"], unit="ms", utc=True)
    merged = merged.set_index("timestamp")
    return merged
