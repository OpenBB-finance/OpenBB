"""Internal-branch tests for ``openbb_bls.models.cpi_seasonal_factors``."""

from __future__ import annotations

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.cpi_seasonal_factors as csf_mod


class _Resp:
    """Stand-in for ``requests.Response`` used by ``_fetch_sa_xlsx`` tests."""

    def __init__(self, status_code, content=b""):
        self.status_code = status_code
        self.content = content


def test_sa_url_builds_canonical_path():
    """``_sa_url`` interpolates the year into the canonical CPI SA URL."""
    assert csf_mod._sa_url(2025).endswith(
        "revised-seasonally-adjusted-indexes-2025.xlsx"
    )


def test_to_float_returns_none_for_blank_and_dash():
    """``_to_float`` returns ``None`` for empty / dash sentinels."""
    assert csf_mod._to_float(None) is None
    assert csf_mod._to_float("") is None
    assert csf_mod._to_float("-") is None
    assert csf_mod._to_float("not-a-number") is None


def test_to_float_passes_numeric_through():
    """``_to_float`` returns floats for both numeric inputs and parseable strings."""
    assert csf_mod._to_float(3) == 3.0
    assert csf_mod._to_float(2.5) == 2.5
    assert csf_mod._to_float("4.25") == 4.25


def test_fetch_sa_xlsx_returns_none_on_redirect(monkeypatch):
    """``_fetch_sa_xlsx`` returns ``None`` when BLS redirects (301/302/etc) or 404s."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(302))
    assert csf_mod._fetch_sa_xlsx(2025) is None


def test_fetch_sa_xlsx_raises_on_unexpected_status(monkeypatch):
    """Non-200 / non-redirect status codes raise ``OpenBBError``."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        csf_mod._fetch_sa_xlsx(2025)


