"""Unit tests for openapi utilities."""

# pylint: disable=W0613,W0621

import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp.server.openapi import MCPType
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.utils.fastapi import (
    _create_prompt_definitions_for_route,
    _get_module_exclusion_targets,
    _should_exclude_by_module_and_path,
    get_api_prefix,
    get_mcp_config,
    process_fastapi_routes_for_mcp,
)


@pytest.fixture
def mock_system_service():
    """Fixture to mock SystemService."""
    with patch("openbb_mcp_server.utils.fastapi.SystemService") as mock_service_class:
        mock_instance = mock_service_class.return_value
        mock_instance.system_settings.api_settings.prefix = "/api"
        yield mock_instance


def test_get_api_prefix(mock_system_service):
    """Test API prefix retrieval logic."""
    assert get_api_prefix(None) == "/api"
    settings = MCPSettings(api_prefix="/custom")  # type: ignore
    assert get_api_prefix(settings) == "/custom"
    settings_empty = MCPSettings(api_prefix=" ")  # type: ignore
    assert get_api_prefix(settings_empty) == "/api"


def test_get_module_exclusion_targets():
    """Test retrieval of module exclusion targets."""
    assert "econometrics" in _get_module_exclusion_targets(None)
    settings = MCPSettings(module_exclusion_map={"custom": "my_module"})  # type: ignore
    assert _get_module_exclusion_targets(settings) == {"custom": "my_module"}


def test_get_mcp_config():
    """Test retrieval and validation of MCP config from a route."""
    valid_route = APIRoute(
        "/", lambda: None, openapi_extra={"mcp_config": {"mcp_type": "tool"}}
    )
    config = get_mcp_config(valid_route)
    assert config.mcp_type and config.mcp_type.value == "tool"

    # Test with x-mcp alias
    x_mcp_route = APIRoute(
        "/", lambda: None, openapi_extra={"x-mcp": {"mcp_type": "resource"}}
    )
    config = get_mcp_config(x_mcp_route)
    assert config.mcp_type and config.mcp_type.value == "resource"

    invalid_route = APIRoute("/", lambda: None, openapi_extra={"mcp_config": "invalid"})
    assert get_mcp_config(invalid_route).mcp_type is None


def test_should_exclude_by_module_and_path(mock_system_service):
    """Test route exclusion based on loaded modules."""
    # Path doesn't match any exclusion rules
    assert not _should_exclude_by_module_and_path("/api/some_other_path", None)

    # Path matches, but module not loaded
    path = "/api/econometrics/test"
    with patch.dict(sys.modules, {}, clear=True):
        assert not _should_exclude_by_module_and_path(path, None)

    # Path matches and module is loaded
    with patch.dict(sys.modules, {"openbb_econometrics": MagicMock()}):
        assert _should_exclude_by_module_and_path(path, None)

    # Custom exclusion map
    settings = MCPSettings(module_exclusion_map={"custom": "my_module"})  # type: ignore
    custom_path = "/api/custom/test"
    with patch.dict(sys.modules, {}, clear=True):
        assert not _should_exclude_by_module_and_path(custom_path, settings)
    with patch.dict(sys.modules, {"my_module": MagicMock()}):
        assert _should_exclude_by_module_and_path(custom_path, settings)


@pytest.fixture
def sample_app():
    """Create a sample FastAPI app for testing route processing."""
    app = FastAPI()

    def endpoint_a():
        """Example endpoint."""

    def endpoint_b():
        """Example endpoint."""

    def endpoint_c():
        """Example endpoint."""

    def endpoint_d(arg1: str, arg2: int = 42):
        """Example endpoint."""

    app.add_api_route("/api/v1/stocks/load", endpoint_a, methods=["GET"])
    app.add_api_route(
        "/api/v1/crypto/price",
        endpoint_b,
        methods=["POST"],
        openapi_extra={"mcp_config": {"expose": False}},
    )
    app.add_api_route("/api/v1/fake/test", endpoint_c, methods=["GET"])
    app.add_api_route(
        "/api/v1/prompts/test",
        endpoint_d,
        methods=["GET"],
        openapi_extra={
            "mcp_config": {
                "prompts": [
                    {
                        "name": "test_prompt",
                        "content": "Test with {arg1} and {arg2}",
                    }
                ]
            }
        },
    )
    return app


