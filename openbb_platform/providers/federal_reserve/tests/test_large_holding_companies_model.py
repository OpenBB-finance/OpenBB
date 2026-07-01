"""Tests for the FFIEC Large Holding Companies fetcher model."""

from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.large_holding_companies import (
    FederalReserveLargeHoldingCompaniesData,
    FederalReserveLargeHoldingCompaniesFetcher,
)

_HOLDERS = [
    {
        "Rank": 2,
        "Name": "BANK OF AMERICA ",
        "RssdId": 1073757,
        "Location": "NC",
        "TotalAssets": 3.5e9,
        "Date": 20250331,
    },
    {
        "Rank": 1,
        "Name": "JPMORGAN CHASE & CO.",
        "RssdId": 1039502,
        "Location": "NY",
        "TotalAssets": 4.9e9,
        "Date": 20250331,
    },
]


def _patch(monkeypatch):
    """Patch the top-holders download to the fixture records."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_top_holders", lambda: list(_HOLDERS)
    )


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_sorts_by_rank_and_applies_limit(self, monkeypatch):
        """Records are sorted by rank and truncated to the limit."""
        _patch(monkeypatch)
        query = FederalReserveLargeHoldingCompaniesFetcher.transform_query({"limit": 1})
        rows = FederalReserveLargeHoldingCompaniesFetcher.extract_data(query, None)
        assert len(rows) == 1
        assert rows[0]["Rank"] == 1

    def test_empty_raises(self, monkeypatch):
        """An empty response raises ``EmptyDataError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_top_holders", lambda: []
        )
        query = FederalReserveLargeHoldingCompaniesFetcher.transform_query({})
        with pytest.raises(EmptyDataError):
            FederalReserveLargeHoldingCompaniesFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_maps_and_parses(self, monkeypatch):
        """Records map to the model with a parsed date and stripped name."""
        _patch(monkeypatch)
        query = FederalReserveLargeHoldingCompaniesFetcher.transform_query({})
        rows = FederalReserveLargeHoldingCompaniesFetcher.extract_data(query, None)
        result = FederalReserveLargeHoldingCompaniesFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReserveLargeHoldingCompaniesData) for r in result
        )
        assert result[0].rank == 1
        assert result[0].name == "JPMORGAN CHASE & CO."
        assert result[0].date == date(2025, 3, 31)
        assert result[0].total_assets == 4.9e12

    def test_invalid_total_assets_is_none(self, monkeypatch):
        """A missing or non-numeric total-assets value resolves to None."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_top_holders",
            lambda: [
                {"Rank": 1, "Name": "X", "RssdId": 1, "TotalAssets": "n/a"},
            ],
        )
        query = FederalReserveLargeHoldingCompaniesFetcher.transform_query({})
        rows = FederalReserveLargeHoldingCompaniesFetcher.extract_data(query, None)
        result = FederalReserveLargeHoldingCompaniesFetcher.transform_data(query, rows)
        assert result[0].total_assets is None
