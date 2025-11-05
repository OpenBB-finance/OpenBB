"""Test merge_apps module."""

import pytest
from fastapi import FastAPI
from openbb_platform_api.utils.merge_apps import (
    get_additional_apps,
    has_additional_apps,
)


def _build_app(include_extra: bool = False, extra_returns_list: bool = True) -> FastAPI:
    app = FastAPI()

    @app.get("/apps.json")
    async def root_apps():
        return [{"appId": "root", "endpoint": "/root"}]

    if include_extra:

        @app.get("/module/apps.json")
        async def module_apps():
            if extra_returns_list:
                return [{"appId": "module", "endpoint": "/module/data"}]
            return "not-a-list"

    return app


def test_has_additional_apps_false_without_extra_routes():
    app = _build_app(include_extra=False)
    assert not has_additional_apps(app)


def test_has_additional_apps_true_with_extra_routes():
    app = _build_app(include_extra=True)
    assert has_additional_apps(app)


@pytest.mark.asyncio
async def test_get_additional_apps_returns_empty_when_none():
    app = _build_app(include_extra=False)
    assert await get_additional_apps(app) == {}


@pytest.mark.asyncio
async def test_get_additional_apps_skips_non_list_responses():
    app = _build_app(include_extra=True, extra_returns_list=False)
    assert await get_additional_apps(app) == {}


@pytest.mark.asyncio
async def test_get_additional_apps_collects_valid_routes():
    app = _build_app(include_extra=True)
    apps = await get_additional_apps(app)
    assert apps == {"/module/": [{"appId": "module", "endpoint": "/module/data"}]}
