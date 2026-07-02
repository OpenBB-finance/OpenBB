"""Federal Reserve Bank of Chicago HTTP access."""

from __future__ import annotations

from typing import Any

from openbb_federal_reserve.utils.curl_session import (
    get_session,
    reset_session as _reset,
)

API_BASE = "https://api.data.chicagofed.org"
SITE_BASE = "https://www.chicagofed.org"
NEWSFEED_URL = f"{SITE_BASE}/forms/NewsFeed/Index"


def _get_session() -> Any:
    """Return a browser-impersonating ``curl_cffi`` session for 403 fallback."""
    return get_session("chicago")


def reset_session() -> None:
    """Drop the cached ``curl_cffi`` session so the next call re-creates it."""
    _reset("chicago")


def get_bytes(url: str) -> bytes:
    """Return the bytes of a Chicago Fed download, falling back on a 403.

    Parameters
    ----------
    url : str
        The fully qualified download URL.

    Returns
    -------
    bytes
        The raw response content.
    """
    from openbb_core.provider.utils.helpers import make_request

    response = make_request(url)
    if response.status_code == 403:
        response = _get_session().get(url, timeout=60)
    response.raise_for_status()
    return response.content


def get_text(url: str) -> str:
    """Return the decoded text of a Chicago Fed download, falling back on a 403.

    Parameters
    ----------
    url : str
        The fully qualified download URL.

    Returns
    -------
    str
        The response body decoded as UTF-8.
    """
    return get_bytes(url).decode("utf-8-sig", "ignore")


def post_newsfeed(series_id: str, page: int = 1) -> list[dict[str, Any]]:
    """Return the cumulative NewsFeed publication list for a series.

    Parameters
    ----------
    series_id : str
        The 32-hex series GUID.
    page : int
        The cumulative page number (1-based).

    Returns
    -------
    list[dict[str, Any]]
        The raw publication records from the feed.
    """
    from openbb_core.provider.utils.helpers import make_request

    url = f"{NEWSFEED_URL}?seriesIds={series_id}&page={page}"
    headers = {"Content-Type": "application/json"}
    response = make_request(url, method="POST", headers=headers, json={})
    if response.status_code == 403:
        response = _get_session().post(url, headers=headers, json={}, timeout=60)
    response.raise_for_status()
    return response.json()
