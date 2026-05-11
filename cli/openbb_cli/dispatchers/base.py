"""Dispatcher Protocol — the shared interface for Local and Http backends."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from openbb_cli.dispatchers.protocol import Request, Response


@runtime_checkable
class Dispatcher(Protocol):
    """Async dispatcher contract.

    Implementations must be stateless across requests: a single dispatcher
    instance may serve thousands of requests concurrently. The runtime never
    inspects implementation state between calls — concurrency safety is the
    implementation's responsibility, but the simplest correct design holds no
    mutable state outside per-request locals.
    """

    async def dispatch(self, request: Request) -> Response:
        """Resolve and run the command described by ``request``.

        Errors must be caught and reported as a Response with ``ok=False`` and
        a populated ``error`` field. Raising bypasses the per-request isolation
        and would crash the batch loop.
        """
        ...  # pragma: no cover

    async def aclose(self) -> None:
        """Release any held resources (HTTP clients, connection pools)."""
        ...  # pragma: no cover
