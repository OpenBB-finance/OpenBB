"""Tests for the BHCPR guide schema helpers and committed schema asset."""

from openbb_federal_reserve.utils import bhcpr_schema
from openbb_federal_reserve.utils.bhcpr_schema import (
    _dehyphenate,
    _item_basis,
    load_schema,
    parse_guide_schema,
    section_titles,
)


class TestDehyphenate:
    """Tests for ``_dehyphenate``."""

    def test_joins_line_break_hyphen(self):
        """A word split by a line-break hyphen is rejoined."""
        assert _dehyphenate("prem- ises and other") == "premises and other"

    def test_leaves_intact_text(self):
        """Text without a split hyphen is returned unchanged (trimmed)."""
        assert _dehyphenate("  hello world  ") == "hello world"


class TestItemBasis:
    """Tests for ``_item_basis`` basis inference from the guide label."""

    def test_guide_basis_wins(self):
        """An explicit guide basis is returned verbatim."""
        assert _item_basis("Anything", "Percent of Average Assets") == (
            "Percent of Average Assets"
        )

    def test_thousands_marker(self):
        """A ``($000)`` marker yields the dollar basis."""
        assert _item_basis("Average Assets ($000)", None) == (
            "Dollar Amount in Thousands"
        )

    def test_multiple_marker(self):
        """A trailing ``(X)`` marker yields the multiple basis."""
        assert _item_basis("Double Leverage (X)", None) == "Multiple (X)"

    def test_number_label(self):
        """A count label yields the number basis."""
        assert _item_basis("Number of BHCs in Peer Group", None) == "Number"

    def test_ratio_denominator(self):
        """A ``numerator / denominator`` label yields the denominator basis."""
        assert _item_basis("Net Income / Average Assets", None) == "Average Assets"

    def test_plain_label_has_no_basis(self):
        """A plain label with no marker yields no basis."""
        assert _item_basis("Operating Income", None) is None


class TestLoadSchema:
    """Tests for the committed schema asset."""

    def test_returns_ordered_sections_with_bound_items(self):
        """The schema asset is a non-empty ordered list of sections with items."""
        schema = load_schema()
        assert isinstance(schema, list) and schema
        assert schema[0]["section"] == "Summary Ratios"
        items = [
            item
            for section in schema
            for item in section["entries"]
            if item["kind"] == "item"
        ]
        assert items
        assert any(item.get("code") for item in items)

    def test_bound_items_carry_a_basis(self):
        """Every code-bound item carries a non-null basis."""
        schema = load_schema()
        bound = [
            item
            for section in schema
            for item in section["entries"]
            if item["kind"] == "item" and item.get("code")
        ]
        assert bound
        assert all(item.get("basis") for item in bound)


class TestSectionTitles:
    """Tests for ``section_titles``."""

    def test_titles_match_schema_order(self):
        """The titles are the schema's section names in order."""
        titles = section_titles()
        schema = load_schema()
        assert titles == [section["section"] for section in schema]
        assert titles[0] == "Summary Ratios"


def _gline(text, font, size):
    """Build a pdfplumber-style text line with uniform char font and size."""
    return {
        "text": text,
        "chars": [{"text": ch, "fontname": font, "size": size} for ch in text],
    }


class _GuidePage:
    """A stand-in pdfplumber page returning fixed text and text-lines."""

    def __init__(self, text, lines=()):
        """Store the page's extracted text and pre-built text lines."""
        self._text = text
        self._lines = list(lines)

    def extract_text(self):
        """Return the page's extracted text."""
        return self._text

    def extract_text_lines(self, layout=False, strip=True):
        """Return the page's pre-built text lines."""
        return self._lines


class _GuidePdf:
    """A stand-in pdfplumber document yielding the guide pages."""

    def __init__(self, pages):
        """Store the document's pages."""
        self.pages = pages

    def __enter__(self):
        """Enter the document context."""
        return self

    def __exit__(self, *exc):
        """Exit the document context."""
        return False


_MD = "AAAAAA-Md"
_IT = "AAAAAA-It"
_RG = "AAAAAA-Rg"


class TestParseGuideSchema:
    """Tests for ``parse_guide_schema`` over fake guide pages."""

    def _parse(self, monkeypatch):
        """Parse a two-page fake guide exercising every branch."""
        page_lines = [
            _gline("Section 3: running header", _RG, 9),
            _gline("   ", _RG, 9),
            _gline("Allowance and Net Credit Losses on Loans and Lease", _MD, 12),
            _gline("Earnings and Profitability", _MD, 10.8),
            _gline("Sub Detail", _MD, 9.5),
            _gline("Net Interest Income", _IT, 9),
            _gline("(Tax Equivalent)", _IT, 9),
            _gline("NII divided by average assets.", _RG, 9),
            _gline("Average Assets", _IT, 9),
            _gline("(Percent of", _IT, 9),
            _gline("Average Assets)", _IT, 9),
            _gline("Return on", _IT, 9),
            _gline("Assets", _IT, 9),
            _gline("Net income over assets.", _RG, 9),
            _gline("Empty Section", _MD, 12),
            _gline("Allowance and Net Credit Losses on Loans and Lease", _MD, 12),
            _gline("Extra Item", _IT, 9),
            _gline("Extra definition.", _RG, 9),
        ]
        pages = [
            _GuidePage("A cover page with no section marker", []),
            _GuidePage("... Sample BHCPR and Definition of Items ...", page_lines),
        ]
        import pdfplumber

        monkeypatch.setattr(pdfplumber, "open", lambda _: _GuidePdf(pages))
        return parse_guide_schema(b"%PDF-1.7")

    def test_single_section_kept_and_title_fixed(self, monkeypatch):
        """Only sections with items survive, and the title fix is applied."""
        schema = self._parse(monkeypatch)
        assert [s["section"] for s in schema] == [
            "Allowance and Net Credit Losses on Loans and Leases"
        ]

    def test_items_labels_in_order(self, monkeypatch):
        """Italic name lines become items in report order, appended names joined."""
        schema = self._parse(monkeypatch)
        items = [e["label"] for e in schema[0]["entries"] if e["kind"] == "item"]
        assert items == [
            "Net Interest Income",
            "Average Assets",
            "Return on Assets",
            "Extra Item",
        ]

    def test_subheaders_carry_nesting_level(self, monkeypatch):
        """A parent sub-header nests at level 0 and its child at level 1."""
        schema = self._parse(monkeypatch)
        subs = {
            e["label"]: e["level"]
            for e in schema[0]["entries"]
            if e["kind"] == "subheader"
        }
        assert subs == {"Earnings and Profitability": 0, "Sub Detail": 1}

    def test_basis_and_definition_captured(self, monkeypatch):
        """An italic ``(...)`` basis and a body definition attach to the item."""
        schema = self._parse(monkeypatch)
        items = {e["label"]: e for e in schema[0]["entries"] if e["kind"] == "item"}
        assert items["Net Interest Income"]["basis"] == "Tax Equivalent"
        assert items["Net Interest Income"]["definition"] == (
            "NII divided by average assets."
        )
        assert items["Average Assets"]["basis"] == "Percent of Average Assets"

    def test_page_without_marker_is_skipped(self, monkeypatch):
        """Content before the definitions marker contributes nothing."""
        schema = self._parse(monkeypatch)
        assert all(
            s["section"] != "A cover page with no section marker" for s in schema
        )


def test_module_urls_present():
    """The guide and schema-asset URLs are module constants."""
    assert bhcpr_schema.GUIDE_URL.endswith(".pdf")
