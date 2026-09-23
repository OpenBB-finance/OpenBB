"""Tests for the offline FR BHCPR report PDF parser and matching helpers."""

import pytest

from openbb_federal_reserve.utils import bhcpr


class TestIso:
    """Tests for ``_iso`` date conversion."""

    def test_us_date_to_iso(self):
        """A ``MM/DD/YYYY`` date converts to ISO."""
        assert bhcpr._iso("03/31/2026") == "2026-03-31"


class TestToNumber:
    """Tests for ``_to_number`` figure coercion."""

    def test_scales_thousands_to_full_dollars(self):
        """A figure scales to full dollars and returns an int."""
        assert bhcpr._to_number("4,759,098,000", scale=1000) == 4759098000000

    def test_unscaled_fractional_kept(self):
        """An unscaled fractional figure is returned as a float."""
        assert bhcpr._to_number("2.15", scale=1) == 2.15

    def test_negative_kept(self):
        """A negative figure parses with its sign."""
        assert bhcpr._to_number("-5", scale=1) == -5

    def test_non_numeric_is_none(self):
        """A non-numeric token returns None."""
        assert bhcpr._to_number("n/a", scale=1) is None
        assert bhcpr._to_number("", scale=1) is None


class TestNormalize:
    """Tests for ``_normalize``."""

    def test_reduces_to_alnum_lowercase(self):
        """Punctuation drops and case/whitespace collapse."""
        assert (
            bhcpr._normalize("Net Income (Tax-Equivalent)!")
            == "net income tax equivalent"
        )


class TestTokenList:
    """Tests for ``_token_list`` synonym expansion."""

    def test_expands_report_abbreviations(self):
        """Report abbreviations expand to their full phrases."""
        assert bhcpr._token_list("OREO") == ["other", "real", "estate", "owned"]

    def test_joins_u_s(self):
        """The split ``U S`` collapses to ``us`` before expansion."""
        assert bhcpr._token_list("U S Treasury") == ["us", "treasury"]

    def test_drops_empty_synonym(self):
        """A synonym mapping to empty (``x``) drops the token."""
        assert bhcpr._token_list("5 x") == ["5"]

    def test_tokens_is_frozenset(self):
        """``_tokens`` returns the token set."""
        assert bhcpr._tokens("Credit Card") == frozenset({"credit", "card"})


class TestContained:
    """Tests for ``_contained`` containment."""

    def test_prefix_is_contained(self):
        """A caption that is a prefix of another is contained."""
        assert bhcpr._contained(["a", "b"], ["a", "b", "c", "d"]) is True

    def test_half_length_subset_is_contained(self):
        """A subset spanning at least half the words is contained."""
        assert bhcpr._contained(["b", "c"], ["a", "b", "c", "d"]) is True

    def test_short_sparse_subset_not_contained(self):
        """A one-word slice of a long caption is not containment."""
        assert bhcpr._contained(["b"], ["a", "b", "c", "d"]) is False

    def test_empty_or_disjoint_not_contained(self):
        """An empty or non-subset caption is not contained."""
        assert bhcpr._contained([], ["a"]) is False
        assert bhcpr._contained(["x"], ["a", "b"]) is False


class TestMatchIndex:
    """Tests for ``match_index`` guide-item to report-row matching."""

    _ROWS = [
        {"label": "Net Income"},
        {"label": "Total Assets"},
        {"label": "Return on Average Assets"},
    ]

    def test_exact_normalized_match(self):
        """An exact normalized caption returns its row."""
        assert bhcpr.match_index("net income!", self._ROWS, set()) == 0

    def test_exact_only_without_exact_returns_none(self):
        """With ``exact_only``, a non-exact caption yields no match."""
        assert bhcpr.match_index("income", self._ROWS, set(), exact_only=True) is None

    def test_used_index_skipped(self):
        """An already-used row is not matched again."""
        assert bhcpr.match_index("Net Income", self._ROWS, {0}) != 0

    def test_fuzzy_containment_match(self):
        """A caption contained in a row matches on the containment boost."""
        assert bhcpr.match_index("Average Assets", self._ROWS, set()) == 2

    def test_empty_query_returns_none(self):
        """A caption that normalizes to nothing yields no match."""
        assert bhcpr.match_index("!!!", self._ROWS, set()) is None

    def test_no_available_rows_returns_none(self):
        """When every row is used there is no match."""
        assert bhcpr.match_index("Net Income", self._ROWS, {0, 1, 2}) is None

    def test_weak_overlap_returns_none(self):
        """A caption sharing too little with any row yields no match."""
        rows = [{"label": "Deposits in Foreign Offices"}]
        assert bhcpr.match_index("Cash", rows, set()) is None

    def test_moderate_overlap_single_candidate_matches(self):
        """A 0.6 overlap with a lone candidate (no containment) still matches."""
        rows = [{"label": "alpha beta gamma epsilon"}]
        assert bhcpr.match_index("alpha beta gamma delta", rows, set()) == 0


