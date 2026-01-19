"""Synchronous helpers for async state stores.

Provides blocking wrappers that allow sync code to interact with async stores.
Uses the server's event loop when available, otherwise creates a temporary one.
"""

from __future__ import annotations

import asyncio
import threading

from typing import TYPE_CHECKING, Any, TypeVar


if TYPE_CHECKING:
    from collections.abc import Coroutine


T = TypeVar("T")


# Module-level fallback loop for pre-server operations
class _FallbackLoopHolder:
    """Holder for fallback event loop to avoid global statement."""

    loop: asyncio.AbstractEventLoop | None = None
    thread: threading.Thread | None = None


_fallback_holder = _FallbackLoopHolder()
_fallback_lock = threading.Lock()


def _get_or_create_fallback_loop() -> asyncio.AbstractEventLoop:
    """Get or create a fallback event loop for pre-server async operations.

    This loop runs in a background thread and persists across multiple
    run_async calls, avoiding the issue of Redis connections becoming
    invalid when asyncio.run() closes its loop.
    """
    with _fallback_lock:
        if _fallback_holder.loop is not None and _fallback_holder.loop.is_running():
            return _fallback_holder.loop

        # Create a new loop in a background thread
        _fallback_holder.loop = asyncio.new_event_loop()

        def run_loop() -> None:
            loop = _fallback_holder.loop
            if loop is not None:
                asyncio.set_event_loop(loop)
                loop.run_forever()

        _fallback_holder.thread = threading.Thread(target=run_loop, daemon=True)
        _fallback_holder.thread.start()

        # Wait for the loop to start
        import time

        for _ in range(50):  # 500ms max wait
            if _fallback_holder.loop.is_running():
                break
            time.sleep(0.01)

        return _fallback_holder.loop


def _get_server_loop() -> asyncio.AbstractEventLoop | None:
    """Get the server's event loop if running."""
    # Import here to avoid circular import
    try:
        from typing import cast

        from pywry.inline import _state

        loop = _state.server_loop
        if loop is not None and loop.is_running():
            return cast("asyncio.AbstractEventLoop", loop)
    except ImportError:
        pass
    return None


def run_async(coro: Coroutine[Any, Any, T], timeout: float | None = 5.0) -> T:
    """Run an async coroutine from sync code.

    Uses the server's event loop if available, otherwise creates a temporary one.
    NOTE: This function CANNOT be called from within an async context on the
    server loop - it will deadlock. Use `await` directly in async code.

    Parameters
    ----------
    coro : Coroutine
        The coroutine to run.
    timeout : float, optional
        Timeout in seconds. Default is 5.0.

    Returns
    -------
    T
        The result of the coroutine.

    Raises
    ------
    TimeoutError
        If the operation times out.
    RuntimeError
        If called from within the server's event loop (would deadlock).
    """
    loop = _get_server_loop()

    if loop is not None:
        # Check if we're already on this loop - would cause deadlock
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop - we're in sync context, safe to proceed
            running_loop = None

        if running_loop is loop:
            raise RuntimeError(
                "run_async() cannot be called from an async context on the server loop. "
                "Use 'await' directly instead."
            )

        # Server is running - use its loop via thread-safe submission
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result(timeout=timeout)
    # No server running - use fallback loop that persists across calls
    # This avoids Redis connection issues when asyncio.run() closes its loop
    fallback_loop = _get_or_create_fallback_loop()
    future = asyncio.run_coroutine_threadsafe(coro, fallback_loop)
    return future.result(timeout=timeout)


def run_async_fire_and_forget(coro: Coroutine[Any, Any, Any]) -> None:
    """Schedule an async coroutine without waiting for result.

    Parameters
    ----------
    coro : Coroutine
        The coroutine to run.
    """
    loop = _get_server_loop()

    if loop is not None:
        asyncio.run_coroutine_threadsafe(coro, loop)
    else:
        # Use fallback loop
        loop = _get_or_create_fallback_loop()
        asyncio.run_coroutine_threadsafe(coro, loop)
