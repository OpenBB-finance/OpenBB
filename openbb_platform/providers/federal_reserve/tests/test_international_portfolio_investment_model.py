"""Tests for the International Portfolio Investment fetcher model."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.international_portfolio_investment import (
    FederalReserveInternationalPortfolioInvestmentData,
    FederalReserveInternationalPortfolioInvestmentFetcher as Fetcher,
    FederalReserveInternationalPortfolioInvestmentQueryParams as QueryParams,
)
from openbb_federal_reserve.utils.ipi import TABLES

_CSV = (
    "Date,Africa,Asia; Japan,Asia; China\n"
    "Jan 2012,37.4,2910.7,--\n"
    "Feb 2012,40.0,2950.0,100.0\n"
)


def _patch(monkeypatch):
    """Point the table download at fixture CSV text."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ipi.fetch_ipi", lambda table: _CSV
    )


class TestExtractData:
    """Tests for the CSV download, melt, and filters."""

    def test_pivots_by_country(self, monkeypatch):
        """Each ``(date, country)`` becomes a row; the measure is the value column."""
        _patch(monkeypatch)
        measure = TABLES["table1"][1]
        query = Fetcher.transform_query({"table": "table1"})
        rows = Fetcher.extract_data(query, None)
        result = Fetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveInternationalPortfolioInvestmentData)
            for r in result
        )
        by_key = {(r.date, r.country): r.model_dump() for r in result}
        # The country dimension survives as a row-group column.
        assert by_key[(date(2012, 1, 1), "Asia; Japan")][measure] == 2910.7
        # "--" coerces to a missing value, leaving the row all-None, so it is
        # dropped rather than surfacing as a blank table row.
        assert (date(2012, 1, 1), "Asia; China") not in by_key
        # The same country surfaces once it carries a real observation.
        assert by_key[(date(2012, 2, 1), "Asia; China")][measure] == 100.0

    def test_country_filter(self, monkeypatch):
        """The country filter matches the term within the region path."""
        _patch(monkeypatch)
        query = Fetcher.transform_query({"table": "table1", "country": "japan"})
        rows = Fetcher.extract_data(query, None)
        assert {row["country"] for row in rows} == {"Asia; Japan"}

    def test_date_window_filters(self, monkeypatch):
        """The start- and end-date filters bound the returned observations."""
        _patch(monkeypatch)
        query = Fetcher.transform_query(
            {
                "table": "table1",
                "start_date": "2012-02-01",
                "end_date": "2012-02-29",
            }
        )
        rows = Fetcher.extract_data(query, None)
        assert rows
        assert all(row["date"] == date(2012, 2, 1) for row in rows)

    def test_empty_raises(self, monkeypatch):
        """A table with no data rows raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ipi.fetch_ipi", lambda table: "Date,Africa\n"
        )
        query = Fetcher.transform_query({"table": "table1"})
        with pytest.raises(EmptyDataError):
            Fetcher.extract_data(query, None)


class TestWidgetOptions:
    """Tests for the human-readable ``table`` dropdown labels."""

    def test_table_options_have_human_labels(self):
        """Every ``table`` code maps to a human label, not a bare code."""
        options = QueryParams.__json_schema_extra__["table"]["x-widget_config"][
            "options"
        ]
        # One option per published IPI table.
        assert {o["value"] for o in options} == set(TABLES)
        for option in options:
            assert option["label"] and option["label"] != option["value"]
            assert not option["label"].startswith("table")
