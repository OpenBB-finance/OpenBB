"""Tests for the development install script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from openbb_platform import dev_install


def _write_minimal_pyproject(path: Path) -> None:
    """Write a minimal Poetry pyproject file for install tests."""
    path.write_text(
        """
[tool.poetry]
name = "test-package"
version = "0.1.0"
description = "test"
authors = []

[tool.poetry.dependencies]
python = ">=3.10,<3.14"
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_ensure_python_module_bootstraps_missing_tomlkit(monkeypatch):
    """Missing modules should be installed via pip bootstrap."""
    commands = []

    def fake_find_spec(module_name: str):
        return None if module_name == "tomlkit" else object()

    def fake_run(command, check, **kwargs):
        commands.append((command, check, kwargs))

    monkeypatch.setattr(dev_install.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(dev_install.subprocess, "run", fake_run)

    dev_install._ensure_python_module(
        "tomlkit",
        "tomlkit",
        bootstrap_installer="pip",
    )

    assert len(commands) == 1
    assert commands[0][0] == [sys.executable, "-m", "pip", "install", "tomlkit"]
    assert commands[0][1] is True
    assert commands[0][2]["env"]["PYTHONIOENCODING"] == "utf-8"
    assert commands[0][2]["env"]["PYTHONUTF8"] == "1"


def test_ensure_poetry_bootstraps_missing_module(monkeypatch):
    """Poetry should be installed via pip when it is not available."""
    commands = []

    def fake_find_spec(module_name: str):
        return None if module_name == "poetry" else object()

    def fake_run(command, check, **kwargs):
        commands.append((command, check, kwargs))

    monkeypatch.setattr(dev_install.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(dev_install.shutil, "which", lambda executable: None)
    monkeypatch.setattr(dev_install.subprocess, "run", fake_run)

    poetry_command = dev_install._ensure_poetry(bootstrap_installer="pip")

    assert poetry_command == [sys.executable, "-m", "poetry"]
    assert len(commands) == 1
    assert commands[0][0] == [sys.executable, "-m", "pip", "install", "poetry"]
    assert commands[0][1] is True
    assert commands[0][2]["env"]["PYTHONIOENCODING"] == "utf-8"
    assert commands[0][2]["env"]["PYTHONUTF8"] == "1"


def test_ensure_python_module_uses_uv_when_requested(monkeypatch):
    """uv bootstrap mode should install helper modules with uv."""
    commands = []

    def fake_find_spec(module_name: str):
        return None if module_name == "tomlkit" else object()

    def fake_run(command, check, **kwargs):
        commands.append((command, check, kwargs))

    monkeypatch.setattr(dev_install.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(dev_install.shutil, "which", lambda executable: "uv")
    monkeypatch.setattr(dev_install.subprocess, "run", fake_run)

    dev_install._ensure_python_module(
        "tomlkit",
        "tomlkit",
        bootstrap_installer="uv",
    )

    assert len(commands) == 1
    assert commands[0][0] == ["uv", "pip", "install", "--python", sys.executable, "tomlkit"]
    assert commands[0][1] is True
    assert commands[0][2]["env"]["PYTHONIOENCODING"] == "utf-8"
    assert commands[0][2]["env"]["PYTHONUTF8"] == "1"


def test_ensure_python_module_auto_falls_back_to_pip_when_uv_fails(monkeypatch):
    """Auto bootstrap mode should fall back to pip when uv bootstrap fails."""
    commands = []

    def fake_find_spec(module_name: str):
        return None if module_name == "poetry" else object()

    def fake_run(command, check, **kwargs):
        commands.append((command, check, kwargs))
        if command[0] == "uv":
            raise subprocess.CalledProcessError(returncode=1, cmd=command)

    monkeypatch.setattr(dev_install.importlib.util, "find_spec", fake_find_spec)
    monkeypatch.setattr(dev_install.shutil, "which", lambda executable: "uv")
    monkeypatch.setattr(dev_install.subprocess, "run", fake_run)

    dev_install._ensure_python_module("poetry", "poetry", bootstrap_installer="auto")

    assert len(commands) == 2
    assert commands[0][0] == ["uv", "pip", "install", "--python", sys.executable, "poetry"]
    assert commands[1][0] == [sys.executable, "-m", "pip", "install", "poetry"]


def test_ensure_python_module_uv_mode_fails_when_uv_missing(monkeypatch):
    """Explicit uv mode should fail fast when uv is unavailable."""
    monkeypatch.setattr(
        dev_install.importlib.util,
        "find_spec",
        lambda module_name: None if module_name == "poetry" else object(),
    )
    monkeypatch.setattr(dev_install.shutil, "which", lambda executable: None)

    with pytest.raises(FileNotFoundError):
        dev_install._ensure_python_module(
            "poetry",
            "poetry",
            bootstrap_installer="uv",
        )


def test_resolve_bootstrap_installer_prefers_cli_over_env(monkeypatch):
    """CLI bootstrap installer should override the environment variable."""
    monkeypatch.setenv("OPENBB_BOOTSTRAP_TOOL", "pip")

    assert dev_install._resolve_bootstrap_installer("uv") == "uv"
    assert dev_install._resolve_bootstrap_installer(None) == "pip"


def test_install_platform_local_restores_files_on_failure(tmp_path, monkeypatch):
    """Editable platform installs must always restore temporary file changes."""
    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "poetry.lock"
    _write_minimal_pyproject(pyproject)
    lockfile.write_text("lock-content\n", encoding="utf-8")
    original_pyproject = pyproject.read_text(encoding="utf-8")
    original_lock = lockfile.read_text(encoding="utf-8")

    monkeypatch.setattr(dev_install, "PLATFORM_PATH", tmp_path)
    monkeypatch.setattr(dev_install, "PYPROJECT", pyproject)
    monkeypatch.setattr(dev_install, "LOCK", lockfile)
    monkeypatch.setattr(dev_install, "_ensure_python_module", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        dev_install,
        "_ensure_poetry",
        lambda **kwargs: [sys.executable, "-m", "poetry"],
    )

    def fail_run(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=args[0])

    monkeypatch.setattr(dev_install.subprocess, "run", fail_run)

    with pytest.raises(subprocess.CalledProcessError):
        dev_install.install_platform_local()

    assert pyproject.read_text(encoding="utf-8") == original_pyproject
    assert lockfile.read_text(encoding="utf-8") == original_lock


def test_install_platform_cli_reraises_install_failures(tmp_path, monkeypatch):
    """CLI editable installs should propagate subprocess failures to callers."""
    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "poetry.lock"
    pyproject.write_text(
        """
[tool.poetry]
name = "openbb-cli"
version = "0.1.0"
description = "test"
authors = []

[tool.poetry.dependencies]
python = ">=3.10,<3.14"
openbb = "^0.0.1"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    lockfile.write_text("cli-lock\n", encoding="utf-8")

    monkeypatch.setattr(dev_install, "CLI_PATH", tmp_path)
    monkeypatch.setattr(dev_install, "CLI_PYPROJECT", pyproject)
    monkeypatch.setattr(dev_install, "CLI_LOCK", lockfile)
    monkeypatch.setattr(dev_install, "_ensure_python_module", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        dev_install,
        "_ensure_poetry",
        lambda **kwargs: [sys.executable, "-m", "poetry"],
    )

    def fail_run(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=args[0])

    monkeypatch.setattr(dev_install.subprocess, "run", fail_run)

    with pytest.raises(subprocess.CalledProcessError):
        dev_install.install_platform_cli()
