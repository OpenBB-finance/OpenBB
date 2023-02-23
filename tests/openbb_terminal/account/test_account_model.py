from pathlib import Path
from unittest.mock import patch

from openbb_terminal import (
    config_plot as cfg_plot,
    config_terminal as cfg,
    feature_flags as obbff,
)
from openbb_terminal.account import account_model
from openbb_terminal.core.config import paths
from openbb_terminal.core.models.user_credentials import CredentialsModel
from openbb_terminal.core.models.user_model import UserModel
from openbb_terminal.session.user import get_current_user


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
    a = "API_KEY_ALPHAVANTAGE"
    b = "API_KEY_FINANCIALMODELINGPREP"
    c = "API_KEY_QUANDL"

    old_credentials = CredentialsModel(
        **{
            a: "key1",
            b: "key2",
            c: "key3",
        }
    )
    test_user = UserModel(credentials=old_credentials)

    new_credentials = {
        a: "new_key1",
        b: "new_key2",
        c: "new_key3",
    }

    mocker.patch(
        target="openbb_terminal.account.account_model.get_current_user",
        return_value=test_user,
    )

    diff = account_model.get_diff_keys(new_credentials)
    assert diff == {
        a: ("key1", "new_key1"),
        b: ("key2", "new_key2"),
        c: ("key3", "new_key3"),
    }


def test_get_diff_keys_empty_keys(mocker):
    a = "API_KEY_ALPHAVANTAGE"
    b = "API_KEY_FINANCIALMODELINGPREP"
    c = "API_KEY_QUANDL"

    old_credentials = CredentialsModel(
        **{
            a: "key1",
            b: "key2",
            c: "key3",
        }
    )
    test_user = UserModel(credentials=old_credentials)

    new_credentials = {}

    mocker.patch(
        target="openbb_terminal.account.account_model.get_current_user",
        return_value=test_user,
    )

    diff = account_model.get_diff_keys(new_credentials)
    assert not diff and isinstance(diff, dict)


def test_get_diff_keys_same_keys(mocker):
    a = "API_KEY_ALPHAVANTAGE"
    b = "API_KEY_FINANCIALMODELINGPREP"
    c = "API_KEY_QUANDL"

    old_credentials = CredentialsModel(
        **{
            a: "key1",
            b: "key2",
            c: "key3",
        }
    )
    test_user = UserModel(credentials=old_credentials)

    new_credentials = {
        a: "key1",
        b: "key2",
        c: "key3",
    }

    mocker.patch(
        target="openbb_terminal.account.account_model.get_current_user",
        return_value=test_user,
    )

    diff = account_model.get_diff_keys(new_credentials)
    assert not diff and isinstance(diff, dict)


def test_get_diff_keys_new_keys(mocker):
    a = "API_KEY_ALPHAVANTAGE"
    b = "API_KEY_FINANCIALMODELINGPREP"

    old_credentials = CredentialsModel(
        **{
            a: "key1",
            b: "key2",
        }
    )
    test_user = UserModel(credentials=old_credentials)

    new_credentials = {
        a: "key1",
        b: "key2",
        "NEW_CREDENTIAL": "new",
    }

    mocker.patch(
        target="openbb_terminal.account.account_model.get_current_user",
        return_value=test_user,
    )

    diff = account_model.get_diff_keys(new_credentials)
    assert not diff and isinstance(diff, dict)


def test_get_diff_settings_empty_settings():
    diff = account_model.get_diff_settings({})
    assert not diff and isinstance(diff, dict)


def test_get_diff_settings_no_diff():
    obbff.value = 1
    cfg.value = 1
    cfg_plot.value = 1
    paths.value = 1
    diff = account_model.get_diff_settings({"value": 1})
    assert not diff and isinstance(diff, dict)


def test_get_diff_settings_obbff_diff():
    obbff.value = 1
    diff = account_model.get_diff_settings({"value": 2})
    assert diff == {"value": (1, 2)}


def test_get_diff_settings_cfg_diff():
    cfg.value = 1
    diff = account_model.get_diff_settings({"value": 2})
    assert diff == {"value": (1, 2)}


def test_get_diff_settings_cfg_plot_diff():
    cfg_plot.value = 1
    diff = account_model.get_diff_settings({"value": 2})
    assert diff == {"value": (1, 2)}


def test_get_diff_settings_paths_diff():
    paths.value = 1
    diff = account_model.get_diff_settings({"value": 2})
    assert diff == {"value": (1, 2)}


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
