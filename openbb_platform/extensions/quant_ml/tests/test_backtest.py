"""Backtest tests."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from openbb_quant_ml.models import BacktestConstraints
from openbb_quant_ml.service.backtest import _estimate_covariance, run_backtest
from openbb_quant_ml.service import portfolio_optimizer_v2 as optimizer_v2


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
                {
                    "date": d,
                    "symbol": symbol,
                    "predicted_return": float(0.01 - idx * 0.002),
                }
            )
    predictions = pd.DataFrame(prediction_rows)

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=price_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        constraints=BacktestConstraints(
            max_weight=0.2, long_only=True, risk_aversion=3.0, lookback_days=60
        ),
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
        assert "CASH" in weights
        risky_weights = {
            symbol: weight for symbol, weight in weights.items() if symbol != "CASH"
        }
        assert all(weight >= -1e-9 for weight in risky_weights.values())
        assert all(weight <= 0.04 + 1e-6 for weight in risky_weights.values())
    assert any(
        period["weights"].get("CASH", 0.0) > 0 for period in result.period_weights
    )
    assert result.cash_weight > 0.0
    assert result.effective_constraints.get("max_weight") == 0.04

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
                {
                    "date": d,
                    "symbol": symbol,
                    "predicted_return": float(base_scores[idx]),
                }
            )
    predictions = pd.DataFrame(prediction_rows)

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=price_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        constraints=BacktestConstraints(
            max_weight=0.35, long_only=False, risk_aversion=1.5, lookback_days=60
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
        portfolio_mode="long_short",
        regime_policy="fixed",
    )

    assert len(result.period_weights) > 0
    assert all(
        abs(weight) <= 0.04 + 1e-6
        for row in result.period_weights
        for symbol, weight in row["weights"].items()
        if symbol != "CASH"
    )
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
        constraints=BacktestConstraints(
            max_weight=0.5, long_only=True, risk_aversion=2.0, lookback_days=60
        ),
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
        constraints=BacktestConstraints(
            max_weight=0.5, long_only=True, risk_aversion=2.0, lookback_days=60
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )

    assert close_close.metrics["net_return"] != open_close.metrics["net_return"]


def test_backtest_cvar_mode_falls_back_to_mv(monkeypatch):
    rng = np.random.default_rng(33)
    symbols = ["A", "B", "C", "D", "E", "F"]
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="B")

    price_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        returns = rng.normal(0.0005, 0.01, len(dates))
        price_panel[symbol] = 100 * np.cumprod(1 + returns)
        open_panel[symbol] = price_panel[symbol] * 0.999

    pred_dates = pd.date_range("2024-01-01", "2024-06-30", freq="BMS")
    predictions = pd.DataFrame(
        [
            {"date": d, "symbol": symbol, "predicted_return": float(0.02 - i * 0.003)}
            for d in pred_dates
            for i, symbol in enumerate(symbols)
        ]
    )

    monkeypatch.setattr(
        optimizer_v2,
        "_solve_cvar_with_cvxpy",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("forced_cvar_fail")),
    )

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=price_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        constraints=BacktestConstraints(
            max_weight=0.2,
            long_only=True,
            risk_aversion=3.0,
            lookback_days=60,
            optimizer_mode="cvar",
            cvar_alpha=0.05,
            cvar_lambda=3.0,
            scenario_lookback_days=120,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )

    assert len(result.period_weights) > 0
    assert "cvar_95" in result.metrics
    assert any(
        "optimizer_fallback_mv" in item.get("binding_constraints", [])
        for item in result.rebalance_history_summary
    )


def test_backtest_mixed_mode_applies_dynamic_risk_budget():
    rng = np.random.default_rng(71)
    symbols = ["A", "B", "C", "D", "E", "F"]
    dates = pd.date_range("2024-01-01", "2024-09-30", freq="B")

    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        # Downward and volatile path to trigger mixed-mode risk scaling.
        returns = rng.normal(-0.0009, 0.02, len(dates))
        close_panel[symbol] = 120 * np.cumprod(1 + returns)
        open_panel[symbol] = close_panel[symbol] * 0.998

    pred_dates = pd.date_range("2024-01-01", "2024-09-30", freq="BMS")
    predictions = pd.DataFrame(
        [
            {"date": d, "symbol": symbol, "predicted_return": float(0.01 - i * 0.002)}
            for d in pred_dates
            for i, symbol in enumerate(symbols)
        ]
    )

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 9, 30),
        constraints=BacktestConstraints(
            max_weight=0.2, long_only=True, risk_aversion=3.0, lookback_days=60
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
        portfolio_mode="long_only",
        regime_policy="mixed",
    )

    assert result.effective_constraints.get("dynamic_risk_budget_mixed") is True
    assert result.effective_constraints.get("risk_budget_scale_avg", 1.0) <= 1.0
    assert result.effective_constraints.get("risk_budget_scale_min", 1.0) <= 1.0
    assert any(
        float(item.get("risk_budget_scale", 1.0)) < 0.999
        for item in result.rebalance_history_summary
    )


def test_covariance_methods_are_finite_and_psd_like():
    rng = np.random.default_rng(101)
    hist = pd.DataFrame(
        rng.normal(0.0, 0.01, size=(120, 5)),
        columns=["A", "B", "C", "D", "E"],
    )
    for method in ("sample", "ewma", "ledoit_wolf", "ewma_shrink"):
        cov = _estimate_covariance(
            hist_returns=hist,
            method=method,
            ewma_halflife=42,
            shrinkage=0.15,
        )
        assert cov.shape == (5, 5)
        assert np.isfinite(cov).all()
        assert np.allclose(cov, cov.T, atol=1e-10)
        eig = np.linalg.eigvalsh(cov)
        assert float(eig.min()) > -1e-6


def test_backtest_holding_period_cap_cash_and_cost_decomposition():
    rng = np.random.default_rng(202)
    symbols = ["A", "B", "C", "D"]
    dates = pd.date_range("2024-01-01", "2024-06-30", freq="B")

    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        r = rng.normal(0.0004, 0.012, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + r)
        open_panel[symbol] = close_panel[symbol] * 0.999

    pred_dates = pd.date_range("2024-01-01", "2024-06-30", freq="BMS")
    predictions = pd.DataFrame(
        [
            {"date": d, "symbol": symbol, "predicted_return": float(0.04 - i * 0.01)}
            for d in pred_dates
            for i, symbol in enumerate(symbols)
        ]
    )

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 30),
        constraints=BacktestConstraints(
            max_weight=0.3,
            long_only=True,
            risk_aversion=2.5,
            lookback_days=60,
            holding_period_days=0,
            commission_bps=8.0,
            half_spread_bps=1.0,
            impact_k=5.0,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )

    trading_days = pd.DataFrame(result.cost_breakdown)
    assert (trading_days["gross_return"].abs() < 1e-14).sum() > 5
    assert np.isclose(
        float(result.metrics["total_cost"]),
        float(result.metrics["total_commission"])
        + float(result.metrics["total_spread_cost"])
        + float(result.metrics["total_impact_cost"]),
        atol=1e-9,
    )
    assert "annual_turnover" in result.metrics
    assert "monthly_turnover" in result.metrics
    assert "sortino" in result.metrics


def test_backtest_leakage_guard_skips_rebalance_without_prior_predictions():
    rng = np.random.default_rng(303)
    symbols = ["A", "B", "C"]
    dates = pd.date_range("2024-01-01", "2024-03-29", freq="B")
    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        r = rng.normal(0.0002, 0.01, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + r)
        open_panel[symbol] = close_panel[symbol] * 0.999

    # Predictions begin later than initial rebalance date.
    predictions = pd.DataFrame(
        [
            {"date": pd.Timestamp("2024-02-01"), "symbol": symbol, "predicted_return": 0.01}
            for symbol in symbols
        ]
    )

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 29),
        constraints=BacktestConstraints(
            max_weight=0.3,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            leakage_guard=True,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )
    assert len(result.equity_curve) > 0
    assert result.metrics["net_return"] == result.metrics["net_return"]
