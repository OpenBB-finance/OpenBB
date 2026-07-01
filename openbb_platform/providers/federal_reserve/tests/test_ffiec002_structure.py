"""Tests for the FFIEC 002 report structure generator."""

import json
from types import SimpleNamespace

import pytest

from openbb_federal_reserve.utils import ffiec002_structure
from openbb_federal_reserve.utils.ffiec002_structure import (
    _appendix_lines,
    _captions,
    _clean_caption,
    _line_reference,
    _normalize_schedule,
    _parse_row,
    _schedule_sort_key,
    generate,
    parse_structure,
    write_asset,
)

# A synthetic Appendix A that exercises every parsing branch: the banner that
# opens the listing and the FFIEC 002S banner that closes it; a single-line data
# row; a Schedule C "C. Part 1" multi-word reference; the "+D47" superscript
# glitch on a RAL row; a wrapped row whose occurrence and references print on the
# following physical lines; a fully wrapped row whose occurrence and schedule/line
# split across two trailing lines; a "Q," wrapped Schedule Q row; a "Cover"
# abbreviation row; a text-item (Y-flag) row; a column-bearing pair that folds the
# column letter into the line; and an under-specified row with no schedule.
_PDF_PAGES = [
    "Prose that precedes the appendix banner.",
    "\n".join(
        [
            "Appendix A",
            "FFIEC 002 Report Detailed Field Specifications",
            "   ",
            "SUB IDENTIFIER RCFD",
            "RC ITEM IDENTIFIER OCCURRENCE TEXT ITEM (Y=YES)",
            "RCFD0010 1 RAL 1A A",
            "RCFN0010 1 RAL 1A B",
            "RCFD1415 1 C. Part 1 1A A",
            "RCFDC421 1 RAL+D47 4B1B A",
            "RCFDG014 ",
            "   ",
            "1 M, Part 4 6A1 A",
            "RCONF233 ",
            "   ",
            "1 ",
            "   ",
            "E M1C ",
            "RCFNF585 1 Q, M3B B",
            "RCON5590 ",
            "RCFD2170 1 RAL 3 A",
            "RCON9395 1 Cover CONSCD",
            "TEXTC366 1 Y Cover Page Name",
            "RCXX9999 1 ",
            "10",
            "DOCUMENT CIPS TECHNICAL RELEASE NUMBER 1.1",
        ]
    ),
    "\n".join(
        [
            "Appendix B",
            "FFIEC 002S Report Detailed Field Specifications",
            "RCFD9998 1 RAL 99 A",
        ]
    ),
]

# A synthetic per-institution CSV: the header row, the identity rows, a short row
# to skip, the ID_RSSD metadata row, and value rows whose captions resolve onto
# the parsed MDRMs (including one with collapsible whitespace, one carrying a
# doubled column-context trailer, one whose trailer is split by a wrap space, and
# one blank). RCFD2170 is reported here so it survives the sample filter.
_CSV_TEXT = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,TEST BRANCH",
        "Short Row",
        "ID_RSSD,Reporting entity identifier,317810",
        "RCFD0010,CASH AND DUE FROM   DEPOSITORIES,6560443",
        "RCFN0010,CASH DUE (BANK U.S.+FOREIGN OFC) (BANK U.S.+FOREIGN OFC),100",
        "RCFD1415,LOANS SECURED BY REAL ESTATE,200",
        "RCFD2170,TOTAL ASSETS (BANK U.S.+FOREIGN OF C),28143263",
        "RCFDBLNK,,500",
    ]
)

# A second sampled filing exercising the membership union: it reports RCONF233,
# an MDRM the first filing omits, so the union covers both.
_CSV_TEXT_SECOND = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,OTHER BRANCH",
        "ID_RSSD,Reporting entity identifier,999999",
        "RCFD0010,CASH AND DUE FROM DEPOSITORIES,42",
        "RCONF233,IRAS AND KEOGH PLAN ACCTS (BANK U.S. OFC ONLY),0",
    ]
)


def _fake_reader(pages):
    """Build a stand-in ``PdfReader`` whose pages yield the given text."""
    return SimpleNamespace(
        pages=[SimpleNamespace(extract_text=lambda text=text: text) for text in pages]
    )


