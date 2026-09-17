"""Test the system_service.py module."""

import json

import pytest

from openbb_core.app.service.system_service import SystemService


@pytest.fixture
def system_service():
    """Fixture for system service."""
    return SystemService()


def test_system_service_init(system_service):
    """Test system service init."""
    assert system_service


def test_read_from_file(system_service):
    """Test read default system settings."""
    system_settings = system_service._read_from_file()

    assert system_settings


def test_write_to_file(system_service, tmp_path):
    """Test write default system settings to a temp path (NOT the real one)."""
    system_settings = system_service._read_from_file()
    target = tmp_path / "system_settings.json"
    system_service.write_to_file(system_settings=system_settings, path=target)

    assert target.exists()
    assert target.read_text().strip()


def test_system_settings(system_service):
    """Test system settings."""
    system_settings = system_service.system_settings

    assert system_settings


def test_system_settings_setter(system_service):
    """Test system settings setter."""
    system_settings = system_service.system_settings

    system_service.system_settings = system_settings

    assert system_service.system_settings == system_settings


def test_refresh_system_settings(system_service):
    """Test refresh system settings."""
    system_settings = system_service.refresh_system_settings()

    assert system_settings


def test_compare_hash_with_explicit_hash():
    import hashlib

    h = hashlib.sha256(b"hello").hexdigest()
    assert SystemService._compare_hash("hello", existing_hash=h) is True
    assert SystemService._compare_hash("hello", existing_hash="0" * 64) is False


def test_compare_hash_default_does_not_match_arbitrary_string():
    assert SystemService._compare_hash("definitely-not-the-pro-secret") is False


def test_read_from_file_filters_disallowed_fields(tmp_path):
    path = tmp_path / "system_settings.json"
    path.write_text(
        json.dumps(
            {
                "test_mode": True,
                "headless": True,
                "this_is_not_allowed": "drop me",
            }
        )
    )
    settings = SystemService._read_from_file(path=path)
    assert settings.test_mode is True
    assert settings.headless is True
    assert not hasattr(settings, "this_is_not_allowed")


def test_read_from_file_logging_sub_app_pro_promotion(tmp_path, monkeypatch):
    path = tmp_path / "system_settings.json"
    path.write_text(json.dumps({"logging_sub_app": "some-secret"}))
    monkeypatch.setattr(
        SystemService, "_compare_hash", classmethod(lambda cls, val: True)
    )
    settings = SystemService._read_from_file(path=path)
    assert settings.logging_sub_app == "pro"


def test_read_from_file_logging_sub_app_invalid_dropped(tmp_path):
    path = tmp_path / "system_settings.json"
    path.write_text(json.dumps({"logging_sub_app": "definitely-not-pro"}))
    settings = SystemService._read_from_file(path=path)
    assert settings.logging_sub_app != "definitely-not-pro"


def test_read_from_file_no_file_uses_kwargs(tmp_path):
    path = tmp_path / "missing.json"
    settings = SystemService._read_from_file(path=path, headless=True)
    assert settings.headless is True
