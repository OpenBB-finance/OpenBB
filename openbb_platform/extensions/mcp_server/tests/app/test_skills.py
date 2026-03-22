"""Unit tests for skill provider loading in the MCP server."""

# pylint: disable=protected-access,unused-argument

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastmcp.prompts.function_prompt import FunctionPrompt
from openbb_mcp_server.app.app import _VENDOR_SKILLS_PROVIDERS, create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings


def _find_system_calls(mock_mcp):
    """Return add_prompt calls tagged with 'system'."""
    return [
        c
        for c in mock_mcp.add_prompt.call_args_list
        if hasattr(c[0][0], "tags") and "system" in c[0][0].tags
    ]


def _add_provider_calls(mock_mcp):
    """Return all add_provider calls."""
    return mock_mcp.add_provider.call_args_list


def _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes):
    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = []
    mock_process_routes.return_value = mock_processed_data
    mock_category_index.return_value = MagicMock()
    mock_mcp = MagicMock()
    mock_mcp.instructions = None
    mock_from_fastapi.return_value = mock_mcp
    return mock_mcp


# ---------------------------------------------------------------------------
# SkillsDirectoryProvider tests
# ---------------------------------------------------------------------------


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_skills_directory_provider_called(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """When default_skills_dir is a valid directory, add_provider is called with SkillsDirectoryProvider."""
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    settings = MCPSettings(default_skills_dir=str(skills_dir))  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    calls = _add_provider_calls(mock_mcp)
    assert len(calls) >= 1
    provider_arg = calls[0][0][0]
    assert isinstance(provider_arg, SkillsDirectoryProvider)


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_skills_reload_passed_to_provider(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """skills_reload=True is forwarded to SkillsDirectoryProvider."""
    from fastmcp.server.providers.skills import SkillsDirectoryProvider

    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    settings = MCPSettings(default_skills_dir=str(skills_dir), skills_reload=True)  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    calls = _add_provider_calls(mock_mcp)
    provider_arg = calls[0][0][0]
    assert isinstance(provider_arg, SkillsDirectoryProvider)
    assert provider_arg._reload is True


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_no_provider_when_skills_dir_is_none(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """No add_provider call is made when default_skills_dir is None."""
    settings = MCPSettings(default_skills_dir=None)  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    assert mock_mcp.add_provider.call_count == 0


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_no_provider_when_skills_dir_missing(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """No add_provider call is made when the skills directory does not exist."""
    settings = MCPSettings(default_skills_dir=str(tmp_path / "nonexistent"))  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    assert mock_mcp.add_provider.call_count == 0


# ---------------------------------------------------------------------------
# Vendor provider tests
# ---------------------------------------------------------------------------


def test_vendor_skills_provider_map_contains_expected_keys():
    """The _VENDOR_SKILLS_PROVIDERS map contains all documented short-names."""
    expected = {
        "claude",
        "cursor",
        "vscode",
        "copilot",
        "codex",
        "gemini",
        "goose",
        "opencode",
    }
    assert expected == set(_VENDOR_SKILLS_PROVIDERS.keys())


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_vendor_provider_added(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """When skills_providers is set, the corresponding vendor provider is registered."""
    from fastmcp.server.providers.skills import ClaudeSkillsProvider

    settings = MCPSettings(default_skills_dir=None, skills_providers=["claude"])  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    calls = _add_provider_calls(mock_mcp)
    assert len(calls) == 1
    assert isinstance(calls[0][0][0], ClaudeSkillsProvider)


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_multiple_vendor_providers_added(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """Multiple vendor provider names result in multiple add_provider calls."""
    from fastmcp.server.providers.skills import (
        ClaudeSkillsProvider,
        CursorSkillsProvider,
    )

    settings = MCPSettings(default_skills_dir=None, skills_providers=["claude", "cursor"])  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    calls = _add_provider_calls(mock_mcp)
    assert len(calls) == 2
    provider_types = {type(c[0][0]) for c in calls}
    assert ClaudeSkillsProvider in provider_types
    assert CursorSkillsProvider in provider_types


@patch("openbb_mcp_server.app.app.logger")
@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_unknown_vendor_provider_logs_warning(
    mock_from_fastapi, mock_category_index, mock_process_routes, mock_logger
):
    """Unknown provider names log a warning and do not crash."""
    settings = MCPSettings(default_skills_dir=None, skills_providers=["unknown_provider"])  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    assert mock_mcp.add_provider.call_count == 0
    mock_logger.warning.assert_called()
    warning_call = mock_logger.warning.call_args
    # First positional arg is the format string
    assert "Unknown skills provider" in warning_call[0][0]


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_skills_reload_passed_to_vendor_providers(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """skills_reload=True is forwarded to vendor providers."""
    from fastmcp.server.providers.skills import ClaudeSkillsProvider

    settings = MCPSettings(default_skills_dir=None, skills_providers=["claude"], skills_reload=True)  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    calls = _add_provider_calls(mock_mcp)
    assert len(calls) == 1
    provider = calls[0][0][0]
    assert isinstance(provider, ClaudeSkillsProvider)
    assert provider._reload is True


# ---------------------------------------------------------------------------
# Default system prompt nudge tests
# ---------------------------------------------------------------------------


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_default_system_prompt_added_when_bundled_skills_loaded(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """When bundled skills dir is valid, a default system prompt nudge is added."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    settings = MCPSettings(default_skills_dir=str(skills_dir))  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    system_calls = _find_system_calls(mock_mcp)
    assert len(system_calls) == 1

    added = system_calls[0][0][0]
    assert isinstance(added, FunctionPrompt)
    assert added.name == "system_prompt"
    assert "system" in added.tags

    content = added.fn()
    assert "list_resources()" in content
    assert "skill://" in content


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_default_system_prompt_added_when_vendor_skills_loaded(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """When vendor skills providers are configured, a default system prompt nudge is added."""
    settings = MCPSettings(default_skills_dir=None, skills_providers=["claude"])  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    system_calls = _find_system_calls(mock_mcp)
    assert len(system_calls) == 1
    content = system_calls[0][0][0].fn()
    assert "list_resources()" in content


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_no_default_system_prompt_when_no_skills(
    mock_from_fastapi, mock_category_index, mock_process_routes
):
    """When no skills are loaded, no default system prompt nudge is added."""
    settings = MCPSettings(default_skills_dir=None)  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    assert len(_find_system_calls(mock_mcp)) == 0
    assert mock_mcp.instructions is None


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_no_default_system_prompt_when_custom_set(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """When a custom system_prompt_file is set, no default nudge prompt is added for skills."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    prompt_file = tmp_path / "custom_prompt.txt"
    prompt_file.write_text("Custom system prompt text.", encoding="utf-8")

    settings = MCPSettings(
        default_skills_dir=str(skills_dir),
        system_prompt_file=str(prompt_file),
    )  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)

    create_mcp_server(settings, FastAPI())

    system_calls = _find_system_calls(mock_mcp)
    assert len(system_calls) == 1
    added = system_calls[0][0][0]
    assert added.name == "system_prompt"
    content = added.fn()
    assert content == "Custom system prompt text."
    assert mock_mcp.instructions == "Custom system prompt text."


@patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
@patch("openbb_mcp_server.app.app.CategoryIndex")
@patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
def test_explicit_instructions_not_overridden(
    mock_from_fastapi, mock_category_index, mock_process_routes, tmp_path
):
    """When instructions is explicitly set in settings, it is not overwritten."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()

    settings = MCPSettings(
        default_skills_dir=str(skills_dir),
        instructions="My explicit instructions.",
    )  # type: ignore
    mock_mcp = _make_mocks(mock_from_fastapi, mock_category_index, mock_process_routes)
    mock_mcp.instructions = "My explicit instructions."

    create_mcp_server(settings, FastAPI())

    system_calls = _find_system_calls(mock_mcp)
    assert len(system_calls) == 1
    assert mock_mcp.instructions == "My explicit instructions."


# ---------------------------------------------------------------------------
# MCPSettings integration tests
# ---------------------------------------------------------------------------


def test_skills_reload_default_is_false():
    """skills_reload defaults to False."""
    assert MCPSettings().skills_reload is False


def test_skills_providers_default_is_none():
    """skills_providers defaults to None."""
    assert MCPSettings().skills_providers is None


def test_skills_providers_comma_separated_env_var():
    """skills_providers accepts comma-separated strings (env var simulation)."""
    settings = MCPSettings(skills_providers="claude,cursor")  # type: ignore
    assert settings.skills_providers == ["claude", "cursor"]


def test_include_exclude_tags_removed():
    """include_tags and exclude_tags are no longer MCPSettings fields."""
    settings = MCPSettings()
    assert not hasattr(settings, "include_tags")
    assert not hasattr(settings, "exclude_tags")


# ---------------------------------------------------------------------------
# StaticPrompt curly-brace safety (unchanged behaviour)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_renders_with_curly_braces():
    """A StaticPrompt with curly braces in content renders without error."""
    from openbb_mcp_server.models.prompts import StaticPrompt

    content = '# Skill\n\n```python\nfetcher_dict = {"Example": ExampleFetcher}\n```'
    prompt = StaticPrompt(
        name="test_curly",
        description="Test skill",
        content=content,
        arguments=None,
        tags={"skill"},
    )
    rendered = await prompt.render()
    assert len(rendered) == 1
    assert rendered[0].content.text == content
