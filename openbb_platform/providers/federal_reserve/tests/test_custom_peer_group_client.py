"""Tests for the FFIEC CDR Custom Peer Group report client helpers."""

import json

import pytest

from openbb_federal_reserve.utils import custom_peer_group as cpg


class TestSectionIndex:
    """Tests for ``_section_index``."""

    def test_default_section(self):
        """A missing section resolves to the first table-of-contents page."""
        assert cpg._section_index(None) == 0

    def test_named_section_is_case_insensitive(self):
        """A section title resolves regardless of case."""
        assert cpg._section_index("balance sheet $") == cpg.UBPR_SECTIONS.index(
            "Balance Sheet $"
        )

    def test_unknown_section_raises(self):
        """An unknown section title raises ``ValueError``."""
        with pytest.raises(ValueError):
            cpg._section_index("Not A Section")


class TestGraphKey:
    """Tests for ``_graph_key``."""

    def test_strips_leading_zeros(self):
        """The graph-set key drops zero-padding from month and day."""
        assert cpg._graph_key("03/31/2026") == "3/31/2026"
        assert cpg._graph_key("12/31/2025") == "12/31/2025"


class TestCaption:
    """Tests for ``_caption``."""

    def test_no_indent_passthrough(self):
        """A flush-left caption is returned unchanged."""
        assert cpg._caption("Net Income") == "Net Income"

    def test_indent_guarded_with_marker_and_nbsp(self):
        """An indented caption gains a leading marker and non-breaking spaces."""
        out = cpg._caption("  Interest Income (TE)")
        assert out.startswith(">")
        assert "  " in out
        assert out.endswith("Interest Income (TE)")


class TestBankName:
    """Tests for ``_bank_name``."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            (
                "JPMORGAN CHASE BANK, NATIONAL ASSOCIATION",
                "JPMorgan Chase Bank, National Association",
            ),
            ("BANK OF AMERICA, N.A.", "Bank of America, N.A."),
            (
                "WELLS FARGO BANK,  NATIONAL  ASSOCIATION",
                "Wells Fargo Bank, National Association",
            ),
            ("ASSOCIATED BANK, NA", "Associated Bank, NA"),
        ],
    )
    def test_titles_all_caps_name(self, raw, expected):
        """An all-caps FFIEC name is rendered readable with acronyms preserved."""
        assert cpg._bank_name(raw) == expected


class TestExtractBankName:
    """Tests for ``_extract_bank_name``."""

    _HEADER = (
        '<table id="headerTable"><tr>'
        '<td class="UbprReportHeadings" colspan="2">JPMORGAN CHASE BANK,'
        " NATIONAL ASSOCIATION; COLUMBUS, OH</td></tr></table>"
    )

    def test_reads_name_from_header_table(self):
        """The readable bank name is read from the header table's name cell."""
        assert (
            cpg._extract_bank_name(self._HEADER, "852218")
            == "JPMorgan Chase Bank, National Association"
        )

    def test_missing_header_table_falls_back_to_rssd(self):
        """A page without the header table falls back to the RSSD identifier."""
        assert cpg._extract_bank_name("<html>no header</html>", "852218") == "852218"

    def test_header_without_name_cell_falls_back_to_rssd(self):
        """A header table without a ``NAME; CITY`` cell falls back to the RSSD."""
        html = '<table id="headerTable"><tr><td>FDIC # 628</td></tr></table>'
        assert cpg._extract_bank_name(html, "852218") == "852218"

    def test_blank_name_cell_falls_back_to_rssd(self):
        """A name cell whose name part is blank falls back to the RSSD."""
        html = (
            '<table id="headerTable"><tr>'
            '<td class="UbprReportHeadings" colspan="2">; COLUMBUS, OH</td>'
            "</tr></table>"
        )
        assert cpg._extract_bank_name(html, "852218") == "852218"


