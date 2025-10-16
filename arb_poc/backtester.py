from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import pandas as pd


@dataclass
class BacktestResult:
    initial_btc: float
    final_btc: float
    num_trades: int
    avg_edge: float
    median_edge: float
    total_return: float  # final/initial - 1


def run_backtest(opps: pd.DataFrame, min_edge: float = 0.001, initial_btc: float = 1.0, max_trades: Optional[int] = None) -> tuple[BacktestResult, pd.DataFrame]:
    """
    Execute a naive backtest that takes every opportunity where best_edge >= min_edge.
    Capital is fully cycled each time (ends back in BTC), compounding over time.
    """
    candidates = opps[opps["best_edge"] >= min_edge].copy()
    if max_trades is not None:
        candidates = candidates.iloc[:max_trades]

    capital = initial_btc
    trade_rows: List[Dict[str, Any]] = []

    for ts, row in candidates.iterrows():
        edge = float(row["best_edge"])  # e.g., 0.001 => 0.1%
        before = capital
        after = capital * (1.0 + edge)
        capital = after
        trade_rows.append({
            "timestamp": ts,
            "route": row["best_route"],
            "edge": edge,
            "capital_before": before,
            "capital_after": after,
        })

    trades_df = pd.DataFrame(trade_rows).set_index("timestamp") if trade_rows else pd.DataFrame(columns=["timestamp","route","edge","capital_before","capital_after"]).set_index("timestamp")

    if len(candidates) > 0:
        avg_edge = float(candidates["best_edge"].mean())
        median_edge = float(candidates["best_edge"].median())
    else:
        avg_edge = 0.0
        median_edge = 0.0

    result = BacktestResult(
        initial_btc=initial_btc,
        final_btc=capital,
        num_trades=len(candidates),
        avg_edge=avg_edge,
        median_edge=median_edge,
        total_return=(capital / initial_btc - 1.0) if initial_btc > 0 else 0.0,
    )
    return result, trades_df
