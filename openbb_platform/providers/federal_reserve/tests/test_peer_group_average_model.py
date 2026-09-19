"""Tests for the FFIEC UBPR Peer Group Average Report (CDR) model."""

import re

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.peer_group_average import (
    PGA_SECTIONS,
    FederalReservePeerGroupAverageData,
    FederalReservePeerGroupAverageFetcher,
)
from openbb_federal_reserve.utils import peer_group_report

from .ffiec_cassettes import replay

_ISO_PERIOD = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_SECTION = {
    "section": "Summary Ratios--Page 1",
    "peer_group": "Insured commercial banks having assets greater than $100 billion",
    "rows": [
        {"label": "Earnings and Profitability", "is_header": True},
        {
            "label": ">   Interest Income (TE)",
            "is_header": False,
            "2026-03-31": 4.43,
            "2025-12-31": 4.69,
        },
        {
            "label": ">      Net Income",
            "is_header": False,
            "2026-03-31": 1.11,
            "2025-12-31": 1.15,
        },
    ],
}


def _patch(monkeypatch, result=None):
    """Point the section fetch at an in-memory fixture; resolve via the snapshot."""
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ubpr_report.report_cycles",
        lambda: [],
    )
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.peer_group_report.fetch_peer_group_section",
        lambda peergroupid, section, all_periods=False: (
            result if result is not None else dict(_SECTION)
        ),
    )


