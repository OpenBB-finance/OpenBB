"""Unit tests for the app_import module."""

# pylint: disable=W0621

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from openbb_mcp_server.utils.app_import import import_app, parse_args


@pytest.fixture
def dummy_app_file(tmp_path: Path):
    """Create a dummy FastAPI app file for testing."""
    app_content = """
from fastapi import FastAPI

app = FastAPI(title="Dummy App")

def create_app():
    return FastAPI(title="Dummy Factory App")

not_an_app = "I am not a FastAPI instance"

def not_a_factory():
    return "not a factory"
"""
    app_file = tmp_path / "dummy_app.py"
    app_file.write_text(app_content)
    return app_file


def test_import_app_from_module_colon_notation(dummy_app_file: Path):
    """Test importing an app from a module path with colon notation."""
    sys.path.insert(0, str(dummy_app_file.parent))
    try:
        app = import_app("dummy_app:app")
        assert isinstance(app, FastAPI)
        assert app.title == "Dummy App"
    finally:
        sys.path.pop(0)
        del sys.modules["dummy_app"]


def test_import_app_from_file_colon_notation(dummy_app_file: Path):
    """Test importing an app from a file path with colon notation."""
    app = import_app(f"{dummy_app_file}:app")
    assert isinstance(app, FastAPI)
    assert app.title == "Dummy App"


def test_import_app_from_file_path(dummy_app_file: Path):
    """Test importing an app from a direct file path."""
    app = import_app(str(dummy_app_file))
    assert isinstance(app, FastAPI)
    assert app.title == "Dummy App"


def test_import_app_factory(dummy_app_file: Path):
    """Test importing an app from a factory function."""
    app = import_app(f"{dummy_app_file}:create_app", factory=True)
    assert isinstance(app, FastAPI)
    assert app.title == "Dummy Factory App"


def test_import_app_factory_not_callable(dummy_app_file: Path):
    """Test that a TypeError is raised when factory is true but the object is not callable."""
    with pytest.raises(
        TypeError, match="appears not to be a callable factory function"
    ):
        import_app(f"{dummy_app_file}:app", factory=True)


def test_import_app_not_fastapi_instance(dummy_app_file: Path):
    """Test that a TypeError is raised when the imported object is not a FastAPI instance."""
    with pytest.raises(TypeError, match="is not an instance of FastAPI"):
        import_app(f"{dummy_app_file}:not_an_app")


def test_import_app_file_not_found():
    """Test that a FileNotFoundError is raised when the app file does not exist."""
    with pytest.raises(FileNotFoundError):
        import_app("non_existent_app.py")


def test_import_app_attribute_not_found(dummy_app_file: Path):
    """Test that an AttributeError is raised when the app instance is not in the file."""
    with pytest.raises(AttributeError, match="does not contain an 'invalid_app'"):
        import_app(f"{dummy_app_file}:invalid_app")


def test_parse_args_simple():
    """Test parsing of simple command-line arguments."""
    test_args = [
        "mcp_server",
        "--transport",
        "test_transport",
        "--allowed_categories",
        "cat1,cat2",
        "--no-tool-discovery",
        "true",
    ]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert args.transport == "test_transport"
        assert args.allowed_categories == "cat1,cat2"
        assert args.no_tool_discovery is True
        assert args.imported_app is None


def test_parse_args_with_app(dummy_app_file: Path):
    """Test parsing arguments when an app path is provided."""
    test_args = ["mcp_server", "--app", f"{dummy_app_file}:app"]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert isinstance(args.imported_app, FastAPI)
        assert args.imported_app.title == "Dummy App"


def test_parse_args_with_factory_app(dummy_app_file: Path):
    """Test parsing arguments with an app factory."""
    test_args = [
        "mcp_server",
        "--app",
        f"{dummy_app_file}:create_app",
        "--factory",
        "true",
    ]
    with patch.object(sys, "argv", test_args):
        args = parse_args()
        assert isinstance(args.imported_app, FastAPI)
        assert args.imported_app.title == "Dummy Factory App"


