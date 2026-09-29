"""Tests for ``openbb_mcp_server.main``."""

import sys
from unittest.mock import patch

import pytest

from openbb_mcp_server import main as main_mod
from openbb_mcp_server.app.args import LAUNCH_SCRIPT_DESCRIPTION

pytestmark = pytest.mark.usefixtures("isolated_config")


class TestMain:
    """The ``openbb-mcp`` entry point."""

    @pytest.mark.parametrize("flag", ["--help", "-h"])
    def test_help_prints_description_and_exits(self, capsys, flag):
        """``--help`` and ``-h`` print the launcher description and exit 0."""
        with (
            patch.object(sys, "argv", ["openbb-mcp", "--port", "1", flag]),
            patch("openbb_mcp_server.app.config.bootstrap_launcher_config") as boot,
            pytest.raises(SystemExit) as excinfo,
        ):
            main_mod.main()
        assert excinfo.value.code == 0
        assert capsys.readouterr().out == LAUNCH_SCRIPT_DESCRIPTION + "\n"
        boot.assert_not_called()

    def test_main_runs_bootstrap_then_launch(self):
        """Non-help ``main()`` bootstraps the config before launching."""
        calls: list[str] = []
        with (
            patch.object(sys, "argv", ["openbb-mcp"]),
            patch(
                "openbb_mcp_server.app.config.bootstrap_launcher_config",
                side_effect=lambda: calls.append("bootstrap"),
            ),
            patch(
                "openbb_mcp_server.app.app.launch_mcp",
                side_effect=lambda: calls.append("launch"),
            ),
        ):
            main_mod.main()
        assert calls == ["bootstrap", "launch"]
