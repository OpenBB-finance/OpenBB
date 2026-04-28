"""Behavioral tests for ``openbb_core.api.auth.user``.

The original tests mocked ``UserService`` and asserted
``mock.assert_called_once`` — i.e. they tested mock plumbing instead
of behavior. This rewrite drives:

* The full HTTP 401 contract on ``authenticate_user`` (status, detail,
  ``WWW-Authenticate`` header) for every credential mismatch shape.
* The success contract (returns ``None``, no exception).
* ``get_user_service`` constructs and returns a real ``UserService``.
* ``get_user_settings`` is identity-level: whatever
  ``UserService.read_from_file`` returns is returned verbatim, and any
  exception propagates.
"""

# ruff: noqa: S105 S106

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials

from openbb_core.api.auth.user import (
    authenticate_user,
    get_user_service,
    get_user_settings,
)
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.user_settings import UserSettings  # noqa: F401
from openbb_core.app.service.user_service import UserService


@pytest.fixture(autouse=True)
def _reset_user_service_singleton():
    """``UserService`` is a singleton; clear it between tests so each builds fresh."""
    SingletonMeta._instances.pop(UserService, None)  # type: ignore[arg-type]
    yield
    SingletonMeta._instances.pop(UserService, None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "configured, supplied",
    [
        (("user", "pass"), ("", "")),
        (("user", "pass"), ("random", "pass")),
        (("user", "pass"), ("user", "random")),
        ((None, None), ("user", "pass")),
        ((None, "pass"), ("user", "pass")),
        (("user", None), ("user", "pass")),
    ],
)
def test_authenticate_user_rejects_bad_credentials(configured, supplied):
    """Wrong creds raise 401 with the documented detail and ``WWW-Authenticate`` header."""
    with patch("openbb_core.api.auth.user.Env") as env:
        env.return_value.API_USERNAME = configured[0]
        env.return_value.API_PASSWORD = configured[1]
        creds = HTTPBasicCredentials(username=supplied[0], password=supplied[1])
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(authenticate_user(creds))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Incorrect email or password"
    assert exc_info.value.headers == {"WWW-Authenticate": "Basic"}


@pytest.mark.parametrize(
    "configured, supplied",
    [
        (("user", "pass"), ("user", "pass")),
        (("admin", "s3cret"), ("admin", "s3cret")),
    ],
)
def test_authenticate_user_accepts_matching_credentials(configured, supplied):
    """Matching creds return ``None`` (the documented success contract)."""
    with patch("openbb_core.api.auth.user.Env") as env:
        env.return_value.API_USERNAME = configured[0]
        env.return_value.API_PASSWORD = configured[1]
        creds = HTTPBasicCredentials(username=supplied[0], password=supplied[1])
        assert asyncio.run(authenticate_user(creds)) is None


def test_authenticate_user_short_circuits_when_no_credentials_supplied():
    """When the dependency yields ``None`` (auth disabled) the hook returns ``None``."""
    assert asyncio.run(authenticate_user(None)) is None  # type: ignore[arg-type]


def test_get_user_service_returns_real_user_service_instance(tmp_path: Path):
    """``get_user_service`` constructs and returns a real ``UserService``.

    Patch ``USER_SETTINGS_PATH`` and ``Credentials._env_defaults`` so the
    construction does NOT read the developer's real settings file or env.
    """
    from openbb_core.app.model import user_settings as us_module
    from openbb_core.app.model.credentials import Credentials

    missing = tmp_path / "missing.json"
    with (
        patch.object(UserService, "USER_SETTINGS_PATH", missing),
        patch.object(us_module, "USER_SETTINGS_PATH", missing),
        patch.object(Credentials, "_env_defaults", {}),
    ):
        service = asyncio.run(get_user_service())

    assert isinstance(service, UserService)
    assert callable(getattr(service, "read_from_file", None))


def test_get_user_settings_returns_what_user_service_read_from_file_returns():
    """``get_user_settings`` is a thin wrapper over ``UserService.read_from_file``.

    The contract is identity-level: whatever ``read_from_file`` returns must be
    returned verbatim. We use an opaque sentinel object so the test never
    constructs a real ``UserSettings`` (whose ``__init__`` reads the developer's
    real settings file from disk).
    """
    sentinel = object()

    service = MagicMock(spec=UserService)
    service.read_from_file.return_value = sentinel

    result = asyncio.run(get_user_settings(None, service))  # type: ignore[arg-type]

    assert result is sentinel
    service.read_from_file.assert_called_once_with()


def test_get_user_settings_propagates_read_from_file_exceptions():
    """If ``read_from_file`` raises, the dependency must propagate (not swallow) the error."""
    service = MagicMock(spec=UserService)
    service.read_from_file.side_effect = ValueError("settings file is corrupt")

    with pytest.raises(ValueError, match="settings file is corrupt"):
        asyncio.run(get_user_settings(None, service))  # type: ignore[arg-type]


def test_get_user_settings_returns_defaults_when_file_missing(tmp_path: Path):
    """A missing settings file yields a default ``UserSettings`` (no exception)."""
    missing = tmp_path / "does_not_exist.json"
    with patch.object(UserService, "USER_SETTINGS_PATH", missing):
        service = UserService()
        result = asyncio.run(get_user_settings(None, service))  # type: ignore[arg-type]

    assert isinstance(result, UserSettings)


