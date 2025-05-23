"""API Utils."""

import json
import os
import socket
import sys
from pathlib import Path
from typing import Optional

from deepdiff import DeepDiff

from .widgets import build_json

LAUNCH_SCRIPT_DESCRIPTION = """
Serve the OpenBB Platform API.


Launcher specific arguments:

    --app                           Absolute path to the Python file with the target FastAPI instance. Default is the installed OpenBB Platform API.
    --name                          Name of the FastAPI instance in the app file. Default is 'app'.
    --factory                       Flag to indicate if the app name is a factory function. Default is 'false'.
    --editable                      Flag to make widgets.json an editable file that can be modified during runtime. Default is 'false'.
    --build                         If the file already exists, changes prompt action to overwrite/append/ignore. Only valid when --editable true.
    --no-build                      Do not build the widgets.json file. Use this flag to load an existing widgets.json file without checking for updates.
    --login                         Login to the OpenBB Platform.
    --exclude                       JSON encoded list of API paths to exclude from widgets.json. Disable entire routes with '*' - e.g. '["/api/v1/*"]'.
    --no-filter                     Do not filter out widgets in widget_settings.json file.
    --widgets-json                  Absolute/relative path to use as the widgets.json file. Default is ~/envs/{env}/assets/widgets.json, when --editable is 'true'.
    --apps-json                     Absolute/relative path to use as the apps.json file. Default is ~/OpenBBUserData/workspace_apps.json.
    --agents-json                   Absolute/relative path to use as the agents.json file. Including this will add the /agents endpoint to the API.


The FastAPI app instance can be imported to another script, modified, and launched by using the --app argument.

If the path to the app file is not absolute, it will be resolved relative to the current working directory.

Imported with:

>>> from openbb_platform_api.main import app
>>>
>>> @app.get()
>>> async def hello(input: str = "Hello") -> str:
>>>     '''Widget description created by doctring.'''
>>>     return f"You entered: {input}"

Launched with:

>>> openbb-api --app /path/to/some_file.py

The app instance name can be defined by either the --name argument, or by referencing the module name, for example:

>>> openbb-api --app some_file.py:main --factory

A name must be set when using the factory flag.

All other arguments will be passed to uvicorn. Here are the most common ones:

    --host TEXT                     Host IP address or hostname.
                                      [default: 127.0.0.1]
    --port INTEGER                  Port number.
                                      [default: 6900]
    --ssl-keyfile TEXT              SSL key file.
    --ssl-certfile TEXT             SSL certificate file.
    --ssl-keyfile-password TEXT     SSL keyfile password.
    --ssl-version INTEGER           SSL version to use.
                                      (see stdlib ssl module's)
                                      [default: 17]
    --ssl-cert-reqs INTEGER         Whether client certificate is required.
                                      (see stdlib ssl module's)
                                      [default: 0]
    --ssl-ca-certs TEXT             CA certificates file.
    --ssl-ciphers TEXT              Ciphers to use.
                                      (see stdlib ssl module's)
                                      [default: TLSv1]

Run `uvicorn --help` to get the full list of arguments.
"""  # noqa: E501


def check_port(host, port):
    """Check if the port number is free."""
    port = int(port)
    not_free = True
    while not_free:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex((host, port))
            if res != 0:
                not_free = False
            else:
                port += 1
    return port


