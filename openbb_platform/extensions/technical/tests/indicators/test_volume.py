"""Tests for openbb_technical.indicators.volume."""

from __future__ import annotations

import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.indicators.volume import (
    AdData,
    AdoscData,
    AdoscQueryParams,
    AdQueryParams,
    ObvData,
    ObvQueryParams,
    VwapData,
    VwapQueryParams,
    ad,
    adosc,
    obv,
    vwap,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Convert the standard OHLCV fixture into ``list[Data]``."""
    return df_to_basemodel(ohlcv_df.reset_index())


class TestObv:
    def test_default(self, long_records):
        result = obv(ObvQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, ObvData) for r in result.results)
        assert result.results[0].obv is not None

    def test_offset(self, long_records):
        result = obv(ObvQueryParams(data=long_records, offset=1))
        assert result.results


class TestAd:
    def test_default(self, long_records):
        result = ad(AdQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, AdData) for r in result.results)
        assert result.results[0].ad is not None

    def test_offset(self, long_records):
        result = ad(AdQueryParams(data=long_records, offset=1))
        assert result.results


class TestAdosc:
    def test_default(self, long_records):
        result = adosc(AdoscQueryParams(data=long_records, fast=3, slow=10))
        assert result.results
        assert all(isinstance(r, AdoscData) for r in result.results)
        assert result.results[0].adosc is not None

    def test_offset(self, long_records):
        result = adosc(AdoscQueryParams(data=long_records, fast=3, slow=10, offset=1))
        assert result.results


class TestVwap:
    def test_default(self, long_records):
        result = vwap(VwapQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, VwapData) for r in result.results)
        assert result.results[0].vwap is not None

    @pytest.mark.parametrize("anchor", ["D", "W"])
    def test_each_anchor(self, long_records, anchor):
        result = vwap(VwapQueryParams(data=long_records, anchor=anchor))
        assert result.results

    def test_offset(self, long_records):
        result = vwap(VwapQueryParams(data=long_records, offset=1))
        assert result.results


class TestQueryParamModels:
    def test_obv_defaults(self, long_records):
        params = ObvQueryParams(data=long_records)
        assert params.index == "date"
        assert params.offset == 0

    def test_ad_defaults(self, long_records):
        params = AdQueryParams(data=long_records)
        assert params.offset == 0

    def test_adosc_defaults(self, long_records):
        params = AdoscQueryParams(data=long_records)
        assert params.fast == 3
        assert params.slow == 10

    def test_vwap_defaults(self, long_records):
        params = VwapQueryParams(data=long_records)
        assert params.anchor == "D"
