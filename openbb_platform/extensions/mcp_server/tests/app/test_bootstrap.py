"""Tests for ``openbb_mcp_server.app.bootstrap``."""

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI

from openbb_mcp_server.app.bootstrap import import_app


@pytest.fixture
def dummy_app_file(tmp_path: Path):
    """Create a dummy FastAPI app file for testing."""
    content = """
from fastapi import FastAPI

app = FastAPI(title="Bootstrap Test App")

def create_app():
    return FastAPI(title="Bootstrap Factory App")

not_an_app = "not a FastAPI"

def not_a_factory():
    return "not a factory"
"""
    f = tmp_path / "bootstrap_dummy.py"
    f.write_text(content)
    return f


def test_import_app_file_path(dummy_app_file: Path):
    """A bare file path imports cleanly."""
    app = import_app(str(dummy_app_file))
    assert isinstance(app, FastAPI)
    assert app.title == "Bootstrap Test App"


def test_import_app_module_colon(dummy_app_file: Path):
    """``module:attr`` falls back to file load when module isn't on path."""
    sys.path.insert(0, str(dummy_app_file.parent))
    try:
        app = import_app("bootstrap_dummy:app")
        assert isinstance(app, FastAPI)
    finally:
        sys.path.pop(0)
        sys.modules.pop("bootstrap_dummy", None)


def test_import_app_factory_flag(dummy_app_file: Path):
    """``factory=True`` invokes the named callable."""
    app = import_app(f"{dummy_app_file}:create_app", factory=True)
    assert app.title == "Bootstrap Factory App"


def test_import_app_factory_flag_validates_callable(dummy_app_file: Path):
    """``factory=True`` against a non-callable raises TypeError."""
    with pytest.raises(TypeError, match="callable factory"):
        import_app(f"{dummy_app_file}:app", factory=True)


def test_import_app_warns_on_implicit_factory(dummy_app_file: Path, capsys):
    """Callable attribute with no ``--factory`` flag is invoked + warned."""
    app = import_app(f"{dummy_app_file}:create_app")
    assert isinstance(app, FastAPI)
    out = capsys.readouterr().out
    assert "App factory detected" in out


def test_import_app_rejects_non_fastapi(dummy_app_file: Path):
    """Non-FastAPI attribute raises TypeError."""
    with pytest.raises(TypeError, match="not an instance of FastAPI"):
        import_app(f"{dummy_app_file}:not_an_app")


def test_import_app_missing_attribute(dummy_app_file: Path):
    """Missing attribute name raises AttributeError."""
    with pytest.raises(AttributeError, match="does not contain"):
        import_app(f"{dummy_app_file}:nope")


def test_import_app_missing_file():
    """Missing file path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        import_app("/definitely/not/a/real/path.py")


def test_import_app_module_colon_fallback_file_path(tmp_path, monkeypatch):
    """``module:attr`` with unimportable module falls back to file lookup."""
    f = tmp_path / "fallback.py"
    f.write_text("from fastapi import FastAPI\napp = FastAPI(title='Fallback')\n")
    monkeypatch.chdir(tmp_path)
    try:
        app = import_app("fallback:app")
        assert isinstance(app, FastAPI)
        assert app.title == "Fallback"
    finally:
        sys.modules.pop("fallback", None)


def test_import_app_module_colon_fallback_raises_when_file_missing(
    monkeypatch, tmp_path
):
    """Both module import and file fallback failing raise ``FileNotFoundError``."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Neither module"):
        import_app("not_real_module:app")


def test_import_app_loader_returns_none_for_bad_spec(monkeypatch, tmp_path):
    """``spec_from_file_location`` returning ``None`` raises RuntimeError."""
    f = tmp_path / "good.py"
    f.write_text("from fastapi import FastAPI\napp = FastAPI()\n")

    from importlib import util

    def _broken_spec(*_args, **_kwargs):
        return None

    monkeypatch.setattr(util, "spec_from_file_location", _broken_spec)
    with pytest.raises(RuntimeError, match="Failed to load the file specs"):
        import_app(str(f))


def test_import_app_handles_windows_style_colon_notation(tmp_path):
    """Drive-letter + colon-notation (``C:\\...:attr``) hits the colon arm."""
    fake_drive_path = "C:\\nonexistent\\path.py:my_app"
    with pytest.raises((FileNotFoundError, ImportError)):
        import_app(fake_drive_path)
