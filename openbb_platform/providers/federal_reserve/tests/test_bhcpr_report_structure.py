"""Tests for the FR BHCPR performance-report PDF parser."""

from types import SimpleNamespace

import pytest

from openbb_federal_reserve.utils import bhcpr_report_structure
from openbb_federal_reserve.utils.bhcpr_report_structure import (
    _amount_period_columns,
    _assign_columns,
    _build_rows,
    _build_sub_band,
    _caption_and_words,
    _caption_level,
    _cluster_right_edges,
    _line_words,
    _marks_thousands,
    _page_label,
    _parse_toc,
    _section_title,
    _to_number,
    parse_bhcpr_pdf,
)

# The five period-end dates printed in every band header, most recent first.
_DATES = ["03/31/2026", "03/31/2025", "12/31/2025", "12/31/2024", "12/31/2023"]

# The canonical right-edge grid of the fifteen ratio value columns
# (bank, peer, percentile) across the five periods, as measured from the report.
_RATIO_GRID = [
    307.0,
    343.5,
    366.5,
    403.0,
    439.5,
    462.5,
    499.0,
    535.5,
    558.5,
    595.0,
    631.5,
    654.5,
    691.0,
    727.5,
    750.5,
]

# The right-edge of each period's date in a ratio-band header (96-point pitch).
_DATE_X1 = [340.8, 436.8, 532.8, 628.8, 724.8]

# The right-edge of each period's date in an amount-band header (80-point pitch);
# dollar values right-align just right of these and left of the next period.
_AMOUNT_DATE_X1 = [332.8, 412.8, 492.8, 572.8, 652.8]

# The right-edge of each period's dollar value in an amount band.
_AMOUNT_VALUE_X1 = [350.5, 430.5, 510.5, 590.5, 670.5]


def _word(text, x1, top, width=None):
    """Build one pdfplumber-style word dict right-aligned to ``x1``."""
    span = width if width is not None else 6.0 * len(text)
    return {"text": text, "x0": x1 - span, "x1": x1, "top": top}


def _caption_words(caption, top, x0=36.0):
    """Build the caption-plus-dotted-leader words for a body row."""
    leader = caption + "." * 30
    return [{"text": leader, "x0": x0, "x1": 269.0, "top": top}]


def _date_header(top, date_x1=None):
    """Build a date-header row with the five period dates."""
    edges = date_x1 if date_x1 is not None else _DATE_X1
    return [_word(date, x1, top, width=37.6) for date, x1 in zip(_DATES, edges)]


def _ratio_label_row(top):
    """Build the ``BHC Peer # <n> Pct`` ratio label row for five periods."""
    words = []
    for period in range(5):
        base = 280.0 + period * 96.0
        words.append(_word("BHC", base + 8, top, width=18))
        words.append(_word("Peer", base + 36, top, width=20))
        words.append(_word("#", base + 50, top, width=6))
        words.append(_word("1", base + 58, top, width=6))
        words.append(_word("Pct", base + 73, top, width=16))
    return words


def _ratio_row(caption, top, triplets):
    """Build a ratio metric row: caption then bank/peer/pct per period."""
    words = _caption_words(caption, top)
    for period, (bhc, peer, pct) in enumerate(triplets):
        for value, x1 in zip(
            (bhc, peer, pct), _RATIO_GRID[period * 3 : period * 3 + 3]
        ):
            if value is not None:
                words.append(_word(value, x1, top))
    return words


def _amount_row(caption, top, amounts, growth=None):
    """Build an amount metric row: one dollar value per period, right of its date."""
    words = _caption_words(caption, top)
    for amount, x1 in zip(amounts, _AMOUNT_VALUE_X1):
        if amount is not None:
            words.append(_word(amount, x1, top))
    if growth:
        for value, x1 in zip(growth, (710.5, 750.5)):
            words.append(_word(value, x1, top))
    return words


def _wide_amount_row(caption, top, amounts):
    """Build a wide-amount row whose values align to the ratio-pitch right edges."""
    words = _caption_words(caption, top)
    wide_x1 = [366.5, 462.5, 558.5, 654.5, 750.5]
    for amount, x1 in zip(amounts, wide_x1):
        if amount is not None:
            words.append(_word(amount, x1, top))
    return words


