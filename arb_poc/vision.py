from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path
from pathlib import Path
from typing import Iterator, Tuple, List

import pandas as pd
import requests
import zipfile

BINANCE_VISION_BASE = "https://data.binance.vision"


def _iter_months(start: datetime, end: datetime) -> Iterator[Tuple[int, int]]:
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    else:
        start = start.astimezone(timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    else:
        end = end.astimezone(timezone.utc)

    y, m = start.year, start.month
    while (y < end.year) or (y == end.year and m <= end.month):
        yield y, m
        if m == 12:
            y += 1
            m = 1
        else:
            m += 1


def _monthly_zip_url(symbol: str, interval: str, year: int, month: int) -> str:
    # Example:
    # https://data.binance.vision/data/spot/monthly/klines/BNBUSDT/1m/BNBUSDT-1m-2025-01.zip
    return (
        f"{BINANCE_VISION_BASE}/data/spot/monthly/klines/{symbol}/{interval}/"
        f"{symbol}-{interval}-{year}-{month:02d}.zip"
    )


def _read_month_csv_from_zip_bytes(zip_bytes: bytes, csv_expected_prefix: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        # Find the first CSV matching the expected prefix
        name = None
        for info in zf.infolist():
            if info.filename.endswith(".csv") and info.filename.startswith(csv_expected_prefix):
                name = info.filename
                break
        if name is None:
            # fallback to any CSV
            for info in zf.infolist():
                if info.filename.endswith(".csv"):
                    name = info.filename
                    break
        if name is None:
            return pd.DataFrame()
        with zf.open(name) as f:
            cols = [
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "num_trades",
                "taker_buy_base_volume", "taker_buy_quote_volume", "ignore",
            ]
            df = pd.read_csv(f, header=None, names=cols)
            return df


def fetch_klines_vision(symbol: str, interval: str, start_dt: datetime, end_dt: datetime) -> pd.DataFrame:
    """Fetch klines from Binance Vision monthly zip archives for [start_dt, end_dt]."""
    frames: List[pd.DataFrame] = []
    for year, month in _iter_months(start_dt, end_dt):
        url = _monthly_zip_url(symbol, interval, year, month)
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 404:
                continue
            r.raise_for_status()
        except requests.RequestException:
            continue

        csv_prefix = f"{symbol}-{interval}-{year}-{month:02d}"
        try:
            df_month = _read_month_csv_from_zip_bytes(r.content, csv_prefix)
        except zipfile.BadZipFile:
            continue
        if df_month is None or df_month.empty:
            continue
        frames.append(df_month)

    if not frames:
        return pd.DataFrame(columns=["open_time","open","high","low","close","volume","close_time"]).astype({
            "open_time": "int64",
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "float64",
            "close_time": "int64",
        })

    df = pd.concat(frames, ignore_index=True)
    # Basic normalization and filtering
    df = df[["open_time","open","high","low","close","volume","close_time"]].copy()
    df["open_time"] = pd.to_numeric(df["open_time"], errors="coerce").astype("int64")
    df["close_time"] = pd.to_numeric(df["close_time"], errors="coerce").astype("int64")
    for col in ["open","high","low","close","volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Normalize timestamp units: some archives use microseconds
    if df["open_time"].max() > 10**13:
        df["open_time"] = (df["open_time"] // 1000).astype("int64")
    if df["close_time"].max() > 10**13:
        df["close_time"] = (df["close_time"] // 1000).astype("int64")

    df = df.dropna().drop_duplicates(subset=["open_time"]).sort_values("open_time").reset_index(drop=True)

    start_ms = int(start_dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ms = int(end_dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
    df = df[(df["open_time"] >= start_ms) & (df["open_time"] <= end_ms)].reset_index(drop=True)
    return df


def fetch_klines_vision_cached(symbol: str, interval: str, start_dt: datetime, end_dt: datetime, cache_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(cache_path)
    except FileNotFoundError:
        pass
    df = fetch_klines_vision(symbol, interval, start_dt, end_dt)
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df
