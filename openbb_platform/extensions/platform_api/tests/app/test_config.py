"""Tests for ``openbb_platform_api.app.config`` — launcher TOML cascade,
``[env]`` injection, and ``[launcher]``-section override semantics.
"""

import os
import sys
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# extract_config_file_from_argv — sniffing the CLI flag without importing args
# ---------------------------------------------------------------------------


def test_extract_config_file_returns_none_when_flag_absent():
    """No ``--config-file`` in argv → ``None``."""
    from openbb_platform_api.app.config import extract_config_file_from_argv

    assert extract_config_file_from_argv(["--port", "6900"]) is None


def test_extract_config_file_picks_value_after_flag():
    """``--config-file /path`` form."""
    from openbb_platform_api.app.config import extract_config_file_from_argv

    assert (
        extract_config_file_from_argv(["--config-file", "/etc/openbb.toml"])
        == "/etc/openbb.toml"
    )


def test_extract_config_file_picks_value_with_equals_form():
    """``--config-file=/path`` form (POSIX-style)."""
    from openbb_platform_api.app.config import extract_config_file_from_argv

    assert (
        extract_config_file_from_argv(["--config-file=/etc/openbb.toml"])
        == "/etc/openbb.toml"
    )


def test_extract_config_file_returns_none_when_value_missing():
    """``--config-file`` followed by another flag (no value) → ``None``."""
    from openbb_platform_api.app.config import extract_config_file_from_argv

    assert extract_config_file_from_argv(["--config-file", "--port", "6900"]) is None


def test_extract_config_file_returns_none_when_equals_value_empty():
    """``--config-file=`` (empty value after equals) → ``None``."""
    from openbb_platform_api.app.config import extract_config_file_from_argv

    assert extract_config_file_from_argv(["--config-file="]) is None


def test_extract_config_file_defaults_to_sys_argv():
    """Omitting ``argv`` falls back to ``sys.argv[1:]``."""
    from openbb_platform_api.app.config import extract_config_file_from_argv

    with patch.object(sys, "argv", ["openbb-api", "--config-file", "/x/y.toml"]):
        assert extract_config_file_from_argv() == "/x/y.toml"


# ---------------------------------------------------------------------------
# resolve_explicit_config_path — priority order
# ---------------------------------------------------------------------------


def test_resolve_explicit_config_cli_wins_over_envs():
    """CLI value beats every env-var slot."""
    from openbb_platform_api.app.config import resolve_explicit_config_path

    fake_env = {"OPENBB_API_CONFIG": "/api.toml", "OPENBB_CONFIG": "/core.toml"}
    assert resolve_explicit_config_path("/cli.toml", env=fake_env) == "/cli.toml"


def test_resolve_explicit_config_api_env_wins_over_core_env():
    """``OPENBB_API_CONFIG`` is launcher-specific and wins over the
    generic ``OPENBB_CONFIG`` slot — explicit beats general.
    """
    from openbb_platform_api.app.config import resolve_explicit_config_path

    fake_env = {"OPENBB_API_CONFIG": "/api.toml", "OPENBB_CONFIG": "/core.toml"}
    assert resolve_explicit_config_path(env=fake_env) == "/api.toml"


def test_resolve_explicit_config_falls_back_to_core_env():
    """When ``OPENBB_API_CONFIG`` is absent, ``OPENBB_CONFIG`` is honored
    so a single env var can configure the whole stack.
    """
    from openbb_platform_api.app.config import resolve_explicit_config_path

    fake_env = {"OPENBB_CONFIG": "/core.toml"}
    assert resolve_explicit_config_path(env=fake_env) == "/core.toml"


def test_resolve_explicit_config_returns_none_when_nothing_set():
    """No CLI, no env vars → ``None`` (cascade falls back to discovery)."""
    from openbb_platform_api.app.config import resolve_explicit_config_path

    assert resolve_explicit_config_path(env={}) is None


def test_resolve_explicit_config_ignores_empty_env_values():
    """Empty string env values are equivalent to unset."""
    from openbb_platform_api.app.config import resolve_explicit_config_path

    fake_env = {"OPENBB_API_CONFIG": "", "OPENBB_CONFIG": ""}
    assert resolve_explicit_config_path(env=fake_env) is None


