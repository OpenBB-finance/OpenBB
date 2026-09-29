"""FastAPI app bootstrapping helpers for ``openbb-mcp``."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI


def import_app(app_path: str, name: str = "app", factory: bool = False) -> FastAPI:
    """Import a user-defined FastAPI app from a path / module spec."""

    from importlib import import_module, util

    def _is_module_colon_notation(app_path: str) -> bool:
        """Tell colon-as-name from colon-as-Windows-drive."""
        if ":" not in app_path:
            return False
        if len(app_path) >= 2 and app_path[1] == ":" and app_path[0].isalpha():
            parts = app_path.split(":")
            return len(parts) > 2
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