class _FakePage:
    """A stand-in pdfplumber page yielding crafted words and flattened text."""

    def __init__(self, word_rows):
        self._words = [w for row in word_rows for w in row]

    def extract_words(self, **_kwargs):
        """Return the page's word dicts."""
        return list(self._words)

    def extract_text(self, **_kwargs):
        """Return the flattened text, one physical line per crafted row."""
        by_top: dict[float, list[dict]] = {}
        for word in self._words:
            by_top.setdefault(round(word["top"], 1), []).append(word)
        lines = []
        for top in sorted(by_top):
            ordered = sorted(by_top[top], key=lambda w: w["x0"])
            lines.append(" ".join(w["text"] for w in ordered))
        return "\n".join(lines)


def _toc_page():
    """Build a Table-of-Contents page with two section entries and noise."""
    return _FakePage(
        [
            [{"text": "Table of Contents", "x0": 36.0, "x1": 140.0, "top": 20.0}],
            [{"text": "Section", "x0": 36.0, "x1": 70.0, "top": 30.0}],
            [
                {
                    "text": "Summary Ratios" + "." * 40 + " 1",
                    "x0": 36.0,
                    "x1": 400.0,
                    "top": 40.0,
                }
            ],
            [
                {
                    "text": "Loan Mix" + "." * 40 + " 7A",
                    "x0": 36.0,
                    "x1": 400.0,
                    "top": 50.0,
                }
            ],
            [
                {
                    "text": "Some descriptive prose with no leader",
                    "x0": 36.0,
                    "x1": 300.0,
                    "top": 60.0,
                }
            ],
        ]
    )


def _banner_rows(page_label, title, banner_top=32.0):
    """Build the page banner: institution line, column labels, and section title."""
    return [
        [
            {
                "text": "JPMORGAN CHASE & CO. NEW YORK, NY",
                "x0": 36.0,
                "x1": 300.0,
                "top": 19.0,
            }
        ],
        [{"text": f"Page {page_label} of 23", "x0": 36.0, "x1": 120.0, "top": 26.0}],
        [
            {
                "text": "RSSD Number FR Dist. Peer #",
                "x0": 280.0,
                "x1": 460.0,
                "top": banner_top,
            }
        ],
        [
            {
                "text": "BHC Name City/State",
                "x0": 36.0,
                "x1": 160.0,
                "top": banner_top + 2.5,
            }
        ],
        [{"text": title, "x0": 36.0, "x1": 200.0, "top": banner_top + 14.0}],
    ]


def _ratio_page():
    """Build a Summary-Ratios page: a sub-header banner and two ratio rows."""
    rows = _banner_rows("1", "Summary Ratios")
    rows.append(_date_header(69.0))
    rows.append(_ratio_label_row(114.0))
    rows.append(
        [{"text": "Earnings and Profitability:", "x0": 36.0, "x1": 200.0, "top": 128.0}]
    )
    rows.append(
        [{"text": "Percent of Average Assets", "x0": 36.0, "x1": 200.0, "top": 135.0}]
    )
    rows.append(
        _ratio_row(
            "Net interest income (tax equivalent)",
            142.0,
            [
                ("2.15", "3.08", "11"),
                ("2.22", "2.86", "16"),
                ("2.17", "2.99", "12"),
                ("2.29", "2.78", "18"),
                ("2.35", "2.84", "18"),
            ],
        )
    )
    rows.append(
        _ratio_row(
            "Net income (Subchapter S adjusted)",
            156.0,
            [("1.20", None, None)] + [(None, None, None)] * 4,
        )
    )
    return _FakePage(rows)


def _amount_page():
    """Build an Income-Statement page: a thousands amount band with growth columns."""
    rows = _banner_rows("2", "Income Statement—Revenues and Expenses")
    header = _date_header(78.0, date_x1=_AMOUNT_DATE_X1)
    header.insert(0, _word("Dollar Amount in Thousands", 271.0, 78.0, width=90))
    rows.append(header)
    rows.append(
        _amount_row(
            "Interest and fees on loans",
            92.0,
            ["24,885,000", "23,195,000", "97,186,000", "95,904,000", "86,431,000"],
            growth=["7.29", "139.53"],
        )
    )
    return _FakePage(rows)


