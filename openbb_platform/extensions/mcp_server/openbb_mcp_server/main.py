"""OpenBB MCP Server."""

import asyncio
import logging
import sys
from typing import Dict, List, Optional, Set

import click
import uvicorn
from fastapi import FastAPI, HTTPException, Query, routing
from fastapi_mcp import FastApiMCP
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.mcp_settings import MCPSettings
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.service.system_service import SystemService
from openbb_core.app.static.container import Container

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "info"):
    """Set up logging for the MCP server."""
    logger.setLevel(log_level.upper())
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_available_tool_categories(app: FastAPI) -> Set[str]:
    """Get available tool categories from the app."""
    categories = set()
    for route in app.routes:
        if hasattr(route, "tags") and route.tags:
            categories.update(route.tags)
    return categories


def filter_tool_categories_by_settings(
    categories: Set[str], settings: MCPSettings
) -> Set[str]:
    """Filter tool categories based on MCP settings."""
    if settings.allowed_tool_categories:
        return {c for c in categories if c in settings.allowed_tool_categories}
    return categories


def filter_providers_by_settings(settings: MCPSettings) -> List[str]:
    """Filter providers based on MCP settings."""
    logger.info(
        f"Filtering providers. Settings allowed_providers: {settings.allowed_providers}"
    )
    # Get all provider names from ProviderInterface
    provider_interface = ProviderInterface()
    all_providers = provider_interface.available_providers

    # Apply settings filters
    providers = all_providers
    if settings.allowed_providers:
        providers = [p for p in providers if p in settings.allowed_providers]
        logger.debug(f"Filtered providers: {providers}")
    else:
        logger.debug("No allowed_providers setting found, returning all providers.")

    # Filter by credentials if required
    if settings.require_valid_credentials:
        container = Container(CommandRunner())
        providers = [
            p for p in providers if container._check_credentials(p) in [True, None]
        ]
        logger.debug(f"Filtered by credentials: {providers}")

    return providers


def get_tools_for_categories(
    app: FastAPI, categories: List[str], allowed_providers: List[str]
) -> Dict[str, List[str]]:
    """Get operation/tool IDs for the given tool categories, filtered by allowed providers."""
    tools: Dict[str, List[str]] = {}
    provider_interface = ProviderInterface()
    provider_map = provider_interface.map

    for category in categories:
        tools[category] = []
        for route in app.routes:
            if (
                hasattr(route, "tags")
                and route.tags
                and category in route.tags
                and hasattr(route, "operation_id")
            ):
                tool_id = route.operation_id
                openapi_extra = getattr(route, "openapi_extra", {}) or {}
                model_name = openapi_extra.get("model")

                include_tool = False
                if model_name and model_name in provider_map:
                    # Get providers supporting this specific tool
                    tool_providers = set(provider_map[model_name].keys())
                    if "openbb" in tool_providers:
                        tool_providers.remove("openbb")

                    # Only include tool if it has at least one allowed provider
                    if any(p in allowed_providers for p in tool_providers):
                        include_tool = True
                elif not model_name and category == "mcp":
                    # Include MCP management tools in the MCP category
                    include_tool = True

                if include_tool:
                    tools[category].append(tool_id)

    return tools


def create_mcp_instance(
    app: FastAPI,
    settings: MCPSettings,
    active_categories: List[str] | None = None,
    active_tools: List[str] | None = None,
) -> FastApiMCP:
    """Create a FastApiMCP instance with specified settings."""
    mcp_final_include_tags = (
        active_categories
        if active_categories is not None
        else settings.default_tool_categories
    )
    mcp_final_include_operations = active_tools if active_tools is not None else []

    # Ensure required tools are always included
    current_tools_set = set(mcp_final_include_operations)
    current_tools_set.update(settings.required_tools)
    mcp_final_include_operations = list(current_tools_set)

    # If specific tools are provided, disable category-based loading
    if settings.initial_tools and len(settings.initial_tools) > 0:
        mcp_final_include_tags = []

    return FastApiMCP(
        app,
        name=settings.name,
        description=settings.description,
        include_tags=mcp_final_include_tags,
        include_operations=mcp_final_include_operations,
        describe_all_responses=settings.describe_all_responses,
        describe_full_response_schema=settings.describe_full_response_schema,
    )


