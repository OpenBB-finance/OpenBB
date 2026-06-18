"""Unit tests for the ``openbb_mcp_server.utils.app_import`` shim."""

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


def test_shim_lazy_resolution_matches_source():
    """``utils.app_import.import_app`` re-exports ``app.bootstrap.import_app``."""
    from openbb_mcp_server.app import bootstrap as bootstrap_mod
    from openbb_mcp_server.utils import app_import as shim

    assert shim.import_app is bootstrap_mod.import_app


def test_shim_parse_args_matches_source():
    """``utils.app_import.parse_args`` re-exports ``app.args.parse_args``."""
    from openbb_mcp_server.app import args as args_mod
    from openbb_mcp_server.utils import app_import as shim

    assert shim.parse_args is args_mod.parse_args


def test_shim_unknown_attribute_raises():
    """Unknown shim attribute access raises a clean ``AttributeError``."""
    from openbb_mcp_server.utils import app_import as shim

    with pytest.raises(AttributeError, match="no attribute 'no_such_thing'"):
        _ = shim.no_such_thing


def test_shim_dir_lists_lazy_targets():
    """``dir(shim)`` surfaces the lazy re-exported names."""
    from openbb_mcp_server.utils import app_import as shim

    listed = dir(shim)
    for name in ("import_app", "parse_args", "cl_doc"):
        assert name in listed
    assert listed == sorted(listed)


def test_shim_cl_doc_proxies_launch_script_description():
    """Legacy ``cl_doc`` resolves to ``app.args.LAUNCH_SCRIPT_DESCRIPTION``."""
    from openbb_mcp_server.app import args as args_mod
    from openbb_mcp_server.utils import app_import as shim

    assert shim.cl_doc is args_mod.LAUNCH_SCRIPT_DESCRIPTION


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


def test_import_app_factory_warning_when_flag_omitted(dummy_app_file: Path, capsys):
    """Without ``factory=True``, a callable is invoked and a soft warning prints."""
    app = import_app(f"{dummy_app_file}:create_app")
    assert isinstance(app, FastAPI)
    captured = capsys.readouterr()
    assert "App factory detected" in captured.out


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


def test_import_app_module_colon_with_failed_import_falls_back_to_file(
    tmp_path: Path, monkeypatch
):
    """Unimportable ``module:app`` falls back to a ``module.py`` file lookup."""
    app_content = """
from fastapi import FastAPI

app = FastAPI(title="Fallback App")
"""
    fallback = tmp_path / "fallback_app.py"
    fallback.write_text(app_content)
    monkeypatch.chdir(tmp_path)

    try:
        app = import_app("fallback_app:app")
        assert isinstance(app, FastAPI)
        assert app.title == "Fallback App"
    finally:
        sys.modules.pop("fallback_app", None)


def test_import_app_module_colon_with_failed_import_raises_when_file_missing(
    tmp_path: Path, monkeypatch
):
    """Both module import and file fallback failing yields ``Neither module``."""
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError, match="Neither module"):
        import_app("does_not_exist:app")


def test_parse_args_simple():
    """Default-flag parse run produces the expected dict shape."""
    test_args = [
        "openbb-mcp",
        "--transport",
        "test_transport",
        "--allowed_categories",
        "cat1,cat2",
        "--tool-discovery",
        "true",
    ]
    with patch.object(sys, "argv", test_args):
        result = parse_args()
        assert result["transport"] == "test_transport"
        assert result["mcp_overrides"]["allowed_categories"] == "cat1,cat2"
        assert result["mcp_overrides"]["tool_discovery"] is True
        assert result["app"] is None


def test_parse_args_with_app(dummy_app_file: Path):
    """``--app PATH`` resolves to a FastAPI instance under ``app``."""
    test_args = ["openbb-mcp", "--app", f"{dummy_app_file}:app"]
    with patch.object(sys, "argv", test_args):
        result = parse_args()
        assert isinstance(result["app"], FastAPI)
        assert result["app"].title == "Dummy App"


def test_parse_args_with_factory_app(dummy_app_file: Path):
    """``--factory true`` invokes the named callable to produce the app."""
    test_args = [
        "openbb-mcp",
        "--app",
        f"{dummy_app_file}:create_app",
        "--factory",
        "true",
    ]
    with patch.object(sys, "argv", test_args):
        result = parse_args()
        assert isinstance(result["app"], FastAPI)
        assert result["app"].title == "Dummy Factory App"


