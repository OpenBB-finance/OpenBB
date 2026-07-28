"""Targeted tests for openbb_core.app.router uncovered branches."""

from __future__ import annotations

import warnings as _warnings

import pytest

from openbb_core.app.router import (
    CommandMap,
    LoadingError,
    Router,
    RouterLoader,
)


def _make_router_with_model() -> Router:
    r = Router()

    @r.command(openapi_extra={"model": "MyModel"}, methods=["GET"])
    def thing() -> str:  # pragma: no cover - signature only
        return "ok"

    return r


def test_get_commands_model_returns_mapping(fake_router):
    """Lines 494-507: get_commands_model walks routes with openapi_extra['model']."""
    out = CommandMap.get_commands_model(fake_router)
    assert isinstance(out, dict)
    # Should contain at least one model entry from the fake router.
    assert any(isinstance(v, str) for v in out.values())


def test_get_commands_model_with_separator(fake_router):
    out = CommandMap.get_commands_model(fake_router, sep=".")
    for key in out:
        assert "/" not in key


def test_router_loader_from_extensions_warns_on_failure(monkeypatch):
    """Lines 531-536: include_router exception path -> warning."""
    from openbb_core.app.extension_loader import ExtensionLoader

    class _Bad:
        pass

    RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(
        ExtensionLoader, "core_objects", property(lambda self: {"bad": _Bad()})
    )
    with _warnings.catch_warnings(record=True) as w:
        _warnings.simplefilter("always")
        RouterLoader.from_extensions()
    assert any("bad" in str(x.message) for x in w)
    RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]


def test_router_loader_from_extensions_raises_in_debug(monkeypatch):
    """Lines 532-534: DEBUG_MODE re-raises as LoadingError."""
    from openbb_core.app.extension_loader import ExtensionLoader
    from openbb_core.env import Env

    class _Bad:
        pass

    RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(
        ExtensionLoader, "core_objects", property(lambda self: {"x": _Bad()})
    )
    monkeypatch.setattr(Env, "DEBUG_MODE", property(lambda self: True))
    with pytest.raises(LoadingError):
        RouterLoader.from_extensions()
    RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