class TestResolvePeerGroupId:
    """Tests for the peer-group-name -> URL peergroupid resolution."""

    def _wire(self, monkeypatch, registry):
        """Point the live ``PGSelector`` registry at an offline fixture."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": "151"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.peer_groups.fetch_peer_groups",
            lambda cycle_id: registry,
        )

    def test_resolves_from_live_registry(self, monkeypatch):
        """A name resolves to the live registry's ``peergroupid``."""
        self._wire(monkeypatch, {"1": {"peergroupid": 4}})
        assert peer_group_report.resolve_peer_group_id("1") == 4

    def test_falls_back_to_static_snapshot(self, monkeypatch):
        """A name absent from the live registry falls back to the baked snapshot."""
        self._wire(monkeypatch, {})
        assert peer_group_report.resolve_peer_group_id("ALCOM") == 236

    def test_whitespace_and_case_tolerated(self, monkeypatch):
        """Surrounding whitespace and case are normalised before resolution."""
        self._wire(monkeypatch, {})
        assert peer_group_report.resolve_peer_group_id("  national ") == 2

    def test_no_cycles_uses_static_snapshot(self, monkeypatch):
        """With no reporting cycles the baked snapshot resolves the name."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [],
        )
        assert peer_group_report.resolve_peer_group_id("1") == 4

    def test_unknown_group_raises(self, monkeypatch):
        """An unknown peer-group name raises ``ValueError``."""
        self._wire(monkeypatch, {})
        with pytest.raises(ValueError, match="Unknown peer group"):
            peer_group_report.resolve_peer_group_id("ZZZ")


class TestCaption:
    """Tests for the indentation-guarding caption helper."""

    def test_indent_guarded(self):
        """A leading indent is preserved behind a ``>`` guard."""
        assert peer_group_report._caption("  Interest Income").startswith(">")

    def test_flush_label_unchanged(self):
        """A flush label is returned unchanged."""
        assert peer_group_report._caption("Net Income") == "Net Income"


class TestDateHelpers:
    """Tests for the report date helpers."""

    def test_iso_conversion(self):
        """A report cell date converts to an ISO date string."""
        assert peer_group_report._iso("3/31/2026") == "2026-03-31"

    def test_date_key_orders_newest_first(self):
        """The date key sorts cell dates chronologically."""
        dates = ["3/31/2025", "3/31/2026", "12/31/2025"]
        assert sorted(dates, key=peer_group_report._date_key, reverse=True) == [
            "3/31/2026",
            "12/31/2025",
            "3/31/2025",
        ]


class TestToc:
    """Tests for the table-of-contents parser."""

    _SHELL = (
        '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl01$lbItem'
        '&#39;,&#39;&#39;)">Cover Page</a>'
        '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02$lbItem'
        '&#39;,&#39;&#39;)">Summary Ratios</a>'
    )

    def test_maps_title_to_control(self):
        """Each section title maps to its postback control target."""
        toc = peer_group_report._toc(self._SHELL)
        assert toc["Summary Ratios"] == "rptTOC$rptTOC$ctl02$lbItem"

    def test_includes_cover_page(self):
        """The cover page control is present in the raw table of contents."""
        assert "Cover Page" in peer_group_report._toc(self._SHELL)


class TestParseRows:
    """Tests for the rendered-report grid parser."""

    _ROW = (
        '<tr><td class="UbprReportDataRow" style="width:20%;">'
        "&nbsp;&nbsp;&nbsp;Interest Income (TE)</td>"
        '<td id="dttrend_1_0" data-graph_set="'
        "[{&quot;category&quot;:&quot;12/31/2025&quot;,&quot;name&quot;:&quot;BANK"
        "&quot;,&quot;value&quot;:&quot;4.69&quot;},"
        "{&quot;category&quot;:&quot;3/31/2026&quot;,&quot;name&quot;:&quot;BANK"
        '&quot;,&quot;value&quot;:&quot;4.43&quot;}]"></td></tr>'
        '<tr><td class="UbprReportDataRow">Earnings and Profitability</td>'
        '<td id="dttrend_1_1" data-graph_set="'
        "[{&quot;category&quot;:&quot;3/31/2026&quot;,&quot;name&quot;:&quot;BANK"
        '&quot;,&quot;value&quot;:&quot;null&quot;}]"></td></tr>'
    )

    def test_parses_label_and_series(self):
        """A data row yields its label, concept code, and date-keyed values."""
        rows = peer_group_report._parse_rows(self._ROW)
        label, code, series = rows[0]
        assert "Interest Income (TE)" in label
        assert code is None
        assert series["3/31/2026"] == 4.43
        assert series["12/31/2025"] == 4.69

    def test_parses_concept_code(self):
        """A row's ``data-graph_descriptor`` yields the MDRM concept code."""
        row = (
            '<tr><td class="UbprReportDataRow">Net Income</td>'
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;UBPR4340'
            '&quot;}]" data-graph_set="[{&quot;category&quot;:&quot;3/31/2026'
            "&quot;,&quot;name&quot;:&quot;BANK&quot;,&quot;value&quot;:"
            '&quot;1.11&quot;}]"></td></tr>'
        )
        label, code, series = peer_group_report._parse_rows(row)[0]
        assert code == "UBPR4340"
        assert series["3/31/2026"] == 1.11

    def test_null_value_is_none(self):
        """A ``null`` graph value parses to ``None``."""
        rows = peer_group_report._parse_rows(self._ROW)
        _, _, series = rows[1]
        assert series["3/31/2026"] is None

    @pytest.mark.parametrize("token", ["##", "--", "NA", "N/A", "", None])
    def test_non_numeric_token_is_none(self, token):
        """A non-numeric peer-group token (``##``, ``--``, ``NA``...) maps to ``None``."""
        assert peer_group_report._value(token) is None

    def test_numeric_token_parsed(self):
        """A numeric token parses to a float."""
        assert peer_group_report._value("4.43") == 4.43

    def test_row_without_data_cell_skipped(self):
        """A ``<tr>`` lacking a ``UbprReportDataRow`` label cell is skipped."""
        page = (
            "<tr><td>Header chrome</td></tr>"
            '<tr><td class="UbprReportDataRow">Net Income</td>'
            '<td data-graph_set="[{&quot;category&quot;:&quot;3/31/2026&quot;,'
            "&quot;name&quot;:&quot;BANK&quot;,&quot;value&quot;:&quot;1.11"
            '&quot;}]"></td></tr>'
        )
        rows = peer_group_report._parse_rows(page)
        assert len(rows) == 1
        assert rows[0][0] == "Net Income"


class TestPeerGroupDescription:
    """Tests for the report-header peer group description extractor."""

    def test_reads_description(self):
        """The peer group description is read from the rendered header."""
        page = (
            '<table id="headerTable"><tr>'
            "<td>UBPR Peer Group Average Report</td>"
            "<td>Insured commercial banks having assets greater than $100 billion</td>"
            "</tr></table>"
        )
        assert peer_group_report._peer_group_description(page) == (
            "Insured commercial banks having assets greater than $100 billion"
        )

    def test_missing_header_returns_none(self):
        """Markup without a header table yields ``None``."""
        assert peer_group_report._peer_group_description("<html></html>") is None

    def test_header_without_matching_cell_returns_none(self):
        """A header table with no peer-group cell yields ``None``."""
        page = (
            '<table id="headerTable"><tr>'
            "<td>UBPR Peer Group Average Report</td>"
            "<td>Report Date 3/31/2026</td>"
            "</tr></table>"
        )
        assert peer_group_report._peer_group_description(page) is None


