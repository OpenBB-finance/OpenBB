"""Tests for the BHCPR User's Guide definition parser."""

from openbb_federal_reserve.utils import bhcpr_guide as guide


def _word(text, x0, top, font, size=10.0):
    """Build a fake pdfplumber word with the given font and position."""
    return {
        "text": text,
        "x0": x0,
        "top": top,
        "fontname": f"ABCDEF+{font}",
        "size": size,
    }


def _line(texts, top, font, size=10.0, x0=36.0):
    """Build a row of fake words at one vertical position in the left column."""
    words = []
    x = x0
    for text in texts:
        words.append(_word(text, x, top, font, size))
        x += 10 * len(text) + 4
    return words


class _FakePage:
    """A minimal stand-in for a pdfplumber page."""

    def __init__(self, text, words, width=612.0):
        self._text = text
        self._words = words
        self.width = width

    def extract_text(self):
        """Return the page's running-header text (gates Section 3 detection)."""
        return self._text

    def extract_words(self, extra_attrs=None):
        """Return the page's fake words."""
        return list(self._words)


_BOLD = "TimesNRMTPro-Bold"
_ITALIC = "TimesNRMTPro-Italic"
_ROMAN = "TimesNRMTPro"


def _summary_page():
    """A Section 3 page with a section title, two items, and their definitions."""
    words = [
        *_line(["Summary", "Ratios"], 50, _BOLD, 13.0),
        *_line(["Overhead", "Expense"], 100, _ITALIC),
        *_line(["(Percent", "of", "Average", "Assets)"], 114, _ITALIC),
        *_line(["The", "sum", "of", "premises"], 128, _ROMAN),
        *_line(["and", "fixed", "assets."], 142, _ROMAN),
        *_line(["Net", "Income"], 170, _ITALIC),
        *_line(["The", "amount", "of", "net", "income."], 184, _ROMAN),
    ]
    return _FakePage("Section 3: Definition of Items | 11", words)


class TestNorm:
    """Tests for ``_norm``."""

    def test_strips_punctuation_and_lowercases(self):
        """Only alphanumerics survive, collapsed and lowercased."""
        assert guide._norm("+ Non-Interest Income ($000)") == "non interest income 000"

    def test_empty_is_empty(self):
        """A blank or ``None`` input normalizes to an empty string."""
        assert guide._norm("") == ""
        assert guide._norm(None) == ""


class TestDehyphenate:
    """Tests for ``_dehyphenate``."""

    def test_joins_line_break_hyphen(self):
        """A word split by a line-break hyphen is rejoined."""
        assert guide._dehyphenate("prem- ises and fixed") == "premises and fixed"

    def test_keeps_real_hyphen(self):
        """A hyphen not followed by a space is preserved."""
        assert guide._dehyphenate("held-to-maturity") == "held-to-maturity"


class TestClassify:
    """Tests for ``_classify`` line typing."""

    def test_section_is_large_bold(self):
        """A 13pt bold line is the section title."""
        assert guide._classify(_line(["Summary", "Ratios"], 0, _BOLD, 13.0))[0] == (
            "section"
        )

    def test_subheader_is_small_bold(self):
        """A 10pt bold line is a sub-category header."""
        assert guide._classify(_line(["Capitalization"], 0, _BOLD, 10.0))[0] == (
            "subheader"
        )

    def test_item_is_italic_without_paren(self):
        """An italic line not opening with ``(`` is an item heading."""
        assert guide._classify(_line(["Overhead", "Expense"], 0, _ITALIC))[0] == "item"

    def test_basis_is_italic_with_paren(self):
        """An italic line opening with ``(`` is the ratio basis."""
        kind, _ = guide._classify(_line(["(Percent", "of", "Assets)"], 0, _ITALIC))
        assert kind == "basis"

    def test_body_is_roman(self):
        """A regular-font line is definition body text."""
        assert guide._classify(_line(["The", "sum", "of"], 0, _ROMAN))[0] == "body"

    def test_numeric_row_is_skipped(self):
        """A sample-report numeric row is skipped."""
        assert guide._classify(_line(["12.34", "56.78", "90.12"], 0, _ROMAN))[0] == (
            "skip"
        )

    def test_single_char_row_is_skipped(self):
        """A rotated running-header row of single characters is skipped."""
        assert guide._classify(_line(["S", "t", "a", "t", "e"], 0, _ROMAN))[0] == "skip"


