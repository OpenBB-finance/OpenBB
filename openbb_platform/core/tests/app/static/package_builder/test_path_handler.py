"""Extended coverage tests for PathHandler."""

from unittest.mock import MagicMock

from openbb_core.app.router import Router
from openbb_core.app.static.package_builder.path_handler import PathHandler


def _make_router_with_dotted_route():
    """Create a Router that has a route with '.' in path (excluded from initial map)."""
    from fastapi import APIRouter as FastAPIRouter

    async def endpoint_fn() -> None:
        pass

    inner = FastAPIRouter()
    inner.add_api_route("/some.dotted/route", endpoint_fn, methods=["GET"])
    r = Router()
    r._api_router = inner
    return r


def test_build_route_map_collects_dotted_path_routes(monkeypatch):
    """Test collect_api_router_routes adds routes with dots in path that were excluded
    from the initial route_map build."""
    r = _make_router_with_dotted_route()
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.path_handler.RouterLoader.from_extensions",
        lambda: r,
    )
    route_map = PathHandler.build_route_map()
    assert "/some.dotted/route" in route_map


def test_build_route_map_skips_non_apiroute(monkeypatch):
    """Test continue when route in api_router.routes is not an APIRoute."""
    from fastapi import APIRouter as FastAPIRouter

    async def real_endpoint() -> None:
        pass

    inner = FastAPIRouter()
    inner.add_api_route("/legit/path", real_endpoint, methods=["GET"])

    r = Router()
    r._api_router = inner

    mock_mount = MagicMock(spec=[])  # NOT an APIRoute instance
    r._api_router.routes.append(mock_mount)

    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.path_handler.RouterLoader.from_extensions",
        lambda: r,
    )
    route_map = PathHandler.build_route_map()
    assert isinstance(route_map, dict)


def test_build_route_map_recurses_into_endpoint_self(monkeypatch):
    """Test collect_api_router_routes recurses when endpoint has __self__."""
    from fastapi import APIRouter as FastAPIRouter

    async def inner_endpoint() -> None:
        pass

    inner_router = FastAPIRouter()
    inner_router.add_api_route("/inner/route", inner_endpoint, methods=["GET"])

    sub = Router()
    sub._api_router = inner_router

    async def outer_endpoint() -> None:
        pass

    outer_router = FastAPIRouter()
    outer_router.add_api_route("/outer/path", outer_endpoint, methods=["GET"])

    outer_route = outer_router.routes[0]
    outer_route.endpoint.__self__ = sub  # type: ignore[attr-defined]

    r = Router()
    r._api_router = outer_router

    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.path_handler.RouterLoader.from_extensions",
        lambda: r,
    )
    route_map = PathHandler.build_route_map()
    assert isinstance(route_map, dict)


def test_get_router_dependencies_skips_falsy_api_router(monkeypatch):
    """Test continue when api_router is falsy for a candidate path."""
    mock_router = MagicMock()
    mock_router.get_attr.return_value = None
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.path_handler.RouterLoader.from_extensions",
        lambda: mock_router,
    )
    result = PathHandler.get_router_dependencies("/equity/price")
    assert result == []


def test_get_child_path_list_adds_direct_child(monkeypatch):
    """Test direct_children.append when route_path is a direct child."""
    monkeypatch.setattr(
        PathHandler,
        "build_route_map",
        staticmethod(lambda: {"/equity/{symbol}": MagicMock()}),
    )
    result = PathHandler.get_child_path_list("/equity", [])
    assert "/equity/{symbol}" in result


def test_get_router_description_returns_description(monkeypatch):
    """Test returns description when the router has one set."""
    mock_router = MagicMock()
    mock_router.get_attr.return_value = "My router description"
    monkeypatch.setattr(
        "openbb_core.app.static.package_builder.path_handler.RouterLoader.from_extensions",
        lambda: mock_router,
    )
    result = PathHandler.get_router_description("/equity")
    assert result == "My router description"
