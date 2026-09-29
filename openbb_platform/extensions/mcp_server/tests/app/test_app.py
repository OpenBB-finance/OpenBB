"""Tests for the core of ``openbb_mcp_server.app.app``."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp.server.providers.openapi import OpenAPIResource, OpenAPITool
from fastmcp.utilities.openapi import HTTPRoute, ResponseInfo

from openbb_mcp_server.app.app import (
    SSEShutdownWrapper,
    _build_runtime_middleware,
    _extract_brief_description,
    _get_mcp_config_from_route,
    _read_system_prompt_file,
    _trim_model_descriptions,
    create_mcp_server,
    stdio_main,
)
from openbb_mcp_server.app.discovery import OpenBBToolCatalog
from openbb_mcp_server.models.settings import MCPSettings


@pytest.fixture(autouse=True)
def _patch_transforms():
    with (
        patch("openbb_mcp_server.app.app.PromptsAsTools", new=MagicMock()),
        patch("openbb_mcp_server.app.app.ResourcesAsTools", new=MagicMock()),
    ):
        yield


def _customizer(settings, path, mcp_config=None, prompt_definitions=()):
    api = FastAPI()
    api.add_api_route(
        path,
        lambda: None,
        methods=["GET"],
        openapi_extra={"mcp_config": mcp_config or {}},
    )
    route = next(r for r in api.routes if isinstance(r, APIRoute))
    processed = MagicMock(
        route_lookup={(path, "GET"): route},
        route_maps=[],
        prompt_definitions=list(prompt_definitions),
    )
    index = MagicMock()
    index.all_tool_names.return_value = set()
    with (
        patch(
            "openbb_mcp_server.app.app.process_fastapi_routes_for_mcp",
            return_value=processed,
        ),
        patch("openbb_mcp_server.app.app.CategoryIndex", return_value=index),
        patch("openbb_mcp_server.app.app.FastMCP.from_fastapi") as from_fastapi,
    ):
        create_mcp_server(settings, api)
    return from_fastapi.call_args.kwargs["mcp_component_fn"]


def _tool(path, description="d"):
    route = HTTPRoute(path=path, method="GET")
    tool = OpenAPITool(
        MagicMock(),
        route,
        name="o",
        description=description,
        parameters={},
        director=MagicMock(),
    )
    return route, tool


class TestExtractBriefDescription:
    """Trimming of route descriptions to their brief form."""

    def test_extract_brief_description(self):
        """Test _extract_brief_description function."""
        assert _extract_brief_description("Brief.\n\n**Query Parameters:**") == "Brief."
        assert _extract_brief_description("Brief.") == "Brief."
        assert _extract_brief_description("") == "No description available"

    def test_extract_brief_description_strips_responses_section(self):
        """``**Responses:`` section is also a split delimiter."""
        full = "Lead.\n\n**Responses:** payload"
        assert _extract_brief_description(full) == "Lead."

    def test_extract_brief_description_returns_default_for_blank_after_split(self):
        """If the brief is empty post-split, the default sentinel is returned."""
        assert _extract_brief_description("\n\n**Query Parameters:** stuff") == (
            "No description available"
        )


class TestGetMcpConfigFromRoute:
    """Reading ``mcp_config`` from a route's ``openapi_extra``."""

    def test_get_mcp_config_from_route(self):
        """Test _get_mcp_config_from_route function."""
        route = APIRoute(
            "/test", lambda: None, openapi_extra={"mcp_config": {"expose": True}}
        )
        assert _get_mcp_config_from_route(route) == {"expose": True}
        assert _get_mcp_config_from_route(None) == {}

    def test_get_mcp_config_handles_non_dict_value(self):
        """If ``mcp_config`` is set but not a dict, ``{}`` is returned."""
        route = APIRoute("/x", lambda: None, openapi_extra={"mcp_config": "bad"})
        assert _get_mcp_config_from_route(route) == {}

    def test_get_mcp_config_falls_back_to_x_mcp_alias(self):
        """Legacy ``x-mcp`` alias is honored."""
        route = APIRoute(
            "/x", lambda: None, openapi_extra={"x-mcp": {"name": "renamed"}}
        )
        assert _get_mcp_config_from_route(route) == {"name": "renamed"}

    def test_get_mcp_config_no_openapi_extra(self):
        """Route without ``openapi_extra`` → empty dict."""
        route = APIRoute("/x", lambda: None)
        route.openapi_extra = None
        assert _get_mcp_config_from_route(route) == {}


