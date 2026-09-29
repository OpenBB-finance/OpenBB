"""Tests for the FFIEC UBPR Peer Group Bank Report (CDR router) model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.peer_group_bank import (
    PEER_GROUP_BANK_SECTIONS,
    FederalReservePeerGroupBankData,
    FederalReservePeerGroupBankFetcher,
    _page_id,
    _peer_group_banks,
    _peer_group_name,
    fetch_peer_group_bank_report,
)


def _run_producer(monkeypatch):
    """Make ``cache.cached`` execute the producer against in-memory fixtures."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.cache.cached",
        lambda key, ttl, producer: producer(),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.cache.seconds_until_next_release",
        lambda cadence, **kwargs: 0.0,
    )


_COL_A = "WELLS FARGO BANK, NATIONAL ASSOCIATION (451965)"
_COL_B = "REGIONS BANK (233031)"

_SECTION = {
    "section": "Summary Ratios",
    "peer_group": "Insured commercial banks having assets greater than $100 billion",
    "columns": [_COL_A, _COL_B],
    "rows": [
        {"label": "Earnings and Profitability", "is_header": True},
        {
            "label": ">  Interest Income (TE)",
            "is_header": False,
            _COL_A: 4.28,
            _COL_B: 4.34,
        },
        {
            "label": "Net Interest Income (TE)",
            "is_header": False,
            _COL_A: 2.88,
            _COL_B: 3.23,
        },
    ],
}


