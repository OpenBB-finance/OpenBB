# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from openbb_terminal.core.config.paths import SESSION_FILE_PATH
from openbb_terminal.core.models.user_model import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    SourcesModel,
    UserModel,
)
from openbb_terminal.core.session import local_model

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
        sources=SourcesModel(),
    )


def test_save_session():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.open", open_mock, create=True):
        local_model.save_session(data=TEST_SESSION)

    open_mock.assert_called_with(SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_called_once_with(json.dumps(TEST_SESSION))


@pytest.mark.record_stdout
def test_save_session_exception():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.open", open_mock, create=True):
        open_mock.side_effect = Exception
        local_model.save_session(data=TEST_SESSION)

    open_mock.assert_called_with(SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_not_called()


def test_get_session():
    open_mock = mock_open(read_data=json.dumps(TEST_SESSION))
    with patch("openbb_terminal.core.session.local_model.os.path") as path_mock, patch(
        "openbb_terminal.core.session.local_model.open", open_mock, create=True
    ):
        assert local_model.get_session() == TEST_SESSION

    path_mock.isfile.assert_called_with(SESSION_FILE_PATH)
    open_mock.assert_called_with(SESSION_FILE_PATH)
    open_mock.return_value.read.assert_called_once()


def test_get_session_not_exist():
    open_mock = mock_open()
    with patch("openbb_terminal.core.session.local_model.os.path") as path_mock:
        path_mock.isfile.return_value = False
        with patch(
            "openbb_terminal.core.session.local_model.open", open_mock, create=True
        ):
            assert local_model.get_session() == {}

    path_mock.isfile.assert_called_with(SESSION_FILE_PATH)
    open_mock.assert_not_called()
    open_mock.return_value.read.assert_not_called()


@pytest.mark.record_stdout
def test_get_session_exception():
    open_mock = mock_open()
    path = "openbb_terminal.core.session.local_model"
    with patch(f"{path}.os.path") as path_mock, patch(
        f"{path}.open", open_mock, create=True
    ):
        open_mock.side_effect = Exception
        assert local_model.get_session() == {}

    path_mock.isfile.assert_called_with(SESSION_FILE_PATH)
    open_mock.assert_called_with(SESSION_FILE_PATH)
    open_mock.return_value.read.assert_not_called()


def test_remove_file():
    test_path = Path("test_path")
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        assert local_model.remove(test_path) is True

    os_mock.path.isfile.assert_called_with(test_path)
    os_mock.remove.assert_called_with(test_path)


def test_remove_directory(mocker):
    os_mock = mocker.patch("openbb_terminal.core.session.local_model.os")
    shutil_mock = mocker.patch("openbb_terminal.core.session.local_model.shutil")
    os_mock.path.isfile.return_value = False
    shutil_mock.rmtree.return_value = True
    test_dir = Path("test_dir")

    assert local_model.remove(test_dir) is True

    os_mock.path.isfile.assert_called_with(test_dir)
    shutil_mock.rmtree.assert_called_with(test_dir)


def test_remove_not_exist(mocker):
    os_mock = mocker.patch("openbb_terminal.core.session.local_model.os")
    shutil_mock = mocker.patch("openbb_terminal.core.session.local_model.shutil")
    os_mock.path.isfile.return_value = False
    shutil_mock.rmtree.return_value = False
    test_path = Path("test_path")

    assert local_model.remove(test_path) is True
    os_mock.path.isfile.assert_called_with(test_path)
    os_mock.remove.assert_not_called()


def test_remove_exception():
    test_path = Path("test_path")
    with patch("openbb_terminal.core.session.local_model.os") as os_mock:
        os_mock.remove.side_effect = Exception
        assert local_model.remove(test_path) is False

    os_mock.path.isfile.assert_called_with(test_path)
    os_mock.remove.assert_called_with(test_path)
