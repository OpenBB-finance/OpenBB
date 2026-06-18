"""Tests for ``openbb_mcp_server.app.spec``."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from openbb_mcp_server.app.spec import (
    SUPPORTED_SPEC_VERSIONS,
    _content_hash,
    _filter_request_headers,
    _filter_response_headers,
    _proxy_request,
    _rewrite_query_string,
    _spec_param_to_openapi,
    _substitute_path_params,
    _trim_uniform_zero_time_columns,
    _trim_uniform_zero_time_in_records,
    build_app_from_spec,
    load_spec,
    synthesize_openapi_from_spec,
)


def _stamp(spec: dict) -> dict:
    """Stamp ``spec`` with a fresh ``content_sha256`` so it loads."""
    spec = {k: v for k, v in spec.items() if k != "content_sha256"}
    spec["content_sha256"] = _content_hash(spec)
    return spec


SAMPLE_SPEC: dict = {
    "version": 5,
    "api_version": "1.2.3",
    "base_url": "https://upstream.example.com",
    "commands": {
        "ping": {
            "url_path": "/v1/ping",
            "method": "get",
            "description": "Simple ping endpoint.",
            "parameters": [
                {
                    "name": "limit",
                    "in": "query",
                    "type": "integer",
                    "default": 10,
                    "wire_name": "$limit",
                    "help": "Number of records.",
                },
                {
                    "name": "tags",
                    "in": "query",
                    "type": "string",
                    "is_list": True,
                    "choices": ["a", "b"],
                    "required": True,
                },
            ],
            "response_schema": {"type": "object"},
        },
        "create": {
            "url_path": "/v1/items",
            "method": "post",
            "description": "Create an item.",
            "parameters": [],
            "request_body_schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            },
        },
        "skip_me": {
            "url_path": "",  # malformed — should be skipped
            "method": "get",
        },
        "skip_method": {
            "url_path": "/v1/x",
            "method": "patch",  # unsupported — skipped
        },
    },
}


@pytest.fixture
def spec_file(tmp_path):
    """Write SAMPLE_SPEC to a tmp .spec file (auto-stamped with hash)."""
    f = tmp_path / "test.spec"
    f.write_text(json.dumps(_stamp(SAMPLE_SPEC)))
    return f


def test_load_spec_returns_dict(spec_file):
    """A valid spec file parses cleanly."""
    spec = load_spec(spec_file)
    assert spec["version"] in SUPPORTED_SPEC_VERSIONS
    assert spec["base_url"] == "https://upstream.example.com"
    assert "ping" in spec["commands"]


def test_load_spec_missing_path(tmp_path):
    """Missing file → FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_spec(tmp_path / "nope.spec")


def test_load_spec_invalid_json(tmp_path):
    """Malformed JSON → ValueError."""
    f = tmp_path / "bad.spec"
    f.write_text("{not json")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_spec(f)


def test_load_spec_top_level_must_be_object(tmp_path):
    """JSON array at top level → ValueError."""
    f = tmp_path / "arr.spec"
    f.write_text("[]")
    with pytest.raises(ValueError, match="top-level object"):
        load_spec(f)


def test_load_spec_unsupported_version(tmp_path):
    """Unknown ``version`` field → ValueError."""
    f = tmp_path / "v999.spec"
    f.write_text(json.dumps({"version": 999, "base_url": "x", "commands": {}}))
    with pytest.raises(ValueError, match="Unsupported spec version"):
        load_spec(f)


def test_load_spec_missing_base_url(tmp_path):
    """Missing ``base_url`` → ValueError."""
    f = tmp_path / "nb.spec"
    f.write_text(json.dumps({"version": 5, "commands": {}}))
    with pytest.raises(ValueError, match="base_url"):
        load_spec(f)


def test_load_spec_missing_commands(tmp_path):
    """Missing ``commands`` table → ValueError."""
    f = tmp_path / "nc.spec"
    f.write_text(json.dumps({"version": 5, "base_url": "x"}))
    with pytest.raises(ValueError, match="commands"):
        load_spec(f)


def test_load_spec_rejects_structurally_invalid_command(tmp_path):
    """Pydantic schema rejects a command missing ``url_path``/``method``."""
    f = tmp_path / "bad.spec"
    f.write_text(
        json.dumps(
            {
                "version": 5,
                "base_url": "https://x",
                "commands": {"oops": {"description": "no url_path/method"}},
            }
        )
    )
    with pytest.raises(ValueError, match="does not conform to the expected schema"):
        load_spec(f)


