"""Standalone launcher and cache manager for the OpenBB SEC provider.

``openbb-sec`` resolves the SEC disk-cache folder — from, highest priority
first, the ``--cache-dir`` argument, the ``OPENBB_SEC_CACHE_DIR`` environment
variable, the ``cache_directory`` preference discovered from openbb.toml / user
settings, then the OpenBB default — and serves the provider as a self-contained
OpenBB Workspace backend by delegating to ``openbb-api`` with a SEC app factory.

Commands
--------
serve (default)
    Launch the SEC backend (``openbb-api --app openbb_sec.cli:create_app
    --factory``), honoring ``--host``, ``--port`` and ``--reload``.
info
    Print the resolved cache folder, size limit and disk usage.
path
    Print the resolved cache folder.
clear
    Empty the cache.
"""

import argparse
import os
import sys

from openbb_sec.utils import cache

_APP_FACTORY = "openbb_sec.cli:create_app"


def _abs(path: str) -> str:
    """Return an absolute, user-expanded path."""
    return os.path.abspath(os.path.expanduser(path))


def resolve_cache_directory(
    cache_dir: "str | None" = None, *, discover: bool = True
) -> str:
    """Resolve the SEC cache folder from arg, env var, openbb.toml, or default.

    Parameters
    ----------
    cache_dir : str | None
        An explicit folder from the command line; wins when provided.
    discover : bool
        When True, load the layered openbb-core config (``.env`` files and
        openbb.toml) so the resolved folder reflects those layers.

    Returns
    -------
    str
        The absolute SEC cache folder.
    """
    if cache_dir:
        return _abs(cache_dir)
    if discover:
        from openbb_core.app.config.loader import load_layered_config

        load_layered_config()
    override = os.environ.get(cache.CACHE_DIR_ENV_VAR)
    if override:
        return _abs(override)
    from openbb_core.app.service.user_service import UserService

    parent = UserService().default_user_settings.preferences.cache_directory
    return os.path.join(_abs(parent), "sec")


def create_app():
    """Build the SEC-focused FastAPI app (factory for ``openbb-api --app``).

    Mounts the OpenBB REST app and serves the SEC ``widgets.json`` / ``apps.json``
    at the backend root so the OpenBB Workspace discovers the SEC dashboards.
    """
    from fastapi.responses import JSONResponse
    from openbb_core.api.rest_api import app

    from openbb_sec import sec_router

    paths = {getattr(route, "path", "") for route in app.routes}
    headers = {"X-Backend-Type": "OpenBB Platform"}

    if "/widgets.json" not in paths:

        @app.get("/widgets.json", include_in_schema=False)
        async def _widgets_json():
            """Serve the SEC widgets.json at the backend root."""
            return JSONResponse(await sec_router.get_widgets_json(), headers=headers)

    if "/apps.json" not in paths:

        @app.get("/apps.json", include_in_schema=False)
        async def _apps_json():
            """Serve the SEC apps.json at the backend root."""
            return JSONResponse(await sec_router.get_apps_json(), headers=headers)

    return app


def _print_info(cache_dir: str) -> None:
    """Print the resolved cache folder, size limit and current disk usage."""
    print(f"SEC cache directory: {cache_dir}")
    print(f"Size limit:          {cache.get_size_limit():,} bytes")
    if not os.path.isdir(cache_dir):
        print("Disk usage:          (not created yet)")
        return
    total = 0
    for root, _dirs, files in os.walk(cache_dir):
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.isfile(file_path):
                total += os.path.getsize(file_path)
    print(f"Disk usage:          {total:,} bytes")


def serve(passthrough: "list[str]") -> int:
    """Launch the SEC backend through ``openbb-api`` with the SEC app factory."""
    import importlib.util
    import subprocess

    if importlib.util.find_spec("openbb_platform_api") is None:
        print(
            "openbb-api is required to serve. Install it with:"
            " pip install openbb-platform-api"
        )
        return 1

    command = [
        sys.executable,
        "-m",
        "openbb_platform_api.main",
        "--app",
        _APP_FACTORY,
        "--factory",
        *passthrough,
    ]
    return subprocess.run(command, check=False).returncode


def main(argv: "list[str] | None" = None) -> int:
    """Entry point for the ``openbb-sec`` console script."""
    parser = argparse.ArgumentParser(
        prog="openbb-sec",
        description="Serve the OpenBB SEC provider and manage its disk cache.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["serve", "info", "path", "clear"],
        default="serve",
        help="Action to run. Defaults to 'serve'.",
    )
    parser.add_argument(
        "-c", "--cache-dir", help="SEC cache folder. Overrides env var and config."
    )
    parser.add_argument("--host", help="Host to serve on. Defaults to 127.0.0.1.")
    parser.add_argument("--port", help="Port to serve on. Defaults to 6900.")
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload while serving."
    )
    args = parser.parse_args(argv)

    cache_dir = resolve_cache_directory(args.cache_dir)
    os.environ[cache.CACHE_DIR_ENV_VAR] = cache_dir

    if args.command == "path":
        print(cache_dir)
        return 0
    if args.command == "info":
        _print_info(cache_dir)
        return 0
    if args.command == "clear":
        print(f"Cleared {cache.clear_cache()} cache entries from {cache_dir}")
        return 0

    passthrough: list[str] = []
    if args.host:
        passthrough += ["--host", args.host]
    if args.port:
        passthrough += ["--port", str(args.port)]
    if args.reload:
        passthrough += ["--reload", "true"]
    return serve(passthrough)


if __name__ == "__main__":  # pragma: no cover - module CLI execution guard
    sys.exit(main())
