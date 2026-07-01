"""Tests for the unified FFIEC Financial Report fetcher model."""

from datetime import datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ValidationError

from openbb_federal_reserve.models.ffiec.financial_report import (
    FederalReserveFinancialReportFetcher,
    _column_suffixes,
    _default_period,
    _latest_filed_period,
    _load_structure,
    _quarter_end,
    _resolve_period,
    _to_number,
)

_NBSP = " "

# A per-institution report payload keyed by MDRM code, mirroring the parsed
# ReturnFinancialReportCSV result. BHCK2170 (dollars) and BHCK3210 (derived
# dollars) scale x1000; BHCK7204 (a rate) is left as filed.
_REPORT = {
    "institution_name": "JPMORGAN CHASE & CO.",
    "report_date": "20250331",
    "rssd_id": "1039502",
    "facts": {
        "BHCK2170": "4357856",
        "BHCK3210": "345000",
        "BHCK7204": "1525",
        "BHCA7204": "6.5983",
    },
}

# A miniature ordered structure: a COVER item (dropped), two schedules, a
# sub-section header, and three line items spanning dollar, derived, and rate.
_STRUCTURE = {
    "schedules": [
        {"schedule": "COVER", "name": "Cover Page"},
        {"schedule": "HC", "name": "Balance Sheet"},
        {"schedule": "HC-R", "name": "Regulatory Capital"},
    ],
    "items": [
        {
            "schedule": "COVER",
            "schedule_name": "Cover Page",
            "line": None,
            "caption": "Legal Title of Holding Company",
            "mdrm": "RSSD9017",
            "level": 1,
            "is_header": False,
        },
        {
            "schedule": "HC",
            "schedule_name": "Balance Sheet",
            "line": None,
            "caption": "Assets:",
            "mdrm": None,
            "level": 1,
            "is_header": True,
        },
        {
            "schedule": "HC",
            "schedule_name": "Balance Sheet",
            "line": "12",
            "caption": "Total assets",
            "mdrm": "BHCK2170",
            "level": 2,
            "is_header": False,
        },
        {
            "schedule": "HC",
            "schedule_name": "Balance Sheet",
            "line": "28",
            "caption": "Total equity capital",
            "mdrm": "BHCK3210",
            "level": 1,
            "is_header": False,
        },
        {
            "schedule": "HC-R",
            "schedule_name": "Regulatory Capital",
            "line": "M.1",
            "caption": "Tier 1 capital ratio",
            "mdrm": "BHCK7204",
            "level": 1,
            "is_header": False,
        },
        {
            "schedule": "HC-R",
            "schedule_name": "Regulatory Capital",
            "line": "M.2",
            "caption": "Tier 1 leverage capital ratio",
            "mdrm": "BHCA7204",
            "level": 1,
            "is_header": False,
        },
    ],
}

_DEFINITIONS = {"BHCK2170": "Total assets reported on a consolidated basis."}

_ITEM_TYPES = {
    "BHCK2170": "F",
    "BHCK3210": "D",
    "BHCK7204": "P",
    "BHCA7204": "F",
}

_ITEM_NAMES = {
    "BHCK2170": "TOTAL ASSETS (BHC CONSOLIDATED)",
    "BHCK3210": "TOTAL EQUITY CAPITAL",
    "BHCK7204": "TIER 1 CAPITAL RATIO",
    "BHCA7204": "TIER 1 LEVERAGE CAPITAL RATIO",
}