def get_user_settings(
    _login: bool, current_user_settings: str, user_settings_copy: str
):
    """Login to the OpenBB Platform."""
    # pylint: disable=import-outside-toplevel
    import getpass

    if Path(current_user_settings).exists():
        with open(current_user_settings, encoding="utf-8") as f:
            _current_settings = json.load(f)
    else:
        _current_settings = {
            "credentials": {},
            "preferences": {},
            "defaults": {"commands": {}},
        }
    if (isinstance(_login, str) and _login.lower() == "false") or not _login:
        return _current_settings

    pat = getpass.getpass(
        "\n\nEnter your personal access token (PAT) to authorize the API and update your local settings."
        + "\nSkip to use a pre-configured 'user_settings.json' file."
        + "\nPress Enter to skip or copy (entered values are not displayed on screen) your PAT to the command line: "
    )

    if pat:
        from openbb_core.app.service.hub_service import HubService

        hub_credentials: dict = {}
        hub_preferences: dict = {}
        hub_defaults: dict = {}
        try:
            Hub = HubService()
            _ = Hub.connect(pat=pat)
            hub_settings = Hub.pull()
            hub_credentials = json.loads(
                hub_settings.credentials.model_dump_json()  # pylint: disable=no-member
            )
            hub_preferences = json.loads(
                hub_settings.preferences.model_dump_json()  # pylint: disable=no-member
            )
            hub_defaults = json.loads(
                hub_settings.defaults.model_dump_json()  # pylint: disable=no-member
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(  # noqa: T201
                f"\n\nError connecting with Hub:\n{e}\n\nUsing the local settings.\n"
            )

        if hub_credentials:
            # Prompt the user to ask if they want to persist the new settings
            persist_input = (
                input(
                    "\n\nDo you want to persist the new settings?"
                    + " Not recommended for public machines. (yes/no): "
                )
                .strip()
                .lower()
            )

            if persist_input in ["yes", "y"]:
                PERSIST = True
            elif persist_input in ["no", "n"]:
                PERSIST = False
            else:
                print(  # noqa: T201
                    "\n\nInvalid input. Defaulting to not persisting the new settings."
                )
                PERSIST = False

            # Save the current settings to restore at the end of the session.
            if PERSIST is False:
                with open(user_settings_copy, "w", encoding="utf-8") as f:
                    json.dump(_current_settings, f, indent=4)

        new_settings = _current_settings.copy()
        new_settings.setdefault("credentials", {})
        new_settings.setdefault("preferences", {})
        new_settings.setdefault("defaults", {"commands": {}})

        # Update the current settings with the new settings
        if hub_credentials:
            for k, v in hub_credentials.items():
                if v:
                    new_settings["credentials"][k] = v.strip('"').strip("'")

        if hub_preferences:
            for k, v in hub_preferences.items():
                if v:
                    new_settings["preferences"][k] = v

        if hub_defaults:
            for k, v in hub_defaults.items():
                if k == "commands":
                    for key, value in hub_defaults["commands"].items():
                        if value:
                            new_settings["defaults"]["commands"][key] = value
                elif v:
                    new_settings["defaults"][k] = v
                else:
                    continue

        # Write the new settings to the user_settings.json file
        with open(current_user_settings, "w", encoding="utf-8") as f:
            json.dump(new_settings, f, indent=4)

        _current_settings = new_settings

    return _current_settings


def get_widgets_json(
    _build: bool,
    _openapi,
    widget_exclude_filter: list,
    editable: bool = False,
    widgets_path: Optional[str] = None,
):
    """Generate and serve the widgets.json for the OpenBB Platform API."""
    if editable is True:
        if widgets_path is None:
            python_path = Path(sys.executable)
            parent_path = (
                python_path.parent if os.name == "nt" else python_path.parents[1]
            )
            widgets_json_path = parent_path.joinpath("assets", "widgets.json").resolve()
        else:
            widgets_json_path = Path(widgets_path).absolute().resolve()

        json_exists = widgets_json_path.exists()

        if not json_exists:
            widgets_json_path.parent.mkdir(parents=True, exist_ok=True)
            _build = True
            json_exists = widgets_json_path.exists()

        existing_widgets_json: dict = {}

        if json_exists:
            with open(widgets_json_path, encoding="utf-8") as f:
                existing_widgets_json = json.load(f)

        _widgets_json = (
            existing_widgets_json
            if _build is False
            else build_json(_openapi, widget_exclude_filter)
        )

        if _build:
            diff = DeepDiff(existing_widgets_json, _widgets_json, ignore_order=True)
            merge_prompt = None
            if diff and json_exists:
                print("Differences found:", diff)  # noqa: T201
                merge_prompt = input(
                    "\nDo you want to overwrite the existing widgets.json configuration?"
                    "\nEnter 'n' to append existing with only new entries, or 'i' to ignore all changes. (y/n/i): "
                )
                if merge_prompt.lower().startswith("n"):
                    _widgets_json.update(existing_widgets_json)
                elif merge_prompt.lower().startswith("i"):
                    _widgets_json = existing_widgets_json

            if merge_prompt is None or not merge_prompt.lower().startswith("i"):
                try:
                    with open(widgets_json_path, "w", encoding="utf-8") as f:
                        json.dump(_widgets_json, f, ensure_ascii=False, indent=4)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(  # noqa: T201
                        f"Error writing widgets.json: {e}.  Loading from memory instead."
                    )
                    _widgets_json = (
                        existing_widgets_json
                        if existing_widgets_json
                        else build_json(_openapi, widget_exclude_filter)
                    )
    else:
        _widgets_json = build_json(_openapi, widget_exclude_filter)

    return _widgets_json


def import_app(app_path: str, name: str = "app", factory: bool = False):
    """Import the FastAPI app instance from a local file or module."""
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI  # noqa
    from fastapi.middleware.cors import CORSMiddleware
    from importlib import import_module, util
    from openbb_core.api.app_loader import AppLoader
    from openbb_core.api.rest_api import system

    def _load_module_from_file_path(file_path: str):
        spec_name = os.path.basename(file_path).split(".")[0]
        spec = util.spec_from_file_location(spec_name, file_path)

        if spec is None:
            raise RuntimeError(f"Failed to load the file specs for '{file_path}'")

        module = util.module_from_spec(spec)  # type: ignore
        sys.modules[spec_name] = module  # type: ignore
        spec.loader.exec_module(module)  # type: ignore
        return module

    # Case 1: Module path with colon notation (e.g., "my_app.main:app" or "main:app")
    if ":" in app_path:
        module_path, name = app_path.split(":")
        try:  # First try to import as a module
            module = import_module(module_path)
        except ImportError:  # If module import fails, try to load as a local file
            if not module_path.endswith(".py"):
                module_path += ".py"

            if not str(module_path).startswith("/"):
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
        if not str(app_path).startswith("/"):
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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=system.api_settings.cors.allow_origins,
        allow_methods=system.api_settings.cors.allow_methods,
        allow_headers=system.api_settings.cors.allow_headers,
    )

    AppLoader.add_exception_handlers(app)

    return app


