"""Multi-spec dispatcher — routes namespaced commands to per-spec backends."""

from __future__ import annotations

from typing import Any

from openbb_cli.dispatchers.http import HttpDispatcher
from openbb_cli.dispatchers.protocol import Request, Response, ResponseError


class MultiSpecDispatcher:
    """Routes ``<namespace>.<command>`` to per-spec ``HttpDispatcher``s."""

    def __init__(self, dispatchers: dict[str, HttpDispatcher]) -> None:
        if not dispatchers:
            raise ValueError("MultiSpecDispatcher requires at least one namespace.")
        self._dispatchers = dict(dispatchers)
        self._spec_doc = self._merge_spec_docs()

    def _merge_spec_docs(self) -> dict[str, Any]:
        """Build an aggregated spec doc for the spec-aware parser path."""
        merged_commands: dict[str, Any] = {}
        merged_routers: dict[str, str] = {}
        merged_reference_paths: dict[str, dict[str, Any]] = {}
        merged_reference_routers: dict[str, dict[str, Any]] = {}
        for namespace, dispatcher in self._dispatchers.items():
            doc = dispatcher._spec_doc
            for cmd, entry in doc.get("commands", {}).items():
                merged_commands[f"{namespace}.{cmd}"] = entry
            merged_routers[namespace] = "menu"
            reference = doc.get("reference") or {}
            for path, meta in (reference.get("paths") or {}).items():
                prefixed = (
                    "/" + namespace + (path if path.startswith("/") else "/" + path)
                )
                merged_reference_paths[prefixed] = meta
            for router, meta in (reference.get("routers") or {}).items():
                if router == "":
                    merged_reference_routers[namespace] = meta
                else:
                    merged_reference_routers[f"{namespace}/{router}"] = meta
        return {
            "commands": merged_commands,
            "routers": merged_routers,
            "reference": {
                "paths": merged_reference_paths,
                "routers": merged_reference_routers,
            },
        }

    async def dispatch(self, request: Request, method: str | None = None) -> Response:
        """Route ``request`` to the namespace named by its leading command segment."""
        if request.command == "__commands__":
            return await self._aggregate_list_commands(request)
        if request.command == "__schema__":
            return await self._forward_schema(request)
        namespace, _, inner = request.command.partition(".")
        if not inner or namespace not in self._dispatchers:
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(
                    type="UnknownNamespace",
                    message=(
                        f"command {request.command!r} does not start with a "
                        f"declared spec namespace. Available: "
                        f"{', '.join(sorted(self._dispatchers))}."
                    ),
                ),
            )
        forwarded = Request(id=request.id, command=inner, params=request.params)
        return await self._dispatchers[namespace].dispatch(forwarded, method=method)

    async def _aggregate_list_commands(self, request: Request) -> Response:
        """Concatenate every namespace's ``__commands__`` with prefixed names."""
        rows: list[dict[str, Any]] = []
        for namespace in sorted(self._dispatchers):
            sub = await self._dispatchers[namespace].dispatch(
                Request(id=None, command="__commands__")
            )
            if not sub.ok or not isinstance(sub.result, list):
                continue
            for entry in sub.result:
                if not isinstance(entry, dict) or "name" not in entry:
                    continue
                rows.append({**entry, "name": f"{namespace}.{entry['name']}"})
        rows.sort(key=lambda r: r["name"])
        return Response(id=request.id, ok=True, result=rows, error=None)

    async def _forward_schema(self, request: Request) -> Response:
        """Strip the leading namespace from ``params['name']`` and forward."""
        params = dict(request.params or {})
        name = params.get("name") or ""
        namespace, _, inner = name.partition(".")
        if not inner or namespace not in self._dispatchers:
            return Response(
                id=request.id,
                ok=False,
                error=ResponseError(
                    type="UnknownNamespace",
                    message=(
                        f"__schema__ name {name!r} does not start with a "
                        f"declared spec namespace. Available: "
                        f"{', '.join(sorted(self._dispatchers))}."
                    ),
                ),
            )
        params["name"] = inner
        return await self._dispatchers[namespace].dispatch(
            Request(id=request.id, command="__schema__", params=params)
        )

    async def aclose(self) -> None:
        """Close every owned dispatcher."""
        for dispatcher in self._dispatchers.values():
            await dispatcher.aclose()
