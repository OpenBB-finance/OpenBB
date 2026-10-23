"""BLS Economic Calendar Model."""

from __future__ import annotations

import re
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_bls.utils.constants import BLS_USER_AGENT

_ARCHIVE_EARLIEST = dateType(2000, 1, 1)
_HEADERS = {
    "User-Agent": BLS_USER_AGENT,
    "Accept": "text/html,*/*",
}


class BlsEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """BLS Economic Calendar Query Parameters."""

    release: str | None = Field(
        default=None,
        description="Case-insensitive substring filter on the BLS release name.",
    )


_HIDE: dict[str, Any] = {"x-widget_config": {"hide": True}}


class BlsEconomicCalendarData(EconomicCalendarData):
    """BLS Economic Calendar Data."""

    country: str | None = Field(
        default="US",
        description="Country code for the release.",
        json_schema_extra=_HIDE,
    )
    category: str | None = Field(
        default=None,
        description="Release category.",
        json_schema_extra=_HIDE,
    )
    importance: str | None = Field(
        default=None,
        description="Importance rating of the release.",
        json_schema_extra=_HIDE,
    )
    currency: str | None = Field(
        default=None,
        description="Currency associated with the release.",
        json_schema_extra=_HIDE,
    )
    unit: str | None = Field(
        default=None,
        description="Unit of the release value.",
        json_schema_extra=_HIDE,
    )
    consensus: str | float | None = Field(
        default=None,
        description="Consensus forecast value.",
        json_schema_extra=_HIDE,
    )
    previous: str | float | None = Field(
        default=None,
        description="Prior-period value.",
        json_schema_extra=_HIDE,
    )
    revised: str | float | None = Field(
        default=None,
        description="Revised value.",
        json_schema_extra=_HIDE,
    )
    actual: str | float | None = Field(
        default=None,
        description="Realized release value.",
        json_schema_extra=_HIDE,
    )
    period: str | None = Field(
        default=None,
        description="Reporting period of the release.",
    )
    time: str | None = Field(
        default=None,
        description="Scheduled release time in Eastern Time.",
    )
    news_release_url: str | None = Field(
        default=None,
        description="Link to the release detail page.",
    )


class BlsEconomicCalendarFetcher(
    Fetcher[BlsEconomicCalendarQueryParams, list[BlsEconomicCalendarData]]
):
    """BLS Economic Calendar Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> BlsEconomicCalendarQueryParams:
        """Validate and coerce the query."""
        return BlsEconomicCalendarQueryParams(**params)

    @staticmethod
    def extract_data(
        query: BlsEconomicCalendarQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Scrape ``bls.gov/schedule/{YYYY}/{MM}_sched.htm`` for every month in range."""
        start, end = _resolve_window(query.start_date, query.end_date)
        rows: list[dict[str, Any]] = []
        for year, month in _iter_months(start, end):
            page = _fetch_schedule(year, month)
            rows.extend(_parse_schedule_page(page, year, month))
        return rows

    @staticmethod
    def transform_data(
        query: BlsEconomicCalendarQueryParams,
        data: list[dict[str, Any]],
        **kwargs: Any,
    ) -> list[BlsEconomicCalendarData]:
        """Apply ``release`` filter and ``start_date`` / ``end_date`` bounds."""
        start, end = _resolve_window(query.start_date, query.end_date)
        needle = query.release.lower().strip() if query.release else ""

        kept: list[BlsEconomicCalendarData] = []
        for row in data:
            dt = row.get("date")
            if dt is None:
                continue
            day = dt.date() if isinstance(dt, datetime) else dt
            if day < start or day > end:
                continue
            if needle and needle not in (row.get("event") or "").lower():
                continue
            kept.append(BlsEconomicCalendarData.model_validate(row))

        if not kept:
            raise EmptyDataError("No BLS releases matched the requested window/filter.")

        kept.sort(key=lambda r: r.event or "")
        kept.sort(key=lambda r: r.date or datetime.min, reverse=True)
        return kept


_DEFAULT_BACKWARD = timedelta(days=2)
_DEFAULT_FORWARD = timedelta(days=21)


def _resolve_window(
    start: dateType | None, end: dateType | None
) -> tuple[dateType, dateType]:
    """Resolve a ``(start, end)`` date window."""
    today = dateType.today()
    if start is None:
        start = today - _DEFAULT_BACKWARD
    if end is None:
        end = today + _DEFAULT_FORWARD
    if start < _ARCHIVE_EARLIEST:
        raise OpenBBError(
            "BLS archive only goes back to January 2000. "
            f"start_date {start.isoformat()} is too early."
        )
    if end < start:
        raise OpenBBError("end_date must be on or after start_date.")
    return start, end


