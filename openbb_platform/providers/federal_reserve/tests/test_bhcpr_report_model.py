"""Tests for the Federal Reserve BHCPR peer-group report viewer model."""

import pytest
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_federal_reserve.models.bhcpr_report import (
    FederalReserveBhcprReportData,
    FederalReserveBhcprReportFetcher,
)

_REPORTS = [
    {
        "name": "BHCPR_PeerGrp1_20240331.pdf",
        "url": "https://x/1q1.pdf",
        "peer_group": 1,
        "year": 2024,
        "quarter": 1,
        "period_end": "2024-03-31",
    },
    {
        "name": "BHCPR_PeerGrp1_20240630.pdf",
        "url": "https://x/1q2.pdf",
        "peer_group": 1,
        "year": 2024,
        "quarter": 2,
        "period_end": "2024-06-30",
    },
    {
        "name": "BHCPR_PeerGrp2_20240331.pdf",
        "url": "https://x/2q1.pdf",
        "peer_group": 2,
        "year": 2024,
        "quarter": 1,
        "period_end": "2024-03-31",
    },
    {
        "name": "BHCPR_PeerGrp1_20230331.pdf",
        "url": "https://x/1y23.pdf",
        "peer_group": 1,
        "year": 2023,
        "quarter": 1,
        "period_end": "2023-03-31",
    },
]


def _patch(monkeypatch):
    """Patch the BHCPR index to the fixture records."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.list_bhcpr_reports",
        lambda: list(_REPORTS),
    )


class TestTransformQuery:
    """Tests for query validation."""

    def test_defaults_to_peer_group_one(self):
        """The peer group defaults to '1'."""
        query = FederalReserveBhcprReportFetcher.transform_query({})
        assert query.peer_group == "1"

    def test_rejects_unknown_peer_group(self):
        """An unknown peer group raises a validation error."""
        with pytest.raises(ValidationError, match="Invalid peer group"):
            FederalReserveBhcprReportFetcher.transform_query({"peer_group": "7"})

    def test_none_peer_group_defaults_to_one(self):
        """An explicit null peer group falls back to '1'."""
        query = FederalReserveBhcprReportFetcher.transform_query({"peer_group": None})
        assert query.peer_group == "1"


class TestExtractData:
    """Tests for ``extract_data`` filtering."""

    def test_filters_by_peer_group(self, monkeypatch):
        """Only the requested peer group's reports are returned."""
        _patch(monkeypatch)
        query = FederalReserveBhcprReportFetcher.transform_query({"peer_group": "1"})
        rows = FederalReserveBhcprReportFetcher.extract_data(query, None)
        assert {r["peer_group"] for r in rows} == {1}

    def test_filters_by_year(self, monkeypatch):
        """The year filter narrows to a single reporting year."""
        _patch(monkeypatch)
        query = FederalReserveBhcprReportFetcher.transform_query(
            {"peer_group": "1", "year": 2024}
        )
        rows = FederalReserveBhcprReportFetcher.extract_data(query, None)
        assert {r["year"] for r in rows} == {2024}
        assert len(rows) == 2

    def test_no_match_raises(self, monkeypatch):
        """An empty result raises ``EmptyDataError``."""
        _patch(monkeypatch)
        query = FederalReserveBhcprReportFetcher.transform_query({"peer_group": "9"})
        with pytest.raises(EmptyDataError):
            FederalReserveBhcprReportFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data`` ordering and validation."""

    def test_sorts_newest_first(self, monkeypatch):
        """Reports are validated and sorted newest-first."""
        _patch(monkeypatch)
        query = FederalReserveBhcprReportFetcher.transform_query({"peer_group": "1"})
        rows = FederalReserveBhcprReportFetcher.extract_data(query, None)
        result = FederalReserveBhcprReportFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveBhcprReportData) for r in result)
        assert (result[0].year, result[0].quarter) == (2024, 2)
        assert result[0].period_end.isoformat() == "2024-06-30"
