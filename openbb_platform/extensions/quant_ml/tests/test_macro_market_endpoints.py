"""Macro market ratio/correlation endpoint service tests."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from openbb_quant_ml.service import macro_service as ms


def test_market_ratio_and_rolling_corr(monkeypatch):
    idx = pd.date_range("2025-01-01", periods=120, freq="B")

    def _mock_market_series(symbol: str, start, end):  # noqa: ANN001
        if symbol.upper() == "GLD":
            values = 200.0 + np.linspace(0, 20, len(idx))
        else:
            values = 100.0 + np.linspace(0, 10, len(idx))
        return pd.Series(values, index=idx, dtype=float), "mock", None

    monkeypatch.setattr(ms, "get_market_series", _mock_market_series)

    ratio = ms.get_market_ratio_response(
        lhs="GLD",
        rhs="SPY",
        start=date(2025, 1, 1),
        end=date(2025, 6, 30),
        freq="D",
        fill="ffill",
    )
    assert ratio.status == "ok"
    assert len(ratio.data) > 20
    assert abs(ratio.data[0].value - 2.0) < 1e-6

    corr = ms.get_market_rolling_corr_response(
        x="GLD",
        y="SPY",
        window=20,
        start=date(2025, 1, 1),
        end=date(2025, 6, 30),
        freq="D",
        fill="ffill",
    )
    assert corr.status == "ok"
    assert len(corr.data) > 20
