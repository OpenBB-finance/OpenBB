"""HTTP client for the build-time cache generator.

This module is deliberately kept separate from
``openbb_government_ca.utils.generate_cache`` so that:

1. The HTTP layer can be unit-tested in isolation (mock ``requests.get``
   once, exercise all the retry / timeout / parsing logic).
2. Both StatsCan (Phase 2) and BoC (Phase 3) fetchers share the same
   resilient HTTP machinery — same timeouts, same retry policy, same
   error shape.

CRITICAL: this module imports only ``requests`` and stdlib. It MUST
NOT import ``openbb_core`` — the build hook runs in an isolated PEP
517 env that doesn't have it.
"""

from __future__ import annotations

import json
import time
from typing import Any

try:
    import requests
except ImportError as e:  # pragma: no cover - build env should always have requests
    raise SystemExit(
        "FATAL: `requests` is required by the build hook but is not "
        "installed. It is listed in [build-system].requires of "
        "pyproject.toml."
    ) from e


class NetworkError(RuntimeError):
    """Raised when an upstream HTTP call fails after all retries.

    The ``url`` and ``cause`` attributes let callers produce clear
    log messages without losing the original exception chain.
    """

    def __init__(
        self,
        url: str,
        message: str,
        *,
        cause: Exception | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(f"{message} (url={url})")
        self.url = url
        self.cause = cause
        self.status_code = status_code


def http_get_json(
    url: str,
    *,
    timeout: float = 30.0,
    retries: int = 2,
    backoff_seconds: float = 1.5,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    user_agent: str = "openbb-government-ca-build-hook/0.1",
) -> Any:
    """GET *url* and return the parsed JSON body.

    Resilience features
    -------------------
    - **Timeout**: every attempt gets ``timeout`` seconds. Default 30s
      matches the OECD generator's behavior and is long enough for
      StatsCan's slow cold-cache responses.
    - **Retries**: transient failures (connection errors, 5xx, read
      timeouts) are retried up to ``retries`` times with exponential
      backoff (``backoff_seconds`` * 1.5^attempt).
    - **4xx are NOT retried**: a 404 means the resource doesn't exist;
      retrying won't help and just wastes time.
    - **User-Agent**: set explicitly so StatsCan/BoC can identify our
      traffic in their logs. Both APIs are public and don't require
      auth, but a clear UA is polite.

    Raises
    ------
    NetworkError
        If all retries are exhausted or a non-retryable error occurs.
    """
    final_headers = {"Accept": "application/json", "User-Agent": user_agent}
    if headers:
        final_headers.update(headers)

    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = requests.get(
                url,
                headers=final_headers,
                params=params,
                timeout=timeout,
            )
        except requests.exceptions.RequestException as exc:
            # Connection error, DNS failure, etc. — retryable.
            last_exc = exc
            if attempt < retries:
                _sleep_backoff(backoff_seconds, attempt)
                continue
            raise NetworkError(url, f"connection failed: {exc}", cause=exc) from exc

        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except json.JSONDecodeError as exc:
                # Body wasn't valid JSON — not retryable.
                raise NetworkError(
                    url,
                    f"response body is not valid JSON (first 200 bytes: "
                    f"{response.text[:200]!r})",
                    cause=exc,
                    status_code=response.status_code,
                ) from exc

        if 400 <= response.status_code < 500:
            # Client error — not retryable. The resource doesn't exist
            # or we're calling it wrong; retrying won't help.
            raise NetworkError(
                url,
                f"client error {response.status_code}: {response.reason}",
                status_code=response.status_code,
            )

        # 5xx or other — retryable.
        last_exc = RuntimeError(
            f"server error {response.status_code}: {response.reason}"
        )
        if attempt < retries:
            _sleep_backoff(backoff_seconds, attempt)
            continue

        raise NetworkError(
            url,
            f"server error {response.status_code} after {retries + 1} attempts",
            cause=last_exc,
            status_code=response.status_code,
        ) from last_exc

    # Should be unreachable — the loop either returns or raises.
    raise NetworkError(
        url, "exhausted retries without resolution", cause=last_exc
    )  # pragma: no cover


def _sleep_backoff(base: float, attempt: int) -> None:
    """Sleep for ``base * 1.5 ** attempt`` seconds (capped at 10s).

    Kept as a separate function so tests can monkey-patch it to
    instant-return — otherwise the retry tests would take 5+ seconds.
    """
    delay = min(base * (1.5**attempt), 10.0)
    time.sleep(delay)
