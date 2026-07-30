"""Tests for the FFIEC UBPR State Average Report (CDR router) model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.state_average import (
    STATE_AVERAGE_SECTIONS,
    FederalReserveStateAverageData,
    FederalReserveStateAverageFetcher,
)
from openbb_federal_reserve.utils import state_average_report

from . import ffiec_cassettes

_SECTION = {
    "section": "Summary Ratios",
    "state": "South Dakota",
    "rows": [
        {"label": "Earnings and Profitability", "is_header": True},
        {
            "label": "> Interest Income (TE)",
            "is_header": False,
            "2026-03-31": 5.31,
            "2025-12-31": 5.48,
        },
        {
            "label": "Number of banks in Peer Group",
            "is_header": False,
            "2026-03-31": 53.0,
            "2025-12-31": 53.0,
        },
    ],
}


def _patch(monkeypatch, result=None):
    """Point the section fetch at an in-memory fixture."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.state_average_report.fetch_state_average_section",
        lambda state, section, group_type="commercial", all_periods=False: (
            result if result is not None else dict(_SECTION)
        ),
    )


class TestPeerGroupResolution:
    """Tests for the state -> peer-group-id resolution."""

    def _wire(self, monkeypatch):
        """Resolve against the baked snapshot offline (no reporting cycles)."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [],
        )

    def test_commercial_id(self, monkeypatch):
        """South Dakota's commercial peer group resolves via the ``SDCOM`` name."""
        self._wire(monkeypatch)
        assert state_average_report.peer_group_id("SD", "commercial") == 281

    def test_savings_id(self, monkeypatch):
        """South Dakota's savings peer group resolves via the ``SDSVG`` name."""
        self._wire(monkeypatch)
        assert state_average_report.peer_group_id("SD", "savings") == 337

    def test_lowercase_code(self, monkeypatch):
        """The state code is case-insensitive."""
        self._wire(monkeypatch)
        assert state_average_report.peer_group_id("sd") == 281

    def test_resolves_from_live_registry(self, monkeypatch):
        """The id resolves from the live registry when reporting cycles exist."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": "151"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.peer_groups.fetch_peer_groups",
            lambda cycle_id: {"NYCOM": {"peergroupid": 271}},
        )
        assert state_average_report.peer_group_id("NY", "commercial") == 271

    def test_state_name(self):
        """The full state name resolves from the code."""
        assert state_average_report.state_name("TX") == "Texas"

    def test_unknown_state_raises(self):
        """An unknown state code raises ``ValueError``."""
        with pytest.raises(ValueError, match="Unknown state"):
            state_average_report.peer_group_id("ZZ")


class TestParseGrid:
    """Tests for the rendered-report grid parser."""

    _HTML = (
        '<tr><td class="UbprReportDateRow">3/31/2026</td>'
        '<td class="UbprReportDateRow">12/31/2025</td></tr>'
        "<tr><td>Earnings and Profitability</td><td></td><td></td></tr>"
        "<tr><td>&nbsp;Interest Income (TE)</td><td>5.31</td><td>5.48</td></tr>"
        "<tr><td>Average Total Assets</td><td>3,806,787</td><td>3,605,901</td></tr>"
        "<script>ignored</script>"
    )

    def test_dates_to_iso(self):
        """Period header dates convert to ISO order."""
        dates, _ = state_average_report._parse_grid(self._HTML)
        assert dates == ["2026-03-31", "2025-12-31"]

    def test_header_has_no_values(self):
        """A header row carries no values."""
        _, rows = state_average_report._parse_grid(self._HTML)
        assert rows[0]["values"] == []

    def test_thousands_separator_value(self):
        """Grouping separators are stripped when parsing numbers."""
        assert state_average_report._number("3,806,787") == 3806787.0
        assert state_average_report._number("") is None

    def test_no_grid_returns_empty(self):
        """Markup without a data grid yields empty results."""
        assert state_average_report._parse_grid("<html></html>") == ([], [])

    def test_concept_code_captured(self):
        """A row's concept code is read from its ``graph_descriptor`` payload."""
        descriptor = (
            '<tr><td class="UbprReportDateRow">3/31/2026</td></tr>'
            "<tr><td>&nbsp;Interest Income (TE)</td>"
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;UBPRE001&quot;}]">'
            "</td><td>5.31</td></tr>"
            "<script>ignored</script>"
        )
        _, rows = state_average_report._parse_grid(descriptor)
        assert rows[0]["concept"] == "UBPRE001"

    def test_concept_code_absent(self):
        """A row without a descriptor carries no concept code."""
        assert state_average_report._concept_code("<td></td>") is None


