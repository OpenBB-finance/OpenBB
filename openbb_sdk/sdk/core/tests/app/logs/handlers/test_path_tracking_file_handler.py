"""Test the path_tracking_file_handler.py file."""
# pylint: disable=redefined-outer-name

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from openbb_core.app.logs.handlers.path_tracking_file_handler import (
    PathTrackingFileHandler,
)


class MockLoggingSettings:
    def __init__(self, app_name, user_logs_directory, session_id, frequency):
        self.app_name = app_name
        self.user_logs_directory = Path(user_logs_directory)
        self.session_id = session_id
        self.frequency = frequency


logging_settings = MagicMock(spec=MockLoggingSettings)
logging_settings.app_name = "test_app_name_xpto"
logging_settings.user_logs_directory = MagicMock()
logging_settings.user_logs_directory.absolute.return_value = Path(
    "/mocked/logs/directory"
)
logging_settings.session_id = "test_session_id"
logging_settings.frequency = "H"


@pytest.fixture(scope="module")
def mocked_path(tmp_path_factory):
    return tmp_path_factory.mktemp("mocked_path") / "mocked_file.log"


@pytest.fixture(scope="module")
def handler(mocked_path):
    # patch `pathlib.Path.joinpath` to return a string containing the joined path
    with patch.object(Path, "joinpath", return_value=mocked_path):
        return PathTrackingFileHandler(logging_settings)


def test_build_log_file_path(handler, mocked_path):
    # Define a sample LoggingSettings object with mock attributes
    settings = MagicMock(spec=MockLoggingSettings)
    settings.app_name = "my_app"
    settings.user_logs_directory = MagicMock()
    settings.user_logs_directory.absolute.return_value = Path("/mocked/logs/directory")
    settings.session_id = "abc123"

    # patch `pathlib.Path.joinpath` to return a string containing the joined path
    with patch.object(Path, "joinpath", return_value=mocked_path) as mock_joinpath:
        result_path = handler.build_log_file_path(settings)

    # Assert the result is correct
    assert result_path == mocked_path

    mock_joinpath.assert_called_once_with("my_app_abc123")


def test_clean_expired_files(handler):
    with patch(
        "openbb_core.app.logs.handlers.path_tracking_file_handler.get_expired_file_list"
    ) as mock_get_expired_file_list, patch(
        "openbb_core.app.logs.handlers.path_tracking_file_handler.remove_file_list"
    ) as mock_remove_file_list:
        handler.clean_expired_files(123)

        assert mock_get_expired_file_list.call_count == 3
        assert mock_remove_file_list.call_count == 3
