"""Test static app factory."""
# pylint: disable=redefined-outer-name

import pytest
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.static.account import Account
from openbb_core.app.static.app_factory import create_app
from openbb_core.app.static.coverage import Coverage


@pytest.fixture(scope="module")
def app_factory():
    """Return app factory."""
    return create_app()


def test_app_factory_init(app_factory):
    """Test app factory init."""
    assert app_factory


def test_app_system_settings(app_factory):
    """Test app system settings."""
    system_settings = app_factory.system
    assert system_settings
    assert isinstance(system_settings, SystemSettings)


def test_app_user_settings(app_factory):
    """Test app user settings."""
    user_settings = app_factory.user
    assert user_settings
    assert isinstance(user_settings, UserSettings)


def test_app_account(app_factory):
    """Test app account."""
    account = app_factory.account
    assert account
    assert isinstance(account, Account)


def test_app_coverage(app_factory):
    """Test app coverage."""
    coverage = app_factory.coverage
    assert coverage
    assert isinstance(coverage, Coverage)
