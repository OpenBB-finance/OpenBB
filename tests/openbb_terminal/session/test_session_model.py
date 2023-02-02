# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json
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
    with patch(
        "openbb_terminal.session.session_model.Hub.get_session"
    ) as mock_get_session:
        mock_get_session.return_value = TEST_SESSION
        with patch(
            "openbb_terminal.session.session_model.Local.save_session"
        ) as mock_save_session:
            session = session_model.create_session(email, password, save)

    assert session == TEST_SESSION
    mock_get_session.assert_called_once_with(email, password)
    if save and session:
        mock_save_session.assert_called_once_with(session)


@patch("openbb_terminal.session.session_model.Hub.fetch_user_configs")
@patch("openbb_terminal.session.session_model.Local.apply_configs")
@patch("openbb_terminal.session.session_model.User.load_user_info")
@patch("openbb_terminal.session.session_model.User.update_flair")
def test_login_no_response(
    mock_update_flair, mock_load_user_info, mock_apply_configs, mock_fetch_user_configs
):

    mock_fetch_user_configs.return_value = None
    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.NO_RESPONSE

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_not_called()
    mock_load_user_info.assert_not_called()
    mock_update_flair.assert_not_called()


@patch("openbb_terminal.session.session_model.Hub.fetch_user_configs")
@patch("openbb_terminal.session.session_model.Local.apply_configs")
@patch("openbb_terminal.session.session_model.User.load_user_info")
@patch("openbb_terminal.session.session_model.User.update_flair")
def test_login_fail_response(
    mock_update_flair, mock_load_user_info, mock_apply_configs, mock_fetch_user_configs
):

    response = Response()
    response.status_code = 400
    mock_fetch_user_configs.return_value = response
    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.FAILED

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_not_called()
    mock_load_user_info.assert_not_called()
    mock_update_flair.assert_not_called()


@patch("openbb_terminal.session.session_model.Hub.fetch_user_configs")
@patch("openbb_terminal.session.session_model.Local.apply_configs")
@patch("openbb_terminal.session.session_model.User.load_user_info")
@patch("openbb_terminal.session.session_model.User.update_flair")
def test_login_success_response(
    mock_update_flair, mock_load_user_info, mock_apply_configs, mock_fetch_user_configs
):

    response = Response()
    response.status_code = 200
    response._content = json.dumps(TEST_SESSION)  # pylint: disable=protected-access
    mock_fetch_user_configs.return_value = response
    assert session_model.login(TEST_SESSION) == session_model.LoginStatus.SUCCESS

    mock_fetch_user_configs.assert_called_once_with(TEST_SESSION)
    mock_apply_configs.assert_called_once()
    mock_load_user_info.assert_called_once()
    mock_update_flair.assert_called_once()
