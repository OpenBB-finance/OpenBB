"""Signal generation tests."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.service.signals import generate_signals


def test_signal_threshold_rule():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-01-31")] * 5,
            "symbol": ["A", "B", "C", "D", "E"],
            "predicted_return": [0.03, 0.015, 0.001, -0.01, -0.025],
            "predicted_xgb": [0.028, 0.012, 0.002, -0.008, -0.023],
            "predicted_lstm": [0.031, 0.014, 0.001, -0.012, -0.024],
        }
    )
    as_of, signals = generate_signals(df, as_of_date=None, top_k=5, score_threshold=0.0)
    assert as_of == "2024-01-31"
    sides = dict(zip(signals["symbol"], signals["side"], strict=False))
    assert sides["A"] == "buy"
    assert sides["E"] == "sell"
    assert set(signals.columns) >= {
        "symbol",
        "side",
        "predicted_return",
        "confidence",
        "reason_codes",
        "z_score",
    }


def test_signal_generation_from_ranker_like_payload():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-02-29")] * 4,
            "symbol": ["A", "B", "C", "D"],
            "predicted_return": [0.02, 0.01, -0.005, -0.015],
        }
    )
    as_of, signals = generate_signals(df, as_of_date=None, top_k=4, score_threshold=0.0)
    assert as_of == "2024-02-29"
    assert "predicted_xgb" in signals.columns
    assert "predicted_lstm" in signals.columns


def test_signal_balanced_long_short_selection():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-03-31")] * 8,
            "symbol": list("ABCDEFGH"),
            "predicted_return": [0.06, 0.04, 0.02, 0.01, -0.01, -0.02, -0.04, -0.06],
        }
    )
    _, signals = generate_signals(
        df,
        as_of_date=None,
        top_k=6,
        score_threshold=0.0,
        balanced_long_short=True,
    )
    sides = list(signals["side"].values)
    assert "buy" in sides
    assert "sell" in sides
