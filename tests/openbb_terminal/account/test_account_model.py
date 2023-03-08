# IMPORTATION STANDARD

from pathlib import Path
from unittest.mock import patch

# IMPORTATION THIRDPARTY
from openbb_terminal import (
    config_terminal as cfg,
)
from openbb_terminal.account import account_model
from openbb_terminal.core.config import paths

# IMPORTATION INTERNAL
from openbb_terminal.core.models.credentials_model import CredentialsModel
from openbb_terminal.core.session.current_user import (
    copy_user,
)


def test_get_var_diff():
    class TestObj:  # pylint: disable=too-few-public-methods
        attr_str = "string"
        attr_int = 10
        attr_float = 3.14
        attr_path = Path("/tmp/test")  # noqa: S108
        attr_bool = True

    obj = TestObj()

    # Test string attribute
    result = account_model.get_var_diff(obj, "attr_str", "new string")
    assert result == ("string", "new string")

    # Test int attribute
    result = account_model.get_var_diff(obj, "attr_int", "20")
    assert result == (10, 20)

    # Test float attribute
    result = account_model.get_var_diff(obj, "attr_float", "6.28")
    assert result == (3.14, 6.28)

    # Test path attribute
    result = account_model.get_var_diff(obj, "attr_path", "/tmp/new_test")  # noqa: S108
    assert result == (Path("/tmp/test"), Path("/tmp/new_test"))  # noqa: S108

    # Test bool attribute
    result = account_model.get_var_diff(obj, "attr_bool", "false")
    assert result == (True, False)


def test_get_diff_keys(mocker):
    credentials = CredentialsModel(
        **{
            "API_KEY_ALPHAVANTAGE": "key1",
            "API_KEY_FINANCIALMODELINGPREP": "key2",
            "API_KEY_QUANDL": "key3",
        }
    )
    mock_current_user = copy_user(credentials=credentials)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    new_credentials = {
        "API_KEY_ALPHAVANTAGE": "new_key1",
        "API_KEY_FINANCIALMODELINGPREP": "new_key2",
        "API_KEY_QUANDL": "new_key3",
    }

    diff = account_model.get_diff_keys(new_credentials)
    assert diff == {
        "API_KEY_ALPHAVANTAGE": ("key1", "new_key1"),
        "API_KEY_FINANCIALMODELINGPREP": ("key2", "new_key2"),
        "API_KEY_QUANDL": ("key3", "new_key3"),
    }


def test_get_diff_keys_empty_keys(mocker):
    credentials = CredentialsModel(
        **{
            "API_KEY_ALPHAVANTAGE": "key1",
            "API_KEY_FINANCIALMODELINGPREP": "key2",
            "API_KEY_QUANDL": "key3",
        }
    )
    mock_current_user = copy_user(credentials=credentials)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    new_credentials = {}

    diff = account_model.get_diff_keys(new_credentials)
    assert not diff and isinstance(diff, dict)


def test_get_diff_keys_same_keys(mocker):
    credentials = CredentialsModel(
        **{
            "API_KEY_ALPHAVANTAGE": "key1",
            "API_KEY_FINANCIALMODELINGPREP": "key2",
            "API_KEY_QUANDL": "key3",
        }
    )
    mock_current_user = copy_user(credentials=credentials)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    new_credentials = {
        "API_KEY_ALPHAVANTAGE": "key1",
        "API_KEY_FINANCIALMODELINGPREP": "key2",
        "API_KEY_QUANDL": "key3",
    }

    diff = account_model.get_diff_keys(new_credentials)

    assert not diff and isinstance(diff, dict)


def test_get_diff_keys_new_keys(mocker):
    credentials = CredentialsModel(
        **{
            "API_KEY_ALPHAVANTAGE": "key1",
            "API_KEY_FINANCIALMODELINGPREP": "key2",
        }
    )
    mock_current_user = copy_user(credentials=credentials)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )

    new_credentials = {
        "API_KEY_ALPHAVANTAGE": "key1",
        "API_KEY_FINANCIALMODELINGPREP": "key2",
        "NEW_CREDENTIAL": "new",
    }

    diff = account_model.get_diff_keys(new_credentials)
    assert not diff and isinstance(diff, dict)


def test_get_diff_settings_empty_settings():
    diff = account_model.get_diff_settings({})
    assert not diff and isinstance(diff, dict)


def test_get_diff_settings_no_diff():
    cfg.value = 1
    paths.value = 1
    diff = account_model.get_diff_settings({"value": 1})
    assert not diff and isinstance(diff, dict)


def test_get_diff_settings():
    paths.value = 1
    diff = account_model.get_diff_settings({"PLOT_HEIGHT": 2})
    assert "PLOT_HEIGHT" in diff


def test_get_diff():
    configs = {
        "features_settings": {"setting1": "value1"},
        "features_keys": {"key1": "value1"},
    }
    expected = {
        "features_settings": {"setting1": "value1"},
        "features_keys": {"key1": "value1"},
    }

    with patch(
        "openbb_terminal.account.account_model.get_diff_settings"
    ) as mock_get_diff_settings:
        mock_get_diff_settings.return_value = {"setting1": ("old_value", "value1")}

        with patch(
            "openbb_terminal.account.account_model.get_diff_keys"
        ) as mock_get_diff_keys:
            mock_get_diff_keys.return_value = {"key1": ("old_value", "value1")}

            result = account_model.get_diff(configs)

    assert result == expected


def test_get_diff_no_keys():
    configs = {
        "features_settings": {"setting1": "value1"},
    }
    expected = {
        "features_settings": {"setting1": "value1"},
    }

    with patch(
        "openbb_terminal.account.account_model.get_diff_settings"
    ) as mock_get_diff_settings:
        mock_get_diff_settings.return_value = {"setting1": ("old_value", "value1")}

        with patch(
            "openbb_terminal.account.account_model.get_diff_keys"
        ) as mock_get_diff_keys:
            mock_get_diff_keys.return_value = {}

            result = account_model.get_diff(configs)

    assert result == expected


def test_get_diff_no_settings():
    configs = {
        "features_keys": {"key1": "value1"},
    }
    expected = {
        "features_keys": {"key1": "value1"},
    }

    with patch(
        "openbb_terminal.account.account_model.get_diff_settings"
    ) as mock_get_diff_settings:
        mock_get_diff_settings.return_value = {}

        with patch(
            "openbb_terminal.account.account_model.get_diff_keys"
        ) as mock_get_diff_keys:
            mock_get_diff_keys.return_value = {"key1": ("old_value", "value1")}

            result = account_model.get_diff(configs)

    assert result == expected


def test_get_diff_no_settings_no_keys():
    configs = {}
    expected = {}

    with patch(
        "openbb_terminal.account.account_model.get_diff_settings"
    ) as mock_get_diff_settings:
        mock_get_diff_settings.return_value = {}

        with patch(
            "openbb_terminal.account.account_model.get_diff_keys"
        ) as mock_get_diff_keys:
            mock_get_diff_keys.return_value = {}

            result = account_model.get_diff(configs)

    assert result == expected
