"""Test the preferences class."""

from openbb_core.app.model.preferences import Preferences


def test_preferences():
    """Test the preferences class."""
    preferences = Preferences()
    assert isinstance(preferences, Preferences)


def test_preferences_repr():
    """Test __repr__ returns a formatted string."""
    preferences = Preferences()
    result = repr(preferences)
    assert "Preferences" in result
    assert "chart_style" in result
