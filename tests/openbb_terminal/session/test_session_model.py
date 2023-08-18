# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json

import pytest
from requests import Response

from openbb_terminal.core.config.paths import HIST_FILE_PATH, SESSION_FILE_PATH

# IMPORTATION INTERNAL
from openbb_terminal.core.session import session_model
from openbb_terminal.core.session.current_user import get_current_user

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}

CONFIGS = {
    "features_settings": {
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
def test_create_session(mocker, email, password, save):
    path = "openbb_terminal.core.session.session_model."
    mock_get_session = mocker.patch(path + "Hub.get_session")
    mock_save_session = mocker.patch(path + "Local.save_session")

    mock_get_session.return_value = TEST_SESSION
    session = session_model.create_session(email, password, save)

    assert session == TEST_SESSION

    mock_get_session.assert_called_once_with(email, password)
    if save and session:
        mock_save_session.assert_called_once_with(session)


def test_login_no_response(mocker):
    path = "openbb_terminal.core.session.session_model."
    mock_fetch_user_configs = mocker.patch(path + "Hub.fetch_user_configs")
    mock_apply_configs = mocker.patch(path + "Local.apply_configs")
    mock_update_flair = mocker.patch(path + "Local.update_flair")
    mock_get_updated_hub_sources = mocker.patch(
        path + "get_updated_hub_sources", return_value={}
    )

    mock_fetch_user_configs.return_value = None

    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.NO_RESPONSE

    mock_fetch_user_configs.assert_called_once_with(
        TEST_SESSION, "https://payments.openbb.co/"
    )
    mock_apply_configs.assert_not_called()
    mock_update_flair.assert_not_called()
    mock_get_updated_hub_sources.assert_not_called()


def test_login_fail_response(mocker):
    path = "openbb_terminal.core.session.session_model."
    mock_fetch_user_configs = mocker.patch(path + "Hub.fetch_user_configs")
    mock_apply_configs = mocker.patch(path + "Local.apply_configs")
    mock_update_flair = mocker.patch(path + "Local.update_flair")
    mock_get_updated_hub_sources = mocker.patch(
        path + "get_updated_hub_sources", return_value={}
    )

    response = Response()
    response.status_code = 400
    mock_fetch_user_configs.return_value = response

    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.FAILED

    mock_fetch_user_configs.assert_called_once_with(
        TEST_SESSION, "https://payments.openbb.co/"
    )
    mock_apply_configs.assert_not_called()
    mock_update_flair.assert_not_called()
    mock_get_updated_hub_sources.assert_not_called()


def test_login_success_response(mocker):
    path = "openbb_terminal.core.session.session_model."
    mock_fetch_user_configs = mocker.patch(path + "Hub.fetch_user_configs")
    mock_apply_configs = mocker.patch(path + "Local.apply_configs")
    mock_update_flair = mocker.patch(path + "Local.update_flair")
    mocker.patch(path + "download_and_save_routines")
    mocker.patch(path + "run_thread")

    response = Response()
    response.status_code = 200
    response._content = json.dumps(CONFIGS).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    mock_fetch_user_configs.return_value = response

    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.SUCCESS

    mock_fetch_user_configs.assert_called_once_with(
        TEST_SESSION, "https://payments.openbb.co/"
    )
    mock_apply_configs.assert_called_once()
    mock_update_flair.assert_called_once()


@pytest.mark.parametrize(
    "guest",
    [
        False,
        True,
    ],
)
def test_logout_user(mocker, guest):
    path = "openbb_terminal.core.session.session_model."
    mock_delete_session = mocker.patch(path + "Hub.delete_session")
    mock_remove = mocker.patch(path + "Local.remove")
    mock_remove_log_handlers = mocker.patch(path + "remove_log_handlers")
    mock_set_default_user = mocker.patch(path + "set_default_user")
    mock_setup_logging = mocker.patch(path + "setup_logging")
    mock_plt_close = mocker.patch(path + "plt.close")

    auth_header = "Bearer test_token"
    token = "test_token"
    base_url = "https://payments.openbb.co/"
    session_model.logout(auth_header, token)

    if not guest:
        mock_delete_session.assert_called_once_with(
            auth_header, token, base_url=base_url
        )
        assert mock_remove.call_args_list[0] == mocker.call(SESSION_FILE_PATH)
        assert mock_remove.call_args_list[1] == mocker.call(HIST_FILE_PATH)
        assert mock_remove.call_args_list[2] == mocker.call(
            get_current_user().preferences.USER_ROUTINES_DIRECTORY / "hub"
        )
    mock_remove_log_handlers.assert_called_once()
    mock_set_default_user.assert_called_once()
    mock_setup_logging.assert_called_once()
    mock_plt_close.assert_called_once()
