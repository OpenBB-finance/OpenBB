"""Tests for ``openbb_mcp_server.app.config``."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from openbb_mcp_server.app import config as config_mod
from openbb_mcp_server.app.config import (
    EXPLICIT_CONFIG_ENVS,
    apply_launcher_env,
    bootstrap_launcher_config,
    expand_env_refs,
    extract_config_file_from_argv,
    get_bootstrapped_config,
    load_launcher_config,
    merge_launcher_kwargs,
    reset_bootstrapped_config,
    resolve_explicit_config_path,
)

pytestmark = pytest.mark.usefixtures("isolated_config")


@pytest.fixture(autouse=True)
def _reset_bootstrap_state():
    """Wipe the module-level cache between tests to avoid leakage."""
    reset_bootstrapped_config()
    yield
    reset_bootstrapped_config()


class TestExtractConfigFileFromArgv:
    """Sniffing ``--config-file`` out of argv."""

    def test_extract_config_file_two_token_form(self):
        """``--config-file PATH`` extracts PATH."""
        assert (
            extract_config_file_from_argv(["--config-file", "/etc/openbb.toml"])
            == "/etc/openbb.toml"
        )

    def test_extract_config_file_equals_form(self):
        """``--config-file=PATH`` extracts PATH."""
        assert (
            extract_config_file_from_argv(["--config-file=/etc/openbb.toml"])
            == "/etc/openbb.toml"
        )

    def test_extract_config_file_missing_returns_none(self):
        """No ``--config-file`` flag → None."""
        assert extract_config_file_from_argv(["--port", "9000"]) is None

    def test_extract_config_file_empty_value_returns_none(self):
        """``--config-file --other-flag`` returns None (next token is a flag)."""
        assert extract_config_file_from_argv(["--config-file", "--port"]) is None

    def test_extract_config_file_equals_empty_returns_none(self):
        """``--config-file=`` (empty value) returns None."""
        assert extract_config_file_from_argv(["--config-file="]) is None

    def test_extract_config_file_defaults_to_sys_argv(self):
        """When ``argv`` is omitted, ``sys.argv[1:]`` is consulted."""
        with patch("sys.argv", ["openbb-mcp", "--config-file", "/from/argv.toml"]):
            assert extract_config_file_from_argv() == "/from/argv.toml"

    def test_extract_config_file_trailing_flag_no_value(self):
        """``--config-file`` at end of argv (no value follows) returns None."""
        assert extract_config_file_from_argv(["--config-file"]) is None


class TestResolveExplicitConfigPath:
    """Choosing the explicit config path."""

    def test_resolve_explicit_cli_wins(self):
        """A non-empty CLI path is returned as-is, ignoring env vars."""
        assert (
            resolve_explicit_config_path(
                cli_path="/cli.toml",
                env={"OPENBB_MCP_CONFIG": "/env.toml"},
            )
            == "/cli.toml"
        )

    def test_resolve_explicit_falls_back_to_env_in_priority_order(self):
        """Walks ``EXPLICIT_CONFIG_ENVS`` left-to-right when no CLI path."""
        env = {EXPLICIT_CONFIG_ENVS[1]: "/second.toml"}
        assert resolve_explicit_config_path(cli_path=None, env=env) == "/second.toml"

    def test_resolve_explicit_returns_none_when_nothing_set(self):
        """No CLI, no env vars → None."""
        assert resolve_explicit_config_path(cli_path=None, env={}) is None

    def test_resolve_explicit_uses_os_environ_by_default(self, monkeypatch):
        """When ``env`` is omitted, ``os.environ`` is consulted."""
        for v in EXPLICIT_CONFIG_ENVS:
            monkeypatch.delenv(v, raising=False)
        monkeypatch.setenv("OPENBB_MCP_CONFIG", "/from/env.toml")
        assert resolve_explicit_config_path() == "/from/env.toml"


class TestLoadLauncherConfig:
    """Running the layered TOML cascade."""

    def test_load_launcher_config_runs_cascade(self, tmp_path):
        """Returns the merged dict from the layered cascade."""
        cfg = tmp_path / "openbb.toml"
        cfg.write_text(
            '[mcp]\nhost = "0.0.0.0"\nport = 8005\n\n[env]\nOPENBB_API_KEY = "abc"\n'
        )
        out = load_launcher_config(
            explicit_path=str(cfg), apply_to_services=False, apply_to_env=False
        )
        assert out["mcp"] == {"host": "0.0.0.0", "port": 8005}  # noqa: S104
        assert out["env"] == {"OPENBB_API_KEY": "abc"}

    def test_load_launcher_config_raises_on_malformed_toml(self, tmp_path):
        """Malformed explicit TOML raises ValueError instead of silent fallback."""
        cfg = tmp_path / "broken.toml"
        cfg.write_text("[mcp\nhost = bad")
        with pytest.raises(ValueError, match="Malformed TOML"):
            load_launcher_config(
                explicit_path=str(cfg), apply_to_services=False, apply_to_env=False
            )

    def test_load_launcher_config_tolerates_missing_explicit_path(self, tmp_path):
        """Missing explicit file is silently skipped (cascade behavior)."""
        missing = tmp_path / "does_not_exist.toml"
        out = load_launcher_config(
            explicit_path=str(missing), apply_to_services=False, apply_to_env=False
        )
        assert out == {}

    def test_load_launcher_config_apply_to_env_path(self, monkeypatch, tmp_path):
        """``apply_to_env=True`` seeds the promoted system flags into the environment."""
        monkeypatch.setenv("OPENBB_DEBUG_MODE", "placeholder")
        monkeypatch.delenv("OPENBB_DEBUG_MODE")
        cfg = tmp_path / "openbb.toml"
        cfg.write_text("debug-mode = true\n")
        load_launcher_config(explicit_path=str(cfg), apply_to_services=False)
        assert os.environ["OPENBB_DEBUG_MODE"] == "True"

    def test_path_round_trip_through_cwd_resolution(self, tmp_path, monkeypatch):
        """``Path`` round-trip on a config-file value resolves consistently."""
        monkeypatch.chdir(tmp_path)
        cfg = Path("local.toml")
        cfg.write_text("[mcp]\nport = 6000\n")
        out = load_launcher_config(
            explicit_path=str(cfg.resolve()),
            apply_to_services=False,
            apply_to_env=False,
        )
        assert out["mcp"]["port"] == 6000

    def test_module_logger_name_matches_convention(self):
        """Module logger uses the canonical dotted name."""
        assert config_mod.logger.name == "openbb_mcp_server.config"


class TestValidateExplicitToml:
    """Validating the explicit TOML file."""

    def test_validate_explicit_toml_handles_missing_path(self, tmp_path):
        """Missing path on private validator is a no-op (cascade tolerance)."""
        config_mod._validate_explicit_toml(str(tmp_path / "nope.toml"))

    def test_validate_explicit_toml_raises_on_bad_toml(self, tmp_path):
        """Malformed TOML on the private validator surfaces ValueError."""
        bad = tmp_path / "bad.toml"
        bad.write_text("[broken\nx = 1\n")
        with pytest.raises(ValueError, match="Malformed TOML"):
            config_mod._validate_explicit_toml(str(bad))


class TestExpandEnvRefs:
    """``$VAR`` / ``${VAR}`` substitution."""

    def test_expand_env_refs_substitutes_present_vars(self):
        """``$VAR`` and ``${VAR}`` resolve from the supplied env mapping."""
        env = {"FOO": "bar", "PORT": "8000"}
        expanded, missing = expand_env_refs("${FOO}-$PORT", env)
        assert expanded == "bar-8000"
        assert missing == []

    def test_expand_env_refs_reports_missing_left_to_right_dedup(self):
        """Missing names are reported in left-to-right order, deduplicated."""
        env = {"OK": "v"}
        expanded, missing = expand_env_refs("$X-$OK-$X-$Y", env)
        assert "$X" in expanded and "$Y" in expanded
        assert missing == ["X", "Y"]

    def test_expand_env_refs_defaults_to_os_environ(self, monkeypatch):
        """Without an explicit env, ``os.environ`` is the source."""
        monkeypatch.setenv("MCP_TEST_VAR", "real")
        expanded, _ = expand_env_refs("$MCP_TEST_VAR")
        assert expanded == "real"

    def test_expand_env_refs_leaves_invalid_dollar_alone(self):
        """``$5`` / ``$@`` aren't valid identifiers — left as literals."""
        expanded, missing = expand_env_refs("$5 dollars - $@", {})
        assert expanded == "$5 dollars - $@"
        assert missing == []


