"""Tests for ``openbb_mcp_server.utils.fastapi``."""

import inspect
import sys
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Query
from fastapi.routing import APIRoute, APIRouter
from fastmcp.server.providers.openapi import MCPType, RouteMap

from openbb_mcp_server.models.mcp_config import MCPConfigModel
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.utils.fastapi import (
    _create_prompt_definitions_for_route,
    _endpoint_argument,
    _get_module_exclusion_targets,
    _methods_from_config_or_route,
    _normalize_methods,
    _resolve_mcp_type,
    _should_exclude_by_module_and_path,
    get_api_prefix,
    get_mcp_config,
    process_fastapi_routes_for_mcp,
    route_naming,
    strip_api_prefix,
    tool_name_for_route,
)


@pytest.fixture
def mock_system_service():
    """Fixture to mock SystemService."""
    with patch("openbb_mcp_server.utils.fastapi.SystemService") as mock_service_class:
        mock_instance = mock_service_class.return_value
        mock_instance.system_settings.api_settings.prefix = "/api"
        yield mock_instance


@pytest.fixture
def sample_app():
    """Create a sample FastAPI app for testing route processing."""
    app = FastAPI()

    def endpoint_a():
        """Handle example endpoint request."""

    def endpoint_b():
        """Handle example endpoint request."""

    def endpoint_c():
        """Handle example endpoint request."""

    def endpoint_d(arg1: str, arg2: int = 42):
        """Handle example endpoint request."""

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


class TestGetApiPrefix:
    """Normalizing the API prefix."""

    def test_get_api_prefix(self, mock_system_service):
        """Test API prefix retrieval logic."""
        assert get_api_prefix(None) == "/api"
        settings = MCPSettings(api_prefix="/custom")
        assert get_api_prefix(settings) == "/custom"
        settings_empty = MCPSettings(api_prefix=" ")
        assert get_api_prefix(settings_empty) == "/api"

    def test_get_api_prefix_strips_trailing_slash(self, mock_system_service):
        """A multi-trailing-slash prefix is normalized to no trailing slash."""
        settings = MCPSettings(api_prefix="/api/")
        assert get_api_prefix(settings) == "/api"


