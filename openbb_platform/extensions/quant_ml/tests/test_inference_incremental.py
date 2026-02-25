"""Incremental inference helper tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from openbb_quant_ml.models import DateRange, TrainRequest
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


def test_refresh_latest_ranker_predictions_forwards_market_workers(
    monkeypatch, tmp_path: Path
):
    run_dir = tmp_path / "run-3"
    run_dir.mkdir(parents=True, exist_ok=True)
    request = TrainRequest(
        symbols=["AAPL"],
        date_range=DateRange(
            start_date=date(2025, 1, 1),
            end_date=date(2026, 2, 22),
        ),
    )

    monkeypatch.setattr(inf, "get_run_dir", lambda run_id: run_dir)
    monkeypatch.setattr(inf, "_load_training_request", lambda _run_dir: request)

    captured: dict[str, object] = {}

    def _load_market_data(*args, **kwargs):  # noqa: ANN002, ANN003
        captured["max_workers"] = kwargs.get("max_workers")
        dataset = {
            "AAPL": pd.DataFrame(
                [
                    {
                        "date": "2026-02-21",
                        "open": 100.0,
                        "close": 101.0,
                        "volume": 1_000_000,
                    }
                ]
            )
        }
        return dataset, []

    monkeypatch.setattr(inf, "load_market_data", _load_market_data)

    def _build_feature_dataset(*args, **kwargs):  # noqa: ANN002, ANN003
        frame = pd.DataFrame(
            [
                {
                    "date": pd.Timestamp("2026-02-21"),
                    "symbol": "AAPL",
                    "close": 101.0,
                    "daily_return": 0.01,
                    "target_return": 0.01,
                    "f1": 1.0,
                }
            ]
        )
        return frame, ["f1"], []

    monkeypatch.setattr(inf, "build_feature_dataset", _build_feature_dataset)

    class _DummyModel:
        def predict(self, x):  # noqa: ANN001
            return np.full(shape=(len(x),), fill_value=0.2, dtype=float)

    monkeypatch.setattr(
        inf,
        "_load_ranker_model_artifacts",
        lambda _run_dir: (
            _DummyModel(),
            {
                "feature_columns": ["f1"],
                "label_return_map": {"0": 0.0, "1": 0.01, "2": 0.02, "3": 0.03},
                "label_return_fallback": 0.0,
            },
        ),
    )
    monkeypatch.setattr(
        inf,
        "_upsert_predictions",
        lambda *_args, **_kwargs: (pd.DataFrame([{"date": "2026-02-21"}]), 1, True),
    )
    monkeypatch.setattr(inf, "_write_market_data_artifact", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(inf, "save_json", lambda *_args, **_kwargs: None)

    payload = inf.refresh_latest_ranker_predictions(
        run_id="run-3",
        model_name="lgbm_ranker",
        max_workers=8,
    )

    assert payload["status"] == "ok"
    assert payload["latest_rows_upserted"] == 1
    assert captured["max_workers"] == 8


def test_score_latest_frame_uses_stacked_components():
    frame = pd.DataFrame(
        [
            {
                "date": pd.Timestamp("2026-02-21"),
                "symbol": "AAPL",
                "close": 101.0,
                "daily_return": 0.01,
                "target_return": 0.02,
                "f1": 1.0,
                "f2": 0.5,
            },
            {
                "date": pd.Timestamp("2026-02-21"),
                "symbol": "MSFT",
                "close": 99.0,
                "daily_return": -0.01,
                "target_return": -0.02,
                "f1": 0.2,
                "f2": -0.3,
            },
        ]
    )

    class _StackedDummy:
        def predict_components(self, x):  # noqa: ANN001
            x_arr = np.asarray(x, dtype=float)
            primary = x_arr[:, 0] + 0.1
            auxiliary = x_arr[:, 0] - 0.2
            combined = 0.7 * primary + 0.3 * auxiliary
            return {
                "primary_score": primary,
                "auxiliary_score": auxiliary,
                "combined_score": combined,
            }

        def predict(self, x):  # noqa: ANN001
            x_arr = np.asarray(x, dtype=float)
            return x_arr[:, 0]

    scored = inf._score_latest_frame(
        frame,
        model=_StackedDummy(),
        metadata={
            "feature_columns": ["f1", "f2"],
            "label_return_map": {"0": -0.02, "1": -0.01, "2": 0.0, "3": 0.01, "4": 0.02},
            "label_return_fallback": 0.0,
        },
    )

    assert "predicted_xgb" in scored.columns
    assert "predicted_lstm" in scored.columns
    assert not np.allclose(
        scored["predicted_xgb"].to_numpy(dtype=float),
        scored["score"].to_numpy(dtype=float),
    )
    assert not np.allclose(
        scored["predicted_lstm"].to_numpy(dtype=float),
        scored["score"].to_numpy(dtype=float),
    )
