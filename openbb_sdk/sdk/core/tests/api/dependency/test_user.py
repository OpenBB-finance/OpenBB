"""Test the user module."""
import asyncio
from unittest.mock import MagicMock, patch

from openbb_core.api.dependency.user import (
    AccessToken,
    UserSettings,
    authenticate_user,
    create_access_token,
    create_jwt_token,
    get_password_hash,
    get_user,
    get_user_service,
    verify_password,
)


def test_password_functions():
    """Test password functions."""
    password = "my_password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)


@patch("openbb_core.api.dependency.user.UserService")
def test_authenticate_user(mock_user_service):
    """Test authenticate_user."""
    mock_user_settings = MagicMock(
        spec=UserSettings, profile=MagicMock(password_hash="hashed_password")
    )
    mock_user_service.user_settings_repository.read_by_profile.return_value = (
        mock_user_settings
    )
    with patch("openbb_core.api.dependency.user.verify_password", return_value=True):
        result = authenticate_user("password", "username", mock_user_service)

    assert result == mock_user_settings


def test_create_access_token():
    """Test create_access_token."""
    sub = "subject"
    access_token = create_access_token(sub)

    assert isinstance(access_token, AccessToken)
    assert access_token.sub == sub


def test_create_jwt_token():
    """Test create_jwt_token."""
    mock_access_token = MagicMock(
        spec=AccessToken, dict=lambda: {"sub": "subject", "exp": 12345}
    )
    jwt_token = create_jwt_token(mock_access_token)

    assert isinstance(jwt_token, str)


@patch("openbb_core.api.dependency.user.UserService")
def test_get_user_service(mock_user_service):
    """Test get_user_service."""
    with patch("openbb_core.api.dependency.user.__user_service", new=None):
        asyncio.run(get_user_service())

    mock_user_service.assert_called_once_with()


@patch("openbb_core.api.dependency.user.jwt.decode")
@patch("openbb_core.api.dependency.user.UserService")
def test_get_user(mock_user_service, mock_decode):
    """Test get_user."""
    mock_decode.return_value = {"sub": "user_id"}
    mock_user_settings = MagicMock(spec=UserSettings, profile=MagicMock(active=True))
    mock_user_service.user_settings_repository.read.return_value = mock_user_settings
    with patch("openbb_core.api.dependency.user.__user_service", new=mock_user_service):
        result = asyncio.run(get_user("jwt_token", mock_user_service))

    assert result == mock_user_settings