def _patch_reader(monkeypatch, pages):
    """Patch the lazily imported ``PdfReader`` to return ``pages``."""
    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", lambda _stream: _fake_reader(pages))


class TestNormalizeSchedule:
    """Coverage for the schedule-reference normalizer."""

    def test_cover_variants(self):
        """Both ``Cover`` and ``Cover Page`` fold to ``Cover Page``."""
        assert _normalize_schedule("Cover") == "Cover Page"
        assert _normalize_schedule("Cover Page") == "Cover Page"

    def test_q_part_folds_to_q(self):
        """Any Schedule Q part qualifier folds to the bare ``Q`` code."""
        assert _normalize_schedule("Q, Part 1") == "Q"
        assert _normalize_schedule("Q") == "Q"

    def test_schedule_c_separator(self):
        """The ``C.`` separator variants normalize to the comma form."""
        assert _normalize_schedule("C.") == "C"
        assert _normalize_schedule("C. Part 1") == "C, Part 1"

    def test_plain_schedule_unchanged(self):
        """A schedule with no variant is returned verbatim."""
        assert _normalize_schedule("RAL") == "RAL"


class TestLineReference:
    """Coverage for the line/column reference combiner."""

    def test_folds_column(self):
        """A column letter folds into the line reference."""
        assert _line_reference("1A", "B") == "1A.B"

    def test_no_column(self):
        """A line with no column is returned as-is."""
        assert _line_reference("M1", None) == "M1"

    def test_no_line(self):
        """A missing line yields ``None``."""
        assert _line_reference(None, "A") is None


class TestParseRow:
    """Coverage for the single-row schedule/line/column resolver."""

    def test_single_line_row(self):
        """A plain row splits into schedule, line, and trailing column."""
        assert _parse_row("RCFD0010", "1 RAL 1A A") == ("RAL", "1A", "A")

    def test_text_flag_consumed(self):
        """The ``Y`` text-item flag is dropped before the schedule."""
        assert _parse_row("TEXTC366", "1 Y Cover Page Name") == (
            "Cover Page",
            "Name",
            None,
        )

    def test_superscript_glitch_stripped(self):
        """A ``+D47`` superscript glitch is stripped from the schedule token."""
        assert _parse_row("RCFDC421", "1 RAL+D47 4B1B A") == ("RAL", "4B1B", "A")

    def test_wrapped_q_comma_form(self):
        """A wrapped Schedule Q row printed as ``Q,`` resolves to ``Q``."""
        assert _parse_row("RCFNF585", "1 Q, M3B B") == ("Q", "M3B", "B")

    def test_multiword_schedule(self):
        """A multi-word schedule reference is matched whole."""
        assert _parse_row("RCFDG014", "1 M, Part 4 6A1 A") == ("M, Part 4", "6A1", "A")

    def test_no_schedule_returns_none(self):
        """A row carrying no schedule reference yields ``None``."""
        assert _parse_row("RCXX9999", "1") is None

    def test_unrecognized_token_returns_none(self):
        """A non-schedule leading token yields ``None``."""
        assert _parse_row("RCXX0000", "1 ZZZ 1 A") is None


