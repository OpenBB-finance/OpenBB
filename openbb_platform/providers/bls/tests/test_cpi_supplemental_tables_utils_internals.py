"""Unit tests for ``openbb_bls.utils.cpi_supplemental_tables`` internals."""

from __future__ import annotations

import io
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openpyxl import Workbook

from openbb_bls.utils import cpi_supplemental_tables as cst


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


def _xlsx_bytes(rows: list[list], sheet_title: str = "Sheet1") -> bytes:
    """Build an XLSX byte payload from a list of row lists."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_title
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_decode_html_utf8_and_latin1():
    """UTF-8 decodes cleanly; invalid UTF-8 falls back to latin-1."""
    assert cst._decode_html("héllo".encode()) == "héllo"
    out = cst._decode_html(b"\xff\xfeplain")
    assert "plain" in out


def test_list_supp_index_non_200_raises(monkeypatch):
    """A non-200 index response raises OpenBBError."""
    import requests

    cst.list_supp_index.cache_clear()
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        cst.list_supp_index()
    cst.list_supp_index.cache_clear()


def test_list_supp_index_parses_and_skips_bad_dates(monkeypatch):
    """Anchors matching the XLSX pattern are grouped by stem; bad dates skipped."""
    import requests

    html = (
        "<html><body>"
        '<a href="/cpi/tables/supplemental-files/cpi-u-202604.xlsx">a</a>'
        '<a href="/cpi/tables/supplemental-files/cpi-u-202603.xlsx">b</a>'
        '<a href="/cpi/tables/supplemental-files/cpi-w-202604.xlsx">c</a>'
        # month 13 -> ValueError -> skipped
        '<a href="/cpi/tables/supplemental-files/historical-cpi-u-202613.xlsx">d</a>'
        '<a href="/some/other/file.pdf">e</a>'
        "</body></html>"
    )
    cst.list_supp_index.cache_clear()
    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _FakeResp(content=html.encode("utf-8"))
    )
    index = cst.list_supp_index()
    cst.list_supp_index.cache_clear()
    assert index["cpi-u"] == (date(2026, 3, 1), date(2026, 4, 1))
    assert index["cpi-w"] == (date(2026, 4, 1),)
    assert "historical-cpi-u" not in index


def test_stem_url():
    """``_stem_url`` zero-pads year and month."""
    assert cst._stem_url("cpi-u", 2026, 4).endswith("cpi-u-202604.xlsx")


def test_fetch_xlsx_redirect_returns_none(monkeypatch):
    """Redirect / 404 status codes return None."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=302))
    assert cst.fetch_xlsx("cpi-u", 2026, 4) is None


def test_fetch_xlsx_non_200_raises(monkeypatch):
    """Unexpected non-200 status raises OpenBBError."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=503))
    with pytest.raises(OpenBBError, match="HTTP 503"):
        cst.fetch_xlsx("cpi-u", 2026, 4)


def test_fetch_xlsx_non_xlsx_returns_none(monkeypatch):
    """A 200 response lacking the XLSX magic bytes returns None."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(content=b"<html>"))
    assert cst.fetch_xlsx("cpi-u", 2026, 4) is None


def test_fetch_xlsx_valid_returns_content(monkeypatch):
    """A valid XLSX payload is returned verbatim."""
    import requests

    payload = cst._XLSX_MAGIC + b"rest"
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(content=payload))
    assert cst.fetch_xlsx("cpi-u", 2026, 4) == payload


def test_discover_latest_uses_index_then_returns(monkeypatch):
    """discover_latest tries the index dates first and returns the first hit."""
    monkeypatch.setattr(
        cst,
        "list_supp_index",
        lambda: {"cpi-u": (date(2026, 3, 1), date(2026, 4, 1))},
    )
    calls: list = []

    def _fake_fetch(stem, y, m):
        calls.append((y, m))
        return cst._XLSX_MAGIC + b"x" if (y, m) == (2026, 4) else None

    monkeypatch.setattr(cst, "fetch_xlsx", _fake_fetch)
    y, m, content = cst.discover_latest("cpi-u")
    assert (y, m) == (2026, 4)
    assert content.startswith(cst._XLSX_MAGIC)
    # Index is iterated newest-first.
    assert calls[0] == (2026, 4)


