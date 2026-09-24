"""Process-wide rate limiter for SEC EDGAR requests."""

import asyncio
import os
import threading
import time
from typing import Any

_DEFAULT_REQUESTS_PER_SECOND = 9.0
REQUESTS_PER_SECOND_ENV_VAR = "OPENBB_SEC_REQUESTS_PER_SECOND"

_lock = threading.Lock()
_next_available = 0.0


def _requests_per_second() -> float:
    """Return the configured request rate, falling back to the default."""
    raw = os.environ.get(REQUESTS_PER_SECOND_ENV_VAR)
    if raw:
        try:
            value = float(raw)
        except ValueError:
            return _DEFAULT_REQUESTS_PER_SECOND
        if value > 0:
            return value
    return _DEFAULT_REQUESTS_PER_SECOND


def _reserve_slot() -> float:
    """Reserve the next request slot; return the seconds to wait before sending."""
    global _next_available  # noqa: PLW0603
    interval = 1.0 / _requests_per_second()
    with _lock:
        now = time.monotonic()
        scheduled = max(now, _next_available)
        _next_available = scheduled + interval
    return scheduled - now


async def sec_rate_limit() -> None:
    """Await this process's next SEC request slot (async paths)."""
    wait = _reserve_slot()
    if wait > 0:
        await asyncio.sleep(wait)


def sec_rate_limit_sync() -> None:
    """Block until this process's next SEC request slot is free (sync paths)."""
    wait = _reserve_slot()
    if wait > 0:
        time.sleep(wait)


async def sec_amake_request(*args: Any, **kwargs: Any) -> Any:
    """Rate-limited ``amake_request`` for SEC EDGAR."""
    from openbb_core.provider.utils.helpers import amake_request  # noqa: PLC0415

    await sec_rate_limit()
    return await amake_request(*args, **kwargs)


def sec_make_request(*args: Any, **kwargs: Any) -> Any:
    """Rate-limited ``make_request`` for SEC EDGAR."""
    from openbb_core.provider.utils.helpers import make_request  # noqa: PLC0415

    sec_rate_limit_sync()
    return make_request(*args, **kwargs)
