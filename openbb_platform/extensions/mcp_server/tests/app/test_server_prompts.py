"""Unit tests for server prompts functionality."""

# pylint: disable=protected-access,unused-argument

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.ToolRegistry")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_load_prompts_from_json(
    mock_from_fastapi, mock_tool_registry, mock_process_routes, tmp_path
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

    settings = MCPSettings(server_prompts_file=str(prompts_file))  # type: ignore
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_registry_instance = MagicMock()
    mock_tool_registry.return_value = mock_registry_instance

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
@patch("openbb_mcp_server.app.app.ToolRegistry")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_skip_invalid_prompts(
    mock_from_fastapi,
    mock_tool_registry,
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

    settings = MCPSettings(server_prompts_file=str(prompts_file))  # type: ignore
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_registry_instance = MagicMock()
    mock_tool_registry.return_value = mock_registry_instance

    mock_mcp_instance = MagicMock()
    mock_from_fastapi.return_value = mock_mcp_instance

    create_mcp_server(settings, fastapi_app)

    mock_mcp_instance.add_prompt.assert_not_called()
    assert mock_logger.error.call_count == 4


@patch("openbb_mcp_server.app.app.logger")
@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.ToolRegistry")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_skip_invalid_arguments_in_prompts(
    mock_from_fastapi,
    mock_tool_registry,
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

    settings = MCPSettings(server_prompts_file=str(prompts_file))  # type: ignore
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_registry_instance = MagicMock()
    mock_tool_registry.return_value = mock_registry_instance

    mock_mcp_instance = MagicMock()
    mock_from_fastapi.return_value = mock_mcp_instance

    create_mcp_server(settings, fastapi_app)

    mock_mcp_instance.add_prompt.assert_called_once()
    added_prompt = mock_mcp_instance.add_prompt.call_args[0][0]
    assert added_prompt.name == "test_prompt_invalid_arg"
    assert not added_prompt.arguments
    mock_logger.error.assert_called_once()


@pytest.mark.asyncio
@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.ToolRegistry")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
async def test_execute_prompt_tool(
    mock_from_fastapi, mock_tool_registry, mock_process_routes, tmp_path
):
    """Test the execute_prompt tool."""
    prompts_data = [
        {
            "name": "test_prompt_with_args",
            "description": "A test prompt with arguments.",
            "content": "Hello, {{ arg1 }} and {{ arg2 }}!",
            "arguments": [
                {"name": "arg1", "type": "str", "description": "Argument 1"},
                {
                    "name": "arg2",
                    "type": "str",
                    "description": "Argument 2",
                    "default": "default_value",
                },
            ],
        }
    ]
    prompts_file = tmp_path / "prompts.json"
    prompts_file.write_text(json.dumps(prompts_data))

    settings = MCPSettings(server_prompts_file=str(prompts_file))  # type: ignore
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data

    mock_registry_instance = MagicMock()
    mock_tool_registry.return_value = mock_registry_instance

    mock_mcp_instance = MagicMock()
    prompt_manager_mock = MagicMock()
    prompt_manager_mock.render_prompt = AsyncMock()
    mock_mcp_instance._prompt_manager = prompt_manager_mock
    mock_from_fastapi.return_value = mock_mcp_instance

    # We need to capture the function that gets decorated
    decorated_functions = {}

    def tool_decorator_factory(*args, **kwargs):
        """Factory for creating tool decorators."""

        def decorator(func):
            decorated_functions[func.__name__] = func
            # Return a mock to simulate the decorator's behavior if needed
            return MagicMock()

        return decorator

    mock_mcp_instance.tool = MagicMock(side_effect=tool_decorator_factory)

    create_mcp_server(settings, fastapi_app)

    execute_prompt_func = decorated_functions.get("execute_prompt")
    assert execute_prompt_func is not None

    # Test with required argument and default for optional
    await execute_prompt_func(
        prompt_name="test_prompt_with_args", arguments={"arg1": "world"}
    )
    mock_mcp_instance._prompt_manager.render_prompt.assert_called_with(
        name="test_prompt_with_args",
        arguments={"arg1": "world", "arg2": "default_value"},
    )

    # Test overriding default argument
    await execute_prompt_func(
        prompt_name="test_prompt_with_args",
        arguments={"arg1": "world", "arg2": "new_value"},
    )
    mock_mcp_instance._prompt_manager.render_prompt.assert_called_with(
        name="test_prompt_with_args",
        arguments={"arg1": "world", "arg2": "new_value"},
    )