def test_load_spec_rejects_non_string_base_url_via_pydantic(tmp_path):
    """A non-string ``base_url`` fails with the legacy error message."""
    f = tmp_path / "bad.spec"
    f.write_text(json.dumps({"version": 5, "base_url": 42, "commands": {}}))
    with pytest.raises(ValueError, match="base_url"):
        load_spec(f)


def test_load_spec_accepts_optional_provenance_fields(tmp_path):
    """Optional provenance fields are preserved on the returned dict."""
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://upstream.example.com",
            "api_version": "3.1.0",
            "generator": "openbb-cli==2.0.0",
            "generated_at": "2026-05-08T00:00:00Z",
            "source_url": "https://upstream.example.com/openapi.json",
            "commands": {
                "ping": {"url_path": "/v1/ping", "method": "get", "parameters": []}
            },
        }
    )
    f = tmp_path / "p.spec"
    f.write_text(json.dumps(payload))
    spec = load_spec(f)
    assert spec["generator"] == "openbb-cli==2.0.0"
    assert spec["generated_at"] == "2026-05-08T00:00:00Z"
    assert spec["source_url"] == "https://upstream.example.com/openapi.json"
    assert spec["api_version"] == "3.1.0"


def test_load_spec_verifies_matching_content_hash(tmp_path):
    """A spec carrying its own correctly-computed SHA-256 loads cleanly."""
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    f = tmp_path / "h.spec"
    f.write_text(json.dumps(payload))
    out = load_spec(f)
    assert out["content_sha256"] == payload["content_sha256"]


def test_load_spec_rejects_tampered_content_hash(tmp_path):
    """A spec whose ``content_sha256`` no longer matches its body fails."""
    payload = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        "content_sha256": "0" * 64,
    }
    f = tmp_path / "tampered.spec"
    f.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="failed integrity check"):
        load_spec(f)


def test_load_spec_rejects_spec_missing_content_sha256(tmp_path):
    """A spec without ``content_sha256`` is rejected."""
    payload = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
    }
    f = tmp_path / "no-hash.spec"
    f.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="content_sha256"):
        load_spec(f)


def test_content_hash_is_stable_across_key_order():
    """Hashing is canonical (sorted keys); dict ordering doesn't move it."""
    from openbb_mcp_server.app.spec import _content_hash

    a = {"version": 5, "base_url": "x", "commands": {}}
    b = {"commands": {}, "base_url": "x", "version": 5}
    assert _content_hash(a) == _content_hash(b)


def test_content_hash_excludes_sha256_field():
    """Adding/removing the ``content_sha256`` field doesn't change the hash."""
    from openbb_mcp_server.app.spec import _content_hash

    a = {"version": 5, "base_url": "x", "commands": {}}
    b = {**a, "content_sha256": "ignored"}
    assert _content_hash(a) == _content_hash(b)


def test_load_spec_accepts_deploy_config_hash_pin(tmp_path):
    """``expected_content_sha256`` supplied (matching) → loads cleanly."""
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    f = tmp_path / "deploy-pinned.spec"
    f.write_text(json.dumps(payload))
    spec = load_spec(f, expected_content_sha256=payload["content_sha256"])
    assert spec is not None


def test_load_spec_rejects_when_deploy_config_pin_mismatches(tmp_path):
    """``expected_content_sha256`` mismatch raises with ``deploy-config pin check``."""
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    f = tmp_path / "drift.spec"
    f.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="deploy-config pin check"):
        load_spec(f, expected_content_sha256="0" * 64)


def test_load_spec_deploy_pin_works_alongside_in_file_hash(tmp_path):
    """Matching in-file hash and ``expected_content_sha256`` both pass."""
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    f = tmp_path / "double-checked.spec"
    f.write_text(json.dumps(payload))
    out = load_spec(f, expected_content_sha256=payload["content_sha256"])
    assert out["content_sha256"] == payload["content_sha256"]


