"""Unit tests for MCPSettings model."""

from openbb_mcp_server.utils.settings import MCPSettings


def test_mcp_settings_defaults():
    settings = MCPSettings()
    assert settings.name == "OpenBB MCP"
    assert settings.default_tool_categories == ["all"]
    assert settings.allowed_tool_categories is None
    assert settings.enable_tool_discovery is True
    assert settings.describe_responses is False


def test_mcp_settings_validation():
    settings = MCPSettings(
        default_tool_categories="cat1,cat2", allowed_tool_categories="cat3"
    )
    assert settings.default_tool_categories == ["cat1", "cat2"]
    assert settings.allowed_tool_categories == ["cat3"]


def test_mcp_settings_repr():
    settings = MCPSettings(name="Test")
    repr_str = repr(settings)
    assert "MCPSettings" in repr_str
    assert "name: Test" in repr_str