def test_process_routes_exclusion(sample_app, mock_system_service):
    """Test that routes are correctly removed based on config and modules."""
    # Test exclusion via `expose: False`
    with patch.dict(sys.modules, {}, clear=True):
        app_instance = MagicMock()
        app_instance.router.routes = list(sample_app.router.routes)
        processed = process_fastapi_routes_for_mcp(app_instance, None)
        assert len(processed.removed_routes) == 1
        assert processed.removed_routes[0].path == "/api/v1/crypto/price"

    # Test exclusion via loaded module
    with patch.dict(sys.modules, {"openbb_fake": MagicMock()}):
        app_instance = MagicMock()
        app_instance.router.routes = list(sample_app.router.routes)
        settings = MCPSettings(
            api_prefix="/api/v1",
            module_exclusion_map={"fake": "openbb_fake"},  # type: ignore
        )
        processed = process_fastapi_routes_for_mcp(app_instance, settings)
        removed_paths = {r.path for r in processed.removed_routes}
        assert "/api/v1/crypto/price" in removed_paths
        assert "/api/v1/fake/test" in removed_paths


def test_process_routes_route_maps(sample_app, mock_system_service):
    """Test that route maps are correctly generated."""
    sample_app.router.routes.append(
        APIRoute(
            "/api/v1/resource/test",
            lambda: None,
            methods=["GET"],
            openapi_extra={"mcp_config": {"mcp_type": "resource"}},
        )
    )
    processed = process_fastapi_routes_for_mcp(sample_app, None)
    assert len(processed.route_maps) == 2  # One explicit, one catch-all
    assert processed.route_maps[0].mcp_type == MCPType.RESOURCE
    assert processed.route_maps[1].mcp_type == MCPType.TOOL

    # Test with custom catch-all
    settings = MCPSettings(default_catchall_mcp_type="resource")  # type: ignore
    processed = process_fastapi_routes_for_mcp(sample_app, settings)
    assert processed.route_maps[-1].mcp_type == MCPType.RESOURCE


def test_process_routes_prompts(sample_app, mock_system_service):
    """Test that prompt definitions are correctly generated."""
    processed = process_fastapi_routes_for_mcp(sample_app, None)
    assert len(processed.prompt_definitions) == 1
    prompt = processed.prompt_definitions[0]
    assert prompt["name"] == "test_prompt"
    assert len(prompt["arguments"]) == 2
    arg_map = {a["name"]: a for a in prompt["arguments"]}
    assert arg_map["arg1"]["type"] == "str"
    assert arg_map["arg2"]["default"] == 42
    assert prompt["tags"] == ["/api/v1/prompts/test"]


def test_create_prompt_definitions_for_route():
    """Test the prompt definition helper function."""

    def my_endpoint(param1: str, param2: bool = False):
        """Example endpoint."""

    route = APIRoute(
        "/prompts/complex",
        my_endpoint,
        methods=["POST"],
        openapi_extra={
            "mcp_config": {
                "prompts": [
                    {
                        "name": "complex_prompt",
                        "content": "Test with {param1}, {param2}, and {custom}",
                        "arguments": [
                            {"name": "custom", "type": "float", "default": 1.0}
                        ],
                        "tags": ["existing_tag"],
                    }
                ]
            }
        },
    )
    with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value="/"):
        defs = _create_prompt_definitions_for_route(route)
    assert len(defs) == 1
    prompt_def = defs[0]
    args = {a["name"]: a for a in prompt_def["arguments"]}
    assert args["param1"]["type"] == "str"
    assert args["param2"]["default"] is False
    assert args["custom"]["default"] == 1.0
    assert prompt_def["tags"] == ["/prompts/complex", "existing_tag"]


def test_create_prompt_definitions_auto_naming():
    """Test auto-naming of prompts when a name is not provided."""

    def my_endpoint():
        pass

    route = APIRoute(
        "/category/subcategory/tool",
        my_endpoint,
        methods=["GET"],
        openapi_extra={
            "mcp_config": {
                "prompts": [
                    {"content": "Prompt 1"},
                    {"content": "Prompt 2"},
                ]
            }
        },
    )
    with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value="/"):
        defs = _create_prompt_definitions_for_route(route)
    assert len(defs) == 2
    assert defs[0]["name"] == "category_subcategory_tool_prompt_0"
    assert defs[1]["name"] == "category_subcategory_tool_prompt_1"
