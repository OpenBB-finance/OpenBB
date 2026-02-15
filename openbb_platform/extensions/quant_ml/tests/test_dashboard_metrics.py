"""Dashboard metrics service tests."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from openbb_quant_ml.service import dashboard_metrics as dm


def _build_test_run(tmp_path: Path, run_id: str = "run-1") -> Path:
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(7)
    dates = pd.date_range("2024-01-01", periods=280, freq="B")
    symbols = ["SPY", "QQQ", "MTUM", "VLUE", "USMV", "IWM", "TLT", "XLK", "XLF"]

    close_panel = pd.DataFrame(index=dates, columns=symbols, dtype=float)
    for symbol in symbols:
        returns = rng.normal(0.0004, 0.01, len(dates))
        close_panel[symbol] = 100 * np.cumprod(1 + returns)

    market_long = (
        close_panel.reset_index()
        .rename(columns={"index": "date"})
        .melt(id_vars=["date"], var_name="symbol", value_name="close")
    )
    market_long.to_parquet(run_dir / "market_data.parquet", index=False)

    prediction_symbols = ["XLK", "XLF", "TLT", "QQQ"]
    prediction_rows: list[dict[str, object]] = []
    for date_value in dates[-180:]:
        for symbol in prediction_symbols:
            pred = rng.normal(0.0007, 0.01)
            target = pred + rng.normal(0, 0.01)
            prediction_rows.append(
                {
                    "date": date_value,
                    "symbol": symbol,
                    "predicted_return": float(pred),
                    "target_return": float(target),
                    "predicted_xgb": float(pred + rng.normal(0, 0.002)),
                    "predicted_lstm": float(pred + rng.normal(0, 0.002)),
                }
            )
    predictions = pd.DataFrame(prediction_rows)
    predictions.to_parquet(run_dir / "predictions_lgbm_ranker.parquet", index=False)
    predictions.to_parquet(run_dir / "predictions.parquet", index=False)

    strategy_returns = rng.normal(0.0005, 0.009, len(dates))
    equity = 100 * np.cumprod(1 + strategy_returns)
    equity_curve = [
        {
            "date": pd.Timestamp(date_value).date().isoformat(),
            "daily_return": float(ret),
            "equity": float(level),
        }
        for date_value, ret, level in zip(dates, strategy_returns, equity, strict=False)
    ]

    rebalance_dates = pd.date_range(dates[0], dates[-1], freq="BMS")
    period_weights = []
    for date_value in rebalance_dates:
        period_weights.append(
            {
                "date": pd.Timestamp(date_value).date().isoformat(),
                "weights": {"XLK": 0.4, "XLF": 0.35, "TLT": 0.25, "UNKNOWN": 0.05},
            }
        )

    backtest_payload = {
        "run_id": run_id,
        "model_name": "lgbm_ranker",
        "start_date": "2024-01-01",
        "end_date": "2025-01-31",
        "benchmark_symbol": "SPY",
        "metrics": {
            "cagr": 0.12,
            "sharpe": 1.1,
            "max_drawdown": -0.2,
            "volatility": 0.14,
            "turnover": 0.35,
        },
        "equity_curve": equity_curve,
        "period_weights": period_weights,
        "constraints": {"max_weight": 0.4, "long_only": True, "risk_aversion": 3.0, "lookback_days": 126},
        "cost_bps": 10.0,
    }
    dm.save_json(run_dir / "backtest_lgbm_ranker.json", backtest_payload)
    dm.save_json(run_dir / "backtest.json", backtest_payload)

    dm.save_json(
        run_dir / "config.json",
        {
            "request": {
                "symbols": symbols + prediction_symbols,
            }
        },
    )
    dm.save_json(run_dir / "metrics_lgbm_ranker.json", {"metrics": {"val_ic": 0.05}})

    return run_dir


def _patch_run(monkeypatch: pytest.MonkeyPatch, run_dir: Path, run_id: str = "run-1") -> None:
    monkeypatch.setattr(dm, "get_run_dir", lambda rid: run_dir if rid == run_id else run_dir.parent / rid)
    monkeypatch.setattr(dm, "_has_run_dir", lambda rid: rid == run_id)
    monkeypatch.setattr(dm, "get_latest_run_id", lambda: run_id)
    monkeypatch.setattr(
        dm,
        "load_universe_config",
        lambda: {
            "assets": [
                {"symbol": "XLK", "category": "us_sector_etf"},
                {"symbol": "XLF", "category": "us_sector_etf"},
                {"symbol": "TLT", "category": "bond_etf"},
                {"symbol": "QQQ", "category": "us_tech_etf"},
            ]
        },
    )


def test_dashboard_health_payload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = _build_test_run(tmp_path)
    _patch_run(monkeypatch, run_dir)

    payload = dm.get_dashboard_health(run_id="run-1", model_name="lgbm_ranker")
    assert payload.status == "ok"
    assert payload.resolved_run_id == "run-1"
    assert payload.data_timestamp is not None
    assert payload.universe_size > 0
    assert payload.gross_exposure > 0
    assert payload.workflow_state.run_status in {"queued", "running", "completed", "failed", "unknown"}
    assert payload.workflow_state.artifacts_ready.predictions is True
    assert payload.workflow_state.artifacts_ready.backtest is True
    assert set(payload.strategy_health.keys()) == {
        "signal_dispersion",
        "crowding_risk_proxy",
        "market_correlation",
        "regime_mismatch_risk",
        "prediction_confidence",
    }


def test_performance_rolling_payload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = _build_test_run(tmp_path)
    _patch_run(monkeypatch, run_dir)

    payload = dm.get_performance_rolling("run-1", "lgbm_ranker")
    assert payload.status == "ok"
    assert len(payload.cumulative_return) > 50
    assert len(payload.rolling_sharpe_3m) > 20
    assert len(payload.rolling_ic_3m) > 0
    assert len(payload.turnover_ts) > 0
    assert len(payload.exposure_ts) > 0


def test_portfolio_exposure_and_risk(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = _build_test_run(tmp_path)
    _patch_run(monkeypatch, run_dir)

    exposure = dm.get_portfolio_exposure("run-1", "lgbm_ranker")
    assert exposure.status == "ok"
    assert len(exposure.sector_exposure) >= 1
    sector_sum = sum(item.weight for item in exposure.sector_exposure)
    assert math.isclose(sector_sum, 1.0, rel_tol=1e-5, abs_tol=1e-5)
    assert "momentum" in exposure.factor_exposure
    assert len(exposure.top10_long) > 0

    risk = dm.get_portfolio_risk("run-1", "lgbm_ranker")
    assert risk.status == "ok"
    assert risk.vol_ex_ante >= 0.0
    assert len(risk.position_risk_contrib_top5) <= 5
    assert len(risk.worst5_positions) <= 5


def test_ic_decay_and_prediction_distribution(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = _build_test_run(tmp_path)
    _patch_run(monkeypatch, run_dir)

    ic_decay = dm.get_model_ic_decay("run-1", "lgbm_ranker", max_horizon=20)
    assert ic_decay.status == "ok"
    assert len(ic_decay.ic_decay) == 20
    assert ic_decay.ic_decay[0]["horizon"] == 1
    assert ic_decay.ic_decay[-1]["horizon"] == 20

    dist = dm.get_prediction_distribution("run-1", "lgbm_ranker", bins=20)
    assert dist.status == "ok"
    assert len(dist.histogram) == 20
    assert len(dist.decile_spread_ts) > 0


def test_regime_and_alerts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = _build_test_run(tmp_path)
    _patch_run(monkeypatch, run_dir)

    regime_current = dm.get_regime_current("run-1", "lgbm_ranker")
    assert regime_current.status == "ok"
    assert regime_current.trend_regime in {"bull", "bear", "sideways"}
    assert regime_current.vol_regime in {"low", "mid", "high"}

    regime_history = dm.get_regime_history("run-1", "lgbm_ranker")
    assert regime_history.status == "ok"
    assert len(regime_history.history) > 100
    assert "transition_rate" in regime_history.regime_transition_stats

    current_alerts = dm.refresh_alerts_for_run("run-1", "lgbm_ranker")
    assert any(item.rule_id == "maxdd_over_15pct" for item in current_alerts.alerts)

    history_alerts = dm.get_alerts_history("run-1", "lgbm_ranker", limit=50)
    assert len(history_alerts.alerts) >= 1

    shap_payload = dm.get_model_shap("run-1", "lgbm_ranker")
    assert shap_payload.status == "insufficient_data"


def test_health_insufficient_when_predictions_and_backtest_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_id = "run-empty"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    dm.save_json(run_dir / "config.json", {"request": {"symbols": ["SPY", "QQQ"]}})

    monkeypatch.setattr(dm, "get_run_dir", lambda rid: run_dir if rid == run_id else run_dir.parent / rid)
    monkeypatch.setattr(dm, "_has_run_dir", lambda rid: rid == run_id)
    monkeypatch.setattr(dm, "get_latest_run_id", lambda: run_id)
    monkeypatch.setattr(dm, "read_registry", lambda: {"runs": {}})

    payload = dm.get_dashboard_health(run_id=run_id, model_name="lgbm_ranker")
    assert payload.status == "insufficient_data"
    assert payload.workflow_state.run_status in {"queued", "unknown"}
    assert payload.workflow_state.artifacts_ready.predictions is False
    assert payload.workflow_state.artifacts_ready.backtest is False


def test_health_marks_stale_running(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_dir = tmp_path / "run-stale"
    run_dir.mkdir(parents=True, exist_ok=True)
    dm.save_json(run_dir / "config.json", {"request": {"symbols": ["XLK", "XLF"]}})
    stale_updated_at = "2025-01-01T00:00:00+00:00"

    monkeypatch.setattr(dm, "get_run_dir", lambda rid: run_dir if rid == "run-stale" else run_dir.parent / rid)
    monkeypatch.setattr(dm, "_has_run_dir", lambda rid: rid == "run-stale")
    monkeypatch.setattr(dm, "get_latest_run_id", lambda: "run-stale")
    monkeypatch.setattr(
        dm,
        "read_registry",
        lambda: {
            "runs": {
                "run-stale": {
                    "status": "running",
                    "progress": 35,
                    "stage": "training_ranker",
                    "updated_at": stale_updated_at,
                }
            }
        },
    )
    monkeypatch.setattr(
        dm,
        "load_universe_config",
        lambda: {
            "assets": [
                {"symbol": "XLK", "category": "us_sector_etf"},
                {"symbol": "XLF", "category": "us_sector_etf"},
                {"symbol": "TLT", "category": "bond_etf"},
            ]
        },
    )

    payload = dm.get_dashboard_health(run_id="run-stale", model_name="lgbm_ranker")
    assert payload.workflow_state.run_status == "failed"
    assert payload.workflow_state.run_stage == "stale_run_timeout"
