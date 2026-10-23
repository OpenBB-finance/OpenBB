"""Tests for openbb_cli.auth — auth hook contract and resolver."""

from __future__ import annotations

import sys
import types

import pytest

from openbb_cli.auth import (
    AuthContext,
    AuthDecision,
    resolve_auth_hook,
)


def test_auth_context_defaults():
    ctx = AuthContext(namespace=None, command="x.y")
    assert ctx.params == {}
    assert ctx.method == "post"


def test_auth_decision_defaults_to_allow():
    d = AuthDecision()
    assert d.allow is True
    assert d.headers is None
    assert d.query_params is None
    assert d.deny_reason is None


def test_resolve_auth_hook_imports_callable(tmp_path, monkeypatch):
    """Module:function path resolves to the callable."""
    mod = types.ModuleType("openbb_cli_test_auth_hook")

    def hook(ctx: AuthContext) -> AuthDecision:
        return AuthDecision(headers={"X-Tested": "1"})

    mod.hook = hook
    monkeypatch.setitem(sys.modules, "openbb_cli_test_auth_hook", mod)

    resolved = resolve_auth_hook("openbb_cli_test_auth_hook:hook")
    assert resolved is hook


def test_resolve_auth_hook_rejects_missing_colon():
    with pytest.raises(ValueError, match="module.path:attribute"):
        resolve_auth_hook("just.a.module")


def test_resolve_auth_hook_rejects_empty_module_or_attr():
    with pytest.raises(ValueError, match="missing module or attribute"):
        resolve_auth_hook(":hook")
    with pytest.raises(ValueError, match="missing module or attribute"):
        resolve_auth_hook("mod:")


def test_resolve_auth_hook_module_not_found():
    with pytest.raises(ImportError):
        resolve_auth_hook("openbb_cli_no_such_module_xyz:hook")


def test_resolve_auth_hook_attr_not_found(monkeypatch):
    mod = types.ModuleType("openbb_cli_test_auth_hook_missing")
    monkeypatch.setitem(sys.modules, "openbb_cli_test_auth_hook_missing", mod)
    with pytest.raises(ImportError, match="not found in"):
        resolve_auth_hook("openbb_cli_test_auth_hook_missing:nope")


def test_resolve_auth_hook_rejects_non_callable(monkeypatch):
    mod = types.ModuleType("openbb_cli_test_auth_hook_not_callable")
    mod.value = 42  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openbb_cli_test_auth_hook_not_callable", mod)
    with pytest.raises(TypeError, match="not callable"):
        resolve_auth_hook("openbb_cli_test_auth_hook_not_callable:value")
