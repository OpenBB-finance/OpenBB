"""Tests for ``openbb_mcp_server.app.spec``."""

import json
import sys
import types

import pytest
from fastapi import FastAPI, Request, Response
from starlette.routing import Mount
from starlette.testclient import TestClient

from openbb_mcp_server.app.spec import (
    SUPPORTED_SPEC_VERSIONS,
    _content_hash,
    _filter_request_headers,
    _filter_response_headers,
    _rewrite_query_string,
    _spec_param_to_openapi,
    _substitute_path_params,
    _trim_uniform_zero_time_columns,
    _trim_uniform_zero_time_in_records,
    build_app_from_spec,
    build_apps_from_specs,
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
            "url_path": "",
            "method": "get",
        },
        "skip_method": {
            "url_path": "/v1/x",
            "method": "patch",
        },
    },
}


@pytest.fixture
def spec_file(tmp_path):
    """Write SAMPLE_SPEC to a tmp .spec file (auto-stamped with hash)."""
    f = tmp_path / "test.spec"
    f.write_text(json.dumps(_stamp(SAMPLE_SPEC)))
    return f


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


class TestLoadSpec:
    """Loading, validating, and verifying ``.spec`` files."""

    def test_load_spec_returns_dict(self, spec_file):
        """A valid spec file parses cleanly."""
        spec = load_spec(spec_file)
        assert spec["version"] in SUPPORTED_SPEC_VERSIONS
        assert spec["base_url"] == "https://upstream.example.com"
        assert "ping" in spec["commands"]

    def test_load_spec_missing_path(self, tmp_path):
        """Missing file → FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_spec(tmp_path / "nope.spec")

    def test_load_spec_invalid_json(self, tmp_path):
        """Malformed JSON → ValueError."""
        f = tmp_path / "bad.spec"
        f.write_text("{not json")
        with pytest.raises(ValueError, match="not valid JSON"):
            load_spec(f)

    def test_load_spec_top_level_must_be_object(self, tmp_path):
        """JSON array at top level → ValueError."""
        f = tmp_path / "arr.spec"
        f.write_text("[]")
        with pytest.raises(ValueError, match="top-level object"):
            load_spec(f)

    def test_load_spec_unsupported_version(self, tmp_path):
        """Unknown ``version`` field → ValueError."""
        f = tmp_path / "v999.spec"
        f.write_text(json.dumps({"version": 999, "base_url": "x", "commands": {}}))
        with pytest.raises(ValueError, match="Unsupported spec version"):
            load_spec(f)

    def test_load_spec_missing_base_url(self, tmp_path):
        """Missing ``base_url`` → ValueError."""
        f = tmp_path / "nb.spec"
        f.write_text(json.dumps({"version": 5, "commands": {}}))
        with pytest.raises(ValueError, match="base_url"):
            load_spec(f)

    def test_load_spec_missing_commands(self, tmp_path):
        """Missing ``commands`` table → ValueError."""
        f = tmp_path / "nc.spec"
        f.write_text(json.dumps({"version": 5, "base_url": "x"}))
        with pytest.raises(ValueError, match="commands"):
            load_spec(f)

    def test_load_spec_rejects_structurally_invalid_command(self, tmp_path):
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

    def test_load_spec_rejects_non_string_base_url_via_pydantic(self, tmp_path):
        """A non-string ``base_url`` fails with the legacy error message."""
        f = tmp_path / "bad.spec"
        f.write_text(json.dumps({"version": 5, "base_url": 42, "commands": {}}))
        with pytest.raises(ValueError, match="base_url"):
            load_spec(f)

    def test_load_spec_accepts_optional_provenance_fields(self, tmp_path):
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

    def test_load_spec_verifies_matching_content_hash(self, tmp_path):
        """A spec carrying its own correctly-computed SHA-256 loads cleanly."""
        payload = _stamp(
            {
                "version": 5,
                "base_url": "https://x",
                "commands": {
                    "p": {"url_path": "/p", "method": "get", "parameters": []}
                },
            }
        )
        f = tmp_path / "h.spec"
        f.write_text(json.dumps(payload))
        out = load_spec(f)
        assert out["content_sha256"] == payload["content_sha256"]

    def test_load_spec_rejects_tampered_content_hash(self, tmp_path):
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

    def test_load_spec_rejects_spec_missing_content_sha256(self, tmp_path):
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

    def test_load_spec_accepts_deploy_config_hash_pin(self, tmp_path):
        """``expected_content_sha256`` supplied (matching) → loads cleanly."""
        payload = _stamp(
            {
                "version": 5,
                "base_url": "https://x",
                "commands": {
                    "p": {"url_path": "/p", "method": "get", "parameters": []}
                },
            }
        )
        f = tmp_path / "deploy-pinned.spec"
        f.write_text(json.dumps(payload))
        spec = load_spec(f, expected_content_sha256=payload["content_sha256"])
        assert spec is not None

    def test_load_spec_rejects_when_deploy_config_pin_mismatches(self, tmp_path):
        """``expected_content_sha256`` mismatch raises with ``deploy-config pin check``."""
        payload = _stamp(
            {
                "version": 5,
                "base_url": "https://x",
                "commands": {
                    "p": {"url_path": "/p", "method": "get", "parameters": []}
                },
            }
        )
        f = tmp_path / "drift.spec"
        f.write_text(json.dumps(payload))
        with pytest.raises(ValueError, match="deploy-config pin check"):
            load_spec(f, expected_content_sha256="0" * 64)

    def test_load_spec_deploy_pin_works_alongside_in_file_hash(self, tmp_path):
        """Matching in-file hash and ``expected_content_sha256`` both pass."""
        payload = _stamp(
            {
                "version": 5,
                "base_url": "https://x",
                "commands": {
                    "p": {"url_path": "/p", "method": "get", "parameters": []}
                },
            }
        )
        f = tmp_path / "double-checked.spec"
        f.write_text(json.dumps(payload))
        out = load_spec(f, expected_content_sha256=payload["content_sha256"])
        assert out["content_sha256"] == payload["content_sha256"]


class TestContentHash:
    """Canonical spec hashing."""

    def test_content_hash_is_stable_across_key_order(self):
        """Hashing is canonical (sorted keys); dict ordering doesn't move it."""
        a = {"version": 5, "base_url": "x", "commands": {}}
        b = {"commands": {}, "base_url": "x", "version": 5}
        assert _content_hash(a) == _content_hash(b)

    def test_content_hash_excludes_sha256_field(self):
        """Adding/removing the ``content_sha256`` field doesn't change the hash."""
        a = {"version": 5, "base_url": "x", "commands": {}}
        b = {**a, "content_sha256": "ignored"}
        assert _content_hash(a) == _content_hash(b)


