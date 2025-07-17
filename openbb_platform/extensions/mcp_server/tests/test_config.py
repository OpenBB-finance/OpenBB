"""Unit tests for config utilities."""

import json
import sys
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from openbb_mcp_server.utils.config import (
    get_mcp_config_path,
    load_mcp_settings,
    load_mcp_settings_with_overrides,
    load_settings_from_env,
    parse_args,
    save_mcp_settings,
)
from openbb_mcp_server.utils.settings import MCPSettings

# Skip all tests if Python version < 3.10
if sys.version_info < (3, 10):
    pytest.skip("MCP server requires Python 3.10+", allow_module_level=True)


def test_get_mcp_config_path():
    path = get_mcp_config_path()
    assert isinstance(path, Path)
    assert path.name == "mcp_settings.json"


@patch("pathlib.Path.exists")
@patch("builtins.open", new_callable=mock_open)
def test_load_mcp_settings_existing(mock_file, mock_exists):
    mock_exists.return_value = True
    mock_file.return_value.read.return_value = json.dumps(
        {"name": "Test", "description": "Test desc"}
    )

    settings = load_mcp_settings()
    assert isinstance(settings, MCPSettings)
    assert settings.name == "Test"
    assert settings.description == "Test desc"


@patch("pathlib.Path.exists", return_value=False)
@patch("builtins.open", new_callable=mock_open)
@patch("openbb_mcp_server.utils.config.save_mcp_settings")
def test_load_mcp_settings_create_default(mock_save, _mock_file, _mock_exists):
    settings = load_mcp_settings()
    assert isinstance(settings, MCPSettings)
    mock_save.assert_called_once_with(settings)


@patch("builtins.open", new_callable=mock_open)
def test_save_mcp_settings(mock_file):
    settings = MCPSettings(name="Test")
    save_mcp_settings(settings)
    mock_file.assert_called_once()
    handle = mock_file()
    written = "".join(call.args[0] for call in handle.write.call_args_list)
    expected = json.dumps(settings.model_dump(), indent=2)
    assert written == expected


@patch("os.environ")
def test_load_settings_from_env(mock_env):
    env_dict = {
        "OPENBB_MCP_NAME": "Env Test",
        "OPENBB_MCP_DEFAULT_TOOL_CATEGORIES": "cat1,cat2",
    }
    mock_env.__getitem__.side_effect = lambda k: env_dict.get(k)
    mock_env.__contains__.side_effect = lambda k: k in env_dict

    env_settings = load_settings_from_env()
    assert env_settings["name"] == "Env Test"
    assert env_settings["default_tool_categories"] == ["cat1", "cat2"]


def test_load_settings_from_env_empty():
    with patch("os.environ", {}):
        assert load_settings_from_env() == {}


@patch("openbb_mcp_server.utils.config.load_mcp_settings")
@patch("openbb_mcp_server.utils.config.load_settings_from_env")
def test_load_mcp_settings_with_overrides(mock_env, mock_load):
    mock_load.return_value = MCPSettings(name="File")
    mock_env.return_value = {"name": "Env"}

    settings = load_mcp_settings_with_overrides(name="Override")
    assert settings.name == "Override"


@patch("sys.argv", ["script.py", "--host", "127.0.0.1", "--port", "9999"])
def test_parse_args():
    args = parse_args()
    assert args.host == "127.0.0.1"
    assert args.port == 9999
    assert not args.no_tool_discovery


@patch("sys.argv", ["script.py", "--help"])
def test_parse_args_help(capsys):
    with pytest.raises(SystemExit):
        parse_args()
    captured = capsys.readouterr()
    assert "usage:" in captured.out