class TestParseGrid:
    """Tests for ``_parse_grid``."""

    def _grid(self, graph_set):
        """Build a minimal rendered section grid around one data row."""
        payload = json.dumps(graph_set).replace('"', "&quot;")
        return (
            '<table id="tableReportData">'
            '<tr><td class="UbprReportDataRow">Earnings and Profitability</td></tr>'
            '<tr><td class="UbprReportDataRow">  Interest Income (TE)</td>'
            f'<td id="dttrend_1" data-graph_set="{payload}"></td></tr>'
            "</table>"
        )

    def test_drops_pg_pct_and_names_column_by_bank_name(self):
        """Only BANK survives as a ``"<ISO> <bank name>"`` column; PG/PCT drop."""
        graph_set = [
            {"category": "12/31/2025", "name": "BANK", "value": "4.52"},
            {"category": "12/31/2025", "name": "PG", "value": "4.61"},
            {"category": "12/31/2025", "name": "PCT", "value": "35"},
        ]
        rows = cpg._parse_grid(
            self._grid(graph_set),
            ["12/31/2025"],
            {"12/31/2025": "2025-12-31"},
            "JPMorgan Chase Bank, National Association",
        )
        assert rows[0] == {"label": "Earnings and Profitability", "is_header": True}
        line = rows[1]
        assert line["is_header"] is False
        assert line["label"].startswith(">")
        assert line["2025-12-31 JPMorgan Chase Bank, National Association"] == 4.52
        assert not any(
            key.endswith(" PG") or key.endswith(" PCT") or key.endswith(" Bank")
            for key in line
        )

    def test_all_null_period_is_header(self):
        """A line whose every period value is null is flagged as a header."""
        graph_set = [
            {"category": "12/31/2025", "name": "BANK", "value": "null"},
            {"category": "12/31/2025", "name": "PG", "value": "null"},
            {"category": "12/31/2025", "name": "PCT", "value": "null"},
        ]
        rows = cpg._parse_grid(
            self._grid(graph_set),
            ["12/31/2025"],
            {"12/31/2025": "2025-12-31"},
            "JPMorgan Chase Bank, National Association",
        )
        assert rows[1]["is_header"] is True
        assert rows[1]["2025-12-31 JPMorgan Chase Bank, National Association"] is None

    def test_missing_table_returns_empty(self):
        """A response without the report table yields no rows."""
        assert (
            cpg._parse_grid("<html>no grid</html>", ["12/31/2025"], {}, "852218") == []
        )

    def test_multiple_periods_named_by_bank_name(self):
        """Each period contributes its own ``"<ISO> <bank name>"`` bank column."""
        graph_set = [
            {"category": "12/31/2025", "name": "BANK", "value": "60892000"},
            {"category": "9/30/2025", "name": "BANK", "value": "78813000"},
        ]
        rows = cpg._parse_grid(
            self._grid(graph_set),
            ["12/31/2025", "9/30/2025"],
            {"12/31/2025": "2025-12-31", "9/30/2025": "2025-09-30"},
            "JPMorgan Chase Bank, National Association",
        )
        line = rows[1]
        name = "JPMorgan Chase Bank, National Association"
        assert line["is_header"] is False
        assert line[f"2025-12-31 {name}"] == 60892000.0
        assert line[f"2025-09-30 {name}"] == 78813000.0


class TestSetPeerGroup:
    """Tests for ``_set_peer_group``."""

    def test_posts_search_and_session_data(self, monkeypatch):
        """The peer list is searched then registered on the CDR session."""
        calls: list[tuple[str, dict]] = []
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: calls.append((requestor_id, criteria)),
        )
        cpg._set_peer_group(object(), "852218,451965", "999")
        assert calls[0] == (
            "CpgSearchBanks",
            {"ReportingCycleID": "999", "FIList": "852218,451965"},
        )
        assert calls[1] == (
            "SetSessionData",
            {
                "SessionData": "852218,451965",
                "SourceObject": "__UbprReportCustomIDRSSDs",
            },
        )


class _Response:
    """A minimal HTTP response exposing ``text``."""

    def __init__(self, text):
        self.text = text


class _Session:
    """A fake CDR session recording its GET/POST calls."""

    def __init__(self, page, rendered):
        self._page = page
        self._rendered = rendered
        self.get_calls: list[str] = []
        self.post_calls: list[tuple[str, dict]] = []

    def get(self, url, timeout=None):
        """Record the report-page GET and return the view-state page."""
        self.get_calls.append(url)
        return _Response(self._page)

    def post(self, url, data, timeout=None):
        """Record the section postback and return the rendered grid."""
        self.post_calls.append((url, data))
        return _Response(self._rendered)


