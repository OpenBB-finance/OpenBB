"""Tests for repository Python interpreter resolution."""

from __future__ import annotations

import sys
from pathlib import Path

from qa.scripts.resolve_python import resolve_python


def test_resolve_python_prefers_repo_virtualenv(tmp_path):
    """A repo-local virtualenv should take precedence over the system interpreter."""
    if sys.platform.startswith("win"):
        venv_python = tmp_path / ".venv" / "Scripts" / "python.exe"
    else:
        venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("", encoding="utf-8")

    assert resolve_python(tmp_path) == venv_python.resolve()


def test_resolve_python_falls_back_to_system_python(tmp_path):
    """The current system Python should be used when no repo virtualenv exists."""
    assert resolve_python(tmp_path) == Path(sys.executable).resolve()
