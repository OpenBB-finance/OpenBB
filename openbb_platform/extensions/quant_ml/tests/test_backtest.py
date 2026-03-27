"""Backtest tests."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest
from openbb_quant_ml.models import BacktestConstraints, BacktestResponse
from openbb_quant_ml.service import portfolio_optimizer_v2 as optimizer_v2
from openbb_quant_ml.service.backtest import (
    _classify_bucket,
    _compute_defensive_floor,
    _estimate_covariance,
    _resolve_defensive_settings,
    _select_candidate_indices,
    run_backtest,
)
from openbb_quant_ml.service.portfolio_policy import get_policy_max_weight_cap
from openbb_quant_ml.service.universe_policy import get_universe_policy


def test_backtest_response_accepts_string_effective_constraints():
    payload = {
        "run_id": "run-1",
        "model_name": "lgbm_ranker",
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "benchmark_symbol": "SPY",
        "metrics": {
            "cagr": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "turnover": 0.0,
        },
        "equity_curve": [],
        "benchmark_curve": [],
        "period_weights": [],
        "effective_constraints": {
            "cov_method": "ewma_shrink",
            "max_weight": 0.03,
            "defensive_floor_mode": "regime",
        },
    }

    parsed = BacktestResponse.model_validate(payload)
    assert parsed.effective_constraints.get("cov_method") == "ewma_shrink"
    assert parsed.effective_constraints.get("defensive_floor_mode") == "regime"


def test_defensive_bucket_classification_and_floor_mapping():
    settings = _resolve_defensive_settings(
        get_universe_policy(),
        BacktestConstraints(defensive_bucket_enabled=True),
    )
    assert _classify_bucket("GOVT", {}, settings) == "defensive_core"
    assert _classify_bucket("HYG", {}, settings) == "risk"
    assert _classify_bucket("EMB", {}, settings) == "risk"
    assert _classify_bucket("VCLT", {}, settings) == "risk"
    assert _classify_bucket("LQD", {}, settings) == "defensive_credit"

    settings_no_vol_trigger = settings
    settings_no_vol_trigger.risk_off_vol_regimes = set()

    floor_low, is_risk_off_low = _compute_defensive_floor(
        trend_regime="sideways",
        vol_regime="low",
        drawdown=0.01,
        settings=settings_no_vol_trigger,
    )
    floor_mid, is_risk_off_mid = _compute_defensive_floor(
        trend_regime="sideways",
        vol_regime="mid",
        drawdown=0.01,
        settings=settings_no_vol_trigger,
    )
    floor_high, is_risk_off_high = _compute_defensive_floor(
        trend_regime="sideways",
        vol_regime="high",
        drawdown=0.01,
        settings=settings_no_vol_trigger,
    )
    floor_risk_off, is_risk_off = _compute_defensive_floor(
        trend_regime="bear",
        vol_regime="mid",
        drawdown=0.01,
        settings=settings_no_vol_trigger,
    )

    assert not is_risk_off_low and abs(floor_low - 0.25) < 1e-9
    assert not is_risk_off_mid and abs(floor_mid - 0.35) < 1e-9
    assert not is_risk_off_high and abs(floor_high - 0.45) < 1e-9
    assert is_risk_off and abs(floor_risk_off - 0.55) < 1e-9


def test_select_candidate_indices_preserves_existing_holdings():
    active_indices = list(range(10))
    mu = np.array([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0], dtype=float)
    current_weights = np.zeros(10, dtype=float)
    current_weights[9] = 0.05

    selected = _select_candidate_indices(
        active_indices,
        mu=mu,
        current_weights=current_weights,
        candidate_cap=5,
    )

    assert len(selected) == 5
    assert 9 in selected


def test_backtest_constraints_are_respected():
    hard_cap = get_policy_max_weight_cap()
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
    assert "calmar" in result.metrics
    assert "omega" in result.metrics
    assert "max_consecutive_loss_days" in result.metrics
    assert len(result.equity_curve) > 0
    assert isinstance(result.monthly_returns, list)
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
        assert all(weight <= hard_cap + 1e-6 for weight in risky_weights.values())
    assert any(
        period["weights"].get("CASH", 0.0) > 0 for period in result.period_weights
    )
    assert result.cash_weight > 0.0
    assert result.effective_constraints.get("max_weight") == hard_cap

    assert isinstance(result.consistency_checks.get("valid"), bool)
    assert len(result.cost_breakdown) > 0


def test_backtest_supports_long_short_mode():
    hard_cap = get_policy_max_weight_cap()
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
        abs(weight) <= hard_cap + 1e-6
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


def test_backtest_cvar_mode_falls_back_to_mv(monkeypatch, caplog):
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

    with caplog.at_level("WARNING", logger=optimizer_v2.__name__):
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
        "CVaR optimization failed; falling back to MV solver" in record.message
        for record in caplog.records
    )
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


def _build_defensive_test_panels(
    *,
    seed: int = 901,
    end_date: str = "2024-09-30",
    include_extended_defensive: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    symbols = [
        "GOVT",
        "IEF",
        "TLT",
        "SHY",
        "VGSH",
        "VGIT",
        "LQD",
        "VCIT",
        "SPY",
        "QQQ",
        "HYG",
        "EMB",
    ]
    if include_extended_defensive:
        symbols.extend(["TIP", "MBB", "SGOV", "TFLO"])

    rng = np.random.default_rng(seed)
    dates = pd.date_range("2024-01-01", end_date, freq="B")
    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        if symbol in {"SPY", "QQQ", "HYG", "EMB"}:
            drift, vol = 0.0006, 0.014
        else:
            drift, vol = 0.0002, 0.006
        ret = rng.normal(drift, vol, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + ret)
        open_panel[symbol] = close_panel[symbol] * 0.999

    pred_dates = pd.date_range("2024-01-01", end_date, freq="BMS")
    rows: list[dict[str, object]] = []
    ranked = {
        "GOVT": 0.016,
        "IEF": 0.014,
        "TLT": 0.013,
        "SHY": 0.012,
        "VGSH": 0.011,
        "VGIT": 0.010,
        "LQD": 0.009,
        "VCIT": 0.008,
        "SPY": 0.006,
        "QQQ": 0.005,
        "HYG": 0.004,
        "EMB": 0.003,
        "TIP": 0.010,
        "MBB": 0.009,
        "SGOV": 0.011,
        "TFLO": 0.010,
    }
    for d in pred_dates:
        for symbol in symbols:
            rows.append(
                {
                    "date": d,
                    "symbol": symbol,
                    "predicted_return": float(ranked.get(symbol, 0.0)),
                }
            )
    predictions = pd.DataFrame(rows)
    return predictions, open_panel, close_panel


def test_defensive_floor_feasible_with_fixed_floor():
    predictions, open_panel, close_panel = _build_defensive_test_panels(seed=902)
    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 9, 30),
        constraints=BacktestConstraints(
            max_weight=0.5,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            defensive_bucket_enabled=True,
            defensive_floor_mode="fixed",
            defensive_floor_fixed=0.25,
            defensive_postcheck_enabled=False,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )
    rows_with_floor = [
        row
        for row in result.rebalance_history_summary
        if row.get("defensive_floor_target") is not None
    ]
    assert rows_with_floor
    for row in rows_with_floor:
        assert float(row.get("defensive_weight_realized", 0.0)) >= float(
            row.get("defensive_floor_target", 0.0)
        ) - 1e-4


def test_defensive_floor_infeasible_is_logged():
    predictions, open_panel, close_panel = _build_defensive_test_panels(seed=903)
    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 9, 30),
        constraints=BacktestConstraints(
            max_weight=0.2,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            defensive_bucket_enabled=True,
            defensive_floor_mode="fixed",
            defensive_floor_fixed=0.70,
            defensive_postcheck_enabled=False,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )
    assert any(
        str(item.get("type", "")) == "defensive_floor_infeasible"
        for item in result.constraint_violations
    )


def test_defensive_postcheck_triggers_when_global_risk_is_tight():
    predictions, open_panel, close_panel = _build_defensive_test_panels(
        seed=904, include_extended_defensive=True
    )
    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 9, 30),
        constraints=BacktestConstraints(
            max_weight=0.5,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            defensive_bucket_enabled=True,
            defensive_floor_mode="fixed",
            defensive_floor_fixed=0.25,
            defensive_postcheck_enabled=True,
            defensive_postcheck_vol_limit=0.0001,
            defensive_postcheck_cvar_limit=0.01,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )
    assert any(
        int(row.get("postcheck_iterations", 0)) > 1
        for row in result.rebalance_history_summary
    )
    assert any(
        bool(row.get("postcheck_actions"))
        for row in result.rebalance_history_summary
    )


def test_defensive_bucket_can_be_disabled_with_constraint_flag():
    predictions, open_panel, close_panel = _build_defensive_test_panels(seed=905)
    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 9, 30),
        constraints=BacktestConstraints(
            max_weight=0.5,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            defensive_bucket_enabled=False,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
    )
    assert not any(
        "defensive_bucket_2stage" in row.get("binding_constraints", [])
        for row in result.rebalance_history_summary
    )


def test_backtest_turnover_limit_is_enforced():
    rng = np.random.default_rng(211)
    symbols = [f"S{i:02d}" for i in range(12)]
    dates = pd.date_range("2024-01-01", "2024-10-31", freq="B")

    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        returns = rng.normal(0.0004, 0.012, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + returns)
        open_panel[symbol] = close_panel[symbol] * 0.999

    pred_dates = pd.date_range("2024-01-01", "2024-10-31", freq="BMS")
    prediction_rows: list[dict[str, object]] = []
    base_scores = np.linspace(0.03, -0.03, len(symbols))
    for idx, d in enumerate(pred_dates):
        scores = base_scores if idx % 2 == 0 else base_scores[::-1]
        for score, symbol in zip(scores, symbols, strict=False):
            prediction_rows.append(
                {
                    "date": d,
                    "symbol": symbol,
                    "predicted_return": float(score),
                }
            )
    predictions = pd.DataFrame(prediction_rows)

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 10, 31),
        constraints=BacktestConstraints(
            max_weight=0.25,
            long_only=True,
            risk_aversion=3.0,
            lookback_days=60,
            turnover_limit=0.012,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        entry_price="next_open",
        exit_price="close",
        portfolio_mode="long_only",
        regime_policy="fixed",
    )

    history = result.rebalance_history_summary
    assert history
    assert all(float(row.get("turnover", 0.0)) <= 0.012001 for row in history)
    assert any("turnover_limit" in row.get("binding_constraints", []) for row in history)
    assert abs(float(result.effective_constraints.get("turnover_limit", 0.0)) - 0.012) < 1e-9


def test_covariance_methods_are_finite_and_psd_like():
    rng = np.random.default_rng(101)
    hist = pd.DataFrame(
        rng.normal(0.0, 0.01, size=(120, 5)),
        columns=["A", "B", "C", "D", "E"],
    )
    for method in ("sample", "ewma", "ledoit_wolf", "ewma_shrink", "stat_factor_pca"):
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


def _build_panels_for_optimizer_tests(
    *,
    start: str = "2024-01-01",
    end: str = "2024-05-31",
    symbols: list[str] | None = None,
    seed: int = 404,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if symbols is None:
        symbols = ["A", "B", "C", "D", "E", "F"]
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start, end, freq="B")
    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        ret = rng.normal(0.0004, 0.01, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + ret)
        open_panel[symbol] = close_panel[symbol] * 0.999
    pred_dates = pd.date_range(start, end, freq="BMS")
    predictions = pd.DataFrame(
        [
            {
                "date": d,
                "symbol": symbol,
                "predicted_return": float(0.02 - i * 0.003),
                "score": float(0.03 - i * 0.004),
            }
            for d in pred_dates
            for i, symbol in enumerate(symbols)
        ]
    )
    return predictions, open_panel, close_panel


def test_optimizer_mv_engine_auto_fallback(monkeypatch):
    predictions, open_panel, close_panel = _build_panels_for_optimizer_tests(seed=405)

    monkeypatch.setattr(
        optimizer_v2,
        "_solve_mv_with_cvxpy",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("forced_mv_fail")),
    )

    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 5, 31),
        constraints=BacktestConstraints(
            max_weight=0.3,
            long_only=True,
            risk_aversion=2.5,
            lookback_days=60,
            mv_optimizer_engine="auto",
            optimizer_strict=False,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
    )
    assert any(
        "optimizer_mv_fallback_slsqp" in row.get("binding_constraints", [])
        for row in result.rebalance_history_summary
    )


def test_optimizer_mv_engine_strict_raises(monkeypatch):
    predictions, open_panel, close_panel = _build_panels_for_optimizer_tests(seed=406)

    monkeypatch.setattr(
        optimizer_v2,
        "_solve_mv_with_cvxpy",
        lambda **kwargs: (_ for _ in ()).throw(ValueError("forced_mv_fail")),
    )

    with pytest.raises(ValueError, match="mv_cvxpy_failed"):
        run_backtest(
            predictions=predictions,
            open_panel=open_panel,
            close_panel=close_panel,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 5, 31),
            constraints=BacktestConstraints(
                max_weight=0.3,
                long_only=True,
                risk_aversion=2.5,
                lookback_days=60,
                mv_optimizer_engine="cvxpy",
                optimizer_strict=True,
            ),
            cost_bps=10.0,
            slippage_bps=2.0,
        )


def test_optimizer_country_cap_override_from_exposure_constraints():
    mu = np.array([0.10, 0.08], dtype=float)
    cov = np.array([[0.01, 0.0], [0.0, 0.01]], dtype=float)
    symbols = ["A", "B"]
    metadata = {
        "A": {"sector_l1": "core", "country": "US", "adv20_usd": 1e9},
        "B": {"sector_l1": "core", "country": "US", "adv20_usd": 1e9},
    }
    base_policy = {
        "portfolio_constraints": {
            "max_weight_per_stock": 0.6,
            "sector_cap": 1.0,
            "country_cap": 0.35,
        },
        "liquidity_constraints": {"max_adv_participation": 1.0},
        "risk_constraints": {"max_risk_contribution_per_stock": 1.0, "epsilon": 1e-9},
    }
    common_kwargs = {
        "mu": mu,
        "cov": cov,
        "symbols": symbols,
        "metadata_by_symbol": metadata,
        "risk_aversion": 1.0,
        "requested_max_weight": 0.6,
        "policy": base_policy,
        "optimizer_mode": "mv",
        "mv_optimizer_engine": "legacy_slsqp",
        "current_weights": np.zeros(2, dtype=float),
        "cost_params": {"commission_bps": 0.0, "half_spread_bps": 0.0, "impact_k": 0.0},
        "exposure_constraints": {
            "allow_short": False,
            "gross_exposure_max": 1.0,
            "net_exposure_min": 0.0,
            "net_exposure_max": 1.0,
            "sector_max_weight": 1.0,
        },
    }

    constrained = optimizer_v2.optimize_weights_v2(**common_kwargs)
    assert float(np.sum(constrained.weights)) <= 0.3501

    overridden = optimizer_v2.optimize_weights_v2(
        **{
            **common_kwargs,
            "exposure_constraints": {
                **common_kwargs["exposure_constraints"],
                "country_max_weight": 1.0,
            },
        }
    )
    assert float(np.sum(overridden.weights)) > 0.35


def test_backtest_mu_mapping_ic_vol_scaled():
    predictions, open_panel, close_panel = _build_panels_for_optimizer_tests(seed=407)
    result = run_backtest(
        predictions=predictions,
        open_panel=open_panel,
        close_panel=close_panel,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 5, 31),
        constraints=BacktestConstraints(
            max_weight=0.3,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            alpha_mapping_mode="ic_vol_scaled",
            ic_lookback_days=120,
            ic_ewma_halflife=30,
            ic_clip_min=-0.1,
            ic_clip_max=0.1,
            ic_fallback=0.02,
            alpha_ema_halflife_days=10,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
        mu_mapping="ic_vol_scaled",
    )
    assert result.effective_constraints.get("alpha_mapping_mode") == "ic_vol_scaled"
    assert result.effective_constraints.get("mu_mapping") == "ic_vol_scaled"
    assert any(row.get("ic_hat") is not None for row in result.rebalance_history_summary)


def test_no_trade_zone_trigger_logic_and_month_end_force():
    symbols = ["A", "B", "C", "D"]
    rng = np.random.default_rng(408)
    dates = pd.date_range("2024-01-01", "2024-03-29", freq="B")
    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    open_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        ret = rng.normal(0.0002, 0.008, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + ret)
        open_panel[symbol] = close_panel[symbol] * 0.999

    pred_dates = pd.date_range("2024-01-01", "2024-03-29", freq="BMS")
    predictions = pd.DataFrame(
        [
            {
                "date": d,
                "symbol": symbol,
                "predicted_return": 0.01,
                "score": 0.01,
            }
            for d in pred_dates
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
            max_weight=0.25,
            long_only=True,
            risk_aversion=2.0,
            lookback_days=60,
            trigger_rebalance_enabled=True,
            trigger_threshold_bps=5000.0,
            trigger_cost_multiplier=1.0,
        ),
        cost_bps=10.0,
        slippage_bps=2.0,
    )

    assert any(
        str(item.get("trigger_reason", "")) == "no_trade_zone"
        for item in result.rebalance_history_summary
    )
    assert any(
        bool(item.get("forced_rebalance"))
        and str(item.get("trigger_reason", "")) == "month_end_forced"
        for item in result.rebalance_history_summary
    )
