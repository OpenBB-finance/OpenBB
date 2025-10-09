"""Unit tests for MCPService."""

# flake8: noqa=W0621
# pylint: disable=W0621,W0212

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.service.mcp_service import MCPService


@pytest.fixture
def service(tmp_path):
    """Fixture for a clean MCPService instance with a temporary config file."""
    # Use a temporary path for the config file to avoid side effects
    config_path = tmp_path / "mcp_settings.json"

    # Patch the class attribute to point to our temporary file
    with patch.object(MCPService, "MCP_SETTINGS_PATH", config_path):
        # Clear any existing singleton instances
        MCPService._instances.pop(MCPService, None)  # type: ignore

        service = MCPService()
        yield service

        # Clean up after the test
        MCPService._instances.pop(MCPService, None)  # type: ignore
        if config_path.exists():
            config_path.unlink()


def test_mcp_settings_path(service: MCPService):
    """Test the MCP_SETTINGS_PATH class attribute."""
    assert isinstance(service.MCP_SETTINGS_PATH, Path)
    assert service.MCP_SETTINGS_PATH.name == "mcp_settings.json"


def test_mcp_service_init_with_existing_file(service: MCPService):
    """Test MCPService initialization when config file exists."""
    # Setup: Create a dummy config file
    config_path = service.MCP_SETTINGS_PATH
    config_path.write_text(json.dumps({"name": "Test from file"}))

    # Action: Re-initialize the service to load from the file
    service.refresh_mcp_settings()

    # Assert
    assert isinstance(service.mcp_settings, MCPSettings)
    assert service.mcp_settings.name == "Test from file"


def test_mcp_service_init_with_corrupted_file(service: MCPService):
    """Test MCPService initialization with a corrupted config file."""
    # Setup: Create a corrupted JSON file
    config_path = service.MCP_SETTINGS_PATH
    config_path.write_text("this is not json")

    # Action: Re-initialize the service
    with patch("logging.warning") as mock_warning:
        service.refresh_mcp_settings()

        # Assert
        assert service.mcp_settings.name == "OpenBB MCP"  # Falls back to default
        mock_warning.assert_called_once()


def test_mcp_service_init_no_file(service: MCPService):
    """Test MCPService initialization when no config file exists."""
    assert isinstance(service.mcp_settings, MCPSettings)
    # Should load with default values from the model
    assert service.mcp_settings.name == "OpenBB MCP"
    assert service.MCP_SETTINGS_PATH.exists()


def test_write_to_file(service: MCPService):
    """Test the write_to_file class method."""
    settings = MCPSettings(name="Test to save")  # type: ignore
    service.write_to_file(settings)

    config_path = service.MCP_SETTINGS_PATH
    assert config_path.exists()
    with config_path.open("r", encoding="utf-8") as f:
        written_data = json.load(f)

    expected_data = settings.model_dump(mode="json")
    assert written_data["name"] == expected_data["name"]


def test_mcp_settings_setter(service: MCPService):
    """Test the setter for mcp_settings property automatically saves changes."""
    new_settings = MCPSettings(name="New settings")  # type: ignore

    with patch.object(service, "write_to_file") as mock_write:
        service.mcp_settings = new_settings
        assert service.mcp_settings == new_settings
        mock_write.assert_called_once_with(new_settings)


def test_load_settings_from_env(service: MCPService):
    """Test loading settings from environment variables."""
    env_dict = {
        "OPENBB_MCP_NAME": "Env Test",
        "OPENBB_MCP_DEFAULT_TOOL_CATEGORIES": "cat1,cat2",
    }
    with patch.dict("os.environ", env_dict, clear=True):
        env_settings = service._load_settings_from_env()
        assert env_settings["name"] == "Env Test"
        assert env_settings["default_tool_categories"] == ["cat1", "cat2"]


def test_load_settings_from_env_empty(service: MCPService):
    """Test loading from empty environment."""
    with patch.dict("os.environ", {}, clear=True):
        assert service._load_settings_from_env() == {}


def test_load_with_overrides(service: MCPService):
    """Test the priority of settings overrides (CLI > env > file)."""
    # Setup: Create a dummy config file
    config_path = service.MCP_SETTINGS_PATH
    config_path.write_text(json.dumps({"name": "File Settings", "version": "1.0"}))
    service.refresh_mcp_settings()

    # Env settings
    env_dict = {
        "OPENBB_MCP_NAME": "Env Settings",
        "OPENBB_MCP_VERSION": "2.0",
    }
    with patch.dict("os.environ", env_dict, clear=True):
        # CLI overrides
        cli_overrides = {"name": "CLI Settings"}

        # Execute
        final_settings = service.load_with_overrides(**cli_overrides)

    # Assert
    assert isinstance(final_settings, MCPSettings)
    assert final_settings.name == "CLI Settings"  # CLI > Env > File
    assert final_settings.version == "2.0"  # Env > File
    assert service.mcp_settings.name == "CLI Settings"  # Service state is updated


def test_map_cli_args_to_settings(service: MCPService):
    """Test the mapping of CLI arguments to settings fields."""
    server_kwargs = {
        "host": "10.10.10.10",
        "port": 9000,
        "allowed_categories": "stocks,crypto",
        "no_tool_discovery": True,
        "httpx_timeout": 30,
        "unknown_param": "some_value",
    }

    mapped = service._map_cli_args_to_settings(server_kwargs)

    assert mapped["uvicorn_config"]["host"] == "10.10.10.10"
    assert mapped["uvicorn_config"]["port"] == 9000
    assert mapped["allowed_tool_categories"] == "stocks,crypto"
    assert mapped["enable_tool_discovery"] is False
    assert mapped["httpx_client_kwargs"]["timeout"] == 30
    assert mapped["uvicorn_config"]["unknown_param"] == "some_value"


def test_map_cli_args_to_settings_system_prompt(service: MCPService):
    """Test mapping of system-prompt CLI argument."""
    server_kwargs = {"system_prompt": "/path/to/prompt.txt"}
    mapped = service._map_cli_args_to_settings(server_kwargs)
    assert mapped["system_prompt_file"] == "/path/to/prompt.txt"