# -------------------------- HTTP integration tests --------------------------
#
# The tests below mount the real auth dependencies on a real FastAPI app and
# drive them through the real HTTP stack via ``TestClient``. They verify that
# the dependency wiring actually rejects/accepts requests end-to-end (status
# code, body, ``WWW-Authenticate`` header), not just the unit behavior of the
# individual coroutines.


def _build_app_with_auth_enabled(monkeypatch, username: str, password: str):
    """Reload the auth module with ``OPENBB_API_AUTH=True`` and mount its hooks.

    The module-level ``security = HTTPBasic() if Env().API_AUTH else lambda: None``
    is evaluated at import time, so the only honest way to exercise the
    auth-enabled path is to set the env vars and reload the module.
    """
    import importlib

    from fastapi import Depends, FastAPI

    from openbb_core.env import Env

    monkeypatch.setenv("OPENBB_API_AUTH", "True")
    monkeypatch.setenv("OPENBB_API_USERNAME", username)
    monkeypatch.setenv("OPENBB_API_PASSWORD", password)

    SingletonMeta._instances.pop(Env, None)  # type: ignore[arg-type]

    from openbb_core.api.auth import user as user_module

    user_module = importlib.reload(user_module)

    app = FastAPI()

    @app.get("/protected")
    async def protected(
        settings=Depends(user_module.get_user_settings),
    ):
        return {"ok": True, "type": type(settings).__name__}

    return app, user_module


def _build_app_with_auth_disabled(monkeypatch):
    """Reload the auth module with ``OPENBB_API_AUTH=False`` and mount its hooks."""
    import importlib

    from fastapi import Depends, FastAPI

    from openbb_core.env import Env

    monkeypatch.delenv("OPENBB_API_AUTH", raising=False)
    monkeypatch.delenv("OPENBB_API_USERNAME", raising=False)
    monkeypatch.delenv("OPENBB_API_PASSWORD", raising=False)

    SingletonMeta._instances.pop(Env, None)  # type: ignore[arg-type]

    from openbb_core.api.auth import user as user_module

    user_module = importlib.reload(user_module)

    app = FastAPI()

    @app.get("/protected")
    async def protected(
        settings=Depends(user_module.get_user_settings),
    ):
        return {"ok": True, "type": type(settings).__name__}

    return app, user_module


def _override_user_service(app, user_module, tmp_path: Path):
    """Override ``get_user_service`` so it never reads the developer's real settings file."""
    from openbb_core.app.model import user_settings as us_module
    from openbb_core.app.model.credentials import Credentials

    missing = tmp_path / "missing_user_settings.json"

    async def _fake_user_service() -> UserService:
        with (
            patch.object(UserService, "USER_SETTINGS_PATH", missing),
            patch.object(us_module, "USER_SETTINGS_PATH", missing),
            patch.object(Credentials, "_env_defaults", {}),
        ):
            return UserService()

    app.dependency_overrides[user_module.get_user_service] = _fake_user_service


def test_http_protected_endpoint_rejects_missing_credentials(monkeypatch, tmp_path):
    """With auth enabled, a request without ``Authorization`` returns 401."""
    from fastapi.testclient import TestClient

    app, user_module = _build_app_with_auth_enabled(monkeypatch, "alice", "s3cret")
    _override_user_service(app, user_module, tmp_path)

    with TestClient(app) as client:
        response = client.get("/protected")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.headers.get("www-authenticate", "").lower().startswith("basic")


@pytest.mark.parametrize(
    "supplied",
    [
        ("alice", "wrong"),
        ("eve", "s3cret"),
        ("", ""),
    ],
)
def test_http_protected_endpoint_rejects_bad_credentials(
    monkeypatch, tmp_path, supplied
):
    """With auth enabled, wrong creds yield 401 + the documented detail/header."""
    from fastapi.testclient import TestClient

    app, user_module = _build_app_with_auth_enabled(monkeypatch, "alice", "s3cret")
    _override_user_service(app, user_module, tmp_path)

    with TestClient(app) as client:
        response = client.get("/protected", auth=supplied)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect email or password"}
    assert response.headers["www-authenticate"] == "Basic"


def test_http_protected_endpoint_accepts_correct_credentials(monkeypatch, tmp_path):
    """With auth enabled, correct creds reach the handler and return 200 + UserSettings."""
    from fastapi.testclient import TestClient

    app, user_module = _build_app_with_auth_enabled(monkeypatch, "alice", "s3cret")
    _override_user_service(app, user_module, tmp_path)

    with TestClient(app) as client:
        response = client.get("/protected", auth=("alice", "s3cret"))

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["type"] == "UserSettings"


def test_http_protected_endpoint_open_when_auth_disabled(monkeypatch, tmp_path):
    """With auth disabled, the endpoint is reachable without any credentials."""
    from fastapi.testclient import TestClient

    app, user_module = _build_app_with_auth_disabled(monkeypatch)
    _override_user_service(app, user_module, tmp_path)

    with TestClient(app) as client:
        response = client.get("/protected")

    assert response.status_code == 200
    assert response.json()["type"] == "UserSettings"


@pytest.fixture(autouse=True)
def _restore_user_module():
    """After every test, reload ``openbb_core.api.auth.user`` with the original env.

    Tests that flip ``OPENBB_API_AUTH`` mutate module-level state
    (``security``); restore the module to its pristine state afterwards so
    the rest of the suite is unaffected.
    """
    yield
    import importlib

    from openbb_core.api.auth import user as user_module
    from openbb_core.env import Env

    SingletonMeta._instances.pop(Env, None)  # type: ignore[arg-type]
    importlib.reload(user_module)
