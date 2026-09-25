"""``openbb-mcp`` entry point."""

from __future__ import annotations

import sys


def main() -> None:
    """Launch the OpenBB MCP server."""

    if any(flag in sys.argv[1:] for flag in ("--help", "-h")):
        from openbb_mcp_server.app.args import LAUNCH_SCRIPT_DESCRIPTION

        print(LAUNCH_SCRIPT_DESCRIPTION)  # noqa: T201
        sys.exit(0)

    from openbb_mcp_server.app.config import bootstrap_launcher_config

    bootstrap_launcher_config()

    from openbb_mcp_server.app.app import launch_mcp

    launch_mcp()


if __name__ == "__main__":  # pragma: no cover
    main()
