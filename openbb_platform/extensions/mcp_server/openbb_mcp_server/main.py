"""``openbb-mcp`` entry point.

Two-phase bootstrap so the layered TOML cascade (and the ``[env]``
table) lands BEFORE any heavy import:

1. ``bootstrap_launcher_config`` — runs the cascade, applies
   ``[env]`` keys to ``os.environ``. Touches only stdlib + the
   core's lightweight loader; safe to call before any
   ``openbb_core`` / ``fastmcp`` import.
2. Import + run the heavy ``openbb_mcp_server.app.app`` module
   surface, which transitively pulls in ``openbb_core.api.rest_api``,
   ``fastmcp``, ``uvicorn``, etc.

The split is what lets ``[env]`` entries influence the very first
``openbb_core.*`` module load — no race between env injection and
module-time ``Env()`` reads.
"""

from __future__ import annotations

import sys


def main() -> None:
    """Launch the OpenBB MCP server."""

    # Quick ``--help`` short-circuit so ``openbb-mcp --help`` stays
    # stdlib-only at module scope (no openbb_core / fastmcp boot).
    if any(flag in sys.argv[1:] for flag in ("--help", "-h")):
        from openbb_mcp_server.app.args import LAUNCH_SCRIPT_DESCRIPTION

        print(LAUNCH_SCRIPT_DESCRIPTION)  # noqa: T201
        sys.exit(0)

    from openbb_mcp_server.app.config import bootstrap_launcher_config

    bootstrap_launcher_config()

    from openbb_mcp_server.app.app import launch_mcp

    launch_mcp()


if __name__ == "__main__":  # pragma: no cover — script entry
    main()
