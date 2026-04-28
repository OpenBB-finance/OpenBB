"""Behavioral tests for ``openbb_core.app.service.auth_service``.

These tests exercise the **real** auth-extension loading path:

* When ``OPENBB_API_AUTH_EXTENSION`` is unset (or names an extension that is
  not installed), ``AuthService`` falls back to the default
  ``openbb_core.api.router.user`` router/hooks.
* When the env var names a real, installed entry point in the
  ``openbb_core_extension`` group, ``AuthService`` loads that module's
  ``router``, ``auth_hook`` and ``user_settings_hook`` and serves them
  through the ``/user`` namespace at the HTTP level.
* If a configured extension cannot be found, ``_get_entry_mod`` raises
  ``AuthServiceError`` with a useful message.

The "real entry point" is registered in-memory via
``importlib_metadata.EntryPoint`` plus a synthetic module installed in
``sys.modules`` — no ``pip install`` required.
"""

import sys
import types
from typing import Annotated

import pytest
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from importlib_metadata import EntryPoint, EntryPoints

from openbb_core.app.extension_loader import ExtensionLoader, OpenBBGroups
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.auth_service import AuthService, AuthServiceError


def _reset_singletons() -> None:
    SingletonMeta._instances.pop(AuthService, None)  # type: ignore[arg-type]
    SingletonMeta._instances.pop(ExtensionLoader, None)  # type: ignore[arg-type]


@pytest.fixture(autouse=True)
def _isolate_singletons():
    _reset_singletons()
    yield
    _reset_singletons()


# --------------------------- Default fallback path --------------------------


def test_auth_service_uses_default_when_no_extension_configured():
    """No ``ext_name`` → default core router and default hooks."""
    from openbb_core.api.router.user import (
        auth_hook as default_auth_hook,
        router as default_router,
        user_settings_hook as default_user_settings_hook,
    )

    service = AuthService(ext_name=None)

    assert service.router is default_router
    assert service.auth_hook is default_auth_hook
    assert service.user_settings_hook is default_user_settings_hook


def test_auth_service_falls_back_when_extension_not_installed():
    """Naming an unknown extension is non-fatal; defaults are used."""
    from openbb_core.api.router.user import (
        auth_hook as default_auth_hook,
        router as default_router,
    )

    service = AuthService(ext_name="definitely_not_installed_xyz")

    assert service.router is default_router
    assert service.auth_hook is default_auth_hook


# --------------------------- Real entry-point path --------------------------


def _install_fake_auth_extension(monkeypatch, ext_name: str = "fake_auth"):
    """Register a real entry point pointing at an in-memory module.

    Returns ``(module, entry_point)``. The module exposes ``router``,
    ``auth_hook`` and ``user_settings_hook`` as required by ``AuthService``.
    """
    module_name = f"_openbb_test_{ext_name}_module"
    module = types.ModuleType(module_name)

    router = APIRouter(prefix="/user", tags=["User"])

    async def auth_hook(request_token: str | None = None) -> None:
        if request_token != "let-me-in":  # noqa: S105
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Custom auth rejected token",
                headers={"X-Auth-Source": "fake-extension"},
            )

    async def user_settings_hook(
        _: Annotated[None, Depends(auth_hook)],
    ) -> UserSettings:
        return UserSettings()

    @router.get("/me")
    async def me(settings: Annotated[UserSettings, Depends(user_settings_hook)]):
        return {"source": "fake-extension"}

    module.router = router  # type: ignore[attr-defined]
    module.auth_hook = auth_hook  # type: ignore[attr-defined]
    module.user_settings_hook = user_settings_hook  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, module_name, module)

    ep = EntryPoint(
        name=ext_name,
        value=f"{module_name}",
        group=OpenBBGroups.core.value,
    )

    real_sorted_entry_points = ExtensionLoader._sorted_entry_points

    def patched_sorted_entry_points(group: str) -> EntryPoints:
        if group == OpenBBGroups.core.value:
            return EntryPoints((ep,))
        return real_sorted_entry_points(group)

    monkeypatch.setattr(
        ExtensionLoader,
        "_sorted_entry_points",
        staticmethod(patched_sorted_entry_points),
    )

    return module, ep


def test_auth_service_loads_router_and_hooks_from_extension(monkeypatch):
    """When the named extension is installed, its router/hooks are used."""
    module, _ = _install_fake_auth_extension(monkeypatch, ext_name="fake_auth")

    service = AuthService(ext_name="fake_auth")

    assert service.router is module.router
    assert service.auth_hook is module.auth_hook
    assert service.user_settings_hook is module.user_settings_hook


def test_auth_extension_serves_real_http_traffic(monkeypatch):
    """End-to-end: mount the loaded router on FastAPI and drive it via HTTP."""
    _install_fake_auth_extension(monkeypatch, ext_name="fake_auth")
    service = AuthService(ext_name="fake_auth")

    app = FastAPI()
    app.include_router(service.router)

    with TestClient(app) as client:
        # Wrong token → 401 with the custom header from the extension's auth_hook
        bad = client.get("/user/me", params={"request_token": "nope"})
        assert bad.status_code == status.HTTP_401_UNAUTHORIZED
        assert bad.json() == {"detail": "Custom auth rejected token"}
        assert bad.headers.get("x-auth-source") == "fake-extension"

        # Correct token → handler runs, returns the extension's marker payload
        ok = client.get("/user/me", params={"request_token": "let-me-in"})
        assert ok.status_code == 200
        assert ok.json() == {"source": "fake-extension"}


def test_get_entry_mod_raises_for_missing_extension(monkeypatch):
    """``_get_entry_mod`` must raise a clear error when the extension is gone."""
    monkeypatch.setattr(
        ExtensionLoader,
        "_sorted_entry_points",
        staticmethod(lambda group: EntryPoints(())),
    )

    with pytest.raises(AuthServiceError, match="ghost_ext"):
        AuthService._get_entry_mod("ghost_ext")


def test_is_installed_true_for_registered_entry_point(monkeypatch):
    """``_is_installed`` must return ``True`` only for a real, name-matching entry point."""
    _install_fake_auth_extension(monkeypatch, ext_name="fake_auth")

    assert AuthService._is_installed("fake_auth") is True
    assert AuthService._is_installed("not_there") is False


def test_auth_service_is_singleton(monkeypatch):
    """Two constructions return the same instance (singleton contract)."""
    _install_fake_auth_extension(monkeypatch, ext_name="fake_auth")

    a = AuthService(ext_name="fake_auth")
    b = AuthService()  # no args -> still the same singleton

    assert a is b
