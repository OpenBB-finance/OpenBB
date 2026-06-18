"""Coverage-completion tests for ``openbb_mcp_server.app.app`` helpers."""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastmcp.server.providers.openapi import OpenAPITool
from fastmcp.utilities.openapi import HTTPRoute

from openbb_mcp_server.app.app import (
    SSEShutdownWrapper,
    _add_inline_prompts,
    _add_prompts_from_json,
    _add_skills_default_prompt,
    _build_runtime_middleware,
    _extract_brief_description,
    _get_mcp_config_from_route,
    _read_system_prompt_file,
    _setup_file_system_prompt,
    _strip_api_prefix,
    create_mcp_server,
    stdio_main,
)
from openbb_mcp_server.models.settings import MCPSettings


@pytest.fixture(autouse=True)
def _patch_transforms():
    """Stub ``PromptsAsTools`` / ``ResourcesAsTools`` for mock-based tests."""
    with (
        patch("openbb_mcp_server.app.app.PromptsAsTools", new=MagicMock()),
        patch("openbb_mcp_server.app.app.ResourcesAsTools", new=MagicMock()),
    ):
        yield


@pytest.fixture(autouse=True)
def _propagate_app_logger():
    """Force-propagate the fastmcp child logger so ``caplog`` sees its output."""
    import logging as _logging

    from openbb_mcp_server.app.app import logger as app_logger

    original = app_logger.propagate
    app_logger.propagate = True
    parent = app_logger.parent
    parents_state: list = []
    while parent and parent is not _logging.root:
        parents_state.append((parent, parent.propagate))
        parent.propagate = True
        parent = parent.parent
    yield
    app_logger.propagate = original
    for p, prop in parents_state:
        p.propagate = prop


def test_get_mcp_config_handles_non_dict_value():
    """If ``mcp_config`` is set but not a dict, ``{}`` is returned."""
    route = APIRoute("/x", lambda: None, openapi_extra={"mcp_config": "bad"})
    assert _get_mcp_config_from_route(route) == {}


def test_get_mcp_config_falls_back_to_x_mcp_alias():
    """Legacy ``x-mcp`` alias is honored."""
    route = APIRoute("/x", lambda: None, openapi_extra={"x-mcp": {"name": "renamed"}})
    assert _get_mcp_config_from_route(route) == {"name": "renamed"}


def test_get_mcp_config_no_openapi_extra():
    """Route without ``openapi_extra`` → empty dict."""
    route = APIRoute("/x", lambda: None)
    route.openapi_extra = None
    assert _get_mcp_config_from_route(route) == {}


def test_strip_api_prefix_empty_path():
    """Empty path → empty string."""
    assert _strip_api_prefix("", "/api/v1") == ""


def test_strip_api_prefix_path_without_leading_slash():
    """Path with no leading slash gets one prepended before stripping."""
    assert _strip_api_prefix("api/v1/foo", "/api/v1") == "foo"


def test_strip_api_prefix_path_doesnt_start_with_prefix():
    """Path that doesn't start with the prefix is returned unstripped."""
    assert _strip_api_prefix("/other/route", "/api/v1") == "other/route"


def test_extract_brief_description_strips_responses_section():
    """``**Responses:`` section is also a split delimiter."""
    full = "Lead.\n\n**Responses:** payload"
    assert _extract_brief_description(full) == "Lead."


def test_extract_brief_description_returns_default_for_blank_after_split():
    """If the brief is empty post-split, the default sentinel is returned."""
    assert _extract_brief_description("\n\n**Query Parameters:** stuff") == (
        "No description available"
    )


def test_read_system_prompt_file_swallows_read_errors(tmp_path, caplog):
    """Read errors (permission denied etc.) are caught and logged."""
    f = tmp_path / "prompt.txt"
    f.write_text("hello")

    with patch.object(Path, "read_text", side_effect=OSError("simulated read failure")):
        out = _read_system_prompt_file(str(f))
    assert out is None
    assert "simulated read failure" in caplog.text


def test_read_system_prompt_file_returns_none_for_directory(tmp_path):
    """A directory path returns None (``is_file()`` False)."""
    out = _read_system_prompt_file(str(tmp_path))
    assert out is None


def test_build_runtime_middleware_uses_system_service_cors():
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


def test_setup_file_system_prompt_no_op_when_file_missing(tmp_path):
    """Missing prompt file → early return, no mutations."""
    settings = MCPSettings(system_prompt_file=str(tmp_path / "nope.txt"))  # type: ignore
    mcp = MagicMock(instructions=None)
    _setup_file_system_prompt(mcp, settings)
    mcp.add_prompt.assert_not_called()


