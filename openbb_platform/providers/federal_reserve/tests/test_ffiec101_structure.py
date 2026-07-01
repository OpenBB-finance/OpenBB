"""Tests for the FFIEC 101 report structure generator."""

import json
from types import SimpleNamespace

from openbb_federal_reserve.utils import ffiec101_structure
from openbb_federal_reserve.utils.ffiec101_structure import (
    _belongs_to_previous,
    _build_grid_items,
    _clean_caption,
    _clean_cover_caption,
    _codes,
    _collapse_doubled,
    _csv_union,
    _drop_orphan_headers,
    _grid_caption,
    _grid_metric,
    _is_codes_only,
    _is_column_label_fragment,
    _is_format_variant_row,
    _is_identity_row,
    _is_limit_format_row,
    _is_noise,
    _is_reference_boundary,
    _latest_quarter_end,
    _level_from_reference,
    _recase,
    _reconcile,
    _split_reference,
    _starts_new_row,
    generate,
    parse_guide,
    parse_structure,
    write_asset,
)

# A synthetic Appendix A that exercises every parsing branch: the pre-banner
# prose dropped before the appendix, page running heads and the item-limits /
# derived-flag notes, a schedule banner, a simple referenced line item, a
# derived ("*") flagged item, a wide-grid schedule with its "(Column A)" banner,
# wrapped column-label fragments, a bare digit-limit format row, doubled grid
# references, a wrapped caption whose MDRM lands on the following line, a
# code-less colon-terminated section header, the Memoranda bare header, a
# detached codes-only row, and a capital-ratio "(effective ...)" format-variant
# restatement that must be dropped.
_PDF_PAGES = [
    "File format prose that precedes the appendix banner.",
    "\n".join(
        [
            "FFIEC101 Report Detailed Field Specifications",
            "   ",
            "Report Form",
            "Line Number",
            "Row Description",
            "10",
            "Item limits, where applicable, are shown as (x,y).",
            "8-character MDRM reference codes are shown in the rightmost column.",
            "(Derived values are flagged with a trailing asterisk.)",
            "Schedule A - Advanced Approaches Regulatory Capital",
            "1. Common stock plus related surplus AAABP742",
            "2. Derived total capital AAABP793 *",
            "AAABP793 10,4 (effective starting March 31, 2016)",
            "Schedule B - Summary Risk-Weighted Asset Information",
            "(Column A) (Column B)",
            "Probability of",
            "Default",
            "8,2 11,0",
            "1. 1. Corporate exposures AAIIJ035 AAIIJ036",
            "31. Credit Valuation Adjustments:",
            "Memoranda",
            "M.1. Wrapped memoranda caption that continues",
            "onto a second physical line",
            "AAIIK100",
            "M.2. Detached column row caption",
            "AAIIK200 AAIIK201",
        ]
    ),
]


def _fake_reader(pages):
    """Build a stand-in ``PdfReader`` whose pages yield the given text."""
    return SimpleNamespace(
        pages=[SimpleNamespace(extract_text=lambda text=text: text) for text in pages]
    )


def _patch_reader(monkeypatch, pages):
    """Patch the lazily imported ``PdfReader`` to return ``pages``."""
    import pypdf

    monkeypatch.setattr(pypdf, "PdfReader", lambda _stream: _fake_reader(pages))


def _csv(rows):
    """Render an ``ItemName,Description,Value`` CSV from ``(name, desc, value)``."""
    body = "\n".join(f'{name},"{desc}",{value}' for name, desc, value in rows)
    return "ItemName,Description,Value\n" + body


