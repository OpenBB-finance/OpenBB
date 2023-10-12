"""Test the user module."""
# ruff: noqa: S105 S106

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi.security import HTTPBasicCredentials
from openbb_core.api.auth.user import (
    UserSettings,
    authenticate_user,
    get_user_service,
    get_user_settings,
)


@pytest.mark.parametrize(
    "error, correct, received",
    [
        (True, (None, None), ("user", "pass")),
        (True, ("user", "pass"), ("", "")),
        (True, ("user", "pass"), ("random", "pass")),
        (True, ("user", "pass"), ("user", "random")),
        (False, ("", ""), ("", "")),
        (False, ("user", "pass"), ("user", "pass")),
    ],
)
@patch("openbb_core.api.auth.user.Env")
@patch("openbb_core.api.auth.user.HTTPBasicCredentials")
def test_authenticate_user(mock_credentials, mock_env, error, correct, received):
    """Test authenticate user."""
    mock_env.return_value.API_USERNAME = correct[0]
    mock_env.return_value.API_PASSWORD = correct[1]
    mock_credentials = HTTPBasicCredentials(username=received[0], password=received[1])

    if error:
        with pytest.raises(Exception):
            result = asyncio.run(authenticate_user(mock_credentials))
    else:
        result = asyncio.run(authenticate_user(mock_credentials))
        assert result is None


@patch("openbb_core.api.auth.user.UserService")
def test_get_user_service(mock_user_service):
    """Test get_user_service."""

    mock_user_service.return_value = MagicMock()

    asyncio.run(get_user_service())

    mock_user_service.assert_called_once_with()


@patch("openbb_core.api.auth.user.UserService")
def test_get_user_settings_(mock_user_service):
    """Test get_user."""
    mock_user_settings = MagicMock(spec=UserSettings, profile=MagicMock(active=True))
    mock_user_service.default_user_settings = mock_user_settings
    mock_user_service.return_value = mock_user_service
    result = asyncio.run(get_user_settings(MagicMock(), mock_user_service))

    assert result == mock_user_settings
