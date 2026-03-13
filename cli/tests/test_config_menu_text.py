"""Test Config Menu Text."""

import pytest
from openbb_cli.config.menu_text import MenuText

# pylint: disable=redefined-outer-name, protected-access


@pytest.fixture
def menu_text():
    """Fixture to create a MenuText instance for testing."""
    return MenuText(path="/test/path")


def test_initialization(menu_text):
    """Test initialization of the MenuText class."""
    assert menu_text.menu_text == ""
    assert menu_text.menu_path == "/test/path"
    assert menu_text.warnings == []


def test_add_raw(menu_text):
    """Test adding raw text."""
    menu_text.add_raw("Example raw text")
    assert "Example raw text" in menu_text.menu_text


def test_add_info(menu_text):
    """Test adding informational text."""
    menu_text.add_info("Info text")
    assert "[info]Info text:[/info]" in menu_text.menu_text


def test_add_cmd(menu_text):
    """Test adding a command."""
    menu_text.add_cmd("command", "Performs an action")
    assert "command" in menu_text.menu_text
    assert "Performs an action" in menu_text.menu_text


def test_format_cmd_name(menu_text):
    """Test formatting of command names that are too long."""
    long_name = "x" * 75  # Assuming CMD_NAME_LENGTH is 65
    formatted_name = menu_text._format_cmd_name(long_name)
    assert len(formatted_name) <= menu_text.CMD_NAME_LENGTH
    assert menu_text.warnings  # Check that a warning was added


def test_format_cmd_description(menu_text):
    """Test truncation of long descriptions."""
    long_description = "y" * 100  # Assuming CMD_DESCRIPTION_LENGTH is 65
    formatted_description = menu_text._format_cmd_description("cmd", long_description)
    assert len(formatted_description) <= menu_text.CMD_DESCRIPTION_LENGTH


def test_add_menu(menu_text):
    """Test adding a menu item."""
    menu_text.add_menu("Settings", "Configure your settings")
    assert "Settings" in menu_text.menu_text
    assert "Configure your settings" in menu_text.menu_text


def test_add_setting(menu_text):
    """Test adding a setting."""
    menu_text.add_setting("Enable Feature", True, "Feature description")
    assert "Enable Feature" in menu_text.menu_text
    assert "Feature description" in menu_text.menu_text
    assert "[green]" in menu_text.menu_text
