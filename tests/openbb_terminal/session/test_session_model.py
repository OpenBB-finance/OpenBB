# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json
import os
from unittest.mock import patch

import pytest
from requests import Response

# IMPORTATION INTERNAL
from openbb_terminal.session import session_model

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}

CONFIGS = {
    "features_settings": {
        "USE_WATERMARK": "False",
        "TIMEZONE": "Europe/London",
        "PLOT_DPI": "95",
        "PLOT_HEIGHT_PERCENTAGE": "50.5",
        "USER_DATA_DIRECTORY": "some/path/to/user/data",
    },
    "features_keys": {
        "API_KEY_ALPHAVANTAGE": "test_av",
        "API_FRED_KEY": "test_fred",
    },
}


@pytest.mark.parametrize(
    "email, password, save",
    [
        (
            "test_email",
            "test_pass",
            False,
        ),
        (
            "test_email",
            "test_pass",
            True,
        ),
    ],
)
def test_create_session(email, password, save):
    path = "openbb_terminal.session.session_model."
    with (
        patch(path + "Hub.get_session") as mock_get_session,
        patch(path + "Local.save_session") as mock_save_session,
    ):
        mock_get_session.return_value = TEST_SESSION
        session = session_model.create_session(email, password, save)

    assert session == TEST_SESSION

    mock_get_session.assert_called_once_with(email, password)
    if save and session:
        mock_save_session.assert_called_once_with(session)


def test_login_no_response():
    path = "openbb_terminal.session.session_model."
    with (
        patch(path + "Hub.fetch_user_configs") as mock_fetch_user_configs,
        patch(path + "Local.apply_configs") as mock_apply_configs,
        patch(path + "User.load_user_info") as mock_load_user_info,
        patch(path + "User.update_flair") as mock_update_flair,
    ):
        mock_fetch_user_configs.return_value = None

        assert (
            session_model.login(TEST_SESSION) == session_model.LoginStatus.NO_RESPONSE
        )

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_not_called()
    mock_load_user_info.assert_not_called()
    mock_update_flair.assert_not_called()


def test_login_fail_response():
    path = "openbb_terminal.session.session_model."
    with (
        patch(path + "Hub.fetch_user_configs") as mock_fetch_user_configs,
        patch(path + "Local.apply_configs") as mock_apply_configs,
        patch(path + "User.load_user_info") as mock_load_user_info,
        patch(path + "User.update_flair") as mock_update_flair,
    ):
        response = Response()
        response.status_code = 400
        mock_fetch_user_configs.return_value = response

        assert session_model.login(TEST_SESSION) == session_model.LoginStatus.FAILED

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_not_called()
    mock_load_user_info.assert_not_called()
    mock_update_flair.assert_not_called()


def test_login_success_response():
    path = "openbb_terminal.session.session_model."
    with (
        patch(path + "Hub.fetch_user_configs") as mock_fetch_user_configs,
        patch(path + "Local.apply_configs") as mock_apply_configs,
        patch(path + "User.load_user_info") as mock_load_user_info,
        patch(path + "User.update_flair") as mock_update_flair,
    ):
        response = Response()
        response.status_code = 200
        response._content = json.dumps(  # pylint: disable=protected-access
            CONFIGS
        ).encode("utf-8")
        mock_fetch_user_configs.return_value = response

        assert session_model.login(TEST_SESSION) == session_model.LoginStatus.SUCCESS

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_called_once()
    mock_load_user_info.assert_called_once()
    mock_update_flair.assert_called_once()


@pytest.mark.parametrize(
    "guest",
    [
        False,
        True,
    ],
)
def test_logout_user(guest):
    path = "openbb_terminal.session.session_model."
    with (
        patch(path + "Hub.delete_session") as mock_delete_session,
        patch(path + "Local.remove_session_file") as mock_remove_session_file,
        patch(path + "Local.remove_cli_history_file") as mock_remove_cli_history_file,
        patch(path + "reload_openbb_modules") as mock_reload_openbb_modules,
        patch(path + "clear_openbb_env_vars") as mock_clear_openbb_env_vars,
        patch(path + "User.clear") as mock_clear_user,
        patch(path + "plt.close") as mock_plt_close,
    ):
        auth_header = "Bearer test_token"
        token = "test_token"
        session_model.logout(auth_header, token, guest)

    if not guest:
        mock_delete_session.assert_called_once_with(auth_header, token)
    mock_clear_user.assert_called_once()
    mock_clear_openbb_env_vars.assert_called_once()
    mock_reload_openbb_modules.assert_called_once()
    mock_remove_session_file.assert_called_once()
    mock_remove_cli_history_file.assert_called_once()
    mock_plt_close.assert_called_once()


def test_clear_openbb_env_vars():
    mock_env = {"OPENBB_TEST": "test", "OPENBB_TEST2": "test2", "TEST": "test"}
    with patch.dict("openbb_terminal.session.session_model.os.environ", mock_env):
        session_model.clear_openbb_env_vars()

        assert "OPENBB_TEST" not in os.environ
        assert "OPENBB_TEST2" not in os.environ
        assert "TEST" in os.environ


def test_reload_openbb_modules():
    with patch("openbb_terminal.session.session_model.importlib.reload") as mock_reload:
        session_model.reload_openbb_modules()

    mock_reload.assert_called()