# ---------------------------------------------------------------------------
# apply_launcher_env — [env] table → os.environ (no clobber)
# ---------------------------------------------------------------------------


def test_apply_launcher_env_pushes_keys_to_environ():
    """New keys get pushed in; the function reports what it applied."""
    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    applied = apply_launcher_env(
        {"OPENBB_API_KEY": "abc", "OPENBB_API_HOST": "0.0.0.0"},  # noqa: S104 — container deploy fixture
        env=target,
    )
    assert sorted(applied) == ["OPENBB_API_HOST", "OPENBB_API_KEY"]
    assert target["OPENBB_API_KEY"] == "abc"
    assert target["OPENBB_API_HOST"] == "0.0.0.0"  # noqa: S104 — container deploy fixture


def test_apply_launcher_env_does_not_clobber_existing_shell_vars():
    """Real shell env vars always win — TOML never overwrites them."""
    from openbb_platform_api.app.config import apply_launcher_env

    target = {"OPENBB_API_HOST": "from-shell"}
    applied = apply_launcher_env(
        {"OPENBB_API_HOST": "from-toml", "OPENBB_API_PORT": "6901"}, env=target
    )
    assert applied == ["OPENBB_API_PORT"]
    assert target["OPENBB_API_HOST"] == "from-shell"
    assert target["OPENBB_API_PORT"] == "6901"


def test_apply_launcher_env_handles_none_section_gracefully():
    """No ``[env]`` table at all → no-op."""
    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    assert apply_launcher_env(None, env=target) == []
    assert target == {}


def test_apply_launcher_env_coerces_values_to_strings():
    """TOML can produce ints / bools / floats — env vars must be strings."""
    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    apply_launcher_env({"PORT": 6900, "DEBUG": True, "RATIO": 0.5}, env=target)
    assert target == {"PORT": "6900", "DEBUG": "True", "RATIO": "0.5"}


def test_apply_launcher_env_skips_non_string_keys():
    """A malformed TOML with non-string keys is tolerated — those entries
    are silently skipped rather than crashing the launcher.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    apply_launcher_env({"GOOD": "ok", 42: "bad"}, env=target)  # type: ignore[dict-item]
    assert target == {"GOOD": "ok"}


def test_apply_launcher_env_expands_bare_dollar_var_reference():
    """``"$GITHUB_TOKEN"`` resolves against the current env — the
    container scenario where the orchestrator injects the secret as a
    shell env var and the TOML maps it to the application's name.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    target = {"GITHUB_TOKEN": "ghp_secret_value"}  # noqa: S105 — synthetic test fixture
    apply_launcher_env({"OPENBB_GITHUB_TOKEN": "$GITHUB_TOKEN"}, env=target)
    assert (
        target["OPENBB_GITHUB_TOKEN"] == "ghp_secret_value"  # noqa: S105 — synthetic test fixture
    )


def test_apply_launcher_env_expands_braced_dollar_var_reference():
    """``${HOST}`` is the disambiguating form — needed when the
    reference is followed by an identifier character.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    target = {"HOST": "0.0.0.0"}  # noqa: S104 — container deploy fixture
    apply_launcher_env({"OPENBB_API_HOST": "${HOST}"}, env=target)
    assert target["OPENBB_API_HOST"] == "0.0.0.0"  # noqa: S104 — container deploy fixture


def test_apply_launcher_env_expands_within_string_template():
    """References embedded in larger strings work — useful for URL
    templating like ``"https://$HOST:$PORT"``.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    target = {"HOST": "api.example.com", "PORT": "8443"}
    apply_launcher_env({"OPENBB_API_URL": "https://$HOST:$PORT/v1"}, env=target)
    assert target["OPENBB_API_URL"] == "https://api.example.com:8443/v1"


