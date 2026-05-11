"""Discover and merge router-attached ``apps.json`` endpoints.

User code can ship its own ``apps.json``-shaped endpoint by registering
a route whose path *ends* with ``apps.json`` (anything other than the
canonical root ``/apps.json``). The launcher walks those routes, calls
each one, and folds the returned templates into the catalogue served at
``/apps.json``.
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute


def has_additional_apps(app: FastAPI) -> bool:
    """Return ``True`` when the app has any non-root ``*apps.json`` route."""
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
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

    # Narrow to ``APIRoute`` at collection so ``r.endpoint`` is typed
    # below. ``BaseRoute`` doesn't expose ``endpoint``.
    apps_routes: list[APIRoute] = []
    for d in app.routes:
        if not isinstance(d, APIRoute):
            continue
        d_path = getattr(d, "path", "")
        if d_path not in {"/apps.json", ""} and d_path.endswith("apps.json"):
            apps_routes.append(d)

    path_apps: dict = {}

    for r in apps_routes:
        if not getattr(r, "endpoint", None) or getattr(r, "path", "") == "/apps.json":
            continue

        apps = await r.endpoint()

        if not isinstance(apps, list):
            continue

        path = getattr(r, "path", "")
        path_apps[path.replace("apps.json", "")] = apps

    return path_apps