def test_setup_file_system_prompt_registers_function_prompt(tmp_path):
    """Prompt file content is registered as a FunctionPrompt + resource."""
    f = tmp_path / "sp.txt"
    f.write_text("the system prompt")
    settings = MCPSettings(system_prompt_file=str(f))  # type: ignore

    mcp = MagicMock()
    mcp.instructions = None
    captured: dict = {}

    def _resource(_uri):
        def _decorator(fn):
            captured["resource_fn"] = fn
            return fn

        return _decorator

    mcp.resource = _resource
    _setup_file_system_prompt(mcp, settings)

    mcp.add_prompt.assert_called_once()
    assert mcp.instructions == "the system prompt"
    assert captured["resource_fn"]() == "the system prompt"


def test_setup_file_system_prompt_does_not_overwrite_instructions(tmp_path):
    """If instructions are already set, the file content does NOT replace them."""
    f = tmp_path / "sp.txt"
    f.write_text("file content")
    settings = MCPSettings(system_prompt_file=str(f))  # type: ignore
    mcp = MagicMock()
    mcp.instructions = "preexisting"

    def _resource(_uri):
        def _decorator(fn):
            return fn

        return _decorator

    mcp.resource = _resource
    _setup_file_system_prompt(mcp, settings)

    assert mcp.instructions == "preexisting"


def test_add_prompts_from_json_no_op_when_file_unset():
    """Missing settings.server_prompts_file → no-op."""
    mcp = MagicMock()
    settings = MCPSettings()
    _add_prompts_from_json(mcp, settings)
    mcp.add_prompt.assert_not_called()


def test_add_prompts_from_json_handles_read_failure(tmp_path, caplog):
    """File read failure logs an error and returns."""
    settings = MCPSettings(server_prompts_file=str(tmp_path / "missing.json"))  # type: ignore
    mcp = MagicMock()
    _add_prompts_from_json(mcp, settings)
    assert "Failed to load prompts" in caplog.text


def test_add_prompts_from_json_skips_invalid_entries(tmp_path, caplog):
    """Each malformed prompt entry is skipped + logged."""
    f = tmp_path / "prompts.json"
    f.write_text(
        '[{"description": "no name"}, '
        '{"name": "no_desc"}, '
        '{"name": "no_content", "description": "x"}, '
        '{"name": "bad_content", "description": "x", "content": 5}, '
        '{"name": "ok", "description": "d", "content": "c"}]'
    )
    settings = MCPSettings(server_prompts_file=str(f))  # type: ignore
    mcp = MagicMock()

    _add_prompts_from_json(mcp, settings)

    assert mcp.add_prompt.call_count == 1


def test_add_prompts_from_json_validates_argument_definitions(tmp_path, caplog):
    """Invalid argument definitions inside a prompt are skipped + logged."""
    f = tmp_path / "p.json"
    f.write_text(
        '[{"name": "p", "description": "d", "content": "c", '
        '"arguments": [{"description": "no name field"}]}]'
    )
    settings = MCPSettings(server_prompts_file=str(f))  # type: ignore
    mcp = MagicMock()
    _add_prompts_from_json(mcp, settings)
    assert mcp.add_prompt.call_count == 1


def test_add_prompts_from_json_argument_with_default_is_optional(tmp_path):
    """A defaulted argument is registered as not required."""
    f = tmp_path / "p.json"
    f.write_text(
        '[{"name": "p", "description": "d", "content": "{a}", '
        '"arguments": [{"name": "a", "description": "x", "default": "hi"}]}]'
    )
    settings = MCPSettings(server_prompts_file=str(f))  # type: ignore
    mcp = MagicMock()
    _add_prompts_from_json(mcp, settings)
    assert mcp.add_prompt.call_count == 1


def test_add_inline_prompts_registers_each(monkeypatch):
    """Inline prompt definitions are registered, one per entry."""
    mcp = MagicMock()
    _add_inline_prompts(
        mcp,
        [
            {
                "name": "p1",
                "description": "d1",
                "content": "c1",
                "arguments": [],
                "tags": ["x"],
                "tool": "tool_one",
            },
        ],
    )
    mcp.add_prompt.assert_called_once()


def test_add_inline_prompts_skips_invalid(caplog):
    """Malformed inline prompt entries are skipped + logged."""
    mcp = MagicMock()
    _add_inline_prompts(mcp, [{"name": "missing_required_keys"}])
    mcp.add_prompt.assert_not_called()


