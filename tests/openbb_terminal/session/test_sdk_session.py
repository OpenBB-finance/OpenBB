# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from unittest.mock import patch

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    SourcesModel,
    UserModel,
)
from openbb_terminal.core.session import sdk_session
from openbb_terminal.core.session.session_model import LoginStatus

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


@pytest.fixture(name="test_user")
def fixture_test_user():
    return UserModel(
        credentials=CredentialsModel(),
        preferences=PreferencesModel(),
        profile=ProfileModel(),
        sources=SourcesModel(),
    )


@pytest.mark.parametrize(
    "email, password, token, save",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
        ),
    ],
)
def test_get_session(email: str, password: str, token: str, save: bool):
    path = "openbb_terminal.core.session.sdk_session."
    with patch(path + "session_model.create_session") as mock_create_session:
        mock_create_session.return_value = TEST_SESSION

        sdk_session.get_session(email=email, password=password, token=token, save=save)
        mock_create_session.assert_called_once_with(email, password, save)


@pytest.mark.parametrize(
    "email, password, token, save",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
        ),
    ],
)
def test_get_session_from_token(email: str, password: str, token: str, save: bool):
    path = "openbb_terminal.core.session.sdk_session."
    with patch(
        path + "session_model.create_session_from_token"
    ) as mock_create_session_from_token:
        mock_create_session_from_token.return_value = TEST_SESSION

        sdk_session.get_session(email=email, password=password, token=token, save=save)
        mock_create_session_from_token.assert_called_once_with(token, save)


@pytest.mark.parametrize(
    "email, password, token, keep_session, has_session, status",
    [
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            False,
            LoginStatus.SUCCESS,
        ),
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            False,
            LoginStatus.FAILED,
        ),
        (
            "test_email",
            "test_pass",
            "test_token",
            True,
            False,
            LoginStatus.NO_RESPONSE,
        ),
    ],
)
def test_login(
    mocker,
    email: str,
    password: str,
    token: str,
    keep_session: bool,
    has_session: bool,
    status: LoginStatus,
):
    path = "openbb_terminal.core.session.sdk_session."
    mock_login = mocker.patch(path + "session_model.login")
    mock_hub_get_session = mocker.patch(path + "get_session")

    mock_hub_get_session.return_value = TEST_SESSION
    mock_login.return_value = status

    sdk_session.login(
        email=email, password=password, token=token, keep_session=keep_session
    )

    if has_session:
        mock_hub_get_session.assert_not_called()
    else:
        mock_hub_get_session.assert_called_once_with(
            email, password, token, keep_session
        )
    mock_login.assert_called_once_with(TEST_SESSION)


@pytest.mark.parametrize(
    "email, password, token, keep_session, has_session, status",
    [
        (
            "",
            "",
            "",
            True,
            False,
            LoginStatus.SUCCESS,
        ),
        (
            "",
            "",
            "",
            True,
            True,
            LoginStatus.SUCCESS,
        ),
    ],
)
def test_login_no_args(
    mocker,
    email: str,
    password: str,
    token: str,
    keep_session: bool,
    has_session: bool,
    status: LoginStatus,
):
    path = "openbb_terminal.core.session.sdk_session."
    mock_login = mocker.patch(path + "session_model.login")
    mock_local_get_session = mocker.patch(path + "Local.get_session")
    mock_hub_get_session = mocker.patch(path + "get_session")

    mock_local_get_session.return_value = TEST_SESSION if has_session else None
    mock_hub_get_session.return_value = TEST_SESSION
    mock_login.return_value = status

    sdk_session.login(
        email=email, password=password, token=token, keep_session=keep_session
    )

    if has_session:
        mock_local_get_session.assert_called_once()
        mock_hub_get_session.assert_not_called()
    else:
        mock_hub_get_session.assert_called_once_with(
            email, password, token, keep_session
        )
    mock_login.assert_called_once_with(TEST_SESSION)


def test_logout(mocker, test_user):
    test_user.profile.load_user_info(TEST_SESSION, "testy@email.com", False)
    mocker.patch(
        target="openbb_terminal.core.session.sdk_session.get_current_user",
        return_value=test_user,
    )
    path = "openbb_terminal.core.session.sdk_session."
    with (patch(path + "session_model.logout") as mock_logout,):
        sdk_session.logout()
        mock_logout.assert_called_once_with(
            auth_header=test_user.profile.get_auth_header(),
            token=test_user.profile.get_token(),
        )


@pytest.mark.record_stdout
def test_whoami_guest():
    sdk_session.whoami()


@pytest.mark.record_stdout
def test_whoami(mocker, test_user):
    test_user.profile.load_user_info(
        {
            "token_type": "MOCK_TOKEN_TYPE",
            "access_token": "MOCK_ACCESS_TOKEN",
            "uuid": "MOCK_UUID",
        },
        email="MOCK_EMAIL",
        remember=False,
    )
    mocker.patch(
        target="openbb_terminal.core.session.sdk_session.get_current_user",
        return_value=test_user,
    )

    sdk_session.whoami()
