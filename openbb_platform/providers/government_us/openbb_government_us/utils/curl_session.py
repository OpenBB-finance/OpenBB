"""Shared curl_cffi session helper for hosts behind a TLS-fingerprinting WAF."""

from typing import Any

_SESSIONS: dict[str, Any] = {}


async def get_session(key: str, warmup: str | None = None) -> Any:
    """Get or create a Chrome-impersonating session for a WAF-protected host.

    Hosts such as www.fas.usda.gov sit behind an Akamai WAF that inspects the
    TLS fingerprint, so aiohttp and plain curl are rejected with HTTP 403
    regardless of headers.

    Parameters
    ----------
    key : str
        Identifier for the cached session, conventionally the host name.
    warmup : str | None
        URL to request once when the session is created, priming any cookies
        the edge sets before the first real request.

    Returns
    -------
    AsyncSession
        A curl_cffi session impersonating Chrome, cached under the key.
    """
    from curl_cffi.requests import AsyncSession

    session = _SESSIONS.get(key)
    if session is None:
        session = AsyncSession(impersonate="chrome")
        if warmup:
            await session.get(warmup)
        _SESSIONS[key] = session
    return session


async def close_sessions() -> None:
    """Close every cached session and clear the cache."""
    while _SESSIONS:
        _, session = _SESSIONS.popitem()
        await session.close()
