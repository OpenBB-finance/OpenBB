"""Tests for the FR Y-15 report structure generator."""

import json
from types import SimpleNamespace

from openbb_federal_reserve.utils import fry15_structure
from openbb_federal_reserve.utils.fry15_structure import (
    _clean_caption,
    _csv_descriptions,
    _form_subheaders,
    _level_from_line,
    _merge_descriptions,
    _parse_calc_table,
    _parse_line_table,
    _prune_empty_headers,
    _schedule_titles,
    _split_caption_header,
    _split_descriptor,
    _value_codes,
    build_items,
    generate,
    validate,
    write_asset,
)

# A synthetic FR Y-15 transfer user-guide PDF. Page one carries the *Line
# Identifiers* table: a domestic-HC (RISK) row, an IHC (RISI) and FBO (RISO)
# column row that get the bracketed-column suffix, a cover-page row, a narrative
# row, and a descriptor that wraps across two physical lines (the L-prefixed
# identifier terminates the row). Page two carries the *Items NOT to Include*
# calculated-MDRM table.
_GUIDE_PAGES = [
    [
        "RISKM337 Schedule A, 1.a. LRISKM337 14",
        "RISKM339 Schedule A, 1.b. LRISKM339 14",
        "RISIK100 Schedule H, 2.a. LRISIK100 14",
        "RISOK200 Schedule I, 2.a. LRISOK200 14",
        "RSSD9017 Cover Page, Name of CFO LRSSD9017 72",
        "RISKM900 Optional Narrative Statement LRISKM900 1",
        "RISKN100 Schedule N, Part I, 2.b LRISKN100 14",
        "RISKW822 Schedule A,",
        "1.c.",
        "LRISKW822 14",
    ],
    [
        "RISKM337 FR Y-9C 3/31/2013 12/31/9999",
        "RISKD200 FFIEC 101 6/30/2014 12/31/9999",
    ],
]

# A synthetic blank-form PDF: the schedule-title headings (one "(continued)"
# repeat that must be ignored, and the "Short-T erm" extraction artifact that
# must be repaired) and the numbered/lettered colon sub-headers whose whitelist
# confirms which CSV-description prefixes are genuine headers.
_FORM_PAGES = [
    [
        "Schedule A—Size Indicator",
        "Schedule C—Continued Substitutability Indicators",
        "Schedule B—Interconnectedness Indicators",
        "Schedule G—Short-T erm Wholesale Funding Indicator",
        "Schedule H—FBO Size Indicator",
        "Schedule I—FBO Interconnectedness Indicators",
        "Schedule N—FBO Short-Term Wholesale Funding Indicator",
        "1. Derivative exposures:",
        "a. Secured financing transactions: .... 5",
    ]
]

# Per-institution caption CSVs. The first (domestic HC) supplies RISK/RSSD
# captions and is the validation filer; the IHC and FBO filers supply the
# RISI/RISO captions a domestic filing omits. The merge keeps the first
# non-empty caption, so the duplicate RISKM337 caption on the second filer loses.
_CSV_HC = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,VALIDATION BANK",
        "ID_RSSD,Reporting entity identifier,1039502",
        "RISK2170,TOTAL ASSETS,5000",
        "RISKM337,Derivative exposures: Current exposure of derivative contracts,100",
        "RISKM339,Gross-up for derivatives collateral,200",
        "RISKW822,Securities financing transactions,300",
        "RISKN100,Part I reported line,700",
        "RISKC447,Is confidential treatment requested? (0=No 1=Yes),0",
        "RSSD9017,Name of CFO,Jane Doe",
        "RISKD200,Total derived exposures,900",
    ]
)
_CSV_IHC = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,IHC BANK",
        "RISKM337,DUPLICATE CAPTION THAT LOSES THE MERGE,111",
        "RISIK100,Intra-financial system assets,400",
    ]
)
_CSV_FBO = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,FBO BANK",
        "RISOK200,Intra-financial system liabilities,500",
    ]
)


def _fake_reader(pages):
    """Build a stand-in ``PdfReader`` whose pages yield the given joined text."""
    return SimpleNamespace(
        pages=[
            SimpleNamespace(extract_text=lambda text="\n".join(page): text)
            for page in pages
        ]
    )


