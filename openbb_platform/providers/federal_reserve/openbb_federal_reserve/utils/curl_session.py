"""Shared process-cached ``curl_cffi`` browser-impersonating sessions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

_sessions: dict[str, Any] = {}


def get_session(key: str, warmup: Callable[[Any], None] | None = None) -> Any:
    """Return the process-cached session for ``key``, creating it on first use.

    Parameters
    ----------
    key : str
        Cache key identifying the caller's session.
    warmup : Callable[[Any], None], optional
        Called once with the freshly created session the first time ``key`` is
        seen, typically to issue a request that primes a bot-management cookie.

    Returns
    -------
    Any
        A ``curl_cffi`` ``requests.Session`` impersonating Chrome.
    """
    if key not in _sessions:
        from curl_cffi import requests as curl_requests

        session = curl_requests.Session(impersonate="chrome")
        if warmup is not None:
            warmup(session)
        _sessions[key] = session
    return _sessions[key]


def reset_session(key: str) -> None:
    """Drop the cached session for ``key`` so the next call recreates and re-warms it.

    Parameters
    ----------
    key : str
        Cache key whose session should be discarded.
    """
    _sessions.pop(key, None)
