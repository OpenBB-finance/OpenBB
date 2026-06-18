"""Tests for ``openbb_mcp_server.app.args``."""

import json
import sys
from unittest.mock import patch

import pytest

from openbb_mcp_server.app.args import (
    LAUNCH_SCRIPT_DESCRIPTION,
    _expand_spec_headers,
    _is_module_colon_notation,
    parse_args,
)
from openbb_mcp_server.app.spec import _content_hash

SAMPLE_SPEC: dict = {
    "version": 5,
    "base_url": "https://upstream.example.com",
    "commands": {
        "ping": {"url_path": "/v1/ping", "method": "get", "parameters": []},
    },
}
SAMPLE_SPEC["content_sha256"] = _content_hash(SAMPLE_SPEC)


@pytest.fixture(autouse=True)
def _reset_state():
    """Reset bootstrapped config between tests."""
    from openbb_mcp_server.app.config import reset_bootstrapped_config

    reset_bootstrapped_config()
    yield
    reset_bootstrapped_config()


def test_expand_spec_headers_substitutes(monkeypatch):
    """``$VAR`` references resolve from os.environ."""
    monkeypatch.setenv("MCP_TOKEN_FOR_TEST", "tok")
    out = _expand_spec_headers({"Authorization": "Bearer $MCP_TOKEN_FOR_TEST"})
    assert out == {"Authorization": "Bearer tok"}


def test_expand_spec_headers_skips_unresolved(monkeypatch, caplog):
    """Entries with missing refs are skipped + logged."""
    monkeypatch.delenv("MCP_NOT_SET", raising=False)
    out = _expand_spec_headers({"X-Bad": "$MCP_NOT_SET", "X-Good": "literal"})
    assert out == {"X-Good": "literal"}
    assert "X-Bad" in caplog.text


def test_expand_spec_headers_falsy_returns_empty():
    """None / empty dict → empty dict."""
    assert _expand_spec_headers(None) == {}
    assert _expand_spec_headers({}) == {}


def test_expand_spec_headers_skips_non_string_keys():
    """Non-string keys (defensive) silently drop."""
    out = _expand_spec_headers({1: "value", "OK": "v"})
    assert "OK" in out
    assert 1 not in out


def test_parse_args_returns_expected_dict_shape():
    """Default invocation returns the documented dict structure."""
    with patch.object(sys, "argv", ["openbb-mcp"]):
        result = parse_args()
        assert set(result) == {"app", "transport", "mcp_overrides", "uvicorn_overrides"}
        assert result["transport"] == "streamable-http"
        assert result["app"] is None