def test_discover_latest_walks_back_and_dedups(monkeypatch):
    """With no index, discover_latest walks back six months and dedups."""
    monkeypatch.setattr(cst, "list_supp_index", lambda: {})
    import openbb_bls.utils.cpi_supplemental_tables as mod

    real_date = mod.dateType

    class _FixedDate(real_date):
        @classmethod
        def today(cls):
            return real_date(2026, 1, 15)

    monkeypatch.setattr(mod, "dateType", _FixedDate)
    seen: list = []

    def _fake_fetch(stem, y, m):
        seen.append((y, m))
        return cst._XLSX_MAGIC if (y, m) == (2025, 10) else None

    monkeypatch.setattr(cst, "fetch_xlsx", _fake_fetch)
    y, m, _ = cst.discover_latest("cpi-u")
    assert (y, m) == (2025, 10)
    # Month rollover from January back into the prior year.
    assert (2025, 12) in seen


def test_discover_latest_exhausts_raises(monkeypatch):
    """When nothing is published, discover_latest raises OpenBBError."""
    monkeypatch.setattr(cst, "list_supp_index", lambda: {})
    monkeypatch.setattr(cst, "fetch_xlsx", lambda *a, **k: None)
    with pytest.raises(OpenBBError, match="Could not locate"):
        cst.discover_latest("cpi-u")


def test_norm_collapses_and_handles_none():
    """``_norm`` collapses whitespace and maps None to ''."""
    assert cst._norm(None) == ""
    assert cst._norm("  a\n b\r c  ") == "a b c"


def test_month_token_to_num():
    """Month tokens (abbrev, full, 'sept', trailing dot) map to ints."""
    assert cst._month_token_to_num("Apr.") == 4
    assert cst._month_token_to_num("September") == 9
    assert cst._month_token_to_num("sept") == 9
    assert cst._month_token_to_num("xyz") is None


def test_parse_single_period_paths():
    """Single-period parsing: no match, bad month, valid."""
    assert cst._parse_single_period("no period here") is None
    assert cst._parse_single_period("Xyz 2026") is None
    assert cst._parse_single_period("Apr. 2026") == date(2026, 4, 1)


def test_parse_range_period_paths():
    """Range parsing: no match, bad month, start-year fallback."""
    assert cst._parse_range_period("nope") is None
    assert cst._parse_range_period("Xyz 2025-Abc 2026") is None
    # No start year -> inherits end year.
    assert cst._parse_range_period("Mar.-Apr. 2026") == (
        date(2026, 3, 1),
        date(2026, 4, 1),
    )
    assert cst._parse_range_period("Apr. 2025-Apr. 2026") == (
        date(2025, 4, 1),
        date(2026, 4, 1),
    )


def test_months_between():
    """``_months_between`` is the absolute month delta."""
    assert cst._months_between(date(2025, 4, 1), date(2026, 4, 1)) == 12
    assert cst._months_between(date(2026, 4, 1), date(2026, 3, 1)) == 1


def test_parse_to_from_super_paths():
    """'Percent change to X from' parsing: no match, bad month, valid."""
    assert cst._parse_to_from_super("no anchor") is None
    assert cst._parse_to_from_super("percent change to Xyz 2026 from") is None
    assert cst._parse_to_from_super("percent change to Apr. 2026 from:") == date(
        2026, 4, 1
    )


def test_parse_value_all_branches():
    """``_parse_value`` handles None, bool, numeric, blank, numeric-str, text."""
    assert cst._parse_value(None) == (None, None)
    assert cst._parse_value(True) == (1.0, "True")
    assert cst._parse_value(5) == (5.0, None)
    assert cst._parse_value("  ") == (None, None)
    assert cst._parse_value("1,234.5") == (1234.5, None)
    assert cst._parse_value("n/a") == (None, "n/a")


