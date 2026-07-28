"""Internal-branch tests for ``openbb_bls.models.cpi_relative_importance``."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.cpi_relative_importance as cri_mod


class _Resp:
    """Stand-in for ``requests.Response``."""

    def __init__(self, status_code, content=b""):
        self.status_code = status_code
        self.content = content


def test_ri_url_format():
    """``_ri_url`` builds the canonical URL for a given year."""
    assert cri_mod._ri_url(2024).endswith("/2024.xlsx")


def test_label_serializer_packs_footnote_when_both_present():
    """``_serialize_label_with_footnote`` returns a dict when both fields exist."""
    record = cri_mod.BlsCpiRelativeImportanceData(
        date=date(2024, 12, 1),
        label="Food",
        footnote="(1) Excludes alcohol.",
        basket="CPI-U",
        relative_importance=12.0,
        row_index=1,
        table_id="tid",
        table_name="t",
    )
    assert record._serialize_label_with_footnote("Food") == {
        "value": "Food",
        "footnote": "(1) Excludes alcohol.",
    }


def test_label_serializer_returns_plain_when_footnote_missing():
    """The serializer returns the plain value when there is no footnote."""
    record = cri_mod.BlsCpiRelativeImportanceData(
        date=date(2024, 12, 1),
        label="Food",
        basket="CPI-U",
        relative_importance=12.0,
        row_index=1,
        table_id="tid",
        table_name="t",
    )
    assert record._serialize_label_with_footnote("Food") == "Food"


def test_fetch_ri_xlsx_returns_none_on_redirect(monkeypatch):
    """``_fetch_ri_xlsx`` returns ``None`` when BLS redirects."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(404))
    assert cri_mod._fetch_ri_xlsx(2025) is None


def test_fetch_ri_xlsx_raises_on_unexpected_status(monkeypatch):
    """Non-200 / non-redirect status codes raise ``OpenBBError``."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        cri_mod._fetch_ri_xlsx(2025)


def test_fetch_ri_xlsx_returns_none_when_payload_is_not_xlsx(monkeypatch):
    """A 200 response without the PK magic bytes returns ``None``."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(200, b"<html></html>"))
    assert cri_mod._fetch_ri_xlsx(2025) is None


def test_fetch_ri_xlsx_returns_bytes_for_valid_payload(monkeypatch):
    """A 200 response with PK magic returns the body."""
    import requests

    payload = b"PK\x03\x04hello"
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(200, payload))
    assert cri_mod._fetch_ri_xlsx(2025) == payload


def test_discover_latest_ri_returns_first_published(monkeypatch):
    """``_discover_latest_ri`` returns the first year whose fetch yields bytes."""
    from datetime import date as _date

    monkeypatch.setattr(
        cri_mod, "_fetch_ri_xlsx", lambda y: b"PK\x03\x04" if y == 2024 else None
    )

    class _Today:
        @staticmethod
        def today():
            return _date(2025, 6, 1)

    monkeypatch.setattr(cri_mod, "dateType", _Today)
    year, content = cri_mod._discover_latest_ri()
    assert year == 2024
    assert content.startswith(b"PK\x03\x04")


def test_discover_latest_ri_raises_when_no_match(monkeypatch):
    """``_discover_latest_ri`` raises when no year in the 6-year window is found."""
    monkeypatch.setattr(cri_mod, "_fetch_ri_xlsx", lambda _y: None)
    with pytest.raises(OpenBBError, match="Could not locate"):
        cri_mod._discover_latest_ri()


def test_extract_data_with_explicit_year(monkeypatch, fixture_bytes):
    """Explicit ``year`` triggers ``_fetch_ri_xlsx`` rather than discovery."""
    monkeypatch.setattr(
        cri_mod,
        "_fetch_ri_xlsx",
        lambda y: fixture_bytes("cpi_relative_importance_2025.xlsx"),
    )
    query = cri_mod.BlsCpiRelativeImportanceQueryParams(year=2025, table=1)
    out = cri_mod.BlsCpiRelativeImportanceFetcher.extract_data(query, None)
    assert out["rows"], "should parse rows from the fixture"


def test_extract_data_raises_when_year_missing(monkeypatch):
    """Explicit ``year`` with no published XLSX raises ``OpenBBError``."""
    monkeypatch.setattr(cri_mod, "_fetch_ri_xlsx", lambda _y: None)
    query = cri_mod.BlsCpiRelativeImportanceQueryParams(year=2099, table=1)
    with pytest.raises(OpenBBError, match="not found"):
        cri_mod.BlsCpiRelativeImportanceFetcher.extract_data(query, None)


