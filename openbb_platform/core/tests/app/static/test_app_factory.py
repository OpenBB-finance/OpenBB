"""Test static app factory."""

# pylint: disable=redefined-outer-name

from unittest.mock import PropertyMock, patch

import pytest
from openbb_core.app.model.hub.hub_session import HubSession
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.static.account import Account
from openbb_core.app.static.app_factory import create_app
from openbb_core.app.static.coverage import Coverage
from pydantic import SecretStr


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


# flake8: noqa: S106 # pylint: disable=W0212
@patch("openbb_core.app.static.account.HubService", autospec=True)
def test_app_account_login(mock_hub_service, app_factory):
    """Test app account login."""
    mock_hub_service.return_value.pull.return_value = UserSettings()
    mock_hub_service.return_value.connect.return_value = None

    # Mock the session object
    mock_session = HubSession(
        access_token=SecretStr("mock_token"),
        token_type="bearer",
        user_uuid="mock_user_uuid",
        email="test@example.com",
        primary_usage="mock_usage",
    )
    # We need to mock the _session attribute and session property on the HubService instance
    mock_hub_service.return_value._session = mock_session
    type(mock_hub_service.return_value).session = PropertyMock(
        return_value=mock_session
    )

    # Get the account object from the app factory
    account = app_factory.account
    assert account
    assert hasattr(account, "login")
    assert callable(account.login)

    # Call the login method
    account.login(email="test@example.com", password="password", remember_me=True)

    # Assert that the hub_session is set in the user settings
    assert app_factory.user.profile.hub_session is not None
    assert (
        app_factory.user.profile.hub_session.access_token.get_secret_value()
        == "mock_token"
    )

    # Assert that the HubService was called correctly
    mock_hub_service.return_value.connect.assert_called_once_with(
        "test@example.com", "password", None
    )
    mock_hub_service.return_value.pull.assert_called_once()

    # Test logout
    with patch("openbb_core.app.static.account.Path.unlink") as mock_unlink:
        account.logout()
        mock_unlink.assert_called_once()


def test_app_coverage(app_factory):
    """Test app coverage."""
    coverage = app_factory.coverage
    assert coverage
    assert isinstance(coverage, Coverage)


def test_app_reference(app_factory):
    """Test app reference."""
    reference = app_factory.reference
    assert reference
    assert isinstance(reference, dict)
