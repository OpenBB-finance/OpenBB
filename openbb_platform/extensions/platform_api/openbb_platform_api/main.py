"""OpenBB Platform API.

Launch script and widgets builder for the OpenBB Workspace Custom Backend.
"""

import json
import logging
import os
import sys
from pathlib import Path

import uvicorn
from fastapi.responses import HTMLResponse, JSONResponse
from openbb_core.api.rest_api import app
from openbb_core.app.service.system_service import SystemService
from openbb_core.env import Env

from .utils.api import (
    FIRST_RUN,
    check_port,
    get_user_settings,
    get_widgets_json,
    parse_args,
)
from .utils.merge_agents import get_additional_agents, has_additional_agents
from .utils.merge_apps import get_additional_apps, has_additional_apps

logger = logging.getLogger("openbb_platform_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("\n%(message)s\n")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Adds the OpenBB Environment variables to the script process.
Env()
HOME = os.environ.get("HOME") or os.environ.get("USERPROFILE")

if not HOME:
    raise ValueError("HOME or USERPROFILE environment variable not set.")

CURRENT_USER_SETTINGS = os.path.join(HOME, ".openbb_platform", "user_settings.json")
# Widget filtering is optional and can be used to exclude widgets from the widgets.json file
# Alternatively, you can supply a JSON-encoded list of API paths to ignore.
WIDGET_SETTINGS = os.path.join(HOME, ".openbb_platform", "widget_settings.json")
kwargs = parse_args()
_app = kwargs.pop("app", None)

if _app:
    app = _app

WIDGETS_PATH = kwargs.pop("widgets-json", None)
APPS_PATH = kwargs.pop("apps-json", None)
EDITABLE = kwargs.pop("editable", None) is True or WIDGETS_PATH is not None
DEFAULT_APPS_PATH = (
    Path(__file__).absolute().parent.joinpath("assets").joinpath("default_apps.json")
)
AGENTS_PATH = kwargs.pop("agents-json", None)
build = kwargs.pop("build", True)
build = False if kwargs.pop("no-build", None) else build
dont_filter = kwargs.pop("no-filter", False)
widget_exclude_filter: list = kwargs.pop("exclude", [])
uvicorn_settings = (
    SystemService().system_settings.python_settings.model_dump().get("uvicorn", {})
)
obb_headers = {"X-Backend-Type": "OpenBB Platform"}

for key, value in uvicorn_settings.items():
    if key not in kwargs and key != "app" and value is not None:
        kwargs[key] = value

if not dont_filter and os.path.exists(WIDGET_SETTINGS):
    with open(WIDGET_SETTINGS, encoding="utf-8") as widget_settings_file:
        try:
            widget_exclude_filter_json = json.load(widget_settings_file).get(
                "exclude", []
            )
            if isinstance(widget_exclude_filter_json, list):
                widget_exclude_filter.extend(widget_exclude_filter_json)
        except json.JSONDecodeError as e:
            logger.info("Error loading widget filter settings -> %s", e)


def check_for_platform_extensions(fastapi_app, widgets_to_exclude) -> list:
    """Check for data-processing Platform extensions and add them to the widget exclude filter."""
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


widget_exclude_filter = check_for_platform_extensions(app, widget_exclude_filter)
openapi = app.openapi()
current_settings = get_user_settings(CURRENT_USER_SETTINGS)
widgets_json = get_widgets_json(
    build, openapi, widget_exclude_filter, EDITABLE, WIDGETS_PATH, app
)
APPS_PATH = (
    APPS_PATH
    if APPS_PATH
    else (
        current_settings.get("preferences", {}).get(
            "data_directory", HOME + "/OpenBBUserData"
        )
        + "/workspace_apps.json"
    )
)


@app.get("/")
async def root():
    """Serve the landing page HTML content."""
    html_path = Path(__file__).parent / "assets" / "landing_page.html"
    with open(html_path, encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


# Check if the app has already defined widgets.json at the root.
has_root_widgets = any(getattr(d, "path", "") == "/widgets.json" for d in app.routes)

if not has_root_widgets:
    # We assume that if an app already has /widgets.json at the app root,
    # we can leave it alone. Otherwise, use our endpoint to serve and/or generate.
    @app.get("/widgets.json")
    async def get_widgets():
        """Widgets configuration file for the OpenBB Workspace."""
        # This allows us to serve an edited widgets.json file without reloading the server.
        global FIRST_RUN  # noqa PLW0603  # pylint: disable=global-statement
        if FIRST_RUN is True:
            FIRST_RUN = False
            return JSONResponse(content=widgets_json, headers=obb_headers)
        if EDITABLE:
            return JSONResponse(
                content=get_widgets_json(
                    False, openapi, widget_exclude_filter, EDITABLE, WIDGETS_PATH, app
                ),
                headers=obb_headers,
            )
        return JSONResponse(content=widgets_json, headers=obb_headers)

else:
    # Populate the local name `get_widgets` with the endpoint function of the existing
    # root /widgets.json route so callers (e.g. get_apps_json) can await it.
    root_route = next(
        (r for r in app.routes if getattr(r, "path", "") == "/widgets.json"), None
    )
    if root_route and getattr(root_route, "endpoint", None):
        get_widgets = root_route.endpoint  # type: ignore
    else:
        # Fallback mechanism
        async def get_widgets():
            """Return the generated widgets.json"""
            return JSONResponse(content=widgets_json, headers=obb_headers)


# Check if the app has already defined apps.json at the root.
has_root_apps = any(getattr(d, "path", "") == "/apps.json" for d in app.routes)

if not has_root_apps:

    @app.get("/apps.json")
    async def get_apps_json():
        """Get the apps.json file."""
        new_templates: list = []
        default_templates: list = []
        widgets = await get_widgets()

        if not os.path.exists(APPS_PATH):
            apps_dir = os.path.dirname(APPS_PATH)
            if not os.path.exists(apps_dir):
                os.makedirs(apps_dir, exist_ok=True)
            # Write an empty file for the user to add exported apps from Workspace to.
            with open(APPS_PATH, "w", encoding="utf-8") as templates_file:
                templates_file.write(json.dumps([]))

        if os.path.exists(DEFAULT_APPS_PATH):
            with open(DEFAULT_APPS_PATH, encoding="utf-8") as f:
                default_templates = json.load(f)

        if has_additional_apps(app):
            additional_apps = await get_additional_apps(app)
            if additional_apps:
                for apps in additional_apps.values():
                    if not apps:
                        continue
                    if apps and isinstance(apps, list):
                        default_templates.extend(apps)
                    elif apps and not isinstance(apps, list):
                        logger.error(
                            "TypeError: Invalid apps.json format. Expected a list[dict] got %s instead -> %s",
                            type(apps),
                            str(apps),
                        )

        if os.path.exists(APPS_PATH):
            with open(APPS_PATH, encoding="utf-8") as templates_file:
                templates = json.load(templates_file)

            if isinstance(templates, dict):
                templates = [templates]

            templates.extend(default_templates)

            for template in templates:
                if _id := template.get("id"):
                    if _id in widgets and template not in new_templates:
                        new_templates.append(template)
                        continue
                elif template.get("layout") or template.get("tabs"):
                    if _tabs := template.get("tabs"):
                        for v in _tabs.values():
                            if v.get("layout", []) and all(
                                item.get("i") in widgets_json
                                for item in v.get("layout")
                            ):
                                new_templates.append(template)
                                break
                    elif (
                        template.get("layout")
                        and all(
                            item.get("i") in widgets_json for item in template["layout"]
                        )
                        and template not in new_templates
                    ):
                        new_templates.append(template)

            if new_templates:
                return JSONResponse(content=new_templates, headers=obb_headers)

        return JSONResponse(content=[], headers=obb_headers)


if AGENTS_PATH:

    @app.get("/agents.json")
    async def get_agents():
        """Get the agents.json file."""
        if os.path.exists(AGENTS_PATH):
            with open(AGENTS_PATH, encoding="utf-8") as f:
                agents = json.load(f)
            return JSONResponse(content=agents, headers=obb_headers)
        return JSONResponse(content={}, headers=obb_headers)


# Check if the app has already defined agents.json at the root.
has_root_agents = any(getattr(d, "path", "") == "/agents.json" for d in app.routes)

if not has_root_agents and has_additional_agents(app):

    @app.get("/agents.json")
    async def get_agents_json():  # type: ignore
        """Get the agents.json file."""
        new_agents: dict = {}
        additional_agents = await get_additional_agents(app)
        if additional_agents:
            for path_agents in additional_agents.values():
                for k, v in path_agents.items():
                    new_agents[k] = v
        return JSONResponse(content=new_agents, headers=obb_headers)

else:

    @app.get("/agents.json")
    async def get_agents_json():
        """Get an empty agents.json file."""
        return {}


def launch_api(**_kwargs):  # noqa PRL0912
    """Main function."""
    host = _kwargs.pop("host", os.getenv("OPENBB_API_HOST", "127.0.0.1"))
    if not host:
        logger.info(
            "OPENBB_API_HOST is set incorrectly. It should be an IP address or hostname."
        )
        host = input("Enter the host IP address or hostname: ")
        if not host:
            host = "127.0.0.1"

    port = _kwargs.pop("port", os.getenv("OPENBB_API_PORT", "6900"))

    try:
        port = int(port)
    except ValueError:
        logger.info("OPENBB_API_PORT is set incorrectly. It should be an port number.")
        port = input("Enter the port number: ")
        try:
            port = int(port)
        except ValueError:
            logger.info("Invalid port number. Defaulting to 6900.")
            port = 6900
    if port < 1025:
        port = 6900
        logger.info("Invalid port number, must be above 1024. Defaulting to 6900.")

    free_port = check_port(host, port)

    if free_port != port:
        logger.info("Port %d is already in use. Using port %d.", port, free_port)
        port = free_port

    if "use_colors" not in _kwargs:
        _kwargs["use_colors"] = "win" not in sys.platform or os.name != "nt"

    package_name = __package__
    _msg = (
        "\nTo access this data from OpenBB Workspace, use the link displayed after the application startup completes."
        "\nChrome is the recommended browser. Other browsers may conflict or require additional configuration."
        f"\n{f'Documentation is available at {app.docs_url}.' if app.docs_url else ''}"
    )
    logger.info(_msg)
    uvicorn.run(f"{package_name}.main:app", host=host, port=port, **_kwargs)


def main():
    """Launch the API."""
    launch_api(**kwargs)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
