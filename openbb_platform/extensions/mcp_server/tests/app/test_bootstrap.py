"""Tests for ``openbb_mcp_server.app.bootstrap``."""

import sys
from importlib import util
from pathlib import Path

import pytest
from fastapi import FastAPI

from openbb_mcp_server.app.bootstrap import import_app


@pytest.fixture
def dummy_app_file(tmp_path: Path):
    """Create a module with an app, a factory, and two non-app attributes."""
    content = """
from fastapi import FastAPI

app = FastAPI(title="Bootstrap Test App")

def create_app():
    return FastAPI(title="Bootstrap Factory App")

not_an_app = "not a FastAPI"
"""
    f = tmp_path / "bootstrap_dummy.py"
    f.write_text(content)
    yield f
    sys.modules.pop("bootstrap_dummy", None)


def _write_app(path: Path, title: str, name: str = "app") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"from fastapi import FastAPI\n{name} = FastAPI(title={title!r})\n")
    return path


class TestImportApp:
    """Importing a FastAPI app from a path, module, or factory."""

    def test_import_app_file_path(self, dummy_app_file: Path):
        """A bare file path imports cleanly."""
        app = import_app(str(dummy_app_file))
        assert isinstance(app, FastAPI)
        assert app.title == "Bootstrap Test App"

    def test_import_app_module_colon(self, dummy_app_file: Path, monkeypatch):
        """``module:attr`` imports the module from ``sys.path``."""
        monkeypatch.syspath_prepend(str(dummy_app_file.parent))
        app = import_app("bootstrap_dummy:app")
        assert app.title == "Bootstrap Test App"

    def test_import_app_factory_flag(self, dummy_app_file: Path):
        """``factory=True`` invokes the named callable."""
        app = import_app(f"{dummy_app_file}:create_app", factory=True)
        assert app.title == "Bootstrap Factory App"

    def test_import_app_factory_flag_validates_callable(self, dummy_app_file: Path):
        """``factory=True`` against a non-callable raises TypeError."""
        with pytest.raises(TypeError, match="callable factory"):
            import_app(f"{dummy_app_file}:app", factory=True)

    def test_import_app_warns_on_implicit_factory(self, dummy_app_file: Path, capsys):
        """Callable attribute with no ``--factory`` flag is invoked + warned."""
        app = import_app(f"{dummy_app_file}:create_app")
        assert app.title == "Bootstrap Factory App"
        assert "App factory detected" in capsys.readouterr().out

    def test_import_app_rejects_non_fastapi(self, dummy_app_file: Path):
        """Non-FastAPI attribute raises TypeError."""
        with pytest.raises(TypeError, match="not an instance of FastAPI"):
            import_app(f"{dummy_app_file}:not_an_app")

    def test_import_app_missing_attribute(self, dummy_app_file: Path):
        """Missing attribute name raises AttributeError."""
        with pytest.raises(AttributeError, match="does not contain an 'nope' instance"):
            import_app(f"{dummy_app_file}:nope")

    def test_import_app_missing_file(self, tmp_path):
        """Missing file path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            import_app(str(tmp_path / "missing.py"))

    def test_import_app_module_colon_fallback_file_path(self, tmp_path, monkeypatch):
        """``module:attr`` with unimportable module falls back to ``<module>.py`` in CWD."""
        _write_app(tmp_path / "fallback.py", "Fallback")
        monkeypatch.chdir(tmp_path)
        monkeypatch.delitem(sys.modules, "fallback", raising=False)
        app = import_app("fallback:app")
        assert app.title == "Fallback"
        sys.modules.pop("fallback", None)

    def test_import_app_module_colon_fallback_raises_when_file_missing(
        self, monkeypatch, tmp_path
    ):
        """Both module import and file fallback failing raise ``FileNotFoundError``."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError, match="Neither module"):
            import_app("not_real_module:app")

    def test_import_app_loader_returns_none_for_bad_spec(self, monkeypatch, tmp_path):
        """``spec_from_file_location`` returning ``None`` raises RuntimeError."""
        f = _write_app(tmp_path / "good.py", "Good")
        monkeypatch.setattr(util, "spec_from_file_location", lambda *_a, **_k: None)
        with pytest.raises(RuntimeError, match="Failed to load the file specs"):
            import_app(str(f))


class TestImportAppPathHandling:
    """Importing apps from absolute, relative, dotted, and colon-suffixed paths."""

    def test_relative_path(self, tmp_path: Path, monkeypatch):
        """A relative file path resolves against CWD."""
        _write_app(tmp_path / "relative_app.py", "Relative Path App")
        monkeypatch.chdir(tmp_path)
        assert import_app("relative_app.py").title == "Relative Path App"

    def test_relative_path_with_subdirectory(self, tmp_path: Path, monkeypatch):
        """A relative path into a subdirectory resolves against CWD."""
        _write_app(tmp_path / "subdir" / "myapp.py", "Subdir App")
        monkeypatch.chdir(tmp_path)
        assert import_app("subdir/myapp.py").title == "Subdir App"

    def test_absolute_file_path_with_colon_attribute(self, tmp_path: Path):
        """An absolute ``file.py:attr`` path loads the named attribute."""
        path = _write_app(tmp_path / "custom_name.py", "Custom", name="custom_app")
        assert import_app(f"{path}:custom_app").title == "Custom"

    def test_dotted_module_path_notation(self, tmp_path: Path, monkeypatch):
        """Dotted module paths like ``package.subpackage.module:app`` import."""
        subpkg_dir = tmp_path / "mypkg" / "subpkg"
        subpkg_dir.mkdir(parents=True)
        (tmp_path / "mypkg" / "__init__.py").write_text("")
        (subpkg_dir / "__init__.py").write_text("")
        _write_app(subpkg_dir / "mymodule.py", "Dotted Module App")
        monkeypatch.syspath_prepend(str(tmp_path))

        assert import_app("mypkg.subpkg.mymodule:app").title == "Dotted Module App"
        for mod in [m for m in sys.modules if m.startswith("mypkg")]:
            del sys.modules[mod]

    def test_windows_drive_path_with_attribute_is_colon_notation(self):
        """A drive-letter path with an ``:attr`` suffix is treated as ``module:attr``."""
        with pytest.raises(FileNotFoundError, match="Neither module"):
            import_app("C:\\nonexistent\\path.py:my_app")

    def test_windows_drive_path_without_attribute_is_a_file(self):
        """A bare drive-letter path is treated as a file path, not ``module:attr``."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            import_app("C:\\nonexistent\\path.py")
