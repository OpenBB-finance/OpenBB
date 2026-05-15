"""Test Config Style."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from openbb_cli.config.style import Style

# pylint: disable=redefined-outer-name, protected-access


@pytest.fixture
def mock_style_directory(tmp_path):
    """Fixture to create a mock styles directory."""
    (tmp_path / "styles" / "default").mkdir(parents=True, exist_ok=True)
    return tmp_path / "styles"


@pytest.fixture
def style(mock_style_directory):
    """Fixture to create a Style instance for testing."""
    return Style(directory=mock_style_directory)


def test_initialization(style):
    """Test that Style class initializes with default properties."""
    assert style.line_width == 1.5
    assert isinstance(style.console_style, dict)


@patch("pathlib.Path.exists", MagicMock(return_value=True))
@patch("pathlib.Path.rglob")
def test_load_styles(mock_rglob, style, mock_style_directory):
    """Test loading styles from directories."""
    mock_rglob.return_value = [mock_style_directory / "default" / "dark.richstyle.json"]
    style._load(mock_style_directory)
    assert "dark" in style.console_styles_available


@patch("builtins.open", new_callable=MagicMock)
@patch("json.load", MagicMock(return_value={"background": "black"}))
def test_from_json(mock_open, style, mock_style_directory):
    """Test loading style from a JSON file."""
    json_file = mock_style_directory / "dark.richstyle.json"
    result = style._from_json(json_file)
    assert result == {"background": "black"}
    mock_open.assert_called_once_with(json_file)


def test_apply_invalid_style(style, mock_style_directory, capsys):
    """Test applying an invalid style and falling back to default."""
    style.apply("nonexistent", mock_style_directory)
    captured = capsys.readouterr()
    assert "Invalid console style" in captured.out


def test_available_styles(style):
    """Test listing available styles."""
    style.console_styles_available = {"dark": Path("/path/to/dark.richstyle.json")}
    assert "dark" in style.available_styles
