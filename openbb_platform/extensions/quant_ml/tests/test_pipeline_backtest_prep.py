"""Regression tests for backtest prediction preparation."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.service.pipeline import _prepare_predictions_for_backtest


def test_prepare_predictions_preserves_predicted_return_when_score_exists():
    frame = pd.DataFrame(
        {
            "date": ["2024-01-31", "2024-01-31"],
            "symbol": ["AAA", "BBB"],
            "predicted_return": [0.02, -0.01],
            "score": [2.0, -1.0],
        }
    )

    prepared = _prepare_predictions_for_backtest(frame)
    assert prepared["predicted_return"].tolist() == [0.02, -0.01]
    assert prepared["score"].tolist() == [2.0, -1.0]


def test_prepare_predictions_fills_missing_columns_bidirectionally():
    score_only = pd.DataFrame(
        {
            "date": ["2024-01-31"],
            "symbol": ["AAA"],
            "score": [0.75],
        }
    )
    pred_only = pd.DataFrame(
        {
            "date": ["2024-01-31"],
            "symbol": ["AAA"],
            "predicted_return": [0.015],
        }
    )

    score_prepared = _prepare_predictions_for_backtest(score_only)
    pred_prepared = _prepare_predictions_for_backtest(pred_only)

    assert float(score_prepared.loc[0, "predicted_return"]) == 0.75
    assert float(pred_prepared.loc[0, "score"]) == 0.015
