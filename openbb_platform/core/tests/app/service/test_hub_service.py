"""Test the hub_service.py module."""

# pylint: disable=W0212
# ruff: noqa: S105 S106


from pathlib import Path
from time import time
from unittest.mock import MagicMock, patch

import pytest
from jwt import encode
from openbb_core.app.model.defaults import Defaults
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


def test_v3tov4_map():
    """Test v3 to v4 map."""

    v3_keys = {
        "databento": "API_DATABENTO_KEY",
        "alpha_vantage": "API_KEY_ALPHAVANTAGE",
        "fmp": "API_KEY_FINANCIALMODELINGPREP",
        "nasdaq": "API_KEY_QUANDL",
        "polygon": "API_POLYGON_KEY",
        "fred": "API_FRED_KEY",
        "news_api": "API_NEWS_TOKEN",
        "biztoc": "API_BIZTOC_TOKEN",
        "cmc": "API_CMC_KEY",
        "finnhub": "API_FINNHUB_KEY",
        "whale_alert": "API_WHALE_ALERT_KEY",
        "glassnode": "API_GLASSNODE_KEY",
        "coinglass": "API_COINGLASS_KEY",
        "ethplorer": "API_ETHPLORER_KEY",
        "cryptopanic": "API_CRYPTO_PANIC_KEY",
        "crypto_panic": "API_CRYPTO_PANIC_KEY",  # If dev choses to use this name
        "bitquery": "API_BITQUERY_KEY",
        "smartstake": ["API_SMARTSTAKE_KEY", "API_SMARTSTAKE_TOKEN"],
        "messari": "API_MESSARI_KEY",
        "shroom": "API_SHROOM_KEY",
        "santiment": "API_SANTIMENT_KEY",
        "eodhd": "API_EODHD_KEY",
        "tokenterminal": "API_TOKEN_TERMINAL_KEY",
        "token_terminal": "API_TOKEN_TERMINAL_KEY",  # If dev choses to use this name
        "intrinio": "API_INTRINIO_KEY",
        "github": "API_GITHUB_KEY",
        "reddit": [
            "API_REDDIT_CLIENT_ID",
            "API_REDDIT_CLIENT_SECRET",
            "API_REDDIT_USERNAME",
            "API_REDDIT_USER_AGENT",
            "API_REDDIT_PASSWORD",
        ],
        "companies_house": "API_COMPANIESHOUSE_KEY",
        "companieshouse": "API_COMPANIESHOUSE_KEY",  # If dev choses to use this name
        "dappradar": "API_DAPPRADAR_KEY",
        "nixtla": "API_KEY_NIXTLA",
    }

    providers = sorted(
        [
            p.stem
            for p in Path("openbb_platform", "providers").glob("*")
            if p.is_dir() and p.name not in ("__pycache__", "tests")
        ]
    )

    for provider in providers:
        if provider in v3_keys:
            keys = v3_keys[provider]
            keys_list = keys if isinstance(keys, list) else [keys]
            for k in keys_list:
                assert k.lower() in HubService.V3TOV4


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
    mock_hub_session = MagicMock(spec=HubSession)
    with patch(
        "requests.post",
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
    ), patch.object(
        HubService,
        "_get_session_from_email_password",
        return_value=mock_hub_session,
    ):
        hub_service = HubService()
        result = hub_service._get_session_from_email_password("email", "password")
        assert isinstance(result, HubSession)