class TestParsePages:
    """Tests for ``_parse_pages``."""

    def test_extracts_item_definitions(self):
        """Each italic item heading maps to its following definition text."""
        result = guide._parse_pages([_summary_page()])
        assert result["summary ratios\x1eoverhead expense"] == (
            "The sum of premises and fixed assets."
        )
        assert result["summary ratios\x1enet income"] == "The amount of net income."

    def test_pages_before_section_three_are_skipped(self):
        """Front-matter pages without the Section 3 header contribute nothing."""
        front = _FakePage("Contents", _line(["Introduction"], 100, _ITALIC))
        assert guide._parse_pages([front]) == {}

    def test_verso_pages_read_after_section_starts(self):
        """Once Section 3 begins, a verso page without the header is still read."""
        verso = _FakePage(
            "A User's Guide | 12",
            [
                *_line(["Net", "Income"], 100, _ITALIC),
                *_line(["The", "amount", "of", "net", "income."], 114, _ROMAN),
            ],
        )
        result = guide._parse_pages([_summary_page(), verso])
        # the verso's item, read under the latched section, is captured
        assert "summary ratios\x1enet income" in result

    def test_multiline_section_title_is_joined(self):
        """A section title wrapped across two bold lines is joined."""
        page = _FakePage(
            "Section 3",
            [
                *_line(["Loan", "Mix", "and", "Analysis", "of"], 50, _BOLD, 13.0),
                *_line(["Concentrations", "of", "Credit"], 66, _BOLD, 13.0),
                *_line(["Agricultural", "Loans"], 100, _ITALIC),
                *_line(["Farm", "loans", "divided", "by", "assets."], 114, _ROMAN),
            ],
        )
        result = guide._parse_pages([page])
        assert (
            "loan mix and analysis of concentrations of credit\x1eagricultural loans"
        ) in result

    def test_multiline_item_name_is_joined(self):
        """An item heading wrapped across two italic lines is joined."""
        page = _FakePage(
            "Section 3",
            [
                *_line(["Assets"], 50, _BOLD, 13.0),
                *_line(["Total", "Held-to-Maturity"], 100, _ITALIC),
                *_line(["Securities"], 114, _ITALIC),
                *_line(["Amortized", "cost", "of", "HTM."], 128, _ROMAN),
            ],
        )
        result = guide._parse_pages([page])
        assert "assets\x1etotal held to maturity securities" in result

    def test_skip_and_header_lines_ignored(self):
        """Numeric sample rows and the running-header line are dropped in parse."""
        page = _FakePage(
            "Section 3",
            [
                *_line(["Section", "3:", "Definition"], 46, _ROMAN),
                *_line(["Summary", "Ratios"], 60, _BOLD, 13.0),
                *_line(["12.34", "56.78"], 90, _ROMAN),
                *_line(["Net", "Income"], 110, _ITALIC),
                *_line(["The", "amount."], 124, _ROMAN),
            ],
        )
        assert guide._parse_pages([page]) == {
            "summary ratios\x1enet income": "The amount."
        }

    def test_subheader_breaks_the_current_item(self):
        """A sub-category header flushes the current item and holds no body."""
        page = _FakePage(
            "Section 3",
            [
                *_line(["Assets"], 50, _BOLD, 13.0),
                *_line(["Total", "Loans"], 100, _ITALIC),
                *_line(["Gross", "loans", "and", "leases."], 114, _ROMAN),
                *_line(["Capitalization"], 140, _BOLD, 10.0),
                *_line(["orphan", "body", "text"], 154, _ROMAN),
            ],
        )
        result = guide._parse_pages([page])
        assert result["assets\x1etotal loans"] == "Gross loans and leases."
        # body after a sub-header with no active item is dropped
        assert not any("orphan" in v for v in result.values())


class TestBhcprNarrative:
    """Tests for ``bhcpr_narrative`` resolution."""

    _DEFS = {
        "summary ratios\x1enet income": "Net income for the summary page.",
        "assets\x1etotal loans": "Gross loans and leases.",
        "parent company\x1enet income": "Parent-only net income.",
    }

    def test_blank_label_returns_none(self):
        """A blank label resolves to ``None`` without a lookup."""
        assert guide.bhcpr_narrative(self._DEFS, "Summary Ratios", "") is None

    def test_section_scoped_match(self):
        """A same-section label match is preferred and returned."""
        assert guide.bhcpr_narrative(self._DEFS, "Assets", "Total loans") == (
            "Gross loans and leases."
        )

    def test_unique_cross_section_fallback(self):
        """A label unique to one section resolves even if the section differs."""
        assert guide.bhcpr_narrative(self._DEFS, "Nowhere", "Total loans") == (
            "Gross loans and leases."
        )

    def test_ambiguous_label_returns_none(self):
        """A label found in multiple sections, out of section, stays unresolved."""
        assert guide.bhcpr_narrative(self._DEFS, "Nowhere", "Net income") is None

    def test_unknown_label_returns_none(self):
        """A label with no definition resolves to ``None``."""
        assert guide.bhcpr_narrative(self._DEFS, "Assets", "Made up item") is None


class TestFetch:
    """Tests for the cached fetch and its download."""

    def test_fetch_guide_reads_content(self, monkeypatch):
        """``_fetch_guide`` returns the downloaded PDF bytes."""

        class _Resp:
            """A stand-in HTTP response carrying the PDF bytes."""

            content = b"%PDF-1.7"

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _Resp(),
        )
        assert guide._fetch_guide() == b"%PDF-1.7"

    def test_fetch_definitions_parses_pdf(self, monkeypatch):
        """``fetch_bhcpr_definitions`` opens the PDF and parses its pages."""
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.cache.cached",
            lambda key, ttl, producer: producer(),
        )
        monkeypatch.setattr(guide, "_fetch_guide", lambda: b"%PDF")

        class _PDF:
            """A context-manager PDF exposing one fake definitions page."""

            pages = [_summary_page()]

            def __enter__(self):
                """Enter the context."""
                return self

            def __exit__(self, *args):
                """Exit the context."""
                return False

        monkeypatch.setattr("pdfplumber.open", lambda *a, **k: _PDF())
        defs = guide.fetch_bhcpr_definitions()
        assert defs["summary ratios\x1enet income"] == "The amount of net income."
