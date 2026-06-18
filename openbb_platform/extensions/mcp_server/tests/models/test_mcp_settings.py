"""Unit tests for MCPSettings model."""

from openbb_mcp_server.models.settings import MCPSettings


def test_mcp_settings_defaults():
    """Test the default values of MCPSettings."""
    settings = MCPSettings()
    assert settings.name == "OpenBB MCP"
    assert settings.default_tool_categories == ["all"]
    assert settings.allowed_tool_categories is None
    assert settings.enable_tool_discovery is False
    assert settings.describe_responses is False


def test_mcp_settings_validation():
    """Test the validation of MCPSettings."""
    settings = MCPSettings(
        default_tool_categories="cat1,cat2",
        allowed_tool_categories="cat3",  # type: ignore
    )
    assert settings.default_tool_categories == ["cat1", "cat2"]
    assert settings.allowed_tool_categories == ["cat3"]


def test_mcp_settings_repr():
    """Test the string representation of MCPSettings."""
    settings = MCPSettings(name="Test")  # type: ignore
    repr_str = repr(settings)
    assert "MCPSettings" in repr_str
    assert "name: Test" in repr_str


def test_get_fastmcp_kwargs():
    """Test the get_fastmcp_kwargs method."""
    settings = MCPSettings(name="TestMCP", version="1.0", cache_expiration_seconds=3600)  # type: ignore
    kwargs = settings.get_fastmcp_kwargs()
    assert kwargs["name"] == "TestMCP"
    assert kwargs["version"] == "1.0"
    assert kwargs["cache_expiration_seconds"] == 3600
    assert "api_prefix" not in kwargs


def test_list_page_size_defaults_none():
    """list_page_size defaults to None and is excluded from fastmcp kwargs."""
    settings = MCPSettings()
    assert settings.list_page_size is None
    assert "list_page_size" not in settings.get_fastmcp_kwargs()


def test_list_page_size_in_fastmcp_kwargs():
    """When set, list_page_size is passed through to FastMCP constructor kwargs."""
    settings = MCPSettings(list_page_size=50)  # type: ignore
    kwargs = settings.get_fastmcp_kwargs()
    assert kwargs["list_page_size"] == 50


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


def test_validate_json_or_tuple_blank_string_returns_none():
    """A blank ``server_auth`` string normalizes to None."""
    settings = MCPSettings(server_auth="   ")  # type: ignore[arg-type]
    assert settings.server_auth is None


def test_validate_json_or_tuple_parses_json_list():
    """A JSON-shaped ``server_auth`` string is decoded to a tuple."""
    settings = MCPSettings(server_auth='["user", "pass"]')  # type: ignore[arg-type]
    assert settings.server_auth == ("user", "pass")


def test_validate_json_or_tuple_passthrough_for_invalid_json():
    """Invalid JSON falls through to the raw string and fails tuple coercion."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        MCPSettings(server_auth="not-json")  # type: ignore[arg-type]


def test_get_httpx_kwargs_attaches_client_auth():
    """``client_auth`` lands on the returned dict under ``auth``."""
    settings = MCPSettings(client_auth=("u", "p"))  # type: ignore[arg-type]
    kwargs = settings.get_httpx_kwargs()
    assert kwargs["auth"] == ("u", "p")