class TestStripApiPrefix:
    """Stripping the API prefix from route paths."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("/api/v1/test", "test"),
            ("/test", "test"),
            ("/api/v1/test/path", "test/path"),
            ("", ""),
            ("api/v1/foo", "foo"),
            ("/other/route", "other/route"),
        ],
    )
    def test_strip_api_prefix(self, path, expected):
        """The prefix and leading slash are removed; other paths only lose the slash."""
        assert strip_api_prefix(path, "/api/v1") == expected


class TestRouteNaming:
    """Categories and tool names built from route paths."""

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("/api/v1", ("general", "general", "general_root")),
            ("/api/v1/{symbol}", ("general", "general", "general_root")),
            ("/api/v1/hello", ("hello", "general", "hello_hello")),
            ("/api/v1/equity/price", ("equity", "general", "equity_price")),
            (
                "/api/v1/equity/price/historical/{symbol}/daily",
                ("equity", "price", "equity_price_historical_daily"),
            ),
        ],
    )
    def test_route_naming(self, path, expected):
        """Placeholders are skipped; the first segment is the category."""
        assert route_naming(path, "/api/v1") == expected


class TestToolNameForRoute:
    """Tool names of the methods of one path."""

    @pytest.mark.parametrize(
        ("method", "exposed", "override", "expected"),
        [
            ("GET", {"GET", "POST"}, None, "demo_multi"),
            ("POST", {"GET", "POST"}, None, "demo_multi_post"),
            ("POST", {"POST"}, None, "demo_multi"),
            ("POST", {"GET", "POST"}, "custom", "custom"),
        ],
    )
    def test_tool_name_for_route(self, method, exposed, override, expected):
        """Non-GET methods sharing a path get a suffix; a configured name wins."""
        path = "/api/v1/demo/multi"
        name = tool_name_for_route(path, method, "/api/v1", {path: exposed}, override)
        assert name == expected


class TestEndpointArgument:
    """Prompt arguments built from endpoint parameters."""

    @staticmethod
    def _endpoint(
        untyped,
        required: str,
        *,
        plain: int = 3,
        optional: str | None = None,
        optional_float: Optional[float] = None,  # noqa: UP045
        either: int | str = 1,
        rows: list[int] | None = None,
        query_default: str = Query("AAPL"),
        query_required: str = Query(...),
        query_unset: str = Query(),
    ):
        """Take one parameter of each kind."""

    def test_defaults_only_when_the_parameter_has_one(self):
        """Required parameters carry no default; ``Query`` defaults are unwrapped."""
        parameters = inspect.signature(self._endpoint).parameters.values()
        arguments = [_endpoint_argument(p) for p in parameters]
        assert arguments == [
            {"name": "untyped", "type": "str"},
            {"name": "required", "type": "str"},
            {"name": "plain", "type": "int", "default": 3},
            {"name": "optional", "type": "str", "default": None},
            {"name": "optional_float", "type": "float", "default": None},
            {"name": "either", "type": "str", "default": 1},
            {"name": "rows", "type": "str", "default": None},
            {"name": "query_default", "type": "str", "default": "AAPL"},
            {"name": "query_required", "type": "str"},
            {"name": "query_unset", "type": "str"},
        ]


class TestGetModuleExclusionTargets:
    """The module exclusion map."""

    @pytest.mark.parametrize(
        ("exclusion_map", "expected"),
        [
            (None, {"coverage": "openbb_core"}),
            ({}, {}),
            ({"custom": "my_module"}, {"custom": "my_module"}),
        ],
    )
    def test_get_module_exclusion_targets(self, exclusion_map, expected):
        """None means the default map; any mapping, even an empty one, is used as given."""
        settings = MCPSettings(module_exclusion_map=exclusion_map)
        assert _get_module_exclusion_targets(settings) == expected

    def test_get_module_exclusion_targets_without_settings(self):
        """Without settings the default map applies."""
        assert _get_module_exclusion_targets(None) == {"coverage": "openbb_core"}


class TestGetMcpConfig:
    """Reading per-route MCP configuration."""

    def test_get_mcp_config(self):
        """Test retrieval and validation of MCP config from a route."""
        valid_route = APIRoute(
            "/", lambda: None, openapi_extra={"mcp_config": {"mcp_type": "tool"}}
        )
        config = get_mcp_config(valid_route)
        assert config.mcp_type and config.mcp_type.value == "tool"

        x_mcp_route = APIRoute(
            "/", lambda: None, openapi_extra={"x-mcp": {"mcp_type": "resource"}}
        )
        config = get_mcp_config(x_mcp_route)
        assert config.mcp_type and config.mcp_type.value == "resource"

        invalid_route = APIRoute(
            "/", lambda: None, openapi_extra={"mcp_config": "invalid"}
        )
        assert get_mcp_config(invalid_route).mcp_type is None

    def test_get_mcp_config_strict_rejects_non_dict(self):
        """``strict=True`` with a non-dict ``mcp_config`` raises TypeError."""
        route = APIRoute("/x", lambda: None, openapi_extra={"mcp_config": "nope"})
        with pytest.raises(TypeError, match="must be a dictionary"):
            get_mcp_config(route, strict=True)

    def test_get_mcp_config_strict_propagates_validation_error(self):
        """``strict=True`` surfaces the underlying validation exception."""
        route = APIRoute(
            "/x", lambda: None, openapi_extra={"mcp_config": {"methods": ["BOGUS"]}}
        )
        with pytest.raises(Exception, match="Invalid HTTP method"):
            get_mcp_config(route, strict=True)

    def test_get_mcp_config_non_strict_swallows_validation_error(self):
        """``strict=False`` (default) on invalid config returns a default model."""
        route = APIRoute(
            "/x", lambda: None, openapi_extra={"mcp_config": {"methods": ["BOGUS"]}}
        )
        config = get_mcp_config(route)
        assert config.methods is None


class TestShouldExcludeByModuleAndPath:
    """Excluding routes of optional modules."""

    def test_should_exclude_by_module_and_path(self, mock_system_service):
        """Routes under a mapped segment are hidden only while its module is imported."""
        assert _should_exclude_by_module_and_path("/api/coverage/commands", None)
        assert not _should_exclude_by_module_and_path("/api/some_other_path", None)
        with patch.dict(sys.modules, {"openbb_technical": MagicMock()}):
            assert not _should_exclude_by_module_and_path("/api/technical/rsi", None)

        settings = MCPSettings(module_exclusion_map={"custom": "my_module"})
        assert not _should_exclude_by_module_and_path("/api/custom/test", settings)
        with patch.dict(sys.modules, {"my_module": MagicMock()}):
            assert _should_exclude_by_module_and_path("/api/custom/test", settings)

    def test_empty_exclusion_map_hides_nothing(self, mock_system_service):
        """An explicitly empty map keeps even the default-excluded routes."""
        settings = MCPSettings(module_exclusion_map={})
        assert not _should_exclude_by_module_and_path(
            "/api/coverage/commands", settings
        )

    def test_should_exclude_normalizes_path_without_slash(self, mock_system_service):
        """A path without leading slash gets one prepended before module-prefix match."""
        assert _should_exclude_by_module_and_path("api/coverage/x", None)


class TestProcessFastapiRoutesForMcp:
    """Filtering routes and building route maps."""

    def test_process_routes_exclusion(self, sample_app, mock_system_service):
        """Excluded routes get EXCLUDE route maps and stay on the app untouched."""
        routes_before = list(sample_app.router.routes)
        processed = process_fastapi_routes_for_mcp(sample_app, None)
        assert [r.path for r in processed.excluded_routes] == ["/api/v1/crypto/price"]
        assert processed.route_maps[0] == RouteMap(
            pattern="^/api/v1/crypto/price$", methods=["POST"], mcp_type=MCPType.EXCLUDE
        )
        assert ("/api/v1/crypto/price", "POST") not in processed.route_lookup
        assert sample_app.router.routes == routes_before

        with patch.dict(sys.modules, {"openbb_fake": MagicMock()}):
            settings = MCPSettings(
                api_prefix="/api/v1",
                module_exclusion_map={"fake": "openbb_fake"},
            )
            processed = process_fastapi_routes_for_mcp(sample_app, settings)
        assert {r.path for r in processed.excluded_routes} == {
            "/api/v1/crypto/price",
            "/api/v1/fake/test",
        }

    def test_process_routes_included_routers_use_effective_paths(
        self, mock_system_service
    ):
        """Routes of (nested) included routers are processed at their served paths."""
        inner = APIRouter(prefix="/price")

        @inner.get(
            "/quote",
            openapi_extra={
                "mcp_config": {"prompts": [{"name": "p", "content": "Quote {symbol}"}]}
            },
        )
        def quote(symbol: str):
            """Quote."""

        @inner.get("/hidden", openapi_extra={"mcp_config": {"expose": False}})
        def hidden():
            """Hidden."""

        outer = APIRouter(prefix="/equity")
        outer.include_router(inner)
        app = FastAPI()
        app.include_router(outer, prefix="/api/v1")

        processed = process_fastapi_routes_for_mcp(
            app, MCPSettings(api_prefix="/api/v1")
        )

        assert list(processed.route_lookup) == [("/api/v1/equity/price/quote", "GET")]
        assert [m.pattern for m in processed.route_maps] == [
            "^/api/v1/equity/price/hidden$",
            ".*",
        ]
        prompt = processed.prompt_definitions[0]
        assert (prompt["tool"], prompt["tags"]) == (
            "equity_price_quote",
            ["/api/v1/equity/price/quote"],
        )

    def test_process_routes_route_maps(self, sample_app, mock_system_service):
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
        assert [m.mcp_type for m in processed.route_maps] == [
            MCPType.EXCLUDE,
            MCPType.RESOURCE,
            MCPType.TOOL,
        ]

        settings = MCPSettings(default_catchall_mcp_type="resource")
        processed = process_fastapi_routes_for_mcp(sample_app, settings)
        assert processed.route_maps[-1].mcp_type == MCPType.RESOURCE

    def test_process_routes_prompts(self, sample_app, mock_system_service):
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

    def test_process_routes_wildcard_methods_in_config(self, mock_system_service):
        """A route whose mcp_config sets ``methods=*`` registers ``["*"]``."""
        app = FastAPI()
        app.add_api_route(
            "/api/x",
            lambda: None,
            methods=["GET"],
            openapi_extra={"mcp_config": {"mcp_type": "tool", "methods": "*"}},
        )
        processed = process_fastapi_routes_for_mcp(app, None)
        explicit = [m for m in processed.route_maps if m.pattern != ".*"]
        assert len(explicit) == 1
        assert explicit[0].methods == ["*"]

    def test_process_routes_route_map_without_methods(self, mock_system_service):
        """A route with only HEAD/OPTIONS still gets an explicit RouteMap registered."""
        app = FastAPI()
        app.add_api_route(
            "/api/onlyhead",
            lambda: None,
            methods=["HEAD"],
            openapi_extra={"mcp_config": {"mcp_type": "tool"}},
        )
        processed = process_fastapi_routes_for_mcp(app, None)
        patterns = [m.pattern for m in processed.route_maps]
        assert "^/api/onlyhead$" in patterns
        assert ".*" in patterns

    def test_process_routes_unconfigured_methods_are_excluded(
        self, mock_system_service
    ):
        """Methods left out of ``methods`` get EXCLUDE route maps and no lookup entry."""
        app = FastAPI()
        app.add_api_route(
            "/api/v1/x/y",
            lambda: None,
            methods=["GET", "POST"],
            openapi_extra={"mcp_config": {"methods": ["GET"]}},
        )
        app.add_api_route(
            "/api/v1/x/gone",
            lambda: None,
            methods=["GET"],
            openapi_extra={"mcp_config": {"methods": ["DELETE"]}},
        )
        processed = process_fastapi_routes_for_mcp(
            app, MCPSettings(api_prefix="/api/v1")
        )
        assert processed.route_maps[:2] == [
            RouteMap(
                pattern="^/api/v1/x/y$", methods=["POST"], mcp_type=MCPType.EXCLUDE
            ),
            RouteMap(
                pattern="^/api/v1/x/gone$", methods=["GET"], mcp_type=MCPType.EXCLUDE
            ),
        ]
        assert list(processed.route_lookup) == [("/api/v1/x/y", "GET")]
        assert processed.exposed_methods == {"/api/v1/x/y": {"GET"}}

    def test_process_routes_outside_allowed_categories(self, sample_app):
        """Routes whose category is not allowed are excluded; ``all`` allows every one."""
        allowed = MCPSettings(api_prefix="/api/v1", allowed_tool_categories=["stocks"])
        processed = process_fastapi_routes_for_mcp(sample_app, allowed)
        assert list(processed.route_lookup) == [("/api/v1/stocks/load", "GET")]
        everything = MCPSettings(api_prefix="/api/v1", allowed_tool_categories=["all"])
        processed = process_fastapi_routes_for_mcp(sample_app, everything)
        assert len(processed.route_lookup) == 3

    def test_process_routes_prompts_name_the_served_tool(self, mock_system_service):
        """A prompt names the GET tool of its path, else its first method's tool."""

        def endpoint():
            """Handle a request."""

        prompts = {"mcp_config": {"prompts": [{"name": "p", "content": "go"}]}}
        app = FastAPI()
        app.add_api_route(
            "/api/v1/x/rw", endpoint, methods=["GET", "POST"], openapi_extra=prompts
        )
        app.add_api_route(
            "/api/v1/x/w",
            endpoint,
            methods=["POST", "PUT"],
            openapi_extra={"mcp_config": {"prompts": [{"name": "q", "content": "go"}]}},
        )
        processed = process_fastapi_routes_for_mcp(
            app, MCPSettings(api_prefix="/api/v1")
        )
        assert [p["tool"] for p in processed.prompt_definitions] == [
            "x_rw",
            "x_w_post",
        ]


