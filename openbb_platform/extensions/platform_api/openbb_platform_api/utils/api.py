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
    --editable                      Flag to make widgets.json an editable file that can be modified during runtime. Default is 'false'.
    --build                         If the file already exists, changes prompt action to overwrite/append/ignore. Only valid when --editable true.
    --no-build                      Do not build the widgets.json file. Use this flag to load an existing widgets.json file without checking for updates.
    --login                         Login to the OpenBB Platform.
    --exclude                       JSON encoded list of API paths to exclude from widgets.json. Disable entire routes with '*' - e.g. '["/api/v1/*"]'.
    --no-filter                     Do not filter out widgets in widget_settings.json file.
    --widgets-path                  Absolute path to the widgets.json file. Default is ~/envs/{env}/assets/widgets.json. Supplying this sets --editable true.
    --templates-path                Absolute path to the workspace_templates.json file. Default is ~/OpenBBUserData/workspace_templates.json.
    --copilots-path                 Absolute path to the copilots.json file. Including this will add the /copilots endpoint to the API.


The FastAPI app instance can be imported to another script, modified, and launched by using the --app argument.

Imported with:

>>> from openbb_platform_api.main import app
>>>
>>> @app.get()
>>> async def hello(input: str = "Hello") -> str:
>>>     '''Widget description created by doctring.'''
>>>     return f"You entered: {input]"

Launched with:

>>> openbb-api --app /path/to/some_file.py


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
            widgets_json_path = (
                Path(widgets_path).absolute().joinpath("widgets.json").resolve()
            )

        json_exists = widgets_json_path.exists()

        if not json_exists:
            widgets_json_path.parent.mkdir(parents=True, exist_ok=True)
            _build = True

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


def import_app(app_path: str):
    """Import the FastAPI app instance from a local file."""
    # pylint: disable=import-outside-toplevel
    from fastapi import FastAPI  # noqa
    from fastapi.middleware.cors import CORSMiddleware
    from importlib import util
    from openbb_core.api.app_loader import AppLoader
    from openbb_core.api.rest_api import system

    if not Path(app_path).exists():
        raise FileNotFoundError(f"Error: The app file '{app_path}' does not exist")

    spec = util.spec_from_file_location("app", app_path)
    if spec is None:
        raise RuntimeError(f"Failed to load the file specs for '{app_path}'")

    module = util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore

    if not hasattr(module, "app"):
        raise AttributeError(
            f"Error: The app file '{app_path}' does not contain an 'app' instance"
        )

    if not isinstance(module.app, FastAPI):
        raise TypeError(
            f"Error: The app instance in '{app_path}' is not an instance of FastAPI"
        )

    app = module.app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=system.api_settings.cors.allow_origins,
        allow_methods=system.api_settings.cors.allow_methods,
        allow_headers=system.api_settings.cors.allow_headers,
    )
    AppLoader.add_openapi_tags(app)
    AppLoader.add_exception_handlers(app)

    return app


def parse_args():
    """Parse the launch script command line arguments."""
    args = sys.argv[1:].copy()
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

    if isinstance(_kwargs.get("exclude"), str):
        _kwargs["exclude"] = [_kwargs["exclude"]]

    if _kwargs.get("copilots-path"):
        _copilots_path = _kwargs.pop("copilots-path", None)
        if not Path(_copilots_path).exists():
            raise FileNotFoundError(
                f"Error: The copilots file '{_copilots_path}' does not exist"
            )
        with open(_copilots_path, encoding="utf-8") as f:
            _kwargs["copilots"] = json.load(f)

    if _kwargs.get("app"):
        _app_path = _kwargs.pop("app", None)
        if not Path(_app_path).exists():
            raise FileNotFoundError(f"Error: The app file '{_app_path}' does not exist")
        _kwargs["app"] = import_app(_app_path)

    if _kwargs.get("widgets_path"):
        _kwargs["editable"] = True

    return _kwargs
