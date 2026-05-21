"""Shared fixtures for the quantitative test suite."""

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

SEED = 42
N_ROWS = 250
FACTOR_N_ROWS = 800


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


@pytest.fixture(scope="session")
def factor_dates() -> pd.DatetimeIndex:
    """Daily business-day index long enough for rolling 252-day windows."""
    return pd.date_range("2018-01-01", periods=FACTOR_N_ROWS, freq="B")


@pytest.fixture(scope="session")
def factor_matrix_df(factor_dates) -> pd.DataFrame:
    """Two synthetic factors plus a constant risk-free column.

    Used together with ``target_returns_df`` so the true betas are known
    (`y = 0.7*f1 - 0.3*f2 + rf + noise`).
    """
    rng = np.random.default_rng(SEED)
    n = len(factor_dates)
    return pd.DataFrame(
        {
            "date": factor_dates,
            "f1": rng.normal(0, 0.01, n),
            "f2": rng.normal(0, 0.01, n),
            # rf varies slightly so statsmodels keeps it as its own regressor
            # instead of folding it into the intercept term.
            "rf": 0.0001 + rng.normal(0, 1e-6, n),
        }
    )


@pytest.fixture(scope="session")
def target_returns_df(factor_dates, factor_matrix_df) -> pd.DataFrame:
    """Target series whose returns are a known linear combo of the factors."""
    rng = np.random.default_rng(SEED + 1)
    n = len(factor_dates)
    y = (
        0.7 * factor_matrix_df["f1"].to_numpy()
        - 0.3 * factor_matrix_df["f2"].to_numpy()
        + factor_matrix_df["rf"].to_numpy()
        + rng.normal(0, 0.002, n)
    )
    return pd.DataFrame({"date": factor_dates, "close": y})


@pytest.fixture(scope="session")
def factor_matrix_data(factor_matrix_df) -> list:
    """Factor matrix as ``list[Data]``."""
    return df_to_basemodel(factor_matrix_df)


@pytest.fixture(scope="session")
def target_returns_data(target_returns_df) -> list:
    """Target returns as ``list[Data]``."""
    return df_to_basemodel(target_returns_df)
