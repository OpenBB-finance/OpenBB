"""Regime transition detection tests."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.service.macro_regime import detect_regime_transitions


def test_detect_regime_transitions_flags_large_axis_moves() -> None:
    frame = pd.DataFrame(
        {
            "risk_on_score": [45.0, 62.0, 64.0],
            "inflation_score": [50.0, 49.0, 48.5],
            "growth_score": [51.0, 52.0, 53.0],
            "liquidity_score": [55.0, 56.0, 57.0],
            "credit_stress_score": [52.0, 53.0, 54.0],
        },
        index=pd.to_datetime(["2025-01-03", "2025-01-10", "2025-01-17"]),
    )

    transitions = detect_regime_transitions(frame, threshold=10.0)
    assert not transitions.empty
    first = transitions.iloc[0]
    assert first["axis"] == "risk_on_score"
    assert first["direction"] == "rising"
    assert abs(float(first["delta"]) - 17.0) < 1e-9