class TestAppendixLines:
    """Coverage for the appendix-boundary extraction from PDF pages."""

    def test_brackets_on_banners(self, monkeypatch):
        """Lines before Appendix A and from Appendix B onward are dropped."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        lines = _appendix_lines(b"%PDF-1.7")
        assert "Appendix A" not in lines
        assert not any("002S" in line for line in lines)
        assert not any("RCFD9998" in line for line in lines)
        assert lines[0] == "SUB IDENTIFIER RCFD"

    def test_handles_empty_page_text(self, monkeypatch):
        """A page whose ``extract_text`` returns ``None`` contributes no lines."""
        _patch_reader(monkeypatch, [None])
        assert _appendix_lines(b"%PDF-1.7") == []


class TestCleanCaption:
    """Coverage for the column-context trailer stripper."""

    def test_strips_doubled_trailer(self):
        """A doubled ``(BANK ...)`` trailer is removed in full."""
        cleaned = _clean_caption(
            "CASH DUE (BANK U.S.+FOREIGN OFC) (BANK U.S.+FOREIGN OFC)"
        )
        assert cleaned == "CASH DUE"

    def test_strips_wrap_split_trailer(self):
        """A trailer whose token is split by a wrap space is still removed."""
        assert _clean_caption("TOTAL ASSETS (BANK U.S.+FOREIGN OF C)") == "TOTAL ASSETS"

    def test_strips_us_office_only_trailer(self):
        """The ``(BANK U.S. OFC ONLY)`` trailer variant is removed."""
        assert _clean_caption("TOTAL DEPOSITS (BANK U.S. OFC ONLY)") == "TOTAL DEPOSITS"

    def test_preserves_meaningful_parenthetical(self):
        """A non-context parenthetical stays in the caption."""
        assert (
            _clean_caption("OTHER LIABILITIES (TO NONRELATED PARTIES)")
            == "OTHER LIABILITIES (TO NONRELATED PARTIES)"
        )


class TestCaptions:
    """Coverage for the CSV caption map."""

    def test_collapses_cleans_and_skips(self):
        """Captions collapse whitespace and drop the trailer; junk rows skip."""
        captions = _captions([_CSV_TEXT])
        assert captions["RCFD0010"] == "CASH AND DUE FROM DEPOSITORIES"
        assert captions["RCFN0010"] == "CASH DUE"
        assert "ID_RSSD" not in captions
        assert "RCFDBLNK" not in captions

    def test_unions_filings_first_wins(self):
        """Codes union across filings; the first filing's caption wins."""
        captions = _captions([_CSV_TEXT, _CSV_TEXT_SECOND])
        assert captions["RCFD0010"] == "CASH AND DUE FROM DEPOSITORIES"
        assert captions["RCONF233"] == "IRAS AND KEOGH PLAN ACCTS"


class TestParseStructure:
    """End-to-end parse over the synthetic appendix and CSV."""

    def test_one_item_per_mdrm(self, monkeypatch):
        """Every parsed MDRM is its own item with a single-code ``columns``."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        codes = [item["mdrm"] for item in items]
        assert codes.count("RCFD0010") == 1
        assert all(item["columns"] == [item["mdrm"]] for item in items)

    def test_column_folded_into_line(self, monkeypatch):
        """The consolidated and foreign-office cells fold their column letters."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = {item["mdrm"]: item for item in parse_structure(b"%PDF-1.7")}
        assert items["RCFD0010"]["line"] == "1A.A"
        assert items["RCFN0010"]["line"] == "1A.B"

    def test_wrapped_rows_recovered(self, monkeypatch):
        """The wrapped RCFDG014 and split RCONF233 rows resolve their schedules."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = {item["mdrm"]: item for item in parse_structure(b"%PDF-1.7")}
        assert items["RCFDG014"]["schedule"] == "M, Part 4"
        assert items["RCONF233"]["schedule"] == "E"
        assert items["RCONF233"]["line"] == "M1C"

    def test_bare_mdrm_before_next_row(self, monkeypatch):
        """A bare MDRM directly before the next data row stays unscheduled."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = {item["mdrm"]: item for item in parse_structure(b"%PDF-1.7")}
        assert items["RCON5590"]["schedule"] == ""
        assert items["RCFD2170"]["line"] == "3.A"

    def test_schedule_titles_and_order(self, monkeypatch):
        """Schedule names resolve to titles and items sort into form order."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        cover = next(i for i in items if i["schedule"] == "Cover Page")
        assert cover["schedule_name"] == "Cover Page"
        ral = next(i for i in items if i["schedule"] == "RAL")
        assert ral["schedule_name"].startswith("Schedule RAL")
        order = [i["schedule"] for i in items]
        assert order.index("Cover Page") < order.index("RAL")

    def test_caption_from_csv(self, monkeypatch):
        """A sampled MDRM's caption comes from the cleaned CSV description."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = {
            item["mdrm"]: item for item in parse_structure(b"%PDF-1.7", [_CSV_TEXT])
        }
        assert items["RCFD0010"]["caption"] == "CASH AND DUE FROM DEPOSITORIES"

    def test_sample_filters_unreported_mdrms(self, monkeypatch):
        """With a sample, an MDRM no filing reports is dropped from the items."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        codes = {item["mdrm"] for item in parse_structure(b"%PDF-1.7", [_CSV_TEXT])}
        assert "RCFD0010" in codes
        assert "RCFDC421" not in codes
        assert "RCXX9999" not in codes

    def test_sample_unions_filings(self, monkeypatch):
        """An MDRM reported only by the second filing still becomes an item."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        codes = {
            item["mdrm"]
            for item in parse_structure(b"%PDF-1.7", [_CSV_TEXT, _CSV_TEXT_SECOND])
        }
        assert "RCONF233" in codes