class TestBuildAppFromSpec:
    """The single-spec proxy app."""

    def test_build_app_from_spec_exposes_provenance_metadata(self, tmp_path):
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
        assert (
            state.openbb_spec_source_url == "https://upstream.example.com/openapi.json"
        )
        assert state.openbb_spec_content_sha256 == payload["content_sha256"]
        assert state.openbb_spec_api_version == "3.1.0"

    def test_build_app_from_spec_state(self, spec_file):
        """``app.state`` carries the spec, base_url, source label, headers."""
        spec = load_spec(spec_file)
        app = build_app_from_spec(spec, spec_name="test.spec")
        assert isinstance(app, FastAPI)
        assert app.state.openbb_spec is spec
        assert app.state.openbb_spec_base_url == "https://upstream.example.com"
        assert app.state.openbb_spec_source == "test.spec"

    def test_build_app_from_spec_routes_registered(self, spec_file):
        """Each command becomes a FastAPI route."""
        app = build_app_from_spec(load_spec(spec_file))
        paths = {r.path for r in app.routes}
        assert "/v1/ping" in paths
        assert "/v1/items" in paths

    def test_build_app_from_spec_base_url_override(self, spec_file):
        """``base_url_override`` replaces the spec's recorded base_url."""
        app = build_app_from_spec(
            load_spec(spec_file), base_url_override="https://other.example.com"
        )
        assert app.state.openbb_spec_base_url == "https://other.example.com"

    def test_build_app_from_spec_extra_headers_persist(self, spec_file):
        """``extra_headers`` are stashed on app.state for the proxy to read."""
        app = build_app_from_spec(
            load_spec(spec_file), extra_headers={"Authorization": "Bearer x"}
        )
        assert app.state.openbb_spec_extra_headers == {"Authorization": "Bearer x"}

    def test_build_app_from_spec_skips_malformed_params(self, tmp_path):
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


