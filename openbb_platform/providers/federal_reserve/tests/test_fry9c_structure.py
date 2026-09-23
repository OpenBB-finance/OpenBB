"""Tests for the FR Y-9C report structure generator."""

import json

import pytest

from openbb_federal_reserve.utils import fry9c_structure, report_structure
from openbb_federal_reserve.utils.fry9c_structure import (
    _clean_caption,
    _is_codes_only,
    _is_noise,
    _is_schedule_banner,
    _level_from_caption,
    _level_from_reference,
    _opens_wrapped_item,
    _pdf_lines,
    _split_reference,
    generate,
    parse_structure,
    write_asset,
)

# A synthetic appendix that exercises every parsing branch: the cover-page
# contact block, a banner-introduced schedule, referenced line items at several
# indent depths, a wrapped item whose MDRM lands on the next physical line, a
# detached HC-R column row, an itemization free-text/amount pair, a code-less
# section header, and the noise and boundary lines bracketing the form.
_APPENDIX_LINES = [
    "Appendix A",
    "FR Y-9C Report Detailed Field Specifications",
    "   ",
    "Report Form",
    "Line Number",
    "8-character mdrm reference",
    "42",
    "-",
    "Column A",
    "TEXT Name of Bank Holding Company TEXT9010",
    "INTEGER Reporting Period RSSD9999",
    "1. Interest income TEXT BHCK4107",
    "2. Interest expense -",
    "1.a. Loans BHCK4011",
    "1.a.(1) Real estate loans BHCK4435",
    "1.a.(1)(a) Construction BHCK4436",
    "Schedule HC-R Part II Risk-Weighted Assets",
    "Schedule HC-R, item 7 cross reference BHCK0001",
    "Schedule HC - Consolidated Balance Sheet",
    "M.2. Memoranda item PERCENT BHCK1234",
    "M.3. Description of itemized detail TEXT1234",
    "8. - BHCK0000",
    "A.1 Schedule prefix item BHCK5678",
    "(a) Lettered subsection header:",
    "(1) Numbered subsection header:",
    "b. Lowercase subsection:",
    "5. Wrapped caption with no code yet",
    "continuing onto a second physical line",
    "BHCK9999",
    "6. Risk weights grid Column A Column B:",
    "BHCKA001 BHCKA002 BHCKA003",
    "7. Itemized other assets - describe",
    "TEXT Description of other assets TEXT4598",
    "7. Itemized other assets amount BHCK4599",
    "FR Y-9C Nonstandard Financial Items and Text Item Character Limits",
    "This trailing Appendix B line must be ignored BHCKZZZZ",
]


def _patch_pages(monkeypatch, lines, *, pages=None):
    """Patch ``read_pdf_pages`` to yield the given synthetic page texts."""
    page_texts = pages if pages is not None else ["\n".join(lines)]
    monkeypatch.setattr(
        report_structure, "read_pdf_pages", lambda _pdf_bytes: list(page_texts)
    )


class TestLineHelpers:
    """Unit coverage for the per-line classifiers and splitters."""

    @pytest.mark.parametrize(
        "line",
        [
            "report form",
            "123",
            "8-character mdrm reference table",
            "-",
        ],
    )
    def test_is_noise_true(self, line):
        """Running heads, page numbers, MDRM banners, and dashes are noise."""
        assert _is_noise(line)

    def test_is_noise_false(self):
        """A real caption is not noise."""
        assert not _is_noise("1. Interest income")

    @pytest.mark.parametrize(
        "reference, level",
        [
            ("1", 1),
            ("1.a", 2),
            ("1.a.(1)", 3),
            ("1.a.(1)(a)", 4),
            ("M.2", 1),
            ("A.1", 1),
        ],
    )
    def test_level_from_reference(self, reference, level):
        """Indent depth follows the reference's nesting."""
        assert _level_from_reference(reference) == level

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
        assert _level_from_caption(caption) == level

    def test_split_reference_match(self):
        """A leading reference is split from its caption."""
        assert _split_reference("1.a. Loans") == ("1.a", "Loans")

    def test_split_reference_no_reference(self):
        """A caption with no leading reference returns ``None``."""
        assert _split_reference("Total assets") == (None, "Total assets")

    def test_clean_caption_strips_type_and_dash(self):
        """Data-type prefixes and trailing filler dashes are removed."""
        assert _clean_caption("TEXT  Other  assets -") == "Other assets"

    def test_is_codes_only(self):
        """A bare MDRM line is codes-only; a captioned line is not."""
        assert _is_codes_only("BHCKA001 BHCKA002")
        assert not _is_codes_only("1. Loans BHCK4011")
        assert not _is_codes_only("No codes here")

    def test_is_schedule_banner(self):
        """Cross references and part/page sub-banners are not schedule banners."""
        pattern = fry9c_structure._SCHEDULE_HEADER

        def banner(line):
            """Match a schedule header line, asserting the pattern matched."""
            match = pattern.match(line)
            assert match is not None
            return _is_schedule_banner(match)

        assert banner("Schedule HC - Balance Sheet")
        assert not banner("Schedule HC-R Part II Grid")
        assert not banner("Schedule HC, item 7 ref")

    def test_opens_wrapped_item(self):
        """A referenced non-colon line opens a wrapped item; a header does not."""
        assert _opens_wrapped_item("5. Wrapped caption with no code yet")
        assert not _opens_wrapped_item("5. Section header:")
        assert not _opens_wrapped_item("Code-less header")


