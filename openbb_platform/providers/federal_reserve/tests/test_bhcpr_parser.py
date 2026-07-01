"""Tests for the FR BHCPR PDF parser."""

import pytest

from openbb_federal_reserve.utils import bhcpr

# Cover page: institution name, city/state, and RSSD in their cover-page layout.
_COVER = "\n".join(
    [
        "Board of Governors of the Federal Reserve System RSSD Number: 1039502 FR BHCPR",
        "Bank Holding Company Performance Report March 31, 2026—FR BHCPR",
        "JPMORGAN CHASE & CO.",
        "BHC Name Table of Contents",
        "City/StateNEW YORK, NY Section Page Number",
        "Summary Ratios............................................................. 1",
        "03/2026",
    ]
)

# A ratio page: the date banner, three pre-banner ``($000)`` rows, the BHC/Peer/
# Pct banner, a sub-header, a full triplet row, and a bank-only Subchapter S row.
_SUMMARY = "\n".join(
    [
        "JPMORGAN CHASE & CO. NEW YORK, NY FR BHCPR",
        "1039502 2 1",
        "Page 1 of 23",
        "BHC Name City/State RSSD Number FR Dist. Peer #",
        "Summary Ratios",
        "03/31/2026 03/31/2025 12/31/2025 12/31/2024 12/31/2023",
        "Average assets ($000)......... 4,759,098,000 4,239,690,000 4,433,249,750"
        " 4,089,686,500 3,830,238,750",
        "Number of BHCs in peer group......... 130 136 128 135 139",
        "BHC Peer # 1 Pct BHC Peer # 1 Pct BHC Peer # 1 Pct BHC Peer # 1 Pct"
        " BHC Peer # 1 Pct",
        "Earnings and Profitability:",
        "Net interest income (tax equivalent)......... 2.15 3.08 11 2.22 2.86 16"
        " 2.17 2.99 12 2.29 2.78 18 2.35 2.84 18",
        "Net income (Subchapter S adjusted)......... 1.20 0.78 0.87 0.79 0.99",
    ]
)

# A dollar page: the ``Dollar Amount in Thousands`` banner with trailing
# percent-change columns, and a metric row whose amounts are in thousands.
_INCOME = "\n".join(
    [
        "JPMORGAN CHASE & CO. NEW YORK, NY FR BHCPR",
        "1039502 2 1",
        "Page 2 of 23",
        "BHC Name City/State RSSD Number FR Dist. Peer #",
        "Income Statement—Revenues and Expenses",
        "Percent Change",
        "Dollar Amount in Thousands 03/31/2026 03/31/2025 12/31/2025 12/31/2024"
        " 12/31/2023 1-Year 5-Year",
        "Interest and fees on loans......... 24,885,000 23,195,000 97,186,000"
        " 95,904,000 86,431,000 7.29 139.53",
    ]
)

# A paired ``% of Total`` page: the ``% of`` band, its ``Total`` continuation,
# the dollar banner, a sub-header, and a paired ten-figure metric row.
_BALANCE = "\n".join(
    [
        "JPMORGAN CHASE & CO. NEW YORK, NY FR BHCPR",
        "1039502 2 1",
        "Page 21 of 23",
        "BHC Name City/State RSSD Number FR Dist. Peer #",
        "Parent Company Balance Sheet",
        "% of % of % of",
        "Total Total Total Percent Change",
        "Dollar Amount in Thousands 03/31/2026 Assets 03/31/2025 Assets 12/31/2025"
        " Assets 12/31/2024 12/31/2023 1-Year 5-Year",
        "Assets",
        "Investment in bank subsidiaries......... 336,992,000 46.63 316,915,000"
        " 46.53 336,203,000 47.35 313,082,000 299,610,000 6.34 21.44",
    ]
)

# A bare-banner page: only the date row, a unit sub-header, a five-figure row,
# and a caption-only blank row (a line item with no figures filed).
_SERVICING = "\n".join(
    [
        "JPMORGAN CHASE & CO. NEW YORK, NY FR BHCPR",
        "1039502 2 1",
        "Page 19 of 23",
        "BHC Name City/State RSSD Number FR Dist. Peer #",
        "Servicing, Securitization and Asset Sale Activities—Part 3",
        "03/31/2026 03/31/2025 12/31/2025 12/31/2024 12/31/2023",
        "30–89 Days Past Due Securitized Assets Percent of Type",
        "1–4 family residential loans......... 1.05 1.24 1.22 1.10 1.05",
        "Credit card receivables.........",
        ".....................................",
    ]
)


