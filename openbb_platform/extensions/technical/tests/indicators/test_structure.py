"""Tests for openbb_technical.indicators.structure."""

from __future__ import annotations

import pytest
from openbb_core.app.utils import df_to_basemodel

from openbb_technical.indicators.structure import (
    DemarkData,
    DemarkQueryParams,
    FibData,
    FibQueryParams,
    PivotPointsData,
    PivotPointsQueryParams,
    demark,
    fib,
    pivot_points,
)


@pytest.fixture(scope="module")
def long_records(ohlcv_df):
    """Convert the standard OHLCV fixture into ``list[Data]``."""
    return df_to_basemodel(ohlcv_df.reset_index())


class TestFib:
    def test_default(self, long_records):
        result = fib(FibQueryParams(data=long_records, period=50))
        assert result.results
        assert all(isinstance(r, FibData) for r in result.results)
        assert result.results[0].level.endswith("%")

    def test_alternate_period(self, long_records):
        result = fib(FibQueryParams(data=long_records, period=30))
        assert result.results


class TestDemark:
    def test_default(self, long_records):
        result = demark(DemarkQueryParams(data=long_records))
        assert result.results
        assert all(isinstance(r, DemarkData) for r in result.results)

    def test_show_all_false(self, long_records):
        result = demark(DemarkQueryParams(data=long_records, show_all=False))
        assert result.results

    def test_asint_false(self, long_records):
        result = demark(DemarkQueryParams(data=long_records, asint=False))
        assert result.results

    def test_offset(self, long_records):
        result = demark(DemarkQueryParams(data=long_records, offset=1))
        assert result.results


class TestPivotPoints:
    @pytest.mark.parametrize(
        "method", ["classic", "fibonacci", "woodie", "camarilla", "demark"]
    )
    def test_each_method(self, long_records, method):
        result = pivot_points(PivotPointsQueryParams(data=long_records, method=method))
        assert result.results
        assert all(isinstance(r, PivotPointsData) for r in result.results)
        row = result.results[0]
        assert row.pivot is not None
        if method == "camarilla":
            assert row.r4 is not None
            assert row.s4 is not None
        else:
            assert row.r4 is None
            assert row.s4 is None

    @pytest.mark.parametrize("anchor", ["day", "week", "month"])
    def test_each_anchor(self, long_records, anchor):
        result = pivot_points(PivotPointsQueryParams(data=long_records, anchor=anchor))
        assert result.results

    def test_fibonacci_has_no_r4_s4(self, long_records):
        result = pivot_points(
            PivotPointsQueryParams(data=long_records, method="fibonacci")
        )
        assert all(r.r4 is None and r.s4 is None for r in result.results)

    def test_demark_has_no_r2_s2(self, long_records):
        result = pivot_points(
            PivotPointsQueryParams(data=long_records, method="demark")
        )
        assert all(r.r2 is None and r.s2 is None for r in result.results)


class TestQueryParamModels:
    def test_fib_defaults(self, long_records):
        params = FibQueryParams(data=long_records)
        assert params.period == 120
        assert params.close_column == "close"

    def test_demark_defaults(self, long_records):
        params = DemarkQueryParams(data=long_records)
        assert params.target == "close"
        assert params.show_all is True
        assert params.asint is True

    def test_pivot_points_defaults(self, long_records):
        params = PivotPointsQueryParams(data=long_records)
        assert params.method == "classic"
        assert params.anchor == "day"