def test_build_app_from_spec_exposes_provenance_metadata(tmp_path):
    """Provenance fields flow onto ``app.state`` for downstream callers."""
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://upstream.example.com",
            "api_version": "3.1.0",
            "generator": "openbb-cli==2.0.0",
            "generated_at": "2026-05-08T00:00:00Z",
            "source_url": "https://upstream.example.com/openapi.json",
            "commands": {
                "ping": {"url_path": "/v1/ping", "method": "get", "parameters": []}
            },
        }
    )
    f = tmp_path / "prov.spec"
    f.write_text(json.dumps(payload))

    app = build_app_from_spec(load_spec(f), spec_name="prov.spec")
    state = app.state
    assert state.openbb_spec_version == 5
    assert state.openbb_spec_generator == "openbb-cli==2.0.0"
    assert state.openbb_spec_generated_at == "2026-05-08T00:00:00Z"
    assert state.openbb_spec_source_url == "https://upstream.example.com/openapi.json"
    assert state.openbb_spec_content_sha256 == payload["content_sha256"]
    assert state.openbb_spec_api_version == "3.1.0"


def _make_spec_dict(base_url: str = "https://x", cmd_path: str = "/p") -> dict:
    """Helper: build + stamp a minimal valid spec for multi-spec tests."""
    return _stamp(
        {
            "version": 5,
            "base_url": base_url,
            "commands": {
                "p": {"url_path": cmd_path, "method": "get", "parameters": []}
            },
        }
    )


def test_build_apps_from_specs_mounts_each_spec_at_named_prefix():
    """Each entry mounts under its dict-key prefix by default."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    parent = build_apps_from_specs(
        {
            "equity": {"spec": _make_spec_dict()},
            "crypto": {"spec": _make_spec_dict()},
        }
    )
    assert "/equity" in parent.state.openbb_specs
    assert "/crypto" in parent.state.openbb_specs


def test_build_apps_from_specs_explicit_mount_overrides_default():
    """``mount`` in the entry overrides the default ``/<name>`` prefix."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    parent = build_apps_from_specs(
        {"equity": {"spec": _make_spec_dict(), "mount": "/markets/equity"}}
    )
    assert "/markets/equity" in parent.state.openbb_specs


def test_build_apps_from_specs_normalizes_mount_without_leading_slash():
    """``mount = "equity"`` (no leading slash) gets normalized."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    parent = build_apps_from_specs(
        {"x": {"spec": _make_spec_dict(), "mount": "stocks"}}
    )
    assert "/stocks" in parent.state.openbb_specs


def test_build_apps_from_specs_rejects_mount_collision():
    """Two specs at the same mount → ValueError."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    with pytest.raises(ValueError, match="mount collision"):
        build_apps_from_specs(
            {
                "a": {"spec": _make_spec_dict(), "mount": "/dup"},
                "b": {"spec": _make_spec_dict(), "mount": "/dup"},
            }
        )


def test_build_apps_from_specs_rejects_empty_config():
    """An empty specs dict raises with a clear message."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    with pytest.raises(ValueError, match="at least one spec entry"):
        build_apps_from_specs({})


def test_build_apps_from_specs_rejects_non_dict_entry():
    """Non-dict entries fail fast."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    with pytest.raises(TypeError, match="must be a dict"):
        build_apps_from_specs({"x": "not a dict"})  # type: ignore[arg-type]