class TestPdfLines:
    """Coverage for the appendix-boundary extraction from PDF pages."""

    def test_extracts_between_banner_and_appendix_b(self, monkeypatch):
        """Lines before the banner and after Appendix B are dropped."""
        _patch_pages(monkeypatch, _APPENDIX_LINES)
        lines = _pdf_lines(b"%PDF-1.7")
        assert "Appendix A" not in lines
        assert lines[0] == "Report Form"
        assert all("Nonstandard" not in line for line in lines)

    def test_returns_all_when_no_appendix_b(self, monkeypatch):
        """When Appendix B never appears, the loop falls through to ``return``."""
        body = [
            "FR Y-9C Report Detailed Field Specifications",
            "1. Interest income BHCK4107",
        ]
        _patch_pages(monkeypatch, body)
        lines = _pdf_lines(b"%PDF-1.7")
        assert lines == ["1. Interest income BHCK4107"]

    def test_handles_empty_page_text(self, monkeypatch):
        """A page with no extractable text contributes no lines."""
        _patch_pages(monkeypatch, [], pages=[""])
        assert _pdf_lines(b"%PDF-1.7") == []


class TestParseStructure:
    """End-to-end parse over the synthetic appendix."""

    def test_cover_then_income_statement(self, monkeypatch):
        """The contact block stays COVER until the first non-cover line flips to HI."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        cover = [r for r in records if r["schedule"] == "COVER"]
        assert cover and cover[0]["caption"] == "Reporting Period"
        income = [r for r in records if r["schedule"] == "HI"]
        assert any(r["caption"].startswith("Interest income") for r in income)

    def test_nested_levels(self, monkeypatch):
        """Referenced items carry the depth implied by their reference."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        by_line = {r["line"]: r for r in records if r["line"]}
        assert by_line["1.a.(1)(a)"]["level"] == 4
        assert by_line["1.a.(1)(a)"]["caption"] == "Construction"

    def test_schedule_banner_switches(self, monkeypatch):
        """A real ``Schedule HC -`` banner changes the active schedule."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        assert any(r["schedule"] == "HC" for r in records)
        memoranda = next(r for r in records if r["line"] == "M.2")
        assert memoranda["schedule"] == "HC"

    def test_part_banner_not_a_schedule(self, monkeypatch):
        """A ``Part II`` sub-banner does not start a new schedule."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        assert not any(r["schedule"] == "HC-R" for r in records)

    def test_wrapped_item_resolves(self, monkeypatch):
        """A caption whose MDRM lands on the next line resolves to one row."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        wrapped = next(r for r in records if r["line"] == "5")
        assert wrapped["mdrm"] == "BHCK9999"
        assert wrapped["caption"].endswith("second physical line")

    def test_detached_columns_attach_to_previous(self, monkeypatch):
        """A bare MDRM row attaches its codes to the preceding grid row."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        grid = next(r for r in records if r["line"] == "6")
        assert grid["columns"] == ["BHCKA001", "BHCKA002", "BHCKA003"]
        assert grid["mdrm"] == "BHCKA001"
        assert grid["is_header"] is False

    def test_itemization_text_dropped_amount_kept(self, monkeypatch):
        """The free-text description half of an itemization pair is dropped."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        amounts = [r for r in records if r["mdrm"] == "BHCK4599"]
        assert amounts and amounts[0]["caption"] == "Itemized other assets amount"
        assert not any(r["mdrm"] == "TEXT4598" for r in records)

    def test_section_header_has_no_mdrm(self, monkeypatch):
        """A code-less colon-terminated line is a header with no MDRM."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        header = by_caption(records, "(a) Lettered subsection header:")
        assert header["is_header"] is True
        assert header["mdrm"] is None
        assert header["level"] == 4

    def test_space_dash_header_emitted_standalone(self, monkeypatch):
        """A code-less ``" -"`` continuation caption becomes its own header row."""
        records = parse_structure_via_lines(monkeypatch, _APPENDIX_LINES)
        header = next(r for r in records if r["line"] == "2")
        assert header["is_header"] is True
        assert header["mdrm"] is None
        assert header["caption"] == "Interest expense"


