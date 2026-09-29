"""Tests for the Money Market Funds Investment Holdings fetcher model."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.money_market_funds import (
    FederalReserveMoneyMarketFundsData,
    FederalReserveMoneyMarketFundsFetcher,
    FederalReserveMoneyMarketFundsQueryParams,
)
from openbb_federal_reserve.utils.mmf import TABLES

_TIME_SERIES = (
    '"Date","U.S. Government security repo (millions)","Other repo (millions)"\n'
    '"Dec 31, 2010",401199,130021\n'
    '"Jan 31, 2011",463967,120901\n'
)
_DETAIL = (
    '"Date","Country","By fund type; Total exposure; All MMFs","Prime"\n'
    '"Apr 30, 2026","Asia/Oceania; Japan","247114.4","100.0"\n'
    '"Apr 30, 2026","Europe","698158.4","293026.7"\n'
)


def _patch(monkeypatch, csv: str):
    """Point the table download at fixture CSV text."""
    monkeypatch.setattr("openbb_federal_reserve.utils.mmf.fetch_mmf", lambda table: csv)


class TestExtractData:
    """Tests for the CSV download, melt, and filters."""

    def test_time_series_table(self, monkeypatch):
        """A time-series table pivots to one row per date with category columns."""
        _patch(monkeypatch, _TIME_SERIES)
        query = FederalReserveMoneyMarketFundsFetcher.transform_query(
            {"table": "total"}
        )
        rows = FederalReserveMoneyMarketFundsFetcher.extract_data(query, None)
        result = FederalReserveMoneyMarketFundsFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveMoneyMarketFundsData) for r in result)
        by_date = {r.date: r for r in result}
        # One row per date; the "(millions)" suffix is stripped from the column.
        row = by_date[date(2010, 12, 31)]
        dumped = row.model_dump()
        assert dumped["U.S. Government security repo"] == 401199
        assert dumped["Other repo"] == 130021
        # Non-detail tables carry no country column at all.
        assert all("country" not in r.model_dump() for r in result)

    def test_detail_country_filter(self, monkeypatch):
        """The detail table carries a country, matched anywhere in the region path."""
        _patch(monkeypatch, _DETAIL)
        query = FederalReserveMoneyMarketFundsFetcher.transform_query(
            {"table": "detail", "country": "japan"}
        )
        rows = FederalReserveMoneyMarketFundsFetcher.extract_data(query, None)
        assert {row["country"] for row in rows} == {"Asia/Oceania; Japan"}
        assert any(
            row["label"] == "By fund type; Total exposure; All MMFs"
            and row["value"] == 247114.4
            for row in rows
        )

    def test_detail_pivots_wide_by_country(self, monkeypatch):
        """The detail table pivots to ``(date, country)`` rows with category columns."""
        _patch(monkeypatch, _DETAIL)
        query = FederalReserveMoneyMarketFundsFetcher.transform_query(
            {"table": "detail"}
        )
        rows = FederalReserveMoneyMarketFundsFetcher.extract_data(query, None)
        result = FederalReserveMoneyMarketFundsFetcher.transform_data(query, rows)
        by_country = {r.country: r for r in result}
        # The country dimension survives as a row-group column.
        assert set(by_country) == {"Asia/Oceania; Japan", "Europe"}
        japan = by_country["Asia/Oceania; Japan"].model_dump()
        assert japan["By fund type; Total exposure; All MMFs"] == 247114.4
        assert japan["Prime"] == 100.0

    def test_date_filter(self, monkeypatch):
        """The start-date filter drops earlier observations."""
        _patch(monkeypatch, _TIME_SERIES)
        query = FederalReserveMoneyMarketFundsFetcher.transform_query(
            {"table": "total", "start_date": "2011-01-01"}
        )
        rows = FederalReserveMoneyMarketFundsFetcher.extract_data(query, None)
        assert all(row["date"] >= date(2011, 1, 1) for row in rows)

    def test_end_date_filter(self, monkeypatch):
        """The end-date filter drops later observations."""
        _patch(monkeypatch, _TIME_SERIES)
        query = FederalReserveMoneyMarketFundsFetcher.transform_query(
            {"table": "total", "end_date": "2010-12-31"}
        )
        rows = FederalReserveMoneyMarketFundsFetcher.extract_data(query, None)
        assert all(row["date"] <= date(2010, 12, 31) for row in rows)

    def test_empty_raises(self, monkeypatch):
        """A table with no data rows raises ``EmptyDataError``."""
        _patch(monkeypatch, '"Date","X (millions)"\n')
        query = FederalReserveMoneyMarketFundsFetcher.transform_query(
            {"table": "total"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveMoneyMarketFundsFetcher.extract_data(query, None)


class TestWidgetOptions:
    """Tests for the human-readable ``table`` dropdown labels."""

    def test_table_options_have_human_labels(self):
        """Every MMF ``table`` code maps to a human label, not a bare code."""
        options = FederalReserveMoneyMarketFundsQueryParams.__json_schema_extra__[
            "table"
        ]["x-widget_config"]["options"]
        # One option per published MMF table.
        assert {o["value"] for o in options} == set(TABLES)
        for option in options:
            assert option["label"] and option["label"] != option["value"]
            assert "money market" in option["label"].lower()