def test_build_apps_from_specs_rejects_entry_missing_spec_field():
    """Entry without the required ``spec`` key fails."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    with pytest.raises(ValueError, match="missing the required 'spec' field"):
        build_apps_from_specs({"x": {"mount": "/x"}})


def test_build_apps_from_specs_state_carries_provenance(tmp_path):
    """Each mount's state snapshot carries the per-spec provenance."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    spec_a = _stamp(
        {
            "version": 5,
            "base_url": "https://a.example.com",
            "generator": "openbb-cli==2.0.0",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    parent = build_apps_from_specs({"a": {"spec": spec_a, "spec_name": "a.spec"}})
    snapshot = parent.state.openbb_specs["/a"]
    assert snapshot["name"] == "a"
    assert snapshot["spec_name"] == "a.spec"
    assert snapshot["base_url"] == "https://a.example.com"
    assert snapshot["generator"] == "openbb-cli==2.0.0"
    assert snapshot["content_sha256"] == spec_a["content_sha256"]


def test_build_apps_from_specs_per_spec_middleware_hooks_applied(monkeypatch):
    """Per-spec ``middleware_hooks`` flow through to the sub-app's stack."""
    import sys
    import types

    from openbb_mcp_server.app.spec import build_apps_from_specs

    mod = types.ModuleType("test_multi_spec_hooks_mw")

    async def mw_hook(request, call_next):  # pragma: no cover
        return await call_next(request)

    mod.mw_hook = mw_hook
    monkeypatch.setitem(sys.modules, "test_multi_spec_hooks_mw", mod)

    parent = build_apps_from_specs(
        {
            "a": {
                "spec": _make_spec_dict(),
                "middleware_hooks": ["test_multi_spec_hooks_mw:mw_hook"],
            }
        }
    )
    from starlette.routing import Mount

    for route in parent.routes:
        if isinstance(route, Mount) and route.name == "a":
            sub_app = route.app
            assert any(
                getattr(m, "kwargs", {}).get("dispatch") is mw_hook
                for m in sub_app.user_middleware
            )
            break
    else:
        raise AssertionError("Expected a mounted sub-app named 'a'.")


def test_build_apps_from_specs_per_spec_auth_hooks_applied(monkeypatch):
    """Per-spec ``auth_hooks`` flow through identically to middleware hooks."""
    import sys
    import types

    from openbb_mcp_server.app.spec import build_apps_from_specs

    mod = types.ModuleType("test_multi_spec_hooks_auth")

    async def auth_hook(request, call_next):  # pragma: no cover
        return await call_next(request)

    mod.auth_hook = auth_hook
    monkeypatch.setitem(sys.modules, "test_multi_spec_hooks_auth", mod)

    parent = build_apps_from_specs(
        {
            "a": {
                "spec": _make_spec_dict(),
                "auth_hooks": ["test_multi_spec_hooks_auth:auth_hook"],
            }
        }
    )
    from starlette.routing import Mount

    for route in parent.routes:
        if isinstance(route, Mount) and route.name == "a":
            sub_app = route.app
            assert any(
                getattr(m, "kwargs", {}).get("dispatch") is auth_hook
                for m in sub_app.user_middleware
            )
            break
    else:
        raise AssertionError("Expected a mounted sub-app named 'a'.")


def test_build_apps_from_specs_rejects_non_list_hook_table():
    """``middleware_hooks`` must be a list — non-list raises TypeError."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    with pytest.raises(TypeError, match="must be a list"):
        build_apps_from_specs(
            {"a": {"spec": _make_spec_dict(), "middleware_hooks": "not a list"}}
        )


def test_build_apps_from_specs_rejects_non_string_hook_entry():
    """Non-string hook entries inside the list raise TypeError."""
    from openbb_mcp_server.app.spec import build_apps_from_specs

    with pytest.raises(TypeError, match="hook entries must be strings"):
        build_apps_from_specs({"a": {"spec": _make_spec_dict(), "auth_hooks": [123]}})


def test_spec_param_to_openapi_scalar():
    """Scalar params produce a flat schema with type, default, enum, description."""
    out = _spec_param_to_openapi(
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "default": 10,
            "choices": [1, 2, 3],
            "help": "Max rows.",
            "example": 5,
        }
    )
    assert out["name"] == "limit"
    assert out["schema"]["type"] == "integer"
    assert out["schema"]["default"] == 10
    assert out["schema"]["enum"] == [1, 2, 3]
    assert out["description"] == "Max rows."
    assert out["example"] == 5


def test_spec_param_to_openapi_list():
    """``is_list`` produces an ``array`` schema with item type."""
    out = _spec_param_to_openapi({"name": "tags", "type": "string", "is_list": True})
    assert out["schema"] == {"type": "array", "items": {"type": "string"}}


def test_spec_param_to_openapi_unknown_type_falls_back_to_string():
    """Unknown ``type`` falls back to ``string``."""
    out = _spec_param_to_openapi({"name": "x", "type": "weird"})
    assert out["schema"]["type"] == "string"


def test_synthesize_openapi_from_spec_basic():
    """Each command becomes a path entry with parameters + response schema."""
    doc = synthesize_openapi_from_spec(SAMPLE_SPEC)
    assert doc["openapi"] == "3.1.0"
    assert "/v1/ping" in doc["paths"]
    assert "/v1/items" in doc["paths"]
    assert "skip_me" not in str(doc["paths"])
    ping = doc["paths"]["/v1/ping"]["get"]
    assert ping["operationId"] == "ping"
    assert ping["responses"]["200"]["content"]["application/json"]["schema"] == {
        "type": "object"
    }
    items_post = doc["paths"]["/v1/items"]["post"]
    assert "requestBody" in items_post


def test_synthesize_openapi_skips_method_unknown():
    """Methods other than get/post are ignored."""
    spec = {
        "version": 5,
        "base_url": "x",
        "commands": {
            "weird": {"url_path": "/x", "method": "delete"},
        },
    }
    doc = synthesize_openapi_from_spec(spec)
    assert doc["paths"] == {}


def test_synthesize_openapi_command_without_response_schema():
    """Commands without ``response_schema`` still produce a 200 entry."""
    spec = {
        "version": 5,
        "base_url": "x",
        "commands": {"bare": {"url_path": "/y", "method": "get"}},
    }
    doc = synthesize_openapi_from_spec(spec)
    assert "/y" in doc["paths"]
    assert doc["paths"]["/y"]["get"]["responses"]["200"] == {
        "content": {"application/json": {}}
    }


def test_build_app_from_spec_state(spec_file):
    """``app.state`` carries the spec, base_url, source label, headers."""
    spec = load_spec(spec_file)
    app = build_app_from_spec(spec, spec_name="test.spec")
    assert isinstance(app, FastAPI)
    assert app.state.openbb_spec is spec
    assert app.state.openbb_spec_base_url == "https://upstream.example.com"
    assert app.state.openbb_spec_source == "test.spec"


def test_build_app_from_spec_routes_registered(spec_file):
    """Each command becomes a FastAPI route."""
    app = build_app_from_spec(load_spec(spec_file))
    paths = {r.path for r in app.routes}
    assert "/v1/ping" in paths
    assert "/v1/items" in paths


def test_build_app_from_spec_base_url_override(spec_file):
    """``base_url_override`` replaces the spec's recorded base_url."""
    app = build_app_from_spec(
        load_spec(spec_file), base_url_override="https://other.example.com"
    )
    assert app.state.openbb_spec_base_url == "https://other.example.com"


def test_build_app_from_spec_extra_headers_persist(spec_file):
    """``extra_headers`` are stashed on app.state for the proxy to read."""
    app = build_app_from_spec(
        load_spec(spec_file), extra_headers={"Authorization": "Bearer x"}
    )
    assert app.state.openbb_spec_extra_headers == {"Authorization": "Bearer x"}


def test_build_app_from_spec_skips_malformed_params(tmp_path):
    """Non-dict parameter entries are filtered out before route registration."""
    spec = {
        "version": 5,
        "base_url": "x",
        "commands": {
            "x": {
                "url_path": "/x",
                "method": "get",
                "parameters": [None, "string", {"name": "ok", "type": "string"}],
            }
        },
    }
    app = build_app_from_spec(spec)
    assert any(r.path == "/x" for r in app.routes)


def test_filter_request_headers_drops_hop_by_hop():
    """Hop-by-hop headers are stripped before forwarding upstream."""
    out = _filter_request_headers(
        {"X-Custom": "keep", "Connection": "close", "host": "drop"}
    )
    assert out == {"X-Custom": "keep"}


def test_filter_response_headers_drops_hop_by_hop():
    """Same on the response side."""
    out = _filter_response_headers({"X": "keep", "Transfer-Encoding": "drop"})
    assert out == {"X": "keep"}


def test_substitute_path_params_replaces_placeholders():
    """``{name}`` placeholders are replaced with the resolved value."""
    out = _substitute_path_params("/breakdown/{axis}", {"axis": "asset_class"})
    assert out == "/breakdown/asset_class"


def test_substitute_path_params_url_quotes_special_characters():
    """Values with slashes, spaces, etc. are URL-quoted (segment-safe)."""
    out = _substitute_path_params("/items/{name}", {"name": "a b/c"})
    assert out == "/items/a%20b%2Fc"


def test_substitute_path_params_no_op_when_template_lacks_placeholders():
    """Templates without ``{...}`` flow through unchanged."""
    assert _substitute_path_params("/static/path", {"x": "y"}) == "/static/path"


def test_substitute_path_params_handles_multiple_placeholders():
    """Multi-segment templates substitute all matching keys."""
    out = _substitute_path_params(
        "/{cat}/{sub}/leaf", {"cat": "equity", "sub": "price"}
    )
    assert out == "/equity/price/leaf"


def test_substitute_path_params_ignores_extra_kwargs():
    """Kwargs without a matching placeholder are silently dropped."""
    out = _substitute_path_params("/{x}", {"x": "1", "extra": "ignored"})
    assert out == "/1"


def test_build_app_from_spec_resolves_path_params(monkeypatch):
    """A synthesized route with a path param hits upstream with the param substituted."""
    spec = {
        "version": 5,
        "base_url": "https://upstream.example.com",
        "commands": {
            "breakdown": {
                "url_path": "/breakdown/{axis}",
                "method": "get",
                "parameters": [
                    {"name": "axis", "in": "path", "type": "string", "required": True}
                ],
            }
        },
    }
    app = build_app_from_spec(spec)

    captured: dict = {}

    class _StubUpstreamCM:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self.status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def read(self):
            return b"{}"

    class _StubSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def request(self, method, url, *, data=None, headers=None):
            captured["url"] = url
            return _StubUpstreamCM()

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", _StubSession)

    client = TestClient(app)
    response = client.get("/breakdown/asset_class")
    assert response.status_code == 200
    assert captured["url"].endswith("/breakdown/asset_class")
    assert "{axis}" not in captured["url"]


def test_rewrite_query_string_passthrough():
    """No map / empty input → original returned."""
    assert _rewrite_query_string("a=1", None) == "a=1"
    assert _rewrite_query_string("", {"a": "$a"}) == ""


def test_rewrite_query_string_swaps_keys():
    """Mapped keys are renamed; unmapped pass through."""
    assert _rewrite_query_string("limit=10&offset=0", {"limit": "$limit"}) == (
        "%24limit=10&offset=0"
    )


def test_rewrite_query_string_keeps_blank_values():
    """``?foo=`` round-trips correctly."""
    out = _rewrite_query_string("foo=", {})
    assert out == "foo="


def test_trim_uniform_zero_time_columns_top_level_list():
    """List of records → uniform-zero-time columns get stripped."""
    payload = [{"date": "2024-01-01T00:00:00.000"}, {"date": "2024-01-02T00:00:00"}]
    out = _trim_uniform_zero_time_columns(payload)
    assert out == [{"date": "2024-01-01"}, {"date": "2024-01-02"}]


def test_trim_uniform_zero_time_columns_envelope_dict():
    """Dict envelope → recurses into the row list."""
    payload = {"results": [{"d": "2024-01-01T00:00:00Z"}]}
    out = _trim_uniform_zero_time_columns(payload)
    assert out["results"] == [{"d": "2024-01-01"}]


def test_trim_uniform_zero_time_columns_one_real_time_blocks_strip():
    """Any row with a real time-of-day disqualifies the whole column."""
    payload = [
        {"date": "2024-01-01T00:00:00"},
        {"date": "2024-01-02T13:45:00"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert out == payload  # unchanged


def test_trim_uniform_zero_time_columns_no_op_for_non_list_dict():
    """Scalar payloads pass through unchanged."""
    assert _trim_uniform_zero_time_columns(42) == 42
    assert _trim_uniform_zero_time_columns("hi") == "hi"


def test_trim_uniform_zero_time_columns_dict_without_envelope_passes_through():
    """A dict without a recognized envelope key is returned as-is."""
    payload = {"foo": "bar"}
    assert _trim_uniform_zero_time_columns(payload) is payload


def test_trim_uniform_zero_time_columns_envelope_no_op_returns_payload():
    """Envelope dict whose inner list needs no trimming returns same identity."""
    payload = {"results": [{"d": "2024-01-01T13:45:00"}]}
    out = _trim_uniform_zero_time_columns(payload)
    assert out is payload


def test_trim_uniform_zero_time_in_records_skips_non_dict_records():
    """Heterogeneous lists with non-dict entries flow through untouched."""
    out = _trim_uniform_zero_time_in_records([{"d": "2024-01-01T00:00:00"}, "scalar"])
    assert "scalar" in out
    assert out[0] == {"d": "2024-01-01"}


def test_trim_uniform_zero_time_in_records_empty_returns_input():
    """Empty list flows through unchanged."""
    src: list = []
    assert _trim_uniform_zero_time_in_records(src) is src


def test_trim_uniform_zero_time_in_records_all_none_column_excluded():
    """Columns where every value is None aren't candidates for trim."""
    out = _trim_uniform_zero_time_in_records([{"x": None}, {"x": None}])
    assert out == [{"x": None}, {"x": None}]


def test_trim_uniform_zero_time_in_records_mixed_string_and_number_skipped():
    """Numeric values disqualify a column from string-stripping."""
    src = [{"x": 1}, {"x": "2024-01-01T00:00:00"}]
    out = _trim_uniform_zero_time_in_records(src)
    assert out is src  # unchanged identity


@pytest.mark.asyncio
async def test_proxy_request_forwards_and_strips_zero_time():
    """End-to-end: incoming request → upstream call → trimmed payload."""

    class _StubUpstreamCM:
        async def __aenter__(self_inner):
            self_inner.headers = {"Content-Type": "application/json"}
            self_inner.status = 200
            return self_inner

        async def __aexit__(self_inner, *args):
            return None

        async def read(self_inner):
            return json.dumps([{"date": "2024-01-01T00:00:00"}]).encode("utf-8")

    class _StubSession:
        def __init__(self_inner, *args, **kwargs):
            pass

        async def __aenter__(self_inner):
            return self_inner

        async def __aexit__(self_inner, *args):
            return None

        def request(self_inner, *args, **kwargs):
            return _StubUpstreamCM()

    request = MagicMock()
    request.body = AsyncMock(return_value=None)
    request.headers = {}
    request.url = MagicMock(query="")

    with patch("aiohttp.ClientSession", _StubSession):
        response = await _proxy_request(request, method="get", upstream_url="https://x")

    assert response.status_code == 200
    assert response.body == b'[{"date": "2024-01-01"}]'


def test_build_app_from_spec_serves_via_test_client(monkeypatch, spec_file):
    """The synthesized app passes a Starlette TestClient round-trip."""
    app = build_app_from_spec(load_spec(spec_file))

    captured: dict = {}

    class _StubUpstreamCM:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self.status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def read(self):
            return b'[{"date": "2024-01-01T00:00:00"}]'

    class _StubSession:
        def __init__(self, *args, **kwargs):
            captured["session_init"] = True

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def request(self, method, url, *, data=None, headers=None):
            captured["url"] = url
            captured["method"] = method
            return _StubUpstreamCM()

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", _StubSession)

    client = TestClient(app)
    response = client.get("/v1/ping?limit=10")
    assert response.status_code == 200
    assert response.json() == [{"date": "2024-01-01"}]
    assert "%24limit=10" in captured["url"]


def test_proxy_post_body_is_forwarded(monkeypatch, spec_file):
    """POST bodies are forwarded as the request data."""
    app = build_app_from_spec(load_spec(spec_file))

    captured: dict = {}

    class _StubUpstreamCM:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self.status = 201

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def read(self):
            return b'{"id": 1}'

    class _StubSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def request(self, method, url, *, data=None, headers=None):
            captured["data"] = data
            return _StubUpstreamCM()

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", _StubSession)

    client = TestClient(app)
    response = client.post("/v1/items", json={"name": "x"})
    assert response.status_code == 201
    assert json.loads(captured["data"]) == {"name": "x"}


def test_proxy_extra_headers_override_incoming(monkeypatch, spec_file):
    """Static extra headers from config override matching incoming headers."""
    app = build_app_from_spec(
        load_spec(spec_file), extra_headers={"Authorization": "Bearer static"}
    )

    captured: dict = {}

    class _StubUpstreamCM:
        def __init__(self):
            self.headers = {"Content-Type": "text/plain"}
            self.status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def read(self):
            return b"ok"

    class _StubSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def request(self, method, url, *, data=None, headers=None):
            captured["headers"] = headers
            return _StubUpstreamCM()

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", _StubSession)

    client = TestClient(app)
    client.get("/v1/ping?limit=10", headers={"Authorization": "Bearer incoming"})

    assert captured["headers"]["Authorization"] == "Bearer static"


def test_proxy_handles_invalid_json_response(monkeypatch, spec_file):
    """Non-JSON-decodable bodies pass through untouched."""
    app = build_app_from_spec(load_spec(spec_file))

    class _StubUpstreamCM:
        def __init__(self):
            self.headers = {"Content-Type": "application/json"}
            self.status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def read(self):
            return b"\xff\xfeNOT JSON"

    class _StubSession:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        def request(self, *args, **kwargs):
            return _StubUpstreamCM()

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", _StubSession)

    client = TestClient(app)
    response = client.get("/v1/ping?limit=10")
    assert response.status_code == 200
    assert response.content == b"\xff\xfeNOT JSON"