def _patch(monkeypatch, result=None, resolved=None):
    """Point the section fetch and the lead-bank resolver at in-memory fixtures."""
    source = _SECTION if result is None else result
    monkeypatch.setattr(
        "openbb_federal_reserve.models.peer_group_bank.fetch_peer_group_bank_report",
        lambda rssd_id, section: {**source, "rows": [dict(r) for r in source["rows"]]},
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
            FederalReservePeerGroupBankFetcher.transform_query({})

    def test_default_section(self):
        """The section defaults to Summary Ratios and is a known section."""
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        assert query.section == "Summary Ratios"
        assert query.section in PEER_GROUP_BANK_SECTIONS


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_returns_section_rows(self, monkeypatch):
        """The section's rows pass through from the router client."""
        _patch(monkeypatch)
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        assert len(FederalReservePeerGroupBankFetcher.extract_data(query, None)) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty section raises ``EmptyDataError``."""
        _patch(
            monkeypatch,
            {"section": "Summary Ratios", "peer_group": "", "columns": [], "rows": []},
        )
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        with pytest.raises(EmptyDataError):
            FederalReservePeerGroupBankFetcher.extract_data(query, None)

    def test_symbol_resolves_to_rssd(self, monkeypatch):
        """A ticker resolves to an RSSD before the section fetch."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: "451965",
        )
        query = FederalReservePeerGroupBankFetcher.transform_query({"symbol": "WFC"})
        assert len(FederalReservePeerGroupBankFetcher.extract_data(query, None)) == 3

    def test_unresolved_symbol_raises(self, monkeypatch):
        """A ticker that resolves to nothing raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: None,
        )
        query = FederalReservePeerGroupBankFetcher.transform_query({"symbol": "ZZZ"})
        with pytest.raises(OpenBBError):
            FederalReservePeerGroupBankFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_wide_rows(self, monkeypatch):
        """Line items carry per-bank columns; headers carry only a label."""
        _patch(monkeypatch)
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        rows = FederalReservePeerGroupBankFetcher.extract_data(query, None)
        result = FederalReservePeerGroupBankFetcher.transform_data(query, rows)
        out = result.result or []
        assert all(isinstance(r, FederalReservePeerGroupBankData) for r in out)
        line = next(r for r in out if not r.is_header)
        assert line.model_dump()[_COL_A] == 4.28
        assert line.label.startswith(">")  # indentation guarded
        header = next(r for r in out if r.is_header)
        assert header.label == "Earnings and Profitability"

    def test_bank_rssd_surfaces_only_its_rssd(self, monkeypatch):
        """A bank RSSD that already files surfaces only its own RSSD in metadata."""
        _patch(monkeypatch)
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        rows = FederalReservePeerGroupBankFetcher.extract_data(query, None)
        result = FederalReservePeerGroupBankFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata["rssd_id"] == "451965"
        assert "name" not in metadata
        assert metadata["section"] == "Summary Ratios"

    def test_holding_company_resolves_and_surfaces_bank(self, monkeypatch):
        """A holding-company RSSD resolves to its lead bank, surfaced in metadata."""
        _patch(monkeypatch, resolved=("852218", "JPMORGAN CHASE BANK NA"))
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "1039502"}
        )
        rows = FederalReservePeerGroupBankFetcher.extract_data(query, None)
        result = FederalReservePeerGroupBankFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata["rssd_id"] == "852218"
        assert metadata["name"] == "JPMORGAN CHASE BANK NA"

    def test_empty_data_validates_without_metadata(self):
        """An empty parsed-row list validates to an empty result with no bank."""
        query = FederalReservePeerGroupBankFetcher.transform_query(
            {"rssd_id": "451965"}
        )
        result = FederalReservePeerGroupBankFetcher.transform_data(query, [])
        assert result.result == []
        assert result.metadata == {"section": "Summary Ratios"}


class TestFetchPeerGroupBankReport:
    """Tests for ``fetch_peer_group_bank_report`` enrichment."""

    _INDEX = {
        "UBPRE001": {
            "name": "Interest Inc (TE)",
            "narrative": None,
            "monetary": False,
        },
        "UBPR1410": {
            "name": "Loans Secured by Real Estate",
            "narrative": None,
            "monetary": False,
        },
        "RIAD4065": {
            "name": "Income From Lease Financing Receivables",
            "narrative": "Includes amortized income from direct and leveraged financing leases.",
            "monetary": True,
        },
    }

    _GUIDE = {
        "UBPRE001": {
            "description": "Interest Income (TE) as a percent of Average Assets",
            "narrative": "Total interest income on a tax-equivalent basis.",
        },
        "UBPR1410": {
            "description": "Loans Secured by Real Estate",
            "narrative": "Loans secured by real estate.",
        },
        "RIAD4065": {
            "description": "Income From Lease Financing Receivables",
            "narrative": None,
        },
    }

    _RAW = [
        {
            "linecaption": "#SectionTitle#Earnings and Profitability",
            "conceptname": "",
            "00_451965": "",
        },
        {
            "linecaption": "  Interest Income (TE)",
            "conceptname": "UBPRE001",
            "datatypeid": "96",
            "00_451965": "4.28",
        },
        {
            "linecaption": "Real Estate Loans",
            "conceptname": "UBPR1410",
            "datatypeid": "155",
            "00_451965": "504275000",
        },
        {
            "linecaption": "Income From Lease Financing",
            "conceptname": "RIAD4065",
            "datatypeid": "155",
            "00_451965": "12345000",
        },
    ]

    def _patch(self, monkeypatch):
        """Patch every network boundary for an offline section fetch."""
        module = "openbb_federal_reserve.models.peer_group_bank"
        monkeypatch.setattr(
            f"{module}._page_id", lambda section: ("PG-1", "Summary Ratios")
        )
        monkeypatch.setattr(
            f"{module}._peer_group_name",
            lambda rssd_id, cycle_id: ("PG-1", "Big banks"),
        )
        monkeypatch.setattr(
            f"{module}._peer_group_banks",
            lambda peer_group_name, cycle_id: [
                {"rssd": "451965", "name": "WELLS FARGO"}
            ],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [
                {
                    "reportingcycleid": "151",
                    "enddateformatted": "03/31/2026",
                }
            ],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: (
                [{"sectionid": "1"}]
                if requestor_id == "MBReportPageSections"
                else self._RAW
            ),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda product, form_type: self._INDEX,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                c: self._GUIDE[c] for c in concepts if c in self._GUIDE
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )

    def test_line_uses_guide_description_and_narrative(self, monkeypatch):
        """A line item gets the cleaned guide Description label and guide narrative."""
        self._patch(monkeypatch)
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        col = "WELLS FARGO (451965)"
        header = result["rows"][0]
        line = result["rows"][1]
        assert header["label"] == "Earnings and Profitability"
        assert line["label"].startswith(">")
        assert line["label"].endswith("Interest Income (TE)")
        assert line["narrative"] == "Total interest income on a tax-equivalent basis."
        assert line[col] == 4.28

    def test_leading_header_carries_page_description(self, monkeypatch):
        """The leading header row's narrative is the section's UBPR page description."""
        from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

        self._patch(monkeypatch)
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        header = result["rows"][0]
        assert header["is_header"] is True
        assert all(header.get(c) is None for c in ("WELLS FARGO (451965)",))
        assert header["narrative"] == UBPR_PAGE_DESCRIPTIONS["Summary Ratios"]
        line = result["rows"][1]
        assert line["narrative"] == "Total interest income on a tax-equivalent basis."

    def test_monetary_datatype_scales_ratio_does_not(self, monkeypatch):
        """A dollar line (``datatypeid`` 155) scales x1000; a ratio line does not."""
        self._patch(monkeypatch)
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        col = "WELLS FARGO (451965)"
        ratio = next(
            r for r in result["rows"] if r["label"].endswith("Interest Income (TE)")
        )
        dollars = next(r for r in result["rows"] if r["label"].endswith("Real Estate"))
        assert ratio[col] == 4.28
        assert dollars[col] == 504275000 * 1000

    def test_call_sourced_line_falls_back_to_concept_index_narrative(self, monkeypatch):
        """A Call-sourced (RIAD) line with no guide narrative uses the concept-index
        narrative, while a UBPR concept keeps its guide narrative."""
        self._patch(monkeypatch)
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        call_line = next(r for r in result["rows"] if "Lease Financing" in r["label"])
        ubpr_line = next(
            r for r in result["rows"] if r["label"].endswith("Interest Income (TE)")
        )
        assert call_line["narrative"] == (
            "Includes amortized income from direct and leveraged financing leases."
        )
        assert ubpr_line["narrative"] == (
            "Total interest income on a tax-equivalent basis."
        )


class TestPeerGroupName:
    """Tests for the ``_peer_group_name`` helper."""

    def test_returns_name_and_description(self, monkeypatch):
        """The first FiAttributes row yields the peer group name and description."""
        _run_producer(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: [
                {"peergroupname": "PG-1", "peergroupdescription": "Big banks"}
            ],
        )
        assert _peer_group_name("451965", "151") == ("PG-1", "Big banks")

    def test_missing_keys_default_to_empty(self, monkeypatch):
        """Absent peergroup keys coerce to empty strings."""
        _run_producer(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: [{}],
        )
        assert _peer_group_name("451965", "151") == ("", "")

    def test_empty_rows_raise(self, monkeypatch):
        """No FiAttributes rows means no assigned peer group, which raises."""
        _run_producer(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: [],
        )
        with pytest.raises(OpenBBError):
            _peer_group_name("451965", "151")


class TestPeerGroupBanks:
    """Tests for the ``_peer_group_banks`` helper."""

    def test_trims_roster_and_skips_invalid_rows(self, monkeypatch):
        """Valid rows yield stripped rssd/name records; non-dicts and blanks drop."""
        _run_producer(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: [
                {"rssd9001": " 451965 ", "rssd9017": " WELLS FARGO "},
                {"rssd9001": "", "rssd9017": "EMPTY"},
                "not-a-dict",
            ],
        )
        banks = _peer_group_banks("PG-1", "151")
        assert banks == [{"rssd": "451965", "name": "WELLS FARGO"}]


class TestPageId:
    """Tests for the ``_page_id`` section resolver."""

    _SECTIONS = [
        {"pageid": "pg-1", "pagetitle": "Summary Ratios"},
        {"pageid": "pg-2", "pagetitle": "Balance Sheet $"},
    ]

    def test_matches_by_title(self, monkeypatch):
        """A section title resolves to its ``(pageid, title)``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: self._SECTIONS,
        )
        assert _page_id("Balance Sheet $") == ("pg-2", "Balance Sheet $")

    def test_matches_by_pageid(self, monkeypatch):
        """A raw pageid resolves to its ``(pageid, title)``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: self._SECTIONS,
        )
        assert _page_id("pg-1") == ("pg-1", "Summary Ratios")

    def test_blank_target_returns_first(self, monkeypatch):
        """An empty/None section returns the first section."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: self._SECTIONS,
        )
        assert _page_id(None) == ("pg-1", "Summary Ratios")

    def test_empty_sections_raise(self, monkeypatch):
        """An empty section list raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: [],
        )
        with pytest.raises(OpenBBError):
            _page_id("Summary Ratios")

    def test_unknown_section_raises(self, monkeypatch):
        """An unrecognized section raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: self._SECTIONS,
        )
        with pytest.raises(OpenBBError):
            _page_id("No Such Section")