UPSTREAM_BODIES: dict[str, tuple[int, str, bytes]] = {
    "/v1/ping": (200, "application/json", b'[{"date": "2024-01-01T00:00:00"}]'),
    "/v1/items": (201, "application/json", b'{"id": 1}'),
    "/v1/text": (200, "text/plain", b"ok"),
    "/v1/broken": (200, "application/json", b"\xff\xfeNOT JSON"),
}


def _upstream_app(recorded: list[dict]) -> FastAPI:
    api = FastAPI()

    @api.api_route("/{path:path}", methods=["GET", "POST"])
    async def upstream(path: str, request: Request) -> Response:
        recorded.append(
            {
                "method": request.method,
                "path": "/" + path,
                "query": request.url.query,
                "authorization": request.headers.get("authorization"),
                "body": await request.body(),
            }
        )
        status, media_type, body = UPSTREAM_BODIES.get(
            "/" + path, (200, "application/json", b"{}")
        )
        return Response(content=body, status_code=status, media_type=media_type)

    return api


@pytest.fixture(scope="module")
def upstream(serve):
    """Serve a recording upstream API and yield ``(base_url, recorded_requests)``."""
    recorded: list[dict] = []
    with serve(_upstream_app(recorded)) as url:
        yield url, recorded


@pytest.fixture
def proxy(upstream):
    """Build a proxy client for a spec pointing at the recording upstream."""
    url, recorded = upstream
    recorded.clear()
    spec = {
        "version": 5,
        "base_url": url + "/",
        "commands": {
            "ping": {
                "url_path": "/v1/ping",
                "method": "get",
                "parameters": [
                    {"name": "limit", "type": "integer", "wire_name": "$limit"}
                ],
            },
            "create": {"url_path": "/v1/items", "method": "post"},
            "text": {"url_path": "/v1/text", "method": "get"},
            "broken": {"url_path": "/v1/broken", "method": "get"},
            "breakdown": {
                "url_path": "/breakdown/{axis}",
                "method": "get",
                "parameters": [
                    {"name": "axis", "in": "path", "type": "string", "required": True}
                ],
            },
        },
    }
    app = build_app_from_spec(spec, extra_headers={"Authorization": "Bearer static"})
    with TestClient(app) as client:
        yield client, recorded


class TestSpecProxy:
    """Spec routes forwarding to a live upstream."""

    def test_get_renames_wire_params_and_trims_zero_times(self, proxy):
        """Query keys are renamed to wire names and midnight timestamps trimmed."""
        client, recorded = proxy
        response = client.get("/v1/ping", params={"limit": 10})
        assert response.status_code == 200
        assert response.json() == [{"date": "2024-01-01"}]
        assert recorded[-1]["query"] == "$limit=10"
        assert recorded[-1]["method"] == "GET"

    def test_post_body_is_forwarded(self, proxy):
        """POST bodies reach the upstream and its status code comes back."""
        client, recorded = proxy
        response = client.post("/v1/items", json={"name": "x"})
        assert response.status_code == 201
        assert response.json() == {"id": 1}
        assert json.loads(recorded[-1]["body"]) == {"name": "x"}

    def test_extra_headers_override_incoming(self, proxy):
        """Static extra headers replace matching incoming headers."""
        client, recorded = proxy
        client.get("/v1/text", headers={"Authorization": "Bearer incoming"})
        assert recorded[-1]["authorization"] == "Bearer static"

    def test_incoming_headers_pass_through_without_extra_headers(self, upstream):
        """Without static headers the incoming ``Authorization`` is forwarded."""
        url, recorded = upstream
        spec = {
            "version": 5,
            "base_url": url,
            "commands": {"text": {"url_path": "/v1/text", "method": "get"}},
        }
        with TestClient(build_app_from_spec(spec)) as client:
            client.get("/v1/text", headers={"Authorization": "Bearer incoming"})
        assert recorded[-1]["authorization"] == "Bearer incoming"

    def test_path_params_are_substituted(self, proxy):
        """Path parameters are resolved into the upstream URL."""
        client, recorded = proxy
        assert client.get("/breakdown/asset class").status_code == 200
        assert recorded[-1]["path"] == "/breakdown/asset class"

    def test_non_json_bodies_pass_through(self, proxy):
        """Plain-text and undecodable JSON bodies are returned untouched."""
        client, _ = proxy
        text = client.get("/v1/text")
        assert (text.headers["content-type"], text.content) == (
            "text/plain; charset=utf-8",
            b"ok",
        )
        assert client.get("/v1/broken").content == b"\xff\xfeNOT JSON"


