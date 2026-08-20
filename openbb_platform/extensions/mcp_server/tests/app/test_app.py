"""Unit tests for app module."""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp.server.providers.openapi import OpenAPITool
from fastmcp.utilities.openapi import HTTPRoute
from openbb_mcp_server.app.app import (
    _extract_brief_description,
    _get_mcp_config_from_route,
    _read_system_prompt_file,
    _strip_api_prefix,
    create_mcp_server,
    main,
    stdio_main,
)
from openbb_mcp_server.models.settings import MCPSettings


@pytest.fixture(autouse=True)
def _patch_transforms():
    with patch("openbb_mcp_server.app.app.PromptsAsTools", new=MagicMock()), patch(
        "openbb_mcp_server.app.app.ResourcesAsTools", new=MagicMock()
    ):
        yield


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


@pytest.mark.asyncio
async def test_stdio_main_runs_when_signal_handlers_are_unsupported():
    """Windows event loops can serve stdio without registering signal handlers."""
    loop = asyncio.get_running_loop()
    mcp_server = MagicMock()

    with patch.object(loop, "add_signal_handler", side_effect=NotImplementedError):
        await stdio_main(mcp_server)

    mcp_server.run.assert_called_once_with("stdio")


def test_main_logs_startup_exception_with_traceback():
    """Startup failures should use exception logging instead of hiding details."""
    args = SimpleNamespace(uvicorn_config={}, imported_app=None, transport="sse")
    settings = MagicMock()
    settings.get_http_run_kwargs.return_value = {"uvicorn_config": {}}
    settings.get_httpx_kwargs.return_value = {}
    mcp_server = MagicMock()
    mcp_server.run.side_effect = RuntimeError("startup failed")

    with (
        patch("openbb_mcp_server.app.app.parse_args", return_value=args),
        patch("openbb_mcp_server.app.app.MCPService") as mock_service,
        patch("openbb_mcp_server.app.app.create_mcp_server", return_value=mcp_server),
        patch("openbb_mcp_server.app.app._build_runtime_middleware", return_value=[]),
        patch("openbb_mcp_server.app.app.logger") as mock_logger,
        pytest.raises(SystemExit, match="1"),
    ):
        mock_service.return_value.load_with_overrides.return_value = settings
        main()

    mock_logger.exception.assert_called_once_with("Server error")


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_customization(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """Test create_mcp_server function ensures tool registration and customization."""
    settings = MCPSettings()
    fastapi_app = FastAPI()

    @fastapi_app.get("/test/dummy")
    def dummy_route():
        """Handle the test dummy route request."""

    route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
    route.openapi_extra = {"mcp_config": {"name": "my_dummy_tool"}}

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {("/test/dummy", "GET"): route}
    mock_processed_data.route_maps = [
        {"path": "/test/dummy", "methods": ["GET"], "mcp_type": "tool"}
    ]
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_index_instance = MagicMock()
    mock_index_instance.all_tool_names.return_value = {"my_dummy_tool"}
    mock_category_index.return_value = mock_index_instance

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
    mock_index_instance.register.assert_called_once_with(
        category="test",
        subcategory="general",
        tool_name="my_dummy_tool",
        description="desc",
    )


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_disables_all_tools_when_discovery_enabled(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """When tool discovery is enabled, all tools are disabled at server level."""
    settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_index_instance = MagicMock()
    mock_index_instance.all_tool_names.return_value = {"tool_a", "tool_b"}
    mock_category_index.return_value = mock_index_instance

    mock_mcp_instance = MagicMock()
    mock_from_fastapi.return_value = mock_mcp_instance

    create_mcp_server(settings, fastapi_app)

    # All tools should be disabled at server level
    mock_mcp_instance.disable.assert_called_once_with(names={"tool_a", "tool_b"})


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_fixed_toolset_mode(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """When discovery disabled, disable all first then re-enable flagged tools."""
    settings = MCPSettings(
        enable_tool_discovery=False,  # type: ignore
        default_tool_categories=["equity"],  # type: ignore
    )
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_index_instance = MagicMock()
    mock_index_instance.all_tool_names.return_value = {"eq_tool", "crypto_tool"}
    mock_category_index.return_value = mock_index_instance

    mock_mcp_instance = MagicMock()
    mock_from_fastapi.return_value = mock_mcp_instance

    create_mcp_server(settings, fastapi_app)

    # All tools disabled first
    mock_mcp_instance.disable.assert_called_once_with(names={"eq_tool", "crypto_tool"})
    # No components were processed (mocked), so _enabled_tools is empty —
    # enable is not called. In real usage it would re-enable matched tools.
    mock_mcp_instance.enable.assert_not_called()