def test_parse_args_help_short_circuits(capsys):
    """--help prints the launch description and exits 0."""
    with patch.object(sys, "argv", ["openbb-mcp", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            parse_args()
        assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "openbb-mcp" in out.lower() or "MCP" in out


def test_launch_script_description_documents_key_flags():
    """Sanity check the docstring covers the flags we care about."""
    for flag in ("--app", "--spec", "--config-file", "--transport"):
        assert flag in LAUNCH_SCRIPT_DESCRIPTION


def test_parse_args_use_colors_pair():
    """``--use-colors`` and ``--no-use-colors`` both map to ``use_colors``."""
    with patch.object(sys, "argv", ["openbb-mcp", "--use-colors"]):
        out = parse_args()
        assert out["uvicorn_overrides"]["use_colors"] is True
    with patch.object(sys, "argv", ["openbb-mcp", "--no-use-colors"]):
        out = parse_args()
        assert out["uvicorn_overrides"]["use_colors"] is False


def test_parse_args_boolean_string_promotion():
    """``--flag true`` / ``--flag false`` parse as booleans."""
    with patch.object(sys, "argv", ["openbb-mcp", "--debug", "true"]):
        out = parse_args()
        assert out["uvicorn_overrides"]["debug"] is True


def test_parse_args_json_value_decoded():
    """JSON-shaped values get json.loads'd."""
    with patch.object(sys, "argv", ["openbb-mcp", "--default_categories", '["a","b"]']):
        out = parse_args()
        assert out["mcp_overrides"]["default_categories"] == ["a", "b"]


def test_parse_args_invalid_json_falls_back_to_string():
    """Malformed JSON-shaped value drops back to raw string."""
    with patch.object(sys, "argv", ["openbb-mcp", "--something", "[bad-json]"]):
        out = parse_args()
        assert out["uvicorn_overrides"]["something"] == "[bad-json]"


def test_parse_args_bare_flag_is_true():
    """Flags with no following value parse as True."""
    with patch.object(sys, "argv", ["openbb-mcp", "--lonely"]):
        out = parse_args()
        assert out["uvicorn_overrides"]["lonely"] is True


def test_parse_args_mcp_overrides_routed():
    """MCP-specific knobs land in ``mcp_overrides``, not uvicorn_overrides."""
    with patch.object(
        sys,
        "argv",
        [
            "openbb-mcp",
            "--allowed_categories",
            "equity",
            "--default_categories",
            "crypto",
            "--tool-discovery",
            "true",
            "--system-prompt",
            "/etc/sp.txt",
            "--server-prompts",
            "/etc/spr.json",
        ],
    ):
        out = parse_args()
        assert out["mcp_overrides"]["allowed_categories"] == "equity"
        assert out["mcp_overrides"]["default_categories"] == "crypto"
        assert out["mcp_overrides"]["tool_discovery"] is True
        assert out["mcp_overrides"]["system_prompt"] == "/etc/sp.txt"
        assert out["mcp_overrides"]["server_prompts"] == "/etc/spr.json"


def test_parse_args_uvicorn_passthrough_for_unknowns():
    """Unrecognized flags land in uvicorn_overrides."""
    with patch.object(  # noqa: S104
        sys,
        "argv",
        ["openbb-mcp", "--host", "0.0.0.0"],  # noqa: S104
    ):
        out = parse_args()
        assert out["uvicorn_overrides"]["host"] == "0.0.0.0"  # noqa: S104


def test_parse_args_spec_loads_app(tmp_path):
    """``--spec PATH`` synthesizes a FastAPI app from the spec."""
    spec = tmp_path / "test.spec"
    spec.write_text(json.dumps(SAMPLE_SPEC))
    with patch.object(sys, "argv", ["openbb-mcp", "--spec", str(spec)]):
        out = parse_args()
        from fastapi import FastAPI

        assert isinstance(out["app"], FastAPI)
        assert out["app"].state.openbb_spec_source == "test.spec"


def test_parse_args_spec_relative_path_resolved(tmp_path, monkeypatch):
    """A relative spec path is resolved against CWD."""
    spec = tmp_path / "rel.spec"
    spec.write_text(json.dumps(SAMPLE_SPEC))
    monkeypatch.chdir(tmp_path)
    with patch.object(sys, "argv", ["openbb-mcp", "--spec", "rel.spec"]):
        out = parse_args()
        assert out["app"] is not None


def test_parse_args_app_imports_user_supplied(tmp_path):
    """``--app PATH`` runs through ``import_app`` and resolves to FastAPI."""
    app_file = tmp_path / "user_app.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI(title='User')\n")
    with patch.object(sys, "argv", ["openbb-mcp", "--app", str(app_file)]):
        out = parse_args()
        assert out["app"].title == "User"


def test_parse_args_spec_and_app_mutually_exclusive(tmp_path):
    """Both --spec and --app set raises ValueError."""
    spec = tmp_path / "x.spec"
    spec.write_text(json.dumps(SAMPLE_SPEC))
    app_file = tmp_path / "a.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")
    with (
        patch.object(
            sys,
            "argv",
            ["openbb-mcp", "--spec", str(spec), "--app", str(app_file)],
        ),
        pytest.raises(ValueError, match="mutually exclusive"),
    ):
        parse_args()


def test_parse_args_factory_without_name_raises(tmp_path):
    """``--factory true --name ''`` raises ValueError."""
    app_file = tmp_path / "x.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")
    with (
        patch.object(
            sys,
            "argv",
            [
                "openbb-mcp",
                "--app",
                str(app_file),
                "--factory",
                "true",
                "--name",
                "",
            ],
        ),
        pytest.raises(ValueError, match="factory function name"),
    ):
        parse_args()


def test_parse_args_factory_no_name_with_windows_drive_path():
    """Windows drive-letter path doesn't fool the factory-name check."""
    test_args = [
        "openbb-mcp",
        "--app",
        r"C:\Users\runner\AppData\Local\Temp\pytest\some_app.py",
        "--factory",
        "true",
        "--name",
        "",
    ]
    with (
        patch.object(sys, "argv", test_args),
        pytest.raises(ValueError, match="factory function name"),
    ):
        parse_args()


def test_is_module_colon_notation_detects_real_colon_notation():
    """``module:attr`` and ``./file.py:attr`` both qualify."""
    assert _is_module_colon_notation("my.module:app") is True
    assert _is_module_colon_notation("./pkg/main.py:create_app") is True


