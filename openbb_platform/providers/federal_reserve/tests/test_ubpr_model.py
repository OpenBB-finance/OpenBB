"""Tests for the FFIEC Uniform Bank Performance Report (UBPR, CDR router) model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.ubpr import (
    UBPR_SECTIONS,
    FederalReserveUBPRData,
    FederalReserveUBPRFetcher,
)
from openbb_federal_reserve.utils import ubpr_report

from .ffiec_cassettes import replay

_SECTION = {
    "section": "Summary Ratios",
    "rows": [
        {"label": "Earnings and Profitability", "is_header": True},
        {
            "label": ">  Interest Income (TE)",
            "is_header": False,
            "2026-03-31 Bank": 4.28,
            "2026-03-31 PG": 4.43,
            "2026-03-31 PCT": 30.0,
        },
        {
            "label": "Net Income",
            "is_header": False,
            "2026-03-31 Bank": 1.31,
            "2026-03-31 PG": 1.11,
            "2026-03-31 PCT": 80.0,
        },
    ],
}


_ALL_PERIODS_SECTION = {
    "section": "Summary Ratios",
    "rows": [
        {"label": "Earnings and Profitability", "is_header": True},
        {
            "label": "Net Income ($000)",
            "is_header": False,
            "2026-03-31": 1310000.0,
            "2025-12-31": 1280000.0,
            "2025-09-30": 1250000.0,
            "2025-06-30": 1220000.0,
            "2025-03-31": 1190000.0,
            "2024-12-31": 1160000.0,
        },
    ],
}


def _patch(monkeypatch, result=None, resolved=None):
    """Point the section fetch and the lead-bank resolver at in-memory fixtures."""
    source = result if result is not None else _SECTION
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ubpr_report.fetch_ubpr_section",
        lambda rssd_id, section, all_periods=False: {
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
            FederalReserveUBPRFetcher.transform_query({})

    def test_default_section(self):
        """The section defaults to Summary Ratios and is a known section."""
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "451965"})
        assert query.section == "Summary Ratios"
        assert query.section in UBPR_SECTIONS


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_returns_section_rows(self, monkeypatch):
        """The section's rows pass through from the router client."""
        _patch(monkeypatch)
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "451965"})
        assert len(FederalReserveUBPRFetcher.extract_data(query, None)) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty section raises ``EmptyDataError``."""
        _patch(monkeypatch, {"section": "Summary Ratios", "rows": []})
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "451965"})
        with pytest.raises(EmptyDataError):
            FederalReserveUBPRFetcher.extract_data(query, None)

    def test_all_blank_shell_raises_no_bank_error(self, monkeypatch):
        """A non-bank RSSD whose rows carry no period values raises the bank error.

        The router returns the full section structure (label/is_header/narrative)
        but no row has any period value, so the result is a misleading all-blank
        shell rather than real data.
        """
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
                        "2026-03-31 Bank": None,
                        "2026-03-31 PG": None,
                        "2026-03-31 PCT": None,
                    },
                ],
            },
        )
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "2162966"})
        with pytest.raises(OpenBBError) as exc:
            FederalReserveUBPRFetcher.extract_data(query, None)
        message = str(exc.value)
        assert "No UBPR data for RSSD 2162966" in message
        assert "FFIEC Call Report" in message
        assert "financial_statements" in message

    def test_symbol_resolves_to_rssd(self, monkeypatch):
        """A ticker resolves to an RSSD before the section fetch."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: "451965",
        )
        query = FederalReserveUBPRFetcher.transform_query({"symbol": "WFC"})
        assert len(FederalReserveUBPRFetcher.extract_data(query, None)) == 3

    def test_unresolved_symbol_raises(self, monkeypatch):
        """A ticker that resolves to nothing raises ``OpenBBError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.resolve_ticker_to_rssd",
            lambda symbol: None,
        )
        query = FederalReserveUBPRFetcher.transform_query({"symbol": "ZZZ"})
        with pytest.raises(OpenBBError):
            FederalReserveUBPRFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_wide_rows(self, monkeypatch):
        """Line items carry per-period Bank/PG/PCT; headers carry only a label."""
        _patch(monkeypatch)
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "451965"})
        rows = FederalReserveUBPRFetcher.extract_data(query, None)
        result = FederalReserveUBPRFetcher.transform_data(query, rows)
        out = result.result or []
        assert all(isinstance(r, FederalReserveUBPRData) for r in out)
        line = next(r for r in out if not r.is_header)
        assert line.model_dump()["2026-03-31 Bank"] == 4.28
        assert line.label.startswith(">")  # indentation guarded
        header = next(r for r in out if r.is_header)
        assert header.label == "Earnings and Profitability"

    def test_unresolved_rssd_carries_no_resolved_name(self, monkeypatch):
        """A bank RSSD that already files surfaces only its own RSSD in metadata."""
        _patch(monkeypatch)
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "451965"})
        rows = FederalReserveUBPRFetcher.extract_data(query, None)
        result = FederalReserveUBPRFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata["rssd_id"] == "451965"
        assert "name" not in metadata
        assert metadata["section"] == "Summary Ratios"

    def test_holding_company_resolves_and_surfaces_bank(self, monkeypatch):
        """A holding-company RSSD resolves to its lead bank, surfaced in metadata."""
        _patch(monkeypatch, resolved=("852218", "JPMORGAN CHASE BANK NA"))
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "1039502"})
        rows = FederalReserveUBPRFetcher.extract_data(query, None)
        result = FederalReserveUBPRFetcher.transform_data(query, rows)
        metadata = result.metadata or {}
        assert metadata["rssd_id"] == "852218"
        assert metadata["name"] == "JPMORGAN CHASE BANK NA"
        assert metadata["section"] == "Summary Ratios"

    def test_empty_data_validates_without_metadata(self):
        """An empty parsed-row list validates to an empty result with no metadata."""
        query = FederalReserveUBPRFetcher.transform_query({"rssd_id": "451965"})
        result = FederalReserveUBPRFetcher.transform_data(query, [])
        assert result.result == []
        assert result.metadata == {"section": "Summary Ratios"}


class TestAllPeriods:
    """Tests for the ``all_periods`` time-series mode."""

    def test_returns_bank_only_time_series(self, monkeypatch):
        """``all_periods`` returns >5 plain ``<ISO>`` columns and no PG/PCT."""
        _patch(monkeypatch, dict(_ALL_PERIODS_SECTION))
        query = FederalReserveUBPRFetcher.transform_query(
            {"rssd_id": "451965", "all_periods": True}
        )
        assert query.all_periods is True
        rows = FederalReserveUBPRFetcher.extract_data(query, None)
        result = FederalReserveUBPRFetcher.transform_data(query, rows)
        out = result.result or []
        line = next(r for r in out if not r.is_header)
        periods = [
            k
            for k in line.model_dump()
            if k not in ("label", "is_header", "narrative") and k is not None
        ]
        assert len(periods) > 5
        assert all(c.count("-") == 2 and " " not in c for c in periods)
        assert not any(c.endswith(" PG") or c.endswith(" PCT") for c in periods)
        assert line.model_dump()["2026-03-31"] == 1310000.0


class _Session:
    """A canned session returning the ``MyUbprLinesData`` section grid."""

    def __init__(self, rows):
        """Store the line rows the router POST resolves to."""
        self._rows = rows

    def post(self, url, data=None, headers=None, timeout=None):
        """Return the section's line rows as the router response."""
        rows = self._rows
        return type("R", (), {"json": lambda self: rows})()


