"""Generate and serve the widgets.json for the OpenBB Platform API."""

# flake8: noqa: T201

import importlib.util
import json
import os
import socket
import sys
from copy import deepcopy
from pathlib import Path
from typing import Dict

import uvicorn
from deepdiff import DeepDiff
from fastapi.responses import JSONResponse
from openbb_core.api.rest_api import app

HOME = os.environ.get("HOME") or os.environ.get("USERPROFILE")

CURRENT_USER_SETTINGS = os.path.join(HOME, ".openbb_platform", "user_settings.json")  # type: ignore
USER_SETTINGS_COPY = os.path.join(HOME, ".openbb_platform", "user_settings_backup.json")  # type: ignore

FIRST_RUN = True


def check_port(host, port) -> int:
    """Check if the port number is free."""
    not_free = True
    port = int(port) - 1
    while not_free:
        port = port + 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex((host, port))
            if res != 0:
                not_free = False
    return port


def get_user_settings(login: bool):
    """Login to the OpenBB Platform."""
    # pylint: disable=import-outside-toplevel
    import getpass

    if Path(CURRENT_USER_SETTINGS).exists():
        with open(CURRENT_USER_SETTINGS) as f:
            current_settings = json.load(f)
    else:
        current_settings = {
            "credentials": {},
            "preferences": {},
            "defaults": {"commands": {}},
        }
    if (isinstance(login, str) and login.lower() == "false") or not login:
        return current_settings

    pat = getpass.getpass(
        "\n\nEnter your personal access token (PAT) to authorize the API and update your local settings."
        + "\nSkip to use a pre-configured 'user_settings.json' file."
        + "\nPress Enter to skip or copy (entered values are not displayed on screen) your PAT to the command line: "
    )

    if pat:
        from openbb_core.app.service.hub_service import HubService

        hub_credentials: Dict = {}
        hub_preferences: Dict = {}
        hub_defaults: Dict = {}
        try:
            Hub = HubService()
            _ = Hub.connect(pat=pat)
            hub_settings = Hub.pull()
            hub_credentials = json.loads(hub_settings.credentials.model_dump_json())
            hub_preferences = json.loads(hub_settings.preferences.model_dump_json())
            hub_defaults = json.loads(hub_settings.defaults.model_dump_json())
        except Exception as e:
            print(f"\n\nError connecting with Hub:\n{e}\n\nUsing the local settings.\n")

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
                print(
                    "\n\nInvalid input. Defaulting to not persisting the new settings."
                )
                PERSIST = False

            # Save the current settings to restore at the end of the session.
            if PERSIST is False:
                with open(USER_SETTINGS_COPY, "w") as f:
                    json.dump(current_settings, f, indent=4)

        new_settings = current_settings.copy()
        new_settings.setdefault("credentials", {})
        new_settings.setdefault("preferences", {})
        new_settings.setdefault("defaults", {"commands": {}})

        # Update the current settings with the new settings
        if hub_credentials:
            for k, v in hub_credentials.items():
                if v:
                    new_settings["credentials"][k] = v

        if hub_preferences:
            for k, v in hub_credentials.items():
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
        with open(CURRENT_USER_SETTINGS, "w") as f:
            json.dump(new_settings, f, indent=4)

        current_settings = new_settings

    return current_settings


