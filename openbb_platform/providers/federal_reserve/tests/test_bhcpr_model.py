"""Tests for the per-institution BHCPR data fetcher model."""

from datetime import datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_federal_reserve.models.ffiec.bhcpr import (
    FederalReserveBhcprFetcher,
    _default_period,
    _filed_periods,
    _quarter_end,
    _resolve_period,
    _sections,
)

_NBSP = " "

# The firm's filed reports as parsed from its NIC profile: it files the BHCPR
# quarterly, newest period first.
_REPORTS = {
    "BHCPR": {
        "name": "BHCPR",
        "periods": [
            {"year": 2026, "quarter": 1, "month_day": "3/31"},
            {"year": 2025, "quarter": 4, "month_day": "12/31"},
        ],
    }
}

# The guide's parsed definitions, keyed ``"norm-section\x1enorm-item"``; only the
# taxable-equivalent net interest income line carries a published definition here.
_GUIDE_DEFS = {
    "summary ratios\x1enet interest income tax equivalent": (
        "NII on a TE basis divided by average assets."
    ),
}

# A parsed BHCPR payload mirroring ``fetch_bhcpr``: identity, the five ISO period
# dates, and two sections -- a ratio section (a sub-header, a triplet metric with
# history, and a bank-only row) and a dollar section (a single amount metric).
_DATA = {
    "identity": {
        "institution_name": "JPMORGAN CHASE & CO.",
        "city_state": "NEW YORK, NY",
        "rssd_id": "1039502",
    },
    "period_dates": [
        "2026-03-31",
        "2025-03-31",
        "2025-12-31",
        "2024-12-31",
        "2023-12-31",
    ],
    "sections": [
        {
            "section": "Summary Ratios",
            "rows": [
                {"label": "Earnings and Profitability:", "is_header": True},
                {
                    "label": "Net interest income (tax equivalent)",
                    "is_header": False,
                    "bank": [2.15, 2.22, 2.17, 2.29, 2.35],
                    "peer": 3.08,
                    "percentile": 11,
                },
                {
                    "label": "Average assets ($000)",
                    "is_header": False,
                    "bank": [4759098000000, None, None, None, None],
                    "peer": None,
                    "percentile": None,
                },
            ],
        },
        {
            "section": "Assets",
            "rows": [
                {
                    "label": "Real estate loans",
                    "is_header": False,
                    "bank": [504352000000, 490921000000, None, None, None],
                    "peer": None,
                    "percentile": None,
                },
            ],
        },
    ],
}