def _last_day_of_month(year: int, month: int) -> dateType:
    """Return the last calendar day of ``year``-``month``."""
    if month == 12:
        return dateType(year, 12, 31)
    next_first = dateType(year, month + 1, 1)
    return dateType.fromordinal(next_first.toordinal() - 1)


def _iter_months(start: dateType, end: dateType):
    """Yield every ``(year, month)`` between *start* and *end* inclusive."""
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        m += 1
        if m == 13:
            y += 1
            m = 1


def _fetch_schedule(year: int, month: int) -> str:
    """GET one ``/schedule/{year}/{MM}_sched.htm`` page, returning the HTML."""
    import requests

    url = f"https://www.bls.gov/schedule/{year}/{month:02d}_sched.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=30)
    if resp.status_code == 404:
        return ""
    if resp.status_code != 200:
        raise OpenBBError(f"BLS returned HTTP {resp.status_code} fetching {url}.")
    return resp.text


_CELL_RE = re.compile(
    r'<td[^>]*\bid="d(\d{4})"(?P<attrs>[^>]*)>(?P<inner>.*?)</td>',
    re.S | re.I,
)
_BLOCK_RE = re.compile(r"<p>(?P<body>.*?)</p>", re.S | re.I)
_TAG_RE = re.compile(r"<[^>]+>")
_HREF_RE = re.compile(r'href="([^"]+)"', re.I)


def _parse_schedule_page(html: str, year: int, month: int) -> list[dict[str, Any]]:
    """Extract every release block from one monthly schedule page."""
    if not html:
        return []
    rows: list[dict[str, Any]] = []
    for match in _CELL_RE.finditer(html):
        attrs = match.group("attrs") or ""
        if "other-month" in attrs:
            continue
        cell_id = match.group(1)
        cell_month = int(cell_id[:2])
        cell_day = int(cell_id[2:])
        if cell_month != month:
            continue
        inner = match.group("inner")
        for block_match in _BLOCK_RE.finditer(inner):
            body = block_match.group("body")
            if 'class="day"' in body:
                continue
            row = _parse_release_block(body, year, cell_month, cell_day)
            if row is not None:
                rows.append(row)
    return rows


def _parse_release_block(
    body: str, year: int, month: int, day: int
) -> dict[str, Any] | None:
    """Parse one ``<p><strong>Release</strong><br>Period<br>Time</p>`` block."""
    href_match = _HREF_RE.search(body)
    news_url = href_match.group(1) if href_match else None
    if news_url and news_url.startswith("/"):
        news_url = f"https://www.bls.gov{news_url}"

    parts = re.split(r"<br\s*/?>", body, flags=re.I)
    cleaned = [_TAG_RE.sub("", p).strip() for p in parts]
    cleaned = [c for c in cleaned if c]
    if not cleaned:
        return None

    event = cleaned[0]
    if not event or event == "&nbsp;":
        return None

    period = cleaned[1] if len(cleaned) > 1 else None
    time_str = cleaned[2] if len(cleaned) > 2 else None

    release_dt: datetime | None = None
    parsed_time = _parse_release_time(time_str)
    if parsed_time is not None:
        release_dt = datetime(year, month, day, parsed_time[0], parsed_time[1])
    else:
        release_dt = datetime(year, month, day)

    return {
        "date": release_dt,
        "country": "US",
        "category": None,
        "event": event,
        "importance": None,
        "source": "BLS",
        "currency": None,
        "unit": None,
        "consensus": None,
        "previous": None,
        "revised": None,
        "actual": None,
        "period": period,
        "time": time_str,
        "news_release_url": news_url,
    }


_TIME_RE = re.compile(r"(\d{1,2}):(\d{2})\s*(AM|PM)", re.I)


def _parse_release_time(text: str | None) -> tuple[int, int] | None:
    """Parse ``"08:30 AM"`` style strings, returning ``(hour, minute)`` or ``None``."""
    if not text:
        return None
    m = _TIME_RE.search(text)
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    meridian = m.group(3).upper()
    if meridian == "PM" and hour != 12:
        hour += 12
    elif meridian == "AM" and hour == 12:
        hour = 0
    return hour, minute
