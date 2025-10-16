from __future__ import annotations

import pandas as pd


def compute_triangular_edges(df: pd.DataFrame, fee: float = 0.001) -> pd.DataFrame:
    """
    Compute triangular arbitrage profit factors for both directions using close prices.

    Route A (clockwise): BTC -> USDT -> BNB -> BTC
      1) Sell BTC for USDT at BTCUSDT
      2) Buy BNB with USDT at BNBUSDT
      3) Sell BNB for BTC at BNBBTC

    Route B (counter-clockwise): BTC -> BNB -> USDT -> BTC
      1) Buy BNB with BTC at BNBBTC
      2) Sell BNB for USDT at BNBUSDT
      3) Buy BTC with USDT at BTCUSDT

    fee is per trade (taker), multiplicative loss per hop: (1 - fee)
    """
    prices = df[["BNBUSDT_close", "BTCUSDT_close", "BNBBTC_close"]].astype("float64")

    f = 1.0 - fee

    # Route A
    # BTC -> USDT: multiply by BTCUSDT price
    # USDT -> BNB: divide by BNBUSDT price
    # BNB -> BTC: multiply by BNBBTC price
    route_a_factor = (prices["BTCUSDT_close"] * f) * (f / prices["BNBUSDT_close"]) * (prices["BNBBTC_close"] * f)

    # Route B
    # BTC -> BNB: divide by BNBBTC price
    # BNB -> USDT: multiply by BNBUSDT price
    # USDT -> BTC: divide by BTCUSDT price
    route_b_factor = (f / prices["BNBBTC_close"]) * (prices["BNBUSDT_close"] * f) * (f / prices["BTCUSDT_close"]) 

    out = df.copy()
    out["route_a_factor"] = route_a_factor
    out["route_b_factor"] = route_b_factor
    out["route_a_edge"] = out["route_a_factor"] - 1.0
    out["route_b_edge"] = out["route_b_factor"] - 1.0
    out["best_edge"] = out[["route_a_edge", "route_b_edge"]].max(axis=1)
    out["best_route"] = (out["route_a_edge"] >= out["route_b_edge"]).map({True: "A", False: "B"})
    return out
