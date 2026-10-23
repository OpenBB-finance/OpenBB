"""Tests for the FFIEC 102 report structure generator."""

import json
from datetime import date

import pytest

from openbb_federal_reserve.utils import ffiec102_structure
from openbb_federal_reserve.utils.ffiec102_structure import (
    _BODY,
    _COVER,
    _build_items,
    _filed_codes,
    _latest_quarter_end,
    generate,
    validate,
    write_asset,
)

# A synthetic per-institution CSV: the header row, an identity row, a DT_ row, a
# short malformed row, a code with a blank value, and value-bearing rows covering
# the cover-page and body codes the form table enumerates.
_CSV_TEXT = "\n".join(
    [
        "ItemName,Description,Value",
        "Institution Name,,TEST BANK",
        "ID_RSSD,Reporting entity identifier,852218",
        "DT_RPT,Report date,20250331",
        "Short Row",
        "MRRRS300,A blank-valued code is skipped,",
        "MRRRS298,PREVIOUS DAY'S VAR-BASED MEASURE,100",
        "MRRRC490,PRINTED NAME OF SENIOR OFFICER,Jane Doe",
    ]
)


def _full_filing() -> str:
    """A synthetic CSV carrying every form-table code so validation passes."""
    rows = ["ItemName,Description,Value", "Institution Name,,TEST BANK"]
    for code, *_ in _COVER:
        rows.append(f"{code},{code} caption,1")
    for code, *_ in _BODY:
        rows.append(f"{code},{code} caption,1")
    return "\n".join(rows)


class TestFiledCodes:
    """Coverage for the per-filing value-bearing code extraction."""

    def test_excludes_identity_dt_blank_and_malformed(self):
        """Identity, DT, blank-valued, and short rows are excluded; codes kept."""
        codes = _filed_codes(_CSV_TEXT)
        assert codes == {"MRRRS298", "MRRRC490"}
        assert "MRRRS300" not in codes

    def test_non_mdrm_item_name_skipped(self):
        """An item name that is not an MDRM code is not a value-bearing code."""
        text = "ItemName,Description,Value\nNOT A CODE,Some caption,500"
        assert _filed_codes(text) == set()


class TestBuildItems:
    """Coverage for the form-table item builder."""

    def test_cover_and_body_items_in_order(self):
        """Cover items precede body items, each carrying a single-code column."""
        items = _build_items()
        cover = [i for i in items if i["schedule"] == "COVER"]
        assert cover[0]["mdrm"] == _COVER[0][0]
        assert cover[0]["columns"] == [_COVER[0][0]]
        assert all(not i["is_header"] for i in cover)

    def test_section_headers_emitted_once_per_section(self):
        """A body section emits one header, demoting its members to level 2."""
        items = _build_items()
        headers = [i for i in items if i["is_header"]]
        section_names = [h["caption"] for h in headers]
        # Each section header is unique and appears exactly once.
        assert len(section_names) == len(set(section_names))
        sectioned = [i for i in items if i["schedule"] == "RC" and not i["is_header"]]
        assert any(i["level"] == 2 for i in sectioned)
        assert any(i["level"] == 1 for i in sectioned)


class TestValidate:
    """Coverage for the form-table-versus-filings reconciliation."""

    def test_passes_when_table_matches_union(self):
        """A filing covering every table code validates and returns the union."""
        union = validate([_full_filing()])
        table = {c for c, *_ in _COVER} | {c for c, *_ in _BODY}
        assert union == table

    def test_raises_on_filed_code_missing_from_table(self):
        """A filed code absent from the form table fails validation."""
        text = _full_filing() + "\nMRRRZZZZ,An unknown filed code,9"
        with pytest.raises(ValueError, match="missing from the form table"):
            validate([text])

    def test_raises_on_permanently_empty_table_code(self):
        """A table code absent from every sampled filing fails validation."""
        rows = ["ItemName,Description,Value"]
        for code, *_ in list(_COVER)[:-1] + list(_BODY):
            rows.append(f"{code},{code} caption,1")
        with pytest.raises(ValueError, match="absent from every sampled filing"):
            validate(["\n".join(rows)])


class TestLatestQuarterEnd:
    """Coverage for the validation quarter-end resolver."""

    def test_picks_most_recent_completed(self, monkeypatch):
        """The most recent quarter end before today is chosen."""

        class _Date(date):
            @classmethod
            def today(cls):
                """Freeze today at a mid-Q2 date."""
                return cls(2025, 5, 15)

        monkeypatch.setattr(ffiec102_structure, "date", _Date)
        assert _latest_quarter_end() == "20250331"

    def test_wraps_to_prior_year_in_early_january(self, monkeypatch):
        """In early January the latest completed quarter is the prior year-end."""

        class _Date(date):
            @classmethod
            def today(cls):
                """Freeze today at the start of the year."""
                return cls(2025, 1, 1)

        monkeypatch.setattr(ffiec102_structure, "date", _Date)
        assert _latest_quarter_end() == "20241231"


class TestGenerateAndWrite:
    """Coverage for the asset-generation entry points."""

    def _patch_fetch(self, monkeypatch):
        """Patch the filer fetch and quarter-end to return a complete filing."""
        monkeypatch.setattr(
            ffiec102_structure, "_latest_quarter_end", lambda: "20250331"
        )
        monkeypatch.setattr(
            ffiec102_structure,
            "_fetch_filer_csv",
            lambda rssd, dt: _full_filing(),
        )

    def test_generate_builds_validated_payload(self, monkeypatch):
        """``generate`` validates the sampled filings and summarizes schedules."""
        self._patch_fetch(monkeypatch)
        payload = generate()
        assert payload["source"] == ffiec102_structure.SOURCE
        assert payload["item_count"] == len(payload["items"])
        assert payload["schedule_count"] == len(payload["schedules"])
        assert {s["schedule"] for s in payload["schedules"]} == {"COVER", "RC"}

    def test_fetch_filer_csv_decodes_bytes(self, monkeypatch):
        """``_fetch_filer_csv`` decodes the per-institution CSV download bytes."""
        import openbb_federal_reserve.utils.ffiec as ffiec_mod

        monkeypatch.setattr(
            ffiec_mod, "_fetch_bytes", lambda *a, **k: _CSV_TEXT.encode("utf-8")
        )
        assert ffiec102_structure._fetch_filer_csv("852218", "20250331") == _CSV_TEXT

    def test_write_asset_writes_payload_json(self, monkeypatch, tmp_path):
        """``write_asset`` writes the payload JSON to the asset path."""
        self._patch_fetch(monkeypatch)
        target = tmp_path / "ffiec102" / "structure.json"
        monkeypatch.setattr(ffiec102_structure, "ASSET_PATH", target)
        path = write_asset()
        assert path == target
        assert json.loads(target.read_text())["items"]

    def test_main_writes_and_prints(self, monkeypatch, tmp_path, capsys):
        """The CLI entry point writes the asset and prints a summary."""
        self._patch_fetch(monkeypatch)
        target = tmp_path / "ffiec102" / "structure.json"
        monkeypatch.setattr(ffiec102_structure, "ASSET_PATH", target)
        monkeypatch.setattr("sys.argv", ["ffiec102_structure", "--rssd", "852218"])
        ffiec102_structure._main()
        assert "schedules" in capsys.readouterr().out
