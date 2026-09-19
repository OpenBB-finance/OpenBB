"""Federal Reserve event calendar feed and FOMC release-availability helper."""

from __future__ import annotations

from datetime import date, datetime

CALENDAR_URL = "https://www.federalreserve.gov/json/calendar.json"


def _fetch_calendar_events() -> list[dict]:
    """Download and parse the Federal Reserve events calendar feed."""
    import json

    from openbb_core.provider.utils.helpers import make_request

    response = make_request(CALENDAR_URL)
    response.raise_for_status()
    payload = json.loads(response.content.decode("utf-8-sig"))
    events = payload.get("events", [])
    return events if isinstance(events, list) else []


def get_calendar_events() -> list[dict]:
    """Return the Fed events calendar, cached for one day."""
    from openbb_federal_reserve.utils.cache import cached, seconds_until_next_release

    return cached(
        "fomc_calendar_events",
        lambda: seconds_until_next_release("daily"),
        _fetch_calendar_events,
    )


def _event_date(event: dict) -> date | None:
    """Parse a calendar event's ``month``/``days`` fields into a date."""
    month = str(event.get("month", ""))
    days = str(event.get("days", "")).replace(",", "-").split("-")[0].strip()
    try:
        year_str, month_str = month.split("-")
        return date(int(year_str), int(month_str), int(days))
    except (ValueError, TypeError):
        return None


def next_fomc_release(*, now: datetime | None = None) -> date | None:
    """Return the date of the next scheduled FOMC release, or ``None``."""
    from openbb_federal_reserve.utils.cache import now_eastern

    today = (now or now_eastern()).date()
    try:
        events = get_calendar_events()
    except Exception:  # noqa: BLE001
        return None

    upcoming = [
        event_date
        for event in events
        if event.get("type") == "FOMC"
        and (event_date := _event_date(event)) is not None
        and event_date >= today
    ]
    return min(upcoming) if upcoming else None


def seconds_until_next_fomc_release(*, now: datetime | None = None) -> float:
    """Return seconds until the next FOMC release, bounded to [1 hour, 7 days]."""
    from openbb_federal_reserve.utils.cache import (
        EASTERN,
        now_eastern,
        seconds_until_next_release,
    )

    current = now or now_eastern()
    release = next_fomc_release(now=current)
    if release is None:
        return seconds_until_next_release("daily", now=current)

    target = datetime(release.year, release.month, release.day, tzinfo=EASTERN)
    seconds = (target - current).total_seconds()
    return min(max(seconds, 3600.0), 7 * 86400.0)
