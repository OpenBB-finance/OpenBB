"""Test the UserSettings model."""

import builtins
import json

import pytest

from openbb_core.app.model import user_settings as user_settings_module
from openbb_core.app.model.credentials import Credentials
from openbb_core.app.model.defaults import Defaults
from openbb_core.app.model.preferences import Preferences
from openbb_core.app.model.user_settings import UserSettings


def test_user_settings():
    """Test the UserSettings model."""
    settings = UserSettings(
        credentials=Credentials(),
        preferences=Preferences(),
        defaults=Defaults(),
    )
    assert isinstance(settings, UserSettings)


def test_user_settings_loads_from_existing_file(tmp_path, monkeypatch):
    p = tmp_path / "user_settings.json"
    payload = {
        "credentials": {"fmp_api_key": "abc"},
        "preferences": {"output_type": "dataframe"},
        "defaults": {"commands": {}},
    }
    p.write_text(json.dumps(payload))

    monkeypatch.setattr(user_settings_module, "USER_SETTINGS_PATH", str(p))

    settings = UserSettings()
    value = settings.credentials.fmp_api_key
    secret = value.get_secret_value() if hasattr(value, "get_secret_value") else value
    assert secret == payload["credentials"]["fmp_api_key"]


def test_user_settings_invalid_json_warns_and_uses_kwargs(tmp_path, monkeypatch):
    p = tmp_path / "user_settings.json"
    p.write_text("{not-json")
    monkeypatch.setattr(user_settings_module, "USER_SETTINGS_PATH", str(p))

    with pytest.warns(UserWarning, match="Error loading user settings"):
        settings = UserSettings(preferences=Preferences(output_type="chart"))

    assert settings.preferences.output_type == "chart"


def test_user_settings_oserror_warns_and_uses_kwargs(monkeypatch):
    monkeypatch.setattr(user_settings_module.os.path, "exists", lambda _p: True)

    def _raise_oserror(*_a, **_k):
        raise OSError("no access")

    monkeypatch.setattr(builtins, "open", _raise_oserror)

    with pytest.warns(UserWarning, match="Error loading user settings"):
        settings = UserSettings(defaults=Defaults(commands={"x": {}}))

    assert "x" in settings.defaults.commands


def test_user_settings_repr_contains_sections():
    settings = UserSettings(
        credentials=Credentials(),
        preferences=Preferences(),
        defaults=Defaults(),
    )
    out = repr(settings)
    assert "UserSettings" in out
    assert "credentials" in out
    assert "preferences" in out
    assert "defaults" in out


def test_user_settings_no_file_uses_kwargs(monkeypatch):
    monkeypatch.setattr(user_settings_module.os.path, "exists", lambda _p: False)

    settings = UserSettings(preferences=Preferences(output_type="chart"))
    assert settings.preferences.output_type == "chart"
