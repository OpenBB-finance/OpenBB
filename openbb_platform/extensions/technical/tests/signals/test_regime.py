"""Tests for openbb_technical.signals.regime."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.signals.regime import (
    RegimeData,
    RegimeQueryParams,
    _classify,
    regime,
)


@pytest.fixture(scope="module")
def trending_records():
    """A clean monotone uptrend — ADX should rise, choppiness should fall."""
    n = 120
    base = np.arange(1, n + 1, dtype="float64")
    df = pd.DataFrame(
        {
            "open": base,
            "high": base + 0.5,
            "low": base - 0.5,
            "close": base,
            "volume": base * 100,
        },
        index=pd.date_range("2022-01-01", periods=n, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


@pytest.fixture(scope="module")
def choppy_records():
    """Sideways sawtooth so choppiness sits near the upper rail."""
    n = 120
    sawtooth = np.tile([100.0, 101.0, 100.0, 99.0], n // 4 + 1)[:n]
    df = pd.DataFrame(
        {
            "open": sawtooth,
            "high": sawtooth + 0.2,
            "low": sawtooth - 0.2,
            "close": sawtooth,
            "volume": np.full(n, 1000.0),
        },
        index=pd.date_range("2022-01-01", periods=n, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


class TestRegimeEndpoint:
    def test_returns_one_row_per_bar(self, trending_records):
        result = regime(RegimeQueryParams(data=trending_records))
        assert len(result.results) == 120
        assert all(isinstance(r, RegimeData) for r in result.results)

    def test_trending_data_reaches_trend_label(self, trending_records):
        result = regime(RegimeQueryParams(data=trending_records))
        labels = {r.regime for r in result.results}
        assert "strong_trend" in labels or "weak_trend" in labels

    def test_first_bars_are_warm_up_transition(self, trending_records):
        result = regime(RegimeQueryParams(data=trending_records))
        assert result.results[0].regime == "transition"
        assert result.results[0].regime_changed is False
        assert result.results[0].adx is None
        assert result.results[0].choppiness is None

    def test_choppy_data_hits_ranging(self, choppy_records):
        result = regime(RegimeQueryParams(data=choppy_records))
        labels = {r.regime for r in result.results}
        assert "ranging" in labels

    def test_regime_changed_flag(self, trending_records):
        result = regime(RegimeQueryParams(data=trending_records))
        assert any(r.regime_changed for r in result.results)

    def test_custom_thresholds_alter_labels(self, trending_records):
        tight = regime(
            RegimeQueryParams(data=trending_records, adx_trend_threshold=200.0)
        )
        assert "strong_trend" not in {r.regime for r in tight.results}


class TestClassifyDirect:
    """Drive ``_classify`` directly to guarantee every branch executes."""

    def test_none_adx_short_circuits(self):
        assert _classify(None, 10.0, 25.0, 61.8) == "transition"

    def test_none_choppiness_short_circuits(self):
        assert _classify(50.0, None, 25.0, 61.8) == "transition"

    def test_strong_trend(self):
        assert _classify(40.0, 30.0, 25.0, 61.8) == "strong_trend"

    def test_weak_trend(self):
        assert _classify(20.0, 70.0, 25.0, 61.8) == "weak_trend"

    def test_weak_trend_high_chop_overrides_strong(self):
        assert _classify(30.0, 70.0, 25.0, 61.8) == "weak_trend"

    def test_ranging(self):
        assert _classify(5.0, 70.0, 25.0, 61.8) == "ranging"

    def test_transition_fallback(self):
        assert _classify(5.0, 30.0, 25.0, 61.8) == "transition"


class TestQueryParamModel:
    def test_defaults(self, trending_records):
        params = RegimeQueryParams(data=trending_records)
        assert params.adx_length == 14
        assert params.choppiness_length == 14
        assert params.adx_trend_threshold == 25.0
        assert params.choppiness_range_threshold == 61.8
