"""Incremental inference helper tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from openbb_quant_ml.service import inference as inf


def test_upsert_predictions_skips_when_latest_already_present(tmp_path: Path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir(parents=True, exist_ok=True)
    existing = pd.DataFrame(
        [
            {
                "date": "2026-02-19",
                "symbol": "AAPL",
                "predicted_return": 0.01,
                "score": 0.3,
                "label": 3,
            }
        ]
    )
    existing.to_parquet(run_dir / "predictions_lgbm_ranker.parquet", index=False)

    scored_latest = existing.copy()
    merged, upserted_rows, changed = inf._upsert_predictions(
        run_dir, "lgbm_ranker", scored_latest
    )
    assert len(merged) == 1
    assert upserted_rows == 0
    assert changed is False


def test_write_market_data_artifact_merges_existing_rows(tmp_path: Path):
    run_dir = tmp_path / "run-2"
    run_dir.mkdir(parents=True, exist_ok=True)
    existing = pd.DataFrame(
        [
            {"date": "2026-02-18", "symbol": "AAPL", "open": 100.0, "close": 101.0},
        ]
    )
    existing.to_parquet(run_dir / "market_data.parquet", index=False)

    datasets = {
        "AAPL": pd.DataFrame(
            [
                {"date": "2026-02-19", "open": 101.0, "close": 102.0},
            ]
        )
    }
    inf._write_market_data_artifact(run_dir, datasets)
    merged = pd.read_parquet(run_dir / "market_data.parquet")
    assert len(merged) == 2
