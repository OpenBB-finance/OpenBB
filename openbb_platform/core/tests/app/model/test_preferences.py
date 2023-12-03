from openbb_core.app.model.preferences import Preferences


def test_preferences():
    preferences = Preferences()
    assert isinstance(preferences, Preferences)