def _patch(monkeypatch, data=None, reports=None):
    """Patch the BHCPR fetch and the firm profile lookup to offline fixtures."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_bhcpr",
        lambda rssd_id, date: dict(data or _DATA),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
        lambda rssd: dict(reports if reports is not None else _REPORTS),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.bhcpr_guide.fetch_bhcpr_definitions",
        lambda: dict(_GUIDE_DEFS),
    )


class TestHelpers:
    """Tests for the module-level helpers."""

    def test_quarter_end(self):
        """Each quarter maps to its calendar quarter-end date."""
        assert _quarter_end(2025, 1) == "20250331"
        assert _quarter_end(2025, 4) == "20251231"

    def test_sections_first_is_summary_ratios(self):
        """The section registry opens with Summary Ratios and is non-empty."""
        sections = _sections()
        assert sections[0] == "Summary Ratios"
        assert "Parent Company Balance Sheet" in sections


class TestDefaultPeriod:
    """Tests for the ``_default_period`` availability heuristic."""

    def test_walks_back_within_year(self, monkeypatch):
        """A mid-year date walks back to the latest filed quarter without wrapping."""

        class _Now:
            """Frozen clock returning a fixed date."""

            @staticmethod
            def now():
                """Return a fixed datetime."""
                return datetime(2025, 11, 10)

        monkeypatch.setattr("openbb_federal_reserve.models.ffiec.bhcpr.datetime", _Now)
        assert _default_period() == (2025, 3)

    def test_walks_back_across_year(self, monkeypatch):
        """An early-quarter date walks back across the year boundary."""

        class _Now:
            """Frozen clock returning a fixed date."""

            @staticmethod
            def now():
                """Return a fixed datetime."""
                return datetime(2025, 1, 10)

        monkeypatch.setattr("openbb_federal_reserve.models.ffiec.bhcpr.datetime", _Now)
        assert _default_period() == (2024, 3)


class TestResolvePeriod:
    """Tests for ``_resolve_period``."""

    def test_explicit_period_passes_through(self):
        """A supplied YYYYMMDD period is used verbatim, trimmed."""
        assert _resolve_period(" 20260331 ", ["20251231"]) == "20260331"

    def test_blank_period_defaults_to_latest_filed(self):
        """A blank period falls back to the firm's latest filed period."""
        assert _resolve_period(None, ["20260331", "20251231"]) == "20260331"
        assert _resolve_period("", ["20260331", "20251231"]) == "20260331"

    def test_no_filed_periods_falls_back_to_heuristic(self, monkeypatch):
        """With no filed period known, the calendar-quarter heuristic is used."""
        monkeypatch.setattr(
            "openbb_federal_reserve.models.ffiec.bhcpr._default_period",
            lambda: (2025, 2),
        )
        assert _resolve_period(None, []) == "20250630"


class TestFiledPeriods:
    """Tests for ``_filed_periods``."""

    def test_returns_filed_period_ends_newest_first(self, monkeypatch):
        """The firm's filed BHCPR periods become YYYYMMDD ends, newest first."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: dict(_REPORTS),
        )
        assert _filed_periods("1039502") == ["20260331", "20251231"]

    def test_blank_rssd_returns_empty(self):
        """A blank RSSD yields no filed periods without a fetch."""
        assert _filed_periods("") == []

    def test_non_mapping_profile_returns_empty(self, monkeypatch):
        """A non-mapping profile result yields no filed periods."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: ["BHCPR"],
        )
        assert _filed_periods("1039502") == []

    def test_profile_failure_returns_empty(self, monkeypatch):
        """An unavailable profile yields no filed periods rather than raising."""

        def _boom(rssd):
            """Raise to simulate an unavailable NIC profile."""
            raise RuntimeError("profile down")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _boom,
        )
        assert _filed_periods("1039502") == []


class TestTransformQuery:
    """Tests for ``transform_query`` validation."""

    def test_requires_rssd_id(self):
        """Omitting the required rssd_id raises a validation error."""
        with pytest.raises(ValidationError):
            FederalReserveBhcprFetcher.transform_query({})


class TestExtractData:
    """Tests for ``extract_data`` selection and period defaulting."""

    def test_fetches_selected_period(self, monkeypatch):
        """The RSSD and resolved period drive the fetch."""
        captured: dict = {}
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_bhcpr",
            lambda rssd_id, date: (
                captured.update(rssd=rssd_id, date=date) or dict(_DATA)
            ),
        )
        query = FederalReserveBhcprFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20260331"}
        )
        data = FederalReserveBhcprFetcher.extract_data(query, None)
        assert captured == {"rssd": "1039502", "date": "20260331"}
        assert data["sections"][0]["section"] == "Summary Ratios"

    def test_unfiled_report_raises_empty(self, monkeypatch):
        """A payload with no sections raises ``EmptyDataError``."""
        _patch(monkeypatch, {**_DATA, "sections": []})
        query = FederalReserveBhcprFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveBhcprFetcher.extract_data(query, None)

    def test_defaults_period_to_latest_filed_when_omitted(self, monkeypatch):
        """Omitting the period defaults it to the firm's latest filed period."""
        captured: dict = {}
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_bhcpr",
            lambda rssd_id, date: captured.update(date=date) or dict(_DATA),
        )
        query = FederalReserveBhcprFetcher.transform_query({"rssd_id": "1039502"})
        FederalReserveBhcprFetcher.extract_data(query, None)
        assert captured["date"] == "20260331"

    def test_resolves_non_filer_to_top_tier_holder(self, monkeypatch):
        """A bank that files no BHCPR is resolved to its BHCPR-filing holder."""
        captured: dict = {}
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_bhcpr",
            lambda rssd_id, date: captured.update(rssd=rssd_id) or dict(_DATA),
        )

        def _reports(rssd):
            """The bank files FFIEC 101 only; its holder files the BHCPR."""
            return dict(_REPORTS) if rssd == "1039502" else {"FFIEC101": {}}

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _reports,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec._top_tier_holder",
            lambda rssd: "1039502",
        )
        query = FederalReserveBhcprFetcher.transform_query({"rssd_id": "852218"})
        FederalReserveBhcprFetcher.extract_data(query, None)
        assert captured["rssd"] == "1039502"