class TestReportSections:
    """Tests for the report table-of-contents fetch."""

    def test_drops_cover_page(self, monkeypatch):
        """The fetched section list excludes the cover page."""
        shell = (
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl01'
            '$lbItem&#39;,&#39;&#39;)">Cover Page</a>'
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02'
            '$lbItem&#39;,&#39;&#39;)">Summary Ratios</a>'
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": "1"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(shell, shell),
        )
        sections = peer_group_report.report_sections(4)
        assert sections == ["Summary Ratios"]


class TestFetchSectionBatch:
    """Tests for the per-batch section render."""

    def test_unknown_section_raises(self, monkeypatch):
        """A section absent from the table of contents raises ``ValueError``."""
        shell = (
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl01'
            '$lbItem&#39;,&#39;&#39;)">Cover Page</a>'
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02'
            '$lbItem&#39;,&#39;&#39;)">Summary Ratios</a>'
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(shell, shell),
        )
        with pytest.raises(ValueError, match="Unknown report section"):
            peer_group_report._fetch_section_batch(4, "Nonexistent Page", "1")


class TestTransformQuery:
    """Tests for ``transform_query``."""

    def test_defaults(self):
        """The defaults resolve to a known peer group and section."""
        query = FederalReservePeerGroupAverageFetcher.transform_query({})
        assert query.peer_group == "1"
        assert query.section in PGA_SECTIONS


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_returns_section_rows(self, monkeypatch):
        """The section's rows pass through from the report client."""
        _patch(monkeypatch)
        query = FederalReservePeerGroupAverageFetcher.transform_query(
            {"peer_group": "1"}
        )
        assert len(FederalReservePeerGroupAverageFetcher.extract_data(query, None)) == 3

    def test_empty_raises(self, monkeypatch):
        """An empty section raises ``EmptyDataError``."""
        _patch(
            monkeypatch, {"section": "Summary Ratios", "peer_group": "x", "rows": []}
        )
        query = FederalReservePeerGroupAverageFetcher.transform_query(
            {"peer_group": "1"}
        )
        with pytest.raises(EmptyDataError):
            FederalReservePeerGroupAverageFetcher.extract_data(query, None)

    def test_unknown_group_raises(self, monkeypatch):
        """An unknown peer group raises ``OpenBBError`` before any fetch."""
        _patch(monkeypatch)
        query = FederalReservePeerGroupAverageFetcher.transform_query(
            {"peer_group": "99"}
        )
        with pytest.raises(OpenBBError):
            FederalReservePeerGroupAverageFetcher.extract_data(query, None)


class _Session:
    """A canned session returning the report shell, then the section grid."""

    def __init__(self, shell, page):
        """Store the shell and section payloads to serve in order."""
        self._shell = shell
        self._page = page

    def get(self, url, timeout=None):
        """Return the report shell on the initial ``GET``."""
        return type("R", (), {"text": self._shell})()

    def post(self, url, data=None, timeout=None):
        """Return the rendered section grid on the TOC postback."""
        return type("R", (), {"text": self._page})()


def _graph_set(values):
    """Build a ``data-graph_set`` payload from ``{date: value}`` pairs."""
    template = (
        "{&quot;category&quot;:&quot;DATE&quot;,&quot;name&quot;:&quot;BANK"
        "&quot;,&quot;value&quot;:&quot;VALUE&quot;}"
    )
    points = ",".join(
        template.replace("DATE", date).replace("VALUE", str(value))
        for date, value in values.items()
    )
    return f"[{points}]"


