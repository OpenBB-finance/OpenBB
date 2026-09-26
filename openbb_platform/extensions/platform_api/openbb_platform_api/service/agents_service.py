"""Discover and merge router-attached ``agents.json`` endpoints.

Mirror of the ``apps_service`` flow: the launcher walks the FastAPI app's
routes for any whose path ends with ``agents.json`` (other than the
canonical root ``/agents.json``), calls each one, and folds the returned
agent definitions into the response served at ``/agents.json``.
"""

from fastapi import FastAPI
from openbb_core.app.route_iter import iter_api_routes


def has_additional_agents(app: FastAPI) -> bool:
    """Return ``True`` when the app has any non-root ``*agents.json`` route."""
    for route in iter_api_routes(app):
        path = getattr(route, "path", "")
        if path == "/agents.json":
            continue
        if path.endswith("agents.json"):
            return True
    return False


async def get_additional_agents(app: FastAPI) -> dict:
    """Collect ``agents`` dicts from every non-root ``*agents.json`` route.

    Returns ``{prefix: agents_dict}`` where ``prefix`` is the route's
    path stripped of the trailing ``agents.json``. Each agent's
    relative ``endpoints`` are rewritten to absolute paths under the
    route's prefix so Workspace can call them directly.
    """
    if not has_additional_agents(app):
        return {}

    path_agents: dict = {}

    # ``iter_api_routes`` resolves routes attached via ``include_router``,
    # which FastAPI 0.137+ wraps in ``_IncludedRouter`` rather than
    # flattening into ``app.routes``. ``original_route`` is the leaf
    # ``APIRoute`` whose ``endpoint`` we invoke.
    for route in iter_api_routes(app):
        path = getattr(route, "path", "")
        if path in {"/agents.json", ""} or not path.endswith("agents.json"):
            continue

        leaf = getattr(route, "original_route", route)
        endpoint = getattr(leaf, "endpoint", None)
        if endpoint is None:
            continue

        agents = await endpoint()

        if not isinstance(agents, dict):
            continue

        path = path.replace("agents.json", "")
        for k, v in agents.copy().items():
            endpoints = v.get("endpoints", {}) if isinstance(v, dict) else {}
            for name, endpoint_path in endpoints.items():
                if (
                    isinstance(endpoint_path, str)
                    and endpoint_path.startswith("/")
                    and not endpoint_path.startswith(path)
                ):
                    agents[k]["endpoints"][name] = path + endpoint_path[1:]

        path_agents[path] = agents

    return path_agents