class TestBuildAppsFromSpecs:
    """The multi-spec parent app."""

    def test_build_apps_from_specs_mounts_each_spec_at_named_prefix(self):
        """Each entry mounts under its dict-key prefix by default."""
        parent = build_apps_from_specs(
            {
                "equity": {"spec": _make_spec_dict()},
                "crypto": {"spec": _make_spec_dict()},
            }
        )
        assert "/equity" in parent.state.openbb_specs
        assert "/crypto" in parent.state.openbb_specs

    def test_build_apps_from_specs_explicit_mount_overrides_default(self):
        """``mount`` in the entry overrides the default ``/<name>`` prefix."""
        parent = build_apps_from_specs(
            {"equity": {"spec": _make_spec_dict(), "mount": "/markets/equity"}}
        )
        assert "/markets/equity" in parent.state.openbb_specs

    def test_build_apps_from_specs_normalizes_mount_without_leading_slash(self):
        """``mount = "equity"`` (no leading slash) gets normalized."""
        parent = build_apps_from_specs(
            {"x": {"spec": _make_spec_dict(), "mount": "stocks"}}
        )
        assert "/stocks" in parent.state.openbb_specs

    def test_build_apps_from_specs_rejects_mount_collision(self):
        """Two specs at the same mount → ValueError."""
        with pytest.raises(ValueError, match="mount collision"):
            build_apps_from_specs(
                {
                    "a": {"spec": _make_spec_dict(), "mount": "/dup"},
                    "b": {"spec": _make_spec_dict(), "mount": "/dup"},
                }
            )

    def test_build_apps_from_specs_rejects_empty_config(self):
        """An empty specs dict raises with a clear message."""
        with pytest.raises(ValueError, match="at least one spec entry"):
            build_apps_from_specs({})

    def test_build_apps_from_specs_rejects_non_dict_entry(self):
        """Non-dict entries fail fast."""
        with pytest.raises(TypeError, match="must be a dict"):
            build_apps_from_specs({"x": "not a dict"})

    def test_build_apps_from_specs_rejects_entry_missing_spec_field(self):
        """Entry without the required ``spec`` key fails."""
        with pytest.raises(ValueError, match="missing the required 'spec' field"):
            build_apps_from_specs({"x": {"mount": "/x"}})

    def test_build_apps_from_specs_state_carries_provenance(self, tmp_path):
        """Each mount's state snapshot carries the per-spec provenance."""
        spec_a = _stamp(
            {
                "version": 5,
                "base_url": "https://a.example.com",
                "generator": "openbb-cli==2.0.0",
                "commands": {
                    "p": {"url_path": "/p", "method": "get", "parameters": []}
                },
            }
        )
        parent = build_apps_from_specs({"a": {"spec": spec_a, "spec_name": "a.spec"}})
        snapshot = parent.state.openbb_specs["/a"]
        assert snapshot["name"] == "a"
        assert snapshot["spec_name"] == "a.spec"
        assert snapshot["base_url"] == "https://a.example.com"
        assert snapshot["generator"] == "openbb-cli==2.0.0"
        assert snapshot["content_sha256"] == spec_a["content_sha256"]

    def test_build_apps_from_specs_per_spec_middleware_hooks_applied(self, monkeypatch):
        """Per-spec ``middleware_hooks`` flow through to the sub-app's stack."""
        mod = types.ModuleType("test_multi_spec_hooks_mw")

        async def mw_hook(request, call_next):
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

    def test_build_apps_from_specs_per_spec_auth_hooks_applied(self, monkeypatch):
        """Per-spec ``auth_hooks`` flow through identically to middleware hooks."""
        mod = types.ModuleType("test_multi_spec_hooks_auth")

        async def auth_hook(request, call_next):
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

    def test_build_apps_from_specs_rejects_non_list_hook_table(self):
        """``middleware_hooks`` must be a list — non-list raises TypeError."""
        with pytest.raises(TypeError, match="must be a list"):
            build_apps_from_specs(
                {"a": {"spec": _make_spec_dict(), "middleware_hooks": "not a list"}}
            )

    def test_build_apps_from_specs_rejects_non_string_hook_entry(self):
        """Non-string hook entries inside the list raise TypeError."""
        with pytest.raises(TypeError, match="hook entries must be strings"):
            build_apps_from_specs(
                {"a": {"spec": _make_spec_dict(), "auth_hooks": [123]}}
            )