def mount_mcp_server(app: FastAPI, settings: MCPSettings, log_level: str = "info"):
    """Mount the MCP server and related endpoints onto the given FastAPI app."""
    # Remove existing MCP routes to prevent duplicates
    mcp_routes = [
        route
        for route in app.routes
        if isinstance(route, routing.APIRoute) and route.path.startswith("/mcp/")
    ]
    for route in mcp_routes:
        app.routes.remove(route)

    setup_logging(log_level)

    all_tool_categories = filter_tool_categories_by_settings(
        get_available_tool_categories(app), settings
    )
    active_categories: list[str] = settings.default_tool_categories[:]
    active_tools: list[str] = list(settings.initial_tools or [])
    active_tools.extend(settings.required_tools)
    active_tools = list(set(active_tools))

    update_lock = asyncio.Lock()

    @app.get(
        "/mcp/available_tool_categories",
        tags=["mcp"],
        operation_id="get_available_tool_categories",
        summary="""Get information about available tools from the OpenBB MCP Server.
        This will return a list of tool categories""",
    )
    async def get_tool_categories_endpoint():
        """Get available and active tool categories."""
        available_providers = filter_providers_by_settings(settings)
        return {
            "available_tool_categories": list(all_tool_categories),
            "active_tool_categories": active_categories,
            "available_providers": available_providers,
        }

    @app.get(
        "/mcp/available_tools",
        tags=["mcp"],
        operation_id="get_available_tools",
        summary="Get available tools for active tool categories.",
    )
    async def get_tools_endpoint():
        """Get tool IDs for currently active tool categories."""
        all_tools = get_tools_for_categories(
            app, active_categories, filter_providers_by_settings(settings)
        )
        available_tools = {}
        for category, tools in all_tools.items():
            available_tools[category] = tools

        return {
            "active_tool_categories": active_categories,
            "available_tools": available_tools,  # Tools available based on active categories
            "active_tools": active_tools,  # Tools currently active for the agent
            "total_available_tools": sum(
                len(tools) for tools in available_tools.values()
            ),
            "total_active_tools": len(active_tools),
        }

    @app.post(
        "/mcp/activate_tool_categories",
        tags=["mcp"],
        operation_id="activate_tool_categories",
        summary="Activate MCP tool categories.",
    )
    # TODO: Some clients need manual refresh to see the new tools (e.g. Cursor)
    async def activate_tool_categories_endpoint(
        categories: List[str] = Query(
            ..., description="The tool categories to activate"
        ),
    ):
        """
        Hot-swap the tool category filter without restarting the server.

        Note: Activating tool categories makes their tools available for selection,
        but does not automatically activate all tools in those categories.
        """
        invalid = set(categories) - all_tool_categories
        if invalid:
            raise HTTPException(
                status_code=422, detail=f"Invalid tool categories: {', '.join(invalid)}"
            )

        async with update_lock:
            active_categories[:] = categories
            # Do NOT update mcp or call setup_server here

        available_tools = get_tools_for_categories(
            app, active_categories, filter_providers_by_settings(settings)
        )
        return {
            "message": "MCP tool categories activated",
            "active_tool_categories": active_categories,
            "available_tools": available_tools,  # Tools now available
            "active_tools": active_tools,  # Currently active tools (unchanged)
            "total_available_tools": sum(
                len(tools) for tools in available_tools.values()
            ),
            "total_active_tools": len(active_tools),
        }

    @app.post(
        "/mcp/activate_tools",
        tags=["mcp"],
        operation_id="activate_tools",
        summary="Activate specific MCP tools.",
    )
    # TODO: Some clients need manual refresh to see the new tools (e.g. Cursor)
    async def update_tools_endpoint(
        tools: List[str] = Query(..., description="The tools to activate"),
    ):
        """
        Hot-swap the tool filter without restarting the server.

        Note: MCP management tools cannot be deactivated.
        """
        tools_set = set(tools)
        tools_set.update(settings.required_tools)

        # Get all available tools from routes for active categories
        available_tools = get_tools_for_categories(
            app, active_categories, filter_providers_by_settings(settings)
        )
        all_available_tools = set()
        for tools_list in available_tools.values():
            all_available_tools.update(tools_list)

        # Check for invalid tools that are not in required_tools
        invalid = {
            tool
            for tool in tools_set
            if tool not in all_available_tools and tool not in settings.required_tools
        }
        if invalid:
            raise HTTPException(
                status_code=422, detail=f"Invalid tool(s): {', '.join(invalid)}"
            )

        async with update_lock:
            active_tools[:] = list(tools_set)
            mcp._include_operations = active_tools
            # Temporarily clear tags to ensure only specified tools are (re)loaded
            mcp._include_tags = []
            mcp.setup_server()

        return {
            "message": "MCP tools updated",
            "active_tool_categories": active_categories,
            "available_tools": available_tools,
            "active_tools": active_tools,
            "total_available_tools": sum(
                len(tools_list) for tools_list in available_tools.values()
            ),
            "total_active_tools": len(active_tools),
        }

    mcp = create_mcp_instance(app, settings, active_categories, active_tools)
    mcp.mount()


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8001, help="Port to listen on")
@click.option(
    "--categories", help="Initial tool categories to enable (comma-separated)"
)
@click.option("--log-level", default="info", help="Logging level")
def main(
    host: Optional[str] = None,
    port: Optional[int] = None,
    categories: Optional[str] = None,
    log_level: Optional[str] = None,
):
    """Start the OpenBB MCP server."""
    try:
        system_service = SystemService()
        mcp_settings = getattr(system_service.system_settings, "mcp_settings", None)

        if isinstance(mcp_settings, MCPSettings):
            settings = mcp_settings
        elif isinstance(mcp_settings, dict):
            settings = MCPSettings(**mcp_settings)
        else:
            settings = MCPSettings()

        # Override with command line arguments
        if categories:
            settings.default_tool_categories = categories.split(",")

        # Import the FastAPI app
        from openbb_core.api.rest_api import app

        mount_mcp_server(app, settings, log_level or "info")
        uvicorn.run(app, host=host, port=port, log_level=(log_level or "info").lower())

    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