def _patch_readers(monkeypatch, guide_pages, form_pages):
    """Patch ``PdfReader`` to dispatch on the stream's leading bytes.

    ``build_items`` reads the guide once and the form twice (titles, then
    sub-headers), so the reader is selected by the synthetic stream marker rather
    than by call order.
    """
    import pypdf

    def _reader(stream):
        """Return the guide or form fake reader by the stream's marker bytes."""
        marker = stream.getvalue() if hasattr(stream, "getvalue") else stream
        pages = form_pages if b"form" in bytes(marker) else guide_pages
        return _fake_reader(pages)

    monkeypatch.setattr(pypdf, "PdfReader", _reader)


class TestParsers:
    """Unit coverage for the table and source parsers."""

    def test_parse_line_table_wraps(self):
        """Every line row parses; a wrapped descriptor resolves to one row."""
        rows = _parse_line_table(_GUIDE_PAGES)
        mdrms = [r["mdrm"] for r in rows]
        assert "RISKM337" in mdrms
        wrapped = next(r for r in rows if r["mdrm"] == "RISKW822")
        assert wrapped["descriptor"] == "Schedule A, 1.c."

    def test_parse_calc_table(self):
        """The calculated-items table yields each MDRM and its source series."""
        rows = _parse_calc_table(_GUIDE_PAGES)
        assert {r["mdrm"] for r in rows} == {"RISKM337", "RISKD200"}
        assert next(r for r in rows if r["mdrm"] == "RISKM337")["source"] == "FR Y-9C"

    def test_schedule_titles(self, monkeypatch):
        """Schedule titles parse, dropping ``(continued)`` and fixing artifacts."""
        import pypdf

        monkeypatch.setattr(
            pypdf, "PdfReader", lambda _stream: _fake_reader(_FORM_PAGES)
        )
        titles = _schedule_titles(b"%PDF")
        assert titles["A"] == "Size Indicator"
        assert titles["G"] == "Short-Term Wholesale Funding Indicator"

    def test_form_subheaders(self, monkeypatch):
        """Colon-terminated numbered/lettered captions become the whitelist."""
        import pypdf

        monkeypatch.setattr(
            pypdf, "PdfReader", lambda _stream: _fake_reader(_FORM_PAGES)
        )
        subheaders = _form_subheaders(b"%PDF")
        assert subheaders["derivative exposures"] == "Derivative exposures"
        assert subheaders["secured financing transactions"] == (
            "Secured financing transactions"
        )

    def test_csv_descriptions(self):
        """Only MDRM-keyed rows contribute captions."""
        descriptions = _csv_descriptions(_CSV_HC.encode("utf-8"))
        assert descriptions["RISKM339"] == "Gross-up for derivatives collateral"
        assert "ID_RSSD" not in descriptions

    def test_merge_descriptions_first_wins(self):
        """The first non-empty caption wins across multiple filers."""
        merged = _merge_descriptions(
            [_CSV_HC.encode("utf-8"), _CSV_IHC.encode("utf-8")]
        )
        assert merged["RISKM337"].startswith("Derivative exposures")
        assert merged["RISIK100"] == "Intra-financial system assets"


class TestValueCodes:
    """Unit coverage for the value-bearing-code extraction and cleaners."""

    def test_value_codes_excludes_identity_and_short_rows(self):
        """Identity item names, total-asset rows, ``DT`` and short rows drop out."""
        csv_text = "\n".join(
            [
                "ItemName,Description,Value",
                "Institution Name,,A BANK",
                "ID_RSSD,Reporting entity identifier,1039502",
                "RISK2170,TOTAL ASSETS,5000",
                "DTBL0001,Reporting period date,20260331",
                "TRUNCATED ROW",
                "RISKM337,Current exposure,100",
            ]
        )
        codes = _value_codes(csv_text.encode("utf-8"))
        assert codes == {"RISKM337"}

    def test_clean_caption_strips_glued_capital(self):
        """A stray leading capital glued to a capitalised word is removed."""
        assert _clean_caption("DOther off-balance sheet exposures: x") == (
            "Other off-balance sheet exposures: x"
        )

    def test_clean_caption_keeps_normal_text(self):
        """An all-caps or normally-capitalised caption is left intact."""
        assert _clean_caption("COMMERCIAL PAPER") == "COMMERCIAL PAPER"
        assert _clean_caption("Derivative exposures") == "Derivative exposures"

    def test_prune_empty_headers_drops_childless(self):
        """A header whose only follower is a sibling header is dropped.

        The first header is bounded by a sibling header at the same level before
        any deeper value-item, and the second header is bounded by the end of its
        schedule, so both are childless and removed.
        """
        items = [
            {"schedule": "A", "level": 1, "is_header": True, "caption": "H1"},
            {"schedule": "A", "level": 1, "is_header": True, "caption": "H2"},
            {"schedule": "B", "level": 1, "is_header": True, "caption": "H3"},
        ]
        assert _prune_empty_headers(items) == []


