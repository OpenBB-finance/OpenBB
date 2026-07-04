"""Federal Reserve Bank of Chicago HTTP access."""

from __future__ import annotations

from typing import Any

from openbb_federal_reserve.utils.curl_session import get_session


def _get_session() -> Any:
    """Return a browser-impersonating ``curl_cffi`` session for 403 fallback."""
    return get_session("chicago")


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
