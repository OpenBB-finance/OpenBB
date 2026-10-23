"""Tests for openbb_technical.indicators.trend."""

from __future__ import annotations

import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.indicators.trend import (
    AdxData,
    AdxQueryParams,
    AroonData,
    AroonQueryParams,
    ChoppinessData,
    ChoppinessQueryParams,
    DiData,
    DiQueryParams,
    MacdData,
    MacdQueryParams,
    adx,
    aroon,
    choppiness,
    di,
    macd,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Convert the standard OHLCV fixture into ``list[Data]``."""
    return df_to_basemodel(ohlcv_df.reset_index())


class TestMacd:
    def test_default(self, long_records):
        result = macd(MacdQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, MacdData) for r in result.results)
        first = result.results[0]
        assert first.macd is not None
        assert first.signal is not None
        assert first.histogram is not None

    def test_custom_windows(self, long_records):
        result = macd(MacdQueryParams(data=long_records, fast=5, slow=13, signal=4))
        assert result.results


class TestAdx:
    def test_default(self, long_records):
        result = adx(AdxQueryParams(data=long_records, length=14))
        assert result.results
        assert all(isinstance(r, AdxData) for r in result.results)
        assert result.results[0].adx is not None

    def test_custom_scalar_and_drift(self, long_records):
        result = adx(AdxQueryParams(data=long_records, length=14, scalar=50.0, drift=2))
        assert result.results


class TestDi:
    def test_default(self, long_records):
        result = di(DiQueryParams(data=long_records, length=14))
        assert result.results
        assert all(isinstance(r, DiData) for r in result.results)
        first = result.results[0]
        assert first.plus_di is not None
        assert first.minus_di is not None
        assert first.dx is not None

    def test_custom_scalar(self, long_records):
        result = di(DiQueryParams(data=long_records, length=14, scalar=200.0, drift=1))
        assert result.results

    def test_dx_handles_zero_total(self):
        import numpy as np
        import pandas as pd

        idx = pd.date_range("2021-01-01", periods=50, freq="D", name="date")
        flat = np.full(50, 10.0)
        df = pd.DataFrame(
            {"open": flat, "high": flat, "low": flat, "close": flat, "volume": flat},
            index=idx,
        )
        records = df_to_basemodel(df.reset_index())
        result = di(DiQueryParams(data=records, length=14))
        assert result.results or result.results == []


class TestAroon:
    def test_default(self, long_records):
        result = aroon(AroonQueryParams(data=long_records, length=25))
        assert result.results
        assert all(isinstance(r, AroonData) for r in result.results)
        first = result.results[0]
        assert first.aroon_up is not None
        assert first.aroon_down is not None
        assert first.aroon_oscillator is not None

    def test_custom_scalar(self, long_records):
        result = aroon(AroonQueryParams(data=long_records, length=25, scalar=50.0))
        assert result.results


class TestChoppiness:
    def test_default(self, long_records):
        result = choppiness(ChoppinessQueryParams(data=long_records, length=14))
        assert result.results
        assert all(isinstance(r, ChoppinessData) for r in result.results)
        assert result.results[0].choppiness is not None

    def test_custom_atr_length_and_scalar(self, long_records):
        result = choppiness(
            ChoppinessQueryParams(
                data=long_records, length=14, atr_length=3, scalar=200.0
            )
        )
        assert result.results


class TestQueryParamModels:
    """Field-level coverage of the QueryParams classes."""

    def test_macd_defaults(self, long_records):
        params = MacdQueryParams(data=long_records)
        assert params.fast == 12
        assert params.slow == 26
        assert params.signal == 9
        assert params.target == "close"

    def test_adx_defaults(self, long_records):
        params = AdxQueryParams(data=long_records)
        assert params.length == 14
        assert params.scalar == 100.0
        assert params.drift == 1

    def test_di_defaults(self, long_records):
        params = DiQueryParams(data=long_records)
        assert params.length == 14
        assert params.scalar == 100.0
        assert params.drift == 1

    def test_aroon_defaults(self, long_records):
        params = AroonQueryParams(data=long_records)
        assert params.length == 25
        assert params.scalar == 100.0

    def test_choppiness_defaults(self, long_records):
        params = ChoppinessQueryParams(data=long_records)
        assert params.length == 14
        assert params.atr_length == 1
        assert params.scalar == 100.0
