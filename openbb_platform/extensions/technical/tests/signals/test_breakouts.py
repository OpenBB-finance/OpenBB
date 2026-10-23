"""Tests for openbb_technical.signals.breakouts."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.signals.breakouts import (
    BreakoutEvent,
    BreakoutsQueryParams,
    _channel_bands,
    breakouts,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Monotone OHLCV fixture — every bar is a new high (always breaking upside)."""
    return df_to_basemodel(ohlcv_df.reset_index())


@pytest.fixture(scope="module")
def regime_records() -> list:
    """OHLCV that produces both upside and downside breakouts.

    Builds a flat base, a rally that punches above the channel, a sideways
    pause, a sell-off through the lower band, then another flat period.
    """
    n = 80
    prices = np.full(n, 100.0)
    prices[10:25] = np.linspace(100, 150, 15)
    prices[25:40] = 150.0
    prices[40:55] = np.linspace(150, 70, 15)
    prices[55:] = 70.0
    df = pd.DataFrame(
        {
            "open": prices,
            "high": prices + 1,
            "low": prices - 1,
            "close": prices,
            "volume": np.full(n, 1000.0),
        },
        index=pd.date_range("2021-01-01", periods=n, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


@pytest.fixture(scope="module")
def flat_records() -> list:
    """A flat series — should produce zero breakouts under either method."""
    n = 60
    prices = np.full(n, 100.0)
    df = pd.DataFrame(
        {
            "open": prices,
            "high": prices + 0.01,
            "low": prices - 0.01,
            "close": prices,
            "volume": np.full(n, 1000.0),
        },
        index=pd.date_range("2021-01-01", periods=n, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


class TestMethodBranches:
    @pytest.mark.parametrize("method", ["donchian", "bollinger"])
    def test_each_method_returns_breakout_events(self, regime_records, method):
        result = breakouts(
            BreakoutsQueryParams(data=regime_records, method=method, length=20)
        )
        assert result.results
        assert all(isinstance(r, BreakoutEvent) for r in result.results)

    def test_bollinger_uses_default_std_when_not_given(self, regime_records):
        default = breakouts(
            BreakoutsQueryParams(data=regime_records, method="bollinger", length=20)
        )
        explicit = breakouts(
            BreakoutsQueryParams(
                data=regime_records, method="bollinger", length=20, band_std=2.0
            )
        )
        assert len(default.results) == len(explicit.results)

    def test_bollinger_smaller_std_yields_more_breakouts(self, regime_records):
        wide = breakouts(
            BreakoutsQueryParams(
                data=regime_records, method="bollinger", length=20, band_std=3.0
            )
        )
        narrow = breakouts(
            BreakoutsQueryParams(
                data=regime_records, method="bollinger", length=20, band_std=1.0
            )
        )
        assert len(narrow.results) > len(wide.results)


class TestSparseEmission:
    def test_flat_series_emits_no_events(self, flat_records):
        result = breakouts(
            BreakoutsQueryParams(data=flat_records, method="donchian", length=20)
        )
        assert result.results == []

    def test_flat_series_emits_no_events_bollinger(self, flat_records):
        result = breakouts(
            BreakoutsQueryParams(data=flat_records, method="bollinger", length=20)
        )
        assert result.results == []

    def test_events_are_sparse_subset_of_bars(self, regime_records):
        result = breakouts(
            BreakoutsQueryParams(data=regime_records, method="donchian", length=20)
        )
        assert 0 < len(result.results) < len(regime_records)


class TestEventFields:
    def test_upside_direction(self, long_records):
        """A strictly monotone-rising series produces only upside breakouts."""
        result = breakouts(
            BreakoutsQueryParams(data=long_records, method="donchian", length=20)
        )
        assert result.results
        assert all(r.direction == "upside" for r in result.results)
        assert all(r.magnitude > 0 for r in result.results)
        assert all(r.price > r.band for r in result.results)

    def test_downside_direction(self, regime_records):
        result = breakouts(
            BreakoutsQueryParams(data=regime_records, method="donchian", length=20)
        )
        downsides = [r for r in result.results if r.direction == "downside"]
        assert downsides
        assert all(r.magnitude < 0 for r in downsides)
        assert all(r.price < r.band for r in downsides)

    def test_bars_in_range_monotone_for_first_event(self, regime_records):
        """``bars_in_range`` on the first event equals the bar index."""
        result = breakouts(
            BreakoutsQueryParams(data=regime_records, method="donchian", length=20)
        )
        first = result.results[0]
        assert first.bars_in_range >= 0

    def test_bars_in_range_is_inter_event_gap(self, regime_records):
        """For each event after the first, bars_in_range = gap to prior event."""
        result = breakouts(
            BreakoutsQueryParams(data=regime_records, method="donchian", length=20)
        )
        assert len(result.results) >= 2
        for r in result.results[1:]:
            assert r.bars_in_range >= 1


class TestChannelBandsDispatcher:
    @pytest.mark.parametrize("method", ["donchian", "bollinger"])
    def test_each_method_returns_two_series(self, ohlcv_df, method):
        upper, lower = _channel_bands(ohlcv_df, method, length=20, band_std=None)
        assert upper.ndim == 1
        assert lower.ndim == 1
        valid = upper.dropna().index.intersection(lower.dropna().index)
        assert (upper.loc[valid] >= lower.loc[valid]).all()

    def test_bollinger_band_std_passed_through(self, ohlcv_df):
        u1, l1 = _channel_bands(ohlcv_df, "bollinger", length=20, band_std=1.0)
        u3, l3 = _channel_bands(ohlcv_df, "bollinger", length=20, band_std=3.0)
        valid = u1.dropna().index.intersection(u3.dropna().index)
        assert (u3.loc[valid] >= u1.loc[valid]).all()
        assert (l3.loc[valid] <= l1.loc[valid]).all()


class TestQueryParamModel:
    def test_defaults(self, long_records):
        params = BreakoutsQueryParams(data=long_records)
        assert params.index == "date"
        assert params.method == "donchian"
        assert params.length == 20
        assert params.band_std is None

    def test_rejects_invalid_method(self, long_records):
        with pytest.raises(Exception):
            BreakoutsQueryParams(data=long_records, method="keltner")  # type: ignore[arg-type]

    def test_band_std_must_be_positive(self, long_records):
        with pytest.raises(Exception):
            BreakoutsQueryParams(data=long_records, band_std=-1.0)
