"""Macro regime SSE route registration tests."""

from __future__ import annotations

from fastapi import FastAPI
from openbb_quant_ml import macro_router


def test_regime_stream_route_is_registered() -> None:
    app = FastAPI()
    app.include_router(macro_router.router.api_router)

    matches = [route for route in app.routes if getattr(route, "path", "") == "/macro/regime/stream"]
    assert matches, "regime stream route is not registered"
    methods = set().union(*(getattr(route, "methods", set()) for route in matches))
    assert "GET" in methods
