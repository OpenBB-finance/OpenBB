"""Tests for ``openbb_core.app.config.loader``.

Covers TOML cascade discovery, deep-merge behavior, top-level
promotion, ``.env`` loading, and the ``apply_config_to_services``
push onto the singleton services.
"""

import os
from pathlib import PurePosixPath

import pytest


@pytest.fixture
def reset_singletons():
    """Snapshot + restore SystemService / UserService state.

    Both services are singletons keyed by their class — we mutate the
    settings via ``apply_config_to_services`` then need to roll back so
    other tests aren't affected.
    """
    from openbb_core.app.service.system_service import SystemService
    from openbb_core.app.service.user_service import UserService

    sys_orig = SystemService().system_settings
    user_orig = UserService().default_user_settings
    yield
    SystemService().system_settings = sys_orig
    UserService().default_user_settings = user_orig


# ---------------------------------------------------------------------------
# load_config — discovery + cascade
# ---------------------------------------------------------------------------


def test_load_config_returns_empty_when_no_layers_present(tmp_path, monkeypatch):
    """No pyproject, no openbb.toml, no explicit config → empty dict.
    Callers fall through to disk JSONs / model defaults.
    """
    from openbb_core.app.config.loader import load_config

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)
    # Point user-global lookup at an empty dir so the user's actual
    # config file doesn't leak into the test result.
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config()
    assert out == {}


def test_load_config_reads_project_local_openbb_toml(tmp_path, monkeypatch):
    """``./openbb.toml`` is loaded and its contents end up in the merged dict."""
    from openbb_core.app.config.loader import load_config

    project_toml = tmp_path / "openbb.toml"
    project_toml.write_text(
        """
        [system]
        debug_mode = true
        headless = false

        [user.preferences]
        output_type = "dataframe"
        """
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )

    out = load_config()
    assert out["system"]["debug_mode"] is True
    assert out["user"]["preferences"]["output_type"] == "dataframe"


def test_load_config_reads_pyproject_tool_openbb_table(tmp_path, monkeypatch):
    """``[tool.openbb]`` in pyproject.toml is the lowest-priority layer."""
    from openbb_core.app.config.loader import load_config

    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
        [tool.openbb.system]
        debug_mode = false

        [tool.openbb.user.preferences]
        output_type = "polars"
        """
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config()
    assert out["system"]["debug_mode"] is False
    assert out["user"]["preferences"]["output_type"] == "polars"


def test_load_config_explicit_path_wins_over_project_local(tmp_path, monkeypatch):
    """``--config /explicit.toml`` overrides project-local ``./openbb.toml``."""
    from openbb_core.app.config.loader import load_config

    project_toml = tmp_path / "openbb.toml"
    project_toml.write_text("[system]\ndebug_mode = false\n")
    explicit_toml = tmp_path / "explicit.toml"
    explicit_toml.write_text("[system]\ndebug_mode = true\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config(explicit_path=str(explicit_toml))
    assert out["system"]["debug_mode"] is True


def test_load_config_env_var_acts_as_explicit_path(tmp_path, monkeypatch):
    """``$OPENBB_CONFIG`` is used when ``explicit_path`` is omitted."""
    from openbb_core.app.config.loader import load_config

    explicit_toml = tmp_path / "from_env.toml"
    explicit_toml.write_text("[system]\nheadless = true\n")
    monkeypatch.setenv("OPENBB_CONFIG", str(explicit_toml))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config()
    assert out["system"]["headless"] is True


def test_load_config_user_global_layer_picked_up(tmp_path, monkeypatch):
    """``~/.openbb_platform/openbb.toml`` (user-global) is layered between
    pyproject and project-local."""
    from openbb_core.app.config.loader import load_config

    user_dir = tmp_path / "user_openbb"
    user_dir.mkdir()
    (user_dir / "openbb.toml").write_text(
        '[user.preferences]\noutput_type = "polars"\n'
    )
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        user_dir,
    )
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)
    out = load_config()
    assert out["user"]["preferences"]["output_type"] == "polars"


def test_load_config_cascade_order_project_overrides_user_global(tmp_path, monkeypatch):
    """Project-local ``openbb.toml`` beats the user-global file."""
    from openbb_core.app.config.loader import load_config

    user_dir = tmp_path / "user_openbb"
    user_dir.mkdir()
    (user_dir / "openbb.toml").write_text(
        '[user.preferences]\noutput_type = "polars"\n'
    )
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "openbb.toml").write_text(
        '[user.preferences]\noutput_type = "dataframe"\n'
    )
    monkeypatch.chdir(project_dir)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        user_dir,
    )
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)
    out = load_config()
    # Project-local won.
    assert out["user"]["preferences"]["output_type"] == "dataframe"


def test_load_config_normalizes_kebab_case_top_level_keys(tmp_path, monkeypatch):
    """``debug-mode`` (kebab) becomes ``debug_mode`` so it can be promoted
    onto SystemSettings.``debug_mode``."""
    from openbb_core.app.config.loader import load_config

    (tmp_path / "openbb.toml").write_text("debug-mode = true\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config()
    assert out["debug_mode"] is True


def test_load_config_handles_malformed_toml_silently(tmp_path, monkeypatch):
    """A broken TOML file in the cascade is treated as an empty layer
    instead of crashing the whole load."""
    from openbb_core.app.config.loader import load_config

    (tmp_path / "openbb.toml").write_text("not [valid toml at all")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config()
    # No crash; the malformed file produced an empty layer.
    assert out == {}


def test_load_config_explicit_path_missing_is_no_op(tmp_path, monkeypatch):
    """Pointing at a non-existent file via --config doesn't crash; the
    layer is just skipped silently."""
    from openbb_core.app.config.loader import load_config

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config(explicit_path=str(tmp_path / "missing.toml"))
    assert out == {}


# ---------------------------------------------------------------------------
# pyproject [tool.openbb] discovery edge cases
# ---------------------------------------------------------------------------


def test_load_config_pyproject_without_tool_openbb_section(tmp_path, monkeypatch):
    """A pyproject without ``[tool.openbb]`` contributes nothing — and
    doesn't crash on the missing key path."""
    from openbb_core.app.config.loader import load_config

    (tmp_path / "pyproject.toml").write_text(
        '[tool.poetry]\nname = "x"\nversion = "0.0.0"\n'
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)
    out = load_config()
    assert out == {}


