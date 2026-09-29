"""Tests for the FFIEC UBPR Custom Peer Group (CPG, CDR router) model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.custom_peer_group import (
    FederalReserveCustomPeerGroupData,
    FederalReserveCustomPeerGroupFetcher,
)
from openbb_federal_reserve.utils import custom_peer_group as cpg

_BANK = "JPMorgan Chase Bank, National Association"

_SECTION = {
    "section": "Summary Ratios",
    "rows": [
        {"label": "Earnings and Profitability", "is_header": True},
        {
            "label": ">  Interest Income (TE)",
            "is_header": False,
            f"2025-12-31 {_BANK}": 4.52,
        },
        {
            "label": "Net Income",
            "is_header": False,
            f"2025-12-31 {_BANK}": 1.31,
        },
    ],
}


def _patch(monkeypatch, result=None, resolved=None):
    """Point the section fetch and the lead-bank resolver at in-memory fixtures."""
    source = _SECTION if result is None else result
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.custom_peer_group.fetch_custom_peer_group",
        lambda rssd_id, peers, section, all_periods=False: {
            "section": source["section"],
            "rows": [dict(row) for row in source["rows"]],
        },
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ticker.resolve_rssd_to_bank",
        lambda rssd_id: resolved if resolved is not None else (str(rssd_id), None),
    )


class TestTransformQuery:
    """Tests for ``transform_query``."""

    def test_requires_identifier(self):
        """Omitting both symbol and rssd_id raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveCustomPeerGroupFetcher.transform_query({"peers": "1,2"})

    def test_requires_peers(self):
        """Omitting the peer list raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveCustomPeerGroupFetcher.transform_query({"rssd_id": "451965"})

    def test_default_section(self):
        """The section defaults to Summary Ratios and is a known section."""
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "451965", "peers": "451965,480228"}
        )
        assert query.section == "Summary Ratios"
        assert query.section in cpg.UBPR_SECTIONS


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_returns_section_rows(self, monkeypatch):
        """The section's rows pass through from the router client."""
        _patch(monkeypatch)
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "451965", "peers": "451965,480228"}
        )
        assert len(FederalReserveCustomPeerGroupFetcher.extract_data(query, None)) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty section raises ``EmptyDataError``."""
        _patch(monkeypatch, {"section": "Summary Ratios", "rows": []})
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "451965", "peers": "451965,480228"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveCustomPeerGroupFetcher.extract_data(query, None)

    def test_symbol_resolves_to_rssd(self, monkeypatch):
        """A ticker resolves to an RSSD before the section fetch."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: "451965",
        )
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"symbol": "WFC", "peers": "451965,480228"}
        )
        assert len(FederalReserveCustomPeerGroupFetcher.extract_data(query, None)) == 3

    def test_unresolved_symbol_raises(self, monkeypatch):
        """A ticker that resolves to nothing raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: None,
        )
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"symbol": "ZZZ", "peers": "451965,480228"}
        )
        with pytest.raises(OpenBBError):
            FederalReserveCustomPeerGroupFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_wide_rows(self, monkeypatch):
        """Line items carry a per-period bank-name column; headers carry a label."""
        _patch(monkeypatch)
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "451965", "peers": "451965,480228"}
        )
        rows = FederalReserveCustomPeerGroupFetcher.extract_data(query, None)
        result = FederalReserveCustomPeerGroupFetcher.transform_data(query, rows)
        out = result.result or []
        assert all(isinstance(r, FederalReserveCustomPeerGroupData) for r in out)
        line = next(r for r in out if not r.is_header)
        assert line.model_dump()[f"2025-12-31 {_BANK}"] == 4.52
        assert line.label.startswith(">")  # indentation guarded
        header = next(r for r in out if r.is_header)
        assert header.label == "Earnings and Profitability"

    def test_bank_rssd_surfaces_only_its_rssd(self, monkeypatch):
        """A bank RSSD that already files surfaces only its own RSSD in metadata."""
        _patch(monkeypatch)
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "451965", "peers": "451965,480228"}
        )
        rows = FederalReserveCustomPeerGroupFetcher.extract_data(query, None)
        result = FederalReserveCustomPeerGroupFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata["rssd_id"] == "451965"
        assert "name" not in metadata
        assert metadata["section"] == "Summary Ratios"

    def test_holding_company_resolves_and_surfaces_bank(self, monkeypatch):
        """A holding-company RSSD resolves to its lead bank, surfaced in metadata."""
        _patch(monkeypatch, resolved=("852218", "JPMORGAN CHASE BANK NA"))
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "1039502", "peers": "1039502,480228"}
        )
        rows = FederalReserveCustomPeerGroupFetcher.extract_data(query, None)
        result = FederalReserveCustomPeerGroupFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata["rssd_id"] == "852218"
        assert metadata["name"] == "JPMORGAN CHASE BANK NA"

    def test_no_bank_report_shell_raises(self, monkeypatch):
        """A resolved RSSD whose rows carry no period values raises the bank error."""
        _patch(
            monkeypatch,
            {
                "section": "Summary Ratios",
                "rows": [
                    {"label": "Earnings and Profitability", "is_header": True},
                    {
                        "label": "Net Income",
                        "is_header": False,
                        "narrative": "Net income for the period.",
                        f"2025-12-31 {_BANK}": None,
                    },
                ],
            },
        )
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "2162966", "peers": "2162966,480228"}
        )
        with pytest.raises(OpenBBError) as exc:
            FederalReserveCustomPeerGroupFetcher.extract_data(query, None)
        assert "No UBPR data for RSSD 2162966" in str(exc.value)

    def test_empty_data_validates_without_metadata(self):
        """An empty parsed-row list validates to an empty result with no bank."""
        query = FederalReserveCustomPeerGroupFetcher.transform_query(
            {"rssd_id": "451965", "peers": "451965,480228"}
        )
        result = FederalReserveCustomPeerGroupFetcher.transform_data(query, [])
        assert result.result == []
        assert result.metadata == {"section": "Summary Ratios"}