class TestSplitters:
    """Unit coverage for the descriptor, level, and header splitters."""

    def test_split_descriptor(self):
        """Schedules, parts, cover page and narrative descriptors split cleanly."""
        assert _split_descriptor("Schedule A, 1.a.") == ("A", None, "1.a")
        assert _split_descriptor("Schedule N, Part II, 3.a") == ("N", "II", "3.a")
        assert _split_descriptor("Cover Page, Name of CFO") == (
            "Cover Page",
            None,
            "Name of CFO",
        )
        assert _split_descriptor("Unparseable descriptor") == (
            "Unparseable descriptor",
            None,
            None,
        )

    def test_level_from_line(self):
        """Indent depth follows the line reference nesting."""
        assert _level_from_line(None) == 1
        assert _level_from_line("1.a") == 2
        assert _level_from_line("1.(1)") == 2
        assert _level_from_line("M.2.(a)") == 2

    def test_split_caption_header(self):
        """A whitelisted ``Header: leaf`` splits; others keep the colon intact."""
        subheaders = {"derivative exposures": "Derivative exposures"}
        assert _split_caption_header(
            "Derivative exposures: Current exposure", subheaders
        ) == ("Derivative exposures", "Current exposure")
        assert _split_caption_header("Unlisted prefix: leaf", subheaders) == (
            None,
            "Unlisted prefix: leaf",
        )
        assert _split_caption_header("No colon", subheaders) == (None, "No colon")