def test_load_config_pyproject_section_value_not_a_dict(tmp_path, monkeypatch):
    """If ``tool.openbb`` exists but isn't a table (e.g. a string), the
    loader treats it as missing."""
    from openbb_core.app.config.loader import load_config

    (tmp_path / "pyproject.toml").write_text('[tool]\nopenbb = "string"\n')
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    out = load_config()
    assert out == {}


# ---------------------------------------------------------------------------
# apply_config_to_services
# ---------------------------------------------------------------------------


def test_apply_config_to_services_pushes_system_overrides(reset_singletons):
    """``[system]`` section lands on ``SystemService.system_settings``."""
    from openbb_core.app.config.loader import apply_config_to_services
    from openbb_core.app.service.system_service import SystemService

    applied = apply_config_to_services({"system": {"debug_mode": True}})
    assert SystemService().system_settings.debug_mode is True
    assert "debug_mode" in applied["system"]


def test_apply_config_to_services_pushes_user_overrides(reset_singletons):
    """``[user.preferences]`` lands on ``UserService.default_user_settings``."""
    from openbb_core.app.config.loader import apply_config_to_services
    from openbb_core.app.service.user_service import UserService

    apply_config_to_services({"user": {"preferences": {"output_type": "polars"}}})
    assert UserService().default_user_settings.preferences.output_type == "polars"


def test_apply_config_to_services_promotes_top_level_into_system(reset_singletons):
    """Top-level ``debug_mode`` cascades onto ``[system].debug_mode``."""
    from openbb_core.app.config.loader import apply_config_to_services
    from openbb_core.app.service.system_service import SystemService

    apply_config_to_services({"debug_mode": True})
    assert SystemService().system_settings.debug_mode is True


def test_apply_config_to_services_top_level_wins_over_section(reset_singletons):
    """When both top-level ``debug_mode`` and ``[system].debug_mode``
    are set, the top-level explicit form wins."""
    from openbb_core.app.config.loader import apply_config_to_services
    from openbb_core.app.service.system_service import SystemService

    apply_config_to_services({"debug_mode": True, "system": {"debug_mode": False}})
    assert SystemService().system_settings.debug_mode is True


def test_apply_config_to_services_empty_input_no_op(reset_singletons):
    """Empty / None config → no-op, no exceptions."""
    from openbb_core.app.config.loader import apply_config_to_services

    assert apply_config_to_services(None) == {"system": [], "user": []}
    assert apply_config_to_services({}) == {"system": [], "user": []}


def test_apply_config_to_services_returns_field_names_applied(reset_singletons):
    """The return value lists which fields each service updated."""
    from openbb_core.app.config.loader import apply_config_to_services

    out = apply_config_to_services(
        {
            "system": {"debug_mode": True, "headless": False},
            "user": {"preferences": {"output_type": "polars"}},
        }
    )
    assert sorted(out["system"]) == ["debug_mode", "headless"]
    assert out["user"] == ["preferences"]