def test_is_header_row():
    """Header detection matches only the 'Indent Level' marker in col 0."""
    assert cst._is_header_row(("Indent Level", "x")) is True
    assert cst._is_header_row((None, "x")) is False
    assert cst._is_header_row(()) is False
    assert cst._is_header_row(("Food", "x")) is False


def test_is_blank_row():
    """Blank detection treats None / whitespace as empty."""
    assert cst._is_blank_row((None, "  ", None)) is True
    assert cst._is_blank_row((None, "x")) is False


def test_is_note_row_variants():
    """Note detection: text-less, NOTE:, footnote-def, 'indexes are issued', 'footnote'."""
    assert cst._is_note_row((None, None)) is False
    assert cst._is_note_row(("NOTE: blah",)) is True
    assert cst._is_note_row(("(1) some def",)) is True
    assert cst._is_note_row(("Indexes are issued monthly",)) is True
    assert cst._is_note_row(("Footnote text",)) is True
    assert cst._is_note_row(("Plain label",)) is False


def test_parse_footnotes():
    """Footnote definitions are collected from trailing rows; non-defs skipped."""
    rows = [
        (None, "plain"),
        ("(1) December 1977=100.",),
        (12345,),
        ("(2) Indexes on an alternate base.", "ignored"),
    ]
    out = cst._parse_footnotes(rows)
    assert out["(1)"] == "December 1977=100."
    assert out["(2)"] == "Indexes on an alternate base."


def test_parse_footnotes_body_fallback_to_full_text():
    """A footnote marker with no trailing body uses the full cell text."""
    out = cst._parse_footnotes([("(3)",)])
    assert out["(3)"] == "(3)"


def test_resolve_footnotes_paths():
    """Footnote resolution: empty inputs, unmatched markers, dedup, join."""
    assert cst._resolve_footnotes(None, {"(1)": "x"}) is None
    assert cst._resolve_footnotes("Food (1)", {}) is None
    # Marker not defined -> None.
    assert cst._resolve_footnotes("Food (9)", {"(1)": "x"}) is None
    # Two markers, one repeated -> deduped, joined.
    resolved = cst._resolve_footnotes(
        "Food (1) (2) (1)", {"(1)": "alpha", "(2)": "beta"}
    )
    assert resolved == "alpha\n\nbeta"


def test_classify_columns_full_spectrum():
    """``_classify_columns`` maps each header kind to its classification tuple."""
    super_row = (
        "Indent Level",
        "Expenditure category",
        "Relative importance",
        "Unadjusted index",
        "Seasonally adjusted index",
        "Seasonally adjusted percent change",
        "Percent change to Apr. 2026 from:",
        "",  # forward-filled from prior
        "",  # forward-filled from prior
        "Pricing schedule",
    )
    sub_row = (
        None,
        None,
        None,
        "Apr. 2026",
        "Apr. 2026",
        "Mar. 2026-Apr. 2026",
        "Apr. 2025",
        "Mar. 2026",
        "Feb. 2026",
        None,
    )
    out = cst._classify_columns(super_row, sub_row)
    assert out[0] is None
    assert out[1] is None
    assert out[2] == ("relative_importance", None)
    assert out[3] == ("index_value", date(2026, 4, 1))
    assert out[4] == ("sa_index_value", date(2026, 4, 1))
    assert out[5] == ("pct_change_1m_sa", date(2026, 4, 1))
    assert out[6] == ("pct_change_12m", date(2026, 4, 1))
    assert out[7] == ("pct_change_1m_nsa", date(2026, 4, 1))
    assert out[8] == ("pct_change_window", (date(2026, 2, 1), date(2026, 4, 1)))
    assert out[9] == ("pricing_schedule", None)


