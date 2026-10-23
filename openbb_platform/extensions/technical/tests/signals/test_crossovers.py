"""Tests for openbb_technical.signals.crossovers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.signals.crossovers import (
    CrossoverEvent,
    CrossoversQueryParams,
    crossovers,
)


@pytest.fixture(scope="module")
def monotone_records(ohlcv_df):
    """Strictly increasing OHLCV — fast and slow MAs never cross."""
    return df_to_basemodel(ohlcv_df.reset_index())


@pytest.fixture(scope="module")
def sinusoidal_records():
    """Sinusoidal close series that guarantees multiple bullish/bearish crossovers."""
    periods = 200
    t = np.arange(periods)
    close = 100 + 10 * np.sin(t / 8.0)
    df = pd.DataFrame(
        {
            "open": close,
            "high": close + 0.5,
            "low": close - 0.5,
            "close": close,
            "volume": close * 100,
        },
        index=pd.date_range("2020-01-01", periods=periods, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


class TestCrossoversBehaviour:
    def test_default_returns_obbject(self, sinusoidal_records):
        result = crossovers(
            CrossoversQueryParams(
                data=sinusoidal_records, fast_length=5, slow_length=20
            )
        )
        assert result.results
        assert all(isinstance(r, CrossoverEvent) for r in result.results)

    @pytest.mark.parametrize("mamode", ["sma", "ema", "wma", "hma", "zlma"])
    def test_each_mamode_produces_events(self, sinusoidal_records, mamode):
        result = crossovers(
            CrossoversQueryParams(
                data=sinusoidal_records, fast_length=5, slow_length=20, mamode=mamode
            )
        )
        assert result.results
        assert all(r.direction in {"bullish", "bearish"} for r in result.results)

    def test_sparse_output_no_crossovers(self, monotone_records):
        """Strictly increasing series produces zero crossovers."""
        result = crossovers(
            CrossoversQueryParams(data=monotone_records, fast_length=5, slow_length=20)
        )
        assert result.results == []

    def test_distance_sign_and_magnitude(self, sinusoidal_records):
        """`distance` equals fast - slow and matches direction polarity."""
        result = crossovers(
            CrossoversQueryParams(
                data=sinusoidal_records, fast_length=5, slow_length=20, mamode="sma"
            )
        )
        assert result.results
        for ev in result.results:
            assert ev.distance == pytest.approx(ev.fast_value - ev.slow_value)
            if ev.direction == "bullish":
                assert ev.distance > 0
            else:
                assert ev.distance < 0

    def test_alternating_directions(self, sinusoidal_records):
        """Adjacent crossover events must alternate direction."""
        result = crossovers(
            CrossoversQueryParams(
                data=sinusoidal_records, fast_length=5, slow_length=20, mamode="sma"
            )
        )
        directions = [e.direction for e in result.results]
        for prev, nxt in zip(directions, directions[1:]):
            assert prev != nxt


class TestCrossoversValidator:
    def test_slow_must_exceed_fast(self, sinusoidal_records):
        with pytest.raises(
            ValueError, match="slow_length must be greater than fast_length"
        ):
            CrossoversQueryParams(
                data=sinusoidal_records, fast_length=50, slow_length=20
            )

    def test_slow_equal_to_fast_rejected(self, sinusoidal_records):
        with pytest.raises(
            ValueError, match="slow_length must be greater than fast_length"
        ):
            CrossoversQueryParams(
                data=sinusoidal_records, fast_length=20, slow_length=20
            )


class TestCrossoversQueryParamDefaults:
    def test_defaults(self, sinusoidal_records):
        params = CrossoversQueryParams(data=sinusoidal_records)
        assert params.target == "close"
        assert params.index == "date"
        assert params.fast_length == 20
        assert params.slow_length == 50
        assert params.mamode == "sma"


class TestCrossoversEdgeCases:
    def test_empty_diff_yields_no_events(self):
        """Insufficient warmup for ``hma`` leaves the diff empty after dropna."""
        periods = 20
        close = np.arange(1, periods + 1, dtype="float64")
        df = pd.DataFrame(
            {
                "open": close,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": close * 100,
            },
            index=pd.date_range("2020-01-01", periods=periods, freq="D", name="date"),
        )
        records = df_to_basemodel(df.reset_index())
        result = crossovers(
            CrossoversQueryParams(
                data=records, fast_length=5, slow_length=20, mamode="hma"
            )
        )
        assert result.results == []