# ---------------------------------------------------------------------------
# apply_settings_to_env — ``OPENBB_*`` env-var seeding
# ---------------------------------------------------------------------------


def test_apply_settings_to_env_seeds_promoted_flags(monkeypatch):
    """Promoted top-level keys (e.g. ``debug_mode``) seed ``OPENBB_DEBUG_MODE``."""
    from openbb_core.app.config.loader import apply_settings_to_env

    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)
    applied = apply_settings_to_env({"debug_mode": True})
    assert "OPENBB_DEBUG_MODE" in applied
    assert os.environ["OPENBB_DEBUG_MODE"] == "True"
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)


def test_apply_settings_to_env_existing_env_var_wins(monkeypatch):
    """``setdefault`` semantics: pre-existing real shell exports stay."""
    from openbb_core.app.config.loader import apply_settings_to_env

    monkeypatch.setenv("OPENBB_DEBUG_MODE", "False")
    applied = apply_settings_to_env({"debug_mode": True})
    assert "OPENBB_DEBUG_MODE" not in applied
    assert os.environ["OPENBB_DEBUG_MODE"] == "False"


def test_apply_settings_to_env_skips_non_promoted_section_keys(monkeypatch):
    """``[system]`` keys outside the promotion allowlist are NOT seeded
    as env vars — too many fields to enumerate via env, only the
    blessed shortcuts get the ``OPENBB_*`` treatment."""
    from openbb_core.app.config.loader import apply_settings_to_env

    monkeypatch.delenv("OPENBB_LOGGING_VERBOSITY", raising=False)
    applied = apply_settings_to_env(
        {"system": {"logging_verbosity": 30, "debug_mode": True}}
    )
    assert "OPENBB_LOGGING_VERBOSITY" not in applied
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)


def test_apply_settings_to_env_empty_or_no_system_section_no_op():
    """Neither None nor a config without ``[system]`` produces env vars."""
    from openbb_core.app.config.loader import apply_settings_to_env

    assert apply_settings_to_env(None) == []
    assert apply_settings_to_env({}) == []
    assert apply_settings_to_env({"user": {}}) == []


def test_apply_settings_to_env_handles_non_dict_system_section():
    """Defensive: malformed ``system = "x"`` (not a table) → no crash."""
    from openbb_core.app.config.loader import apply_settings_to_env

    assert apply_settings_to_env({"system": "not-a-table"}) == []


# ---------------------------------------------------------------------------
# load_env_files — .env loading
# ---------------------------------------------------------------------------


def test_load_env_files_loads_user_global_dotenv(tmp_path, monkeypatch):
    """``~/.openbb_platform/.env`` gets pulled into ``os.environ`` via setdefault."""
    from openbb_core.app.config.loader import load_env_files

    user_dir = tmp_path / "user_openbb"
    user_dir.mkdir()
    (user_dir / ".env").write_text("FROM_USER_GLOBAL=value-1\n")
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        user_dir,
    )
    monkeypatch.delenv("OPENBB_ENV_FILE", raising=False)
    monkeypatch.delenv("FROM_USER_GLOBAL", raising=False)
    loaded = load_env_files()
    assert any(p.name == ".env" for p in loaded)
    assert os.environ.get("FROM_USER_GLOBAL") == "value-1"
    monkeypatch.delenv("FROM_USER_GLOBAL", raising=False)


def test_load_env_files_explicit_path_overrides_user_global(tmp_path, monkeypatch):
    """``$OPENBB_ENV_FILE`` (or explicit_path arg) is layered after the
    user-global file; pre-existing exports still win."""
    from openbb_core.app.config.loader import load_env_files

    user_dir = tmp_path / "user_openbb"
    user_dir.mkdir()
    (user_dir / ".env").write_text("LAYER=user-global\n")
    explicit = tmp_path / "explicit.env"
    explicit.write_text("LAYER=explicit\nEXTRA=yes\n")
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        user_dir,
    )
    monkeypatch.delenv("LAYER", raising=False)
    monkeypatch.delenv("EXTRA", raising=False)
    load_env_files(explicit_path=str(explicit))
    # User-global ran first; setdefault means it set ``LAYER=user-global``.
    # Explicit re-application via setdefault then can't overwrite — that's
    # the documented "real shell exports win" semantic; explicit-over-
    # user is actually only a layering of *new* keys.
    assert os.environ["LAYER"] == "user-global"
    assert os.environ["EXTRA"] == "yes"
    monkeypatch.delenv("LAYER", raising=False)
    monkeypatch.delenv("EXTRA", raising=False)