class _FakePage:
    """A stand-in pdfplumber page returning fixed extracted text."""

    def __init__(self, text):
        """Store the page's extracted text, or None for a blank page."""
        self._text = text

    def extract_text(self):
        """Return the page's extracted text."""
        return self._text


class _FakePdf:
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


@pytest.fixture
def _patch_pdfplumber(monkeypatch):
    """Patch ``pdfplumber.open`` to yield the supplied fixture page texts."""

    def _apply(texts):
        """Install a fake document built from the page texts."""
        import pdfplumber

        pages = [_FakePage(text) for text in texts]
        monkeypatch.setattr(pdfplumber, "open", lambda _: _FakePdf(pages))

    return _apply


class TestHelpers:
    """Tests for the module-level token and label helpers."""

    def test_to_number_scales_thousands(self):
        """A figure scales to full dollars; a non-numeric token is None."""
        assert bhcpr._to_number("4,759,098,000", scale=1000) == 4759098000000
        assert bhcpr._to_number("2.15") == 2.15
        assert bhcpr._to_number("n/a") is None

    def test_split_label_figures_dotted_leader(self):
        """A dotted leader separates the caption from its figures."""
        label, figures = bhcpr._split_label_figures("Net income......... 1.39 1.13 76")
        assert label == "Net income"
        assert figures == ["1.39", "1.13", "76"]

    def test_split_label_figures_no_leader(self):
        """Without a leader the caption ends at the first numeric token."""
        label, figures = bhcpr._split_label_figures("Number of BHCs 130 136")
        assert label == "Number of BHCs"
        assert figures == ["130", "136"]

    def test_split_label_figures_subheader(self):
        """A caption with non-numeric trailing text is a figure-less sub-header."""
        label, figures = bhcpr._split_label_figures("Earnings and Profitability:")
        assert label == "Earnings and Profitability:"
        assert figures == []

    def test_split_label_figures_mixed_tail_is_caption(self):
        """A dotted row whose tail mixes text and numbers is a caption, not data."""
        label, figures = bhcpr._split_label_figures("See note......... 1 see page 2")
        assert label == "See note......... 1 see page 2"
        assert figures == []

    def test_split_label_figures_leading_leader_has_no_label(self):
        """A row that is only a dotted leader has an empty caption and no figures."""
        label, figures = bhcpr._split_label_figures("...........")
        assert label == ""
        assert figures == []

    def test_period_dates_absent_returns_empty(self):
        """A page band without a five-date row yields no period dates."""
        assert bhcpr._period_dates(["no dates here", "03/31/2026 only one"]) == []

    def test_bank_series_pct(self):
        """A pct row keeps the bank figure of each period's triplet."""
        figures = [str(i) for i in range(15)]
        assert bhcpr._bank_series(figures, "pct") == ["0", "3", "6", "9", "12"]

    def test_bank_series_paired(self):
        """A paired row keeps the amount of each period, skipping its percents."""
        figures = ["a", "p", "b", "p", "c", "p", "d", "e", "x", "y"]
        assert bhcpr._bank_series(figures, "paired") == ["a", "b", "c", "d", "e"]

    def test_bank_series_plain(self):
        """A plain row keeps the first five per-period figures."""
        figures = ["1", "2", "3", "4", "5", "6", "7"]
        assert bhcpr._bank_series(figures, "plain") == ["1", "2", "3", "4", "5"]


