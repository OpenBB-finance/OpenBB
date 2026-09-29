"""Tests for the FFIEC bank-supervision subrouter and its commands."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openbb_core.app.route_iter import iter_api_routes

from openbb_federal_reserve import ffiec

_COMMAND_NAMES = (
    "institutions",
    "call_report",
    "ubpr",
    "executive_summary",
    "custom_peer_group",
    "peer_group_average",
    "peer_group_bank",
    "peer_group_distribution",
    "state_average",
    "list_of_banks_peer_group",
    "call_report_sectioned",
    "country_exposure",
    "large_holding_companies",
    "institution_structure",
    "bhcpr_report",
    "bhcpr",
    "financial_report",
    "financial_report_pdf",
)


class TestFfiecRoutes:
    """The FFIEC subrouter registers its commands and utility endpoints."""

    def test_command_routes_registered(self):
        """Every FFIEC command binds on the subrouter as a bare path."""
        paths = {route.path for route in iter_api_routes(ffiec.router.api_router)}
        for name in _COMMAND_NAMES:
            assert f"/{name}" in paths, name

    def test_bhcpr_utility_routes_registered(self):
        """The BHCPR download and choices endpoints bind on the subrouter."""
        paths = {route.path for route in iter_api_routes(ffiec.router.api_router)}
        assert {"/bhcpr_report_download", "/bhcpr_report_choices"} <= paths

    def test_financial_report_options_routes_registered(self):
        """The financial-report options endpoints bind on the subrouter."""
        paths = {route.path for route in iter_api_routes(ffiec.router.api_router)}
        assert {"/report_types", "/report_periods", "/report_sections"} <= paths

    def test_financial_report_pdf_routes_registered(self):
        """The filed-PDF choices and download endpoints bind on the subrouter."""
        paths = {route.path for route in iter_api_routes(ffiec.router.api_router)}
        assert {
            "/financial_report_pdf_choices",
            "/financial_report_pdf_download",
        } <= paths

    def test_bhcpr_sections_route_registered(self):
        """The BHCPR data-section options endpoint binds on the subrouter."""
        paths = {route.path for route in iter_api_routes(ffiec.router.api_router)}
        assert "/bhcpr_sections" in paths


class TestBhcprSections:
    """Tests for the ``bhcpr_sections`` options endpoint."""

    @pytest.mark.asyncio
    async def test_lists_sections_with_all_first(self):
        """Sections follow an "All Sections" choice, Summary Ratios first."""
        choices = await ffiec.bhcpr_sections()
        assert choices[0] == {"label": "All Sections", "value": "All Sections"}
        assert choices[1] == {"label": "Summary Ratios", "value": "Summary Ratios"}
        assert all(choice["label"] == choice["value"] for choice in choices[1:])


class TestReportTypes:
    """Tests for the ``report_types`` options endpoint."""

    @pytest.mark.asyncio
    async def test_lists_ready_reports(self):
        """Every ready report is offered as a ``{label, value}`` choice."""
        choices = await ffiec.report_types()
        values = {choice["value"] for choice in choices}
        assert {
            "FRY9C",
            "FRY9LP",
            "FRY9SP",
            "FFIEC002",
            "FFIEC101",
            "FFIEC102",
            "FRY15",
            "FRQ1",
        } <= values
        assert all(choice["label"] for choice in choices)

    @pytest.mark.asyncio
    async def test_intersects_with_firm_filed_reports(self, monkeypatch):
        """A selected RSSD narrows the choices to the firm's filed ready reports."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FFIEC101": {"name": None, "periods": []},
                "FFIEC102": {"name": None, "periods": []},
                "FRY2320": {"name": None, "periods": []},
            },
        )
        choices = await ffiec.report_types("852218")
        # Only ready reports the firm files survive; FRY9C (filed by HCs, not this
        # bank) and FRY2320 (not a ready report) are both excluded.
        assert {c["value"] for c in choices} == {"FFIEC101", "FFIEC102"}

    @pytest.mark.asyncio
    async def test_labels_with_official_profile_name(self, monkeypatch):
        """Each option is labelled by the profile's official NIC name when present."""
        official = (
            "Regulatory Capital Reporting for Institutions Subject to the"
            " Advanced Capital Adequacy Framework (FFIEC 101)"
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FFIEC101": {"name": official, "periods": []},
                "FFIEC102": {"name": None, "periods": []},
            },
        )
        choices = await ffiec.report_types("852218")
        labels = {c["value"]: c["label"] for c in choices}
        assert labels["FFIEC101"] == official
        # A series lacking a profile name falls back to its ready-report name.
        assert labels["FFIEC102"] == "FFIEC 102 Market Risk Regulatory Report"

    @pytest.mark.asyncio
    async def test_falls_back_to_all_ready_when_profile_fails(self, monkeypatch):
        """An unavailable profile falls back to offering every ready report."""

        def _boom(rssd):
            """Raise to simulate an unavailable NIC profile."""
            raise RuntimeError("profile down")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _boom,
        )
        choices = await ffiec.report_types("852218")
        assert {"FRY9C", "FFIEC101", "FRQ1"} <= {c["value"] for c in choices}


