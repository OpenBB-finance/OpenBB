"""Test APISettings model."""

from openbb_core.app.model.api_settings import APISettings


def test_api_settings_prefix():
    """Test prefix property returns formatted version string."""
    settings = APISettings(version="2")
    assert settings.prefix == "/api/v2"

    settings_v1 = APISettings(version="1")
    assert settings_v1.prefix == "/api/v1"


def test_api_settings_repr():
    """Test __repr__ returns formatted string with class name and fields."""
    settings = APISettings(version="1")
    result = repr(settings)
    assert "APISettings" in result
    assert "version" in result
