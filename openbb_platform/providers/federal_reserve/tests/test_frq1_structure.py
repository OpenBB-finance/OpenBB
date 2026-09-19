"""Tests for the FR Q-1 report structure generator."""

import json

from openbb_federal_reserve.utils import frq1_structure, report_structure
from openbb_federal_reserve.utils.frq1_structure import (
    _csv_value_codes,
    _is_header,
    _is_note_tail,
    _prune_to_union,
    _public_code_union,
    _sample_csv_payloads,
    _schedule_code,
    _table_lines,
    generate,
    parse_structure,
    validate,
    write_asset,
)

# A synthetic FR Q-1 upload-specification body exercising every parse branch: the
# Cover Page block, a Schedule banner, a single-line row, a wrapped caption whose
# MDRM lands on a later line, a wrapped Notes/Length tail that must be consumed
# (not leaked into the next caption), an `</br>` caption break, a reinsurance
# Pool No. N schedule and a Pool Description schedule, and the trailing Contexts
# section that extraction must stop at.
_PDF_PAGES = [
    "Front-matter XML-format prose that precedes the table heading.",
    "\n".join(
        [
            "FR Q-1 Item Data MDRMs",
            "Cover Page",
            "Data Items",
            "MDRM",
            "Data",
            "Type",
            "Field",
            "Length Notes",
            "",
            "Name / Title INSQ8901 Text 72",
            "(Mailing Address of the Holding Company) Street /",
            "P.O. Box",
            "RSSD9110 Text",
            "72",
            "Schedule I to VII - Company Inventory to Section 171 Calculation",
            "Data Items",
            "MDRM",
            "Data",
            "Type",
            "Field",
            "Length Notes",
            "Company Assets INSQ2170 Numeric",
            "14",
            "Reported in whole dollars without",
            "commas and leading zeroes.",
            "Company Liabilities INSQ2950 Numeric 14",
            "Material Financial Building Block Parent</br>(0 =",
            "No, 1 = Yes, 2 = Opt Out) INSQLJ57 Numeric",
            "1",
            "Reported in up to 1 digit, 0=No,",
            "1=Yes, 2=Opt",
            "Equity Ownership Percentage INSQLJ53 Decimal",
            "10,4",
            "maximum of 10 digits before the",
            "decimal and 4 digits after the",
            "decimal.",
            "Schedule XIII - Reinsurance Pool Description",
            "Data Items",
            "Pool No. 1 INSQLL29 Text 864",
            "Schedule XIII - Reinsurance Pool No. 1",
            "Data Items",
            "Participants INSQLL31 Text 219",
            "10",
        ]
    ),
    "\n".join(
        [
            "Contexts used in variable schedules:",
            "Schedule",
            "Company ID INSQLJ44 Numeric",
            "Example FR Q-1 XML File Upload",
            '<itemData mdrm="INSQ8901"><value>Text</value></itemData>',
        ]
    ),
]

# Two synthetic per-institution CSVs. Each carries identity/admin rows plus a
# subset of the documented data-item codes; their union (INSQ8901, RSSD9110,
# INSQ2170, INSQ2950) is the public report's true item set the structure prunes
# to. The confidential Schedule XIII codes (INSQLL29/INSQLL31) and the wrapped
# enumeration code (INSQLJ57/INSQLJ53) appear in neither and must be dropped.
_CSV_TEXT_A = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,FIRST INSURER",
        "Street Address,,1 MAIN ST",
        "ID_RSSD,,1447376",
        'Report Date,,"December 31, 2025"',
        "INSQ8901,,Jane Doe",
        "INSQ2170,,100",
        "RSSD9110,,1 MAIN ST",
    ]
)
_CSV_TEXT_B = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,SECOND INSURER",
        "ID_RSSD,,1250101",
        "INSQ8901,,John Roe",
        "INSQ2950,,200",
    ]
)
_PUBLIC_UNION = {"INSQ8901", "RSSD9110", "INSQ2170", "INSQ2950"}


def _patch_reader(monkeypatch, pages):
    """Patch ``read_pdf_pages`` to return the synthetic page-text list."""
    monkeypatch.setattr(
        report_structure, "read_pdf_pages", lambda _pdf_bytes: list(pages)
    )


