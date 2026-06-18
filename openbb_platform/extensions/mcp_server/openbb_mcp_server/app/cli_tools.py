"""First-class MCP tools wrapping ``openbb-cli`` dispatchers.

Exposes ``openbb-cli``'s NDJSON dispatcher protocol as MCP tools so
agents can issue OpenBB commands without standing up a Python REPL or
shelling out. Two execution modes share the same tool surface:

* **Local** (in-process) — ``LocalDispatcher`` resolves commands
  against the ``obb`` namespace. Single-tenant, pays the heavy
  ``import openbb`` once at startup.
* **Remote** (over HTTP) — ``HttpDispatcher`` proxies commands to a
  long-running ``openbb-platform-api`` server. Multi-tenant,
  container-friendly (the heavy import lives on the server).

Mode selection is per-call: pass ``server_url`` (or set
``OPENBB_SERVER_URL``) to use the HTTP dispatcher, otherwise the
local dispatcher runs in-process.

The tools are only registered when ``openbb-cli`` is installed —
``openbb-mcp-server`` declares it as an optional extra
(``openbb-mcp-server[cli]``) so deployments that only need the
REST→MCP bridge don't have to ship the CLI surface.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Field

if TYPE_CHECKING:  # pragma: no cover — TYPE_CHECKING-only import
    from fastmcp import FastMCP

# Use stdlib logging instead of fastmcp.utilities.logging.get_logger so
# the module body stays import-cheap — this matters for the
# ``--help`` short-circuit in ``main.py``, which loads
# ``openbb_mcp_server.app/__init__.py`` (which eagerly binds every
# submodule for mock.patch reliability) but doesn't actually want to
# pay for fastmcp on the help path.
logger = logging.getLogger("openbb_mcp_server.cli_tools")


def _openbb_cli_available() -> bool:
    """Return True when ``openbb-cli`` is importable.

    Used as a soft gate so the MCP server boots cleanly on
    deployments that didn't install the optional ``[cli]`` extra.
    """
    try:
        import openbb_cli.dispatchers  # noqa: F401
    except ImportError:
        return False
    return True


def register_cli_tools(mcp: FastMCP) -> bool:
    """Register the ``openbb-cli`` dispatcher tools on ``mcp``.

    Returns ``True`` when the tools were registered, ``False`` when
    ``openbb-cli`` isn't installed (the caller logs an info message
    and continues).

    The registered tools share session-lifetime dispatcher singletons
    so the heavy ``import openbb`` (LocalDispatcher) and the httpx
    client (HttpDispatcher) only initialize once per server process.
    """
    if not _openbb_cli_available():
        logger.info(
            "openbb-cli not installed; skipping CLI dispatcher tool registration. "
            "Install 'openbb-mcp-server[cli]' to enable openbb_dispatch / openbb_batch."
        )
        return False

    from openbb_cli.dispatchers import HttpDispatcher, LocalDispatcher, Request

    # Lazy singletons — instantiating ``LocalDispatcher`` triggers
    # ``import openbb`` (heavy), so we defer to first call. Same for
    # ``HttpDispatcher`` per server URL.
    _local: dict[str, LocalDispatcher] = {}
    _http: dict[str, HttpDispatcher] = {}

    def _resolve_server_url(supplied: str | None) -> str | None:
        """Pick the server URL: explicit arg → env var → None (local)."""
        if supplied:
            return supplied
        return os.environ.get("OPENBB_SERVER_URL") or None

    def _get_local() -> LocalDispatcher:
        if "default" not in _local:
            _local["default"] = LocalDispatcher()
        return _local["default"]

    def _get_http(server_url: str) -> HttpDispatcher:
        if server_url not in _http:
            _http[server_url] = HttpDispatcher(base_url=server_url)
        return _http[server_url]

    @mcp.tool(tags={"cli", "openbb"})
    async def openbb_dispatch(
        command: Annotated[
            str,
            Field(
                description=(
                    "Dotted command path under the ``obb`` namespace. "
                    "Examples: ``equity.price.historical``, ``economy.gdp``, "
                    "``crypto.search``. Use ``openbb_list_commands`` to discover "
                    "what's available."
                ),
            ),
        ],
        params: Annotated[
            dict[str, Any] | None,
            Field(
                description=(
                    "Keyword arguments forwarded to the underlying command. "
                    "Use the same parameter names the command's Python signature "
                    'accepts (e.g. ``{"symbol": "AAPL", "provider": "yfinance"}``).'
                ),
            ),
        ] = None,
        server_url: Annotated[
            str | None,
            Field(
                description=(
                    "When set, dispatches against a remote ``openbb-platform-api`` "
                    "server (HTTP). When omitted, falls back to ``OPENBB_SERVER_URL`` "
                    "env var, then to in-process local dispatch. Use a remote "
                    "server in container deployments where ``import openbb`` is "
                    "too heavy for the MCP process."
                ),
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Execute a single OpenBB command and return its serialized result.

        Wraps ``openbb-cli``'s dispatcher protocol — the same Request/
        Response shape ``openbb --batch`` uses on stdin/stdout. The tool
        serializes the command result via ``model_dump`` (Pydantic) /
        ``to_dict(orient="records")`` (DataFrame) / passthrough so the
        return value is always JSON-friendly.
        """
        request = Request(command=command, params=params or {})
        url = _resolve_server_url(server_url)

        if url:
            response = await _get_http(url).dispatch(request)
        else:
            response = await _get_local().dispatch(request)

        return response.model_dump(mode="json")

    @mcp.tool(tags={"cli", "openbb"})
    async def openbb_batch_dispatch(
        requests: Annotated[
            list[dict[str, Any]],
            Field(
                description=(
                    "List of dispatch requests. Each entry must have ``command`` "
                    "(dotted path) and may have ``params`` (dict) and ``id`` "
                    "(opaque correlation id echoed on the response)."
                ),
            ),
        ],
        server_url: Annotated[
            str | None,
            Field(
                description=(
                    "Same semantics as ``openbb_dispatch`` — explicit URL → "
                    "``OPENBB_SERVER_URL`` env var → in-process local dispatch."
                ),
            ),
        ] = None,
    ) -> list[dict[str, Any]]:
        """Execute many OpenBB commands and return results in input order.

        Concurrent on the dispatcher: each request is awaited as its own
        task so independent commands don't serialize. Order of results
        matches input order; failures surface as response objects with
        ``ok=False`` and a structured ``error`` block (no exception
        bubbles up — errors are per-request, not per-batch).
        """
        import asyncio

        url = _resolve_server_url(server_url)
        dispatcher = _get_http(url) if url else _get_local()

        request_objs = [
            Request(
                command=r["command"],
                params=r.get("params") or {},
                id=r.get("id"),
            )
            for r in requests
        ]
        responses = await asyncio.gather(
            *(dispatcher.dispatch(req) for req in request_objs)
        )
        return [r.model_dump(mode="json") for r in responses]

    @mcp.tool(tags={"cli", "openbb"})
    async def openbb_describe_command(
        command: Annotated[
            str,
            Field(
                description=(
                    "Dotted command path. Returns the parameter schema, "
                    "description, and provider info as known to the dispatcher."
                ),
            ),
        ],
        server_url: Annotated[
            str | None,
            Field(
                description="See ``openbb_dispatch`` for URL resolution.",
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Return ``--describe`` metadata for a single command.

        Uses ``HttpDispatcher.describe`` against a remote spec when a
        ``server_url`` is in play; otherwise introspects the local
        ``obb`` namespace via the LocalDispatcher.
        """
        url = _resolve_server_url(server_url)

        if url:
            http = _get_http(url)
            describe = getattr(http, "describe", None)
            if describe is None:
                raise RuntimeError(
                    "Remote describe is not supported by this openbb-cli version."
                )
            if _is_coroutine_function(describe):
                return await describe(command)
            return describe(command)

        local = _get_local()
        describe = getattr(local, "describe", None)
        if describe is None:
            raise RuntimeError(
                "Local describe is not supported by this openbb-cli version."
            )
        if _is_coroutine_function(describe):
            return await describe(command)
        return describe(command)

    return True


def _is_coroutine_function(fn) -> bool:
    """Return True when ``fn`` should be ``await``ed.

    Wraps ``inspect.iscoroutinefunction`` so the check stays in one
    place — ``LocalDispatcher.describe`` may be sync or async
    depending on the openbb-cli version we're running against.
    """
    import inspect

    return inspect.iscoroutinefunction(fn)