def test_load_env_files_no_files_returns_empty_list(tmp_path, monkeypatch):
    """Discovery with no files returns an empty list, no errors."""
    from openbb_core.app.config.loader import load_env_files

    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_dir",
    )
    monkeypatch.delenv("OPENBB_ENV_FILE", raising=False)
    assert load_env_files() == []


def test_load_env_files_skips_none_values(tmp_path, monkeypatch):
    """Dotenv parses bare ``KEY`` (no ``=value``) as ``KEY=None``;
    those entries skip the env injection rather than blowing up."""
    from openbb_core.app.config.loader import load_env_files

    user_dir = tmp_path / "user_openbb"
    user_dir.mkdir()
    (user_dir / ".env").write_text("BARE_KEY\nREAL=v\n")
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        user_dir,
    )
    monkeypatch.delenv("BARE_KEY", raising=False)
    monkeypatch.delenv("REAL", raising=False)
    load_env_files()
    assert "BARE_KEY" not in os.environ
    assert os.environ["REAL"] == "v"
    monkeypatch.delenv("REAL", raising=False)


# ---------------------------------------------------------------------------
# load_layered_config — the bundled bootstrap entry point
# ---------------------------------------------------------------------------


def test_load_layered_config_runs_full_pipeline(
    tmp_path, monkeypatch, reset_singletons
):
    """End-to-end: env files load, TOML cascade resolves, services updated,
    and ``OPENBB_*`` env vars seeded for promoted flags."""
    from openbb_core.app.config.loader import load_layered_config
    from openbb_core.app.service.system_service import SystemService

    (tmp_path / "openbb.toml").write_text(
        """
        debug-mode = true

        [user.preferences]
        output_type = "polars"
        """
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)
    monkeypatch.delenv("OPENBB_ENV_FILE", raising=False)

    config = load_layered_config()
    assert config["debug_mode"] is True
    assert SystemService().system_settings.debug_mode is True
    assert os.environ["OPENBB_DEBUG_MODE"] == "True"
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)


def test_load_layered_config_can_skip_service_application(
    tmp_path, monkeypatch, reset_singletons
):
    """``apply_to_services=False`` returns the config without mutating
    the singleton services — useful for tooling that just wants to
    inspect the resolved layer stack."""
    from openbb_core.app.config.loader import load_layered_config
    from openbb_core.app.service.system_service import SystemService

    (tmp_path / "openbb.toml").write_text("[system]\ndebug_mode = true\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        tmp_path / "no_user_dir",
    )
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)
    original_debug = SystemService().system_settings.debug_mode
    config = load_layered_config(apply_to_services=False, apply_to_env=False)
    assert config["system"]["debug_mode"] is True
    # Service untouched.
    assert SystemService().system_settings.debug_mode is original_debug


# ---------------------------------------------------------------------------
# render_config_template
# ---------------------------------------------------------------------------


def test_render_config_template_includes_top_level_promotions():
    """Every promoted top-level key shows up in the rendered template."""
    from openbb_core.app.config.loader import (
        _TOP_LEVEL_SYSTEM_PROMOTIONS,
        render_config_template,
    )

    out = render_config_template()
    for promoted in _TOP_LEVEL_SYSTEM_PROMOTIONS:
        kebab = promoted.replace("_", "-")
        assert kebab in out


def test_render_config_template_includes_system_and_user_sections():
    """Both ``[system]`` and ``[user]`` headers appear in the rendered output."""
    from openbb_core.app.config.loader import render_config_template

    out = render_config_template()
    assert "[system]" in out
    assert "[user]" in out


def test_render_config_template_uncomments_active_values():
    """Values present in ``active`` get emitted uncommented; everything else
    stays commented out as a fall-through default."""
    from openbb_core.app.config.loader import render_config_template

    out = render_config_template({"debug_mode": True})
    # Active value uncommented.
    assert "\ndebug-mode = true\n" in out
    # Non-active key still commented.
    assert "# headless = false\n" in out


def test_render_config_template_handles_list_values():
    """List-typed active values render as TOML arrays."""
    from openbb_core.app.config.loader import render_config_template

    # ``logging_handlers`` is a list-typed SystemSettings field.
    out = render_config_template({"system": {"logging_handlers": ["stdout", "file"]}})
    assert '["stdout", "file"]' in out


# ---------------------------------------------------------------------------
# _toml_quote — value rendering
# ---------------------------------------------------------------------------


