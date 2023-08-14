# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import json
from unittest.mock import mock_open

import pytest
from requests import Response

# IMPORTATION INTERNAL
from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    SourcesModel,
    UserModel,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.core.session.routines_handler import (
    download_routines,
    read_routine,
    save_routine,
)


@pytest.fixture(name="test_user")
def fixture_test_user():
    return UserModel(
        credentials=CredentialsModel(),
        preferences=PreferencesModel(),
        profile=ProfileModel(),
        sources=SourcesModel(),
    )


def test_read_routine(mocker, test_user):
    file_name = "test_routine.openbb"
    routine = "do something"
    current_user = get_current_user()
    path = "openbb_terminal.core.session.routines_handler"

    mocker.patch(
        target=path + ".get_current_user",
        return_value=test_user,
    )
    walk_mock = mocker.patch(
        path + ".walk",
        return_value=[
            (
                current_user.preferences.USER_ROUTINES_DIRECTORY / "hub",
                ["personal"],
                [],
            ),
            (
                current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / "personal",
                [],
                [file_name],
            ),
        ],
    )
    relpath_mock = mocker.patch(path + ".os.path.relpath", return_value="hub/personal")
    open_mock = mocker.patch(path + ".open", mock_open(read_data=json.dumps(routine)))
    assert read_routine(file_name=file_name) == json.dumps(routine)

    walk_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / "hub"
    )
    relpath_mock.assert_called_once_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / "personal",
        current_user.preferences.USER_ROUTINES_DIRECTORY,
    )
    open_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY
        / "hub"
        / "personal"
        / file_name
    )


def test_read_routine_exception(mocker, test_user):
    file_name = "test_routine.openbb"
    current_user = get_current_user()
    path = "openbb_terminal.core.session.routines_handler"
    mocker.patch(
        target=path + ".get_current_user",
        return_value=test_user,
    )
    walk_mock = mocker.patch(
        path + ".walk",
        return_value=[
            (
                current_user.preferences.USER_ROUTINES_DIRECTORY / "hub",
                ["personal"],
                [],
            ),
            (
                current_user.preferences.USER_ROUTINES_DIRECTORY / "hub" / "personal",
                [],
                ["do something"],
            ),
        ],
    )
    relpath_mock = mocker.patch(path + ".os.path.relpath")
    open_mock = mocker.patch(
        path + ".open",
        side_effect=Exception("test exception"),
    )
    assert read_routine(file_name=file_name) is None

    walk_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / "hub"
    )
    relpath_mock.assert_not_called()
    open_mock.assert_called_with(
        current_user.preferences.USER_ROUTINES_DIRECTORY / file_name
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
    routine = ["do something", "personal"]
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
            == current_user.preferences.USER_ROUTINES_DIRECTORY
            / "hub"
            / "personal"
            / file_name
        )
        makedirs_mock.assert_called_once()
        open_mock.assert_called_with(
            current_user.preferences.USER_ROUTINES_DIRECTORY
            / "hub"
            / "personal"
            / file_name,
            "w",
        )

    assert exists_mock.call_count == 2


def test_save_routine_exception(mocker, test_user):
    file_name = "test_routine.openbb"
    routine = ["do something", "personal"]
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


def test_download_routine(mocker, test_user, silent=False):
    path_hub_model = "openbb_terminal.core.session.hub_model"
    path_routines_handler = "openbb_terminal.core.session.routines_handler"
    mocker.patch(
        target=path_routines_handler + ".get_current_user",
        return_value=test_user,
    )
    response_default = Response()
    response_default.status_code = 200
    content = {
        "data": [{"name": "script1", "description": "abc", "script": "do something"}]
    }
    response_default._content = json.dumps(
        content
    ).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    # print(response_default._content)

    response_personal = Response()
    response_personal.status_code = 200
    content = {
        "items": [{"name": "script2", "description": "cde", "script": "do something"}]
    }

    response_personal._content = json.dumps(
        content
    ).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    get_default_routines_mock = mocker.patch(
        target=path_hub_model + ".get_default_routines", return_value=response_default
    )
    get_personal_routines_mock = mocker.patch(
        target=path_hub_model + ".list_routines", return_value=response_personal
    )
    assert download_routines(test_user.profile.get_auth_header()) == [
        {"script2": ["do something", "personal"]},
        {"script1": ["do something", "default"]},
    ]

    get_default_routines_mock.assert_called_once()
    get_personal_routines_mock.assert_called_once_with(
        auth_header=test_user.profile.get_auth_header(),
        fields=["name", "script"],
        page=1,
        size=100,
        base_url="https://payments.openbb.co/",
        silent=silent,
    )