def parse_args():  # noqa: PLR0912  # pylint: disable=too-many-branches
    """Parse the launch script command line arguments."""
    args = sys.argv[1:].copy()
    cwd = Path.cwd()
    _kwargs: dict = {}
    for i, arg in enumerate(args):
        if arg == "--help":
            print(LAUNCH_SCRIPT_DESCRIPTION)  # noqa: T201
            sys.exit(0)
        if arg.startswith("--"):
            key = arg[2:]
            if key in ["no-use-colors", "use-colors"]:
                _kwargs["use_colors"] = key == "use-colors"
            elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                if isinstance(value, str) and value.lower() in ["false", "true"]:
                    _kwargs[key] = value.lower() == "true"
                elif key == "exclude":
                    _kwargs[key] = json.loads(value)
                else:
                    _kwargs[key] = value
            else:
                _kwargs[key] = True

    if _kwargs.get("app"):
        _app_path = _kwargs.pop("app", None)
        _name = _kwargs.pop("name", "app")
        _factory = _kwargs.pop("factory", False)

        if ":" in _app_path:
            _app_instance_name = _app_path.split(":")[-1]
            _name = _app_instance_name if _app_instance_name else _name

        if _factory and not _name:
            raise ValueError(
                "Error: The factory function name must be provided to the --name parameter when the factory flag is set."
            )
        _kwargs["app"] = import_app(_app_path, _name, _factory)

    if isinstance(_kwargs.get("exclude"), str):
        _kwargs["exclude"] = [_kwargs["exclude"]]

    if _kwargs.get("agents-json") or _kwargs.get("copilots-path"):
        _agents_path = _kwargs.pop("agents-json", None) or _kwargs.pop(
            "copilots-path", None
        )

        if not str(_agents_path).endswith(".json"):
            _agents_path = (
                f"{_agents_path}{'' if _agents_path.endswith('/') else '/'}agents.json"
            )

        if str(_agents_path).startswith("./"):
            _agents_path = str(cwd.joinpath(_agents_path).resolve())

        _kwargs["agents-json"] = _agents_path

    if _kwargs.get("widgets-json") or _kwargs.get("widgets-path"):
        _widgets_path = _kwargs.pop("widgets-json", None) or _kwargs.pop(
            "widgets-path", None
        )

        # If it's a file (endswith .json), use as is; else treat as directory and append widgets.json
        if str(_widgets_path).endswith(".json"):
            widgets_file_path = _widgets_path
        else:
            widgets_file_path = f"{_widgets_path}{'' if str(_widgets_path).endswith('/') else '/'}widgets.json"

        # Resolve relative paths to absolute
        if str(widgets_file_path).startswith("./"):
            widgets_file_path = str(cwd.joinpath(widgets_file_path).resolve())

        _kwargs["widgets-json"] = widgets_file_path

    if _kwargs.get("widgets-json"):
        _kwargs["editable"] = True
        # If the file already exists, we assume that it is already built.
        if os.path.exists(_kwargs["widgets-json"]):
            _kwargs["no-build"] = True

    # Handle apps-json and templates-path in the same way as widgets-path
    if _kwargs.get("apps-json") or _kwargs.get("templates-path"):
        _apps_path = _kwargs.pop("apps-json", None) or _kwargs.pop(
            "templates-path", None
        )

        # If it's a file (endswith .json), use as is; else treat as directory and append apps.json
        if str(_apps_path).endswith(".json"):
            apps_file_path = _apps_path
        else:
            # Check if "workspace_apps.json" exists in the given path
            possible_workspace_file = f"{_apps_path}{'' if str(_apps_path).endswith('/') else '/'}workspace_apps.json"
            if os.path.isfile(possible_workspace_file):
                apps_file_path = possible_workspace_file
            else:
                apps_file_path = f"{_apps_path}{'' if str(_apps_path).endswith('/') else '/'}apps.json"

        # Resolve relative paths to absolute
        if str(apps_file_path).startswith("./"):
            apps_file_path = str(cwd.joinpath(apps_file_path).resolve())

        _kwargs["apps-json"] = apps_file_path

    return _kwargs