class TestParseBhcprPdf:
    """Tests for ``parse_bhcpr_pdf`` over representative page text."""

    def _parse(self, patch, extra_pages=()):
        """Parse a document of the cover plus the supplied data pages."""
        patch([_COVER, *extra_pages])
        return bhcpr.parse_bhcpr_pdf(b"%PDF")

    def test_non_pdf_content_returns_empty_sections(self):
        """A non-PDF response (a non-filer's HTML error page) yields no sections.

        A commercial bank does not file the BHCPR — its holding company does — so
        the NIC returns an HTML error page rather than a PDF. Parsing must return
        an empty structure so the fetcher raises ``EmptyDataError`` instead of
        letting pdfplumber crash the request with a 500.
        """
        result = bhcpr.parse_bhcpr_pdf(b"<!DOCTYPE html><html>Not found</html>")
        assert result["sections"] == []
        assert result["period_dates"] == []
        assert result["identity"]["rssd_id"] is None

    def test_identity_from_cover(self, _patch_pdfplumber):
        """The cover yields the institution name, city/state, and RSSD."""
        parsed = self._parse(_patch_pdfplumber, [_SUMMARY])
        assert parsed["identity"] == {
            "institution_name": "JPMORGAN CHASE & CO.",
            "city_state": "NEW YORK, NY",
            "rssd_id": "1039502",
        }

    def test_period_dates_are_iso_latest_first(self, _patch_pdfplumber):
        """The five period-end dates are ISO strings, latest first."""
        parsed = self._parse(_patch_pdfplumber, [_SUMMARY])
        assert parsed["period_dates"] == [
            "2026-03-31",
            "2025-03-31",
            "2025-12-31",
            "2024-12-31",
            "2023-12-31",
        ]

    def test_ratio_row_carries_peer_and_percentile(self, _patch_pdfplumber):
        """A pct row carries five bank values, a peer average, and a rank."""
        parsed = self._parse(_patch_pdfplumber, [_SUMMARY])
        rows = parsed["sections"][0]["rows"]
        metric = next(r for r in rows if r["label"].startswith("Net interest income"))
        assert metric["bank"] == [2.15, 2.22, 2.17, 2.29, 2.35]
        assert metric["peer"] == 3.08
        assert metric["percentile"] == 11

    def test_thousands_marked_row_scales(self, _patch_pdfplumber):
        """A ``($000)`` caption scales its bank series to full dollars."""
        parsed = self._parse(_patch_pdfplumber, [_SUMMARY])
        rows = parsed["sections"][0]["rows"]
        avg = next(r for r in rows if r["label"].startswith("Average assets"))
        assert avg["bank"][0] == 4759098000000

    def test_bank_only_row_pads_to_five(self, _patch_pdfplumber):
        """A bank-only pct row (no peer) keeps five bank values and no peer."""
        parsed = self._parse(_patch_pdfplumber, [_SUMMARY])
        rows = parsed["sections"][0]["rows"]
        sub_s = next(r for r in rows if "Subchapter S" in r["label"])
        assert sub_s["bank"] == [1.20, 0.78, 0.87, 0.79, 0.99]
        assert sub_s["peer"] is None

    def test_subheader_row_is_header(self, _patch_pdfplumber):
        """A caption-only line becomes a header row carrying no figures."""
        parsed = self._parse(_patch_pdfplumber, [_SUMMARY])
        rows = parsed["sections"][0]["rows"]
        assert any(
            r["is_header"] and r["label"] == "Earnings and Profitability:" for r in rows
        )

    def test_dollar_section_scales_amounts(self, _patch_pdfplumber):
        """A dollar section scales its thousands amounts to full dollars."""
        parsed = self._parse(_patch_pdfplumber, [_INCOME])
        rows = parsed["sections"][0]["rows"]
        loans = next(r for r in rows if r["label"].startswith("Interest and fees"))
        assert loans["bank"] == [
            24885000000,
            23195000000,
            97186000000,
            95904000000,
            86431000000,
        ]

    def test_paired_page_keeps_period_amounts(self, _patch_pdfplumber):
        """A paired ``% of Total`` row keeps one amount per period, no percents."""
        parsed = self._parse(_patch_pdfplumber, [_BALANCE])
        rows = parsed["sections"][0]["rows"]
        assert not any("Total Total" in r["label"] for r in rows)
        invest = next(r for r in rows if r["label"].startswith("Investment in bank"))
        assert invest["bank"] == [
            336992000000,
            316915000000,
            336203000000,
            313082000000,
            299610000000,
        ]

    def test_bare_page_unit_subheader_and_blank_row(self, _patch_pdfplumber):
        """A bare-banner page keeps a unit sub-header and a figure-less row."""
        parsed = self._parse(_patch_pdfplumber, [_SERVICING])
        rows = parsed["sections"][0]["rows"]
        assert any(
            r["is_header"] and r["label"].endswith("Percent of Type") for r in rows
        )
        blank = next(r for r in rows if r["label"].startswith("Credit card"))
        assert blank["is_header"] is True

    def test_skips_blank_and_titleless_pages(self, _patch_pdfplumber):
        """Blank pages and pages without a section title are skipped."""
        titleless = "JPMORGAN CHASE & CO. NEW YORK, NY FR BHCPR\nno label band here"
        parsed = self._parse(_patch_pdfplumber, [None, titleless, _SUMMARY])
        assert [s["section"] for s in parsed["sections"]] == ["Summary Ratios"]
