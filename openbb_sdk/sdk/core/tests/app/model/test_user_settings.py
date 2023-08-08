from unittest.mock import MagicMock

from openbb_core.app.model.user_settings import UserSettings


def test_user_settings():
    settings = UserSettings(
        credentials=MagicMock(),
        profile=MagicMock(),
        preferences=MagicMock(),
        defaults=MagicMock(),
    )
    assert isinstance(settings, UserSettings)
