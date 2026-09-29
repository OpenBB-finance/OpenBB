"""Unit tests for BLS CPI News Release parser internals."""

from __future__ import annotations

from datetime import date

import pytest

import openbb_bls.models.cpi_news_release as nr


class _Resp:
    """Minimal requests.Response stand-in."""

    def __init__(self, status_code=200, content=b""):
        self.status_code = status_code
        self.content = content


def test_nr_url_format():
    """_nr_url builds the canonical supplemental-files URL."""
    url = nr._nr_url(2026, 4, 1)
    assert url.endswith("news-release-table1-202604.xlsx")


def test_fetch_nr_xlsx_redirect_returns_none(monkeypatch):
    """A redirect status yields None (file not published)."""
    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(status_code=302))
    assert nr._fetch_nr_xlsx(2026, 4, 1) is None


def test_fetch_nr_xlsx_non_200_raises(monkeypatch):
    """A non-200 / non-redirect status raises OpenBBError."""
    import requests
    from openbb_core.app.model.abstract.error import OpenBBError

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        nr._fetch_nr_xlsx(2026, 4, 1)


def test_fetch_nr_xlsx_non_xlsx_returns_none(monkeypatch):
    """A 200 response without the XLSX magic bytes yields None."""
    import requests

    monkeypatch.setattr(
        requests, "get", lambda *a, **k: _Resp(content=b"<html>not xlsx")
    )
    assert nr._fetch_nr_xlsx(2026, 4, 1) is None


def test_fetch_nr_xlsx_valid_returns_bytes(monkeypatch):
    """A 200 response with the PK magic returns the content."""
    import requests

    payload = b"PK\x03\x04rest-of-xlsx"
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(content=payload))
    assert nr._fetch_nr_xlsx(2026, 4, 1) == payload


def test_discover_latest_nr_walks_back(monkeypatch):
    """_discover_latest_nr returns the first month that yields content."""
    calls = {"n": 0}

    def _fake(year, month, table):
        calls["n"] += 1
        return b"PK\x03\x04" if calls["n"] == 2 else None

    monkeypatch.setattr(nr, "_fetch_nr_xlsx", _fake)
    monkeypatch.setattr(nr, "dateType", nr.dateType)
    year, month, content = nr._discover_latest_nr(1)
    assert content == b"PK\x03\x04"


def test_discover_latest_nr_year_rollover(monkeypatch):
    """The walk-back rolls the year over when month hits zero."""

    class _FakeDate:
        @staticmethod
        def today():
            return date(2026, 1, 1)

    monkeypatch.setattr(nr, "dateType", _FakeDate)
    seen: list[tuple[int, int]] = []

    def _fake(year, month, table):
        seen.append((year, month))
        return b"PK\x03\x04" if (year, month) == (2025, 12) else None

    monkeypatch.setattr(nr, "_fetch_nr_xlsx", _fake)
    year, month, _ = nr._discover_latest_nr(1)
    assert (year, month) == (2025, 12)
    assert (2025, 12) in seen


def test_discover_latest_nr_exhausted_raises(monkeypatch):
    """Six misses raise OpenBBError."""
    from openbb_core.app.model.abstract.error import OpenBBError

    monkeypatch.setattr(nr, "_fetch_nr_xlsx", lambda *a, **k: None)
    with pytest.raises(OpenBBError, match="within the"):
        nr._discover_latest_nr(1)


def test_fetch_and_parse_missing_month_raises(monkeypatch):
    """_fetch_and_parse raises when the explicit month is not published."""
    from openbb_core.app.model.abstract.error import OpenBBError

    monkeypatch.setattr(nr, "_fetch_nr_xlsx", lambda *a, **k: None)
    with pytest.raises(OpenBBError, match="was not found"):
        nr._fetch_and_parse(1, date(2026, 4, 1))


@pytest.mark.parametrize(
    "raw,expected",
    [(None, None), (5, 5.0), ("", None), ("-", None), ("x", None), ("3.2", 3.2)],
)
def test_to_float(raw, expected):
    """_to_float coerces numerics, mapping blanks / sentinels / junk to None."""
    assert nr._to_float(raw) == expected