class TestCaption:
    """Tests for the indentation-guarding caption helper."""

    def test_indent_guarded(self):
        """A leading indent is preserved behind a ``>`` guard."""
        assert state_average_report._caption("  Interest Income").startswith(">")

    def test_flush_label_unchanged(self):
        """A flush label is returned unchanged."""
        assert state_average_report._caption("Net Income") == "Net Income"


class TestTransformQuery:
    """Tests for ``transform_query``."""

    def test_defaults(self):
        """The defaults resolve to a known state and section."""
        query = FederalReserveStateAverageFetcher.transform_query({})
        assert query.state == "SD"
        assert query.group_type == "commercial"
        assert query.section in STATE_AVERAGE_SECTIONS

    def test_unknown_state_raises(self):
        """An unknown state raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveStateAverageFetcher.transform_query({"state": "ZZ"})

    def test_unknown_group_type_raises(self):
        """An unknown group type raises ``OpenBBError``."""
        with pytest.raises(OpenBBError):
            FederalReserveStateAverageFetcher.transform_query({"group_type": "trust"})


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_returns_section_rows(self, monkeypatch):
        """The section's rows pass through from the report client."""
        _patch(monkeypatch)
        query = FederalReserveStateAverageFetcher.transform_query({"state": "SD"})
        assert len(FederalReserveStateAverageFetcher.extract_data(query, None)) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty section raises ``EmptyDataError``."""
        _patch(monkeypatch, {"section": "Summary Ratios", "state": "X", "rows": []})
        query = FederalReserveStateAverageFetcher.transform_query({"state": "SD"})
        with pytest.raises(EmptyDataError):
            FederalReserveStateAverageFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_wide_rows(self, monkeypatch):
        """Line items carry one value per period; headers carry only a label."""
        _patch(monkeypatch)
        query = FederalReserveStateAverageFetcher.transform_query({"state": "SD"})
        rows = FederalReserveStateAverageFetcher.extract_data(query, None)
        result = FederalReserveStateAverageFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReserveStateAverageData) for r in result)
        line = next(r for r in result if not r.is_header)
        assert line.model_dump()["2026-03-31"] == 5.31
        assert line.label.startswith(">")
        header = next(r for r in result if r.is_header)
        assert header.label == "Earnings and Profitability"


class TestAllPeriods:
    """Tests for the ``all_periods`` query parameter."""

    _PERIODS = [
        "2026-03-31",
        "2025-12-31",
        "2025-09-30",
        "2025-06-30",
        "2025-03-31",
        "2024-12-31",
        "2024-09-30",
    ]

    def _full(self):
        """A fixture spanning more than the recent-five cap."""
        line = {"label": "> Average Total Assets", "is_header": False}
        for index, date in enumerate(self._PERIODS):
            line[date] = 3_806_787.0 + index
        return {
            "section": "Summary Ratios",
            "state": "New York",
            "rows": [
                {"label": "Earnings and Profitability", "is_header": True},
                line,
            ],
        }

    def test_param_defaults_false(self):
        """The parameter defaults to False."""
        query = FederalReserveStateAverageFetcher.transform_query({"state": "NY"})
        assert query.all_periods is False

    def test_param_threaded(self, monkeypatch):
        """The flag reaches the report client."""
        seen = {}
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.state_average_report.fetch_state_average_section",
            lambda state, section, group_type="commercial", all_periods=False: (
                seen.update(all_periods=all_periods) or self._full()
            ),
        )
        query = FederalReserveStateAverageFetcher.transform_query(
            {"state": "NY", "all_periods": True}
        )
        FederalReserveStateAverageFetcher.extract_data(query, None)
        assert seen["all_periods"] is True

    def test_returns_more_than_five_periods(self, monkeypatch):
        """All-periods mode returns the full period history."""
        _patch(monkeypatch, self._full())
        query = FederalReserveStateAverageFetcher.transform_query(
            {"state": "NY", "all_periods": True}
        )
        rows = FederalReserveStateAverageFetcher.extract_data(query, None)
        result = FederalReserveStateAverageFetcher.transform_data(query, rows)
        line = next(r for r in result if not r.is_header)
        columns = [
            key
            for key in line.model_dump()
            if key not in ("label", "is_header", "narrative")
        ]
        assert len(columns) > 5
        assert not any(col.endswith((" PG", " PCT")) for col in columns)

    def test_monetary_scaled_x1000(self, monkeypatch):
        """A monetary line stays scaled by 1000 across the full period history."""
        from openbb_federal_reserve.utils import cache, cdr, concepts, ubpr_report

        cycles = [{"reportingcycleid": str(900 + i)} for i in range(len(self._PERIODS))]
        parsed = {
            "dates": self._PERIODS,
            "rows": [
                {
                    "label": " Average Total Assets",
                    "values": ["3,806,787"] * len(self._PERIODS),
                    "concept": "UBPRD659",
                }
            ],
        }

        monkeypatch.setattr(
            state_average_report,
            "report_sections",
            lambda: [{"pagetitle": "Summary Ratios"}],
        )
        monkeypatch.setattr(ubpr_report, "report_cycles", lambda: cycles)
        monkeypatch.setattr(cdr, "_get_session", lambda: None)
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, _producer: parsed)
        monkeypatch.setattr(
            concepts,
            "concept_index",
            lambda _name: {
                "UBPRD659": {
                    "name": "Average Total Assets",
                    "monetary": True,
                    "narrative": None,
                }
            },
        )
        monkeypatch.setattr(concepts, "indented_name", lambda label, name: name)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: {
                "UBPRD659": {
                    "description": "Average Total Assets as a percent of Average Assets",
                    "narrative": "Average of total assets over the reporting period.",
                }
            },
        )

        result = state_average_report.fetch_state_average_section(
            "NY", "Summary Ratios", all_periods=True
        )
        line = next(r for r in result["rows"] if not r["is_header"])
        columns = [k for k in line if k not in ("label", "is_header", "narrative")]
        assert len(columns) > 5
        assert line["label"] == "Average Total Assets"
        assert line["narrative"] == "Average of total assets over the reporting period."
        assert line[self._PERIODS[0]] == 3_806_787.0 * 1000


class TestPageDescriptionHeader:
    """Tests for the leading header row's page-description hover card."""

    def _build(self, monkeypatch, section, header_label="Earnings and Profitability"):
        """Run the section fetch with a single header + single line item."""
        from openbb_federal_reserve.utils import cache, cdr, concepts, ubpr_report

        periods = ["2026-03-31", "2025-12-31"]
        cycles = [{"reportingcycleid": str(900 + i)} for i in range(len(periods))]
        parsed = {
            "dates": periods,
            "rows": [
                {"label": header_label, "values": [], "concept": None},
                {
                    "label": " Interest Income (TE)",
                    "values": ["5.31", "5.48"],
                    "concept": "UBPRE001",
                },
            ],
        }
        monkeypatch.setattr(
            state_average_report,
            "report_sections",
            lambda: [{"pagetitle": section}],
        )
        monkeypatch.setattr(ubpr_report, "report_cycles", lambda: cycles)
        monkeypatch.setattr(cdr, "_get_session", lambda: None)
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, _producer: parsed)
        monkeypatch.setattr(
            concepts,
            "concept_index",
            lambda _name: {
                "UBPRE001": {"name": "Interest Income (TE)", "narrative": None}
            },
        )
        monkeypatch.setattr(concepts, "indented_name", lambda label, name: name)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: {
                "UBPRE001": {
                    "description": "Interest Income (TE)",
                    "narrative": "Total interest income on a tax-equivalent basis.",
                }
            },
        )
        return state_average_report.fetch_state_average_section("NY", section)

    def test_header_carries_page_description(self, monkeypatch):
        """The leading header row's narrative is the section's page description."""
        from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

        result = self._build(monkeypatch, "Summary Ratios")
        header = result["rows"][0]
        assert header["is_header"] is True
        assert header["narrative"] == UBPR_PAGE_DESCRIPTIONS["Summary Ratios"]

    def test_line_item_keeps_own_narrative(self, monkeypatch):
        """Line-item narratives are untouched by the header override."""
        result = self._build(monkeypatch, "Summary Ratios")
        line = next(r for r in result["rows"] if not r["is_header"])
        assert line["narrative"] == "Total interest income on a tax-equivalent basis."

    def test_unmapped_section_leaves_header_none(self, monkeypatch):
        """A section absent from the map leaves the header narrative as None."""
        result = self._build(monkeypatch, "Not A Real Section")
        assert result["rows"][0]["narrative"] is None


