"""Tests for the FFIEC UBPR Peer Group Average Distribution client helpers."""

import pytest

from openbb_federal_reserve.utils import peer_group_distribution as pgd

_NBSP = " "


class TestGrid:
    """Tests for ``_grid``."""

    def _grid(self, rows):
        """Build a minimal rendered distribution table around ``rows``."""
        header = "".join(
            f"<td>{name}</td>" for name in ["Line Item", *pgd.PERCENTILE_COLUMNS]
        )
        body = ""
        for cells in rows:
            body += "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
        return f'<table id="tableReportData"><tr>{header}</tr>{body}</table>'

    def test_parses_values_and_headers(self):
        """A valued row yields percentile floats; a label-only row is a header."""
        html = self._grid(
            [
                ["Percent of Average Assets:"],
                ["&nbsp;&nbsp;&nbsp;Interest Income (TE)"]
                + ["2.32"]
                + ["2.50" for _ in pgd.PERCENTILE_COLUMNS[1:]],
            ]
        )
        rows = pgd._grid(html)
        assert rows[0]["label"] == "Percent of Average Assets:"
        assert rows[0]["is_header"] is True
        assert rows[1]["is_header"] is False
        assert rows[1]["label"].startswith(">")
        assert rows[1]["1ST"] == 2.32
        assert rows[1]["5TH"] == 2.50
        assert pgd.PEER_GROUP_COLUMN not in rows[1]

    def test_memo_footer_routed_to_peer_group_column(self):
        """A row populating only the first data column is a peer-group aggregate."""
        html = self._grid(
            [
                ["Average Total Assets"]
                + ["17,551,127,411"]
                + ["" for _ in pgd.PERCENTILE_COLUMNS[1:]],
            ]
        )
        rows = pgd._grid(html)
        assert rows[0]["is_header"] is False
        assert rows[0][pgd.PEER_GROUP_COLUMN] == 17551127411.0
        assert "1ST" not in rows[0]

    def test_blank_label_row_skipped(self):
        """A row whose label cell is empty is dropped."""
        html = self._grid([[_NBSP, *["" for _ in pgd.PERCENTILE_COLUMNS]]])
        assert pgd._grid(html) == []

    def test_missing_table_returns_empty(self):
        """A response without the report table yields no rows."""
        assert pgd._grid("<html>no grid</html>") == []

    def test_table_with_only_empty_rows_returns_empty(self):
        """A table whose rows carry no cells parses to no rows."""
        html = '<table id="tableReportData"><tr></tr><tr></tr></table>'
        assert pgd._grid(html) == []


