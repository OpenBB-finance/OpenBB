"""Discover and merge router-attached ``apps.json`` endpoints.

User code can ship its own ``apps.json``-shaped endpoint by registering
a route whose path *ends* with ``apps.json`` (anything other than the
canonical root ``/apps.json``). The launcher walks those routes, calls
each one, and folds the returned templates into the catalogue served at
``/apps.json``.
"""

from fastapi import FastAPI
from openbb_core.app.route_iter import iter_api_routes


def has_additional_apps(app: FastAPI) -> bool:
    """Return ``True`` when the app has any non-root ``*apps.json`` route."""
    for route in iter_api_routes(app):
        path = getattr(route, "path", "")
        if path == "/apps.json":
            continue
        if path.endswith("apps.json"):
            return True
    return False


async def get_additional_apps(app: FastAPI) -> dict:
    """Collect ``apps`` lists from every non-root ``*apps.json`` route.

    Returns ``{prefix: [app, ...]}`` where ``prefix`` is the route's
    path stripped of the trailing ``apps.json``. Routes whose endpoint
    returns a non-list payload are skipped — the merger expects each
    fragment to be a list of app templates.
    """
    if not has_additional_apps(app):
        return {}

    path_apps: dict = {}

    # ``iter_api_routes`` resolves routes attached via ``include_router``,
    # which FastAPI 0.137+ wraps in ``_IncludedRouter`` rather than
    # flattening into ``app.routes``. ``original_route`` is the leaf
    # ``APIRoute`` whose ``endpoint`` we invoke.
    for route in iter_api_routes(app):
        path = getattr(route, "path", "")
        if path in {"/apps.json", ""} or not path.endswith("apps.json"):
            continue

        leaf = getattr(route, "original_route", route)
        endpoint = getattr(leaf, "endpoint", None)
        if endpoint is None:
            continue

        apps = await endpoint()

        if not isinstance(apps, list):
            continue

        path_apps[path.replace("apps.json", "")] = apps

    return path_apps
