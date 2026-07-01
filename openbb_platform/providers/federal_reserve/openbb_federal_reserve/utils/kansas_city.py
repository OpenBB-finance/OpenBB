"""Federal Reserve Bank of Kansas City HTTP client.

The Kansas City Fed main site (``www.kansascityfed.org``) sits behind Akamai bot
management that hangs ordinary HTTP clients. Access requires a browser-TLS
-impersonating session (``curl_cffi``) warmed up against the site home page. The
research data host (``kcresearch-share.kansascityfed.org``) serves clean CSVs and
is fetched through the same session for safety. All upstream byte fetches funnel
through :func:`fetch_kansas_city` so tests can monkeypatch a single seam.
"""

from __future__ import annotations

from typing import Any

from openbb_federal_reserve.utils.curl_session import (
    get_session,
    reset_session as _reset,
)

DATA_HOST = "https://kcresearch-share.kansascityfed.org"
SITE_HOST = "https://www.kansascityfed.org"


def _warmup(session: Any) -> None:
    """Prime the Akamai cookie against the site home page."""
    session.get(f"{SITE_HOST}/", timeout=30)


def _get_session() -> Any:
    """Return a warmed ``curl_cffi`` session impersonating Chrome."""
    return get_session("kansas_city", _warmup)


def reset_session() -> None:
    """Drop the cached session so the next call re-warms the Akamai cookie."""
    _reset("kansas_city")


def fetch_kansas_city(url: str, *, referer: str | None = None) -> bytes:
    """Fetch a Kansas City Fed URL as bytes, re-warming once on a 403.

    Parameters
    ----------
    url : str
        The absolute URL to download.
    referer : str | None
        An optional ``Referer`` header; defaults to the site home page.

    Returns
    -------
    bytes
        The raw response body.
    """
    headers = {"Referer": referer or f"{SITE_HOST}/"}
    session = _get_session()
    response = session.get(url, headers=headers, timeout=180)
    if response.status_code == 403:
        reset_session()
        response = _get_session().get(url, headers=headers, timeout=180)
    response.raise_for_status()
    return response.content