def _patch(monkeypatch):
    """Patch the report fetch, the structure, and the MDRM lookups."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
        lambda report_code, rssd_id, date: dict(_REPORT),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.models.ffiec.financial_report._load_structure",
        lambda report_type: dict(_STRUCTURE),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.mdrm.fetch_mdrm_definitions",
        lambda as_of=None: dict(_DEFINITIONS),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.mdrm.fetch_mdrm_dictionary",
        lambda as_of=None: dict(_ITEM_NAMES),
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.mdrm.fetch_mdrm_item_types",
        lambda: dict(_ITEM_TYPES),
    )


class TestHelpers:
    """Tests for the module-level helpers."""

    def test_quarter_end(self):
        """Each quarter maps to its calendar quarter-end date."""
        assert _quarter_end(2025, 1) == "20250331"
        assert _quarter_end(2025, 4) == "20251231"

    def test_to_number(self):
        """A numeric string parses; a non-numeric value coerces to None."""
        assert _to_number("4,357,856") == 4357856.0
        assert _to_number("n/a") is None

    def test_load_structure_unknown_raises(self):
        """An unknown report type raises ``OpenBBError``."""
        _load_structure.cache_clear()
        with pytest.raises(OpenBBError):
            _load_structure("NOPE")

    def test_load_structure_loads_committed_asset(self):
        """A ready report loads its committed structure with schedules and items."""
        _load_structure.cache_clear()
        structure = _load_structure("FRY9C")
        assert structure["schedules"]
        assert structure["items"]


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

        monkeypatch.setattr(
            "openbb_federal_reserve.models.ffiec.financial_report.datetime", _Now
        )
        assert _default_period() == (2025, 3)

    def test_walks_back_across_year(self, monkeypatch):
        """An early-quarter date walks back across the year boundary."""

        class _Now:
            """Frozen clock returning a fixed date."""

            @staticmethod
            def now():
                """Return a fixed datetime."""
                return datetime(2025, 1, 10)

        monkeypatch.setattr(
            "openbb_federal_reserve.models.ffiec.financial_report.datetime", _Now
        )
        assert _default_period() == (2024, 3)


class TestResolvePeriod:
    """Tests for ``_resolve_period`` and ``_latest_filed_period``."""

    def test_explicit_period_passes_through(self):
        """A supplied YYYYMMDD period is used verbatim, trimmed."""
        assert _resolve_period(" 20250630 ", "1039502", "FRY9C") == "20250630"

    def test_blank_period_defaults_to_latest_filed(self, monkeypatch):
        """A blank period defaults to the firm+report's newest filed period."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FRY9SP": {
                    "name": None,
                    "periods": [
                        {"year": 2025, "quarter": 4, "month_day": "12/31"},
                        {"year": 2025, "quarter": 2, "month_day": "6/30"},
                    ],
                }
            },
        )
        # The semiannual filer's newest filed period (2025 Q4) wins over any
        # computed current quarter the firm has not filed.
        assert _resolve_period(None, "1020395", "FRY9SP") == "20251231"
        assert _resolve_period("", "1020395", "FRY9SP") == "20251231"

    def test_blank_period_falls_back_to_computed_quarter(self, monkeypatch):
        """With no filed period for the report, the computed quarter is used."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {},
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.models.ffiec.financial_report._default_period",
            lambda: (2025, 2),
        )
        assert _resolve_period(None, "1039502", "FRQ1") == "20250630"

    def test_latest_filed_period_handles_profile_failure(self, monkeypatch):
        """An unavailable profile yields None so the caller can fall back."""

        def _boom(rssd):
            """Raise to simulate an unavailable NIC profile."""
            raise RuntimeError("profile down")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _boom,
        )
        assert _latest_filed_period("1039502", "FRY9C") is None


class TestTransformQuery:
    """Tests for ``transform_query`` validation."""

    def test_requires_rssd_id(self):
        """Omitting the required rssd_id raises a validation error."""
        with pytest.raises(ValidationError):
            FederalReserveFinancialReportFetcher.transform_query({})


class TestExtractData:
    """Tests for ``extract_data`` selection and period defaulting."""

    def test_fetches_selected_report(self, monkeypatch):
        """The report code, RSSD, and period drive the fetch."""
        captured: dict = {}
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: (
                captured.update(code=report_code, rssd=rssd_id, date=date)
                or dict(_REPORT)
            ),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {"FRY9C": {"name": None, "periods": []}},
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "report_type": "FRY9C", "period": "20250331"}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        assert captured == {"code": "FRY9C", "rssd": "1039502", "date": "20250331"}
        assert data["facts"]["BHCK2170"] == "4357856"

    def test_unknown_report_type_raises(self):
        """An unknown report type raises ``OpenBBError``."""
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1", "report_type": "NOPE"}
        )
        with pytest.raises(OpenBBError):
            FederalReserveFinancialReportFetcher.extract_data(query, None)

    def test_unfiled_report_raises_empty(self, monkeypatch):
        """A report with no value-bearing facts raises ``EmptyDataError``.

        Also exercises the profile-unavailable path: when the firm's filed
        reports cannot be read, the requested report is rendered as requested
        rather than crashing the options-driven default.
        """

        def _unavailable(rssd):
            raise RuntimeError("profile unavailable")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _unavailable,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: {**_REPORT, "facts": {}},
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1", "report_type": "FRY9C", "period": "20250331"}
        )
        with pytest.raises(EmptyDataError):
            FederalReserveFinancialReportFetcher.extract_data(query, None)

    def test_defaults_period_to_latest_filed_when_omitted(self, monkeypatch):
        """Omitting the period defaults it to the firm+report's newest filed period."""
        _patch(monkeypatch)
        captured: dict = {}
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: (
                captured.update(date=date) or dict(_REPORT)
            ),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FRY9C": {
                    "name": None,
                    "periods": [{"year": 2025, "quarter": 1, "month_day": "3/31"}],
                }
            },
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502"}
        )
        FederalReserveFinancialReportFetcher.extract_data(query, None)
        assert captured["date"] == "20250331"


