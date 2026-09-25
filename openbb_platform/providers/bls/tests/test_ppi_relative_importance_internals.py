"""Unit tests for BLS PPI Relative Importance parser internals."""

from __future__ import annotations

from datetime import date

import pytest

import openbb_bls.models.ppi_relative_importance as pri


def test_detect_header_row_found():
    """_detect_header_row returns the header list + next data index."""
    rows = [
        ("note", None),
        ("Group code", "Item code", "Index", "Dec. 2024"),
        (0, "00", "All commodities", 100.0),
    ]
    headers, data_start = pri._detect_header_row(rows)
    assert headers[1] == "Item code"
    assert data_start == 2


def test_detect_header_row_not_found():
    """_detect_header_row returns ([], 0) when no header row exists."""
    rows = [("a", "b"), ("c", "d")]
    assert pri._detect_header_row(rows) == ([], 0)


def test_detect_value_cols():
    """_detect_value_cols maps year-bearing headers to December reference dates."""
    headers = ["Group code", "Item code", "Index", "Dec. 2023", "Dec. 2024"]
    cols = pri._detect_value_cols(headers)
    assert cols == [(3, date(2023, 12, 1)), (4, date(2024, 12, 1))]


def test_first_label_col_found_and_missing():
    """_first_label_col finds the Index column, else None."""
    assert pri._first_label_col(["Code", "Index", "Dec. 2024"]) == 1
    assert pri._first_label_col(["Code", "Title", "Dec. 2024"]) is None


def test_row_to_records_empty_row_or_no_value_cols():
    """_row_to_records short-circuits on empty rows / no value columns."""
    assert pri._row_to_records((), [], set(), None, [], "t", "n") == []
    assert pri._row_to_records((1, 2), [], set(), None, [], "t", "n") == []


def test_row_to_records_code_index_out_of_range_and_blank():
    """Code-column scan skips out-of-range and blank/non-string cells."""
    headers = ["Group code", "Item code", "Index", "Dec. 2024"]
    value_cols = [(3, date(2024, 12, 1))]
    # code_col_indices includes an out-of-range index (9) and a blank cell (0)
    row = ("   ", "01", "Farm products", 12.5)
    records = pri._row_to_records(
        row, headers, {9, 0, 1}, 2, value_cols, "ppi-x", "label"
    )
    assert len(records) == 1
    assert records[0]["code"] == "01"
    assert records[0]["label"] == "Farm products"
    assert records[0]["relative_importance"] == 12.5
    assert records[0]["date"] == date(2024, 12, 1)


def test_row_to_records_value_parsing_paths():
    """Value parsing skips out-of-range, None, blank, dash, and non-numeric cells."""
    headers = ["Code", "Index", "Dec. 2023", "Dec. 2024", "Dec. 2025"]
    # cols 2,3,4 + an out-of-range col 9
    value_cols = [
        (2, date(2023, 12, 1)),
        (3, date(2024, 12, 1)),
        (4, date(2025, 12, 1)),
        (9, date(2099, 12, 1)),
    ]
    row = ("00", "All commodities", "-", "not-a-number", 7.5)
    records = pri._row_to_records(row, headers, {0}, 1, value_cols, "ppi-x", "label")
    # Only the numeric 7.5 (Dec 2025) survives.
    assert len(records) == 1
    assert records[0]["relative_importance"] == 7.5
    assert records[0]["date"] == date(2025, 12, 1)


def test_row_to_records_code_index_only_out_of_range():
    """When the only code column is out of range, code stays None."""
    headers = ["Code", "Index", "Dec. 2024"]
    value_cols = [(2, date(2024, 12, 1))]
    row = ("00", "All commodities", 5.0)
    # Sole code index (9) is past the row length → code remains None, but the
    # label still carries the row, so a record is produced.
    records = pri._row_to_records(row, headers, {9}, 1, value_cols, "t", "n")
    assert len(records) == 1
    assert records[0]["code"] is None
    assert records[0]["label"] == "All commodities"


def test_row_to_records_non_numeric_value_skipped():
    """A value cell that is neither str / int / float is skipped."""
    from datetime import datetime

    headers = ["Code", "Index", "Dec. 2024", "Dec. 2025"]
    value_cols = [(2, date(2024, 12, 1)), (3, date(2025, 12, 1))]
    row = ("00", "All commodities", datetime(2024, 1, 1), 9.0)
    records = pri._row_to_records(row, headers, {0}, 1, value_cols, "t", "n")
    assert len(records) == 1
    assert records[0]["relative_importance"] == 9.0


def test_row_to_records_no_value_returns_empty():
    """A row with no numeric values yields no records."""
    headers = ["Code", "Index", "Dec. 2024"]
    value_cols = [(2, date(2024, 12, 1))]
    row = ("00", "All commodities", None)
    assert pri._row_to_records(row, headers, {0}, 1, value_cols, "t", "n") == []


def test_row_to_records_no_code_no_label_returns_empty():
    """A row with values but neither code nor label is dropped."""
    headers = ["Code", "Index", "Dec. 2024"]
    value_cols = [(2, date(2024, 12, 1))]
    # code blank, label blank, but a value present
    row = (None, None, 5.0)
    assert pri._row_to_records(row, headers, {0}, 1, value_cols, "t", "n") == []


def test_row_to_records_int_value_coerced():
    """Integer cells are coerced to float."""
    headers = ["Code", "Index", "Dec. 2024"]
    value_cols = [(2, date(2024, 12, 1))]
    row = ("00", "All commodities", 100)
    records = pri._row_to_records(row, headers, {0}, 1, value_cols, "t", "n")
    assert records[0]["relative_importance"] == 100.0


def test_fetch_xlsx_table_non_200_raises(monkeypatch):
    """_fetch_xlsx_table surfaces non-200 responses as OpenBBError."""
    from openbb_core.app.model.abstract.error import OpenBBError

    class _Resp:
        status_code = 500
        content = b""

    monkeypatch.setattr(
        pri,
        "requests",
        type("_R", (), {"get": staticmethod(lambda *a, **k: _Resp())}),
        raising=False,
    )

    # _fetch_xlsx_table does `import requests` inside; patch the shared module.
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
    with pytest.raises(OpenBBError, match="HTTP 500"):
        pri._fetch_xlsx_table("ppi-fdallrel", "https://x", "label")


def test_fetch_xlsx_table_no_header_returns_empty(monkeypatch):
    """A workbook whose first sheet lacks a header row yields no rows."""
    import io

    import openpyxl
    import requests

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["just", "some", "noise"])
    ws.append(["more", "noise", "here"])
    buf = io.BytesIO()
    wb.save(buf)

    class _Resp:
        status_code = 200
        content = buf.getvalue()

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp())
    result = pri._fetch_xlsx_table("ppi-fdallrel", "https://x", "label")
    assert result == {"rows": [], "table_id": "ppi-fdallrel", "table_name": "label"}


def test_transform_data_empty_raises():
    """transform_data raises EmptyDataError on an empty row set."""
    from openbb_core.provider.utils.errors import EmptyDataError

    fetcher = pri.BlsPpiRelativeImportanceFetcher
    query = fetcher.transform_query({"category": "final_demand"})
    with pytest.raises(EmptyDataError):
        fetcher.transform_data(query, {"rows": [], "table_id": "ppi-fdallrel"})
