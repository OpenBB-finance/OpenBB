"""MCP server boot subpackage.

* ``args`` — command-line argument parsing for the ``openbb-mcp``
  launcher.
* ``bootstrap`` — pluggable FastAPI app loading (``import_app``).
* ``cli_tools`` — registers ``openbb-cli`` dispatcher tools when the
  optional ``[cli]`` extra is installed.
* ``config`` — layered TOML cascade + ``[env]`` injection bootstrap.
* ``middleware`` — auth + HTTP middleware hook resolver.
* ``spec`` — synthesize a FastAPI proxy app from an ``openbb-cli``
  generated ``.spec`` file.
* ``app`` — the launcher entry point. Holds ``create_mcp_server`` and
  ``launch_mcp``.

Each submodule is imported via ``import openbb_mcp_server.app.X`` —
that form binds ``X`` as an attribute on the package after the
submodule's body has finished, regardless of the parent package's
own initialization state. The earlier ``from openbb_mcp_server.app
import (X, ...)`` form tripped a partially-initialized-module
ImportError on CPython 3.13 because the from-import resolves
attributes against the in-progress package object before the
implicit submodule fallback runs.
"""

import openbb_mcp_server.app.args  # noqa: F401
import openbb_mcp_server.app.bootstrap  # noqa: F401
import openbb_mcp_server.app.cli_tools  # noqa: F401
import openbb_mcp_server.app.config  # noqa: F401
import openbb_mcp_server.app.middleware  # noqa: F401
import openbb_mcp_server.app.spec  # noqa: F401

__all__ = [
    "args",
    "bootstrap",
    "cli_tools",
    "config",
    "middleware",
    "spec",
]