def test_apply_launcher_env_skips_entry_when_reference_unresolved(caplog):
    """A reference to an unset variable means the operator's
    deployment is misconfigured. Skip the entry (don't set a literal
    ``$MISSING`` value) and log a warning so the missing var surfaces.
    """
    import logging

    from openbb_platform_api.app.config import apply_launcher_env

    target = {"HOST": "example.com"}  # no GITHUB_TOKEN here
    with caplog.at_level(logging.WARNING, logger="openbb_platform_api.config"):
        applied = apply_launcher_env(
            {
                "OPENBB_API_HOST": "$HOST",  # resolves
                "OPENBB_GITHUB_TOKEN": "$GITHUB_TOKEN",  # missing
            },
            env=target,
        )
    assert applied == ["OPENBB_API_HOST"]
    assert "OPENBB_API_HOST" in target
    assert "OPENBB_GITHUB_TOKEN" not in target
    # Warning surfaces the missing name so ops can debug fast.
    assert any(
        "OPENBB_GITHUB_TOKEN" in rec.message and "GITHUB_TOKEN" in rec.message
        for rec in caplog.records
    )


def test_apply_launcher_env_chained_references_resolve_in_order():
    """TOML preserves insertion order. An earlier ``[env]`` entry that
    lands in ``os.environ`` becomes resolvable for a later entry —
    so a single TOML can build composite values without needing a
    pre-existing shell var.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    apply_launcher_env(
        {
            "BASE_URL": "https://api.example.com",
            "FULL_URL": "$BASE_URL/v1/data",
        },
        env=target,
    )
    assert target["BASE_URL"] == "https://api.example.com"
    assert target["FULL_URL"] == "https://api.example.com/v1/data"


def test_apply_launcher_env_dollar_not_followed_by_identifier_is_literal():
    """A bare ``$`` followed by punctuation, digits-only, or
    whitespace is left as-is — not flagged as a missing reference.
    Lets values like ``"price > $5"`` pass through unchanged.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    apply_launcher_env(
        {"NOTE": "price > $5", "EMOTE": "$@!"},
        env=target,
    )
    assert target["NOTE"] == "price > $5"
    assert target["EMOTE"] == "$@!"


def test_apply_launcher_env_repeated_missing_ref_reported_once(caplog):
    """``"$X-$X"`` should log ``X`` as missing only once — keeps
    container startup logs clean when the same secret name is
    referenced multiple places.
    """
    import logging

    from openbb_platform_api.app.config import apply_launcher_env

    target: dict[str, str] = {}
    with caplog.at_level(logging.WARNING, logger="openbb_platform_api.config"):
        apply_launcher_env({"COMBO_KEY": "$MISSING-$MISSING-$MISSING"}, env=target)
    warning_records = [r for r in caplog.records if "COMBO_KEY" in r.message]
    assert len(warning_records) == 1
    # The missing name appears exactly once in that warning, not three.
    assert warning_records[0].message.count("MISSING") == 1


def test_apply_launcher_env_defaults_to_real_os_environ(monkeypatch):
    """Without an explicit ``env`` arg, the function operates on
    ``os.environ`` directly. Use monkeypatch so the test's env stays
    isolated.
    """
    from openbb_platform_api.app.config import apply_launcher_env

    monkeypatch.delenv("LAUNCHER_TEST_KEY", raising=False)
    apply_launcher_env({"LAUNCHER_TEST_KEY": "yes"})
    assert os.environ.get("LAUNCHER_TEST_KEY") == "yes"


# ---------------------------------------------------------------------------
# merge_launcher_kwargs — [launcher] under CLI (CLI wins)
# ---------------------------------------------------------------------------


def test_merge_launcher_kwargs_cli_wins_for_overlapping_keys():
    """CLI values always override the TOML defaults — the whole point
    of the layered cascade.
    """
    from openbb_platform_api.app.config import merge_launcher_kwargs

    cli = {"port": 7000}
    launcher = {"port": 6900, "host": "0.0.0.0"}  # noqa: S104 — container deploy fixture
    out = merge_launcher_kwargs(cli, launcher)
    assert out == {"port": 7000, "host": "0.0.0.0"}  # noqa: S104 — container deploy fixture


def test_merge_launcher_kwargs_fills_only_missing_keys():
    """Keys absent on CLI take the TOML default; CLI-provided keys are
    untouched even when the TOML has the same key.
    """
    from openbb_platform_api.app.config import merge_launcher_kwargs

    cli = {"agents-json": "/cli/agents.json"}
    launcher = {
        "agents-json": "/toml/agents.json",
        "host": "0.0.0.0",  # noqa: S104 — container deploy fixture
        "port": 6900,
    }
    out = merge_launcher_kwargs(cli, launcher)
    assert out["agents-json"] == "/cli/agents.json"
    assert out["host"] == "0.0.0.0"  # noqa: S104 — container deploy fixture
    assert out["port"] == 6900