def test_classify_columns_label_like_supers_are_none():
    """Special-aggregate / title / item / area supers classify as None."""
    super_row = ("Indent Level", "Special aggregate indexes", "Title", "Item", "Area")
    out = cst._classify_columns(super_row, None)
    assert out == [None, None, None, None, None]


def test_classify_columns_endswith_indexes_and_unadjusted_pct():
    """'... indexes' maps to index_value; 'unadjusted percent change' splits 12m/1m."""
    super_row = (
        "Indent Level",
        "Expenditure category",
        "Monthly indexes",
        "Unadjusted percent change",
        "Unadjusted percent change",
    )
    sub_row = (
        None,
        None,
        "Apr. 2026",
        "Apr. 2025-Apr. 2026",
        "Mar. 2026-Apr. 2026",
    )
    out = cst._classify_columns(super_row, sub_row)
    assert out[2] == ("index_value", date(2026, 4, 1))
    assert out[3] == ("pct_change_12m", date(2026, 4, 1))
    assert out[4] == ("pct_change_1m_nsa", date(2026, 4, 1))


def test_classify_columns_unparseable_percent_change_to_is_none():
    """'Percent change to' with unparseable anchors classifies as None."""
    super_row = ("Indent Level", "Expenditure category", "Percent change to Xyz from:")
    sub_row = (None, None, "Xyz 9999")
    out = cst._classify_columns(super_row, sub_row)
    assert out[2] is None


def test_classify_columns_unadjusted_pct_no_range_is_none():
    """'Unadjusted percent change' with no parseable range classifies as None."""
    super_row = ("Indent Level", "Expenditure category", "Unadjusted percent change")
    sub_row = (None, None, "garbage")
    out = cst._classify_columns(super_row, sub_row)
    assert out[2] is None


def test_classify_columns_unknown_super_is_none():
    """An unrecognised super header classifies as None."""
    super_row = ("Indent Level", "Expenditure category", "Totally unknown header")
    out = cst._classify_columns(super_row, (None, None, "Apr. 2026"))
    assert out[2] is None


def test_discover_latest_skips_duplicate_candidate(monkeypatch):
    """A month present in both the index and the walk-back is fetched only once."""
    import openbb_bls.utils.cpi_supplemental_tables as mod

    real_date = mod.dateType

    class _FixedDate(real_date):
        @classmethod
        def today(cls):
            return real_date(2026, 5, 15)

    monkeypatch.setattr(mod, "dateType", _FixedDate)
    monkeypatch.setattr(cst, "list_supp_index", lambda: {"cpi-u": (date(2026, 4, 1),)})
    seen: list = []

    def _fake_fetch(stem, y, m):
        seen.append((y, m))
        return cst._XLSX_MAGIC if (y, m) == (2026, 3) else None

    monkeypatch.setattr(cst, "fetch_xlsx", _fake_fetch)
    y, m, _ = cst.discover_latest("cpi-u")
    assert (y, m) == (2026, 3)
    # (2026, 4) is in the index AND the walk-back; the dedup skip keeps it to one fetch.
    assert seen.count((2026, 4)) == 1


def test_parse_table_missing_sheet_raises():
    """A workbook lacking the spec's sheet raises OpenBBError."""
    spec = cst.TABLE_REGISTRY["cpi-u-us"]  # sheet == "US"
    content = _xlsx_bytes([["Indent Level", "x"]], sheet_title="Wrong")
    with pytest.raises(OpenBBError, match="no sheet named"):
        cst.parse_table(content, spec, 2026, 4)


def test_parse_table_no_header_raises():
    """A workbook with the right sheet but no Indent Level header raises."""
    spec = cst.TABLE_REGISTRY["cpi-u-us"]
    content = _xlsx_bytes([["nothing", "useful"], ["here", "either"]], sheet_title="US")
    with pytest.raises(OpenBBError, match="no 'Indent Level' header"):
        cst.parse_table(content, spec, 2026, 4)