def test_parse_args_help():
    """The --help flag exits 0 after printing the launch description."""
    with patch.object(sys, "argv", ["openbb-mcp", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            parse_args()
        assert excinfo.value.code == 0


def test_parse_args_factory_no_name_error(tmp_path: Path):
    """``--factory true --name ""`` for a path without a colon raises."""
    app_file = tmp_path / "some_app.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")

    test_args = [
        "openbb-mcp",
        "--app",
        str(app_file),
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


def test_parse_args_factory_no_name_error_with_windows_drive_path():
    """Windows drive-letter path doesn't fool the factory-name check."""
    test_args = [
        "openbb-mcp",
        "--app",
        r"C:\Users\runner\AppData\Local\Temp\pytest\some_app.py",
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


def test_parse_args_module_colon_notation_extracts_name(tmp_path: Path):
    """``--app PATH:create_app`` resolves ``create_app`` as the factory name."""
    app_file = tmp_path / "factory_app.py"
    app_file.write_text(
        "from fastapi import FastAPI\n"
        "def create_app():\n"
        "    return FastAPI(title='Factory App')\n"
    )

    test_args = [
        "openbb-mcp",
        "--app",
        f"{app_file}:create_app",
        "--factory",
        "true",
    ]
    with patch.object(sys, "argv", test_args):
        result = parse_args()
        assert isinstance(result["app"], FastAPI)
        assert result["app"].title == "Factory App"


def test_parse_args_uvicorn_passthrough():
    """Unrecognized launcher flags land in ``uvicorn_overrides``."""
    with patch.object(  # noqa: S104
        sys,
        "argv",
        ["openbb-mcp", "--host", "0.0.0.0", "--port", "9000"],  # noqa: S104
    ):
        result = parse_args()
        assert result["uvicorn_overrides"]["host"] == "0.0.0.0"  # noqa: S104
        assert result["uvicorn_overrides"]["port"] == "9000"


def test_parse_args_use_colors_flag():
    """``--use-colors`` / ``--no-use-colors`` map to the same kwarg."""
    with patch.object(sys, "argv", ["openbb-mcp", "--no-use-colors"]):
        result = parse_args()
        assert result["uvicorn_overrides"].get("use_colors") is False
    with patch.object(sys, "argv", ["openbb-mcp", "--use-colors"]):
        result = parse_args()
        assert result["uvicorn_overrides"].get("use_colors") is True


def test_parse_args_json_value_decodes():
    """JSON-shaped values (``[...]`` / ``{...}``) get decoded."""
    with patch.object(
        sys, "argv", ["openbb-mcp", "--default_categories", '["equity","crypto"]']
    ):
        result = parse_args()
        assert result["mcp_overrides"]["default_categories"] == ["equity", "crypto"]


def test_parse_args_bare_flag_is_true():
    """A flag with no following value parses as ``True``."""
    with patch.object(sys, "argv", ["openbb-mcp", "--debug"]):
        result = parse_args()
        assert result["uvicorn_overrides"].get("debug") is True


def test_parse_args_spec_and_app_mutually_exclusive(tmp_path: Path):
    """Supplying both ``--spec`` and ``--app`` raises a clear error."""
    spec_file = tmp_path / "x.spec"
    spec_file.write_text("{}")
    app_file = tmp_path / "a.py"
    app_file.write_text("from fastapi import FastAPI\napp = FastAPI()\n")
    with (
        patch.object(
            sys,
            "argv",
            ["openbb-mcp", "--spec", str(spec_file), "--app", str(app_file)],
        ),
        pytest.raises(ValueError, match="--spec and --app are mutually exclusive"),
    ):
        parse_args()


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
        """Test Windows-style absolute paths."""
        app = import_app(str(app_file), "app", False)
        assert isinstance(app, FastAPI)

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_path_with_colon_notation(self, app_file: Path):
        """Test Windows path with colon notation."""
        app = import_app(f"{app_file}:app", "app", False)
        assert isinstance(app, FastAPI)


class TestPathDetectionHelpers:
    """Test path detection logic for cross-platform compatibility."""

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="Unix-style absolute paths only — '/home/...' is relative on Windows",
    )
    def test_is_absolute_path_detection_unix(self):
        """Test absolute path detection for Unix paths."""
        assert Path("/home/user/app.py").is_absolute() is True
        assert Path("/app.py").is_absolute() is True
        assert Path("app.py").is_absolute() is False
        assert Path("./app.py").is_absolute() is False
        assert Path("subdir/app.py").is_absolute() is False

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_is_absolute_path_detection_windows(self):
        """Test absolute path detection for Windows paths."""
        assert Path("C:\\Users\\app.py").is_absolute() is True
        assert Path("D:/Projects/app.py").is_absolute() is True
        assert Path("app.py").is_absolute() is False
        assert Path(".\\app.py").is_absolute() is False

    def test_colon_notation_vs_windows_drive(self):
        """Test distinguishing module:name notation from Windows drive letters."""
        module_notations = [
            "module:app",
            "package.module:app",
            "my_app.main:create_app",
        ]

        for notation in module_notations:
            assert ":" in notation
            parts = notation.split(":")
            assert len(parts[0]) > 1 or not parts[0].isalpha()

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_windows_drive_letter_detection(self):
        """Test detection of Windows drive letters vs colon notation."""
        windows_paths = [
            "C:\\app.py",
            "D:/Projects/app.py",
            "E:\\Users\\test\\app.py",
        ]

        for path_str in windows_paths:
            path = Path(path_str)
            assert path.is_absolute()
            assert path.drive != ""

        complex_path = "C:\\Projects\\app.py:myapp"
        assert complex_path.count(":") == 2


class TestModuleColonNotationHelper:
    """Test the _is_module_colon_notation helper function behavior."""

    def test_simple_module_notation(self):
        """Test simple module:name notation is detected correctly."""
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
            for mod in list(sys.modules.keys()):
                if mod.startswith("mypkg"):
                    del sys.modules[mod]