class TestRenderSection:
    """Tests for ``_render_section``."""

    _PAGE = (
        '<input type="hidden" id="__VIEWSTATE" value="vs1" />'
        '<input type="hidden" id="__VIEWSTATEGENERATOR" value="gen1" />'
        '<input type="hidden" id="__EVENTVALIDATION" value="ev1" />'
    )

    def test_posts_back_section_with_view_state(self):
        """The report page is fetched then the section TOC link is posted back."""
        session = _Session(self._PAGE, "<table id='tableReportData'></table>")
        rendered = cpg._render_section(session, "852218", "1,2,3", 0)
        assert rendered == "<table id='tableReportData'></table>"
        url = session.get_calls[0]
        assert "rptid=288" in url
        assert "idrssd=852218" in url
        assert "rptCycleIds=1,2,3" in url
        assert "usetrimmed=0" in url
        _, payload = session.post_calls[0]
        assert payload["__EVENTTARGET"] == "rptTOC$rptTOC$ctl02$lbItem"
        assert payload["__VIEWSTATE"] == "vs1"
        assert payload["__VIEWSTATEGENERATOR"] == "gen1"
        assert payload["__EVENTVALIDATION"] == "ev1"

    def test_section_offset_encoded(self):
        """The section offset is encoded as the table-of-contents postback target."""
        session = _Session(self._PAGE, "")
        cpg._render_section(session, "1", "5", 3)
        assert "rptid=288" in session.get_calls[0]
        _, payload = session.post_calls[0]
        assert payload["__EVENTTARGET"] == "rptTOC$rptTOC$ctl05$lbItem"


class TestMergeBatches:
    """Tests for ``_merge_batches``."""

    def test_appends_rows_absent_from_base(self):
        """A later batch row past the base length is appended verbatim."""
        newest = [{"label": "Earnings", "is_header": True}]
        older = [
            {"label": "Earnings", "is_header": True},
            {
                "label": ">  Extra Line",
                "is_header": False,
                "concept": "Z",
                "2025-12-31": 2.0,
            },
        ]
        merged = cpg._merge_batches([newest, older])
        assert len(merged) == 2
        assert merged[1]["label"] == ">  Extra Line"
        assert merged[1]["2025-12-31"] == 2.0
        assert merged[1]["is_header"] is False

    def test_unions_period_columns_newest_first(self):
        """Per-batch rows merge by index, unioning ``<ISO>`` value columns."""
        newest = [
            {"label": "Earnings", "is_header": True},
            {
                "label": ">  Net Income",
                "is_header": False,
                "concept": "X",
                "2026-03-31": 1.5,
            },
        ]
        older = [
            {"label": "Earnings", "is_header": True},
            {
                "label": ">  Net Income",
                "is_header": False,
                "concept": "X",
                "2025-12-31": 1.4,
            },
        ]
        merged = cpg._merge_batches([newest, older])
        keys = [k for k in merged[1] if k.startswith("20")]
        assert keys == ["2026-03-31", "2025-12-31"]
        assert merged[1]["2026-03-31"] == 1.5
        assert merged[1]["2025-12-31"] == 1.4

    def test_header_recomputed_from_merged_values(self):
        """A line null in the newest batch but valued later is not a header."""
        newest = [
            {
                "label": ">  Late Line",
                "is_header": True,
                "concept": "Y",
                "2026-03-31": None,
            },
        ]
        older = [
            {
                "label": ">  Late Line",
                "is_header": False,
                "concept": "Y",
                "2025-12-31": 9.0,
            },
        ]
        merged = cpg._merge_batches([newest, older])
        assert merged[0]["is_header"] is False

    def test_empty_batches_returns_empty(self):
        """No batches yields no rows."""
        assert cpg._merge_batches([]) == []


