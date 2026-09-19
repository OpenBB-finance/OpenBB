"""Tests for the shared Appendix A field-specification parser."""

import re
from types import SimpleNamespace

import pytest

from openbb_federal_reserve.utils import report_structure
from openbb_federal_reserve.utils.report_structure import (
    ReportConfig,
    clean_caption,
    collapse_doubled,
    is_codes_only,
    is_header_line,
    is_noise,
    is_not_applicable,
    level_from_caption,
    level_from_reference,
    norm,
    opens_wrapped_item,
    parse_structure,
    pdf_lines,
    split_reference,
    starts_new_row,
    summarize,
)

_SCHEDULE_HEADER = re.compile(r"^Schedule\s+([A-Z]{2}(?:-[A-Z])?)\s*[-–]\s*(.+)$")

# A synthetic appendix exercising every parser branch: a first implicit
# schedule, a banner switch, nested references, a wrapped item whose MDRM lands
# on a following line, a wrapped caption with an unclosed parenthetical that must
# not be split at its inner sub-reference, a doubled reference, a stray-leader
# memoranda reference, an itemization free-text/amount pair, a space-dash header,
# a colon header, an asterisk-then-colon header, a "Not applicable" placeholder,
# and an instructional-prose block.
_APPENDIX = [
    "BANNER",
    "Report Form",
    "8-character reference",
    "7",
    "-",
    "1. First implicit schedule item BHCP0001",
    "Schedule SB - Second Schedule",
    "2. Securities:*",
    "2.a. Treasury BHCP0003",
    "3. Wrapped item caption",
    "continuing here BHCP0004",
    "4.f. Loans net of allowance (sum of items",
    "4.c and 4.d minus item 4.e)",
    "BHCP0005",
    "5. Interest expense -",
    "6. 6. Doubled reference item BHCP0006",
    "Memoranda",
    "Note items are to be completed by holding companies that elected",
    "the fair value option.",
    "sM.1.a. Total assets BHCP0007",
    "7. Not applicable",
    "8. Itemized other assets - describe",
    "TEXT Description of other assets TEXT0008",
    "8. Itemized other assets amount BHCP0008",
]

_CONFIG = ReportConfig(
    appendix_banner="banner",
    schedule_header=_SCHEDULE_HEADER,
    noise={"report form"},
    first_schedule=("FIRST", "First Schedule"),
    cover_schedule=("COVER", "Cover Page"),
    is_note_prose=lambda text: "to be completed" in text.lower(),
)


def _parse(monkeypatch, lines, config=_CONFIG):
    """Parse a synthetic appendix by patching the PDF page reader."""
    pages = ["\n".join(lines)]
    monkeypatch.setattr(
        report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
    )
    return parse_structure(b"%PDF-1.7", config)


def _by_line(records, reference):
    """Return the first record whose line reference matches exactly."""
    return next(r for r in records if r["line"] == reference)


