"""Discover and merge router-attached ``agents.json`` endpoints.

Mirror of the ``apps_service`` flow: the launcher walks the FastAPI app's
routes for any whose path ends with ``agents.json`` (other than the
canonical root ``/agents.json``), calls each one, and folds the returned
agent definitions into the response served at ``/agents.json``.
"""

from fastapi import FastAPI
from fastapi.routing import APIRoute


def has_additional_agents(app: FastAPI) -> bool:
    """Return ``True`` when the app has any non-root ``*agents.json`` route."""
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
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

    # Narrow to ``APIRoute`` at collection time so ``r.endpoint`` is
    # strictly typed below. Bare ``BaseRoute`` doesn't expose ``endpoint``,
    # which is the launcher-only callable we want to invoke.
    agents_routes: list[APIRoute] = []
    for d in app.routes:
        if not isinstance(d, APIRoute):
            continue
        d_path = getattr(d, "path", "")
        if d_path not in {"/agents.json", ""} and d_path.endswith("agents.json"):
            agents_routes.append(d)

    path_agents: dict = {}

    for r in agents_routes:
        if not getattr(r, "endpoint", None) or getattr(r, "path", "") == "/agents.json":
            continue

        agents = await r.endpoint()

        if not isinstance(agents, dict):
            continue

        path = getattr(r, "path", "").replace("agents.json", "")
        for k, v in agents.copy().items():
            endpoints = v.get("endpoints", {}) if isinstance(v, dict) else {}
            for name, endpoint in endpoints.items():
                if (
                    isinstance(endpoint, str)
                    and endpoint.startswith("/")
                    and not endpoint.startswith(path)
                ):
                    new_endpoint = path + endpoint[1:]
                    agents[k]["endpoints"][name] = new_endpoint

        path_agents[path] = agents

    return path_agents
