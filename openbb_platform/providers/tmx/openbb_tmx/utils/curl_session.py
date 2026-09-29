"""Cloudflare-capable sessions for the hosts that reject plain clients."""

from functools import lru_cache
from typing import Any

WARMUP_URLS = {
    "ciro": "https://bondtradedata.ciro.ca/",
}

REFUSED_CODES = (403, 503)

ATTEMPTS = 5

BACKOFF = 0.75


@lru_cache(maxsize=4)
def get_session(key: str, warmup: bool = True):
    """Return a browser-impersonating session for one host.

    Parameters
    ----------
    key : str
        The host key, used to select the warmup URL.
    warmup : bool
        Whether to prime the session against the site root.

    Returns
    -------
    Session
        A session that survives the Cloudflare check.
    """
    from curl_cffi import requests

    session = requests.Session(impersonate="chrome")

    if warmup and key in WARMUP_URLS:
        session.get(WARMUP_URLS[key], timeout=60)

    return session


def request_with_retry(key: str, method: str, url: str, **kwargs):
    """Make one request, riding out the refusals Cloudflare hands back.

    Parameters
    ----------
    key : str
        The host key.
    method : str
        The HTTP method.
    url : str
        The URL to request.
    **kwargs : Any
        Passed through to the session.

    Returns
    -------
    Response
        The first response the host did not refuse.

    Raises
    ------
    OpenBBError
        If every attempt was refused.
    """
    import time

    from openbb_core.app.model.abstract.error import OpenBBError

    for attempt in range(ATTEMPTS):
        response = get_session(key).request(method, url, **kwargs)

        if response.status_code not in REFUSED_CODES:
            return response

        if attempt == ATTEMPTS // 2:
            get_session.cache_clear()

        if attempt < ATTEMPTS - 1:
            time.sleep(BACKOFF * 2**attempt)

    raise OpenBBError(f"Request to {url} was refused by the host.")


async def get_json(key: str, url: str, **kwargs: Any) -> Any:
    """Fetch JSON through a browser-impersonating session, off the event loop.

    Parameters
    ----------
    key : str
        The host key.
    url : str
        The URL to fetch.

    Returns
    -------
    Any
        The decoded JSON body.

    Raises
    ------
    OpenBBError
        If the host does not return a successful response.
    """
    import asyncio

    from openbb_core.app.model.abstract.error import OpenBBError

    def _fetch():
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Referer": WARMUP_URLS.get(key, url),
        }
        response = request_with_retry(
            key, "GET", url, headers=headers, timeout=300, **kwargs
        )

        if response.status_code != 200:
            raise OpenBBError(
                f"Request to {url} failed with status {response.status_code}."
            )

        return response.json()

    return await asyncio.to_thread(_fetch)
