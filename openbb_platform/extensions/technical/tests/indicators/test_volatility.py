"""Tests for openbb_technical.indicators.volatility."""

from __future__ import annotations

import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.indicators.volatility import (
    _VOL_FUNCTIONS,
    AtrData,
    AtrQueryParams,
    ConesData,
    ConesQueryParams,
    RealizedVolatilityCompareData,
    RealizedVolatilityCompareQueryParams,
    RealizedVolatilityData,
    RealizedVolatilityQueryParams,
    atr,
    cones,
    realized_volatility,
    realized_volatility_compare,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Convert the standard OHLCV fixture into ``list[Data]``."""
    return df_to_basemodel(ohlcv_df.reset_index())


@pytest.fixture(scope="module")
def long_records_400():
    """OHLCV with 400 rows — enough for the longest cones window (360)."""
    import numpy as np
    import pandas as pd

    base = np.arange(1, 401, dtype="float64")
    df = pd.DataFrame(
        {
            "open": base,
            "high": base + 0.5,
            "low": base - 0.5,
            "close": base,
            "volume": base * 100,
        },
        index=pd.date_range("2020-01-01", periods=400, freq="D", name="date"),
    )
    return df_to_basemodel(df.reset_index())


class TestRealizedVolatility:
    @pytest.mark.parametrize("model", list(_VOL_FUNCTIONS.keys()))
    def test_each_model_returns_data(self, long_records, model):
        result = realized_volatility(
            RealizedVolatilityQueryParams(data=long_records, model=model, window=20)
        )
        assert result.results
        assert all(isinstance(r, RealizedVolatilityData) for r in result.results)
        assert result.results[0].model == model

    def test_is_crypto_uses_365(self, long_records):
        result = realized_volatility(
            RealizedVolatilityQueryParams(
                data=long_records, model="std", is_crypto=True, window=20
            )
        )
        assert result.results[0].trading_periods == 365

    def test_explicit_trading_periods_override(self, long_records):
        result = realized_volatility(
            RealizedVolatilityQueryParams(
                data=long_records, model="std", trading_periods=200, window=20
            )
        )
        assert result.results[0].trading_periods == 200

    def test_clean_false_keeps_warmup_rows(self, long_records):
        cleaned = realized_volatility(
            RealizedVolatilityQueryParams(
                data=long_records, model="std", window=20, clean=True
            )
        )
        raw = realized_volatility(
            RealizedVolatilityQueryParams(
                data=long_records, model="std", window=20, clean=False
            )
        )
        assert len(raw.results) > len(cleaned.results)

    def test_window_below_two_rejected_for_ht(self, long_records):
        with pytest.raises(ValueError, match="hodges_tompkins requires window"):
            RealizedVolatilityQueryParams(
                data=long_records, model="hodges_tompkins", window=1
            )

    def test_window_below_two_rejected_for_yz(self, long_records):
        with pytest.raises(ValueError, match="yang_zhang requires window"):
            RealizedVolatilityQueryParams(
                data=long_records, model="yang_zhang", window=1
            )


class TestRealizedVolatilityCompare:
    def test_default_includes_all_models(self, long_records):
        result = realized_volatility_compare(
            RealizedVolatilityCompareQueryParams(data=long_records, window=20)
        )
        row = result.results[0]
        assert isinstance(row, RealizedVolatilityCompareData)
        assert row.std is not None
        assert row.yang_zhang is not None

    def test_subset_of_models(self, long_records):
        result = realized_volatility_compare(
            RealizedVolatilityCompareQueryParams(
                data=long_records, models=["std", "parkinson"], window=20
            )
        )
        assert result.results
        row = result.results[0]
        assert row.std is not None
        assert row.parkinson is not None
        assert row.garman_klass is None

    def test_clean_false_keeps_warmup(self, long_records):
        cleaned = realized_volatility_compare(
            RealizedVolatilityCompareQueryParams(
                data=long_records, window=20, clean=True
            )
        )
        raw = realized_volatility_compare(
            RealizedVolatilityCompareQueryParams(
                data=long_records, window=20, clean=False
            )
        )
        assert len(raw.results) >= len(cleaned.results)


class TestCones:
    def test_default_table(self, long_records_400):
        result = cones(ConesQueryParams(data=long_records_400))
        assert result.results
        assert all(isinstance(r, ConesData) for r in result.results)
        first = result.results[0]
        assert first.window > 0
        assert first.lower is not None
        assert first.upper is not None

    @pytest.mark.parametrize("model", list(_VOL_FUNCTIONS.keys()))
    def test_each_model(self, long_records_400, model):
        result = cones(ConesQueryParams(data=long_records_400, model=model))
        assert result.results

    def test_is_crypto_branch(self, long_records_400):
        result = cones(ConesQueryParams(data=long_records_400, is_crypto=True))
        assert result.results

    def test_explicit_trading_periods(self, long_records_400):
        result = cones(ConesQueryParams(data=long_records_400, trading_periods=200))
        assert result.results


class TestAtr:
    def test_default(self, long_records):
        result = atr(AtrQueryParams(data=long_records, length=14))
        assert result.results
        assert all(isinstance(r, AtrData) for r in result.results)
        assert result.results[0].atr is not None

    @pytest.mark.parametrize("mamode", ["sma", "ema", "wma", "rma"])
    def test_each_mamode(self, long_records, mamode):
        result = atr(AtrQueryParams(data=long_records, length=14, mamode=mamode))
        assert result.results

    def test_drift_and_offset(self, long_records):
        result = atr(AtrQueryParams(data=long_records, length=14, drift=2, offset=1))
        assert result.results


class TestQueryParamModels:
    """Field-level coverage of the QueryParams classes."""

    def test_realized_volatility_defaults(self, long_records):
        params = RealizedVolatilityQueryParams(data=long_records)
        assert params.model == "yang_zhang"
        assert params.window == 30
        assert params.is_crypto is False

    def test_compare_defaults_include_all_models(self, long_records):
        params = RealizedVolatilityCompareQueryParams(data=long_records)
        assert set(params.models) == set(_VOL_FUNCTIONS.keys())

    def test_cones_defaults(self, long_records_400):
        params = ConesQueryParams(data=long_records_400)
        assert params.lower_q == 0.25
        assert params.upper_q == 0.75
        assert params.model == "std"

    def test_atr_defaults(self, long_records):
        params = AtrQueryParams(data=long_records)
        assert params.length == 14
        assert params.mamode == "rma"
