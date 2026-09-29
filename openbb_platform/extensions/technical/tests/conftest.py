"""Shared fixtures for the openbb-technical test suite."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="session")
def ohlcv_df() -> pd.DataFrame:
    """Return a deterministic OHLCV DataFrame indexed by daily dates.

    Used by helpers, router, and views tests. The values are a smooth
    monotone series so volatility / momentum / trend computations all
    produce non-NaN, finite results without per-test seeding.
    """
    periods = 99
    base = np.arange(1, periods + 1, dtype="float64")
    return pd.DataFrame(
        {
            "open": base,
            "high": base + 0.5,
            "low": base - 0.5,
            "close": base,
            "volume": base * 100,
        },
        index=pd.date_range("2021-01-01", periods=periods, freq="D", name="date"),
    )


@pytest.fixture(scope="session")
def ohlcv_records(ohlcv_df: pd.DataFrame) -> list[dict]:
    """List-of-dicts form of ``ohlcv_df`` for ``Data``-coercion router tests."""
    out = ohlcv_df.reset_index()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    return out.to_dict(orient="records")