class TestLineHelpers:
    """Unit coverage for the per-line classifiers and splitters."""

    def test_is_noise(self):
        """Running heads, bare page numbers, and the format notes are noise."""
        assert _is_noise("Report Form")
        assert _is_noise("42")
        assert _is_noise("Item limits, where applicable, are shown")
        assert _is_noise("8-character MDRM reference codes")
        assert _is_noise("(Derived values are flagged with an asterisk)")
        assert not _is_noise("1. Common stock AAABP742")

    def test_clean_caption(self):
        """Limit notes, stray asterisks and trailing dashes are stripped."""
        assert _clean_caption("Total   capital 10,4 (mmyyyy) *") == "Total capital"
        assert _clean_caption("Other assets -–") == "Other assets"

    def test_codes_strips_derived_flag(self):
        """The derived ``*`` flag is consumed; only the bare code is returned."""
        assert _codes("Derived total AAABP793 *") == ["AAABP793"]
        assert _codes("Grid AAIIJ035 AAIIJ036") == ["AAIIJ035", "AAIIJ036"]

    def test_level_from_reference(self):
        """Indent depth follows the reference nesting."""
        assert _level_from_reference("1") == 1
        assert _level_from_reference("a") == 2
        assert _level_from_reference("1.7a") == 3
        assert _level_from_reference("2.10.") == 2

    def test_is_reference_boundary(self):
        """End-of-line, space and period follow a genuine reference."""
        assert _is_reference_boundary("")
        assert _is_reference_boundary(" ")
        assert _is_reference_boundary(".")
        assert not _is_reference_boundary(",")

    def test_split_reference(self):
        """A line splits into reference and caption only at a real boundary."""
        assert _split_reference("1. Common stock") == ("1", "Common stock")
        assert _split_reference("Code-less caption") == (None, "Code-less caption")
        assert _split_reference("4, 15, and 21) note") == (
            None,
            "4, 15, and 21) note",
        )

    def test_collapse_doubled(self):
        """A doubled grid reference collapses to the prefixed canonical copy."""
        assert _collapse_doubled("26. 26. Unsettled txns") == "26. Unsettled txns"
        assert _collapse_doubled("M.2. 2. Regulated item") == "M.2. Regulated item"
        assert _collapse_doubled("1. Single reference") == "1. Single reference"

    def test_starts_new_row(self):
        """A reference followed by caption opens a row; enumeration text does not."""
        assert _starts_new_row("1. 1. Corporate exposures")
        assert not _starts_new_row("4, 15, and 21) continued text")
        assert not _starts_new_row("Wrapped caption fragment")

    def test_is_limit_format_row(self):
        """A bare comma-joined digit-pair row is a precision banner, not data."""
        assert _is_limit_format_row("8,2 11,0 8,2")
        assert not _is_limit_format_row("1. Item AAABP742")
        assert not _is_limit_format_row("Probability of Default")

    def test_is_column_label_fragment(self):
        """A code-less, reference-less, non-parenthetical line is a label fragment."""
        assert _is_column_label_fragment("Probability of")
        assert not _is_column_label_fragment("1. Numbered row")
        assert not _is_column_label_fragment("Code AAABP742")
        assert not _is_column_label_fragment("(Column A)")

    def test_is_codes_only(self):
        """A line of solely MDRM codes is a detached column row."""
        assert _is_codes_only("AAIIK200 AAIIK201")
        assert not _is_codes_only("M.1. Caption AAIIK100")
        assert not _is_codes_only("Probability of Default")

    def test_is_format_variant_row(self):
        """A line restating a captured MDRM with only a limit note is a variant."""
        items = [{"columns": ["AAABP793"]}]
        assert _is_format_variant_row(
            "AAABP793 10,4 (effective starting March 31, 2016)", items
        )
        assert not _is_format_variant_row("AAABP793 New caption text", items)
        assert not _is_format_variant_row("AAABZZZZ 10,4 (effective ...)", items)

    def test_belongs_to_previous(self):
        """A code-only line repeating the previous row's MDRM belongs to it."""
        previous = {"columns": ["AAABP793"]}
        assert _belongs_to_previous("AAABP793", previous)
        assert not _belongs_to_previous("AAABQQQQ", previous)


