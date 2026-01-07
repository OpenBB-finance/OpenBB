"""Async utility helpers for PyWry.

This module provides decorators and utilities for working with
asynchronous code in a synchronous context.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar


F = TypeVar("F", bound=Callable[..., Any])


def run_async(func: F) -> F:
    """Run an async function synchronously.

    Create a new event loop, run the coroutine, and close the loop.

    Parameters
    ----------
    func : Callable
        The async function to wrap.

    Returns
    -------
    Callable
        A synchronous wrapper function.
    """
    import asyncio

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(func(*args, **kwargs))
        loop.close()
        return result

    return wrapper  # type: ignore[return-value]


def async_task(func: F) -> F:
    """Mark a function as an async task.

    A simple passthrough wrapper for async functions.

    Parameters
    ----------
    func : Callable
        The async function to wrap.

    Returns
    -------
    Callable
        The wrapped async function.
    """

    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        return await func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def run_in_thread(func: F) -> Callable[..., Any]:
    """Run a function in a new thread.

    Parameters
    ----------
    func : Callable
        The function to run in a thread.

    Returns
    -------
    Callable
        A wrapper that starts the function in a new thread
        and returns the thread object.
    """
    import threading

    def wrapper(*args: Any, **kwargs: Any) -> threading.Thread:
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper
