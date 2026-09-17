"""Shared deterministic real-data fixtures for the charting test suite."""

from __future__ import annotations

import sys
import types

import numpy as np
import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data

SYMBOLS = ("AAA", "BBB", "CCC", "DDD")


def _install_fake_pywry() -> None:
    """Install a minimal fake ``pywry`` so the GUI backend runs headlessly.

    ``pywry`` is an optional GUI dependency with no wheels for every supported
    Python (e.g. 3.14), so CI cannot install it. It is the one true external
    boundary — the window/websocket layer — so a faithful in-memory stand-in is
    the correct test double. Installing it unconditionally keeps backend tests
    deterministic across every environment.
    """
    pywry = types.ModuleType("pywry")
    pywry._OPENBB_FAKE = True  # type: ignore[attr-defined]

    class _Component:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class Toolbar(_Component):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.items = kwargs.get("items", [])

    class _App:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.theme = kwargs.get("theme")

        def show_plotly(self, **kwargs):
            return None

        def show_dataframe(self, **kwargs):
            return None

        def show(self, **kwargs):
            return None

        def emit(self, *args, **kwargs):
            return None

        def close(self, *args, **kwargs):
            return None

    class ThemeMode:
        DARK = "dark"
        LIGHT = "light"

    pywry.PyWry = _App  # type: ignore[attr-defined]
    pywry.ThemeMode = ThemeMode  # type: ignore[attr-defined]
    pywry.Toolbar = Toolbar  # type: ignore[attr-defined]
    pywry.Button = _Component  # type: ignore[attr-defined]
    pywry.Div = _Component  # type: ignore[attr-defined]
    pywry.TextArea = _Component  # type: ignore[attr-defined]
    pywry.PlotlyConfig = _Component  # type: ignore[attr-defined]

    grid = types.ModuleType("pywry.grid")

    class _GridData:
        def __init__(self, frame):
            self.columns = list(frame.columns)
            self.index_columns = []
            self.column_types = {col: "text" for col in frame.columns}
            self.row_data = frame.to_dict(orient="records")

    grid.normalize_data = _GridData  # type: ignore[attr-defined]
    grid.build_column_defs = lambda columns, index_columns, column_types: [  # type: ignore[attr-defined]
        {"field": col} for col in columns
    ]
    pywry.grid = grid  # type: ignore[attr-defined]

    sys.modules["pywry"] = pywry
    sys.modules["pywry.grid"] = grid


_install_fake_pywry()


def _make_ohlcv(
    seed: int, periods: int = 200, start: str = "2023-01-01"
) -> pd.DataFrame:
    """Build a deterministic, valid OHLCV frame with a ``date`` index."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=periods, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, periods))
    open_ = close + rng.normal(0, 0.5, periods)
    high = np.maximum(open_, close) + np.abs(rng.normal(0, 0.5, periods))
    low = np.minimum(open_, close) - np.abs(rng.normal(0, 0.5, periods))
    volume = rng.integers(1_000_000, 5_000_000, periods)
    frame = pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )
    frame.index.name = "date"
    return frame


@pytest.fixture
def ohlcv_df() -> pd.DataFrame:
    """A single-symbol OHLCV DataFrame indexed by date (200 rows)."""
    return _make_ohlcv(seed=42)


@pytest.fixture
def ohlcv_records(ohlcv_df) -> list[dict]:
    """The OHLCV frame as a list of ``date``-stamped record dicts."""
    out = ohlcv_df.reset_index()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d")
    return out.to_dict(orient="records")


@pytest.fixture
def ohlcv_data(ohlcv_records) -> list[Data]:
    """The OHLCV records as real ``Data`` models."""
    return [Data.model_validate(row) for row in ohlcv_records]


@pytest.fixture
def multi_close_df() -> pd.DataFrame:
    """A multi-symbol close-price frame (wide), indexed by date."""
    frames = {sym: _make_ohlcv(seed=i)["close"] for i, sym in enumerate(SYMBOLS)}
    wide = pd.DataFrame(frames)
    wide.index.name = "date"
    return wide
