"""Behavioral tests for ``openbb_core.api.router.user``.

The route is a thin pass-through over the injected ``user_settings``
dependency. We test:

* The bare handler returns its argument verbatim (identity).
* The full FastAPI route invokes ``get_user_settings`` and serializes
  the resolved value as JSON. The dependency is overridden via FastAPI's
  ``dependency_overrides`` so we never construct a real ``UserSettings``
  (whose ``__init__`` reads the developer's real settings file from disk).
"""

# ruff: noqa: S106

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from openbb_core.api.auth.user import get_user_settings
from openbb_core.api.router.user import (
    read_user_settings,
    router as user_router,
)


def test_read_user_settings_is_a_pass_through():
    """Handler returns the *exact* injected value, regardless of its type."""
    sentinel = object()
    result = asyncio.run(read_user_settings(user_settings=sentinel))  # type: ignore[arg-type]
    assert result is sentinel


@pytest.fixture
def app_with_user_router():
    """A FastAPI app with only the ``/user`` router mounted."""
    app = FastAPI()
    app.include_router(user_router)
    return app


def test_user_router_get_me_serializes_dependency_result(app_with_user_router):
    """``GET /user/me`` serializes whatever ``get_user_settings`` returned.

    Override the dependency with a plain dict — FastAPI's
    ``jsonable_encoder`` passes dicts through unchanged. This avoids
    constructing a real ``UserSettings`` (which would read the developer's
    settings file).
    """
    payload = {
        "id": "behavioral-test-id",
        "credentials": {"polygon_api_key": "behavioral_token_99"},
        "preferences": {},
        "defaults": {"commands": {}},
    }

    async def _override():
        return payload

    app_with_user_router.dependency_overrides[get_user_settings] = _override

    client = TestClient(app_with_user_router)
    resp = client.get("/user/me")

    assert resp.status_code == 200
    assert resp.json() == payload


def test_user_router_get_me_propagates_dependency_exception(app_with_user_router):
    """If the ``get_user_settings`` dependency raises, the route surfaces a 500."""

    async def _raises():
        raise RuntimeError("boom")

    app_with_user_router.dependency_overrides[get_user_settings] = _raises

    client = TestClient(app_with_user_router, raise_server_exceptions=False)
    resp = client.get("/user/me")

    assert resp.status_code == 500
