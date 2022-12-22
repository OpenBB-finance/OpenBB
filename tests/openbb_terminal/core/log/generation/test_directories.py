import logging
from pathlib import Path

from openbb_terminal.core.log.generation.directories import get_log_dir, get_log_sub_dir
from openbb_terminal.loggers import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


def test_get_log_dir(mocker):
    mock_file_path = mocker.Mock()
    mocker.patch(
        "openbb_terminal.core.log.generation.directories.Path",
        return_value=mock_file_path,
    )

    log_dir = get_log_dir()
    logger.info("Testing log")

    assert isinstance(log_dir, Path)

    log_file = Path(logging.getLoggerClass().root.handlers[0].baseFilename)

    assert log_file.parent == log_dir

    log_dir_bis = get_log_dir()

    assert isinstance(log_dir, Path)
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
