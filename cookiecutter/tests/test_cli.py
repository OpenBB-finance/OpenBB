"""Tests for the openbb-cookiecutter command line."""

from pathlib import Path

import pytest

from openbb_cookiecutter import cli


class TestParseExtensionTypes:
    """Extension types are validated."""

    def test_valid(self):
        assert cli._parse_extension_types("router, provider") == ["router", "provider"]

    @pytest.mark.parametrize("value", ["", "router,bogus"])
    def test_invalid(self, value):
        with pytest.raises(ValueError):
            cli._parse_extension_types(value)


class TestMain:
    """The command generates a project."""

    def test_no_input(self, tmp_path):
        code = cli.main(["--no-input", "-o", str(tmp_path), "-e", "router", "provider"])
        project = tmp_path / "extension-template"
        assert code == 0
        assert (project / "extension_template/routers/template.py").exists()
        assert (project / "extension_template/providers/template").is_dir()
        assert not (project / "extension_template/obbject").exists()

    def test_extra_context_requires_key_value(self, tmp_path, capsys):
        code = cli.main(["--no-input", "-o", str(tmp_path), "--extra-context", "bad"])
        assert code == 1
        assert "KEY=VALUE" in capsys.readouterr().out

    def test_generation_error_returns_nonzero(self, tmp_path, capsys):
        code = cli.main(
            [
                "--no-input",
                "-o",
                str(tmp_path),
                "--extra-context",
                "package_name=1-bad",
            ]
        )
        assert code == 1
        assert "Error:" in capsys.readouterr().err
        assert not Path(tmp_path / "extension-template").exists()