class TestLineHelpers:
    """Unit coverage for the per-line classifiers and splitters."""

    def test_norm(self):
        """Whitespace is collapsed and the text lower-cased."""
        assert norm("  FR  Y-9LP  ") == "fr y-9lp"

    @pytest.mark.parametrize(
        "reference, level",
        [
            ("1", 1),
            ("1.a", 2),
            ("1.a.(1)", 3),
            ("1.a.(1)(a)", 4),
            ("M.2", 1),
            ("A.1", 1),
            ("g", 2),
        ],
    )
    def test_level_from_reference(self, reference, level):
        """Indent depth follows the reference's nesting."""
        assert level_from_reference(reference) == level

    @pytest.mark.parametrize(
        "caption, level",
        [
            ("(a) lettered", 4),
            ("(1) numbered", 3),
            ("b. lettered", 2),
            ("plain header", 1),
        ],
    )
    def test_level_from_caption(self, caption, level):
        """Unreferenced headers infer depth from their bullet token."""
        assert level_from_caption(caption) == level

    def test_split_reference_match(self):
        """A leading reference is split from its caption."""
        assert split_reference("1.a. Loans") == ("1.a", "Loans")

    def test_split_reference_no_reference(self):
        """A caption with no leading reference returns ``None``."""
        assert split_reference("Total assets") == (None, "Total assets")

    def test_collapse_doubled_reference(self):
        """A reference printed twice collapses to a single reference."""
        assert collapse_doubled("14. 14. Holding company") == "14. Holding company"

    def test_collapse_doubled_stray_leader(self):
        """A stray lowercase leader before a memoranda reference is dropped."""
        assert collapse_doubled("sM.1.a. Total assets") == "M.1.a. Total assets"

    def test_collapse_doubled_passthrough(self):
        """A line with no doubled reference is returned unchanged."""
        assert collapse_doubled("1. Plain item") == "1. Plain item"

    def test_starts_new_row(self):
        """A reference followed by a space opens a row; enumeration does not."""
        assert starts_new_row("2.a. Treasury")
        assert not starts_new_row("continuing here")

    @pytest.mark.parametrize(
        "line",
        ["19. Not applicable", "g. Not applicable", "Not applicable"],
    )
    def test_is_not_applicable_true(self, line):
        """Referenced and bare reserved placeholders are recognized."""
        assert is_not_applicable(line)

    def test_is_not_applicable_false(self):
        """A real caption is not a placeholder."""
        assert not is_not_applicable("1. Real line")

    def test_clean_caption_strips_type_and_dash(self):
        """Data-type prefixes and trailing filler dashes are removed."""
        assert clean_caption("TEXT  Other  assets -") == "Other assets"

    def test_is_codes_only(self):
        """A bare MDRM line is codes-only; a captioned line is not."""
        assert is_codes_only("BHCP0001 BHCP0002")
        assert not is_codes_only("1. Loans BHCP0001")
        assert not is_codes_only("No codes here")

    def test_is_header_line(self):
        """A code-less space-dash caption is a header; a code line is not."""
        assert is_header_line("5. Interest expense -")
        assert not is_header_line("5. Interest BHCP0001")

    def test_opens_wrapped_item(self):
        """A referenced non-colon line opens a wrapped item; colons do not."""
        assert opens_wrapped_item("3. Wrapped item caption")
        assert not opens_wrapped_item("1. Section header:")
        assert not opens_wrapped_item("2. Securities:*")
        assert not opens_wrapped_item("Code-less header")


class TestNoise:
    """Coverage for the noise classifier."""

    @pytest.mark.parametrize(
        "line",
        ["Report Form", "123", "8-character reference", "-"],
    )
    def test_is_noise_true(self, line):
        """Running heads, page numbers, MDRM banners, and dashes are noise."""
        assert is_noise(line, _CONFIG)

    def test_is_noise_false(self):
        """A real caption is not noise."""
        assert not is_noise("1. Interest income", _CONFIG)


class TestPdfLines:
    """Coverage for the appendix-boundary extraction from PDF pages."""

    def test_extracts_between_banner_and_end(self, monkeypatch):
        """Lines before the banner and from the end banner on are dropped."""
        config = ReportConfig(
            appendix_banner="banner",
            schedule_header=_SCHEDULE_HEADER,
            appendix_end="the end",
        )
        pages = ["intro\nBANNER\n1. Item BHCP0001\nThe End\n2. After BHCP0002"]
        monkeypatch.setattr(
            report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
        )
        lines = pdf_lines(b"%PDF-1.7", config)
        assert lines == ["1. Item BHCP0001"]

    def test_reads_to_document_end_without_end_banner(self, monkeypatch):
        """Without an end banner the listing runs to the last page."""
        pages = ["BANNER\n1. Item BHCP0001"]
        monkeypatch.setattr(
            report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
        )
        assert pdf_lines(b"%PDF-1.7", _CONFIG) == ["1. Item BHCP0001"]

    def test_handles_empty_page_text(self, monkeypatch):
        """A page whose text is empty contributes no lines."""
        pages = [""]
        monkeypatch.setattr(
            report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
        )
        assert pdf_lines(b"%PDF-1.7", _CONFIG) == []

    def test_strips_soft_hyphens(self, monkeypatch):
        """Soft hyphens inside captions are removed before joining."""
        pages = ["BANNER\n1. Mort­gage BHCP0001"]
        monkeypatch.setattr(
            report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
        )
        assert pdf_lines(b"%PDF-1.7", _CONFIG) == ["1. Mortgage BHCP0001"]