class TestFetchReportBranches:
    """Tests for the error and skip branches of ``fetch_peer_group_bank_report``."""

    def test_no_cycles_raises(self, monkeypatch):
        """An empty reporting-cycle list raises ``OpenBBError``."""
        module = "openbb_federal_reserve.models.peer_group_bank"
        monkeypatch.setattr(
            f"{module}._page_id", lambda section: ("PG-1", "Summary Ratios")
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles", lambda: []
        )
        with pytest.raises(OpenBBError):
            fetch_peer_group_bank_report("451965", "Summary Ratios")

    def _patch_common(self, monkeypatch):
        """Patch the cycle, page, and cache seams shared by the branch tests."""
        module = "openbb_federal_reserve.models.peer_group_bank"
        monkeypatch.setattr(
            f"{module}._page_id", lambda section: ("PG-1", "Summary Ratios")
        )
        monkeypatch.setattr(
            f"{module}._peer_group_name",
            lambda rssd_id, cycle_id: ("PG-1", "Big banks"),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": "151", "enddateformatted": "03/31/2026"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )

    def test_empty_banks_returns_empty_section(self, monkeypatch):
        """A peer group with no member banks returns an empty section."""
        self._patch_common(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.models.peer_group_bank._peer_group_banks",
            lambda peer_group_name, cycle_id: [],
        )
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        assert result == {
            "section": "Summary Ratios",
            "peer_group": "Big banks",
            "columns": [],
            "rows": [],
        }

    def test_empty_lines_returns_empty_section(self, monkeypatch):
        """No line rows from the section data producer returns an empty section."""
        self._patch_common(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.models.peer_group_bank._peer_group_banks",
            lambda peer_group_name, cycle_id: [
                {"rssd": "451965", "name": "WELLS FARGO"}
            ],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: (
                [{"sectionid": "1"}] if requestor_id == "MBReportPageSections" else []
            ),
        )
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        assert result == {
            "section": "Summary Ratios",
            "peer_group": "Big banks",
            "columns": [],
            "rows": [],
        }

    def test_blank_line_skipped_and_unparseable_value_is_none(self, monkeypatch):
        """``#BlankLine#`` rows drop; a non-numeric monetary value becomes ``None``."""
        self._patch_common(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.models.peer_group_bank._peer_group_banks",
            lambda peer_group_name, cycle_id: [
                {"rssd": "451965", "name": "WELLS FARGO"}
            ],
        )
        raw = [
            {"linecaption": "#BlankLine#", "conceptname": "", "00_451965": ""},
            {
                "linecaption": "Real Estate Loans",
                "conceptname": "UBPR1410",
                "datatypeid": "155",
                "00_451965": "n/a",
            },
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: (
                [{"sectionid": "1"}] if requestor_id == "MBReportPageSections" else raw
            ),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda product, form_type: {},
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {},
        )
        result = fetch_peer_group_bank_report("451965", "Summary Ratios")
        labels = [r["label"] for r in result["rows"]]
        assert all("#BlankLine#" not in label for label in labels)
        line = next(r for r in result["rows"] if not r["is_header"])
        assert line["WELLS FARGO (451965)"] is None