def test_parse_table_sheetless_spec_uses_first_sheet():
    """A spec with ``sheet=None`` parses the workbook's first sheet."""
    spec = cst.TABLE_REGISTRY["c-cpi-u"]  # sheet is None
    rows = [
        ["C-CPI-U", None, None],
        ["Indent Level", "Item", "Unadjusted index"],
        [None, None, "Apr. 2026"],
        [0, "All items", 200.0],
    ]
    content = _xlsx_bytes(rows, sheet_title="Whatever")
    out = cst.parse_table(content, spec, 2026, 4)
    assert len(out) == 1
    assert out[0]["index_value"] == 200.0
    assert out[0]["date"] == date(2026, 4, 1)


def test_parse_table_full_pivot_and_edge_rows():
    """A rich CPI-U-US sheet exercises pivoting, footnotes, and every skip path."""
    spec = cst.TABLE_REGISTRY["cpi-u-us"]
    h1 = [
        "Indent Level",
        "Expenditure category",
        "Relative importance",
        "Unadjusted index",
        "Seasonally adjusted index",
        "Seasonally adjusted percent change",
        "Percent change to Apr. 2026 from:",
        None,
        None,
        "Pricing schedule",
        "Unadjusted index",
    ]
    h2 = [
        None,
        None,
        None,
        "Apr. 2026",
        "Apr. 2026",
        "Mar. 2026-Apr. 2026",
        "Apr. 2025",
        "Mar. 2026",
        "Feb. 2026",
        None,
        "garbage",  # unparseable period -> ("index_value", None) -> ref_date None skip
    ]
    rows = [
        ["CPI-U", None, None, None, None, None, None, None, None, None, None],
        h1,
        h2,
        # Full data row: pivots into a single Apr-2026 record; footnote (1) resolves.
        [0, "All items (1)", 100.0, 310.0, 311.0, 0.3, 2.5, 0.2, 0.4, "Monthly", 5.0],
        # Whitespace indent -> None; relative-importance only -> no-per_date record.
        ["  ", "Special item", 50.0, None, None, None, None, None, None, None, None],
        # Label present but no values / rel / pricing -> dropped.
        [None, "Empty row label", None, None, None, None, None, None, None, None, None],
        # Label cell None -> dropped.
        [2, None, 99.0, None, None, None, None, None, None, None, None],
        # Label strips to empty -> dropped.
        [3, "   ", 1.0, None, None, None, None, None, None, None, None],
        # Fully blank body row -> dropped.
        [None] * 11,
        # Trailing NOTE flips to footnote mode.
        [
            "NOTE: General note.",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
        # Blank row while in trailing -> skipped.
        [None] * 11,
        # Footnote definition.
        [
            "(1) December 1977=100 base.",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ],
    ]
    content = _xlsx_bytes(rows, sheet_title="US")
    out = cst.parse_table(content, spec, 2026, 4)
    assert len(out) == 2
    all_items = [r for r in out if r["label"] == "All items (1)"][0]
    assert all_items["date"] == date(2026, 4, 1)
    assert all_items["index_value"] == 310.0
    assert all_items["sa_index_value"] == 311.0
    assert all_items["pct_change_1m_sa"] == 0.3
    assert all_items["pct_change_12m"] == 2.5
    assert all_items["pct_change_1m_nsa"] == 0.2
    assert all_items["pct_change_window"] == 0.4
    assert all_items["pct_change_window_start_date"] == date(2026, 2, 1)
    assert all_items["relative_importance"] == 100.0
    assert all_items["pricing_schedule"] == "Monthly"
    assert all_items["footnote"] == "December 1977=100 base."
    special = [r for r in out if r["label"] == "Special item"][0]
    assert special["relative_importance"] == 50.0
    assert special["indent_level"] is None
    assert special["date"] == date(2026, 4, 1)


def test_parse_index_values_sheet_via_parse_table():
    """The historical index-values dispatch parses year × month grids."""
    spec = cst.TABLE_REGISTRY["historical-cpi-u-index"]  # sheet "Index values"
    h1 = [
        "Indent Level",
        "Year",
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    rows = [
        ["Historical CPI-U"] + [None] * 13,
        h1,
        [
            None,
            2025,
            300.0,
            301.0,
            302.0,
            303.0,
            304.0,
            305.0,
            306.0,
            307.0,
            308.0,
            309.0,
            310.0,
            311.0,
        ],
        [None, "notayear", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        [
            None,
            2024,
            None,
            200.0,
            201.0,
            202.0,
            203.0,
            204.0,
            205.0,
            206.0,
            207.0,
            208.0,
            209.0,
            210.0,
        ],
        [None] * 14,
        ["NOTE: monthly base."] + [None] * 13,
    ]
    content = _xlsx_bytes(rows, sheet_title="Index values")
    out = cst.parse_table(content, spec, 2026, 5)
    jan_2025 = [r for r in out if r["date"] == date(2025, 1, 1)][0]
    assert jan_2025["index_value"] == 300.0
    assert jan_2025["label"] == "All items"
    # The bad-year row contributes nothing; the None January 2024 cell is skipped.
    assert not [r for r in out if r["date"] == date(2024, 1, 1)]
    assert [r for r in out if r["date"] == date(2024, 2, 1)]


def test_parse_index_values_sheet_no_header_returns_empty():
    """An index-values sheet without an Indent Level header yields no rows."""
    spec = cst.TABLE_REGISTRY["historical-cpi-u-index"]
    content = _xlsx_bytes(
        [["no", "header"], ["here", "either"]], sheet_title="Index values"
    )
    assert cst.parse_table(content, spec, 2026, 5) == []


def test_parse_index_averages_sheet_via_parse_table():
    """The historical index-averages dispatch classifies semiannual/annual columns."""
    spec = cst.TABLE_REGISTRY["historical-cpi-u-averages"]  # sheet "Index averages"
    h1 = [
        "Indent Level",
        "Year",
        "Semiannual",
        "Semiannual",
        "Semiannual",
        "Annual avg",
        "Percent change from previous",
        "Percent change from previous",
        "Percent change from previous",
        "Mystery header",  # matches no branch -> outer else
    ]
    h2 = [
        None,
        None,
        "1st half",
        "2nd half",
        "garbage",
        None,
        "Dec.",
        "Annual avg",
        "Other",
        None,
    ]
    rows = [
        ["Historical CPI-U averages"] + [None] * 9,
        h1,
        h2,
        [None, 2025, 100.0, 101.0, 102.0, 103.0, 2.1, 2.2, 9.9, 8.8],
        [None, "notayear", 1, 2, 3, 4, 5, 6, 7, 8],
        [None, 2024, None, None, None, None, None, None, None, None],
        [None] * 10,
        ["NOTE: averages base."] + [None] * 9,
    ]
    content = _xlsx_bytes(rows, sheet_title="Index averages")
    out = cst.parse_table(content, spec, 2026, 5)
    # 6 classified columns for 2025: two semiannual halves + half-None + annual
    # index + Dec pct-change + annual-avg pct-change.
    rec_2025 = [r for r in out if r["snapshot_date"] == date(2026, 5, 1)]
    assert len(rec_2025) == 6
    jan_1st = [r for r in out if r["date"] == date(2025, 1, 1) and r["half"] == "1st"][
        0
    ]
    assert jan_1st["index_value"] == 100.0
    assert jan_1st["frequency"] == "semiannual"
    dec_pct = [r for r in out if r["date"] == date(2025, 12, 1)][0]
    assert dec_pct["pct_change_12m"] == 2.1


def test_parse_index_averages_sheet_no_header_returns_empty():
    """An index-averages sheet without an Indent Level header yields no rows."""
    spec = cst.TABLE_REGISTRY["historical-cpi-u-averages"]
    content = _xlsx_bytes([["x", "y"], ["a", "b"]], sheet_title="Index averages")
    assert cst.parse_table(content, spec, 2026, 5) == []
