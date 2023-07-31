import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from openbb_core.app.logs.utils.utils import get_app_id, get_log_dir, get_session_id

## get_session_id


def test_get_session_id_return_type():
    # Test if the returned value is a string
    session_id = get_session_id()
    assert isinstance(session_id, str)


def test_get_session_id_format():
    # Test if the returned string has the format "UUID-current_time"
    session_id = get_session_id()

    parts = session_id.split("-")

    assert len(parts) == 6

    uuid_part = "-".join(parts[0:5])
    time_part = str(parts[5])

    # Check if the first part (UUID) is a valid UUID
    assert uuid.UUID(uuid_part)

    # Check if the second part (current_time) is numeric
    assert int(time_part)


def test_get_session_id_uniqueness():
    # Test if subsequent calls return different session IDs
    session_id1 = get_session_id()
    session_id2 = get_session_id()
    assert session_id1 != session_id2


## get_app_id


def test_get_app_id_success():
    # Mock the return value of get_log_dir to simulate a successful scenario
    with patch("openbb_core.app.logs.utils.utils.get_log_dir") as mock_get_log_dir:
        mock_get_log_dir
        mock_get_log_dir.return_value = Path(
            "/path/to/contextual_user_data_directory/app_id.log"
        )
        app_id = get_app_id("/path/to/contextual_user_data_directory")
        assert app_id == "app_id"


def test_get_app_id_os_error():
    # Test handling of OSError with errno 30 (Read-only file system)
    with patch("openbb_core.app.logs.utils.utils.get_log_dir") as mock_get_log_dir:
        mock_get_log_dir.side_effect = OSError(30, "Read-only file system")
        with pytest.raises(OSError):
            get_app_id("/path/to/contextual_user_data_directory")


def test_get_app_id_other_exception():
    # Test handling of other exceptions
    with patch("openbb_core.app.logs.utils.utils.get_log_dir") as mock_get_log_dir:
        mock_get_log_dir.side_effect = Exception("Some other error")
        with pytest.raises(Exception, match="Some other error"):
            get_app_id("/path/to/contextual_user_data_directory")


## get_log_dir


def test_get_log_dir():
    with patch(
        "openbb_core.app.logs.utils.utils.create_log_dir_if_not_exists",
        return_value="/test_dir",
    ) as mock_create_log_dir, patch(
        "openbb_core.app.logs.utils.utils.create_log_uuid_if_not_exists",
        return_value="12345",
    ) as mock_create_log_uuid, patch(
        "openbb_core.app.logs.utils.utils.create_uuid_dir_if_not_exists",
        return_value="/test_dir/12345",
    ) as mock_create_uuid_dir:
        # Call the get_log_dir function
        result = get_log_dir("contextual_user_data_directory")

        # Assertions
        assert result == "/test_dir/12345"
        mock_create_log_dir.assert_called_once_with("contextual_user_data_directory")
        mock_create_log_uuid.assert_called_once_with("/test_dir")
        mock_create_uuid_dir.assert_called_once_with("/test_dir", "12345")