class TestPdfLines:
    """Coverage for the appendix-boundary extraction from PDF pages."""

    def test_drops_pre_banner_prose(self, monkeypatch):
        """Lines before the Appendix banner are dropped."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        lines = ffiec101_structure._pdf_lines(b"%PDF-1.7")
        assert all("file format prose" not in line.lower() for line in lines)
        assert "FFIEC101 Report Detailed Field Specifications" not in lines

    def test_handles_empty_page_text(self, monkeypatch):
        """A page whose ``extract_text`` returns ``None`` contributes no lines."""
        _patch_reader(monkeypatch, [None])
        assert ffiec101_structure._pdf_lines(b"%PDF-1.7") == []


class TestParseGuide:
    """End-to-end guide parse over the synthetic appendix."""

    def test_schedule_banner_switches(self, monkeypatch):
        """The ``Schedule A -`` / ``Schedule B -`` banners set the active schedule."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        schedules = {r["schedule"] for r in records}
        assert {"A", "B"} <= schedules
        first = next(r for r in records if r["mdrm"] == "AAABP742")
        assert first["schedule"] == "A"
        assert first["schedule_name"] == "Advanced Approaches Regulatory Capital"

    def test_simple_and_derived_items(self, monkeypatch):
        """A plain line item and a derived ``*`` item both capture their MDRM."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        plain = next(r for r in records if r["mdrm"] == "AAABP742")
        assert plain["caption"] == "Common stock plus related surplus"
        assert plain["is_header"] is False
        derived = next(r for r in records if r["mdrm"] == "AAABP793")
        assert derived["caption"] == "Derived total capital"

    def test_format_variant_row_dropped(self, monkeypatch):
        """The capital ``(effective ...)`` code-and-limit restatement is dropped."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        ratios = [r for r in records if r["mdrm"] == "AAABP793"]
        assert len(ratios) == 1
        assert ratios[0]["caption"] == "Derived total capital"

    def test_grid_doubled_reference_and_columns(self, monkeypatch):
        """A wide-grid row collapses its doubled reference and keeps both columns."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        grid = next(r for r in records if r["line"] == "1" and r["schedule"] == "B")
        assert grid["columns"] == ["AAIIJ035", "AAIIJ036"]
        assert grid["mdrm"] == "AAIIJ035"
        assert grid["caption"] == "Corporate exposures"

    def test_column_label_fragments_suppressed(self, monkeypatch):
        """Wrapped grid column-header label fragments are not emitted as items."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        captions = {r["caption"] for r in records}
        assert "Probability of" not in captions
        assert "Default" not in captions

    def test_colon_section_header(self, monkeypatch):
        """A code-less colon-terminated line becomes a standalone header."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        header = next(
            r for r in records if r["caption"] == "Credit Valuation Adjustments:"
        )
        assert header["is_header"] is True
        assert header["mdrm"] is None

    def test_bare_memoranda_header(self, monkeypatch):
        """The bare ``Memoranda`` line is emitted as its own header item."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        header = next(r for r in records if r["caption"] == "Memoranda")
        assert header["is_header"] is True

    def test_wrapped_item_resolves(self, monkeypatch):
        """A caption whose MDRM lands on the next line resolves to one row."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        wrapped = next(r for r in records if r["mdrm"] == "AAIIK100")
        assert wrapped["caption"].endswith("second physical line")
        assert wrapped["line"] == "M.1"

    def test_detached_columns_row(self, monkeypatch):
        """A caption followed by a bare codes-only line captures every column."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        records = parse_guide(b"%PDF-1.7")
        detached = next(r for r in records if r["line"] == "M.2")
        assert detached["columns"] == ["AAIIK200", "AAIIK201"]