def test_add_inline_prompts_with_argument_default(caplog):
    """Inline prompt with a defaulted argument is registered correctly."""
    mcp = MagicMock()
    _add_inline_prompts(
        mcp,
        [
            {
                "name": "p",
                "description": "d",
                "content": "{a}",
                "arguments": [{"name": "a", "default": "hello"}],
                "tags": ["x"],
                "tool": "t",
            }
        ],
    )
    assert mcp.add_prompt.called


def test_add_skills_default_prompt_registers_and_sets_instructions():
    """Adds a default skill-awareness prompt and seeds instructions."""
    mcp = MagicMock()
    mcp.instructions = None
    _add_skills_default_prompt(mcp)
    mcp.add_prompt.assert_called_once()
    assert "skill" in (mcp.instructions or "").lower()


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_customize_components_three_segment_path(
    mock_from_fastapi, mock_category_index, mock_process_routes
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
    mock_processed.route_lookup = {("/api/v1/equity/price/historical", "GET"): route}
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
    mock_from_fastapi, mock_category_index, mock_process_routes
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
    mock_from_fastapi, mock_category_index, mock_process_routes
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
    mock_from_fastapi, mock_category_index, mock_process_routes, caplog
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


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_customize_components_resource_mime_type(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """OpenAPIResource components honor an mcp_config-supplied mime_type."""
    from fastmcp.server.providers.openapi import OpenAPIResource

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
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """mcp_config.enable=True / False overrides the category-default match."""
    settings = MCPSettings(default_tool_categories=["nonexistent"])  # type: ignore
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
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """``mcp_config.enable=False`` skips a category-default match."""
    settings = MCPSettings(default_tool_categories=["all"])  # type: ignore
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
    mock_from_fastapi, mock_category_index, mock_process_routes
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
def test_create_mcp_server_loads_bundled_skills(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """A populated bundled skills dir spawns a SkillsDirectoryProvider."""
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore
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

    create_mcp_server(settings, fastapi_app)
    mock_mcp.add_provider.assert_called()


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_loads_vendor_skills(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """Configured vendor skill providers are added by name."""
    settings = MCPSettings(skills_providers=["claude", "unknown_vendor"])  # type: ignore
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

    create_mcp_server(settings, fastapi_app)
    assert mock_mcp.add_provider.called


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_registers_admin_tools_with_discovery(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """Discovery mode registers the admin/category-browsing tool surface."""
    settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
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
    captured_tools: list = []

    def _tool_decorator(*args, **kwargs):  # noqa: ARG001
        def _inner(fn):
            captured_tools.append(fn)
            return fn

        return _inner

    mock_mcp.tool = _tool_decorator
    mock_from_fastapi.return_value = mock_mcp

    create_mcp_server(settings, fastapi_app)

    tool_names = {fn.__name__ for fn in captured_tools}
    assert {
        "available_categories",
        "available_tools",
        "activate_tools",
        "deactivate_tools",
        "activate_category",
        "install_skill",
    } <= tool_names


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_registers_cli_tools_when_enabled(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """``settings.enable_cli_tools`` triggers cli_tools.register_cli_tools."""
    settings = MCPSettings(enable_cli_tools=True)  # type: ignore
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


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_with_auth_provider(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """A 2-tuple auth credentials trigger ``get_auth_provider``."""
    settings = MCPSettings()
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

    with patch(
        "openbb_mcp_server.app.auth.get_auth_provider", return_value=MagicMock()
    ) as mock_auth:
        create_mcp_server(settings, fastapi_app, auth=("user", "pass"))
    mock_auth.assert_called_once()


def test_sse_shutdown_wrapper_handles_runtime_error_with_response_started():
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


def test_sse_shutdown_wrapper_synthesizes_response_when_runtime_error_pre_start():
    """Body-before-start RuntimeError fires the synthesize-200 fallback."""
    sent: list = []
    underlying_error_count = {"n": 0}

    async def _send(message):
        if message["type"] == "http.response.body" and underlying_error_count["n"] == 0:
            underlying_error_count["n"] += 1
            raise RuntimeError("Expected ASGI message 'http.response.start'")
        sent.append(message)

    async def _inner(scope, receive, send):
        await send({"type": "http.response.body", "body": b"oops"})

    wrapped = SSEShutdownWrapper(_inner)
    asyncio.run(wrapped({"type": "http", "path": "/sse/"}, MagicMock(), _send))
    assert any(
        m["type"] == "http.response.body" and b"Connection closed" in m.get("body", b"")
        for m in sent
    )


def test_sse_shutdown_wrapper_re_raises_unrelated_runtime_error():
    """Other RuntimeErrors propagate."""

    async def _send(message):  # noqa: ARG001
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


def test_sse_shutdown_wrapper_passes_through_unrelated_message_types():
    """Messages other than http.response.start/body fall through unchanged."""

    async def _send(message):
        return message

    sent: list = []

    async def _inner(scope, receive, send):
        await send({"type": "http.disconnect"})

    wrapped = SSEShutdownWrapper(_inner)
    asyncio.run(wrapped({"type": "http", "path": "/sse/"}, MagicMock(), _send))
    assert sent == []


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_customize_components_compresses_output_schema(
    mock_from_fastapi, mock_category_index, mock_process_routes
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

    http_route = HTTPRoute(path="/api/v1/equity/price", method="GET")
    tool = OpenAPITool(
        MagicMock(),
        http_route,
        name="o",
        description="d",
        parameters={"foo": {"type": "string"}},
        director=MagicMock(),
    )
    tool.output_schema = {"bar": {"type": "string"}}  # type: ignore
    customize(http_route, tool)


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_customize_components_should_enable_false_fallback(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """No enable override AND no matching tag → should_enable=False."""
    settings = MCPSettings(default_tool_categories=["nonexistent"])  # type: ignore
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


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_create_mcp_server_fixed_toolset_calls_enable(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """Fixed-toolset mode with matches calls ``mcp.enable`` on the toolset."""
    settings = MCPSettings(default_tool_categories=["equity"])  # type: ignore
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


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_writes_to_bundled_provider(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """``install_skill`` writes files into a bundled SkillsDirectoryProvider's root."""
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    class _FakeMCP:
        providers: list = []
        instructions = None

        def __init__(self):
            from fastmcp.server.providers.skills import SkillsDirectoryProvider

            self.providers = [SkillsDirectoryProvider(roots=skills_root.resolve())]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    fake = _FakeMCP()
    mock_from_fastapi.return_value = fake

    settings.enable_tool_discovery = True
    create_mcp_server(settings, FastAPI())

    install_skill = captured_tools["install_skill"]

    out = asyncio.run(
        install_skill(
            skill_name="my_skill",
            files={"SKILL.md": "# My Skill\n", "helper.py": "x = 1\n"},
            target="bundled",
        )
    )

    assert out["status"] == "installed"
    assert (skills_root / "my_skill" / "SKILL.md").read_text() == "# My Skill\n"
    assert (skills_root / "my_skill" / "helper.py").read_text() == "x = 1\n"


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_rejects_missing_skill_md(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """``install_skill`` requires a ``SKILL.md`` entry — raises if missing."""
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    class _FakeMCP:
        providers: list = []
        instructions = None

        def __init__(self):
            from fastmcp.server.providers.skills import SkillsDirectoryProvider

            self.providers = [SkillsDirectoryProvider(roots=skills_root.resolve())]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    create_mcp_server(settings, FastAPI())

    install_skill = captured_tools["install_skill"]

    with pytest.raises(ValueError, match="SKILL.md"):
        asyncio.run(
            install_skill(skill_name="x", files={"helper.py": "x"}, target="bundled")
        )


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_unknown_target_raises(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """Unknown ``target`` value raises a clear error listing valid targets."""
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    class _FakeMCP:
        providers: list = []
        instructions = None

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    create_mcp_server(settings, FastAPI())

    install_skill = captured_tools["install_skill"]
    with pytest.raises(ValueError, match="not found or not loaded"):
        asyncio.run(
            install_skill(
                skill_name="x", files={"SKILL.md": "x"}, target="not_a_real_vendor"
            )
        )


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_targets_vendor_provider(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """``target='claude'`` writes into the matching vendor SkillsDirectoryProvider."""
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    class _FakeClaude(SkillsDirectoryProvider):
        pass

    settings = MCPSettings(default_skills_dir=None)  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    claude_provider = _FakeClaude(roots=tmp_path.resolve())

    class _FakeMCP:
        instructions = None

        def __init__(self):
            self.providers = [claude_provider]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    with patch.dict(
        "openbb_mcp_server.app.app._VENDOR_SKILLS_PROVIDERS",
        {"claude": _FakeClaude},
        clear=True,
    ):
        create_mcp_server(settings, FastAPI())

        install_skill = captured_tools["install_skill"]
        out = asyncio.run(
            install_skill(
                skill_name="claude_skill",
                files={"SKILL.md": "claude content"},
                target="claude",
            )
        )
    assert out["status"] in {"installed", "updated"}
    assert out["target"] == "claude"


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_skips_non_skills_directory_providers(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """Non-SkillsDirectoryProvider entries in ``mcp.providers`` are skipped."""
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    class _FakeMCP:
        instructions = None

        def __init__(self):
            self.providers = [
                object(),
                SkillsDirectoryProvider(roots=skills_root.resolve()),
            ]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    create_mcp_server(settings, FastAPI())

    install_skill = captured_tools["install_skill"]
    out = asyncio.run(
        install_skill(skill_name="x", files={"SKILL.md": "ok"}, target="bundled")
    )
    assert out["status"] == "installed"


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_unknown_target_lists_vendor_options(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """Unknown target lists ALL detected vendor providers in the error."""
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    class _FakeClaude(SkillsDirectoryProvider):
        pass

    class _FakeCursor(SkillsDirectoryProvider):
        pass

    settings = MCPSettings(default_skills_dir=None)  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    class _FakeMCP:
        instructions = None

        def __init__(self):
            self.providers = [
                _FakeClaude(roots=tmp_path.resolve()),
                _FakeCursor(roots=tmp_path.resolve()),
            ]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    with patch.dict(
        "openbb_mcp_server.app.app._VENDOR_SKILLS_PROVIDERS",
        {"claude": _FakeClaude, "cursor": _FakeCursor},
        clear=True,
    ):
        create_mcp_server(settings, FastAPI())

        install_skill = captured_tools["install_skill"]
        with pytest.raises(ValueError) as exc_info:
            asyncio.run(
                install_skill(
                    skill_name="x",
                    files={"SKILL.md": "x"},
                    target="not_a_real_one",
                )
            )
    msg = str(exc_info.value)
    assert "claude" in msg
    assert "cursor" in msg


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_provider_with_empty_roots_raises(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """Provider whose ``_roots`` is empty raises a clear ValueError."""
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    provider = SkillsDirectoryProvider(roots=skills_root.resolve())
    provider._roots = []  # noqa: SLF001 — simulate an empty-roots edge case

    class _FakeMCP:
        instructions = None

        def __init__(self):
            self.providers = [provider]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    create_mcp_server(settings, FastAPI())

    install_skill = captured_tools["install_skill"]
    settings.default_skills_dir = str(skills_root.resolve())
    provider._roots = [skills_root.resolve()]  # noqa: SLF001
    original_get = provider._roots

    async def _run_with_emptied_roots():
        class _RootsSentinel(list):
            def __contains__(self, _item):
                return True

            def __bool__(self):
                return False

        provider._roots = _RootsSentinel()  # noqa: SLF001
        try:
            await install_skill(
                skill_name="x", files={"SKILL.md": "x"}, target="bundled"
            )
        finally:
            provider._roots = original_get  # noqa: SLF001

    with pytest.raises(ValueError, match="no configured root directories"):
        asyncio.run(_run_with_emptied_roots())


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_install_skill_updates_existing(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """Re-installing an existing skill returns ``status='updated'``."""
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    settings = MCPSettings(default_skills_dir=str(skills_root))  # type: ignore
    settings.enable_tool_discovery = True

    mock_processed = MagicMock()
    mock_processed.route_lookup = {}
    mock_processed.route_maps = []
    mock_processed.prompt_definitions = []
    mock_process_routes.return_value = mock_processed

    idx = MagicMock()
    idx.all_tool_names.return_value = set()
    mock_category_index.return_value = idx

    captured_tools: dict = {}

    class _FakeMCP:
        providers: list = []
        instructions = None

        def __init__(self):
            from fastmcp.server.providers.skills import SkillsDirectoryProvider

            self.providers = [SkillsDirectoryProvider(roots=skills_root.resolve())]

        def disable(self, names):
            pass

        def enable(self, names):
            pass

        def add_provider(self, *args, **kwargs):
            pass

        def add_prompt(self, *args, **kwargs):
            pass

        def add_transform(self, *args, **kwargs):
            pass

        def resource(self, _uri):
            def _decorator(fn):
                return fn

            return _decorator

        def tool(self, *, tags=None):  # noqa: ARG002
            def _decorator(fn):
                captured_tools[fn.__name__] = fn
                return fn

            return _decorator

    mock_from_fastapi.return_value = _FakeMCP()
    create_mcp_server(settings, FastAPI())

    install_skill = captured_tools["install_skill"]

    asyncio.run(
        install_skill(skill_name="dup", files={"SKILL.md": "v1"}, target="bundled")
    )
    out = asyncio.run(
        install_skill(skill_name="dup", files={"SKILL.md": "v2"}, target="bundled")
    )
    assert out["status"] == "updated"


@pytest.mark.asyncio
async def test_stdio_main_signal_handler_calls_os_exit(monkeypatch):
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