def _split_page():
    """Build a Regulatory-Capital page: a thousands amount region then a ratio grid."""
    rows = _banner_rows("14", "Regulatory Capital Components and Ratios")
    header = _date_header(69.0)
    header.insert(0, _word("Dollar Amount in Thousands", 271.0, 69.0, width=90))
    rows.append(header)
    rows.append(
        [{"text": "Common Equity Tier 1 Capital", "x0": 36.0, "x1": 200.0, "top": 82.0}]
    )
    rows.append(
        _wide_amount_row(
            "Retained earnings",
            96.0,
            ["428,206,000", "386,616,000", "416,055,000", "376,886,000", "334,341,000"],
        )
    )
    rows.append(_ratio_label_row(462.7))
    rows.append([{"text": "Capital Ratios", "x0": 36.0, "x1": 120.0, "top": 476.0}])
    rows.append(
        _ratio_row(
            "Tier 1 leverage",
            490.0,
            [
                ("6.60", "9.86", "6"),
                ("7.16", "9.95", "6"),
                ("6.88", "9.76", "7"),
                ("7.24", "9.86", "6"),
                ("7.24", "9.48", "7"),
            ],
        )
    )
    return _FakePage(rows)


def _fake_pdf():
    """Assemble a full stand-in BHCPR PDF spanning every band layout."""
    return SimpleNamespace(
        pages=[_toc_page(), _ratio_page(), _amount_page(), _split_page()]
    )


@pytest.fixture
def parsed(monkeypatch):
    """Parse the synthetic BHCPR PDF with ``pdfplumber.open`` stubbed out."""
    import pdfplumber

    monkeypatch.setattr(pdfplumber, "open", lambda _stream: _fake_pdf())
    return parse_bhcpr_pdf(b"%PDF-fake")


class TestHelpers:
    """Unit coverage for the geometry and value helpers."""

    def test_to_number_int_and_float(self):
        """Comma-separated integers and decimals convert without formatting loss."""
        assert _to_number("4,759,098,000") == 4759098000
        assert _to_number("2.15") == 2.15
        assert _to_number("-0.07") == -0.07

    def test_cluster_right_edges_splits_on_gap(self):
        """Right-edges within the gap collapse; a wide gap opens a new column."""
        assert _cluster_right_edges([307.0, 307.0, 343.5, 750.5]) == [
            307.0,
            343.5,
            750.5,
        ]

    def test_marks_thousands(self):
        """Thousands-dollar unit banners are detected, plain captions are not."""
        assert _marks_thousands("Dollar Amount in Thousands")
        assert _marks_thousands("Average assets ($000)")
        assert not _marks_thousands("Tier 1 leverage")

    def test_caption_and_words_splits_on_leader(self):
        """The dotted leader separates caption text from trailing value words."""
        words = _ratio_row(
            "Net interest income (tax equivalent)",
            142.0,
            [("2.15", "3.08", "11")] + [(None, None, None)] * 4,
        )
        caption, numeric = _caption_and_words(words)
        assert caption == "Net interest income (tax equivalent)"
        assert [w["text"] for w in numeric] == ["2.15", "3.08", "11"]

    def test_caption_and_words_without_leader(self):
        """A leaderless line still drops numeric words from the caption."""
        words = [
            _word("12.40", 307.0, 10.0),
            {"text": "Header", "x0": 36.0, "x1": 80.0, "top": 10.0},
        ]
        caption, numeric = _caption_and_words(words)
        assert caption == "Header"
        assert [w["text"] for w in numeric] == ["12.40"]

    def test_amount_period_columns_ignores_growth(self):
        """Each period maps to its dollar column; trailing growth columns drop out."""
        grid = [350.5, 430.5, 510.5, 590.5, 670.5, 710.5, 750.5]
        amount_date_x1 = [332.8, 412.8, 492.8, 572.8, 652.8]
        date_words = [
            _word(d, x1, 78.0, width=37.6) for d, x1 in zip(_DATES, amount_date_x1)
        ]
        columns = _amount_period_columns(grid, date_words)
        assert columns == [[0], [1], [2], [3], [4]]

    @pytest.mark.parametrize("x0,level", [(36.0, 0), (50.0, 1), (72.0, 2)])
    def test_caption_level(self, x0, level):
        """Indent level steps with the caption's left margin."""
        assert _caption_level(x0) == level

    def test_amount_period_columns_no_candidate(self):
        """A period with no value column in its window maps to an empty list."""
        date_words = [
            _word(d, x1, 78.0, width=37.6) for d, x1 in zip(_DATES, _AMOUNT_DATE_X1)
        ]
        assert _amount_period_columns([], date_words) == [[], [], [], [], []]

    def test_line_words_groups_offset_baselines(self):
        """A caption and its values a fraction of a point apart stay one line."""
        page = _FakePage(
            [
                [{"text": "Caption" + "." * 20, "x0": 36.0, "x1": 200.0, "top": 142.0}],
                [_word("2.15", 307.0, 141.7)],
            ]
        )
        lines = _line_words(page)
        assert len(lines) == 1
        assert {w["text"] for w in lines[0][1]} == {"Caption" + "." * 20, "2.15"}