def build_json(openapi):
    """Build the widgets.json file."""

    # We need to import the utils module as a dynamic relative import.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    utils_path = os.path.join(script_dir, "utils.py")
    spec = importlib.util.spec_from_file_location("utils", utils_path)  # type: ignore
    utils = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(utils)  # type: ignore

    # Assign the required functions from the utils module
    data_schema_to_columns_defs = utils.data_schema_to_columns_defs
    get_data_schema_for_widget = utils.get_data_schema_for_widget
    get_query_schema_for_widget = utils.get_query_schema_for_widget

    widgets_json: Dict = {}
    routes = [
        p
        for p in openapi["paths"]
        if p.startswith("/api") and "get" in openapi["paths"][p]
    ]
    for route in routes:
        route_api = openapi["paths"][route]
        method = list(route_api)[0]
        widget_id = route_api[method]["operationId"]

        # Prepare the query schema of the widget
        query_schema, has_chart = get_query_schema_for_widget(openapi, route)

        # Prepare the data schema of the widget
        data_schema = get_data_schema_for_widget(openapi, widget_id)
        if (
            data_schema
            and "properties" in data_schema
            and "results" in data_schema["properties"]
        ):
            response_schema_refs = data_schema["properties"]["results"]
            columns_defs = data_schema_to_columns_defs(  # noqa F841
                openapi, response_schema_refs
            )
        _cat = route.split("v1/")[-1]
        _cats = _cat.split("/")
        category = _cats[0].title()
        category = category.replace("Fixedincome", "Fixed Income")
        subcat = _cats[1].title().replace("_", " ") if len(_cats) > 2 else None
        name = (
            widget_id.replace("fixedincome", "fixed income").replace("_", " ").title()
        )
        to_caps = [
            "Pe",
            "Sloos",
            "Eps",
            "Ebitda",
            "Otc",
            "Cpi",
            "Pce",
            "Gdp",
            "Lbma",
            "Ipo",
            "Nbbo",
            "Ameribor",
            "Sonia",
            "Effr",
            "Sofr",
            "Iorb",
            "Estr",
            "Ecb",
            "Dpcredit",
            "Tcm",
            "Us",
            "Ice",
            "Bofa",
            "Hqm",
            "Sp500",
            "Sec",
            "Cftc",
            "Cot",
            "Etf",
            "Eu",
            "Tips",
            "Rss",
            "Sic",
            "Cik",
            "Bls",
            "Fred",
        ]
        name = " ".join(
            [(word.upper() if word in to_caps else word) for word in name.split()]
        )
        widget_config = {
            "name": name + " (OpenBB API)",
            "description": route_api["get"]["description"],
            "category": category,
            "searchCategory": category,
            "widgetId": widget_id + "_obb",
            "params": query_schema,
            "endpoint": route.replace("/api", "api"),
            "gridData": {"w": 45, "h": 15},
            "data": {
                "dataKey": "results",
                "table": {
                    "showAll": False,
                },
            },
        }

        if subcat:
            subcat = " ".join(
                [(word.upper() if word in to_caps else word) for word in subcat.split()]
            )
            subcat = (
                subcat.replace("Estimates", "Analyst Estimates")
                .replace("Fundamental", "Fundamental Analysis")
                .replace("Compare", "Comparison Analysis")
            )
            widget_config["subCategory"] = subcat

        # if columns_defs:
        #    widget_config["data"]["table"]["columnsDefs"] = columns_defs
        #    if "date" in columns_defs:
        #        widget_config["data"]["table"]["index"] = "date"
        #    if "period" in columns_defs:
        #        widget_config["data"]["table"]["index"] = "period"

        # Add the widget configuration to the widgets.json
        widgets_json[widget_config["widgetId"]] = widget_config

        if has_chart:
            widget_config_chart = deepcopy(widget_config)
            widget_config_chart["name"] = (
                f"{widget_config_chart['name'].replace(' (OpenBB API)', '')} Chart (OpenBB API)"
            )
            widget_config_chart["widgetId"] = f"{widget_config_chart['widgetId']}_chart"
            widget_config_chart["params"].append(
                {
                    "paramName": "chart",
                    "label": "Chart",
                    "description": "Returns chart",
                    "optional": True,
                    "value": True,
                    "type": "boolean",
                    "show": False,
                },
            )
            widget_config_chart["searchCategory"] = "chart"
            widget_config_chart["gridData"]["h"] = 20
            widget_config_chart["gridData"]["w"] = 50
            widget_config_chart["defaultViz"] = "chart"
            widget_config_chart["data"]["dataKey"] = "chart.content"
            widgets_json[widget_config_chart["widgetId"]] = widget_config_chart

    return widgets_json


