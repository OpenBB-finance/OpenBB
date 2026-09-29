"""Tests for the FFIEC UBPR Peer Group Average Distribution model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.peer_group_distribution import (
    FederalReservePeerGroupDistributionData,
    FederalReservePeerGroupDistributionFetcher,
)

_ROWS = [
    {"label": "Percent of Average Assets:", "is_header": True},
    {
        "label": ">   Interest Income (TE)",
        "is_header": False,
        "1ST": 2.32,
        "50TH": 4.34,
        "99TH": 6.58,
        "TRIMMED AVERAGE": 4.43,
    },
    {
        "label": ">   - Interest Expense",
        "is_header": False,
        "1ST": 0.33,
        "50TH": 1.74,
        "99TH": 3.91,
        "TRIMMED AVERAGE": 1.93,
    },
]

_CYCLES = [
    {"reportingcycleid": "151", "enddateformatted": "03/31/2026"},
    {"reportingcycleid": "150", "enddateformatted": "12/31/2025"},
    {"reportingcycleid": "149", "enddateformatted": "09/30/2025"},
]


def _patch_fetch(monkeypatch, captured):
    """Patch ``fetch_distribution`` to capture its args and return fixtures."""

    def _fake(peer_group, section, *, cycle_id=None):
        captured["peer_group"] = peer_group
        captured["section"] = section
        captured["cycle_id"] = cycle_id
        return {
            "section": section,
            "period": "2026-03-31",
            "peer_group": peer_group.upper(),
            "rows": list(_ROWS),
        }

    monkeypatch.setattr(
        "openbb_federal_reserve.utils.peer_group_distribution.fetch_distribution",
        _fake,
    )


def _patch_cycles(monkeypatch):
    """Patch ``report_cycles`` to the fixture cycle list."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ubpr_report.report_cycles",
        lambda: list(_CYCLES),
    )


class TestTransformQuery:
    """Tests for query validation."""

    def test_defaults(self):
        """Peer group and section default to '1' and Summary Ratios."""
        query = FederalReservePeerGroupDistributionFetcher.transform_query({})
        assert query.peer_group == "1"
        assert query.section == "Summary Ratios"

    def test_named_peer_group_accepted(self):
        """A named peer group key is accepted."""
        query = FederalReservePeerGroupDistributionFetcher.transform_query(
            {"peer_group": "NATIONAL"}
        )
        assert query.peer_group == "NATIONAL"

    def test_rejects_unknown_peer_group(self):
        """An unknown peer group raises an error."""
        with pytest.raises(OpenBBError, match="Unknown peer group"):
            FederalReservePeerGroupDistributionFetcher.transform_query(
                {"peer_group": "999"}
            )


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_passes_peer_group_and_section(self, monkeypatch):
        """The peer group and section reach the client unchanged."""
        captured: dict = {}
        _patch_fetch(monkeypatch, captured)
        query = FederalReservePeerGroupDistributionFetcher.transform_query(
            {"peer_group": "1", "section": "Capital Analysis-a"}
        )
        rows = FederalReservePeerGroupDistributionFetcher.extract_data(query, None)
        assert captured["peer_group"] == "1"
        assert captured["section"] == "Capital Analysis-a"
        assert captured["cycle_id"] is None
        assert len(rows) == 3

    def test_resolves_period_to_cycle_id(self, monkeypatch):
        """A period date is resolved to its reporting-cycle id."""
        captured: dict = {}
        _patch_fetch(monkeypatch, captured)
        _patch_cycles(monkeypatch)
        query = FederalReservePeerGroupDistributionFetcher.transform_query(
            {"peer_group": "1", "period": "2025-12-31"}
        )
        FederalReservePeerGroupDistributionFetcher.extract_data(query, None)
        assert captured["cycle_id"] == "150"

    def test_unknown_period_passes_none(self, monkeypatch):
        """A period with no matching cycle resolves to ``None``."""
        captured: dict = {}
        _patch_fetch(monkeypatch, captured)
        _patch_cycles(monkeypatch)
        query = FederalReservePeerGroupDistributionFetcher.transform_query(
            {"peer_group": "1", "period": "1999-01-01"}
        )
        FederalReservePeerGroupDistributionFetcher.extract_data(query, None)
        assert captured["cycle_id"] is None

    def test_empty_rows_raises(self, monkeypatch):
        """An empty grid raises ``EmptyDataError``."""

        def _empty(peer_group, section, *, cycle_id=None):
            return {"section": section, "period": "", "peer_group": "", "rows": []}

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.peer_group_distribution.fetch_distribution",
            _empty,
        )
        query = FederalReservePeerGroupDistributionFetcher.transform_query(
            {"peer_group": "1"}
        )
        with pytest.raises(EmptyDataError):
            FederalReservePeerGroupDistributionFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data`` validation."""

    def test_validates_rows(self, monkeypatch):
        """Rows validate into the data model with dynamic percentile fields."""
        captured: dict = {}
        _patch_fetch(monkeypatch, captured)
        query = FederalReservePeerGroupDistributionFetcher.transform_query(
            {"peer_group": "1"}
        )
        rows = FederalReservePeerGroupDistributionFetcher.extract_data(query, None)
        result = FederalReservePeerGroupDistributionFetcher.transform_data(query, rows)
        assert all(
            isinstance(r, FederalReservePeerGroupDistributionData) for r in result
        )
        assert result[0].is_header is True
        dumped = result[1].model_dump()
        assert dumped["50TH"] == 4.34
        assert dumped["TRIMMED AVERAGE"] == 4.43