class TestParseEdgeCases:
    """Targeted guide parses for the loop's less-common branches."""

    def _parse(self, monkeypatch, body_lines):
        """Parse a one-page synthetic appendix below the banner."""
        pages = [
            "FFIEC101 Report Detailed Field Specifications\n" + "\n".join(body_lines)
        ]
        _patch_reader(monkeypatch, pages)
        return parse_guide(b"%PDF-1.7")

    def test_empty_caption_row_skipped(self, monkeypatch):
        """A row whose caption cleans to empty is not emitted."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule A - Capital",
                "1. Real item AAABP742",
                "2. - *",
            ],
        )
        assert all(r["line"] != "2" for r in records)

    def test_limit_format_row_under_grid_skipped(self, monkeypatch):
        """A bare ``(x,y)`` precision row under a column banner is dropped."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule B - Grid",
                "(Column A) (Column B)",
                "1. Corporate exposures AAIIJ035 AAIIJ036",
                "8,2 11,0",
                "2. Bank exposures AAIIJ100 AAIIJ101",
            ],
        )
        captions = {r["caption"] for r in records}
        assert "8,2 11,0" not in captions
        assert {"Corporate exposures", "Bank exposures"} <= captions

    def test_wrapped_header_flushed_when_new_row_opens(self, monkeypatch):
        """A buffered code-less caption flushes as a header when a row opens."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule A - Capital",
                "5. Wrapped header caption with no code",
                "1. Next row item AAABP742",
            ],
        )
        header = next(r for r in records if r["line"] == "5")
        assert header["is_header"] is True
        assert header["mdrm"] is None
        item = next(r for r in records if r["line"] == "1")
        assert item["mdrm"] == "AAABP742"

    def test_stray_column_label_fragment_dropped(self, monkeypatch):
        """A code-less, reference-less banner fragment is not emitted."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule B - Grid",
                "(Column A)",
                "1. Corporate exposures AAIIJ035",
                "Probability",
            ],
        )
        assert all(r["caption"] != "Probability" for r in records)

    def test_codes_only_belongs_to_previous_dropped(self, monkeypatch):
        """A code-only line repeating the previous row's MDRM is dropped."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule A - Capital",
                "1. Capital ratio AAABP793",
                "AAABP793",
            ],
        )
        ratios = [r for r in records if r["mdrm"] == "AAABP793"]
        assert len(ratios) == 1

    def test_detached_new_codes_only_row_with_empty_buffer(self, monkeypatch):
        """A new code-only line with an empty buffer flushes without a caption."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule A - Capital",
                "1. Item one AAABP742",
                "AAABZZZZ",
            ],
        )
        assert [r["mdrm"] for r in records] == ["AAABP742"]

    def test_dedupe_drops_repeated_mdrm_caption(self, monkeypatch):
        """A later item repeating a prior MDRM and caption is de-duplicated."""
        records = self._parse(
            monkeypatch,
            [
                "Schedule A - Capital",
                "1. Common stock AAABP742",
                "1. Common stock AAABP742",
            ],
        )
        assert sum(1 for r in records if r["mdrm"] == "AAABP742") == 1


class TestCsvUnion:
    """Coverage for the public item-set union recovered from the CSVs."""

    def test_union_excludes_identity_and_empty(self):
        """Identity/admin rows and empty values are excluded from the union."""
        csv_text = _csv(
            [
                ("Institution Name", "", "ACME BANK"),
                ("ID_RSSD", "Reporting entity identifier", "852218"),
                ("DT_REPORT", "Report date", "20260331"),
                ("AAABP742", "COMMON STOCK", "100"),
                ("AAABP793", "EMPTY ITEM", ""),
            ]
        )
        union = _csv_union([csv_text])
        assert union == {"AAABP742": "COMMON STOCK"}

    def test_union_merges_filers_first_description_wins(self):
        """The union spans filers and keeps the first description seen."""
        first = _csv([("AAABP742", "FIRST DESC", "100")])
        second = _csv(
            [
                ("AAABP742", "SECOND DESC", "200"),
                ("AAAB3247", "RETAINED EARNINGS", "50"),
            ]
        )
        union = _csv_union([first, second])
        assert union["AAABP742"] == "FIRST DESC"
        assert union["AAAB3247"] == "RETAINED EARNINGS"

    def test_union_skips_short_and_malformed_rows(self):
        """Rows with fewer than three fields or non-MDRM names are skipped."""
        csv_text = "ItemName,Description,Value\nONLYONE\nnotacode,desc,5\n"
        assert _csv_union([csv_text]) == {}

    def test_is_identity_row(self):
        """Identity rows, the RSSD, and the reporting-date columns are admin."""
        assert _is_identity_row("Institution Name")
        assert _is_identity_row("ID_RSSD")
        assert _is_identity_row("DT")
        assert _is_identity_row("DT_REPORT_Q")
        assert not _is_identity_row("AAABP742")


class TestRecase:
    """Coverage for the ALL-CAPS description recasing."""

    def test_recase_preserves_acronyms_and_connectors(self):
        """Acronyms keep their casing and connector words go lowercase."""
        assert _recase("RISK WEIGHTED ASSETS") == "Risk Weighted Assets"
        assert _recase("WHOLESALE EXPOSURES: OTC DERIVATIVES") == (
            "Wholesale Exposures: OTC Derivatives"
        )
        assert _recase("ASSETS NOT INCLUDED IN A DEFINED CATEGORY") == (
            "Assets Not Included in a Defined Category"
        )

    def test_recase_hyphenated_and_leading_acronym(self):
        """Hyphenated tokens recase per piece and a leading acronym stays cased."""
        assert _recase("CLOSED-END FIRST LIEN") == "Closed-End First Lien"
        assert _recase("LGD AFTER MITIGANTS") == "LGD After Mitigants"

    def test_recase_passes_through_pure_punctuation(self):
        """A token with no alphabetic core is returned unchanged."""
        assert _recase("100% (DERIVED)") == "100% (Derived)"