def get_widgets_json(build: bool, openapi):
    """Generate and serve the widgets.json for the OpenBB Platform API."""
    python_path = Path(sys.executable)
    widgets_json_path = (
        python_path.parents[0 if os.name == "nt" else 1]
        .joinpath("assets")
        .resolve()
        .joinpath("widgets.json")
    )
    json_exists = widgets_json_path.exists()

    if not json_exists:
        widgets_json_path.parent.mkdir(parents=True, exist_ok=True)
        build = True

    existing_widgets_json: Dict = {}

    if json_exists:
        with open(widgets_json_path, encoding="utf-8") as f:
            existing_widgets_json = json.load(f)

    widgets_json = existing_widgets_json if build is False else build_json(openapi)

    if build:
        diff = DeepDiff(existing_widgets_json, widgets_json, ignore_order=True)
        merge_prompt = None
        if diff and json_exists:
            print("Differences found:", diff)
            merge_prompt = input(
                "\nDo you want to overwrite the existing widgets.json configuration?"
                "\nEnter 'n' to append existing with only new entries, or 'i' to ignore all changes. (y/n/i): "
            )
            if merge_prompt.lower().startswith("n"):
                widgets_json.update(existing_widgets_json)
            elif merge_prompt.lower().startswith("i"):
                widgets_json = existing_widgets_json

        if merge_prompt is None or not merge_prompt.lower().startswith("i"):
            try:
                with open(widgets_json_path, "w", encoding="utf-8") as f:
                    json.dump(widgets_json, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Error writing widgets.json: {e}.  Loading from memory instead.")
                widgets_json = (
                    existing_widgets_json
                    if existing_widgets_json
                    else build_json(openapi)
                )

    return widgets_json


def main():
    """Entry point for the main script."""
    # pylint: disable=import-outside-toplevel
    args = sys.argv[1:].copy()
    kwargs: Dict = {}
    for i in range(len(args)):
        if args[i].startswith("--"):
            key = args[i][2:]
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                value = args[i + 1]
                kwargs[key] = value
            else:
                kwargs[key] = True

    openapi = app.openapi()
    build = kwargs.pop("build", True)
    build = False if kwargs.pop("no-build", None) else build
    login = kwargs.pop("login", False)
    # We don't need the current settings,
    # but we need to call the function to update, login, and/or identify the settings file.
    current_settings = get_user_settings(login)  # noqa F841

    widgets_json = get_widgets_json(build, openapi)

    @app.get("/")
    async def get_root():
        """The API root response."""
        return JSONResponse(
            content="Welcome to the OpenBB Platform API."
            + " Learn how to connect to Pro in docs.openbb.co/pro/data-connectors,"
            + " or see the API documentation here: /docs"
        )

    @app.get("/widgets.json")
    async def get_widgets():
        """Widgets configuration file for the OpenBB Terminal Pro."""
        # This allows us to serve an edited widgets.json file without reloading the server.
        global FIRST_RUN  # noqa PLW0603
        if FIRST_RUN is True:
            FIRST_RUN = False
            return JSONResponse(content=widgets_json)
        else:
            return JSONResponse(content=get_widgets_json(False, openapi))

    def launch_api(**kwargs):  # noqa PRL0912
        """Main function."""
        host = kwargs.pop("host", os.getenv("OPENBB_API_HOST", "127.0.0.1"))
        if not host:
            print(
                "\n\nOPENBB_API_HOST is set incorrectly. It should be an IP address or hostname."
            )
            host = input("Enter the host IP address or hostname: ")
            if not host:
                host = "127.0.0.1"

        port = kwargs.pop("port", os.getenv("OPENBB_API_PORT", "6900"))

        try:
            port = int(port)
        except ValueError:
            print(
                "\n\nOPENBB_API_PORT is set incorrectly. It should be an port number."
            )
            port = input("Enter the port number: ")
            try:
                port = int(port)
            except ValueError:
                print("\n\nInvalid port number. Defaulting to 6900.")
                port = 6900
        if port < 1025:
            port = 6900
            print("\n\nInvalid port number, must be above 1024. Defaulting to 6900.")

        free_port = check_port(host, port)

        if free_port != port:
            print(f"\n\nPort {port} is already in use. Using port {free_port}.\n")
            port = free_port

        try:
            package_name = __package__
            uvicorn.run(f"{package_name}.api:app", host=host, port=port, **kwargs)
        finally:
            # If user_settings_copy.json exists, then restore the original settings.
            if os.path.exists(USER_SETTINGS_COPY):
                print("\n\nRestoring the original settings.\n")
                os.replace(USER_SETTINGS_COPY, CURRENT_USER_SETTINGS)

    launch_api(**kwargs)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        print("Restoring the original settings.")
