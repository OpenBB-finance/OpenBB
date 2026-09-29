"""Tests for openbb_core.app.logs.models.logging_settings."""

from pathlib import Path
from types import SimpleNamespace

from openbb_core.app.logs.models.logging_settings import LoggingSettings
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings


def test_logging_settings_defaults():
    ls = LoggingSettings()
    assert isinstance(ls.app_name, str)
    assert isinstance(ls.app_id, str) and ls.app_id
    assert isinstance(ls.session_id, str) and ls.session_id
    assert isinstance(ls.user_logs_directory, Path)


def test_logging_settings_uses_provided_user_and_system_settings(tmp_path):
    user = UserSettings()
    user.preferences.data_directory = str(tmp_path)
    system = SystemSettings()
    ls = LoggingSettings(user_settings=user, system_settings=system)
    assert str(tmp_path) in str(ls.user_logs_directory)
    assert ls.app_name == system.logging_app_name
    assert ls.frequency == system.logging_frequency
    assert ls.handler_list == system.logging_handlers
    assert ls.verbosity == system.logging_verbosity
    assert ls.platform == system.platform
    assert ls.python_version == system.python_version
    assert ls.platform_version == system.version


def test_logging_settings_no_preferences_falls_back_to_home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))  # type: ignore[arg-type]
    user = SimpleNamespace(preferences=None)
    ls = LoggingSettings(user_settings=user)  # type: ignore[arg-type]
    assert "OpenBBUserData" in str(ls.user_logs_directory)
