"""Tests for stacked ranker v1 path."""

from __future__ import annotations

import numpy as np
import pandas as pd

from openbb_quant_ml.models import RankerConfig, WalkForwardConfig
from openbb_quant_ml.service import ranker_modeling as rm


class _DummyModel:
    def __init__(self, scale: float):
        self._scale = float(scale)

    def predict(self, x_input):  # noqa: ANN001
        x = np.asarray(x_input, dtype=float)
        return (x[:, 0] * self._scale) + 0.01


def _build_frame() -> pd.DataFrame:
    rng = np.random.default_rng(17)
    dates = pd.date_range("2024-01-01", periods=220, freq="B")
    symbols = ["AAA", "BBB", "CCC", "DDD"]
    rows: list[dict[str, float | str | pd.Timestamp]] = []
    for date_value in dates:
        for idx, symbol in enumerate(symbols):
            f1 = float(0.1 * idx + rng.normal(0.0, 1.0))
            f2 = float(rng.normal(0.0, 1.0))
            target = float(0.25 * f1 + 0.1 * f2 + rng.normal(0.0, 0.02))
            rows.append(
                {
                    "date": date_value,
                    "symbol": symbol,
                    "close": 100.0 + idx,
                    "daily_return": 0.0,
                    "target_return": target,
                    "f1": f1,
                    "f2": f2,
                }
            )
    return pd.DataFrame(rows)


def test_ranker_stacking_v1_backend(monkeypatch):
    monkeypatch.setattr(
        rm,
        "_fit_ranker_model",
        lambda **kwargs: (_DummyModel(1.0), np.array([1.0, 0.7]), "lightgbm"),
    )
    monkeypatch.setattr(
        rm,
        "_fit_aux_xgb_regressor",
        lambda **kwargs: (_DummyModel(0.5), np.array([0.5, 0.2])),
    )

    frame = _build_frame()
    output = rm.train_ranker_models(
        feature_data=frame,
        feature_columns=["f1", "f2"],
        walk_forward=WalkForwardConfig(
            train_months=6,
            embargo_months=0,
            val_months=1,
            step_months=1,
            purging_mode="legacy_month_cutoff",
        ),
        ranker_config=RankerConfig(
            n_estimators=500,
            early_stopping_rounds=30,
            stacking_enabled=True,
            stacking_alpha=1.0,
        ),
        theta_grid=[0.8, 1.0, 1.2],
        horizon_days=1,
        backend="lightgbm",
    )

    assert output.inference_backend == "stacked_v1"
    assert output.model_meta.get("stacked_v1") is True
    assert not output.predictions.empty
    assert {"predicted_xgb", "predicted_lstm", "score", "predicted_return"}.issubset(
        set(output.predictions.columns)
    )
    x_input = frame[["f1", "f2"]].head(6).to_numpy(dtype=float)
    preds = output.inference_model.predict(x_input)
    assert isinstance(preds, np.ndarray)
    assert preds.shape[0] == 6
