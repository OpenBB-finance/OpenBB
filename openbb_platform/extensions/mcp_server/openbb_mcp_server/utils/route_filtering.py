"""Route filtering utilities for MCP server using FastMCP RouteMap."""

import re
from typing import List

from fastmcp.server.openapi import MCPType, RouteMap

from .settings import MCPSettings


def create_route_maps_from_settings(settings: MCPSettings) -> List[RouteMap]:
    """
    Create RouteMap objects based on MCPSettings for filtering routes.

    Parameters
    ----------
    settings : MCPSettings
        MCPSettings instance with filtering configuration

    Returns
    -------
    List[RouteMap]
        List of RouteMap objects that FastMCP will use for filtering
    """
    route_maps = []

    if settings.allowed_tool_categories:
        # Create patterns for allowed categories
        allowed_pattern = "|".join(
            re.escape(cat) for cat in settings.allowed_tool_categories
        )

        # Include only allowed categories
        route_maps.append(
            RouteMap(
                pattern=rf"^/api/v\d+/({allowed_pattern})/.*",
                mcp_type=MCPType.TOOL,
            )
        )

        # Exclude everything else
        route_maps.append(
            RouteMap(
                pattern=rf"^/api/v\d+/(?!({allowed_pattern})/).*",
                mcp_type=MCPType.EXCLUDE,
            )
        )

    return route_maps
