from datetime import datetime
from openbb_terminal.core.log.generation import expired_files

# pylint: disable=too-few-public-methods


class MockObject:
    def __init__(self):
        self.st_mtime = datetime(2020, 11, 11)


class MockFile:
    def is_file(self):
        return True

    def lstat(self):
        return MockObject()

    def unlink(self, missing_ok):
        print(missing_ok)


class MockDir:
    def __init__(self):
        self.exists = True

    def is_dir(self):
        return True

    def iterdir(self):
        return [MockFile(), MockFile()]


def test_get_expired_files():
    value = expired_files.get_expired_file_list(MockDir(), datetime.now())
    assert value


def test_remove_file_list():
    expired_files.remove_file_list([MockFile(), MockFile()])