class TestFetchUbprSection:
    """Tests for ``fetch_ubpr_section`` guide-sourced labels and narratives."""

    def _wire(self, monkeypatch):
        """Point the client at canned cycles, section, session, and guide.

        The ratio page carries the bank ``UBPR4340`` plus its peer ``UBPS4340``
        and percentile ``UBPK4340`` parts.
        """
        cycles = [{"reportingcycleid": "1", "enddateformatted": "3/31/2026"}]
        rows = [
            {
                "linedisplayorder": "1",
                "linecaption": "#SectionTitle#Earnings and Profitability",
                "lineid": "100",
                "03_31_2026": None,
            },
            {
                "linedisplayorder": "2",
                "linecaption": "Net Inc",
                "lineid": "101",
                "03_31_2026": "1.31;UBPR4340, 1.11;UBPS4340, 80.0;UBPK4340",
            },
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles", lambda: cycles
        )
        monkeypatch.setattr(
            ubpr_report,
            "_section_id",
            lambda section, report_type_id: ("p1", "Summary Ratios"),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(rows),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda name: {
                "UBPR4340": {"monetary": False, "name": "Net Inc"},
                "UBPS4340": {"monetary": False, "name": "Net Inc"},
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                "UBPR4340": {
                    "description": "Net Income as a percent of Average Assets",
                    "narrative": "Net income for the period.",
                }
            },
        )

    def _wire_dollars(self, monkeypatch):
        """Point the client at a dollar page: bank ``UBPR4010`` and a sibling ratio.

        Part 1 is a ratio concept (no ``UBPS`` prefix) that must not be shown as a
        peer group, and the monetary bank value must scale by one thousand.
        """
        cycles = [{"reportingcycleid": "1", "enddateformatted": "3/31/2026"}]
        rows = [
            {
                "linedisplayorder": "1",
                "linecaption": "#SectionTitle#Interest Income",
                "lineid": "200",
                "03_31_2026": None,
            },
            {
                "linedisplayorder": "2",
                "linecaption": "Interest and Fees on Loans",
                "lineid": "201",
                "03_31_2026": "94627000.0;UBPR4010, 1.628164;UBPRE044",
            },
            {
                "linedisplayorder": "3",
                "linecaption": "Income From Lease Financing",
                "lineid": "202",
                "03_31_2026": "12345000.0;RIAD4065",
            },
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles", lambda: cycles
        )
        monkeypatch.setattr(
            ubpr_report,
            "_section_id",
            lambda section, report_type_id: ("p2", "Income Statement $"),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(rows),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda name: {
                "UBPR4010": {"monetary": True, "name": "Int and Fees on Loans"},
                "UBPRE044": {"monetary": False, "name": "Int and Fees on Loans 1Yr"},
                "RIAD4065": {
                    "monetary": True,
                    "name": "Income From Lease Financing",
                    "narrative": (
                        "Includes amortized income from direct and leveraged"
                        " financing leases."
                    ),
                },
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                "UBPR4010": {
                    "description": "Interest and Fees on Loans ($000)",
                    "narrative": "Interest and fees on loans for the period.",
                },
                "RIAD4065": {
                    "description": "Income From Lease Financing ($000)",
                    "narrative": None,
                },
            },
        )

    def test_line_label_from_guide_description(self, monkeypatch):
        """A line item's label is the cleaned guide Description, not the MDRM name."""
        self._wire(monkeypatch)
        rows = ubpr_report.fetch_ubpr_section("852218", "Summary Ratios")["rows"]
        line = next(r for r in rows if not r["is_header"])
        assert line["label"] == "Net Income"
        assert line["narrative"] == "Net income for the period."

    def test_header_label_unchanged(self, monkeypatch):
        """A header row keeps its caption label."""
        self._wire(monkeypatch)
        rows = ubpr_report.fetch_ubpr_section("852218", "Summary Ratios")["rows"]
        header = next(r for r in rows if r["is_header"])
        assert header["label"] == "Earnings and Profitability"

    def test_leading_header_carries_page_description(self, monkeypatch):
        """The leading header row's narrative is the section's page description."""
        from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

        self._wire(monkeypatch)
        rows = ubpr_report.fetch_ubpr_section("852218", "Summary Ratios")["rows"]
        assert rows[0]["is_header"] is True
        assert rows[0]["narrative"] == UBPR_PAGE_DESCRIPTIONS["Summary Ratios"]
        line = next(r for r in rows if not r["is_header"])
        assert line["narrative"] == "Net income for the period."

    def test_ratio_page_has_bank_pg_pct_unscaled(self, monkeypatch):
        """A ratio page emits Bank/PG/PCT columns with the ratio values unscaled."""
        self._wire(monkeypatch)
        rows = ubpr_report.fetch_ubpr_section("852218", "Summary Ratios")["rows"]
        line = next(r for r in rows if not r["is_header"])
        assert line["2026-03-31 Bank"] == 1.31
        assert line["2026-03-31 PG"] == 1.11
        assert line["2026-03-31 PCT"] == 80.0
        assert "2026-03-31" not in line

    def test_dollar_page_has_plain_bank_columns_scaled(self, monkeypatch):
        """A dollar page emits a single bank column, scaled by a thousand, no PG/PCT."""
        self._wire_dollars(monkeypatch)
        rows = ubpr_report.fetch_ubpr_section("852218", "Income Statement $")["rows"]
        line = next(r for r in rows if not r["is_header"])
        assert line["label"] == "Interest and Fees on Loans"
        assert line["2026-03-31"] == 94627000.0 * 1000
        assert "2026-03-31 Bank" not in line
        assert "2026-03-31 PG" not in line
        assert "2026-03-31 PCT" not in line

    def test_call_sourced_line_uses_concept_index_narrative(self, monkeypatch):
        """A Call-sourced (RIAD) line falls back to the concept-index narrative.

        The guide carries no narrative for Call Report concepts, so the line
        takes the MDRM definition from the concept index, while a UBPR concept
        keeps its guide narrative unchanged.
        """
        self._wire_dollars(monkeypatch)
        rows = ubpr_report.fetch_ubpr_section("852218", "Income Statement $")["rows"]
        ubpr_line = next(r for r in rows if r["label"] == "Interest and Fees on Loans")
        call_line = next(r for r in rows if r["label"] == "Income from Lease Financing")
        assert ubpr_line["narrative"] == "Interest and fees on loans for the period."
        assert call_line["narrative"] == (
            "Includes amortized income from direct and leveraged financing leases."
        )


