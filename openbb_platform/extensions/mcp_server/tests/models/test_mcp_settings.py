"""Unit tests for MCPSettings model."""

from openbb_mcp_server.models.settings import (
    DEFAULT_CODE_MODE_MAX_DURATION_SECS,
    DEFAULT_CODE_MODE_MAX_MEMORY,
    DEFAULT_CODE_MODE_SEARCH_MAX_RESULTS,
    MCPSettings,
)


def test_mcp_settings_defaults():
    """Test the default values of MCPSettings."""
    settings = MCPSettings()
    assert settings.name == "OpenBB MCP"
    assert settings.default_tool_categories == ["all"]
    assert settings.allowed_tool_categories is None
    assert settings.enable_code_mode is False
    assert settings.enable_tool_discovery is True
    assert settings.describe_responses is False
    assert settings.get_code_mode_limits() == {
        "max_duration_secs": DEFAULT_CODE_MODE_MAX_DURATION_SECS,
        "max_memory": DEFAULT_CODE_MODE_MAX_MEMORY,
    }
    assert settings.code_mode_search_max_results == DEFAULT_CODE_MODE_SEARCH_MAX_RESULTS
    assert settings.code_mode_search_output_format == "markdown"


def test_mcp_settings_validation():
    """Test the validation of MCPSettings."""
    settings = MCPSettings(
        default_tool_categories="cat1,cat2",
        allowed_tool_categories="cat3",  # type: ignore
    )
    assert settings.default_tool_categories == ["cat1", "cat2"]
    assert settings.allowed_tool_categories == ["cat3"]


def test_mcp_settings_code_mode_aliases():
    """Test code-mode fields via env aliases."""
    settings = MCPSettings(
        OPENBB_MCP_ENABLE_CODE_MODE=True,
        OPENBB_MCP_CODE_MODE_MAX_DURATION_SECS=15,
        OPENBB_MCP_CODE_MODE_MAX_MEMORY=2048,
        OPENBB_MCP_CODE_MODE_MAX_ALLOCATIONS=1000,
        OPENBB_MCP_CODE_MODE_MAX_RECURSION_DEPTH=25,
        OPENBB_MCP_CODE_MODE_GC_INTERVAL=5,
        OPENBB_MCP_CODE_MODE_SEARCH_MAX_RESULTS=3,
        OPENBB_MCP_CODE_MODE_SEARCH_OUTPUT_FORMAT="json",
    )
    assert settings.enable_code_mode is True
    assert settings.get_code_mode_limits() == {
        "max_duration_secs": 15.0,
        "max_memory": 2048,
        "max_allocations": 1000,
        "max_recursion_depth": 25,
        "gc_interval": 5,
    }
    assert settings.code_mode_search_max_results == 3
    assert settings.code_mode_search_output_format == "json"


def test_mcp_settings_repr():
    """Test the string representation of MCPSettings."""
    settings = MCPSettings(name="Test")  # type: ignore
    repr_str = repr(settings)
    assert "MCPSettings" in repr_str
    assert "name: Test" in repr_str


def test_get_fastmcp_kwargs():
    """Test the get_fastmcp_kwargs method."""
    settings = MCPSettings(
        name="TestMCP",
        version="1.0",
        cache_expiration_seconds=3600,
        on_duplicate="error",
    )  # type: ignore
    kwargs = settings.get_fastmcp_kwargs()
    assert kwargs["name"] == "TestMCP"
    assert kwargs["version"] == "1.0"
    assert kwargs["cache_expiration_seconds"] == 3600
    assert kwargs["on_duplicate"] == "error"
    assert "api_prefix" not in kwargs
    assert "on_duplicate_tools" not in kwargs
    assert "on_duplicate_resources" not in kwargs
    assert "on_duplicate_prompts" not in kwargs


def test_get_fastmcp_kwargs_legacy_duplicate_fallback():
    """Test fallback from legacy duplicate fields to on_duplicate."""
    settings = MCPSettings(
        on_duplicate_tools="replace",
        on_duplicate_resources="warn",
        on_duplicate_prompts="ignore",
    )  # type: ignore
    kwargs = settings.get_fastmcp_kwargs()
    assert kwargs["on_duplicate"] == "replace"


def test_get_http_run_kwargs():
    """Test the get_http_run_kwargs method."""
    settings = MCPSettings(uvicorn_config={"host": "0.0.0.0", "port": 9000})  # type: ignore  # noqa: S104
    kwargs = settings.get_http_run_kwargs()
    assert kwargs["uvicorn_config"]["host"] == "0.0.0.0"  # noqa: S104
    assert kwargs["uvicorn_config"]["port"] == 9000


def test_get_httpx_kwargs():
    """Test the get_httpx_kwargs method."""
    settings = MCPSettings(httpx_client_kwargs={"timeout": 120})  # type: ignore
    kwargs = settings.get_httpx_kwargs()
    assert kwargs["timeout"] == 120


def test_update_settings():
    """Test updating settings from another MCPSettings instance."""
    settings1 = MCPSettings(name="Initial")  # type: ignore
    settings2 = MCPSettings(name="Updated", describe_responses=True)  # type: ignore
    settings1.update(settings2)
    assert settings1.name == "Updated"
    assert settings1.describe_responses is True
