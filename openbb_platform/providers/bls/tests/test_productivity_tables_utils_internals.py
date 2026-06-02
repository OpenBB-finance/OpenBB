"""Unit tests for ``openbb_bls.utils.productivity_tables`` internals."""

from __future__ import annotations

import io
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openpyxl import Workbook

from openbb_bls.utils import productivity_tables as pt


@pytest.fixture(autouse=True)
def _clear_fetch_xlsx_cache():
    """Clear the memoised workbook download around every test for isolation."""
    pt.fetch_xlsx.cache_clear()
    yield
    pt.fetch_xlsx.cache_clear()


class _FakeResp:
    """Minimal ``requests.Response`` stand-in."""

    def __init__(self, content: bytes = b"", status_code: int = 200):
        self.content = content
        self.status_code = status_code


def _multi_sheet_xlsx(sheets: dict[str, list[list]]) -> bytes:
    """Build an XLSX byte payload from a mapping of sheet name to row lists."""
    wb = Workbook()
    default = wb.active
    first = True
    for name, rows in sheets.items():
        if first:
            ws = default
            ws.title = name
            first = False
        else:
            ws = wb.create_sheet(name)
        for row in rows:
            ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_fetch_xlsx_non_200_raises(monkeypatch):
    """A non-200 response raises OpenBBError."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        pt.fetch_xlsx("x.xlsx")


def test_fetch_xlsx_non_xlsx_raises(monkeypatch):
    """A 200 response without XLSX magic bytes raises OpenBBError."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(content=b"<html>"))
    with pytest.raises(OpenBBError, match="non-XLSX content"):
        pt.fetch_xlsx("x.xlsx")


def test_fetch_xlsx_valid_returns_content(monkeypatch):
    """A valid XLSX payload is returned verbatim."""
    import requests

    payload = pt._XLSX_MAGIC + b"data"
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp(content=payload))
    assert pt.fetch_xlsx("x.xlsx") == payload


def test_fetch_xlsx_is_memoised(monkeypatch):
    """Repeated downloads of the same workbook hit the network only once."""
    import requests

    calls = {"n": 0}

    def _get(*a, **k):
        calls["n"] += 1
        return _FakeResp(content=pt._XLSX_MAGIC + b"data")

    monkeypatch.setattr(requests, "get", _get)
    first = pt.fetch_xlsx("memo.xlsx")
    second = pt.fetch_xlsx("memo.xlsx")
    assert first == second
    assert calls["n"] == 1


def test_parse_value_all_branches():
    """``_parse_value`` handles None, bool, numeric, blank, numeric-str, text."""
    assert pt._parse_value(None) == (None, None)
    assert pt._parse_value(True) == (1.0, "True")
    assert pt._parse_value(5) == (5.0, None)
    assert pt._parse_value("  ") == (None, None)
    assert pt._parse_value("1,234.5") == (1234.5, None)
    assert pt._parse_value("abc") == (None, "abc")


def test_quarter_to_date_branches():
    """``_quarter_to_date`` covers None/bad year, annual, bad/oob qtr, valid Q."""
    assert pt._quarter_to_date(None, 1) == (None, "unknown")
    assert pt._quarter_to_date("notyear", 1) == (None, "unknown")
    assert pt._quarter_to_date(2025, "Annual") == (date(2025, 1, 1), "annual")
    assert pt._quarter_to_date(2025, "xyz") == (date(2025, 1, 1), "unknown")
    assert pt._quarter_to_date(2025, 5) == (date(2025, 1, 1), "unknown")
    assert pt._quarter_to_date(2025, 3) == (date(2025, 7, 1), "Q3")


def test_detect_release_date_found():
    """A 'Data released ...' string yields the parsed date."""
    rows = [("Data released May 1, 2026",)]
    assert pt._detect_release_date(rows) == date(2026, 5, 1)


def test_detect_release_date_skips_non_str_and_no_match():
    """Non-string cells and non-matching strings are skipped, returning None."""
    rows = [(123, "no date here"), ("still nothing",)]
    assert pt._detect_release_date(rows) is None


def test_detect_release_date_bad_month_returns_none():
    """An unrecognised month name is skipped, returning None."""
    rows = [("Data released Xyz 1, 2026",)]
    assert pt._detect_release_date(rows) is None


def test_detect_release_date_invalid_day_returns_none():
    """A regex match with an out-of-range day surfaces as None."""
    rows = [("Data released May 99, 2026",)]
    assert pt._detect_release_date(rows) is None


