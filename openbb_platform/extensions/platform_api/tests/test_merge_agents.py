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
