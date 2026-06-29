"""Tests for ``openbb_government_ca.government_ca_router``.

The router in Fase 1 only exposes a ``/_health`` endpoint — Fase 4
and Fase 5 will mount the BoC and StatsCan sub-routers.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from openbb_government_ca.government_ca_router import router


def _client() -> TestClient:
    """Build a TestClient wrapping just the government_ca router."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestHealthEndpoint:
    """The ``/_health`` liveness probe — minimal but verifies router mount."""

    def test_health_returns_ok(self):
        """``GET /government_ca/_health`` returns 200 with a static payload."""
        client = _client()
        response = client.get("/government_ca/_health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["provider"] == "government_ca"
