"""Tests for the FR Y-9SP report structure generator."""

import json
import re

import pytest

from openbb_federal_reserve.utils import fry9sp_structure
from openbb_federal_reserve.utils.fry9sp_structure import (
    _build_items,
    _csv_value_codes,
    _filed_union,
    generate,
    validate,
    write_asset,
)

# A live-CSV stand-in: identity and submission-administration rows are skipped,
# value-bearing MDRM rows are kept. The codes chosen exercise the cover block, a
# memoranda audit-firm text item, and a balance-sheet section with one filed and
# one unfiled child so the header-keep logic is covered both ways.
_CSV = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,VALIDATION BANK",
        "Street Address,,1 MAIN ST",
        "Report Date,,December 31, 2025",
        "ID_RSSD,Reporting entity identifier,1020395",
        "BHSPC490,Printed Name,JANE DOE",
        "BHSP0508,Dividends,100",
        "BHSP2122,Loans and leases,200",
        "TEXTC703,Audit firm,SOME LLP",
        "BHSP2170,Total assets,400",
        "BHSPK141,Note amount,0",
    ]
)

# The value-bearing codes of ``_CSV`` (the identity rows above are excluded).
_CSV_CODES = {"BHSPC490", "BHSP0508", "BHSP2122", "TEXTC703", "BHSP2170", "BHSPK141"}


class TestCsvValueCodes:
    """Coverage for the per-CSV value-bearing-code extractor."""

    def test_identity_rows_excluded(self):
        """Institution, address, RSSD and report-date rows are not value codes."""
        codes = _csv_value_codes(_CSV.encode("utf-8"))
        assert codes == _CSV_CODES

    def test_short_and_blank_rows_skipped(self):
        """Rows shorter than three columns or with a blank name are ignored."""
        text = "ItemName,Description,Value\nBHSP0508,A,1\n,,\nshort\r\n"
        assert _csv_value_codes(text.encode("utf-8")) == {"BHSP0508"}

    def test_non_mdrm_name_skipped(self):
        """A row whose name is not an eight-character MDRM is not a value code."""
        text = "ItemName,Description,Value\nNot A Code,A,1\nBHSP0508,B,2"
        assert _csv_value_codes(text.encode("utf-8")) == {"BHSP0508"}


class TestFiledUnion:
    """Coverage for the multi-CSV union."""

    def test_unions_across_payloads(self):
        """The union pools the value codes of every sampled payload."""
        first = "ItemName,Description,Value\nBHSP0508,A,1"
        second = "ItemName,Description,Value\nBHSP2170,B,2"
        union = _filed_union([first.encode("utf-8"), second.encode("utf-8")])
        assert union == {"BHSP0508", "BHSP2170"}

    def test_empty_payloads_yield_empty_union(self):
        """No payloads yield an empty union."""
        assert _filed_union([]) == set()


class TestBuildItems:
    """Coverage for projecting the curated form onto a filed item set."""

    def test_keeps_only_filed_value_items(self):
        """A value row survives only when its MDRM is in the filed set."""
        items = _build_items(_CSV_CODES)
        codes = {item["mdrm"] for item in items if item["mdrm"]}
        assert codes == _CSV_CODES

    def test_drops_header_with_no_filed_child(self):
        """A section header with no surviving child is dropped."""
        # ``BHSP0508`` (SI 1.a) is filed but ``BHSP2111`` (SI 1.b) is not, so the
        # "Income from non-bank subsidary(ies)" header (no filed child) is gone.
        items = _build_items(_CSV_CODES)
        captions = {item["caption"] for item in items if item["is_header"]}
        assert "Income from bank subsidary(ies)" in captions
        assert "Income from non-bank subsidary(ies)" not in captions

    def test_keeps_header_with_filed_child(self):
        """A section header is kept when a filed value item nests under it."""
        items = _build_items({"TEXTC703"})
        captions = [item["caption"] for item in items if item["is_header"]]
        assert any(
            caption.startswith("If response to Memorandum") for caption in captions
        )

    def test_item_shape_and_columns(self):
        """Each emitted item carries the committed structure shape."""
        items = _build_items({"BHSP0508"})
        value = next(item for item in items if item["mdrm"] == "BHSP0508")
        assert value["schedule"] == "SI"
        assert value["schedule_name"] == "Schedule SI - Income Statement"
        assert value["columns"] == ["BHSP0508"]
        assert value["is_header"] is False
        header = next(item for item in items if item["is_header"])
        assert header["mdrm"] is None
        assert header["columns"] is None


class TestValidation:
    """Coverage for the filed-union comparison."""

    def test_full_coverage_no_permanent_empty(self):
        """A structure mapping exactly the filed set is complete and clean."""
        items = _build_items(_CSV_CODES)
        result = validate(items, _CSV_CODES)
        assert result["coverage"] == 100.0
        assert result["missing"] == []
        assert result["permanent_empty"] == []
        assert result["duplicate_codes"] == []

    def test_reports_missing_and_permanent_empty(self):
        """An unmapped filed code and a never-filed structure code are reported."""
        items = [{"mdrm": "BHSP0508"}, {"mdrm": "BHSP9999"}]
        result = validate(items, {"BHSP0508", "BHSPZZZZ"})
        assert result["missing"] == ["BHSPZZZZ"]
        assert result["permanent_empty"] == ["BHSP9999"]
        assert result["coverage"] == 50.0

    def test_reports_duplicate_codes(self):
        """A code carried by two structure items is reported as a duplicate."""
        items = [{"mdrm": "BHSP0508"}, {"mdrm": "BHSP0508"}]
        result = validate(items, {"BHSP0508"})
        assert result["duplicate_codes"] == ["BHSP0508"]

    def test_empty_filed_set(self):
        """An empty filed set yields zero coverage rather than dividing by zero."""
        assert validate([], set())["coverage"] == 0.0


