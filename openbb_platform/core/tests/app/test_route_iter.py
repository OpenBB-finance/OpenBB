"""Tests for the ``route_iter`` helpers."""

from fastapi import APIRouter

from openbb_core.app import route_iter
from openbb_core.app.route_iter import iter_api_routes, iter_included_routers


def test_iter_api_routes_object_without_routes():
    """An object that exposes no ``routes`` attribute yields nothing."""
    assert list(iter_api_routes(object())) == []


def test_iter_included_routers_object_without_routes():
    """An object that exposes no ``routes`` attribute yields nothing."""
    assert list(iter_included_routers(object())) == []


def test_iter_included_routers_without_included_router_support(monkeypatch):
    """Without ``_IncludedRouter`` support there is nothing to walk into."""
    inner = APIRouter()
    outer = APIRouter()
    outer.include_router(inner, prefix="/inner")

    monkeypatch.setattr(route_iter, "_IncludedRouter", None)
    assert list(iter_included_routers(outer)) == []