class TestReportSections:
    """Tests for the cached section table-of-contents producer."""

    def test_producer_filters_rows(self, monkeypatch):
        """The producer keeps dict rows with a pageid and drops the rest."""
        from openbb_federal_reserve.utils import cache, ubpr_report

        monkeypatch.setattr(
            ubpr_report,
            "_post",
            lambda _req, _crit: [
                {"pageid": "1", "pagetitle": "Summary Ratios"},
                {"pageid": "", "pagetitle": "Blank"},
                "not-a-dict",
            ],
        )
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        sections = state_average_report.report_sections()
        assert sections == [{"pageid": "1", "pagetitle": "Summary Ratios"}]


class TestField:
    """Tests for the hidden-field extractor."""

    def test_reads_value(self):
        """A matching hidden field returns its value."""
        html = '<input id="__VIEWSTATE" value="abc123" />'
        assert state_average_report._field(html, "__VIEWSTATE") == "abc123"

    def test_missing_field_returns_empty(self):
        """An absent hidden field returns an empty string."""
        assert state_average_report._field("<html></html>", "__VIEWSTATE") == ""


class TestTocTargets:
    """Tests for the table-of-contents postback-target map."""

    def test_maps_labels_to_targets(self):
        """Each section label maps to its first postback target."""
        html = (
            '<a href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02$lbItem&#39;,'
            '&#39;&#39;)">Summary Ratios</a>'
            '<a href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl03$lbItem&#39;,'
            '&#39;&#39;)">Income Statement</a>'
        )
        targets = state_average_report._toc_targets(html)
        assert targets["Summary Ratios"] == "rptTOC$rptTOC$ctl02$lbItem"
        assert targets["Income Statement"] == "rptTOC$rptTOC$ctl03$lbItem"


