"""Test Config Menu Text."""

import pytest

from openbb_cli.config.menu_text import MenuText


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
    """Test that _format_cmd_name returns the name as-is (no truncation)."""
    long_name = "x" * 75
    formatted_name = menu_text._format_cmd_name(long_name)
    assert formatted_name == long_name


def test_format_cmd_description(menu_text):
    """Test truncation of long descriptions."""
    long_description = "y" * 100
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


def test_get_providers_returns_non_standard_keys(menu_text, monkeypatch):
    """``_get_providers`` reads ``obb.reference['paths']`` and drops the 'standard' key.

    The ``obb`` import is lazy inside the helper, so we inject a fake ``openbb``
    module into ``sys.modules`` rather than patching the menu_text module.
    """
    import sys
    import types

    fake_obb_mod = types.ModuleType("openbb")
    fake_obb_mod.obb = type(
        "Obb",
        (),
        {
            "reference": {
                "paths": {
                    "/equity/price/historical": {
                        "parameters": {
                            "standard": {},
                            "fmp": {},
                            "yfinance": {},
                        }
                    }
                }
            },
        },
    )
    monkeypatch.setitem(sys.modules, "openbb", fake_obb_mod)
    providers = menu_text._get_providers("/equity/price/historical")
    assert providers == ["fmp", "yfinance"]


def test_format_cmd_description_blanks_when_matches_path(menu_text):
    """If the description equals ``menu_path + name``, it gets blanked."""
    out = menu_text._format_cmd_description("command", "/test/pathcommand")
    assert out == ""


def test_add_raw_with_left_spacing(menu_text):
    """``left_spacing=True`` prepends SECTION_SPACING and a newline."""
    menu_text.add_raw("hello", left_spacing=True)
    assert menu_text.menu_text.endswith("hello\n")
    assert menu_text.menu_text.startswith(" " * menu_text.SECTION_SPACING)


def test_get_providers_returns_empty_when_openbb_missing(menu_text, monkeypatch):
    """Spec-driven REPL: ``openbb`` import fails → return []."""
    import sys

    monkeypatch.setitem(sys.modules, "openbb", None)
    assert menu_text._get_providers("/whatever") == []


def test_add_cmd_emits_provider_tag(menu_text, monkeypatch):
    """When providers are known for the path, the line ends with ``[src][...]``."""
    import sys
    import types

    fake_obb_mod = types.ModuleType("openbb")
    fake_obb_mod.obb = type(
        "Obb",
        (),
        {
            "reference": {
                "paths": {"/test/pathshow": {"parameters": {"standard": {}, "fmp": {}}}}
            },
        },
    )
    monkeypatch.setitem(sys.modules, "openbb", fake_obb_mod)
    menu_text.add_cmd("show", "do thing")
    assert "[src]" in menu_text.menu_text
    assert "fmp" in menu_text.menu_text


def test_add_menu_blanks_description_matching_path(menu_text):
    """``description == menu_path+name`` is blanked just like in ``add_cmd``."""
    menu_text.add_menu("settings", description="/test/pathsettings")
    assert "/test/pathsettings" not in menu_text.menu_text


def test_add_menu_truncates_long_description(menu_text):
    """Description longer than CMD_DESCRIPTION_LENGTH is truncated with ``...``."""
    long_desc = "y" * (menu_text.CMD_DESCRIPTION_LENGTH + 20)
    menu_text.add_menu("settings", description=long_desc)
    assert "..." in menu_text.menu_text
