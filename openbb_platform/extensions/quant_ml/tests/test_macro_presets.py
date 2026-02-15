"""Macro preset computation tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from openbb_quant_ml.service.macro_presets import get_copper_gold_preset_response


def test_copper_gold_preset_ratio_modes():
    idx = pd.date_range("2024-01-05", periods=30, freq="W-FRI")

    def resolver(symbol: str) -> pd.Series:
        key = symbol.upper()
        if key == "HG":
            return pd.Series(16.0, index=idx, dtype=float)
        if key == "GC":
            return pd.Series(2.0, index=idx, dtype=float)
        if key == "FRED:DGS10":
            return pd.Series(np.linspace(3.0, 2.0, len(idx)), index=idx, dtype=float)
        raise ValueError(symbol)

    simple = get_copper_gold_preset_response(
        resolver,
        freq="W",
        fill="ffill",
        scale=1000,
        adjust_units=False,
        include_corr=False,
    )
    adjusted = get_copper_gold_preset_response(
        resolver,
        freq="W",
        fill="ffill",
        scale=1000,
        adjust_units=True,
        include_corr=False,
    )
    assert simple.status == "ok"
    assert adjusted.status == "ok"
    simple_ratio = next(item for item in simple.series if item.id == "copper_gold_ratio")
    adjusted_ratio = next(item for item in adjusted.series if item.id == "copper_gold_ratio")
    assert abs(simple_ratio.data[0].value - 8000.0) < 1e-6
    assert abs(adjusted_ratio.data[0].value - (1000.0 / (2.0 * 0.911458))) < 1e-6
    assert abs(simple_ratio.data[0].value - adjusted_ratio.data[0].value) > 1.0


def test_copper_gold_preset_divergence_single_run():
    idx = pd.date_range("2023-01-06", periods=40, freq="W-FRI")

    def resolver(symbol: str) -> pd.Series:
        key = symbol.upper()
        if key == "HG":
            return pd.Series(np.linspace(10.0, 20.0, len(idx)), index=idx, dtype=float)
        if key == "GC":
            return pd.Series(1.0, index=idx, dtype=float)
        if key == "FRED:DGS10":
            return pd.Series(np.linspace(4.0, 1.0, len(idx)), index=idx, dtype=float)
        raise ValueError(symbol)

    payload = get_copper_gold_preset_response(
        resolver,
        freq="W",
        fill="ffill",
        include_corr=True,
        corr_window=12,
        slope_window=8,
        divergence_min_weeks=4,
    )
    assert payload.status == "ok"
    assert len(payload.series) >= 3
    assert any(item.id == "rolling_corr" for item in payload.series)
    assert len(payload.events) == 1
    assert payload.events[0].event_type == "ratio_up_yield_down"
