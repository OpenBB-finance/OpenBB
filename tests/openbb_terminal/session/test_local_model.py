# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json
from unittest.mock import mock_open, patch

import pytest

from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    UserModel,
)
from openbb_terminal.core.session import local_model

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import get_current_user

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


@pytest.fixture(autouse=True)
def revert_current_user(mocker):
    mocker.patch(
        target="openbb_terminal.keys_model.set_credential",
    )

    yield


@pytest.fixture(name="test_user")
def fixture_test_user():
    return UserModel(
        credentials=CredentialsModel(),
        preferences=PreferencesModel(),
        profile=ProfileModel(),
    )


def test_save_session():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.open", open_mock, create=True):
        local_model.save_session(data=TEST_SESSION)

    open_mock.assert_called_with(local_model.SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_called_once_with(json.dumps(TEST_SESSION))


@pytest.mark.record_stdout
def test_save_session_exception():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.open", open_mock, create=True):
        open_mock.side_effect = Exception
        local_model.save_session(data=TEST_SESSION)

    open_mock.assert_called_with(local_model.SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_not_called()


def test_get_session():
    open_mock = mock_open(read_data=json.dumps(TEST_SESSION))
    with patch("openbb_terminal.core.session.local_model.os.path") as path_mock:
        with patch(
            "openbb_terminal.core.session.local_model.open", open_mock, create=True
        ):
            assert local_model.get_session() == TEST_SESSION

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.return_value.read.assert_called_once()


def test_get_session_not_exist():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.os.path") as path_mock:
        path_mock.isfile.return_value = False
        with patch(
            "openbb_terminal.core.session.local_model.open", open_mock, create=True
        ):
            assert local_model.get_session() == {}

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_not_called()
    open_mock.return_value.read.assert_not_called()


@pytest.mark.record_stdout
def test_get_session_exception():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.os.path") as path_mock:
        with patch(
            "openbb_terminal.core.session.local_model.open", open_mock, create=True
        ):
            open_mock.side_effect = Exception
            assert local_model.get_session() == {}

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.return_value.read.assert_not_called()


def test_remove_session_file():
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        assert local_model.remove_session_file() is True

    os_mock.path.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.SESSION_FILE_PATH)


def test_remove_session_file_not_exist():
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        os_mock.path.isfile.return_value = False
        assert local_model.remove_session_file() is True

    os_mock.path.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    os_mock.remove.assert_not_called()


@pytest.mark.record_stdout
def test_remove_session_file_exception():
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        os_mock.remove.side_effect = Exception
        assert local_model.remove_session_file() is False

    os_mock.path.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.SESSION_FILE_PATH)


def test_remove_cli_history_file():
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        assert local_model.remove_cli_history_file() is True

    os_mock.path.isfile.assert_called_with(local_model.HIST_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.HIST_FILE_PATH)


def test_remove_cli_history_file_not_exist():
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        os_mock.path.isfile.return_value = False
        assert local_model.remove_cli_history_file() is True

    os_mock.path.isfile.assert_called_with(local_model.HIST_FILE_PATH)
    os_mock.remove.assert_not_called()


@pytest.mark.record_stdout
def test_remove_cli_history_file_exception():
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        os_mock.remove.side_effect = Exception
        assert local_model.remove_cli_history_file() is False

    os_mock.path.isfile.assert_called_with(local_model.HIST_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.HIST_FILE_PATH)


# Configs to apply
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


@pytest.mark.skip("Not working?")
@pytest.mark.parametrize(
    "sync",
    [
        "False",
        "True",
    ],
)
def test_apply_configs_sync(mocker, sync: str, test_user: UserModel):
    mocker.patch(
        target="openbb_terminal.core.session.current_user.set_current_user",
        return_value=test_user,
    )
    mocker.patch(
        target="openbb_terminal.core.session.current_user.get_current_user",
        return_value=test_user,
    )

    CONFIGS["features_settings"]["SYNC_ENABLED"] = sync
    local_model.apply_configs(CONFIGS)

    preferences = test_user.preferences

    print("__TEST__", sync, type(sync))
    if sync == "False":
        assert preferences.SYNC_ENABLED is False
    else:
        assert preferences.SYNC_ENABLED is True


@pytest.mark.parametrize(
    "exists",
    [
        False,
        True,
    ],
)
def test_get_routine(mocker, exists: bool, test_user):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    routine = "do something"
    current_user = get_current_user()

    test_user.profile.uuid = uuid
    mocker.patch(
        target="openbb_terminal.core.session.local_model.get_current_user",
        return_value=test_user,
    )

    exists_mock = mocker.patch(
        "openbb_terminal.core.session.local_model.os.path.exists", return_value=exists
    )
    open_mock = mocker.patch(
        "openbb_terminal.core.session.local_model.open",
        mock_open(read_data=json.dumps(routine)),
    )

    assert local_model.get_routine(file_name=file_name) == json.dumps(routine)

    exists_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / uuid / file_name
    )
    if exists:
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY / uuid / file_name
        )
    else:
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY / file_name
        )


def test_get_routine_exception(mocker, test_user):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    current_user = get_current_user()

    test_user.profile.uuid = uuid
    mocker.patch(
        target="openbb_terminal.core.session.local_model.get_current_user",
        return_value=test_user,
    )
    exists_mock = mocker.patch(
        "openbb_terminal.core.session.local_model.os.path.exists"
    )
    open_mock = mocker.patch(
        "openbb_terminal.core.session.local_model.open",
        side_effect=Exception("test exception"),
    )

    assert local_model.get_routine(file_name=file_name) is None

    exists_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / uuid / file_name
    )
    open_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / uuid / file_name
    )


@pytest.mark.parametrize(
    "exists",
    [
        False,
        True,
    ],
)
def test_save_routine(mocker, exists: bool, test_user):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    routine = "do something"
    current_user = get_current_user()

    test_user.profile.uuid = uuid
    mocker.patch(
        target="openbb_terminal.core.session.local_model.get_current_user",
        return_value=test_user,
    )

    exists_mock = mocker.patch(
        "openbb_terminal.core.session.local_model.os.path.exists", return_value=exists
    )
    makedirs_mock = mocker.patch("openbb_terminal.core.session.local_model.os.makedirs")
    open_mock = mocker.patch(
        "openbb_terminal.core.session.local_model.open",
    )

    result = local_model.save_routine(file_name=file_name, routine=routine)

    if exists:
        assert result == "File already exists"
        makedirs_mock.assert_not_called()
    else:
        assert (
            result
            == current_user.preferences.USER_ROUTINES_DIRECTORY / uuid / file_name
        )
        makedirs_mock.assert_called_once()
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY / uuid / file_name, "w"
        )

    assert exists_mock.call_count == 2


def test_save_routine_exception(mocker, test_user):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    routine = "do something"

    test_user.profile.uuid = uuid
    mocker.patch(
        target="openbb_terminal.core.session.local_model.get_current_user",
        return_value=test_user,
    )

    mocker.patch(
        "openbb_terminal.core.session.local_model.os.path.exists", return_value=False
    )
    mocker.patch("openbb_terminal.core.session.local_model.os.makedirs")
    mocker.patch(
        "openbb_terminal.core.session.local_model.open",
        side_effect=Exception("test exception"),
    )

    result = local_model.save_routine(file_name=file_name, routine=routine)
    assert result is None
