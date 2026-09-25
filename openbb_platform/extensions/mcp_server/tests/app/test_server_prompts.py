"""Tests for registering system, server, and inline prompts."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from openbb_mcp_server.app.app import (
    _add_inline_prompts,
    _add_prompts_from_json,
    _setup_file_system_prompt,
    create_mcp_server,
)
from openbb_mcp_server.models.category_index import CategoryIndex
from openbb_mcp_server.models.prompts import StaticPrompt
from openbb_mcp_server.models.settings import MCPSettings


@pytest.fixture(autouse=True)
def _patch_transforms():
    with (
        patch("openbb_mcp_server.app.app.PromptsAsTools", new=MagicMock()),
        patch("openbb_mcp_server.app.app.ResourcesAsTools", new=MagicMock()),
    ):
        yield


def _capture_decorated_tools(mock_mcp_instance):
    """Capture the undecorated tool closures registered on ``mock_mcp_instance``."""
    decorated: dict[str, object] = {}

    def tool_decorator_factory(*args, **kwargs):
        def decorator(func):
            decorated[func.__name__] = func
            return MagicMock()

        return decorator

    mock_mcp_instance.tool = MagicMock(side_effect=tool_decorator_factory)
    return decorated


def _build_server(
    settings: MCPSettings,
    *,
    index: CategoryIndex | None = None,
    prompts_json: list | None = None,
):
    """Build the MCP server with mocks and return ``(mcp_mock, decorated, index)``."""
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = prompts_json or []

    mock_mcp_instance = MagicMock()
    mock_mcp_instance.render_prompt = AsyncMock()

    decorated = _capture_decorated_tools(mock_mcp_instance)

    if index is None:
        index = CategoryIndex()

    with (
        patch(
            "openbb_mcp_server.app.app.process_fastapi_routes_for_mcp",
            return_value=mock_processed_data,
        ),
        patch(
            "openbb_mcp_server.app.app.CategoryIndex",
            return_value=index,
        ),
        patch(
            "openbb_mcp_server.app.app.FastMCP.from_fastapi",
            return_value=mock_mcp_instance,
        ),
    ):
        create_mcp_server(settings, fastapi_app)

    return mock_mcp_instance, decorated, index


class TestSetupFileSystemPrompt:
    """The system prompt loaded from a file."""

    def test_setup_file_system_prompt_no_op_when_file_missing(self, tmp_path):
        """Missing prompt file → early return, no mutations."""
        settings = MCPSettings(system_prompt_file=str(tmp_path / "nope.txt"))
        mcp = MagicMock(instructions=None)
        _setup_file_system_prompt(mcp, settings)
        mcp.add_prompt.assert_not_called()

    def test_setup_file_system_prompt_registers_function_prompt(self, tmp_path):
        """Prompt file content is registered as a FunctionPrompt + resource."""
        f = tmp_path / "sp.txt"
        f.write_text("the system prompt")
        settings = MCPSettings(system_prompt_file=str(f))

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

    def test_setup_file_system_prompt_does_not_overwrite_instructions(self, tmp_path):
        """If instructions are already set, the file content does NOT replace them."""
        f = tmp_path / "sp.txt"
        f.write_text("file content")
        settings = MCPSettings(system_prompt_file=str(f))
        mcp = MagicMock()
        mcp.instructions = "preexisting"

        def _resource(_uri):
            def _decorator(fn):
                return fn

            return _decorator

        mcp.resource = _resource
        _setup_file_system_prompt(mcp, settings)

        assert mcp.instructions == "preexisting"


class TestAddPromptsFromJson:
    """Server prompts loaded from a JSON file."""

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_load_prompts_from_json(
        self, mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
    ):
        """Test that prompts are loaded correctly from a JSON file."""
        prompts_data = [
            {
                "name": "test_prompt",
                "description": "A test prompt.",
                "content": "This is a test.",
                "arguments": [
                    {
                        "name": "arg1",
                        "type": "str",
                        "description": "Argument 1",
                        "default": "default1",
                    }
                ],
                "tags": ["test"],
            }
        ]
        prompts_file = tmp_path / "prompts.json"
        prompts_file.write_text(json.dumps(prompts_data))

        settings = MCPSettings(
            server_prompts_file=str(prompts_file), default_skills_dir=None
        )
        fastapi_app = FastAPI()

        mock_processed_data = MagicMock()
        mock_processed_data.route_lookup = {}
        mock_processed_data.route_maps = []
        mock_processed_data.prompt_definitions = []
        mock_process_routes.return_value = mock_processed_data

        mock_registry_instance = MagicMock()
        mock_category_index.return_value = mock_registry_instance

        mock_mcp_instance = MagicMock()
        mock_from_fastapi.return_value = mock_mcp_instance

        create_mcp_server(settings, fastapi_app)

        mock_mcp_instance.add_prompt.assert_called()
        added_prompt = mock_mcp_instance.add_prompt.call_args[0][0]
        assert added_prompt.name == "test_prompt"
        assert added_prompt.description == "A test prompt."
        assert added_prompt.content == "This is a test."
        assert "server" in added_prompt.tags
        assert "test" in added_prompt.tags

    @patch("openbb_mcp_server.app.app.logger")
    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_skip_invalid_prompts(
        self,
        mock_from_fastapi,
        mock_category_index,
        mock_process_routes,
        mock_logger,
        tmp_path,
    ):
        """Test that invalid prompt definitions are skipped and warnings are logged."""
        prompts_data = [
            {"description": "Missing name.", "content": "Content."},
            {"name": "missing_description", "content": "Content."},
            {"name": "missing_content", "description": "Description."},
            {"name": "invalid_content", "description": "Description.", "content": 123},
        ]
        prompts_file = tmp_path / "prompts.json"
        prompts_file.write_text(json.dumps(prompts_data))

        settings = MCPSettings(
            server_prompts_file=str(prompts_file), default_skills_dir=None
        )
        fastapi_app = FastAPI()

        mock_processed_data = MagicMock()
        mock_processed_data.route_lookup = {}
        mock_processed_data.route_maps = []
        mock_processed_data.prompt_definitions = []
        mock_process_routes.return_value = mock_processed_data

        mock_registry_instance = MagicMock()
        mock_category_index.return_value = mock_registry_instance

        mock_mcp_instance = MagicMock()
        mock_from_fastapi.return_value = mock_mcp_instance

        create_mcp_server(settings, fastapi_app)

        mock_mcp_instance.add_prompt.assert_not_called()
        assert mock_logger.error.call_count == 4

    @patch("openbb_mcp_server.app.app.logger")
    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_skip_invalid_arguments_in_prompts(
        self,
        mock_from_fastapi,
        mock_category_index,
        mock_process_routes,
        mock_logger,
        tmp_path,
    ):
        """Test that invalid argument definitions in prompts are skipped and errors are logged."""
        prompts_data = [
            {
                "name": "test_prompt_invalid_arg",
                "description": "A test prompt with an invalid argument.",
                "content": "This is a test.",
                "arguments": [{"description": "Missing name"}],
            }
        ]
        prompts_file = tmp_path / "prompts.json"
        prompts_file.write_text(json.dumps(prompts_data))

        settings = MCPSettings(
            server_prompts_file=str(prompts_file), default_skills_dir=None
        )
        fastapi_app = FastAPI()

        mock_processed_data = MagicMock()
        mock_processed_data.route_lookup = {}
        mock_processed_data.route_maps = []
        mock_processed_data.prompt_definitions = []
        mock_process_routes.return_value = mock_processed_data

        mock_registry_instance = MagicMock()
        mock_category_index.return_value = mock_registry_instance

        mock_mcp_instance = MagicMock()
        mock_from_fastapi.return_value = mock_mcp_instance

        create_mcp_server(settings, fastapi_app)

        mock_mcp_instance.add_prompt.assert_called_once()
        added_prompt = mock_mcp_instance.add_prompt.call_args[0][0]
        assert added_prompt.name == "test_prompt_invalid_arg"
        assert not added_prompt.arguments
        mock_logger.error.assert_called_once()

    def test_add_prompts_from_json_no_op_when_file_unset(self):
        """Missing settings.server_prompts_file → no-op."""
        mcp = MagicMock()
        settings = MCPSettings()
        _add_prompts_from_json(mcp, settings)
        mcp.add_prompt.assert_not_called()

    def test_add_prompts_from_json_handles_read_failure(self, tmp_path, app_caplog):
        """File read failure logs an error and returns."""
        settings = MCPSettings(server_prompts_file=str(tmp_path / "missing.json"))
        mcp = MagicMock()
        _add_prompts_from_json(mcp, settings)
        assert "Failed to load prompts" in app_caplog.text

    def test_add_prompts_from_json_skips_invalid_entries(self, tmp_path, app_caplog):
        """Each malformed prompt entry is skipped + logged."""
        f = tmp_path / "prompts.json"
        f.write_text(
            '[{"description": "no name"}, '
            '{"name": "no_desc"}, '
            '{"name": "no_content", "description": "x"}, '
            '{"name": "bad_content", "description": "x", "content": 5}, '
            '{"name": "ok", "description": "d", "content": "c"}]'
        )
        settings = MCPSettings(server_prompts_file=str(f))
        mcp = MagicMock()

        _add_prompts_from_json(mcp, settings)

        assert mcp.add_prompt.call_count == 1
        assert mcp.add_prompt.call_args[0][0].name == "ok"
        assert "without a name" in app_caplog.text
        assert "without a description" in app_caplog.text
        assert "without content" in app_caplog.text
        assert "invalid content type" in app_caplog.text

    def test_add_prompts_from_json_validates_argument_definitions(
        self, tmp_path, app_caplog
    ):
        """Invalid argument definitions inside a prompt are skipped + logged."""
        f = tmp_path / "p.json"
        f.write_text(
            '[{"name": "p", "description": "d", "content": "c", '
            '"arguments": [{"description": "no name field"}]}]'
        )
        settings = MCPSettings(server_prompts_file=str(f))
        mcp = MagicMock()
        _add_prompts_from_json(mcp, settings)
        assert mcp.add_prompt.call_count == 1
        assert mcp.add_prompt.call_args[0][0].arguments is None
        assert "Skipping argument definition in server prompt, p" in app_caplog.text

    def test_add_prompts_from_json_argument_with_default_is_optional(self, tmp_path):
        """Defaulted arguments are optional; others are required, description or not."""
        f = tmp_path / "p.json"
        f.write_text(
            '[{"name": "p", "description": "d", "content": "{a} {b}", '
            '"arguments": [{"name": "a", "description": "x", "default": "hi"}, '
            '{"name": "b"}]}]'
        )
        settings = MCPSettings(server_prompts_file=str(f))
        mcp = MagicMock()
        _add_prompts_from_json(mcp, settings)
        prompt = mcp.add_prompt.call_args[0][0]
        assert [(a.name, a.description, a.required) for a in prompt.arguments] == [
            ("a", "x", False),
            ("b", None, True),
        ]
        assert prompt.argument_defaults == {"a": "hi"}


class TestAddInlinePrompts:
    """Prompts declared inline on routes."""

    def test_add_inline_prompts_registers_each(self):
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
                {"name": "p2", "description": "d2", "content": "c2", "tool": "two"},
            ],
        )
        prompts = [call.args[0] for call in mcp.add_prompt.call_args_list]
        assert [prompt.name for prompt in prompts] == ["p1", "p2"]
        assert prompts[0].tags == {"x", "route-specific", "tool_one"}
        assert prompts[1].tags == {"route-specific", "two"}

    def test_add_inline_prompts_skips_invalid(self, app_caplog):
        """Malformed inline prompt entries are skipped + logged."""
        mcp = MagicMock()
        _add_inline_prompts(mcp, [{"name": "missing_required_keys"}])
        mcp.add_prompt.assert_not_called()
        assert "Skipping invalid prompt definition" in app_caplog.text

    def test_add_inline_prompts_with_argument_default(self):
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
        prompt = mcp.add_prompt.call_args[0][0]
        assert [(a.name, a.required) for a in prompt.arguments] == [("a", False)]
        assert prompt.argument_defaults == {"a": "hello"}

    def test_inline_prompt_stores_argument_defaults(self):
        """Inline prompt definitions store defaults on StaticPrompt.argument_defaults."""
        prompt_def = {
            "name": "my_prompt",
            "description": "Test",
            "content": "Hello {name}, focus on {aspect}",
            "arguments": [
                {"name": "name", "type": "str", "description": "Name"},
                {
                    "name": "aspect",
                    "type": "str",
                    "description": "Aspect",
                    "default": "fundamentals",
                },
            ],
        }
        settings = MCPSettings()
        mock_mcp, _, _ = _build_server(settings, prompts_json=[prompt_def])

        added_prompts = [
            call[0][0]
            for call in mock_mcp.add_prompt.call_args_list
            if isinstance(call[0][0], StaticPrompt)
        ]
        assert len(added_prompts) == 1
        assert added_prompts[0].argument_defaults == {"aspect": "fundamentals"}


class TestPromptTransforms:
    """Prompts and resources exposed as tools."""

    def test_transforms_are_added(self):
        """Both PromptsAsTools and ResourcesAsTools transforms are registered."""
        from openbb_mcp_server.app import app as app_module

        settings = MCPSettings()
        mock_mcp, _, _ = _build_server(settings)

        added = [call.args[0] for call in mock_mcp.add_transform.call_args_list]
        assert added == [
            app_module.PromptsAsTools.return_value,
            app_module.ResourcesAsTools.return_value,
        ]

    def test_no_hand_rolled_prompt_or_resource_tools(self):
        """The old list_prompts / execute_prompt / list_resources / read_resource closures are no longer registered."""
        settings = MCPSettings()
        _, decorated, _ = _build_server(settings)

        assert "list_prompts" not in decorated
        assert "execute_prompt" not in decorated
        assert "list_resources" not in decorated
        assert "read_resource" not in decorated
