"""Unit tests for the Federal Reserve Treasury Rates fetcher."""

# ruff: noqa: I001

from datetime import date as dateType, datetime, timedelta
from types import SimpleNamespace

import pytest

from openbb_federal_reserve.models.treasury_rates import (
    FederalReserveTreasuryRatesData,
    FederalReserveTreasuryRatesFetcher,
    FederalReserveTreasuryRatesQueryParams,
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
    b"2024-06-26,ND,ND,ND,ND,ND,ND,ND,ND,ND,ND,ND\n"
    b"2023-01-03,4.17,4.42,4.77,4.72,4.40,4.13,3.94,3.92,3.79,4.05,3.88\n"
)


def _response() -> SimpleNamespace:
    """Return a stand-in HTTP response carrying the canned CSV bytes."""
    return SimpleNamespace(content=CSV_BYTES)


class TestFederalReserveTreasuryRatesFetcher:
    """Tests for the Treasury Rates fetcher methods."""

    def test_transform_query_defaults_dates(self):
        """Missing dates default to a one-year lookback ending today."""
        q = FederalReserveTreasuryRatesFetcher.transform_query({})
        assert isinstance(q, FederalReserveTreasuryRatesQueryParams)
        now = datetime.now().date()
        assert q.end_date == now
        assert q.start_date == now - timedelta(days=365)

    def test_transform_query_respects_provided_dates(self):
        """Explicit start/end dates are passed through unchanged."""
        q = FederalReserveTreasuryRatesFetcher.transform_query(
            {"start_date": dateType(2024, 6, 24), "end_date": dateType(2024, 6, 25)}
        )
        assert q.start_date == dateType(2024, 6, 24)
        assert q.end_date == dateType(2024, 6, 25)

    def test_extract_data_parses_and_drops_all_nan_rows(self, monkeypatch):
        """The CSV is parsed, ``ND`` becomes NaN, and all-NaN rows are dropped."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveTreasuryRatesQueryParams()
        df = FederalReserveTreasuryRatesFetcher.extract_data(q, None)
        assert list(df.columns) == [
            "date",
            *[
                "month_1",
                "month_3",
                "month_6",
                "year_1",
                "year_2",
                "year_3",
                "year_5",
                "year_7",
                "year_10",
                "year_20",
                "year_30",
            ],
        ]
        assert "2024-06-26" not in set(df["date"])
        assert len(df) == 3

    def test_transform_data_filters_window_and_scales(self, monkeypatch):
        """The date window is applied and basis-point columns scale to decimals."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveTreasuryRatesQueryParams(
            start_date=dateType(2024, 6, 24), end_date=dateType(2024, 6, 25)
        )
        df = FederalReserveTreasuryRatesFetcher.extract_data(q, None)
        out = FederalReserveTreasuryRatesFetcher.transform_data(q, df)
        assert len(out) == 2
        assert all(isinstance(d, FederalReserveTreasuryRatesData) for d in out)
        first = next(d for d in out if d.date == dateType(2024, 6, 24))
        assert first.month_1 == pytest.approx(0.0543)
        assert first.year_30 == pytest.approx(0.0436)

    def test_transform_data_window_excludes_out_of_range(self, monkeypatch):
        """Rows outside the requested window are excluded."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _response(),
        )
        q = FederalReserveTreasuryRatesQueryParams(
            start_date=dateType(2024, 6, 24), end_date=dateType(2024, 6, 25)
        )
        df = FederalReserveTreasuryRatesFetcher.extract_data(q, None)
        out = FederalReserveTreasuryRatesFetcher.transform_data(q, df)
        assert dateType(2023, 1, 3) not in {d.date for d in out}