class TestTableLines:
    """Coverage for the table-boundary extraction from PDF pages."""

    def test_drops_pre_table_prose(self, monkeypatch):
        """Lines before the table heading are dropped."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        lines = _table_lines(b"%PDF-1.7")
        assert all("precedes the table heading" not in line for line in lines)
        assert lines[0] == "Cover Page"

    def test_stops_at_contexts_marker(self, monkeypatch):
        """Extraction stops at the variable-schedule contexts section."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        lines = _table_lines(b"%PDF-1.7")
        assert all("Contexts used" not in line for line in lines)
        assert all("INSQLJ44" not in line for line in lines)

    def test_stops_at_example_heading(self, monkeypatch):
        """Extraction stops before the example-upload heading."""
        _patch_reader(monkeypatch, _PDF_PAGES[:2] + [_PDF_PAGES[2].split("\n")[-2]])
        lines = _table_lines(b"%PDF-1.7")
        assert all("itemData" not in line for line in lines)
        assert all(line != frq1_structure._TABLE_END for line in lines)

    def test_normalizes_html_break(self, monkeypatch):
        """An ``</br>`` caption break is normalized to whitespace."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        lines = _table_lines(b"%PDF-1.7")
        broken = next(line for line in lines if "Material Financial" in line)
        assert "</br>" not in broken
        assert "br>" not in broken

    def test_handles_empty_page_text(self, monkeypatch):
        """A page yielding empty text contributes no lines."""
        _patch_reader(monkeypatch, [""])
        assert _table_lines(b"%PDF-1.7") == []


class TestScheduleCode:
    """Coverage for the schedule-code derivation."""

    def test_plain_roman(self):
        """A plain schedule keeps its roman numeral."""
        assert _schedule_code("VIII", "Framework Information") == "VIII"

    def test_compound_roman(self):
        """A compound ``I to VII`` roman dasherizes."""
        assert _schedule_code("I to VII", "Company Inventory") == "I-to-VII"

    def test_pool_number_suffix(self):
        """A pool schedule appends its pool number."""
        assert _schedule_code("XIII", "Reinsurance Pool No. 2") == "XIII-2"

    def test_description_suffix(self):
        """A pool description schedule appends ``DESC``."""
        assert _schedule_code("XIII", "Reinsurance Pool Description") == "XIII-DESC"


class TestIsHeader:
    """Coverage for the column-header predicate."""

    def test_column_header(self):
        """A column-header word is a header line."""
        assert _is_header("Length Notes") is True

    def test_table_title(self):
        """The table title is a header line."""
        assert _is_header("FR Q-1 Item Data MDRMs") is True

    def test_data_row_not_header(self):
        """A genuine caption is not a header line."""
        assert _is_header("Name / Title") is False


class TestIsNoteTail:
    """Coverage for the wrapped Notes/Length tail predicate."""

    def test_note_sentence_fragment(self):
        """A boilerplate note-sentence fragment is a tail."""
        assert _is_note_tail("commas and leading zeroes.") is True

    def test_reported_prefix(self):
        """A ``Reported ...`` note opens a tail."""
        assert _is_note_tail("Reported in whole dollars without") is True

    def test_bare_field_length(self):
        """A bare field length is a tail."""
        assert _is_note_tail("72") is True

    def test_precision_token(self):
        """A precision token is a tail."""
        assert _is_note_tail("10,4") is True

    def test_unspaced_enumeration(self):
        """An unspaced enumeration note is a tail."""
        assert _is_note_tail("1=Yes, 2=Opt") is True

    def test_caption_is_not_tail(self):
        """A genuine caption is not a tail."""
        assert _is_note_tail("Company Assets") is False

    def test_spaced_enumeration_caption_is_not_tail(self):
        """A spaced caption enumeration is not a note tail."""
        assert _is_note_tail("No, 1 = Yes, 2 = Opt Out)") is False


class TestParseStructure:
    """End-to-end parse over the synthetic upload specification."""

    def test_cover_single_and_wrapped_captions(self, monkeypatch):
        """Cover rows parse, including a single-line and a wrapped caption."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        cover = [i for i in items if i["schedule"] == "COVER"]
        single = next(i for i in cover if i["mdrm"] == "INSQ8901")
        assert single["caption"] == "Name / Title"
        wrapped = next(i for i in cover if i["mdrm"] == "RSSD9110")
        assert wrapped["caption"] == (
            "(Mailing Address of the Holding Company) Street / P.O. Box"
        )

    def test_notes_tail_not_leaked(self, monkeypatch):
        """A wrapped Notes/Length tail never leaks into the next caption."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        liabilities = next(i for i in items if i["mdrm"] == "INSQ2950")
        assert liabilities["caption"] == "Company Liabilities"
        equity = next(i for i in items if i["mdrm"] == "INSQLJ53")
        assert equity["caption"] == "Equity Ownership Percentage"

    def test_html_break_caption_joined(self, monkeypatch):
        """A caption broken by ``</br>`` rejoins around the break."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        item = next(i for i in items if i["mdrm"] == "INSQLJ57")
        assert item["caption"] == (
            "Material Financial Building Block Parent (0 = No, 1 = Yes, 2 = Opt Out)"
        )

    def test_pool_schedules_distinct(self, monkeypatch):
        """The pool description and pool schedules carry distinct codes."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        codes = {i["schedule"] for i in items}
        assert "XIII-DESC" in codes
        assert "XIII-1" in codes

    def test_every_item_value_bearing(self, monkeypatch):
        """FR Q-1 carries no line references and no code-less sub-headers."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        assert all(i["line"] is None for i in items)
        assert all(i["is_header"] is False for i in items)
        assert all(i["mdrm"] for i in items)