class TestCreatePromptDefinitionsForRoute:
    """Building prompt definitions from route configuration."""

    def test_create_prompt_definitions_for_route(self):
        """Test the prompt definition helper function."""

        def my_endpoint(param1: str, param2: bool = False):
            """Handle example endpoint request."""

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

    def test_create_prompt_definitions_does_not_repeat_route_tag(self):
        """A prompt already tagged with its route path is not tagged twice."""

        def my_endpoint():
            pass

        route = APIRoute(
            "/cat/sub/tool",
            my_endpoint,
            methods=["GET"],
            openapi_extra={
                "mcp_config": {
                    "prompts": [
                        {"name": "p", "content": "go", "tags": ["x", "/cat/sub/tool"]}
                    ]
                }
            },
        )
        with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value=""):
            defs = _create_prompt_definitions_for_route(route)
        assert defs[0]["tags"] == ["x", "/cat/sub/tool"]

    def test_create_prompt_definitions_auto_naming(self):
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

    def test_create_prompt_definitions_normalizes_path_without_slash(self):
        """A route path without a leading slash is normalized before splitting."""

        def fn(x: str):
            pass

        route = APIRoute(
            "/raw",
            fn,
            methods=["GET"],
            openapi_extra={
                "mcp_config": {"prompts": [{"name": "p", "content": "hi {x}"}]}
            },
        )
        route.path = "raw"
        with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value=""):
            defs = _create_prompt_definitions_for_route(route)
        assert defs[0]["name"] == "p"

    def test_create_prompt_definitions_single_segment_path(self):
        """A single-segment local path resolves to category=segment, tool=segment."""

        def fn():
            pass

        route = APIRoute(
            "/solo",
            fn,
            methods=["GET"],
            openapi_extra={"mcp_config": {"prompts": [{"content": "go"}]}},
        )
        with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value=""):
            defs = _create_prompt_definitions_for_route(route)
        assert defs[0]["name"] == "solo_solo_prompt"

    def test_create_prompt_definitions_no_segments_falls_back_to_general(self):
        """A path consisting only of placeholders resolves to ``general_root``."""

        def fn(x: str):
            pass

        route = APIRoute(
            "/{x}",
            fn,
            methods=["GET"],
            openapi_extra={"mcp_config": {"prompts": [{"content": "go"}]}},
        )
        with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value=""):
            defs = _create_prompt_definitions_for_route(route)
        assert defs[0]["name"] == "general_root_prompt"

    def test_create_prompt_definitions_unbound_var_gets_default_str(self):
        """A content variable not declared as an arg or endpoint param falls back to ``str``."""

        def fn():
            pass

        route = APIRoute(
            "/cat/sub/tool",
            fn,
            methods=["GET"],
            openapi_extra={
                "mcp_config": {"prompts": [{"name": "p", "content": "hello {orphan}"}]}
            },
        )
        with patch("openbb_mcp_server.utils.fastapi.get_api_prefix", return_value=""):
            defs = _create_prompt_definitions_for_route(route)
        args = {a["name"]: a for a in defs[0]["arguments"]}
        assert args["orphan"] == {"name": "orphan", "type": "str"}