class TestParseGridBlankRow:
    """Tests for the grid parser skipping fully blank rows."""

    def test_all_blank_cells_skipped(self):
        """A row whose cells are all blank is skipped."""
        html = (
            '<tr><td class="UbprReportDateRow">3/31/2026</td></tr>'
            "<tr><td></td><td>  </td></tr>"
            "<tr><td>&nbsp;Interest Income (TE)</td><td>5.31</td></tr>"
            "<script>ignored</script>"
        )
        _, rows = state_average_report._parse_grid(html)
        assert len(rows) == 1
        assert rows[0]["label"].strip() == "Interest Income (TE)"


class TestUnknownSection:
    """Tests for the section-name guard in the section fetch."""

    def test_unknown_section_raises(self, monkeypatch):
        """A section absent from the page list raises ``ValueError``."""
        monkeypatch.setattr(
            state_average_report,
            "report_sections",
            lambda: [{"pagetitle": "Summary Ratios"}],
        )
        with pytest.raises(ValueError, match="Unknown report section"):
            state_average_report.fetch_state_average_section("NY", "Made Up")


class _FakeResponse:
    """A stand-in HTTP response carrying a fixed body."""

    def __init__(self, text):
        self.text = text


class _FakeSession:
    """A stand-in session returning a GET page then a POST grid."""

    def __init__(self, page, grid):
        self._page = page
        self._grid = grid
        self.posted: dict | None = None

    def get(self, _url, timeout=None):
        """Return the report landing page."""
        return _FakeResponse(self._page)

    def post(self, _url, data=None, headers=None, timeout=None):
        """Record the postback form and return the rendered grid."""
        self.posted = data
        return _FakeResponse(self._grid)


