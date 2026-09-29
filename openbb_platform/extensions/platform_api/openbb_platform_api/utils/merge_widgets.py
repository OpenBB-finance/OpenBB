"""Helper module for merging multiple Fast API endpoints returning widgets.json"""

from fastapi import FastAPI
from openbb_core.app.route_iter import iter_api_routes


def has_additional_widgets(app: FastAPI) -> bool:
    """Check for the existence of additional widgets.json endpoints."""
    for route in iter_api_routes(app):
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

    path_widgets: dict = {}

    # ``iter_api_routes`` resolves routes attached via ``include_router``,
    # which FastAPI 0.137+ wraps in ``_IncludedRouter`` rather than
    # flattening into ``app.routes``. ``original_route`` is the leaf
    # ``APIRoute`` whose ``endpoint`` we invoke.
    for route in iter_api_routes(app):
        path = getattr(route, "path", "")
        if path in {"/widgets.json", ""} or not path.endswith("widgets.json"):
            continue

        leaf = getattr(route, "original_route", route)
        endpoint = getattr(leaf, "endpoint", None)
        if endpoint is None:
            continue

        widgets = await endpoint()

        if not isinstance(widgets, dict):
            continue

        path_widgets[path.replace("widgets.json", "")] = dict(widgets.items())

    return path_widgets


def fix_router_widgets(path, widgets):
    """Restore the full API route path on every router-attached widget."""
    updated_widgets: dict = {}

    def _restore(value: str) -> str:
        if not value or "://" in value or value.startswith(path):
            return value
        return path + value.lstrip("/")

    for widget_id, widget in widgets.items():
        if not isinstance(widget, dict) or widget_id.endswith("/widgets.json"):
            continue

        new_widget: dict = widget.copy()

        if endpoint := widget.get("endpoint", ""):
            new_widget["endpoint"] = _restore(endpoint)
        if ws_endpoint := widget.get("wsEndpoint", ""):
            new_widget["wsEndpoint"] = _restore(ws_endpoint)
        if img_url := widget.get("imgUrl", ""):
            new_widget["imgUrl"] = _restore(img_url)

        new_params: list = []
        for param in widget.get("params", []):
            new_param: dict = param.copy()
            if endpoint := param.get("endpoint", ""):
                new_param["endpoint"] = _restore(endpoint)
            if opt_endpoint := param.get("optionsEndpoint", ""):
                new_param["optionsEndpoint"] = _restore(opt_endpoint)
            new_params.append(new_param)

        new_widget["params"] = new_params
        updated_widgets[new_widget.get("widgetId", widget_id)] = new_widget

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
