"""Shared query parameter helpers for the FRED provider."""

from typing import Any

from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

USE_CACHE_DESCRIPTION = (
    "When True, the request is served from, and written to, the FRED response cache."
)


class UseCacheQueryParams(QueryParams):
    """Query parameters carrying the FRED response cache switch."""

    use_cache: bool = Field(default=True, description=USE_CACHE_DESCRIPTION)


def join_dates(value: Any) -> str | None:
    """Normalize a date parameter to comma-separated ISO dates.

    Parameters
    ----------
    value : Any
        A date, a string of one or more comma-separated dates, or a sequence
        of either.

    Returns
    -------
    str or None
        The dates as ``YYYY-MM-DD``, comma-separated, or None when none were
        given.

    Raises
    ------
    OpenBBError
        If an entry cannot be read as a date.
    """
    from datetime import date as dateType

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.app.utils_optional import require_optional

    if value is None:
        return None

    items = value if isinstance(value, (list, tuple)) else str(value).split(",")
    to_datetime = require_optional("pandas").to_datetime
    dates: list[str] = []

    for item in items:
        if isinstance(item, dateType):
            dates.append(item.strftime("%Y-%m-%d"))
            continue

        text = str(item).strip()

        if not text:
            continue

        try:
            dates.append(to_datetime(text).date().strftime("%Y-%m-%d"))
        except (ValueError, TypeError) as error:
            raise OpenBBError(f"Invalid date: {item}") from error

    return ",".join(dates) if dates else None
