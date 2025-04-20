"""
MCP Server for the OpenBB Platform.
"""

import asyncio
from typing import List, Set

from fastapi import FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.service.user_service import UserService


def enable_openbb_llm_mode():
    """
    Set OpenBB preferences for LLM interaction.
    """
    UserService().default_user_settings.preferences.output_type = "llm"
    system_service = SystemService()
    system_service.system_settings.python_settings.docstring_sections = [
        "description",
        "examples",
    ]
    system_service.system_settings.python_settings.docstring_max_length = 1024


def get_available_tags(app: FastAPI) -> Set[str]:
    """
    Get all available tags from the REST API routes.
    """
    tags = set()
    for route in app.routes:
        if hasattr(route, "tags") and route.tags:
            tags.update(t for t in route.tags if isinstance(t, str))
    return tags


def create_mcp_instance(app: FastAPI, active_tags: List[str] | None = None) -> FastApiMCP:
    """
    Create a FastApiMCP instance with specified tags.
    """

    return FastApiMCP(
        app,
        name="OpenBB MCP",
        description=(
            """
            All OpenBB REST endpoints exposed as MCP tools. Enables LLM agents
            to query financial data, run screeners, and build workflows using
            the exact same operations available to REST clients.
            """
        ),
        include_tags=active_tags,
        # This allows an agent to decide which endpoints is best for the task
        include_operations=["get_available_tags", "update_tags"],
        describe_all_responses=False,
        describe_full_response_schema=False,
    )


def mount_mcp_server(app: FastAPI):
    """Mounts the MCP server and related endpoints onto the given FastAPI app."""
    enable_openbb_llm_mode()

    all_tags = get_available_tags(app)
    # Start with a default subset of tags that is small and easy to manage
    initial_tags = ["news"] if "news" in all_tags else list(all_tags)[:1]
    active_tags: list[str] = initial_tags[:]
    update_lock = asyncio.Lock()

    @app.get(
        "/mcp/available_tags",
        tags=["mcp"],
        operation_id="get_available_tags",
        summary="Use this to get information about the available tools from the OpenBB MCP Server.",
    )
    async def get_tags_endpoint():
        return {"available_tags": list(all_tags), "active_tags": active_tags}

    @app.post(
        "/mcp/update_tags",
        tags=["mcp"],
        operation_id="update_tags",
        summary="Use this to update the active MCP tool tags.",
    )
    async def update_tags_endpoint(tags: List[str] = Query(...)):
        """
        Hot-swap the tag filter without restarting the server.
        Clients might need to reconnect to see the new tool list.
        """
        invalid = set(tags) - all_tags
        if invalid:
            raise HTTPException(status_code=422, detail=f"Invalid tag(s): {', '.join(invalid)}")

        async with update_lock:
            # Update the active_tags list in place
            active_tags[:] = tags
            mcp._include_tags = active_tags
            mcp.setup_server()

        return {"message": "MCP tags updated", "active_tags": active_tags}

    mcp = create_mcp_instance(app, active_tags)

    # Mount the main MCP SSE endpoint
    mcp.mount()