class TestCoverCaption:
    """Coverage for the cover/admin caption cleanup."""

    def test_strips_prefix_and_length(self):
        """The ``Cover Page`` prefix and trailing field-length token are removed."""
        assert _clean_cover_caption("Cover Page Contact Name 72") == "Contact Name"
        assert _clean_cover_caption("Cover Page State of Bank 2") == "State of Bank"

    def test_strips_length_pair_and_format_hint(self):
        """A length pair and a date-format hint are stripped from the caption."""
        assert (
            _clean_cover_caption("Cover Page Legal Entity Identifier 0 or exactly 20")
            == "Legal Entity Identifier"
        )
        assert _clean_cover_caption("Cover Page Signature Date MM/DD/YYYY") == (
            "Signature Date"
        )


class TestGridItems:
    """Coverage for the Schedule B grid-cell recovery from the CSV."""

    def test_grid_metric_and_caption(self):
        """The metric heads the column; the exposure row captions the cell."""
        desc = "RISK WEIGHTED ASSETS - WHOLESALE EXPOSURES: CORPORATE (DERIVED)"
        assert _grid_metric(desc) == "Risk Weighted Assets"
        assert _grid_caption(desc) == "Wholesale Exposures: Corporate"

    def test_build_grid_items_groups_by_column(self):
        """Grid cells group under per-column metric headers in column order."""
        union = {
            "AABAJ124": "WEIGHTED AVERAGE PROBABILITY OF DEFAULT - CORPORATE (DERIVED)",
            "AABBJ124": "BALANCE SHEET AMOUNT - CORPORATE (DERIVED)",
            "AABBJ125": "BALANCE SHEET AMOUNT - BANK (DERIVED)",
            "AABGJ150": "RISK WEIGHTED ASSETS - SUM",
        }
        items = _build_grid_items(union, "Schedule B")
        headers = [i["caption"] for i in items if i["is_header"]]
        assert headers == [
            "Weighted Average Probability of Default",
            "Balance Sheet Amount",
        ]
        # AABGJ150 is a guide-enumerated tail code, excluded from the grid.
        assert all(i["mdrm"] != "AABGJ150" for i in items)
        members = [i for i in items if not i["is_header"]]
        assert all(i["level"] == 2 and i["schedule"] == "B" for i in members)
        assert [i["mdrm"] for i in members] == ["AABAJ124", "AABBJ124", "AABBJ125"]


class TestDropOrphanHeaders:
    """Coverage for the header pruning after union-filtering."""

    def test_drops_header_with_no_value_descendant(self):
        """A header with no deeper value item before its peer is dropped."""
        items = [
            {"caption": "Kept", "level": 1, "is_header": True},
            {"caption": "Item", "level": 2, "is_header": False, "mdrm": "AAABP742"},
            {"caption": "Orphan", "level": 1, "is_header": True},
            {"caption": "Peer", "level": 1, "is_header": True},
            {"caption": "Item2", "level": 2, "is_header": False, "mdrm": "AAAB3247"},
        ]
        result = _drop_orphan_headers(items)
        captions = [i["caption"] for i in result]
        assert "Orphan" not in captions
        assert {"Kept", "Peer"} <= set(captions)


