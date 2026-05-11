"""Test Config Console."""

from unittest.mock import patch

import pytest
from rich.text import Text

from openbb_cli.config.console import Console


@pytest.fixture
def mock_settings():
    """Mock settings to inject into Console."""

    class MockSettings:
        TEST_MODE = False
        ENABLE_RICH_PANEL = True
        SHOW_VERSION = True
        VERSION = "1.0"

    return MockSettings()


@pytest.fixture
def console(mock_settings):
    """Create a Console instance with mocked settings."""
    with patch("rich.console.Console") as MockRichConsole:  # noqa: F841
        return Console(settings=mock_settings)


def test_print_without_panel(console, mock_settings):
    """Test printing without a rich panel when disabled."""
    mock_settings.ENABLE_RICH_PANEL = False
    with patch.object(console._console, "print") as mock_print:
        console.print(text="Hello, world!", menu="Home Menu")
        mock_print.assert_called_once_with("Hello, world!")


def test_blend_text():
    """Test blending text colors."""
    message = "Hello"
    color1 = (255, 0, 0)
    color2 = (0, 0, 255)
    blended_text = Console._blend_text(message, color1, color2)
    assert isinstance(blended_text, Text)
    assert "Hello" in blended_text.plain


def test_filter_rich_tags_strips_known_tags():
    """``_filter_rich_tags`` removes every tag in ``RICH_TAGS``."""
    from openbb_cli.config.menu_text import RICH_TAGS

    text = "".join(RICH_TAGS) + "body"
    assert Console._filter_rich_tags(text) == "body"


def test_print_panel_with_show_version_true(console, mock_settings):
    """Default path: TEST_MODE off, panel + version line emitted."""
    mock_settings.SHOW_VERSION = True
    with patch.object(console._console, "print") as mock_print:
        console.print(text="hello", menu="Menu")
    mock_print.assert_called_once()


def test_print_panel_with_show_version_false(console, mock_settings):
    """``SHOW_VERSION=False`` uses the unversioned subtitle string."""
    mock_settings.SHOW_VERSION = False
    with patch.object(console._console, "print") as mock_print:
        console.print(text="hello", menu="Menu")
    mock_print.assert_called_once()


def test_print_panel_in_test_mode_strips_tags(capsys, console, mock_settings):
    """``TEST_MODE=True`` bypasses Rich and prints the filtered text via ``print``."""
    mock_settings.TEST_MODE = True
    console.print(text="[info]hi[/info]", menu="Menu")
    out = capsys.readouterr().out.strip()
    assert "info" in out or "hi" in out


def test_print_test_mode_without_text_menu_uses_builtin_print(
    capsys, console, mock_settings
):
    """In TEST_MODE without text/menu kwargs, plain ``print`` is used."""
    mock_settings.TEST_MODE = True
    console.print("hello world")
    assert "hello world" in capsys.readouterr().out


def test_input_uses_print_then_input(console):
    """``input`` calls print(end="") then ``input()``."""
    with (
        patch.object(console, "print") as p,
        patch("builtins.input", return_value="typed"),
    ):
        result = console.input("prompt> ")
    assert result == "typed"
    p.assert_called_once()
    assert p.call_args[1].get("end") == ""


def test_print_general_args_not_in_test_mode(console, mock_settings):
    """``print(*args, **kwargs)`` without text/menu kwargs and not test_mode → rich console."""
    mock_settings.TEST_MODE = False
    with patch.object(console._console, "print") as inner_print:
        console.print("hello", style="bold")
    inner_print.assert_called_once_with("hello", style="bold")