class TestEnrich:
    """Tests for ``_enrich``."""

    _INDEX = {
        "UBPRD659": {
            "name": "Institution Quarterly Avg Assets Calendar Yr",
            "narrative": "Pseudo MDRM.",
            "monetary": True,
        },
        "UBPR4340": {
            "name": "Net Income (Loss)",
            "narrative": "Pseudo MDRM.",
            "monetary": True,
        },
        "UBPRE013": {
            "name": "Net Income",
            "narrative": "Pseudo MDRM.",
            "monetary": False,
        },
        "UBPRE001": {
            "name": "Interest Income (Tax Equivalent)",
            "narrative": "Pseudo MDRM.",
            "monetary": False,
        },
    }

    _GUIDE = {
        "UBPRD659": {
            "description": "Average Total Assets as a percent of Average Assets",
            "narrative": "Average amount of total assets.",
        },
        "UBPR4340": {
            "description": "Net Income",
            "narrative": "Net income for the period.",
        },
        "UBPRE001": {
            "description": "Interest Income (TE) as a percent of Average Assets",
            "narrative": "Total interest income on a tax-equivalent basis.",
        },
    }

    def _patch_guide(self, monkeypatch):
        """Patch the guide concept fetch to an offline fixture."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.guide.fetch_guide_concepts",
            lambda concepts, lines=None: {
                c: self._GUIDE[c] for c in concepts if c in self._GUIDE
            },
        )

    def test_monetary_memo_scaled_and_named(self, monkeypatch):
        """A monetary memo aggregate gets its full name and scaled peer-group value."""
        self._patch_guide(monkeypatch)
        rows = pgd._enrich(
            [
                {
                    "label": "Average Total Assets",
                    "is_header": False,
                    pgd.PEER_GROUP_COLUMN: 17551127411.0,
                }
            ],
            {"Average Total Assets": "UBPRD659"},
            self._INDEX,
        )
        row = rows[0]
        assert row["label"] == "Average Total Assets"
        assert row["narrative"] == "Average amount of total assets."
        assert row[pgd.PEER_GROUP_COLUMN] == 17551127411000.0

    def test_memo_net_income_pins_dollar_concept(self, monkeypatch):
        """The Net Income memo resolves to its dollar concept, not the ratio line."""
        self._patch_guide(monkeypatch)
        rows = pgd._enrich(
            [
                {
                    "label": "Net Income",
                    "is_header": False,
                    pgd.PEER_GROUP_COLUMN: 52457451.0,
                }
            ],
            {"Net Income": "UBPRE013"},
            self._INDEX,
        )
        assert rows[0]["narrative"] == "Net income for the period."
        assert rows[0][pgd.PEER_GROUP_COLUMN] == 52457451000.0

    def test_bank_count_memo_unscaled(self, monkeypatch):
        """The bank-count memo has no concept and is left unscaled."""
        self._patch_guide(monkeypatch)
        rows = pgd._enrich(
            [
                {
                    "label": "Number of Banks in Peer Group",
                    "is_header": False,
                    pgd.PEER_GROUP_COLUMN: 29.0,
                }
            ],
            {},
            self._INDEX,
        )
        assert rows[0][pgd.PEER_GROUP_COLUMN] == 29.0
        assert rows[0]["narrative"] is None

    def test_non_monetary_line_unscaled(self, monkeypatch):
        """A ratio line keeps its values, gains a full name and guide narrative."""
        self._patch_guide(monkeypatch)
        rows = pgd._enrich(
            [
                {
                    "label": f">{_NBSP}{_NBSP}{_NBSP}Interest Income (TE)",
                    "is_header": False,
                    "1ST": 2.32,
                }
            ],
            {"Interest Income (TE)": "UBPRE001"},
            self._INDEX,
        )
        assert rows[0]["label"] == f">{_NBSP}{_NBSP}{_NBSP}Interest Income (TE)"
        assert rows[0]["1ST"] == 2.32
        assert (
            rows[0]["narrative"] == "Total interest income on a tax-equivalent basis."
        )

    def test_unknown_caption_keeps_label(self, monkeypatch):
        """A line with no matching concept keeps its caption and a null narrative."""
        self._patch_guide(monkeypatch)
        rows = pgd._enrich(
            [{"label": ">  Some Caption", "is_header": False, "1ST": 5.0}],
            {},
            self._INDEX,
        )
        assert rows[0]["label"] == ">  Some Caption"
        assert rows[0]["narrative"] is None
        assert rows[0]["1ST"] == 5.0

    def test_header_row_narrative_none(self, monkeypatch):
        """A header row is left labelled with a null narrative."""
        self._patch_guide(monkeypatch)
        rows = pgd._enrich(
            [{"label": "Earnings and Profitability", "is_header": True}],
            {},
            self._INDEX,
        )
        assert rows[0]["label"] == "Earnings and Profitability"
        assert rows[0]["narrative"] is None

    def test_call_sourced_line_falls_back_to_index_narrative(self, monkeypatch):
        """A Call-sourced line with no guide narrative gains the concept-index one."""
        self._patch_guide(monkeypatch)
        index = {
            "RIAD4065": {
                "name": "Income from Lease Financing Receivables",
                "narrative": "Includes amortized income from direct and leveraged financing leases.",
                "monetary": False,
            },
            "UBPRE001": {
                "name": "Interest Income (Tax Equivalent)",
                "narrative": None,
                "monetary": False,
            },
        }
        rows = pgd._enrich(
            [
                {
                    "label": ">  Income from Lease Financing",
                    "is_header": False,
                    "1ST": 0.12,
                },
                {
                    "label": ">  Interest Income (TE)",
                    "is_header": False,
                    "1ST": 2.32,
                },
            ],
            {
                "Income from Lease Financing": "RIAD4065",
                "Interest Income (TE)": "UBPRE001",
            },
            index,
        )
        assert (
            rows[0]["narrative"]
            == "Includes amortized income from direct and leveraged financing leases."
        )
        assert (
            rows[1]["narrative"] == "Total interest income on a tax-equivalent basis."
        )


class TestNumber:
    """Tests for ``_number``."""

    def test_parses_numeric_tokens(self):
        """Comma-grouped and plain numeric strings parse to floats."""
        assert pgd._number("2.32") == 2.32
        assert pgd._number("17,551,127,411") == 17551127411.0

    def test_non_numeric_tokens_map_to_none(self):
        """Marker and missing tokens map to ``None`` rather than raising."""
        for token in ("##", "--", "NA", "N/A", "", _NBSP):
            assert pgd._number(token) is None


class TestSetPageNarrative:
    """Tests for ``_set_page_narrative``."""

    def test_leading_header_gets_page_description(self):
        """The leading header row's narrative becomes the section page description."""
        rows = [
            {
                "label": "Earnings and Profitability",
                "is_header": True,
                "narrative": None,
            },
            {"label": ">  Interest Income (TE)", "is_header": False, "1ST": 2.32},
        ]
        pgd._set_page_narrative(rows, "Summary Ratios")
        assert rows[0]["narrative"] == pgd.UBPR_PAGE_DESCRIPTIONS["Summary Ratios"]
        assert "narrative" not in rows[1] or rows[1].get("narrative") is None

    def test_unknown_section_leaves_none(self):
        """An unmapped section leaves the header narrative null."""
        rows = [{"label": "Header", "is_header": True, "narrative": None}]
        pgd._set_page_narrative(rows, "Not A Real Section")
        assert rows[0]["narrative"] is None

    def test_valued_first_row_untouched(self):
        """A leading row carrying period values is not treated as the page header."""
        rows = [{"label": ">  Line", "is_header": False, "1ST": 2.32, "narrative": "x"}]
        pgd._set_page_narrative(rows, "Summary Ratios")
        assert rows[0]["narrative"] == "x"

    def test_empty_rows_no_error(self):
        """An empty row list is handled without error."""
        pgd._set_page_narrative([], "Summary Ratios")