class TestBuildItems:
    """End-to-end assembly over the synthetic guide, form, and CSVs."""

    def _build(self, monkeypatch):
        """Build items by patching the guide and form ``PdfReader`` calls."""
        _patch_readers(monkeypatch, _GUIDE_PAGES, _FORM_PAGES)
        return build_items(
            b"%PDF-guide",
            b"%PDF-form",
            [
                _CSV_HC.encode("utf-8"),
                _CSV_IHC.encode("utf-8"),
                _CSV_FBO.encode("utf-8"),
            ],
        )

    def test_schedule_codes_and_titles(self, monkeypatch):
        """Reported schedule, cover and calculated codes carry their titles."""
        items, titles = self._build(monkeypatch)
        by_schedule = {item["schedule"] for item in items}
        assert {"A", "H", "I", "COVER", "CALCULATED"} <= by_schedule
        cover = next(item for item in items if item["schedule"] == "COVER")
        assert cover["schedule_name"] == "Cover Page"

    def test_unreported_codes_are_dropped(self, monkeypatch):
        """A line-table code no sampled filer reports is excluded as permanent-empty.

        ``RISKM900`` (Optional Narrative Statement) is in the guide line table but
        absent from every sampled CSV, so it never becomes a structure value-item
        and its schedule does not appear.
        """
        items, _ = self._build(monkeypatch)
        codes = {item["mdrm"] for item in items if item["mdrm"]}
        assert "RISKM900" not in codes
        assert "NARRATIVE" not in {item["schedule"] for item in items}

    def test_total_assets_description_excluded(self, monkeypatch):
        """An MDRM row described as ``TOTAL ASSETS`` is not a value-item."""
        items, _ = self._build(monkeypatch)
        assert "RISK2170" not in {item["mdrm"] for item in items if item["mdrm"]}

    def test_csv_only_code_appended_to_cover(self, monkeypatch):
        """A reported code absent from the guide tables is filed under COVER."""
        items, _ = self._build(monkeypatch)
        confidential = next(item for item in items if item["mdrm"] == "RISKC447")
        assert confidential["schedule"] == "COVER"
        assert confidential["is_header"] is False

    def test_narrative_schedule_when_reported(self, monkeypatch):
        """The narrative line survives when a sampled filer reports its code."""
        _patch_readers(monkeypatch, _GUIDE_PAGES, _FORM_PAGES)
        narrative_csv = "\n".join(
            [
                "ItemName,Description,Value",
                "Institution Name,,NARRATIVE BANK",
                "RISKM900,Optional narrative statement,Some text",
            ]
        )
        items, _ = build_items(
            b"%PDF-guide", b"%PDF-form", [narrative_csv.encode("utf-8")]
        )
        narrative = next(item for item in items if item["mdrm"] == "RISKM900")
        assert narrative["schedule"] == "NARRATIVE"

    def test_part_schedule_code_and_name(self, monkeypatch):
        """A ``Part`` descriptor yields a ``N-I`` schedule code and a part suffix."""
        items, _ = self._build(monkeypatch)
        part = next(item for item in items if item["mdrm"] == "RISKN100")
        assert part["schedule"] == "N-I"
        assert part["schedule_name"].endswith("- Part I")

    def test_column_suffix_for_ihc_and_fbo(self, monkeypatch):
        """The IHC and FBO column MDRMs get a bracketed-column caption suffix."""
        items, _ = self._build(monkeypatch)
        ihc = next(item for item in items if item["mdrm"] == "RISIK100")
        assert ihc["caption"].endswith("(IHC)")
        fbo = next(item for item in items if item["mdrm"] == "RISOK200")
        assert fbo["caption"].endswith("(FBO)")

    def test_subheader_emitted_once(self, monkeypatch):
        """A whitelisted caption prefix is surfaced as a single header item."""
        items, _ = self._build(monkeypatch)
        headers = [
            item
            for item in items
            if item["is_header"] and item["caption"] == "Derivative exposures"
        ]
        assert len(headers) == 1
        leaf = next(item for item in items if item["mdrm"] == "RISKM337")
        assert leaf["caption"] == "Current exposure of derivative contracts"
        assert leaf["is_header"] is False

    def test_calculated_items_with_source(self, monkeypatch):
        """Calculated MDRMs not in the line table carry their source series."""
        items, _ = self._build(monkeypatch)
        calc = next(item for item in items if item["mdrm"] == "RISKD200")
        assert calc["schedule"] == "CALCULATED"
        assert calc["source"] == "FFIEC 101"

    def test_calculated_skips_already_seen(self, monkeypatch):
        """A calculated MDRM already emitted from the line table is not repeated."""
        items, _ = self._build(monkeypatch)
        risk_m337 = [item for item in items if item["mdrm"] == "RISKM337"]
        assert len(risk_m337) == 1
        assert risk_m337[0]["schedule"] == "A"


class TestValidate:
    """Coverage for the MDRM-coverage validation summary."""

    def test_validate_counts_and_missing(self, monkeypatch):
        """Validation reports full coverage and no permanently-empty items."""
        items, _ = TestBuildItems()._build(monkeypatch)
        report = validate(
            items,
            [
                _CSV_HC.encode("utf-8"),
                _CSV_IHC.encode("utf-8"),
                _CSV_FBO.encode("utf-8"),
            ],
        )
        assert report["missing"] == []
        assert report["permanent_empty"] == []
        assert report["coverage"] == 100.0
        assert report["covered_count"] == report["csv_mdrm_count"]

    def test_validate_empty_csv(self):
        """An empty sample yields zero coverage rather than dividing by zero."""
        report = validate([], [b"ItemName,Description,Value\n"])
        assert report["coverage"] == 0.0
        assert report["csv_mdrm_count"] == 0
        assert report["permanent_empty"] == []


