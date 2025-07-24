"""Unit tests for main module."""

import sys
from unittest.mock import ANY, MagicMock, patch

import pytest
from fastapi import FastAPI
from openbb_mcp_server.main import _extract_brief_description, create_mcp_server, main
from openbb_mcp_server.utils.settings import MCPSettings

# Skip all tests if Python version < 3.10
if sys.version_info < (3, 10):
    pytest.skip("MCP server requires Python 3.10+", allow_module_level=True)


def test_extract_brief_description():
    full_desc = """Brief description.

**Query Parameters:**
Details..."""
    assert _extract_brief_description(full_desc) == "Brief description."

    no_desc = ""
    assert _extract_brief_description(no_desc) == "No description available"

    no_split = "Just brief."
    assert _extract_brief_description(no_split) == "Just brief."

    responses_split = """Brief.

**Responses:**
Details..."""
    assert _extract_brief_description(responses_split) == "Brief."


@patch("openbb_mcp_server.main.FastMCP.from_fastapi")
@patch("openbb_mcp_server.main.ToolRegistry")
def test_create_mcp_server(_mock_registry, mock_from_fastapi):
    settings = MCPSettings(enable_tool_discovery=False)
    app = FastAPI()

    mock_mcp = MagicMock()
    mock_from_fastapi.return_value = mock_mcp

    mcp = create_mcp_server(settings, app)
    assert mcp == mock_mcp
    mock_from_fastapi.assert_called_once()

    # Test with discovery enabled
    settings = MCPSettings(enable_tool_discovery=True)
    create_mcp_server(settings, app)


@patch("openbb_mcp_server.main.parse_args")
@patch("openbb_mcp_server.main.load_mcp_settings_with_overrides")
@patch("openbb_mcp_server.main.create_mcp_server")
@patch("openbb_mcp_server.main.SystemService")
@patch("sys.exit")
def test_main(mock_exit, mock_system, mock_create, mock_load, mock_parse):
    mock_args = MagicMock()
    mock_args.transport = "http"
    mock_args.host = "localhost"
    mock_args.port = 8000
    mock_args.allowed_categories = None
    mock_args.default_categories = "all"
    mock_args.no_tool_discovery = False
    mock_parse.return_value = mock_args

    mock_settings = MCPSettings()
    mock_load.return_value = mock_settings

    mock_mcp = MagicMock()
    mock_create.return_value = mock_mcp

    mock_system.return_value.system_settings.api_settings.cors.allow_origins = ["*"]
    mock_system.return_value.system_settings.api_settings.cors.allow_methods = ["*"]
    mock_system.return_value.system_settings.api_settings.cors.allow_headers = ["*"]

    main()
    mock_mcp.run.assert_called_once_with(
        transport="http",
        host="localhost",
        port=8000,
        middleware=ANY,
    )

    # Test stdio transport
    mock_args.transport = "stdio"
    main()
    mock_mcp.run.assert_called_with(transport="stdio")

    # Test exception handling
    mock_create.side_effect = Exception("Test error")
    main()
    mock_exit.assert_called_once_with(1)