class TestConceptMap:
    """Tests for ``_concept_map``."""

    def test_maps_first_caption_to_code(self, monkeypatch):
        """Each non-marker caption maps to its concept code; first occurrence wins."""
        payload = [
            {"linecaption": "#SectionTitle#Earnings", "03_31_2026": "x;UBPRZ999"},
            {"linecaption": "  Interest Income (TE)", "03_31_2026": "2.32;UBPRE001"},
            {"linecaption": "Tier 1 Capital Ratio", "03_31_2026": "9.0;UBPRD487"},
            {"linecaption": "Tier 1 Capital Ratio", "03_31_2026": "9.0;UBPRR032"},
            {"linecaption": "#BlankLine#", "03_31_2026": "x;FAKE"},
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._section_id",
            lambda section, report_type_id: ("PG-1", section),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: payload,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        mapping = pgd._concept_map("Summary Ratios", "151")
        assert mapping["Interest Income (TE)"] == "UBPRE001"
        assert mapping["Tier 1 Capital Ratio"] == "UBPRD487"
        assert "#BlankLine#" not in mapping


class TestField:
    """Tests for ``_field``."""

    def test_reads_hidden_field_value(self):
        """A matching hidden input id yields its value attribute."""
        html = '<input type="hidden" id="__VIEWSTATE" value="ABC123" />'
        assert pgd._field(html, "__VIEWSTATE") == "ABC123"

    def test_missing_field_returns_empty(self):
        """An absent field id yields an empty string."""
        assert pgd._field("<html></html>", "__EVENTVALIDATION") == ""


class TestToc:
    """Tests for ``_toc``."""

    def test_parses_postback_targets_and_titles(self):
        """Each ``__doPostBack`` anchor yields its target and trimmed title."""
        html = (
            '<a href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl00$lbItem&#39;,'
            '&#39;&#39;)">Summary Ratios</a>'
            '<a href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl01$lbItem&#39;,'
            '&#39;&#39;)">Capital Analysis-a</a>'
        )
        toc = pgd._toc(html)
        assert toc == [
            ("rptTOC$rptTOC$ctl00$lbItem", "Summary Ratios"),
            ("rptTOC$rptTOC$ctl01$lbItem", "Capital Analysis-a"),
        ]

    def test_no_postback_anchors_returns_empty(self):
        """A shell with no table-of-contents anchors yields no entries."""
        assert pgd._toc("<html>no toc</html>") == []


class _FakeResponse:
    """A stand-in HTTP response exposing only a ``text`` body."""

    def __init__(self, text):
        """Store the response body."""
        self.text = text


class _FakeSession:
    """A stand-in session returning canned shell and rendered bodies."""

    def __init__(self, shell, rendered):
        """Store the shell and rendered bodies and capture posted forms."""
        self._shell = shell
        self._rendered = rendered
        self.posted: dict = {}

    def get(self, url, headers=None, timeout=None):
        """Return the report shell body."""
        return _FakeResponse(self._shell)

    def post(self, url, data=None, headers=None, timeout=None):
        """Capture the postback form and return the rendered body."""
        self.posted = data or {}
        return _FakeResponse(self._rendered)


class TestFetchDistribution:
    """Tests for ``fetch_distribution``."""

    _CYCLES = [
        {"reportingcycleid": "151", "enddateformatted": "03/31/2026"},
        {"reportingcycleid": "150", "enddateformatted": "12/31/2025"},
        {"reportingcycleid": "149", "enddateformatted": "09/30/2025"},
    ]

    _SHELL = (
        '<input type="hidden" id="__VIEWSTATE" value="VS" />'
        '<input type="hidden" id="__VIEWSTATEGENERATOR" value="VG" />'
        '<input type="hidden" id="__EVENTVALIDATION" value="EV" />'
        '<a href="javascript:__doPostBack(&#39;rptTOC$rptTOC$ctl00$lbItem&#39;,'
        '&#39;&#39;)">Summary Ratios</a>'
    )

    _RENDERED = (
        '<table id="tableReportData">'
        "<tr><td>Line Item</td>"
        + "".join(f"<td>{name}</td>" for name in pgd.PERCENTILE_COLUMNS)
        + "</tr>"
        "<tr><td>Percent of Average Assets:</td>"
        + "".join("<td></td>" for _ in pgd.PERCENTILE_COLUMNS)
        + "</tr>"
        "<tr><td>&nbsp;&nbsp;Interest Income (TE)</td>"
        + "".join("<td>2.32</td>" for _ in pgd.PERCENTILE_COLUMNS)
        + "</tr>"
        "</table>"
    )

    def _patch_seams(self, monkeypatch, session):
        """Patch every network, cache, and helper seam to offline fixtures."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session", lambda: session
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: list(self._CYCLES),
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.concepts.concept_index",
            lambda key: {},
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.rectangularize",
            lambda rows: rows,
        )
        monkeypatch.setattr(pgd, "_concept_map", lambda title, cycle_ids: {})
        monkeypatch.setattr(pgd, "_enrich", lambda rows, codes, index: rows)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.peer_groups.resolve_peer_group_id",
            lambda name, cycle_id=None: 4,
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )

    def test_rejects_unknown_peer_group(self):
        """An unknown peer-group key raises ``ValueError``."""
        with pytest.raises(ValueError, match="Unknown peer group"):
            pgd.fetch_distribution("999")

    def test_empty_cycles_raises(self, monkeypatch):
        """An empty reporting-cycle list raises ``ValueError``."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [],
        )
        with pytest.raises(ValueError, match="reporting-cycle list"):
            pgd.fetch_distribution("1")

    def test_renders_default_latest_cycle(self, monkeypatch):
        """The default request renders the latest cycle and parses the grid."""
        session = _FakeSession(self._SHELL, self._RENDERED)
        self._patch_seams(monkeypatch, session)
        result = pgd.fetch_distribution("1")
        assert result["peer_group"] == "1"
        assert result["section"] == "Summary Ratios"
        assert result["period"] == "2026-03-31"
        assert result["rows"][0]["label"] == "Percent of Average Assets:"
        assert session.posted["__VIEWSTATE"] == "VS"
        assert session.posted["__EVENTTARGET"] == "rptTOC$rptTOC$ctl00$lbItem"

    def test_selects_requested_cycle_id(self, monkeypatch):
        """A matching ``cycle_id`` renders that period."""
        session = _FakeSession(self._SHELL, self._RENDERED)
        self._patch_seams(monkeypatch, session)
        result = pgd.fetch_distribution("1", cycle_id="150")
        assert result["period"] == "2025-12-31"

    def test_unknown_section_raises(self, monkeypatch):
        """A section absent from the table-of-contents raises ``ValueError``."""
        session = _FakeSession(self._SHELL, self._RENDERED)
        self._patch_seams(monkeypatch, session)
        with pytest.raises(ValueError, match="Unknown report section"):
            pgd.fetch_distribution("1", section="Not A Page")