class TestSpecParamToOpenapi:
    """Converting spec parameters to OpenAPI parameters."""

    def test_spec_param_to_openapi_scalar(self):
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

    def test_spec_param_to_openapi_list(self):
        """``is_list`` produces an ``array`` schema with item type."""
        out = _spec_param_to_openapi(
            {"name": "tags", "type": "string", "is_list": True}
        )
        assert out["schema"] == {"type": "array", "items": {"type": "string"}}

    def test_spec_param_to_openapi_unknown_type_falls_back_to_string(self):
        """Unknown ``type`` falls back to ``string``."""
        out = _spec_param_to_openapi({"name": "x", "type": "weird"})
        assert out["schema"]["type"] == "string"


class TestSynthesizeOpenapiFromSpec:
    """Synthesizing an OpenAPI document from a spec."""

    def test_synthesize_openapi_from_spec_basic(self):
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

    def test_synthesize_openapi_skips_method_unknown(self):
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

    def test_synthesize_openapi_command_without_response_schema(self):
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


class TestHeaderFilters:
    """Dropping hop-by-hop headers."""

    def test_filter_request_headers_drops_hop_by_hop(self):
        """Hop-by-hop headers are stripped before forwarding upstream."""
        out = _filter_request_headers(
            {"X-Custom": "keep", "Connection": "close", "host": "drop"}
        )
        assert out == {"X-Custom": "keep"}

    def test_filter_response_headers_drops_hop_by_hop(self):
        """Same on the response side."""
        out = _filter_response_headers({"X": "keep", "Transfer-Encoding": "drop"})
        assert out == {"X": "keep"}


class TestSubstitutePathParams:
    """Resolving path-parameter placeholders."""

    def test_substitute_path_params_replaces_placeholders(self):
        """``{name}`` placeholders are replaced with the resolved value."""
        out = _substitute_path_params("/breakdown/{axis}", {"axis": "asset_class"})
        assert out == "/breakdown/asset_class"

    def test_substitute_path_params_url_quotes_special_characters(self):
        """Values with slashes, spaces, etc."""
        out = _substitute_path_params("/items/{name}", {"name": "a b/c"})
        assert out == "/items/a%20b%2Fc"

    def test_substitute_path_params_no_op_when_template_lacks_placeholders(self):
        """Templates without ``{...}`` flow through unchanged."""
        assert _substitute_path_params("/static/path", {"x": "y"}) == "/static/path"

    def test_substitute_path_params_handles_multiple_placeholders(self):
        """Multi-segment templates substitute all matching keys."""
        out = _substitute_path_params(
            "/{cat}/{sub}/leaf", {"cat": "equity", "sub": "price"}
        )
        assert out == "/equity/price/leaf"

    def test_substitute_path_params_ignores_extra_kwargs(self):
        """Kwargs without a matching placeholder are silently dropped."""
        out = _substitute_path_params("/{x}", {"x": "1", "extra": "ignored"})
        assert out == "/1"