class TestTransformData:
    """Tests for ``transform_data`` grouped rendering."""

    def _result(self, monkeypatch, params=None):
        """Run the full extract/transform pipeline against the miniature payload."""
        _patch(monkeypatch)
        query = FederalReserveBhcprFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20260331", **(params or {})}
        )
        data = FederalReserveBhcprFetcher.extract_data(query, None)
        return FederalReserveBhcprFetcher.transform_data(query, data)

    def test_returns_annotated_result_with_metadata(self, monkeypatch):
        """The result is annotated with the RSSD, name, city/state, and date."""
        result = self._result(monkeypatch)
        assert isinstance(result, AnnotatedResult)
        assert result.metadata == {
            "rssd_id": "1039502",
            "name": "JPMORGAN CHASE & CO.",
            "city_state": "NEW YORK, NY",
            "section": "Summary Ratios",
            "reporting_date": "2026-03-31",
        }

    def test_emits_section_header(self, monkeypatch):
        """The selected section opens with a header row carrying no values."""
        rows = self._result(monkeypatch).result
        assert rows[0].label == "Summary Ratios"
        assert rows[0].is_header is True
        assert rows[0].model_dump().get("BHC") is None

    def test_rows_are_rectangular(self, monkeypatch):
        """Every row carries the same value columns so the table renders them all.

        The Workspace derives the table's columns from the first (header) row, so a
        ragged header would hide every value column under ``showAll``.
        """
        rows = self._result(monkeypatch).result
        header_keys = set(rows[0].model_dump())
        assert {"BHC", "Peer Group", "Percentile"} <= header_keys
        assert all(set(row.model_dump()) == header_keys for row in rows)

    def test_subheader_rendered_as_indented_header(self, monkeypatch):
        """A section's sub-header is an indented header row carrying no values."""
        rows = self._result(monkeypatch).result
        sub = next(r for r in rows if r.label.strip() == "Earnings and Profitability:")
        assert sub.is_header is True
        assert sub.label == _NBSP * 2 + "Earnings and Profitability:"

    def test_metric_carries_bank_peer_percentile(self, monkeypatch):
        """A ratio row carries the BHC value, peer average, and percentile rank.

        The value columns are dynamic (emitted as extra fields, not a fixed schema)
        so ``showAll`` renders them; they are read back through ``model_dump``.
        """
        rows = self._result(monkeypatch).result
        ratio = next(r for r in rows if r.label.endswith("(tax equivalent)"))
        assert ratio.label == ">" + _NBSP * 2 + "Net interest income (tax equivalent)"
        dumped = ratio.model_dump()
        assert dumped["BHC"] == 2.15
        assert dumped["Peer Group"] == 3.08
        assert dumped["Percentile"] == 11

    def test_metric_carries_prior_period_history(self, monkeypatch):
        """A row carries the bank value for each prior period as an ISO-date column."""
        rows = self._result(monkeypatch).result
        ratio = next(r for r in rows if r.label.endswith("(tax equivalent)"))
        dumped = ratio.model_dump()
        assert dumped["2025-03-31"] == 2.22
        assert dumped["2023-12-31"] == 2.35

    def test_missing_prior_period_is_null(self, monkeypatch):
        """A row with fewer filed periods keeps null history columns aligned."""
        rows = self._result(monkeypatch).result
        avg = next(r for r in rows if r.label.endswith("Average assets ($000)"))
        dumped = avg.model_dump()
        assert dumped["BHC"] == 4759098000000
        assert dumped["2025-03-31"] is None

    def test_dollar_metric_renders_in_full_dollars(self, monkeypatch):
        """A dollar section row renders the filed full-dollar amount and history."""
        rows = self._result(monkeypatch, {"section": "Assets"}).result
        loans = next(r for r in rows if r.label.endswith("Real estate loans"))
        dumped = loans.model_dump()
        assert dumped["BHC"] == 504352000000
        assert dumped["2025-03-31"] == 490921000000

    def test_all_sections_when_section_is_all(self, monkeypatch):
        """The 'All Sections' choice renders every section's header and rows."""
        rows = self._result(monkeypatch, {"section": "All Sections"}).result
        headers = {r.label for r in rows if r.is_header}
        assert "Summary Ratios" in headers
        assert "Assets" in headers

    def test_all_sections_when_section_omitted(self, monkeypatch):
        """An empty section also renders every section."""
        rows = self._result(monkeypatch, {"section": ""}).result
        headers = {r.label for r in rows if r.is_header}
        assert {"Summary Ratios", "Assets"} <= headers

    def test_section_selects_by_title(self, monkeypatch):
        """A section given by title selects only that section."""
        result = self._result(monkeypatch, {"section": "Assets"})
        labels = {r.label for r in result.result}
        assert "Assets" in labels
        assert "Summary Ratios" not in labels

    def test_unknown_section_raises(self, monkeypatch):
        """A section matching no title raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            self._result(monkeypatch, {"section": "Nonexistent"})

    def test_falls_back_to_query_rssd_and_missing_date(self, monkeypatch):
        """Absent identity and dates, the query RSSD stands in and the date drops."""
        _patch(
            monkeypatch,
            {
                "identity": {},
                "period_dates": [],
                "sections": _DATA["sections"],
            },
        )
        query = FederalReserveBhcprFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20260331"}
        )
        data = FederalReserveBhcprFetcher.extract_data(query, None)
        result = FederalReserveBhcprFetcher.transform_data(query, data)
        assert result.metadata["rssd_id"] == "1039502"
        assert "reporting_date" not in result.metadata
        assert "name" not in result.metadata

    def test_metric_carries_guide_narrative(self, monkeypatch):
        """A metric row carries its BHCPR User's Guide definition as the narrative."""
        rows = self._result(monkeypatch).result
        ratio = next(r for r in rows if r.label.endswith("(tax equivalent)"))
        assert ratio.narrative == "NII on a TE basis divided by average assets."

    def test_metric_without_definition_has_no_narrative(self, monkeypatch):
        """A metric with no published definition carries a null narrative."""
        rows = self._result(monkeypatch).result
        avg = next(r for r in rows if r.label.endswith("Average assets ($000)"))
        assert avg.narrative is None

    def test_guide_failure_leaves_narratives_null(self, monkeypatch):
        """An unavailable guide leaves every narrative null without failing."""
        _patch(monkeypatch)

        def _boom():
            """Raise to simulate an unavailable BHCPR User's Guide."""
            raise RuntimeError("guide down")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.bhcpr_guide.fetch_bhcpr_definitions", _boom
        )
        query = FederalReserveBhcprFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20260331"}
        )
        data = FederalReserveBhcprFetcher.extract_data(query, None)
        result = FederalReserveBhcprFetcher.transform_data(query, data)
        assert all(row.narrative is None for row in result.result)