class TestCsvValueCodes:
    """Coverage for the per-CSV value-bearing-code extraction."""

    def test_drops_identity_and_keeps_mdrms(self):
        """Identity/admin rows are dropped; MDRM-shaped item names survive."""
        codes = _csv_value_codes(_CSV_TEXT_A.encode("utf-8"))
        assert codes == {"INSQ8901", "INSQ2170", "RSSD9110"}

    def test_drops_dt_period_rows(self):
        """A ``DT``/``DT_*Q`` reporting-period row is dropped."""
        text = "\n".join(
            [
                "ItemName,Description,Value",
                "DT,,20251231",
                "DT_1Q,,20250930",
                "INSQ8901,,Jane",
            ]
        )
        assert _csv_value_codes(text.encode("utf-8")) == {"INSQ8901"}

    def test_skips_blank_rows(self):
        """A blank CSV row is skipped without error."""
        text = "ItemName,Description,Value\n\nINSQ8901,,Jane\n"
        assert _csv_value_codes(text.encode("utf-8")) == {"INSQ8901"}


class TestPublicCodeUnion:
    """Coverage for the cross-filer union builder."""

    def test_union_across_filers(self):
        """The union spans the value codes of every sampled filer."""
        union = _public_code_union(
            [_CSV_TEXT_A.encode("utf-8"), _CSV_TEXT_B.encode("utf-8")]
        )
        assert union == _PUBLIC_UNION


