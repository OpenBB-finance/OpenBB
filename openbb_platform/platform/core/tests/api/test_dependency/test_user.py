"""Test the user module."""
import asyncio
from unittest.mock import MagicMock, patch

from openbb_core.api.dependency.user import (
    UserSettings,
    get_user_service,
    get_user_settings,
)

# ruff: noqa: S105 S106


@patch("openbb_core.api.dependency.user.UserService")
def test_get_user_service(mock_user_service):
    """Test get_user_service."""

    mock_user_service.return_value = MagicMock()

    asyncio.run(get_user_service())

    mock_user_service.assert_called_once_with()


@patch("openbb_core.api.dependency.user.Env")
@patch("openbb_core.api.dependency.user.HTTPBasicCredentials")
@patch("openbb_core.api.dependency.user.UserService")
def test_get_user_settings_(mock_user_service, mock_credentials, mock_env):
    """Test get_user."""
    mock_env.return_value = MagicMock(
        API_USERNAME="some_username", API_PASSWORD="some_password"
    )

    mock_credentials.username = "some_username"
    mock_credentials.password = "some_password"

    mock_user_settings = MagicMock(spec=UserSettings, profile=MagicMock(active=True))
    mock_user_service.default_user_settings = mock_user_settings
    mock_user_service.return_value = mock_user_service
    result = asyncio.run(get_user_settings(mock_credentials, mock_user_service))

    assert result == mock_user_settings