class TestSectionTitle:
    """Tests for ``_section_title``."""

    def test_title_follows_column_band(self):
        """The section title is the line after the column-label band."""
        lines = ["BHC Name City/State RSSD Number", "Summary Ratios", "03/31/2026"]
        assert bhcpr._section_title(lines) == "Summary Ratios"

    def test_no_band_returns_none(self):
        """A page without the column band has no section title."""
        assert bhcpr._section_title(["Some text", "More text"]) is None


class TestWordsByLine:
    """Tests for ``_words_by_line`` baseline grouping."""

    def test_groups_by_baseline_sorted_left_to_right(self):
        """Words group into visual lines, each sorted left to right."""
        words = [
            {"text": "b", "x0": 30, "top": 100},
            {"text": "a", "x0": 10, "top": 100},
            {"text": "c", "x0": 5, "top": 110},
        ]
        lines = bhcpr._words_by_line(words)
        assert [[w["text"] for w in line] for line in lines] == [["a", "b"], ["c"]]


class _Table:
    """A stand-in pdfplumber table with a fixed bounding box and grid."""

    def __init__(self, bbox, grid):
        """Store the table's bounding box and extracted grid."""
        self.bbox = bbox
        self._grid = grid

    def extract(self):
        """Return the table's extracted cell grid."""
        return self._grid


class _Page:
    """A stand-in pdfplumber page returning fixed text, words, and tables."""

    def __init__(self, text="", words=None, tables=None):
        """Store the page's extracted text, words, and tables."""
        self._text = text
        self._words = words or []
        self._tables = tables or []

    def extract_text(self):
        """Return the page's extracted text."""
        return self._text

    def extract_words(self):
        """Return the page's extracted words."""
        return self._words

    def find_tables(self):
        """Return the page's tables."""
        return self._tables


class _Pdf:
    """A stand-in pdfplumber document yielding the fixture pages."""

    def __init__(self, pages):
        """Store the document's pages."""
        self.pages = pages

    def __enter__(self):
        """Enter the document context."""
        return self

    def __exit__(self, *exc):
        """Exit the document context."""
        return False


def _word(text, x0, x1, top):
    """Build a pdfplumber-style word box."""
    return {"text": text, "x0": x0, "x1": x1, "top": top}


_COVER = _Page(
    "\n".join(
        [
            "Board of Governors RSSD Number: 1039502 FR BHCPR",
            "JPMORGAN CHASE & CO.",
            "BHC Name Table of Contents",
            "City/State NEW YORK, NY Section Page Number",
        ]
    )
)


def _dollar_page():
    """A thousands-regime page: a scaled dollar row and an unscaled count row."""
    text = "\n".join(
        [
            "BHC Name City/State RSSD Number FR Dist. Peer #",
            "Income Statement",
        ]
    )
    tables = [
        _Table(
            (200, 100, 500, 170),
            [["Dollar Amount in Thousands 03/31/2026 03/31/2025 12/31/2025"]],
        )
    ]
    words = [
        _word("03/31/2026", 225, 275, 102),
        _word("03/31/2025", 325, 375, 102),
        _word("12/31/2025", 425, 475, 102),
        _word("Interest", 50, 90, 140),
        _word("fees.........", 100, 198, 140),
        _word("24,885,000", 220, 280, 140),
        _word("23,195,000", 320, 380, 140),
        _word("97,186,000", 420, 480, 140),
        _word("Number", 50, 90, 155),
        _word("BHCs.........", 100, 198, 155),
        _word("130", 240, 260, 155),
        _word("136", 340, 360, 155),
        _word("128", 440, 460, 155),
    ]
    return _Page(text, words, tables)


