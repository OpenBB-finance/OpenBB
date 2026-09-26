"""Tests for openbb_technical.signals.thresholds."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.signals.thresholds import (
    _DEFAULT_THRESHOLDS,
    OscillatorSignal,
    OscillatorSignalsQueryParams,
    _compute_oscillator,
    oscillator_signals,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Monotone OHLCV — used for happy-path defaults."""
    return df_to_basemodel(ohlcv_df.reset_index())


@pytest.fixture(scope="module")
def regime_change_df() -> pd.DataFrame:
    """A constructed series that visits overbought, neutral, and oversold regimes."""
    n = 80
    prices = np.full(n, 100.0)
    prices[10:25] = np.linspace(100, 150, 15)
    prices[25:40] = 150.0
    prices[40:55] = np.linspace(150, 70, 15)
    prices[55:] = 70.0
    return pd.DataFrame(
        {
            "open": prices,
            "high": prices + 1,
            "low": prices - 1,
            "close": prices,
            "volume": np.full(n, 1000.0),
        },
        index=pd.date_range("2021-01-01", periods=n, freq="D", name="date"),
    )


@pytest.fixture(scope="module")
def regime_records(regime_change_df) -> list:
    return df_to_basemodel(regime_change_df.reset_index())


class TestOscillatorSignalsBranches:
    """Cover every Literal branch of ``indicator``."""

    @pytest.mark.parametrize("indicator", list(_DEFAULT_THRESHOLDS.keys()))
    def test_each_indicator_returns_dense_series(self, long_records, indicator):
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=long_records, indicator=indicator, length=14
            )
        )
        assert len(result.results) == len(long_records)
        assert all(isinstance(r, OscillatorSignal) for r in result.results)

    @pytest.mark.parametrize("indicator", list(_DEFAULT_THRESHOLDS.keys()))
    def test_first_row_has_no_crossing_flags(self, long_records, indicator):
        """The first bar has no prior — every flag must be False."""
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=long_records, indicator=indicator, length=14
            )
        )
        first = result.results[0]
        assert first.crossed_into_overbought is False
        assert first.crossed_into_oversold is False
        assert first.crossed_out_of_overbought is False
        assert first.crossed_out_of_oversold is False


class TestThresholdDefaults:
    """Confirm the documented per-indicator defaults are actually applied."""

    @pytest.mark.parametrize(
        "indicator,ob,os_",
        [
            ("rsi", 70.0, 30.0),
            ("mfi", 80.0, 20.0),
            ("stoch", 80.0, 20.0),
            ("williams_r", -20.0, -80.0),
            ("cci", 100.0, -100.0),
        ],
    )
    def test_default_table(self, indicator, ob, os_):
        assert _DEFAULT_THRESHOLDS[indicator] == (ob, os_)

    def test_explicit_overrides_take_precedence(self, regime_records):
        """If both thresholds are given, defaults must NOT be used."""
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=regime_records,
                indicator="rsi",
                length=14,
                overbought_threshold=-1e9,
                oversold_threshold=-2e9,
            )
        )
        non_warmup = [r for r in result.results if r.value != 0.0]
        assert all(r.regime == "overbought" for r in non_warmup)

    def test_overbought_only_override(self, regime_records):
        """Only setting ``overbought_threshold`` keeps the default oversold band."""
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=regime_records,
                indicator="rsi",
                length=14,
                overbought_threshold=200.0,
            )
        )
        regimes = {r.regime for r in result.results}
        assert "overbought" not in regimes
        assert "oversold" in regimes

    def test_oversold_only_override(self, regime_records):
        """Only setting ``oversold_threshold`` keeps the default overbought band."""
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=regime_records,
                indicator="rsi",
                length=14,
                oversold_threshold=-200.0,
            )
        )
        regimes = {r.regime for r in result.results}
        assert "oversold" not in regimes
        assert "overbought" in regimes


class TestRegimeAndCrossings:
    def test_visits_all_three_regimes(self, regime_records):
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=regime_records, indicator="rsi", length=14
            )
        )
        regimes = {r.regime for r in result.results}
        assert regimes == {"overbought", "neutral", "oversold"}

    def test_crossing_flag_count_matches_regime_changes(self, regime_records):
        """The crossings_into_X count == number of regime->X transitions."""
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=regime_records, indicator="rsi", length=14
            )
        )
        labels = [r.regime for r in result.results]
        into_ob_manual = sum(
            1
            for i in range(1, len(labels))
            if labels[i] == "overbought" and labels[i - 1] != "overbought"
        )
        into_os_manual = sum(
            1
            for i in range(1, len(labels))
            if labels[i] == "oversold" and labels[i - 1] != "oversold"
        )
        into_ob_flag = sum(r.crossed_into_overbought for r in result.results)
        into_os_flag = sum(r.crossed_into_oversold for r in result.results)
        assert into_ob_flag == into_ob_manual
        assert into_os_flag == into_os_manual

    def test_crossing_out_matches_regime_exits(self, regime_records):
        result = oscillator_signals(
            OscillatorSignalsQueryParams(
                data=regime_records, indicator="rsi", length=14
            )
        )
        labels = [r.regime for r in result.results]
        out_ob_manual = sum(
            1
            for i in range(1, len(labels))
            if labels[i - 1] == "overbought" and labels[i] != "overbought"
        )
        out_os_manual = sum(
            1
            for i in range(1, len(labels))
            if labels[i - 1] == "oversold" and labels[i] != "oversold"
        )
        out_ob_flag = sum(r.crossed_out_of_overbought for r in result.results)
        out_os_flag = sum(r.crossed_out_of_oversold for r in result.results)
        assert out_ob_flag == out_ob_manual
        assert out_os_flag == out_os_manual


class TestComputeOscillatorDispatcher:
    """Direct unit-coverage on the dispatch helper."""

    @pytest.mark.parametrize(
        "indicator",
        ["rsi", "mfi", "stoch", "williams_r", "cci"],
    )
    def test_dispatch(self, ohlcv_df, indicator):
        series = _compute_oscillator(ohlcv_df, indicator, length=14, target="close")
        assert series.ndim == 1
        assert series.dropna().shape[0] > 0


class TestQueryParamModel:
    def test_defaults(self, long_records):
        params = OscillatorSignalsQueryParams(data=long_records, indicator="rsi")
        assert params.target == "close"
        assert params.index == "date"
        assert params.length == 14
        assert params.overbought_threshold is None
        assert params.oversold_threshold is None

    def test_indicator_required(self, long_records):
        with pytest.raises(Exception):
            OscillatorSignalsQueryParams(data=long_records)  # type: ignore[call-arg]

    def test_rejects_invalid_indicator(self, long_records):
        with pytest.raises(Exception):
            OscillatorSignalsQueryParams(data=long_records, indicator="macd")  # type: ignore[arg-type]