class TestReportPeriods:
    """Tests for the ``report_periods`` options endpoint."""

    @pytest.mark.asyncio
    async def test_blank_rssd_returns_empty(self):
        """Without a selected institution there are no periods to offer."""
        assert await ffiec.report_periods("") == []

    @pytest.mark.asyncio
    async def test_lists_filed_periods_as_quarter_ends(self, monkeypatch):
        """A report's filed periods become ``"YYYY Qn"`` / ``YYYYMMDD`` choices."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FFIEC102": {
                    "name": None,
                    "periods": [
                        {"year": 2026, "quarter": 1, "month_day": "3/31"},
                        {"year": 2025, "quarter": 4, "month_day": "12/31"},
                    ],
                }
            },
        )
        choices = await ffiec.report_periods("852218", "ffiec102")
        assert choices == [
            {"label": "2026 Q1", "value": "20260331"},
            {"label": "2025 Q4", "value": "20251231"},
        ]

    @pytest.mark.asyncio
    async def test_profile_failure_returns_empty(self, monkeypatch):
        """An unavailable profile yields no period choices."""

        def _boom(rssd):
            """Raise to simulate an unavailable NIC profile."""
            raise RuntimeError("profile down")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _boom,
        )
        assert await ffiec.report_periods("852218", "FFIEC102") == []

    @pytest.mark.asyncio
    async def test_non_mapping_result_returns_empty(self, monkeypatch):
        """A non-mapping result (e.g. a stale cache shape) yields no choices."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: ["FFIEC102"],
        )
        assert await ffiec.report_periods("852218", "FFIEC102") == []


class TestBhcprPeriods:
    """Tests for the ``bhcpr_periods`` options endpoint."""

    @pytest.mark.asyncio
    async def test_delegates_to_report_periods_for_bhcpr(self, monkeypatch):
        """``bhcpr_periods`` reads the firm's filed BHCPR periods."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "BHCPR": {
                    "name": None,
                    "periods": [{"year": 2026, "quarter": 1, "month_day": "3/31"}],
                }
            },
        )
        assert await ffiec.bhcpr_periods("1039502") == [
            {"label": "2026 Q1", "value": "20260331"}
        ]

    @pytest.mark.asyncio
    async def test_blank_rssd_returns_empty(self):
        """A blank firm yields no periods without a lookup."""
        assert await ffiec.bhcpr_periods() == []
        assert await ffiec.bhcpr_periods("  ") == []

    @pytest.mark.asyncio
    async def test_resolves_non_filer_before_listing_periods(self, monkeypatch):
        """A bank is resolved to its BHCPR-filing holder before periods are listed."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.resolve_bhcpr_holder",
            lambda rssd: "1039502",
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: (
                {
                    "BHCPR": {
                        "name": None,
                        "periods": [{"year": 2026, "quarter": 1, "month_day": "3/31"}],
                    }
                }
                if rssd == "1039502"
                else {}
            ),
        )
        assert await ffiec.bhcpr_periods("852218") == [
            {"label": "2026 Q1", "value": "20260331"}
        ]


class TestReportSections:
    """Tests for the ``report_sections`` options endpoint."""

    @pytest.mark.asyncio
    async def test_lists_schedules_with_all_sections_first(self):
        """A report's schedules are listed after an "All Sections" choice."""
        choices = await ffiec.report_sections("FFIEC102")
        assert choices[0] == {"label": "All Sections", "value": None}
        assert {"label": "Market Risk Regulatory Report", "value": "RC"} in choices

    @pytest.mark.asyncio
    async def test_omits_cover_schedule(self):
        """The administrative cover schedule is excluded from the choices."""
        choices = await ffiec.report_sections("FRY9C")
        assert all(choice["value"] != "COVER" for choice in choices)

    @pytest.mark.asyncio
    async def test_omits_cover_schedule_by_name(self):
        """FFIEC 002 codes its cover page other than ``COVER``; it drops by name."""
        choices = await ffiec.report_sections("FFIEC002")
        assert all(choice["label"] != "Cover Page" for choice in choices)
        assert {"label": "Schedule RAL - Assets and Liabilities", "value": "RAL"} in (
            choices
        )

    @pytest.mark.asyncio
    async def test_unknown_report_returns_empty(self):
        """An unknown report code yields no choices."""
        assert await ffiec.report_sections("NOPE") == []


