"""Deterministic, self-contained fixtures for the charting integration suite."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.abstract.data import Data

from openbb_charting.charting import Charting
from openbb_charting.core.backend import Backend

# pylint: disable=protected-access


def _ohlcv(seed: int, periods: int = 120, symbol: str | None = None) -> pd.DataFrame:
    """Build a deterministic OHLCV frame with a string ``date`` column."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-01", periods=periods, freq="D")
    close = 100 + np.cumsum(rng.normal(0, 1, periods))
    frame = pd.DataFrame(
        {
            "date": idx.strftime("%Y-%m-%d"),
            "open": close + rng.normal(0, 0.5, periods),
            "high": np.maximum(close, close + 1),
            "low": np.minimum(close, close - 1),
            "close": close,
            "volume": rng.integers(1_000_000, 5_000_000, periods),
        }
    )
    if symbol is not None:
        frame["symbol"] = symbol
    return frame


def _records(frame: pd.DataFrame) -> list[Data]:
    """Convert a frame to a list of real ``Data`` records."""
    return [Data.model_validate(row) for row in frame.to_dict(orient="records")]


def ohlcv_single() -> list[Data]:
    """Single-symbol OHLCV records (candlestick path)."""
    return _records(_ohlcv(7))


def ohlcv_multi() -> list[Data]:
    """Long-format OHLCV records for three symbols (multi-series line path)."""
    frames = [_ohlcv(i, symbol=sym) for i, sym in enumerate(("AAA", "BBB", "CCC"))]
    return _records(pd.concat(frames, ignore_index=True))


_PERF_COLS = (
    "one_day",
    "one_week",
    "one_month",
    "three_month",
    "six_month",
    "ytd",
    "one_year",
    "two_year",
    "three_year",
    "four_year",
    "five_year",
)


def performance_records() -> list[Data]:
    """Two-symbol price-performance records (bar path)."""
    rows = []
    for sym, sign in (("AAA", 1.0), ("BBB", -1.0)):
        values = {
            col: round(sign * (i + 1) / 100, 4) for i, col in enumerate(_PERF_COLS)
        }
        rows.append({"symbol": sym, **values})
    return [Data.model_validate(row) for row in rows]


def long_close_records() -> list[Data]:
    """Long-format ``date``/``symbol``/``close`` records (correlation path)."""
    rng = np.random.default_rng(0)
    idx = pd.date_range("2023-01-01", periods=60, freq="D")
    rows = []
    for sym in ("AAA", "BBB", "CCC"):
        close = 100 + np.cumsum(rng.normal(0, 1, 60))
        for stamp, value in zip(idx, close):
            rows.append(
                {
                    "date": stamp.strftime("%Y-%m-%d"),
                    "symbol": sym,
                    "close": float(value),
                }
            )
    return [Data.model_validate(row) for row in rows]


CASES = [
    ("single_symbol_candlestick", "/equity/price/historical", ohlcv_single, {}),
    ("multi_symbol_line", "/equity/price/historical", ohlcv_multi, {"target": "close"}),
    (
        "sma_indicator_overlay",
        "/equity/price/historical",
        ohlcv_single,
        {"indicators": {"sma": {"length": [20]}}},
    ),
    ("price_performance_bar", "/equity/price/performance", performance_records, {}),
    (
        "correlation_matrix_heatmap",
        "/econometrics/correlation_matrix",
        long_close_records,
        {},
    ),
]


class IntegrationViews:
    """A fixed, known charting view registered for the integration suite."""

    @staticmethod
    def equity_price_historical(**kwargs):
        """Delegate to the real price-historical builder."""
        from openbb_charting.charts.price_historical import price_historical

        return price_historical(**kwargs)

    @staticmethod
    def equity_price_performance(**kwargs):
        """Delegate to the real price-performance builder."""
        from openbb_charting.charts.price_performance import price_performance

        return price_performance(**kwargs)

    @staticmethod
    def econometrics_correlation_matrix(**kwargs):
        """Delegate to the real correlation-matrix builder."""
        from openbb_charting.charts.correlation_matrix import correlation_matrix

        return correlation_matrix(**kwargs)


@pytest.fixture(autouse=True)
def known_views():
    """Register the fixed, known view class for the duration of each test."""
    original = Charting._extension_views_cache
    Charting._extension_views_cache = [IntegrationViews]
    try:
        yield
    finally:
        Charting._extension_views_cache = original


@pytest.fixture(autouse=True)
def reset_backend():
    """Reset the ``Backend`` singleton around each test to avoid GUI/state leakage."""
    Backend.instance = None
    yield
    Backend.instance = None


def make_obbject(route: str, results: list[Data], **standard_params) -> OBBject:
    """Build a real ``OBBject`` shaped as the given command route would return it."""
    obj = OBBject(results=results, provider="test")
    obj._route = route
    obj._standard_params = standard_params or {}
    obj._extra_params = {}
    return obj
