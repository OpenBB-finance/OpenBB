from openbb_core.app.model.profile import Profile


def test_preferences():
    preferences = Profile()
    assert isinstance(preferences, Profile)
