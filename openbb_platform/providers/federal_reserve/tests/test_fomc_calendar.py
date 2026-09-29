"""Tests for the FOMC event-calendar feed and availability helper."""

import json
from datetime import date, datetime
from unittest.mock import MagicMock

from openbb_federal_reserve.utils import (
    cache,
    fomc_calendar as fc,
)


def _calendar_response(payload: dict) -> MagicMock:
    """Build a make_request response with a UTF-8-BOM JSON body."""
    response = MagicMock()
    response.content = ("﻿" + json.dumps(payload)).encode("utf-8")
    response.raise_for_status = MagicMock()
    return response


class TestFetchCalendarEvents:
    """Tests for ``_fetch_calendar_events`` and ``get_calendar_events``."""

    def test_parses_bom_encoded_events(self, monkeypatch):
        """The BOM-prefixed JSON feed is decoded into the events list."""
        events = [{"type": "FOMC", "month": "2026-03", "days": "18"}]
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _calendar_response({"events": events}),
        )
        assert fc._fetch_calendar_events() == events

    def test_non_list_events_yield_empty(self, monkeypatch):
        """A malformed ``events`` value degrades to an empty list."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: _calendar_response({"events": {}}),
        )
        assert fc._fetch_calendar_events() == []

    def test_get_calendar_events_caches_the_feed(self, monkeypatch):
        """The feed is fetched once and served from the cache thereafter."""
        events = [{"type": "FOMC", "month": "2026-03", "days": "18"}]
        calls: list[int] = []

        def _make_request(*_a, **_k):
            calls.append(1)
            return _calendar_response({"events": events})

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _make_request
        )
        assert fc.get_calendar_events() == events
        assert fc.get_calendar_events() == events
        assert calls == [1]


class TestEventDate:
    """Tests for ``_event_date`` parsing."""

    def test_parses_single_day(self):
        """A ``YYYY-MM`` month and single day parse to a date."""
        assert fc._event_date({"month": "2026-03", "days": "18"}) == date(2026, 3, 18)

    def test_uses_first_day_of_a_range(self):
        """A day range keeps the first day."""
        assert fc._event_date({"month": "2026-03", "days": "18-19"}) == date(
            2026, 3, 18
        )

    def test_invalid_fields_return_none(self):
        """Unparseable month/day fields return ``None``."""
        assert fc._event_date({"month": "bad", "days": "x"}) is None


class TestNextFomcRelease:
    """Tests for ``next_fomc_release``."""

    def test_returns_nearest_future_fomc_event(self, monkeypatch):
        """Only future FOMC-typed events count; the nearest is returned."""
        events = [
            {"type": "FOMC", "month": "2026-03", "days": "18"},
            {"type": "Speeches", "month": "2026-01", "days": "5"},
            {"type": "FOMC", "month": "2026-06", "days": "17"},
        ]
        monkeypatch.setattr(fc, "get_calendar_events", lambda: events)
        now = datetime(2026, 2, 1, tzinfo=cache.EASTERN)
        assert fc.next_fomc_release(now=now) == date(2026, 3, 18)

    def test_returns_none_without_upcoming_events(self, monkeypatch):
        """No upcoming FOMC events yields ``None``."""
        monkeypatch.setattr(fc, "get_calendar_events", lambda: [])
        now = datetime(2026, 2, 1, tzinfo=cache.EASTERN)
        assert fc.next_fomc_release(now=now) is None

    def test_calendar_failure_degrades_to_none(self, monkeypatch):
        """A feed error is swallowed and returns ``None``."""

        def _boom():
            raise RuntimeError("feed down")

        monkeypatch.setattr(fc, "get_calendar_events", _boom)
        now = datetime(2026, 2, 1, tzinfo=cache.EASTERN)
        assert fc.next_fomc_release(now=now) is None


class TestSecondsUntilNextFomcRelease:
    """Tests for ``seconds_until_next_fomc_release`` bounds and fallback."""

    def test_uses_release_date_within_bounds(self, monkeypatch):
        """A near release yields the exact seconds until its US/Eastern midnight."""
        monkeypatch.setattr(fc, "next_fomc_release", lambda now=None: date(2026, 2, 3))
        now = datetime(2026, 2, 1, 12, 0, tzinfo=cache.EASTERN)
        assert fc.seconds_until_next_fomc_release(now=now) == 36 * 3600

    def test_caps_at_seven_days(self, monkeypatch):
        """A distant release is capped at seven days."""
        monkeypatch.setattr(fc, "next_fomc_release", lambda now=None: date(2026, 6, 1))
        now = datetime(2026, 2, 1, 12, 0, tzinfo=cache.EASTERN)
        assert fc.seconds_until_next_fomc_release(now=now) == 7 * 86400

    def test_floors_at_one_hour(self, monkeypatch):
        """A release already past its midnight floors at one hour."""
        monkeypatch.setattr(fc, "next_fomc_release", lambda now=None: date(2026, 2, 1))
        now = datetime(2026, 2, 1, 12, 0, tzinfo=cache.EASTERN)
        assert fc.seconds_until_next_fomc_release(now=now) == 3600.0

    def test_falls_back_to_daily_when_unknown(self, monkeypatch):
        """No release date falls back to the daily cadence."""
        monkeypatch.setattr(fc, "next_fomc_release", lambda now=None: None)
        now = datetime(2026, 2, 1, 12, 0, tzinfo=cache.EASTERN)
        assert fc.seconds_until_next_fomc_release(now=now) == (
            cache.seconds_until_next_release("daily", now=now)
        )
