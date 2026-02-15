"""Macro transform utility tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from openbb_quant_ml.service.macro_transforms import (
    apply_publish_lag,
    apply_transform,
    compute_stats,
    normalize_series,
    resample_series,
)


def _sample_monthly_series() -> pd.Series:
    idx = pd.date_range("2020-01-31", periods=36, freq="ME")
    values = np.linspace(100.0, 130.0, len(idx))
    return pd.Series(values, index=idx, dtype=float)


def test_normalize_and_resample():
    rows = [
        {"date": "2025-01-31", "value": 4.0},
        {"date": "2025-02-28", "value": 4.1},
        {"date": "2025-03-31", "value": 4.2},
    ]
    series = normalize_series(rows)
    assert len(series) == 3
    daily = resample_series(series, freq="D", fill="ffill")
    assert len(daily) >= 50
    assert float(daily.dropna().iloc[-1]) == 4.2


def test_transforms_and_stats():
    series = _sample_monthly_series()
    yoy = apply_transform(series, "yoy")
    zscore = apply_transform(series, "zscore")
    pct = apply_transform(series, "percentile_5y")
    assert yoy.dropna().shape[0] > 10
    assert zscore.dropna().shape[0] == series.shape[0]
    assert pct.dropna().shape[0] > 0
    stats = compute_stats(zscore)
    assert stats["last"] is not None
    assert stats["z"] is not None


def test_publish_lag():
    series = _sample_monthly_series().iloc[:3]
    lagged = apply_publish_lag(series, 30)
    assert lagged.index[0] > series.index[0]