class TestTableOfContents:
    """Coverage for Table-of-Contents parsing."""

    def test_parses_entries_in_order(self):
        """Section entries are kept in order; the header and prose are dropped."""
        toc = _parse_toc(_toc_page())
        assert toc == [
            {"section": "Summary Ratios", "page": "1"},
            {"section": "Loan Mix", "page": "7A"},
        ]

    def test_skips_empty_caption_entry(self):
        """A leader line with no caption text before it is ignored."""
        page = _FakePage(
            [[{"text": "." * 30 + " 5", "x0": 36.0, "x1": 200.0, "top": 30.0}]]
        )
        assert _parse_toc(page) == []

    def test_skips_section_header_line(self):
        """A bare ``Section .... Page`` heading line is not treated as an entry."""
        page = _FakePage(
            [
                [
                    {
                        "text": "Section" + "." * 30 + " Page",
                        "x0": 36.0,
                        "x1": 200.0,
                        "top": 30.0,
                    }
                ]
            ]
        )
        assert _parse_toc(page) == []


class TestPageHeader:
    """Coverage for the per-page section title and page label."""

    def test_page_label_absent(self):
        """A page without a ``Page n of m`` line yields no label."""
        lines = _line_words(_FakePage([[_word("x", 100.0, 10.0)]]))
        assert _page_label(lines) is None

    def test_section_title_no_band(self):
        """A page with no date-header band yields no section title."""
        lines = _line_words(_FakePage([[_word("x", 100.0, 10.0)]]))
        assert _section_title(lines) is None

    def test_section_title_no_banner(self):
        """A date band without the column banner above it yields no title."""
        lines = _line_words(_FakePage([_date_header(69.0)]))
        assert _section_title(lines) is None

    def test_section_title_and_page_label(self):
        """The title below the banner and the ``Page n of m`` label are recovered."""
        lines = _line_words(_ratio_page())
        assert _section_title(lines) == "Summary Ratios"
        assert _page_label(lines) == "1"

    def test_section_title_letter_suffix_label(self):
        """A letter-suffixed page label such as ``7A`` is recovered."""
        page = _FakePage(_banner_rows("7A", "Loan Mix") + [_date_header(69.0)])
        lines = _line_words(page)
        assert _page_label(lines) == "7A"
        assert _section_title(lines) == "Loan Mix"


