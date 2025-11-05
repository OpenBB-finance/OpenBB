"""Helper module for merging multiple Fast API endpoints returning agents.json"""

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute


def has_additional_agents(app: FastAPI) -> bool:
    """Check for the existence of additional agents.json endpoints."""
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
    """Collect agents.json from non-root endpoints."""
    if not has_additional_agents(app):
        return {}

    agents_routes: list[BaseRoute] = []
    for d in app.routes:
        d_path = getattr(d, "path", "")
        if d_path not in {"/agents.json", ""} and d_path.endswith("agents.json"):
            agents_routes.append(d)

    path_agents: dict = {}

    for r in agents_routes:
        if not getattr(r, "endpoint", None) or getattr(r, "path", "") == "/agents.json":
            continue

        agents = await r.endpoint()  # type: ignore

        if not isinstance(agents, dict):
            continue

        path = getattr(r, "path", "")
        path_agents[path.replace("agents.json", "")] = agents

    return path_agents
