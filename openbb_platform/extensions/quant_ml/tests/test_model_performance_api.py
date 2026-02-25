"""Tests for model performance payload enrichment."""

from __future__ import annotations

from pathlib import Path

from openbb_quant_ml.service import pipeline
from openbb_quant_ml.service.storage import save_json


def test_get_model_performance_includes_backend_fields(
    monkeypatch, tmp_path: Path
) -> None:
    run_id = "run-perf-1"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    save_json(
        run_dir / "metrics_lgbm_ranker.json",
        {
            "model_name": "lgbm_ranker",
            "metrics": {
                "train_ic": 0.04,
                "val_ic": 0.03,
                "ndcg": {"ndcg_10": 0.62},
                "hit_rate": 0.57,
            },
            "model_meta": {
                "backend": "stacked_v1",
                "primary_backend": "lightgbm",
                "stacked_v1": True,
            },
        },
    )
    save_json(
        run_dir / "backtest_lgbm_ranker.json",
        {
            "metrics": {
                "sharpe": 0.8,
                "max_drawdown": -0.19,
                "turnover": 0.42,
            }
        },
    )

    monkeypatch.setattr(pipeline, "get_run_dir", lambda rid: run_dir)

    payload = pipeline.get_model_performance(run_id=run_id)
    assert payload.run_id == run_id
    assert len(payload.models) == 1
    item = payload.models[0]
    assert item.model_name == "lgbm_ranker"
    assert item.backend == "stacked_v1"
    assert item.primary_backend == "lightgbm"
    assert item.stacked_v1 is True
