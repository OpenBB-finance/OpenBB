"""Tests for CLI module.

Tests the command-line interface for PyWry configuration management.
"""

import argparse
import contextlib
import sys
import tempfile

from io import StringIO
from pathlib import Path
from unittest.mock import patch

from pywry.cli import format_config_show, handle_config, handle_init, main, show_config_sources
from pywry.config import PyWrySettings


class TestMainEntryPoint:
    """Tests for CLI main entry point."""

    def test_no_args_prints_help_text(self):
        """Running with no args prints help text with usage info."""
        with (
            patch.object(sys, "argv", ["pywry"]),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            result = main()

        output = mock_stdout.getvalue()
        assert result == 0
        assert "usage:" in output.lower() or "pywry" in output
        assert "config" in output  # Should mention config subcommand
        assert "init" in output  # Should mention init subcommand

    def test_help_flag_shows_usage(self):
        """--help flag shows usage information."""
        with (
            patch.object(sys, "argv", ["pywry", "--help"]),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
            contextlib.suppress(SystemExit),
        ):
            main()

        output = mock_stdout.getvalue()
        assert "usage:" in output.lower()
        assert "pywry" in output

    def test_config_command_dispatches_to_handler(self):
        """config command calls handle_config."""
        with (
            patch.object(sys, "argv", ["pywry", "config", "--show"]),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            result = main()

        output = mock_stdout.getvalue()
        assert result == 0
        # handle_config with --show should output configuration
        assert "csp" in output.lower() or "[" in output

    def test_init_command_dispatches_to_handler(self):
        """init command calls handle_init."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            with (
                patch.object(sys, "argv", ["pywry", "init", "--path", str(config_path)]),
                patch("sys.stdout", new_callable=StringIO) as mock_stdout,
            ):
                result = main()

            output = mock_stdout.getvalue()
            assert result == 0
            assert config_path.exists()
            assert "created" in output.lower() or str(config_path) in output


class TestHandleConfigShow:
    """Tests for config --show command."""

    def test_show_outputs_all_sections(self):
        """--show outputs all configuration sections."""
        args = argparse.Namespace(show=True, toml=False, env=False, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        # Must contain all section headers
        assert "[csp]" in output
        assert "[theme]" in output
        assert "[timeout]" in output
        assert "[window]" in output
        assert "[hot_reload]" in output

    def test_show_outputs_csp_values(self):
        """--show outputs CSP directive values."""
        args = argparse.Namespace(show=True, toml=False, env=False, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "default_src" in output
        assert "script_src" in output
        assert "'self'" in output  # CSP value

    def test_show_outputs_window_dimensions(self):
        """--show outputs window width and height."""
        args = argparse.Namespace(show=True, toml=False, env=False, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "width" in output
        assert "height" in output
        assert "1280" in output  # Default width
        assert "720" in output  # Default height


class TestHandleConfigToml:
    """Tests for config --toml command."""

    def test_toml_outputs_valid_toml(self):
        """--toml outputs valid TOML format."""
        args = argparse.Namespace(show=False, toml=True, env=False, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        # TOML format: [section] headers and key = value
        assert "[csp]" in output
        assert "[theme]" in output
        assert "=" in output

    def test_toml_contains_csp_section(self):
        """--toml contains [csp] section with directives."""
        args = argparse.Namespace(show=False, toml=True, env=False, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "[csp]" in output
        assert "default_src" in output

    def test_toml_output_to_file(self):
        """--toml --output writes to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "config.toml"
            args = argparse.Namespace(
                show=False, toml=True, env=False, sources=False, output=str(output_path)
            )

            with patch("sys.stdout", new_callable=StringIO):
                result = handle_config(args)

            assert result == 0
            assert output_path.exists()
            content = output_path.read_text()
            assert "[csp]" in content
            assert "[theme]" in content


class TestHandleConfigEnv:
    """Tests for config --env command."""

    def test_env_outputs_environment_variables(self):
        """--env outputs environment variable format."""
        args = argparse.Namespace(show=False, toml=False, env=True, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "PYWRY_" in output
        assert "=" in output

    def test_env_outputs_csp_variables(self):
        """--env outputs CSP-related environment variables."""
        args = argparse.Namespace(show=False, toml=False, env=True, sources=False, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        # Should have CSP env vars
        assert "PYWRY_CSP__" in output or "CSP" in output.upper()


class TestHandleConfigSources:
    """Tests for config --sources command."""

    def test_sources_shows_source_list(self):
        """--sources shows configuration source list."""
        args = argparse.Namespace(show=False, toml=False, env=False, sources=True, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "source" in output.lower()
        assert "built-in" in output.lower() or "default" in output.lower()

    def test_sources_mentions_toml_files(self):
        """--sources mentions TOML configuration files."""
        args = argparse.Namespace(show=False, toml=False, env=False, sources=True, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "toml" in output.lower() or ".toml" in output

    def test_sources_mentions_env_vars(self):
        """--sources mentions environment variables."""
        args = argparse.Namespace(show=False, toml=False, env=False, sources=True, output=None)

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = handle_config(args)

        output = mock_stdout.getvalue()
        assert result == 0
        assert "environment" in output.lower() or "PYWRY_" in output


class TestHandleInit:
    """Tests for init command handling."""

    def test_init_creates_toml_file(self):
        """Init creates pywry.toml file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            args = argparse.Namespace(path=str(config_path), force=False)

            with patch("sys.stdout", new_callable=StringIO):
                result = handle_init(args)

            assert result == 0
            assert config_path.exists()

    def test_init_file_contains_toml_sections(self):
        """Init creates file with TOML section headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            args = argparse.Namespace(path=str(config_path), force=False)

            with patch("sys.stdout", new_callable=StringIO):
                handle_init(args)

            content = config_path.read_text()
            assert "[csp]" in content
            assert "[theme]" in content
            assert "[window]" in content

    def test_init_file_contains_header_comment(self):
        """Init creates file with documentation header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            args = argparse.Namespace(path=str(config_path), force=False)

            with patch("sys.stdout", new_callable=StringIO):
                handle_init(args)

            content = config_path.read_text()
            assert "# PyWry Configuration" in content
            assert "PYWRY_" in content  # Env var docs

    def test_init_refuses_overwrite_existing(self):
        """Init refuses to overwrite existing file without --force."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            original_content = "# existing config"
            config_path.write_text(original_content)
            args = argparse.Namespace(path=str(config_path), force=False)

            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = handle_init(args)

            assert result == 1
            assert (
                "already exists" in mock_stderr.getvalue().lower()
                or "error" in mock_stderr.getvalue().lower()
            )
            # File should not be modified
            assert config_path.read_text() == original_content

    def test_init_force_overwrites_existing(self):
        """Init --force overwrites existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            config_path.write_text("# old content only")
            args = argparse.Namespace(path=str(config_path), force=True)

            with patch("sys.stdout", new_callable=StringIO):
                result = handle_init(args)

            assert result == 0
            content = config_path.read_text()
            assert "[csp]" in content  # New TOML content
            assert "# old content only" not in content

    def test_init_prints_success_message(self):
        """Init prints success message with path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pywry.toml"
            args = argparse.Namespace(path=str(config_path), force=False)

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                handle_init(args)

            output = mock_stdout.getvalue()
            assert "created" in output.lower() or str(config_path) in output


class TestFormatConfigShow:
    """Tests for format_config_show function."""

    def test_formats_settings_with_header(self):
        """Formats settings with PyWry Configuration header."""
        settings = PyWrySettings()
        output = format_config_show(settings)
        assert "PyWry Configuration" in output

    def test_formats_all_sections(self):
        """Formats all configuration sections."""
        settings = PyWrySettings()
        output = format_config_show(settings)
        assert "[csp]" in output
        assert "[theme]" in output
        assert "[timeout]" in output
        assert "[asset]" in output
        assert "[log]" in output
        assert "[window]" in output
        assert "[hot_reload]" in output

    def test_formats_field_values(self):
        """Formats field names and values."""
        settings = PyWrySettings()
        output = format_config_show(settings)
        # Check some known fields exist with values
        assert "default_src" in output
        assert "width" in output
        assert "=" in output


class TestShowConfigSources:
    """Tests for show_config_sources function."""

    def test_shows_source_table(self):
        """Shows configuration source table."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = show_config_sources()

        output = mock_stdout.getvalue()
        assert result == 0
        assert "Source" in output
        assert "Status" in output

    def test_shows_builtin_defaults(self):
        """Shows built-in defaults as active."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            show_config_sources()

        output = mock_stdout.getvalue()
        assert "built-in" in output.lower() or "default" in output.lower()
        assert "✓" in output  # Active indicator

    def test_shows_pywry_toml_source(self):
        """Shows pywry.toml as a source."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            show_config_sources()

        output = mock_stdout.getvalue()
        assert "pywry.toml" in output

    def test_shows_env_vars_source(self):
        """Shows environment variables as a source."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            show_config_sources()

        output = mock_stdout.getvalue()
        assert "environment" in output.lower()

    def test_shows_precedence_note(self):
        """Shows note about source precedence."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            show_config_sources()

        output = mock_stdout.getvalue()
        assert "override" in output.lower() or "precedence" in output.lower()
