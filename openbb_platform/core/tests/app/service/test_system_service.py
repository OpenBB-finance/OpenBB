"""Test the system_service.py module."""
# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.service.system_service import SystemService


@pytest.fixture
def system_service():
    """Fixture for system service."""
    return SystemService()


def test_system_service_init(system_service):
    """Test system service init."""
    assert system_service


def test_read_default_system_settings(system_service):
    """Test read default system settings."""
    system_settings = system_service._read_default_system_settings()

    assert system_settings


def test_write_default_system_settings(system_service):
    """Test write default system settings."""
    system_settings = system_service._read_default_system_settings()
    system_service.write_default_system_settings(system_settings=system_settings)

    assert system_service


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