class TestTransformData:
    """Tests for ``transform_data`` grouped rendering."""

    def _result(self, monkeypatch, params=None):
        """Run the full extract/transform pipeline against the miniature structure."""
        _patch(monkeypatch)
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331", **(params or {})}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        return FederalReserveFinancialReportFetcher.transform_data(query, data)

    def test_returns_annotated_result_with_metadata(self, monkeypatch):
        """The result is annotated with the RSSD, name, type, and reporting date."""
        result = self._result(monkeypatch)
        assert isinstance(result, AnnotatedResult)
        assert result.metadata == {
            "rssd_id": "1039502",
            "name": "JPMORGAN CHASE & CO.",
            "report_type": "FRY9C",
            "reporting_date": "2025-03-31",
        }

    def test_drops_cover_page(self, monkeypatch):
        """The administrative cover-page schedule is excluded from the output."""
        rows = self._result(monkeypatch).result or []
        assert all("Legal Title" not in r.label for r in rows)
        assert all(r.label != "Cover Page" for r in rows)

    def test_drops_cover_page_by_schedule_name(self, monkeypatch):
        """A cover page coded other than ``COVER`` (FFIEC 002) drops by its name."""
        structure = {
            "schedules": [
                {"schedule": "Cover Page", "name": "Cover Page"},
                {"schedule": "RAL", "name": "Schedule RAL - Assets and Liabilities"},
            ],
            "items": [
                {
                    "schedule": "Cover Page",
                    "schedule_name": "Cover Page",
                    "line": None,
                    "caption": "Consolidation code",
                    "mdrm": "RCON9395",
                    "level": 1,
                    "is_header": False,
                },
                {
                    "schedule": "RAL",
                    "schedule_name": "Schedule RAL - Assets and Liabilities",
                    "line": "1",
                    "caption": "Total assets",
                    "mdrm": "BHCK2170",
                    "level": 1,
                    "is_header": False,
                },
            ],
        }
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.models.ffiec.financial_report._load_structure",
            lambda report_type: dict(structure),
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1", "report_type": "FFIEC002", "period": "20250331"}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        rows = (
            FederalReserveFinancialReportFetcher.transform_data(query, data).result
            or []
        )
        assert all(r.label != "Cover Page" for r in rows)
        assert all("Consolidation code" not in r.label for r in rows)
        assert rows[0].label == "Schedule RAL - Assets and Liabilities"

    def test_emits_schedule_and_subsection_headers(self, monkeypatch):
        """A header row is emitted per schedule and per sub-section, with no value."""
        rows = self._result(monkeypatch).result or []
        assert rows[0].label == "Balance Sheet"
        assert rows[0].is_header is True
        assert rows[0].value is None
        subsection = next(r for r in rows if r.label.endswith("Assets:"))
        assert subsection.is_header is True
        assert any(r.label == "Regulatory Capital" and r.is_header for r in rows)

    def test_line_items_carry_indented_labels(self, monkeypatch):
        """Line-item labels are indented by their structure level with the NBSP marker."""
        rows = self._result(monkeypatch).result or []
        total_assets = next(r for r in rows if r.label.endswith("Total assets"))
        assert total_assets.label == ">" + _NBSP * 2 + "Total assets"
        equity = next(r for r in rows if r.label.endswith("Total equity capital"))
        assert equity.label == "Total equity capital"

    def test_scales_dollar_items_selectively(self, monkeypatch):
        """Monetary items scale x1000; rates and named non-monetary stay as filed."""
        rows = self._result(monkeypatch).result or []
        by_caption = {
            r.label.lstrip(">" + _NBSP): r.value for r in rows if not r.is_header
        }
        assert by_caption["Total assets"] == 4357856 * 1000
        assert by_caption["Total equity capital"] == 345000 * 1000
        assert by_caption["Tier 1 capital ratio"] == 1525
        # An ``F`` code named in the committed non-monetary asset is a ratio, not a
        # dollar amount, so it passes through unscaled despite its ItemType.
        assert by_caption["Tier 1 leverage capital ratio"] == 6.5983

    def test_attaches_narrative_for_hover_card(self, monkeypatch):
        """A line item carries its MDRM definition as the hover-card narrative."""
        rows = self._result(monkeypatch).result or []
        total_assets = next(r for r in rows if r.label.endswith("Total assets"))
        assert total_assets.narrative == _DEFINITIONS["BHCK2170"]
        equity = next(r for r in rows if r.label.endswith("Total equity capital"))
        assert equity.narrative is None

    def test_section_filter_renders_only_selected_schedule(self, monkeypatch):
        """A section selects a single schedule (by code), dropping the others."""
        rows = self._result(monkeypatch, {"section": "HC"}).result or []
        assert {r.label for r in rows if r.is_header} == {"Balance Sheet", "Assets:"}
        assert all("Tier 1" not in r.label for r in rows)
        assert self._result(monkeypatch).metadata is not None

    def test_section_filter_matches_schedule_name(self, monkeypatch):
        """A section given as a schedule name also selects that schedule."""
        result = self._result(monkeypatch, {"section": "Regulatory Capital"})
        labels = {r.label for r in result.result}
        assert "Regulatory Capital" in labels
        assert all(r.label != "Balance Sheet" for r in result.result)
        assert result.metadata["section"] == "Regulatory Capital"

    def test_section_with_no_match_raises_empty(self, monkeypatch):
        """A section that matches no schedule yields an empty result error."""
        with pytest.raises(EmptyDataError):
            self._result(monkeypatch, {"section": "Nonexistent"})

    def test_missing_report_date_yields_no_reporting_date(self, monkeypatch):
        """A report with no parseable date drops the metadata date; values render."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: {**_REPORT, "report_date": None},
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331"}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        result = FederalReserveFinancialReportFetcher.transform_data(query, data)
        assert "reporting_date" not in (result.metadata or {})
        total_assets = next(
            r for r in (result.result or []) if r.label.endswith("Total assets")
        )
        assert total_assets.value == 4357856 * 1000

    def test_hides_unfiled_line_items(self, monkeypatch):
        """A line item the filer did not report (no fact) is dropped from the rows."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: {
                **_REPORT,
                "facts": {"BHCK2170": "4357856", "BHCK7204": "1525"},
            },
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331"}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        rows = (
            FederalReserveFinancialReportFetcher.transform_data(query, data).result
            or []
        )
        # The unfiled BHCK3210 line is hidden; the filed siblings remain.
        assert all("Total equity capital" not in r.label for r in rows)
        assert any(r.label.endswith("Total assets") for r in rows)
        assert any(r.label.endswith("Tier 1 capital ratio") for r in rows)

    def test_hides_headers_with_no_valued_descendant(self, monkeypatch):
        """A schedule and sub-header with every descendant unfiled are dropped."""
        _patch(monkeypatch)
        # Only the HC-R rate item is filed; the entire Balance Sheet schedule —
        # its "Assets:" sub-header and both line items — has no surviving value.
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: {
                **_REPORT,
                "facts": {"BHCK7204": "1525"},
            },
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331"}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        rows = (
            FederalReserveFinancialReportFetcher.transform_data(query, data).result
            or []
        )
        labels = {r.label for r in rows}
        assert "Balance Sheet" not in labels
        assert not any(r.label.endswith("Assets:") for r in rows)
        assert {r.label for r in rows if r.is_header} == {"Regulatory Capital"}

    def test_keeps_filed_zeros(self, monkeypatch):
        """A filed zero is a real value and is retained, not pruned as empty."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: {
                **_REPORT,
                "facts": {"BHCK3210": "0"},
            },
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331"}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        rows = (
            FederalReserveFinancialReportFetcher.transform_data(query, data).result
            or []
        )
        equity = next(r for r in rows if r.label.endswith("Total equity capital"))
        assert equity.value == 0


class TestColumnSuffixes:
    """Tests for the per-column distinguishing-label helper."""

    def test_strips_shared_prefix_to_differing_tail(self):
        """Columns sharing a name prefix are labelled by their differing tail."""
        names = {
            "C1": "LOANS SECURED BY FARMLAND - PAST DUE 30 THROUGH 89 DAYS",
            "C2": "LOANS SECURED BY FARMLAND - PAST DUE 90 DAYS OR MORE",
            "C3": "LOANS SECURED BY FARMLAND - NONACCRUAL",
        }
        suffixes = _column_suffixes(["C1", "C2", "C3"], names)
        assert suffixes == [
            "Past Due 30 Through 89 Days",
            "Past Due 90 Days Or More",
            "Nonaccrual",
        ]

    def test_missing_column_name_falls_back_to_none(self):
        """A column with no resolvable MDRM name yields a ``None`` suffix."""
        names = {
            "C1": "TOTAL - PAST DUE 30 DAYS",
            "C2": "TOTAL - NONACCRUAL",
        }
        suffixes = _column_suffixes(["C1", "C2", "C3"], names)
        assert suffixes == ["Past Due 30 Days", "Nonaccrual", None]

    def test_fewer_than_two_names_yields_all_none(self):
        """With under two resolvable names there is no prefix to strip."""
        assert _column_suffixes(["C1", "C2"], {"C1": "ONLY ONE NAME"}) == [None, None]

    def test_identical_names_fall_back_to_full_title(self):
        """Columns whose names are wholly shared keep the full titled name."""
        names = {"C1": "SAME NAME", "C2": "SAME NAME"}
        assert _column_suffixes(["C1", "C2"], names) == ["Same Name", "Same Name"]


# A structure whose HC-N line is a three-column grid (one MDRM per column),
# exercising the per-column explode path.
_GRID_STRUCTURE = {
    "schedules": [{"schedule": "HC-N", "name": "Past Due and Nonaccrual"}],
    "items": [
        {
            "schedule": "HC-N",
            "schedule_name": "Past Due and Nonaccrual",
            "line": "1.b",
            "caption": "Secured by farmland",
            "mdrm": "BHCK3493",
            "columns": ["BHCK3493", "BHCK3494", "BHCK3495"],
            "level": 2,
            "is_header": False,
        }
    ],
}

_GRID_REPORT = {
    "institution_name": "JPMORGAN CHASE & CO.",
    "report_date": "20250331",
    "rssd_id": "1039502",
    "facts": {"BHCK3493": "100", "BHCK3494": "200", "BHCK3495": "300"},
    "descriptions": {},
}

_GRID_NAMES = {
    "BHCK3493": "SECURED BY FARMLAND - PAST DUE 30 THROUGH 89 DAYS",
    "BHCK3494": "SECURED BY FARMLAND - PAST DUE 90 DAYS OR MORE",
    "BHCK3495": "SECURED BY FARMLAND - NONACCRUAL",
}


class TestMultiColumnRendering:
    """Tests for grid (multi-column) line rendering."""

    def _grid_result(self, monkeypatch, report=None, structure=None, params=None):
        """Run the pipeline against the grid structure."""
        _patch(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_financial_report",
            lambda report_code, rssd_id, date: dict(report or _GRID_REPORT),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.models.ffiec.financial_report._load_structure",
            lambda report_type: dict(structure or _GRID_STRUCTURE),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.mdrm.fetch_mdrm_dictionary",
            lambda as_of=None: dict(_GRID_NAMES),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.mdrm.fetch_mdrm_item_types",
            lambda: {"BHCK3493": "F", "BHCK3494": "F", "BHCK3495": "F"},
        )
        query = FederalReserveFinancialReportFetcher.transform_query(
            {"rssd_id": "1039502", "period": "20250331", **(params or {})}
        )
        data = FederalReserveFinancialReportFetcher.extract_data(query, None)
        return (
            FederalReserveFinancialReportFetcher.transform_data(query, data).result
            or []
        )

    def test_explodes_columns_into_child_rows(self, monkeypatch):
        """A grid line emits its caption as a header plus one row per column."""
        rows = self._grid_result(monkeypatch)
        caption = next(r for r in rows if r.label.endswith("Secured by farmland"))
        assert caption.is_header is True
        values = [r.value for r in rows if not r.is_header]
        assert values == [100 * 1000, 200 * 1000, 300 * 1000]
        labels = [r.label.lstrip(">" + _NBSP) for r in rows if not r.is_header]
        assert labels == [
            "Past Due 30 Through 89 Days",
            "Past Due 90 Days Or More",
            "Nonaccrual",
        ]

    def test_falls_back_to_code_when_name_missing(self, monkeypatch):
        """A column with no resolvable name is labelled by its bare MDRM code."""
        rows = self._grid_result(
            monkeypatch,
            structure={
                "schedules": [{"schedule": "X", "name": "X"}],
                "items": [
                    {
                        "schedule": "X",
                        "schedule_name": "X",
                        "line": "1",
                        "caption": "Line",
                        "mdrm": "AAAA0001",
                        "columns": ["AAAA0001", "AAAA0002"],
                        "level": 1,
                        "is_header": False,
                    }
                ],
            },
            report={
                **_GRID_REPORT,
                "facts": {"AAAA0001": "1", "AAAA0002": "2"},
            },
        )
        labels = [r.label.lstrip(">" + _NBSP) for r in rows if not r.is_header]
        assert labels == ["AAAA0001", "AAAA0002"]


def _enumerated_codes(structure):
    """Return the set of every MDRM code the structure's items enumerate."""
    return {
        str(code).upper()
        for item in structure["items"]
        for code in (item.get("columns") or ([item["mdrm"]] if item["mdrm"] else []))
    }


