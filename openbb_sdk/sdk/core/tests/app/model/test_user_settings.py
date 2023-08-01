from openbb_core.app.model.user_settings import UserSettings

from unittest.mock import MagicMock


def test_user_settings():
    settings = UserSettings(
        credentials=MagicMock(),
        profile=MagicMock(),
        preferences=MagicMock(),
        defaults=MagicMock(),
    )
    assert isinstance(settings, UserSettings)
