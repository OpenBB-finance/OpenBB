"""Portfolio current endpoint logic tests."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from openbb_quant_ml.service import pipeline


def test_portfolio_current_aggregates_weights_and_maps_other(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(pipeline, "_ensure_run_completed", lambda run_id, **_: None)
    monkeypatch.setattr(
        pipeline,
        "_load_backtest_payload",
        lambda run_id, model_name="lgbm_ranker": {
            "period_weights": [
                {
                    "date": "2026-02-01",
                    "weights": {"CASH": 0.55, "XLK": 0.2, "XLF": 0.1, "UNKNOWN": 0.05},
                }
            ],
            "constraints": {
                "max_weight": 0.2,
                "long_only": True,
                "risk_aversion": 3.0,
                "lookback_days": 126,
            },
            "effective_constraints": {
                "max_weight_requested": 0.2,
                "max_weight_applied": 0.1,
                "max_weight": 0.1,
                "long_only": True,
                "risk_aversion": 3.0,
                "lookback_days": 126.0,
            },
            "cost_bps": 10.0,
        },
    )
    monkeypatch.setattr(
        pipeline,
        "get_symbol_metadata_map",
        lambda: {
            "XLK": {
                "symbol": "XLK",
                "name": "Technology Select Sector SPDR",
                "market": "US",
                "sector_l1": "Technology",
                "category_l2": "us_sector_etf",
                "category": "us_sector_etf",
            },
            "XLF": {
                "symbol": "XLF",
                "name": "Financial Select Sector SPDR",
                "market": "US",
                "sector_l1": "Financial",
                "category_l2": "us_sector_etf",
                "category": "us_sector_etf",
            },
        },
    )

    payload = pipeline.get_portfolio_current("run-1", model_name="lgbm_ranker")
    assert payload.as_of_date == "2026-02-01"
    assert len(payload.symbol_weights) == 4
    assert len(payload.asset_class_weights) >= 1
    total = sum(item.weight for item in payload.asset_class_weights)
    assert math.isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6)
    categories = {item.category for item in payload.asset_class_weights}
    assert "other" in categories
    assert len(payload.asset_class_weights_l1) >= 1
    xlk_row = next(item for item in payload.symbol_weights if item.symbol == "XLK")
    assert xlk_row.name == "Technology Select Sector SPDR"
    assert xlk_row.market == "US"
    assert xlk_row.sector_l1 == "Technology"
    assert xlk_row.category_l2 == "us_sector_etf"
    cash_row = next(item for item in payload.symbol_weights if item.symbol == "CASH")
    assert cash_row.name == "Cash Buffer"
    assert cash_row.category_l2 == "cash_proxy"
    assert len(payload.rationale.summary_lines) == 3


def test_portfolio_current_empty_period_weights(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pipeline, "_ensure_run_completed", lambda run_id, **_: None)
    monkeypatch.setattr(
        pipeline,
        "_load_backtest_payload",
        lambda run_id, model_name="lgbm_ranker": {
            "period_weights": [],
            "constraints": {
                "max_weight": 0.2,
                "long_only": True,
                "risk_aversion": 3.0,
                "lookback_days": 126,
            },
            "cost_bps": 10.0,
        },
    )

    payload = pipeline.get_portfolio_current("run-2", model_name="lgbm_ranker")
    assert payload.total_weight == 0.0
    assert payload.symbol_weights == []
    assert payload.asset_class_weights == []
    assert payload.asset_class_weights_l1 == []
    assert len(payload.rationale.summary_lines) == 3


def test_portfolio_current_requires_backtest(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pipeline, "_ensure_run_completed", lambda run_id, **_: None)

    def _raise(*_args, **_kwargs):
        raise ValueError("missing")

    monkeypatch.setattr(pipeline, "_load_backtest_payload", _raise)

    with pytest.raises(ValueError, match="Run backtest first"):
        pipeline.get_portfolio_current("run-3", model_name="lgbm_ranker")


def test_get_run_restores_from_artifacts(monkeypatch: pytest.MonkeyPatch, tmp_path):
    run_dir = tmp_path / "run-restore"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics_lgbm_ranker.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(pipeline, "get_run_state_dict", lambda run_id: None)
    monkeypatch.setattr(pipeline, "get_run_dir", lambda run_id: run_dir)

    payload = pipeline.get_run("run-restore")
    assert payload.run_id == "run-restore"
    assert payload.status == "completed"
    assert payload.progress == 95
    assert payload.stage == "training_completed"


def test_get_run_restores_config_only_as_queued(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    run_dir = tmp_path / "run-config-only"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(pipeline, "get_run_state_dict", lambda run_id: None)
    monkeypatch.setattr(pipeline, "get_run_dir", lambda run_id: run_dir)

    payload = pipeline.get_run("run-config-only")
    assert payload.run_id == "run-config-only"
    assert payload.status == "queued"
    assert payload.progress == 5
    assert payload.stage == "configured"


def test_get_model_regime_avoids_index_mismatch(monkeypatch: pytest.MonkeyPatch):
    dates = pd.date_range("2025-01-01", periods=20, freq="B")
    backtest_payload = {
        "equity_curve": [
            {
                "date": date_value.date().isoformat(),
                "daily_return": float(idx) / 1000.0,
                "equity": 100.0 + float(idx),
            }
            for idx, date_value in enumerate(dates, start=1)
        ]
    }
    close_panel = pd.DataFrame(
        {"SPY": np.linspace(100.0, 120.0, len(dates))}, index=dates
    )

    monkeypatch.setattr(
        pipeline,
        "_load_backtest_payload",
        lambda run_id, model_name="lgbm_ranker": backtest_payload,
    )
    monkeypatch.setattr(pipeline, "_load_close_panel", lambda run_id: close_panel)

    payload = pipeline.get_model_regime("run-regime", model_name="lgbm_ranker")
    assert isinstance(payload.regimes, dict)


def test_get_run_stale_running_timeout(monkeypatch: pytest.MonkeyPatch):
    state = {
        "run_id": "run-stale",
        "status": "running",
        "progress": 40,
        "stage": "training_ranker",
        "created_at": "2025-01-01T00:00:00+00:00",
        "updated_at": "2025-01-01T00:00:00+00:00",
        "logs_tail": ["still running"],
        "error": None,
    }

    def _get_state(run_id: str):
        return dict(state)

    def _update(run_id: str, **kwargs):
        state.update(kwargs)
        state["updated_at"] = "2026-01-01T00:00:00+00:00"

    monkeypatch.setattr(pipeline, "get_run_state_dict", _get_state)
    monkeypatch.setattr(pipeline, "_run_has_completion_artifacts", lambda run_id: False)
    monkeypatch.setattr(pipeline, "update_run", _update)
    monkeypatch.setattr(pipeline, "append_log", lambda *args, **kwargs: None)

    payload = pipeline.get_run("run-stale")
    assert payload.status == "failed"
    assert payload.stage == "stale_run_timeout"
