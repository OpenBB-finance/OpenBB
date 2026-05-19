"""Shared fixtures for the quantitative test suite."""

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

SEED = 42
N_ROWS = 250


@pytest.fixture(scope="session")
def prices_df() -> pd.DataFrame:
    """Build a deterministic OHLCV price series with a date column."""
    rng = np.random.default_rng(SEED)
    t = np.arange(N_ROWS)
    close = 100 + 0.1 * t + rng.normal(0, 1, N_ROWS).cumsum() * 0.5
    dates = pd.date_range("2022-01-03", periods=N_ROWS, freq="B")

    return pd.DataFrame(
        {
            "date": dates,
            "open": close + rng.normal(0, 0.3, N_ROWS),
            "high": close + np.abs(rng.normal(0.8, 0.3, N_ROWS)),
            "low": close - np.abs(rng.normal(0.8, 0.3, N_ROWS)),
            "close": close,
            "volume": (1e6 + rng.normal(0, 5e4, N_ROWS)).astype(float),
        }
    )


@pytest.fixture(scope="session")
def prices_data(prices_df) -> list:
    """Expose the price DataFrame as a ``list[Data]``."""
    return df_to_basemodel(prices_df)
