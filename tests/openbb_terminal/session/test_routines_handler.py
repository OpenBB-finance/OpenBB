# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import json
from unittest.mock import mock_open

import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    SourcesModel,
    UserModel,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.core.session.routines_handler import read_routine, save_routine


@pytest.fixture(name="test_user")
def fixture_test_user():
    return UserModel(
        credentials=CredentialsModel(),
        preferences=PreferencesModel(),
        profile=ProfileModel(),
        sources=SourcesModel(),
    )


@pytest.mark.parametrize(
    "exists",
    [
        False,
        True,
    ],
)
def test_read_routine(mocker, exists: bool, test_user):
    file_name = "test_routine.openbb"
    routine = "do something"
    current_user = get_current_user()
    path = "openbb_terminal.core.session.routines_handler"

    mocker.patch(
        target=path + ".get_current_user",
        return_value=test_user,
    )

    exists_mock = mocker.patch(path + ".os.path.exists", return_value=exists)
    open_mock = mocker.patch(
        path + ".open",
        mock_open(read_data=json.dumps(routine)),
    )

    assert read_routine(file_name=file_name) == json.dumps(routine)

    exists_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / file_name
    )
    if exists:
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / file_name
        )
    else:
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY / file_name
        )


def test_read_routine_exception(mocker, test_user):
    file_name = "test_routine.openbb"
    current_user = get_current_user()
    path = "openbb_terminal.core.session.routines_handler"

    mocker.patch(
        target=path + ".get_current_user",
        return_value=test_user,
    )
    exists_mock = mocker.patch(path + ".os.path.exists")
    open_mock = mocker.patch(
        path + ".open",
        side_effect=Exception("test exception"),
    )

    assert read_routine(file_name=file_name) is None

    exists_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / file_name
    )
    open_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / file_name
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
    routine = "do something"
    current_user = get_current_user()
    path = "openbb_terminal.core.session.routines_handler"

    mocker.patch(
        target=path + ".get_current_user",
        return_value=test_user,
    )

    exists_mock = mocker.patch(path + ".os.path.exists", return_value=exists)
    makedirs_mock = mocker.patch(path + ".os.makedirs")
    open_mock = mocker.patch(
        path + ".open",
    )

    result = save_routine(file_name=file_name, routine=routine)

    if exists:
        assert result == "File already exists"
        makedirs_mock.assert_not_called()
    else:
        assert (
            result
            == current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / file_name
        )
        makedirs_mock.assert_called_once()
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / file_name, "w"
        )

    assert exists_mock.call_count == 2


def test_save_routine_exception(mocker, test_user):
    file_name = "test_routine.openbb"
    routine = "do something"
    path = "openbb_terminal.core.session.routines_handler"

    mocker.patch(
        target=path + ".get_current_user",
        return_value=test_user,
    )

    mocker.patch(path + ".os.path.exists", return_value=False)
    mocker.patch(path + ".os.makedirs")
    mocker.patch(
        path + ".open",
        side_effect=Exception("test exception"),
    )

    result = save_routine(file_name=file_name, routine=routine)
    assert result is None
