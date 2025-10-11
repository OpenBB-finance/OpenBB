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
