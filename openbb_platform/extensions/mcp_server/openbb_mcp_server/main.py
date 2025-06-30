"""OpenBB MCP Server."""

import logging
import re
import sys
from typing import Annotated

import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.server.openapi import (
    FastMCPOpenAPI,
    OpenAPIResource,
    OpenAPIResourceTemplate,
    OpenAPITool,
)
from fastmcp.utilities.openapi import HTTPRoute
from openbb_core.api.rest_api import app
from openbb_core.app.service.system_service import SystemService
from pydantic import Field
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .registry import ToolRegistry
from .tool_models import CategoryInfo, SubcategoryInfo, ToolInfo
from .utils.config import load_mcp_settings_with_overrides, parse_args
from .utils.route_filtering import create_route_maps_from_settings
from .utils.settings import MCPSettings

logger = logging.getLogger("openbb_mcp_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("\n%(message)s\n")
handler.setFormatter(formatter)
logger.addHandler(handler)

PREFIX_SEGMENTS = ("api",)
VERSION_SEGMENT_RE = re.compile(r"v\d+\Z")


def _extract_brief_description(full_description: str) -> str:
    """Extract only the brief description before the detailed API documentation."""
    if not full_description:
        return "No description available"

    brief, *_ = re.split(
        r"\n{2,}\*\*(?:Query Parameters|Responses):", full_description, maxsplit=1
    )

    return brief.strip() or "No description available"


def create_mcp_server(settings: MCPSettings, fastapi_app: FastAPI) -> FastMCPOpenAPI:
    """Create and configure the MCP server."""
    tool_registry = ToolRegistry()

    def customize_components(
        route: HTTPRoute,
        component: OpenAPITool | OpenAPIResource | OpenAPIResourceTemplate,
    ) -> None:
        """Attach category/tool tags & disable tools that are not admin."""
        if not isinstance(component, OpenAPITool):
            return

        segments = [seg for seg in route.path.lstrip("/").split("/") if "{" not in seg]

        while segments and segments[0] in PREFIX_SEGMENTS:
            segments.pop(0)
        if segments and VERSION_SEGMENT_RE.match(segments[0]):
            segments.pop(0)

        if len(segments) < 2:
            return

        # Use hierarchical structure: category/subcategory/tool
        category = segments[0]
        if len(segments) == 2:
            subcategory = "general"
            tool = segments[1]
        else:
            subcategory = segments[1]
            tool_parts = segments[2:]
            tool = "_".join(tool_parts)

        component.name = (
            f"{category}_{subcategory}_{tool}"
            if subcategory != "general"
            else f"{category}_{tool}"
        )
        component.tags.add(category)

        if not settings.describe_responses:
            component.description = _extract_brief_description(
                component.description or ""
            )

        if "all" in settings.default_tool_categories or any(
            tag in settings.default_tool_categories for tag in component.tags
        ):
            component.enable()
        else:
            component.disable()

        tool_registry.register_tool(
            category=category,
            subcategory=subcategory,
            tool_name=component.name,
            tool=component,
        )

        return

    mcp = FastMCP.from_fastapi(
        app=fastapi_app,
        mcp_component_fn=customize_components,
        name=settings.name,
        route_maps=create_route_maps_from_settings(settings),
    )

    # Add discovery tools if enabled
    if settings.enable_tool_discovery:

        @mcp.tool(tags={"admin"})
        def available_categories() -> list[CategoryInfo]:
            """List all categories with their subcategories and tool counts.

            This gives you a complete overview of what types of tasks you can solve.
            """
            categories = tool_registry.get_categories()
            return [
                CategoryInfo(
                    name=category_name,
                    subcategories=[
                        SubcategoryInfo(name=subcat_name, tool_count=len(tools))
                        for subcat_name, tools in sorted(subcategories.items())
                    ],
                    total_tools=sum(len(tools) for tools in subcategories.values()),
                )
                for category_name, subcategories in sorted(categories.items())
            ]

        @mcp.tool(tags={"admin"})
        def available_tools(
            category: Annotated[
                str, Field(description="The category of tools to list")
            ],
            subcategory: Annotated[
                str | None,
                Field(
                    description="Optional subcategory to filter by. Use 'general' for tools directly under the category."
                ),
            ] = None,
        ) -> list[ToolInfo]:
            """For a category, list tools and whether they're currently enabled. Optionally filter by subcategory."""
            category_data = tool_registry.get_category_subcategories(category)
            if not category_data:
                available_categories = list(tool_registry.get_categories().keys())
                categories_str = ", ".join(sorted(available_categories))
                raise ValueError(
                    f"Category '{category}' not found. Available categories: {categories_str}"
                )

            if subcategory:
                # Single subcategory
                tools_dict = tool_registry.get_category_tools(category, subcategory)
                if not tools_dict:
                    available_subcategories = list(category_data.keys())
                    subcategories_str = ", ".join(sorted(available_subcategories))
                    raise ValueError(
                        f"Subcategory '{subcategory}' not found in category '{category}'. "
                        f"Available subcategories: {subcategories_str}"
                    )

                return [
                    ToolInfo(
                        name=name,
                        active=tool.enabled,
                        description=_extract_brief_description(tool.description or ""),
                    )
                    for name, tool in sorted(tools_dict.items())
                ]

            # All subcategories - flatten them
            tools_dict = tool_registry.get_category_tools(category)
            return [
                ToolInfo(
                    name=name,
                    active=tool.enabled,
                    description=_extract_brief_description(tool.description or ""),
                )
                for name, tool in sorted(tools_dict.items())
            ]

        @mcp.tool(tags={"admin"})
        def activate_tools(
            tool_names: Annotated[
                list[str], Field(description="The name of the tool to activate")
            ],
        ) -> str:
            """Activate a tool or a list of tools."""
            return tool_registry.toggle_tools(tool_names, enable=True).message

        @mcp.tool(tags={"admin"})
        def deactivate_tools(
            tool_names: Annotated[
                list[str], Field(description="The name of the tool to deactivate")
            ],
        ) -> str:
            """Deactivate a tool or a list of tools."""
            return tool_registry.toggle_tools(tool_names, enable=False).message

    return mcp


def main():
    """Start the OpenBB MCP server."""
    args = parse_args()

    try:
        overrides = {}
        if args.allowed_categories:
            overrides["allowed_tool_categories"] = args.allowed_categories.split(",")
        if args.default_categories:
            overrides["default_tool_categories"] = args.default_categories.split(",")
        if args.no_tool_discovery:
            overrides["enable_tool_discovery"] = False

        settings = load_mcp_settings_with_overrides(**overrides)
        mcp = create_mcp_server(settings, app)

        if args.transport == "stdio":
            mcp.run(transport=args.transport, host=args.host, port=args.port)

        else:
            # Get CORS settings from system configuration
            system_service = SystemService()
            cors_settings = system_service.system_settings.api_settings.cors

            cors_middleware = [
                Middleware(
                    CORSMiddleware,
                    allow_origins=cors_settings.allow_origins,
                    allow_methods=cors_settings.allow_methods,
                    allow_headers=cors_settings.allow_headers,
                ),
            ]

            # Create ASGI app with cors middleware
            http_app = mcp.http_app(
                middleware=cors_middleware,
                transport=args.transport,
                stateless_http=True,
            )

            uvicorn.run(http_app, host=args.host, port=args.port)

    except Exception as e:
        logger.error("Failed to start MCP server: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
