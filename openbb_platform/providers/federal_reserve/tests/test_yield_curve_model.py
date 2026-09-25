"""Unit tests for the Federal Reserve Yield Curve fetcher."""

# ruff: noqa: I001

from datetime import date as dateType
from types import SimpleNamespace

import pytest

from openbb_federal_reserve.models.yield_curve import (
    FederalReserveYieldCurveData,
    FederalReserveYieldCurveFetcher,
    FederalReserveYieldCurveQueryParams,
    maturities,
)

CSV_BYTES = (
    b'"Series Description","1m","3m","6m","1y","2y","3y","5y","7y","10y","20y","30y"\n'
    b'"Unit:","Percent","Percent","Percent","Percent","Percent","Percent","Percent",'
    b'"Percent","Percent","Percent","Percent"\n'
    b'"Multiplier:","1","1","1","1","1","1","1","1","1","1","1"\n'
    b'"Currency:","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA","NA"\n'
    b'"Unique Identifier:","A","B","C","D","E","F","G","H","I","J","K"\n'
    b'"Time Period","M1","M3","M6","Y1","Y2","Y3","Y5","Y7","Y10","Y20","Y30"\n'
    b"2024-06-24,5.43,5.49,5.37,5.10,4.65,4.45,4.25,4.23,4.23,4.46,4.36\n"
    b"2024-06-25,5.44,5.50,5.38,5.11,4.66,4.46,4.26,4.24,4.24,4.47,4.37\n"
)


def _response() -> SimpleNamespace:
    """Return a stand-in HTTP response carrying the canned CSV bytes."""
    return SimpleNamespace(content=CSV_BYTES)


class TestFederalReserveYieldCurve:
    """Tests for the Yield Curve fetcher methods."""

    def test_transform_query_passes_through(self):
        """``transform_query`` builds the params model from a dict."""
        q = FederalReserveYieldCurveFetcher.transform_query({"date": "2024-06-24"})
        assert isinstance(q, FederalReserveYieldCurveQueryParams)
        assert q.date == "2024-06-24"

    def test_extract_data_parses_columns(self, monkeypatch):
        """The CSV parses into the canonical ``date`` + maturity columns."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveYieldCurveQueryParams(date="2024-06-24")
        df = FederalReserveYieldCurveFetcher.extract_data(q, None)
        assert list(df.columns) == ["date", *maturities]
        assert len(df) == 2

    def test_transform_data_explicit_date_scales_and_orders(self, monkeypatch):
        """An explicit date selects that curve, scaled and ordered by maturity."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveYieldCurveQueryParams(date="2024-06-24")
        df = FederalReserveYieldCurveFetcher.extract_data(q, None)
        out = FederalReserveYieldCurveFetcher.transform_data(q, df)
        assert len(out) == len(maturities)
        assert all(isinstance(d, FederalReserveYieldCurveData) for d in out)
        assert {d.date for d in out} == {dateType(2024, 6, 24)}
        assert [d.maturity for d in out] == maturities
        by_mat = {d.maturity: d.rate for d in out}
        assert by_mat["month_1"] == pytest.approx(0.0543)
        assert by_mat["year_30"] == pytest.approx(0.0436)

    def test_transform_data_defaults_to_latest_date(self, monkeypatch):
        """When no date is given the most recent curve is returned."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveYieldCurveQueryParams()
        df = FederalReserveYieldCurveFetcher.extract_data(q, None)
        out = FederalReserveYieldCurveFetcher.transform_data(q, df)
        assert {d.date for d in out} == {dateType(2024, 6, 25)}
        by_mat = {d.maturity: d.rate for d in out}
        assert by_mat["month_1"] == pytest.approx(0.0544)

    def test_transform_data_multiple_dates(self, monkeypatch):
        """Comma-separated dates return one curve per requested date."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveYieldCurveQueryParams(date="2024-06-24,2024-06-25")
        df = FederalReserveYieldCurveFetcher.extract_data(q, None)
        out = FederalReserveYieldCurveFetcher.transform_data(q, df)
        assert {d.date for d in out} == {dateType(2024, 6, 24), dateType(2024, 6, 25)}
        assert len(out) == 2 * len(maturities)