class TestReconcile:
    """Coverage for reconciling the guide enumeration against the CSV union."""

    def _guide(self):
        """A minimal guide enumeration spanning cover, Schedule A and B."""
        return [
            {
                "schedule": "S",
                "schedule_name": "Operational Risk",
                "line": None,
                "caption": "Cover Page Legal Entity Identifier 0 or exactly 20",
                "mdrm": "AAXX9224",
                "columns": ["AAXX9224"],
                "level": 1,
                "is_header": False,
            },
            {
                "schedule": "S",
                "schedule_name": "Operational Risk",
                "line": None,
                "caption": "Cover Page Contact Name 72",
                "mdrm": "AAXX8901",
                "columns": ["AAXX8901"],
                "level": 1,
                "is_header": False,
            },
            {
                "schedule": "A",
                "schedule_name": "Capital",
                "line": "1",
                "caption": "Common stock",
                "mdrm": "AAABP742",
                "columns": ["AAABP742"],
                "level": 1,
                "is_header": False,
            },
            {
                "schedule": "A",
                "schedule_name": "Capital",
                "line": "2",
                "caption": "Confidential item",
                "mdrm": "AACAJ005",
                "columns": ["AACAJ005"],
                "level": 1,
                "is_header": False,
            },
            {
                "schedule": "B",
                "schedule_name": "Schedule B",
                "line": "31",
                "caption": "Credit Valuation Adjustments:",
                "mdrm": None,
                "columns": None,
                "level": 1,
                "is_header": True,
            },
            {
                "schedule": "B",
                "schedule_name": "Schedule B",
                "line": "31.a",
                "caption": "31. a. Credit Valuation Adjustments: Simple",
                "mdrm": "AABGP925",
                "columns": ["AABGP925"],
                "level": 2,
                "is_header": False,
            },
            {
                "schedule": "B",
                "schedule_name": "Schedule B",
                "line": "26",
                "caption": "Unsettled transactions",
                "mdrm": "AABBJ147",
                "columns": ["AABBJ147", "AABGJ147"],
                "level": 1,
                "is_header": False,
            },
        ]

    def _union(self):
        """The public union covering the kept guide codes plus a grid cell."""
        return {
            "AAXX9224": "LEGAL ENTITY IDENTIFIER",
            "AAABP742": "COMMON STOCK",
            "AABGP925": "RISK-WEIGHTED ASSETS - CVA: SIMPLE",
            "AABBJ147": "BALANCE SHEET AMOUNT - OTHER ASSETS: UNSETTLED TRANSACTIONS",
            "AABGJ147": "RISK WEIGHTED ASSETS - OTHER ASSETS: UNSETTLED TRANSACTIONS",
            "AABAJ124": "WEIGHTED AVERAGE PROBABILITY OF DEFAULT - CORPORATE (DERIVED)",
        }

    def test_cover_relocated_and_cleaned(self):
        """The filed cover code moves to COVER with a clean caption."""
        result = _reconcile(self._guide(), self._union())
        lei = next(r for r in result if r["mdrm"] == "AAXX9224")
        assert lei["schedule"] == "COVER"
        assert lei["schedule_name"] == "Cover Page"
        assert lei["caption"] == "Legal Entity Identifier"

    def test_unfiled_cover_and_confidential_dropped(self):
        """An unfiled cover code and a confidential value code are dropped."""
        result = _reconcile(self._guide(), self._union())
        codes = {r["mdrm"] for r in result if not r["is_header"]}
        assert "AAXX8901" not in codes
        assert "AACAJ005" not in codes

    def test_redundant_number_prefix_stripped(self):
        """A ``31. a.`` caption prefix is stripped, the line reference carrying it."""
        result = _reconcile(self._guide(), self._union())
        cva = next(r for r in result if r["mdrm"] == "AABGP925")
        assert cva["caption"] == "Credit Valuation Adjustments: Simple"

    def test_two_column_guide_row_flows_through_grid(self):
        """A two-column guide row is dropped; both cells come from the grid."""
        result = _reconcile(self._guide(), self._union())
        members = [r for r in result if not r["is_header"]]
        codes = [r["mdrm"] for r in members]
        # One item per filed cell: both the Balance Sheet and RWA columns appear.
        assert codes.count("AABBJ147") == 1
        assert codes.count("AABGJ147") == 1
        # Each carries only its own code, so the model renders both values.
        unsettled = [r for r in members if r["mdrm"] in ("AABBJ147", "AABGJ147")]
        assert all(r["columns"] == [r["mdrm"]] for r in unsettled)

    def test_grid_inserted_before_schedule_b_body(self):
        """The recovered grid precedes the guide's Schedule B body rows."""
        result = _reconcile(self._guide(), self._union())
        codes = [r["mdrm"] for r in result if not r["is_header"]]
        assert codes.index("AABAJ124") < codes.index("AABGP925")

    def test_only_union_codes_survive(self):
        """Every surviving value item's code is in the public union."""
        union = self._union()
        result = _reconcile(self._guide(), union)
        for record in result:
            if not record["is_header"]:
                assert record["mdrm"] in union


