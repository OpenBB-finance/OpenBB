import os
from pathlib import Path
from openbb_terminal.core.log.generation import directories


class MockFilePath:
    def __init__(self, _):
        self.parent = Path(__file__)




def test_get_log_dir(mocker):
    mocker.patch("openbb_terminal.core.log.generation.directories.Path", MockFilePath)
    path = directories.get_log_dir()
    os.rmdir(path.parent)
