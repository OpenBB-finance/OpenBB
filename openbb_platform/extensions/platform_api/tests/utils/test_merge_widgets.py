"""Test merge_widgets module."""

import copy

import pytest
from fastapi import APIRouter, FastAPI

from openbb_platform_api.utils.merge_widgets import (
    fix_router_widgets,
    get_additional_widgets,
    get_and_fix_widget_paths,
    has_additional_widgets,
)


def _build_app(include_extra: bool = False, extra_returns_dict: bool = True) -> FastAPI:
    app = FastAPI()

    @app.get("/widgets.json")
    async def root_widgets():
        return {"root": {"widgetId": "root", "endpoint": "/root"}}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    if include_extra:

        @app.get("/module/widgets.json")
        async def module_widgets():
            if extra_returns_dict:
                return {
                    "module": {
                        "widgetId": "module",
                        "endpoint": "/module/data",
                        "params": [],
                    }
                }
            return "not-a-dict"

    return app


def _build_included_app() -> FastAPI:
    """Attach a widgets.json route via ``include_router``.

    FastAPI 0.137+ wraps included routes in ``_IncludedRouter`` instead
    of flattening them into ``app.routes``, so the merge must walk the
    routes through ``iter_api_routes`` to find them.
    """
    app = FastAPI()

    @app.get("/widgets.json")
    async def root_widgets():
        return {"root": {"widgetId": "root", "endpoint": "/root"}}

    sub = APIRouter()

    @sub.get("/widgets.json")
    async def sub_widgets():
        return {
            "module": {
                "widgetId": "module",
                "endpoint": "/sub/data",
                "params": [],
            }
        }

    app.include_router(sub, prefix="/sub")
    return app


def test_has_additional_widgets_false_without_extra_routes():
    app = _build_app(include_extra=False)
    assert not has_additional_widgets(app)


def test_has_additional_widgets_true_with_extra_routes():
    app = _build_app(include_extra=True)
    assert has_additional_widgets(app)


def test_has_additional_widgets_true_with_included_router():
    """A widgets.json route attached via include_router is detected (0.137+)."""
    app = _build_included_app()
    assert has_additional_widgets(app)


@pytest.mark.asyncio
async def test_get_additional_widgets_returns_empty_when_none():
    app = _build_app(include_extra=False)
    assert await get_additional_widgets(app) == {}


@pytest.mark.asyncio
async def test_get_additional_widgets_skips_non_dict_responses():
    app = _build_app(include_extra=True, extra_returns_dict=False)
    assert await get_additional_widgets(app) == {}


@pytest.mark.asyncio
async def test_get_additional_widgets_collects_valid_routes():
    app = _build_app(include_extra=True)
    widgets = await get_additional_widgets(app)
    assert widgets == {
        "/module/": {
            "module": {
                "widgetId": "module",
                "endpoint": "/module/data",
                "params": [],
            }
        }
    }


@pytest.mark.asyncio
async def test_get_additional_widgets_collects_from_included_router():
    """A widgets.json route added via include_router is collected (0.137+ guard)."""
    app = _build_included_app()
    widgets = await get_additional_widgets(app)
    assert widgets == {
        "/sub/": {
            "module": {
                "widgetId": "module",
                "endpoint": "/sub/data",
                "params": [],
            }
        }
    }


@pytest.mark.asyncio
async def test_get_additional_widgets_skips_routes_with_no_endpoint():
    """A route entry whose ``endpoint`` is missing/None gets skipped."""
    from fastapi.routing import APIRoute

    app = FastAPI()

    @app.get("/module/widgets.json")
    async def module_widgets():
        return {"module": {"widgetId": "module"}}

    fake_route = APIRoute(
        path="/garbage/widgets.json",
        endpoint=lambda: None,
        methods=["GET"],
    )
    fake_route.endpoint = None  # ty: ignore[invalid-assignment]
    app.routes.append(fake_route)

    result = await get_additional_widgets(app)
    assert "/module/" in result
    assert "/garbage/" not in result


