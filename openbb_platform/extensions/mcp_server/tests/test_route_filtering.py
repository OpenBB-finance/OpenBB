"""Unit tests for route filtering utilities."""

from fastmcp.server.openapi import MCPType
from openbb_mcp_server.utils.route_filtering import create_route_maps_from_settings
from openbb_mcp_server.utils.settings import MCPSettings


def test_create_route_maps_from_settings_no_allowed():
    settings = MCPSettings(allowed_tool_categories=None)
    route_maps = create_route_maps_from_settings(settings)
    assert len(route_maps) == 1
    assert route_maps[0].methods == ["POST"]
    assert route_maps[0].mcp_type == MCPType.EXCLUDE


def test_create_route_maps_from_settings_with_allowed():
    settings = MCPSettings(allowed_tool_categories=["equity", "crypto"])
    route_maps = create_route_maps_from_settings(settings)
    assert len(route_maps) == 3

    # Include allowed
    assert route_maps[0].pattern == r"^/api/v\d+/(equity|crypto)/.*"
    assert route_maps[0].mcp_type == MCPType.TOOL

    # Exclude others
    assert route_maps[1].pattern == r"^/api/v\d+/(?!(equity|crypto)/).*"
    assert route_maps[1].mcp_type == MCPType.EXCLUDE

    # POST exclude
    assert route_maps[2].methods == ["POST"]
    assert route_maps[2].mcp_type == MCPType.EXCLUDE


def test_create_route_maps_from_settings_empty_allowed():
    settings = MCPSettings(allowed_tool_categories=[])
    route_maps = create_route_maps_from_settings(settings)
    assert len(route_maps) == 1
    assert route_maps[0].methods == ["POST"]
    assert route_maps[0].mcp_type == MCPType.EXCLUDE
