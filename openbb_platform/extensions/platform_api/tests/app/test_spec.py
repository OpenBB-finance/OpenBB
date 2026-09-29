"""Tests for ``openbb_platform_api.app.spec`` — spec loading, OpenAPI
synthesis, proxy app construction, and end-to-end widgets.json
generation against a spec-built app.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from openbb_platform_api.app.spec import _content_hash


def _stamp(spec: dict) -> dict:
    """Stamp ``spec`` with a fresh ``content_sha256``.

    Every spec carries a ``content_sha256`` — the launcher refuses
    to load specs without one. This helper computes the canonical
    hash AFTER any field edits the test makes, matching the
    openbb-cli generator's stamp-at-write semantics.
    """
    spec = {k: v for k, v in spec.items() if k != "content_sha256"}
    spec["content_sha256"] = _content_hash(spec)
    return spec


SAMPLE_SPEC = {
    "version": 5,
    "base_url": "https://upstream.example.com/api/v1",
    "api_prefix": "/api/v1",
    "api_version": "3.1.0",
    "generated_at": "2026-05-07T00:00:00Z",
    "commands": {
        "equity.price.historical": {
            "url_path": "/api/v1/equity/price/historical",
            "method": "get",
            "description": "Historical OHLCV bars.",
            "providers": ["fmp"],
            "parameters": [
                {
                    "name": "symbol",
                    "in": "query",
                    "type": "string",
                    "is_list": False,
                    "required": True,
                    "default": None,
                    "choices": [],
                    "example": "AAPL",
                    "help": "The ticker symbol.",
                    "providers": ["fmp"],
                },
                {
                    "name": "interval",
                    "in": "query",
                    "type": "string",
                    "is_list": False,
                    "required": False,
                    "default": "1d",
                    "choices": ["1m", "5m", "1h", "1d"],
                    "example": None,
                    "help": "Bar size.",
                    "providers": ["fmp"],
                },
            ],
            "request_body_schema": None,
            "response_schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "format": "date",
                                    "title": "Date",
                                },
                                "close": {
                                    "type": "number",
                                    "title": "Close",
                                },
                            },
                        },
                    }
                },
            },
        },
        "user.preferences.update": {
            "url_path": "/api/v1/user/preferences",
            "method": "post",
            "description": "Update user preferences.",
            "providers": [],
            "parameters": [],
            "request_body_schema": {
                "type": "object",
                "properties": {"theme": {"type": "string", "enum": ["light", "dark"]}},
            },
            "response_schema": {"type": "boolean"},
        },
    },
    "routers": {},
    "reference": {},
}
SAMPLE_SPEC["content_sha256"] = _content_hash(SAMPLE_SPEC)


# ---------------------------------------------------------------------------
# load_spec — parse + structural validation
# ---------------------------------------------------------------------------


def test_load_spec_parses_well_formed_file(tmp_path):
    """Round-trip a well-formed spec through ``load_spec``."""
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "cli.spec"
    p.write_text(json.dumps(SAMPLE_SPEC))
    out = load_spec(p)
    assert out["base_url"] == SAMPLE_SPEC["base_url"]
    assert "equity.price.historical" in out["commands"]


def test_load_spec_raises_for_missing_file(tmp_path):
    """A missing path yields ``FileNotFoundError`` with the path in the
    message — operations error that needs to surface fast.
    """
    from openbb_platform_api.app.spec import load_spec

    with pytest.raises(FileNotFoundError, match="missing"):
        load_spec(tmp_path / "missing.spec")


def test_load_spec_raises_for_invalid_json(tmp_path):
    """Malformed JSON → ``ValueError`` (not ``json.JSONDecodeError``)
    so callers can treat all spec errors uniformly.
    """
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "broken.spec"
    p.write_text("{not json")
    with pytest.raises(ValueError, match="not valid JSON"):
        load_spec(p)


def test_load_spec_raises_for_unsupported_version(tmp_path):
    """Spec from a future / unknown version is rejected with a clear
    ``regenerate`` hint — protects against silent breakage when the
    spec format evolves.
    """
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "future.spec"
    spec = {**SAMPLE_SPEC, "version": 999}
    p.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match="Unsupported spec version"):
        load_spec(p)


def test_load_spec_raises_for_missing_base_url(tmp_path):
    """Without ``base_url`` the proxy has nowhere to forward — refuse
    to load instead of silently producing a non-functional launcher.
    """
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "no_base.spec"
    bad = {k: v for k, v in SAMPLE_SPEC.items() if k != "base_url"}
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="base_url"):
        load_spec(p)


def test_load_spec_raises_for_missing_commands_table(tmp_path):
    """Without ``commands`` there's nothing to proxy — refuse load."""
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "no_cmds.spec"
    bad = {k: v for k, v in SAMPLE_SPEC.items() if k != "commands"}
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="commands"):
        load_spec(p)


def test_load_spec_rejects_non_object_top_level(tmp_path):
    """A top-level array (or any non-object) is structurally wrong."""
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "list.spec"
    p.write_text("[]")
    with pytest.raises(ValueError, match="top-level"):
        load_spec(p)


# ---------------------------------------------------------------------------
# Spec provenance + integrity verification
# ---------------------------------------------------------------------------


def test_load_spec_rejects_structurally_invalid_command(tmp_path):
    """Pydantic schema rejects a command missing ``url_path``/``method``."""
    from openbb_platform_api.app.spec import load_spec

    p = tmp_path / "bad.spec"
    p.write_text(
        json.dumps(
            {
                "version": 5,
                "base_url": "https://x",
                "commands": {"oops": {"description": "no url_path/method"}},
            }
        )
    )
    with pytest.raises(ValueError, match="does not conform to the expected schema"):
        load_spec(p)


def test_load_spec_accepts_optional_provenance_fields(tmp_path):
    """``generator``/``generated_at``/``source_url``/``api_version`` are
    optional; their presence is preserved on the returned dict.
    """
    from openbb_platform_api.app.spec import load_spec

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
    p = tmp_path / "p.spec"
    p.write_text(json.dumps(payload))
    spec = load_spec(p)
    assert spec["generator"] == "openbb-cli==2.0.0"
    assert spec["generated_at"] == "2026-05-08T00:00:00Z"
    assert spec["source_url"] == "https://upstream.example.com/openapi.json"
    assert spec["api_version"] == "3.1.0"


def test_load_spec_verifies_matching_content_hash(tmp_path):
    """A spec carrying its own correctly-computed SHA-256 loads cleanly."""
    from openbb_platform_api.app.spec import load_spec

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    p = tmp_path / "h.spec"
    p.write_text(json.dumps(payload))
    out = load_spec(p)
    assert out["content_sha256"] == payload["content_sha256"]


def test_load_spec_rejects_tampered_content_hash(tmp_path):
    """A spec whose ``content_sha256`` no longer matches its body fails."""
    from openbb_platform_api.app.spec import load_spec

    payload = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        "content_sha256": "0" * 64,  # deliberately wrong
    }
    p = tmp_path / "tampered.spec"
    p.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="failed integrity check"):
        load_spec(p)


def test_load_spec_rejects_spec_missing_content_sha256(tmp_path):
    """``content_sha256`` is REQUIRED — every openbb-cli spec carries
    one, so an absent field indicates corruption / forgery and the
    launcher refuses to load.
    """
    from openbb_platform_api.app.spec import load_spec

    payload = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
    }
    p = tmp_path / "no-hash.spec"
    p.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="content_sha256"):
        load_spec(p)