def test_fix_router_widgets_updates_nested_paths_without_mutating_source():
    original = {
        "widgetA": {
            "widgetId": "widgetA",
            "endpoint": "/data",
            "wsEndpoint": "/stream",
            "imgUrl": "/images/icon.png",
            "params": [
                {
                    "name": "param1",
                    "endpoint": "/param",
                    "optionsEndpoint": "/param/options",
                },
                {"name": "param2", "endpoint": "http://external/api"},
            ],
        },
        "widgetB/widgets.json": {"endpoint": "/should/skip"},
        "not_a_dict": "skip_me",
    }
    snapshot = copy.deepcopy(original)
    updated = fix_router_widgets("/api/", original)

    assert snapshot == original
    assert list(updated.keys()) == ["widgetA"]
    widget = updated["widgetA"]
    assert widget["endpoint"] == "/api/data"
    assert widget["wsEndpoint"] == "/api/stream"
    assert widget["imgUrl"] == "/api/images/icon.png"
    assert widget["params"][0]["endpoint"] == "/api/param"
    assert widget["params"][0]["optionsEndpoint"] == "/api/param/options"
    assert widget["params"][1]["endpoint"] == "http://external/api"


def test_fix_router_widgets_leaves_prefixed_and_missing_fields_untouched():
    """Already-prefixed or absent endpoint/wsEndpoint/imgUrl are left as-is."""
    widgets = {
        "widgetA": {
            "widgetId": "widgetA",
            "endpoint": "/api/data",
        }
    }
    updated = fix_router_widgets("/api/", widgets)
    assert updated["widgetA"]["endpoint"] == "/api/data"
    assert "wsEndpoint" not in updated["widgetA"]
    assert "imgUrl" not in updated["widgetA"]
    assert updated["widgetA"]["params"] == []


def test_fix_router_widgets_skips_external_and_missing_optional_fields():
    """External (scheme) wsEndpoint/imgUrl and missing param fields are skipped."""
    widgets = {
        "widgetA": {
            "widgetId": "widgetA",
            "endpoint": "/data",
            "wsEndpoint": "wss://external/stream",
            "imgUrl": "https://external/icon.png",
            "params": [
                {
                    "name": "param1",
                    "endpoint": "https://x/y",
                    "optionsEndpoint": "ws://z",
                }
            ],
        }
    }
    updated = fix_router_widgets("/api/", widgets)
    assert updated["widgetA"]["endpoint"] == "/api/data"
    assert updated["widgetA"]["wsEndpoint"] == "wss://external/stream"
    assert updated["widgetA"]["imgUrl"] == "https://external/icon.png"
    assert updated["widgetA"]["params"][0]["endpoint"] == "https://x/y"
    assert updated["widgetA"]["params"][0]["optionsEndpoint"] == "ws://z"


@pytest.mark.asyncio
async def test_get_and_fix_widget_paths_integrates_collection_and_fixing():
    app = FastAPI()

    @app.get("/widgets.json")
    async def root_widgets():
        return {}

    @app.get("/api/widgets.json")
    async def api_widgets():
        return {
            "first": {
                "widgetId": "first",
                "endpoint": "/data",
                "wsEndpoint": "/stream",
                "imgUrl": "/assets/icon.png",
                "params": [{"endpoint": "/param"}],
            },
            "ignore": "non-dict",
        }

    result = await get_and_fix_widget_paths(app)
    assert "/api/" in result
    fixed = result["/api/"]["first"]
    assert fixed["endpoint"] == "/api/data"
    assert fixed["wsEndpoint"] == "/api/stream"
    assert fixed["imgUrl"] == "/api/assets/icon.png"
    assert fixed["params"][0]["endpoint"] == "/api/param"


@pytest.mark.asyncio
async def test_get_and_fix_widget_paths_returns_empty_when_no_additional_widgets():
    """When no router-attached widget routes are present, the wrapped
    path-fix pass short-circuits to ``{}``.
    """
    app = FastAPI()

    @app.get("/widgets.json")
    async def root_widgets():
        return {}

    result = await get_and_fix_widget_paths(app)
    assert result == {}


@pytest.mark.asyncio
async def test_get_and_fix_widget_paths_keeps_paths_when_no_widgets_are_fixable():
    """When every widget on a path is skipped, the path is left unchanged."""
    app = FastAPI()

    @app.get("/widgets.json")
    async def root_widgets():
        return {}

    @app.get("/api/widgets.json")
    async def api_widgets():
        return {"skip/widgets.json": {"endpoint": "/x"}, "bad": "non-dict"}

    result = await get_and_fix_widget_paths(app)
    assert result == {
        "/api/": {"skip/widgets.json": {"endpoint": "/x"}, "bad": "non-dict"}
    }