class TestRewriteQueryString:
    """Renaming query keys to their wire names."""

    def test_rewrite_query_string_passthrough(self):
        """No map / empty input → original returned."""
        assert _rewrite_query_string("a=1", None) == "a=1"
        assert _rewrite_query_string("", {"a": "$a"}) == ""

    def test_rewrite_query_string_swaps_keys(self):
        """Mapped keys are renamed; unmapped pass through."""
        assert _rewrite_query_string("limit=10&offset=0", {"limit": "$limit"}) == (
            "%24limit=10&offset=0"
        )

    def test_rewrite_query_string_keeps_blank_values(self):
        """``?foo=`` round-trips correctly."""
        out = _rewrite_query_string("foo=", {})
        assert out == "foo="


class TestTrimUniformZeroTimeColumns:
    """Trimming midnight timestamps in response payloads."""

    def test_trim_uniform_zero_time_columns_top_level_list(self):
        """List of records → uniform-zero-time columns get stripped."""
        payload = [{"date": "2024-01-01T00:00:00.000"}, {"date": "2024-01-02T00:00:00"}]
        out = _trim_uniform_zero_time_columns(payload)
        assert out == [{"date": "2024-01-01"}, {"date": "2024-01-02"}]

    def test_trim_uniform_zero_time_columns_envelope_dict(self):
        """Dict envelope → recurses into the row list."""
        payload = {"results": [{"d": "2024-01-01T00:00:00Z"}]}
        out = _trim_uniform_zero_time_columns(payload)
        assert out["results"] == [{"d": "2024-01-01"}]

    def test_trim_uniform_zero_time_columns_one_real_time_blocks_strip(self):
        """Any row with a real time-of-day disqualifies the whole column."""
        payload = [
            {"date": "2024-01-01T00:00:00"},
            {"date": "2024-01-02T13:45:00"},
        ]
        out = _trim_uniform_zero_time_columns(payload)
        assert out == payload

    def test_trim_uniform_zero_time_columns_no_op_for_non_list_dict(self):
        """Scalar payloads pass through unchanged."""
        assert _trim_uniform_zero_time_columns(42) == 42
        assert _trim_uniform_zero_time_columns("hi") == "hi"

    def test_trim_uniform_zero_time_columns_dict_without_envelope_passes_through(self):
        """A dict without a recognized envelope key is returned as-is."""
        payload = {"foo": "bar"}
        assert _trim_uniform_zero_time_columns(payload) is payload

    def test_trim_uniform_zero_time_columns_envelope_no_op_returns_payload(self):
        """Envelope dict whose inner list needs no trimming returns same identity."""
        payload = {"results": [{"d": "2024-01-01T13:45:00"}]}
        out = _trim_uniform_zero_time_columns(payload)
        assert out is payload


class TestTrimUniformZeroTimeInRecords:
    """Trimming midnight timestamps in record lists."""

    def test_trim_uniform_zero_time_in_records_skips_non_dict_records(self):
        """Heterogeneous lists with non-dict entries flow through untouched."""
        out = _trim_uniform_zero_time_in_records(
            [{"d": "2024-01-01T00:00:00"}, "scalar"]
        )
        assert "scalar" in out
        assert out[0] == {"d": "2024-01-01"}

    def test_trim_uniform_zero_time_in_records_empty_returns_input(self):
        """Empty list flows through unchanged."""
        src: list = []
        assert _trim_uniform_zero_time_in_records(src) is src

    def test_trim_uniform_zero_time_in_records_all_none_column_excluded(self):
        """Columns where every value is None aren't candidates for trim."""
        out = _trim_uniform_zero_time_in_records([{"x": None}, {"x": None}])
        assert out == [{"x": None}, {"x": None}]

    def test_trim_uniform_zero_time_in_records_mixed_string_and_number_skipped(self):
        """Numeric values disqualify a column from string-stripping."""
        src = [{"x": 1}, {"x": "2024-01-01T00:00:00"}]
        out = _trim_uniform_zero_time_in_records(src)
        assert out is src
