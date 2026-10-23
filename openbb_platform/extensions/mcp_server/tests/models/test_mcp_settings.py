"""Tests for ``openbb_mcp_server.models.settings``."""

import pytest
from fastmcp import FastMCP
from pydantic import ValidationError

from openbb_mcp_server.models.settings import MCPSettings


class TestFastMCPConstructorKwargs:
    """Every kwarg from ``get_fastmcp_kwargs`` is accepted by the real ``FastMCP``."""

    def test_all_settings_populated(self):
        settings = MCPSettings(
            name="Kwargs",
            version="2.0",
            instructions="Use the tools.",
            on_duplicate="replace",
            mask_error_details=True,
            list_page_size=10,
        )
        kwargs = settings.get_fastmcp_kwargs()
        assert set(kwargs) == {
            "name",
            "version",
            "instructions",
            "on_duplicate",
            "mask_error_details",
            "list_page_size",
        }
        server = FastMCP(**kwargs)
        assert server.name == "Kwargs"
        assert server.instructions == "Use the tools."

    def test_defaults(self):
        server = FastMCP(**MCPSettings().get_fastmcp_kwargs())
        assert server.name == "OpenBB MCP"


class TestMCPSettings:
    """Settings defaults, validation, and derived kwargs."""

    def test_mcp_settings_defaults(self):
        """Test the default values of MCPSettings."""
        settings = MCPSettings()
        assert settings.name == "OpenBB MCP"
        assert settings.default_tool_categories == ["all"]
        assert settings.allowed_tool_categories is None
        assert settings.enable_tool_discovery is False
        assert settings.describe_responses is False

    def test_mcp_settings_validation(self):
        """Test the validation of MCPSettings."""
        settings = MCPSettings(
            default_tool_categories="cat1,cat2",
            allowed_tool_categories="cat3",
        )
        assert settings.default_tool_categories == ["cat1", "cat2"]
        assert settings.allowed_tool_categories == ["cat3"]

    def test_mcp_settings_repr(self):
        """Test the string representation of MCPSettings."""
        settings = MCPSettings(name="Test")
        repr_str = repr(settings)
        assert "MCPSettings" in repr_str
        assert "name: Test" in repr_str

    def test_get_fastmcp_kwargs(self):
        """Test the get_fastmcp_kwargs method."""
        settings = MCPSettings(name="TestMCP", version="1.0", on_duplicate="error")
        kwargs = settings.get_fastmcp_kwargs()
        assert kwargs["name"] == "TestMCP"
        assert kwargs["version"] == "1.0"
        assert kwargs["on_duplicate"] == "error"
        assert "api_prefix" not in kwargs

    def test_list_page_size_defaults_none(self):
        """list_page_size defaults to None and is excluded from fastmcp kwargs."""
        settings = MCPSettings()
        assert settings.list_page_size is None
        assert "list_page_size" not in settings.get_fastmcp_kwargs()

    def test_list_page_size_in_fastmcp_kwargs(self):
        """When set, list_page_size is passed through to FastMCP constructor kwargs."""
        settings = MCPSettings(list_page_size=50)
        kwargs = settings.get_fastmcp_kwargs()
        assert kwargs["list_page_size"] == 50

    def test_get_http_run_kwargs(self):
        """Test the get_http_run_kwargs method."""
        settings = MCPSettings(uvicorn_config={"host": "0.0.0.0", "port": 9000})  # noqa: S104
        kwargs = settings.get_http_run_kwargs()
        assert kwargs["uvicorn_config"]["host"] == "0.0.0.0"  # noqa: S104
        assert kwargs["uvicorn_config"]["port"] == 9000

    def test_get_http_run_kwargs_without_uvicorn_config(self):
        """No uvicorn config yields no HTTP run arguments."""
        assert MCPSettings(uvicorn_config=None).get_http_run_kwargs() == {}

    def test_get_httpx_kwargs(self):
        """Test the get_httpx_kwargs method."""
        settings = MCPSettings(httpx_client_kwargs={"timeout": 120})
        kwargs = settings.get_httpx_kwargs()
        assert kwargs["timeout"] == 120

    def test_update_settings(self):
        """Test updating settings from another MCPSettings instance."""
        settings1 = MCPSettings(name="Initial")
        settings2 = MCPSettings(name="Updated", describe_responses=True)
        settings1.update(settings2)
        assert settings1.name == "Updated"
        assert settings1.describe_responses is True

    def test_validate_json_or_tuple_blank_string_returns_none(self):
        """A blank ``server_auth`` string normalizes to None."""
        settings = MCPSettings(server_auth="   ")
        assert settings.server_auth is None

    def test_validate_json_or_tuple_parses_json_list(self):
        """A JSON-shaped ``server_auth`` string is decoded to a tuple."""
        settings = MCPSettings(server_auth='["user", "pass"]')
        assert settings.server_auth == ("user", "pass")

    def test_validate_json_or_tuple_passthrough_for_invalid_json(self):
        """Invalid JSON falls through to the raw string and fails tuple coercion."""
        with pytest.raises(ValidationError):
            MCPSettings(server_auth="not-json")

    def test_get_httpx_kwargs_attaches_client_auth(self):
        """``client_auth`` is returned under ``auth`` without mutating the settings."""
        settings = MCPSettings(
            client_auth=("u", "p"), httpx_client_kwargs={"timeout": 5}
        )
        assert settings.get_httpx_kwargs() == {"timeout": 5, "auth": ("u", "p")}
        assert settings.httpx_client_kwargs == {"timeout": 5}

    def test_skills_reload_default_is_false(self):
        """skills_reload defaults to False."""
        assert MCPSettings().skills_reload is False

    def test_skills_providers_default_is_none(self):
        """skills_providers defaults to None."""
        assert MCPSettings().skills_providers is None

    def test_skills_providers_comma_separated_env_var(self):
        """skills_providers accepts comma-separated strings (env var simulation)."""
        settings = MCPSettings(skills_providers="claude,cursor")
        assert settings.skills_providers == ["claude", "cursor"]