class TestConceptCode:
    """Tests for ``_concept_code``."""

    def test_reads_concept_from_guide_anchor(self):
        """The concept code is read from the label cell's user-guide anchor."""
        cell = (
            '<a href="/Public/Reports/InteractiveUserGuide.aspx?Report=upbr'
            '&LineID=1&Concept=UBPRE002&ReportDate=3/31/2026">- Interest Expense</a>'
        )
        assert cpg._concept_code(cell) == "UBPRE002"

    def test_no_anchor_is_none(self):
        """A label cell without a concept anchor resolves to ``None``."""
        assert cpg._concept_code("<span>Earnings and Profitability</span>") is None


class TestEnrich:
    """Tests for ``_enrich``."""

    _INDEX = {
        "UBPR4010": {
            "name": "Interest and Fee Income on Loans; Total",
            "narrative": None,
            "monetary": True,
        },
        "UBPRE003": {
            "name": "Net Income",
            "narrative": None,
            "monetary": False,
        },
        "RIAD4065": {
            "name": "Income from Lease Financing Receivables",
            "narrative": "Includes amortized income from direct and leveraged"
            " financing leases.",
            "monetary": True,
        },
    }

    _GUIDE = {
        "UBPR4010": {
            "description": "Interest and Fee Income on Loans as a percent of"
            " Average Assets",
            "narrative": "Total interest and fee income on loans.",
        },
        "UBPRE003": {
            "description": "Net Income as a percent of Average Assets",
            "narrative": "Net income as a percent of average assets.",
        },
        "RIAD4065": {
            "description": "Income from Lease Financing Receivables",
            "narrative": None,
        },
    }

    def _patch_index(self, monkeypatch):
        """Point the concept index and guide at in-memory fixtures."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda product, form_type: self._INDEX,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                code: dict(data) for code, data in self._GUIDE.items()
            },
        )

    def test_monetary_line_scaled_and_named(self, monkeypatch):
        """A monetary line gets its full name and bank value scaled to dollars."""
        self._patch_index(monkeypatch)
        name = "JPMorgan Chase Bank, National Association"
        rows = cpg._enrich(
            [
                {
                    "label": ">  Interest and Fees on Loans",
                    "is_header": False,
                    "concept": "UBPR4010",
                    f"2025-12-31 {name}": 22631000.0,
                }
            ]
        )
        row = rows[0]
        assert row["label"] == ">  Interest and Fee Income on Loans"
        assert row["narrative"] == self._GUIDE["UBPR4010"]["narrative"]
        assert row[f"2025-12-31 {name}"] == 22631000000.0
        assert "concept" not in row

    def test_monetary_multiple_period_columns_scaled(self, monkeypatch):
        """Every monetary ``"<ISO> <bank name>"`` column is scaled to dollars."""
        self._patch_index(monkeypatch)
        name = "JPMorgan Chase Bank, National Association"
        rows = cpg._enrich(
            [
                {
                    "label": ">  Interest and Fees on Loans",
                    "is_header": False,
                    "concept": "UBPR4010",
                    f"2025-12-31 {name}": 22631000.0,
                    f"2025-09-30 {name}": 21000000.0,
                }
            ]
        )
        assert rows[0][f"2025-12-31 {name}"] == 22631000000.0
        assert rows[0][f"2025-09-30 {name}"] == 21000000000.0

    def test_non_monetary_line_unscaled(self, monkeypatch):
        """A ratio line keeps its values and gains a narrative."""
        self._patch_index(monkeypatch)
        name = "JPMorgan Chase Bank, National Association"
        rows = cpg._enrich(
            [
                {
                    "label": "Net Income",
                    "is_header": False,
                    "concept": "UBPRE003",
                    f"2025-12-31 {name}": 1.31,
                }
            ]
        )
        assert rows[0]["label"] == "Net Income"
        assert rows[0][f"2025-12-31 {name}"] == 1.31
        assert rows[0]["narrative"] == self._GUIDE["UBPRE003"]["narrative"]

    def test_unknown_concept_keeps_caption(self, monkeypatch):
        """A line with no matching concept keeps its caption and a null narrative."""
        self._patch_index(monkeypatch)
        name = "JPMorgan Chase Bank, National Association"
        rows = cpg._enrich(
            [
                {
                    "label": ">  Some Caption",
                    "is_header": False,
                    "concept": None,
                    f"2025-12-31 {name}": 5.0,
                }
            ]
        )
        assert rows[0]["label"] == ">  Some Caption"
        assert rows[0]["narrative"] is None
        assert rows[0][f"2025-12-31 {name}"] == 5.0

    def test_call_sourced_line_uses_concept_index_narrative(self, monkeypatch):
        """A Call-sourced line falls back to the concept-index (MDRM) narrative."""
        self._patch_index(monkeypatch)
        name = "JPMorgan Chase Bank, National Association"
        rows = cpg._enrich(
            [
                {
                    "label": ">  Income From Lease Financing Receivables",
                    "is_header": False,
                    "concept": "RIAD4065",
                    f"2025-12-31 {name}": 1000.0,
                },
                {
                    "label": "Net Income",
                    "is_header": False,
                    "concept": "UBPRE003",
                    f"2025-12-31 {name}": 1.31,
                },
            ]
        )
        assert rows[0]["narrative"] == self._INDEX["RIAD4065"]["narrative"]
        assert rows[1]["narrative"] == self._GUIDE["UBPRE003"]["narrative"]

    def test_header_row_narrative_none(self, monkeypatch):
        """A header row is left labelled with a null narrative and no concept."""
        self._patch_index(monkeypatch)
        rows = cpg._enrich([{"label": "Earnings and Profitability", "is_header": True}])
        assert rows[0]["label"] == "Earnings and Profitability"
        assert rows[0]["narrative"] is None
        assert "concept" not in rows[0]


class TestNumber:
    """Tests for ``_number``."""

    def test_parses_numeric_string(self):
        """A numeric token parses to a float."""
        assert cpg._number("4.52") == 4.52

    @pytest.mark.parametrize("token", ["##", "--", "NA", "N/A", "", "null", None, "  "])
    def test_non_numeric_token_is_none(self, token):
        """A non-numeric token, including the ``##`` peer-group flag, is ``None``."""
        assert cpg._number(token) is None


