# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import json
from unittest.mock import patch, mock_open

# IMPORTATION INTERNAL
from openbb_terminal.session import local_model


def test_save_good_session():
    open_mock = mock_open()
    with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
        data = {
            "access_token": "test_token",
            "token_type": "bearer",
            "uuid": "test_uuid",
        }
        local_model.save_session(data=data)

    open_mock.assert_called_with(local_model.SESSION_FILE_PATH, "w")
    open_mock.return_value.write.assert_called_once_with(json.dumps(data))


def test_get_session():
    data = {
        "access_token": "test_token",
        "token_type": "bearer",
        "uuid": "test_uuid",
    }
    open_mock = mock_open(read_data=json.dumps(data))
    with patch("openbb_terminal.session.local_model.os.path") as path_mock:
        with patch("openbb_terminal.session.local_model.open", open_mock, create=True):
            assert local_model.get_session() == data

    path_mock.isfile.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.assert_called_with(local_model.SESSION_FILE_PATH)
    open_mock.return_value.read.assert_called_once()


def test_remove_session_file():
    with patch("openbb_terminal.session.local_model.os") as os_mock:
        local_model.remove_session_file()

    os_mock.remove.assert_called_with(local_model.SESSION_FILE_PATH)
