"""Test Config Console."""

from unittest.mock import patch

import pytest
from openbb_cli.config.console import Console
from rich.text import Text

# pylint: disable=redefined-outer-name, unused-argument, unused-variable, protected-access


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
    color1 = (255, 0, 0)  # Red
    color2 = (0, 0, 255)  # Blue
    blended_text = Console._blend_text(message, color1, color2)
    assert isinstance(blended_text, Text)
    assert "Hello" in blended_text.plain