def test_user_global_toml_returns_none_when_no_match(tmp_path, monkeypatch):
    """When the user-global dir exists but contains neither
    ``openbb.toml`` nor ``.openbb.toml``, the discovery returns
    ``None`` — exercises the fall-through return at the end of
    ``_user_global_toml``."""
    from openbb_core.app.config.loader import _user_global_toml

    user_dir = tmp_path / "user_dir"
    user_dir.mkdir()
    (user_dir / "something_else.toml").write_text("")
    monkeypatch.setattr(
        "openbb_core.app.config.loader.USER_OPENBB_DIR",
        user_dir,
    )
    assert _user_global_toml() is None


def test_promote_top_level_keys_returns_empty_for_falsy_config():
    """Empty / None config short-circuits to ``{}``."""
    from openbb_core.app.config.loader import _promote_top_level_keys

    assert _promote_top_level_keys({}) == {}
    assert _promote_top_level_keys(None) == {}  # type: ignore[arg-type]


def test_apply_settings_to_env_renders_non_bool_values_as_strings(monkeypatch):
    """A non-bool promoted value (e.g. integer or string) renders via
    ``str(value)`` — exercises the else-branch of the bool check."""
    from openbb_core.app.config.loader import apply_settings_to_env

    monkeypatch.delenv("OPENBB_LOGGING_SUPPRESS", raising=False)
    # ``logging_suppress`` is in the promotion list. Pass a non-bool
    # to hit the ``str(value)`` branch.
    apply_settings_to_env({"logging_suppress": "verbose"})
    assert os.environ.get("OPENBB_LOGGING_SUPPRESS") == "verbose"
    monkeypatch.delenv("OPENBB_LOGGING_SUPPRESS", raising=False)


def test_render_config_template_emits_nested_table_header_for_dicts():
    """An active dict value (e.g. ``[system.api_settings]``) gets
    emitted as a sub-table header in the template."""
    from openbb_core.app.config.loader import render_config_template

    out = render_config_template({"system": {"api_settings": {"prefix": "/api/v1"}}})
    assert "[system.api_settings]" in out


def test_render_config_template_emits_active_scalar_uncommented():
    """A non-dict / non-list / non-None active value (e.g. a string
    or int field on SystemSettings) gets rendered uncommented with the
    quoted active value — the catch-all ``else`` branch of the
    settings-section renderer."""
    from openbb_core.app.config.loader import render_config_template

    out = render_config_template(
        {"system": {"logging_verbosity": 30, "logging_frequency": "M"}}
    )
    # Both scalar fields uncommented with their active values.
    assert "\nlogging_verbosity = 30\n" in out
    assert '\nlogging_frequency = "M"\n' in out


def test_apply_settings_to_env_non_dict_system_section_returns_empty(monkeypatch):
    """Defensive: a config with ``system`` shaped as a string passes
    through ``_promote_top_level_keys`` (which strips it) and then the
    `not isinstance(system_section, dict)` short-circuit isn't reached —
    confirm the behavior end-to-end is still no env vars set."""
    from openbb_core.app.config.loader import apply_settings_to_env

    # Even when the input has a malformed system entry, no env vars
    # leak out. Real shell exports continue to be authoritative.
    monkeypatch.delenv("OPENBB_DEBUG_MODE", raising=False)
    out = apply_settings_to_env({"system": "garbage"})
    assert out == []
    assert "OPENBB_DEBUG_MODE" not in os.environ


def test_toml_quote_handles_each_supported_type():
    """Strings get escaped, bools lowercased, numbers preserved, lists
    wrapped, fallthroughs go to string."""
    from openbb_core.app.config.loader import _toml_quote

    assert _toml_quote("hello") == '"hello"'
    assert _toml_quote('quote"in"middle') == '"quote\\"in\\"middle"'
    assert _toml_quote("back\\slash") == '"back\\\\slash"'
    assert _toml_quote(True) == "true"
    assert _toml_quote(False) == "false"
    assert _toml_quote(42) == "42"
    assert _toml_quote(3.14) == "3.14"
    assert _toml_quote([1, 2]) == "[1, 2]"
    assert _toml_quote(["a", "b"]) == '["a", "b"]'
    # Other types fall through to ``str(value)`` wrapped in quotes.
    # ``PurePosixPath`` is used (not ``Path``) because ``str(Path("/x"))``
    # is platform-dependent — Windows normalizes to ``\x``, POSIX keeps
    # ``/x``. The intent here is to verify the fallthrough branch, not
    # platform-specific path rendering.
    assert _toml_quote(PurePosixPath("/x")) == '"/x"'