def test_is_module_colon_notation_rejects_bare_paths_and_drives():
    """Bare paths and Windows drive-letter paths do NOT qualify."""
    assert _is_module_colon_notation("/abs/path/app.py") is False
    assert _is_module_colon_notation("relative/app.py") is False
    assert _is_module_colon_notation(r"C:\path\app.py") is False
    assert _is_module_colon_notation("D:/projects/app.py") is False


def test_is_module_colon_notation_drive_letter_with_attr_suffix():
    """``C:\\path\\app.py:create_app`` has two colons; treat as module:attr."""
    assert _is_module_colon_notation(r"C:\path\app.py:create_app") is True


def test_parse_args_loads_mcp_table_from_explicit_config(tmp_path):
    """``[mcp]`` table fills CLI defaults; CLI value still wins."""
    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        '[mcp]\nhost = "0.0.0.0"\nport = 7000\n'  # noqa: S104
    )
    with patch.object(
        sys,
        "argv",
        ["openbb-mcp", "--config-file", str(cfg), "--port", "9000"],
    ):
        out = parse_args()
    assert out["uvicorn_overrides"]["host"] == "0.0.0.0"  # noqa: S104
    assert out["uvicorn_overrides"]["port"] == "9000"


def test_parse_args_loads_spec_from_mcp_spec_table(tmp_path):
    """``[mcp.spec].path`` is honored just like ``--spec``."""
    spec = tmp_path / "tabled.spec"
    spec.write_text(json.dumps(SAMPLE_SPEC))
    cfg = tmp_path / "openbb.toml"
    cfg.write_text(f'[mcp.spec]\npath = "{spec.as_posix()}"\n')
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg)]):
        out = parse_args()
        assert out["app"] is not None
        assert out["app"].state.openbb_spec_source == "tabled.spec"


def test_parse_args_loads_spec_headers_from_table(tmp_path, monkeypatch):
    """``[mcp.spec.headers]`` table flows through with $VAR expansion."""
    monkeypatch.setenv("MCP_INJECTED_TOKEN", "tok-from-env")
    spec = tmp_path / "h.spec"
    spec.write_text(json.dumps(SAMPLE_SPEC))
    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        f'''
[mcp.spec]
path = "{spec.as_posix()}"
[mcp.spec.headers]
Authorization = "Bearer $MCP_INJECTED_TOKEN"
'''
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg)]):
        out = parse_args()
    assert out["app"].state.openbb_spec_extra_headers == {
        "Authorization": "Bearer tok-from-env"
    }


def test_parse_args_passes_deploy_config_hash_pin_to_load_spec(tmp_path):
    """A mismatched ``[mcp.spec].content_sha256`` raises the pin-check error."""
    payload: dict = {
        "version": 5,
        "base_url": "https://upstream.example.com",
        "commands": {
            "ping": {"url_path": "/v1/ping", "method": "get", "parameters": []}
        },
    }
    payload["content_sha256"] = _content_hash(payload)
    spec_file = tmp_path / "pinned.spec"
    spec_file.write_text(json.dumps(payload))

    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        f"""
[mcp.spec]
path = "{spec_file.as_posix()}"
content_sha256 = "{"f" * 64}"
"""
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg_file)]):
        with pytest.raises(ValueError, match="deploy-config pin check"):
            parse_args()


def test_parse_args_deploy_config_hash_pin_matches(tmp_path):
    """A matching ``[mcp.spec].content_sha256`` lets the spec load cleanly."""
    payload: dict = {
        "version": 5,
        "base_url": "https://upstream.example.com",
        "commands": {
            "ping": {"url_path": "/v1/ping", "method": "get", "parameters": []}
        },
    }
    expected = _content_hash(payload)
    payload["content_sha256"] = expected
    spec_file = tmp_path / "good-pinned.spec"
    spec_file.write_text(json.dumps(payload))

    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        f"""
[mcp.spec]
path = "{spec_file.as_posix()}"
content_sha256 = "{expected}"
"""
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg_file)]):
        out = parse_args()
    assert out["app"] is not None


def test_collect_multi_spec_entries_filters_non_spec_subtables():
    """Sibling tables under ``[mcp.spec]`` aren't treated as nested entries."""
    from openbb_mcp_server.app.args import _collect_multi_spec_entries

    section = {
        "path": "/single.spec",
        "headers": {"Authorization": "x"},
        "equity": {"path": "/eq.spec"},
        "scalar_value": "ignored",
    }
    out = _collect_multi_spec_entries(section)
    assert out == {"equity": {"path": "/eq.spec"}}


