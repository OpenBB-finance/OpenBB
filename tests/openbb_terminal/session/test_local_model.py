# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.session import local_model

TEST_SESSION = {
    "access_token": "test_token",
    "token_type": "bearer",
    "uuid": "test_uuid",
}


def test_save_session():
    open_mock = mock_open()
    with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
        local_model.save_session(data=TEST_SESSION)

    open_mock.assert_called_with(local_model.SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_called_once_with(json.dumps(TEST_SESSION))


@pytest.mark.record_stdout
def test_save_session_exception():
    open_mock = mock_open()
    with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
        open_mock.side_effect = Exception
        local_model.save_session(data=TEST_SESSION)

    open_mock.assert_called_with(local_model.SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_not_called()


def test_get_session():
    open_mock = mock_open(read_data=json.dumps(TEST_SESSION))
    with patch("openbb_terminal.session.local_model.os.path") as path_mock:
        with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
            assert local_model.get_session() == TEST_SESSION

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.return_value.read.assert_called_once()


def test_get_session_not_exist():
    open_mock = mock_open()
    with patch("openbb_terminal.session.local_model.os.path") as path_mock:
        path_mock.isfile.return_value = False
        with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
            assert local_model.get_session() == {}

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_not_called()
    open_mock.return_value.read.assert_not_called()


@pytest.mark.record_stdout
def test_get_session_exception():
    open_mock = mock_open()
    with patch("openbb_terminal.session.local_model.os.path") as path_mock:
        with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
            open_mock.side_effect = Exception
            assert local_model.get_session() == {}

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.return_value.read.assert_not_called()


def test_remove_session_file():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        assert local_model.remove_session_file() is True

    os_mock.path.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.SESSION_FILE_PATH)


def test_remove_session_file_not_exist():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        os_mock.path.isfile.return_value = False
        assert local_model.remove_session_file() is True

    os_mock.path.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    os_mock.remove.assert_not_called()


@pytest.mark.record_stdout
def test_remove_session_file_exception():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        os_mock.remove.side_effect = Exception
        assert local_model.remove_session_file() is False

    os_mock.path.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.SESSION_FILE_PATH)


def test_remove_cli_history_file():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        assert local_model.remove_cli_history_file() is True

    os_mock.path.isfile.assert_called_with(local_model.HIST_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.HIST_FILE_PATH)


def test_remove_cli_history_file_not_exist():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        os_mock.path.isfile.return_value = False
        assert local_model.remove_cli_history_file() is True

    os_mock.path.isfile.assert_called_with(local_model.HIST_FILE_PATH)
    os_mock.remove.assert_not_called()


@pytest.mark.record_stdout
def test_remove_cli_history_file_exception():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        os_mock.remove.side_effect = Exception
        assert local_model.remove_cli_history_file() is False

    os_mock.path.isfile.assert_called_with(local_model.HIST_FILE_PATH)
    os_mock.remove.assert_called_with(local_model.HIST_FILE_PATH)


# Patch the config classes
class obbff:
    SYNC_ENABLED = True
    USE_WATERMARK = True
    TIMEZONE = "America/New_York"


class cfg_plot:
    PLOT_DPI = 100
    PLOT_HEIGHT_PERCENTAGE = 50.0


class paths:
    USER_DATA_DIRECTORY = Path("user_home/OpenBBUserData")


class cfg:
    API_KEY_ALPHAVANTAGE = "REPLACE_ME"
    API_FRED_KEY = "REPLACE_ME"


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


@pytest.mark.parametrize(
    "sync",
    [
        "False",
        "True",
    ],
)
@patch("openbb_terminal.session.local_model.obbff", obbff)
@patch("openbb_terminal.session.local_model.cfg_plot", cfg_plot)
@patch("openbb_terminal.session.local_model.paths", paths)
@patch("openbb_terminal.session.local_model.cfg", cfg)
def test_apply_configs_sync(sync: str):
    CONFIGS["features_settings"]["SYNC_ENABLED"] = sync
    local_model.apply_configs(CONFIGS)

    if sync == "False":
        assert obbff.SYNC_ENABLED is False
        assert obbff.USE_WATERMARK is True
        assert obbff.TIMEZONE == "America/New_York"
        assert cfg_plot.PLOT_DPI == 100
        assert cfg_plot.PLOT_HEIGHT_PERCENTAGE == 50.0
        assert paths.USER_DATA_DIRECTORY == Path("user_home/OpenBBUserData")
        assert cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME"
        assert cfg.API_FRED_KEY == "REPLACE_ME"
    else:
        assert obbff.SYNC_ENABLED is True
        assert obbff.USE_WATERMARK is False
        assert obbff.TIMEZONE == "Europe/London"
        assert cfg_plot.PLOT_DPI == 95
        assert cfg_plot.PLOT_HEIGHT_PERCENTAGE == 50.5
        assert paths.USER_DATA_DIRECTORY == Path("some/path/to/user/data")
        assert cfg.API_KEY_ALPHAVANTAGE == "test_av"
        assert cfg.API_FRED_KEY == "test_fred"