def test_download_default_routine_exception(mocker, test_user, silent=False):
    path_hub_model = "openbb_terminal.core.session.hub_model"
    path_routines_handler = "openbb_terminal.core.session.routines_handler"
    mocker.patch(
        target=path_routines_handler + ".get_current_user",
        return_value=test_user,
    )
    response_personal = Response()
    response_personal.status_code = 200
    content = {
        "items": [{"name": "script2", "description": "cde", "script": "do something"}]
    }
    response_personal._content = json.dumps(
        content
    ).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    get_personal_routines_mock = mocker.patch(
        target=path_hub_model + ".list_routines", return_value=response_personal
    )
    get_default_routines_mock = mocker.patch(
        path_hub_model + ".get_default_routines",
        side_effect=Exception("test exception"),
    )
    assert download_routines(test_user.profile.get_auth_header()) == [
        {"script2": ["do something", "personal"]},
        {},
    ]
    get_default_routines_mock.assert_called_once()
    get_personal_routines_mock.assert_called_once_with(
        auth_header=test_user.profile.get_auth_header(),
        fields=["name", "script"],
        page=1,
        size=100,
        base_url="https://payments.openbb.co/",
        silent=silent,
    )


def test_download_personal_routine_exception(mocker, test_user, silent=False):
    path_hub_model = "openbb_terminal.core.session.hub_model"
    path_routines_handler = "openbb_terminal.core.session.routines_handler"
    mocker.patch(
        target=path_routines_handler + ".get_current_user",
        return_value=test_user,
    )
    response_default = Response()
    response_default.status_code = 200
    content = {
        "data": [{"name": "script1", "description": "abc", "script": "do something"}]
    }
    response_default._content = json.dumps(
        content
    ).encode(  # pylint: disable=protected-access
        "utf-8"
    )
    get_default_routines_mock = mocker.patch(
        target=path_hub_model + ".get_default_routines", return_value=response_default
    )
    get_personal_routines_mock = mocker.patch(
        path_hub_model + ".list_routines",
        side_effect=Exception("test exception"),
    )
    assert download_routines(test_user.profile.get_auth_header()) == [
        {},
        {"script1": ["do something", "default"]},
    ]
    get_default_routines_mock.assert_called_once()
    get_personal_routines_mock.assert_called_once_with(
        auth_header=test_user.profile.get_auth_header(),
        fields=["name", "script"],
        page=1,
        size=100,
        base_url="https://payments.openbb.co/",
        silent=silent,
    )


def test_download_default_and_personal_routine_exception(
    mocker, test_user, silent=False
):
    path_hub_model = "openbb_terminal.core.session.hub_model"
    path_routines_handler = "openbb_terminal.core.session.routines_handler"
    mocker.patch(
        target=path_routines_handler + ".get_current_user",
        return_value=test_user,
    )
    get_default_routines_mock = mocker.patch(
        path_hub_model + ".get_default_routines",
        side_effect=Exception("test exception"),
    )

    get_personal_routines_mock = mocker.patch(
        path_hub_model + ".list_routines",
        side_effect=Exception("test exception"),
    )
    assert download_routines(test_user.profile.get_auth_header()) == [{}, {}]
    get_default_routines_mock.assert_called_once()
    get_personal_routines_mock.assert_called_once_with(
        auth_header=test_user.profile.get_auth_header(),
        fields=["name", "script"],
        page=1,
        size=100,
        base_url="https://payments.openbb.co/",
        silent=silent,
    )
