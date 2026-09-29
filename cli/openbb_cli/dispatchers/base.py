"""Dispatcher Protocol — the shared interface for Local and Http backends."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from openbb_cli.dispatchers.protocol import Request, Response


@runtime_checkable
class Dispatcher(Protocol):
    """Async dispatcher contract."""

    async def dispatch(self, request: Request) -> Response:
        """Resolve and run the command described by ``request``."""
        ...  # pragma: no cover

    async def aclose(self) -> None:
        """Release any held resources (HTTP clients, connection pools)."""
        ...  # pragma: no cover
