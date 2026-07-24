"""Resilient asynchronous HTTP client for CME Group public endpoints."""

from __future__ import annotations

import asyncio
import os
import random
import threading
import time
from email.utils import parsedate_to_datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError

_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.cmegroup.com/",
}
_RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}


def _float_env(name: str, default: float) -> float:
    """Read a non-negative float environment setting."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return max(float(raw), 0.0)
    except (TypeError, ValueError):
        return default


def _int_env(name: str, default: int) -> int:
    """Read a positive integer environment setting."""
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return max(int(raw), 1)
    except (TypeError, ValueError):
        return default


DEFAULT_TIMEOUT_SECONDS = _float_env("OPENBB_CME_TIMEOUT", 20.0)
DEFAULT_MAX_ATTEMPTS = _int_env("OPENBB_CME_MAX_ATTEMPTS", 4)
DEFAULT_BACKOFF_SECONDS = _float_env("OPENBB_CME_BACKOFF", 0.5)
DEFAULT_MAX_BACKOFF_SECONDS = _float_env("OPENBB_CME_MAX_BACKOFF", 8.0)
DEFAULT_MIN_INTERVAL_SECONDS = _float_env("OPENBB_CME_MIN_INTERVAL", 0.1)
DEFAULT_MAX_CONCURRENCY = _int_env("OPENBB_CME_MAX_CONCURRENCY", 8)

_throttle_lock = threading.Lock()
_last_request_at = 0.0


class CMERequestError(OpenBBError):
    """A CME request failed after applying the provider's retry policy."""

    def __init__(
        self,
        message: str,
        *,
        url: str,
        status_code: int | None = None,
        attempts: int = 1,
    ) -> None:
        self.url = url
        self.status_code = status_code
        self.attempts = attempts
        super().__init__(message)


class _InvalidPayloadError(Exception):
    """Internal retryable error for malformed upstream payloads."""


def _retry_after_seconds(value: str | None) -> float | None:
    """Parse a Retry-After header containing seconds or an HTTP date."""
    if not value:
        return None
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(value)
            return max(retry_at.timestamp() - time.time(), 0.0)
        except (TypeError, ValueError, OverflowError):
            return None


async def _throttle(min_interval: float) -> None:
    """Enforce a process-wide minimum interval between CME requests."""
    global _last_request_at  # noqa: PLW0603  # pylint: disable=global-statement
    if min_interval <= 0:
        return
    while True:
        with _throttle_lock:
            now = time.monotonic()
            wait_for = _last_request_at + min_interval - now
            if wait_for <= 0:
                _last_request_at = now
                return
        await asyncio.sleep(wait_for)


class CMEHttpClient:
    """Pooled CME HTTP client with throttling and bounded retries."""

    def __init__(
        self,
        *,
        session: Any | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        backoff: float = DEFAULT_BACKOFF_SECONDS,
        max_backoff: float = DEFAULT_MAX_BACKOFF_SECONDS,
        min_interval: float = DEFAULT_MIN_INTERVAL_SECONDS,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._session = session
        self._owns_session = session is None
        self._timeout = timeout
        self._max_attempts = max(max_attempts, 1)
        self._backoff = max(backoff, 0.0)
        self._max_backoff = max(max_backoff, 0.0)
        self._min_interval = max(min_interval, 0.0)
        self._semaphore = asyncio.Semaphore(max(max_concurrency, 1))

    async def __aenter__(self) -> CMEHttpClient:
        """Create the underlying curl-cffi session when needed."""
        if self._session is None:
            # Imported lazily so importing the provider remains lightweight.
            # pylint: disable=import-outside-toplevel
            from curl_cffi.requests import AsyncSession

            self._session = AsyncSession(impersonate="chrome120")
        return self

    async def __aexit__(self, *_args: Any) -> None:
        """Close a session owned by this client."""
        if self._owns_session and self._session is not None:
            close_result = self._session.close()
            if hasattr(close_result, "__await__"):
                await close_result
            self._session = None

    def _delay(self, attempt: int, retry_after: float | None = None) -> float:
        """Return a bounded exponential delay with small random jitter."""
        if retry_after is not None:
            return retry_after
        base = min(self._backoff * (2 ** (attempt - 1)), self._max_backoff)
        return base + random.uniform(0, base * 0.2)  # noqa: S311

    async def get_json(self, url: str) -> dict | list:
        """Fetch and validate one JSON object or array from CME."""
        if self._session is None:
            raise RuntimeError(
                "CMEHttpClient must be used as an async context manager."
            )

        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            retry_after = None
            status_code = None
            try:
                async with self._semaphore:
                    await _throttle(self._min_interval)
                    response = await self._session.get(
                        url,
                        headers=_HEADERS,
                        timeout=self._timeout,
                    )
                status_code = getattr(response, "status_code", None)
                if status_code in _RETRYABLE_STATUS_CODES:
                    retry_after = _retry_after_seconds(
                        response.headers.get("Retry-After")
                        if getattr(response, "headers", None)
                        else None
                    )
                    raise RuntimeError(f"HTTP {status_code}")
                response.raise_for_status()
                try:
                    payload = response.json()
                except Exception as exc:
                    raise _InvalidPayloadError("invalid JSON") from exc
                if not isinstance(payload, (dict, list)):
                    raise _InvalidPayloadError("unexpected JSON payload")
                return payload
            except CMERequestError:
                raise
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                last_error = exc
                should_retry = (
                    status_code is None
                    or status_code in _RETRYABLE_STATUS_CODES
                    or isinstance(exc, _InvalidPayloadError)
                )
                if not should_retry or attempt == self._max_attempts:
                    if isinstance(exc, _InvalidPayloadError):
                        raise CMERequestError(
                            (f"CME returned {exc} after {attempt} attempt(s): {url}"),
                            url=url,
                            status_code=status_code,
                            attempts=attempt,
                        ) from exc
                    status = f" (HTTP {status_code})" if status_code is not None else ""
                    raise CMERequestError(
                        f"CME request failed{status} after {attempt} attempt(s): {url}",
                        url=url,
                        status_code=status_code,
                        attempts=attempt,
                    ) from exc
                await asyncio.sleep(self._delay(attempt, retry_after))

        raise CMERequestError(
            f"CME request failed after {self._max_attempts} attempt(s): {url}",
            url=url,
            attempts=self._max_attempts,
        ) from last_error
