"""Test the router settings.py module."""
import asyncio
from unittest.mock import Mock

from openbb_core.api.router.user import patch_user_credentials, read_users_settings
from openbb_core.app.model.credentials import Credentials
from openbb_core.app.model.user_settings import UserSettings


def test_read_users_settings():
    """Test read users settings."""
    mock_user_settings = Mock()

    result = asyncio.run(read_users_settings(user_settings=mock_user_settings))

    assert result == mock_user_settings


def test_patch_user_credentials():
    """Test patch user credentials."""
    credentials = Credentials(username="testuser", password="testpass")
    user_settings = UserSettings(credentials=credentials)

    mock_user_service = Mock()

    result = asyncio.run(
        patch_user_credentials(credentials, user_settings, mock_user_service)
    )

    assert result == user_settings
    mock_user_service.user_settings_repository.update.assert_called_once_with(
        user_settings
    )
