"""Unit tests for app module."""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp.server.openapi import OpenAPITool
from fastmcp.utilities.openapi import HTTPRoute
from openbb_mcp_server.app.app import (
    _extract_brief_description,
    _get_mcp_config_from_route,
    _read_system_prompt_file,
    _strip_api_prefix,
    create_mcp_server,
)
from openbb_mcp_server.models.settings import MCPSettings


def test_extract_brief_description():
    """Test _extract_brief_description function."""
    assert _extract_brief_description("Brief.\n\n**Query Parameters:**") == "Brief."
    assert _extract_brief_description("Brief.") == "Brief."
    assert _extract_brief_description("") == "No description available"


def test_get_mcp_config_from_route():
    """Test _get_mcp_config_from_route function."""
    route = APIRoute(
        "/test", lambda: None, openapi_extra={"mcp_config": {"expose": True}}
    )
    assert _get_mcp_config_from_route(route) == {"expose": True}
    assert _get_mcp_config_from_route(None) == {}


def test_strip_api_prefix():
    """Test _strip_api_prefix function."""
    assert _strip_api_prefix("/api/v1/test", "/api/v1") == "test"
    assert _strip_api_prefix("/test", "/api/v1") == "test"
    assert _strip_api_prefix("/api/v1/test/path", "/api/v1") == "test/path"


def test_read_system_prompt_file(tmp_path):
    """Test _read_system_prompt_file function."""
    prompt_file = tmp_path / "prompt.txt"
    prompt_file.write_text("Test prompt")
    assert _read_system_prompt_file(str(prompt_file)) == "Test prompt"
    assert _read_system_prompt_file("nonexistent.txt") is None


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.ToolRegistry")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_customization(
    mock_from_fastapi, mock_tool_registry, mock_process_routes
):
    """Test create_mcp_server function ensures tool registration and customization."""
    settings = MCPSettings()
    fastapi_app = FastAPI()

    @fastapi_app.get("/test/dummy")
    def dummy_route():
        """Dummy Route."""

    route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
    route.openapi_extra = {"mcp_config": {"name": "my_dummy_tool"}}

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {("/test/dummy", "GET"): route}
    mock_processed_data.route_maps = [
        {"path": "/test/dummy", "methods": ["GET"], "mcp_type": "tool"}
    ]
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_registry_instance = MagicMock()
    mock_tool_registry.return_value = mock_registry_instance

    mock_mcp_instance = MagicMock()
    mock_from_fastapi.return_value = mock_mcp_instance

    mcp_server = create_mcp_server(settings, fastapi_app)

    assert mcp_server == mock_mcp_instance
    mock_from_fastapi.assert_called_once()

    _, kwargs = mock_from_fastapi.call_args
    customize_components_func = kwargs["mcp_component_fn"]

    mock_http_route = HTTPRoute(path="/test/dummy", method="GET")
    mock_openapi_tool = OpenAPITool(
        MagicMock(),
        mock_http_route,
        name="original_name",
        description="desc",
        parameters={},
        director=MagicMock(),
    )

    customize_components_func(mock_http_route, mock_openapi_tool)

    assert mock_openapi_tool.name == "my_dummy_tool"
    mock_registry_instance.register_tool.assert_called_once_with(
        category="test",
        subcategory="general",
        tool_name="my_dummy_tool",
        tool=mock_openapi_tool,
    )


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.ToolRegistry")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_tool_enable_disable(
    mock_from_fastapi, mock_tool_registry, mock_process_routes
):
    """Test tool enable/disable logic based on settings."""
    settings = MCPSettings(default_tool_categories=["enabled_category"])  # type: ignore
    fastapi_app = FastAPI()

    # Mock routes for two different categories
    @fastapi_app.get("/enabled_category/tool1")
    def enabled_route():
        pass

    @fastapi_app.get("/disabled_category/tool2")
    def disabled_route():
        pass

    enabled_fa_route = next(
        r
        for r in fastapi_app.routes
        if isinstance(r, APIRoute) and r.path == "/enabled_category/tool1"
    )
    disabled_fa_route = next(
        r
        for r in fastapi_app.routes
        if isinstance(r, APIRoute) and r.path == "/disabled_category/tool2"
    )

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {
        ("/enabled_category/tool1", "GET"): enabled_fa_route,
        ("/disabled_category/tool2", "GET"): disabled_fa_route,
    }
    mock_processed_data.route_maps = [
        {"path": "/enabled_category/tool1", "methods": ["GET"], "mcp_type": "tool"},
        {"path": "/disabled_category/tool2", "methods": ["GET"], "mcp_type": "tool"},
    ]
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_registry_instance = MagicMock()
    mock_tool_registry.return_value = mock_registry_instance

    create_mcp_server(settings, fastapi_app)

    _, kwargs = mock_from_fastapi.call_args
    customize_components_func = kwargs["mcp_component_fn"]

    # Test enabled tool
    enabled_http_route = HTTPRoute(path="/enabled_category/tool1", method="GET")
    enabled_tool = OpenAPITool(
        MagicMock(),
        enabled_http_route,
        name="tool1",
        description="desc",
        parameters={},
        director=MagicMock(),
    )
    customize_components_func(enabled_http_route, enabled_tool)
    assert enabled_tool.enabled

    # Test disabled tool
    disabled_http_route = HTTPRoute(path="/disabled_category/tool2", method="GET")
    disabled_tool = OpenAPITool(
        MagicMock(),
        disabled_http_route,
        name="tool2",
        description="desc",
        parameters={},
        director=MagicMock(),
    )
    customize_components_func(disabled_http_route, disabled_tool)
    assert not disabled_tool.enabled
