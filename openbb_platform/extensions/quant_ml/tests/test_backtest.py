"""Backtest tests."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from openbb_quant_ml.models import BacktestConstraints
from openbb_quant_ml.service.backtest import run_backtest


def test_backtest_constraints_are_respected():
    rng = np.random.default_rng(13)
    symbols = ["A", "B", "C", "D", "E", "F"]
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="B")

    price_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        returns = rng.normal(0.0005, 0.01, len(dates))
        price_panel[symbol] = 100 * np.cumprod(1 + returns)
        open_panel[symbol] = price_panel[symbol] * (1.0 - 0.001)

    pred_dates = pd.date_range("2024-01-01", "2024-06-30", freq="BMS")
    prediction_rows = []
    for d in pred_dates:
        for idx, symbol in enumerate(symbols):
            prediction_rows.append(
                {"date": d, "symbol": symbol, "predicted_return": float(0.01 - idx * 0.002)}
            )
    predictions = pd.DataFrame(prediction_rows)

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=price_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        constraints=BacktestConstraints(max_weight=0.2, long_only=True, risk_aversion=3.0, lookback_days=60),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )

    assert "cagr" in result.metrics
    assert "sharpe" in result.metrics
    assert "max_drawdown" in result.metrics
    assert "volatility" in result.metrics
    assert "turnover" in result.metrics
    assert len(result.equity_curve) > 0
    assert len(result.period_weights) > 0
    assert result.benchmark_symbol == "SPY"
    assert len(result.benchmark_curve) > 0
    assert abs(result.base_index - 100.0) < 1e-9
    assert abs(result.equity_curve[0]["equity"] - 100.0) < 1e-9
    assert abs(result.benchmark_curve[0]["benchmark"] - 100.0) < 1e-9

    for period in result.period_weights:
        weights = period["weights"]
        assert abs(sum(weights.values()) - 1.0) < 1e-6
        assert all(weight >= -1e-9 for weight in weights.values())
        assert all(weight <= 0.2 + 1e-6 for weight in weights.values())

    assert isinstance(result.consistency_checks.get("valid"), bool)
    assert len(result.cost_breakdown) > 0


def test_backtest_supports_long_short_mode():
    rng = np.random.default_rng(23)
    symbols = ["A", "B", "C", "D", "E", "F", "G", "H"]
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="B")

    price_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        returns = rng.normal(0.0003, 0.012, len(dates))
        price_panel[symbol] = 100 * np.cumprod(1 + returns)
        open_panel[symbol] = price_panel[symbol] * (1.0 - 0.0015)

    pred_dates = pd.date_range("2024-01-01", "2024-06-30", freq="BMS")
    prediction_rows = []
    base_scores = [0.03, 0.02, 0.01, 0.0, -0.01, -0.02, -0.03, -0.04]
    for d in pred_dates:
        for idx, symbol in enumerate(symbols):
            prediction_rows.append(
                {"date": d, "symbol": symbol, "predicted_return": float(base_scores[idx])}
            )
    predictions = pd.DataFrame(prediction_rows)

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=price_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        constraints=BacktestConstraints(max_weight=0.35, long_only=False, risk_aversion=1.5, lookback_days=60),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
        portfolio_mode="long_short",
        regime_policy="fixed",
    )

    assert len(result.period_weights) > 0
    has_negative_weight = any(any(weight < -1e-6 for weight in row["weights"].values()) for row in result.period_weights)
    assert has_negative_weight
    assert len(result.regime_mode_by_period) > 0


def test_backtest_execution_price_modes_change_outcome():
    dates = pd.date_range("2024-01-01", "2024-04-30", freq="B")
    symbols = ["A", "B", "C"]
    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    rng = np.random.default_rng(99)
    for symbol in symbols:
        base = 100 * np.cumprod(1 + rng.normal(0.0002, 0.01, len(dates)))
        close_panel[symbol] = base
        open_panel[symbol] = base * (1.0 - 0.003)

    pred_dates = pd.date_range("2024-01-01", "2024-04-30", freq="BMS")
    predictions = pd.DataFrame(
        [
            {"date": d, "symbol": symbol, "predicted_return": float(0.03 - i * 0.01)}
            for d in pred_dates
            for i, symbol in enumerate(symbols)
        ]
    )

    close_close = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 4, 30),
        constraints=BacktestConstraints(max_weight=0.5, long_only=True, risk_aversion=2.0, lookback_days=60),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="close",
        exit_price="close",
    )
    open_close = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 4, 30),
        constraints=BacktestConstraints(max_weight=0.5, long_only=True, risk_aversion=2.0, lookback_days=60),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )

    assert close_close.metrics["net_return"] != open_close.metrics["net_return"]