class TestFetchBytes:
    """Coverage for the source-download dispatcher."""

    def test_public_pdf_via_requests(self, monkeypatch):
        """A non-FFIEC URL is fetched with plain ``requests``."""
        import requests

        class _Resp:
            content = b"%PDF body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
        assert fry15_structure._fetch_bytes(fry15_structure.GUIDE_URL) == b"%PDF body"

    def test_ffiec_csv_via_impersonating_session(self, monkeypatch):
        """An FFIEC URL is fetched through the browser-impersonating session."""
        from openbb_federal_reserve.utils import curl_session

        class _Resp:
            content = b"csv body"

            def raise_for_status(self):
                """No-op success."""

        class _Session:
            def get(self, *a, **k):
                """Return the canned response for both warmup and fetch."""
                return _Resp()

        def _get_session(_key, warmup):
            """Build the session and run the warmup callback against it."""
            session = _Session()
            warmup(session)
            return session

        monkeypatch.setattr(curl_session, "get_session", _get_session)
        url = fry15_structure.CSV_URL.format(rssd=1039502, date="20250331")
        assert fry15_structure._fetch_bytes(url) == b"csv body"

    def test_lookalike_host_uses_ordinary_client(self, monkeypatch):
        """A host with ``ffiec.gov`` only as a substring is not trusted as FFIEC.

        Guards the URL-host check against incomplete substring matching: a
        look-alike host must fall to the ordinary client, never the
        browser-impersonating FFIEC session.
        """
        import requests

        from openbb_federal_reserve.utils import curl_session

        class _Resp:
            content = b"body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())

        def _forbidden(*a, **k):
            """Fail if the FFIEC session is used for a look-alike host."""
            raise AssertionError("look-alike host must not use the FFIEC session")

        monkeypatch.setattr(curl_session, "get_session", _forbidden)
        assert fry15_structure._fetch_bytes("https://ffiec.gov.evil.com/x") == b"body"


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def test_generate_from_local_files(self, monkeypatch, tmp_path):
        """``generate`` reads local PDF and CSV paths and summarizes schedules."""
        _patch_readers(monkeypatch, _GUIDE_PAGES, _FORM_PAGES)
        guide = tmp_path / "guide.pdf"
        guide.write_bytes(b"%PDF-guide")
        form = tmp_path / "form.pdf"
        form.write_bytes(b"%PDF-form")
        hc = tmp_path / "hc.csv"
        hc.write_text(_CSV_HC, encoding="utf-8")
        ihc = tmp_path / "ihc.csv"
        ihc.write_text(_CSV_IHC, encoding="utf-8")
        payload = generate(str(guide), str(form), [str(hc), str(ihc)])
        assert payload["item_count"] == len(payload["items"])
        assert payload["schedule_count"] == len(payload["schedules"])
        assert payload["validation"]["csv_mdrm_count"] == 8
        assert payload["validation"]["coverage"] == 100.0
        assert payload["validation"]["permanent_empty"] == []

    def test_generate_fetches_when_no_paths(self, monkeypatch):
        """Without paths, ``generate`` downloads the guide, form, and CSVs."""
        _patch_readers(monkeypatch, _GUIDE_PAGES, _FORM_PAGES)
        csv_cycle = iter(
            [
                _CSV_HC.encode("utf-8"),
                _CSV_IHC.encode("utf-8"),
                _CSV_FBO.encode("utf-8"),
            ]
        )

        def _fetch(url):
            """Return the two PDFs by URL and the CSVs in filer order."""
            if url == fry15_structure.GUIDE_URL:
                return b"%PDF-guide"
            if url == fry15_structure.FORM_URL:
                return b"%PDF-form"
            return next(csv_cycle)

        monkeypatch.setattr(fry15_structure, "_fetch_bytes", _fetch)
        payload = generate()
        assert payload["source"] == fry15_structure.GUIDE_URL
        assert payload["form_source"] == fry15_structure.FORM_URL

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        _patch_readers(monkeypatch, _GUIDE_PAGES, _FORM_PAGES)
        guide = tmp_path / "guide.pdf"
        guide.write_bytes(b"%PDF-guide")
        form = tmp_path / "form.pdf"
        form.write_bytes(b"%PDF-form")
        hc = tmp_path / "hc.csv"
        hc.write_text(_CSV_HC, encoding="utf-8")
        target = tmp_path / "fry15" / "structure.json"
        monkeypatch.setattr(fry15_structure, "ASSET_PATH", target)
        path = write_asset(str(guide), str(form), [str(hc)])
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a coverage summary."""
        _patch_readers(monkeypatch, _GUIDE_PAGES, _FORM_PAGES)
        guide = tmp_path / "guide.pdf"
        guide.write_bytes(b"%PDF-guide")
        form = tmp_path / "form.pdf"
        form.write_bytes(b"%PDF-form")
        hc = tmp_path / "hc.csv"
        hc.write_text(_CSV_HC, encoding="utf-8")
        target = tmp_path / "fry15" / "structure.json"
        monkeypatch.setattr(fry15_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv",
            [
                "fry15_structure",
                "--guide",
                str(guide),
                "--form",
                str(form),
                "--csv",
                str(hc),
            ],
        )
        fry15_structure._main()
        out = capsys.readouterr().out
        assert "schedules" in out and "coverage" in out