class TestLeadingHeaderNarrative:
    """Tests for the section page description on the leading header row."""

    def test_header_row_carries_page_description(self, monkeypatch):
        """The leading header row's narrative is the section's page description."""
        from openbb_federal_reserve.utils.ubpr_pages import UBPR_PAGE_DESCRIPTIONS

        rows = [
            {"label": "Earnings and Profitability", "is_header": True},
            {
                "label": ">  Net Income",
                "is_header": False,
                "narrative": "Net income as a percent of average assets.",
                "2025-12-31 JPMorgan Chase Bank, National Association": 1.31,
            },
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": "1", "enddateformatted": "12/31/2025"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: rows,
        )
        result = cpg.fetch_custom_peer_group(
            "852218", "852218,451965", "Summary Ratios"
        )
        assert result["section"] == "Summary Ratios"
        header = result["rows"][0]
        assert header["is_header"] is True
        assert header["narrative"] == UBPR_PAGE_DESCRIPTIONS["Summary Ratios"]
        assert (
            result["rows"][1]["narrative"]
            == "Net income as a percent of average assets."
        )

    def test_section_absent_from_map_leaves_header_narrative_none(self, monkeypatch):
        """A section absent from the page-description map yields a null narrative."""
        rows = [{"label": "Some Header", "is_header": True}]
        monkeypatch.setattr(cpg, "UBPR_PAGE_DESCRIPTIONS", {})
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": "1", "enddateformatted": "12/31/2025"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: rows,
        )
        result = cpg.fetch_custom_peer_group("852218", "852218", "Summary Ratios")
        assert result["rows"][0]["narrative"] is None