class TestStructureCompleteness:
    """The committed structure must enumerate every filed value code.

    The structure is the sole source of truth: a value code a sample filer
    reports that the structure does not enumerate would render nowhere, so the
    committed ``fry9c_filed_codes.json`` fixture (the union of value-bearing,
    non-administrative codes both sample filers report at the reconciliation
    period) must be wholly covered by the committed ``structure.json``.
    """

    def _load_fixture(self):
        """Load the committed FR Y-9C filed-code fixture."""
        import json
        from pathlib import Path

        path = Path(__file__).resolve().parent / "fixtures" / "fry9c_filed_codes.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_every_filed_code_is_enumerated(self):
        """Every filed FR Y-9C value code is covered by the committed structure."""
        _load_structure.cache_clear()
        structure = _load_structure("FRY9C")
        enumerated = _enumerated_codes(structure)
        filed = {code.upper() for code in self._load_fixture()["codes"]}
        missing = sorted(filed - enumerated)
        assert not missing, (
            "FR Y-9C structure is missing filed value codes; regenerate the asset"
            f" (python -m openbb_federal_reserve.utils.fry9c_structure): {missing}"
        )

    def test_a_missing_code_is_detected(self):
        """The completeness check fails loudly when a filed code is unenumerated."""
        structure = {"items": [{"mdrm": "BHCK2170", "columns": None}]}
        enumerated = _enumerated_codes(structure)
        filed = {"BHCK2170", "BHCKPV05"}
        assert sorted(filed - enumerated) == ["BHCKPV05"]
