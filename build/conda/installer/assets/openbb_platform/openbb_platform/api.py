"""Generate and serve the widgets.json for the OpenBB Platform API."""

# flake8: noqa: T201

import json
import os
import socket
from pathlib import Path

from fastapi.responses import JSONResponse
from openbb_core.api.rest_api import app

from openbb_platform.utils import (
    data_schema_to_columns_defs,
    get_data_schema_for_widget,
    get_query_schema_for_widget,
)

HOME = os.environ.get("HOME") or os.environ.get("USERPROFILE")

CURRENT_USER_SETTINGS = os.path.join(HOME, ".openbb_platform", "user_settings.json")
USER_SETTINGS_COPY = os.path.join(HOME, ".openbb_platform", "user_settings_backup.json")

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
    import getpass

    if Path(CURRENT_USER_SETTINGS).exists():
        with open(CURRENT_USER_SETTINGS) as f:
            current_settings = json.load(f)
    else:
        current_settings = {"credentials": {}, "preferences": {}, "defaults": {"commands": {}}}
    if (isinstance(login, str) and login.lower() == "false") or not login:
        return current_settings

    pat = getpass.getpass(
        "\n\nEnter your personal access token (PAT) to authorize the API and update your local settings."
        + "\nSkip to use a pre-configured 'user_settings.json' file."
        + "\nPress Enter to skip or copy (entered values are not displayed on screen) your PAT to the command line: "
    )

    if pat:
        from openbb_core.app.service.hub_service import HubService

        try:
            Hub = HubService()
            _ = Hub.connect(pat=pat)
            hub_settings = Hub.pull()
            hub_credentials = json.loads(hub_settings.credentials.model_dump_json())
            hub_preferences = json.loads(hub_settings.preferences.model_dump_json())
            hub_defaults = json.loads(hub_settings.defaults.model_dump_json())
        except Exception as e:
            print(f"\n\nError connecting with Hub:\n{e}\n\nUsing the local settings.\n")
            hub_credentials = {}
            hub_preferences = {}
            hub_defaults = {}

        if hub_credentials:
            # Prompt the user to ask if they want to persist the new settings
            persist_input = input(
                "\n\nDo you want to persist the new settings?"
                + " Not recommended for public machines. (yes/no): "
            ).strip().lower()

            if persist_input in ["yes", "y"]:
                PERSIST = True
            elif persist_input in ["no", "n"]:
                PERSIST = False
            else:
                print("\n\nInvalid input. Defaulting to not persisting the new settings.")
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
    widgets_json = {}
    routes = [
        p for p in openapi["paths"] if p.startswith("/api") and "get" in openapi["paths"][p]
    ]
    for route in routes:
        route_api = openapi["paths"][route]
        widget_id = route_api["get"]["operationId"]

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
            columns_defs = data_schema_to_columns_defs(openapi, response_schema_refs)  # noqa F841

        widget_config = {
            "name": f'OBB {route_api["get"]["operationId"].replace("_", " ").title()}',
            "description": route_api["get"]["description"],
            "category": route_api["get"]["tags"][0].title(),
            "widgetType": route_api["get"]["tags"][0],
            "widgetId": f"OBB {widget_id}",
            "params": query_schema,  # Use the fetched query schema
            "endpoint": route.replace("/api", "api"),
            "gridData": {"w": 45, "h": 15},
            "data": {
                "dataKey": "results",
                "table": {
                    "showAll": False,
                },
            },
        }

        #if columns_defs:
        #    widget_config["data"]["table"]["columnsDefs"] = columns_defs
        #    if "date" in columns_defs:
        #        widget_config["data"]["table"]["index"] = "date"
        #    if "period" in columns_defs:
        #        widget_config["data"]["table"]["index"] = "period"

        # Add the widget configuration to the widgets.json
        widgets_json[widget_config["widgetId"]] = widget_config

        if has_chart:
            # deepcopy the widget_config
            widget_config_chart = json.loads(json.dumps(widget_config))
            del widget_config_chart["data"]["table"]

            widget_config_chart["name"] = f"{widget_config_chart['name']} Chart"
            widget_config_chart["widgetId"] = f"{widget_config_chart['widgetId']}_chart"
            widget_config_chart["params"]["chart"] = True

            widget_config_chart["defaultViz"] = "chart"
            widget_config_chart["data"]["dataKey"] = "chart.content"
            widget_config_chart["data"]["chart"] = {
                "type": "line",
            }

            widgets_json[widget_config_chart["widgetId"]] = widget_config_chart

    return widgets_json


def get_widgets_json(build: bool, openapi):
    """Generate and serve the widgets.json for the OpenBB Platform API."""

    python_path = Path(os.sys.executable)
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

    existing_widgets_json = {}

    if json_exists:
        with open(widgets_json_path, encoding="utf-8") as f:
            existing_widgets_json = json.load(f)

    widgets_json = existing_widgets_json if build is False else build_json(openapi)

    if existing_widgets_json and build is True:
        merge_prompt = input(
            "\n'widgets.json' was previously built. Do you want to overwrite the existing widgets.json configuration?"
            "\nEnter 'n' to append existing (y/n): "
        )
        if merge_prompt.lower().startswith("n"):
            widgets_json.update(existing_widgets_json)

    # Write the widgets_json to the assets folder.
    with open(widgets_json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(widgets_json, indent=4))

    return widgets_json


def main():
    """Main function."""
    import uvicorn

    args = os.sys.argv[1:].copy()
    kwargs = {}
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
    # but we need to call the function to update login and/or identify the settings file.
    current_settings = get_user_settings(login)  # noqa F841

    widgets_json = get_widgets_json(build, openapi)

    @app.get("/")
    async def get_root():
        """API Root."""
        return JSONResponse(content={})

    @app.get("/widgets.json")
    async def get_widgets():
        """Widgets configuration file for the OpenBB Terminal Pro."""
        return JSONResponse(content=widgets_json)

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

        port = kwargs.pop("port", os.getenv("OPENBB_API_PORT", "8000"))

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
                print("\n\nInvalid port number. Defaulting to 8000.")
                port = 8000
        if port < 1025:
            port = 8000
            print("\n\nInvalid port number, must be above 1024. Defaulting to 8000.")

        free_port = check_port(host, port)

        if free_port != port:
            print(f"\n\nPort {port} is already in use. Using port {free_port}.\n")
            port = free_port

        try:
            uvicorn.run("openbb_platform.api:app", host=host, port=port, **kwargs)
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
