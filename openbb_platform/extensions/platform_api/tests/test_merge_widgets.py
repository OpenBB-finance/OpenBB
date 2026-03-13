"""Test merge_widgets module."""

import copy

import pytest
from fastapi import FastAPI
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


def test_has_additional_widgets_false_without_extra_routes():
    app = _build_app(include_extra=False)
    assert not has_additional_widgets(app)


def test_has_additional_widgets_true_with_extra_routes():
    app = _build_app(include_extra=True)
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
