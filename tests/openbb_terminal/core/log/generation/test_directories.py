import os
from pathlib import Path
from openbb_terminal.core.log.generation import directories

# pylint: disable=too-few-public-methods


class MockFilePath:
    def __init__(self, _):
        self.parent = Path(__file__)


def test_get_log_dir(mocker):
    mocker.patch("openbb_terminal.core.log.generation.directories.Path", MockFilePath)
    path = directories.get_log_dir()
    os.rmdir(path)
    os.remove(path.parent.joinpath(".logid"))
    os.rmdir(path.parent)
