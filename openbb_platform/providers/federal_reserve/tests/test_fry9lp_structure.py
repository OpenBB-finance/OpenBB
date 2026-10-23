"""Tests for the FR Y-9LP report structure generator."""

import json
import re

import pytest

from openbb_federal_reserve.utils import fry9lp_structure, report_structure
from openbb_federal_reserve.utils.fry9lp_structure import (
    _csv_mdrms,
    _hoist_cover_items,
    _latest_quarter_end,
    _prune_permanent_empties,
    _union_mdrms,
    build_items,
    generate,
    validate,
    write_asset,
)

# A synthetic FR Y-9LP appendix exercising the schedule banner, a Memoranda
# sub-header, a wrapped item, the cover-page block (hoisted to its own COVER
# schedule), and a numeric note item whose free-text description half is dropped.
_APPENDIX = [
    "Appendix A",
    "FR Y- 9LP Report Detailed Field Specifications",
    "Report Form",
    "Item",
    "8-character",
    "MDRM",
    "Financial Data Items",
    "Schedule PI - Parent Company Only Income Statement",
    "1.a.(1) Dividends BHCP0508",
    "1.f. Total operating income",
    "(sum of items above) BHCP4000",
    "Memoranda",
    "M.1. Noncash items BHCP4647",
    "Schedule PC-B - Memoranda",
    "Notes to the Parent Company Only Financial Statements",
    "1. Amount BHCP5485",
    "Text Items",
    "1. Description TEXT5485",
    "Cover Page Contact Name BHPX8901",
    "Cover Page Legal Title of Holding Company RSSD9017",
]

# A live-CSV stand-in: identity rows are skipped, value-bearing MDRMs are kept.
# ``BHCP5485`` carries a blank value here so the union is exercised by the second
# filer; ``RSSD9017`` (cover-page legal title) is absent from every filer and so
# is a permanent-empty that must be pruned from the structure.
_CSV = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,VALIDATION BANK",
        "Report Date,,June 30, 2025",
        "ID_RSSD,,1039502",
        "DT_RPTQ,,20250630",
        "BHCP0508,Dividends,100",
        "BHCP4000,Total operating income,200",
        "BHCP4647,Noncash items,300",
        "BHCP5485,Amount,",
        "BHPX8901,Contact Name,Jane Doe",
    ]
)

# A second filer whose union with ``_CSV`` adds the value-bearing ``BHCP5485``.
_CSV_2 = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,VALIDATION BANK TWO",
        "ID_RSSD,,1073757",
        "BHCP0508,Dividends,150",
        "BHCP4000,Total operating income,250",
        "BHCP4647,Noncash items,350",
        "BHCP5485,Amount,5",
        "BHPX8901,Contact Name,John Roe",
    ]
)


def _patch_reader(monkeypatch, lines=_APPENDIX):
    """Patch ``read_pdf_pages`` to yield the synthetic appendix as one page."""
    monkeypatch.setattr(
        report_structure, "read_pdf_pages", lambda _pdf_bytes: ["\n".join(lines)]
    )


class TestBuildItems:
    """End-to-end parse of the synthetic FR Y-9LP appendix."""

    def test_schedules_and_items(self, monkeypatch):
        """Both schedules plus the hoisted cover block are present."""
        _patch_reader(monkeypatch)
        items = build_items(b"%PDF-1.7")
        schedules = {item["schedule"] for item in items}
        assert {"PI", "PC-B", "COVER"} <= schedules

    def test_wrapped_item_resolves(self, monkeypatch):
        """A caption whose MDRM lands on the next line resolves to one row."""
        _patch_reader(monkeypatch)
        items = build_items(b"%PDF-1.7")
        row = next(r for r in items if r["line"] == "1.f")
        assert row["mdrm"] == "BHCP4000"

    def test_memoranda_header(self, monkeypatch):
        """The bare ``Memoranda`` line is emitted as a section header."""
        _patch_reader(monkeypatch)
        items = build_items(b"%PDF-1.7")
        header = next(r for r in items if r["caption"] == "Memoranda")
        assert header["is_header"] and header["mdrm"] is None

    def test_text_description_dropped(self, monkeypatch):
        """The free-text description half of the notes pair is dropped."""
        _patch_reader(monkeypatch)
        items = build_items(b"%PDF-1.7")
        assert not any(r["mdrm"] == "TEXT5485" for r in items)
        assert any(r["mdrm"] == "BHCP5485" for r in items)