def test_parse_cycle_period_branches():
    """``_parse_cycle_period`` covers valid, no-match, and invalid-year paths."""
    assert pt._parse_cycle_period("1948 Q4 - 1953 Q2") == (
        date(1948, 10, 1),
        date(1953, 4, 1),
    )
    assert pt._parse_cycle_period("no cycle here") == (None, None)
    # Year 0 matches the regex but is out of range for ``date`` -> ValueError.
    assert pt._parse_cycle_period("0000 Q4 - 0000 Q2") == (None, None)


def test_parse_machine_readable_empty_returns_empty():
    """No rows yields an empty list."""
    assert pt._parse_machine_readable([], "major-sectors-quarterly", None, "f") == []


def test_parse_machine_readable_missing_column_raises():
    """A header missing a required column raises OpenBBError."""
    rows = [("Sector", "Basis", "Measure", "Units", "Year", "Qtr")]  # no Value
    with pytest.raises(OpenBBError, match="missing an expected column"):
        pt._parse_machine_readable(rows, "major-sectors-quarterly", None, "f")


def test_parse_machine_readable_quarterly_filters_annual():
    """Quarterly dataset keeps Q-periods and drops annual rows; component resolved."""
    rows = [
        ("Sector", "Basis", "Measure", "Units", "Year", "Qtr", "Value", "Component"),
        ("NFB", "OPH", "Labor productivity", "Index", 2025, 1, 112.5, "C1"),
        ("NFB", "OPH", "Labor productivity", "Index", 2025, "Annual", 113.0, "C1"),
        (None, None, None, None, None, None, None, None),
    ]
    out = pt._parse_machine_readable(
        rows, "major-sectors-quarterly", date(2026, 5, 1), "f.xlsx"
    )
    assert len(out) == 1
    rec = out[0]
    assert rec["period_kind"] == "Q1"
    assert rec["year"] == 2025
    assert rec["quarter"] == 1
    assert rec["component"] == "C1"
    assert rec["value"] == 112.5
    assert rec["release_date"] == date(2026, 5, 1)


def test_parse_machine_readable_annual_filters_quarterly():
    """Annual dataset keeps only annual rows; quarter retains the string token."""
    rows = [
        ("Sector", "Basis", "Measure", "Units", "Year", "Qtr", "Value", "Component"),
        ("NFB", "OPH", "Labor productivity", "Index", 2025, 1, 112.5, "C1"),
        ("NFB", "OPH", "Labor productivity", "Index", 2025, "Annual", 113.0, "C1"),
    ]
    out = pt._parse_machine_readable(rows, "major-sectors-annual", None, "f.xlsx")
    assert len(out) == 1
    assert out[0]["period_kind"] == "annual"
    assert out[0]["quarter"] == "Annual"


def test_parse_machine_readable_any_keeps_all_and_component_none():
    """'any' keep mode keeps all rows; missing Component column yields None."""
    rows = [
        ("Sector", "Basis", "Measure", "Units", "Year", "Qtr", "Value"),
        ("Total", "Hours", "Hours worked", "Index", "2025", 2, 100.0),
        ("Total", "Hours", "Hours worked", "Index", 2024, None, None),
    ]
    out = pt._parse_machine_readable(
        rows, "total-economy-hours-employment", None, "f.xlsx"
    )
    assert len(out) == 2
    first, second = out
    # String year is not coerced into the int year field.
    assert first["year"] is None
    assert first["quarter"] == 2
    assert first["component"] is None
    assert first["value"] == 100.0
    # None quarter stays None; missing value stays None.
    assert second["year"] == 2024
    assert second["quarter"] is None
    assert second["value"] is None


def test_parse_business_cycles_missing_header_raises():
    """A BusinessCycles sheet without a 'Sector' header row raises."""
    rows = [("title",), ("foo", "bar")]
    with pytest.raises(OpenBBError, match="missing the 'Sector' header"):
        pt._parse_business_cycles(rows, "major-sectors-business-cycles")


def test_parse_business_cycles_no_cycle_headers_raises():
    """A 'Sector' header with no cycle columns raises."""
    rows = [
        ("Sector", "Basis", "Measure", "Units"),
        ("NFB", "x", "y", "z"),
    ]
    with pytest.raises(OpenBBError, match="no business-cycle column headers"):
        pt._parse_business_cycles(rows, "major-sectors-business-cycles")