def test_transform_data_raises_when_rows_empty():
    """``transform_data`` raises ``EmptyDataError`` for no rows."""
    query = cri_mod.BlsCpiRelativeImportanceQueryParams(table=1)
    with pytest.raises(EmptyDataError, match="No rows parsed"):
        cri_mod.BlsCpiRelativeImportanceFetcher.transform_data(
            query, {"rows": [], "table_id": "x"}
        )


# --------------------------------------------------------------------------
# Helper functions: footnotes, label refs, section header, column classifier
# --------------------------------------------------------------------------


def test_parse_footnotes_block_extracts_marker_definitions():
    """``_parse_footnotes_block`` extracts ``(N) text`` definitions from rows."""
    rows = [
        (None, None),
        ("ignore", "still ignore"),
        ("(1) Footnote text one", None),
        ("(2) Footnote text two", None),
    ]
    out = cri_mod._parse_footnotes_block(rows)
    assert out == {"(1)": "Footnote text one", "(2)": "Footnote text two"}


def test_parse_footnotes_block_skips_empty_rows_and_non_strings():
    """``_parse_footnotes_block`` skips empty rows and non-string cells."""
    rows = [(), (None, 1, 2.0), ("(3) only-marker", None)]
    out = cri_mod._parse_footnotes_block(rows)
    assert out == {"(3)": "only-marker"}


def test_parse_footnotes_block_returns_marker_text_when_body_empty():
    """When the regex captures an empty body, the full cell text is used."""
    rows = [("(4)",)]
    out = cri_mod._parse_footnotes_block(rows)
    assert out == {"(4)": "(4)"}


def test_resolve_label_footnotes_returns_none_when_no_markers():
    """``_resolve_label_footnotes`` returns None when nothing matches."""
    assert cri_mod._resolve_label_footnotes(None, {"(1)": "x"}) is None
    assert cri_mod._resolve_label_footnotes("label", {}) is None
    assert cri_mod._resolve_label_footnotes("plain label", {"(1)": "x"}) is None


def test_resolve_label_footnotes_deduplicates_and_concatenates():
    """Multiple unique markers concatenate with a blank line in between."""
    footnotes = {"(1)": "first", "(2)": "second"}
    out = cri_mod._resolve_label_footnotes("Food (1) (2) (1)", footnotes)
    assert out == "first\n\nsecond"


def test_is_section_header_row_recognises_known_section_titles():
    """``_is_section_header_row`` returns True for known section titles."""
    assert cri_mod._is_section_header_row((None, "Expenditure category"))
    assert cri_mod._is_section_header_row((None, "Special aggregate indexes"))
    assert cri_mod._is_section_header_row((None, "Items"))


def test_is_section_header_row_rejects_short_or_nonstring_rows():
    """Rows shorter than 2 cells or whose label is non-string return False."""
    assert cri_mod._is_section_header_row(()) is False
    assert cri_mod._is_section_header_row((None,)) is False
    assert cri_mod._is_section_header_row((None, 42)) is False
    assert cri_mod._is_section_header_row((1, "Food and beverages")) is False


def test_classify_ri_columns_picks_cpiu_and_cpiw():
    """``_classify_ri_columns`` identifies CPI-U / CPI-W columns and their area."""
    super_headers = ("Indent level", "Label", "U.S. City Average", "U.S. City Average")
    sub_headers = (None, None, "CPI-U", "CPI-W")
    out = cri_mod._classify_ri_columns(super_headers, sub_headers)
    assert out == [
        (2, "U.S. City Average", "CPI-U"),
        (3, "U.S. City Average", "CPI-W"),
    ]


def test_classify_ri_columns_multi_area_keeps_each_area():
    """Repeated CPI-U / CPI-W pairs map to their respective super-header area."""
    super_headers = ("Indent level", "Label", "Boston", "Boston", "Dallas", "Dallas")
    sub_headers = (None, None, "CPI-U", "CPI-W", "CPI-U", "CPI-W")
    out = cri_mod._classify_ri_columns(super_headers, sub_headers)
    assert out == [
        (2, "Boston", "CPI-U"),
        (3, "Boston", "CPI-W"),
        (4, "Dallas", "CPI-U"),
        (5, "Dallas", "CPI-W"),
    ]


def test_classify_ri_columns_area_none_when_super_header_blank():
    """Blank super headers yield ``area=None``; non-basket sub-headers are skipped."""
    super_headers = ("Indent level", "Label", None, "   ", "Area")
    sub_headers = (None, None, "CPI-U", "CPI-W", "Other")
    out = cri_mod._classify_ri_columns(super_headers, sub_headers)
    assert out == [(2, None, "CPI-U"), (3, None, "CPI-W")]


