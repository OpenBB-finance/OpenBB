"""Tests for the MCP server."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from openbb_core.api.rest_api import app
from openbb_core.app.model.mcp_settings import MCPSettings
from openbb_mcp_server.main import mount_mcp_server


def test_get_available_tool_categories():
    """Test getting available tool categories."""
    settings = MCPSettings()
    mount_mcp_server(app, settings)

    client = TestClient(app)
    response = client.get("/mcp/available_tool_categories")
    assert response.status_code == 200

    data = response.json()
    assert "available_tool_categories" in data
    assert "active_tool_categories" in data
    assert "available_providers" in data
    assert isinstance(data["available_tool_categories"], list)
    assert isinstance(data["active_tool_categories"], list)
    assert isinstance(data["available_providers"], list)
    assert data["active_tool_categories"] == settings.default_tool_categories


def test_get_available_tools():
    """Test getting available tools for active categories."""
    settings = MCPSettings()
    mount_mcp_server(app, settings)

    client = TestClient(app)
    response = client.get("/mcp/available_tools")
    assert response.status_code == 200

    data = response.json()
    assert "active_tool_categories" in data
    assert "available_tools" in data
    assert "active_tools" in data
    assert "total_available_tools" in data
    assert "total_active_tools" in data
    assert isinstance(data["available_tools"], dict)
    assert isinstance(data["total_available_tools"], int)
    assert data["active_tool_categories"] == settings.default_tool_categories

    # Each category should have a list of tools
    for category in data["active_tool_categories"]:
        assert category in data["available_tools"]
        assert isinstance(data["available_tools"][category], list)


def test_activate_tool_categories():
    """Test activating tool categories."""
    settings = MCPSettings(allowed_tool_categories=["equity", "news"])
    mount_mcp_server(app, settings)

    client = TestClient(app)

    # Test valid categories
    response = client.post(
        "/mcp/activate_tool_categories", params={"categories": ["equity"]}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["active_tool_categories"] == ["equity"]

    # Test invalid categories
    response = client.post(
        "/mcp/activate_tool_categories", params={"categories": ["invalid"]}
    )
    assert response.status_code == 422


def test_activate_tools():
    """Test activating specific tools."""
    settings = MCPSettings()
    mount_mcp_server(app, settings)

    client = TestClient(app)

    # Get current tools
    response = client.get("/mcp/available_tools")
    assert response.status_code == 200
    available_tools = []
    for tools in response.json()["available_tools"].values():
        available_tools.extend(tools)

    if available_tools:
        # Try to activate specific tools
        tools = list(settings.required_tools)
        tools.append(available_tools[0])
        response = client.post("/mcp/activate_tools", params={"tools": tools})
        assert response.status_code == 200


@patch("openbb_mcp_server.main.ProviderInterface")
def test_provider_filtering(mock_provider_interface):
    """Test provider filtering functionality."""
    # Mock provider interface
    mock_provider_instance = MagicMock()
    mock_provider_instance.available_providers = ["yfinance", "fmp", "polygon"]
    mock_provider_interface.return_value = mock_provider_instance

    settings = MCPSettings(
        allowed_providers=["yfinance", "fmp"],
        require_valid_credentials=False,
    )
    mount_mcp_server(app, settings)

    client = TestClient(app)
    response = client.get("/mcp/available_tool_categories")
    assert response.status_code == 200

    data = response.json()
    assert "available_providers" in data


@patch("openbb_mcp_server.main.Container")
@patch("openbb_mcp_server.main.ProviderInterface")
def test_credential_validation(mock_provider_interface, mock_container):
    """Test provider filtering with credential validation."""
    # Mock provider interface
    mock_provider_instance = MagicMock()
    mock_provider_instance.available_providers = ["yfinance", "fmp", "polygon"]
    mock_provider_interface.return_value = mock_provider_instance

    # Mock container's credential check
    mock_container_instance = MagicMock()

    def check_credentials(provider):
        valid_providers = {"yfinance": None, "fmp": False, "polygon": True}
        return valid_providers.get(provider, False)

    mock_container_instance._check_credentials.side_effect = check_credentials
    mock_container.return_value = mock_container_instance

    settings = MCPSettings(
        allowed_providers=["yfinance", "fmp", "polygon"],
        require_valid_credentials=True,
    )
    mount_mcp_server(app, settings)

    client = TestClient(app)
    response = client.get("/mcp/available_tool_categories")
    assert response.status_code == 200

    data = response.json()
    assert "available_providers" in data
    # Should include yfinance (no creds needed) and polygon (valid creds)
    assert set(data["available_providers"]) == {"yfinance", "polygon"}


def test_custom_settings():
    """Test server with custom settings."""
    settings = MCPSettings(
        name="Test MCP",
        description="Test Server",
        default_tool_categories=["equity"],
        allowed_tool_categories=["equity", "news"],
        require_valid_credentials=False,
    )
    mount_mcp_server(app, settings)

    client = TestClient(app)
    response = client.get("/mcp/available_tool_categories")
    assert response.status_code == 200

    data = response.json()
    assert data["active_tool_categories"] == ["equity"]
    assert data["available_tool_categories"] == ["equity", "news"]