class TestHoistCoverItems:
    """Coverage for moving the trailing cover-page block to its own schedule."""

    def test_cover_items_retagged(self, monkeypatch):
        """Cover-page rows become COVER and lose the redundant prefix."""
        _patch_reader(monkeypatch)
        items = build_items(b"%PDF-1.7")
        cover = [r for r in items if r["schedule"] == "COVER"]
        assert cover
        contact = next(r for r in cover if r["mdrm"] == "BHPX8901")
        assert contact["caption"] == "Contact Name"
        assert contact["line"] is None and contact["level"] == 1

    def test_non_cover_rows_untouched(self):
        """A row that is not a cover-page line keeps its schedule and caption."""
        items = [
            {
                "schedule": "PI",
                "schedule_name": "Income",
                "line": "1",
                "caption": "Dividends",
                "mdrm": "BHCP0508",
                "level": 2,
            }
        ]
        _hoist_cover_items(items)
        assert items[0]["schedule"] == "PI"
        assert items[0]["caption"] == "Dividends"


class TestValidation:
    """Coverage for the CSV-coverage comparison."""

    def test_csv_mdrms_skips_identity(self):
        """Identity and reporting-date rows are skipped; value-bearing kept."""
        codes = _csv_mdrms(_CSV)
        assert "BHCP0508" in codes
        assert "ID_RSSD" not in codes
        assert "DT_RPTQ" not in codes

    def test_csv_mdrms_skips_blank_values(self):
        """A row whose value is blank is not value-bearing and is skipped."""
        assert "BHCP5485" not in _csv_mdrms(_CSV)

    def test_csv_mdrms_skips_short_rows(self):
        """A row with fewer than three fields is ignored."""
        text = "ItemName,Description,Value\nBHCP0001\nBHCP0002,Caption,5"
        assert _csv_mdrms(text) == {"BHCP0002"}

    def test_union_combines_filers(self):
        """The union adds the second filer's value-bearing ``BHCP5485``."""
        union = _union_mdrms([_CSV, _CSV_2])
        assert "BHCP5485" in union
        assert "BHCP0508" in union

    def test_prune_drops_permanent_empties(self):
        """A value-item whose code is in no CSV is dropped; headers are kept."""
        items = [
            {"mdrm": "BHCP0508", "caption": "Kept"},
            {"mdrm": "RSSD9017", "caption": "Pruned"},
            {"mdrm": None, "caption": "Header"},
        ]
        pruned = _prune_permanent_empties(items, {"BHCP0508"})
        captions = [item["caption"] for item in pruned]
        assert captions == ["Kept", "Header"]

    def test_validate_full_coverage(self, monkeypatch):
        """Every union code maps in and no structure code is permanently empty."""
        _patch_reader(monkeypatch)
        items = build_items(b"%PDF-1.7")
        union = _union_mdrms([_CSV, _CSV_2])
        items = _prune_permanent_empties(items, union)
        result = validate(items, [_CSV, _CSV_2])
        assert result["coverage"] == 100.0
        assert result["missing"] == []
        assert result["permanent_empty"] == []

    def test_validate_reports_missing(self):
        """An uncovered union code is reported and lowers coverage."""
        items = [{"mdrm": "BHCP0508"}]
        text = "ItemName,Description,Value\nBHCP0508,A,1\nBHCP9999,B,2"
        result = validate(items, [text])
        assert result["missing"] == ["BHCP9999"]
        assert result["coverage"] == 50.0

    def test_validate_reports_permanent_empty(self):
        """A structure code absent from every CSV is reported as permanent-empty."""
        items = [{"mdrm": "BHCP0508"}, {"mdrm": "RSSD9017"}]
        text = "ItemName,Description,Value\nBHCP0508,A,1"
        result = validate(items, [text])
        assert result["permanent_empty"] == ["RSSD9017"]
        assert result["coverage"] == 100.0

    def test_validate_empty_csv(self):
        """An empty CSV yields zero coverage rather than dividing by zero."""
        result = validate([], ["ItemName,Description,Value"])
        assert result["coverage"] == 0.0


class TestLatestQuarterEnd:
    """Coverage for the validation period helper."""

    def test_steps_back_a_quarter(self, monkeypatch):
        """Mid-quarter, the helper returns the prior quarter-end."""
        import datetime as dt

        class _Date(dt.date):
            @classmethod
            def today(cls):
                """Pin today to the second quarter of 2025."""
                return cls(2025, 5, 15)

        monkeypatch.setattr("datetime.date", _Date)
        assert _latest_quarter_end() == "20250331"

    def test_rolls_into_prior_year(self, monkeypatch):
        """In the first quarter, the helper rolls back to the prior year-end."""
        import datetime as dt

        class _Date(dt.date):
            @classmethod
            def today(cls):
                """Pin today to the first quarter of 2025."""
                return cls(2025, 2, 1)

        monkeypatch.setattr("datetime.date", _Date)
        assert _latest_quarter_end() == "20241231"