# --------------------------------------------------------------------------
# _parse_ri_table edge cases via tiny in-memory workbooks
# --------------------------------------------------------------------------


def _build_ri_workbook(table_number: int, rows) -> bytes:
    """Build a one-sheet XLSX whose sheet is named ``'Table N'``."""
    import io

    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Table {table_number}"
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_parse_ri_table_raises_when_sheet_missing():
    """A workbook without the requested sheet raises ``OpenBBError``."""
    content = _build_ri_workbook(1, [("hi",)])
    with pytest.raises(OpenBBError, match="does not contain"):
        cri_mod._parse_ri_table(content, 2025, 2)


def test_parse_ri_table_returns_empty_when_indent_header_missing():
    """No ``indent level`` header row returns an empty result."""
    content = _build_ri_workbook(
        1,
        [
            ("no header here",),
            ("still no header",),
        ],
    )
    out = cri_mod._parse_ri_table(content, 2025, 1)
    assert out["rows"] == []


def test_parse_ri_table_returns_empty_when_no_basket_columns():
    """A workbook with an indent header but no CPI-U / CPI-W sub-cells returns empty."""
    content = _build_ri_workbook(
        1,
        [
            ("Indent level", "Label", "Other"),
            (None, None, None),
            (1, "Food", 12.0),
        ],
    )
    out = cri_mod._parse_ri_table(content, 2025, 1)
    assert out["rows"] == []


def test_parse_ri_table_handles_assorted_body_rows():
    """Body rows exercise None cells, bad indent, string parses, section headers."""
    content = _build_ri_workbook(
        1,
        [
            ("Indent level", "Label", "Importance", "Importance"),
            (None, None, "CPI-U", "CPI-W"),
            (None, "Expenditure category", None, None),  # section header
            (None, "", None, None),  # blank row (skipped)
            ("bogus-indent", "Should skip", 1.0, 1.0),  # bad indent -> skip
            (0, None, None, None),  # missing label -> skip
            (1, "Food", 12.5, "13.0"),  # one numeric + one string-coerced
            (1, "Energy", None, "-"),  # None + dash -> None
            (1, "ParseFail", "not-a-number", "x"),  # non-floatable strings -> None
            (1, "Short", 5.0),  # row missing the CPI-W column -> partial
            ("(1) Definition text.",),  # footnote definition (trailing block)
        ],
    )
    out = cri_mod._parse_ri_table(content, 2025, 1)
    labels = {(r["label"], r["basket"]) for r in out["rows"]}
    assert ("Food", "CPI-U") in labels
    assert ("Food", "CPI-W") in labels
    # The Energy CPI-U entry should be present with None value:
    energy = [r for r in out["rows"] if r["label"] == "Energy"]
    assert all(r["relative_importance"] is None for r in energy)
    # Short row contributes a Food/Short row in both baskets — openpyxl pads
    # short rows to the full column width with None, so the CPI-W slot picks
    # up an implicit None value:
    short = [r for r in out["rows"] if r["label"] == "Short"]
    assert {r["basket"] for r in short} == {"CPI-U", "CPI-W"}


def test_parse_ri_table_multi_area_keeps_areas_distinct():
    """A multi-area sheet (Tables 2-7 shape) keeps one row per (area, basket)."""
    content = _build_ri_workbook(
        2,
        [
            ("Indent level", "Label", "Boston", "Boston", "Dallas", "Dallas"),
            (None, None, "CPI-U", "CPI-W", "CPI-U", "CPI-W"),
            (1, "Food", 10.0, 11.0, 12.0, 13.0),
            (1, "Energy", 1.0, 2.0, 3.0, 4.0),
        ],
    )
    out = cri_mod._parse_ri_table(content, 2025, 2)
    rows = out["rows"]
    # Two items * two areas * two baskets = 8 rows, all unique, no duplication.
    keys = {(r["label"], r["area"], r["basket"]) for r in rows}
    assert len(rows) == 8
    assert len(keys) == 8
    assert {r["area"] for r in rows} == {"Boston", "Dallas"}
    boston_food_u = [
        r
        for r in rows
        if r["area"] == "Boston" and r["label"] == "Food" and r["basket"] == "CPI-U"
    ][0]
    assert boston_food_u["relative_importance"] == 10.0
    # row_index is a contiguous 1..N sequence across every series.
    assert sorted(r["row_index"] for r in rows) == list(range(1, 9))