class TestFetchPeerGroupSectionPeriods:
    """Tests for the recent-periods cap and the ``all_periods`` time series."""

    _DATES = [
        "3/31/2026",
        "12/31/2025",
        "9/30/2025",
        "6/30/2025",
        "3/31/2025",
        "12/31/2024",
    ]

    def _wire(self, monkeypatch):
        """Point the client at canned cycles, session, and concept metadata."""
        cycles = [
            {"reportingcycleid": str(i), "enddateformatted": date}
            for i, date in enumerate(self._DATES)
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: cycles,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        values = {date: 1.5 for date in self._DATES}
        shell = (
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02'
            '$lbItem&#39;,&#39;&#39;)">Summary Ratios</a>'
        )
        page = (
            '<tr><td class="UbprReportDataRow">Total Assets</td>'
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;UBPR2170'
            f'&quot;}}]" data-graph_set="{_graph_set(values)}"></td></tr>'
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(shell, page),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda name: {"UBPR2170": {"monetary": True, "name": "Tot Assets"}},
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                "UBPR2170": {
                    "description": "Total Assets as a percent of Average Assets",
                    "narrative": "Total assets as reported on the balance sheet.",
                }
            },
        )

    def test_default_caps_at_five_periods(self, monkeypatch):
        """The default fetch returns only the five most recent periods."""
        self._wire(monkeypatch)
        rows = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")["rows"]
        line = next(r for r in rows if not r["is_header"])
        periods = sorted(k for k in line if _ISO_PERIOD.match(k))
        assert len(periods) == 5

    def test_all_periods_returns_full_history(self, monkeypatch):
        """``all_periods`` returns every reported period as ``<ISO>`` columns."""
        self._wire(monkeypatch)
        rows = peer_group_report.fetch_peer_group_section(
            4, "Summary Ratios", all_periods=True
        )["rows"]
        line = next(r for r in rows if not r["is_header"])
        periods = sorted(k for k in line if _ISO_PERIOD.match(k))
        assert len(periods) == 6
        assert not any(k.endswith((" PG", " PCT")) for k in line)

    def test_monetary_line_scaled_in_both_modes(self, monkeypatch):
        """A monetary line is scaled x1000 in both the default and full modes."""
        self._wire(monkeypatch)
        default = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")
        full = peer_group_report.fetch_peer_group_section(
            4, "Summary Ratios", all_periods=True
        )
        for result in (default, full):
            line = next(r for r in result["rows"] if not r["is_header"])
            assert line["2026-03-31"] == 1500.0

    def test_line_narrative_from_guide(self, monkeypatch):
        """A line item's narrative is sourced from the guide, headers stay ``None``."""
        self._wire(monkeypatch)
        rows = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")["rows"]
        line = next(r for r in rows if not r["is_header"])
        assert line["narrative"] == "Total assets as reported on the balance sheet."

    def test_line_label_from_guide_description(self, monkeypatch):
        """A line item's label is the cleaned guide Description, not the MDRM name."""
        self._wire(monkeypatch)
        rows = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")["rows"]
        line = next(r for r in rows if not r["is_header"])
        assert line["label"] == "Total Assets"

    def test_leading_header_carries_page_description(self, monkeypatch):
        """The leading header row's narrative is the section's UBPR page description."""
        from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

        self._wire_with_header(monkeypatch)
        rows = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")["rows"]
        assert rows[0]["is_header"] is True
        assert all(not _ISO_PERIOD.match(k) or rows[0][k] is None for k in rows[0])
        assert rows[0]["narrative"] == UBPR_PAGE_DESCRIPTIONS["Summary Ratios"]
        line = next(r for r in rows if not r["is_header"])
        assert line["narrative"] == "Total assets as reported on the balance sheet."

    def _wire_with_header(self, monkeypatch):
        """Wire the client with a leading header row preceding the data row."""
        self._wire(monkeypatch)
        values = {date: 1.5 for date in self._DATES}
        shell = (
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02'
            '$lbItem&#39;,&#39;&#39;)">Summary Ratios</a>'
        )
        page = (
            '<tr><td class="UbprReportDataRow">Earnings and Profitability</td>'
            "<td></td></tr>"
            '<tr><td class="UbprReportDataRow">Total Assets</td>'
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;UBPR2170'
            f'&quot;}}]" data-graph_set="{_graph_set(values)}"></td></tr>'
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(shell, page),
        )

    def _wire_call_sourced(self, monkeypatch):
        """Wire a UBPR line plus a Call-sourced (RIAD) line lacking a guide narrative."""
        self._wire(monkeypatch)
        values = {date: 1.5 for date in self._DATES}
        shell = (
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02'
            '$lbItem&#39;,&#39;&#39;)">Summary Ratios</a>'
        )
        page = (
            '<tr><td class="UbprReportDataRow">Total Assets</td>'
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;UBPR2170'
            f'&quot;}}]" data-graph_set="{_graph_set(values)}"></td></tr>'
            '<tr><td class="UbprReportDataRow">Income From Lease Financing</td>'
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;RIAD4065'
            f'&quot;}}]" data-graph_set="{_graph_set(values)}"></td></tr>'
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(shell, page),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda name: {
                "UBPR2170": {"monetary": True, "name": "Tot Assets"},
                "RIAD4065": {
                    "monetary": False,
                    "name": "Income From Lease Financing",
                    "narrative": "Includes amortized income from direct and "
                    "leveraged financing leases.",
                },
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                "UBPR2170": {
                    "description": "Total Assets as a percent of Average Assets",
                    "narrative": "Total assets as reported on the balance sheet.",
                },
                "RIAD4065": {"description": "Income From Lease Financing"},
            },
        )

    def test_blank_label_row_skipped(self, monkeypatch):
        """A parsed row whose label is blank is dropped before shaping."""
        self._wire(monkeypatch)
        values = {date: 1.5 for date in self._DATES}
        shell = (
            '<a id="lbItem" href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl02'
            '$lbItem&#39;,&#39;&#39;)">Summary Ratios</a>'
        )
        page = (
            '<tr><td class="UbprReportDataRow">   </td>'
            f'<td data-graph_set="{_graph_set(values)}"></td></tr>'
            '<tr><td class="UbprReportDataRow">Total Assets</td>'
            '<td data-graph_descriptor="[{&quot;conceptname&quot;:&quot;UBPR2170'
            f'&quot;}}]" data-graph_set="{_graph_set(values)}"></td></tr>'
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(shell, page),
        )
        rows = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")["rows"]
        assert all(r["label"].strip() for r in rows)

    def test_call_sourced_line_uses_concept_index_narrative(self, monkeypatch):
        """A Call-sourced (RIAD) line with no guide narrative falls back to the index."""
        self._wire_call_sourced(monkeypatch)
        rows = peer_group_report.fetch_peer_group_section(4, "Summary Ratios")["rows"]
        ubpr = next(r for r in rows if r["label"] == "Total Assets")
        call = next(r for r in rows if r["label"] == "Income from Lease Financing")
        assert ubpr["narrative"] == "Total assets as reported on the balance sheet."
        assert call["narrative"] == (
            "Includes amortized income from direct and leveraged financing leases."
        )


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_wide_rows(self, monkeypatch):
        """Line items carry one value per period; headers carry only a label."""
        _patch(monkeypatch)
        query = FederalReservePeerGroupAverageFetcher.transform_query(
            {"peer_group": "1"}
        )
        rows = FederalReservePeerGroupAverageFetcher.extract_data(query, None)
        result = FederalReservePeerGroupAverageFetcher.transform_data(query, rows)
        assert all(isinstance(r, FederalReservePeerGroupAverageData) for r in result)
        line = next(r for r in result if not r.is_header)
        assert line.model_dump()["2026-03-31"] == 4.43
        assert line.label.startswith(">")
        header = next(r for r in result if r.is_header)
        assert header.label == "Earnings and Profitability"


