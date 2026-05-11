"""In-process dispatcher — resolves commands against the real ``obb`` namespace.

The dispatcher walks ``obb.<...>`` attributes the same way every other CLI
controller does, so integration tests that build a synthetic extension and
regenerate the static ``openbb/package/`` exercise the dispatcher through
the same code path production runs.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

from openbb_cli.dispatchers.protocol import Request, Response, ResponseError


class CommandNotFound(KeyError):
    """Raised when a dotted command path does not resolve under ``obb``."""


class LocalDispatcher:
    """Single-tenant in-process dispatcher.

    On construction, imports ``openbb`` lazily and captures ``obb``. Each
    dispatch resolves a dotted command path by attribute walk and invokes the
    leaf — async callables are awaited; sync ones run on the default thread
    pool so concurrent batch requests don't block the loop.
    """

    def __init__(self) -> None:
        from openbb import obb

        self._obb = obb

    @staticmethod
    def _resolve(root: Any, path: str) -> Any:
        node: Any = root
        for part in path.split("."):
            if not part:
                raise CommandNotFound(f"Empty segment in command path: {path!r}")
            try:
                node = getattr(node, part)
            except AttributeError as exc:
                raise CommandNotFound(
                    f"Command not found: {path!r} (failed at {part!r})"
                ) from exc
        return node

    @staticmethod
    def _serialize(value: Any) -> Any:
        if value is None:
            return None
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "to_dict"):
            return value.to_dict(orient="records")
        return value

    async def dispatch(self, request: Request) -> Response:
        """Resolve ``request`` against ``obb`` and execute the leaf command."""
        try:
            command = self._resolve(self._obb, request.command)
            if not callable(
                command
            ):  # pragma: no cover — defensive against malformed namespace
                raise CommandNotFound(
                    f"Resolved {request.command!r} but it is not callable"
                )
            if inspect.iscoroutinefunction(command):
                result = await command(**request.params)
            else:
                result = await asyncio.to_thread(command, **request.params)
            return Response(
                id=request.id, ok=True, result=self._serialize(result), error=None
            )
        except CommandNotFound as exc:
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(type="CommandNotFound", message=str(exc)),
            )
        except Exception as exc:  # noqa: BLE001 — surface failures, don't crash the loop
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(type=type(exc).__name__, message=str(exc)),
            )

    async def aclose(self) -> None:
        """No-op — the local dispatcher holds no external resources."""
        return None
