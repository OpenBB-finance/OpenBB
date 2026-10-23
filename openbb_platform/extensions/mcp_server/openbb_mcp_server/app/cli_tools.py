"""MCP tools that wrap the ``openbb-cli`` dispatcher protocol."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Field

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger("openbb_mcp_server.cli_tools")

_SERVER_URL_DESCRIPTION = (
    "When set, targets a remote ``openbb-platform-api`` server (HTTP). When omitted,"
    " falls back to the ``OPENBB_SERVER_URL`` env var, then to the in-process"
    " ``obb`` namespace. Use a remote server in container deployments where"
    " ``import openbb`` is too heavy for the MCP process."
)


def _openbb_cli_available() -> bool:
    """Return True when ``openbb-cli`` is importable."""
    try:
        import openbb_cli.dispatchers  # noqa: F401
    except ImportError:
        return False
    return True


def register_cli_tools(mcp: FastMCP) -> bool:
    """Register the ``openbb-cli`` dispatcher tools on ``mcp``.

    Parameters
    ----------
    mcp : FastMCP
        The server to register the tools on.

    Returns
    -------
    bool
        True when the tools were registered, False when ``openbb-cli`` is not installed.
    """
    if not _openbb_cli_available():
        logger.info(
            "openbb-cli not installed; skipping CLI dispatcher tool registration. "
            "Install 'openbb-mcp-server[cli]' to enable openbb_dispatch / openbb_batch_dispatch."
        )
        return False

    from openbb_cli.dispatchers import LocalDispatcher, Request
    from openbb_cli.dispatchers.http import (
        HttpDispatcher,
        http_dispatcher_from_server,
        http_dispatcher_from_spec,
    )
    from openbb_cli.dispatchers.spec import build_spec_document

    local: dict[str, Any] = {}
    remote: dict[str, HttpDispatcher] = {}

    def _resolve_server_url(supplied: str | None) -> str | None:
        """Pick the server URL: explicit argument, then ``OPENBB_SERVER_URL``, else None."""
        return supplied or os.environ.get("OPENBB_SERVER_URL") or None

    def _local_dispatcher() -> LocalDispatcher:
        """Return the shared in-process dispatcher."""
        if "dispatcher" not in local:
            local["dispatcher"] = LocalDispatcher()
        return local["dispatcher"]

    def _local_catalog() -> HttpDispatcher:
        """Return a spec-backed dispatcher that answers introspection for the local ``obb``."""
        if "catalog" not in local:
            from openbb_core.api.rest_api import app

            local["catalog"] = http_dispatcher_from_spec(
                build_spec_document(app.openapi(), base_url="http://localhost")
            )
        return local["catalog"]

    async def _remote_dispatcher(server_url: str) -> HttpDispatcher:
        """Return the shared spec-backed dispatcher for one remote server."""
        if server_url not in remote:
            remote[server_url] = await asyncio.to_thread(
                http_dispatcher_from_server, server_url
            )
        return remote[server_url]

    async def _executor(server_url: str | None) -> LocalDispatcher | HttpDispatcher:
        """Return the dispatcher that executes commands for ``server_url``."""
        url = _resolve_server_url(server_url)
        return await _remote_dispatcher(url) if url else _local_dispatcher()

    async def _catalog(server_url: str | None) -> HttpDispatcher:
        """Return the dispatcher that answers introspection for ``server_url``."""
        url = _resolve_server_url(server_url)
        return await _remote_dispatcher(url) if url else _local_catalog()

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
            str | None, Field(description=_SERVER_URL_DESCRIPTION)
        ] = None,
    ) -> dict[str, Any]:
        """Execute one OpenBB command and return its serialized response."""
        dispatcher = await _executor(server_url)
        response = await dispatcher.dispatch(
            Request(command=command, params=params or {})
        )
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
            str | None, Field(description=_SERVER_URL_DESCRIPTION)
        ] = None,
    ) -> list[dict[str, Any]]:
        """Execute OpenBB commands concurrently and return their responses in input order."""
        dispatcher = await _executor(server_url)
        responses = await asyncio.gather(
            *(
                dispatcher.dispatch(
                    Request(
                        command=entry["command"],
                        params=entry.get("params") or {},
                        id=entry.get("id"),
                    )
                )
                for entry in requests
            )
        )
        return [response.model_dump(mode="json") for response in responses]

    @mcp.tool(tags={"cli", "openbb"})
    async def openbb_list_commands(
        server_url: Annotated[
            str | None, Field(description=_SERVER_URL_DESCRIPTION)
        ] = None,
    ) -> dict[str, Any]:
        """List every OpenBB command with a one-line description."""
        catalog = await _catalog(server_url)
        response = await catalog.dispatch(Request(command="__commands__"))
        return response.model_dump(mode="json")

    @mcp.tool(tags={"cli", "openbb"})
    async def openbb_describe_command(
        command: Annotated[
            str,
            Field(description="Dotted command path, e.g. ``equity.price.historical``."),
        ],
        provider: Annotated[
            str | None,
            Field(
                description="Optional provider to narrow the parameters and output schema to."
            ),
        ] = None,
        server_url: Annotated[
            str | None, Field(description=_SERVER_URL_DESCRIPTION)
        ] = None,
    ) -> dict[str, Any]:
        """Return the parameters and output schema of one OpenBB command."""
        params: dict[str, Any] = {"name": command}
        if provider:
            params["provider"] = provider
        catalog = await _catalog(server_url)
        response = await catalog.dispatch(Request(command="__schema__", params=params))
        return response.model_dump(mode="json")

    return True