class TestApplyLauncherEnv:
    """Pushing the ``[env]`` table into the environment."""

    def test_apply_launcher_env_sets_unset_keys(self):
        """New keys are pushed; existing keys are NOT clobbered."""
        target: dict = {"ALREADY_SET": "preserved"}
        applied = apply_launcher_env(
            {"NEW_KEY": "new", "ALREADY_SET": "ignored"}, env=target
        )
        assert sorted(applied) == ["NEW_KEY"]
        assert target["ALREADY_SET"] == "preserved"
        assert target["NEW_KEY"] == "new"

    def test_apply_launcher_env_substitutes_refs(self):
        """Values support ``$VAR`` / ``${VAR}`` against the current env."""
        target = {"HOST": "example.com"}
        apply_launcher_env({"URL": "https://$HOST/api"}, env=target)
        assert target["URL"] == "https://example.com/api"

    def test_apply_launcher_env_skips_unresolved_refs(self, caplog):
        """Entries with missing refs are SKIPPED with a warning."""
        target: dict = {}
        applied = apply_launcher_env({"BROKEN": "$NEVER_SET"}, env=target)
        assert applied == []
        assert "BROKEN" not in target
        assert "BROKEN" in caplog.text

    def test_apply_launcher_env_returns_empty_on_falsy_section(self):
        """Empty / None section → empty applied list, no mutations."""
        assert apply_launcher_env(None, env={}) == []
        assert apply_launcher_env({}, env={}) == []

    def test_apply_launcher_env_skips_non_string_keys(self):
        """Non-string TOML keys (defensive) are silently dropped."""
        target: dict = {}
        applied = apply_launcher_env({1: "value", "OK": "v"}, env=target)
        assert "OK" in applied
        assert 1 not in target

    def test_apply_launcher_env_defaults_to_os_environ(self, monkeypatch):
        """Without an explicit env, ``os.environ`` is the target."""
        monkeypatch.setenv("MCP_TEST_APPLY_DEFAULT", "placeholder")
        monkeypatch.delenv("MCP_TEST_APPLY_DEFAULT")
        apply_launcher_env({"MCP_TEST_APPLY_DEFAULT": "yes"})
        assert os.environ.get("MCP_TEST_APPLY_DEFAULT") == "yes"

    def test_apply_launcher_env_populates_expanded_value_in_target(self):
        """Later entries can reference earlier ones applied in the same call."""
        target: dict = {}
        applied = apply_launcher_env(
            {"BASE": "value", "DERIVED": "${BASE}-suffix"}, env=target
        )
        assert sorted(applied) == ["BASE", "DERIVED"]
        assert target["DERIVED"] == "value-suffix"