def parse_structure_via_lines(monkeypatch, lines):
    """Parse a synthetic appendix by patching ``read_pdf_pages``."""
    _patch_pages(monkeypatch, lines)
    return parse_structure(b"%PDF-1.7")


def by_caption(records, caption):
    """Return the first record whose caption matches exactly."""
    return next(r for r in records if r["caption"] == caption)


class TestReconcileHelpers:
    """Unit coverage for the filing-reconciliation helpers."""

    def test_is_admin_item(self):
        """Identity, total, and date-stamp rows are administrative; codes are not."""
        from openbb_federal_reserve.utils.fry9c_structure import _is_admin_item

        assert _is_admin_item("Institution Name")
        assert _is_admin_item("Report Date")
        assert _is_admin_item("DT")
        assert _is_admin_item("DT_0331Q")
        assert not _is_admin_item("BHCK4107")

    def test_caption_from_description(self):
        """An all-caps filing description becomes a clean mixed-case caption."""
        from openbb_federal_reserve.utils.fry9c_structure import (
            _caption_from_description,
        )

        out = _caption_from_description(
            "OTHER UNUSED COMMITMENTS: LOANS (REPORTED IN SCHEDULE HC-D, "
            "ITEMS 6.A.1) (BHC CONSOLIDATED)"
        )
        assert "(BHC CONSOLIDATED)" not in out
        assert "HC-D" in out
        assert "6.a.1" in out
        assert out.startswith("Other Unused Commitments")

    def test_apply_code_repairs(self):
        """Renames, grid replacements, and duplicate drops are applied in place."""
        from openbb_federal_reserve.utils.fry9c_structure import _apply_code_repairs

        items = [
            {"schedule": "HC-Q", "line": "10.a", "columns": ["BHCT3547", "BHCTG512"]},
            {"schedule": "HC-Q", "line": "11", "columns": ["BHCKG521", "BHCKG518"]},
            {"schedule": "HC-D", "line": "M.1.a.(2)", "columns": ["BHCKF632"]},
            {"schedule": "HI", "line": "1", "columns": None},
        ]
        _apply_code_repairs(items)
        assert items[0]["columns"] == ["BHCT3547", "BHCKG512"]
        assert items[1]["columns"] == ["BHCKG521", "BHCKG522"]
        assert items[2]["columns"] == []
        assert items[2]["mdrm"] is None
        assert items[3]["columns"] is None

    def test_insert_text_descriptions(self):
        """A filed itemization description is emitted before its amount row."""
        from openbb_federal_reserve.utils.fry9c_structure import (
            _insert_text_descriptions,
        )

        items = [
            {
                "schedule": "HI",
                "line": "4",
                "caption": "4. Amount",
                "mdrm": "BHCK5351",
                "columns": ["BHCK5351"],
            },
            {
                "schedule": "HI",
                "line": "5",
                "caption": "5. Amount",
                "mdrm": "BHCK5352",
                "columns": ["BHCK5352"],
            },
        ]
        out = _insert_text_descriptions(items, {"TEXT5351"})
        assert [it["mdrm"] for it in out] == ["TEXT5351", "BHCK5351", "BHCK5352"]
        assert out[0]["caption"] == "Description"

    def test_insert_missing_items(self):
        """A filed code the guide omits is inserted after its filed neighbor."""
        from openbb_federal_reserve.utils.fry9c_structure import _insert_missing_items

        items = [{"schedule": "HC-D", "line": "M.1.a", "columns": ["BHCKHT66"]}]
        _insert_missing_items(
            items,
            {"BHCKHT67"},
            {"BHCKHT67": "ALL OTHER LOANS (BHC CONSOLIDATED)"},
            ["BHCKHT66", "BHCKHT67"],
        )
        assert items[1]["mdrm"] == "BHCKHT67"
        assert items[1]["schedule"] == "HC-D"
        assert items[1]["caption"] == "All Other Loans"

    def test_insert_missing_items_skips_unfiled_or_anchorless(self):
        """An unfiled or unanchored omitted code is not inserted."""
        from openbb_federal_reserve.utils.fry9c_structure import _insert_missing_items

        items = [{"schedule": "HC-D", "line": "M.1.a", "columns": ["BHCKHT66"]}]
        _insert_missing_items(items, set(), {}, [])
        assert len(items) == 1
        # Filed but no prior neighbor present in the structure: no anchor found.
        _insert_missing_items(items, {"BHCKHT67"}, {}, ["BHCKHT67"])
        assert len(items) == 1

    def test_insert_guide_text_block(self):
        """The auditor text block is inserted before the named schedule's first item."""
        from openbb_federal_reserve.utils.fry9c_structure import (
            _insert_guide_text_block,
        )

        items = [
            {"schedule": "HC", "line": "1", "columns": ["BHCK2170"]},
            {"schedule": "HC-B", "line": "1", "columns": ["BHCK0211"]},
        ]
        _insert_guide_text_block(items)
        auditor = [it for it in items if it["schedule"] == "HC-M"]
        assert auditor and auditor[0]["mdrm"] == "TEXTC703"
        # Inserted ahead of the first HC-B item.
        assert items[items.index(auditor[0]) + len(auditor)]["schedule"] == "HC-B"

    def test_insert_guide_text_block_no_anchor(self):
        """With no target schedule present, the block is not inserted."""
        from openbb_federal_reserve.utils.fry9c_structure import (
            _insert_guide_text_block,
        )

        items = [{"schedule": "HC", "line": "1", "columns": ["BHCK2170"]}]
        _insert_guide_text_block(items)
        assert len(items) == 1

    def test_prune_to_filed(self):
        """Unfiled columns and rows drop; empty headers drop; filed rows stay."""
        from openbb_federal_reserve.utils.fry9c_structure import _prune_to_filed

        items = [
            {"schedule": "HI", "caption": "h", "level": 1, "is_header": True},
            {
                "schedule": "HI",
                "caption": "kept",
                "level": 2,
                "is_header": False,
                "columns": ["BHCK4107", "BHCK9999"],
            },
            {"schedule": "HI", "caption": "no codes", "level": 1, "is_header": False},
            {
                "schedule": "HI",
                "caption": "empty header",
                "level": 1,
                "is_header": True,
            },
            {
                "schedule": "HI",
                "caption": "dropped",
                "level": 2,
                "is_header": False,
                "columns": ["BHCK9999"],
            },
        ]
        out = _prune_to_filed(items, {"BHCK4107"})
        captions = [it["caption"] for it in out]
        # "empty header" is dropped: its only descendant ("dropped") was pruned,
        # leaving no value item before the list ends.
        assert captions == ["h", "kept", "no codes"]
        kept = next(it for it in out if it["caption"] == "kept")
        assert kept["columns"] == ["BHCK4107"]
        assert kept["mdrm"] == "BHCK4107"

    def test_collect_filed_set(self, monkeypatch):
        """The union excludes admin rows and blanks; first filer sets the order."""
        from openbb_federal_reserve.utils import structure_common
        from openbb_federal_reserve.utils.fry9c_structure import collect_filed_set

        payloads = {
            "1": (
                "ItemName,Description,Value\n"
                "Institution Name,,JPM\n"
                "\n"
                "BHCK4107,Interest,100\n"
                "BHCK4011,Blank,\n"
                "BHCK4435,Loans,5\n"
            ),
            "2": (
                "ItemName,Description,Value\n"
                "Report Date,,2025\n"
                "BHCK4107,Interest,200\n"
                "BHCK9999,Other,9\n"
            ),
        }
        monkeypatch.setattr(
            structure_common,
            "fetch_report_csv",
            lambda _rpt, rssd, _dt: payloads[str(rssd)],
        )
        filed, descriptions, order = collect_filed_set(("1", "2"), "20251231")
        assert filed == {"BHCK4107", "BHCK4435", "BHCK9999"}
        assert "BHCK4011" not in filed
        assert descriptions["BHCK4107"] == "Interest"
        assert order == ["BHCK4107", "BHCK4435"]

    def test_reconcile_end_to_end(self, monkeypatch):
        """``reconcile`` repairs, inserts, and prunes against the filed set."""
        from openbb_federal_reserve.utils.fry9c_structure import reconcile

        items = [
            {
                "schedule": "HI",
                "line": "1",
                "caption": "1. Interest income",
                "mdrm": "BHCK4107",
                "columns": ["BHCK4107"],
                "level": 1,
                "is_header": False,
            },
            {
                "schedule": "HC-Q",
                "line": "10.a",
                "caption": "a. Derivative liabilities",
                "mdrm": "BHCT3547",
                "columns": ["BHCT3547", "BHCTG512"],
                "level": 2,
                "is_header": False,
            },
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.fry9c_structure.collect_filed_set",
            lambda *_a, **_k: ({"BHCK4107", "BHCT3547", "BHCKG512"}, {}, ["BHCK4107"]),
        )
        out = reconcile(items, date_str="20251231")
        derivative = next(it for it in out if it["line"] == "10.a")
        assert derivative["columns"] == ["BHCT3547", "BHCKG512"]
        assert all(it["mdrm"] != "BHCTG512" for it in out)


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def test_generate_from_local_pdf(self, monkeypatch, tmp_path):
        """``generate`` reads a local PDF path and summarizes the schedules."""
        _patch_pages(monkeypatch, _APPENDIX_LINES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        payload = generate(str(pdf), offline=True)
        assert payload["item_count"] == len(payload["items"])
        assert payload["schedule_count"] == len(payload["schedules"])
        assert {s["schedule"] for s in payload["schedules"]} >= {"COVER", "HI", "HC"}

    def test_generate_reconciles_against_filings(self, monkeypatch, tmp_path):
        """``generate`` reconciles the parsed layout against the filed item set."""
        _patch_pages(monkeypatch, _APPENDIX_LINES)
        # Only ``BHCK4107`` and ``BHCK4599`` are "filed"; every other parsed code
        # is pruned, and the missing-item insertions whose code is not filed are
        # skipped.
        monkeypatch.setattr(
            fry9c_structure,
            "collect_filed_set",
            lambda *_a, **_k: ({"BHCK4107", "BHCK4599"}, {}, ["BHCK4107", "BHCK4599"]),
        )
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        payload = generate(str(pdf))
        codes = {item["mdrm"] for item in payload["items"] if item["mdrm"]}
        assert codes == {"BHCK4107", "BHCK4599"}

    def test_generate_fetches_when_no_path(self, monkeypatch):
        """Without a path, ``generate`` downloads the canonical PDF."""
        monkeypatch.setattr(fry9c_structure, "_fetch_pdf_bytes", lambda: b"%PDF-1.7")
        _patch_pages(monkeypatch, _APPENDIX_LINES)
        payload = generate(offline=True)
        assert payload["source"] == fry9c_structure.USER_GUIDE_URL

    def test_fetch_pdf_bytes(self, monkeypatch):
        """``_fetch_pdf_bytes`` returns the response body and raises for status."""
        import requests

        class _Resp:
            content = b"%PDF-1.7 body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
        assert fry9c_structure._fetch_pdf_bytes() == b"%PDF-1.7 body"

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        _patch_pages(monkeypatch, _APPENDIX_LINES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        target = tmp_path / "fry9c" / "structure.json"
        monkeypatch.setattr(fry9c_structure, "ASSET_PATH", target)
        path = write_asset(str(pdf), offline=True)
        assert path == target
        payload = json.loads(target.read_text())
        assert payload["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a summary."""
        _patch_pages(monkeypatch, _APPENDIX_LINES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        target = tmp_path / "fry9c" / "structure.json"
        monkeypatch.setattr(fry9c_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv", ["fry9c_structure", "--pdf", str(pdf), "--offline"]
        )
        fry9c_structure._main()
        out = capsys.readouterr().out
        assert "schedules" in out and "items" in out
