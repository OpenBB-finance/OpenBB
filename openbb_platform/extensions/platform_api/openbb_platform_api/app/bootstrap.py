"""FastAPI app bootstrapping helpers.

* ``import_app`` — load a user-supplied FastAPI app from a file path,
  module path, or factory function. Used by the ``--app`` launcher flag
  to swap in a custom app while preserving the launcher's middleware /
  exception-handler wiring.
* ``check_for_platform_extensions`` — detect installed data-processing
  extensions (econometrics, quantitative, technical) and add their
  routes to the widget exclude filter so they don't pollute the
  Workspace widget catalogue.
* ``apply_cors_from_system_service`` — install ``CORSMiddleware`` on
  the FastAPI app using the origins/methods/headers configured on
  ``SystemService.system_settings.api_settings.cors``. Idempotent —
  skips installation when ``CORSMiddleware`` is already in the
  middleware stack so the launcher can call it unconditionally
  regardless of which path produced the app instance.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI


def apply_cors_from_system_service(app: FastAPI) -> bool:
    """Add ``CORSMiddleware`` to ``app`` from SystemService settings.

    Without this, OPTIONS preflight requests from a browser hit the
    actual route (which only allows GET/POST) and return ``405 Method
    Not Allowed`` — Workspace shows the widget as broken.

    Idempotent: returns ``True`` when the middleware was added,
    ``False`` when it was already present (e.g. ``rest_api`` already
    installed it on the default app, or a user-supplied app brought
    its own CORS configuration).
    """
    from fastapi.middleware.cors import CORSMiddleware
    from openbb_core.app.service.system_service import SystemService

    if any(getattr(m, "cls", None) is CORSMiddleware for m in app.user_middleware):
        return False

    cors = SystemService().system_settings.api_settings.cors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors.allow_origins,
        allow_methods=cors.allow_methods,
        allow_headers=cors.allow_headers,
    )
    return True


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

    Wires CORS + OpenBB exception handlers into the imported app so
    the launcher's standard middleware applies regardless of which
    app the user pointed at.

    Raises ``FileNotFoundError`` / ``AttributeError`` / ``TypeError``
    on import / lookup / shape mismatches.
    """

    from importlib import import_module, util

    from fastapi.exceptions import ResponseValidationError

    # Decoupled from ``openbb_core.api.rest_api`` and
    # ``openbb_core.api.app_loader`` on purpose: those modules pull in
    # ``RouterLoader`` / ``ExtensionLoader``, which discover and mount
    # every installed extension. The user supplied their own app via
    # ``--app`` precisely to avoid that machinery, so we go directly
    # to the lightweight pieces (CORS + exception handler functions)
    # without booting the default app.
    from openbb_core.api.exception_handlers import ExceptionHandlers
    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.provider.utils.errors import (
        EmptyDataError,
        UnauthorizedError,
    )
    from pydantic import ValidationError

    def _is_module_colon_notation(app_path: str) -> bool:
        """Tell colon-as-name from colon-as-Windows-drive."""
        if ":" not in app_path:
            return False
        # Windows absolute path check (e.g., C:\path or D:/path)
        if len(app_path) >= 2 and app_path[1] == ":" and app_path[0].isalpha():
            # Could still have colon notation: C:\path\file.py:app
            parts = app_path.split(":")
            return len(parts) > 2  # More than just drive letter colon
        return True

    def _load_module_from_file_path(file_path: str):
        spec_name = os.path.basename(file_path).split(".")[0]
        spec = util.spec_from_file_location(spec_name, file_path)

        if spec is None or spec.loader is None:
            # ``spec_from_file_location`` returns None for unloadable
            # paths; the loader can be None when the spec is a
            # namespace package or otherwise un-execable. Either way
            # we can't run the module, so surface a clear error.
            raise RuntimeError(f"Failed to load the file specs for '{file_path}'")

        module = util.module_from_spec(spec)
        sys.modules[spec_name] = module
        spec.loader.exec_module(module)
        return module

    if _is_module_colon_notation(app_path):
        module_path, name = app_path.rsplit(":", 1)
        try:  # First try to import as a module
            module = import_module(module_path)
        except ImportError:  # If module import fails, try to load as a local file
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

    # Bare file path (e.g., "main.py" or "my_app/main.py")
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

    # Mirror uvicorn's factory detection: if the attribute is callable,
    # invoke it; if the user didn't pass --factory but it works, soft-
    # warn rather than failing.
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

    apply_cors_from_system_service(app)

    # Inlined from ``AppLoader.add_exception_handlers`` so this code path
    # avoids importing ``openbb_core.api.app_loader`` (which transitively
    # pulls in ``RouterLoader`` / ``ExtensionLoader``).
    app.exception_handlers[Exception] = ExceptionHandlers.exception
    app.exception_handlers[ValidationError] = ExceptionHandlers.validation
    app.exception_handlers[ResponseValidationError] = ExceptionHandlers.validation
    app.exception_handlers[OpenBBError] = ExceptionHandlers.openbb
    app.exception_handlers[EmptyDataError] = ExceptionHandlers.empty_data
    app.exception_handlers[UnauthorizedError] = ExceptionHandlers.unauthorized

    return app


def check_for_platform_extensions(
    fastapi_app: FastAPI, widgets_to_exclude: list
) -> list:
    """Add data-processing-extension routes to the widget exclude filter.

    ``econometrics`` / ``quantitative`` / ``technical`` are utility
    extensions that operate on already-fetched data; they don't make
    sense as Workspace widgets. When the launcher detects any of them
    loaded into the FastAPI app's tags, it adds their route prefix
    (``/api/v1/<tag>/*``) to the exclude filter so those endpoints
    don't sprout widgets in the catalogue.
    """

    from openbb_core.app.service.system_service import SystemService

    to_check_for = ["econometrics", "quantitative", "technical"]
    openapi_tags = fastapi_app.openapi_tags or []
    tags: list = []
    for tag in openapi_tags:
        if any(mod in tag.get("name", "") for mod in to_check_for):
            tags.append(tag.get("name", ""))

    if tags and (any(f"openbb_{mod}" in sys.modules for mod in to_check_for)):
        api_prefix = SystemService().system_settings.api_settings.prefix
        for tag in tags:
            if f"openbb_{tag}" in sys.modules:
                # If the module is loaded, we can safely add it to the exclude filter.
                widgets_to_exclude.append(f"{api_prefix}/{tag}/*")

    return widgets_to_exclude
