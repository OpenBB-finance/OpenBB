"""Test the CommandContext model."""

from openbb_core.app.model.command_context import (
    CommandContext,
    SystemSettings,
    UserSettings,
)


def test_command_context():
    """Test the CommandContext model."""
    cc = CommandContext()
    assert isinstance(cc, CommandContext)
    assert isinstance(cc.user_settings, UserSettings)
    assert isinstance(cc.system_settings, SystemSettings)


def test_fields():
    """Test the CommandContext fields."""
    fields = CommandContext.model_fields
    fields_keys = fields.keys()

    assert "user_settings" in fields_keys
    assert "system_settings" in fields_keys
