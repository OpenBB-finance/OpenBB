"""Helper module for merging multiple Fast API endpoints returning widgets.json"""

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute


def has_additional_widgets(app: FastAPI) -> bool:
    """Check for the existence of additional widgets.json endpoints."""
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        path = getattr(route, "path", "")
        if path == "/widgets.json":
            continue
        if path.endswith("widgets.json"):
            return True
    return False


async def get_additional_widgets(app: FastAPI) -> dict:
    """Collect widgets.json from non-root endpoints."""
    if not has_additional_widgets(app):
        return {}

    widget_routes: list[BaseRoute] = []
    for d in app.routes:
        d_path = getattr(d, "path", "")
        if d_path not in {"/widgets.json", ""} and d_path.endswith("widgets.json"):
            widget_routes.append(d)

    path_widgets: dict = {}

    for r in widget_routes:
        if (
            not getattr(r, "endpoint", None)
            or getattr(r, "path", "") == "/widgets.json"
        ):
            continue

        widgets = await r.endpoint()  # type: ignore

        if not isinstance(widgets, dict):
            continue

        path = getattr(r, "path", "")
        path_widgets[path.replace("widgets.json", "")] = dict(widgets.items())

    return path_widgets


def fix_router_widgets(path, widgets):
    """Append the API prefix and path to the function, if necessary."""
    updated_widgets: dict = {}
    for widget_id, widget in widgets.items():
        if not isinstance(widget, dict) or widget_id.endswith("/widgets.json"):
            continue

        new_widget: dict = widget.copy()
        params = widget.get("params", [])

        if (endpoint := widget.get("endpoint", "")) and not endpoint.startswith(path):
            new_widget["endpoint"] = (
                path + endpoint[1:] if endpoint.startswith("/") else endpoint
            )

        if (
            (ws_endpoint := widget.get("wsEndpoint", ""))
            and "://" not in ws_endpoint
            and not ws_endpoint.startswith(path)
        ):
            new_widget["wsEndpoint"] = (
                path + ws_endpoint[1:] if ws_endpoint.startswith("/") else ws_endpoint
            )

        if (
            (img_url := widget.get("imgUrl", ""))
            and "://" not in img_url
            and not img_url.startswith(path)
        ):
            new_widget["imgUrl"] = (
                path + img_url[1:] if img_url.startswith("/") else img_url
            )

        new_params: list = []

        for param in params:
            new_param: dict = param.copy()

            if (
                (endpoint := param.get("endpoint", ""))
                and "://" not in endpoint
                and not endpoint.startswith(path)
            ):
                new_param["endpoint"] = (
                    path + endpoint[1:] if endpoint.startswith("/") else endpoint
                )

            if (
                (opt_endpoint := param.get("optionsEndpoint", ""))
                and "://" not in opt_endpoint
                and not opt_endpoint.startswith(path)
            ):
                new_param["optionsEndpoint"] = (
                    path + opt_endpoint[1:]
                    if opt_endpoint.startswith("/")
                    else opt_endpoint
                )

            new_params.append(new_param)

        new_widget["params"] = new_params
        updated_widgets[new_widget.get("widgetId", new_widget["endpoint"])] = new_widget

    return updated_widgets


async def get_and_fix_widget_paths(app: FastAPI):
    """Fix the endpoint definitions to account for the prefix."""
    path_widgets = await get_additional_widgets(app)

    if not path_widgets:
        return {}

    for path, widgets in path_widgets.copy().items():
        new_widgets = fix_router_widgets(path.replace("widgets.json", ""), widgets)
        if new_widgets:
            path_widgets[path.replace("widgets.json", "")] = new_widgets
    return path_widgets