class TestMergeLauncherKwargs:
    """Overlaying ``[mcp]`` defaults under CLI kwargs."""

    def test_merge_launcher_kwargs_cli_wins(self):
        """CLI kwargs override the launcher TOML defaults."""
        cli = {"port": "9999"}
        launcher = {"host": "0.0.0.0", "port": "8000"}  # noqa: S104
        out = merge_launcher_kwargs(cli, launcher)
        assert out["port"] == "9999"
        assert out["host"] == "0.0.0.0"  # noqa: S104

    def test_merge_launcher_kwargs_returns_cli_unchanged_when_no_section(self):
        """Empty / missing ``[mcp]`` section is a no-op."""
        cli = {"port": "9999"}
        assert merge_launcher_kwargs(cli, None) == cli
        assert merge_launcher_kwargs(cli, {}) == cli


class TestBootstrapLauncherConfig:
    """The bootstrap cache used by ``main``."""

    def test_bootstrap_launcher_config_stores_result(self, tmp_path):
        """The merged config is cached and reachable via ``get_bootstrapped_config``."""
        cfg = tmp_path / "openbb.toml"
        cfg.write_text("[mcp]\nport = 7000\n")
        out = bootstrap_launcher_config(["--config-file", str(cfg)])
        assert out["mcp"]["port"] == 7000
        assert get_bootstrapped_config()["mcp"]["port"] == 7000

    def test_get_bootstrapped_config_empty_dict_when_unset(self):
        """Without bootstrap, ``get_bootstrapped_config`` returns ``{}``."""
        assert get_bootstrapped_config() == {}

    def test_bootstrap_launcher_config_applies_env_table(self, monkeypatch, tmp_path):
        """``[env]`` keys land in ``os.environ`` (no clobber)."""
        monkeypatch.setenv("OPENBB_BOOT_TEST_KEY", "placeholder")
        monkeypatch.delenv("OPENBB_BOOT_TEST_KEY")
        cfg = tmp_path / "openbb.toml"
        cfg.write_text('[env]\nOPENBB_BOOT_TEST_KEY = "yes"\n')
        bootstrap_launcher_config(["--config-file", str(cfg)])
        assert os.environ.get("OPENBB_BOOT_TEST_KEY") == "yes"

    def test_reset_bootstrapped_config_clears_state(self, tmp_path):
        """``reset_bootstrapped_config`` blanks the stored config."""
        cfg = tmp_path / "openbb.toml"
        cfg.write_text("[mcp]\nport = 7100\n")
        bootstrap_launcher_config(["--config-file", str(cfg)])
        assert get_bootstrapped_config() != {}
        reset_bootstrapped_config()
        assert get_bootstrapped_config() == {}
