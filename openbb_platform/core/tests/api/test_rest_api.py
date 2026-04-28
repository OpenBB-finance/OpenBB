"""Behavioral tests for ``openbb_core.api.rest_api`` — the assembled FastAPI app.

The original test was a single line: ``assert app.openapi()``. That tests
that ``openapi()`` returns a truthy dict — which is true for *any* FastAPI
app, including an empty one. These rewrites assert the *actual contract*
of the assembled application:

* The OpenAPI schema declares the configured title, version, license,
  and contact metadata sourced from ``SystemSettings.api_settings``.
* The CORS middleware is installed with the configured allow-list.
* ``/openapi.json`` is reachable through ``TestClient``.
* The conditional router-inclusion logic in ``rest_api.py`` holds:
  whenever any command route is mounted, the coverage routes are too.
"""

from fastapi.testclient import TestClient

from openbb_core.api.rest_api import app, system


def test_openapi_schema_metadata_matches_system_settings():
    """OpenAPI ``info`` block reflects ``SystemSettings.api_settings``."""
    schema = app.openapi()
    info = schema["info"]

    assert info["title"] == system.api_settings.title
    assert info["version"] == system.api_settings.version
    assert info["contact"]["name"] == system.api_settings.contact_name
    assert info["license"]["name"] == system.api_settings.license_name


def test_openapi_schema_servers_match_system_settings():
    """OpenAPI ``servers`` block is sourced from ``api_settings.servers``."""
    schema = app.openapi()
    schema_servers = [
        (s.get("url"), s.get("description")) for s in schema.get("servers", [])
    ]
    expected = [(s.url, s.description) for s in system.api_settings.servers]
    assert schema_servers == expected


def test_cors_middleware_is_installed_with_configured_origins():
    """``CORSMiddleware`` is on the stack with the configured allow-list."""
    cors = next(
        (m for m in app.user_middleware if m.cls.__name__ == "CORSMiddleware"),
        None,
    )
    assert cors is not None, "CORSMiddleware not installed"
    assert cors.kwargs.get("allow_origins") == system.api_settings.cors.allow_origins


def test_openapi_endpoint_is_reachable_through_test_client():
    """The app serves its own OpenAPI schema over HTTP."""
    client = TestClient(app)
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    body = resp.json()
    assert body["info"]["title"] == system.api_settings.title


def test_router_inclusion_invariant_commands_imply_coverage():
    """Whenever any command route is mounted, the coverage routes are too.

    ``rest_api.py`` chooses the router set conditionally:
      * DEV_MODE: auth + system + coverage + commands
      * else if commands has routes: commands + coverage
      * else: commands only
    The invariant we test: if there exists any command route, coverage
    routes must exist. This catches accidental removal of the conditional.
    """
    paths = {getattr(r, "path", None) for r in app.routes}
    prefix = system.api_settings.prefix

    coverage_paths = {
        f"{prefix}/coverage/providers",
        f"{prefix}/coverage/commands",
        f"{prefix}/coverage/command_model",
    }
    has_coverage = bool(coverage_paths & paths)

    builtin_paths = coverage_paths | {f"{prefix}/system", f"{prefix}/user/me"}
    has_command_path = any(
        p and p.startswith(prefix) and p not in builtin_paths for p in paths if p
    )
    if has_command_path:
        assert has_coverage, (
            f"command routes mounted without coverage routes; mounted: {paths}"
        )