def _percent_page():
    """A percent-regime page: a BHC/Peer/Pct triplet row over three periods."""
    text = "\n".join(
        [
            "BHC Name City/State RSSD Number FR Dist. Peer #",
            "Summary Ratios",
        ]
    )
    tables = [
        _Table(
            (150, 100, 560, 160),
            [["BHC Peer # 1 Pct BHC Peer # 1 Pct BHC Peer # 1 Pct"]],
        )
    ]
    words = [
        _word("03/31/2026", 235, 285, 102),
        _word("03/31/2025", 365, 415, 102),
        _word("12/31/2025", 495, 545, 102),
        _word("Return", 20, 60, 140),
        _word("assets.........", 62, 145, 140),
        _word("1.10", 235, 250, 140),
        _word("1.05", 255, 270, 140),
        _word("62", 275, 290, 140),
        _word("1.08", 365, 380, 140),
        _word("1.02", 385, 400, 140),
        _word("58", 405, 420, 140),
        _word("1.15", 495, 510, 140),
        _word("1.09", 515, 530, 140),
        _word("60", 535, 550, 140),
    ]
    return _Page(text, words, tables)


def _paired_page():
    """A ``% of Total`` page: an amount/pct row with trailing percent changes."""
    text = "\n".join(
        [
            "BHC Name City/State RSSD Number FR Dist. Peer #",
            "Parent Company Balance Sheet",
        ]
    )
    tables = [
        _Table(
            (160, 100, 590, 170),
            [["% of Total 03/31/2026 Assets 03/31/2025 Assets 12/31/2025 Change"]],
        )
    ]
    words = [
        _word("5-Year", 545, 575, 90),
        _word("03/31/2026", 175, 225, 102),
        _word("03/31/2025", 275, 325, 102),
        _word("12/31/2025", 375, 425, 102),
        _word("1-Year", 490, 510, 102),
        _word("Investment", 20, 60, 140),
        _word("subs.........", 62, 158, 140),
        _word("336,992,000", 170, 230, 140),
        _word("46.63", 235, 260, 140),
        _word("316,915,000", 270, 330, 140),
        _word("46.53", 335, 360, 140),
        _word("336,203,000", 370, 430, 140),
        _word("47.35", 435, 460, 140),
        _word("6.34", 490, 510, 140),
        _word("21.44", 545, 575, 140),
        _word("03/2026", 100, 150, 400),
    ]
    return _Page(text, words, tables)


def _emptygrid_page():
    """A page whose only table extracts an empty grid, so it is skipped."""
    text = "\n".join(["BHC Name City/State RSSD Number FR Dist. Peer #", "Grid Gone"])
    return _Page(text, [], [_Table((200, 100, 500, 160), None)])


def _nodate_page():
    """A page whose only table has no dated header, so it is rejected."""
    text = "\n".join(["BHC Name City/State RSSD Number FR Dist. Peer #", "Bad Section"])
    tables = [_Table((200, 100, 500, 160), [["Dollar Amount in Thousands 03/31/2026"]])]
    words = [_word("03/31/2026", 225, 275, 102)]
    return _Page(text, words, tables)


def _status_page():
    """A page with a carried figure-less caption feeding two status rows."""
    text = "\n".join(["BHC Name City/State RSSD Number FR Dist. Peer #", "Past Due"])
    tables = [
        _Table(
            (200, 100, 500, 220),
            [["Dollar Amount in Thousands 03/31/2026 03/31/2025 12/31/2025"]],
        )
    ]
    words = [
        _word("03/31/2026", 225, 275, 102),
        _word("03/31/2025", 325, 375, 102),
        _word("12/31/2025", 425, 475, 102),
        _word("Loans", 50, 90, 130),
        _word("Commercial", 20, 70, 150),
        _word("30-89", 72, 100, 150),
        _word("days", 102, 120, 150),
        _word("past", 122, 140, 150),
        _word("due", 142, 160, 150),
        _word("100", 240, 260, 150),
        _word("110", 340, 360, 150),
        _word("120", 440, 460, 150),
        _word("Auto", 40, 70, 170),
        _word("90+", 72, 95, 170),
        _word("days", 97, 120, 170),
        _word("past", 122, 145, 170),
        _word("due", 147, 165, 170),
        _word("5", 245, 255, 170),
        _word("6", 345, 355, 170),
        _word("7", 445, 455, 170),
        _word("03/2026", 100, 150, 400),
    ]
    return _Page(text, words, tables)


