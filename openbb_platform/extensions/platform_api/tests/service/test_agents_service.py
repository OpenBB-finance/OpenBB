"""Test merge_agents module."""

import pytest
from fastapi import FastAPI

from openbb_platform_api.utils.merge_agents import (
    get_additional_agents,
    has_additional_agents,
)


def _build_app(include_extra: bool = False, extra_returns_dict: bool = True) -> FastAPI:
    app = FastAPI()

    @app.get("/agents.json")
    async def root_agents():
        return {"root": {"id": "root-agent"}}

    if include_extra:

        @app.get("/module/agents.json")
        async def module_agents():
            if extra_returns_dict:
                return {"module": {"id": "module-agent"}}
            return ["not-a-dict"]

    return app


def test_has_additional_agents_false_without_extra_routes():
    app = _build_app(include_extra=False)
    assert not has_additional_agents(app)


def test_has_additional_agents_true_with_extra_routes():
    app = _build_app(include_extra=True)
    assert has_additional_agents(app)


@pytest.mark.asyncio
async def test_get_additional_agents_returns_empty_when_none():
    app = _build_app(include_extra=False)
    assert await get_additional_agents(app) == {}


@pytest.mark.asyncio
async def test_get_additional_agents_collects_valid_routes():
    app = _build_app(include_extra=True)
    additional = await get_additional_agents(app)
    assert additional == {"/module/": {"module": {"id": "module-agent"}}}


@pytest.mark.asyncio
async def test_get_additional_agents_skips_non_dict_responses():
    app = _build_app(include_extra=True, extra_returns_dict=False)
    assert await get_additional_agents(app) == {}


@pytest.mark.asyncio
async def test_get_additional_agents_skips_routes_with_no_endpoint_or_root_path():
    """Routes without an ``endpoint`` attr (defensive) and routes whose
    path is the root ``/agents.json`` get skipped during the merge —
    we only iterate over additional, non-root routes.
    """
    from fastapi.routing import APIRoute

    app = FastAPI()

    @app.get("/module/agents.json")
    async def module_agents():
        return {"module": {"id": "module-agent"}}

    # Stub a route with endpoint=None to exercise the
    # ``not getattr(r, "endpoint", None)`` skip.
    fake_route = APIRoute(
        path="/garbage/agents.json",
        endpoint=lambda: None,
        methods=["GET"],
    )
    fake_route.endpoint = None  # ty: ignore[invalid-assignment]
    app.routes.append(fake_route)

    result = await get_additional_agents(app)
    # Only the well-formed module route survived.
    assert "/module/" in result
    assert "/garbage/" not in result


@pytest.mark.asyncio
async def test_get_additional_agents_rewrites_relative_endpoint_paths():
    """Each agent's ``endpoints`` get prefixed with the route's path
    (when they're absolute and not already prefixed) so Workspace can
    call them directly.
    """
    app = FastAPI()

    @app.get("/myrouter/agents.json")
    async def router_agents():
        return {
            "agent_a": {
                "endpoints": {
                    "tool1": "/tool1",  # relative, will get prefixed
                    "tool2": "/myrouter/tool2",  # already prefixed, untouched
                    "tool3": "https://other-host.example/x",  # not "/", untouched
                }
            }
        }

    result = await get_additional_agents(app)
    rewritten = result["/myrouter/"]["agent_a"]["endpoints"]
    assert rewritten["tool1"] == "/myrouter/tool1"
    assert rewritten["tool2"] == "/myrouter/tool2"
    assert rewritten["tool3"] == "https://other-host.example/x"


@pytest.mark.asyncio
async def test_get_additional_agents_handles_non_dict_agent_value():
    """Defensive: an agent whose value isn't a dict (e.g. a string) is
    handled without crashing the prefix-rewrite loop.
    """
    app = FastAPI()

    @app.get("/x/agents.json")
    async def router_agents():
        return {"agent": "not a dict"}

    result = await get_additional_agents(app)
    # Survived without raising; the non-dict agent is preserved as-is.
    assert result["/x/"]["agent"] == "not a dict"