@pytest.mark.parametrize(
    "exists",
    [
        False,
        True,
    ],
)
def test_get_routine(mocker, exists: bool):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    routine = "do something"

    user_mock = mocker.patch(
        "openbb_terminal.session.local_model.User.get_uuid", return_value=uuid
    )
    exists_mock = mocker.patch(
        "openbb_terminal.session.local_model.os.path.exists", return_value=exists
    )
    open_mock = mocker.patch(
        "openbb_terminal.session.local_model.open",
        mock_open(read_data=json.dumps(routine)),
    )

    assert local_model.get_routine(file_name=file_name) == json.dumps(routine)

    user_mock.assert_called_once()
    exists_mock.assert_called_with(
        local_model.USER_ROUTINES_DIRECTORY / uuid / file_name
    )
    if exists:
        open_mock.assert_called_with(
            local_model.USER_ROUTINES_DIRECTORY / uuid / file_name
        )
    else:
        open_mock.assert_called_with(local_model.USER_ROUTINES_DIRECTORY / file_name)


def test_get_routine_exception(mocker):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"

    user_mock = mocker.patch(
        "openbb_terminal.session.local_model.User.get_uuid", return_value=uuid
    )
    exists_mock = mocker.patch("openbb_terminal.session.local_model.os.path.exists")
    open_mock = mocker.patch(
        "openbb_terminal.session.local_model.open",
        side_effect=Exception("test exception"),
    )

    assert local_model.get_routine(file_name=file_name) is None

    user_mock.assert_called_once()
    exists_mock.assert_called_with(
        local_model.USER_ROUTINES_DIRECTORY / uuid / file_name
    )
    open_mock.assert_called_with(local_model.USER_ROUTINES_DIRECTORY / uuid / file_name)


@pytest.mark.parametrize(
    "exists",
    [
        False,
        True,
    ],
)
def test_save_routine(mocker, exists: bool):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    routine = "do something"

    user_mock = mocker.patch(
        "openbb_terminal.session.local_model.User.get_uuid", return_value=uuid
    )
    exists_mock = mocker.patch(
        "openbb_terminal.session.local_model.os.path.exists", return_value=exists
    )
    makedirs_mock = mocker.patch("openbb_terminal.session.local_model.os.makedirs")
    open_mock = mocker.patch(
        "openbb_terminal.session.local_model.open",
    )

    assert (
        local_model.save_routine(file_name=file_name, routine=routine)
        == local_model.USER_ROUTINES_DIRECTORY / uuid / file_name
    )

    user_mock.assert_called_once()
    exists_mock.assert_called_with(local_model.USER_ROUTINES_DIRECTORY / uuid)
    if exists:
        makedirs_mock.assert_not_called()
    else:
        makedirs_mock.assert_called_with(local_model.USER_ROUTINES_DIRECTORY / uuid)

    open_mock.assert_called_with(
        local_model.USER_ROUTINES_DIRECTORY / uuid / file_name, "w"
    )


def test_save_routine_exception(mocker):
    file_name = "test_routine.openbb"
    uuid = "test_uuid"
    routine = "do something"

    user_mock = mocker.patch(
        "openbb_terminal.session.local_model.User.get_uuid", return_value=uuid
    )
    exists_mock = mocker.patch("openbb_terminal.session.local_model.os.path.exists")
    open_mock = mocker.patch(
        "openbb_terminal.session.local_model.open",
        side_effect=Exception("test exception"),
    )

    assert local_model.save_routine(file_name=file_name, routine=routine) is None

    user_mock.assert_called_once()
    exists_mock.assert_called_with(local_model.USER_ROUTINES_DIRECTORY / uuid)
    open_mock.assert_called_with(
        local_model.USER_ROUTINES_DIRECTORY / uuid / file_name, "w"
    )