class TestFinancialReportPdfChoices:
    """Tests for the ``financial_report_pdf_choices`` options endpoint."""

    @pytest.mark.asyncio
    async def test_missing_firm_returns_empty(self):
        """Without a firm there are no PDFs to offer, whatever the report type."""
        assert await ffiec.financial_report_pdf_choices() == []
        assert await ffiec.financial_report_pdf_choices(None, "FRY9C") == []

    @pytest.mark.asyncio
    async def test_no_report_type_lists_latest_of_each(self, monkeypatch):
        """A firm with no report type selected (the default state) is never empty.

        The file selector must offer files for a filer even before a report is
        picked, so the endpoint lists the latest filed PDF of each report the firm
        files rather than short-circuiting to an empty list.
        """
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FFIEC101": {
                    "name": "FFIEC 101",
                    "periods": [
                        {"year": 2026, "quarter": 1, "month_day": "3/31"},
                        {"year": 2025, "quarter": 4, "month_day": "12/31"},
                    ],
                },
                "FFIEC102": {
                    "name": "FFIEC 102",
                    "periods": [{"year": 2026, "quarter": 1, "month_day": "3/31"}],
                },
            },
        )
        choices = await ffiec.financial_report_pdf_choices("852218")
        assert [c["label"] for c in choices] == [
            "FFIEC 101 — 2026 Q1",
            "FFIEC 102 — 2026 Q1",
        ]

    @pytest.mark.asyncio
    async def test_builds_pdf_url_choices_newest_first(self, monkeypatch):
        """Each filed period becomes a labelled ReturnFinancialReportPDF URL."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            lambda rssd: {
                "FRY9C": {
                    "name": None,
                    "periods": [
                        {"year": 2025, "quarter": 1, "month_day": "3/31"},
                        {"year": 2024, "quarter": 4, "month_day": "12/31"},
                    ],
                }
            },
        )
        choices = await ffiec.financial_report_pdf_choices("1039502", "FRY9C")
        assert choices == [
            {
                "label": "2025 Q1",
                "value": "https://www.ffiec.gov/npw/FinancialReport/"
                "ReturnFinancialReportPDF?rpt=FRY9C&id=1039502&dt=20250331",
            },
            {
                "label": "2024 Q4",
                "value": "https://www.ffiec.gov/npw/FinancialReport/"
                "ReturnFinancialReportPDF?rpt=FRY9C&id=1039502&dt=20241231",
            },
        ]

    @pytest.mark.asyncio
    async def test_profile_failure_returns_empty(self, monkeypatch):
        """An unavailable profile yields no choices."""

        def _boom(rssd):
            """Raise to simulate an unavailable NIC profile."""
            raise RuntimeError("profile down")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.fetch_institution_financial_reports",
            _boom,
        )
        assert await ffiec.financial_report_pdf_choices("1039502", "FRY9C") == []


class TestFinancialReportPdfDownload:
    """Tests for the ``financial_report_pdf_download`` utility endpoint."""

    _URL = (
        "https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportPDF"
        "?rpt=FRY9C&id=1039502&dt=20250331"
    )

    @pytest.mark.asyncio
    async def test_base64_encodes_pdf(self, monkeypatch):
        """Each fetched PDF is base64-encoded with a descriptive filename."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_financial_report_pdf",
            lambda url: b"%PDF-1.7 body",
        )
        out = await ffiec.financial_report_pdf_download({"url": [self._URL]})
        assert out[0]["data_format"]["data_type"] == "pdf"
        assert out[0]["data_format"]["filename"] == "FRY9C_1039502_20250331.pdf"
        assert out[0]["content"]

    @pytest.mark.asyncio
    async def test_download_error_with_args_is_captured(self, monkeypatch):
        """A failure carrying args records the first arg as the message."""

        def _boom(url):
            """Raise to simulate a failed download."""
            raise RuntimeError("nope")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_financial_report_pdf", _boom
        )
        out = await ffiec.financial_report_pdf_download({"url": [self._URL]})
        assert out[0]["error_type"] == "download_error"
        assert out[0]["content"] == "RuntimeError: nope"
        assert out[0]["filename"] == "FRY9C_1039502_20250331.pdf"

    @pytest.mark.asyncio
    async def test_download_error_without_args_falls_back_to_str(self, monkeypatch):
        """A failure with no args falls back to ``str(exc)`` for the message."""

        def _boom(url):
            """Raise with no args to exercise the str fallback."""
            raise RuntimeError()

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_financial_report_pdf", _boom
        )
        out = await ffiec.financial_report_pdf_download({"url": [self._URL]})
        assert out[0]["content"] == "RuntimeError: "

    @pytest.mark.asyncio
    async def test_filename_falls_back_to_last_segment(self, monkeypatch):
        """A URL lacking the report query params falls back to its last segment."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_financial_report_pdf",
            lambda url: b"%PDF body",
        )
        out = await ffiec.financial_report_pdf_download(
            {"url": ["https://x/path/raw.pdf"]}
        )
        assert out[0]["data_format"]["filename"] == "raw.pdf"

    @pytest.mark.asyncio
    async def test_empty_url_list_returns_empty(self):
        """An absent ``url`` key yields an empty result list."""
        assert await ffiec.financial_report_pdf_download({}) == []


class TestBhcprReportChoices:
    """Tests for the ``bhcpr_report_choices`` utility endpoint."""

    @pytest.mark.asyncio
    async def test_filters_by_peer_group_and_year(self, monkeypatch):
        """``bhcpr_report_choices`` filters the index by peer group and year."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.list_bhcpr_reports",
            lambda: [
                {
                    "name": "a.pdf",
                    "url": "https://x/a.pdf",
                    "peer_group": 1,
                    "year": 2024,
                    "quarter": 1,
                    "period_end": "2024-03-31",
                },
                {
                    "name": "b.pdf",
                    "url": "https://x/b.pdf",
                    "peer_group": 2,
                    "year": 2024,
                    "quarter": 1,
                    "period_end": "2024-03-31",
                },
            ],
        )
        choices = await ffiec.bhcpr_report_choices(peer_group="1", year=2024)
        assert choices == [{"label": "Q1 2024", "value": "https://x/a.pdf"}]

    @pytest.mark.asyncio
    async def test_returns_all_when_unfiltered(self, monkeypatch):
        """With no filters every report is returned, newest first."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.list_bhcpr_reports",
            lambda: [
                {
                    "url": "https://x/old.pdf",
                    "peer_group": 1,
                    "year": 2023,
                    "quarter": 4,
                },
                {
                    "url": "https://x/new.pdf",
                    "peer_group": 1,
                    "year": 2024,
                    "quarter": 1,
                },
            ],
        )
        choices = await ffiec.bhcpr_report_choices()
        assert [c["value"] for c in choices] == [
            "https://x/new.pdf",
            "https://x/old.pdf",
        ]


class TestBhcprReportDownload:
    """Tests for the ``bhcpr_report_download`` utility endpoint."""

    @pytest.mark.asyncio
    async def test_base64_encodes_pdf(self, monkeypatch):
        """``bhcpr_report_download`` base64-encodes each fetched PDF."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_bhcpr_pdf",
            lambda url: b"%PDF-1.7 body",
        )
        out = await ffiec.bhcpr_report_download(
            {"url": ["https://www.ffiec.gov/npw/StaticData/bhcpRRPT/x.pdf"]}
        )
        assert out[0]["data_format"]["data_type"] == "pdf"
        assert out[0]["data_format"]["filename"] == "x.pdf"
        assert out[0]["content"]

    @pytest.mark.asyncio
    async def test_download_error_with_args_is_captured(self, monkeypatch):
        """A failure carrying args records the first arg as the message."""

        def _boom(url):
            """Raise to simulate a failed download."""
            raise RuntimeError("nope")

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_bhcpr_pdf", _boom
        )
        out = await ffiec.bhcpr_report_download({"url": ["https://x/y.pdf"]})
        assert out[0]["error_type"] == "download_error"
        assert out[0]["content"] == "RuntimeError: nope"
        assert out[0]["filename"] == "y.pdf"

    @pytest.mark.asyncio
    async def test_download_error_without_args_falls_back_to_str(self, monkeypatch):
        """A failure with no args falls back to ``str(exc)`` for the message."""

        def _boom(url):
            """Raise with no args to exercise the str fallback."""
            raise RuntimeError()

        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ffiec.download_bhcpr_pdf", _boom
        )
        out = await ffiec.bhcpr_report_download({"url": ["https://x/z.pdf"]})
        assert out[0]["content"] == "RuntimeError: "

    @pytest.mark.asyncio
    async def test_empty_url_list_returns_empty(self):
        """An absent ``url`` key yields an empty result list."""
        assert await ffiec.bhcpr_report_download({}) == []


class TestFfiecCommandBodies:
    """Each FFIEC command delegates to ``OBBject.from_query``."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", _COMMAND_NAMES)
    async def test_command_delegates_to_from_query(self, name):
        """The command awaits ``OBBject.from_query`` and returns its result."""
        sentinel = object()
        with (
            patch.object(ffiec, "Query", new=MagicMock()),
            patch.object(
                ffiec.OBBject, "from_query", new=AsyncMock(return_value=sentinel)
            ) as mock_from_query,
        ):
            out = await getattr(ffiec, name)(
                cc=MagicMock(),
                provider_choices=MagicMock(),
                standard_params=MagicMock(),
                extra_params=MagicMock(),
            )
        assert out is sentinel
        mock_from_query.assert_awaited_once()
