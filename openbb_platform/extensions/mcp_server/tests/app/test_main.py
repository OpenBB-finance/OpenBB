"""Tests for ``openbb_mcp_server.main``."""

import sys
from unittest.mock import patch

import pytest


def test_main_help_short_circuits(capsys):
    """``--help`` exits 0 before any heavy import runs."""
    from openbb_mcp_server import main as main_mod

    with patch.object(sys, "argv", ["openbb-mcp", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            main_mod.main()
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "openbb-mcp" in out.lower() or "MCP" in out


def test_main_dash_h_short_circuits(capsys):
    """``-h`` matches ``--help`` behavior."""
    from openbb_mcp_server import main as main_mod

    with patch.object(sys, "argv", ["openbb-mcp", "-h"]):
        with pytest.raises(SystemExit) as excinfo:
            main_mod.main()
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "MCP" in captured.out or "openbb-mcp" in captured.out.lower()


def test_main_runs_bootstrap_then_launch():
    """Non-help main() chains bootstrap_launcher_config → launch_mcp."""
    from openbb_mcp_server import main as main_mod

    with (
        patch.object(sys, "argv", ["openbb-mcp"]),
        patch("openbb_mcp_server.app.config.bootstrap_launcher_config") as mock_boot,
        patch("openbb_mcp_server.app.app.launch_mcp") as mock_launch,
    ):
        main_mod.main()

    mock_boot.assert_called_once()
    mock_launch.assert_called_once()


def test_main_help_uses_args_module_constant(capsys):
    """``--help`` output is the constant from ``app.args``."""
    from openbb_mcp_server import main as main_mod
    from openbb_mcp_server.app.args import LAUNCH_SCRIPT_DESCRIPTION

    with patch.object(sys, "argv", ["openbb-mcp", "--help"]):
        with pytest.raises(SystemExit):
            main_mod.main()

    out = capsys.readouterr().out
    assert "openbb.toml" in out
    assert LAUNCH_SCRIPT_DESCRIPTION.strip() in out


def test_back_compat_main_alias_in_app_app():
    """Legacy ``openbb_mcp_server.app.app:main`` forwards to the new entry."""
    from openbb_mcp_server.app import app as app_mod

    with (
        patch.object(sys, "argv", ["openbb-mcp"]),
        patch("openbb_mcp_server.main.main") as mock_main,
    ):
        app_mod.main()
    mock_main.assert_called_once()