class TestNormalizeMethods:
    """Normalizing HTTP methods."""

    def test_normalize_methods_empty_returns_empty_list(self):
        """``_normalize_methods`` returns ``[]`` for falsy input."""
        assert _normalize_methods(None) == []
        assert _normalize_methods([]) == []

    def test_normalize_methods_filters_falsy_and_head_options(self):
        """Falsy entries and HEAD/OPTIONS are dropped from the output."""
        assert _normalize_methods(["", None, "GET", "HEAD", "options"]) == ["GET"]


class TestMethodsFromConfigOrRoute:
    """Choosing methods from configuration or the route."""

    def test_methods_from_config_with_wildcard_returns_star(self):
        """``cfg.methods`` containing ``*`` short-circuits to ``["*"]``."""
        cfg = MCPConfigModel(methods="*")
        route = APIRoute("/x", lambda: None, methods=["GET"])
        assert _methods_from_config_or_route(cfg, route) == ["*"]

    def test_methods_from_config_explicit_list_uses_cfg_values(self):
        """A non-wildcard ``cfg.methods`` is unwrapped to its enum values."""
        cfg = MCPConfigModel(methods=["GET", "POST"])
        route = APIRoute("/x", lambda: None, methods=["DELETE"])
        assert _methods_from_config_or_route(cfg, route) == ["GET", "POST"]


class TestResolveMcpType:
    """Mapping configuration values to MCP types."""

    def test_resolve_mcp_type_covers_each_branch(self):
        """Each accepted alias maps to the matching MCPType enum."""
        assert _resolve_mcp_type("tool") == MCPType.TOOL
        assert _resolve_mcp_type("RESOURCE") == MCPType.RESOURCE
        assert _resolve_mcp_type("resource_template") == MCPType.RESOURCE_TEMPLATE
        assert _resolve_mcp_type("resource-template") == MCPType.RESOURCE_TEMPLATE
        assert _resolve_mcp_type("nonsense") is None