def test_clean_header():
    """_clean_header collapses newlines / whitespace; None yields empty string."""
    assert nr._clean_header(None) == ""
    assert nr._clean_header("Apr.\n2026") == "Apr. 2026"


def test_parse_single_period_paths():
    """_parse_single_period handles valid, no-match, and bad-month inputs."""
    assert nr._parse_single_period("Apr. 2026", 2026) == date(2026, 4, 1)
    assert nr._parse_single_period("no date", 2026) is None
    assert nr._parse_single_period("Zzz 2026", 2026) is None


def test_parse_range_period_paths():
    """_parse_range_period handles valid range, no-match, and bad-month."""
    rng = nr._parse_range_period("Mar. 2026-Apr. 2026")
    assert rng == (date(2026, 3, 1), date(2026, 4, 1))
    assert nr._parse_range_period("no range") is None
    assert nr._parse_range_period("Zzz 2026-Apr. 2026") is None
    # start year omitted → inherits end year
    rng2 = nr._parse_range_period("Jan.-Apr. 2026")
    assert rng2 == (date(2026, 1, 1), date(2026, 4, 1))


def test_parse_to_from_super_paths():
    """_parse_to_from_super extracts the 'to' anchor or returns None."""
    assert nr._parse_to_from_super("Percent change to Apr. 2026 from:") == date(
        2026, 4, 1
    )
    assert nr._parse_to_from_super("no anchor here") is None
    assert nr._parse_to_from_super("Percent change to Zzz 2026 from:") is None


def test_parse_month_year_label_paths():
    """_parse_month_year_label parses 'Month YYYY' labels or returns None."""
    assert nr._parse_month_year_label("December 2013") == date(2013, 12, 1)
    assert nr._parse_month_year_label("not a label") is None
    assert nr._parse_month_year_label("Zzz 2013") is None


def test_parse_nr_footnotes():
    """_parse_nr_footnotes maps (N) markers to text, skipping junk rows."""
    rows = [
        (),
        (None, 42),
        ("", "(1) Not seasonally adjusted."),
        ("(2) Indexes on a December 2024=100 base.",),
    ]
    out = nr._parse_nr_footnotes(rows)
    assert out["(1)"] == "Not seasonally adjusted."
    assert out["(2)"].startswith("Indexes")


def test_resolve_nr_footnotes_paths():
    """_resolve_nr_footnotes returns None when no markers or no footnotes."""
    assert nr._resolve_nr_footnotes(None, {"(1)": "x"}) is None
    assert nr._resolve_nr_footnotes("All items", {}) is None
    assert nr._resolve_nr_footnotes("All items", {"(1)": "x"}) is None
    # Duplicate markers dedupe; unknown markers skipped.
    text = nr._resolve_nr_footnotes("Food(1)(1)(9)", {"(1)": "note one"})
    assert text == "note one"


def test_find_pricing_schedule_col():
    """_find_pricing_schedule_col locates the column or returns None."""
    assert (
        nr._find_pricing_schedule_col(("Indent", "Area", "Pricing Schedule"), ()) == 2
    )
    assert nr._find_pricing_schedule_col(("Indent", "Area"), ()) is None


def test_classify_columns_branches():
    """_classify_columns covers every header-classification branch."""
    super_row = (
        "Indent Level",  # 0 → None
        "Expenditure category",  # 1 → None (label col)
        "Relative importance",  # relative_importance
        "Unadjusted indexes",  # index_nsa
        "Seasonally adjusted percent change",  # 1m SA
        "Percent change to Apr. 2026 from:",  # to/from window
        "Twelve Month",  # twelve fallback
        "One Month",  # one-month fallback
        "Unadjusted percent change",  # generic pct change
        "Mystery heading",  # → None
    )
    sub_row = (
        "",  # 0
        "",  # 1
        "",  # relative importance has no sub
        "Apr. 2026",  # index date
        "Mar. 2026-Apr. 2026",  # SA 1m range
        "Feb. 2026",  # to/from start (2-month window)
        "Apr. 2025-Apr. 2026",  # twelve range
        "Seasonally adjusted percent change Mar. 2026-Apr. 2026",  # one-month SA
        "Apr. 2025-Apr. 2026",  # generic 12m
        "whatever",
    )
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    kinds = [c[0] if c else None for c in cols]
    assert kinds[0] is None
    assert kinds[1] is None
    assert kinds[2] == "relative_importance"
    assert kinds[3] == "index_nsa"
    assert kinds[4] == "pct_change_1m_sa"
    assert kinds[5] == "pct_change_window"  # 2-month window
    assert kinds[6] == "pct_change_12m_nsa"
    assert kinds[7] == "pct_change_1m_sa"  # sub says "seasonally adjusted"
    assert kinds[8] == "pct_change_12m_nsa"
    assert kinds[9] is None


