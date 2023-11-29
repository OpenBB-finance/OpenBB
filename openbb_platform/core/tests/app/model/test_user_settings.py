from openbb_core.app.model.credentials import Credentials
from openbb_core.app.model.defaults import Defaults
from openbb_core.app.model.preferences import Preferences
from openbb_core.app.model.profile import Profile
from openbb_core.app.model.user_settings import UserSettings


def test_user_settings():
    settings = UserSettings(
        credentials=Credentials(),
        profile=Profile(),
        preferences=Preferences(),
        defaults=Defaults(),
    )
    assert isinstance(settings, UserSettings)
