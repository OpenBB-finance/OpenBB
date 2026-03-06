"""Tests for backtest artifact cache hit path."""

from __future__ import annotations

from datetime import date

from openbb_quant_ml.models import BacktestConstraints, BacktestRequest
from openbb_quant_ml.service import pipeline
from openbb_quant_ml.service.storage import save_json


def _minimal_backtest_payload(run_id: str) -> dict:
    return {
        "run_id": run_id,
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
        "constraints": BacktestConstraints().model_dump(mode="json"),
        "cost_bps": 10.0,
        "slippage_bps": 2.0,
        "entry_price": "next_open",
        "exit_price": "close",
        "portfolio_mode": "long_only",
        "mu_mapping": "quantile_mean_return",
        "regime_policy": "mixed",
    }


def test_load_cached_backtest_response_matches_signature(tmp_path, monkeypatch) -> None:
    run_id = "run-cache-1"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pipeline, "get_run_dir", lambda _: run_dir)

    request = BacktestRequest(
        run_id=run_id,
        model_name="lgbm_ranker",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
        constraints=BacktestConstraints(),
    )
    payload = _minimal_backtest_payload(run_id)
    payload["request_signature"] = pipeline._build_backtest_request_signature(
        request, "lgbm_ranker"
    )
    save_json(run_dir / "backtest_lgbm_ranker.json", payload)

    cached = pipeline._load_cached_backtest_response(request, "lgbm_ranker")
    assert cached is not None
    assert cached.run_id == run_id


def test_load_cached_backtest_response_rejects_mismatch(tmp_path, monkeypatch) -> None:
    run_id = "run-cache-2"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(pipeline, "get_run_dir", lambda _: run_dir)

    request = BacktestRequest(
        run_id=run_id,
        model_name="lgbm_ranker",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 1, 31),
        constraints=BacktestConstraints(),
    )
    payload = _minimal_backtest_payload(run_id)
    payload["request_signature"] = {
        "run_id": run_id,
        "model_name": "lgbm_ranker",
        "start_date": "2025-02-01",
        "end_date": "2025-02-28",
    }
    save_json(run_dir / "backtest_lgbm_ranker.json", payload)

    cached = pipeline._load_cached_backtest_response(request, "lgbm_ranker")
    assert cached is None