def test_classify_columns_fallback_anchors():
    """Twelve/One Month headers with no parseable sub fall back to the release anchor."""
    super_row = ("Indent Level", "Category", "Twelve Month", "One Month")
    sub_row = ("", "", "", "")  # no range, no single period
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2] == ("pct_change_12m_nsa", date(2026, 4, 1), None)
    assert cols[3] == ("pct_change_1m_nsa", date(2026, 4, 1), None)


def test_classify_columns_twelve_single_period():
    """Twelve Month with a single-period sub uses that date."""
    super_row = ("Indent Level", "Category", "Twelve Month")
    sub_row = ("", "", "Apr. 2026")
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2] == ("pct_change_12m_nsa", date(2026, 4, 1), None)


def test_classify_columns_one_month_single_period():
    """One Month with a single-period sub uses that date (NSA)."""
    super_row = ("Indent Level", "Category", "One Month")
    sub_row = ("", "", "Apr. 2026")
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2] == ("pct_change_1m_nsa", date(2026, 4, 1), None)


def test_classify_columns_to_from_unparseable():
    """A 'Percent change to ... from' header with no parseable dates yields None."""
    super_row = ("Indent Level", "Category", "Percent change to from:")
    sub_row = ("", "", "")
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2] is None


def test_classify_columns_to_from_12m_and_1m():
    """to/from windows resolve to 12-month and 1-month based on span."""
    super_row = (
        "Indent Level",
        "Area",
        "Percent change to Apr. 2026 from:",
        "Percent change to Apr. 2026 from:",
    )
    sub_row = ("", "", "Apr. 2025", "Mar. 2026")
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2][0] == "pct_change_12m_nsa"
    assert cols[3][0] == "pct_change_1m_nsa"


def test_classify_columns_generic_pct_change_no_range():
    """A generic percent-change header with no range yields None."""
    super_row = ("Indent Level", "Category", "Unadjusted percent change")
    sub_row = ("", "", "no range token")
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2] is None


def test_classify_columns_generic_pct_change_1m():
    """A generic percent-change header with a 1-month range is classified NSA 1m."""
    super_row = ("Indent Level", "Category", "Unadjusted percent change")
    sub_row = ("", "", "Mar. 2026-Apr. 2026")
    cols = nr._classify_columns(super_row, sub_row, 2026, 4)
    assert cols[2] == ("pct_change_1m_nsa", date(2026, 4, 1), None)


def _make_nr_xlsx(rows: list[tuple]) -> bytes:
    """Render an in-memory News Release XLSX from raw cell tuples."""
    import io

    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_fetch_and_parse_discover_path(monkeypatch):
    """_fetch_and_parse with query_date=None resolves via _discover_latest_nr."""
    content = _make_nr_xlsx(
        [
            ("Indent Level", "Expenditure category", "Unadjusted indexes"),
            (None, None, "Apr. 2026"),
            (0, "All items", 333.0),
        ]
    )
    monkeypatch.setattr(nr, "_discover_latest_nr", lambda table: (2026, 4, content))
    result = nr._fetch_and_parse(1, None)
    assert result["rows"]
    assert result["rows"][0]["label"] == "All items"


def test_fetcher_transform_data_empty_raises():
    """The per-table fetcher closure raises EmptyDataError on empty rows."""
    from openbb_core.provider.utils.errors import EmptyDataError

    with pytest.raises(EmptyDataError):
        nr.BlsCpiNrTable1Fetcher.transform_data(
            nr.BlsCpiNrTable1Fetcher.transform_query({}),
            {"rows": [], "table_id": "cpi-nr-2026-04-t1"},
        )


