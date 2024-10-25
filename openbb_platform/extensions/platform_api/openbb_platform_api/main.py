"""OpenBB Platform API.

Launch script and widgets builder for the OpenBB Terminal Custom Backend.
"""

import json
import logging
import os
import sys

import uvicorn
from fastapi.responses import JSONResponse
from openbb_core.api.rest_api import app

from .utils.api import check_port, get_user_settings, get_widgets_json, parse_args

logger = logging.getLogger("openbb_platform_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("\n%(message)s\n")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


FIRST_RUN = True

HOME = os.environ.get("HOME") or os.environ.get("USERPROFILE")

if not HOME:
    raise ValueError("HOME or USERPROFILE environment variable not set.")

CURRENT_USER_SETTINGS = os.path.join(HOME, ".openbb_platform", "user_settings.json")
USER_SETTINGS_COPY = os.path.join(HOME, ".openbb_platform", "user_settings_backup.json")

# Widget filtering is optional and can be used to exclude widgets from the widgets.json file
# You can generate this filter on OpenBB Hub: https://my.openbb.co/app/platform/widgets
WIDGET_SETTINGS = os.path.join(HOME, ".openbb_platform", "widget_settings.json")

kwargs = parse_args()
build = kwargs.pop("build", True)
build = False if kwargs.pop("no-build", None) else build
login = kwargs.pop("login", False)
dont_filter = kwargs.pop("no-filter", False)
widget_exclude_filter: list = []

if not dont_filter and os.path.exists(WIDGET_SETTINGS):
    with open(WIDGET_SETTINGS) as f:
        try:
            widget_exclude_filter = json.load(f)["exclude"]
        except json.JSONDecodeError as e:
            logger.info("Error loading widget filter settings -> %s", e)


openapi = app.openapi()

# We don't need the current settings,
# but we need to call the function to update, login, and/or identify the settings file.
current_settings = get_user_settings(login, CURRENT_USER_SETTINGS, USER_SETTINGS_COPY)

widgets_json = get_widgets_json(build, openapi, widget_exclude_filter)


@app.get("/")
async def get_root():
    """Root response and welcome message."""
    return JSONResponse(
        content="Welcome to the OpenBB Platform API."
        + " Learn how to connect to Pro in https://docs.openbb.co/pro/custom-backend,"
        + " or see the API documentation here: /docs"
    )


@app.get("/widgets.json")
async def get_widgets():
    """Widgets configuration file for the OpenBB Terminal Pro."""
    # This allows us to serve an edited widgets.json file without reloading the server.
    global FIRST_RUN  # noqa PLW0603  # pylint: disable=global-statement
    if FIRST_RUN is True:
        FIRST_RUN = False
        return JSONResponse(content=widgets_json)
    return JSONResponse(content=get_widgets_json(False, openapi, widget_exclude_filter))


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

    try:
        package_name = __package__
        logger.info(
            "\nTo access this data from OpenBB Terminal, use the link displayed after the application startup completes."
            "\nChrome is the recommended browser. Other browsers may conflict or require additional configuration."
            "\nDocumentation is available at /docs."
        )
        uvicorn.run(f"{package_name}.main:app", host=host, port=port, **_kwargs)
    finally:
        # If user_settings_copy.json exists, then restore the original settings.
        if os.path.exists(USER_SETTINGS_COPY):
            logger.info("Restoring the original settings.")
            os.replace(USER_SETTINGS_COPY, CURRENT_USER_SETTINGS)


def main():
    """Launch the API."""
    launch_api(**kwargs)


if __name__ == "__main__":

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