class TestProducer:
    """Tests for the ``_producer`` body driven through ``fetch_custom_peer_group``."""

    _PAGE = (
        '<input type="hidden" id="__VIEWSTATE" value="vs1" />'
        '<input type="hidden" id="__VIEWSTATEGENERATOR" value="gen1" />'
        '<input type="hidden" id="__EVENTVALIDATION" value="ev1" />'
    )

    def _grid(self, graph_set):
        """Build a rendered section grid around one data row."""
        payload = json.dumps(graph_set).replace('"', "&quot;")
        return (
            '<table id="headerTable"><tr>'
            '<td class="UbprReportHeadings" colspan="2">JPMORGAN CHASE BANK,'
            " NATIONAL ASSOCIATION; COLUMBUS, OH</td></tr></table>"
            '<table id="tableReportData">'
            '<tr><td class="UbprReportDataRow">Earnings and Profitability</td></tr>'
            '<tr><td class="UbprReportDataRow">'
            '<a href="?Concept=UBPRE003">  Net Income</a></td>'
            f'<td data-graph_set="{payload}"></td></tr>'
            "</table>"
        )

    def _patch_common(self, monkeypatch, cycles, grid):
        """Patch the network, session, cache, and enrichment seams."""
        session = _Session(self._PAGE, grid)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session", lambda: session
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: None,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles", lambda: cycles
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda product, form_type: {
                "UBPRE003": {"name": "Net Income", "narrative": None, "monetary": False}
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                "UBPRE003": {
                    "description": "Net Income as a percent of Average Assets",
                    "narrative": "Net income as a percent of average assets.",
                }
            },
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        return session

    def test_single_request_branch(self, monkeypatch):
        """all_periods=False renders one section request and enriches the grid."""
        cycles = [
            {"reportingcycleid": "1", "enddateformatted": "12/31/2025"},
            {"reportingcycleid": "2", "enddateformatted": "09/30/2025"},
        ]
        graph_set = [
            {"category": "12/31/2025", "name": "BANK", "value": "1.31"},
            {"category": "12/31/2025", "name": "PG", "value": "1.40"},
            {"category": "12/31/2025", "name": "PCT", "value": "60"},
            {"category": "9/30/2025", "name": "BANK", "value": "1.20"},
            {"category": "9/30/2025", "name": "PG", "value": "1.30"},
            {"category": "9/30/2025", "name": "PCT", "value": "55"},
        ]
        session = self._patch_common(monkeypatch, cycles, self._grid(graph_set))
        result = cpg.fetch_custom_peer_group(
            "852218", "852218, 451965 ,", "Summary Ratios", periods=2
        )
        name = "JPMorgan Chase Bank, National Association"
        assert result["section"] == "Summary Ratios"
        assert len(session.post_calls) == 1
        line = result["rows"][1]
        assert line["label"].endswith("Net Income")
        assert line["narrative"] == "Net income as a percent of average assets."
        assert line[f"2025-12-31 {name}"] == 1.31
        assert line[f"2025-09-30 {name}"] == 1.20
        assert not any(
            key.endswith(" Bank") or key.endswith(" PG") or key.endswith(" PCT")
            for key in line
        )

    def test_all_periods_batches_branch(self, monkeypatch):
        """all_periods=True renders the history in five-period batches and merges."""
        cycles = [
            {"reportingcycleid": str(i), "enddateformatted": f"12/31/{2025 - i}"}
            for i in range(7)
        ]
        graph_set = [
            {"category": f"12/31/{2025 - i}", "name": "BANK", "value": "1.31"}
            for i in range(7)
        ]
        session = self._patch_common(monkeypatch, cycles, self._grid(graph_set))
        result = cpg.fetch_custom_peer_group(
            "852218", "852218", "Summary Ratios", all_periods=True
        )
        name = "JPMorgan Chase Bank, National Association"
        assert len(session.post_calls) == 2
        line = result["rows"][1]
        assert line[f"2025-12-31 {name}"] == 1.31
        assert line[f"2019-12-31 {name}"] == 1.31
        assert not any(key.endswith(" Bank") for key in line)


class TestFieldExtraction:
    """Tests for ``_field``."""

    def test_reads_hidden_input_value(self):
        """A hidden ASP.NET field's value is read from the page markup."""
        html = '<input type="hidden" id="__VIEWSTATE" value="abc123" />'
        assert cpg._field("__VIEWSTATE", html) == "abc123"

    def test_missing_field_is_empty(self):
        """A field absent from the page resolves to an empty string."""
        assert cpg._field("__VIEWSTATE", "<html></html>") == ""
