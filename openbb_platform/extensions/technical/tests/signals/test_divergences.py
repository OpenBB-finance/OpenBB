"""Tests for openbb_technical.signals.divergences."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.signals.divergences import (
    DivergenceEvent,
    DivergencesQueryParams,
    _classify_pair,
    _compute_indicator,
    _local_extrema,
    _strength,
    divergences,
)


def _records(prices: list[float], start: str = "2022-01-01") -> list:
    n = len(prices)
    df = pd.DataFrame(
        {
            "open": prices,
            "high": [p + 0.1 for p in prices],
            "low": [p - 0.1 for p in prices],
            "close": prices,
            "volume": [1000.0] * n,
        },
        index=pd.date_range(start, periods=n, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


@pytest.fixture(scope="module")
def regular_bullish_records():
    """Price lower-low, indicator higher-low."""
    prices: list[float] = []
    prices.extend([100.0] * 20)
    prices.extend([float(v) for v in np.linspace(100, 80, 11)[1:]])
    prices.extend([float(v) for v in np.linspace(80, 95, 11)[1:]])
    prices.extend([95.0] * 5)
    prices.extend([float(v) for v in np.linspace(95, 75, 11)[1:]])
    prices.extend([float(v) for v in np.linspace(75, 85, 11)[1:]])
    while len(prices) < 100:
        prices.append(85.0)
    return _records(prices[:100])


@pytest.fixture(scope="module")
def regular_bearish_records():
    """Price higher-high, indicator lower-high."""
    prices: list[float] = []
    prices.extend([100.0] * 20)
    prices.extend([float(v) for v in np.linspace(100, 120, 11)[1:]])
    prices.extend([float(v) for v in np.linspace(120, 105, 11)[1:]])
    prices.extend([105.0] * 5)
    prices.extend([float(v) for v in np.linspace(105, 125, 11)[1:]])
    prices.extend([float(v) for v in np.linspace(125, 115, 11)[1:]])
    while len(prices) < 100:
        prices.append(115.0)
    return _records(prices[:100])


@pytest.fixture(scope="module")
def hidden_bullish_records():
    """Price higher-low, indicator lower-low."""
    prices: list[float] = [
        100.0,
        101.0,
        100.5,
        101.5,
        101.0,
        102.0,
        101.5,
        100.5,
        99.5,
        100.0,
        99.5,
        98.5,
        97.5,
        96.5,
        95.5,
        94.5,
        93.5,
        92.5,
        91.5,
        90.5,
        90.0,
    ]
    prices.extend([float(v) for v in np.linspace(90, 105, 11)[1:]])
    prices.extend([105.0] * 10)
    prices.extend([105.0, 103.0, 100.0, 97.0, 95.0])
    prices.extend([96.0, 98.0, 100.0, 102.0, 104.0])
    while len(prices) < 100:
        prices.append(104.0)
    return _records(prices[:100])


@pytest.fixture(scope="module")
def hidden_bearish_records():
    """Price lower-high, indicator higher-high."""
    prices: list[float] = [
        100.0,
        99.0,
        99.5,
        98.5,
        99.0,
        98.0,
        98.5,
        99.5,
        100.5,
        100.0,
        100.5,
        101.5,
        102.5,
        103.5,
        104.5,
        105.5,
        106.5,
        107.5,
        108.5,
        109.5,
        110.0,
    ]
    prices.extend([float(v) for v in np.linspace(110, 95, 11)[1:]])
    prices.extend([95.0] * 10)
    prices.extend([95.0, 97.0, 100.0, 103.0, 105.0])
    prices.extend([104.0, 102.0, 100.0, 98.0, 96.0])
    while len(prices) < 100:
        prices.append(96.0)
    return _records(prices[:100])


@pytest.fixture(scope="module")
def random_walk_records():
    """A 100-bar random walk — used to exercise every indicator branch."""
    np.random.seed(7)
    prices = (100 + np.cumsum(np.random.randn(100))).tolist()
    return _records(prices)


class TestDivergencesEndpoint:
    def test_regular_bullish(self, regular_bullish_records):
        result = divergences(
            DivergencesQueryParams(
                data=regular_bullish_records,
                indicator="rsi",
                lookback=100,
                min_swing_distance=5,
            )
        )
        kinds = {e.kind for e in result.results}
        assert "regular_bullish" in kinds
        events = [e for e in result.results if e.kind == "regular_bullish"]
        e = events[0]
        assert e.price_at_confirmation < e.price_at_prior
        assert e.indicator_at_confirmation > e.indicator_at_prior
        assert 0.0 <= e.strength <= 1.0
        assert isinstance(e, DivergenceEvent)

    def test_regular_bearish(self, regular_bearish_records):
        result = divergences(
            DivergencesQueryParams(
                data=regular_bearish_records,
                indicator="rsi",
                lookback=100,
                min_swing_distance=5,
            )
        )
        kinds = {e.kind for e in result.results}
        assert "regular_bearish" in kinds
        events = [e for e in result.results if e.kind == "regular_bearish"]
        e = events[0]
        assert e.price_at_confirmation > e.price_at_prior
        assert e.indicator_at_confirmation < e.indicator_at_prior

    def test_hidden_bullish(self, hidden_bullish_records):
        result = divergences(
            DivergencesQueryParams(
                data=hidden_bullish_records,
                indicator="rsi",
                lookback=100,
                min_swing_distance=5,
            )
        )
        kinds = {e.kind for e in result.results}
        assert "hidden_bullish" in kinds

    def test_hidden_bearish(self, hidden_bearish_records):
        result = divergences(
            DivergencesQueryParams(
                data=hidden_bearish_records,
                indicator="rsi",
                lookback=100,
                min_swing_distance=5,
            )
        )
        kinds = {e.kind for e in result.results}
        assert "hidden_bearish" in kinds

    @pytest.mark.parametrize("indicator", ["rsi", "macd", "stoch", "cci"])
    def test_every_indicator_runs(self, random_walk_records, indicator):
        result = divergences(
            DivergencesQueryParams(
                data=random_walk_records,
                indicator=indicator,
                lookback=100,
                min_swing_distance=5,
            )
        )
        dates = [e.confirmation_date for e in result.results]
        assert dates == sorted(dates)

    def test_short_lookback_returns_empty(self, regular_bullish_records):
        result = divergences(
            DivergencesQueryParams(
                data=regular_bullish_records,
                indicator="rsi",
                lookback=8,
                min_swing_distance=5,
            )
        )
        assert result.results == []

    def test_events_sorted_chronologically(self, regular_bullish_records):
        result = divergences(
            DivergencesQueryParams(
                data=regular_bullish_records,
                indicator="rsi",
                lookback=100,
                min_swing_distance=5,
            )
        )
        dates = [e.confirmation_date for e in result.results]
        assert dates == sorted(dates)


class TestLocalExtrema:
    def test_finds_clear_peak_and_trough(self):
        values = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 9.0, 8.0, 7.0, 6.0, 5.0]
        highs, lows = _local_extrema(values, distance=3)
        assert highs == [5]
        assert lows == []

    def test_plateau_at_extremum_skipped(self):
        values = [1.0, 2.0, 3.0, 3.0, 2.0, 1.0]
        highs, lows = _local_extrema(values, distance=1)
        assert highs == []

    def test_min_in_middle(self):
        values = [10.0, 9.0, 8.0, 7.0, 6.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        highs, lows = _local_extrema(values, distance=3)
        assert lows == [5]


class TestClassifyPair:
    def test_regular_bearish(self):
        assert _classify_pair(100, 110, 80, 70, is_high=True) == "regular_bearish"

    def test_hidden_bearish(self):
        assert _classify_pair(110, 100, 70, 80, is_high=True) == "hidden_bearish"

    def test_high_no_divergence(self):
        assert _classify_pair(100, 110, 70, 80, is_high=True) is None

    def test_regular_bullish(self):
        assert _classify_pair(100, 90, 20, 30, is_high=False) == "regular_bullish"

    def test_hidden_bullish(self):
        assert _classify_pair(90, 100, 30, 20, is_high=False) == "hidden_bullish"

    def test_low_no_divergence(self):
        assert _classify_pair(100, 90, 30, 20, is_high=False) is None


class TestStrength:
    def test_zero_displacement(self):
        assert _strength(100.0, 100.0, 50.0, 50.0) == 0.0

    def test_clamped_to_unit_interval(self):
        s = _strength(1e-12, 1.0, 1e-12, 1.0)
        assert 0.0 <= s <= 1.0


class TestComputeIndicator:
    @pytest.mark.parametrize("indicator", ["rsi", "macd", "stoch", "cci"])
    def test_returns_aligned_series(self, random_walk_records, indicator):
        df = pd.DataFrame(
            {
                "open": [r.open for r in random_walk_records],
                "high": [r.high for r in random_walk_records],
                "low": [r.low for r in random_walk_records],
                "close": [r.close for r in random_walk_records],
                "volume": [r.volume for r in random_walk_records],
            },
            index=pd.to_datetime([r.date for r in random_walk_records]),
        )
        series = _compute_indicator(df, indicator, 14, "close")
        assert len(series) == len(df)


class TestQueryParamModel:
    def test_defaults(self, regular_bullish_records):
        params = DivergencesQueryParams(data=regular_bullish_records, indicator="rsi")
        assert params.indicator_length == 14
        assert params.target == "close"
        assert params.lookback == 60
        assert params.min_swing_distance == 5
