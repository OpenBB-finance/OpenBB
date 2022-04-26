from openbb_terminal.core.log.generation.directories import get_log_dir, get_log_sub_dir
from pathlib import Path


def test_get_log_dir(mocker, tmp_path):
    mock_file_path = mocker.Mock()
    mock_file_path.parent.parent.parent.parent = tmp_path
    mocker.patch(
        "openbb_terminal.core.log.generation.directories.Path",
        return_value=mock_file_path,
    )

    log_dir = get_log_dir()

    assert isinstance(log_dir, Path)
    assert log_dir.parent.parent == tmp_path

    log_dir_bis = get_log_dir()

    assert isinstance(log_dir, Path)
    assert log_dir.parent.parent == tmp_path
    assert log_dir_bis == log_dir


def test_get_log_sub_dir(mocker, tmp_path):
    mocker.patch(
        "openbb_terminal.core.log.generation.directories.get_log_dir",
        return_value=tmp_path,
    )
    name = "mock_sub_dir"
    sub_dir = get_log_sub_dir(name=name)

    assert isinstance(sub_dir, Path)
    assert sub_dir.parent == tmp_path