class TestProducerNetworkPath:
    """Tests for the real cycle-window producer (session GET + POST + parse)."""

    def _wire(self, monkeypatch, session):
        """Wire the section fetch to run the producer against a fake session."""
        from openbb_federal_reserve.utils import cache, cdr, concepts, ubpr_report

        cycles = [{"reportingcycleid": "900"}, {"reportingcycleid": "901"}]
        monkeypatch.setattr(
            state_average_report,
            "report_sections",
            lambda: [{"pagetitle": "Summary Ratios"}],
        )
        monkeypatch.setattr(ubpr_report, "report_cycles", lambda: cycles)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.peer_groups.resolve_peer_group_id",
            lambda name, cycle_id=None: 271,
        )
        monkeypatch.setattr(cdr, "_get_session", lambda: session)
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())
        monkeypatch.setattr(concepts, "concept_index", lambda _name: {})
        monkeypatch.setattr(concepts, "indented_name", lambda label, name: name)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: {},
        )

    def test_producer_renders_grid(self, monkeypatch):
        """The producer posts the TOC target and parses the rendered grid."""
        page = (
            '<a href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02$lbItem&#39;,'
            '&#39;&#39;)">Summary Ratios</a>'
            '<input id="__VIEWSTATE" value="vs" />'
            '<input id="__VIEWSTATEGENERATOR" value="gen" />'
        )
        grid = (
            '<tr><td class="UbprReportDateRow">3/31/2026</td>'
            '<td class="UbprReportDateRow">12/31/2025</td></tr>'
            "<tr><td>Earnings and Profitability</td><td></td><td></td></tr>"
            "<tr><td>&nbsp;Interest Income (TE)</td><td>5.31</td><td>5.48</td></tr>"
            "<script>ignored</script>"
        )
        session = _FakeSession(page, grid)
        self._wire(monkeypatch, session)
        result = state_average_report.fetch_state_average_section(
            "NY", "Summary Ratios"
        )
        posted = session.posted
        assert posted is not None
        assert posted["__EVENTTARGET"] == "rptTOC$rptTOC$ctl02$lbItem"
        assert posted["__VIEWSTATE"] == "vs"
        assert posted["__VIEWSTATEGENERATOR"] == "gen"
        line = next(r for r in result["rows"] if not r["is_header"])
        assert line["2026-03-31"] == 5.31

    def test_producer_missing_target_returns_empty(self, monkeypatch):
        """A page without the section's postback target yields no rows."""
        page = '<input id="__VIEWSTATE" value="vs" />'
        session = _FakeSession(page, "")
        self._wire(monkeypatch, session)
        result = state_average_report.fetch_state_average_section(
            "NY", "Summary Ratios"
        )
        assert session.posted is None
        assert result["rows"] == []


