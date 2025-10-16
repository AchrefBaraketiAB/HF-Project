from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .data_utils import year_range_utc, load_three_markets, ensure_dir
from .strategy import compute_triangular_edges
from .backtester import run_backtest


SYMBOL_BNBUSDT = "BNBUSDT"
SYMBOL_BTCUSDT = "BTCUSDT"
SYMBOL_BNBBTC = "BNBBTC"


def parse_dt(value: str) -> datetime:
    # Accept formats: YYYY-MM-DD or full ISO
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid datetime format: {value}")


def cli() -> None:
    parser = argparse.ArgumentParser(description="Triangular arbitrage POC for BNB/BTC using USDT legs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="Fetch 1m klines for BNBUSDT, BTCUSDT, BNBBTC")
    f.add_argument("--start", type=parse_dt, help="Start datetime (UTC)")
    f.add_argument("--end", type=parse_dt, help="End datetime (UTC)")
    f.add_argument("--year", type=int, help="Year to fetch if start/end not provided")
    f.add_argument("--data-dir", type=str, default="data/raw", help="Directory to store raw CSVs")
    f.add_argument("--pause", type=float, default=0.1, help="Pause between API requests (seconds)")

    b = sub.add_parser("backtest", help="Compute opportunities and run backtest")
    b.add_argument("--start", type=parse_dt, help="Start datetime (UTC)")
    b.add_argument("--end", type=parse_dt, help="End datetime (UTC)")
    b.add_argument("--year", type=int, help="Year to backtest if start/end not provided")
    b.add_argument("--fee", type=float, default=0.001, help="Per-hop taker fee (e.g., 0.001 = 0.1%)")
    b.add_argument("--min-edge", type=float, default=0.001, help="Minimum edge to take a trade (e.g., 0.001 = 0.1%)")
    b.add_argument("--initial-btc", type=float, default=1.0, help="Initial BTC capital")
    b.add_argument("--max-trades", type=int, default=None, help="Cap number of trades (debug/demo)")
    b.add_argument("--data-dir", type=str, default="data/raw", help="Directory with raw CSVs")
    b.add_argument("--out-dir", type=str, default="data/outputs", help="Directory to write outputs")

    args = parser.parse_args()

    if args.cmd == "fetch":
        if args.start and args.end:
            start, end = args.start, args.end
        elif args.year:
            start, end = year_range_utc(args.year)
        else:
            now = datetime.now(timezone.utc)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)  # today
            end = now

        df = load_three_markets(SYMBOL_BNBUSDT, SYMBOL_BTCUSDT, SYMBOL_BNBBTC, start, end, data_dir=args.data_dir, request_pause_s=args.pause)
        print(f"Fetched and cached data: {len(df)} aligned minutes between {start} and {end}")

    elif args.cmd == "backtest":
        if args.start and args.end:
            start, end = args.start, args.end
        elif args.year:
            start, end = year_range_utc(args.year)
        else:
            now = datetime.now(timezone.utc)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now

        df = load_three_markets(SYMBOL_BNBUSDT, SYMBOL_BTCUSDT, SYMBOL_BNBBTC, start, end, data_dir=args.data_dir)
        opps = compute_triangular_edges(df, fee=args.fee)

        ensure_dir(args.out_dir)
        opps_path = Path(args.out_dir) / f"opportunities_{start.date()}_{end.date()}.csv"
        opps.to_csv(opps_path)

        result, trades = run_backtest(opps, min_edge=args.min_edge, initial_btc=args.initial_btc, max_trades=args.max_trades)
        trades_path = Path(args.out_dir) / f"trades_{start.date()}_{end.date()}.csv"
        trades.to_csv(trades_path)

        print("Backtest summary:")
        print({
            "initial_btc": result.initial_btc,
            "final_btc": result.final_btc,
            "num_trades": result.num_trades,
            "avg_edge": result.avg_edge,
            "median_edge": result.median_edge,
            "total_return": result.total_return,
            "opportunities_csv": str(opps_path),
            "trades_csv": str(trades_path),
        })


if __name__ == "__main__":
    cli()
