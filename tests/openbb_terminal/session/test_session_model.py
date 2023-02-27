# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json

import pytest
from requests import Response

# IMPORTATION INTERNAL
from openbb_terminal.core.session import session_model

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


@pytest.mark.skip("Not working?")
def test_login_no_response(mocker):
    path = "openbb_terminal.core.session.session_model."
    mock_clear_openbb_env_vars = mocker.patch(path + "clear_openbb_env_vars")
    mock_reload_openbb_config_modules = mocker.patch(
        path + "reload_openbb_config_modules"
    )
    mock_fetch_user_configs = mocker.patch(path + "Hub.fetch_user_configs")
    mock_apply_configs = mocker.patch(path + "Local.apply_configs")
    mock_update_flair = mocker.patch(path + "update_flair")

    mock_fetch_user_configs.return_value = None

    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.NO_RESPONSE

    mock_clear_openbb_env_vars.assert_called_once()
    mock_reload_openbb_config_modules.assert_called_once()
    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_not_called()
    mock_update_flair.assert_not_called()


@pytest.mark.skip("Not working?")
def test_login_fail_response(mocker):
    path = "openbb_terminal.core.session.session_model."
    mock_clear_openbb_env_vars = mocker.patch(path + "clear_openbb_env_vars")
    mock_reload_openbb_config_modules = mocker.patch(
        path + "reload_openbb_config_modules"
    )
    mock_fetch_user_configs = mocker.patch(path + "Hub.fetch_user_configs")
    mock_apply_configs = mocker.patch(path + "Local.apply_configs")
    mock_update_flair = mocker.patch(path + "update_flair")

    response = Response()
    response.status_code = 400
    mock_fetch_user_configs.return_value = response

    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.FAILED

    mock_clear_openbb_env_vars.assert_called_once()
    mock_reload_openbb_config_modules.assert_called_once()
    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_not_called()
    mock_update_flair.assert_not_called()


@pytest.mark.skip("Not working?")
def test_login_success_response(mocker):
    path = "openbb_terminal.core.session.session_model."
    mock_clear_openbb_env_vars = mocker.patch(path + "clear_openbb_env_vars")
    mock_reload_openbb_config_modules = mocker.patch(
        path + "reload_openbb_config_modules"
    )
    mock_fetch_user_configs = mocker.patch(path + "Hub.fetch_user_configs")
    mock_apply_configs = mocker.patch(path + "Local.apply_configs")
    mock_update_flair = mocker.patch(path + "update_flair")

    response = Response()
    response.status_code = 200
    response._content = json.dumps(CONFIGS).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    mock_fetch_user_configs.return_value = response

    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.SUCCESS

    mock_clear_openbb_env_vars.assert_called_once()
    mock_reload_openbb_config_modules.assert_called_once()
    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_called_once()
    mock_update_flair.assert_called_once()


@pytest.mark.skip("Not working?")
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
    mock_remove_session_file = mocker.patch(path + "Local.remove_session_file")
    mock_remove_cli_history_file = mocker.patch(path + "Local.remove_cli_history_file")
    mock_reload_openbb_config_modules = mocker.patch(
        path + "reload_openbb_config_modules"
    )
    mock_clear_openbb_env_vars = mocker.patch(path + "clear_openbb_env_vars")
    mock_plt_close = mocker.patch(path + "plt.close")

    auth_header = "Bearer test_token"
    token = "test_token"
    session_model.logout(auth_header, token, guest)

    if not guest:
        mock_delete_session.assert_called_once_with(auth_header, token)
        mock_remove_session_file.assert_called_once()
    mock_clear_openbb_env_vars.assert_called_once()
    mock_reload_openbb_config_modules.assert_called_once()
    mock_remove_cli_history_file.assert_called_once()
    mock_plt_close.assert_called_once()
