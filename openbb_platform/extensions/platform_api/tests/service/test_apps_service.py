"""Test apps_service module."""

import pytest
from fastapi import APIRouter, FastAPI

from openbb_platform_api.utils.merge_apps import (
    get_additional_apps,
    has_additional_apps,
)


def _build_app(include_extra: bool = False, extra_returns_list: bool = True) -> FastAPI:
    app = FastAPI()

    @app.get("/apps.json")
    async def root_apps():
        return [{"appId": "root", "endpoint": "/root"}]

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    if include_extra:

        @app.get("/module/apps.json")
        async def module_apps():
            if extra_returns_list:
                return [{"appId": "module", "endpoint": "/module/data"}]
            return "not-a-list"

    return app


def _build_included_app() -> FastAPI:
    """Attach an apps.json route via ``include_router``.

    FastAPI 0.137+ wraps included routes in ``_IncludedRouter`` instead
    of flattening them into ``app.routes``, so the merge must walk the
    routes through ``iter_api_routes`` to find them.
    """
    app = FastAPI()

    @app.get("/apps.json")
    async def root_apps():
        return [{"appId": "root"}]

    sub = APIRouter()

    @sub.get("/apps.json")
    async def sub_apps():
        return [{"appId": "module", "endpoint": "/sub/data"}]

    app.include_router(sub, prefix="/sub")
    return app


def test_has_additional_apps_false_without_extra_routes():
    app = _build_app(include_extra=False)
    assert not has_additional_apps(app)


def test_has_additional_apps_true_with_extra_routes():
    app = _build_app(include_extra=True)
    assert has_additional_apps(app)


def test_has_additional_apps_true_with_included_router():
    """An apps.json route attached via include_router is detected (0.137+)."""
    app = _build_included_app()
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


@pytest.mark.asyncio
async def test_get_additional_apps_collects_from_included_router():
    """An apps.json route added via include_router is collected (0.137+ guard)."""
    app = _build_included_app()
    apps = await get_additional_apps(app)
    assert apps == {"/sub/": [{"appId": "module", "endpoint": "/sub/data"}]}


@pytest.mark.asyncio
async def test_get_additional_apps_skips_routes_with_no_endpoint_or_root_path():
    """Routes whose endpoint is None or whose path is the root
    ``/apps.json`` are explicitly skipped during the merge.
    """
    from fastapi.routing import APIRoute

    app = FastAPI()

    @app.get("/module/apps.json")
    async def module_apps():
        return [{"appId": "module"}]

    fake_route = APIRoute(
        path="/garbage/apps.json",
        endpoint=lambda: None,
        methods=["GET"],
    )
    fake_route.endpoint = None  # ty: ignore[invalid-assignment]
    app.routes.append(fake_route)

    result = await get_additional_apps(app)
    assert "/module/" in result
    assert "/garbage/" not in result