class TestCassetteIntegration:
    """Run the full fetcher against a recorded FFIEC peer-group cassette."""

    def test_real_summary_ratios_parses_from_cassette(self):
        """The full pipeline parses the real captured Summary Ratios section.

        Replays the recorded ``UbprReport.aspx`` shell and section render, the
        router responses, the parsed guide concepts and the filtered concept index,
        running ``transform_query`` -> ``extract_data`` -> ``transform_data`` so the
        actual parse executes on the peer group's real captured averages with no
        live network and no pre-warmed cache.
        """
        with replay("peer_group_average"):
            query = FederalReservePeerGroupAverageFetcher.transform_query(
                {"peer_group": "1", "section": "Summary Ratios"}
            )
            rows = FederalReservePeerGroupAverageFetcher.extract_data(query, None)
            result = FederalReservePeerGroupAverageFetcher.transform_data(query, rows)

        assert query.section == "Summary Ratios"
        assert result
        assert all(isinstance(r, FederalReservePeerGroupAverageData) for r in result)

        headers = [r for r in result if r.is_header]
        lines = [r for r in result if not r.is_header]
        assert len(headers) > 1
        assert len(lines) > 1

        header_labels = {h.label for h in headers}
        assert "Earnings and Profitability" in header_labels
        assert "Margin Analysis:" in header_labels
        assert "Liquidity" in header_labels

        assert result[0].is_header is True
        assert result[0].label == "Earnings and Profitability"
        assert result[0].narrative

        income = next(r for r in lines if "Interest Income (TE)" in r.label)
        assert income.label.startswith(">")
        assert income.narrative and income.narrative.startswith(
            "All income from earning assets"
        )

        net_income = next(
            r
            for r in lines
            if r.label.startswith(">") and r.label.endswith("Net Income")
        )
        dumped = net_income.model_dump()
        # The cassette captures a single reporting cycle so the report-page HTML
        # stays small; the report-builder grid carries one averaged value per line.
        assert dumped["2026-03-31"] == 1.11

        period_cols = [k for k in dumped if _ISO_PERIOD.match(k)]
        assert set(period_cols) == {"2026-03-31"}

        for item in lines:
            value = item.model_dump()["2026-03-31"]
            assert value is not None
            assert isinstance(value, (int, float))
            assert not isinstance(value, bool)

        for header in headers:
            dump = header.model_dump()
            assert all(dump.get(k) is None for k in dump if _ISO_PERIOD.match(k))

        labels = {r.label for r in result}
        assert "Summary Ratios--Page 1" not in labels
        assert not any(label.endswith((" PG", " PCT")) for label in labels)