def test_parse_business_cycles_full():
    """A BusinessCycles grid pivots wide cycle columns into long records."""
    rows = [
        ("Title Data released June 2, 2026", None, None, None, None, None, None, None),
        # Spacer columns (None / blank) between real cycle headers are skipped.
        (
            "Sector",
            "Basis",
            "Measure",
            "Units",
            "1948 Q4 - 1953 Q2",
            None,
            "  ",
            "1953 Q2 - 1957 Q3",
        ),
        (
            "Nonfarm business",
            "OPH",
            "Labor productivity",
            "Index",
            2.5,
            None,
            None,
            3.1,
        ),
        (None, None, None, None, None, None, None, None),  # all-None row skipped
        ("", "", "", "", None, None, None, None),  # blank sector skipped
        (
            "Data released line",
            "x",
            "y",
            "z",
            1.0,
            None,
            None,
            2.0,
        ),  # 'data released' skipped
        (
            "Manufacturing",
            "B2",
            "M2",
            "U2",
            None,
            None,
            None,
            4.0,
        ),  # col4 None, col7 kept
    ]
    out = pt._parse_business_cycles(rows, "major-sectors-business-cycles")
    assert len(out) == 3
    first = out[0]
    assert first["sector"] == "Nonfarm business"
    assert first["period_kind"] == "business_cycle"
    assert first["cycle_period"] == "1948 Q4 - 1953 Q2"
    assert first["cycle_start_date"] == date(1948, 10, 1)
    assert first["cycle_end_date"] == date(1953, 4, 1)
    assert first["release_date"] == date(2026, 6, 2)
    mfg = [r for r in out if r["sector"] == "Manufacturing"]
    assert len(mfg) == 1
    assert mfg[0]["value"] == 4.0


def test_parse_dataset_sheet_missing_raises():
    """A workbook lacking the dataset's sheet raises OpenBBError."""
    content = _multi_sheet_xlsx({"Other": [["x"]]})
    with pytest.raises(OpenBBError, match="does not contain a 'MachineReadable'"):
        pt.parse_dataset(content, "major-sectors-quarterly")


def test_parse_dataset_quarterly_detects_release_and_filters():
    """Quarterly dispatch detects the release date and drops annual rows."""
    content = _multi_sheet_xlsx(
        {
            "MachineReadable": [
                [
                    "Sector",
                    "Basis",
                    "Measure",
                    "Units",
                    "Year",
                    "Qtr",
                    "Value",
                    "Component",
                ],
                ["NFB", "OPH", "Labor productivity", "Index", 2025, 1, 112.5, "C1"],
                [
                    "NFB",
                    "OPH",
                    "Labor productivity",
                    "Index",
                    2025,
                    "Annual",
                    113.0,
                    "C1",
                ],
            ],
            "Quarterly": [["Quarterly series. Data released May 1, 2026."]],
            "Annual": [["Annual series."]],
        }
    )
    out = pt.parse_dataset(content, "major-sectors-quarterly")
    assert len(out) == 1
    assert out[0]["release_date"] == date(2026, 5, 1)
    assert out[0]["period_kind"] == "Q1"


def test_parse_dataset_total_economy_no_release_date():
    """Total-economy dispatch has no Quarterly/Annual sheets, so release is None."""
    content = _multi_sheet_xlsx(
        {
            "MachineReadable": [
                ["Sector", "Basis", "Measure", "Units", "Year", "Qtr", "Value"],
                ["Total", "Hours", "Hours worked", "Index", 2025, 2, 100.0],
            ]
        }
    )
    out = pt.parse_dataset(content, "total-economy-hours-employment")
    assert len(out) == 1
    assert out[0]["release_date"] is None


def test_parse_dataset_business_cycles_dispatch():
    """Business-cycles dispatch routes to the wide→long parser."""
    content = _multi_sheet_xlsx(
        {
            "BusinessCycles": [
                ["Title Data released June 2, 2026", None, None, None, None],
                ["Sector", "Basis", "Measure", "Units", "1948 Q4 - 1953 Q2"],
                ["NFB", "OPH", "Labor productivity", "Index", 2.5],
            ]
        }
    )
    out = pt.parse_dataset(content, "major-sectors-business-cycles")
    assert len(out) == 1
    assert out[0]["period_kind"] == "business_cycle"
    assert out[0]["cycle_start_date"] == date(1948, 10, 1)
