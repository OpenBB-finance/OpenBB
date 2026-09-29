"""Tests for the BLS Economic Calendar fetcher and parser helpers."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

import openbb_bls.models.economic_calendar as ec_mod
from openbb_bls.models.economic_calendar import (
    BlsEconomicCalendarFetcher,
    BlsEconomicCalendarQueryParams,
    _fetch_schedule,
    _iter_months,
    _last_day_of_month,
    _parse_release_block,
    _parse_release_time,
    _parse_schedule_page,
    _resolve_window,
)

_FIXTURES = Path(__file__).parent / "fixtures"
_SCHEDULE_HTML = (_FIXTURES / "bls_schedule.html").read_text()


class _FakeResponse:
    """Minimal requests.Response stand-in."""

    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


def _make_get(text: str, status_code: int = 200):
    """Build a fake requests.get returning the given payload."""

    def _get(url, *args, **kwargs):
        return _FakeResponse(text, status_code=status_code)

    return _get


def test_query_params_release_default():
    """release defaults to None when not provided."""
    q = BlsEconomicCalendarQueryParams()
    assert q.release is None


def test_resolve_window_defaults_to_today_centered_range():
    """None inputs are resolved to a window around today."""
    start, end = _resolve_window(None, None)
    today = date.today()
    assert start <= today <= end
    assert (end - start).days >= 21


def test_resolve_window_rejects_too_early_start():
    """A start_date before the 2000 archive boundary raises OpenBBError."""
    with pytest.raises(OpenBBError, match="too early"):
        _resolve_window(date(1999, 12, 31), date(2000, 6, 1))


def test_resolve_window_rejects_inverted_range():
    """end_date < start_date raises OpenBBError."""
    with pytest.raises(OpenBBError, match="on or after"):
        _resolve_window(date(2026, 5, 10), date(2026, 5, 1))


def test_last_day_of_month_for_december():
    """December resolves to the 31st without rolling year over."""
    assert _last_day_of_month(2026, 12) == date(2026, 12, 31)


def test_last_day_of_month_for_february_leap_year():
    """February in a leap year resolves to the 29th."""
    assert _last_day_of_month(2024, 2) == date(2024, 2, 29)


def test_iter_months_spans_year_boundary():
    """_iter_months yields every (year, month) inclusive across year boundary."""
    months = list(_iter_months(date(2025, 11, 20), date(2026, 2, 5)))
    assert months == [(2025, 11), (2025, 12), (2026, 1), (2026, 2)]


def test_iter_months_single_month():
    """_iter_months yields exactly one entry when start/end share a month."""
    months = list(_iter_months(date(2026, 5, 1), date(2026, 5, 31)))
    assert months == [(2026, 5)]


@pytest.mark.parametrize(
    "text,expected",
    [
        ("08:30 AM", (8, 30)),
        ("12:00 PM", (12, 0)),
        ("12:00 AM", (0, 0)),
        ("01:15 PM", (13, 15)),
        ("noon", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_release_time_branches(text, expected):
    """_parse_release_time handles AM/PM noon/midnight and missing input."""
    assert _parse_release_time(text) == expected


def test_parse_release_block_full():
    """A standard release block produces a populated row dict."""
    body = (
        '<strong><a href="/news.release/cpi.nr0.htm">Consumer Price Index</a></strong>'
        "<br>April 2026<br>08:30 AM"
    )
    row = _parse_release_block(body, 2026, 5, 3)
    assert row is not None
    assert row["event"] == "Consumer Price Index"
    assert row["period"] == "April 2026"
    assert row["time"] == "08:30 AM"
    assert row["date"] == datetime(2026, 5, 3, 8, 30)
    assert row["news_release_url"] == "https://www.bls.gov/news.release/cpi.nr0.htm"


def test_parse_release_block_absolute_url():
    """Pre-absolute href is preserved verbatim."""
    body = (
        '<strong><a href="https://www.bls.gov/news.release/ppi.nr0.htm">PPI</a></strong>'
        "<br>April 2026<br>08:30 AM"
    )
    row = _parse_release_block(body, 2026, 5, 3)
    assert row["news_release_url"] == "https://www.bls.gov/news.release/ppi.nr0.htm"


def test_parse_release_block_no_anchor_no_time():
    """Block without an anchor and without parseable time falls back to date-only."""
    body = "<strong>Some Release</strong><br>March 2026<br>tentative"
    row = _parse_release_block(body, 2026, 6, 8)
    assert row["news_release_url"] is None
    assert row["time"] == "tentative"
    assert row["date"] == datetime(2026, 6, 8)


def test_parse_release_block_empty_body_returns_none():
    """An entirely empty body returns None."""
    assert _parse_release_block("<br>", 2026, 5, 3) is None


def test_parse_release_block_nbsp_event_returns_none():
    """An &nbsp; event is treated as empty and skipped."""
    body = "&nbsp;"
    assert _parse_release_block(body, 2026, 5, 3) is None


def test_parse_release_block_no_period_or_time():
    """A block with only an event title fills period/time with None."""
    body = "<strong>Lonely Release</strong>"
    row = _parse_release_block(body, 2026, 5, 3)
    assert row["event"] == "Lonely Release"
    assert row["period"] is None
    assert row["time"] is None


def test_parse_schedule_page_empty_html_returns_empty():
    """An empty HTML string yields no rows."""
    assert _parse_schedule_page("", 2026, 5) == []


def test_parse_schedule_page_skips_other_month_and_wrong_month():
    """other-month cells and cells whose id-month mismatches are skipped."""
    rows = _parse_schedule_page(_SCHEDULE_HTML, 2026, 5)
    events = sorted(r["event"] for r in rows)
    assert events == ["Consumer Price Index", "Producer Price Index", "Real Earnings"]


def test_fetch_schedule_returns_text_on_200(monkeypatch):
    """A 200 response returns the page text verbatim."""
    import requests

    monkeypatch.setattr(requests, "get", _make_get("<html>ok</html>"))
    assert _fetch_schedule(2026, 5) == "<html>ok</html>"


def test_fetch_schedule_returns_empty_on_404(monkeypatch):
    """A 404 is swallowed and returns an empty string."""
    import requests

    monkeypatch.setattr(requests, "get", _make_get("", status_code=404))
    assert _fetch_schedule(2099, 12) == ""


def test_fetch_schedule_raises_on_other_status(monkeypatch):
    """Non-200/404 responses raise OpenBBError."""
    import requests

    monkeypatch.setattr(requests, "get", _make_get("", status_code=500))
    with pytest.raises(OpenBBError, match="HTTP 500"):
        _fetch_schedule(2026, 5)


def test_fetcher_transform_query_coerces_dict():
    """transform_query produces a BlsEconomicCalendarQueryParams from a dict."""
    q = BlsEconomicCalendarFetcher.transform_query(
        {"start_date": date(2026, 5, 1), "end_date": date(2026, 5, 31)}
    )
    assert isinstance(q, BlsEconomicCalendarQueryParams)
    assert q.start_date == date(2026, 5, 1)
    assert q.end_date == date(2026, 5, 31)


def test_fetcher_extract_data_calls_fetch_and_parser(monkeypatch):
    """extract_data iterates months and concatenates parsed rows."""
    calls: list[tuple[int, int]] = []

    def _fake_fetch(year, month):
        calls.append((year, month))
        return _SCHEDULE_HTML

    monkeypatch.setattr(ec_mod, "_fetch_schedule", _fake_fetch)
    q = BlsEconomicCalendarFetcher.transform_query(
        {"start_date": date(2026, 5, 1), "end_date": date(2026, 5, 31)}
    )
    rows = BlsEconomicCalendarFetcher.extract_data(q, None)
    assert calls == [(2026, 5)]
    assert any(r["event"] == "Consumer Price Index" for r in rows)


def test_fetcher_transform_data_filters_window_and_release(monkeypatch):
    """transform_data drops rows outside the window and not matching release substring."""
    monkeypatch.setattr(ec_mod, "_fetch_schedule", lambda y, m: _SCHEDULE_HTML)
    q = BlsEconomicCalendarFetcher.transform_query(
        {
            "start_date": date(2026, 5, 1),
            "end_date": date(2026, 5, 31),
            "release": "consumer price",
        }
    )
    raw = BlsEconomicCalendarFetcher.extract_data(q, None)
    out = BlsEconomicCalendarFetcher.transform_data(q, raw)
    assert len(out) == 1
    assert out[0].event == "Consumer Price Index"


def test_fetcher_transform_data_drops_rows_outside_window(monkeypatch):
    """Rows whose date falls outside (start, end) are skipped."""
    monkeypatch.setattr(ec_mod, "_fetch_schedule", lambda y, m: "")
    q = BlsEconomicCalendarFetcher.transform_query(
        {"start_date": date(2026, 5, 1), "end_date": date(2026, 5, 31)}
    )
    raw = [
        {
            "date": datetime(2026, 5, 15, 8, 30),
            "event": "In window",
            "country": "US",
            "source": "BLS",
        },
        {
            "date": datetime(2026, 7, 1, 8, 30),
            "event": "Out of window",
            "country": "US",
            "source": "BLS",
        },
    ]
    out = BlsEconomicCalendarFetcher.transform_data(q, raw)
    assert [r.event for r in out] == ["In window"]


def test_fetcher_transform_data_drops_rows_without_date(monkeypatch):
    """Rows whose date is None are skipped."""
    monkeypatch.setattr(ec_mod, "_fetch_schedule", lambda y, m: _SCHEDULE_HTML)
    q = BlsEconomicCalendarFetcher.transform_query(
        {"start_date": date(2026, 5, 1), "end_date": date(2026, 5, 31)}
    )
    raw = BlsEconomicCalendarFetcher.extract_data(q, None)
    raw.append({"date": None, "event": "ignored", "country": "US", "source": "BLS"})
    out = BlsEconomicCalendarFetcher.transform_data(q, raw)
    assert all(r.event != "ignored" for r in out)


def test_fetcher_transform_data_accepts_date_objects(monkeypatch):
    """A row with a plain date (no time) is accepted by the window filter."""
    monkeypatch.setattr(ec_mod, "_fetch_schedule", lambda y, m: "")
    q = BlsEconomicCalendarFetcher.transform_query(
        {"start_date": date(2026, 5, 1), "end_date": date(2026, 5, 31)}
    )
    raw = [
        {
            "date": date(2026, 5, 15),
            "event": "Plain Date Release",
            "country": "US",
            "source": "BLS",
        }
    ]
    out = BlsEconomicCalendarFetcher.transform_data(q, raw)
    assert len(out) == 1
    assert out[0].event == "Plain Date Release"


def test_fetcher_transform_data_raises_when_empty(monkeypatch):
    """An empty filter result raises EmptyDataError."""
    monkeypatch.setattr(ec_mod, "_fetch_schedule", lambda y, m: _SCHEDULE_HTML)
    q = BlsEconomicCalendarFetcher.transform_query(
        {
            "start_date": date(2026, 5, 1),
            "end_date": date(2026, 5, 31),
            "release": "nonexistent release name",
        }
    )
    raw = BlsEconomicCalendarFetcher.extract_data(q, None)
    with pytest.raises(EmptyDataError):
        BlsEconomicCalendarFetcher.transform_data(q, raw)


def test_fetcher_end_to_end(monkeypatch):
    """transform_query -> extract_data -> transform_data produces sorted rows."""
    monkeypatch.setattr(ec_mod, "_fetch_schedule", lambda y, m: _SCHEDULE_HTML)
    q = BlsEconomicCalendarFetcher.transform_query(
        {"start_date": date(2026, 5, 1), "end_date": date(2026, 5, 31)}
    )
    raw = BlsEconomicCalendarFetcher.extract_data(q, None)
    out = BlsEconomicCalendarFetcher.transform_data(q, raw)
    events = {r.event for r in out}
    assert "Consumer Price Index" in events
    assert "Producer Price Index" in events
    assert "Real Earnings" in events
