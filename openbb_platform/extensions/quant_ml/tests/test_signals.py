"""Signal generation tests."""

from __future__ import annotations

import numpy as np
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


def test_signal_postprocess_is_finite_and_rank_monotonic():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-04-30")] * 7,
            "symbol": list("ABCDEFG"),
            "predicted_return": [-0.04, -0.02, -0.01, 0.0, 0.01, 0.03, 0.05],
            "predicted_xgb": [-0.04, -0.02, -0.01, 0.0, 0.01, 0.03, 0.05],
            "predicted_lstm": [-0.04, -0.02, -0.01, 0.0, 0.01, 0.03, 0.05],
        }
    )
    _, signals = generate_signals(
        df,
        as_of_date=None,
        top_k=7,
        score_threshold=0.0,
        selection_mode="quantile",
        q_long=0.4,
        q_short=0.4,
        confidence_sizing_enabled=False,
    )
    assert np.isfinite(signals["z_score"].to_numpy()).all()
    corr = np.corrcoef(
        signals["predicted_return"].to_numpy(dtype=float),
        signals["z_score"].to_numpy(dtype=float),
    )[0, 1]
    assert corr > 0.95


def test_quantile_hysteresis_reduces_churn_for_existing_long():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-05-31")] * 6,
            "symbol": list("ABCDEF"),
            "predicted_return": [0.06, 0.025, 0.02, 0.0, -0.01, -0.03],
            "predicted_xgb": [0.06, 0.025, 0.02, 0.0, -0.01, -0.03],
            "predicted_lstm": [0.06, 0.025, 0.02, 0.0, -0.01, -0.03],
        }
    )
    prev_positions = {"A": "buy", "B": "buy"}
    prev_holds = {"A": 2, "B": 2}

    _, no_hys = generate_signals(
        df,
        as_of_date=None,
        top_k=6,
        score_threshold=0.0,
        selection_mode="quantile",
        use_hysteresis=False,
        q_long=0.1,
        q_short=0.2,
        prev_positions=prev_positions,
        prev_holding_periods=prev_holds,
        confidence_sizing_enabled=False,
    )
    _, with_hys = generate_signals(
        df,
        as_of_date=None,
        top_k=6,
        score_threshold=0.0,
        selection_mode="quantile",
        use_hysteresis=True,
        entry_q_long=0.1,
        exit_q_long=0.5,
        entry_q_short=0.2,
        exit_q_short=0.5,
        prev_positions=prev_positions,
        prev_holding_periods=prev_holds,
        confidence_sizing_enabled=False,
    )
    sides_no = dict(zip(no_hys["symbol"], no_hys["side"], strict=False))
    sides_hy = dict(zip(with_hys["symbol"], with_hys["side"], strict=False))
    assert sides_no.get("B") != "buy"
    assert sides_hy.get("B") == "buy"


def test_long_only_never_opens_new_short_but_can_exit():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-06-28")] * 4,
            "symbol": ["A", "B", "C", "D"],
            "predicted_return": [0.03, 0.01, -0.02, -0.04],
            "predicted_xgb": [0.03, 0.01, -0.02, -0.04],
            "predicted_lstm": [0.03, 0.01, -0.02, -0.04],
        }
    )
    _, no_prev = generate_signals(
        df,
        as_of_date=None,
        top_k=4,
        score_threshold=0.0,
        selection_mode="quantile",
        long_only=True,
        q_long=0.25,
        q_short=0.25,
        confidence_sizing_enabled=False,
    )
    assert "sell" not in set(no_prev["side"])

    _, with_prev = generate_signals(
        df,
        as_of_date=None,
        top_k=4,
        score_threshold=0.0,
        selection_mode="quantile",
        long_only=True,
        q_long=0.25,
        q_short=0.25,
        prev_positions={"D": "buy"},
        prev_holding_periods={"D": 2},
        confidence_sizing_enabled=False,
    )
    assert "sell" in set(with_prev["side"])


def test_liquidity_filter_graceful_skip_and_confidence_monotonicity():
    df = pd.DataFrame(
        {
            "date": [pd.Timestamp("2024-07-31")] * 3,
            "symbol": ["A", "B", "C"],
            "predicted_return": [0.02, 0.02, 0.02],
            "predicted_xgb": [0.02, 0.03, 0.10],
            "predicted_lstm": [0.02, 0.02, -0.10],
        }
    )
    _, signals = generate_signals(
        df,
        as_of_date=None,
        top_k=3,
        score_threshold=0.0,
        selection_mode="z_threshold",
        liquidity_filter_enabled=True,
        confidence_sizing_enabled=True,
        confidence_disagreement_scale=0.05,
    )
    reason_map = dict(zip(signals["symbol"], signals["reason_codes"], strict=False))
    assert all("liquidity_filter_skipped" in codes for codes in reason_map.values())

    conf_map = dict(zip(signals["symbol"], signals["confidence"], strict=False))
    assert conf_map["A"] >= conf_map["B"] >= conf_map["C"]