class TestParseBhcprPdf:
    """End-to-end coverage of the assembled report."""

    def test_sections_in_order(self, parsed):
        """Every data page contributes one ordered section with its page label."""
        assert parsed["sections"] == [
            {"section": "Summary Ratios", "page": "1"},
            {"section": "Income Statement—Revenues and Expenses", "page": "2"},
            {"section": "Regulatory Capital Components and Ratios", "page": "14"},
        ]

    def test_summary_ratios_sample(self, parsed):
        """The flagship ratio row carries bank, peer, and percentile per period."""
        row = next(
            r
            for r in parsed["rows"]
            if r["caption"] == "Net interest income (tax equivalent)"
            and not r["is_header"]
        )
        assert row["unit"] == "ratio"
        assert row["sub_header"] == "Percent of Average Assets"
        assert row["values_by_period"]["03/31/2026"] == {
            "bhc": 2.15,
            "peer": 3.08,
            "pct": 11,
        }
        assert row["values_by_period"]["12/31/2023"] == {
            "bhc": 2.35,
            "peer": 2.84,
            "pct": 18,
        }

    def test_sub_header_row_emitted(self, parsed):
        """A colon-terminated caption becomes a value-less sub-header row."""
        header = next(
            r
            for r in parsed["rows"]
            if r["caption"] == "Earnings and Profitability" and r["is_header"]
        )
        assert header["sub_header"] is None
        assert all(
            cell == {"bhc": None, "peer": None, "pct": None}
            for cell in header["values_by_period"].values()
        )

    def test_blank_cells_stay_aligned(self, parsed):
        """A single-value ratio row leaves the other periods blank."""
        row = next(
            r
            for r in parsed["rows"]
            if r["caption"] == "Net income (Subchapter S adjusted)"
            and not r["is_header"]
        )
        assert row["values_by_period"]["03/31/2025"] == {
            "bhc": None,
            "peer": None,
            "pct": None,
        }

    def test_amount_band_expands_thousands(self, parsed):
        """A thousands amount row expands the bank value to true dollars."""
        row = next(
            r
            for r in parsed["rows"]
            if r["caption"] == "Interest and fees on loans" and not r["is_header"]
        )
        assert row["unit"] == "dollars"
        assert row["values_by_period"]["03/31/2026"]["bhc"] == 24_885_000_000
        assert row["values_by_period"]["03/31/2026"]["peer"] is None

    def test_skips_page_without_title(self, monkeypatch):
        """A data page lacking a recoverable title or label is skipped."""
        import pdfplumber

        blank = _FakePage([_date_header(69.0)])
        pdf = SimpleNamespace(pages=[_toc_page(), blank])
        monkeypatch.setattr(pdfplumber, "open", lambda _stream: pdf)
        result = parse_bhcpr_pdf(b"%PDF-fake")
        assert result["sections"] == []
        assert result["rows"] == []

    def test_split_page_dollar_then_ratio(self, parsed):
        """A page with a dollar region above the ratio grid parses both correctly."""
        retained = next(
            r
            for r in parsed["rows"]
            if r["caption"] == "Retained earnings" and not r["is_header"]
        )
        assert retained["unit"] == "dollars"
        assert retained["values_by_period"]["03/31/2026"]["bhc"] == 428_206_000_000
        leverage = next(
            r
            for r in parsed["rows"]
            if r["caption"] == "Tier 1 leverage" and not r["is_header"]
        )
        assert leverage["unit"] == "ratio"
        assert leverage["values_by_period"]["03/31/2026"] == {
            "bhc": 6.60,
            "peer": 9.86,
            "pct": 6,
        }