@pytest.fixture
def _patch_pdfplumber(monkeypatch):
    """Patch ``pdfplumber.open`` to yield the supplied fixture pages."""

    def _apply(pages):
        """Install a fake document from the given pages."""
        import pdfplumber

        monkeypatch.setattr(pdfplumber, "open", lambda _: _Pdf(pages))

    return _apply


class TestParseBhcprPdf:
    """Tests for ``parse_bhcpr_pdf`` over fake pdfplumber pages."""

    def test_non_pdf_returns_empty(self):
        """A non-PDF response (a non-filer's HTML error page) yields no sections."""
        result = bhcpr.parse_bhcpr_pdf(b"<!DOCTYPE html><html>Not found</html>")
        assert result["sections"] == {}
        assert result["identity"]["rssd_id"] is None

    def test_identity_from_cover(self, _patch_pdfplumber):
        """The cover page yields the institution name, city/state, and RSSD."""
        _patch_pdfplumber([_COVER, _dollar_page()])
        parsed = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")
        assert parsed["identity"] == {
            "institution_name": "JPMORGAN CHASE & CO.",
            "city_state": "NEW YORK, NY",
            "rssd_id": "1039502",
        }

    def test_dollar_row_scaled_and_count_unscaled(self, _patch_pdfplumber):
        """A dollar row scales x1000; a ``Number of`` row is read as filed."""
        _patch_pdfplumber([_COVER, _dollar_page()])
        rows = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")["sections"]["Income Statement"]
        fees = next(r for r in rows if r["label"].startswith("Interest"))
        assert fees["regime"] == "thousands"
        assert fees["periods"]["2026-03-31"]["amount"] == 24885000000
        assert fees["periods"]["2025-12-31"]["amount"] == 97186000000
        count = next(r for r in rows if r["label"].startswith("Number"))
        assert count["periods"]["2026-03-31"]["amount"] == 130

    def test_percent_row_carries_bhc_peer_pct(self, _patch_pdfplumber):
        """A percent-regime row carries BHC, peer, and percentile per period."""
        _patch_pdfplumber([_COVER, _percent_page()])
        rows = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")["sections"]["Summary Ratios"]
        row = next(r for r in rows if r["label"].startswith("Return"))
        assert row["regime"] == "percent"
        cell = row["periods"]["2026-03-31"]
        assert cell == {"bhc": 1.10, "peer": 1.05, "pct": 62}

    def test_titleless_page_skipped(self, _patch_pdfplumber):
        """A page without the section-title band contributes no section."""
        _patch_pdfplumber([_COVER, _Page("no band here"), _percent_page()])
        parsed = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")
        assert list(parsed["sections"]) == ["Summary Ratios"]

    def test_paired_regime_with_change_columns(self, _patch_pdfplumber):
        """A ``% of Total`` row keeps amount and pct, plus trailing percent changes."""
        _patch_pdfplumber([_COVER, _paired_page()])
        rows = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")["sections"][
            "Parent Company Balance Sheet"
        ]
        row = next(r for r in rows if r["label"].startswith("Investment"))
        cell = row["periods"]["2026-03-31"]
        assert cell == {"amount": 336992000000, "pct_total": 46.63}
        assert row["change"] == {"1y": 6.34, "5y": 21.44}

    def test_table_without_dates_rejected(self, _patch_pdfplumber):
        """A table with no dated header is not read; its section stays empty."""
        _patch_pdfplumber([_COVER, _nodate_page()])
        parsed = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")
        assert parsed["sections"]["Bad Section"] == []

    def test_empty_grid_table_skipped(self, _patch_pdfplumber):
        """A table that extracts an empty grid is skipped without error."""
        _patch_pdfplumber([_COVER, _emptygrid_page()])
        parsed = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")
        assert parsed["sections"]["Grid Gone"] == []

    def test_status_rows_prepend_carried_loan_type(self, _patch_pdfplumber):
        """A figure-less caption is carried onto the following status rows."""
        _patch_pdfplumber([_COVER, _status_page()])
        rows = bhcpr.parse_bhcpr_pdf(b"%PDF-1.7")["sections"]["Past Due"]
        labels = [r["label"] for r in rows]
        assert "Loans Commercial 30-89 days past due" in labels
        assert "Auto 90+ days past due" in labels
        assert "Loans" not in labels