class TestPruneToUnion:
    """Coverage for the union-driven structure pruning."""

    def test_keeps_only_union_codes(self, monkeypatch):
        """Only items whose code is in the union survive pruning."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        pruned = _prune_to_union(items, _PUBLIC_UNION)
        assert {i["mdrm"] for i in pruned} == _PUBLIC_UNION
        assert all(i["mdrm"] in _PUBLIC_UNION for i in pruned)


class TestValidate:
    """Coverage for the union-coverage validation."""

    def test_full_coverage_no_permanent_empties(self, monkeypatch):
        """A pruned structure covers the whole union with no empty rows."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        pruned = _prune_to_union(items, _PUBLIC_UNION)
        result = validate(pruned, _PUBLIC_UNION)
        assert result["available"] is True
        assert result["union_count"] == 4
        assert result["covered_count"] == 4
        assert result["missing"] == []
        assert result["coverage"] == 100.0
        assert result["permanent_empty_items"] == 0

    def test_unavailable_when_union_empty(self, monkeypatch):
        """An empty union (no filer CSV) reports as unavailable."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        items = parse_structure(b"%PDF-1.7")
        result = validate(items, set())
        assert result["available"] is False
        assert result["coverage"] is None
        assert result["permanent_empty_items"] == len(
            {i["mdrm"] for i in items if i["mdrm"]}
        )


class TestFetchBytes:
    """Coverage for the dual-source byte fetcher."""

    def test_public_pdf_via_requests(self, monkeypatch):
        """A frbservices URL is fetched with an ordinary client."""
        import requests

        class _Resp:
            content = b"%PDF body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
        assert (
            frq1_structure._fetch_bytes(frq1_structure.USER_GUIDE_URL) == b"%PDF body"
        )

    def test_ffiec_csv_via_curl_session(self, monkeypatch):
        """An ffiec.gov URL is fetched through the browser-impersonating session."""
        import openbb_federal_reserve.utils.curl_session as curl_mod

        class _Resp:
            content = b"ItemName,Description,Value"

            def raise_for_status(self):
                """No-op success."""

        class _Session:
            def get(self, *a, **k):
                """Return the warmup response or the CSV response."""
                return _Resp()

        def _get_session(key, warmup=None):
            """Run the warmup against the session the way the real helper does."""
            session = _Session()
            if warmup is not None:
                warmup(session)
            return session

        monkeypatch.setattr(curl_mod, "get_session", _get_session)
        url = frq1_structure.CSV_URL.format(rssd=1447376, date="20251231")
        assert frq1_structure._fetch_bytes(url) == b"ItemName,Description,Value"

    def test_lookalike_host_uses_ordinary_client(self, monkeypatch):
        """A host with ``ffiec.gov`` only as a substring is not trusted as FFIEC.

        Guards the URL-host check against incomplete substring matching: a
        look-alike host must fall to the ordinary client, never the
        browser-impersonating FFIEC session.
        """
        import requests

        import openbb_federal_reserve.utils.curl_session as curl_mod

        class _Resp:
            content = b"body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())

        def _forbidden(*a, **k):
            """Fail if the FFIEC session is used for a look-alike host."""
            raise AssertionError("look-alike host must not use the FFIEC session")

        monkeypatch.setattr(curl_mod, "get_session", _forbidden)
        assert frq1_structure._fetch_bytes("https://ffiec.gov.evil.com/x") == b"body"


class TestSampleCsvPayloads:
    """Coverage for the per-filer latest-period CSV fetch."""

    def test_resolves_latest_period_per_filer(self, monkeypatch):
        """Each filer's most recent filed period is fetched."""
        import openbb_federal_reserve.utils.ffiec as ffiec_mod

        def _reports(rssd):
            """Return one filed FR Q-1 period per filer."""
            return {
                "FRQ1": {
                    "name": "Capital and Asset Report (FR Q-1)",
                    "periods": [
                        {"year": 2025, "quarter": 4, "month_day": "12/31"},
                    ],
                }
            }

        requested: list[str] = []

        def _fetch(url):
            """Record each requested CSV URL and return a per-filer payload."""
            requested.append(url)
            return _CSV_TEXT_A.encode("utf-8")

        monkeypatch.setattr(ffiec_mod, "fetch_institution_financial_reports", _reports)
        monkeypatch.setattr(frq1_structure, "_fetch_bytes", _fetch)
        payloads = _sample_csv_payloads()
        assert len(payloads) == len(frq1_structure.VALIDATION_RSSDS)
        assert all("dt=20251231" in url for url in requested)

    def test_skips_filer_without_periods(self, monkeypatch):
        """A filer with no filed FR Q-1 period contributes no payload."""
        import openbb_federal_reserve.utils.ffiec as ffiec_mod

        monkeypatch.setattr(
            ffiec_mod, "fetch_institution_financial_reports", lambda rssd: {}
        )
        monkeypatch.setattr(
            frq1_structure, "_fetch_bytes", lambda url: _CSV_TEXT_A.encode("utf-8")
        )
        assert _sample_csv_payloads() == []

    def test_skips_filer_on_fetch_error(self, monkeypatch):
        """A single filer's failed fetch is skipped rather than raising."""
        import openbb_federal_reserve.utils.ffiec as ffiec_mod

        def _reports(rssd):
            """Return one filed period for every filer."""
            return {
                "FRQ1": {
                    "name": "Capital and Asset Report (FR Q-1)",
                    "periods": [{"year": 2025, "quarter": 4, "month_day": "12/31"}],
                }
            }

        def _fetch(url):
            """Always fail the CSV fetch."""
            raise RuntimeError("blocked")

        monkeypatch.setattr(ffiec_mod, "fetch_institution_financial_reports", _reports)
        monkeypatch.setattr(frq1_structure, "_fetch_bytes", _fetch)
        assert _sample_csv_payloads() == []


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def test_generate_from_local_files(self, monkeypatch, tmp_path):
        """``generate`` reads local PDF and CSV paths and prunes to the union."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_a = tmp_path / "a.csv"
        csv_a.write_text(_CSV_TEXT_A, encoding="utf-8")
        csv_b = tmp_path / "b.csv"
        csv_b.write_text(_CSV_TEXT_B, encoding="utf-8")
        payload = generate(str(pdf), [str(csv_a), str(csv_b)])
        assert payload["item_count"] == len(payload["items"])
        assert payload["schedule_count"] == len(payload["schedules"])
        assert {i["mdrm"] for i in payload["items"]} == _PUBLIC_UNION
        assert payload["validation"]["coverage"] == 100.0
        assert payload["validation"]["permanent_empty_items"] == 0

    def test_generate_fetches_when_no_paths(self, monkeypatch):
        """Without paths, ``generate`` downloads the PDF and samples the filers."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        monkeypatch.setattr(frq1_structure, "_fetch_bytes", lambda url: b"%PDF-1.7")
        monkeypatch.setattr(
            frq1_structure,
            "_sample_csv_payloads",
            lambda: [_CSV_TEXT_A.encode("utf-8"), _CSV_TEXT_B.encode("utf-8")],
        )
        payload = generate()
        assert payload["source"] == frq1_structure.USER_GUIDE_URL
        assert payload["caption_source"] == frq1_structure.USER_GUIDE_URL
        assert payload["validation"]["available"] is True
        assert payload["validation"]["coverage"] == 100.0

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_a = tmp_path / "a.csv"
        csv_a.write_text(_CSV_TEXT_A, encoding="utf-8")
        target = tmp_path / "frq1" / "structure.json"
        monkeypatch.setattr(frq1_structure, "ASSET_PATH", target)
        path = write_asset(str(pdf), [str(csv_a)])
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints_coverage(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints the coverage summary."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_a = tmp_path / "a.csv"
        csv_a.write_text(_CSV_TEXT_A, encoding="utf-8")
        csv_b = tmp_path / "b.csv"
        csv_b.write_text(_CSV_TEXT_B, encoding="utf-8")
        target = tmp_path / "frq1" / "structure.json"
        monkeypatch.setattr(frq1_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv",
            [
                "frq1_structure",
                "--pdf",
                str(pdf),
                "--csv",
                str(csv_a),
                "--csv",
                str(csv_b),
            ],
        )
        frq1_structure._main()
        out = capsys.readouterr().out
        assert "schedules" in out and "items" in out and "100.0%" in out
        assert "permanent_empty_items 0" in out

    def test_main_prints_unavailable_coverage(self, monkeypatch, tmp_path, capsys):
        """The CLI prints ``n/a`` when no sampled filer yields a code union."""
        _patch_reader(monkeypatch, _PDF_PAGES)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        shell = tmp_path / "shell.csv"
        shell.write_text("<!DOCTYPE html><html></html>", encoding="utf-8")
        target = tmp_path / "frq1" / "structure.json"
        monkeypatch.setattr(frq1_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv",
            ["frq1_structure", "--pdf", str(pdf), "--csv", str(shell)],
        )
        frq1_structure._main()
        out = capsys.readouterr().out
        assert "n/a (CSV unavailable)" in out