class TestTrimModelDescriptions:
    """Cutting model docstrings in tool schemas to their summary."""

    def test_trims_nested_model_descriptions_only(self):
        """Titled object schemas keep their first paragraph; everything else is untouched."""
        schema = {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Input rows.\n\nOne per bar.",
                    "items": {
                        "type": "object",
                        "title": "Data",
                        "description": "The model.\n\nLong explanation.",
                    },
                },
                "extra": {
                    "type": "object",
                    "description": "Untitled.\n\nKept whole.",
                },
                "plain": {"type": "object", "title": "Plain"},
                "choices": {"anyOf": [{"type": "string"}, 5]},
            },
        }
        trimmed = _trim_model_descriptions(schema)
        properties = trimmed["properties"]
        assert properties["data"]["items"]["description"] == "The model."
        assert properties["data"]["description"] == "Input rows.\n\nOne per bar."
        assert properties["extra"]["description"] == "Untitled.\n\nKept whole."
        assert properties["plain"] == {"type": "object", "title": "Plain"}
        assert properties["choices"] == {"anyOf": [{"type": "string"}, 5]}
        assert schema["properties"]["data"]["items"]["description"] == (
            "The model.\n\nLong explanation."
        )


class TestReadSystemPromptFile:
    """Reading the system prompt file."""

    def test_read_system_prompt_file(self, tmp_path):
        """Test _read_system_prompt_file function."""
        prompt_file = tmp_path / "prompt.txt"
        prompt_file.write_text("Test prompt")
        assert _read_system_prompt_file(str(prompt_file)) == "Test prompt"
        assert _read_system_prompt_file("nonexistent.txt") is None

    def test_read_system_prompt_file_swallows_read_errors(self, tmp_path, app_caplog):
        """Read errors (permission denied etc.) are caught and logged."""
        f = tmp_path / "prompt.txt"
        f.write_text("hello")

        with patch.object(
            Path, "read_text", side_effect=OSError("simulated read failure")
        ):
            out = _read_system_prompt_file(str(f))
        assert out is None
        assert "simulated read failure" in app_caplog.text

    def test_read_system_prompt_file_returns_none_for_directory(self, tmp_path):
        """A directory path returns None (``is_file()`` False)."""
        out = _read_system_prompt_file(str(tmp_path))
        assert out is None


class TestBuildRuntimeMiddleware:
    """CORS middleware built from the system settings."""

    def test_build_runtime_middleware_uses_system_service_cors(self):
        """CORS allow-list is read from SystemService and wrapped in Middleware."""
        fake_cors = MagicMock(
            allow_origins=["https://example.com"],
            allow_methods=["GET"],
            allow_headers=["X"],
        )
        fake_settings = MagicMock()
        fake_settings.api_settings.cors = fake_cors
        fake_system = MagicMock(system_settings=fake_settings)

        with patch(
            "openbb_mcp_server.app.app.SystemService",
            return_value=fake_system,
        ):
            out = _build_runtime_middleware()

        assert len(out) == 1
        mw = out[0]
        assert mw.kwargs["allow_origins"] == ["https://example.com"]


