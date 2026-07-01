"""Tests for the FFIEC UBPR Interactive User's Guide concept client."""

from openbb_federal_reserve.utils import guide


class TestField:
    """Tests for ``_field`` labelled-field extraction."""

    def test_extracts_and_collapses_whitespace(self):
        """A labelled field's inner text is stripped of tags and whitespace."""
        segment = (
            "<b>Description</b></div><div class='v'>Pretax <b>Net</b>\n"
            "   Operating  Income</div>"
        )
        assert guide._field(segment, "Description") == "Pretax Net Operating Income"

    def test_inline_tag_split_does_not_insert_space(self):
        """An inline tag splitting a word joins the halves with no added space."""
        segment = "<b>Description</b></div><div>Non-<b></b>accrual</div>"
        assert guide._field(segment, "Description") == "Non-accrual"

    def test_nested_div_is_captured_whole(self):
        """A field whose content holds a nested ``<div>`` is not truncated."""
        segment = (
            "<b>Narrative</b></div><div class='c'>Alpha "
            "<div>beta</div> gamma</div><b>Next</b>"
        )
        assert guide._field(segment, "Narrative") == "Alpha beta gamma"

    def test_block_break_inserts_space_between_words(self):
        """A block-level break between words yields a space, never a fused word."""
        segment = (
            "<b>Narrative</b></div><div class='c'>fair value<br>as<p>a</p>percent</div>"
        )
        assert guide._field(segment, "Narrative") == "fair value as a percent"

    def test_decodes_html_entities(self):
        """HTML entities in the field content are decoded."""
        segment = (
            "<b>Description</b></div><div>Loans &amp; Leases &#37; of&nbsp;Assets</div>"
        )
        assert guide._field(segment, "Description") == "Loans & Leases % of Assets"

    def test_missing_content_div_returns_empty(self):
        """A header not followed by a content ``<div>`` yields an empty string."""
        assert guide._field("<b>Narrative</b></div>plain text", "Narrative") == ""

    def test_unbalanced_div_captures_to_end(self):
        """An unterminated content div captures through the end of the segment."""
        segment = "<b>Narrative</b></div><div>Trailing text with no close"
        assert guide._field(segment, "Narrative") == "Trailing text with no close"

    def test_missing_label_returns_empty(self):
        """A label absent from the segment yields an empty string."""
        assert guide._field("<div>nothing here</div>", "Narrative") == ""


class TestParseGuide:
    """Tests for ``_parse_guide`` concept-block parsing."""

    def test_parses_description_and_narrative(self):
        """A concept block yields its description and narrative fields."""
        html = (
            "<b>Concept</b>"
            "<div id=\"contentUBPR1234-label\" class='x'> UBPR1234 <"
            "<b>Description</b></div><div>Pretax Net Operating Income</div>"
            "<b>Narrative</b></div><div>The definition text.</div>"
        )
        result = guide._parse_guide(html)
        assert result["UBPR1234"]["description"] == "Pretax Net Operating Income"
        assert result["UBPR1234"]["narrative"] == "The definition text."

    def test_skips_block_without_label_and_dedupes(self):
        """A block lacking a concept label is skipped; duplicates are not overwritten."""
        html = (
            "<b>Concept</b><div>no label marker</div>"
            "<b>Concept</b>"
            '<div id="contentUBPR1234-label"> UBPR1234 <'
            "<b>Description</b></div><div>First</div>"
            "<b>Concept</b>"
            '<div id="contentUBPR1234-label"> UBPR1234 <'
            "<b>Description</b></div><div>Second</div>"
        )
        result = guide._parse_guide(html)
        assert list(result) == ["UBPR1234"]
        assert result["UBPR1234"]["description"] == "First"


class TestReportDate:
    """Tests for ``_report_date`` newest-cycle resolution."""

    def test_returns_latest_end_date(self, monkeypatch):
        """The newest cycle's formatted end date is returned."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"enddateformatted": "03/31/2026"}],
        )
        assert guide._report_date() == "03/31/2026"

    def test_returns_empty_without_cycles(self, monkeypatch):
        """No reporting cycles yields an empty date string."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [],
        )
        assert guide._report_date() == ""


