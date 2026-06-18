"""FastAPI app bootstrapping helpers for ``openbb-mcp``.

* ``import_app`` — load a user-supplied FastAPI app from a file path,
  module path, or factory function. Used by the ``--app`` launcher
  flag to swap in a custom app whose routes the MCP server will
  expose as tools.

The MCP server uses the imported FastAPI app only as a route source —
it isn't served over HTTP, so the platform-api's CORS / exception-
handler wiring isn't needed here. The MCP transport layer
(``streamable-http`` / ``sse`` / ``stdio``) brings its own middleware.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI


def import_app(app_path: str, name: str = "app", factory: bool = False) -> FastAPI:
    """Import a user-defined FastAPI app from a path / module spec.

    ``app_path`` accepts three forms:

    * Module-colon notation — ``my.module:app`` or
      ``./my_file.py:app``. The text after ``:`` overrides ``name``.
    * Bare file path — ``./my_app/main.py`` (relative or absolute).
      Falls back to a ``spec_from_file_location`` import.
    * Bare module path — ``my.module``. Goes through ``import_module``.

    ``factory=True`` calls the resulting attribute and uses its return
    value as the app instance; the launcher prints a soft-warning and
    invokes the factory anyway when it detects callability without the
    flag set, matching uvicorn's behavior.

    Raises ``FileNotFoundError`` / ``AttributeError`` / ``TypeError``
    on import / lookup / shape mismatches.
    """

    from importlib import import_module, util

    def _is_module_colon_notation(app_path: str) -> bool:
        """Tell colon-as-name from colon-as-Windows-drive."""
        if ":" not in app_path:
            return False
        # Windows absolute path check (e.g., C:\path or D:/path)
        if len(app_path) >= 2 and app_path[1] == ":" and app_path[0].isalpha():
            parts = app_path.split(":")
            return len(parts) > 2  # More than just drive letter colon
        return True

    def _load_module_from_file_path(file_path: str):
        spec_name = os.path.basename(file_path).split(".")[0]
        spec = util.spec_from_file_location(spec_name, file_path)

        if spec is None or spec.loader is None:
            raise RuntimeError(f"Failed to load the file specs for '{file_path}'")

        module = util.module_from_spec(spec)
        sys.modules[spec_name] = module
        spec.loader.exec_module(module)
        return module

    if _is_module_colon_notation(app_path):
        module_path, name = app_path.rsplit(":", 1)
        try:
            module = import_module(module_path)
        except ImportError:
            if not module_path.endswith(".py"):
                module_path += ".py"

            if not Path(module_path).is_absolute():
                cwd = Path.cwd()
                file_path = str(cwd.joinpath(module_path).resolve())
            else:
                file_path = module_path

            if not Path(file_path).exists():
                raise FileNotFoundError(
                    f"Error: Neither module '{module_path}' could be imported nor file '{file_path}' exists"
                )

            module = _load_module_from_file_path(file_path)

    else:
        if not Path(app_path).is_absolute():
            cwd = Path.cwd()
            app_path = str(cwd.joinpath(app_path).resolve())

        if not Path(app_path).exists():
            raise FileNotFoundError(f"Error: The app file '{app_path}' does not exist")

        module = _load_module_from_file_path(app_path)

    if not hasattr(module, name):
        raise AttributeError(
            f"Error: The app file '{app_path}' does not contain an '{name}' instance"
        )

    app_or_factory = getattr(module, name)

    try:
        app = app_or_factory()
        if not factory:
            print(  # noqa: T201
                "\n\n[WARNING]   "
                "App factory detected. Using it, but please consider setting the --factory flag explicitly.\n"
            )
    except TypeError:
        if factory:
            raise TypeError(
                f"Error: The {name} instance in '{app_path}' appears not to be a callable factory function"
            )
        app = app_or_factory

    if not isinstance(app, FastAPI):
        raise TypeError(
            f"Error: The {name} instance in '{app_path}' is not an instance of FastAPI"
        )

    return app