class TestCustomizeComponents:
    """Per-route naming, tagging, and enablement of MCP components."""

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_create_mcp_server_customization(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
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
    def test_customize_components_three_segment_path(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """A three-segment path produces ``category_subcategory_tool`` naming."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price/historical")
        def deep_route():
            """Test route."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {
            ("/api/v1/equity/price/historical", "GET"): route
        }
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/equity/price/historical", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="orig",
            description="d",
            parameters={},
            director=MagicMock(),
        )
        customize(http_route, tool)
        assert tool.name == "equity_price_historical"

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_two_segment_path(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """A two-segment local path uses ``general`` as the subcategory."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price")
        def two_seg():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity/price", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/equity/price", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="o",
            description="d",
            parameters={},
            director=MagicMock(),
        )
        customize(http_route, tool)
        assert tool.name == "equity_price"

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_no_segments_falls_back_to_general(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """A path with no segments after stripping → general/general/root."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1")
        def root_route():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="o",
            description="d",
            parameters={},
            director=MagicMock(),
        )
        customize(http_route, tool)
        assert tool.name == "general_root"

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_invalid_mcp_config_logged(
        self, mock_from_fastapi, mock_category_index, mock_process_routes, app_caplog
    ):
        """Invalid mcp_config dicts are skipped with an error log."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/test")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {"mcp_config": {"unknown_key": "value"}}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/test", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/test", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="orig",
            description="d",
            parameters={},
            director=MagicMock(),
        )

        with patch(
            "openbb_mcp_server.app.app.is_valid_mcp_config",
            return_value=ValueError("bad config"),
        ):
            customize(http_route, tool)
        assert tool.name == "test_test"
        assert (
            "Invalid MCP config found in route, 'GET /api/v1/test'" in app_caplog.text
        )

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_resource_mime_type(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """OpenAPIResource components honor an mcp_config-supplied mime_type."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {"mcp_config": {"mime_type": "application/csv"}}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/equity", method="GET")
        resource = MagicMock(spec=OpenAPIResource)
        resource.tags = set()
        resource.description = "x"
        customize(http_route, resource)
        assert resource.mime_type == "application/csv"

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_enable_override_in_mcp_config(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """mcp_config.enable=True / False overrides the category-default match."""
        settings = MCPSettings(default_tool_categories=["nonexistent"])
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {"mcp_config": {"enable": True}}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity/price", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = {"equity_price"}
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/equity/price", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="o",
            description="d",
            parameters={},
            director=MagicMock(),
        )
        customize(http_route, tool)
        idx.register.assert_called_once()

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_disable_override_explicit_false(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """``mcp_config.enable=False`` skips a category-default match."""
        settings = MCPSettings(default_tool_categories=["all"])
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {"mcp_config": {"enable": False, "tags": ["custom"]}}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity/price", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/equity/price", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="o",
            description="d.\n\n**Query Parameters:** ignore",
            parameters={"x": "y"},
            director=MagicMock(),
        )
        customize(http_route, tool)
        assert "custom" in tool.tags

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_attaches_prompt_metadata(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Prompt metadata for a tool is appended to the description."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {"mcp_config": {"name": "equity_tool"}}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = [
            {
                "tool": "equity_tool",
                "name": "explain_it",
                "description": "Explain.",
                "arguments": [{"name": "tone"}],
            }
        ]
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(path="/api/v1/equity", method="GET")
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="orig",
            description="Base desc.",
            parameters={},
            director=MagicMock(),
        )
        customize(http_route, tool)
        assert "Associated Prompts" in (tool.description or "")
        assert "explain_it" in (tool.description or "")

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_compresses_output_schema(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Tools with an ``output_schema`` get it compressed via ``compress_schema``."""
        settings = MCPSettings()
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity/price", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        create_mcp_server(settings, fastapi_app)
        customize = mock_from_fastapi.call_args.kwargs["mcp_component_fn"]

        http_route = HTTPRoute(
            path="/api/v1/equity/price",
            method="GET",
            responses={
                "422": ResponseInfo(content_schema={"application/json": {}}),
                "200": ResponseInfo(content_schema={"application/json": {}}),
            },
        )
        tool = OpenAPITool(
            MagicMock(),
            http_route,
            name="o",
            description="d",
            parameters={
                "type": "object",
                "properties": {"foo": {"type": "string"}},
                "$defs": {"Unused": {"type": "string"}},
            },
            director=MagicMock(),
        )
        tool.output_schema = {
            "type": "object",
            "properties": {"bar": {"type": "string"}},
            "$defs": {"Unused": {"type": "integer"}},
        }
        customize(http_route, tool)
        assert tool.parameters == {
            "type": "object",
            "properties": {"foo": {"type": "string"}},
        }
        assert tool.output_schema == {
            "type": "object",
            "properties": {"bar": {"type": "string"}},
        }

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_customize_components_should_enable_false_fallback(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """No enable override AND no matching tag → should_enable=False."""
        settings = MCPSettings(default_tool_categories=["nonexistent"])
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity/price", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = {"equity_price"}
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()

        def _from_fastapi(**kwargs):
            http_route = HTTPRoute(path="/api/v1/equity/price", method="GET")
            tool = OpenAPITool(
                MagicMock(),
                http_route,
                name="o",
                description="d",
                parameters={},
                director=MagicMock(),
            )
            kwargs["mcp_component_fn"](http_route, tool)
            return mock_mcp

        mock_from_fastapi.side_effect = _from_fastapi

        create_mcp_server(settings, fastapi_app)
        mock_mcp.disable.assert_called_once_with(names={"equity_price"})
        mock_mcp.enable.assert_not_called()

    def test_customize_components_lists_every_prompt_of_a_tool(self):
        """Each prompt of a tool is listed, with arguments only when it has some."""
        customize = _customizer(
            MCPSettings(),
            "/api/v1/equity",
            {"name": "equity_tool"},
            [
                {
                    "tool": "equity_tool",
                    "name": "a",
                    "description": "A.",
                    "arguments": [{"name": "x"}],
                },
                {
                    "tool": "equity_tool",
                    "name": "b",
                    "description": "B.",
                    "arguments": [],
                },
                {"tool": "", "name": "orphan", "description": "O.", "arguments": []},
            ],
        )
        route, tool = _tool("/api/v1/equity", "Base.")
        customize(route, tool)
        assert tool.description == (
            "Base.\n\n**Associated Prompts:**"
            "\n- **a**: A.\n  - Arguments: `x`"
            "\n- **b**: B."
        )

    def test_customize_components_describe_responses_keeps_full_description(self):
        """``describe_responses`` keeps the full route description."""
        customize = _customizer(MCPSettings(describe_responses=True), "/api/v1/equity")
        route, tool = _tool("/api/v1/equity", "Lead.\n\n**Responses:** payload")
        customize(route, tool)
        assert tool.description == "Lead.\n\n**Responses:** payload"

    def test_customize_components_resource_without_mime_type(self):
        """A resource without a configured ``mime_type`` keeps its own."""
        customize = _customizer(MCPSettings(), "/api/v1/equity")
        resource = MagicMock(spec=OpenAPIResource)
        resource.tags = set()
        resource.description = "x"
        resource.mime_type = "text/plain"
        customize(HTTPRoute(path="/api/v1/equity", method="GET"), resource)
        assert resource.mime_type == "text/plain"


class TestToolsetModes:
    """Fixed-toolset enablement versus discovery mode."""

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_create_mcp_server_catalogs_tools_when_discovery_enabled(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Discovery mode keeps tools enabled and folds them into the tool catalog."""
        settings = MCPSettings(enable_tool_discovery=True)
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

        mock_mcp_instance.disable.assert_not_called()
        mock_mcp_instance.enable.assert_not_called()
        assert any(
            isinstance(call.args[0], OpenBBToolCatalog)
            for call in mock_mcp_instance.add_transform.call_args_list
        )

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_create_mcp_server_fixed_toolset_mode(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """When discovery disabled, disable all first then re-enable flagged tools."""
        settings = MCPSettings(
            enable_tool_discovery=False,
            default_tool_categories=["equity"],
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

        mock_mcp_instance.disable.assert_called_once_with(
            names={"eq_tool", "crypto_tool"}
        )
        mock_mcp_instance.enable.assert_not_called()

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_create_mcp_server_fixed_toolset_calls_enable(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Fixed-toolset mode with matches calls ``mcp.enable`` on the toolset."""
        settings = MCPSettings(default_tool_categories=["equity"])
        fastapi_app = FastAPI()

        @fastapi_app.get("/api/v1/equity/price")
        def t():
            """Test."""

        route = next(r for r in fastapi_app.routes if isinstance(r, APIRoute))
        route.openapi_extra = {}

        mock_processed = MagicMock()
        mock_processed.route_lookup = {("/api/v1/equity/price", "GET"): route}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = {"equity_price"}
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()

        def _from_fastapi(**kwargs):
            customize = kwargs["mcp_component_fn"]
            http_route = HTTPRoute(path="/api/v1/equity/price", method="GET")
            tool = OpenAPITool(
                MagicMock(),
                http_route,
                name="o",
                description="d",
                parameters={},
                director=MagicMock(),
            )
            tool.tags.add("equity")
            customize(http_route, tool)
            return mock_mcp

        mock_from_fastapi.side_effect = _from_fastapi

        create_mcp_server(settings, fastapi_app)
        mock_mcp.enable.assert_called_once()


class TestCreateMcpServer:
    """Optional features wired by ``create_mcp_server``."""

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_create_mcp_server_registers_cli_tools_when_enabled(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """``settings.enable_cli_tools`` triggers cli_tools.register_cli_tools."""
        settings = MCPSettings(enable_cli_tools=True)
        settings.default_skills_dir = None
        fastapi_app = FastAPI()

        mock_processed = MagicMock()
        mock_processed.route_lookup = {}
        mock_processed.route_maps = []
        mock_processed.prompt_definitions = []
        mock_process_routes.return_value = mock_processed

        idx = MagicMock()
        idx.all_tool_names.return_value = set()
        mock_category_index.return_value = idx

        mock_mcp = MagicMock()
        mock_from_fastapi.return_value = mock_mcp

        with patch("openbb_mcp_server.app.app.register_cli_tools") as mock_register:
            create_mcp_server(settings, fastapi_app)
        mock_register.assert_called_once_with(mock_mcp)


class TestSSEShutdownWrapper:
    """Graceful SSE shutdown handling."""

    def test_sse_shutdown_wrapper_passes_through_non_http_scopes(self):
        """Non-HTTP scopes flow straight to the inner ASGI app."""
        inner = MagicMock()

        async def _inner(*args, **kwargs):
            inner(*args, **kwargs)

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(wrapped({"type": "lifespan"}, MagicMock(), MagicMock()))
        inner.assert_called()

    def test_sse_shutdown_wrapper_passes_through_non_sse_paths(self):
        """HTTP requests on non-SSE paths pass through verbatim."""
        inner_mock = MagicMock()

        async def _inner(scope, receive, send):
            inner_mock(scope)

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(
            wrapped(
                {"type": "http", "path": "/mcp"},
                MagicMock(),
                MagicMock(),
            )
        )
        inner_mock.assert_called_once()

    def test_sse_shutdown_wrapper_handles_sse_path_normal_send(self):
        """SSE path with a normal http.response.start + body sends through."""
        sent_messages = []

        async def _send(message):
            sent_messages.append(message)

        async def _inner(scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"event: ping\n"})

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(
            wrapped(
                {"type": "http", "path": "/sse/"},
                MagicMock(),
                _send,
            )
        )
        assert sent_messages[0]["type"] == "http.response.start"
        assert sent_messages[1]["type"] == "http.response.body"

    def test_sse_shutdown_wrapper_swallows_connection_reset(self):
        """ConnectionResetError mid-stream is swallowed (client disconnect)."""
        raised = {"count": 0}

        async def _send(message):
            raised["count"] += 1
            raise ConnectionResetError()

        async def _inner(scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(
            wrapped(
                {"type": "http", "path": "/sse/"},
                MagicMock(),
                _send,
            )
        )
        assert raised["count"] == 1

    def test_sse_shutdown_wrapper_handles_runtime_error_with_response_started(self):
        """Mid-stream RuntimeError after ``response.start`` is swallowed."""
        sent: list = []

        async def _send(message):
            if message["type"] == "http.response.body":
                raise RuntimeError("Expected ASGI message x but got y")
            sent.append(message)

        async def _inner(scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"x"})

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(
            wrapped(
                {"type": "http", "path": "/sse/"},
                MagicMock(),
                _send,
            )
        )
        assert sent[0]["type"] == "http.response.start"

    def test_sse_shutdown_wrapper_synthesizes_response_when_runtime_error_pre_start(
        self,
    ):
        """Body-before-start RuntimeError fires the synthesize-200 fallback."""
        sent: list = []
        underlying_error_count = {"n": 0}

        async def _send(message):
            if (
                message["type"] == "http.response.body"
                and underlying_error_count["n"] == 0
            ):
                underlying_error_count["n"] += 1
                raise RuntimeError("Expected ASGI message 'http.response.start'")
            sent.append(message)

        async def _inner(scope, receive, send):
            await send({"type": "http.response.body", "body": b"oops"})

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(wrapped({"type": "http", "path": "/sse/"}, MagicMock(), _send))
        assert any(
            m["type"] == "http.response.body"
            and b"Connection closed" in m.get("body", b"")
            for m in sent
        )

    def test_sse_shutdown_wrapper_re_raises_unrelated_runtime_error(self):
        """Other RuntimeErrors propagate."""

        async def _send(message):
            raise RuntimeError("totally unrelated")

        async def _inner(scope, receive, send):
            await send({"type": "http.response.start", "status": 200, "headers": []})

        wrapped = SSEShutdownWrapper(_inner)
        with pytest.raises(RuntimeError, match="totally unrelated"):
            asyncio.run(
                wrapped(
                    {"type": "http", "path": "/sse/"},
                    MagicMock(),
                    _send,
                )
            )

    def test_sse_shutdown_wrapper_drops_non_response_messages(self):
        """Messages other than ``http.response.start``/``body`` are not forwarded on SSE paths."""

        sent: list = []

        async def _send(message):
            sent.append(message)

        async def _inner(scope, receive, send):
            await send({"type": "http.disconnect"})

        wrapped = SSEShutdownWrapper(_inner)
        asyncio.run(wrapped({"type": "http", "path": "/sse/"}, MagicMock(), _send))
        assert sent == []


class TestStdioMain:
    """The STDIO transport runner."""

    @pytest.mark.asyncio
    async def test_stdio_main_runs_when_signal_handlers_are_unsupported(self):
        """Windows event loops can serve stdio without registering signal handlers."""
        loop = asyncio.get_running_loop()
        mcp_server = MagicMock()

        with patch.object(loop, "add_signal_handler", side_effect=NotImplementedError):
            await stdio_main(mcp_server)

        mcp_server.run.assert_called_once_with("stdio")

    @pytest.mark.asyncio
    async def test_stdio_main_invokes_run(self, monkeypatch):
        """``stdio_main`` ultimately calls ``mcp.run('stdio')`` via executor."""
        from openbb_mcp_server.app import app as app_module

        server = MagicMock(name="MCPServer")
        server.run = MagicMock(return_value=None)

        fake_loop = MagicMock()
        fake_loop.add_signal_handler = MagicMock()

        async def _fake_run_in_executor(_executor, fn, *args):
            fn(*args)

        fake_loop.run_in_executor = _fake_run_in_executor
        monkeypatch.setattr(app_module.asyncio, "get_running_loop", lambda: fake_loop)

        await app_module.stdio_main(server)
        server.run.assert_called_with("stdio")

    @pytest.mark.asyncio
    async def test_stdio_main_signal_handler_calls_os_exit(self, monkeypatch):
        """The installed signal handler ultimately calls ``os._exit(0)``."""
        from openbb_mcp_server.app import app as app_module

        captured: dict = {}

        fake_loop = MagicMock()

        def _add_signal_handler(_sig, handler):
            captured["handler"] = handler

        fake_loop.add_signal_handler = _add_signal_handler

        async def _run_in_executor(_executor, fn, *args):
            return fn(*args)

        fake_loop.run_in_executor = _run_in_executor
        monkeypatch.setattr(app_module.asyncio, "get_running_loop", lambda: fake_loop)

        server = MagicMock()
        server.run = MagicMock(return_value=None)

        await stdio_main(server)
        with patch.object(app_module.os, "_exit") as mock_exit:
            captured["handler"]()
        mock_exit.assert_called_once_with(0)


class TestBackCompatMain:
    """The legacy ``app.app:main`` entry point."""

    def test_back_compat_main_alias_in_app_app(self):
        """Legacy ``openbb_mcp_server.app.app:main`` forwards to the new entry."""
        from openbb_mcp_server.app import app as app_mod

        with (
            patch.object(sys, "argv", ["openbb-mcp"]),
            patch("openbb_mcp_server.main.main") as mock_main,
        ):
            app_mod.main()
        mock_main.assert_called_once()
