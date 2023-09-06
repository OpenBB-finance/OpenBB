from openbb_core.app.model.command_context import (
    CommandContext,
    SystemSettings,
    UserSettings,
)


def test_command_context():
    cc = CommandContext()
    assert isinstance(cc, CommandContext)
    assert isinstance(cc.user_settings, UserSettings)
    assert isinstance(cc.system_settings, SystemSettings)


def test_fields():
    fields = CommandContext.__fields__
    fields_keys = fields.keys()

    assert "user_settings" in fields_keys
    assert "system_settings" in fields_keys
