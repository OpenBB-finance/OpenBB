"""Backtest extended statistics tests."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from openbb_quant_ml.models import BacktestConstraints
from openbb_quant_ml.service.backtest import run_backtest


def _panel(symbols: list[str], start: str, end: str, seed: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq="B")
    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        ret = rng.normal(0.0003, 0.011, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + ret)
        open_panel[symbol] = close_panel[symbol] * 0.999
    return open_panel, close_panel


def _predictions(symbols: list[str], start: str, end: str) -> pd.DataFrame:
    pred_dates = pd.date_range(start, end, freq="BMS")
    rows: list[dict[str, object]] = []
    for d in pred_dates:
        for idx, symbol in enumerate(symbols):
            rows.append(
                {
                    "date": d,
                    "symbol": symbol,
                    "predicted_return": float(0.02 - idx * 0.003),
                }
            )
    return pd.DataFrame(rows)


def test_backtest_response_contains_extended_stats_and_monthly_returns() -> None:
    symbols = ["SPY", "QQQ", "IWM", "EFA", "TLT", "GLD"]
    open_panel, close_panel = _panel(symbols, "2024-01-01", "2024-12-31", seed=41)
    predictions = _predictions(symbols, "2024-01-01", "2024-12-31")

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        constraints=BacktestConstraints(
            max_weight=0.2,
            long_only=True,
            risk_aversion=3.0,
            lookback_days=60,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )

    for key in ("sharpe", "sortino", "calmar", "omega", "max_consecutive_loss_days"):
        assert key in result.metrics
    assert isinstance(result.metrics["max_consecutive_loss_days"], int)
    assert isinstance(result.monthly_returns, list)
    assert len(result.monthly_returns) > 0
    for row in result.monthly_returns:
        assert {"year", "month", "return"} <= set(row.keys())