class TestCassetteIntegration:
    """Run the full fetcher against a recorded FFIEC router cassette."""

    def test_real_summary_ratios_parses_from_cassette(self, monkeypatch):
        """The full pipeline parses the real captured Summary Ratios section.

        Replays the recorded ``PeriodsEndDateList``/``UbprReportPagesList``/
        ``MyUbprLinesData`` router responses, the parsed guide concepts and the
        filtered concept index, running ``transform_query`` -> ``extract_data`` ->
        ``transform_data`` so the actual parse executes on real captured data with
        no live network and no pre-warmed cache. The Call Report filer set (used to
        resolve a holding company to its lead bank) is served as the bank's own
        RSSD so the resolution is a no-op and never touches the network.
        """
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ticker.call_report_filers",
            lambda: {"852218"},
        )
        with replay("ubpr"):
            query = FederalReserveUBPRFetcher.transform_query(
                {"rssd_id": "852218", "section": "Summary Ratios"}
            )
            rows = FederalReserveUBPRFetcher.extract_data(query, None)
            result = (
                FederalReserveUBPRFetcher.transform_data(query, rows)
            ).result or []

        assert query.section == "Summary Ratios"
        assert result
        assert all(isinstance(r, FederalReserveUBPRData) for r in result)

        headers = [r for r in result if r.is_header]
        lines = [r for r in result if not r.is_header]
        assert len(headers) > 1
        assert len(lines) > 1

        header_labels = {h.label for h in headers}
        assert "Earnings and Profitability" in header_labels
        assert "Margin Analysis:" in header_labels
        assert "Capitalization" in header_labels

        assert result[0].is_header is True
        assert result[0].label == "Earnings and Profitability"
        assert result[0].narrative

        line = next(r for r in lines if r.label == "Net Interest Income (TE)")
        dumped = line.model_dump()
        assert dumped["2026-03-31 Bank"] == 2.592498
        assert dumped["2026-03-31 PG"] == 2.504
        assert dumped["2026-03-31 PCT"] == 40.0
        assert line.narrative and line.narrative.startswith("Total interest income")

        period_cols = [
            c
            for c in dumped
            if c not in ("label", "is_header", "narrative") and dumped[c] is not None
        ]
        bank_cols = [c for c in period_cols if c.endswith(" Bank")]
        pg_cols = [c for c in period_cols if c.endswith(" PG")]
        pct_cols = [c for c in period_cols if c.endswith(" PCT")]
        assert len(bank_cols) == 5
        assert len(pg_cols) == 5
        assert len(pct_cols) == 5
        assert {c.rsplit(" ", 1)[0] for c in bank_cols} == {
            "2025-03-31",
            "2025-06-30",
            "2025-09-30",
            "2025-12-31",
            "2026-03-31",
        }

        for item in lines:
            value = item.model_dump()["2026-03-31 Bank"]
            assert value is not None
            assert isinstance(value, (int, float))
            assert not isinstance(value, bool)

        all_values = [
            v
            for r in lines
            for k, v in r.model_dump().items()
            if k.endswith((" Bank", " PG", " PCT")) and v is not None
        ]
        assert 4.28 not in all_values
        assert 1.31 not in all_values
