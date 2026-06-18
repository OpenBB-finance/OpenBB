"""Tests for ``openbb_mcp_server.app.middleware``."""

import sys
import types

import pytest
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

from openbb_mcp_server.app.middleware import (
    _hook_to_middleware,
    _resolve_entrypoint,
    _validate_middleware_callable,
    build_hook_middleware,
)


@pytest.fixture
def fake_hook_module(request):
    """Register a unique stub module under sys.modules and clean up after."""
    name = f"test_mcp_hook_{request.node.name}"
    module = types.ModuleType(name)
    sys.modules[name] = module
    yield name, module
    sys.modules.pop(name, None)


def test_resolve_entrypoint_returns_attribute(fake_hook_module):
    """``module:attr`` walks the module + attribute chain."""
    name, module = fake_hook_module

    async def hook(request, call_next):
        return await call_next(request)

    module.hook = hook
    out = _resolve_entrypoint(f"{name}:hook")
    assert out is hook


def test_resolve_entrypoint_walks_dotted_attr(fake_hook_module):
    """``module:Class.method`` resolves the dotted attribute chain."""
    name, module = fake_hook_module

    class Thing:
        async def m(self, request, call_next):  # pragma: no cover
            return await call_next(request)

    module.Thing = Thing
    out = _resolve_entrypoint(f"{name}:Thing.m")
    assert out is Thing.m


def test_resolve_entrypoint_requires_colon():
    """Missing ``:`` separator raises ValueError."""
    with pytest.raises(ValueError, match="module:attr"):
        _resolve_entrypoint("no_colon")


def test_resolve_entrypoint_module_not_importable():
    """Unimportable module raises ImportError naming the entrypoint."""
    with pytest.raises(ImportError, match="not_real_module_zzz"):
        _resolve_entrypoint("not_real_module_zzz:fn")


def test_resolve_entrypoint_attribute_missing(fake_hook_module):
    """Missing attribute raises AttributeError naming the entrypoint."""
    name, _ = fake_hook_module
    with pytest.raises(AttributeError, match="missing"):
        _resolve_entrypoint(f"{name}:missing")


def test_validate_middleware_callable_accepts_async():
    """A 2-arg async callable validates cleanly."""

    async def good(request, call_next):  # pragma: no cover
        return await call_next(request)

    _validate_middleware_callable(good, "x:good")


def test_validate_middleware_callable_rejects_non_callable():
    """Non-callable hook raises TypeError."""
    with pytest.raises(TypeError, match="non-callable"):
        _validate_middleware_callable("not callable", "x:y")


def test_validate_middleware_callable_rejects_sync():
    """Sync function raises TypeError."""

    def sync_hook(request, call_next):
        return call_next(request)

    with pytest.raises(TypeError, match="async function"):
        _validate_middleware_callable(sync_hook, "x:sync_hook")


def test_validate_middleware_callable_rejects_low_arity():
    """Async function with fewer than 2 positional args raises TypeError."""

    async def too_few(request):  # pragma: no cover
        return None

    with pytest.raises(TypeError, match="positional"):
        _validate_middleware_callable(too_few, "x:too_few")


def test_hook_to_middleware_wraps_in_base_http_middleware():
    """Hook is wrapped as ``Middleware(BaseHTTPMiddleware, dispatch=fn)``."""

    async def hook(request, call_next):  # pragma: no cover
        return await call_next(request)

    mw = _hook_to_middleware(hook)
    assert isinstance(mw, Middleware)
    assert mw.cls is BaseHTTPMiddleware
    assert mw.kwargs.get("dispatch") is hook


def test_build_hook_middleware_empty_returns_empty_list():
    """No hooks returns an empty list."""
    assert build_hook_middleware(None, None) == []
    assert build_hook_middleware([], []) == []


def test_build_hook_middleware_auth_runs_before_middleware(fake_hook_module):
    """Auth hooks register before middleware hooks."""
    name, module = fake_hook_module

    async def auth_a(request, call_next):  # pragma: no cover
        return await call_next(request)

    async def mw_a(request, call_next):  # pragma: no cover
        return await call_next(request)

    module.auth_a = auth_a
    module.mw_a = mw_a

    out = build_hook_middleware(
        auth_hooks=[f"{name}:auth_a"],
        middleware_hooks=[f"{name}:mw_a"],
    )
    assert len(out) == 2
    assert out[0].kwargs["dispatch"] is auth_a
    assert out[1].kwargs["dispatch"] is mw_a


def test_build_hook_middleware_within_list_order_preserved(fake_hook_module):
    """Within each list, registration order matches TOML order."""
    name, module = fake_hook_module

    async def first(request, call_next):  # pragma: no cover
        return await call_next(request)

    async def second(request, call_next):  # pragma: no cover
        return await call_next(request)

    module.first = first
    module.second = second

    out = build_hook_middleware(
        auth_hooks=None,
        middleware_hooks=[f"{name}:first", f"{name}:second"],
    )
    assert [m.kwargs["dispatch"] for m in out] == [first, second]


def test_build_hook_middleware_rejects_non_list_table():
    """Non-list ``hooks`` value raises TypeError."""
    with pytest.raises(TypeError, match="must be a list"):
        build_hook_middleware(auth_hooks="not a list", middleware_hooks=None)


def test_build_hook_middleware_rejects_non_string_entry():
    """Non-string entry inside the hooks list raises TypeError."""
    with pytest.raises(TypeError, match="entries must be strings"):
        build_hook_middleware(auth_hooks=None, middleware_hooks=[123, "ok:fn"])