class TestFetchers:
    """Coverage for the network-fetch entry points."""

    def test_fetch_pdf_bytes(self, monkeypatch):
        """``_fetch_pdf_bytes`` returns the response body and raises for status."""
        import requests

        class _Resp:
            content = b"%PDF-1.7 body"

            def raise_for_status(self):
                """No-op success."""

        monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
        assert fry9lp_structure._fetch_pdf_bytes() == b"%PDF-1.7 body"

    def test_fetch_filer_csv(self, monkeypatch):
        """``_fetch_filer_csv`` decodes one filer's per-institution CSV bytes."""
        from openbb_federal_reserve.utils import ffiec

        monkeypatch.setattr(ffiec, "_fetch_bytes", lambda *a, **k: b"row,one,1")
        monkeypatch.setattr(fry9lp_structure, "_latest_quarter_end", lambda: "20250331")
        assert fry9lp_structure._fetch_filer_csv(1039502) == "row,one,1"


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def test_generate_from_local_paths(self, monkeypatch, tmp_path):
        """``generate`` reads local PDF and CSV paths, prunes, and validates."""
        _patch_reader(monkeypatch)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_one = tmp_path / "filer1.csv"
        csv_one.write_text(_CSV, encoding="utf-8")
        csv_two = tmp_path / "filer2.csv"
        csv_two.write_text(_CSV_2, encoding="utf-8")
        payload = generate(str(pdf), [str(csv_one), str(csv_two)])
        assert payload["item_count"] == len(payload["items"])
        assert payload["validation"]["coverage"] == 100.0
        assert payload["validation"]["permanent_empty"] == []
        assert not any(item["mdrm"] == "RSSD9017" for item in payload["items"])
        assert {s["schedule"] for s in payload["schedules"]} >= {"PI", "COVER"}

    def test_generate_fetches_when_no_paths(self, monkeypatch):
        """Without paths, ``generate`` downloads the PDF and each filer CSV."""
        _patch_reader(monkeypatch)
        monkeypatch.setattr(fry9lp_structure, "_fetch_pdf_bytes", lambda: b"%PDF-1.7")
        monkeypatch.setattr(fry9lp_structure, "_fetch_filer_csv", lambda rssd: _CSV)
        payload = generate()
        assert payload["source"] == fry9lp_structure.USER_GUIDE_URL

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        _patch_reader(monkeypatch)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_path = tmp_path / "filer.csv"
        csv_path.write_text(_CSV, encoding="utf-8")
        target = tmp_path / "fry9lp" / "structure.json"
        monkeypatch.setattr(fry9lp_structure, "ASSET_PATH", target)
        path = write_asset(str(pdf), [str(csv_path)])
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a coverage summary."""
        _patch_reader(monkeypatch)
        pdf = tmp_path / "guide.pdf"
        pdf.write_bytes(b"%PDF-1.7")
        csv_one = tmp_path / "filer1.csv"
        csv_one.write_text(_CSV, encoding="utf-8")
        csv_two = tmp_path / "filer2.csv"
        csv_two.write_text(_CSV_2, encoding="utf-8")
        target = tmp_path / "fry9lp" / "structure.json"
        monkeypatch.setattr(fry9lp_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv",
            [
                "fry9lp_structure",
                "--pdf",
                str(pdf),
                "--csv",
                str(csv_one),
                "--csv",
                str(csv_two),
            ],
        )
        fry9lp_structure._main()
        out = capsys.readouterr().out
        assert "coverage" in out and "permanent_empty" in out


class TestCommittedAsset:
    """Sanity checks on the committed structure asset."""

    def test_asset_mdrms_are_well_formed(self):
        """Every value-bearing row carries a syntactically valid MDRM code."""
        payload = json.loads(fry9lp_structure.ASSET_PATH.read_text(encoding="utf-8"))
        for item in payload["items"]:
            if not item["is_header"]:
                assert re.fullmatch(r"[A-Z]{4}[A-Z0-9]{4}", item["mdrm"])

    def test_asset_coverage_is_complete(self):
        """The committed asset records full coverage with no permanent-empties."""
        payload = json.loads(fry9lp_structure.ASSET_PATH.read_text(encoding="utf-8"))
        assert payload["validation"]["coverage"] == 100.0
        assert payload["validation"]["missing"] == []
        assert payload["validation"]["permanent_empty"] == []


@pytest.mark.parametrize(
    "code, registered",
    [("FRY9LP", True), ("UNKNOWN", False)],
)
def test_report_registered(code, registered):
    """FR Y-9LP is registered in the report catalog pointing at its asset."""
    from openbb_federal_reserve.utils.ffiec import READY_REPORTS

    assert (code in READY_REPORTS) is registered
    if registered:
        assert READY_REPORTS[code]["structure"] == "fry9lp"