def test_content_hash_is_stable_across_key_order():
    """Hashing is canonical (sorted keys) so payload dict ordering doesn't
    move the digest.
    """
    from openbb_platform_api.app.spec import _content_hash

    a = {"version": 5, "base_url": "x", "commands": {}}
    b = {"commands": {}, "base_url": "x", "version": 5}
    assert _content_hash(a) == _content_hash(b)


def test_content_hash_excludes_sha256_field():
    """Adding/removing the ``content_sha256`` field doesn't change the hash."""
    from openbb_platform_api.app.spec import _content_hash

    a = {"version": 5, "base_url": "x", "commands": {}}
    b = {**a, "content_sha256": "ignored"}
    assert _content_hash(a) == _content_hash(b)


def test_load_spec_accepts_deploy_config_hash_pin(tmp_path):
    """``expected_content_sha256`` supplied (matching) → loads cleanly."""
    from openbb_platform_api.app.spec import load_spec

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    p = tmp_path / "deploy-pinned.spec"
    p.write_text(json.dumps(payload))
    spec = load_spec(p, expected_content_sha256=payload["content_sha256"])
    assert spec is not None


def test_load_spec_rejects_when_deploy_config_pin_mismatches(tmp_path):
    """``expected_content_sha256`` mismatch → ValueError with explicit
    ``deploy-config pin check`` wording so ops can distinguish a
    config-pin failure from in-file tampering.
    """
    from openbb_platform_api.app.spec import load_spec

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    p = tmp_path / "drift.spec"
    p.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="deploy-config pin check"):
        load_spec(p, expected_content_sha256="0" * 64)


def test_load_spec_deploy_pin_works_alongside_in_file_hash(tmp_path):
    """In-file ``content_sha256`` (always present) AND
    ``expected_content_sha256`` matching → both checks pass.
    """
    from openbb_platform_api.app.spec import load_spec

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    p = tmp_path / "double-checked.spec"
    p.write_text(json.dumps(payload))
    out = load_spec(p, expected_content_sha256=payload["content_sha256"])
    assert out["content_sha256"] == payload["content_sha256"]


# ---------------------------------------------------------------------------
# build_apps_from_specs — multi-spec mounting
# ---------------------------------------------------------------------------


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
    from openbb_platform_api.app.spec import build_apps_from_specs

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
    from openbb_platform_api.app.spec import build_apps_from_specs

    parent = build_apps_from_specs(
        {"equity": {"spec": _make_spec_dict(), "mount": "/markets/equity"}}
    )
    assert "/markets/equity" in parent.state.openbb_specs


def test_build_apps_from_specs_normalizes_mount_without_leading_slash():
    """``mount = "stocks"`` (no leading slash) gets normalized to ``/stocks``."""
    from openbb_platform_api.app.spec import build_apps_from_specs

    parent = build_apps_from_specs(
        {"x": {"spec": _make_spec_dict(), "mount": "stocks"}}
    )
    assert "/stocks" in parent.state.openbb_specs


def test_build_apps_from_specs_rejects_mount_collision():
    """Two specs at the same mount → ValueError."""
    from openbb_platform_api.app.spec import build_apps_from_specs

    with pytest.raises(ValueError, match="mount collision"):
        build_apps_from_specs(
            {
                "a": {"spec": _make_spec_dict(), "mount": "/dup"},
                "b": {"spec": _make_spec_dict(), "mount": "/dup"},
            }
        )


def test_build_apps_from_specs_rejects_empty_config():
    """An empty specs dict raises with a clear message."""
    from openbb_platform_api.app.spec import build_apps_from_specs

    with pytest.raises(ValueError, match="at least one spec entry"):
        build_apps_from_specs({})


def test_build_apps_from_specs_rejects_non_dict_entry():
    """Non-dict entries fail fast."""
    from openbb_platform_api.app.spec import build_apps_from_specs

    with pytest.raises(TypeError, match="must be a dict"):
        build_apps_from_specs({"x": "not a dict"})  # type: ignore[arg-type]


def test_build_apps_from_specs_rejects_entry_missing_spec_field():
    """Entry without the required ``spec`` key fails."""
    from openbb_platform_api.app.spec import build_apps_from_specs

    with pytest.raises(ValueError, match="missing the required 'spec' field"):
        build_apps_from_specs({"x": {"mount": "/x"}})