class TestCallSourcedNarrativeFallback:
    """Tests for the concept-index narrative fallback on Call-sourced lines."""

    def _build(self, monkeypatch):
        """Run the fetch with a Call-sourced line and a UBPR-concept line."""
        from openbb_federal_reserve.utils import cache, cdr, concepts, ubpr_report

        periods = ["2026-03-31", "2025-12-31"]
        cycles = [{"reportingcycleid": str(900 + i)} for i in range(len(periods))]
        parsed = {
            "dates": periods,
            "rows": [
                {"label": "Earnings and Profitability", "values": [], "concept": None},
                {
                    "label": " Interest Income (TE)",
                    "values": ["5.31", "5.48"],
                    "concept": "UBPRE001",
                },
                {
                    "label": " Income From Lease Financing",
                    "values": ["1.23", "1.45"],
                    "concept": "RIAD4065",
                },
            ],
        }
        monkeypatch.setattr(
            state_average_report,
            "report_sections",
            lambda: [{"pagetitle": "Summary Ratios"}],
        )
        monkeypatch.setattr(ubpr_report, "report_cycles", lambda: cycles)
        monkeypatch.setattr(cdr, "_get_session", lambda: None)
        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, _producer: parsed)
        monkeypatch.setattr(
            concepts,
            "concept_index",
            lambda _name: {
                "UBPRE001": {"name": "Interest Income (TE)", "narrative": None},
                "RIAD4065": {
                    "name": "Income From Lease Financing",
                    "narrative": "Includes amortized income from direct and leveraged"
                    " financing leases.",
                },
            },
        )
        monkeypatch.setattr(concepts, "indented_name", lambda label, name: name)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda _concepts, lines=None: {
                "UBPRE001": {
                    "description": "Interest Income (TE)",
                    "narrative": "Total interest income on a tax-equivalent basis.",
                },
                "RIAD4065": {"description": "Income From Lease Financing"},
            },
        )
        return state_average_report.fetch_state_average_section("NY", "Summary Ratios")

    def test_call_line_gains_concept_index_narrative(self, monkeypatch):
        """A Call-sourced line with no guide narrative falls back to the MDRM."""
        result = self._build(monkeypatch)
        line = next(r for r in result["rows"] if "Lease Financing" in r["label"])
        assert line["narrative"] == (
            "Includes amortized income from direct and leveraged financing leases."
        )

    def test_ubpr_line_keeps_guide_narrative(self, monkeypatch):
        """A UBPR-concept line keeps its guide narrative unchanged."""
        result = self._build(monkeypatch)
        line = next(r for r in result["rows"] if r["label"] == "Interest Income (TE)")
        assert line["narrative"] == "Total interest income on a tax-equivalent basis."


class TestStateAverageCassette:
    """Cassette-backed integration test running the full real model fetcher."""

    @pytest.fixture
    def _replayed(self):
        """Run the full fetcher under the state-average cassette with a cold cache.

        Serves the router/grid responses, parsed guide concepts and filtered
        concept index entirely from the recording, so the real producers parse the
        captured data with no live network and no pre-warmed cache.
        """
        query = FederalReserveStateAverageFetcher.transform_query(
            {"state": "SD", "section": "Summary Ratios", "group_type": "commercial"}
        )
        with ffiec_cassettes.replay("state_average"):
            rows = FederalReserveStateAverageFetcher.extract_data(query, None)
            result = FederalReserveStateAverageFetcher.transform_data(query, rows)
        return result

    def test_parses_real_section_structure(self, _replayed):
        """Headers and indented line items parse from the real captured grid."""
        headers = [row for row in _replayed if row.is_header]
        lines = [row for row in _replayed if not row.is_header]
        assert len(_replayed) > 20
        assert headers
        assert lines
        assert all(isinstance(row, FederalReserveStateAverageData) for row in _replayed)
        assert "Earnings and Profitability" in {row.label for row in headers}
        assert any(row.label.startswith(">") for row in lines)

    def test_periods_carry_real_numeric_values(self, _replayed):
        """Each period column on a line item holds a real captured float."""
        lines = [row for row in _replayed if not row.is_header]
        interest = next(
            row
            for row in lines
            if row.label.replace("\xa0", " ").startswith("> Interest Income (TE)")
        )
        dump = interest.model_dump()
        periods = [
            key
            for key in dump
            if key not in ("label", "is_header", "narrative") and dump[key] is not None
        ]
        # The cassette captures a single reporting cycle so the report-page HTML
        # stays small; one averaged value per line is replayed.
        assert len(periods) == 1
        assert all(isinstance(dump[period], float) for period in periods)
        assert dump["2026-03-31"] == 5.31

    def test_headers_carry_no_period_values(self, _replayed):
        """Section headers carry only a label, never a period value."""
        header = next(row for row in _replayed if row.is_header)
        dump = header.model_dump()
        periods = [
            key for key in dump if key not in ("label", "is_header", "narrative")
        ]
        assert all(dump[period] is None for period in periods)

    def test_line_items_carry_real_narratives(self, _replayed):
        """At least one line item resolves a real MDRM/guide narrative."""
        lines = [row for row in _replayed if not row.is_header]
        narratives = [row.narrative for row in lines if row.narrative]
        assert narratives
        assert all(len(text.strip()) > 10 for text in narratives)
