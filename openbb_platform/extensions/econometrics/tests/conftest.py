"""Shared fixtures for the econometrics test suite."""

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_econometrics.utils import mock_multi_index_data

SEED = 42
N_ROWS = 120


@pytest.fixture(scope="session")
def timeseries_df() -> pd.DataFrame:
    """Build a smooth, slightly-noisy OHLCV timeseries DataFrame."""
    rng = np.random.default_rng(SEED)
    t = np.arange(N_ROWS)
    base = 100 + 0.5 * t + rng.normal(0, 2, N_ROWS).cumsum() * 0.3
    close = base + rng.normal(0, 1, N_ROWS)

    return pd.DataFrame(
        {
            "open": close + rng.normal(0, 0.5, N_ROWS),
            "high": close + np.abs(rng.normal(1, 0.5, N_ROWS)),
            "low": close - np.abs(rng.normal(1, 0.5, N_ROWS)),
            "close": close,
            "volume": (1e6 + rng.normal(0, 1e5, N_ROWS) + 5000 * t).astype(float),
        }
    )


@pytest.fixture(scope="session")
def timeseries_data(timeseries_df) -> list:
    """Expose the timeseries DataFrame as a ``list[Data]``."""
    return df_to_basemodel(timeseries_df)


@pytest.fixture(scope="session")
def symbol_df() -> pd.DataFrame:
    """Build a long-format DataFrame with a ``symbol`` column and >1 symbol."""
    rng = np.random.default_rng(SEED)
    rows = 30
    frames = []
    for sym in ("AAA", "BBB", "CCC"):
        close = 100 + rng.normal(0, 1, rows).cumsum()
        frames.append(pd.DataFrame({"symbol": sym, "close": close}))
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="session")
def symbol_data(symbol_df) -> list:
    """Expose the multi-symbol DataFrame as a ``list[Data]``."""
    return df_to_basemodel(symbol_df)


@pytest.fixture(scope="session")
def panel_df() -> pd.DataFrame:
    """Build a panel (entity/time MultiIndex) DataFrame."""
    np.random.seed(SEED)
    return mock_multi_index_data()


@pytest.fixture(scope="session")
def panel_data(panel_df) -> list:
    """Expose the panel DataFrame as a ``list[Data]`` (MultiIndex preserved)."""
    return df_to_basemodel(panel_df, index=True)


@pytest.fixture(scope="session")
def non_numeric_data() -> list:
    """A dataset whose ``open`` column is non-numeric."""
    rng = np.random.default_rng(SEED)
    rows = 20
    df = pd.DataFrame(
        {
            "open": [f"label_{i}" for i in range(rows)],
            "high": rng.normal(10, 1, rows),
            "close": rng.normal(10, 1, rows),
        }
    )
    return df_to_basemodel(df)


@pytest.fixture(scope="session")
def small_panel_data() -> list:
    """A panel dataset with only 2 rows."""
    df = pd.DataFrame(
        {"portfolio_value": [10.0, 12.0], "risk_free_rate": [0.01, 0.02]},
        index=pd.MultiIndex.from_tuples(
            [("entity_1", 1), ("entity_1", 2)], names=("entity", "time")
        ),
    )
    return df_to_basemodel(df, index=True)
