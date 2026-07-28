"""Route iteration helpers."""

from collections.abc import Iterator
from typing import Any

from fastapi.routing import APIRoute

_IncludedRouter: type | None = None
try:  # noqa: SIM105
    from fastapi.routing import (
        _IncludedRouter,  # type: ignore[attr-defined,no-redef]
    )
except ImportError:  # pragma: no cover
    pass


def iter_api_routes(router: Any) -> Iterator:
    """Yield prefix-resolved route descriptors from a router or app."""
    if not hasattr(router, "routes"):
        return
    for route in router.routes:
        if _IncludedRouter is not None and isinstance(route, _IncludedRouter):
            yield from route.effective_route_contexts()
        elif isinstance(route, APIRoute):
            yield route


def iter_included_routers(router: Any) -> Iterator:
    """Yield every original ``APIRouter`` reachable through ``include_router``."""
    if not hasattr(router, "routes") or _IncludedRouter is None:
        return
    for route in router.routes:
        if isinstance(route, _IncludedRouter):
            yield route.original_router
            yield from iter_included_routers(route.original_router)