def test_get_session_from_platform_token():
    """Test get session from Platform personal access token."""
    mock_hub_session = MagicMock(spec=HubSession)
    with patch(
        "requests.post",
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
    ), patch.object(
        HubService,
        "_get_session_from_platform_token",
        return_value=mock_hub_session,
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
        "requests.get",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {"success": True},
        ),
    ), patch.object(
        HubService,
        "_post_logout",
        return_value=True,
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        hub_service = HubService(mock_hub_session)

        assert hub_service.disconnect() is True
        assert hub_service.session is None


def test_get_user_settings():
    """Test get user settings."""
    with patch(
        "requests.get",
        return_value=MagicMock(
            status_code=200,
            json=lambda: {},
        ),
    ), patch.object(
        HubService,
        "_get_user_settings",
        return_value=MagicMock(spec=HubUserSettings),
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        hub_service = HubService(mock_hub_session)
        user_settings = hub_service._get_user_settings()
        assert isinstance(user_settings, HubUserSettings)


def test_put_user_settings():
    """Test put user settings."""

    with patch(
        "requests.put",
        return_value=MagicMock(
            status_code=200,
        ),
    ), patch.object(
        HubService,
        "_put_user_settings",
        return_value=True,
    ):
        mock_hub_session = MagicMock(
            spec=HubSession, access_token=SecretStr("token"), token_type="Bearer"
        )
        mock_user_settings = MagicMock(spec=HubUserSettings)

        hub_service = HubService(mock_hub_session)
        assert (
            hub_service._put_user_settings(mock_hub_session, mock_user_settings) is True
        )


def test_hub2platform_v4_only():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "fmp_api_key": "abc",
        "polygon_api_key": "def",
        "fred_api_key": "ghi",
    }
    mock_user_settings.features_settings = {}

    credentials, _ = HubService().hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "abc"
    assert credentials.polygon_api_key.get_secret_value() == "def"
    assert credentials.fred_api_key.get_secret_value() == "ghi"


def test_hub2platform_v3_only():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "api_key_financialmodelingprep": "abc",
        "api_polygon_key": "def",
        "api_fred_key": "ghi",
    }
    mock_user_settings.features_settings = {}

    credentials, _ = HubService().hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "abc"
    assert credentials.polygon_api_key.get_secret_value() == "def"
    assert credentials.fred_api_key.get_secret_value() == "ghi"


def test_hub2platform_v3v4():
    """Test hub2platform."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {
        "api_key_financialmodelingprep": "abc",
        "fmp_api_key": "other_key",
        "api_polygon_key": "def",
        "api_fred_key": "ghi",
    }
    mock_user_settings.features_settings = {}

    credentials, _ = HubService().hub2platform(mock_user_settings)
    assert isinstance(credentials, Credentials)
    assert credentials.fmp_api_key.get_secret_value() == "other_key"
    assert credentials.polygon_api_key.get_secret_value() == "def"
    assert credentials.fred_api_key.get_secret_value() == "ghi"


def test_platform2hub():
    """Test platform2hub."""
    mock_user_settings = MagicMock(spec=HubUserSettings)
    mock_user_settings.features_keys = {  # Received from Hub
        "api_key_financialmodelingprep": "abc",
        "fmp_api_key": "other_key",
        "api_fred_key": "ghi",
    }
    mock_user_settings.features_settings = {}
    mock_hub_service = HubService()
    mock_hub_service._hub_user_settings = mock_user_settings
    mock_credentials = Credentials(  # Current credentials
        fmp_api_key=SecretStr("fmp"),
        polygon_api_key=SecretStr("polygon"),
        fred_api_key=SecretStr("fred"),
        benzinga_api_key=SecretStr("benzinga"),
        some_api_key=SecretStr("some"),
    )
    mock_defaults = Defaults()
    user_settings = mock_hub_service.platform2hub(mock_credentials, mock_defaults)

    assert isinstance(user_settings, HubUserSettings)
    assert user_settings.features_keys["api_key_financialmodelingprep"] == "fmp"
    assert user_settings.features_keys["fmp_api_key"] == "other_key"
    assert user_settings.features_keys["polygon_api_key"] == "polygon"
    assert user_settings.features_keys["api_fred_key"] == "fred"
    assert user_settings.features_keys["benzinga_api_key"] == "benzinga"
    assert "some_api_key" not in user_settings.features_keys
    assert "defaults" in user_settings.features_settings


@pytest.mark.parametrize(
    "offset, message",
    [
        # valid
        (
            100,
            None,
        ),
        # expired
        (
            0,
            "Platform personal access token expired.",
        ),
        # invalid
        (None, "Failed to decode Platform token."),
    ],
)
def test__check_token_expiration(offset, message):
    """Test check token expiration function."""

    token = (
        encode(
            {"some": "payload", "exp": int(time()) + offset},
            "secret",
            algorithm="HS256",
        )
        if offset is not None
        else "invalid_token"
    )

    if message:
        with pytest.raises(OpenBBError, match=message):
            HubService._check_token_expiration(token)
    else:
        HubService._check_token_expiration(token)