class TestUbprConceptLines:
    """Tests for ``ubpr_concept_lines`` section walking."""

    def _patch_cache(self, monkeypatch):
        """Run the cached producer body directly against fixtures."""
        from openbb_federal_reserve.utils import cache

        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())

    def test_returns_empty_without_cycles(self, monkeypatch):
        """No reporting cycles short-circuits to an empty mapping."""
        self._patch_cache(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [],
        )
        assert guide.ubpr_concept_lines() == {}

    def test_maps_concepts_to_line_ids(self, monkeypatch):
        """Each line's first period cell yields the concept-to-line mapping."""
        self._patch_cache(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": 999}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: [{"pageid": "P1"}],
        )
        rows = [
            {
                "lineid": "868900",
                "03_31_2026": "13105;UBPR1234, more",
                "12_31_2025": "999;UBPRZZZZ",
            },
            {"lineid": None, "03_31_2026": "1;UBPRSKIP"},
            {"lineid": "868901", "notaperiod": "x;UBPRBAD", "03_31_2026": ""},
            {"lineid": "868902", "03_31_2026": "noseparator"},
            {"lineid": "868903", "03_31_2026": "1;"},
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: list(rows),
        )
        mapping = guide.ubpr_concept_lines()
        assert mapping == {"UBPR1234": "868900"}

    def test_non_list_rows_yield_empty(self, monkeypatch):
        """A non-list ``_post`` response contributes no mappings."""
        self._patch_cache(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_cycles",
            lambda: [{"reportingcycleid": 1}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report.report_sections",
            lambda report_type_id: [{"pageid": "P1"}],
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ubpr_report._post",
            lambda requestor_id, criteria: {"unexpected": "dict"},
        )
        assert guide.ubpr_concept_lines() == {}


class _Resp:
    """Minimal HTTP response stub carrying ``text``."""

    def __init__(self, text):
        self.text = text


class _Session:
    """Minimal session stub returning a fixed response from ``get``."""

    def __init__(self, text):
        self._text = text

    def get(self, url, timeout=None):
        """Return the stubbed response regardless of URL."""
        return _Resp(self._text)


class TestConceptGuide:
    """Tests for ``_concept_guide`` per-line guide fetching."""

    def _patch_cache(self, monkeypatch):
        """Run the cached producer body directly against fixtures."""
        from openbb_federal_reserve.utils import cache

        monkeypatch.setattr(cache, "cached", lambda _key, _ttl, producer: producer())

    def test_parses_matching_concept(self, monkeypatch):
        """A guide page containing the concept returns its parsed fields."""
        self._patch_cache(monkeypatch)
        html = (
            "<b>Concept</b>"
            '<div id="contentUBPR1234-label"> UBPR1234 <'
            "<b>Description</b></div><div>Desc</div>"
            "<b>Narrative</b></div><div>Narr</div>"
        )
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session(html),
        )
        result = guide._concept_guide("UBPR1234", "868900", "03/31/2026")
        assert result == {"description": "Desc", "narrative": "Narr"}

    def test_missing_concept_returns_blank(self, monkeypatch):
        """A guide page without the concept returns empty fields."""
        self._patch_cache(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cdr._get_session",
            lambda: _Session("<html>nothing</html>"),
        )
        result = guide._concept_guide("UBPR1234", "868900", "03/31/2026")
        assert result == {"description": "", "narrative": ""}


class TestFetchGuideConcepts:
    """Tests for ``fetch_guide_concepts`` orchestration."""

    def test_resolves_via_provided_lines(self, monkeypatch):
        """Concepts present in the provided line map are fetched and returned."""
        monkeypatch.setattr(guide, "_report_date", lambda: "03/31/2026")
        monkeypatch.setattr(
            guide,
            "_concept_guide",
            lambda concept, line_id, report_date: {
                "description": f"D-{concept}",
                "narrative": f"N-{concept}",
            },
        )
        result = guide.fetch_guide_concepts(
            ["UBPR1234", "UBPRMISS"], lines={"UBPR1234": "868900"}
        )
        assert result == {
            "UBPR1234": {"description": "D-UBPR1234", "narrative": "N-UBPR1234"}
        }

    def test_falls_back_to_concept_lines(self, monkeypatch):
        """Without a provided map, the cached concept-line map is used."""
        monkeypatch.setattr(guide, "ubpr_concept_lines", lambda: {"UBPR1234": "868900"})
        monkeypatch.setattr(guide, "_report_date", lambda: "03/31/2026")
        monkeypatch.setattr(
            guide,
            "_concept_guide",
            lambda concept, line_id, report_date: {
                "description": "D",
                "narrative": "N",
            },
        )
        result = guide.fetch_guide_concepts(["UBPR1234"])
        assert result == {"UBPR1234": {"description": "D", "narrative": "N"}}

    def test_no_pairs_returns_empty(self, monkeypatch):
        """No resolvable concepts yields an empty result."""
        monkeypatch.setattr(guide, "_report_date", lambda: "03/31/2026")
        assert guide.fetch_guide_concepts(["UNKNOWN"], lines={}) == {}

    def test_no_report_date_returns_empty(self, monkeypatch):
        """A missing report date yields an empty result."""
        monkeypatch.setattr(guide, "_report_date", lambda: "")
        assert (
            guide.fetch_guide_concepts(["UBPR1234"], lines={"UBPR1234": "868900"}) == {}
        )

    def test_drops_concepts_with_empty_data(self, monkeypatch):
        """A concept whose fetched data is falsy is dropped from the result."""
        monkeypatch.setattr(guide, "_report_date", lambda: "03/31/2026")
        monkeypatch.setattr(
            guide,
            "_concept_guide",
            lambda concept, line_id, report_date: {},
        )
        result = guide.fetch_guide_concepts(["UBPR1234"], lines={"UBPR1234": "868900"})
        assert result == {}


class TestFetchGuideNarratives:
    """Tests for ``fetch_guide_narratives`` narrative extraction."""

    def test_returns_only_nonempty_narratives(self, monkeypatch):
        """Concepts with a narrative are kept; blank narratives are dropped."""
        monkeypatch.setattr(
            guide,
            "fetch_guide_concepts",
            lambda concepts, lines=None: {
                "UBPR1234": {"description": "D", "narrative": "N"},
                "UBPR5678": {"description": "D2", "narrative": ""},
            },
        )
        assert guide.fetch_guide_narratives(["UBPR1234", "UBPR5678"]) == {
            "UBPR1234": "N"
        }