class TestFetchBytes:
    """Coverage for the network-fetch entry point."""

    def test_fetches_ffiec_csv_through_session(self, monkeypatch):
        """The CSV is fetched through the browser-impersonating session."""
        captured = {}

        class _Resp:
            content = b"ItemName,Description,Value"

            def raise_for_status(self):
                """No-op success."""

        class _Session:
            def get(self, url, **kwargs):
                """Record the URL and return the canned response."""
                captured["url"] = url
                return _Resp()

        from openbb_federal_reserve.utils import curl_session

        def _get_session(_key, warmup):
            """Run the warmup callback the way the real session helper does."""
            warmup(_Session())
            return _Session()

        monkeypatch.setattr(curl_session, "get_session", _get_session)
        out = fry9sp_structure._fetch_bytes(
            "https://www.ffiec.gov/npw/FinancialReport/x"
        )
        assert out == b"ItemName,Description,Value"
        assert "ffiec.gov" in captured["url"]


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def test_generate_from_local_paths(self, tmp_path):
        """``generate`` reads local CSV paths and validates coverage."""
        csv_path = tmp_path / "filer.csv"
        csv_path.write_text(_CSV, encoding="utf-8")
        payload = generate([str(csv_path)])
        assert payload["item_count"] == len(payload["items"])
        assert payload["validation"]["coverage"] == 100.0
        assert payload["validation"]["permanent_empty"] == []
        assert {s["schedule"] for s in payload["schedules"]} >= {"SI", "COVER"}
        assert payload["sampled_filers"] == list(fry9sp_structure.SAMPLE_RSSDS)

    def test_generate_fetches_and_skips_non_report_responses(self, monkeypatch):
        """Without paths, ``generate`` fetches and skips non-FR-Y-9SP responses."""

        def _fetch(url):
            """Return the CSV for the first filer, an error page for the rest."""
            if f"id={fry9sp_structure.SAMPLE_RSSDS[0]}" in url:
                return _CSV.encode("utf-8")
            return b"<!DOCTYPE html><html>We are sorry...</html>"

        monkeypatch.setattr(fry9sp_structure, "_fetch_bytes", _fetch)
        payload = generate()
        assert payload["source"] == fry9sp_structure.USER_GUIDE_URL
        assert payload["validation"]["coverage"] == 100.0

    def test_write_asset(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        csv_path = tmp_path / "filer.csv"
        csv_path.write_text(_CSV, encoding="utf-8")
        target = tmp_path / "fry9sp" / "structure.json"
        monkeypatch.setattr(fry9sp_structure, "ASSET_PATH", target)
        path = write_asset([str(csv_path)])
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a coverage summary."""
        csv_path = tmp_path / "filer.csv"
        csv_path.write_text(_CSV, encoding="utf-8")
        target = tmp_path / "fry9sp" / "structure.json"
        monkeypatch.setattr(fry9sp_structure, "ASSET_PATH", target)
        monkeypatch.setattr(
            "sys.argv",
            ["fry9sp_structure", "--csv", str(csv_path)],
        )
        fry9sp_structure._main()
        out = capsys.readouterr().out
        assert "coverage" in out and "permanent_empty" in out


class TestCommittedAsset:
    """Sanity checks on the committed structure asset."""

    def test_asset_mdrms_are_well_formed(self):
        """Every value-bearing row carries a syntactically valid MDRM code."""
        payload = json.loads(fry9sp_structure.ASSET_PATH.read_text(encoding="utf-8"))
        for item in payload["items"]:
            if not item["is_header"]:
                assert re.fullmatch(r"[A-Z]{4}[A-Z0-9]{4}", item["mdrm"])

    def test_asset_coverage_is_complete_with_no_permanent_empty(self):
        """The committed asset records full coverage and no never-filed rows."""
        payload = json.loads(fry9sp_structure.ASSET_PATH.read_text(encoding="utf-8"))
        validation = payload["validation"]
        assert validation["coverage"] == 100.0
        assert validation["missing"] == []
        assert validation["permanent_empty"] == []
        assert validation["duplicate_codes"] == []

    def test_asset_cover_block_under_cover_schedule(self):
        """The administrative cover/contact items live under the COVER schedule."""
        payload = json.loads(fry9sp_structure.ASSET_PATH.read_text(encoding="utf-8"))
        cover = [item for item in payload["items"] if item["schedule"] == "COVER"]
        assert cover
        assert all(item["schedule_name"] == "Cover Page" for item in cover)

    def test_asset_captions_are_clean(self):
        """No caption is a bare field-length integer or starts with glued junk."""
        payload = json.loads(fry9sp_structure.ASSET_PATH.read_text(encoding="utf-8"))
        for item in payload["items"]:
            caption = item["caption"]
            assert caption.strip()
            assert not re.fullmatch(r"\d+", caption)
            assert caption[0] not in {".", ")"}


@pytest.mark.parametrize(
    "code, registered",
    [("FRY9SP", True), ("UNKNOWN", False)],
)
def test_report_registered(code, registered):
    """FR Y-9SP is registered in the report catalog pointing at its asset."""
    from openbb_federal_reserve.utils.ffiec import READY_REPORTS

    assert (code in READY_REPORTS) is registered
    if registered:
        assert READY_REPORTS[code]["structure"] == "fry9sp"
