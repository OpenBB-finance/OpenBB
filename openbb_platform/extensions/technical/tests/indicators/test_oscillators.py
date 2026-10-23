"""Tests for openbb_technical.indicators.oscillators."""

from __future__ import annotations

import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.indicators.oscillators import (
    AwesomeOscillatorData,
    AwesomeOscillatorQueryParams,
    CciData,
    CciQueryParams,
    CgData,
    CgQueryParams,
    FisherData,
    FisherQueryParams,
    MfiData,
    MfiQueryParams,
    RsiData,
    RsiQueryParams,
    StochData,
    StochQueryParams,
    TrixData,
    TrixQueryParams,
    UltimateOscillatorData,
    UltimateOscillatorQueryParams,
    WilliamsRData,
    WilliamsRQueryParams,
    awesome_oscillator,
    cci,
    cg,
    fisher,
    mfi,
    rsi,
    stoch,
    trix,
    ultimate_oscillator,
    williams_r,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Convert the standard OHLCV fixture into ``list[Data]``."""
    return df_to_basemodel(ohlcv_df.reset_index())


class TestRsi:
    def test_default(self, long_records):
        result = rsi(RsiQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, RsiData) for r in result.results)
        assert result.results[0].rsi is not None

    def test_custom_length(self, long_records):
        result = rsi(RsiQueryParams(data=long_records, length=20))
        assert result.results

    def test_custom_target(self, long_records):
        result = rsi(RsiQueryParams(data=long_records, target="high"))
        assert result.results

    def test_custom_scalar(self, long_records):
        result = rsi(RsiQueryParams(data=long_records, scalar=50.0))
        assert result.results

    def test_custom_drift(self, long_records):
        result = rsi(RsiQueryParams(data=long_records, drift=2))
        assert result.results


class TestStoch:
    def test_default(self, long_records):
        result = stoch(StochQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, StochData) for r in result.results)
        first = result.results[0]
        assert first.k is not None
        assert first.d is not None

    def test_custom_fast_k(self, long_records):
        result = stoch(StochQueryParams(data=long_records, fast_k_period=10))
        assert result.results

    def test_custom_slow_d(self, long_records):
        result = stoch(StochQueryParams(data=long_records, slow_d_period=5))
        assert result.results

    def test_custom_slow_k(self, long_records):
        result = stoch(StochQueryParams(data=long_records, slow_k_period=4))
        assert result.results


class TestCci:
    def test_default(self, long_records):
        result = cci(CciQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, CciData) for r in result.results)
        assert result.results[0].cci is not None

    def test_custom_length(self, long_records):
        result = cci(CciQueryParams(data=long_records, length=20))
        assert result.results

    def test_custom_scalar(self, long_records):
        result = cci(CciQueryParams(data=long_records, scalar=0.02))
        assert result.results


class TestFisher:
    def test_default(self, long_records):
        result = fisher(FisherQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, FisherData) for r in result.results)
        assert result.results[0].fisher is not None

    def test_custom_length(self, long_records):
        result = fisher(FisherQueryParams(data=long_records, length=20))
        assert result.results

    def test_custom_signal(self, long_records):
        result = fisher(FisherQueryParams(data=long_records, signal=3))
        assert result.results


class TestCg:
    def test_default(self, long_records):
        result = cg(CgQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, CgData) for r in result.results)
        assert result.results[0].cg is not None

    def test_custom_length(self, long_records):
        result = cg(CgQueryParams(data=long_records, length=20))
        assert result.results


class TestWilliamsR:
    def test_default(self, long_records):
        result = williams_r(WilliamsRQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, WilliamsRData) for r in result.results)
        assert result.results[0].williams_r is not None

    def test_custom_length(self, long_records):
        result = williams_r(WilliamsRQueryParams(data=long_records, length=20))
        assert result.results


class TestMfi:
    def test_default(self, long_records):
        result = mfi(MfiQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, MfiData) for r in result.results)
        assert result.results[0].mfi is not None

    def test_custom_length(self, long_records):
        result = mfi(MfiQueryParams(data=long_records, length=20))
        assert result.results


class TestTrix:
    def test_default(self, long_records):
        result = trix(TrixQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, TrixData) for r in result.results)
        first = result.results[0]
        assert first.trix is not None
        assert first.signal is not None

    def test_custom_length(self, long_records):
        result = trix(TrixQueryParams(data=long_records, length=15))
        assert result.results

    def test_custom_signal(self, long_records):
        result = trix(TrixQueryParams(data=long_records, signal=5))
        assert result.results

    def test_custom_target(self, long_records):
        result = trix(TrixQueryParams(data=long_records, target="high"))
        assert result.results


class TestUltimateOscillator:
    def test_default(self, long_records):
        result = ultimate_oscillator(UltimateOscillatorQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, UltimateOscillatorData) for r in result.results)
        assert result.results[0].ultimate_oscillator is not None

    def test_custom_fast(self, long_records):
        result = ultimate_oscillator(
            UltimateOscillatorQueryParams(data=long_records, fast=5)
        )
        assert result.results

    def test_custom_medium(self, long_records):
        result = ultimate_oscillator(
            UltimateOscillatorQueryParams(data=long_records, medium=10)
        )
        assert result.results

    def test_custom_slow(self, long_records):
        result = ultimate_oscillator(
            UltimateOscillatorQueryParams(data=long_records, slow=20)
        )
        assert result.results

    def test_custom_fast_weight(self, long_records):
        result = ultimate_oscillator(
            UltimateOscillatorQueryParams(data=long_records, fast_weight=5.0)
        )
        assert result.results

    def test_custom_medium_weight(self, long_records):
        result = ultimate_oscillator(
            UltimateOscillatorQueryParams(data=long_records, medium_weight=3.0)
        )
        assert result.results

    def test_custom_slow_weight(self, long_records):
        result = ultimate_oscillator(
            UltimateOscillatorQueryParams(data=long_records, slow_weight=2.0)
        )
        assert result.results


class TestAwesomeOscillator:
    def test_default(self, long_records):
        result = awesome_oscillator(AwesomeOscillatorQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, AwesomeOscillatorData) for r in result.results)
        assert result.results[0].awesome_oscillator is not None

    def test_custom_fast(self, long_records):
        result = awesome_oscillator(
            AwesomeOscillatorQueryParams(data=long_records, fast=3)
        )
        assert result.results

    def test_custom_slow(self, long_records):
        result = awesome_oscillator(
            AwesomeOscillatorQueryParams(data=long_records, slow=20)
        )
        assert result.results


class TestQueryParamModels:
    """Field-level coverage of the QueryParams classes."""

    def test_rsi_defaults(self, long_records):
        params = RsiQueryParams(data=long_records)
        assert params.length == 14
        assert params.scalar == 100.0
        assert params.drift == 1
        assert params.target == "close"

    def test_stoch_defaults(self, long_records):
        params = StochQueryParams(data=long_records)
        assert params.fast_k_period == 14
        assert params.slow_d_period == 3
        assert params.slow_k_period == 3

    def test_cci_defaults(self, long_records):
        params = CciQueryParams(data=long_records)
        assert params.length == 14
        assert params.scalar == 0.015

    def test_fisher_defaults(self, long_records):
        params = FisherQueryParams(data=long_records)
        assert params.length == 14
        assert params.signal == 1

    def test_cg_defaults(self, long_records):
        params = CgQueryParams(data=long_records)
        assert params.length == 14

    def test_williams_r_defaults(self, long_records):
        params = WilliamsRQueryParams(data=long_records)
        assert params.length == 14

    def test_mfi_defaults(self, long_records):
        params = MfiQueryParams(data=long_records)
        assert params.length == 14

    def test_trix_defaults(self, long_records):
        params = TrixQueryParams(data=long_records)
        assert params.length == 30
        assert params.signal == 9
        assert params.target == "close"

    def test_ultimate_oscillator_defaults(self, long_records):
        params = UltimateOscillatorQueryParams(data=long_records)
        assert params.fast == 7
        assert params.medium == 14
        assert params.slow == 28
        assert params.fast_weight == 4.0
        assert params.medium_weight == 2.0
        assert params.slow_weight == 1.0

    def test_awesome_oscillator_defaults(self, long_records):
        params = AwesomeOscillatorQueryParams(data=long_records)
        assert params.fast == 5
        assert params.slow == 34
