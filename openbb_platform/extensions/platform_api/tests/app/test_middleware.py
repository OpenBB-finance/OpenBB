"""Tests for ``openbb_platform_api.app.middleware`` — HTTP middleware
hook entrypoints loaded from the launcher TOML.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Helpers — register a module on sys.modules so module:attr resolution works
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_middleware_module(request):
    """Register a test module under a unique name so each test gets a
    clean slate. Cleans up sys.modules afterwards.
    """
    name = f"test_mw_{request.node.name}"
    module = types.ModuleType(name)
    sys.modules[name] = module
    yield name, module
    sys.modules.pop(name, None)


# ---------------------------------------------------------------------------
# _resolve_entrypoint — module:attr lookup
# ---------------------------------------------------------------------------


def test_resolve_entrypoint_picks_module_attr(fake_middleware_module):
    """``module:attr`` resolves to the named attribute."""
    from openbb_platform_api.app.middleware import _resolve_entrypoint

    name, module = fake_middleware_module
    sentinel = object()
    module.my_callable = sentinel  # type: ignore[attr-defined]
    assert _resolve_entrypoint(f"{name}:my_callable") is sentinel


def test_resolve_entrypoint_handles_dotted_attribute(fake_middleware_module):
    """``module:Outer.inner`` walks the dotted attribute path —
    method-on-class references work without a separate import.
    """
    from openbb_platform_api.app.middleware import _resolve_entrypoint

    name, module = fake_middleware_module

    class Outer:
        @staticmethod
        async def inner(request, call_next):
            return await call_next(request)

    module.Outer = Outer  # type: ignore[attr-defined]
    fn = _resolve_entrypoint(f"{name}:Outer.inner")
    assert fn is Outer.inner


def test_resolve_entrypoint_rejects_path_without_colon():
    """The entrypoint format is enforced — a missing colon is a
    config error, not silently treated as a bare module name.
    """
    from openbb_platform_api.app.middleware import _resolve_entrypoint

    with pytest.raises(ValueError, match="module:attr"):
        _resolve_entrypoint("just_a_module")


def test_resolve_entrypoint_raises_helpful_import_error():
    """Missing module → ImportError with the entrypoint string in the
    message so deploy logs name the bad reference.
    """
    from openbb_platform_api.app.middleware import _resolve_entrypoint

    with pytest.raises(ImportError, match="nonexistent_pkg"):
        _resolve_entrypoint("nonexistent_pkg.module:fn")


def test_resolve_entrypoint_raises_helpful_attribute_error(
    fake_middleware_module,
):
    """Module loads but attribute is missing → AttributeError naming
    the offending entrypoint string.
    """
    from openbb_platform_api.app.middleware import _resolve_entrypoint

    name, _module = fake_middleware_module
    with pytest.raises(AttributeError, match="missing_attr"):
        _resolve_entrypoint(f"{name}:missing_attr")


# ---------------------------------------------------------------------------
# _validate_middleware_callable — signature checks
# ---------------------------------------------------------------------------


def test_validate_middleware_callable_accepts_async_two_arg():
    """The canonical Starlette HTTP middleware signature passes."""
    from openbb_platform_api.app.middleware import _validate_middleware_callable

    async def good(request, call_next):
        return await call_next(request)

    _validate_middleware_callable(good, "tests:good")


def test_validate_middleware_callable_rejects_non_callable():
    """A plain object that happens to be referenced as middleware
    fails with a clear type message.
    """
    from openbb_platform_api.app.middleware import _validate_middleware_callable

    with pytest.raises(TypeError, match="non-callable"):
        _validate_middleware_callable(object(), "tests:bad")


def test_validate_middleware_callable_rejects_sync_function():
    """Sync middleware silently breaks the Starlette chain — reject
    at config-load time so the failure mode is a startup error,
    not a runtime mystery.
    """
    from openbb_platform_api.app.middleware import _validate_middleware_callable

    def sync_fn(request, call_next):
        return call_next(request)

    with pytest.raises(TypeError, match="async function"):
        _validate_middleware_callable(sync_fn, "tests:sync_fn")


def test_validate_middleware_callable_rejects_too_few_args():
    """Single-arg callable can't match ``(request, call_next)``."""
    from openbb_platform_api.app.middleware import _validate_middleware_callable

    async def too_few(request):
        return None

    with pytest.raises(TypeError, match="positional parameter"):
        _validate_middleware_callable(too_few, "tests:too_few")