class _FakePdf:
    """A stand-in ``pdfplumber`` document usable as a context manager."""

    def __init__(self, page_texts):
        self.pages = [
            SimpleNamespace(extract_text=lambda text=text: text) for text in page_texts
        ]

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


class TestReadPdfPages:
    """Coverage for the shared pdfplumber reader."""

    def test_extracts_each_page_text(self, monkeypatch):
        """Each page's extracted text is returned in order."""
        import pdfplumber

        monkeypatch.setattr(
            pdfplumber,
            "open",
            lambda _stream: _FakePdf(["First page", "Second page"]),
        )
        assert report_structure.read_pdf_pages(b"%PDF-1.7") == [
            "First page",
            "Second page",
        ]

    def test_none_page_text_becomes_empty_string(self, monkeypatch):
        """A page whose ``extract_text`` returns ``None`` yields an empty string."""
        import pdfplumber

        monkeypatch.setattr(
            pdfplumber, "open", lambda _stream: _FakePdf([None, "Text"])
        )
        assert report_structure.read_pdf_pages(b"%PDF-1.7") == ["", "Text"]


class TestParseStructure:
    """End-to-end parse over the synthetic appendix."""

    def test_first_implicit_schedule(self, monkeypatch):
        """The opening item sits under the implicit first schedule."""
        records = _parse(monkeypatch, _APPENDIX)
        assert _by_line(records, "1")["schedule"] == "FIRST"

    def test_banner_switches_schedule(self, monkeypatch):
        """A ``Schedule SB -`` banner changes the active schedule."""
        records = _parse(monkeypatch, _APPENDIX)
        assert _by_line(records, "2.a")["schedule"] == "SB"

    def test_asterisk_colon_header(self, monkeypatch):
        """A reference caption ending in ``:*`` is a standalone header."""
        records = _parse(monkeypatch, _APPENDIX)
        header = _by_line(records, "2")
        assert header["is_header"] and header["mdrm"] is None

    def test_wrapped_item_resolves(self, monkeypatch):
        """A caption whose MDRM lands on the next line resolves to one row."""
        records = _parse(monkeypatch, _APPENDIX)
        wrapped = _by_line(records, "3")
        assert wrapped["mdrm"] == "BHCP0004"
        assert wrapped["caption"].endswith("continuing here")

    def test_open_paren_enumeration_not_split(self, monkeypatch):
        """A sub-reference inside an unclosed parenthetical stays in the caption."""
        records = _parse(monkeypatch, _APPENDIX)
        row = _by_line(records, "4.f")
        assert row["mdrm"] == "BHCP0005"
        assert "4.c and 4.d" in row["caption"]

    def test_space_dash_header(self, monkeypatch):
        """A code-less space-dash caption becomes its own header row."""
        records = _parse(monkeypatch, _APPENDIX)
        header = _by_line(records, "5")
        assert header["is_header"] and header["mdrm"] is None

    def test_doubled_reference_collapsed(self, monkeypatch):
        """A doubled reference renders one row with a single reference."""
        records = _parse(monkeypatch, _APPENDIX)
        assert _by_line(records, "6")["caption"] == "Doubled reference item"

    def test_note_prose_dropped(self, monkeypatch):
        """An instructional-prose block is dropped, not emitted as a header."""
        records = _parse(monkeypatch, _APPENDIX)
        assert not any("to be completed" in r["caption"].lower() for r in records)

    def test_stray_leader_memoranda_resolves(self, monkeypatch):
        """The ``sM.1.a.`` typo resolves to a clean memoranda row."""
        records = _parse(monkeypatch, _APPENDIX)
        row = _by_line(records, "M.1.a")
        assert row["mdrm"] == "BHCP0007"
        assert row["caption"] == "Total assets"

    def test_not_applicable_dropped(self, monkeypatch):
        """A reserved ``Not applicable`` placeholder produces no row."""
        records = _parse(monkeypatch, _APPENDIX)
        assert not any("Not applicable" in r["caption"] for r in records)

    def test_itemization_text_dropped_amount_kept(self, monkeypatch):
        """The free-text half of an itemization pair is dropped; amount kept."""
        records = _parse(monkeypatch, _APPENDIX)
        amounts = [r for r in records if r["mdrm"] == "BHCP0008"]
        assert amounts and amounts[0]["caption"] == "Itemized other assets amount"
        assert not any(r["mdrm"] == "TEXT0008" for r in records)

    def test_empty_caption_row_skipped(self, monkeypatch):
        """A row whose caption cleans to empty is not emitted."""
        records = _parse(monkeypatch, ["BANNER", "1. - BHCP0009"], _CONFIG)
        assert all(r["caption"] for r in records)

    def test_plain_codeless_line_becomes_header(self, monkeypatch):
        """A code-less, non-wrapping caption flushes as a header row."""
        lines = ["BANNER", "Standalone caption", "1. Item BHCP0001"]
        records = _parse(monkeypatch, lines, _CONFIG)
        header = next(r for r in records if r["caption"] == "Standalone caption")
        assert header["is_header"]

    def test_consecutive_wrapped_headers(self, monkeypatch):
        """A new row opening while a code-less buffer is pending flushes it first.

        ``"3. Open item"`` buffers as a wrapped item; the next physical line
        opens its own numbered row before any MDRM arrives, so the buffered line
        is emitted as a header and the new row begins a fresh buffer.
        """
        lines = ["BANNER", "3. Open item", "4. Next wrapped item", "tail BHCP0001"]
        records = _parse(monkeypatch, lines, _CONFIG)
        assert _by_line(records, "3")["is_header"]
        assert _by_line(records, "4")["mdrm"] == "BHCP0001"

    def test_buffered_text_description_dropped(self, monkeypatch):
        """A wrapped ``TEXT`` description resolved via the buffer is dropped.

        The leading caption ``"9. Itemized describe"`` buffers; its description
        half arrives as ``"... Description TEXT0009"`` (the code not at line
        start, bypassing the early drop), so the dropping happens at flush.
        """
        lines = [
            "BANNER",
            "9. Itemized describe",
            "of other assets Description TEXT0009",
        ]
        records = _parse(monkeypatch, lines, _CONFIG)
        assert not any(r["mdrm"] == "TEXT0009" for r in records)

    def test_blank_line_within_appendix(self, monkeypatch):
        """A blank physical line inside the appendix is skipped, not parsed."""
        pages = ["BANNER\n1. Item BHCP0001\n\n2. Item BHCP0002"]
        monkeypatch.setattr(
            report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
        )
        records = parse_structure(b"%PDF-1.7", _CONFIG)
        assert {r["mdrm"] for r in records} == {"BHCP0001", "BHCP0002"}


class TestSummarize:
    """Coverage for the asset-summary wrapper."""

    def test_summarize_collects_schedules(self):
        """Schedules are collected once, in first-seen order, with the source."""
        items = [
            {"schedule": "A", "schedule_name": "Alpha"},
            {"schedule": "A", "schedule_name": "Alpha"},
            {"schedule": "B", "schedule_name": "Beta"},
        ]
        payload = summarize(items, "http://example/guide.pdf")
        assert payload["source"] == "http://example/guide.pdf"
        assert payload["item_count"] == 3
        assert payload["schedule_count"] == 2
        assert [s["schedule"] for s in payload["schedules"]] == ["A", "B"]


def test_module_exposes_mdrm_pattern():
    """The shared MDRM pattern is importable for reuse by report generators."""
    assert report_structure.MDRM.fullmatch("BHCP0508")