class TestParseStructure:
    """Coverage for the reconciled public structure from PDF plus CSVs."""

    def test_parse_structure_reconciles(self, monkeypatch):
        """Only filed codes survive and the cover block lands under COVER."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        csv_text = _csv(
            [
                ("AAABP742", "COMMON STOCK", "100"),
                ("AAIIJ035", "CORPORATE EXPOSURES", "200"),
            ]
        )
        records = parse_structure(b"%PDF-1.7", [csv_text])
        codes = {r["mdrm"] for r in records if not r["is_header"]}
        assert codes == {"AAABP742", "AAIIJ035"}

    def test_parse_structure_fetches_csvs_when_omitted(self, monkeypatch):
        """Without CSVs, the live sampled-filer CSVs are fetched."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        csv_text = _csv([("AAABP742", "COMMON STOCK", "100")])
        monkeypatch.setattr(
            ffiec101_structure, "_fetch_validation_csv", lambda rssd: csv_text
        )
        records = parse_structure(b"%PDF-1.7")
        assert any(r["mdrm"] == "AAABP742" for r in records)


class TestLatestQuarterEnd:
    """Coverage for the validation-period helper."""

    def test_returns_recent_completed_quarter(self):
        """The helper returns an eight-digit quarter-end date."""
        value = _latest_quarter_end()
        assert len(value) == 8 and value.isdigit()
        assert value.endswith(("0331", "0630", "0930", "1231"))


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def _csv_paths(self, tmp_path):
        """Write a synthetic sampled-filer CSV and return its path list."""
        csv_text = _csv(
            [
                ("AAABP742", "COMMON STOCK", "100"),
                ("AAIIJ035", "CORPORATE EXPOSURES", "200"),
            ]
        )
        path = tmp_path / "filer.csv"
        path.write_text(csv_text, encoding="utf-8")
        return [str(path)]

    def test_generate_from_local_pdf_and_csv(self, monkeypatch, tmp_path):
        """``generate`` reads local PDF and CSV paths and summarizes schedules."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        payload = generate(str(pdf), self._csv_paths(tmp_path))
        assert payload["item_count"] == len(payload["items"])
        assert payload["schedule_count"] == len(payload["schedules"])
        assert {s["schedule"] for s in payload["schedules"]} >= {"A", "B"}

    def test_generate_fetches_when_no_path(self, monkeypatch):
        """Without paths, ``generate`` downloads the PDF and fetches the CSVs."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        monkeypatch.setattr(ffiec101_structure, "_fetch_pdf_bytes", lambda: b"%PDF-1.7")
        monkeypatch.setattr(
            ffiec101_structure,
            "_fetch_validation_csv",
            lambda rssd: _csv([("AAABP742", "COMMON STOCK", "100")]),
        )
        payload = generate()
        assert payload["source"] == ffiec101_structure.USER_GUIDE_URL

    def test_fetch_pdf_bytes(self, monkeypatch):
        """``_fetch_pdf_bytes`` returns the response body and raises for status."""
        import requests

        class _Resp:
            content = b"%PDF-1.7 body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
        assert ffiec101_structure._fetch_pdf_bytes() == b"%PDF-1.7 body"

    def test_fetch_validation_csv(self, monkeypatch):
        """``_fetch_validation_csv`` decodes the per-institution CSV bytes."""
        from openbb_federal_reserve.utils import ffiec

        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: b"ItemName,x,y")
        assert ffiec101_structure._fetch_validation_csv("852218") == "ItemName,x,y"

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        target = tmp_path / "ffiec101" / "structure.json"
        monkeypatch.setattr(ffiec101_structure, "ASSET_PATH", target)
        path = write_asset(str(pdf), self._csv_paths(tmp_path))
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a summary."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        target = tmp_path / "ffiec101" / "structure.json"
        monkeypatch.setattr(ffiec101_structure, "ASSET_PATH", target)
        csv_path = self._csv_paths(tmp_path)[0]
        monkeypatch.setattr(
            "sys.argv",
            ["ffiec101_structure", "--pdf", str(pdf), "--csv", csv_path],
        )
        ffiec101_structure._main()
        out = capsys.readouterr().out
        assert "schedules" in out and "items" in out