class TestScheduleSortKey:
    """Coverage for the schedule ordering key."""

    def test_known_schedule_in_order(self):
        """A known schedule sorts by its form position."""
        assert _schedule_sort_key("RAL") < _schedule_sort_key("A")

    def test_unknown_schedule_last(self):
        """An unknown schedule sorts after every known schedule."""
        assert _schedule_sort_key("ZZ")[0] > _schedule_sort_key("T")[0]


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def test_generate_from_local_files(self, monkeypatch, tmp_path):
        """``generate`` reads local PDF and CSV paths and summarizes schedules."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_file = tmp_path / "report.csv"
        csv_file.write_text(_CSV_TEXT, encoding="utf-8")
        payload = generate(str(pdf), [str(csv_file)])
        assert payload["item_count"] == len(payload["items"])
        assert payload["schedule_count"] == len(payload["schedules"])
        assert "RAL" in {s["schedule"] for s in payload["schedules"]}

    def test_generate_fetches_when_no_paths(self, monkeypatch):
        """Without paths, ``generate`` downloads the PDF and sampled filings."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        monkeypatch.setattr(
            ffiec002_structure, "fetch_pdf_bytes", lambda _url: b"%PDF-1.7"
        )
        monkeypatch.setattr(
            ffiec002_structure, "_fetch_validation_csvs", lambda: [_CSV_TEXT]
        )
        payload = generate()
        assert payload["source"] == ffiec002_structure.USER_GUIDE_URL

    def test_generate_raises_without_sample(self, monkeypatch):
        """An empty sample raises rather than emitting an unfiltered structure."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        monkeypatch.setattr(
            ffiec002_structure, "fetch_pdf_bytes", lambda _url: b"%PDF-1.7"
        )
        monkeypatch.setattr(ffiec002_structure, "_fetch_validation_csvs", list)
        with pytest.raises(RuntimeError, match="No sampled FFIEC 002 filing"):
            generate()

    def test_fetch_validation_csvs_skips_error_pages(self, monkeypatch):
        """``_fetch_validation_csvs`` keeps CSV payloads and drops error pages."""
        served = {ffiec002_structure.VALIDATION_RSSDS[0]: _CSV_TEXT}

        def _fake_fetch(_rpt, rssd, _dt):
            """Serve a CSV for one filer and the NIC error page for the rest."""
            return served.get(rssd, "<!DOCTYPE html><html>Error</html>")

        monkeypatch.setattr(ffiec002_structure, "fetch_report_csv", _fake_fetch)
        monkeypatch.setattr(
            ffiec002_structure, "latest_quarter_end", lambda: "20260331"
        )
        assert ffiec002_structure._fetch_validation_csvs() == [_CSV_TEXT]

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_file = tmp_path / "report.csv"
        csv_file.write_text(_CSV_TEXT, encoding="utf-8")
        target = tmp_path / "ffiec002" / "structure.json"
        monkeypatch.setattr(ffiec002_structure, "ASSET_PATH", target)
        path = write_asset(str(pdf), [str(csv_file)])
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a summary."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_file = tmp_path / "report.csv"
        csv_file.write_text(_CSV_TEXT, encoding="utf-8")
        target = tmp_path / "ffiec002" / "structure.json"
        monkeypatch.setattr(ffiec002_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv",
            ["ffiec002_structure", "--pdf", str(pdf), "--csv", str(csv_file)],
        )
        ffiec002_structure._main()
        out = capsys.readouterr().out
        assert "schedules" in out and "items" in out
