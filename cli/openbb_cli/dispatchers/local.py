"""In-process dispatcher — resolves commands against the real ``obb`` namespace."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any

from openbb_cli.dispatchers.protocol import Request, Response, ResponseError


class CommandNotFound(KeyError):
    """Raised when a dotted command path does not resolve under ``obb``."""


class LocalDispatcher:
    """Single-tenant in-process dispatcher."""

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
            return value.model_dump(exclude_unset=True, exclude_none=True)
        if hasattr(value, "to_dict"):
            return value.to_dict(orient="records")
        return value

    async def dispatch(self, request: Request) -> Response:
        """Resolve ``request`` against ``obb`` and execute the leaf command."""
        try:
            command = self._resolve(self._obb, request.command)
            if not callable(command):  # pragma: no cover
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
        except Exception as exc:  # noqa: BLE001
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(type=type(exc).__name__, message=str(exc)),
            )

    async def aclose(self) -> None:
        """No-op — the local dispatcher holds no external resources."""
        return None
