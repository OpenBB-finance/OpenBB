import os
from openbb_terminal.core.log.generation.expired_files import (
    get_timestamp_from_x_days,
    get_expired_file_list,
    remove_file_list,
)


def test_get_timestamp_from_x_days():
    timestamp = get_timestamp_from_x_days(x=1)

    assert isinstance(timestamp, float)


def test_get_expired_files(tmp_path):
    mock_file_list = [
        tmp_path.joinpath("mock_file_1"),
        tmp_path.joinpath("mock_file_2"),
    ]

    x = 2
    mock_timestamp = get_timestamp_from_x_days(x=x + 1)
    before_timestamp = get_timestamp_from_x_days(x=x)

    for path in mock_file_list:
        path.touch()
        os.utime(path, times=(mock_timestamp, mock_timestamp))

    expired_file_list = get_expired_file_list(
        directory=tmp_path, before_timestamp=before_timestamp
    )

    assert len(expired_file_list) == len(mock_file_list)

    for path in mock_file_list:
        assert path in expired_file_list


def test_remove_file_list(mocker):
    file_list = [mocker.Mock(), mocker.Mock()]
    remove_file_list(file_list=file_list)

    for file in file_list:
        file.unlink.assert_called_once()
