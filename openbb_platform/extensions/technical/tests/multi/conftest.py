"""Shared fixtures for the ``openbb_technical.multi`` tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel


@pytest.fixture(scope="module")
def multi_symbol_records() -> list:
    """Long-format ``list[Data]`` with 3 symbols x 300 daily bars.

    The series are independent geometric random walks so correlations are
    finite but non-trivial, and indicators have enough rows to warm up.
    """
    periods = 300
    rng = np.random.default_rng(42)
    dates = pd.date_range("2021-01-01", periods=periods, freq="D", name="date")
    frames: list[pd.DataFrame] = []
    for symbol, drift in [("AAA", 0.001), ("BBB", 0.0005), ("CCC", -0.0005)]:
        rets = rng.normal(loc=drift, scale=0.02, size=periods)
        close = 100.0 * np.exp(np.cumsum(rets))
        df = pd.DataFrame(
            {
                "date": dates,
                "symbol": symbol,
                "open": close * (1 + rng.normal(0, 0.001, periods)),
                "high": close * (1 + np.abs(rng.normal(0, 0.005, periods))),
                "low": close * (1 - np.abs(rng.normal(0, 0.005, periods))),
                "close": close,
                "volume": rng.integers(1_000_000, 5_000_000, periods).astype(float),
            }
        )
        frames.append(df)
    big = pd.concat(frames, ignore_index=True)
    return df_to_basemodel(big)


@pytest.fixture(scope="module")
def single_symbol_records(multi_symbol_records: list) -> list:
    """Single-symbol slice (AAA only) for compose/screen tests."""
    return [r for r in multi_symbol_records if r.symbol == "AAA"]
