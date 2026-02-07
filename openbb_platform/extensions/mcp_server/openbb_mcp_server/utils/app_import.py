"""App import utilities for MCP Server."""

import json
import os
import sys
from pathlib import Path

from fastapi import FastAPI


def import_app(app_path: str, name: str = "app", factory: bool = False) -> FastAPI:
    """Import the FastAPI app instance from a local file or module."""
    # pylint: disable=import-outside-toplevel
    from importlib import import_module, util

    def _is_module_colon_notation(app_path: str) -> bool:
        """Check if the path uses module:name notation vs a Windows path."""
        if ":" not in app_path:
            return False
        # Windows absolute path check (e.g., C:\path or D:/path)
        if len(app_path) >= 2 and app_path[1] == ":" and app_path[0].isalpha():
            # Could still have colon notation: C:\path\file.py:app
            parts = app_path.split(":")
            return len(parts) > 2  # More than just drive letter colon
        return True

    def _load_module_from_file_path(file_path: str):
        """Load a Python module from a file path."""
        spec_name = os.path.basename(file_path).split(".")[0]
        spec = util.spec_from_file_location(spec_name, file_path)

        if spec is None:
            raise RuntimeError(f"Failed to load the file specs for '{file_path}'")

        module = util.module_from_spec(spec)  # type: ignore
        sys.modules[spec_name] = module  # type: ignore
        spec.loader.exec_module(module)  # type: ignore
        return module

    # Case 1: Module path with colon notation (e.g., "my_app.main:app" or "main:app")
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
                raise FileNotFoundError(  # pylint: disable=raise-missing-from
                    f"Error: Neither module '{module_path}' could be imported nor file '{file_path}' exists"
                )

            module = _load_module_from_file_path(file_path)

    # Case 2: File path (e.g., "main.py" or "my_app/main.py")
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

    # Here we use the same approach as uvicorn to handle factory functions.
    # This prevents us from relying on explicit type annotations.
    # See: https://github.com/encode/uvicorn/blob/master/uvicorn/config.py
    try:
        app = app_or_factory()
        if not factory:
            print(  # noqa: T201
                "\n\n[WARNING]   "
                "App factory detected. Using it, but please consider setting the --factory flag explicitly.\n"
            )
    except TypeError:
        if factory:
            raise TypeError(  # pylint: disable=raise-missing-from
                f"Error: The {name} instance in '{app_path}' appears not to be a callable factory function"
            )
        app = app_or_factory

    if not isinstance(app, FastAPI):
        raise TypeError(
            f"Error: The {name} instance in '{app_path}' is not an instance of FastAPI"
        )

    return app


cl_doc = """OpenBB MCP Server

Usage:
    >>> python -m openbb_mcp_server [OPTIONS]

    >>> openbb-mcp --app ./some_app.py --host 0.0.0.0 --port 8005

Description:
    The OpenBB MCP Server is a component of the OpenBB Platform that provides
    a server for the Model-Context-Protocol. REST endpoints are converted into
    tools and made available to connected clients.

    Settings can be defined in the configuration file, `~/.openbb_platform/mcp_settings.json`.

    Alternatively, they can be defined as environment variables, with key values prefaced with `OPENBB_MCP_`

Options:
    --help
        Show this help message and exit.

    --app <app_path>
        The path to the FastAPI app instance. This can be in the format
        'module.path:app_instance' or a file path 'path/to/app.py'.
        If not provided, the server will run with the default built-in app.

    --name <name>
        The name of the FastAPI app instance or factory function in the app file.
        Defaults to 'app'.

    --factory
        If set, the app is treated as a factory function that will be called
        to create the FastAPI app instance.

    --host <host>
        The host to bind the server to. Defaults to '127.0.0.1'.
        This is a uvicorn argument.

    --port <port>
        The port to bind the server to. Defaults to 8000.
        This is a uvicorn argument.

    --transport <transport>
        The transport mechanism to use for the MCP server.
        Defaults to 'streamable-http'.

    --allowed-categories <categories>
        A comma-separated list of tool categories to allow.
        If not provided, all categories are allowed.

    --default-categories <categories>
        A comma-separated list of tool categories to be enabled by default.
        Defaults to 'all'.

    --no-tool-discovery
        If set, tool discovery will be disabled.

    --system-prompt <path>
        Path to a TXT file with the system prompt.

    --server-prompts <path>
        Path to a JSON file with a list of server prompts.

All other arguments are passed through as MCPSettings.
"""


def parse_args():
    """Parse command line arguments."""
    # pylint: disable=import-outside-toplevel
    from openbb_core.env import Env

    _ = Env()

    args = sys.argv[1:].copy()
    _kwargs: dict = {}

    # Parse all command line arguments into kwargs
    for i, arg in enumerate(args):
        if arg == "--help":
            print(cl_doc)  # noqa: T201
            sys.exit(0)
        if arg.startswith("--"):
            key = arg[2:].replace("-", "_")
            if key in ["no_use_colors", "use_colors"]:
                _kwargs["use_colors"] = key == "use_colors"
            elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                if isinstance(value, str) and value.lower() in ["false", "true"]:
                    _kwargs[key] = value.lower() == "true"
                else:
                    try:
                        if (value.startswith("{") and value.endswith("}")) or (
                            value.startswith("[") and value.endswith("]")
                        ):
                            _kwargs[key] = json.loads(value)
                        elif (
                            key != "app"
                            and ":" in value
                            and all(":" in part for part in value.split(","))
                        ):
                            _kwargs[key] = {
                                k.strip(): v.strip()
                                for k, v in (p.split(":", 1) for p in value.split(","))
                            }
                        else:
                            _kwargs[key] = value
                    except (json.JSONDecodeError, ValueError):
                        _kwargs[key] = value
            else:
                _kwargs[key] = True

    # Extract and handle app import arguments
    _app_path = _kwargs.pop("app", None)
    _name = _kwargs.pop("name", "app")
    _factory = _kwargs.pop("factory", False)

    imported_app = None
    if _app_path:
        if ":" in _app_path:
            _app_instance_name = _app_path.split(":")[-1]
            _name = _app_instance_name if _app_instance_name else _name

        if _factory and not _name:
            raise ValueError(
                "Error: The factory function name must be provided to the --name parameter when the factory flag is set."
            )
        imported_app = import_app(_app_path, _name, _factory)

    # Extract MCP-specific arguments
    transport = _kwargs.pop("transport", "streamable-http")
    allowed_categories = _kwargs.pop("allowed_categories", None)
    default_categories = _kwargs.pop("default_categories", "all")
    no_tool_discovery = _kwargs.pop("no_tool_discovery", False)
    system_prompt = _kwargs.pop("system_prompt", None)
    server_prompts = _kwargs.pop("server_prompts", None)

    class Args:
        """Container for parsed command line arguments."""

        def __init__(self):
            """Initialize the Args container."""
            self.imported_app = imported_app
            self.transport = transport
            self.allowed_categories = allowed_categories
            self.default_categories = default_categories
            self.no_tool_discovery = no_tool_discovery
            self.system_prompt = system_prompt
            self.server_prompts = server_prompts
            self.uvicorn_config = _kwargs  # All remaining kwargs go to uvicorn

    return Args()