def test_parse_args_loads_multi_spec_from_named_subtables(tmp_path):
    """``[mcp.spec.NAME]`` subtables build a parent with each spec mounted."""
    payload_a: dict = {
        "version": 5,
        "base_url": "https://a.example.com",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
    }
    payload_a["content_sha256"] = _content_hash(payload_a)
    payload_b: dict = {
        "version": 5,
        "base_url": "https://b.example.com",
        "commands": {"q": {"url_path": "/q", "method": "get", "parameters": []}},
    }
    payload_b["content_sha256"] = _content_hash(payload_b)

    spec_a = tmp_path / "a.spec"
    spec_a.write_text(json.dumps(payload_a))
    spec_b = tmp_path / "b.spec"
    spec_b.write_text(json.dumps(payload_b))

    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        f"""
[mcp.spec.equity]
path = "{spec_a.as_posix()}"

[mcp.spec.crypto]
path = "{spec_b.as_posix()}"
"""
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg_file)]):
        out = parse_args()
    state = out["app"].state
    assert "/equity" in state.openbb_specs
    assert "/crypto" in state.openbb_specs


def test_parse_args_multi_spec_relative_path_resolved_against_cwd(
    tmp_path, monkeypatch
):
    """Per-spec relative paths resolve against CWD, mirroring single-spec."""
    payload: dict = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
    }
    payload["content_sha256"] = _content_hash(payload)
    spec = tmp_path / "rel.spec"
    spec.write_text(json.dumps(payload))
    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        """
[mcp.spec.rel]
path = "rel.spec"
"""
    )
    monkeypatch.chdir(tmp_path)
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg_file)]):
        out = parse_args()
    assert "/rel" in out["app"].state.openbb_specs


def test_parse_args_multi_spec_per_spec_content_sha256_pin(tmp_path):
    """A mismatched per-spec ``content_sha256`` raises at parse_args time."""
    payload: dict = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
    }
    payload["content_sha256"] = _content_hash(payload)
    spec = tmp_path / "pinned.spec"
    spec.write_text(json.dumps(payload))
    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        f"""
[mcp.spec.equity]
path = "{spec.as_posix()}"
content_sha256 = "{"f" * 64}"
"""
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg_file)]):
        with pytest.raises(ValueError, match="deploy-config pin check"):
            parse_args()


def test_parse_args_multi_spec_with_per_spec_hooks(tmp_path, monkeypatch):
    """Per-spec auth + middleware hooks land on the sub-app's middleware stack."""
    import types

    payload: dict = {
        "version": 5,
        "base_url": "https://x",
        "commands": {"p": {"url_path": "/p", "method": "get", "parameters": []}},
    }
    payload["content_sha256"] = _content_hash(payload)
    spec = tmp_path / "hooks.spec"
    spec.write_text(json.dumps(payload))

    mod = types.ModuleType("test_multi_spec_args_hooks")

    async def auth(request, call_next):  # pragma: no cover
        return await call_next(request)

    async def mw(request, call_next):  # pragma: no cover
        return await call_next(request)

    mod.auth = auth
    mod.mw = mw
    monkeypatch.setitem(sys.modules, "test_multi_spec_args_hooks", mod)

    cfg_file = tmp_path / "openbb.toml"
    cfg_file.write_text(
        f"""
[mcp.spec.equity]
path = "{spec.as_posix()}"
[mcp.spec.equity.auth]
hooks = ["test_multi_spec_args_hooks:auth"]
[mcp.spec.equity.middleware]
hooks = ["test_multi_spec_args_hooks:mw"]
"""
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg_file)]):
        out = parse_args()

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


def test_parse_args_supports_top_level_spec_table(tmp_path):
    """``[spec]`` (top-level, no [mcp] prefix) works as a fallback."""
    spec = tmp_path / "topspec.spec"
    spec.write_text(json.dumps(SAMPLE_SPEC))
    cfg = tmp_path / "openbb.toml"
    cfg.write_text(f'[spec]\npath = "{spec.as_posix()}"\n')
    with patch.object(sys, "argv", ["openbb-mcp", "--config-file", str(cfg)]):
        out = parse_args()
        assert out["app"] is not None


def test_parse_args_app_with_colon_strips_name_from_path(tmp_path):
    """``--app PATH:attr`` strips the colon-suffix name override."""
    app_file = tmp_path / "the_app.py"
    app_file.write_text(
        "from fastapi import FastAPI\nmy_app = FastAPI(title='Colon')\n"
    )
    with patch.object(sys, "argv", ["openbb-mcp", "--app", f"{app_file}:my_app"]):
        out = parse_args()
    assert out["app"].title == "Colon"