def test_parse_nr_table_no_header_returns_empty():
    """_parse_nr_table returns no rows when the Indent Level header is absent."""
    content = _make_nr_xlsx([("just", "noise"), ("more", "noise")])
    result = nr._parse_nr_table(content, 2026, 4, 1)
    assert result["rows"] == []


def test_parse_nr_table_body_edge_rows():
    """_parse_nr_table skips non-int levels, blank labels; reads numeric pricing cells."""
    content = _make_nr_xlsx(
        [
            (None, None, None, None),  # leading blank row -> header-search skip
            ("Indent Level", "Area", "Pricing Schedule", "Unadjusted indexes"),
            (None, None, None, "Apr. 2026"),
            ("notint", "Bad level row", "M", 1.0),  # level int parse fails -> skip
            (0, None, "M", 2.0),  # blank label -> skip
            (0, "U.S. city average", 7, 333.0),  # numeric pricing cell branch
            (1, "Region", "M", " "),  # whitespace measure -> empty-string skip
        ]
    )
    result = nr._parse_nr_table(content, 2026, 4, 4)
    labels = {r["label"] for r in result["rows"]}
    assert "U.S. city average" in labels
    assert "Bad level row" not in labels


def test_parse_nr_table_5_direct():
    """_parse_nr_table_5 classifies basket columns and skips junk."""
    super_row = (
        "Indent Level",
        "Month Year",
        "Unadjusted 1-month percent change",
        "Unadjusted 1-month percent change",
        "Annual change",  # neither 12-month nor 1-month -> None
        "Unadjusted 12-month percent change",  # valid kind, no basket -> None
    )
    sub_row = ("", "", "C-CPI-U(1)", "CPI-U", "C-CPI-U", "Nonbasket")
    body_rows = [
        ("", "December 2013", 0.1, 0.2, 9.9, 9.9),
        ("", 12345, 0.1, 0.2, 9.9, 9.9),  # non-string label -> skip
        ("", "not a month label", 0.1, 0.2, 9.9, 9.9),  # unparseable -> skip
    ]
    rows = nr._parse_nr_table_5(
        body_rows,
        super_row,
        sub_row,
        2026,
        4,
        "tid",
        "tname",
        "April 2026",
        date(2026, 4, 1),
        {},
    )
    assert len(rows) == 2  # C-CPI-U + CPI-U for December 2013
    assert {r["label"] for r in rows} == {"C-CPI-U", "CPI-U"}


def test_parse_nr_table_6_7_direct():
    """_parse_nr_table_6_7 skips blank-indent and non-int-level rows."""
    body_rows = [
        (None, "skip blank indent", 100.0),  # row[0] is None -> skip
        ("notint", "skip bad level", 100.0),  # int parse fails -> skip
        (1, "", 1.0),  # blank label -> skip
        (0, "All items", 100.0, 0.6, 0.04, 0.07, "S-Feb. 2026", 0.3),
    ]
    rows = nr._parse_nr_table_6_7(
        body_rows, 6, 2026, 4, "tid", "tname", "April 2026", date(2026, 4, 1), {}
    )
    assert len(rows) == 1
    assert rows[0]["label"] == "All items"
    assert rows[0]["relative_importance"] == 100.0
    assert rows[0]["pct_change_1m_sa"] == 0.6
    assert rows[0]["largest_or_smallest_since_marker"] == "S-Feb. 2026"


def test_label_serializer_with_and_without_footnote():
    """The base label serializer wraps with footnote only when one exists."""
    row = nr.BlsCpiNrTable1Data(
        date=date(2026, 4, 1),
        label="Food(1)",
        footnote="Not seasonally adjusted.",
        table_id="t",
        table_name="n",
        release_period="April 2026",
    )
    dumped = row.model_dump(mode="json")
    assert dumped["label"] == {
        "value": "Food(1)",
        "footnote": "Not seasonally adjusted.",
    }

    row2 = nr.BlsCpiNrTable1Data(
        date=date(2026, 4, 1),
        label="Food",
        footnote=None,
        table_id="t",
        table_name="n",
        release_period="April 2026",
    )
    assert row2.model_dump(mode="json")["label"] == "Food"
