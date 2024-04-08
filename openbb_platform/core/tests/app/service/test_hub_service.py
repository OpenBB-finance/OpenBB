"""Test the hub_service.py module."""

# pylint: disable=W0212
# ruff: noqa: S105 S106


from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.service.hub_service import (
    Credentials,
    HubService,
    HubSession,
    HubUserSettings,
    OpenBBError,
)
from pydantic import SecretStr


@pytest.fixture
def mocker():
    """Fixture for mocker."""
    with patch("openbb_core.app.service.hub_service.HubService") as mock:
        yield mock


def test_connect_with_email_password():
    """Test connect with email and password."""
    mock_hub_session = MagicMock(spec=HubSession)
    with patch(
        "requests.post", return_value=MagicMock(status_code=200, json=lambda: {})
    ), patch.object(
        HubService,
        "_get_session_from_email_password",
        return_value=mock_hub_session,
    ):
        hub_service = HubService()
        result = hub_service.connect(email="test@example.com", password="password")

        assert result == mock_hub_session
        assert hub_service.session == mock_hub_session


def test_connect_with_sdk_token():
    """Test connect with Platform personal access token."""
    mock_hub_session = MagicMock(spec=HubSession)
    with patch(
        "requests.post", return_value=MagicMock(status_code=200, json=lambda: {})
    ), patch.object(
        HubService, "_get_session_from_platform_token", return_value=mock_hub_session
    ):
        hub_service = HubService()
        result = hub_service.connect(pat="pat")

        assert result == mock_hub_session
        assert hub_service.session == mock_hub_session


def test_connect_without_credentials():
    """Test connect without credentials."""
    hub_service = HubService()
    with pytest.raises(
        OpenBBError, match="Please provide 'email' and 'password' or 'pat'"
    ):
        hub_service.connect()


def test_get_session_from_email_password():
    """Test get session from email and password."""

    with patch(
        "openbb_core.app.service.hub_service.post",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "token",
                "token_type": "Bearer",
                "uuid": "uuid",
                "email": "email",
                "username": "username",
                "primary_usage": "primary_usage",
            },
        ),
    ):
        result = HubService()._get_session_from_email_password("email", "password")
        assert isinstance(result, HubSession)


def test_get_session_from_platform_token():
    """Test get session from Platform personal access token."""

    with patch(
        "openbb_core.app.service.hub_service.post",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {
                "access_token": "token",
                "token_type": "Bearer",
                "uuid": "uuid",
                "username": "username",
                "email": "email",
                "primary_usage": "primary_usage",
            },
        ),
    ):
        mock_token = (
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiIsImtpZCI6ImRiMjEyZDdhZj"
            "c2MWI0ZTNlOGNjZGM3OWQ5Zjk4YWM5In0.eyJhY2Nlc3NfdG9rZW4iOiJ0"
            "b2tlbiIsInRva2VuX3R5cGUiOiJCZWFyZXIiLCJ1dWlkIjoidXVpZCIsInV"
            "zZXJuYW1lIjoidXNlcm5hbWUiLCJlbWFpbCI6ImVtYWlsIiwicHJpbWFyeV9"
            "1c2FnZSI6InByaW1hcnlfdXNhZ2UifQ.FAtE8-a1a-313Zoa6dREIxGZOHaW9"
            "-JLZnFzyJ6dlHBZnkjQT2tfaaefxnTdAlSmToQwxGykvuatmI7L0wztPQ"
        )

        result = HubService()._get_session_from_platform_token(mock_token)
        assert isinstance(result, HubSession)


def test_disconnect():
    """Test disconnect."""

    with patch(
        "openbb_core.app.service.hub_service.get",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"success": True},
        ),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        hub_service = HubService(session=mock_hub_session)

        assert hub_service.disconnect() is True
        assert hub_service.session is None


def test_get_user_settings():
    """Test get user settings."""
    with patch(
        "openbb_core.app.service.hub_service.get",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {},
        ),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )

        user_settings = HubService()._get_user_settings(mock_hub_session)
        assert isinstance(user_settings, HubUserSettings)


def test_put_user_settings():
    """Test put user settings."""

    with patch(
        "openbb_core.app.service.hub_service.put",
        return_value=MagicMock(
            status_code=200,
        ),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        mock_user_settings = MagicMock(spec=HubUserSettings)

        assert (
            HubService()._put_user_settings(mock_hub_session, mock_user_settings)
            is True
        )


def test_hub2platform_v4_only():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "fmp_api_key": "abc",
        "polygon_api_key": "def",
        "fred_api_key": "ghi",
    }

    credentials = HubService().hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "abc"
    assert credentials.polygon_api_key.get_secret_value() == "def"
    assert credentials.fred_api_key.get_secret_value() == "ghi"


def test_hub2platform_v3_only():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "API_KEY_FINANCIALMODELINGPREP": "abc",
        "API_POLYGON_KEY": "def",
        "API_FRED_KEY": "ghi",
    }

    credentials = HubService().hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "abc"
    assert credentials.polygon_api_key.get_secret_value() == "def"
    assert credentials.fred_api_key.get_secret_value() == "ghi"


def test_hub2platform_v3v4():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "API_KEY_FINANCIALMODELINGPREP": "abc",
        "fmp_api_key": "other_key",
        "API_POLYGON_KEY": "def",
        "API_FRED_KEY": "ghi",
    }

    credentials = HubService().hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "other_key"
    assert credentials.polygon_api_key.get_secret_value() == "def"
    assert credentials.fred_api_key.get_secret_value() == "ghi"


def test_platform2hub():
    """Test platform2hub."""
    mock_credentials = Credentials(
        fmp_api_key=SecretStr("fmp"),
        polygon_api_key=SecretStr("polygon"),
        fred_api_key=SecretStr("fred"),
    )
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "API_KEY_FINANCIALMODELINGPREP": "abc",
        "fmp_api_key": "other_key",
        "API_POLYGON_KEY": "def",
        "API_FRED_KEY": "ghi",
    }
    mock_hub_service = HubService()
    mock_hub_service._hub_user_settings = mock_user_settings
    user_settings = mock_hub_service.platform2hub(mock_credentials)

    assert isinstance(user_settings, HubUserSettings)
    assert user_settings.features_keys["API_KEY_FINANCIALMODELINGPREP"] == "abc"
    assert user_settings.features_keys["API_POLYGON_KEY"] == "def"
    assert user_settings.features_keys["API_FRED_KEY"] == "ghi"
    assert user_settings.features_keys["fmp_api_key"] == "fmp"
    assert user_settings.features_keys["polygon_api_key"] == "polygon"
    assert user_settings.features_keys["fred_api_key"] == "fred"