def test_build_apps_from_specs_state_carries_provenance():
    """Each mount's state snapshot carries the per-spec provenance."""
    from openbb_platform_api.app.spec import build_apps_from_specs

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
    """Per-spec ``middleware_hooks`` flow through to the sub-app's
    middleware stack.
    """
    import sys
    import types

    from openbb_platform_api.app.spec import build_apps_from_specs

    mod = types.ModuleType("test_multi_spec_hooks_mw_papi")

    async def mw_hook(request, call_next):  # pragma: no cover
        return await call_next(request)

    mod.mw_hook = mw_hook
    monkeypatch.setitem(sys.modules, "test_multi_spec_hooks_mw_papi", mod)

    parent = build_apps_from_specs(
        {
            "a": {
                "spec": _make_spec_dict(),
                "middleware_hooks": ["test_multi_spec_hooks_mw_papi:mw_hook"],
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
    """Per-spec ``auth_hooks`` flow through identically."""
    import sys
    import types

    from openbb_platform_api.app.spec import build_apps_from_specs

    mod = types.ModuleType("test_multi_spec_hooks_auth_papi")

    async def auth_hook(request, call_next):  # pragma: no cover
        return await call_next(request)

    mod.auth_hook = auth_hook
    monkeypatch.setitem(sys.modules, "test_multi_spec_hooks_auth_papi", mod)

    parent = build_apps_from_specs(
        {
            "a": {
                "spec": _make_spec_dict(),
                "auth_hooks": ["test_multi_spec_hooks_auth_papi:auth_hook"],
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
    from openbb_platform_api.app.spec import build_apps_from_specs

    with pytest.raises(TypeError, match="must be a list"):
        build_apps_from_specs(
            {"a": {"spec": _make_spec_dict(), "middleware_hooks": "not a list"}}
        )


def test_build_apps_from_specs_rejects_non_string_hook_entry():
    """Non-string hook entries inside the list raise TypeError."""
    from openbb_platform_api.app.spec import build_apps_from_specs

    with pytest.raises(TypeError, match="hook entries must be strings"):
        build_apps_from_specs({"a": {"spec": _make_spec_dict(), "auth_hooks": [123]}})


# ---------------------------------------------------------------------------
# parse_args wiring — multi-spec
# ---------------------------------------------------------------------------


def test_collect_multi_spec_entries_filters_non_spec_subtables():
    """Sibling tables under ``[spec]`` (``headers``/``auth``/...)
    aren't mistaken for nested spec entries.
    """
    from openbb_platform_api.app.args import _collect_multi_spec_entries

    section = {
        "path": "/single.spec",
        "headers": {"Authorization": "x"},
        "equity": {"path": "/eq.spec"},
        "scalar_value": "ignored",
    }
    out = _collect_multi_spec_entries(section)
    assert out == {"equity": {"path": "/eq.spec"}}


def test_parse_args_loads_multi_spec_from_named_subtables(tmp_path):
    """``[spec.NAME]`` subtables build a parent with each spec mounted."""
    import sys
    from unittest.mock import patch

    from openbb_platform_api.app.args import parse_args
    from openbb_platform_api.app.config import reset_bootstrapped_config

    payload_a = _stamp(
        {
            "version": 5,
            "base_url": "https://a.example.com",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    payload_b = _stamp(
        {
            "version": 5,
            "base_url": "https://b.example.com",
            "commands": {"q": {"url_path": "/q", "method": "get", "parameters": []}},
        }
    )
    spec_a = tmp_path / "a.spec"
    spec_a.write_text(json.dumps(payload_a))
    spec_b = tmp_path / "b.spec"
    spec_b.write_text(json.dumps(payload_b))

    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        f"""
[spec.equity]
path = "{spec_a.as_posix()}"

[spec.crypto]
path = "{spec_b.as_posix()}"
"""
    )

    reset_bootstrapped_config()
    try:
        with patch.object(sys, "argv", ["openbb-api", "--config-file", str(cfg)]):
            out = parse_args()
        state = out["app"].state
        assert "/equity" in state.openbb_specs
        assert "/crypto" in state.openbb_specs
    finally:
        reset_bootstrapped_config()


def test_parse_args_multi_spec_relative_path_resolved_against_cwd(
    tmp_path, monkeypatch
):
    """Per-spec relative paths resolve against CWD."""
    import sys
    from unittest.mock import patch

    from openbb_platform_api.app.args import parse_args
    from openbb_platform_api.app.config import reset_bootstrapped_config

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    spec = tmp_path / "rel.spec"
    spec.write_text(json.dumps(payload))
    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        """
[spec.rel]
path = "rel.spec"
"""
    )
    monkeypatch.chdir(tmp_path)

    reset_bootstrapped_config()
    try:
        with patch.object(sys, "argv", ["openbb-api", "--config-file", str(cfg)]):
            out = parse_args()
        assert "/rel" in out["app"].state.openbb_specs
    finally:
        reset_bootstrapped_config()


def test_parse_args_multi_spec_per_spec_content_sha256_pin(tmp_path):
    """Each ``[spec.NAME]`` subtable's ``content_sha256`` flows to that
    spec's ``load_spec`` — a mismatch on one entry kills startup.
    """
    import sys
    from unittest.mock import patch

    from openbb_platform_api.app.args import parse_args
    from openbb_platform_api.app.config import reset_bootstrapped_config

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    spec = tmp_path / "pinned.spec"
    spec.write_text(json.dumps(payload))
    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        f"""
[spec.equity]
path = "{spec.as_posix()}"
content_sha256 = "{"f" * 64}"
"""
    )

    reset_bootstrapped_config()
    try:
        with patch.object(sys, "argv", ["openbb-api", "--config-file", str(cfg)]):
            with pytest.raises(ValueError, match="deploy-config pin check"):
                parse_args()
    finally:
        reset_bootstrapped_config()


def test_parse_args_multi_spec_with_per_spec_hooks(tmp_path, monkeypatch):
    """Per-spec auth + middleware hooks land on the sub-app's middleware
    stack via the full parse_args → load_spec → build_apps_from_specs
    chain.
    """
    import sys
    import types
    from unittest.mock import patch

    from openbb_platform_api.app.args import parse_args
    from openbb_platform_api.app.config import reset_bootstrapped_config

    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    spec = tmp_path / "hooks.spec"
    spec.write_text(json.dumps(payload))

    mod = types.ModuleType("test_multi_spec_args_hooks_papi")

    async def auth(request, call_next):  # pragma: no cover
        return await call_next(request)

    async def mw(request, call_next):  # pragma: no cover
        return await call_next(request)

    mod.auth = auth
    mod.mw = mw
    monkeypatch.setitem(sys.modules, "test_multi_spec_args_hooks_papi", mod)

    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        f"""
[spec.equity]
path = "{spec.as_posix()}"
[spec.equity.auth]
hooks = ["test_multi_spec_args_hooks_papi:auth"]
[spec.equity.middleware]
hooks = ["test_multi_spec_args_hooks_papi:mw"]
"""
    )

    reset_bootstrapped_config()
    try:
        with patch.object(sys, "argv", ["openbb-api", "--config-file", str(cfg)]):
            out = parse_args()
    finally:
        reset_bootstrapped_config()

    from starlette.routing import Mount

    for route in out["app"].routes:
        if isinstance(route, Mount) and route.name == "equity":
            sub_app = route.app
            dispatchers = {
                getattr(m, "kwargs", {}).get("dispatch")
                for m in sub_app.user_middleware
            }
            assert auth in dispatchers
            assert mw in dispatchers
            break
    else:
        raise AssertionError("Expected mounted sub-app 'equity'.")


def test_parse_args_passes_deploy_config_hash_pin_to_load_spec(tmp_path):
    """``[spec].content_sha256`` from the deploy TOML is forwarded to
    ``load_spec`` — when it mismatches, ``parse_args`` raises with the
    pin-check error so a misconfigured deployment fails at startup.
    """
    import sys
    from unittest.mock import patch

    from openbb_platform_api.app.args import parse_args
    from openbb_platform_api.app.config import reset_bootstrapped_config

    # Build a fully-stamped spec; the deploy TOML pins a deliberately
    # wrong expected hash to trigger the pin-check failure.
    payload = _stamp(
        {
            "version": 5,
            "base_url": "https://x",
            "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
        }
    )
    spec_file = tmp_path / "pinned.spec"
    spec_file.write_text(json.dumps(payload))

    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        f"""
[spec]
path = "{spec_file.as_posix()}"
content_sha256 = "{"f" * 64}"
"""
    )

    reset_bootstrapped_config()
    try:
        with patch.object(sys, "argv", ["openbb-api", "--config-file", str(cfg_file)]):
            with pytest.raises(ValueError, match="deploy-config pin check"):
                parse_args()
    finally:
        reset_bootstrapped_config()


def test_build_app_from_spec_exposes_provenance_metadata(tmp_path):
    """Every recorded provenance field flows onto ``app.state`` so
    callers (widgets builder, telemetry, custom middleware) can
    fingerprint the active spec.
    """
    from openbb_platform_api.app.spec import (
        _content_hash,
        build_app_from_spec,
        load_spec,
    )

    payload = {
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
    payload["content_sha256"] = _content_hash(payload)
    p = tmp_path / "prov.spec"
    p.write_text(json.dumps(payload))

    app = build_app_from_spec(load_spec(p), spec_name="prov.spec")
    state = app.state
    assert state.openbb_spec_version == 5
    assert state.openbb_spec_generator == "openbb-cli==2.0.0"
    assert state.openbb_spec_generated_at == "2026-05-08T00:00:00Z"
    assert state.openbb_spec_source_url == "https://upstream.example.com/openapi.json"
    assert state.openbb_spec_content_sha256 == payload["content_sha256"]
    assert state.openbb_spec_api_version == "3.1.0"


# ---------------------------------------------------------------------------
# synthesize_openapi_from_spec — build_json fodder
# ---------------------------------------------------------------------------


def test_synthesize_openapi_produces_paths_for_each_command():
    """Every command becomes a ``paths[url_path][method]`` entry."""
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    out = synthesize_openapi_from_spec(SAMPLE_SPEC)
    assert "/api/v1/equity/price/historical" in out["paths"]
    assert "get" in out["paths"]["/api/v1/equity/price/historical"]
    assert "post" in out["paths"]["/api/v1/user/preferences"]


def test_synthesize_openapi_renests_parameters_into_schema_block():
    """Spec hoists ``type``/``default``/``choices`` to the top of the
    parameter dict; OpenAPI nests them under ``schema``. The synthesizer
    re-nests so the launcher's widget builder reads them where it
    expects.
    """
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    out = synthesize_openapi_from_spec(SAMPLE_SPEC)
    op = out["paths"]["/api/v1/equity/price/historical"]["get"]
    interval = next(p for p in op["parameters"] if p["name"] == "interval")
    assert interval["schema"]["type"] == "string"
    assert interval["schema"]["default"] == "1d"
    assert interval["schema"]["enum"] == ["1m", "5m", "1h", "1d"]
    assert interval["required"] is False


def test_synthesize_openapi_marks_required_params():
    """``required: true`` round-trips."""
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    out = synthesize_openapi_from_spec(SAMPLE_SPEC)
    op = out["paths"]["/api/v1/equity/price/historical"]["get"]
    symbol = next(p for p in op["parameters"] if p["name"] == "symbol")
    assert symbol["required"] is True


def test_synthesize_openapi_translates_is_list_to_array_schema():
    """A ``is_list: true`` spec param becomes ``type: "array"`` with
    ``items`` carrying the original scalar type.
    """
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    spec = {
        **SAMPLE_SPEC,
        "commands": {
            "x": {
                "url_path": "/x",
                "method": "get",
                "parameters": [
                    {
                        "name": "tickers",
                        "in": "query",
                        "type": "string",
                        "is_list": True,
                        "required": False,
                        "default": None,
                        "choices": [],
                    }
                ],
            }
        },
    }
    out = synthesize_openapi_from_spec(spec)
    p = out["paths"]["/x"]["get"]["parameters"][0]
    assert p["schema"] == {"type": "array", "items": {"type": "string"}}


def test_synthesize_openapi_skips_command_without_url_path():
    """A malformed command (missing ``url_path``) is dropped instead
    of crashing the synthesis — defensive against partial specs.
    """
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    spec = {
        **SAMPLE_SPEC,
        "commands": {"bad": {"method": "get"}, **SAMPLE_SPEC["commands"]},
    }
    out = synthesize_openapi_from_spec(spec)
    # Only the well-formed entries land.
    paths = list(out["paths"])
    assert "/api/v1/equity/price/historical" in paths
    # No path for the bad command.
    assert all("bad" not in p for p in paths)


def test_synthesize_openapi_skips_command_with_unknown_method():
    """``method: delete`` (or anything other than get/post) is dropped
    — the launcher only synthesizes Workspace-relevant verbs.
    """
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    spec = {
        **SAMPLE_SPEC,
        "commands": {"del": {"url_path": "/x", "method": "delete", "parameters": []}},
    }
    out = synthesize_openapi_from_spec(spec)
    assert "/x" not in out["paths"]


def test_synthesize_openapi_carries_response_schema_into_responses_block():
    """The spec's ``response_schema`` lands at
    ``paths[...].get.responses["200"].content["application/json"].schema``
    — exactly where the launcher's column auto-detection reads it.
    """
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    out = synthesize_openapi_from_spec(SAMPLE_SPEC)
    op = out["paths"]["/api/v1/equity/price/historical"]["get"]
    schema = op["responses"]["200"]["content"]["application/json"]["schema"]
    assert "properties" in schema
    assert "results" in schema["properties"]


def test_synthesize_openapi_handles_post_request_body_schema():
    """POST commands get their ``request_body_schema`` wired into
    ``requestBody.content."application/json".schema``.
    """
    from openbb_platform_api.app.spec import synthesize_openapi_from_spec

    out = synthesize_openapi_from_spec(SAMPLE_SPEC)
    op = out["paths"]["/api/v1/user/preferences"]["post"]
    body = op["requestBody"]["content"]["application/json"]["schema"]
    assert body["properties"]["theme"]["enum"] == ["light", "dark"]


# ---------------------------------------------------------------------------
# build_app_from_spec — FastAPI synthesis
# ---------------------------------------------------------------------------


def test_build_app_registers_one_route_per_command():
    """Each spec command becomes one FastAPI route at its ``url_path``."""
    from openbb_platform_api.app.spec import build_app_from_spec

    app = build_app_from_spec(SAMPLE_SPEC)
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    assert "/api/v1/equity/price/historical" in paths
    assert "/api/v1/user/preferences" in paths


def test_build_app_skips_malformed_commands():
    """Commands missing ``url_path`` or with an unsupported method are
    silently dropped — partial / forward-compatible specs shouldn't
    crash the launcher.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    spec = {
        **SAMPLE_SPEC,
        "commands": {
            "no_url": {"method": "get", "parameters": []},
            "delete_method": {
                "url_path": "/api/v1/x",
                "method": "delete",
                "parameters": [],
            },
            **SAMPLE_SPEC["commands"],
        },
    }
    app = build_app_from_spec(spec)
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    # The well-formed entries are still present.
    assert "/api/v1/equity/price/historical" in paths
    # The malformed ones produced no routes.
    assert "/api/v1/x" not in paths


def test_build_app_records_spec_on_app_state():
    """The original spec + base_url are stashed on ``app.state`` so
    callers can introspect what was built.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    app = build_app_from_spec(SAMPLE_SPEC)
    assert app.state.openbb_spec is SAMPLE_SPEC
    assert app.state.openbb_spec_base_url == SAMPLE_SPEC["base_url"]


def test_build_app_openapi_parameters_drive_widgets_json():
    """End-to-end: a spec-built app's generated OpenAPI feeds the
    launcher's ``build_json``, which produces a widget per command.
    Regression guard for the whole reason the spec → openapi_extra
    bridge exists.
    """
    from openbb_platform_api.app.spec import build_app_from_spec
    from openbb_platform_api.utils.widgets import build_json

    app = build_app_from_spec(SAMPLE_SPEC)
    # Trigger FastAPI's lazy openapi build.
    openapi = app.openapi()
    out = build_json(openapi, [])
    # The historical-price command surfaces as a widget (custom
    # provider since the spec doesn't carry the OpenBB provider param
    # mechanism — that's fine, the launcher treats it as ``custom``).
    historical_widgets = [w for w_id, w in out.items() if "historical" in w_id]
    assert historical_widgets, f"No historical widget found in {list(out)}"
    widget = historical_widgets[0]
    # Parameter metadata flowed through unchanged.
    param_names = {p["paramName"] for p in widget.get("params", [])}
    assert "symbol" in param_names
    assert "interval" in param_names


def test_build_app_post_routes_marked_excluded_unless_special_type():
    """POST routes (other than ssrm/omni/multi-file) get added to the
    exclude filter by ``build_json`` — same treatment as a real
    in-process app's POST endpoints. Regression guard against the spec
    proxy generating ghost POST widgets.
    """
    from openbb_platform_api.app.spec import build_app_from_spec
    from openbb_platform_api.utils.widgets import build_json

    app = build_app_from_spec(SAMPLE_SPEC)
    openapi = app.openapi()
    exclude_filter: list = []
    build_json(openapi, exclude_filter)
    # The POST command's widget id is filtered out.
    assert any("user_preferences" in entry for entry in exclude_filter)


# ---------------------------------------------------------------------------
# _substitute_path_params — path-template resolution before forwarding
# ---------------------------------------------------------------------------


def test_substitute_path_params_replaces_placeholders():
    """``{name}`` placeholders are replaced with the resolved value."""
    from openbb_platform_api.app.spec import _substitute_path_params

    out = _substitute_path_params("/breakdown/{axis}", {"axis": "asset_class"})
    assert out == "/breakdown/asset_class"


def test_substitute_path_params_url_quotes_special_characters():
    """Values with slashes, spaces, etc. are URL-quoted (segment-safe)."""
    from openbb_platform_api.app.spec import _substitute_path_params

    out = _substitute_path_params("/items/{name}", {"name": "a b/c"})
    assert out == "/items/a%20b%2Fc"


def test_substitute_path_params_no_op_when_template_lacks_placeholders():
    """Templates without ``{...}`` flow through unchanged."""
    from openbb_platform_api.app.spec import _substitute_path_params

    assert _substitute_path_params("/static/path", {"x": "y"}) == "/static/path"


def test_substitute_path_params_handles_multiple_placeholders():
    """Multi-segment templates substitute all matching keys."""
    from openbb_platform_api.app.spec import _substitute_path_params

    out = _substitute_path_params(
        "/{cat}/{sub}/leaf", {"cat": "equity", "sub": "price"}
    )
    assert out == "/equity/price/leaf"


def test_substitute_path_params_ignores_extra_kwargs():
    """Kwargs without a matching placeholder are silently dropped."""
    from openbb_platform_api.app.spec import _substitute_path_params

    out = _substitute_path_params("/{x}", {"x": "1", "extra": "ignored"})
    assert out == "/1"


def test_build_app_resolves_path_params_before_forwarding(monkeypatch):
    """End-to-end regression: a route with a ``{axis}`` template hits the
    upstream URL with the param value substituted (not the template).

    Caught against the BlackRock spec during the live integration test
    of ``openbb-mcp`` — the same proxy machinery lives here.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    spec = {
        "version": 5,
        "base_url": "https://upstream.example.com",
        "commands": {
            "breakdown": {
                "url_path": "/breakdown/{axis}",
                "method": "get",
                "parameters": [
                    {
                        "name": "axis",
                        "in": "path",
                        "type": "string",
                        "required": True,
                    }
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
    # Upstream URL has the resolved value, not ``{axis}``.
    assert captured["url"].endswith("/breakdown/asset_class")
    assert "{axis}" not in captured["url"]


# ---------------------------------------------------------------------------
# Proxy handler — request forwarding
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_proxy_request_forwards_method_query_and_body():
    """The proxy replays method, query string, body, and headers
    against ``upstream_url``, and streams the response back.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    fake_upstream_response = MagicMock()
    fake_upstream_response.read = AsyncMock(
        return_value=b'{"results": [{"date": "2024-01-01", "close": 100.0}]}'
    )
    fake_upstream_response.headers = {"Content-Type": "application/json"}
    fake_upstream_response.status = 200

    fake_session_ctx = MagicMock()
    fake_session_ctx.__aenter__ = AsyncMock(return_value=fake_upstream_response)
    fake_session_ctx.__aexit__ = AsyncMock(return_value=None)

    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=fake_session_ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(SAMPLE_SPEC)
    client = TestClient(app)

    with patch("aiohttp.ClientSession", return_value=fake_session):
        response = client.get(
            "/api/v1/equity/price/historical?symbol=AAPL&interval=1d",
            headers={"Authorization": "Bearer xyz"},
        )

    assert response.status_code == 200
    assert response.json() == {"results": [{"date": "2024-01-01", "close": 100.0}]}
    # Verify forward used the right URL + method + headers.
    call_args, call_kwargs = fake_session.request.call_args
    assert call_args[0] == "GET"
    assert call_args[1].startswith(SAMPLE_SPEC["base_url"])
    assert "symbol=AAPL" in call_args[1]
    assert call_kwargs["headers"].get("authorization") == "Bearer xyz"


def test_proxy_filters_hop_by_hop_request_headers():
    """Hop-by-hop headers (``Connection``, ``Transfer-Encoding``,
    etc.) must NOT cross the proxy — RFC 7230 §6.1.
    """
    from openbb_platform_api.app.spec import _filter_request_headers

    incoming = {
        "Authorization": "Bearer xyz",
        "Connection": "keep-alive",
        "Host": "client.example.com",
        "Transfer-Encoding": "chunked",
        "X-Custom": "preserve-me",
    }
    out = _filter_request_headers(incoming)
    assert "Authorization" in out
    assert "X-Custom" in out
    assert "Connection" not in out
    assert "Host" not in out
    assert "Transfer-Encoding" not in out


def test_proxy_filters_hop_by_hop_response_headers():
    """Same filter on the response side — let the launcher's response
    infrastructure set Content-Length / Content-Encoding rather than
    echoing potentially mismatched upstream values.
    """
    from openbb_platform_api.app.spec import _filter_response_headers

    incoming = {
        "Content-Type": "application/json",
        "Content-Length": "9999",
        "Content-Encoding": "gzip",
        "X-Trace-Id": "abc",
    }
    out = _filter_response_headers(incoming)
    assert "Content-Type" in out
    assert "X-Trace-Id" in out
    assert "Content-Length" not in out
    assert "Content-Encoding" not in out


# ---------------------------------------------------------------------------
# parse_args integration — --spec hooks into the launcher
# ---------------------------------------------------------------------------


def test_parse_args_loads_spec_into_app_kwarg(tmp_path, monkeypatch):
    """``--spec /path/to/cli.spec`` results in ``kwargs["app"]`` being
    a synthesized FastAPI instance (same slot ``--app`` populates).
    The spec file's full name (extension included) is captured on
    ``app.state.openbb_spec_source`` for use as the widget citation
    label.
    """
    import sys

    from openbb_platform_api.app.args import parse_args

    spec_file = tmp_path / "fertilizer.spec"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))
    monkeypatch.setattr(sys, "argv", ["openbb-api", "--spec", str(spec_file)])
    out = parse_args()
    # The synthesized app is in the ``app`` slot — uvicorn-ready.
    app = out.get("app")
    assert app is not None
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    assert "/api/v1/equity/price/historical" in paths
    # Full filename (extension included) flows through as the spec
    # source — ``widgets_service`` uses this to override the
    # auto-generated ``["Custom"]`` source on every widget.
    assert app.state.openbb_spec_source == "fertilizer.spec"


def test_build_app_base_url_override_replaces_spec_recorded_url():
    """``base_url_override`` swaps the spec's recorded ``base_url``.
    Lets a single spec serve staging/prod or reroute internal hosts
    without regenerating the file.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    app = build_app_from_spec(
        SAMPLE_SPEC, base_url_override="https://elsewhere.example.com/api/v1"
    )
    assert app.state.openbb_spec_base_url == "https://elsewhere.example.com/api/v1"


def test_build_app_spec_name_captured_on_app_state():
    """``spec_name`` is stashed on ``app.state.openbb_spec_source`` so
    ``widgets_service.get_widgets_json`` can use it as the citation
    label that overrides the auto-generated ``["Custom"]`` source.
    Stored verbatim — the caller (``parse_args``) decides on the
    full filename vs. stem; this layer just relays.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    app = build_app_from_spec(SAMPLE_SPEC, spec_name="fertilizer.spec")
    assert app.state.openbb_spec_source == "fertilizer.spec"


def test_build_app_spec_name_defaults_to_none_for_legacy_callers():
    """Legacy callers that don't pass ``spec_name`` get ``None`` on
    ``app.state.openbb_spec_source``, which the override helper treats
    as a no-op signal.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    app = build_app_from_spec(SAMPLE_SPEC)
    assert app.state.openbb_spec_source is None


def test_build_app_extra_headers_recorded_on_app_state():
    """Static headers from ``[spec.headers]`` are captured on
    ``app.state`` so the proxy handlers can reference the same dict
    without per-request closure copies.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    headers = {"Authorization": "Bearer abc", "X-API-Key": "xyz"}
    app = build_app_from_spec(SAMPLE_SPEC, extra_headers=headers)
    assert app.state.openbb_spec_extra_headers == headers


def test_proxy_extra_headers_override_incoming_request_headers():
    """Config-supplied headers OVERRIDE matching incoming-request
    headers. Reasoning: ``[spec.headers]`` is the credential
    injection point — a misbehaving client can't leak its own auth
    value upstream by sending the same header name.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    fake_upstream_response = MagicMock()
    fake_upstream_response.read = AsyncMock(return_value=b"{}")
    fake_upstream_response.headers = {"Content-Type": "application/json"}
    fake_upstream_response.status = 200

    fake_session_ctx = MagicMock()
    fake_session_ctx.__aenter__ = AsyncMock(return_value=fake_upstream_response)
    fake_session_ctx.__aexit__ = AsyncMock(return_value=None)
    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=fake_session_ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(
        SAMPLE_SPEC,
        extra_headers={"Authorization": "Bearer SERVER-CREDENTIAL"},
    )
    client = TestClient(app)

    with patch("aiohttp.ClientSession", return_value=fake_session):
        client.get(
            "/api/v1/equity/price/historical?symbol=AAPL",
            headers={"Authorization": "Bearer CLIENT-LEAKED"},
        )

    forwarded = fake_session.request.call_args.kwargs["headers"]
    # Server-supplied credential wins. Client-supplied auth header
    # never reaches upstream.
    assert forwarded.get("Authorization") == "Bearer SERVER-CREDENTIAL"


def test_parse_args_resolves_relative_spec_path_against_cwd(tmp_path, monkeypatch):
    """A relative ``[spec] path`` is resolved against ``cwd``. Lets a
    config file in the project root point at a sibling ``./cli.spec``
    without absolute paths.
    """
    import sys

    from openbb_platform_api.app.args import parse_args

    spec_file = tmp_path / "cli.spec"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))

    config_file = tmp_path / "openbb.toml"
    config_file.write_text('[spec]\npath = "cli.spec"\n')

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["openbb-api", "--config-file", str(config_file)])

    out = parse_args()
    app = out["app"]
    # App was successfully built — relative path resolved against cwd.
    assert hasattr(app.state, "openbb_spec")


def test_expand_spec_headers_skips_non_string_keys():
    """A malformed ``[spec.headers]`` entry with a non-string key
    (impossible from real TOML, but defensive against programmatic
    misuse) is silently dropped — TOML libraries can produce
    surprising shapes when configs are merged.
    """
    from openbb_platform_api.app.args import _expand_spec_headers

    out = _expand_spec_headers({42: "bad-key", "X-Good": "ok"})
    assert out == {"X-Good": "ok"}


def test_expand_spec_headers_returns_empty_for_none_or_empty():
    """Missing / empty headers table → empty dict, no crash."""
    from openbb_platform_api.app.args import _expand_spec_headers

    assert _expand_spec_headers(None) == {}
    assert _expand_spec_headers({}) == {}


def test_parse_args_loads_spec_table_with_headers_and_base_url(tmp_path, monkeypatch):
    """``[spec]`` table populates path, base_url override, and the
    headers table. ``[spec.headers]`` resolves ``$VAR`` references
    against the (already-applied) ``[env]`` table — credential
    injection in the single-config-file deployment scenario.
    """
    import sys

    from openbb_platform_api.app.args import parse_args

    spec_file = tmp_path / "cli.spec"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))

    config_file = tmp_path / "openbb.toml"
    # ``.as_posix()`` keeps forward slashes on Windows so the TOML
    # parser doesn't interpret ``\U`` / ``\r`` / etc. inside the
    # interpolated path as hex/escape sequences. Forward slashes are
    # accepted by Python's ``os.path``/``Path`` on every platform.
    config_file.write_text(
        f'''
[env]
OPENBB_UPSTREAM_TOKEN = "tok-from-env"

[spec]
path = "{spec_file.as_posix()}"
base_url = "https://prod.example.com"

[spec.headers]
Authorization = "Bearer $OPENBB_UPSTREAM_TOKEN"
X-Static = "literal-value"
'''
    )

    monkeypatch.setattr(sys, "argv", ["openbb-api", "--config-file", str(config_file)])
    # Make sure no leftover env causes a collision.
    monkeypatch.delenv("OPENBB_UPSTREAM_TOKEN", raising=False)

    # main.py's bootstrap normally applies [env] before parse_args
    # runs. Mimic that here so the $VAR refs in [spec.headers]
    # resolve against an os.environ that already has the value.
    from openbb_platform_api.app.config import bootstrap_launcher_config

    bootstrap_launcher_config(["--config-file", str(config_file)])

    out = parse_args()
    app = out["app"]
    assert app.state.openbb_spec_base_url == "https://prod.example.com"
    headers = app.state.openbb_spec_extra_headers
    assert headers["Authorization"] == "Bearer tok-from-env"
    assert headers["X-Static"] == "literal-value"


def test_parse_args_skips_spec_header_with_unresolved_var(
    tmp_path, monkeypatch, caplog
):
    """A ``[spec.headers]`` entry referencing an unset variable is
    SKIPPED (not set to the literal ``$MISSING``) and a warning
    surfaces — same semantics as ``[env]`` injection.
    """
    import logging
    import sys

    from openbb_platform_api.app.args import parse_args

    spec_file = tmp_path / "cli.spec"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))

    config_file = tmp_path / "openbb.toml"
    # ``.as_posix()`` keeps forward slashes on Windows so the TOML
    # parser doesn't interpret ``\U`` / ``\r`` / etc. inside the
    # interpolated path as hex/escape sequences.
    config_file.write_text(
        f'''
[spec]
path = "{spec_file.as_posix()}"

[spec.headers]
Authorization = "Bearer $NEVER_SET_ANYWHERE"
X-Good = "just-text"
'''
    )

    monkeypatch.setattr(sys, "argv", ["openbb-api", "--config-file", str(config_file)])
    monkeypatch.delenv("NEVER_SET_ANYWHERE", raising=False)

    with caplog.at_level(logging.WARNING, logger="openbb_platform_api.spec.headers"):
        out = parse_args()
    app = out["app"]
    headers = app.state.openbb_spec_extra_headers
    # Bad header dropped; good one passes through.
    assert "Authorization" not in headers
    assert headers.get("X-Good") == "just-text"
    # Warning surfaces the missing var name + header name.
    assert any(
        "Authorization" in r.message and "NEVER_SET_ANYWHERE" in r.message
        for r in caplog.records
    )


def test_parse_args_rejects_spec_and_app_combined(tmp_path, monkeypatch):
    """``--spec`` and ``--app`` can't both populate the app slot. Fail
    loudly at startup instead of silently using one and ignoring the
    other.
    """
    import sys

    from openbb_platform_api.app.args import parse_args

    spec_file = tmp_path / "cli.spec"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "openbb-api",
            "--spec",
            str(spec_file),
            "--app",
            "/some/app.py",
        ],
    )
    with pytest.raises(ValueError, match="mutually exclusive"):
        parse_args()


# ---------------------------------------------------------------------------
# wire_name translation — Socrata $limit/$offset case
# ---------------------------------------------------------------------------


def test_rewrite_query_string_translates_friendly_to_wire_names():
    """``wire_name`` rewrites the friendly param name to whatever the
    upstream expects. Without this, Socrata responds ``Unrecognized
    arguments [limit]`` because the user sees ``limit`` in the widget
    UI but the actual SoQL parameter is ``$limit``.
    """
    from openbb_platform_api.app.spec import _rewrite_query_string

    out = _rewrite_query_string(
        "limit=1000&offset=50&region=Asia",
        {"limit": "$limit", "offset": "$offset"},
    )
    # Order preserved; values untouched; mapped keys swapped; unmapped
    # keys (``region``) flow through verbatim.
    assert out == "%24limit=1000&%24offset=50&region=Asia"


def test_rewrite_query_string_passthrough_when_no_map():
    """``None`` / empty map → no rewrite; query string returned
    unchanged. Keeps the common no-translation path cheap.
    """
    from openbb_platform_api.app.spec import _rewrite_query_string

    qs = "symbol=AAPL&interval=1d"
    assert _rewrite_query_string(qs, None) == qs
    assert _rewrite_query_string(qs, {}) == qs


def test_rewrite_query_string_empty_input():
    """Empty input is a no-op even with a non-empty map — avoid
    constructing ``urlencode`` output for nothing.
    """
    from openbb_platform_api.app.spec import _rewrite_query_string

    assert _rewrite_query_string("", {"limit": "$limit"}) == ""


def test_rewrite_query_string_preserves_blank_values():
    """``?foo=`` round-trips correctly — ``parse_qsl`` is invoked with
    ``keep_blank_values=True`` so deliberately-blank filter args
    aren't silently dropped.
    """
    from openbb_platform_api.app.spec import _rewrite_query_string

    out = _rewrite_query_string("limit=&offset=10", {"limit": "$limit"})
    # Blank ``limit`` value preserved (urlencode emits ``key=``).
    assert out == "%24limit=&offset=10"


def test_build_app_captures_wire_name_map_from_spec_parameters():
    """A spec command that declares ``wire_name`` on its params builds
    a route whose handler closes over the friendly→wire map.
    Verified end-to-end via the proxy: the upstream sees ``$limit``
    even though the client sent ``limit``.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    socrata_spec = {
        "version": 5,
        "base_url": "https://data.example.com",
        "api_prefix": "",
        "commands": {
            "fertilizer.prices": {
                "url_path": "/resource/abcd-1234.json",
                "method": "get",
                "description": "Fertilizer prices.",
                "providers": [],
                "parameters": [
                    {
                        "name": "region",
                        "in": "query",
                        "type": "string",
                        "is_list": False,
                        "required": False,
                        "default": None,
                        "choices": [],
                        "providers": [],
                    },
                    {
                        "name": "limit",
                        "in": "query",
                        "type": "integer",
                        "is_list": False,
                        "required": False,
                        "default": 1000,
                        "choices": [],
                        "providers": [],
                        "wire_name": "$limit",
                    },
                    {
                        "name": "offset",
                        "in": "query",
                        "type": "integer",
                        "is_list": False,
                        "required": False,
                        "default": None,
                        "choices": [],
                        "providers": [],
                        "wire_name": "$offset",
                    },
                ],
                "request_body_schema": None,
                "response_schema": None,
            }
        },
        "routers": {},
        "reference": {},
    }

    fake_resp = MagicMock()
    fake_resp.read = AsyncMock(return_value=b"[]")
    fake_resp.headers = {"Content-Type": "application/json"}
    fake_resp.status = 200
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=fake_resp)
    ctx.__aexit__ = AsyncMock(return_value=None)
    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(socrata_spec)
    client = TestClient(app)
    with patch("aiohttp.ClientSession", return_value=fake_session):
        client.get("/resource/abcd-1234.json?limit=1000&offset=50&region=Asia")

    # The upstream URL forwarded to aiohttp uses the WIRE names — the
    # whole point of the rewrite. Without this, Socrata returns
    # ``Unrecognized arguments [limit]``.
    target_url = fake_session.request.call_args.args[1]
    assert "%24limit=1000" in target_url
    assert "%24offset=50" in target_url
    assert "region=Asia" in target_url
    # And the friendly names DON'T leak into the upstream call.
    assert "&limit=" not in target_url
    assert "?limit=" not in target_url


def test_build_app_skips_non_dict_parameter_entries():
    """A parameter entry that isn't a dict (corrupt / partial spec)
    is silently skipped during the wire_name map build — keeps the
    launcher tolerant of malformed specs without crashing on import.
    """
    from openbb_platform_api.app.spec import build_app_from_spec

    spec = {
        **SAMPLE_SPEC,
        "commands": {
            "x": {
                "url_path": "/x",
                "method": "get",
                # Mix of valid dict + a bare string (malformed) — the
                # string is skipped, the dict is processed.
                "parameters": [
                    "not-a-dict",
                    {
                        "name": "limit",
                        "in": "query",
                        "type": "integer",
                        "is_list": False,
                        "required": False,
                        "default": 1000,
                        "choices": [],
                        "wire_name": "$limit",
                    },
                ],
            }
        },
    }
    # Builds without crashing.
    app = build_app_from_spec(spec)
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    assert "/x" in paths


def test_build_app_no_wire_name_means_passthrough():
    """When a spec command's params have no ``wire_name`` field, the
    proxy forwards friendly names verbatim — preserves the existing
    spec-mode behavior for non-Socrata backends.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    fake_resp = MagicMock()
    fake_resp.read = AsyncMock(return_value=b"{}")
    fake_resp.headers = {"Content-Type": "application/json"}
    fake_resp.status = 200
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=fake_resp)
    ctx.__aexit__ = AsyncMock(return_value=None)
    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(SAMPLE_SPEC)
    client = TestClient(app)
    with patch("aiohttp.ClientSession", return_value=fake_session):
        client.get("/api/v1/equity/price/historical?symbol=AAPL&interval=1d")

    target_url = fake_session.request.call_args.args[1]
    # Friendly names go through unchanged.
    assert "symbol=AAPL" in target_url
    assert "interval=1d" in target_url


# ---------------------------------------------------------------------------
# _trim_uniform_zero_time_columns — runtime data-driven date normalization
# ---------------------------------------------------------------------------


def test_trim_uniform_zero_time_strips_when_every_row_is_midnight():
    """When EVERY row's value for a column ends with ``T00:00:00*``,
    the time portion carries no information. Strip it across the whole
    column. Other columns (numbers, text) are untouched.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00.000", "year": 2023, "region": "California"},
        {"date": "2023-02-01T00:00:00.000", "year": 2023, "region": "California"},
        {"date": "2023-03-01T00:00:00.000", "year": 2023, "region": "California"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert out == [
        {"date": "2023-01-01", "year": 2023, "region": "California"},
        {"date": "2023-02-01", "year": 2023, "region": "California"},
        {"date": "2023-03-01", "year": 2023, "region": "California"},
    ]


def test_trim_uniform_zero_time_leaves_column_alone_when_any_row_has_real_time():
    """A single non-midnight row in a column means the time portion
    IS meaningful — every row's time stays, including the midnight
    ones. Midnight is a legitimate time when the upstream actually
    records it.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"ts": "2023-01-01T00:00:00.000"},
        {"ts": "2023-01-02T13:45:00.000"},  # real time-of-day
        {"ts": "2023-01-03T00:00:00.000"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    # Returned object is the SAME identity — function detected no-op
    # so the caller skips the JSON re-encode.
    assert out is payload


def test_trim_uniform_zero_time_per_column_independence():
    """The unanimity check is per-column. ``date`` may be uniformly
    midnight (trim) while ``ts`` has real time-of-day (don't trim) in
    the same response.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00.000", "ts": "2023-01-01T13:45:00.000"},
        {"date": "2023-01-02T00:00:00.000", "ts": "2023-01-02T09:00:00.000"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert out[0]["date"] == "2023-01-01"  # trimmed
    assert out[1]["date"] == "2023-01-02"
    assert out[0]["ts"] == "2023-01-01T13:45:00.000"  # left alone
    assert out[1]["ts"] == "2023-01-02T09:00:00.000"


def test_trim_uniform_zero_time_handles_obbject_envelope():
    """Top-level dict with a ``results`` list (OBBject envelope) gets
    the trim applied to the inner list. Other top-level keys flow
    through unchanged.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = {
        "results": [
            {"date": "2023-01-01T00:00:00.000", "value": 100},
            {"date": "2023-01-02T00:00:00.000", "value": 110},
        ],
        "provider": "fred",
        "warnings": None,
    }
    out = _trim_uniform_zero_time_columns(payload)
    assert out["results"] == [
        {"date": "2023-01-01", "value": 100},
        {"date": "2023-01-02", "value": 110},
    ]
    assert out["provider"] == "fred"
    assert out["warnings"] is None


def test_trim_uniform_zero_time_handles_alt_envelope_keys():
    """``data`` / ``rows`` / ``records`` are all recognized envelope
    keys — covers payload shapes from non-OBBject backends.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    for key in ("data", "rows", "records"):
        payload = {key: [{"date": "2023-01-01T00:00:00.000"}]}
        out = _trim_uniform_zero_time_columns(payload)
        assert out[key][0]["date"] == "2023-01-01"


def test_trim_uniform_zero_time_passes_through_unrecognized_dict():
    """A plain dict (single record) without an envelope key passes
    through unchanged — with only one row there's no cross-row signal,
    and midnight on a lone record could be meaningful.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = {"date": "2023-01-01T00:00:00.000", "value": 100}
    out = _trim_uniform_zero_time_columns(payload)
    assert out is payload  # no-op, identity preserved


def test_trim_uniform_zero_time_passes_through_scalars_and_empty():
    """Non-list / non-dict inputs and empty lists are no-ops."""
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    assert _trim_uniform_zero_time_columns("not a payload") == "not a payload"
    assert _trim_uniform_zero_time_columns(None) is None
    assert _trim_uniform_zero_time_columns([]) == []
    # List of non-dicts: nothing to scan.
    assert _trim_uniform_zero_time_columns([1, 2, 3]) == [1, 2, 3]


def test_trim_uniform_zero_time_ignores_columns_with_no_string_values():
    """A column where all values are numeric / None has nothing to
    trim and shouldn't be flagged. Mixed columns where strings ARE
    present and uniformly zero-time get trimmed.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00.000", "value": 100, "extra": None},
        {"date": "2023-01-02T00:00:00.000", "value": 110, "extra": None},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert out[0]["date"] == "2023-01-01"
    assert out[0]["value"] == 100
    # ``extra`` was all-None — nothing to trim, but also nothing to
    # disqualify. It just stays None.
    assert out[0]["extra"] is None


def test_trim_uniform_zero_time_handles_optional_nulls_in_date_column():
    """A null in a date column doesn't disqualify the column — the
    unanimity check looks at present values only. Nulls flow through
    unchanged.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00.000"},
        {"date": None},
        {"date": "2023-01-03T00:00:00.000"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert out[0]["date"] == "2023-01-01"
    assert out[1]["date"] is None
    assert out[2]["date"] == "2023-01-03"


def test_trim_uniform_zero_time_recognizes_zero_offset_variants():
    """Various ``T00:00:00`` shapes — bare, with milliseconds, with
    Z, with explicit offset — all match the zero-time pattern.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00"},
        {"date": "2023-01-02T00:00:00.000"},
        {"date": "2023-01-03T00:00:00Z"},
        {"date": "2023-01-04T00:00:00.000Z"},
        {"date": "2023-01-05T00:00:00+00:00"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert [r["date"] for r in out] == [
        "2023-01-01",
        "2023-01-02",
        "2023-01-03",
        "2023-01-04",
        "2023-01-05",
    ]


def test_trim_uniform_zero_time_preserves_non_dict_records_in_list():
    """A list mixing dict records with scalars (rare but possible in
    heterogeneous responses) keeps the scalars intact while trimming
    the dict records' uniform-zero-time columns.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00.000", "value": 100},
        "scalar-not-a-dict",  # passes through untouched
        {"date": "2023-01-02T00:00:00.000", "value": 110},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    assert out[0] == {"date": "2023-01-01", "value": 100}
    assert out[1] == "scalar-not-a-dict"
    assert out[2] == {"date": "2023-01-02", "value": 110}


def test_trim_uniform_zero_time_does_not_strip_real_milliseconds():
    """``T00:00:00.001`` has a real (non-zero) sub-second component —
    that's a real time, the column has data variance, leave alone.
    """
    from openbb_platform_api.app.spec import _trim_uniform_zero_time_columns

    payload = [
        {"date": "2023-01-01T00:00:00.001"},
        {"date": "2023-01-02T00:00:00.000"},
    ]
    out = _trim_uniform_zero_time_columns(payload)
    # Mixed shapes (one zero, one non-zero ms) → not unanimous → no trim.
    assert out is payload


def test_proxy_response_trim_through_real_app(tmp_path):
    """End-to-end integration: spec proxy synthesizes routes, fetches
    a fake upstream JSON, and the trimmed response reaches the client.
    Mirrors the original screenshot scenario — Socrata-shaped payload
    with T00:00:00.000 across every row gets normalized to YYYY-MM-DD.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    fake_resp = MagicMock()
    fake_resp.read = AsyncMock(
        return_value=json.dumps(
            [
                {"date": "2023-01-01T00:00:00.000", "value": 835},
                {"date": "2023-02-01T00:00:00.000", "value": 835},
                {"date": "2023-03-01T00:00:00.000", "value": 813},
            ]
        ).encode()
    )
    fake_resp.headers = {"Content-Type": "application/json"}
    fake_resp.status = 200
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=fake_resp)
    ctx.__aexit__ = AsyncMock(return_value=None)
    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(SAMPLE_SPEC)
    client = TestClient(app)
    with patch("aiohttp.ClientSession", return_value=fake_session):
        response = client.get("/api/v1/equity/price/historical?symbol=AAPL")

    assert response.status_code == 200
    body = response.json()
    assert [r["date"] for r in body] == [
        "2023-01-01",
        "2023-02-01",
        "2023-03-01",
    ]


def test_proxy_response_no_trim_for_non_json(tmp_path):
    """Non-JSON responses (CSV, binary, etc.) bypass the trim entirely
    — the proxy doesn't attempt to parse and never mutates them.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    csv_bytes = (
        b"date,value\n2023-01-01T00:00:00.000,835\n2023-02-01T00:00:00.000,835\n"
    )
    fake_resp = MagicMock()
    fake_resp.read = AsyncMock(return_value=csv_bytes)
    fake_resp.headers = {"Content-Type": "text/csv"}
    fake_resp.status = 200
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=fake_resp)
    ctx.__aexit__ = AsyncMock(return_value=None)
    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(SAMPLE_SPEC)
    client = TestClient(app)
    with patch("aiohttp.ClientSession", return_value=fake_session):
        response = client.get("/api/v1/equity/price/historical?symbol=AAPL")

    # CSV bytes flow through verbatim — including the T00:00:00.000
    # values that the JSON path would have trimmed.
    assert response.status_code == 200
    assert b"2023-01-01T00:00:00.000" in response.content


def test_proxy_response_trim_skipped_on_invalid_json():
    """Malformed JSON in an ``application/json`` response must not
    crash the proxy — the trim is best-effort and falls back to
    pass-through on parse failure.
    """
    from fastapi.testclient import TestClient

    from openbb_platform_api.app.spec import build_app_from_spec

    # Truncated / broken JSON.
    bad_bytes = b'{"results": [{"date": "2023-01-01T00:00'
    fake_resp = MagicMock()
    fake_resp.read = AsyncMock(return_value=bad_bytes)
    fake_resp.headers = {"Content-Type": "application/json"}
    fake_resp.status = 200
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=fake_resp)
    ctx.__aexit__ = AsyncMock(return_value=None)
    fake_session = MagicMock()
    fake_session.request = MagicMock(return_value=ctx)
    fake_session.__aenter__ = AsyncMock(return_value=fake_session)
    fake_session.__aexit__ = AsyncMock(return_value=None)

    app = build_app_from_spec(SAMPLE_SPEC)
    client = TestClient(app)
    with patch("aiohttp.ClientSession", return_value=fake_session):
        response = client.get("/api/v1/equity/price/historical?symbol=AAPL")

    # Bad bytes pass through verbatim; status code preserved.
    assert response.status_code == 200
    assert response.content == bad_bytes