class TestBuildRows:
    """Coverage for band assembly edge cases."""

    def test_no_band_returns_empty(self):
        """A page with no date-header band contributes no rows."""
        page = _FakePage([[_word("text", 100.0, 10.0)]])
        assert _build_rows(page, "Section", "1") == []

    def test_short_date_header_not_a_band(self):
        """A header row with fewer than five dates is not treated as a band start."""
        rows = _banner_rows("9", "Foreign Activities")
        partial = [
            _word(d, x1, 69.0, width=37.6) for d, x1 in zip(_DATES[:4], _DATE_X1[:4])
        ]
        rows.append(partial)
        rows.append(_ratio_label_row(114.0))
        rows.append(_ratio_row("Some ratio", 142.0, [("1.0", "2.0", "3")] * 5))
        built = _build_rows(_FakePage(rows), "Foreign Activities", "9")
        assert built == []

    def test_ratio_sub_band_short_grid_guard(self):
        """A ratio band whose later periods never have values leaves them blank."""
        lines = _line_words(
            _FakePage(
                [
                    _date_header(69.0),
                    _ratio_label_row(114.0),
                    _ratio_row(
                        "Sparse ratio",
                        142.0,
                        [("1.0", "2.0", "3")] + [(None, None, None)] * 4,
                    ),
                ]
            )
        )
        built = _build_sub_band(
            lines,
            69.0,
            540.0,
            _date_header(69.0),
            "",
            _DATES,
            "S",
            "1",
            is_ratio=True,
        )
        row = built[0]
        assert row["values_by_period"]["03/31/2026"] == {
            "bhc": 1.0,
            "peer": 2.0,
            "pct": 3,
        }
        assert row["values_by_period"]["12/31/2023"] == {
            "bhc": None,
            "peer": None,
            "pct": None,
        }

    def test_assign_columns_collision_and_out_of_span(self):
        """A second word in a column is dropped; out-of-span tokens are ignored."""
        grid = [307.0]
        words = [
            _word("1.11", 307.0, 10.0),
            _word("2.22", 308.0, 10.0),
            {"text": "Caption", "x0": 36.0, "x1": 120.0, "top": 10.0},
        ]
        assert _assign_columns(words, grid) == ["1.11"]

    def test_sub_band_skips_inner_date_and_pct(self):
        """A date line and a Pct label inside a sub-band are not emitted."""
        lines = _line_words(
            _FakePage(
                [
                    _date_header(69.0),
                    [_word("06/30/2025", 400.0, 100.0, width=37.6)],
                    _ratio_label_row(114.0),
                    _ratio_row("Kept ratio", 142.0, [("1.0", "2.0", "3")] * 5),
                ]
            )
        )
        header_words = _date_header(69.0)
        built = _build_sub_band(
            lines, 69.0, 540.0, header_words, "", _DATES, "S", "1", is_ratio=True
        )
        captions = [r["caption"] for r in built]
        assert captions == ["Kept ratio"]

    def test_growth_and_banner_lines_skipped(self):
        """``Percent Change`` and growth-label lines are not emitted as rows."""
        rows = _banner_rows("2", "Income Statement—Revenues and Expenses")
        header = _date_header(78.0, date_x1=_AMOUNT_DATE_X1)
        header.insert(0, _word("Dollar Amount in Thousands", 271.0, 78.0, width=90))
        rows.append(header)
        rows.append([{"text": "Percent Change", "x0": 600.0, "x1": 660.0, "top": 82.0}])
        rows.append([_word("1-Year", 705.2, 87.0), _word("5-Year", 745.2, 87.0)])
        rows.append(
            _amount_row(
                "Interest and fees on loans",
                92.0,
                ["24,885,000", "23,195,000", "97,186,000", "95,904,000", "86,431,000"],
            )
        )
        built = _build_rows(_FakePage(rows), "Income", "2")
        captions = [r["caption"] for r in built]
        assert "Percent Change" not in captions
        assert "Interest and fees on loans" in captions


class TestAssetGeneration:
    """Coverage for the committed section-list asset writer."""

    def test_write_sections_asset(self, monkeypatch, tmp_path):
        """The writer serializes the section list as indented JSON."""
        import json

        target = tmp_path / "bhcpr" / "sections.json"
        monkeypatch.setattr(bhcpr_report_structure, "ASSET_PATH", target)
        bhcpr_report_structure._write_sections_asset(
            [{"section": "Summary Ratios", "page": "1"}]
        )
        assert json.loads(target.read_text()) == [
            {"section": "Summary Ratios", "page": "1"}
        ]

    def test_main_from_local_pdf(self, monkeypatch, tmp_path, capsys):
        """``_main`` parses a local PDF and writes the section asset."""
        import pdfplumber

        target = tmp_path / "sections.json"
        monkeypatch.setattr(bhcpr_report_structure, "ASSET_PATH", target)
        monkeypatch.setattr(pdfplumber, "open", lambda _stream: _fake_pdf())
        local = tmp_path / "report.pdf"
        local.write_bytes(b"%PDF-fake")
        monkeypatch.setattr(
            "sys.argv",
            ["prog", "--pdf", str(local)],
        )
        bhcpr_report_structure._main()
        assert target.exists()
        assert "3 sections" in capsys.readouterr().out

    def test_main_fetches_remote_pdf(self, monkeypatch, tmp_path, capsys):
        """``_main`` without ``--pdf`` fetches the report through the FFIEC client."""
        import pdfplumber

        from openbb_federal_reserve.utils import ffiec

        target = tmp_path / "sections.json"
        monkeypatch.setattr(bhcpr_report_structure, "ASSET_PATH", target)
        monkeypatch.setattr(pdfplumber, "open", lambda _stream: _fake_pdf())
        captured = {}

        def _fake_fetch(path, referer=None):
            captured["path"] = path
            return b"%PDF-fake"

        monkeypatch.setattr(ffiec, "_fetch_bytes", _fake_fetch)
        monkeypatch.setattr("sys.argv", ["prog", "--id", "1039502", "--dt", "20260331"])
        bhcpr_report_structure._main()
        assert "id=1039502" in captured["path"] and "dt=20260331" in captured["path"]
        assert target.exists()