def test_merge_launcher_kwargs_returns_cli_unchanged_when_no_section():
    """Empty / missing ``[launcher]`` table is a no-op."""
    from openbb_platform_api.app.config import merge_launcher_kwargs

    cli = {"port": 7000}
    assert merge_launcher_kwargs(cli, None) == cli
    assert merge_launcher_kwargs(cli, {}) == cli


def test_merge_launcher_kwargs_replaces_lists_wholesale():
    """No deep-merge for lists — the CLI's list completely replaces the
    TOML's. Keeps the exclude-filter semantics simple and predictable.
    """
    from openbb_platform_api.app.config import merge_launcher_kwargs

    cli = {"exclude": ["/api/cli/*"]}
    launcher = {"exclude": ["/api/toml/*", "/api/other/*"]}
    out = merge_launcher_kwargs(cli, launcher)
    assert out["exclude"] == ["/api/cli/*"]


# ---------------------------------------------------------------------------
# load_launcher_config — uses the core layered loader
# ---------------------------------------------------------------------------


def test_load_launcher_config_returns_merged_dict_from_explicit_path(tmp_path):
    """Explicit ``--config-file`` path produces a merged dict with
    ``[launcher]`` and ``[env]`` tables intact.
    """
    from openbb_platform_api.app.config import load_launcher_config

    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        '[launcher]\nhost = "0.0.0.0"\nport = 6900\n\n[env]\nOPENBB_API_KEY = "abc"\n'
    )
    out = load_launcher_config(
        explicit_path=str(cfg),
        apply_to_services=False,
        apply_to_env=False,
    )
    assert out["launcher"] == {
        "host": "0.0.0.0",  # noqa: S104 — container deploy fixture
        "port": 6900,
    }
    assert out["env"] == {"OPENBB_API_KEY": "abc"}


def test_load_launcher_config_no_file_returns_empty_dict(tmp_path, monkeypatch):
    """When no TOML exists in the cascade and no explicit path is set,
    ``load_launcher_config`` returns an empty / default dict — the
    launcher should still boot cleanly. Container-compat check.
    """
    from openbb_platform_api.app.config import load_launcher_config

    # CWD is empty + HOME points at empty tmp dir → no cascade hits.
    empty_home = tmp_path / "empty_home"
    empty_home.mkdir()
    empty_cwd = tmp_path / "empty_cwd"
    empty_cwd.mkdir()
    monkeypatch.setenv("HOME", str(empty_home))
    monkeypatch.chdir(empty_cwd)

    out = load_launcher_config(apply_to_services=False, apply_to_env=False)
    assert out.get("launcher") in (None, {})
    assert out.get("env") in (None, {})


# ---------------------------------------------------------------------------
# bootstrap_launcher_config — one-call entry used by main.py
# ---------------------------------------------------------------------------


def test_bootstrap_launcher_config_applies_env_section(tmp_path, monkeypatch):
    """End-to-end: a config file with ``[env]`` keys + a CLI flag
    pointing at it ends up populating ``os.environ``.
    """
    from openbb_platform_api.app.config import bootstrap_launcher_config

    cfg = tmp_path / "openbb.toml"
    cfg.write_text('[env]\nOPENBB_BOOT_TEST = "yes"\n')

    monkeypatch.delenv("OPENBB_BOOT_TEST", raising=False)
    monkeypatch.delenv("OPENBB_API_CONFIG", raising=False)
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)

    bootstrap_launcher_config(["--config-file", str(cfg)])
    assert os.environ.get("OPENBB_BOOT_TEST") == "yes"


def test_bootstrap_launcher_config_picks_up_api_config_env(tmp_path, monkeypatch):
    """Container scenario: no CLI flag, but ``OPENBB_API_CONFIG`` is
    set in the container env. Bootstrap must pick that up.
    """
    from openbb_platform_api.app.config import bootstrap_launcher_config

    cfg = tmp_path / "container.toml"
    cfg.write_text('[env]\nOPENBB_CONTAINER_TEST = "yes"\n')

    monkeypatch.setenv("OPENBB_API_CONFIG", str(cfg))
    monkeypatch.delenv("OPENBB_CONTAINER_TEST", raising=False)

    bootstrap_launcher_config([])
    assert os.environ.get("OPENBB_CONTAINER_TEST") == "yes"