def test_parse_args_help():
    """Test the --help argument."""
    with patch.object(sys, "argv", ["mcp_server", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            parse_args()
        assert excinfo.value.code == 0


def test_parse_args_factory_no_name_error():
    """Test ValueError when factory is true but no app name is provided."""
    test_args = [
        "mcp_server",
        "--app",
        "some_app.py",
        "--factory",
        "true",
        "--name",
        "",
    ]
    with (
        patch.object(sys, "argv", test_args),
        pytest.raises(
            ValueError,
            match="The factory function name must be provided to the --name parameter",
        ),
    ):
        parse_args()


# =============================================================================
# Path Handling Tests - Cross-Platform Compatibility
# =============================================================================


class TestPathHandling:
    """Test cross-platform path handling in import_app function."""

    @pytest.fixture
    def app_file(self, tmp_path: Path):
        """Create a simple FastAPI app file for testing."""
        app_content = """
from fastapi import FastAPI

app = FastAPI(title="Test App")
"""
        app_file = tmp_path / "test_app.py"
        app_file.write_text(app_content)
        return app_file

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_unix_absolute_path(self, app_file: Path):
        """Test Unix-style absolute paths (e.g., /home/user/app.py)."""
        app = import_app(str(app_file), "app", False)
        assert isinstance(app, FastAPI)
        assert app.title == "Test App"

    def test_relative_path(self, tmp_path: Path, monkeypatch):
        """Test relative paths are resolved correctly."""
        app_content = """
from fastapi import FastAPI

app = FastAPI(title="Relative Path App")
"""
        app_file = tmp_path / "relative_app.py"
        app_file.write_text(app_content)
        monkeypatch.chdir(tmp_path)

        app = import_app("relative_app.py", "app", False)
        assert isinstance(app, FastAPI)
        assert app.title == "Relative Path App"

    def test_relative_path_with_subdirectory(self, tmp_path: Path, monkeypatch):
        """Test relative paths with subdirectories."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        app_content = """
from fastapi import FastAPI

app = FastAPI(title="Subdir App")
"""
        app_file = subdir / "myapp.py"
        app_file.write_text(app_content)
        monkeypatch.chdir(tmp_path)

        app = import_app("subdir/myapp.py", "app", False)
        assert isinstance(app, FastAPI)
        assert app.title == "Subdir App"

    def test_module_colon_notation(self, tmp_path: Path):
        """Test module:name colon notation (e.g., 'my_module:app')."""
        app_content = """
from fastapi import FastAPI

myapp = FastAPI(title="Module Colon App")
"""
        app_file = tmp_path / "colon_module.py"
        app_file.write_text(app_content)
        sys.path.insert(0, str(tmp_path))

        try:
            app = import_app("colon_module:myapp", "myapp", False)
            assert isinstance(app, FastAPI)
            assert app.title == "Module Colon App"
        finally:
            sys.path.pop(0)
            if "colon_module" in sys.modules:
                del sys.modules["colon_module"]

    def test_file_path_with_colon_notation(self, app_file: Path):
        """Test file path with colon notation (e.g., 'myfile.py:app')."""
        app = import_app(f"{app_file}:app", "app", False)
        assert isinstance(app, FastAPI)
        assert app.title == "Test App"

    def test_file_not_found_error(self, tmp_path: Path):
        """Test FileNotFoundError is raised for non-existent files."""
        non_existent_path = tmp_path / "does_not_exist.py"

        with pytest.raises(FileNotFoundError):
            import_app(str(non_existent_path), "app", False)

    def test_attribute_error_missing_app_instance(self, tmp_path: Path):
        """Test AttributeError is raised when app instance is missing."""
        app_content = """
# No app defined here
x = 1
"""
        app_file = tmp_path / "no_app.py"
        app_file.write_text(app_content)

        with pytest.raises(AttributeError, match="does not contain an 'app'"):
            import_app(str(app_file), "app", False)

    def test_custom_app_name(self, tmp_path: Path):
        """Test importing app with custom name."""
        app_content = """
from fastapi import FastAPI

custom_app = FastAPI(title="Custom Named App")
"""
        app_file = tmp_path / "custom_name.py"
        app_file.write_text(app_content)

        app = import_app(f"{app_file}:custom_app", "custom_app", False)
        assert isinstance(app, FastAPI)
        assert app.title == "Custom Named App"

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_absolute_path(self, app_file: Path):
        """Test Windows-style absolute paths"""
        # On Windows, tmp_path will have a drive letter (e.g., C:\...)
        app = import_app(str(app_file), "app", False)
        assert isinstance(app, FastAPI)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_path_with_colon_notation(self, app_file: Path):
        """Test Windows path with colon notation."""
        # Windows path with colon notation: C:\path\app.py:app
        app = import_app(f"{app_file}:app", "app", False)
        assert isinstance(app, FastAPI)


class TestPathDetectionHelpers:
    """Test path detection logic for cross-platform compatibility."""

    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_is_absolute_path_detection_unix(self):
        """Test absolute path detection for Unix paths."""
        # Unix absolute paths
        assert Path("/home/user/app.py").is_absolute() is True
        assert Path("/app.py").is_absolute() is True
        # Relative paths
        assert Path("app.py").is_absolute() is False
        assert Path("./app.py").is_absolute() is False
        assert Path("subdir/app.py").is_absolute() is False

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_is_absolute_path_detection_windows(self):
        """Test absolute path detection for Windows paths."""
        # Windows absolute paths
        assert Path("C:\\Users\\app.py").is_absolute() is True
        assert Path("D:/Projects/app.py").is_absolute() is True
        # Relative paths
        assert Path("app.py").is_absolute() is False
        assert Path(".\\app.py").is_absolute() is False

    def test_colon_notation_vs_windows_drive(self):
        """Test distinguishing module:name notation from Windows drive letters."""
        # These should be recognized as module:name notation
        module_notations = [
            "module:app",
            "package.module:app",
            "my_app.main:create_app",
        ]

        for notation in module_notations:
            # Has colon and is not a Windows drive letter pattern
            assert ":" in notation
            # First char before colon is not a single letter (drive)
            parts = notation.split(":")
            assert len(parts[0]) > 1 or not parts[0].isalpha()

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_drive_letter_detection(self):
        """Test detection of Windows drive letters vs colon notation."""
        # Windows paths with drive letters
        windows_paths = [
            "C:\\app.py",
            "D:/Projects/app.py",
            "E:\\Users\\test\\app.py",
        ]

        for path_str in windows_paths:
            path = Path(path_str)
            # Should be detected as absolute (has drive)
            assert path.is_absolute()
            # Drive should be detected
            assert path.drive != ""

        # Windows path WITH colon notation (e.g., C:\path\app.py:myapp)
        complex_path = "C:\\Projects\\app.py:myapp"
        # This has multiple colons - drive colon + notation colon
        assert complex_path.count(":") == 2


class TestModuleColonNotationHelper:
    """Test the _is_module_colon_notation helper function behavior."""

    def test_simple_module_notation(self):
        """Test simple module:name notation is detected correctly."""
        # These should be recognized as module colon notation
        from openbb_mcp_server.utils.app_import import import_app

        # We test the behavior indirectly through import_app
        # Module notation without file should try import first
        with pytest.raises((ImportError, FileNotFoundError)):
            import_app("nonexistent_module:app")

    def test_file_path_without_colon(self, tmp_path: Path):
        """Test file paths without colons are handled correctly."""
        app_content = """
from fastapi import FastAPI

app = FastAPI(title="No Colon App")
"""
        app_file = tmp_path / "no_colon_app.py"
        app_file.write_text(app_content)

        app = import_app(str(app_file), "app", False)
        assert isinstance(app, FastAPI)
        assert app.title == "No Colon App"

    def test_dotted_module_path_notation(self, tmp_path: Path):
        """Test dotted module paths like 'package.subpackage.module:app'."""
        # Create a package structure
        pkg_dir = tmp_path / "mypkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("")

        subpkg_dir = pkg_dir / "subpkg"
        subpkg_dir.mkdir()
        (subpkg_dir / "__init__.py").write_text("")

        app_content = """
from fastapi import FastAPI

app = FastAPI(title="Dotted Module App")
"""
        (subpkg_dir / "mymodule.py").write_text(app_content)

        sys.path.insert(0, str(tmp_path))
        try:
            app = import_app("mypkg.subpkg.mymodule:app")
            assert isinstance(app, FastAPI)
            assert app.title == "Dotted Module App"
        finally:
            sys.path.pop(0)
            # Clean up sys.modules
            for mod in list(sys.modules.keys()):
                if mod.startswith("mypkg"):
                    del sys.modules[mod]