def test_fetch_sa_xlsx_returns_none_when_payload_is_not_xlsx(monkeypatch):
    """A 200 response without the PK\\x03\\x04 magic bytes is treated as missing."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(200, b"<html></html>"))
    assert csf_mod._fetch_sa_xlsx(2025) is None


def test_fetch_sa_xlsx_returns_bytes_for_valid_payload(monkeypatch):
    """A 200 with the XLSX magic is returned verbatim."""
    import requests

    payload = b"PK\x03\x04hello"
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(200, payload))
    assert csf_mod._fetch_sa_xlsx(2025) == payload


def test_discover_latest_sa_returns_first_match(monkeypatch):
    """``_discover_latest_sa`` returns the first year whose fetch yields bytes."""
    monkeypatch.setattr(
        csf_mod, "_fetch_sa_xlsx", lambda y: b"PK\x03\x04" if y == 2025 else None
    )
    from datetime import date as _date

    class _Today:
        @staticmethod
        def today():
            return _date(2026, 1, 1)

    monkeypatch.setattr(csf_mod, "dateType", _Today)
    year, content = csf_mod._discover_latest_sa()
    assert year == 2025
    assert content.startswith(b"PK\x03\x04")


def test_discover_latest_sa_raises_when_nothing_published(monkeypatch):
    """``_discover_latest_sa`` raises when the six-year walk-back returns nothing."""
    monkeypatch.setattr(csf_mod, "_fetch_sa_xlsx", lambda _y: None)
    with pytest.raises(OpenBBError, match="Could not locate"):
        csf_mod._discover_latest_sa()


def test_extract_data_with_explicit_year_calls_fetch(monkeypatch, fixture_bytes):
    """Explicit ``year`` triggers ``_fetch_sa_xlsx`` rather than discovery."""
    monkeypatch.setattr(
        csf_mod,
        "_fetch_sa_xlsx",
        lambda y: fixture_bytes("cpi_seasonal_factors_2025.xlsx"),
    )
    query = csf_mod.BlsCpiSeasonalFactorsQueryParams(year=2025)
    out = csf_mod.BlsCpiSeasonalFactorsFetcher.extract_data(query, None)
    assert out["rows"], "should parse rows from the fixture"


def test_extract_data_raises_when_explicit_year_missing(monkeypatch):
    """Explicit ``year`` with no published XLSX raises ``OpenBBError``."""
    monkeypatch.setattr(csf_mod, "_fetch_sa_xlsx", lambda _y: None)
    query = csf_mod.BlsCpiSeasonalFactorsQueryParams(year=2099)
    with pytest.raises(OpenBBError, match="not found"):
        csf_mod.BlsCpiSeasonalFactorsFetcher.extract_data(query, None)


def test_transform_data_raises_for_empty_rows():
    """``transform_data`` raises ``EmptyDataError`` for empty rows."""
    query = csf_mod.BlsCpiSeasonalFactorsQueryParams()
    with pytest.raises(EmptyDataError, match="No rows parsed"):
        csf_mod.BlsCpiSeasonalFactorsFetcher.transform_data(
            query, {"rows": [], "table_id": "tid"}
        )


# --------------------------------------------------------------------------
# _parse_sa_xlsx edge cases via tiny in-memory workbooks
# --------------------------------------------------------------------------


def _build_sa_workbook(rows) -> bytes:
    """Build a one-sheet XLSX whose values come from the given row tuples."""
    import io

    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_parse_sa_xlsx_returns_empty_when_item_header_absent():
    """``_parse_sa_xlsx`` returns no rows if it cannot find an ``ITEM`` header."""
    content = _build_sa_workbook([("NOT", "A", "HEADER")])
    out = csf_mod._parse_sa_xlsx(content, 2025)
    assert out["rows"] == []


def test_parse_sa_xlsx_returns_empty_when_required_column_missing():
    """``_parse_sa_xlsx`` bails when required ``TITLE``/``SERIESID``/etc cols are missing."""
    content = _build_sa_workbook(
        [
            ("ITEM", "JUNK", "JUNK2"),
            ("AA", "stuff", "more"),
        ]
    )
    out = csf_mod._parse_sa_xlsx(content, 2025)
    assert out["rows"] == []


def test_parse_sa_xlsx_returns_empty_when_month_columns_incomplete():
    """``_parse_sa_xlsx`` bails when fewer than 12 month columns are detected."""
    header = ["ITEM", "TITLE", "SERIESID", "DATA_TYPE", "YEAR", "JAN", "FEB"]
    content = _build_sa_workbook(
        [tuple(header), ("AA", "t", "sid", "FACTOR", 2025, 1.0, 1.1)]
    )
    out = csf_mod._parse_sa_xlsx(content, 2025)
    assert out["rows"] == []


def test_parse_sa_xlsx_skips_rows_with_bad_year_or_no_data_type():
    """Body rows with un-parseable ``YEAR`` cells and rows whose ``DATA_TYPE`` is None are skipped."""
    months = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]
    header = ["ITEM", "TITLE", "SERIESID", "DATA_TYPE", "YEAR", *months]
    rows = [tuple(header)]
    # Bad year string:
    rows.append(("AA", "t", "sid", "INDEX", "not-a-year", *([1.0] * 12)))
    # DATA_TYPE is None — skipped:
    rows.append(("BB", "t", "sid", None, 2025, *([1.0] * 12)))
    # None item — skipped:
    rows.append((None, "t", "sid", "INDEX", 2025, *([1.0] * 12)))
    # Valid row to keep:
    rows.append(("CC", "Title C", "SIDC", "INDEX", 2025, *([2.0] * 12)))
    # FACTOR row whose values are all None — no observations produced:
    rows.append(("DD", "Title D", "SIDD", "FACTOR", 2025, *([None] * 12)))
    content = _build_sa_workbook(rows)
    out = csf_mod._parse_sa_xlsx(content, 2025)
    items = {r["item_code"] for r in out["rows"]}
    # CC should produce 12 months of index values; DD has no values at all
    # and AA/BB/None were skipped before reaching the per-month pivot.
    assert items == {"CC"}
    assert len([r for r in out["rows"] if r["item_code"] == "CC"]) == 12