def test_load_launcher_config_explicit_missing_path_is_tolerated(tmp_path):
    """A missing file at the explicit path is tolerated — the cascade
    just falls through to the next layer. Only parse failures escalate.
    Important for setups where the operator templated a path that
    doesn't always exist (e.g. multi-stage container builds).
    """
    from openbb_platform_api.app.config import load_launcher_config

    missing = tmp_path / "not_here.toml"
    out = load_launcher_config(
        explicit_path=str(missing),
        apply_to_services=False,
        apply_to_env=False,
    )
    # No crash; returns whatever the cascade has (likely empty).
    assert isinstance(out, dict)


def test_bootstrap_launcher_config_malformed_toml_raises_loudly(tmp_path):
    """A malformed TOML must surface an error — silent corruption
    is worse than a clear startup crash.
    """
    from openbb_platform_api.app.config import bootstrap_launcher_config

    cfg = tmp_path / "broken.toml"
    cfg.write_text("[launcher\nhost = bad")

    with pytest.raises(Exception):
        bootstrap_launcher_config(["--config-file", str(cfg)])


# ---------------------------------------------------------------------------
# parse_args integration — [launcher] flows through as fallback values
# ---------------------------------------------------------------------------


def test_parse_args_uses_launcher_section_for_missing_cli_flags(tmp_path, monkeypatch):
    """A ``[launcher]`` section in the TOML provides defaults for any
    CLI flag not explicitly set. CLI-supplied flags still win.
    """
    from openbb_platform_api.app.args import parse_args

    cfg = tmp_path / "openbb.toml"
    cfg.write_text(
        '[launcher]\nhost = "0.0.0.0"\nport = 7000\nagents-json = "/toml/agents.json"\n'
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "openbb-api",
            "--config-file",
            str(cfg),
            "--port",
            "9999",  # CLI override
        ],
    )

    out = parse_args()
    assert out["host"] == "0.0.0.0"  # noqa: S104 — from TOML container deploy fixture
    assert out["port"] == "9999"  # CLI wins
    # ``agents-json`` flows through the TOML (path may be normalized).
    assert "/toml/agents.json" in out.get("agents-json", "")


def test_parse_args_strips_config_file_from_returned_kwargs(tmp_path, monkeypatch):
    """``--config-file`` is consumed by the config layer; it must NOT
    leak into the kwargs that get passed to ``uvicorn.run``.
    """
    from openbb_platform_api.app.args import parse_args

    cfg = tmp_path / "openbb.toml"
    cfg.write_text('[launcher]\nhost = "0.0.0.0"\n')
    monkeypatch.setattr(sys, "argv", ["openbb-api", "--config-file", str(cfg)])

    out = parse_args()
    assert "config-file" not in out
    assert "config_file" not in out


def test_bootstrapped_config_cache_round_trips(tmp_path, monkeypatch):
    """``bootstrap_launcher_config`` stashes the merged config so
    later boot phases (``parse_args``, middleware registration) can
    read the same value without re-running cascade discovery —
    important because only the bootstrap call sniffs ``--config-file``
    from argv. Without this cache, ``app.py`` would have no way to
    find the same explicit path.
    """
    from openbb_platform_api.app.config import (
        bootstrap_launcher_config,
        get_bootstrapped_config,
        reset_bootstrapped_config,
    )

    cfg = tmp_path / "openbb.toml"
    cfg.write_text('[middleware]\nhooks = ["my_pkg:my_mw"]\n[launcher]\nport = 9999\n')
    monkeypatch.delenv("OPENBB_API_CONFIG", raising=False)
    monkeypatch.delenv("OPENBB_CONFIG", raising=False)

    reset_bootstrapped_config()
    assert get_bootstrapped_config() == {}

    bootstrap_launcher_config(["--config-file", str(cfg)])
    cached = get_bootstrapped_config()
    assert cached["middleware"]["hooks"] == ["my_pkg:my_mw"]
    assert cached["launcher"]["port"] == 9999

    reset_bootstrapped_config()
    assert get_bootstrapped_config() == {}
