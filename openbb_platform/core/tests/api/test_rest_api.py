"""Test rest_api.py."""

from __future__ import annotations

import importlib

import openbb_core.api.rest_api as rest_api_module
import pytest
from fastapi.testclient import TestClient
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.env import Env

app = rest_api_module.app


def test_openapi():
    """Test openapi schema generation when docs are enabled."""
    if app.openapi_url is None:
        assert app.docs_url is None
        return
    assert app.openapi()


def _reload_rest_api_for_docs_mode(
    monkeypatch: pytest.MonkeyPatch, mode: str
):
    SingletonMeta._instances.pop(Env, None)
    monkeypatch.setenv("OPENBB_API_DOCS_MODE", mode)
    return importlib.reload(rest_api_module).app


def test_docs_mode_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    app_disabled = _reload_rest_api_for_docs_mode(monkeypatch, "disabled")
    client = TestClient(app_disabled)
    assert app_disabled.openapi_url is None
    assert app_disabled.docs_url is None
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/docs").status_code == 404


def test_docs_mode_full(monkeypatch: pytest.MonkeyPatch) -> None:
    app_full = _reload_rest_api_for_docs_mode(monkeypatch, "full")
    client = TestClient(app_full)
    assert app_full.openapi_url == "/openapi.json"
    assert app_full.docs_url == "/docs"
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code in (200, 307)