# ---------------------------------------------------------------------------
# apply_http_middleware_hooks — registration + ordering
# ---------------------------------------------------------------------------


def test_apply_hooks_returns_empty_for_no_hooks():
    """Empty / None hooks list is a no-op, returns ``[]``."""
    from openbb_platform_api.app.middleware import apply_http_middleware_hooks

    app = MagicMock()
    assert apply_http_middleware_hooks(app, None) == []
    assert apply_http_middleware_hooks(app, []) == []
    app.middleware.assert_not_called()


def test_apply_hooks_rejects_non_list_input():
    """A scalar ``hooks`` value (string, dict, …) is a config error
    that should fail loudly rather than be silently ignored.
    """
    from openbb_platform_api.app.middleware import apply_http_middleware_hooks

    app = MagicMock()
    with pytest.raises(TypeError, match="must be a list"):
        apply_http_middleware_hooks(app, "single_hook")  # type: ignore[arg-type]


def test_apply_hooks_rejects_non_string_entries():
    """Mixed-type entries fail loudly — keeps TOML parse errors from
    silently producing partial registrations.
    """
    from openbb_platform_api.app.middleware import apply_http_middleware_hooks

    app = MagicMock()
    with pytest.raises(TypeError, match="must be strings"):
        apply_http_middleware_hooks(app, [123])  # type: ignore[list-item]


def test_apply_hooks_registers_in_outer_to_inner_order(fake_middleware_module):
    """TOML list order = outermost to innermost. Internally the
    launcher registers in REVERSE so Starlette's stack ends up with
    the first entry on top (where it sees requests first).
    """
    from openbb_platform_api.app.middleware import apply_http_middleware_hooks

    name, module = fake_middleware_module

    async def outer(request, call_next):
        return await call_next(request)

    async def inner(request, call_next):
        return await call_next(request)

    module.outer = outer  # type: ignore[attr-defined]
    module.inner = inner  # type: ignore[attr-defined]

    app = MagicMock()
    decorator = MagicMock(side_effect=lambda fn: fn)
    app.middleware.return_value = decorator

    out = apply_http_middleware_hooks(app, [f"{name}:outer", f"{name}:inner"])
    assert out == [f"{name}:outer", f"{name}:inner"]
    # ``app.middleware("http")`` called twice (once per hook).
    assert app.middleware.call_count == 2
    # Registration order is REVERSED — inner first, outer last —
    # so Starlette's ``add_middleware`` stack ends up with ``outer``
    # on top.
    registered_funcs = [call.args[0] for call in decorator.call_args_list]
    assert registered_funcs == [inner, outer]


def test_apply_hooks_end_to_end_on_real_fastapi_app(fake_middleware_module):
    """Integration: register a hook on a real FastAPI app and verify
    it actually intercepts the request via TestClient. This is the
    only assurance that the registration call shape is right.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.middleware import apply_http_middleware_hooks

    name, module = fake_middleware_module

    invocations: list[str] = []

    async def tag_middleware(request, call_next):
        invocations.append("middleware-in")
        response = await call_next(request)
        invocations.append("middleware-out")
        response.headers["X-Tagged"] = "yes"
        return response

    module.tag_middleware = tag_middleware  # type: ignore[attr-defined]

    app = FastAPI()

    @app.get("/ping")
    async def ping():
        invocations.append("handler")
        return {"ok": True}

    apply_http_middleware_hooks(app, [f"{name}:tag_middleware"])

    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.headers.get("X-Tagged") == "yes"
    assert invocations == ["middleware-in", "handler", "middleware-out"]


def test_apply_hooks_failure_during_registration_raises_immediately():
    """A bad reference in the middle of the list aborts the whole
    registration — preserves "all-or-nothing" semantics so we never
    end up with a partially configured app at startup.
    """
    from openbb_platform_api.app.middleware import apply_http_middleware_hooks

    app = MagicMock()
    with pytest.raises(ImportError):
        apply_http_middleware_hooks(app, ["nonexistent_pkg.never_loaded:fn"])
    # Nothing got registered — the resolution failed before any
    # ``app.middleware`` calls.
    app.middleware.assert_not_called()
